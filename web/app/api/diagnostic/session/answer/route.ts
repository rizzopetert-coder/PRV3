import { NextRequest, NextResponse } from "next/server";
import {
  getSession,
  saveSession,
  completeSession,
  spliceDistinguishers,
  isLastQuestionInSequence,
  validateIndexInvariant,
  severityFollowOnAlreadyAsked,
  spliceLabel,
  resolveQuestionLabel,
  type AnswerLogEntry,
  type CheckpointResult,
  type DiagnosticSession,
} from "@/lib/session-store";
import {
  invokeAccumulate,
  invokeCheckpoint,
  invokeComplete,
  invokeQuestionCopy,
} from "@/lib/engine-client";
import type {
  PrivateOutputPayload,
  StateRef,
  SynthesisFields,
} from "@/lib/types";
import { translateResolutionFamily } from "@/lib/resolution-family";

// Checkpoint ID mapping (Phase 2) — Q27 has two branch IDs (Q27A/Q27B)
// depending on intake.significant_events; Phase 1's locked intake adapter
// always takes the Q27B branch (session-store.ts header), but both map to
// the same canonical checkpoint position so this route doesn't hardcode
// that assumption. Only question_ids present here trigger a checkpoint
// evaluation call below.
const checkpointIdMap: Record<string, "Q11" | "Q19" | "Q27"> = {
  Q11: "Q11",
  Q19: "Q19",
  Q27A: "Q27",
  Q27B: "Q27",
};

// Three independent DiagnosticSession slots (Stage 1) — not a nested dict.
function checkpointSlot(
  session: DiagnosticSession,
  position: "Q11" | "Q19" | "Q27",
): CheckpointResult | null {
  if (position === "Q11") return session.checkpoint_q11;
  if (position === "Q19") return session.checkpoint_q19;
  return session.checkpoint_q27;
}

