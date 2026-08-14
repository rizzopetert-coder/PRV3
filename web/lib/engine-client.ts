import type { PrivateIntakeEcho, FrictionTaxEstimate, LegalTailRiskExposure } from "@/lib/types";
import type { AccumulatedVector, AnswerLogEntry } from "@/lib/session-store";

const ENGINE_SECRET = process.env.ENGINE_SECRET ?? "";

// Deployment Protection (Vercel's SSO gate on Preview/branch deployments)
// applies to every serverless function in a protected deployment, including
// function-to-function calls over the public URL -- the Next.js function
// and api/engine.py's Python function are genuinely separate services, not
// an in-process call, so a call from one to the other is subject to the
// same gate an external request would hit. VERCEL_AUTOMATION_BYPASS_SECRET
// is Vercel's own mechanism for this exact case (Project Settings ->
// Deployment Protection -> "Protection Bypass for Automation", added as a
// System Environment Variable so it's available to server-side code).
// Server-side only -- never NEXT_PUBLIC_-prefixed, never reaches the
// browser bundle. Absent in Production today (no Deployment Protection
// there), so this is a harmless no-op there and only activates the header
// when the env var is actually set. Discovered and fixed Session 71 while
// testing Path 1 against a protected Preview deployment; applies equally
// to Path B's invokeEngine() below, which had the identical unprotected
// gap -- would have failed the same way if Deployment Protection were ever
// enabled on Production.
const VERCEL_PROTECTION_BYPASS = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;

function engineHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "x-engine-secret": ENGINE_SECRET,
  };
  if (VERCEL_PROTECTION_BYPASS) {
    headers["x-vercel-protection-bypass"] = VERCEL_PROTECTION_BYPASS;
  }
  return headers;
}

async function engineFetch(url: string, body: unknown): Promise<Response> {
  return fetch(url, {
    method: "POST",
    headers: engineHeaders(),
    body: JSON.stringify(body),
  });
}

function resolveEngineUrl(): string {
  if (process.env.ENGINE_URL) {
    return process.env.ENGINE_URL;
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}/api/engine`;
  }
  return "http://localhost:3000/api/engine";
}

// Path 1 (Session 71, Phase 1) endpoints — same api/engine.py FastAPI app,
// different routes. ENGINE_URL is intentionally NOT consulted here: its
// existing contract (set above) is a full override scoped to /api/engine
// specifically. Extending its meaning to a base-URL-plus-path convention
// for these new endpoints would be a silent contract change to a
// production env var — a deliberate follow-up decision if ever wanted,
// not assumed here. VERCEL_URL / localhost fallback logic is duplicated
// (not extracted into resolveEngineUrl) for the same reason: it keeps
// the existing /api/engine caller's behavior untouched.
function resolveEnginePath(path: string): string {
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}${path}`;
  }
  return `http://localhost:3000${path}`;
}

export interface EnginePayload {
  selectedStateIds: string[];
  intake: {
    headcount: string;
    industry: string;
    orgType: string;
    jurisdictions: string[];
    significantEvents: string[];
    principalRole: string;
  };
}

export interface EngineResult {
  session_id: string;
  intake: Record<string, unknown>;
  state_distribution: Array<{
    state_id: string;
    state_name: string;
    score: number;
    rank: number;
    above_floor: boolean;
    descriptive_prose: string;
  }>;
  output_type: "single_state" | "multi_state" | "no_signal";
  identified_states: Array<{
    state_id: string;
    state_name: string;
    score: number;
    descriptive_prose: string;
    distinguishing_language: string | null;
  }>;
  severity: {
    tier: "Emerging" | "Entrenched" | "Endemic";
    score: number;
    anchor_text: string;
    inputs: Record<string, unknown>;
  };
  asset_score: {
    score: number;
    primary_asset_domain: string;
    resolution_anchor_text: string;
  };
  dimension_summary: {
    aptitude: number;
    authority: number;
    alliance: number;
    attitude: number;
  };
  narrative_modulation: {
    fired: boolean;
    trigger_point: string | null;
    overall_confidence: number;
    signals_extracted: number;
    state_delta: number;
    severity_delta: number;
  };
  checkpoint_log: Record<string, unknown>;
  jurisdiction_flags: Record<string, unknown>;
  private_output: {
    opening_text: string;
    resolution_routing: string;
    friction_tax_estimate: FrictionTaxEstimate | null;
    legal_tail_risk_exposure: LegalTailRiskExposure | null;
    cascade_risk: number;
    causation_pattern: {
      pattern: "single_point" | "diffuse" | "insufficient_signal";
      dispersion: number;
      qualified_state_count: number;
    };
    trajectory: {
      delta: number;
      dispersion_delta: number;
      direction: "escalating" | "stable" | "decelerating" | "insufficient_data";
      duration_band: "0_6mo" | "6_18mo" | "18mo_plus" | null;
    } | null;
    urgency_window: {
      time_to_consequence: "Acute" | "Medium-Term" | "Attritional" | null;
      response_window: "Extended" | "Near-Term" | "Immediate" | null;
    };
  };
  shareable_output: {
    attribution_text: string;
  };
  synthesis: {
    liability_condition_text:     string;
    asset_resolution_anchor_text: string;
    framing_text:                 string;
    observable_indicators:        string[];
    resolution_framing_text:      string;
    headline:                     string;
    synthesis_confidence:         number;
    is_fallback:                  boolean;
  } | null;
  engine_version: string;
  monitoring_metadata: Record<string, unknown>;
}

