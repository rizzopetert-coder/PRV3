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
// Widened beyond the 4 single names -- translateResolutionFamily()
// (web/lib/resolution-family.ts) can also produce a compound string
// (e.g. "People Tactics and Strategy + Intervention") for any state whose
// real StateProfile.resolution_family is compound, which is the common
// case (33 of 57 states). SingleResolutionFamily keeps the 4-value union
// available for call sites that only ever construct a single name.
export type SingleResolutionFamily =
  | "People Tactics and Strategy"
  | "Training & Development"
  | "Intervention"
  | "Executive Advisory";

export type ResolutionFamily = SingleResolutionFamily | (string & {});

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
export interface SignificantEventOption {
  value: string;
  label: string;
}

// Canonical significant-events vocabulary -- mirrors engine/data/intake.py's
// PRIOR_ADJUSTERS event_id/event_label pairs. Mechanism 1 (prior-probability
// scoring) was deprecated this session (Decision Register); these 10 values
// now flow through as synthesis-only narrative metadata, never a scoring
// input. Two labels lightly trimmed for checkbox-length readability
// (attitude_departure, aptitude_redesign) -- see Decision Register for the
// approved copy; the other 7 are verbatim. "other" (A1, this session) has
// no PRIOR_ADJUSTER_INDEX counterpart -- it never existed as a Mechanism-1
// event type, so engine/output_synthesis.py's format_event_for_synthesis()
// special-cases it using the free-text significant_event_elaboration field
// instead of a lookup label. Single source of truth, imported by both the
// intake UI (web/components/DiagnosticFlow.tsx) and server-side validation
// (web/app/api/diagnostic/session/start/route.ts).
export const SIGNIFICANT_EVENT_OPTIONS: readonly SignificantEventOption[] = [
  { value: "acquisition_or_merger", label: "Acquisition or merger" },
  { value: "external_legal_claim", label: "External legal claim or regulatory inquiry" },
  { value: "restructuring_or_layoff", label: "Restructuring or layoff" },
  { value: "rapid_growth", label: "Rapid growth 25%+" },
  { value: "leadership_departure", label: "Leadership departure or transition" },
  { value: "attitude_conduct", label: "A known performance or conduct issue involving a specific individual remains unresolved." },
  { value: "attitude_departure", label: "A termination or unexpected departure revealed something about how the organization operates that you're still addressing." },
  { value: "aptitude_redesign", label: "A role, team, or function was created, redesigned, or eliminated in the past 18 months." },
  { value: "other", label: "Other" },
  { value: "none", label: "None" },
];

export interface ShareableIntakeEcho {
  // string | number is TEMPORARY -- see the Priority Queue's dated
  // follow-up to collapse this to number-only once ShareableOutputPayload's
  // 30-day KV TTL has fully cycled past this deployment and no legacy
  // string-bucket records remain.
  organization_size: string | number;
  industry: string;
  role_level: string;
  tenure_in_role: string;
  direct_reports: string;
  jurisdiction: string;
  significant_events: string[];
}

// Private-only superset of ShareableIntakeEcho -- A1 (free-text "Other"
// elaboration), Gemini-cleared with a structural airgap: this field exists
// on the private type only, never on ShareableIntakeEcho, so the
// TypeScript compiler blocks it from ever reaching ShareableOutputPayload
// rather than relying on a runtime flag or a strip step. Populated only
// when "other" is among significant_events -- the diagnostic UI
// (DiagnosticFlow.tsx) requires non-empty elaboration text in that case.
export interface PrivateIntakeEcho extends ShareableIntakeEcho {
  significant_event_elaboration?: string;
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
 * in engine/friction_tax.py for the exact trigger logic. band is the
 * same qualitative value ShareableOutputPayload.legal_tail_risk_band
 * carries publicly -- present here too so the shareable-path builder
 * (web/app/api/share/create/route.ts) can read it straight off
 * engineResult.private_output without a separate computation.
 */
export interface LegalTailRiskExposure {
  low: number;
  high: number;
  currency: string;
  band: LegalTailRiskBand | null;
  caveat: string;
  has_unpriced_conditions: boolean;
}

/**
 * Qualitative severity band for legal tail-risk exposure. Computed
 * server-side in engine/friction_tax.py's _legal_exposure_band() and
 * carried through LegalTailRiskExposure.band (private output) into
 * ShareableOutputPayload.legal_tail_risk_band (shareable output) --
 * the shareable path never gets a dollar figure, only this band
 * (Addendum 11: a specific number in a shareable artifact could
 * function as documented notice of a contingent liability).
 */
export type LegalTailRiskBand = "Minor" | "Moderate" | "Elevated" | "Significant";

/**
 * Per-axis normalized asset ratio (aptitude/authority/alliance/attitude),
 * each 0.0-1.0. From engine/contract.py's dimension_summary field
 * (assemble_output() — Gemini-cleared, single normalized scalar per axis,
 * not the raw liability/asset split, per P-03). Always present — computed
 * unconditionally alongside asset_score, never optional.
 *
 * Consumed live by the live-mode ConstellationField (web/components/
 * ConstellationField.tsx), wired in web/components/PrivateOutput.tsx. This
 * comment previously said "not yet consumed, pending separate review" --
 * stale as of the Direction 1 build (Category E, this session), corrected
 * here.
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

  // Urgency Window (Diagnostic Dimension Expansion, Candidate 5). Same
  // Path 1 / Path B scoping as the three fields above -- optional, Path B
  // not wired this commit. Unlike trajectory, the object itself is never
  // null when present -- engine/contract.py's assemble_output() always
  // constructs a populated dict for both paths; only the two inner
  // values can independently be null (time_to_consequence: no lead/
  // qualified state at all; response_window: trajectory_result is None,
  // Path B only -- Path 1 always computes a real trajectory_result).
  urgency_window?: {
    time_to_consequence: "Acute" | "Medium-Term" | "Attritional" | null;
    response_window: "Extended" | "Near-Term" | "Immediate" | null;
  };

  // Intake echo — all six fields for recognition framing, plus
  // significant_event_elaboration when "other" was selected (private only).
  intake: PrivateIntakeEcho;

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

  // Legal/Compliance qualitative band (nullable) -- Addendum 11.
  // web/app/api/share/create/route.ts populates this from
  // engineResult.private_output.legal_tail_risk_exposure?.band.
  legal_tail_risk_band: LegalTailRiskBand | null;

  // Intake echo — grounds friction_tax_estimate math for external audience.
  // ShareableIntakeEcho specifically -- significant_event_elaboration (if
  // any) never reaches this payload, enforced at the type level (see
  // PrivateIntakeEcho above).
  intake: ShareableIntakeEcho;

  // Share metadata
  share_id: string;
  expires_at: string; // ISO 8601 timestamp, 30-day TTL
  created_at: string; // ISO 8601 timestamp, moment of share creation
}
