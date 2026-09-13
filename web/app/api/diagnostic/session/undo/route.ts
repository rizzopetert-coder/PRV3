import { NextRequest, NextResponse } from "next/server";
import {
  getSession,
  saveSession,
  removeFromSequence,
  shouldSpliceQ28,
  shouldSpliceQ45,
  checkpointIdMap,
  checkpointSlot,
  setCheckpointSlot,
  resolveQuestionLabel,
  ZERO_VECTOR,
  type AccumulatedVector,
} from "@/lib/session-store";
import { invokeAccumulate, invokeQuestionCopy } from "@/lib/engine-client";

// ---------------------------------------------------------------------------
// Path 1 — session/undo (this session)
//
// Single-step "back to previous question" undo. NOT the descoped edit-and-
// replay case: the user is always at the frontier, so there is nothing
// downstream to replay -- this reverses exactly the most recently answered
// question and nothing else. See tools/_mob.txt (grep "truncate-and-replay")
// for why the harder, arbitrary-position case stays parked; that reasoning
// does not apply here.
//
// Same request/response shape and error-handling philosophy as
// session/answer/route.ts (explicit reject over silent-ignore, index
// invariant style validation) -- this is a sibling route, not a different
// convention.
// ---------------------------------------------------------------------------

interface UndoRequest {
  session_id: string;
}

function validateRequest(body: unknown): body is UndoRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return typeof b.session_id === "string";
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

  const { session_id } = body;

  const session = await getSession(session_id);
  if (!session) {
    return NextResponse.json({ error: "Session not found or expired" }, { status: 404 });
  }

  if (session.status !== "in_progress") {
    return NextResponse.json({ error: "Session already complete" }, { status: 400 });
  }

  // Nothing to undo at Q01 -- clean no-op, not an error. The client is
  // expected to disable/hide the back button in this state (checked
  // client-side against history.length === 0); this guard exists so a
  // stale or duplicate request can't produce a confusing error.
  if (session.answers_log.length === 0) {
    const label = resolveQuestionLabel(session.next_question_id, session.question_labels);
    const question = await invokeQuestionCopy(session.next_question_id);
    return NextResponse.json({ status: "noop", question, label });
  }

  // Narrative modulation has already begun -- undoing across that boundary
  // is deliberately out of scope for this pass (see tools/_mob.txt). Not a
  // live path today: narrative is a distinct FlowState phase on the client
  // ("narrative", not "question"), so the back button is never visible when
  // this would fire. Kept as an explicit reject rather than an assumption,
  // same philosophy as session/answer's own index invariant check.
  if (
    session.narrative_fired ||
    session.pending_narrative_prompt !== null ||
    session.pending_completion
  ) {
    return NextResponse.json(
      { error: "Cannot undo past a narrative transition" },
      { status: 400 },
    );
  }

  const lastEntry = session.answers_log[session.answers_log.length - 1];
  const questionBeingUndone = lastEntry.question_id;

  // Recompute this answer's exact contribution by replaying it against a
  // ZERO base vector through the same engine call the forward path uses --
  // not a parallel reimplementation. accumulate_one_answer() starts a fresh
  // AccumulationSession from whatever base vector it's given and adds this
  // one answer's contribution once, so a zero base makes the response's
  // accumulated_vector exactly equal to that contribution. Deterministic
  // and order-independent: confirmed directly against engine/accumulation.py
  // this session -- _apply_signal_reliability()/_apply_axis_modifiers() only
  // touch IntakeData fields (role, industry, org_type, jurisdictions) fixed
  // once at session start, never any other answer or session state.
  const followOnOrigin = session.severity_follow_on_origins[questionBeingUndone];
  const delta = await invokeAccumulate({
    accumulated_vector: ZERO_VECTOR,
    question_id: questionBeingUndone,
    option_ids: lastEntry.option_ids,
    intake: session.intake,
    trigger_question_id: followOnOrigin?.trigger_question_id,
    triggering_option_id: followOnOrigin?.triggering_option_id,
  });

  // Element-wise subtraction -- exact inverse of accumulate_answer()'s
  // element-wise addition in engine/accumulation.py, same shape.
  const reverted: AccumulatedVector = { ...session.accumulated_vector };
  for (const field of Object.keys(reverted) as Array<keyof AccumulatedVector>) {
    reverted[field] = reverted[field] - delta.accumulated_vector[field];
  }
  session.accumulated_vector = reverted;

  // Pop this answer's own severity_inputs entries -- appended in order
  // (session/answer/route.ts), and nothing after the undone answer has
  // been touched, so the last N entries (N = however many this replay
  // produced) are exactly the ones this question added.
  if (delta.severity_inputs.length > 0) {
    session.severity_inputs = session.severity_inputs.slice(
      0,
      session.severity_inputs.length - delta.severity_inputs.length,
    );
  }

  session.answers_log = session.answers_log.slice(0, -1);

  // Reverse whatever this answer spliced into question_sequence, if
  // anything. Removal by ID membership (not position) is safe here: nothing
  // after the undone answer has been touched, so any question it spliced in
  // is guaranteed not yet answered.
  const idsToRemove: string[] = [];

  for (const id of delta.severity_follow_on_ids) {
    idsToRemove.push(id);
    delete session.severity_follow_on_origins[id];
    delete session.question_labels[id];
  }

  if (questionBeingUndone === "Q06" && shouldSpliceQ28(lastEntry.option_ids)) {
    idsToRemove.push("Q28");
    delete session.question_labels["Q28"];
  }
  if (questionBeingUndone === "Q44" && shouldSpliceQ45(lastEntry.option_ids)) {
    idsToRemove.push("Q45");
    delete session.question_labels["Q45"];
  }

  // Checkpoint reset -- if the undone question was itself a checkpoint
  // position (Q11/Q19/Q27) and it fired, remove its distinguishers too and
  // reset the slot to null so it can re-fire correctly once this question
  // is re-answered (session/answer/route.ts only evaluates a checkpoint
  // while its slot is still null).
  const checkpointPosition = checkpointIdMap[questionBeingUndone];
  if (checkpointPosition) {
    const slot = checkpointSlot(session, checkpointPosition);
    if (slot !== null) {
      if (slot.fires) {
        for (const id of slot.distinguishers) {
          idsToRemove.push(id);
          delete session.question_labels[id];
        }
      }
      setCheckpointSlot(session, checkpointPosition, null);
    }
  }

  if (idsToRemove.length > 0) {
    session.question_sequence = removeFromSequence(session.question_sequence, idsToRemove);
  }

  session.next_question_id = questionBeingUndone;
  await saveSession(session);

  const question = await invokeQuestionCopy(questionBeingUndone);
  const label = resolveQuestionLabel(questionBeingUndone, session.question_labels);
  // lastEntry.option_ids -- captured above, before answers_log was popped --
  // so the client can pre-fill the same selection on the re-rendered
  // question rather than showing it fresh. This is the only thing this
  // route returns that reflects the undone answer itself; everything else
  // in the response describes the question being returned to.
  return NextResponse.json({
    status: "in_progress",
    question,
    label,
    option_ids: lastEntry.option_ids,
  });
}
