import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import type {
  ShareableOutputPayload,
  StateRef,
  IntakeEcho,
  ResolutionFamily,
  ShareableSynthesisFields,
} from "@/lib/types";
import { invokeEngine } from "@/lib/engine-client";

// ---------------------------------------------------------------------------
// Payload separation contract:
//   PrivateOutput is NEVER written to KV.
//   KV stores ShareableOutput only.
//
// Engine call is independent of /api/result — engine runs twice if user shares.
// That is correct and intentional. Option D baseline preserved:
//   no KV write occurs until the user explicitly requests a share link.
// ---------------------------------------------------------------------------

const redis = Redis.fromEnv();
const KV_TTL_SECONDS = 30 * 24 * 60 * 60; // 30 days

// ---------------------------------------------------------------------------
// Resolution family map — mirrors engine/resolution_families.py (S38)
// ---------------------------------------------------------------------------

const STATE_RESOLUTION_FAMILY: Record<string, ResolutionFamily> = {
  the_unformed_leader:              "developmental",
  the_overloaded_manager:           "developmental",
  the_dormant_talent:               "developmental",
  built_to_fail:                    "developmental",
  the_uninitiated:                  "developmental",
  groundhog_day:                    "developmental",
  the_undefined_role:               "structural",
  the_paper_tiger:                  "structural",
  the_founders_grip:                "structural",
  leadership_continuity_risk:       "structural",
  decision_paralysis:               "structural",
  the_policy_lag:                   "structural",
  dueling_narratives:               "structural",
  the_unsolved_problem:             "structural",
  transition_paralysis:             "structural",
  the_lost_map:                     "structural",
  invisible_influence_architecture: "structural",
  the_fracture:                     "structural",
  silosolation:                     "structural",
  the_broken_compass:               "structural",
  the_exposed:                      "investigative",
  hr_capture:                       "investigative",
  the_unexamined_algorithm:         "investigative",
  heard_and_ignored:                "investigative",
  the_tolerated_violation:          "investigative",
  paper_shield:                     "investigative",
  pay_exposure:                     "investigative",
  the_pay_fog:                      "investigative",
  the_second_close:                 "investigative",
  the_suppression_filter:           "investigative",
  the_arbitrary_standard:           "investigative",
  decision_blindness:               "investigative",
  the_untouchable:                  "investigative",
  what_nobody_says:                 "investigative",
  the_diversity_ceiling:            "investigative",
  the_unreported_hazard:            "investigative",
  the_unlocked_door:                "investigative",
  culture_drift:                    "directional",
  identity_erosion:                 "directional",
  the_culture_that_wasnt:           "directional",
  the_burned_credibility:           "directional",
  invisible_burnout:                "directional",
  the_basement_standard:            "directional",
  the_inside_track:                 "directional",
  narrative_lock:                   "directional",
  the_wrong_reward:                 "directional",
  leadership_deafness:              "directional",
};

function getPrimaryFamily(stateIds: string[]): ResolutionFamily {
  if (stateIds.length === 0) return "structural";
  return STATE_RESOLUTION_FAMILY[stateIds[0]] ?? "structural";
}

// ---------------------------------------------------------------------------
// Weight computation
// ---------------------------------------------------------------------------

function computeWeights(
  states: Array<{ id: string; name: string; score: number }>,
  path: "A" | "B"
): StateRef[] {
  if (states.length === 0) return [];
  if (path === "B") {
    const w = 1 / states.length;
    return states.map((s) => ({ id: s.id, name: s.name, weight: w }));
  }
  const total = states.reduce((sum, s) => sum + s.score, 0);
  return states.map((s) => ({
    id: s.id,
    name: s.name,
    weight: total > 0 ? s.score / total : 1 / states.length,
  }));
}

// ---------------------------------------------------------------------------
// Intake mapping
// ---------------------------------------------------------------------------

