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
    by_state: Array<{
      state_id: string;
      tier: "Emerging" | "Entrenched" | "Endemic";
      score_0_100: number;
    }>;
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
  // Checkpoint 2 (SeverityResult per-state redesign) -- both optional,
  // populated by the caller only when question_id is itself a SEVER-##
  // follow-on with a recorded origin (DiagnosticSession.
  // severity_follow_on_origins). Absent/undefined for every other
  // question, matching today's payload shape exactly -- pure addition,
  // not a breaking change to any existing call.
  trigger_question_id?: string;
  triggering_option_id?: string;
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
  // Checkpoint 2 -- optional, mirrors SeverityInput.triggering_option_id
  // (engine/severity.py). Required only for SEVER-03/SEVER-07's
  // per-option attribution; undefined for every other follow-on.
  triggering_option_id?: string;
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
  // Checkpoint 2 -- maps each entry in severity_follow_on_ids to the
  // option_id (within THIS call's option_ids) that produced it. Mirrors
  // accumulate_answers()'s new return key (engine/main.py). {} when
  // severity_follow_on_ids is empty. Exists so the caller never has to
  // guess origin from option_ids' length/position -- correct even if a
  // single weighted_multi_select answer (Q06-style) fires more than one
  // follow-on from different options in the same request.
  severity_follow_on_origins: Record<string, string>;
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
  // Narrative modulation (Phase 3) -- True whenever Q27 itself fires
  // (evaluate_checkpoint() already computed this internally; this
  // wire field is what surfaces it). False for Q11/Q19 always.
  narrative_trigger: boolean;
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
  // Narrative modulation (Phase 3) -- all six optional/undefined when
  // narrative never fired this session, preserving every existing
  // caller's behavior exactly. narrative_trigger_point mirrors
  // SessionData.narrative_trigger's own locked vocabulary
  // ("Q27" | "Q34" | None) -- "Q34" means the standard/end-of-
  // sequence trigger, not the literal question, matching that
  // dataclass's pre-existing contract rather than inventing a new
  // value. The remaining fields (overall_confidence/signals_count/
  // pre_narrative_rankings) are exactly what invokeNarrativeProcess()
  // returned earlier this session, round-tripped through Redis --
  // same P-03 status as accumulated_vector already crossing this
  // boundary every request.
  narrative_response?: string;
  narrative_severity_addition?: number;
  narrative_trigger_point?: "Q27" | "Q34";
  narrative_overall_confidence?: number;
  narrative_signals_count?: number;
  pre_narrative_rankings?: Array<{ state_id: string; rank: number; score: number; distance: number }>;
  // Ceiling binding fix (this session's own verification pass) -- the
  // 12pp state probability ceiling's enforced rankings, threaded
  // through to run_accumulated_engine() so it's used directly in place
  // of a fresh rank_states() call, same optional/undefined-when-absent
  // shape as pre_narrative_rankings above.
  post_narrative_rankings?: Array<{ state_id: string; rank: number; score: number; distance: number }>;
}

export async function invokeComplete(
  payload: CompletePayload,
): Promise<EngineResult> {
  const response = await engineFetch(resolveEnginePath("/api/complete"), payload);

  if (!response.ok) {
    // Root-cause pass, this session: the body (api/engine.py's HTTPException
    // detail -- e.g. the real TypeError/ValueError/KeyError message) was
    // being discarded entirely, leaving only the HTTP status code visible
    // anywhere, including Vercel's own server logs. FastAPI's default
    // HTTPException handler returns {"detail": "..."} as JSON -- parsed
    // when possible, falling back to the raw text for any other shape.
    const bodyText = await response.text();
    let detail = bodyText;
    try {
      const parsed = JSON.parse(bodyText);
      if (parsed && typeof parsed.detail === "string") {
        detail = parsed.detail;
      }
    } catch {
      // Not JSON -- bodyText as-is is still more useful than nothing.
    }
    throw new Error(`Complete invocation failed: ${response.status} -- ${detail}`);
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

// ---------------------------------------------------------------------------
// Narrative modulation (Phase 3)
// ---------------------------------------------------------------------------

export interface NarrativePromptPayload {
  accumulated_vector: AccumulatedVector;
  answered_question_count: number;
}

export interface NarrativePromptResult {
  prompt: string;
  is_fallback: boolean;
}

export async function invokeNarrativePrompt(
  payload: NarrativePromptPayload,
): Promise<NarrativePromptResult> {
  const response = await engineFetch(resolveEnginePath("/api/narrative-prompt"), payload);

  if (!response.ok) {
    throw new Error(`Narrative-prompt invocation failed: ${response.status}`);
  }

  return response.json() as Promise<NarrativePromptResult>;
}

export interface NarrativeProcessPayload {
  accumulated_vector: AccumulatedVector;
  narrative_text: string;
  answered_question_count: number;
}

// Mirrors process_narrative_response()'s return shape exactly
// (engine/main.py) -- the caller persists all five fields on the
// session and threads them into a later CompletePayload so
// assemble_output()'s narrative_modulation output block reports real
// values instead of defaults.
export interface NarrativeProcessResult {
  accumulated_vector: AccumulatedVector;
  narrative_severity_addition: number;
  narrative_overall_confidence: number;
  narrative_signals_count: number;
  pre_narrative_rankings: Array<{ state_id: string; rank: number; score: number; distance: number }>;
  // Ceiling binding fix, this session -- mirrors process_narrative_
  // response()'s new return key exactly (engine/main.py).
  post_narrative_rankings: Array<{ state_id: string; rank: number; score: number; distance: number }>;
}

export async function invokeNarrativeProcess(
  payload: NarrativeProcessPayload,
): Promise<NarrativeProcessResult> {
  const response = await engineFetch(resolveEnginePath("/api/narrative-process"), payload);

  if (!response.ok) {
    throw new Error(`Narrative-process invocation failed: ${response.status}`);
  }

  return response.json() as Promise<NarrativeProcessResult>;
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
