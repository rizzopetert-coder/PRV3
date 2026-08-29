// PRV3 Path 1 — Diagnostic Session Store
// web/lib/session-store.ts
//
// Stateful backend session for the live sequential-question diagnostic
// (Path 1), stored in Upstash Redis. Locked P-03 grounds: the accumulated
// dimensional vector must never round-trip to the client — only this
// server-side layer and the Python engine ever see it.
//
// Phase 1 scope: linear core sequence (see PHASE_1_QUESTION_SEQUENCE) plus
// live splices -- Phase 2 checkpoint distinguishers, severity follow-ons,
// and Q28's Q06-conditional splice are all wired and live. Aptitude addenda
// (Q35-Q39) are wired too, as plain unconditional core questions. No
// narrative modulation.
// next_question_id is a string (question ID), not a positional integer —
// dynamic splice-based assignment does not require a schema change.
//
// Session 71 (Claude.ai) Path 1 Phase 1 handoff. Full rationale:
// prompts/path1-phase1-handoff.md.

import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import type { PrivateIntakeEcho } from "@/lib/types";
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
// Phase 1 linear question sequence — 32 positions, conditional pairs
// resolved to their "no significant event" branch (Q03B, Q27B) since
// Phase 1's intake adapter always sets significant_events=["none"]
// (Session 71 architecture decision — org_type and significant_events have
// no locked-spec intake equivalent, confirmed with Pete before this build).
// Verified against the live QUESTION_LIBRARY's sequence_position field, not
// hand-derived.
//
// Q28 and Q31 deliberately excluded (live-session investigation, this
// session): both were authored with a "fires only if Q06 A or B selected"
// condition baked directly into their own question_text (a leaked dev
// annotation, stripped separately in engine/data/questions.py) but neither
// was ever actually gated -- both fired unconditionally to every session
// regardless of Q06's answer. Q28 is now wired as a real conditional
// splice off Q06 (see the answer route) rather than a fixed position, so
// it no longer belongs in this static template. Q31's own guard ("Q06 A/B
// AND Q28 not yet asked") is mathematically unreachable under that same
// single-condition gate -- Q28 fires deterministically whenever the shared
// condition is true, so Q31's "not yet asked" clause can never be
// satisfied. Building it as live defensive logic would be correct-looking
// code that can never produce a different outcome -- the same landmine
// already avoided once this session (Trajectory, Category A). Q31 is
// PARKED: content intact in questions.py, not deleted, not spliced, not
// guarded, no firing logic of any kind. Do not build Q31 firing logic
// until a real distinguishing condition is found or authored -- not the
// current self-contradicting one.
// ---------------------------------------------------------------------------
export const PHASE_1_QUESTION_SEQUENCE: readonly string[] = [
  "Q01", "Q02", "Q03B", "Q04", "Q05", "Q06", "Q07", "Q08", "Q09", "Q10",
  "Q11", "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18", "Q19", "Q20",
  "Q21", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27B", "Q30",
  "Q32", "Q33", "Q34",
  // Aptitude addenda (Q35-Q39) -- authored Session 14, never previously
  // added to this array. Plain unconditional core questions (no
  // severity_trigger, no conditional-splice metadata in
  // engine/data/questions.py), inserted at their own authored
  // sequence_position (35-39). Already answered unconditionally by every
  // profile in tools/calibration_runner.py's _CORE_QUESTION_IDS loop --
  // this closes a live/calibration mismatch, not new uncalibrated signal.
  "Q35", "Q36", "Q37", "Q38", "Q39",
  // MC_CENTROID_39 recalibration, Step 1 core expansion (this session) --
  // Q40-Q49 close severity-tier reachability for 7 states; Q50-Q51 are
  // the_inner_circle's own two questions (58th state). Full content/
  // rationale: tools/gemini_handoff_11_states_package.md.
  "Q40", "Q41", "Q42", "Q43", "Q44", "Q46", "Q47", "Q48", "Q49",
  "Q50", "Q51",
  // A5 + Structure 3 combined recalibration (N: 44 -> 42), this session --
  // Q29 removed (literal duplicate of Q16; its severity_follow_on
  // (SEVER-12) now chains off SEVER-01 instead, same pattern as
  // SEVER-30 -> SEVER-31). Q45 converted from core to a Q44-conditional
  // splice (fires only when Q44's answer is B/C/D, mirroring Q06 -> Q28,
  // see session/answer/route.ts). Q46 deliberately untouched -- confirmed
  // no topical continuity with Q44/Q45 (different state target); its own
  // content redesign is a separate future item.
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

// option_ids widened from a single option_id -- A.2, this session (Q06
// weighted_multi_select). Every existing single-select entry now stores
// a 1-element array -- one shape, not a dual-format union.
export interface AnswerLogEntry {
  question_id: string;
  option_ids: string[];
}

// Checkpoint 2 (SeverityResult per-state redesign) -- recorded at splice
// time (session/answer/route.ts, alongside question_labels) for every
// severity follow-on question, so its own eventual answer can still
// attribute triggering_option_id correctly even though the trigger's
// answer and the follow-on's answer arrive in two separate HTTP
// requests, with the session round-tripping through Redis in between.
export interface SeverityFollowOnOrigin {
  trigger_question_id: string;
  triggering_option_id: string;
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
  // Narrative modulation (Phase 3) -- mirrors
  // CheckpointResultPayload's own field exactly (engine-client.ts).
  narrative_trigger: boolean;
}

export interface DiagnosticSession {
  session_id: string;
  intake: PrivateIntakeEcho;
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
  // Checkpoint 2 (SeverityResult per-state redesign) -- one entry per
  // severity follow-on spliced this session, keyed by the follow-on's
  // own question_id (e.g. "SEVER-03"). Populated at the same splice site
  // as question_labels below, from accumulateResult.
  // severity_follow_on_origins (engine/main.py's accumulate_answers()).
  // Consumed once, at the moment that follow-on question is itself
  // answered -- looked up and threaded into that answer's own
  // invokeAccumulate() payload. Never cleaned up after consumption, same
  // append-only convention as question_labels/answers_log below --
  // bounded by the ~19-entry real SEVER-## count, no meaningful growth
  // concern.
  severity_follow_on_origins: Record<string, SeverityFollowOnOrigin>;
  // Display labels for spliced questions only (question_id -> "[parent]
  // [letter]", e.g. "6A", "11A", "11B"). Core questions never get an
  // entry here -- their label is always derivable via
  // coreQuestionPosition(), which is why it isn't stored. Populated at
  // each splice site (checkpoint distinguishers, severity follow-ons,
  // Q28's Q06-conditional splice) in the answer route.
  question_labels: Record<string, string>;
  // Narrative modulation (Phase 3). narrative_fired guards against
  // firing twice, same role as severityFollowOnAlreadyAsked() plays
  // for SEVER-## follow-ons. pending_narrative_prompt is non-null
  // exactly when the client has been sent a narrative prompt it
  // hasn't answered yet -- session/resume reads this to reconstruct
  // the same state without a second LLM call. pending_completion is
  // true exactly when the final core question has already been
  // answered but narrative hasn't fired yet -- distinguishes "resume
  // into the next question" from "resume into completion" once the
  // narrative response arrives. The remaining fields mirror
  // NarrativeProcessResult (engine-client.ts) exactly, persisted
  // across the request boundary between /session/narrative and
  // whatever request later completes the session.
  narrative_fired: boolean;
  narrative_response: string;
  narrative_severity_addition: number;
  narrative_trigger_point: "Q27" | "Q34" | null;
  narrative_overall_confidence: number;
  narrative_signals_count: number;
  // Pure Stateful Modulation with Completion Re-ranking (this session's
  // fix, replacing pre_narrative_rankings/post_narrative_rankings) --
  // accumulated_vector exactly as it stood before narrative's
  // modulation was applied. Populated at session/narrative/route.ts
  // from invokeNarrativeProcess()'s result, threaded into
  // diagnostic-completion.ts's CompletePayload at true completion so
  // run_accumulated_engine() can re-derive the 12pp ceiling comparison
  // against the session's real final accumulated_vector, not a
  // snapshot frozen at whichever question narrative fired on.
  pre_narrative_vector: AccumulatedVector | null;
  pending_narrative_prompt: string | null;
  pending_completion: boolean;
}

// Anonymized calibration-relevant record — the only thing that survives
// past session completion. No session_id, no answers_log, no per-answer
// history: Transition Rule (Task 1) strips identifiable data at the moment
// status flips to "complete".
export interface AnonymizedCompletion {
  industry: string;
  organization_size: number;
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
// question_id already appears in answers_log). General-purpose guard
// against re-splicing the same follow-on twice from more than one parent.
// engine/data/questions.py's own header comment notes SEVER-11 was
// originally authored with two possible parents (Q28 and Q31) -- with Q31
// now parked (see PHASE_1_QUESTION_SEQUENCE's comment above) and never
// spliced, SEVER-11 can in practice only ever fire from Q28 today. Kept as
// real, general infrastructure rather than removed -- any future
// multi-parent follow-on would need exactly this check, and it costs
// nothing to leave in place for a case that isn't live today.
export function severityFollowOnAlreadyAsked(
  answersLog: AnswerLogEntry[],
  followOnId: string,
): boolean {
  return answersLog.some((entry) => entry.question_id === followOnId);
}

// ---------------------------------------------------------------------------
// Display labeling (splice-numbering fix)
//
// Two categories. Core questions (PHASE_1_QUESTION_SEQUENCE members) get a
// static "N of TOTAL" position, looked up directly by array index rather
// than tracked via an incrementing counter -- correct regardless of how
// many splices occurred earlier in the session. Replaces
// web/components/DiagnosticFlow.tsx's prior questionNumber + fixed
// TOTAL_QUESTIONS=34 pattern, which drifted past its denominator the
// moment 2+ splices occurred in one session (confirmed live: Pete's own
// session showed "Question 36/40 of 34"; the Part 1 live-verification
// round trip this session independently reproduced the same pattern,
// reaching 38 total answers against a fixed 34).
//
// Spliced questions (checkpoint distinguishers, severity follow-ons, Q28)
// get a "[parent][letter]" label instead -- parent = the triggering
// question's own core position (itself looked up the same way, not
// hardcoded), letter = firing order among any siblings spliced from the
// same parent in the same splice call.
// ---------------------------------------------------------------------------

export const TOTAL_CORE_QUESTIONS = PHASE_1_QUESTION_SEQUENCE.length;

// Returns the 1-indexed static position of a core question, or null if
// questionId isn't a member of PHASE_1_QUESTION_SEQUENCE (i.e. it's a
// spliced question -- DIST-##, SEVER-##, or Q28).
export function coreQuestionPosition(questionId: string): number | null {
  const index = PHASE_1_QUESTION_SEQUENCE.indexOf(questionId);
  return index === -1 ? null : index + 1;
}

// letterIndex is 0-based (0 -> "A", 1 -> "B", ...) -- the firing order of
// this question among any siblings spliced from the same parent in the
// same call (checkpoints can splice up to 2 at once; severity follow-ons
// and Q28 only ever splice one, so letterIndex is always 0 for those).
//
// existingLabels: the session's current question_labels map. Needed for
// ancestry-aware labeling -- when the parent is itself a spliced (non-
// core) question, coreQuestionPosition(parentQuestionId) returns null,
// and the correct label is the parent's OWN already-resolved label
// (looked up here) with this splice's letter appended, not the parent's
// raw ID string. E.g. a follow-up of "34A" becomes "34AA", not
// "SEVER-30A". Falls back to the raw parent ID only if the parent's own
// label genuinely isn't in existingLabels yet, which should not happen
// in practice -- every splice call site sets question_labels for a
// question before it can ever be answered (and thus become a parent).
export function spliceLabel(
  parentQuestionId: string,
  letterIndex: number,
  existingLabels: Record<string, string>,
): string {
  const parentPosition = coreQuestionPosition(parentQuestionId);
  const letter = String.fromCharCode(65 + letterIndex);
  const parentLabel =
    parentPosition !== null
      ? String(parentPosition)
      : existingLabels[parentQuestionId] ?? parentQuestionId;
  return `${parentLabel}${letter}`;
}

// A question's resolved display label -- exactly one of the two shapes.
// Core positions are always derivable (never stored); splice labels are
// looked up from session.question_labels, populated at splice time.
export type QuestionLabel =
  | { kind: "core"; position: number; total: number }
  | { kind: "spliced"; label: string };

export function resolveQuestionLabel(
  questionId: string,
  spliceLabels: Record<string, string>,
): QuestionLabel {
  const corePosition = coreQuestionPosition(questionId);
  if (corePosition !== null) {
    return { kind: "core", position: corePosition, total: TOTAL_CORE_QUESTIONS };
  }
  return { kind: "spliced", label: spliceLabels[questionId] ?? questionId };
}

// ---------------------------------------------------------------------------
// Session CRUD
// ---------------------------------------------------------------------------

export async function createSession(intake: PrivateIntakeEcho): Promise<DiagnosticSession> {
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
    severity_follow_on_origins: {},
    question_labels: {},
    narrative_fired: false,
    narrative_response: "",
    narrative_severity_addition: 0,
    narrative_trigger_point: null,
    narrative_overall_confidence: 0,
    narrative_signals_count: 0,
    pre_narrative_vector: null,
    pending_narrative_prompt: null,
    pending_completion: false,
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
