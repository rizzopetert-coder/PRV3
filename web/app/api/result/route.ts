import { NextRequest, NextResponse } from "next/server";
import type { PrivateOutputPayload } from "@/lib/output-renderer";

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

  const { sessionId, selectedStateIds } = body;

  const outputType: PrivateOutputPayload["outputType"] =
    selectedStateIds.length === 0
      ? "no_signal"
      : selectedStateIds.length === 1
        ? "single_state"
        : "multi_state";

  const primaryFamily = getPrimaryFamily(selectedStateIds);

  // TODO(S40): Call Python engine with session payload.
  // Engine returns full contract VII.1 output. Extract private_output fields only.
  // synthesis.private_synthesis arrives from engine as an opaque string — never generated here.
  // ShareableOutput is never constructed in this handler.

  const privatePayload: PrivateOutputPayload = {
    sessionId,
    outputType,
    identifiedStates: selectedStateIds.map((id, i) => ({
      state_id: id,
      state_name: formatStateName(id),
      score: parseFloat((1.0 - i * 0.05).toFixed(4)), // TODO(S40): replace with engine scores
      distinguishing_language: null as null,
    })),
    severity: {
      tier: "Entrenched",             // TODO(S40): from engine severity_result
      score: 50,                      // TODO(S40): from engine severity_result
      anchor_text: "COPY PENDING",
    },
    privateOutput: {
      opening_text: "COPY PENDING",      // TODO(S40): from engine private_output
      liability_block: "COPY PENDING",   // TODO(S40): from engine private_output
      asset_anchor_text: "COPY PENDING", // TODO(S40): from engine private_output
      resolution_routing: primaryFamily, // wired — mirrors engine/resolution_families.py
      friction_tax_estimate: null,       // TODO(S40): from compute_friction_tax()
    },
    // synthesis populated by engine (S40) — opaque string, never generated in TypeScript layer
  };

  // ShareableOutput is NEVER serialized into this response.
  return NextResponse.json(privatePayload);
}
