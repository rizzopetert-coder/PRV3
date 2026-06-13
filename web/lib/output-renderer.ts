/**
 * PRV3 Output Renderer
 * web/lib/output-renderer.ts
 *
 * Normalizes API response data for the PrivateOutput and ShareableOutput
 * component trees. No imports from engine/ — clinical boundary enforced.
 *
 * Three rendering passes:
 *   Pass 1 (Layer 1) — LLM synthesis text, async, may arrive after initial render
 *   Pass 2 (Layer 2) — Per-state condition blocks, sync
 *   Pass 3 (Layer 3) — Resolution direction block, sync
 *
 * Spec reference: PRV3 Output Layer Brief — Step 5
 */

// ---------------------------------------------------------------------------
// Shared types
// ---------------------------------------------------------------------------

export interface IdentifiedStateBlock {
  stateId: string;
  stateName: string;
  score: number;
}

export interface FrictionTax {
  low: number | null;
  high: number | null;
  currency: string;
  orgSizeLabel: string;
  severityScalar: number;
  calibrationComplete: boolean;
}

// ---------------------------------------------------------------------------
// Private output types (principal-facing only)
// ---------------------------------------------------------------------------

/** Raw shape of the /api/result response payload. */
export interface PrivateOutputPayload {
  sessionId: string;
  outputType: "single_state" | "multi_state" | "no_signal";
  identifiedStates: Array<{
    state_id: string;
    state_name: string;
    score: number;
    distinguishing_language?: string | null;
  }>;
  severity: {
    tier: string;
    score: number;
    anchor_text: string;
  };
  privateOutput: {
    opening_text: string;
    liability_block: string;
    asset_anchor_text: string;
    resolution_routing: string;
    friction_tax_estimate: {
      low: number | null;
      high: number | null;
      currency: string;
      org_size_label: string;
      severity_scalar: number;
      calibration_complete: boolean;
    } | null;
  };
  synthesis?: {
    privateSynthesis: string;
    synthesisConfidence: number;
    isFallback: boolean;
  };
}

/** Normalized private output ready for PrivateOutput.tsx. */
export interface RenderedPrivateOutput {
  sessionId: string;
  outputType: "single_state" | "multi_state" | "no_signal";

  // Layer 1 — Pass 1 (async synthesis)
  synthesis: {
    text: string;
    confidence: number;
    isFallback: boolean;
    isReady: boolean;
  };

  // Layer 2 — Pass 2 (per-state blocks, sync)
  identifiedStates: IdentifiedStateBlock[];
  severity: {
    tier: string;
    score: number;
    anchorText: string;
  };
  frictionTax: FrictionTax;

  // Layer 3 — Pass 3 (resolution direction, sync)
  resolution: {
    openingText: string;
    liabilityBlock: string;
    assetAnchorText: string;
    routingFamily: string;
  };
}

// ---------------------------------------------------------------------------
// Shareable output types (third-party safe)
// ---------------------------------------------------------------------------

/** Raw shape of the /api/share/[id] response payload. */
export interface ShareableOutputPayload {
  sessionId: string;
  shareKey: string;
  expiresAt: string;
  outputType: "single_state" | "multi_state" | "no_signal";
  identifiedStates: Array<{
    state_id: string;
    state_name: string;
    score: number;
  }>;
  severity: {
    tier: string;
    anchor_text: string;
  };
  shareableOutput: {
    framing_text: string;
    observable_indicators: string[];
    resolution_framing: string;
    attribution_text: string;
  };
  synthesis?: {
    shareableSynthesis: string;
    synthesisConfidence: number;
    isFallback: boolean;
  };
}

/** Normalized shareable output ready for ShareableOutput.tsx. */
export interface RenderedShareableOutput {
  sessionId: string;
  shareKey: string;
  expiresAt: string;
  outputType: "single_state" | "multi_state" | "no_signal";

  // Layer 1 — Pass 1 (async synthesis)
  synthesis: {
    text: string;
    confidence: number;
    isFallback: boolean;
    isReady: boolean;
  };

  // Layer 2 — Pass 2 (per-state blocks, sync)
  identifiedStates: IdentifiedStateBlock[];
  severity: {
    tier: string;
    anchorText: string;
  };
  observableIndicators: string[];
  framingText: string;

  // Layer 3 — Pass 3 (resolution direction, sync)
  resolution: {
    resolutionFraming: string;
    attributionText: string;
  };
}

// ---------------------------------------------------------------------------
// Renderers
// ---------------------------------------------------------------------------

export function renderPrivateOutput(
  payload: PrivateOutputPayload
): RenderedPrivateOutput {
  const ft = payload.privateOutput.friction_tax_estimate;

  return {
    sessionId: payload.sessionId,
    outputType: payload.outputType,

    synthesis: {
      text: payload.synthesis?.privateSynthesis ?? "",
      confidence: payload.synthesis?.synthesisConfidence ?? 0,
      isFallback: payload.synthesis?.isFallback ?? true,
      isReady: Boolean(payload.synthesis?.privateSynthesis),
    },

    identifiedStates: payload.identifiedStates.map((s) => ({
      stateId: s.state_id,
      stateName: s.state_name,
      score: s.score,
    })),

    severity: {
      tier: payload.severity.tier,
      score: payload.severity.score,
      anchorText: payload.severity.anchor_text,
    },

    frictionTax: ft
      ? {
          low: ft.low,
          high: ft.high,
          currency: ft.currency,
          orgSizeLabel: ft.org_size_label,
          severityScalar: ft.severity_scalar,
          calibrationComplete: ft.calibration_complete,
        }
      : {
          low: null,
          high: null,
          currency: "USD",
          orgSizeLabel: "",
          severityScalar: 1.0,
          calibrationComplete: false,
        },

    resolution: {
      openingText: payload.privateOutput.opening_text,
      liabilityBlock: payload.privateOutput.liability_block,
      assetAnchorText: payload.privateOutput.asset_anchor_text,
      routingFamily: payload.privateOutput.resolution_routing,
    },
  };
}

export function renderShareableOutput(
  payload: ShareableOutputPayload
): RenderedShareableOutput {
  return {
    sessionId: payload.sessionId,
    shareKey: payload.shareKey,
    expiresAt: payload.expiresAt,
    outputType: payload.outputType,

    synthesis: {
      text: payload.synthesis?.shareableSynthesis ?? "",
      confidence: payload.synthesis?.synthesisConfidence ?? 0,
      isFallback: payload.synthesis?.isFallback ?? true,
      isReady: Boolean(payload.synthesis?.shareableSynthesis),
    },

    identifiedStates: payload.identifiedStates.map((s) => ({
      stateId: s.state_id,
      stateName: s.state_name,
      score: s.score,
    })),

    severity: {
      tier: payload.severity.tier,
      anchorText: payload.severity.anchor_text,
    },

    observableIndicators: payload.shareableOutput.observable_indicators,
    framingText: payload.shareableOutput.framing_text,

    resolution: {
      resolutionFraming: payload.shareableOutput.resolution_framing,
      attributionText: payload.shareableOutput.attribution_text,
    },
  };
}
