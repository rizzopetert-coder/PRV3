import { NextRequest, NextResponse } from "next/server";
import {
  createCondensedSession,
  condensedQuestionPosition,
  CONDENSED_TOTAL_QUESTIONS,
  type CondensedIntake,
} from "@/lib/condensed-session-store";
import { invokeQuestionCopy } from "@/lib/engine-client";

// ---------------------------------------------------------------------------
// Category D (free condensed diagnostic), this session -- session/start
// equivalent for the separate condensed flow (web/lib/condensed-session-
// store.ts). Industry-only intake -- nothing else the 9 fixed questions'
// scoring or get_industry_wage() consumes.
// ---------------------------------------------------------------------------

function validateIntake(body: unknown): body is CondensedIntake {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return typeof b.industry === "string" && b.industry.length > 0;
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

  const session = await createCondensedSession(body);
  // Always set to CONDENSED_QUESTION_SEQUENCE[0] by createCondensedSession()
  // -- never null immediately after creation.
  const firstQuestionId = session.next_question_id as string;
  const firstQuestion = await invokeQuestionCopy(firstQuestionId);

  return NextResponse.json({
    session_id: session.session_id,
    question: firstQuestion,
    position: condensedQuestionPosition(firstQuestionId),
    total: CONDENSED_TOTAL_QUESTIONS,
  });
}
