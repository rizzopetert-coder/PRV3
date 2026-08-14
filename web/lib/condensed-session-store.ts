import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import { ZERO_VECTOR, type AccumulatedVector } from "@/lib/session-store";

// ---------------------------------------------------------------------------
// Category D (free condensed diagnostic), this session -- separate session
// infrastructure from the full diagnostic's session-store.ts, deliberately.
// checkpointIdMap (web/app/api/diagnostic/session/answer/route.ts) fires
// real checkpoint/severity-follow-on splicing keyed to literal question IDs
// regardless of what sequence they're embedded in -- reusing the full
// session store with a mode flag would risk silently invoking full-
// diagnostic calibration machinery inside a condensed flow never designed
// to carry it (Decision Register, this session).
//
// 5 of the 9 questions below carry real severity triggers (Q01/SEVER-28,
// Q05/SEVER-25, Q12/SEVER-29, Q14/SEVER-17, Q26/SEVER-08) -- /api/accumulate
// will compute and return a real severity_follow_on_id for these regardless
// of caller (stateless per-call, engine/main.py:accumulate_one_answer()).
// This file, and web/app/api/diagnostic/condensed/answer/route.ts, must
// never read that field from the response -- inert by deliberate omission,
// confirmed sound and sufficient for zero calibration risk (Gemini round 4,
// this session). Only accumulated_vector is ever consumed.
// ---------------------------------------------------------------------------

export const CONDENSED_QUESTION_SEQUENCE: readonly string[] = [
  "Q01", "Q05", "Q07", "Q12", "Q14", "Q15", "Q26", "Q47", "Q50",
];

export const CONDENSED_TOTAL_QUESTIONS = CONDENSED_QUESTION_SEQUENCE.length;

// 1 hour, sliding -- shorter than the full diagnostic's 6-hour TTL
// (session-store.ts's own SESSION_TTL_SECONDS), matching Category D's own
// <5-minute design target (prompts/category-d-condensed-diagnostic.md).
// Adjustable if a real abandonment pattern ever suggests otherwise -- no
// data behind this specific number yet, a reasonable default only.
export const CONDENSED_SESSION_TTL_SECONDS = 60 * 60;

const CONDENSED_SESSION_KEY_PREFIX = "condensed-diagnostic-session:";

const redis = Redis.fromEnv();

function condensedSessionKey(sessionId: string): string {
  return `${CONDENSED_SESSION_KEY_PREFIX}${sessionId}`;
}

export interface CondensedAnswerLogEntry {
  question_id: string;
  option_id: string;
}

// Industry-only -- nothing else the 9 selected questions' scoring or
// get_industry_wage() consumes (Decision Register, this session). Not
// PrivateIntakeEcho -- a deliberately smaller, separate shape. Threaded
// through to the engine as {"industry": ...}; _locked_intake_to_engine_
// intake() (engine/main.py) defaults every other IntakeData field via
// dict.get() when a key is absent, confirmed safe by direct read, not
// assumed.
export interface CondensedIntake {
  industry: string;
}

export interface CondensedSession {
  session_id: string;
  intake: CondensedIntake;
  // null once all 9 questions are answered -- the answer route treats
  // this as the completion signal rather than a separate status check.
  next_question_id: string | null;
  accumulated_vector: AccumulatedVector;
  answers_log: CondensedAnswerLogEntry[];
  status: "in_progress" | "completed";
}

export async function createCondensedSession(
  intake: CondensedIntake,
): Promise<CondensedSession> {
  const session: CondensedSession = {
    session_id: nanoid(),
    intake,
    next_question_id: CONDENSED_QUESTION_SEQUENCE[0],
    accumulated_vector: { ...ZERO_VECTOR },
    answers_log: [],
    status: "in_progress",
  };

  await redis.set(condensedSessionKey(session.session_id), JSON.stringify(session), {
    ex: CONDENSED_SESSION_TTL_SECONDS,
  });

  return session;
}

export async function getCondensedSession(sessionId: string): Promise<CondensedSession | null> {
  const raw = await redis.get<string | CondensedSession>(condensedSessionKey(sessionId));
  if (raw === null || raw === undefined) return null;
  return typeof raw === "string" ? (JSON.parse(raw) as CondensedSession) : raw;
}

export async function saveCondensedSession(session: CondensedSession): Promise<void> {
  await redis.set(condensedSessionKey(session.session_id), JSON.stringify(session), {
    ex: CONDENSED_SESSION_TTL_SECONDS,
  });
}

// Transition Rule, same as the full diagnostic (session-store.ts) --
// completed sessions are deleted, not retained, once their result has
// been returned to the caller.
export async function deleteCondensedSession(sessionId: string): Promise<void> {
  await redis.del(condensedSessionKey(sessionId));
}

// 1-indexed position of a condensed question, or null if not a member --
// no splice labels exist in this flow (no checkpoints, no severity
// follow-ons spliced in), so this is always exactly the fixed array
// index, unlike session-store.ts's coreQuestionPosition() which has to
// account for splices.
export function condensedQuestionPosition(questionId: string): number | null {
  const index = CONDENSED_QUESTION_SEQUENCE.indexOf(questionId);
  return index === -1 ? null : index + 1;
}
