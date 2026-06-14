import { NextRequest, NextResponse } from "next/server";
import type { PrivateOutputPayload } from "@/lib/output-renderer";
import { invokeEngine } from "@/lib/engine-client";

// ---------------------------------------------------------------------------
// Payload separation contract:
//   PrivateOutput is returned to the browser. Never written to KV.
//   ShareableOutput is never constructed here.
//   No KV write of any kind occurs in this handler.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Resolution family map — mirrors engine/resolution_families.py (S38)
// No service names. Four families: structural | developmental | investigative | directional
// ---------------------------------------------------------------------------

const STATE_RESOLUTION_FAMILY: Record<string, string> = {
  // Developmental
  the_unformed_leader:              "developmental",
  the_overloaded_manager:           "developmental",
  the_dormant_talent:               "developmental",
  built_to_fail:                    "developmental",
  the_uninitiated:                  "developmental",
  groundhog_day:                    "developmental",
  // Structural
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
  // Investigative
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
  // Directional
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

function getPrimaryFamily(stateIds: string[]): string {
  if (stateIds.length === 0) return "structural";
  return STATE_RESOLUTION_FAMILY[stateIds[0]] ?? "structural";
}

function formatStateName(stateId: string): string {
  return stateId.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

// ---------------------------------------------------------------------------
// Request schema
// ---------------------------------------------------------------------------

interface ResultRequest {
  sessionId: string;
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
    typeof b.sessionId === "string" &&
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

  const { sessionId, selectedStateIds, intake } = body;

  const engineResult = await invokeEngine({ selectedStateIds, intake });

  const privatePayload: PrivateOutputPayload = {
    sessionId,
    outputType: engineResult.output_type,
    identifiedStates: engineResult.identified_states.map((s) => ({
      state_id: s.state_id,
      state_name: s.state_name,
      score: s.score,
      distinguishing_language: s.distinguishing_language,
    })),
    severity: {
      tier: engineResult.severity.tier,
      score: engineResult.severity.score,
      anchor_text: engineResult.severity.anchor_text,
    },
    privateOutput: {
      opening_text: engineResult.private_output.opening_text,
      liability_block: engineResult.private_output.liability_block,
      asset_anchor_text: engineResult.private_output.asset_anchor_text,
      resolution_routing: engineResult.private_output.resolution_routing,
      friction_tax_estimate: null,
    },
    // synthesis: opaque string from engine — not present in Path B (no output_synthesis call)
  };

  // ShareableOutput is NEVER serialized into this response.
  return NextResponse.json(privatePayload);
}
