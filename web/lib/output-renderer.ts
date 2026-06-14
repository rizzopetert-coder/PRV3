/**
 * PRV3 Output Renderer
 * web/lib/output-renderer.ts
 *
 * Normalizes PrivateOutputPayload and ShareableOutputPayload for the
 * PrivateOutput and ShareableOutput component trees. Payload type definitions
 * live in web/lib/types.ts. No imports from engine/ — clinical boundary enforced.
 *
 * Three rendering passes:
 *   Pass 1 (Layer 1) — LLM synthesis text, async, may arrive after initial render
 *   Pass 2 (Layer 2) — Per-state condition blocks, sync
 *   Pass 3 (Layer 3) — Resolution direction block, sync
 *
 * Spec reference: PRV3 Output Layer Brief — Step 5
 */

import type {
  PrivateOutputPayload,
  ShareableOutputPayload,
} from "./types";

// ---------------------------------------------------------------------------
// Renderer-internal view model types (component-facing)
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
// Private output view model (principal-facing only)
// ---------------------------------------------------------------------------

/** Normalized private output ready for PrivateOutput.tsx. */
export interface RenderedPrivateOutput {
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
// Shareable output view model (third-party safe)
// ---------------------------------------------------------------------------

/** Normalized shareable output ready for ShareableOutput.tsx. */
export interface RenderedShareableOutput {
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
  const allStates = [payload.primary_state, ...payload.secondary_states];
  const outputType: RenderedPrivateOutput["outputType"] =
    payload.secondary_states.length === 0 ? "single_state" : "multi_state";

  const ft = payload.friction_tax_estimate;

  return {
    outputType,

    synthesis: {
      text:       payload.synthesis.liability_condition_text,
      confidence: payload.synthesis.synthesis_confidence,
      isFallback: payload.synthesis.is_fallback,
      isReady:    Boolean(payload.synthesis.liability_condition_text),
    },

    identifiedStates: allStates.map((s) => ({
      stateId: s.id,
      stateName: s.name,
      score: s.weight,
    })),

    severity: {
      tier: payload.severity,
      score: 0,
      anchorText: "",
    },

    frictionTax: ft
      ? {
          low: ft.low,
          high: ft.high,
          currency: ft.currency,
          orgSizeLabel: "",
          severityScalar: 1.0,
          calibrationComplete: true,
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
      openingText:    "",
      liabilityBlock: payload.synthesis.liability_condition_text,
      assetAnchorText: payload.synthesis.asset_resolution_anchor_text,
      routingFamily:  payload.resolution_family,
    },
  };
}

export function renderShareableOutput(
  payload: ShareableOutputPayload
): RenderedShareableOutput {
  const allStates = [payload.primary_state, ...payload.secondary_states];
  const outputType: RenderedShareableOutput["outputType"] =
    payload.secondary_states.length === 0 ? "single_state" : "multi_state";

  return {
    shareKey: payload.share_id,
    expiresAt: payload.expires_at,
    outputType,

    synthesis: {
      text:       payload.synthesis.framing_text,
      confidence: payload.synthesis.synthesis_confidence,
      isFallback: payload.synthesis.is_fallback,
      isReady:    Boolean(payload.synthesis.framing_text),
    },

    identifiedStates: allStates.map((s) => ({
      stateId: s.id,
      stateName: s.name,
      score: s.weight,
    })),

    severity: {
      tier: payload.severity,
      anchorText: "",
    },

    observableIndicators: payload.synthesis.observable_indicators,
    framingText: payload.synthesis.framing_text,

    resolution: {
      resolutionFraming: payload.synthesis.resolution_framing_text,
      attributionText: "Identified using the PRV3 diagnostic instrument.",
    },
  };
}
