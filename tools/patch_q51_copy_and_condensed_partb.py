"""
Two items (Pete, 2026-09-27).

1. Q51 answer options in house style: A, C, D used " -- " (em-dash)
   connectives. Same convention as the TC-* pass: a colon for a
   label-then-explanation (A), commas for continuations (C, D). Meaning
   unchanged. No test pins these strings (git grep: only a generated audit
   document mentions D).

2. Phase 2 Part B: CondensedOutput parity with the full report's new lead,
   without a data constellation (Pete's standing decision: 8-10 answers are
   too thin to draw a shape honestly).
   - Locked constellation silhouette in the chart slot: the live chart's own
     neutral reference grid (axis lines + 25/50/75% guide diamonds, from the
     exported LIVE_CENTER / LIVE_MAX_R / AXES / polarPoint), grey, no shape,
     no data, plus one line saying the shape unlocks with the full diagnostic.
   - Locked indicators: unchanged.
   - The shared ConditionsList: the lead card open, verdict_text as its
     detail, the previously unused headline as the block's lead line, and one
     locked row below: "N more conditions surfaced, unlock the full
     diagnostic". ConditionsList gains two optional props (intro, lockedRow);
     the full report and share page pass neither, so they render as before.
   - N = identified_states.length - 1, computed in the condensed answer route
     from the engine result it already receives: web-only, no engine change.
     In single-state routing the engine sends only the lead, so N is 0 and
     the locked row is omitted.
   - Cost benchmark and CTA: unchanged. The old "Most prominent pattern" hero
     is removed.

Usage:
    python tools/patch_q51_copy_and_condensed_partb.py --dry-run
    python tools/patch_q51_copy_and_condensed_partb.py --write
"""
import argparse
import pathlib
import sys

QS = pathlib.Path('engine/data/questions.py')
TY = pathlib.Path('web/lib/types.ts')
RT = pathlib.Path('web/app/api/diagnostic/condensed/answer/route.ts')
CL = pathlib.Path('web/components/ConditionsList.tsx')
CO = pathlib.Path('web/components/CondensedOutput.tsx')

Q51 = [
    ("It's based on role and relevance — the right people are in the room for the right reasons.",
     "It's based on role and relevance: the right people are in the room for the right reasons."),
    ("It's a consistent, recognizable group — and being outside it means being out of the real conversations.",
     "It's a consistent, recognizable group, and being outside it means being out of the real conversations."),
    ("It's the same small group every time, regardless of who's actually closest to the issue — and everyone else has stopped expecting to be included.",
     "It's the same small group every time, regardless of who's actually closest to the issue, and everyone else has stopped expecting to be included."),
]

EDITS = {
    TY: [
        ('  verdict_text: string;\n',
         '  verdict_text: string;\n'
         '  // Phase 2 Part B: identified_states.length - 1 from the condensed\n'
         '  // engine result. 0 in single-state routing (the engine sends only\n'
         '  // the lead). Optional so older payloads still type-check.\n'
         '  additional_condition_count?: number;\n',
         'CondensedOutputPayload.additional_condition_count'),
    ],
    RT: [
        ('    verdict_text: engineResult.synthesis?.liability_condition_text ?? "",\n',
         '    verdict_text: engineResult.synthesis?.liability_condition_text ?? "",\n'
         '    additional_condition_count: Math.max(0, engineResult.identified_states.length - 1),\n',
         'route: additional_condition_count'),
    ],
    CL: [
        ('export default function ConditionsList({\n'
         '  rows,\n'
         '  leadDetail,\n'
         '  renderExtra,\n'
         '}: {\n',
         'export default function ConditionsList({\n'
         '  rows,\n'
         '  leadDetail,\n'
         '  renderExtra,\n'
         '  intro,\n'
         '  lockedRow,\n'
         '}: {\n',
         'props destructure'),
        ('  renderExtra?: (row: ConditionRow) => ReactNode;\n'
         '}) {\n',
         '  renderExtra?: (row: ConditionRow) => ReactNode;\n'
         '  // Lead line under the heading (the condensed report\'s headline).\n'
         '  intro?: string;\n'
         '  // A locked, non-expandable row after the list (the condensed report\'s\n'
         '  // "N more conditions" teaser).\n'
         '  lockedRow?: string;\n'
         '}) {\n',
         'props types'),
        ('        Conditions identified\n'
         '      </p>\n',
         '        Conditions identified\n'
         '      </p>\n'
         '      {intro && (\n'
         '        <p className="text-base font-medium leading-relaxed text-charcoal mb-3">{intro}</p>\n'
         '      )}\n',
         'intro line'),
        ('      </ul>\n'
         '      {anyBar && (\n',
         '      </ul>\n'
         '      {lockedRow && (\n'
         '        <div className="mt-3 rounded-md border border-dashed border-gray-300 bg-gray-50 px-4 py-3">\n'
         '          <p className="text-sm text-gray-500 leading-relaxed">{lockedRow}</p>\n'
         '        </div>\n'
         '      )}\n'
         '      {anyBar && (\n',
         'locked row'),
    ],
}

CONDENSED = '''import type { CondensedOutputPayload } from "@/lib/types";
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
        className="w-full h-auto opacity-60"
        viewBox="0 0 600 600"
        role="img"
        aria-label="Locked diagnostic shape"
      >
        <g stroke="#e5e7eb" strokeWidth="1" fill="none">
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

interface CondensedOutputProps {
  payload: CondensedOutputPayload;
}

export default function CondensedOutput({ payload }: CondensedOutputProps) {
  const { low, high, currency } = payload.financial_range;
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
        lockedRow={
          more > 0
            ? `${more} more condition${more === 1 ? "" : "s"} surfaced, unlock the full diagnostic`
            : undefined
        }
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
            {currency === "USD" ? "$" : ""}
            {low!.toLocaleString()} – {currency === "USD" ? "$" : ""}
            {high!.toLocaleString()}{" "}
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
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = {}
    q = QS.read_text(encoding='utf-8')
    for old, new in Q51:
        if q.count(old) != 1:
            print(f'ERROR: Q51 text found {q.count(old)} times: {old[:50]!r}', file=sys.stderr)
            sys.exit(1)
        q = q.replace(old, new, 1)
    print(f'[{QS} :: Q51 A/C/D] OK')
    out[QS] = q
    for path, edits in EDITS.items():
        t = path.read_text(encoding='utf-8')
        for old, new, label in edits:
            if t.count(old) != 1:
                print(f'ERROR: {path} :: {label} x{t.count(old)}', file=sys.stderr)
                sys.exit(1)
            t = t.replace(old, new, 1)
            print(f'[{path} :: {label}] OK')
        out[path] = t
    co = CO.read_text(encoding='utf-8')
    if 'Most prominent pattern' not in co:
        print('ERROR: CondensedOutput.tsx is not the expected pre-change version.', file=sys.stderr)
        sys.exit(1)
    out[CO] = CONDENSED
    print(f'[{CO} :: rewritten for Part B] OK')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    for p, t in out.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE: {p}')


if __name__ == '__main__':
    main()