export async function invokeEngine(payload: EnginePayload): Promise<EngineResult> {
  const url = resolveEngineUrl();
  const response = await engineFetch(url, payload);

  if (!response.ok) {
    throw new Error(`Engine invocation failed: ${response.status}`);
  }

  return response.json() as Promise<EngineResult>;
}

// ---------------------------------------------------------------------------
// Path 1 (Session 71, Phase 1) — accumulate, complete, question-copy
// ---------------------------------------------------------------------------

export interface AccumulatePayload {
  accumulated_vector: AccumulatedVector;
  question_id: string;
  option_ids: string[];
  intake: PrivateIntakeEcho;
}

// Mirrors engine.severity.SeverityInput's constructor kwargs exactly.
// trigger_question_id/severity_follow_on_id are always present;
// duration_band/population_band/prior_failed_resolution/
// financial_indicators/named_condition are mutually optional -- each
// SEVER-01..13 option maps to exactly one of the five per
// engine/data/questions.py's _severity_input_tags, never more than one.
export interface SeverityInputPayload {
  trigger_question_id: string;
  severity_follow_on_id: string;
  duration_band?: "0_6mo" | "6_18mo" | "18mo_plus";
  population_band?: "under_10pct" | "10_30pct" | "30pct_plus";
  prior_failed_resolution?: boolean;
  financial_indicators?: boolean;
  named_condition?: boolean;
}

// Mirrors accumulate_answers()'s return shape exactly (engine/main.py) --
// A.2, this session: pluralized from accumulate_one_answer()'s single-
// option shape, since a weighted_multi_select answer (Q06) can select
// more than one severity_trigger=true option at once (confirmed real,
// not hypothetical: Q06's A -> SEVER-27 and D -> SEVER-21 are both
// severity_trigger=true).
export interface AccumulateResult {
  accumulated_vector: AccumulatedVector;
  // One entry per selected option whose answer maps to a real
  // SeverityInput field -- [] when none do, including every core
  // question that only triggers a follow-on without itself carrying one.
  severity_inputs: SeverityInputPayload[];
  // One entry per selected option carrying severity_trigger=true -- the
  // SEVER-## question_id(s) to splice into the sequence next. [] when
  // none do, including on SEVER-01..13 answers themselves (those never
  // trigger a further follow-on... except via an explicit chain, e.g.
  // SEVER-01 -> SEVER-12, which is exactly this same mechanism firing
  // again one level deeper).
  severity_follow_on_ids: string[];
}

export async function invokeAccumulate(
  payload: AccumulatePayload,
): Promise<AccumulateResult> {
  const response = await engineFetch(resolveEnginePath("/api/accumulate"), payload);

  if (!response.ok) {
    throw new Error(`Accumulate invocation failed: ${response.status}`);
  }

  return response.json() as Promise<AccumulateResult>;
}

export interface CheckpointPayload {
  checkpoint_position: "Q11" | "Q19" | "Q27";
  accumulated_vector: AccumulatedVector;
  // Session's true live answer count at the moment this checkpoint fires
  // (session.answers_log.length on the caller side) -- NOT derived from
  // checkpoint_position. rank_states()'s centroid displacement scales
  // directly off this count, and a session with an earlier checkpoint
  // splice already in its sequence will have answered more than 11/19/27
  // questions by the time a later checkpoint position is reached.
  answered_question_count: number;
  already_asked: string[];
}

export interface CheckpointResultPayload {
  entropy: number;
  threshold: number;
  fires: boolean;
  distinguishers: string[];
  top_cluster: string | null;
}

export async function invokeCheckpoint(
  payload: CheckpointPayload,
): Promise<CheckpointResultPayload> {
  const response = await engineFetch(resolveEnginePath("/api/checkpoint"), payload);

  if (!response.ok) {
    throw new Error(`Checkpoint invocation failed: ${response.status}`);
  }

  return response.json() as Promise<CheckpointResultPayload>;
}

