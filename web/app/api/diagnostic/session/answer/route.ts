import { NextRequest, NextResponse } from "next/server";
import {
  getSession,
  saveSession,
  completeSession,
  PHASE_1_QUESTION_SEQUENCE,
  type AnswerLogEntry,
} from "@/lib/session-store";
import { invokeAccumulate, invokeComplete, invokeQuestionCopy } from "@/lib/engine-client";
import type {
  PrivateOutputPayload,
  StateRef,
  ResolutionFamily,
  SynthesisFields,
} from "@/lib/types";

// ---------------------------------------------------------------------------
// Path 1 (Session 71, Phase 1) — session/answer
//
// Enforces the index invariant (Gemini-specified security boundary, given
// NanoID-only session ownership, consistent with the existing
// ShareableOutput trust model): request.question_id MUST match the
// session's current next_question_id, or this returns 400. Explicit reject
// over silent-ignore — the only caller is our own frontend, so an explicit
// error is more debuggable and costs nothing.
//
// On Q34: routes into the same output shape /api/result already produces
// (PrivateOutputPayload), reusing SeverityEngine/OutputEngine/
// OutputSynthesisEngine via engine.main.run_accumulated_engine() rather
// than duplicating that pipeline. Weighting differs from Path B on
// purpose: real normalized cosine scores (Path A), not equal weight.
// ---------------------------------------------------------------------------

// STATE_RESOLUTION_FAMILY + getPrimaryFamily duplicated here matching the
// existing convention already established across /api/result and
// /api/share/create (both already duplicate this same map independently) —
// per the standing rule against refactoring adjacent files for a
// same-session build, not extracted into a shared module. Flagged as a
// pre-existing pattern, not new tech debt introduced by this file.
const STATE_RESOLUTION_FAMILY: Record<string, ResolutionFamily> = {
  the_unformed_leader:              "Training & Development",
  the_overloaded_manager:           "Training & Development",
  the_dormant_talent:               "Training & Development",
  built_to_fail:                    "Training & Development",
  the_uninitiated:                  "Training & Development",
  groundhog_day:                    "Training & Development",
  the_undefined_role:               "People Tactics and Strategy",
  the_paper_tiger:                  "People Tactics and Strategy",
  the_founders_grip:                "People Tactics and Strategy",
  leadership_continuity_risk:       "People Tactics and Strategy",
  decision_paralysis:               "People Tactics and Strategy",
  the_policy_lag:                   "People Tactics and Strategy",
  dueling_narratives:                "People Tactics and Strategy",
  the_unsolved_problem:             "People Tactics and Strategy",
  transition_paralysis:             "People Tactics and Strategy",
  the_lost_map:                     "People Tactics and Strategy",
  invisible_influence_architecture: "People Tactics and Strategy",
  the_fracture:                     "People Tactics and Strategy",
  silosolation:                     "People Tactics and Strategy",
  the_broken_compass:               "People Tactics and Strategy",
  the_exposed:                      "Intervention",
  hr_capture:                       "Intervention",
  the_unexamined_algorithm:         "Intervention",
  heard_and_ignored:                "Intervention",
  the_tolerated_violation:          "Intervention",
  paper_shield:                     "Intervention",
  pay_exposure:                     "Intervention",
  the_pay_fog:                      "Intervention",
  the_second_close:                 "Intervention",
  the_suppression_filter:           "Intervention",
  the_arbitrary_standard:           "Intervention",
  decision_blindness:               "Intervention",
  the_untouchable:                  "Intervention",
  what_nobody_says:                 "Intervention",
  the_diversity_ceiling:            "Intervention",
  the_unreported_hazard:            "Intervention",
  the_unlocked_door:                "Intervention",
  culture_drift:                    "Executive Advisory",
  identity_erosion:                 "Executive Advisory",
  the_culture_that_wasnt:           "Executive Advisory",
  the_burned_credibility:           "Executive Advisory",
  invisible_burnout:                "Executive Advisory",
  the_basement_standard:            "Executive Advisory",
  the_inside_track:                 "Executive Advisory",
  narrative_lock:                   "Executive Advisory",
  the_wrong_reward:                 "Executive Advisory",
  leadership_deafness:              "Executive Advisory",
};

