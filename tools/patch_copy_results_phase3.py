"""
"Copy results" (web/lib/output-text.ts buildResultsText) includes the Phase 3
sections (Pete, 2026-09-27). Added into the existing structure (existing
content and order untouched, so the pinned output-text tests still hold):
  - Executive summary, first, when present (hr-dx only in practice).
  - Where strength shows up, after the asset anchor block: strongest area(s),
    the four net scores (this export is the comprehensive version and already
    includes numbers the screen omits), and any quoted signals.
  - After the legal block: how the legal figure was calculated (receipts),
    the friction tax with its timeframe and receipts, and the cost comparison
    in the same separated form as the screen.
  - Tactical & compliance review, when tactical_findings exist (hr-dx only):
    section, gap count, synthesis.
Shared across brands except the executive summary and tactical review, which
only ever have data on hr-dx.

Usage: python tools/patch_copy_results_phase3.py --dry-run | --write
"""
import argparse
import pathlib
import sys

OT = pathlib.Path('web/lib/output-text.ts')
TT = pathlib.Path('web/lib/output-text.test.ts')

HELPERS = '''
// Phase 3 export helpers.
function money(low: number, high: number): string {
  const f = (v: number) => `$${Math.round(v).toLocaleString()}`;
  return low === high ? f(low) : `${f(low)} – ${f(high)}`;
}

function receiptLines(title: string, receipts: EvidenceReceipt[] | undefined): string[] {
  if (!receipts || receipts.length === 0) return [];
  const out = ["", title];
  for (const r of receipts) {
    out.push(`— ${r.category}: ${r.rationale}`);
    if (r.triggering_answer) out.push(`  Based on your answers: ${r.triggering_answer}`);
  }
  return out;
}

const ASSET_AXIS_NAMES: Record<string, string> = {
  aptitude: "Aptitude",
  authority: "Authority",
  alliance: "Alliance",
  attitude: "Attitude",
};

'''

EDITS = [
    ('import type { PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";\n',
     'import type { EvidenceReceipt, PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";\n',
     'imports'),
    ('export function buildResultsText(',
     HELPERS.lstrip('\n') + 'export function buildResultsText(',
     'helpers'),
    ('  // Block 1 -- condition header.\n',
     '  // Phase 3 -- executive summary, first when present.\n'
     '  if (payload.synthesis.executive_summary) {\n'
     '    lines.push("Executive summary:", payload.synthesis.executive_summary, "");\n'
     '  }\n'
     '\n'
     '  // Block 1 -- condition header.\n',
     'executive summary'),
    ('  // Block 4 -- resolution pathway.\n',
     '  // Phase 3 -- where strength shows up (net asset scores).\n'
     '  const ev = payload.asset_evidence;\n'
     '  if (ev) {\n'
     '    const strongest = ev.strongest_axes.map((a) => ASSET_AXIS_NAMES[a] ?? a);\n'
     '    const scores = Object.keys(ASSET_AXIS_NAMES)\n'
     '      .map((a) => `${ASSET_AXIS_NAMES[a]} ${ev.net_scores[a as keyof typeof ev.net_scores] ?? 0}`)\n'
     '      .join(" | ");\n'
     '    lines.push("", `Where strength shows up: ${joinNames(strongest)} (net asset signal: ${scores})`);\n'
     '    for (const s of ev.contributing_signals) {\n'
     '      lines.push(`— ${s.observation_text}`);\n'
     '    }\n'
     '  }\n'
     '\n'
     '  // Block 4 -- resolution pathway.\n',
     'asset strength'),
    ('  // ── Section 2 -- additional diagnostic detail (never shown on screen) ──\n',
     '  // Phase 3 -- show-your-work receipts and the cost comparison.\n'
     '  if (legal) {\n'
     '    lines.push(...receiptLines("How the legal figure was calculated:", legal.driving_factors));\n'
     '  }\n'
     '  const friction = payload.friction_tax_estimate;\n'
     '  if (friction) {\n'
     '    lines.push("", `Friction tax, recurring every year: ${money(friction.low, friction.high)}`);\n'
     '    lines.push(...receiptLines("How the friction tax was calculated:", friction.driving_factors));\n'
     '  }\n'
     '  const scc = payload.service_cost_comparison;\n'
     '  if (scc && (friction || legalHasPrice)) {\n'
     '    lines.push("", "Cost comparison:");\n'
     '    if (friction) {\n'
     '      lines.push(`— Friction tax, recurring every year: ${money(friction.low, friction.high)}`);\n'
     '    }\n'
     '    if (legalHasPrice) {\n'
     '      lines.push(`— Legal exposure, one-time if a claim arises: ${money(legal!.low!, legal!.high!)}`);\n'
     '    }\n'
     '    const service = scc.target_service_name || payload.resolution_family;\n'
     '    const priced = scc.service_estimate_low !== null && scc.service_estimate_high !== null;\n'
     '    lines.push(\n'
     '      priced\n'
     '        ? `— ${service}: ${money(scc.service_estimate_low!, scc.service_estimate_high!)}${scc.pricing_model_note ? `. ${scc.pricing_model_note}` : ""}`\n'
     '        : `— ${service ? `${service}: ` : ""}Ask for pricing. Scoped to what this diagnostic found.`,\n'
     '    );\n'
     '  }\n'
     '\n'
     '  // Phase 3 -- tactical & compliance review (hr-dx only in practice).\n'
     '  const findings = payload.tactical_findings ?? [];\n'
     '  if (findings.length > 0) {\n'
     '    lines.push("", "Tactical & compliance review:");\n'
     '    for (const f of findings) {\n'
     '      const count = f.flagged_count === 0\n'
     '        ? `No gaps in these ${f.total_count} answers.`\n'
     '        : `${f.flagged_count} of ${f.total_count} answers show a gap.`;\n'
     '      lines.push(`— ${f.section_name}: ${count}`);\n'
     '      if (f.synthesis_text) lines.push(`  ${f.synthesis_text}`);\n'
     '    }\n'
     '  }\n'
     '\n'
     '  // ── Section 2 -- additional diagnostic detail (never shown on screen) ──\n',
     'receipts, friction, cost comparison, tactical'),
]