// The three accumulated CheckpointResultPayload objects a session computed
// live during Q11/Q19/Q27, or null per slot if that checkpoint was never
// reached (a session can complete before reaching Q27, and in principle
// before Q19 or Q11 too). Lets the Python-side completion handler populate
// SessionData.checkpoint_q11/19/27 from what was already computed, rather
// than recomputing at Q34 (Stage 2/Stage 4).
export interface CheckpointResultsBundle {
  q11: CheckpointResultPayload | null;
  q19: CheckpointResultPayload | null;
  q27: CheckpointResultPayload | null;
}

export interface CompletePayload {
  accumulated_vector: AccumulatedVector;
  intake: PrivateIntakeEcho;
  answered_question_count: number;
  checkpoint_results: CheckpointResultsBundle;
  // Every SeverityInputPayload collected across the session (one per
  // answered SEVER-01..13 follow-on) -- threaded into
  // run_accumulated_engine()'s severity_inputs parameter so
  // SeverityEngine.add_input() is called for each before scoring. []
  // (never fired) preserves the original constant-"Emerging" behavior.
  severity_inputs: SeverityInputPayload[];
  // Full answer history -- threaded into run_accumulated_engine()'s
  // answers_log parameter, used server-side to build signal_map_context
  // (salience-ranked, authored observation_text only -- see
  // engine/main.py::_build_signal_map_context()). Session data only,
  // never option_id-to-weight info computed client-side -- P-03.
  answers_log: AnswerLogEntry[];
}

export async function invokeComplete(
  payload: CompletePayload,
): Promise<EngineResult> {
  const response = await engineFetch(resolveEnginePath("/api/complete"), payload);

  if (!response.ok) {
    throw new Error(`Complete invocation failed: ${response.status}`);
  }

  return response.json() as Promise<EngineResult>;
}

// format ("forced_choice" | "weighted_multi_select") -- A.2, this
// session. Drives QuestionView's rendering branch (checkbox-plus-
// continue vs. single-click-advance) in web/components/DiagnosticFlow.tsx.
export interface QuestionCopy {
  question_id: string;
  question_text: string;
  format: "forced_choice" | "weighted_multi_select";
  options: Array<{ option_id: string; option_text: string }>;
}

export interface CondensedFinancialRange {
  low: number | null;
  high: number | null;
  currency: "USD";
}

// Category D (free condensed diagnostic), this session. Deliberately a
// much smaller payload than CompletePayload above -- no checkpoint_
// results/severity_inputs/answers_log, since the condensed session never
// collects any of them by design (web/lib/condensed-session-store.ts).
// intake is industry-only (CondensedIntake), not the full
// PrivateIntakeEcho -- nothing else the 9 selected questions' scoring or
// get_industry_wage() consumes.
export interface CondensedCompletePayload {
  accumulated_vector: AccumulatedVector;
  intake: { industry: string };
  answered_question_count: number;
}

// Deliberately NOT EngineResult -- run_condensed_engine() (engine/main.py)
// does not call assemble_output(), so this does not have the full VII.1
// contract's other fields (private_output, dimension_summary,
// narrative_modulation, etc.). Matches exactly what that function
// actually returns, plus condensed_financial_range merged in by the
// /api/condensed-complete route.
export interface CondensedCompleteResult {
  identified_states: Array<{
    state_id: string;
    state_name: string;
    score: number;
    descriptive_prose: string;
  }>;
  severity: {
    tier: "Emerging" | "Entrenched" | "Endemic";
  };
  resolution_routing: string;
  synthesis: {
    liability_condition_text:     string;
    asset_resolution_anchor_text: string;
    framing_text:                 string;
    observable_indicators:        string[];
    resolution_framing_text:      string;
    headline:                     string;
    synthesis_confidence:         number;
    is_fallback:                  boolean;
  } | null;
  condensed_financial_range: CondensedFinancialRange;
}

export async function invokeCondensedComplete(
  payload: CondensedCompletePayload,
): Promise<CondensedCompleteResult> {
  const response = await engineFetch(resolveEnginePath("/api/condensed-complete"), payload);

  if (!response.ok) {
    throw new Error(`Condensed complete invocation failed: ${response.status}`);
  }

  return response.json() as Promise<CondensedCompleteResult>;
}

export async function invokeQuestionCopy(
  questionId: string,
): Promise<QuestionCopy> {
  const response = await engineFetch(resolveEnginePath("/api/question-copy"), {
    question_id: questionId,
  });

  if (!response.ok) {
    throw new Error(`Question-copy invocation failed: ${response.status}`);
  }

  return response.json() as Promise<QuestionCopy>;
}