function mapIntake(engineIntake: Record<string, unknown>): IntakeEcho {
  const jurisdictions = Array.isArray(engineIntake.jurisdictions)
    ? (engineIntake.jurisdictions as string[])
    : [];
  return {
    organization_size: (engineIntake.org_size as string) ?? "",
    industry: (engineIntake.industry as string) ?? "",
    role_level: (engineIntake.principal_role as string) ?? "",
    tenure_in_role: "",
    direct_reports: "",
    jurisdiction: jurisdictions[0] ?? "",
  };
}

// ---------------------------------------------------------------------------
// Request schema
// Client re-sends { selectedStateIds, intake } (Path X, locked S40).
// Engine invoked independently of /api/result.
// ---------------------------------------------------------------------------

interface CreateShareRequest {
  selectedStateIds: string[];
  intake: {
    headcount: string;
    industry: string;
    orgType: string;
    jurisdictions: string[];
    significantEvents: string[];
    principalRole: string;
  };
}

function validateRequest(body: unknown): body is CreateShareRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    Array.isArray(b.selectedStateIds) &&
    b.selectedStateIds.every((id) => typeof id === "string") &&
    typeof b.intake === "object" &&
    b.intake !== null
  );
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!validateRequest(body)) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const { selectedStateIds, intake } = body;

  const engineResult = await invokeEngine({ selectedStateIds, intake });

  const allEngineStates = engineResult.identified_states;
  if (allEngineStates.length === 0) {
    return NextResponse.json({ error: "Engine returned no states" }, { status: 500 });
  }

  const allStateRefs = computeWeights(
    allEngineStates.map((s) => ({
      id: s.state_id,
      name: s.state_name,
      score: s.score,
    })),
    "B"
  );

  const primaryState = allStateRefs[0];
  const allSecondaries = allStateRefs.slice(1);

  // Secondary state filter: weight >= 0.20, max 2
  // Rationale: precision over completeness for board/CFO audience.
  const filteredSecondaries = allSecondaries
    .filter((s) => s.weight >= 0.20)
    .slice(0, 2);

  const shareId = nanoid(21);
  const createdAt = new Date().toISOString();
  const expiresAt = new Date(Date.now() + KV_TTL_SECONDS * 1000).toISOString();

  // Airgap: liability_condition_text and asset_resolution_anchor_text are private —
  // principal only, never written to KV (Gemini Q1 revised, S42).
  // framing_text, observable_indicators, resolution_framing_text are KV-safe.
  const engSynthesis = engineResult.synthesis;
  const synthesis: ShareableSynthesisFields = engSynthesis
    ? {
        framing_text:            engSynthesis.framing_text,
        observable_indicators:   engSynthesis.observable_indicators,
        resolution_framing_text: engSynthesis.resolution_framing_text,
        synthesis_confidence:    engSynthesis.synthesis_confidence,
        is_fallback:             engSynthesis.is_fallback,
      }
    : {
        framing_text:            "",
        observable_indicators:   [],
        resolution_framing_text: "",
        synthesis_confidence:    0.0,
        is_fallback:             true,
      };

  const shareablePayload: ShareableOutputPayload = {
    synthesis,

    primary_state: primaryState,
    secondary_states: filteredSecondaries,

    severity: engineResult.severity.tier,

    resolution_family: getPrimaryFamily(selectedStateIds),

    // friction_tax_estimate: null in Path B (CALIBRATION TARGET)
    friction_tax_estimate: null,

    intake: mapIntake(engineResult.intake as Record<string, unknown>),

    share_id: shareId,
    expires_at: expiresAt,
    created_at: createdAt,
  };

  // Write to KV — ShareableOutput only. PrivateOutput never written to KV.
  await redis.set(`share:${shareId}`, JSON.stringify(shareablePayload), {
    ex: KV_TTL_SECONDS,
  });

  const origin = request.headers.get("origin") ?? "";

  return NextResponse.json({
    share_id: shareId,
    shareUrl: `${origin}/share/${shareId}`,
    expiresAt,
  });
}
