import type { CondensedOutputPayload } from "@/lib/types";
import { formatUsdRange } from "@/lib/output-text";
import {
  AXES,
  LIVE_CENTER,
  LIVE_MAX_R,
  polarPoint,
} from "@/components/ConstellationField";
import ConditionsList from "@/components/ConditionsList";

// ---------------------------------------------------------------------------
// Category D (free condensed diagnostic) -- deliberately NOT PrivateOutput.tsx
// and NOT a mode flag on it. Separate rendering target for a separate, much
// smaller payload shape (CondensedOutputPayload, web/lib/types.ts) -- see the
// Decision Register for the architecture reasoning.
//
// Phase 2 Part B (Pete, 2026-09-27): same lead order as the full report
// (chart slot, indicators, conditions list), with the limitation shown rather
// than simulated:
//   - No data constellation (Pete's standing decision: an 8-10-question
//     dimension_summary is too thin to draw a shape honestly). The chart slot
//     holds a locked silhouette: the live chart's own neutral reference grid,
//     grey, with no shape plotted.
//   - Indicators ship fully locked (the condensed synthesis has no real
//     indicator content to partially show).
//   - The shared ConditionsList with the lead open (verdict_text as its
//     detail), headline as the lead line, and a locked count of the other
//     conditions the engine surfaced.
// ---------------------------------------------------------------------------

function LockedConstellation() {
  const axisKeys = Object.keys(AXES) as Array<keyof typeof AXES>;
  const diamond = (r: number) =>
    axisKeys
      .map((k) => {
        const p = polarPoint(1, AXES[k], LIVE_CENTER, r);
        return `${p.x},${p.y}`;
      })
      .join(" ");
  return (
    <div className="max-w-70 mx-auto pb-4">
      <svg
        className="w-full h-auto opacity-70"
        viewBox="0 0 600 600"
        role="img"
        aria-label="Locked diagnostic shape"
      >
        <g stroke="#9ca3af" strokeWidth="1" fill="none">
          <line
            x1={LIVE_CENTER.x}
            y1={LIVE_CENTER.y - LIVE_MAX_R}
            x2={LIVE_CENTER.x}
            y2={LIVE_CENTER.y + LIVE_MAX_R}
          />
          <line
            x1={LIVE_CENTER.x - LIVE_MAX_R}
            y1={LIVE_CENTER.y}
            x2={LIVE_CENTER.x + LIVE_MAX_R}
            y2={LIVE_CENTER.y}
          />
          {[0.25, 0.5, 0.75, 1].map((frac) => (
            <polygon key={frac} points={diamond(LIVE_MAX_R * frac)} strokeDasharray="4 6" />
          ))}
        </g>
      </svg>
      <p className="text-center text-[12px] text-gray-500 mt-1">
        Your organization&apos;s shape unlocks with the full diagnostic.
      </p>
    </div>
  );
}

// Above this, the count reads as noise for a 9-answer sample (real sessions
// gave either 1-5 or 10-47 additional conditions), so the locked row says
// "Several more" instead of a number. Pete-confirmed 2026-09-27.
const LOCKED_COUNT_CAP = 3;

function moreConditionsText(more: number): string | undefined {
  if (more <= 0) return undefined;
  if (more > LOCKED_COUNT_CAP) return "Several more conditions surfaced, unlock the full diagnostic";
  return `${more} more condition${more === 1 ? "" : "s"} surfaced, unlock the full diagnostic`;
}

interface CondensedOutputProps {
  payload: CondensedOutputPayload;
}

export default function CondensedOutput({ payload }: CondensedOutputProps) {
  const { low, high } = payload.financial_range;
  const hasFinancialRange = low !== null && high !== null;
  const more = payload.additional_condition_count ?? 0;

  return (
    <div className="max-w-2xl">
      <LockedConstellation />

      {/* Indicators, fully locked. Not a partial reveal -- there is no real
          per-respondent indicator content behind this (see file header). */}
      <div className="pb-4">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Observable indicators
        </p>
        <div className="rounded-md border border-dashed border-gray-300 bg-gray-50 px-4 py-4">
          <p className="text-sm text-gray-500 leading-relaxed">
            All indicators locked — unlock the full diagnostic to see what&apos;s driving this
            result.
          </p>
        </div>
      </div>

      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      <ConditionsList
        rows={[
          {
            id: payload.primary_state.id,
            name: payload.primary_state.name,
            prose: payload.verdict_text,
            tier: payload.severity,
            severity: null,
          },
        ]}
        intro={payload.headline || undefined}
        lockedRow={moreConditionsText(more)}
      />

      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      {/* Financial benchmark. Null-path: omitted with an explicit unavailable
          note, never a broken figure, when get_industry_wage() returned None
          for an unrecognized industry (Decision Register). */}
      <div className="py-4">
        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">
          Estimated cost of one departure in this pattern
        </p>
        {hasFinancialRange ? (
          <p className="text-sm text-charcoal">
            {formatUsdRange(low!, high!)}{" "}
            <span className="text-gray-400">
              (roughly 50–75% of one departing employee&apos;s estimated salary)
            </span>
          </p>
        ) : (
          <p className="text-sm text-gray-400">
            A benchmark figure isn&apos;t available for the industry provided.
          </p>
        )}
      </div>

      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      {/* Resolution family + CTA. resolution_family is sourced from the lead
          QualifiedState (engine/main.py run_condensed_engine), so it is real
          in both routing modes. */}
      <div className="py-4 space-y-3">
        <div className="space-y-1">
          <p className="text-[11px] uppercase tracking-wide text-gray-400">
            Resolution pathway
          </p>
          <p className="text-[13px] font-medium text-charcoal">{payload.resolution_family}</p>
        </div>
        <a
          href="/diagnostic"
          className="inline-block font-ui text-sm font-medium text-charcoal border border-charcoal rounded-md px-4 py-2 hover:bg-charcoal hover:text-white transition-colors"
        >
          Get your full diagnostic
        </a>
      </div>
    </div>
  );
}
