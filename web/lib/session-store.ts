// PRV3 Path 1 — Diagnostic Session Store
// web/lib/session-store.ts
//
// Stateful backend session for the live sequential-question diagnostic
// (Path 1), stored in Upstash Redis. Locked P-03 grounds: the accumulated
// dimensional vector must never round-trip to the client — only this
// server-side layer and the Python engine ever see it.
//
// Phase 1 scope: linear Q01-Q34 core sequence only. No narrative
// modulation, no Aptitude addenda (Q35-Q39), no severity follow-ons.
// next_question_id is a string (question ID), not a positional integer —
// Phase 2's checkpoint-based dynamic assignment does not require a schema
// change. Phase 2 checkpoint fields (checkpoint_q11/19/27,
// question_sequence) are present on DiagnosticSession as of this schema
// change but not yet wired into session/answer's routing logic.
//
// Session 71 (Claude.ai) Path 1 Phase 1 handoff. Full rationale:
// prompts/path1-phase1-handoff.md.

import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import type { IntakeEcho } from "@/lib/types";
import type { SeverityInputPayload } from "@/lib/engine-client";

const redis = Redis.fromEnv();

// ---------------------------------------------------------------------------
// TTL — 6 hours, sliding (refreshed on every write, session/start and
// session/answer alike).
//
// Reasoning: no strong precedent to anchor to (ShareableOutput's 30-day TTL
// answers a different question — how long should a completed result be
// retrievable, not how long should an in-progress session survive). 6 hours
// covers a realistically distracted single sitting through 34 questions
// without leaving abandoned sessions alive indefinitely. Sliding rather than
// fixed-from-creation: same redis.set(key, val, { ex }) pattern already used
// for ShareableOutput (Redis SET with EX always resets expiry from now, so
// this is the simpler implementation, not a new Redis API surface) — and
// sliding is the better UX call here, since someone working through 34
// questions slowly shouldn't be cut off mid-flow because they started 5.9
// hours ago while the session itself has had no gap in activity.
// ---------------------------------------------------------------------------
export const SESSION_TTL_SECONDS = 6 * 60 * 60;

const SESSION_KEY_PREFIX = "diagnostic-session:";
const AGGREGATE_KEY = "diagnostic-aggregate";

function sessionKey(sessionId: string): string {
  return `${SESSION_KEY_PREFIX}${sessionId}`;
}

// ---------------------------------------------------------------------------
// Phase 1 linear question sequence — 34 positions, sequence_position 1-34
// from engine/data/questions.py, conditional pairs resolved to their "no
// significant event" branch (Q03B, Q27B) since Phase 1's intake adapter
// always sets significant_events=["none"] (Session 71 architecture
// decision — org_type and significant_events have no locked-spec intake
// equivalent, confirmed with Pete before this build). Verified against the
// live QUESTION_LIBRARY's sequence_position field, not hand-derived.
// ---------------------------------------------------------------------------
export const PHASE_1_QUESTION_SEQUENCE: readonly string[] = [
  "Q01", "Q02", "Q03B", "Q04", "Q05", "Q06", "Q07", "Q08", "Q09", "Q10",
  "Q11", "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18", "Q19", "Q20",
  "Q21", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27B", "Q28", "Q29", "Q30",
  "Q31", "Q32", "Q33", "Q34",
];

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

// Mirrors engine.data.states.DIMENSIONAL_FIELDS exactly (8 fields).
export interface AccumulatedVector {
  aptitude_liability: number;
  aptitude_asset: number;
  authority_liability: number;
  authority_asset: number;
  alliance_liability: number;
  alliance_asset: number;
  attitude_liability: number;
  attitude_asset: number;
}

export const ZERO_VECTOR: AccumulatedVector = {
  aptitude_liability: 0,
  aptitude_asset: 0,
  authority_liability: 0,
  authority_asset: 0,
  alliance_liability: 0,
  alliance_asset: 0,
  attitude_liability: 0,
  attitude_asset: 0,
};

export interface AnswerLogEntry {
  question_id: string;
  option_id: string;
}

// Mirrors engine.checkpoint.CheckpointResult. Three independent optional
// slots on DiagnosticSession below — not a nested dict — matching Python's
// SessionData pattern (confirmed against engine/contract.py lines 47-62).
export interface CheckpointResult {
  entropy: number;
  threshold: number;
  fires: boolean;
  distinguishers: string[]; // DIST-[cluster]-## IDs
  top_cluster: string | null;
}

export interface DiagnosticSession {
  session_id: string;
  intake: IntakeEcho;
  next_question_id: string;
  accumulated_vector: AccumulatedVector;
  // Append-only. Not read back in Phase 1 — required now because Phase 3
  // narrative modulation needs the full per-answer history, and adding it
  // later would be a mid-flight schema migration on live session data.
  answers_log: AnswerLogEntry[];
  status: "in_progress" | "complete";
  checkpoint_q11: CheckpointResult | null;
  checkpoint_q19: CheckpointResult | null;
  checkpoint_q27: CheckpointResult | null;
  // Live per-session routing source of truth (Phase 2). Initialized from
  // PHASE_1_QUESTION_SEQUENCE in createSession(); the static export stays
  // the canonical template and is never mutated. A checkpoint firing
  // splices distinguisher questions into this array — session/answer's
  // route logic reads from this, not from the static template, once Phase
  // 2 wiring lands.
  question_sequence: string[];
  // Severity follow-on wiring (Path 1). Append-only, one entry per
  // answered SEVER-01..13 follow-on this session -- mirrors answers_log's
  // append-only shape. Threaded into invokeComplete()'s severity_inputs
  // at Q34 so run_accumulated_engine() can call SeverityEngine.add_input()
  // for each, the first path by which severity.tier can vary from the
  // "Emerging" constant. [] (no follow-ons fired) preserves that constant
  // exactly, same as before this wiring existed.
  severity_inputs: SeverityInputPayload[];
}

