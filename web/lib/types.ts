// PRV3 Output Layer — Core Type Definitions
// web/lib/types.ts
//
// Authoritative type contracts for PrivateOutputPayload and ShareableOutputPayload.
// Imported by: output-renderer.ts, /api/result, /api/share/create, /api/share/[id]
//
// Clinical boundary enforced here:
//   - ShareableOutputPayload never contains synthesis
//   - ShareableOutputPayload never names a specific service (resolution_family only)
//   - PrivateOutputPayload never written to KV
//
// Locked: S41. Gemini reviewed. MOB v4.6 governs.

// ---------------------------------------------------------------------------
// Primitives
// ---------------------------------------------------------------------------

export type SeverityTier = "Emerging" | "Entrenched" | "Endemic";

// Commercial service names. Matches ENGINE_TO_COMMERCIAL_NAME in engine/resolution_families.py.
export type ResolutionFamily =
  | "People Tactics and Strategy"
  | "Training & Development"
  | "Intervention"
  | "Executive Advisory";

// ---------------------------------------------------------------------------
// Shared interfaces
// ---------------------------------------------------------------------------

/**
 * A single organizational state in an output payload.
 * weight: normalized proportion of the diagnosis this state represents.
 * Always sums to 1.0 across primary_state + secondary_states.
 *
 * Path B (self-selection): weight = 1 / total_selected_states for all states.
 * Path A (full diagnostic): weight = score_i / sum(all_returned_scores), normalized.
 */
export interface StateRef {
  id: string;
  name: string;
  weight: number;
  descriptive_prose?: string;
}

/**
 * Intake fields echoed into both outputs.
 * Required in ShareableOutputPayload to ground friction_tax_estimate math —
 * the shareable document must state the organizational parameters under which
 * the estimate was calculated.
 */
export interface IntakeEcho {
  organization_size: string;
  industry: string;
  role_level: string;
  tenure_in_role: string;
  direct_reports: string;
  jurisdiction: string;
}

/**
 * Friction tax estimate.
 * Populated with a real computed value in both private-output paths
 * (web/app/api/result/route.ts, web/app/api/diagnostic/session/answer/route.ts
 * both read engineResult.private_output.friction_tax_estimate directly)
 * now that STATE_MULTIPLIERS is fully calibrated (Option A rescale,
 * 2026-08-03) -- no longer a "Phase 3" TODO. Still hardcoded null in the
 * shareable path (web/app/api/share/create/route.ts) -- a known,
 * separate bug (prompts/friction-tax-legal-compliance-methodology.md,
 * Addendum 11, Finding 1), not a calibration gap. Components render
 * Option B treatment when null:
 * "Economic impact estimate available after full diagnostic."
 */
export interface FrictionTaxEstimate {
  low: number;
  high: number;
  currency: string;
}

/**
 * Legal/Compliance tail-risk exposure (private output only).
 * prompts/friction-tax-legal-compliance-methodology.md, Addendum 11.
 * Non-null when either a real dollar range exists or at least one
 * identified state carries real-but-unpriced exposure
 * (has_unpriced_conditions) -- see compute_legal_compliance_exposure()
 * in engine/friction_tax.py for the exact trigger logic.
 */
export interface LegalTailRiskExposure {
  low: number;
  high: number;
  currency: string;
  caveat: string;
  has_unpriced_conditions: boolean;
}

/**
 * Qualitative severity band for legal tail-risk exposure in the
 * shareable output only -- no dollar figure exposed publicly (Addendum
 * 11: a specific number in a shareable artifact could function as
 * documented notice of a contingent liability). Deliberately a bare
 * string union rather than a {low, high, caveat}-shaped interface like
 * LegalTailRiskExposure -- the shareable path has no caveat text of its
 * own yet (Finding 1: friction_tax_estimate is still hardcoded null
 * there). Revisit this shape once Finding 1's fix builds out real
 * shareable-path caveat copy -- a bare string may no longer be enough
 * once that lands.
 */
export type LegalTailRiskBand = "Minor" | "Moderate" | "Elevated" | "Significant";

/**
 * Per-axis normalized asset ratio (aptitude/authority/alliance/attitude),
 * each 0.0-1.0. From engine/contract.py's dimension_summary field
 * (assemble_output() — Gemini-cleared, single normalized scalar per axis,
 * not the raw liability/asset split, per P-03). Always present — computed
 * unconditionally alongside asset_score, never optional.
 *
 * Not yet consumed by any component — the live-mode ConstellationField
 * (web/components/ConstellationField.tsx) that will read this is built
 * and tested against representative mock data but not wired to this real
 * field yet, pending a separate review of that wiring step.
 */
export interface DimensionSummary {
  aptitude: number;
  authority: number;
  alliance: number;
  attitude: number;
}

// ---------------------------------------------------------------------------
// Synthesis types — S42 5-field contract migration
// ---------------------------------------------------------------------------

export interface SynthesisFields {
  liability_condition_text:     string;
  asset_resolution_anchor_text: string;
  framing_text:                 string;
  observable_indicators:        string[];
  resolution_framing_text:      string;
  headline:                     string;
  synthesis_confidence:         number;
  is_fallback:                  boolean;
}

