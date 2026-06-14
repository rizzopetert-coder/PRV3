"use client";

// Airgap enforced at component boundary (S42):
// RenderedShareableOutput never contains liability_condition_text or
// asset_resolution_anchor_text — those fields are excluded at /api/share/create
// before KV write, and are not present in ShareableSynthesisFields.

import type { RenderedShareableOutput } from "@/lib/output-renderer";

interface ShareableOutputProps {
  output: RenderedShareableOutput;
}

export default function ShareableOutput({ output }: ShareableOutputProps) {
  return (
    <div>
      {/* Layer 1 — Pass 1: framing_text (shareable synthesis, sync) */}
      {output.synthesis.isReady && (
        <div>
          <p>{output.synthesis.text}</p>
        </div>
      )}

      {/* Layer 2 — Pass 2: Observable indicators (shareable, sync) */}
      {output.observableIndicators.length > 0 && (
        <ul>
          {output.observableIndicators.map((indicator, i) => (
            <li key={i}>{indicator}</li>
          ))}
        </ul>
      )}

      {/* Layer 2 — Identified states (sync) */}
      <div>
        {output.identifiedStates.map((state) => (
          <div key={state.stateId}>
            <p>{state.stateName}</p>
          </div>
        ))}
      </div>

      {/* Layer 3 — Pass 3: Resolution direction (sync) */}
      <div>
        <p>{output.resolution.resolutionFraming}</p>
      </div>

      {/* Attribution */}
      <p>{output.resolution.attributionText}</p>
    </div>
  );
}