TESTS = '''

describe("buildResultsText -- Phase 3 sections", () => {
  const phase3: PrivateOutputPayload = {
    ...FULL_PAYLOAD,
    synthesis: { ...FULL_PAYLOAD.synthesis, executive_summary: "The summary sentence." },
    friction_tax_estimate: {
      low: 50000, high: 70000, currency: "USD",
      driving_factors: [{ category: "Payroll baseline", rationale: "Estimated annual payroll: $1,000,000." }],
    },
    legal_tail_risk_exposure: {
      ...FULL_PAYLOAD.legal_tail_risk_exposure!,
      driving_factors: [{ category: "Wage and hour", rationale: "State X: $100,000.", triggering_answer: "Time records are informal." }],
    },
    service_cost_comparison: {
      target_service_name: "", inaction_cost_low: 150000, inaction_cost_high: 520000,
      service_estimate_low: null, service_estimate_high: null, pricing_model_note: "",
    },
    asset_evidence: {
      strongest_axes: ["attitude"], contributing_signals: [],
      net_scores: { aptitude: 0, authority: 1.4, alliance: 0, attitude: 1.9 },
    },
    tactical_findings: [{
      section_id: "TC-PAYROLL", section_name: "Payroll & Wage-Hour", flagged_count: 2, total_count: 4,
      synthesis_text: "Overtime classifications may have drifted.", flagged_items: [],
    }],
  };
  const text = buildResultsText(phase3);

  it("opens with the executive summary", () => {
    expect(text.startsWith("Executive summary:\\nThe summary sentence.")).toBe(true);
  });
  it("includes where strength shows up, with net scores", () => {
    expect(text).toContain("Where strength shows up: Attitude (net asset signal: Aptitude 0 | Authority 1.4 | Alliance 0 | Attitude 1.9)");
  });
  it("includes both receipt lists, with the triggering answer when present", () => {
    expect(text).toContain("How the legal figure was calculated:");
    expect(text).toContain("— Wage and hour: State X: $100,000.");
    expect(text).toContain("  Based on your answers: Time records are informal.");
    expect(text).toContain("How the friction tax was calculated:");
    expect(text).toContain("— Payroll baseline: Estimated annual payroll: $1,000,000.");
  });
  it("includes the cost comparison with separate timeframes, never a combined total", () => {
    expect(text).toContain("Cost comparison:");
    expect(text).toContain("— Friction tax, recurring every year: $50,000 – $70,000");
    expect(text).toContain("— Legal exposure, one-time if a claim arises: $100,000 – $450,000");
    expect(text).toContain("— People Tactics & Strategy: Ask for pricing.");
    expect(text).not.toContain("520,000");
  });
  it("includes the tactical review", () => {
    expect(text).toContain("— Payroll & Wage-Hour: 2 of 4 answers show a gap.");
    expect(text).toContain("  Overtime classifications may have drifted.");
  });
  it("omits every Phase 3 section when the payload has none", () => {
    const plain = buildResultsText(MINIMAL_PAYLOAD);
    for (const s of ["Executive summary:", "Where strength shows up", "How the legal figure", "Cost comparison:", "Tactical & compliance review:"]) {
      expect(plain).not.toContain(s);
    }
  });
});
'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    a = ap.parse_args()
    t = OT.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        if t.count(old) != 1:
            print(f'ERROR {label} x{t.count(old)}', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{OT} :: {label}] OK')
    tt = TT.read_text(encoding='utf-8').rstrip('\n') + '\n' + TESTS
    print(f'[{TT} :: Phase 3 tests] OK')
    if a.dry_run:
        print('DRY RUN -- nothing written.')
        return
    OT.write_text(t, encoding='utf-8')
    TT.write_text(tt, encoding='utf-8')
    print('WROTE')


if __name__ == '__main__':
    main()
