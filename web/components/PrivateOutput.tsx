"use client";

import type { PrivateOutputPayload } from "@/lib/types";

interface PrivateOutputProps {
  payload: PrivateOutputPayload;
}

export default function PrivateOutput({ payload }: PrivateOutputProps) {
  const allStates = [payload.primary_state, ...payload.secondary_states];

  return (
    <div>
      {/* Layer 1 — Pass 1: LLM synthesis private fields */}
      {Boolean(payload.synthesis.liability_condition_text) && (
        <div>
          <p>{payload.synthesis.liability_condition_text}</p>
        </div>
      )}
      {Boolean(payload.synthesis.asset_resolution_anchor_text) && (
        <div>
          <p>{payload.synthesis.asset_resolution_anchor_text}</p>
        </div>
      )}

      {/* Layer 2 — Pass 2: Identified state blocks (sync) */}
      <div>
        {allStates.map((state) => (
          <div key={state.id}>
            <p>{state.name}</p>
          </div>
        ))}
      </div>

      {/* Layer 2 — Severity */}
      <div>
        <p>{payload.severity}</p>
      </div>

      {/* Layer 2 — Friction tax (calibration pending — null in Path B) */}
      {payload.friction_tax_estimate !== null && (
        <div>
          <p>
            {payload.friction_tax_estimate.low} &ndash;{" "}
            {payload.friction_tax_estimate.high}{" "}
            {payload.friction_tax_estimate.currency}
          </p>
        </div>
      )}

      {/* Layer 3 — Pass 3: Resolution direction (sync) */}
      <div>
        <p>{payload.resolution_family}</p>
        <p>{payload.resolution_routing}</p>
      </div>
    </div>
  );
}
