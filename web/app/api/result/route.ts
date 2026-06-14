import { NextRequest, NextResponse } from "next/server";
import type {
  PrivateOutputPayload,
  StateRef,
  IntakeEcho,
  ResolutionFamily,
} from "@/lib/types";
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

const STATE_RESOLUTION_FAMILY: Record<string, ResolutionFamily> = {
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

function getPrimaryFamily(stateIds: string[]): ResolutionFamily {
  if (stateIds.length === 0) return "structural";
  return STATE_RESOLUTION_FAMILY[stateIds[0]] ?? "structural";
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

  const privatePayload: PrivateOutputPayload = {
    // synthesis: opaque string from engine. Not present in Path B (no output_synthesis call).
    synthesis: "",

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