// Airgap enforced per Gemini Q1 revised (S42):
// liability_condition_text: private — principal only, never written to KV.
// asset_resolution_anchor_text: private — principal only, never written to KV.
// framing_text, observable_indicators, resolution_framing_text are KV-safe.
export type ShareableSynthesisFields = Omit<
  SynthesisFields,
  "liability_condition_text" | "asset_resolution_anchor_text"
>;

// ---------------------------------------------------------------------------
// PrivateOutputPayload
// ---------------------------------------------------------------------------
// Confrontational, felt. Stays in the session (React state only).
// NEVER written to KV. NEVER serialized to persistent storage.
// Three-layer structure: synthesis → state blocks → resolution direction.

export interface PrivateOutputPayload {
  // Layer 1 — synthesis
  // Five-field struct from Python engine (output_synthesis.py).
  // TypeScript never generates this. Lock: S39. Contract: S42.
  synthesis: SynthesisFields;

  // Layer 2 — state blocks
  // All returned states, normalized weights summing to 1.0.
  primary_state: StateRef;
  secondary_states: StateRef[];

  severity: SeverityTier;

  // Layer 3 — resolution direction
  resolution_family: ResolutionFamily;
  resolution_routing: string; // human-readable routing description

  // Economic (nullable)
  friction_tax_estimate: FrictionTaxEstimate | null;

  // Legal/Compliance tail-risk exposure (nullable) -- Addendum 11.
  legal_tail_risk_exposure: LegalTailRiskExposure | null;

  // Cross-Dimensional Cascade Risk -- Shannon-entropy liability dispersion
  // x session intensity, [0.0, 1.0]. Optional: Path 1 populates this
  // (web/app/api/diagnostic/session/answer/route.ts); Path B
  // (web/app/api/result/route.ts) does not yet -- deliberate, separate
  // decision, not an oversight.
  cascade_risk?: number;

  // SPOF vs. Diffuse Causation. Same Path 1 / Path B scoping as
  // cascade_risk above -- optional, Path B not wired this commit.
  causation_pattern?: {
    pattern: "single_point" | "diffuse" | "insufficient_signal";
    dispersion: number;
    qualified_state_count: number;
  };

  // Trajectory / Directionality. Same Path 1 / Path B scoping as the two
  // fields above -- optional, Path B not wired this commit. `| null`
  // included because the raw engine field can genuinely be null (Path B
  // calls assemble_output() without trajectory_result), passed through
  // directly from engine-client.ts with no undefined-coercion.
  trajectory?: {
    delta: number;
    dispersion_delta: number;
    direction: "escalating" | "stable" | "decelerating" | "insufficient_data";
    duration_band: "0_6mo" | "6_18mo" | "18mo_plus" | null;
  } | null;

  // Intake echo — all six fields for recognition framing
  intake: IntakeEcho;

  // Per-axis asset ratio for the live-mode ConstellationField visualization.
  dimension_summary: DimensionSummary;

  // Report Depth Initiative Tier 1: engine-computed via
  // _compute_asset_score(), already present on EngineResult.asset_score --
  // was never threaded through to this payload (no field existed here at
  // all, not just unused). Required, not optional: unlike
  // cascade_risk/causation_pattern/trajectory this is NOT Path-dependent --
  // both PrivateOutputPayload builders (answer/route.ts, result/route.ts)
  // populate it unconditionally from the same always-present EngineResult
  // field, so there is no path left where it could be missing.
  primary_asset_domain: string;
}

// ---------------------------------------------------------------------------
// ShareableOutputPayload
// ---------------------------------------------------------------------------
// Professional, credible. Travels without the user present.
// Written to KV (Upstash Redis, 30-day TTL).
// NEVER contains synthesis. NEVER names a specific service.
//
// Secondary state filtering rules (applied in /api/share/create before KV write):
//   - Include only secondary states with weight >= 0.20
//   - Maximum 2 secondary states (total max 3 states in shareable output)
// Rationale: precision over completeness for board/CFO audience.

export interface ShareableOutputPayload {
  // Layer 1 — synthesis (shareable fields only — private fields excluded at /api/share/create)
  synthesis: ShareableSynthesisFields;

  // Condition
  primary_state: StateRef;
  secondary_states: StateRef[]; // pre-filtered: weight >= 0.20, max 2

  severity: SeverityTier;

  // Resolution — family only, no service name (clinical boundary, S34)
  resolution_family: ResolutionFamily;

  // Economic (nullable — Option B rendering when null)
  friction_tax_estimate: FrictionTaxEstimate | null;

  // Legal/Compliance qualitative band (nullable, optional) -- Addendum 11.
  // Optional because web/app/api/share/create/route.ts isn't wired to
  // populate this yet (deferred alongside Finding 1's fix) -- present
  // in the type now so that wiring is a small addition later, not a
  // schema change.
  legal_tail_risk_band?: LegalTailRiskBand | null;

  // Intake echo — grounds friction_tax_estimate math for external audience
  intake: IntakeEcho;

  // Share metadata
  share_id: string;
  expires_at: string; // ISO 8601 timestamp, 30-day TTL
  created_at: string; // ISO 8601 timestamp, moment of share creation
}
