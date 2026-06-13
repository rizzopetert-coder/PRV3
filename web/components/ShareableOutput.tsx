"use client";

import type { RenderedShareableOutput } from "@/lib/output-renderer";

interface ShareableOutputProps {
  output: RenderedShareableOutput;
}

export default function ShareableOutput({ output }: ShareableOutputProps) {
  return (
    <div>
      {/* Layer 1 — Pass 1: LLM synthesis (async, may not be ready on first render) */}
      {output.synthesis.isReady && (
        <div>
          <p>{output.synthesis.text}</p>
        </div>
      )}

      {/* Layer 2 — Pass 2: Framing and observable indicators (sync) */}
      <div>
        <p>{output.framingText}</p>
      </div>

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