function getPrimaryFamily(stateId: string | undefined): ResolutionFamily {
  if (!stateId) return "People Tactics and Strategy";
  return STATE_RESOLUTION_FAMILY[stateId] ?? "People Tactics and Strategy";
}

interface AnswerRequest {
  session_id: string;
  question_id: string;
  option_id: string;
}

function validateRequest(body: unknown): body is AnswerRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    typeof b.session_id === "string" &&
    typeof b.question_id === "string" &&
    typeof b.option_id === "string"
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

  const { session_id, question_id, option_id } = body;

  const session = await getSession(session_id);
  if (!session) {
    return NextResponse.json({ error: "Session not found or expired" }, { status: 404 });
  }

  if (session.status !== "in_progress") {
    return NextResponse.json({ error: "Session already complete" }, { status: 400 });
  }

  // Index invariant — the actual security boundary given NanoID-only
  // session ownership.
  if (question_id !== session.next_question_id) {
    return NextResponse.json(
      { error: "question_id does not match session's current question" },
      { status: 400 },
    );
  }

  const updatedVector = await invokeAccumulate({
    accumulated_vector: session.accumulated_vector,
    question_id,
    option_id,
    intake: session.intake,
  });

  const answerEntry: AnswerLogEntry = { question_id, option_id };
  session.accumulated_vector = updatedVector;
  session.answers_log = [...session.answers_log, answerEntry];

  const currentIndex = PHASE_1_QUESTION_SEQUENCE.indexOf(question_id);
  const isLastQuestion = currentIndex === PHASE_1_QUESTION_SEQUENCE.length - 1;

  if (!isLastQuestion) {
    const nextQuestionId = PHASE_1_QUESTION_SEQUENCE[currentIndex + 1];
    session.next_question_id = nextQuestionId;
    await saveSession(session);

    const nextQuestion = await invokeQuestionCopy(nextQuestionId);
    return NextResponse.json({ status: "in_progress", question: nextQuestion });
  }

  // Q34 just answered — completion. Route into the real accumulation-based
  // engine pipeline (Path A), not Path B's declared-diagnosis shortcut.
  const engineResult = await invokeComplete({
    accumulated_vector: session.accumulated_vector,
    intake: session.intake,
    answered_question_count: session.answers_log.length,
  });

  const allEngineStates = engineResult.identified_states;
  if (allEngineStates.length === 0) {
    return NextResponse.json({ error: "Engine returned no states" }, { status: 500 });
  }

  // Path A weighting — real normalized cosine scores, not Path B's equal
  // weight. Mirrors the doc comment already on StateRef in web/lib/types.ts:
  // "Path A (full diagnostic): weight = score_i / sum(all_returned_scores)".
  const totalScore = allEngineStates.reduce((sum, s) => sum + s.score, 0);
  const stateRefs: StateRef[] = allEngineStates.map((s) => ({
    id: s.state_id,
    name: s.state_name,
    weight: totalScore > 0 ? s.score / totalScore : 1 / allEngineStates.length,
  }));

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

    resolution_family: getPrimaryFamily(stateRefs[0]?.id),
    resolution_routing: engineResult.private_output.resolution_routing,

    // friction_tax_estimate: null — CALIBRATION TARGET, STATE_MULTIPLIERS
    // not set, same as Path B.
    friction_tax_estimate: null,

    intake: session.intake,
  };

  // Transition Rule — strips identifiable data the moment status becomes
  // complete. session itself is never marked "complete" and re-saved; it
  // is deleted outright inside completeSession().
  await completeSession(
    session,
    stateRefs.map((s) => ({ id: s.id, name: s.name, weight: s.weight })),
  );

  return NextResponse.json({ status: "complete", result: privatePayload });
}
