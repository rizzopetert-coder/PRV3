import { NextRequest, NextResponse } from "next/server";
import type {
  PrivateOutputPayload,
  StateRef,
  IntakeEcho,
  ResolutionFamily,
  SynthesisFields,
} from "@/lib/types";
import { invokeEngine } from "@/lib/engine-client";

// ---------------------------------------------------------------------------
// Payload separation contract:
//   PrivateOutput is returned to the browser. Never written to KV.
//   ShareableOutput is never constructed here.
//   No KV write of any kind occurs in this handler.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Resolution family map — commercial names (S45)
// Groundwork | Development | First Call | Advisory
// ---------------------------------------------------------------------------

const STATE_RESOLUTION_FAMILY: Record<string, ResolutionFamily> = {
  // Development
  the_unformed_leader:              "Development",
  the_overloaded_manager:           "Development",
  the_dormant_talent:               "Development",
  built_to_fail:                    "Development",
  the_uninitiated:                  "Development",
  groundhog_day:                    "Development",
  // Groundwork
  the_undefined_role:               "Groundwork",
  the_paper_tiger:                  "Groundwork",
  the_founders_grip:                "Groundwork",
  leadership_continuity_risk:       "Groundwork",
  decision_paralysis:               "Groundwork",
  the_policy_lag:                   "Groundwork",
  dueling_narratives:               "Groundwork",
  the_unsolved_problem:             "Groundwork",
  transition_paralysis:             "Groundwork",
  the_lost_map:                     "Groundwork",
  invisible_influence_architecture: "Groundwork",
  the_fracture:                     "Groundwork",
  silosolation:                     "Groundwork",
  the_broken_compass:               "Groundwork",
  // First Call
  the_exposed:                      "First Call",
  hr_capture:                       "First Call",
  the_unexamined_algorithm:         "First Call",
  heard_and_ignored:                "First Call",
  the_tolerated_violation:          "First Call",
  paper_shield:                     "First Call",
  pay_exposure:                     "First Call",
  the_pay_fog:                      "First Call",
  the_second_close:                 "First Call",
  the_suppression_filter:           "First Call",
  the_arbitrary_standard:           "First Call",
  decision_blindness:               "First Call",
  the_untouchable:                  "First Call",
  what_nobody_says:                 "First Call",
  the_diversity_ceiling:            "First Call",
  the_unreported_hazard:            "First Call",
  the_unlocked_door:                "First Call",
  // Advisory
  culture_drift:                    "Advisory",
  identity_erosion:                 "Advisory",
  the_culture_that_wasnt:           "Advisory",
  the_burned_credibility:           "Advisory",
  invisible_burnout:                "Advisory",
  the_basement_standard:            "Advisory",
  the_inside_track:                 "Advisory",
  narrative_lock:                   "Advisory",
  the_wrong_reward:                 "Advisory",
  leadership_deafness:              "Advisory",
};

function getPrimaryFamily(stateIds: string[]): ResolutionFamily {
  if (stateIds.length === 0) return "Groundwork";
  return STATE_RESOLUTION_FAMILY[stateIds[0]] ?? "Groundwork";
}

// ---------------------------------------------------------------------------
// Weight computation
// Path B: equal weight (1 / n) for all selected states.
// Path A: normalized cosine scores.
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
// Intake mapping — engine echo fields → IntakeEcho contract
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
// ---------------------------------------------------------------------------

interface ResultRequest {
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

function validateRequest(body: unknown): body is ResultRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    Array.isArray(b.selectedStateIds) &&
    b.selectedStateIds.every((id) => typeof id === "string") &&
    typeof b.intake === "object" &&
    b.intake !== null
  );
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

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

  const stateRefs = computeWeights(
    allEngineStates.map((s) => ({
      id: s.state_id,
      name: s.state_name,
      score: s.score,
    })),
    "B"
  );

  const engSynthesis = engineResult.synthesis;
  const synthesis: SynthesisFields = engSynthesis
    ? {
        liability_condition_text:     engSynthesis.liability_condition_text,
        asset_resolution_anchor_text: engSynthesis.asset_resolution_anchor_text,
        framing_text:                 engSynthesis.framing_text,
        observable_indicators:        engSynthesis.observable_indicators,
        resolution_framing_text:      engSynthesis.resolution_framing_text,
        synthesis_confidence:         engSynthesis.synthesis_confidence,
        is_fallback:                  engSynthesis.is_fallback,
      }
    : {
        liability_condition_text:     "",
        asset_resolution_anchor_text: "",
        framing_text:                 "",
        observable_indicators:        [],
        resolution_framing_text:      "",
        synthesis_confidence:         0.0,
        is_fallback:                  true,
      };

  const privatePayload: PrivateOutputPayload = {
    synthesis,

    primary_state: stateRefs[0],
    secondary_states: stateRefs.slice(1),

    severity: engineResult.severity.tier,

    resolution_family: getPrimaryFamily(selectedStateIds),
    // resolution_routing: legacy service-name string from states.py profile (old naming, pre-S32)
    resolution_routing: engineResult.private_output.resolution_routing,

    // friction_tax_estimate: null in Path B (CALIBRATION TARGET — STATE_MULTIPLIERS not set)
    friction_tax_estimate: null,

    intake: mapIntake(engineResult.intake as Record<string, unknown>),
  };

  // ShareableOutput is NEVER serialized into this response.
  return NextResponse.json(privatePayload);
}
