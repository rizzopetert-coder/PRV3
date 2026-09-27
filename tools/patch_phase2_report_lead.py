"""
Phase 2, Part A: report visual restructure (Pete, 2026-09-27, Gemini spec).
Frontend only, no engine or AI changes.

  - The "Most prominent pattern" hero (big name + severity badge) and the
    separate "Severity across conditions" section are removed and merged into
    one new element, ConditionsList.
  - New lead order in PrivateOutput: ConstellationField, then observable
    indicators, then the conditions list, then the narrative (headline,
    liability, framing, asset anchor), then everything else as before.
  - ConditionsList (new, brand-agnostic): every qualifying state in
    descending score order, from payload.all_qualified_states (Pass 1 field:
    {state_id, state_name, score, descriptive_prose}, already score-sorted by
    the engine), falling back to primary_state + secondary_states when absent
    (older payloads, self-select, dev fixtures). The lead state is open by
    default with full detail (full prose, severity bar, severity anchor
    text); every other state is a collapsed card (name + first sentence),
    user-expandable. Native <details>, the codebase's existing accordion
    pattern. Severity badge/bar only where severity_by_state has the state
    (single-mode extras have none, so they show no badge rather than a
    guessed one).
  - The former "Co-occurring conditions" block is folded in: the list now
    carries every one of those states, so keeping it would list them twice.
  - PR only: each expanded card gets a small book link via StateBookLinkPR,
    which stays code-split (dynamic import), so nothing /book-related reaches
    an hr-dx bundle. StateBookLinkPR gains an optional small-link `label`.
  - ShareableOutput (PR-only share page): same order where its payload
    allows (no constellation data there): indicators, the conditions list
    (primary + up to 2 secondaries), then headline and framing. Its small
    name + badge header is replaced.

Usage:
    python tools/patch_phase2_report_lead.py --dry-run
    python tools/patch_phase2_report_lead.py --write
"""
import argparse
import pathlib
import sys

PO = pathlib.Path('web/components/PrivateOutput.tsx')
SO = pathlib.Path('web/components/ShareableOutput.tsx')
SB = pathlib.Path('web/components/StateBookLinkPR.tsx')
CL = pathlib.Path('web/components/ConditionsList.tsx')

CONDITIONS_LIST = '''"use client";

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
'''

SB_EDITS = [
    ('export default function StateBookLinkPR({ id, name }: { id: string; name: string }) {\n'
     '  return (\n',
     'export default function StateBookLinkPR({\n'
     '  id,\n'
     '  name,\n'
     '  label,\n'
     '}: {\n'
     '  id: string;\n'
     '  name: string;\n'
     '  // Phase 2: a small secondary link (e.g. inside an expanded condition\n'
     '  // card) instead of the large name link.\n'
     '  label?: string;\n'
     '}) {\n'
     '  if (label) {\n'
     '    return (\n'
     '      <a\n'
     '        href={`/book/toc#${stateIdToSlug(id)}`}\n'
     '        aria-label={`${label}: ${name}`}\n'
     '        className="font-ui text-[12px] text-slate hover:underline"\n'
     '      >\n'
     '        {label}\n'
     '      </a>\n'
     '    );\n'
     '  }\n'
     '  return (\n',
     'label prop'),
]

PO_IMPORT = [
    ('import { firstSentence, buildCoreCluster, joinNames } from "@/lib/output-text";\n',
     'import { joinNames } from "@/lib/output-text";\n'
     'import ConditionsList, { type ConditionRow } from "@/components/ConditionsList";\n',
     'imports'),
]

