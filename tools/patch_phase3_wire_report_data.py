"""
Phase 3 (Pete, 2026-09-27): render the Pass 1 data in the full report.
Frontend only. New brand-neutral web/components/ReportDetails.tsx, placed
from PrivateOutput.tsx:

  1. ExecutiveSummary: top of the report, directly under "About this
     report" and above the constellation. Rendered only when
     synthesis.executive_summary is non-empty (today: hr-dx sessions with TC
     answers, when Calls 1 and 2 both succeeded).
  2. TacticalReview replaces the raw Q&A transcript: per section, its name,
     the referral chips (unchanged), a gap count, and synthesis_text from
     tactical_findings. The raw Q&A stays available, collapsed ("Your
     answers"), with flagged answers marked. A section with no finding
     (Call 2 failed) falls back to today's open Q&A list.
  3. EvidenceReceipts: a collapsed "How this figure was calculated" under
     the legal exposure block and inside the friction ledger, from
     driving_factors (category, rationale, triggering_answer when present).
  4. CostComparison after the ledger: inaction cost (friction + legal, as
     the engine sums it) beside the resolution service, "Ask for pricing"
     while service estimates are null. Service name: target_service_name,
     falling back to payload.resolution_family (the engine's is "" for most
     PR multi-state results), both already brand-safe.
  5. AssetStrength inside the narrative's asset subsection: the strongest
     area(s) and four relative bars (no raw scores), quotes only if
     contributing_signals has any (none yet for anyone), so it reads as a
     complete finding with zero quoted evidence.

New copy (for review): "Executive summary", "How this figure was
calculated", "Based on your answers:", "Cost comparison", "If these
conditions go unaddressed", "Estimated friction tax and legal exposure
combined.", "Ask for pricing", "Scoped to what this diagnostic found.",
"Where strength shows up", "Your answers", gap-count lines, "Minor gap",
"Significant gap or unknown".

Usage:
    python tools/patch_phase3_wire_report_data.py --dry-run
    python tools/patch_phase3_wire_report_data.py --write
"""
import argparse
import pathlib
import sys

PO = pathlib.Path('web/components/PrivateOutput.tsx')
RD = pathlib.Path('web/components/ReportDetails.tsx')