// Anonymized calibration-relevant record — the only thing that survives
// past session completion. No session_id, no answers_log, no per-answer
// history: Transition Rule (Task 1) strips identifiable data at the moment
// status flips to "complete".
export interface AnonymizedCompletion {
  industry: string;
  organization_size: string;
  final_state_rankings: Array<{ id: string; name: string; weight: number }>;
  completed_at: string; // ISO 8601
}

// ---------------------------------------------------------------------------
// Pure session-sequence helpers (Phase 2)
//
// No I/O, no Redis, no mutation of inputs — extracted from
// session/answer/route.ts so they're testable in isolation. The route
// calls these directly; this is not a parallel reimplementation the route
// could drift from.
// ---------------------------------------------------------------------------

// Returns a NEW array with distinguishers inserted immediately after
// currentIndex. Does not mutate sequence — the route is responsible for
// assigning the result back onto session.question_sequence.
export function spliceDistinguishers(
  sequence: string[],
  currentIndex: number,
  distinguishers: string[],
): string[] {
  return [
    ...sequence.slice(0, currentIndex + 1),
    ...distinguishers,
    ...sequence.slice(currentIndex + 1),
  ];
}

// True when currentIndex is the last position in sequence. "Last question"
// means end of THIS sequence as it currently stands — call after any
// same-question splice has already been applied, not before.
export function isLastQuestionInSequence(
  sequence: string[],
  currentIndex: number,
): boolean {
  return currentIndex === sequence.length - 1;
}

// The index invariant (Gemini-specified security boundary, given
// NanoID-only session ownership): the answered question_id must match the
// session's current next_question_id.
export function validateIndexInvariant(
  questionId: string,
  nextQuestionId: string,
): boolean {
  return questionId === nextQuestionId;
}

// True when a SEVER-## follow-on has already been asked this session (its
// question_id already appears in answers_log) -- prevents re-splicing the
// same follow-on twice when two different core questions share one (e.g.
// Q28 and Q31 both map to SEVER-11, per engine/data/questions.py's own
// header comment: "Q28a and Q31a share SEVER-11"). Safe against the
// sequence's own linear ordering: Q28 always precedes Q31 in
// PHASE_1_QUESTION_SEQUENCE, so SEVER-11's first splice (from Q28) is
// always answered, and therefore present in answers_log, before Q31 is
// ever reached.
export function severityFollowOnAlreadyAsked(
  answersLog: AnswerLogEntry[],
  followOnId: string,
): boolean {
  return answersLog.some((entry) => entry.question_id === followOnId);
}

// ---------------------------------------------------------------------------
// Session CRUD
// ---------------------------------------------------------------------------

export async function createSession(intake: IntakeEcho): Promise<DiagnosticSession> {
  const session: DiagnosticSession = {
    session_id: nanoid(),
    intake,
    next_question_id: PHASE_1_QUESTION_SEQUENCE[0],
    accumulated_vector: { ...ZERO_VECTOR },
    answers_log: [],
    status: "in_progress",
    checkpoint_q11: null,
    checkpoint_q19: null,
    checkpoint_q27: null,
    question_sequence: [...PHASE_1_QUESTION_SEQUENCE],
    severity_inputs: [],
  };

  await redis.set(sessionKey(session.session_id), JSON.stringify(session), {
    ex: SESSION_TTL_SECONDS,
  });

  return session;
}

export async function getSession(sessionId: string): Promise<DiagnosticSession | null> {
  const raw = await redis.get<string | DiagnosticSession>(sessionKey(sessionId));
  if (raw === null || raw === undefined) return null;
  // Upstash's client auto-parses JSON-shaped strings for some SDK versions —
  // handle both a raw string and an already-parsed object defensively.
  return typeof raw === "string" ? (JSON.parse(raw) as DiagnosticSession) : raw;
}

// Overwrites the full session record, refreshing the sliding TTL.
export async function saveSession(session: DiagnosticSession): Promise<void> {
  await redis.set(sessionKey(session.session_id), JSON.stringify(session), {
    ex: SESSION_TTL_SECONDS,
  });
}

// ---------------------------------------------------------------------------
// Transition Rule (Task 1) — fires the moment status becomes "complete".
//
// Extracts ONLY industry, organization_size, and final state rankings into
// the shared anonymized-aggregate list, then immediately hard-deletes the
// session token and its full answers_log. The identifiable per-answer
// history must not persist past session completion — this implements the
// already-locked Session 34 Option D data-retention decision, not a new
// decision.
//
// Aggregate storage: a single shared Redis list (RPUSH), not one key per
// completion — individually NanoID-keyed "anonymized" records would still
// carry a correlatable identifier even with PII stripped out. One shared
// list has no per-session key to correlate back to.
// ---------------------------------------------------------------------------
export async function completeSession(
  session: DiagnosticSession,
  finalRankings: Array<{ id: string; name: string; weight: number }>,
): Promise<void> {
  const record: AnonymizedCompletion = {
    industry: session.intake.industry,
    organization_size: session.intake.organization_size,
    final_state_rankings: finalRankings,
    completed_at: new Date().toISOString(),
  };

  await redis.rpush(AGGREGATE_KEY, JSON.stringify(record));
  await redis.del(sessionKey(session.session_id));
}
