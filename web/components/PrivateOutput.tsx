"use client";

import type { RenderedPrivateOutput } from "@/lib/output-renderer";

interface PrivateOutputProps {
  output: RenderedPrivateOutput;
}

export default function PrivateOutput({ output }: PrivateOutputProps) {
  return (
    <div>
      {/* Layer 1 — Pass 1: LLM synthesis (async, may not be ready on first render) */}
      {output.synthesis.isReady && (
        <div>
          <p>{output.synthesis.text}</p>
        </div>
      )}

      {/* Layer 2 — Pass 2: Identified state blocks (sync) */}
      <div>
        {output.identifiedStates.map((state) => (
          <div key={state.stateId}>
            <p>{state.stateName}</p>
          </div>
        ))}
      </div>

      {/* Layer 2 — Severity */}
      <div>
        <p>{output.severity.tier}</p>
        <p>{output.severity.anchorText}</p>
      </div>

      {/* Layer 2 — Friction tax (calibration pending) */}
      {output.frictionTax.calibrationComplete && (
        <div>
          <p>
            {output.frictionTax.low} – {output.frictionTax.high}{" "}
            {output.frictionTax.currency}
          </p>
        </div>
      )}

      {/* Layer 3 — Pass 3: Resolution direction (sync) */}
      <div>
        <p>{output.resolution.openingText}</p>
        <p>{output.resolution.liabilityBlock}</p>
        <p>{output.resolution.assetAnchorText}</p>
      </div>
    </div>
  );
}
