import { NextRequest, NextResponse } from "next/server";
import {
  getCondensedSession,
  saveCondensedSession,
  deleteCondensedSession,
  condensedQuestionPosition,
  CONDENSED_QUESTION_SEQUENCE,
  CONDENSED_TOTAL_QUESTIONS,
} from "@/lib/condensed-session-store";
import {
  invokeAccumulate,
  invokeQuestionCopy,
  invokeCondensedComplete,
} from "@/lib/engine-client";
import { translateResolutionFamily } from "@/lib/resolution-family";
import type { PrivateIntakeEcho, CondensedOutputPayload } from "@/lib/types";

// ---------------------------------------------------------------------------
// Category D (free condensed diagnostic), this session -- session/answer
// equivalent for the separate condensed flow. Structurally simpler than
// the full diagnostic's answer/route.ts by design: no checkpointIdMap, no
// severity-follow-on splicing, no Q06-conditional Q28 splice -- the fixed
// 9-question sequence never branches.
//
// severity_follow_on_ids / severity_inputs on invokeAccumulate()'s response
// are read from the destructured result below but deliberately never used
// -- 5 of the 9 questions (Q01, Q05, Q12, Q14, Q26) carry real severity
// triggers with real follow-on IDs, computed statelessly by the engine
// regardless of caller. This is the explicit, documented design boundary
// confirmed sound in Gemini round 4 (Decision Register, this session):
// inert by deliberate omission, not a silent gap.
// ---------------------------------------------------------------------------

interface AnswerBody {
  session_id: string;
  question_id: string;
  option_id: string;
}

function validateBody(body: unknown): body is AnswerBody {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    typeof b.session_id === "string" &&
    typeof b.question_id === "string" &&
    typeof b.option_id === "string"
  );
}

// invokeAccumulate()'s AccumulatePayload.intake is typed PrivateIntakeEcho
// (the full diagnostic's shape) -- Category D's own CondensedIntake is
// deliberately smaller (industry-only). Rather than widen the shared
// AccumulatePayload type (risk to the full diagnostic's own call site),
// this builds a full PrivateIntakeEcho-shaped object with safe minimal
// defaults for every field but industry, same pattern already used and
// verified working in DiagnosticFixturePicker.tsx this session.
// engine/main.py::_locked_intake_to_engine_intake() defaults every
// IntakeData field via dict.get() when a key is empty/absent, confirmed
// safe by direct read.
function toPrivateIntakeEchoShape(industry: string): PrivateIntakeEcho {
  return {
    organization_size: "",
    industry,
    role_level: "",
    tenure_in_role: "",
    direct_reports: "",
    jurisdiction: "",
    significant_events: [],
  };
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!validateBody(body)) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const session = await getCondensedSession(body.session_id);
  if (!session || session.status !== "in_progress") {
    return NextResponse.json({ error: "Session not found or already completed" }, { status: 404 });
  }

  if (body.question_id !== session.next_question_id) {
    return NextResponse.json({ error: "Question mismatch" }, { status: 400 });
  }

  const intakeShape = toPrivateIntakeEchoShape(session.intake.industry);

  const { accumulated_vector } = await invokeAccumulate({
    accumulated_vector: session.accumulated_vector,
    question_id: body.question_id,
    option_ids: [body.option_id],
    intake: intakeShape,
  });

  session.accumulated_vector = accumulated_vector;
  session.answers_log.push({ question_id: body.question_id, option_id: body.option_id });

  const currentIndex = CONDENSED_QUESTION_SEQUENCE.indexOf(body.question_id);
  const nextIndex = currentIndex + 1;

  if (nextIndex < CONDENSED_QUESTION_SEQUENCE.length) {
    const nextQuestionId = CONDENSED_QUESTION_SEQUENCE[nextIndex];
    session.next_question_id = nextQuestionId;
    await saveCondensedSession(session);

    const nextQuestion = await invokeQuestionCopy(nextQuestionId);
    return NextResponse.json({
      completed: false,
      question: nextQuestion,
      position: condensedQuestionPosition(nextQuestionId),
      total: CONDENSED_TOTAL_QUESTIONS,
    });
  }

  // Last question answered -- complete the session. Transition Rule: the
  // session is deleted once its result has been returned, same as the
  // full diagnostic (session-store.ts).
  session.next_question_id = null;
  session.status = "completed";

  const engineResult = await invokeCondensedComplete({
    accumulated_vector: session.accumulated_vector,
    intake: { industry: session.intake.industry },
    answered_question_count: CONDENSED_TOTAL_QUESTIONS,
  });

  await deleteCondensedSession(session.session_id);

  if (engineResult.identified_states.length === 0) {
    return NextResponse.json({ error: "Engine returned no states" }, { status: 500 });
  }

  // Builds the clean CondensedOutputPayload contract from the raw engine
  // result, same separation of concerns as session/answer/route.ts's own
  // PrivateOutputPayload construction -- routes transform, components
  // render. lead is the top identified_states entry, same source
  // session/answer/route.ts uses for its own primary_state (identified_
  // states, not state_distribution).
  const lead = engineResult.identified_states[0];
  const result: CondensedOutputPayload = {
    primary_state: { id: lead.state_id, name: lead.state_name },
    severity: engineResult.severity.tier,
    resolution_family: translateResolutionFamily(engineResult.resolution_routing),
    headline: engineResult.synthesis?.headline ?? "",
    verdict_text: engineResult.synthesis?.liability_condition_text ?? "",
    financial_range: engineResult.condensed_financial_range,
  };

  return NextResponse.json({
    completed: true,
    result,
  });
}