PO_HELPERS_OLD = (
    '  // Severity-conditional accent — reuses the same tested function live-mode\n'
    '  // ConstellationField uses for its own rings, rather than a parallel\n'
    '  // implementation. --urgency/--urgency-text only at genuine Endemic;\n'
    '  // --oxide/--oxide-text at Emerging/Entrenched.\n'
    '  const accent = severityAccentTokens(payload.severity);\n'
    '\n'
    '  // Direction 3, this session -- see buildCoreCluster() above.\n'
    '  const { core: coreCluster, overflowCount } = buildCoreCluster(\n'
    '    payload.secondary_states,\n'
    '    payload.primary_state.weight,\n'
    '  );\n'
    '\n'
    '  // Visualize Your Data (Layer 3). severity_by_state entries carry\n'
    '  // state_id only -- both real builders derive primary_state/\n'
    '  // secondary_states from the exact same identified_states array\n'
    '  // severity_by_state comes from, so this lookup always resolves.\n'
    '  const stateNameById = new Map<string, string>([\n'
    '    [payload.primary_state.id, payload.primary_state.name],\n'
    '    ...payload.secondary_states.map((s): [string, string] => [s.id, s.name]),\n'
    '  ]);\n'
)
PO_HELPERS_NEW = (
    '  // Phase 2 conditions list: every qualifying state, descending score.\n'
    '  // all_qualified_states (Pass 1) is already score-sorted by the engine and\n'
    '  // includes every above-floor state even in single mode; older payloads,\n'
    '  // self-select, and dev fixtures fall back to primary + secondary. Severity\n'
    '  // badge/bar only where severity_by_state has the state.\n'
    '  const severityById = new Map(\n'
    '    (payload.severity_by_state ?? []).map((e) => [e.state_id, e] as const),\n'
    '  );\n'
    '  const qualifiedSource =\n'
    '    payload.all_qualified_states && payload.all_qualified_states.length > 0\n'
    '      ? payload.all_qualified_states.map((s) => ({\n'
    '          id: s.state_id, name: s.state_name, prose: s.descriptive_prose,\n'
    '        }))\n'
    '      : [payload.primary_state, ...payload.secondary_states].map((s) => ({\n'
    '          id: s.id, name: s.name, prose: s.descriptive_prose ?? "",\n'
    '        }));\n'
    '  const conditionRows: ConditionRow[] = qualifiedSource.map((s, i) => {\n'
    '    const entry = severityById.get(s.id);\n'
    '    return {\n'
    '      ...s,\n'
    '      tier: entry?.tier ?? (i === 0 ? payload.severity : null),\n'
    '      severity: entry ? { tier: entry.tier, score_0_100: entry.score_0_100 } : null,\n'
    '    };\n'
    '  });\n'
    '\n'
    '  // Names for the legal/ledger blocks below, which carry state_id only.\n'
    '  const stateNameById = new Map<string, string>([\n'
    '    [payload.primary_state.id, payload.primary_state.name],\n'
    '    ...payload.secondary_states.map((s): [string, string] => [s.id, s.name]),\n'
    '    ...conditionRows.map((r): [string, string] => [r.id, r.name]),\n'
    '  ]);\n'
)

LEAD_START = '      {/* Block 1 — Condition header. Hero typographic treatment\n'
LEAD_END = '      {/* Block 4 — Resolution pathway */}\n'
LEAD_NEW = '''      {/* Phase 2 lead (Pete, 2026-09-27): the constellation, then the
          observable indicators, open the report. The former "Most prominent
          pattern" hero and "Severity across conditions" section are merged
          into ConditionsList below. */}
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

      {observableIndicators.length > 0 && (
        <div className="pb-4">
          <p className="text-[11px] uppercase tracking-wide text-slate mb-2">
            Observable indicators
          </p>
          <ul className="space-y-1">
            {observableIndicators.map((indicator, i) => (
              <li key={i} className="flex gap-2 text-[13px] leading-[1.6] text-charcoal">
                <span className="text-gray-300 shrink-0" aria-hidden>—</span>
                <span>{indicator}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      <Rule />

      <ConditionsList
        rows={conditionRows}
        leadDetail={SEVERITY_ANCHOR[payload.severity]}
        renderExtra={
          brand === "hr_diagnostic"
            ? undefined
            : (row) => <StateBookLinkPR id={row.id} name={row.name} label="Read more in The Book" />
        }
      />
      <Rule />

      {/* Narrative: headline, liability condition, framing text, and the
          asset resolution anchor, one continuous block. */}
      <div className="py-4 space-y-4">
        {headline && (
          <p className="text-base font-medium leading-relaxed text-charcoal">{headline}</p>
        )}

        <p className="text-sm leading-[1.65] text-charcoal">
          {liabilityText || payload.resolution_routing}
        </p>

        {framingText && (
          <p className="text-sm leading-[1.65] text-charcoal">{framingText}</p>
        )}

        {(anchorText || primaryAssetDomain) && (
          <div>
            {primaryAssetDomain && (
              <p className="text-[11px] uppercase tracking-wide text-slate mb-2">
                Primary asset domain: {primaryAssetDomain}
              </p>
            )}
            {anchorText && (
              <p className="text-[13px] text-charcoal">{anchorText}</p>
            )}
          </div>
        )}
      </div>
      <Rule />

'''

