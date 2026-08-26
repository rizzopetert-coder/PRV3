import { NextRequest, NextResponse } from "next/server";
import { getSession, resolveQuestionLabel } from "@/lib/session-store";
import { invokeQuestionCopy } from "@/lib/engine-client";

// ---------------------------------------------------------------------------
// Path 1 -- session/resume
//
// Additive capability, not part of the original Session 71 handoff: lets a
// caller who already holds a session_id (tools/diagnostic_fast_forward.py's
// Mode 2, or a Pete-held mid-flow link) fetch the CURRENT question for that
// session without submitting an answer -- a read-only companion to
// session/answer, which only ever advances state. Touches nothing:
// accumulated_vector, question_sequence, checkpoint slots, and severity
// state are all read via the existing getSession(), never mutated here.
// ---------------------------------------------------------------------------

interface ResumeRequest {
  session_id: string;
}

function validateRequest(body: unknown): body is ResumeRequest {
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

  const session = await getSession(body.session_id);
  if (!session) {
    return NextResponse.json({ error: "Session not found or expired" }, { status: 404 });
  }

  if (session.status !== "in_progress") {
    return NextResponse.json({ error: "Session already complete" }, { status: 400 });
  }

  // Narrative modulation (Phase 3) -- a pending narrative prompt isn't a
  // QUESTION_LIBRARY entry, so it needs its own resume branch, same
  // reason the live flow itself returns a distinct {status: "narrative"}
  // response instead of a normal question. Reconstructed from the
  // already-generated prompt text -- no second LLM call.
  if (session.pending_narrative_prompt !== null) {
    return NextResponse.json({ status: "narrative", prompt: session.pending_narrative_prompt });
  }

  const question = await invokeQuestionCopy(session.next_question_id);
  const label = resolveQuestionLabel(session.next_question_id, session.question_labels);

  return NextResponse.json({ question, label });
}