REPORT_DETAILS = '''"use client";

import type {
  AssetAxis,
  AssetEvidence,
  EvidenceReceipt,
  ServiceCostComparison,
  TacticalFinding,
  TacticalSectionResult,
} from "@/lib/types";

// Phase 3 report blocks (Pete, 2026-09-27). Brand-neutral: every brand-
// specific value (service names, referral chips) arrives as data.

function usd(value: number): string {
  return `$${Math.round(value).toLocaleString()}`;
}

function joinWords(items: string[]): string {
  if (items.length <= 1) return items.join("");
  if (items.length === 2) return `${items[0]} and ${items[1]}`;
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

export function ExecutiveSummary({ text }: { text?: string }) {
  if (!text) return null;
  return (
    <div className="pb-4">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-2">Executive summary</p>
      <p className="text-base leading-relaxed text-charcoal">{text}</p>
    </div>
  );
}

export function EvidenceReceipts({ receipts }: { receipts?: EvidenceReceipt[] }) {
  if (!receipts || receipts.length === 0) return null;
  return (
    <details className="mt-3">
      <summary className="text-[12px] text-slate cursor-pointer hover:underline">
        How this figure was calculated
      </summary>
      <ol className="mt-2 space-y-2.5 border-l border-gray-200 pl-3">
        {receipts.map((r, i) => (
          <li key={i} className="text-[12px] leading-relaxed">
            <p className="text-[10px] uppercase tracking-wide text-slate">{r.category}</p>
            <p className="text-charcoal">{r.rationale}</p>
            {r.triggering_answer && (
              <p className="text-slate">Based on your answers: {r.triggering_answer}</p>
            )}
          </li>
        ))}
      </ol>
    </details>
  );
}

export function CostComparison({
  comparison,
  fallbackServiceName,
}: {
  comparison?: ServiceCostComparison;
  fallbackServiceName: string;
}) {
  if (!comparison || comparison.inaction_cost_low === null || comparison.inaction_cost_high === null) {
    return null;
  }
  const service = comparison.target_service_name || fallbackServiceName;
  const priced =
    comparison.service_estimate_low !== null && comparison.service_estimate_high !== null;
  return (
    <div className="py-4">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-3">Cost comparison</p>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-md border border-gray-200 px-4 py-3">
          <p className="text-[11px] text-slate mb-1">If these conditions go unaddressed</p>
          <p className="text-sm font-medium text-charcoal">
            {usd(comparison.inaction_cost_low)} – {usd(comparison.inaction_cost_high)}
          </p>
          <p className="text-[11px] text-slate mt-1">
            Estimated friction tax and legal exposure combined.
          </p>
        </div>
        <div className="rounded-md border border-gray-200 px-4 py-3">
          {service && <p className="text-[11px] text-slate mb-1">{service}</p>}
          {priced ? (
            <p className="text-sm font-medium text-charcoal">
              {usd(comparison.service_estimate_low!)} – {usd(comparison.service_estimate_high!)}
            </p>
          ) : (
            <p className="text-sm font-medium text-charcoal">Ask for pricing</p>
          )}
          <p className="text-[11px] text-slate mt-1">
            {priced && comparison.pricing_model_note
              ? comparison.pricing_model_note
              : "Scoped to what this diagnostic found."}
          </p>
        </div>
      </div>
    </div>
  );
}

const AXIS_NAMES: Record<AssetAxis, string> = {
  aptitude: "Aptitude",
  authority: "Authority",
  alliance: "Alliance",
  attitude: "Attitude",
};

export function AssetStrength({ evidence }: { evidence?: AssetEvidence }) {
  if (!evidence) return null;
  const axes = Object.keys(AXIS_NAMES) as AssetAxis[];
  const max = Math.max(...axes.map((a) => evidence.net_scores[a] ?? 0));
  if (max <= 0) return null;
  const strongest = evidence.strongest_axes.map((a) => AXIS_NAMES[a]);
  return (
    <div className="mt-3">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-1.5">Where strength shows up</p>
      <p className="text-[13px] text-charcoal mb-2">
        Your answers show the most strength in {joinWords(strongest)}.
      </p>
      <ul className="space-y-1.5 max-w-sm">
        {axes.map((a) => (
          <li key={a} className="flex items-center gap-2">
            <span className="w-20 shrink-0 text-[11px] text-slate">{AXIS_NAMES[a]}</span>
            <div className="flex-1 h-1 rounded-full bg-gray-100">
              <div
                className="h-1 rounded-full"
                style={{
                  width: `${((evidence.net_scores[a] ?? 0) / max) * 100}%`,
                  backgroundColor: "var(--color-slate)",
                }}
              />
            </div>
          </li>
        ))}
      </ul>
      {evidence.contributing_signals.length > 0 && (
        <ul className="mt-2 space-y-1">
          {evidence.contributing_signals.map((s, i) => (
            <li key={i} className="text-[12px] text-charcoal leading-relaxed">
              {s.observation_text}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function AnswerList({
  section,
  flagged,
}: {
  section: TacticalSectionResult;
  flagged: Map<string, "minor" | "severe">;
}) {
  return (
    <ul className="space-y-3">
      {section.answers.map((a) => {
        const gap = flagged.get(a.question_id);
        return (
          <li key={a.question_id}>
            <p className="text-sm font-medium text-charcoal">{a.question_text}</p>
            <p className="text-sm text-slate">
              {a.selected_option_text}
              {gap && (
                <span className="ml-2 text-[10px] uppercase tracking-wide text-charcoal">
                  {gap === "severe" ? "Significant gap or unknown" : "Minor gap"}
                </span>
              )}
            </p>
          </li>
        );
      })}
    </ul>
  );
}

export function TacticalReview({
  sections,
  findings,
}: {
  sections: TacticalSectionResult[];
  findings?: TacticalFinding[];
}) {
  if (sections.length === 0) return null;
  const byId = new Map((findings ?? []).map((f) => [f.section_id, f] as const));
  return (
    <div className="mt-8 pt-8 border-t border-gray-200">
      <p className="text-[11px] uppercase tracking-wide text-slate mb-4">
        Tactical &amp; compliance review
      </p>
      <div className="space-y-6">
        {sections.map((section) => {
          const f = byId.get(section.question_set_id);
          const flagged = new Map(
            (f?.flagged_items ?? []).map((i) => [i.question_id, i.severity] as const),
          );
          return (
            <div key={section.question_set_id}>
              {f && <p className="font-display text-lg text-charcoal mb-1">{f.section_name}</p>}
              <div className="flex flex-wrap gap-2 mb-2">
                {section.referral.map((r) => (
                  <span
                    key={r}
                    className="text-[10px] uppercase tracking-wide bg-gray-100 text-charcoal rounded-full px-2 py-0.5"
                  >
                    {r}
                  </span>
                ))}
              </div>
              {f ? (
                <>
                  <p className="text-[12px] text-slate mb-1">
                    {f.flagged_count === 0
                      ? `No gaps in these ${f.total_count} answers.`
                      : `${f.flagged_count} of ${f.total_count} answers show a gap.`}
                  </p>
                  {f.synthesis_text && (
                    <p className="text-sm text-charcoal leading-relaxed mb-2">{f.synthesis_text}</p>
                  )}
                  <details>
                    <summary className="text-[12px] text-slate cursor-pointer hover:underline">
                      Your answers
                    </summary>
                    <div className="mt-2">
                      <AnswerList section={section} flagged={flagged} />
                    </div>
                  </details>
                </>
              ) : (
                <AnswerList section={section} flagged={flagged} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
'''