CLUSTER_START = '      {/* Block 4b — Core cluster of co-occurring conditions (Direction\n'
CLUSTER_END = '      {/* Block 4d — Legal/Compliance tail-risk exposure (Addendum 11).\n'

SO_IMPORT_OLD = 'import { useBrand } from "@/components/BrandContext";\n'
SO_IMPORT_NEW = ('import { useBrand } from "@/components/BrandContext";\n'
                 'import ConditionsList from "@/components/ConditionsList";\n')
SO_START = '      {/* Blocks 2/2b — Condition identified + headline, one continuous\n'
SO_END = '      {/* Block 5 — Resolution pathway */}\n'
SO_NEW = '''      {/* Phase 2 (Pete, 2026-09-27): observable indicators lead (no
          constellation data on the shared payload), then the conditions list
          (primary + up to 2 secondaries), then headline and framing. The
          former name + severity header is merged into the list. */}
      {observableIndicators.length > 0 && (
        <div className="py-4">
          <p className="text-[11px] uppercase tracking-wide text-slate mb-2">
            Observable indicators
          </p>
          <ul className="space-y-1">
            {observableIndicators.map((indicator, i) => (
              <li key={i} className="flex gap-2 text-[13px] leading-[1.6] text-charcoal">
                <span className="text-gray-300 shrink-0" aria-hidden>—</span>
                <span>{indicator}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      <Rule />

      <ConditionsList
        rows={[payload.primary_state, ...payload.secondary_states].map((s, i) => ({
          id: s.id,
          name: s.name,
          prose: s.descriptive_prose ?? "",
          tier: i === 0 ? payload.severity : null,
          severity: null,
        }))}
      />
      <Rule />

      <div className="py-4 space-y-4">
        {payload.synthesis.headline && (
          <p className="text-base font-medium leading-relaxed text-charcoal">
            {payload.synthesis.headline}
          </p>
        )}
        <p className="text-sm leading-[1.65] text-charcoal">
          {payload.synthesis.framing_text}
        </p>
      </div>
      <Rule />

'''


def replace_span(text, start, end, new, label, keep_end=True):
    if text.count(start) != 1 or text.count(end) != 1:
        print(f'ERROR: {label}: start x{text.count(start)}, end x{text.count(end)}', file=sys.stderr)
        sys.exit(1)
    a, b = text.index(start), text.index(end)
    if b <= a:
        print(f'ERROR: {label}: end before start', file=sys.stderr)
        sys.exit(1)
    print(f'[{label}] replaced {text[a:b].count(chr(10))} lines')
    return text[:a] + new + text[b:]


def edits(text, pairs, path):
    for old, new, label in pairs:
        if text.count(old) != 1:
            print(f'ERROR: {path} :: {label} anchor x{text.count(old)}', file=sys.stderr)
            sys.exit(1)
        text = text.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if CL.exists():
        print(f'ERROR: {CL} already exists.', file=sys.stderr)
        sys.exit(1)
    po = PO.read_text(encoding='utf-8')
    po = edits(po, PO_IMPORT + [(PO_HELPERS_OLD, PO_HELPERS_NEW, 'helpers')], PO)
    po = replace_span(po, LEAD_START, LEAD_END, LEAD_NEW, 'PrivateOutput lead (hero, headline, constellation, narrative)')
    po = replace_span(po, CLUSTER_START, CLUSTER_END, '', 'PrivateOutput co-occurring + severity-across sections')
    so = SO.read_text(encoding='utf-8')
    so = edits(so, [(SO_IMPORT_OLD, SO_IMPORT_NEW, 'imports')], SO)
    so = replace_span(so, SO_START, SO_END, SO_NEW, 'ShareableOutput header + narrative')
    sb = edits(SB.read_text(encoding='utf-8'), SB_EDITS, SB)
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    CL.write_text(CONDITIONS_LIST, encoding='utf-8')
    PO.write_text(po, encoding='utf-8')
    SO.write_text(so, encoding='utf-8')
    SB.write_text(sb, encoding='utf-8')
    print(f'WROTE: {CL} (new), {PO}, {SO}, {SB}')


if __name__ == '__main__':
    main()
