import { NextRequest, NextResponse } from "next/server";
import { createSession, resolveQuestionLabel } from "@/lib/session-store";
import { invokeQuestionCopy } from "@/lib/engine-client";
import { SIGNIFICANT_EVENT_OPTIONS, type PrivateIntakeEcho } from "@/lib/types";

const VALID_SIGNIFICANT_EVENTS = new Set(SIGNIFICANT_EVENT_OPTIONS.map((o) => o.value));

// ---------------------------------------------------------------------------
// Path 1 (Session 71, Phase 1) — session/start
//
// Creates a stateful Redis session and returns Q1's copy only (question
// text + option labels). No dimensional_contributions or any other scoring
// field reaches this response — P-03 boundary, enforced server-side by
// engine.main.get_question_copy(), not by omission-in-this-file alone.
// ---------------------------------------------------------------------------

function validateIntake(body: unknown): body is PrivateIntakeEcho {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  // Soft transition (locked decision) -- accepts a real int from the new
  // stepper UI or a legacy non-empty bucket string, never hard-rejects
  // an old-format submission.
  const validOrgSize =
    (typeof b.organization_size === "number" && Number.isFinite(b.organization_size)) ||
    (typeof b.organization_size === "string" && b.organization_size.length > 0);
  const validSignificantEvents =
    Array.isArray(b.significant_events) &&
    b.significant_events.length > 0 &&
    b.significant_events.every(
      (v): v is string => typeof v === "string" && VALID_SIGNIFICANT_EVENTS.has(v)
    );
  // A1 -- elaboration is optional in general, but required non-empty
  // whenever "other" is among significant_events. This is the real
  // server-side trust boundary, not the browser -- the client's own
  // isComplete gate (DiagnosticFlow.tsx) enforces the same rule, but
  // this is what actually stops a bad submission.
  const elaboration = b.significant_event_elaboration;
  const validElaboration =
    elaboration === undefined || typeof elaboration === "string";
  const otherSatisfied =
    !validSignificantEvents ||
    !(b.significant_events as unknown[]).includes("other") ||
    (typeof elaboration === "string" && elaboration.trim().length > 0);
  return (
    validOrgSize &&
    typeof b.industry === "string" &&
    typeof b.role_level === "string" &&
    typeof b.tenure_in_role === "string" &&
    typeof b.direct_reports === "string" &&
    typeof b.jurisdiction === "string" &&
    validSignificantEvents &&
    validElaboration &&
    otherSatisfied
  );
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!validateIntake(body)) {
    return NextResponse.json({ error: "Invalid intake payload" }, { status: 400 });
  }

  const session = await createSession(body);
  const firstQuestion = await invokeQuestionCopy(session.next_question_id);
  const label = resolveQuestionLabel(session.next_question_id, session.question_labels);

  return NextResponse.json({
    session_id: session.session_id,
    question: firstQuestion,
    label,
  });
}
