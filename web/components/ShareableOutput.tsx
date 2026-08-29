"use client";

// Airgap enforced at component boundary (S42):
// liability_condition_text and asset_resolution_anchor_text are never present in
// ShareableOutputPayload — excluded at /api/share/create before KV write.

import type { ShareableOutputPayload } from "@/lib/types";
import { severityAccentTokens } from "@/components/ConstellationField";
import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";

function Rule() {
  return (
    <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />
  );
}

interface ShareableOutputProps {
  payload: ShareableOutputPayload;
}

export default function ShareableOutput({ payload }: ShareableOutputProps) {
  const createdDate = new Date(payload.created_at).toLocaleDateString("en-US", {
    month: "short",
    year: "numeric",
  });

  const hasIndustry = Boolean(payload.intake.industry);
  const hasOrgSize = Boolean(payload.intake.organization_size);
  // organization_size is string | number (Phase 2 soft-transition union) --
  // a precise int renders "~N employees"; a share record still carrying a
  // legacy bucket string (written before this deployment, within the 30-day
  // KV transition window) renders bare, exactly as it did before this change.
  const orgSizeDisplay =
    typeof payload.intake.organization_size === "number"
      ? `~${payload.intake.organization_size} employees`
      : payload.intake.organization_size;
  let clientIdentifier: string;
  if (hasIndustry && hasOrgSize) {
    clientIdentifier = `${payload.intake.industry} · ${orgSizeDisplay} · ${createdDate}`;
  } else if (hasIndustry) {
    clientIdentifier = `${payload.intake.industry} · ${createdDate}`;
  } else if (hasOrgSize) {
    clientIdentifier = `${orgSizeDisplay} · ${createdDate}`;
  } else {
    clientIdentifier = `Confidential · Assessed ${createdDate}`;
  }

  const observableIndicators = payload.synthesis.observable_indicators ?? [];

  // Severity-conditional accent -- reuses the same tested function
  // PrivateOutput.tsx/CondensedOutput.tsx already use, rather than a
  // parallel implementation. --color-rust only at genuine Endemic;
  // --color-slate at Emerging/Entrenched.
  const accent = severityAccentTokens(payload.severity);

  return (
    <div className="max-w-2xl">

      {/* Contextual orientation — sits above Block 1, singleton per render. */}
      <div className="mb-3">
        <ContextOrientation
          variant="inline"
          topic="output-shareable"
          {...getResultsOrientation(payload.severity, payload.resolution_family)}
        />
      </div>

      {/* Block 1 — Header bar */}
      <div className="flex items-center justify-between pb-3">
        <span className="text-[12px] font-medium text-charcoal">
          Principal Resolution
        </span>
        <span className="text-[11px] text-gray-400">{clientIdentifier}</span>
      </div>
      <Rule />

      {/* Block 2 — Condition identified */}
      <div className="py-4">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Condition identified
        </p>
        <div className="flex items-center flex-wrap gap-2">
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
      </div>
      <Rule />

      {/* Block 2b — Headline (omit entirely if empty) */}
      {payload.synthesis.headline && (
        <>
          <div className="py-4">
            <p className="text-base font-medium leading-relaxed text-charcoal">
              {payload.synthesis.headline}
            </p>
          </div>
          <Rule />
        </>
      )}

      {/* Block 3 — Framing text */}
      <div className="py-4">
        <p className="text-sm leading-[1.65] text-charcoal">
          {payload.synthesis.framing_text}
        </p>
      </div>
      <Rule />

      {/* Block 4 — Observable indicators (omit entirely if empty) */}
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

      {/* Block 5 — Resolution pathway */}
      <div className="py-4 space-y-1">
        <p className="text-[11px] uppercase tracking-wide text-gray-400">
          Resolution pathway
        </p>
        <p className="text-[13px] font-medium text-charcoal">
          {payload.resolution_family}
        </p>
        {payload.synthesis.resolution_framing_text && (
          <p className="text-[13px] text-gray-500">
            {payload.synthesis.resolution_framing_text}
          </p>
        )}
      </div>

      {/* Block 6 — Attribution */}
      <div className="mt-6 pt-4" style={{ borderTop: "0.5px solid #e5e7eb" }}>
        <p className="text-[11px] text-gray-400">
          Assessed using the PRV3 diagnostic instrument. This document was generated
          from the principal&apos;s responses and is intended for senior leadership review.
        </p>
      </div>

    </div>
  );
}
