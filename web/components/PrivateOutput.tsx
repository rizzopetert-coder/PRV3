"use client";

import type { PrivateOutputPayload, SeverityTier } from "@/lib/types";
import type { EnginePayload } from "@/lib/engine-client";
import ShareButton from "@/components/ShareButton";
import { ConstellationField, severityAccentTokens } from "@/components/ConstellationField";

// Tier-based LOCKED copy — mirrors engine/severity.py SEVERITY_TIER_DESCRIPTIONS.
const SEVERITY_ANCHOR: Record<SeverityTier, string> = {
  Emerging:
    "Something is wrong and you can see it. It hasn't settled into the organization yet. The consequences are coming but haven't fully arrived. This is the easiest moment to move.",
  Entrenched:
    "The condition has been here long enough that people have stopped treating it as a problem to solve. Workarounds exist. Expectations have adjusted. The organization has absorbed it without resolving it.",
  Endemic:
    "This is how the organization works now. The condition isn't something that happens inside the organization anymore. It is part of the operating environment itself. People make decisions inside it without questioning it. Resolution means changing the environment, not just addressing the condition.",
};

function Rule() {
  return (
    <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />
  );
}

interface PrivateOutputProps {
  payload: PrivateOutputPayload;
  selectedStateIds: string[];
  intake: EnginePayload["intake"];
  // Path 1 (Session 71, Phase 1): ShareButton re-invokes /api/share/create
  // with Path B's declared-diagnosis logic (equal weight, selectedStateIds
  // as the diagnosis), which would silently recompute — and corrupt — Path
  // 1's real cosine-similarity-derived weights. ShareableOutput generation
  // for Path 1 is explicitly out of scope this phase. Default true —
  // existing self-select callers are unaffected.
  enableSharing?: boolean;
}

export default function PrivateOutput({
  payload,
  selectedStateIds,
  intake,
  enableSharing = true,
}: PrivateOutputProps) {
  const liabilityText = payload.synthesis.liability_condition_text;
  const anchorText = payload.synthesis.asset_resolution_anchor_text;
  const resolutionFramingText = payload.synthesis.resolution_framing_text;
  const framingText = payload.synthesis.framing_text;
  const observableIndicators = payload.synthesis.observable_indicators ?? [];
  const primaryAssetDomain = payload.primary_asset_domain;
  const headline = payload.synthesis.headline;

  // Block 2 uses resolution_routing as fallback when liability_condition_text is empty.
  // Block 4 must not repeat it if it was already used in block 2.
  const usedRoutingInBlock2 = !liabilityText && Boolean(payload.resolution_routing);

  // Severity-conditional accent — reuses the same tested function live-mode
  // ConstellationField uses for its own rings, rather than a parallel
  // implementation. --urgency/--urgency-text only at genuine Endemic;
  // --oxide/--oxide-text at Emerging/Entrenched.
  const accent = severityAccentTokens(payload.severity);

  return (
    <div className="max-w-2xl">

      {/* Block 1 — Condition header */}
      <div className="pb-4">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Condition identified
        </p>
        <div className="flex items-center gap-2 flex-wrap mb-2">
          <span className="text-[13px] font-medium text-gray-500">
            {payload.primary_state.name}
          </span>
          <span
            className="text-[11px] rounded-md px-2 py-0.5 border"
            style={{ borderColor: accent.stroke, color: accent.text }}
          >
            {payload.severity}
          </span>
        </div>
        <p className="text-[12px] text-gray-400 leading-relaxed">
          {SEVERITY_ANCHOR[payload.severity]}
        </p>
      </div>

      {/* Block 1a — Headline (omit entirely if empty) */}
      {headline && (
        <div className="pb-4">
          <p className="text-base font-medium leading-relaxed text-charcoal">{headline}</p>
        </div>
      )}

      {/* Block 1b — Weighted dimensional shape (live mode). Placeholder
          mock weights from Stage 3's scaffolding replaced with the real
          dimension_summary field (shipped commit 9c52e7d) — confirmed
          present in this payload at runtime for both Path A and Path B,
          not just in the type. */}
      <div className="max-w-70 mx-auto pb-4">
        <ConstellationField
          mode="live"
          weights={{
            apt: payload.dimension_summary.aptitude,
            auth: payload.dimension_summary.authority,
            all: payload.dimension_summary.alliance,
            att: payload.dimension_summary.attitude,
          }}
          severityTier={payload.severity}
        />
      </div>
      <Rule />

      {/* Block 2 — Liability condition */}
      <div className="py-4">
        <p className="text-sm leading-[1.65] text-charcoal">
          {liabilityText || payload.resolution_routing}
        </p>
      </div>
      <Rule />

      {/* Block 2b — Framing text (omit entirely if empty) */}
      {framingText && (
        <>
          <div className="py-4">
            <p className="text-sm leading-[1.65] text-charcoal">{framingText}</p>
          </div>
          <Rule />
        </>
      )}

      {/* Block 2c — Observable indicators (omit entirely if empty) */}
      {observableIndicators.length > 0 && (
        <>
          <div className="py-4">
            <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
              Observable indicators
            </p>
            <ul className="space-y-1">
              {observableIndicators.map((indicator, i) => (
                <li key={i} className="flex gap-2 text-[13px] leading-[1.6] text-gray-500">
                  <span className="text-gray-300 shrink-0" aria-hidden>—</span>
                  <span>{indicator}</span>
                </li>
              ))}
            </ul>
          </div>
          <Rule />
        </>
      )}

      {/* Block 3 — Asset resolution anchor + primary asset domain (omit entirely if both empty) */}
      {(anchorText || primaryAssetDomain) && (
        <>
          <div className="py-4">
            {primaryAssetDomain && (
              <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
                Primary asset domain: {primaryAssetDomain}
              </p>
            )}
            {anchorText && (
              <p className="text-[13px] text-gray-500">{anchorText}</p>
            )}
          </div>
          <Rule />
        </>
      )}

      {/* Block 4 — Resolution pathway */}
      <div className="py-4 space-y-1">
        <p className="text-[11px] uppercase tracking-wide text-gray-400">
          Resolution pathway
        </p>
        <p className="text-[13px] font-medium text-charcoal">
          {payload.resolution_family}
        </p>
        {resolutionFramingText ? (
          <p className="text-[13px] text-gray-500">{resolutionFramingText}</p>
        ) : (
          !usedRoutingInBlock2 && payload.resolution_routing && (
            <p className="text-[13px] text-gray-500">{payload.resolution_routing}</p>
          )
        )}
      </div>

      {/* Block 4b — Secondary states acknowledgment (omit entirely if none) */}
      {payload.secondary_states.length > 0 && (
        <div className="py-4">
          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
            Also present
          </p>
          <p className="text-[13px] text-gray-500">
            {payload.secondary_states
              .map((s) => `${s.name} (${(s.weight * 100).toFixed(0)}%)`)
              .join(", ")}
          </p>
        </div>
      )}

      {/* Block 5 — ShareButton */}
      {enableSharing && (
        <div className="mt-2 w-full">
          <ShareButton selectedStateIds={selectedStateIds} intake={intake} />
        </div>
      )}

      {/* Block 6 — friction_tax_estimate: null in Path B — render nothing */}
    </div>
  );
}
