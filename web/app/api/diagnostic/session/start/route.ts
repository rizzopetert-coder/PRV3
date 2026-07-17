import { NextRequest, NextResponse } from "next/server";
import { createSession } from "@/lib/session-store";
import { invokeQuestionCopy } from "@/lib/engine-client";
import type { IntakeEcho } from "@/lib/types";

// ---------------------------------------------------------------------------
// Path 1 (Session 71, Phase 1) — session/start
//
// Creates a stateful Redis session and returns Q1's copy only (question
// text + option labels). No dimensional_contributions or any other scoring
// field reaches this response — P-03 boundary, enforced server-side by
// engine.main.get_question_copy(), not by omission-in-this-file alone.
// ---------------------------------------------------------------------------

function validateIntake(body: unknown): body is IntakeEcho {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    typeof b.organization_size === "string" &&
    typeof b.industry === "string" &&
    typeof b.role_level === "string" &&
    typeof b.tenure_in_role === "string" &&
    typeof b.direct_reports === "string" &&
    typeof b.jurisdiction === "string"
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

  return NextResponse.json({
    session_id: session.session_id,
    question: firstQuestion,
  });
}
