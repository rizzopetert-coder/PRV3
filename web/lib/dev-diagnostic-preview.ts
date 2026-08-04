import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import type {
  SynthesisFields,
  StateRef,
  SeverityTier,
  ResolutionFamily,
  FrictionTaxEstimate,
  LegalTailRiskExposure,
  IntakeEcho,
  DimensionSummary,
} from "@/lib/types";

// ---------------------------------------------------------------------------
// DEV / TEST ONLY -- Preview environment exclusively.
//
// tools/diagnostic_fast_forward.py (Mode 1) drives a real Path 1 session to
// completion against the live API, then hands the resulting payload here so
// Pete can view it through the same <PrivateOutput> component a real
// respondent sees, without needing a live browser session of his own.
//
// DevDiagnosticPreviewPayload is deliberately NOT PrivateOutputPayload
// (web/lib/types.ts) -- that type's own doc comment is an absolute contract
// ("NEVER written to KV. NEVER serialized to persistent storage.") that this
// file must not create an exception to, even for synthetic test data.
// This is a separate type with the same field shapes, reusing the same
// sub-types (SynthesisFields, StateRef, etc. carry no such contract
// individually) so it renders through <PrivateOutput> unchanged, but the
// top-level type and its storage are both new, isolated surface area.
//
// Never populated from a real respondent's session -- only ever from
// tools/diagnostic_fast_forward.py's synthetic, state/severity-targeted
// completions.
// ---------------------------------------------------------------------------

export interface DevDiagnosticPreviewPayload {
  synthesis: SynthesisFields;
  primary_state: StateRef;
  secondary_states: StateRef[];
  severity: SeverityTier;
  resolution_family: ResolutionFamily;
  resolution_routing: string;
  friction_tax_estimate: FrictionTaxEstimate | null;
  legal_tail_risk_exposure: LegalTailRiskExposure | null;
  intake: IntakeEcho;
  dimension_summary: DimensionSummary;
  primary_asset_domain: string;
}

const DEV_PREVIEW_TTL_SECONDS = 24 * 60 * 60; // 24h -- disposable test data, not a real result
const DEV_PREVIEW_KEY_PREFIX = "dev-diagnostic-preview:";

function devPreviewKey(id: string): string {
  return `${DEV_PREVIEW_KEY_PREFIX}${id}`;
}

// Vercel sets VERCEL_ENV to "production" | "preview" | "development"
// automatically on every deployment -- no custom env var needed. Production
// is excluded explicitly; "development" (local `next dev`, where VERCEL_ENV
// is unset) is allowed so this remains testable without a live Preview
// deploy. Both the route and the page below call this before touching Redis
// at all, so there is no Production data path under any condition.
export function isPreviewEnvironment(): boolean {
  return process.env.VERCEL_ENV !== "production";
}

export async function createDevPreview(
  payload: DevDiagnosticPreviewPayload,
): Promise<string> {
  const redis = Redis.fromEnv();
  const id = nanoid(21);
  await redis.set(devPreviewKey(id), JSON.stringify(payload), {
    ex: DEV_PREVIEW_TTL_SECONDS,
  });
  return id;
}

export async function getDevPreview(
  id: string,
): Promise<DevDiagnosticPreviewPayload | null> {
  const redis = Redis.fromEnv();
  const raw = await redis.get<string | DevDiagnosticPreviewPayload>(devPreviewKey(id));
  if (raw === null || raw === undefined) return null;
  return typeof raw === "string" ? (JSON.parse(raw) as DevDiagnosticPreviewPayload) : raw;
}
