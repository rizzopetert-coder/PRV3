"use client";

import type { ReactNode } from "react";
import type { SeverityTier } from "@/lib/types";
import { severityAccentTokens } from "@/components/ConstellationField";
import { firstSentence } from "@/lib/output-text";

// Phase 2 (Pete, 2026-09-27): one list of every qualifying condition, in
// descending signal strength. Replaces the "Most prominent pattern" hero, the
// "Severity across conditions" section, and the "Co-occurring conditions"
// block. The lead condition is open by default with full detail. Every other
// condition is a collapsed card (name + one line), user-expandable. Brand-
// agnostic: any brand-specific extra (the PR book link) comes in through
// renderExtra, so nothing brand-specific is bundled here.

export interface ConditionRow {
  id: string;
  name: string;
  prose: string;
  tier: SeverityTier | null;
  // Present only when the result carries a per-state severity entry.
  severity: { tier: SeverityTier; score_0_100: number } | null;
}

// Mirrors engine/severity.py's tier bands (same values as before in
// PrivateOutput.tsx, moved here with the severity bars).
const SEVERITY_TIER_BAND: Record<SeverityTier, { min: number; max: number }> = {
  Emerging:   { min: 0,  max: 33 },
  Entrenched: { min: 33, max: 66 },
  Endemic:    { min: 66, max: 100 },
};

function tierFillPercent(tier: SeverityTier, score: number): number {
  const { min, max } = SEVERITY_TIER_BAND[tier];
  const fraction = (score - min) / (max - min);
  return Math.max(0, Math.min(1, fraction)) * 100;
}

export default function ConditionsList({
  rows,
  leadDetail,
  renderExtra,
}: {
  rows: ConditionRow[];
  // Extra text shown only in the lead condition's detail (e.g. the severity
  // anchor paragraph that used to sit in the hero).
  leadDetail?: string;
  renderExtra?: (row: ConditionRow) => ReactNode;
}) {
  if (rows.length === 0) return null;
  const anyBar = rows.some((r) => r.severity !== null);
  return (
    <div className="py-4">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-3">
        Conditions identified
      </p>
      <ul className="space-y-3">
        {rows.map((row, i) => {
          const accent = row.tier ? severityAccentTokens(row.tier) : null;
          return (
            <li key={row.id}>
              <details open={i === 0} className="group">
                <summary className="list-none cursor-pointer [&::-webkit-details-marker]:hidden">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      aria-hidden
                      className="text-[10px] text-slate inline-block transition-transform group-open:rotate-90"
                    >
                      &#9656;
                    </span>
                    <span
                      className={
                        i === 0
                          ? "font-display text-2xl font-semibold text-charcoal"
                          : "font-display text-lg text-charcoal"
                      }
                    >
                      {row.name}
                    </span>
                    {row.tier && accent && (
                      <span
                        className="text-[10px] rounded-md px-1.5 py-0.5 border"
                        style={{ borderColor: accent.stroke, color: accent.text }}
                      >
                        {row.tier}
                      </span>
                    )}
                  </div>
                  {row.prose && (
                    <p className="text-[12px] text-slate leading-relaxed mt-0.5 ml-4 group-open:hidden">
                      {firstSentence(row.prose)}
                    </p>
                  )}
                </summary>
                <div className="ml-4 mt-1.5 space-y-2">
                  {row.prose && (
                    <p className="text-[12px] text-charcoal leading-relaxed">{row.prose}</p>
                  )}
                  {row.severity && accent && (
                    <div className="h-1 rounded-full bg-gray-100">
                      <div
                        className="h-1 rounded-full"
                        style={{
                          width: `${tierFillPercent(row.severity.tier, row.severity.score_0_100)}%`,
                          backgroundColor: accent.stroke,
                        }}
                      />
                    </div>
                  )}
                  {i === 0 && leadDetail && (
                    <p className="text-[12px] text-charcoal leading-relaxed">{leadDetail}</p>
                  )}
                  {renderExtra?.(row)}
                </div>
              </details>
            </li>
          );
        })}
      </ul>
      {anyBar && (
        <p className="text-[11px] text-slate mt-3 leading-relaxed">
          A short bar at Emerging reflects a real finding, not a
          partial or uncertain one — Emerging is the floor of the
          severity scale.
        </p>
      )}
    </div>
  );
}
