import { NextRequest, NextResponse } from "next/server";
import {
  getSession,
  saveSession,
  resolveQuestionLabel,
} from "@/lib/session-store";
import { invokeNarrativeProcess, invokeQuestionCopy } from "@/lib/engine-client";
import { completeDiagnosticSession } from "@/lib/diagnostic-completion";

// ---------------------------------------------------------------------------
// Narrative modulation (Phase 3) -- session/narrative
//
// Companion to session/answer: fires only after that route (or resume)
// has returned {status: "narrative", prompt} and the client has collected
// the principal's free-text response. Accepts {session_id, narrative_text}
// -- an empty string is a valid, deliberate skip (extract_signals("")
// returns overall_confidence=0.0, so modulation and severity addition
// both become no-ops via their own existing floor checks -- no separate
// skip code path needed).
//
// session.pending_completion (set by session/answer when the standard,
// end-of-sequence trigger fired) decides whether this call completes the
// session or returns the next question -- next_question_id was already
// set correctly by session/answer before the narrative detour in the
// early-trigger case, so this route never needs to recompute it.
// ---------------------------------------------------------------------------

interface NarrativeRequest {
  session_id: string;
  narrative_text: string;
}

function validateRequest(body: unknown): body is NarrativeRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return typeof b.session_id === "string" && typeof b.narrative_text === "string";
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

  const { session_id, narrative_text } = body;

  const session = await getSession(session_id);
  if (!session) {
    return NextResponse.json({ error: "Session not found or expired" }, { status: 404 });
  }

  if (session.status !== "in_progress") {
    return NextResponse.json({ error: "Session already complete" }, { status: 400 });
  }

  // No question_id/next_question_id invariant applies here (narrative
  // isn't a QUESTION_LIBRARY entry) -- the real guard is that a prompt
  // must actually be pending, mirroring session/answer's own explicit-
  // reject-over-silent-ignore philosophy.
  if (session.narrative_fired || session.pending_narrative_prompt === null) {
    return NextResponse.json(
      { error: "No narrative prompt is currently pending for this session" },
      { status: 400 },
    );
  }

  const result = await invokeNarrativeProcess({
    accumulated_vector: session.accumulated_vector,
    narrative_text,
    answered_question_count: session.answers_log.length,
  });

  session.accumulated_vector = result.accumulated_vector;
  session.narrative_fired = true;
  session.narrative_response = narrative_text;
  session.narrative_severity_addition = result.narrative_severity_addition;
  // pending_completion (set by session/answer) distinguishes the standard
  // trigger ("Q34" -- SessionData's own locked label for the
  // end-of-sequence trigger, not the literal question) from the early
  // trigger ("Q27").
  session.narrative_trigger_point = session.pending_completion ? "Q34" : "Q27";
  session.narrative_overall_confidence = result.narrative_overall_confidence;
  session.narrative_signals_count = result.narrative_signals_count;
  // Pure Stateful Modulation with Completion Re-ranking (this session's
  // fix) -- see session-store.ts's own field comment.
  session.pre_narrative_vector = result.pre_narrative_vector;
  session.pending_narrative_prompt = null;

  if (session.pending_completion) {
    await saveSession(session);
    return completeDiagnosticSession(session);
  }

  await saveSession(session);
  const nextQuestion = await invokeQuestionCopy(session.next_question_id);
  const label = resolveQuestionLabel(session.next_question_id, session.question_labels);
  return NextResponse.json({ status: "in_progress", question: nextQuestion, label });
}
