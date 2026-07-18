import type { IntakeEcho } from "@/lib/types";
import type { AccumulatedVector } from "@/lib/session-store";

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
  }>;
  output_type: "single_state" | "multi_state" | "no_signal";
  identified_states: Array<{
    state_id: string;
    state_name: string;
    score: number;
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
    friction_tax_estimate: number | null;
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
  option_id: string;
  intake: IntakeEcho;
}

export async function invokeAccumulate(
  payload: AccumulatePayload,
): Promise<AccumulatedVector> {
  const response = await engineFetch(resolveEnginePath("/api/accumulate"), payload);

  if (!response.ok) {
    throw new Error(`Accumulate invocation failed: ${response.status}`);
  }

  return response.json() as Promise<AccumulatedVector>;
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
  intake: IntakeEcho;
  answered_question_count: number;
  checkpoint_results: CheckpointResultsBundle;
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

export interface QuestionCopy {
  question_id: string;
  question_text: string;
  options: Array<{ option_id: string; option_text: string }>;
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