function setCheckpointSlot(
  session: DiagnosticSession,
  position: "Q11" | "Q19" | "Q27",
  result: CheckpointResult,
): void {
  if (position === "Q11") session.checkpoint_q11 = result;
  else if (position === "Q19") session.checkpoint_q19 = result;
  else session.checkpoint_q27 = result;
}

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
  if (!validateIndexInvariant(question_id, session.next_question_id)) {
    return NextResponse.json(
      { error: "question_id does not match session's current question" },
      { status: 400 },
    );
  }

  const accumulateResult = await invokeAccumulate({
    accumulated_vector: session.accumulated_vector,
    question_id,
    option_id,
    intake: session.intake,
  });

  const answerEntry: AnswerLogEntry = { question_id, option_id };
  session.accumulated_vector = accumulateResult.accumulated_vector;
  session.answers_log = [...session.answers_log, answerEntry];

  // Severity follow-on wiring (Path 1): question_id itself was a SEVER-##
  // follow-on that maps to a real SeverityInput field -- collect it for
  // threading into invokeComplete() at Q34.
  if (accumulateResult.severity_input) {
    session.severity_inputs = [...session.severity_inputs, accumulateResult.severity_input];
  }

  // currentIndex is stable across the splices below — both insert strictly
  // after this position, so the just-answered question's own index never
  // shifts as a result of its own follow-on or checkpoint firing.
  const currentIndex = session.question_sequence.indexOf(question_id);

  // Severity follow-on splice — simple per-answer boolean check on the
  // just-answered option's own severity_trigger flag (already present on
  // AnswerOption, previously unread), NOT an entropy calculation like
  // checkpoints use. Mirrors spliceDistinguishers()'s existing pattern
  // exactly, reusing the same function (a single-element distinguishers
  // list is exactly what it already handles) rather than a parallel
  // reimplementation. Guarded against re-firing an already-asked follow-on
  // (SEVER-11's parked Q31 alternate parent means this only matters for
  // Q28 today, but the guard is real, general infrastructure -- see
  // session-store.ts).
  const severityFollowOnId = accumulateResult.severity_follow_on_id;
  if (
    severityFollowOnId &&
    !severityFollowOnAlreadyAsked(session.answers_log, severityFollowOnId)
  ) {
    session.question_sequence = spliceDistinguishers(
      session.question_sequence,
      currentIndex,
      [severityFollowOnId],
    );
    session.question_labels[severityFollowOnId] = spliceLabel(question_id, 0);
  }

  // Q28 conditional splice — the only one of the two live-session-surfaced
  // "adaptive" annotations actually built as a real conditional trigger
  // (Q31 is parked, see PHASE_1_QUESTION_SEQUENCE's comment). Q06 itself
  // carries no severity_trigger of its own (its options don't set one),
  // so this is a direct, explicit check rather than reusing the severity
  // mechanism above -- a single hardcoded case, not a generalized
  // framework, since nothing else currently needs this shape.
  if (question_id === "Q06" && (option_id === "A" || option_id === "B")) {
    session.question_sequence = spliceDistinguishers(
      session.question_sequence,
      currentIndex,
      ["Q28"],
    );
    session.question_labels["Q28"] = spliceLabel("Q06", 0);
  }

  // Checkpoint evaluation — at most once per canonical position per
  // session, guarded by the slot-null check (the index invariant above
  // should already prevent replaying a question_id, but this doesn't rely
  // on that alone, per explicit instruction).
  const checkpointPosition = checkpointIdMap[question_id];
  if (checkpointPosition && checkpointSlot(session, checkpointPosition) === null) {
    const alreadyAsked = session.answers_log
      .filter((entry) => entry.question_id.startsWith("DIST-"))
      .map((entry) => entry.question_id);

    // Propagates on failure — explicit error over silent-ignore, matching
    // this route's existing philosophy for the index invariant above. A
    // checkpoint call that fails must not be treated as "evaluated, did
    // not fire."
    const checkpointResult = await invokeCheckpoint({
      checkpoint_position: checkpointPosition,
      accumulated_vector: session.accumulated_vector,
      // True live count at this exact moment, not derived from
      // checkpointPosition -- session.answers_log was already updated
      // above for the just-answered question, so this is the same value
      // the Q34 completion call below uses (session.answers_log.length),
      // computed the same way for the same reason.
      answered_question_count: session.answers_log.length,
      already_asked: alreadyAsked,
    });

    setCheckpointSlot(session, checkpointPosition, checkpointResult);

    if (checkpointResult.fires) {
      session.question_sequence = spliceDistinguishers(
        session.question_sequence,
        currentIndex,
        checkpointResult.distinguishers,
      );
      checkpointResult.distinguishers.forEach((distinguisherId, letterIndex) => {
        session.question_labels[distinguisherId] = spliceLabel(question_id, letterIndex);
      });
    }
  }

  // Computed AFTER the possible splice above, so length reflects any
  // distinguishers just inserted for THIS question. "Last question" means
  // end of this session's own (possibly-extended) sequence, not a
  // hardcoded position 34.
  const isLastQuestion = isLastQuestionInSequence(session.question_sequence, currentIndex);

  if (!isLastQuestion) {
    const nextQuestionId = session.question_sequence[currentIndex + 1];
    session.next_question_id = nextQuestionId;
    await saveSession(session);

    const nextQuestion = await invokeQuestionCopy(nextQuestionId);
    const label = resolveQuestionLabel(nextQuestionId, session.question_labels);
    return NextResponse.json({ status: "in_progress", question: nextQuestion, label });
  }

  // Q34 just answered — completion. Route into the real accumulation-based
  // engine pipeline (Path A), not Path B's declared-diagnosis shortcut.
  const engineResult = await invokeComplete({
    accumulated_vector: session.accumulated_vector,
    intake: session.intake,
    answered_question_count: session.answers_log.length,
    checkpoint_results: {
      q11: session.checkpoint_q11,
      q19: session.checkpoint_q19,
      q27: session.checkpoint_q27,
    },
    severity_inputs: session.severity_inputs,
    answers_log: session.answers_log,
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
    descriptive_prose: s.descriptive_prose,
  }));

  const engSynthesis = engineResult.synthesis;
  const synthesis: SynthesisFields = engSynthesis
    ? {
        liability_condition_text:     engSynthesis.liability_condition_text,
        asset_resolution_anchor_text: engSynthesis.asset_resolution_anchor_text,
        framing_text:                 engSynthesis.framing_text,
        observable_indicators:        engSynthesis.observable_indicators,
        resolution_framing_text:      engSynthesis.resolution_framing_text,
        headline:                     engSynthesis.headline,
        synthesis_confidence:         engSynthesis.synthesis_confidence,
        is_fallback:                  engSynthesis.is_fallback,
      }
    : {
        liability_condition_text:     "",
        asset_resolution_anchor_text: "",
        framing_text:                 "",
        observable_indicators:        [],
        resolution_framing_text:      "",
        headline:                     "",
        synthesis_confidence:         0.0,
        is_fallback:                  true,
      };

  const privatePayload: PrivateOutputPayload = {
    synthesis,

    primary_state: stateRefs[0],
    secondary_states: stateRefs.slice(1),

    severity: engineResult.severity.tier,

    resolution_family: translateResolutionFamily(engineResult.private_output.resolution_routing),
    resolution_routing: engineResult.private_output.resolution_routing,

    friction_tax_estimate: engineResult.private_output.friction_tax_estimate,
    legal_tail_risk_exposure: engineResult.private_output.legal_tail_risk_exposure,

    cascade_risk: engineResult.private_output.cascade_risk,
    causation_pattern: engineResult.private_output.causation_pattern,
    trajectory: engineResult.private_output.trajectory,
    urgency_window: engineResult.private_output.urgency_window,

    intake: session.intake,

    dimension_summary: engineResult.dimension_summary,
    primary_asset_domain: engineResult.asset_score.primary_asset_domain,
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