EDITS = [
    ('import ConditionsList, { type ConditionRow } from "@/components/ConditionsList";\n',
     'import ConditionsList, { type ConditionRow } from "@/components/ConditionsList";\n'
     'import {\n'
     '  AssetStrength,\n'
     '  CostComparison,\n'
     '  EvidenceReceipts,\n'
     '  ExecutiveSummary,\n'
     '  TacticalReview,\n'
     '} from "@/components/ReportDetails";\n',
     'imports'),
    ('      </div>\n'
     '\n'
     '      {/* Phase 2 lead (Pete, 2026-09-27): the constellation, then the\n',
     '      </div>\n'
     '\n'
     '      {/* Phase 3: executive summary opens the report when present. */}\n'
     '      <ExecutiveSummary text={payload.synthesis.executive_summary} />\n'
     '\n'
     '      {/* Phase 2 lead (Pete, 2026-09-27): the constellation, then the\n',
     'executive summary'),
    ('        {(anchorText || primaryAssetDomain) && (\n'
     '          <div>\n',
     '        {(anchorText || primaryAssetDomain || payload.asset_evidence) && (\n'
     '          <div>\n',
     'asset subsection condition'),
    ('            {anchorText && (\n'
     '              <p className="text-[13px] text-charcoal">{anchorText}</p>\n'
     '            )}\n'
     '          </div>\n'
     '        )}\n',
     '            {anchorText && (\n'
     '              <p className="text-[13px] text-charcoal">{anchorText}</p>\n'
     '            )}\n'
     '            <AssetStrength evidence={payload.asset_evidence} />\n'
     '          </div>\n'
     '        )}\n',
     'asset strength'),
    ('            {legal.caveat}\n'
     '          </p>\n'
     '        </div>\n'
     '      )}\n',
     '            {legal.caveat}\n'
     '          </p>\n'
     '          <EvidenceReceipts receipts={legal.driving_factors} />\n'
     '        </div>\n'
     '      )}\n',
     'legal receipts'),
    ('            {FRICTION_TAX_LEDGER_FOOTNOTE}\n'
     '          </p>\n'
     '        </details>\n'
     '      )}\n',
     '            {FRICTION_TAX_LEDGER_FOOTNOTE}\n'
     '          </p>\n'
     '          <EvidenceReceipts receipts={payload.friction_tax_estimate?.driving_factors} />\n'
     '        </details>\n'
     '      )}\n'
     '\n'
     '      {/* Phase 3: inaction cost beside the resolution service. */}\n'
     '      <CostComparison\n'
     '        comparison={payload.service_cost_comparison}\n'
     '        fallbackServiceName={payload.resolution_family}\n'
     '      />\n',
     'friction receipts + cost comparison'),
]

TACTICAL_START = '      {/* Block 8 -- Tactical & Compliance results (hr-dx.com only).\n'
TACTICAL_END_MARKER = '    </div>\n  );\n}\n'
TACTICAL_NEW = '''      {/* Block 8 -- Tactical & Compliance review (hr-dx.com only). Phase 3:
          per-section synthesis from tactical_findings, raw answers kept
          collapsed. Referral chips unchanged. */}
      {tacticalResults && tacticalResults.length > 0 && (
        <TacticalReview sections={tacticalResults} findings={payload.tactical_findings} />
      )}
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if RD.exists():
        print(f'ERROR: {RD} already exists.', file=sys.stderr)
        sys.exit(1)
    t = PO.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        if t.count(old) != 1:
            print(f'ERROR: {label} anchor x{t.count(old)}', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{PO} :: {label}] OK')
    if t.count(TACTICAL_START) != 1 or not t.endswith(TACTICAL_END_MARKER):
        print('ERROR: tactical block anchors not as expected.', file=sys.stderr)
        sys.exit(1)
    a = t.index(TACTICAL_START)
    b = len(t) - len(TACTICAL_END_MARKER)
    print(f'[{PO} :: tactical block] replacing {t[a:b].count(chr(10))} lines')
    t = t[:a] + TACTICAL_NEW + t[b:]
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    RD.write_text(REPORT_DETAILS, encoding='utf-8')
    PO.write_text(t, encoding='utf-8')
    print(f'WROTE: {RD} (new), {PO}')


if __name__ == '__main__':
    main()
