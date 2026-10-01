"""
Friction tax rebuild, Stage 6: update the existing web test fixtures to the new shape.
Every change traces to a type or behavior change in patch_stage6_web.py: the estimate
is the two-channel shape, ledger rows carry channels instead of dollar_exposure,
service_cost_comparison has no inaction_cost fields, the visible ledger no longer
prints per-row figures or the two notes that described the old severity-scaled
estimate, and the typical-loss line replaces the friction range line.

Usage: python tools/patch_stage6_web_tests.py --dry-run | --write
"""
import sys
from pathlib import Path

W = Path(__file__).resolve().parents[1] / "web"


def run(path: Path, edits, write: bool) -> None:
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    for e in edits:
        if e[0] == "between":
            _, start, end, new = e
            assert t.count(start) == 1, f"{path.name}: start count {t.count(start)}: {start[:70]!r}"
            i = t.index(start)
            j = t.index(end, i)
            t = t[:i] + new + t[j:]
        else:
            old, new = e
            assert t.count(old) == 1, f"{path.name}: count {t.count(old)}: {old[:80]!r}"
            t = t.replace(old, new)
    print(f"{path.name}: {len(edits)} edits ok ({'CRLF' if crlf else 'LF'})")
    if write:
        path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


NEW_EST_INLINE = """friction_tax_estimate: {
    currency: "USD",
    typical_baseline: {
      total: { amount: 63923.24, percent_of_payroll: 12.6759 },
      channels: [
        { channel: "engagement", amount: 35401.02, percent_of_payroll: 7.02, inputs: [] },
        { channel: "turnover", amount: 28522.22, percent_of_payroll: 5.6559, inputs: [] },
      ],
    },
    excess: null,
  },"""

OT_PHASE3 = """    friction_tax_estimate: {
      currency: "USD",
      typical_baseline: {
        total: { amount: 63923.24, percent_of_payroll: 12.6759 },
        channels: [
          { channel: "engagement", amount: 35401.02, percent_of_payroll: 7.02, inputs: [] },
          { channel: "turnover", amount: 28522.22, percent_of_payroll: 5.6559, inputs: [] },
        ],
      },
      excess: null,
    },
    friction_receipts: [{ category: "Payroll baseline", rationale: "Estimated annual payroll: $1,000,000." }],
    friction_tax_ledger: [
      {
        state_id: "the_paper_tiger", state_name: "The Paper Tiger", risk_label: "Entrenched",
        channels: ["turnover"],
        top_contributing_answers: ["Decisions get made, then get reopened."],
      },
      {
        state_id: "state_b", state_name: "State B", risk_label: "Emerging",
        channels: [], top_contributing_answers: [],
      },
    ],
"""

OT_LEDGER_TEST = """  it("includes the friction tax ledger rows (no per-row figure) and the friction receipts", () => {
    expect(text).toContain("Friction tax ledger:\\n— The Paper Tiger (Entrenched)\\n  Decisions get made, then get reopened.\\n— State B (Emerging)");
    expect(text).not.toContain("Estimates are calculated");
    expect(text).not.toContain("Estimate not available");
    expect(text).toContain("How the friction tax was calculated:\\n— Payroll baseline: Estimated annual payroll: $1,000,000.");
  });
"""

OT_GROUPED_VISIBLE = """  it("groups ledger rows with the same evidence set into one row, evidence once", () => {
    const shared = ["Answer one.", "Answer two."];
    const grouped = buildResultsText({
      ...phase3,
      friction_tax_ledger: [
        { state_id: "a", state_name: "Cond A", risk_label: "Emerging",
          channels: ["turnover"], top_contributing_answers: shared },
        { state_id: "b", state_name: "Cond B", risk_label: "Entrenched",
          channels: ["engagement"], top_contributing_answers: [...shared].reverse() },
        { state_id: "c", state_name: "Cond C", risk_label: "Emerging",
          channels: [], top_contributing_answers: ["Answer three."] },
      ],
    }, undefined, { frictionDollarsVisible: true });
    expect(grouped).toContain(
      "— Cond A (Emerging), Cond B (Entrenched)\\n  Answer one.\\n  Answer two.",
    );
    expect(grouped.split("Answer one.").length - 1).toBe(1);
    expect(grouped).toContain("— Cond C (Emerging)\\n  Answer three.");
    expect(grouped).not.toContain("highest standalone");
  });
"""


def main():
    write = "--write" in sys.argv

    run(W / "lib/output-text.test.ts", [
        ("  FRICTION_TAX_LEDGER_STANDALONE_NOTE, groupLedgerRows, formatUsd, formatUsdRange,\n",
         "  groupLedgerRows, formatUsd, formatUsdRange, FRICTION_TYPICAL_LOSS_LABEL,\n"),
        ('  friction_tax_estimate: { low: 50000, high: 120000, currency: "USD" },\n',
         "  " + NEW_EST_INLINE + "\n"),
        ("between", '    friction_tax_estimate: {\n      low: 50000, high: 70000, currency: "USD",',
         "    legal_tail_risk_exposure: {\n      ...FULL_PAYLOAD.legal_tail_risk_exposure!,", OT_PHASE3),
        ('      target_service_name: "", inaction_cost_low: 150000, inaction_cost_high: 520000,\n',
         '      target_service_name: "",\n'),
        ("between", '  it("includes the friction tax ledger rows, the footnote, and the friction receipts", () => {',
         '  it("includes the legal receipts, with the triggering answer when present"', OT_LEDGER_TEST),
        ('    expect(text).toContain("— Friction tax, recurring every year: $50,000 – $70,000");\n',
         '    expect(text).toContain(`— ${FRICTION_TYPICAL_LOSS_LABEL}: $63,900`);\n'),
        ("between", '  it("groups ledger rows with the same evidence set into one row, highest standalone estimate, evidence once", () => {',
         '  it("friction dollars hidden (default): conditions and their answers, no friction figure or footnote"', OT_GROUPED_VISIBLE),
        ('    for (const s of ["$20,000", "$28,000", "$50,000", "$70,000", "$1,000,000", "Friction tax", "friction tax",',
         '    for (const s of ["$20,000", "$28,000", "$63,900", "$35,400", "$1,000,000", "Friction tax", "friction tax",'),
        ('"Estimates are calculated", "Drives cost through", FRICTION_TAX_LEDGER_STANDALONE_NOTE]) {',
         '"Estimates are calculated", "Drives cost through", "Each row estimates"]) {'),
        ("between", '  it("friction dollars hidden: a grouped row names every condition, evidence once", () => {',
         '  it("friction dollars hidden, no priced legal exposure: the cost comparison is omitted entirely"',
         """  it("friction dollars hidden: a grouped row names every condition, evidence once", () => {
    const shared = ["Answer one.", "Answer two."];
    const g = buildResultsText({
      ...phase3,
      friction_tax_ledger: [
        { state_id: "a", state_name: "Cond A", risk_label: "Emerging",
          channels: ["turnover"], top_contributing_answers: shared },
        { state_id: "b", state_name: "Cond B", risk_label: "Entrenched",
          channels: ["engagement"], top_contributing_answers: [...shared].reverse() },
      ],
    });
    expect(g).toContain("— Cond A (Emerging), Cond B (Entrenched)\\n  Answer one.\\n  Answer two.");
    expect(g.split("Answer one.").length - 1).toBe(1);
  });
"""),
        ('      { state_id: "a", state_name: "A", risk_label: "Emerging", dollar_exposure: null, top_contributing_answers: [] },\n      { state_id: "b", state_name: "B", risk_label: "Emerging", dollar_exposure: null, top_contributing_answers: [] },\n',
         '      { state_id: "a", state_name: "A", risk_label: "Emerging", channels: [], top_contributing_answers: [] },\n      { state_id: "b", state_name: "B", risk_label: "Emerging", channels: [], top_contributing_answers: [] },\n'),
        ("between", '  it("ledger note: plain language, no dashes or semicolons", () => {',
         '  it("on Call 2 failure, copies what the screen shows', ""),
    ], write)

    run(W / "components/PrivateOutput.friction.test.ts", [
        ('import type { PrivateOutputPayload } from "@/lib/types";\n',
         'import type { PrivateOutputPayload } from "@/lib/types";\nimport { NEW_ESTIMATE, NEW_RECEIPTS, NEW_LEDGER, FRICTION_DOLLAR_STRINGS } from "@/lib/friction-test-fixtures";\n'),
        ("between", "  friction_tax_estimate: {\n    low: 1234567, high: 1728394,", "  legal_tail_risk_exposure: {",
         "  friction_tax_estimate: NEW_ESTIMATE,\n  friction_receipts: NEW_RECEIPTS,\n  friction_tax_ledger: NEW_LEDGER,\n"),
        ('    target_service_name: "People Tactics & Strategy", inaction_cost_low: 1334567, inaction_cost_high: 2178394,\n',
         '    target_service_name: "People Tactics & Strategy",\n'),
        ('    for (const s of ["$1,230,000", "$1,730,000", "$556,000", "$778,000", "$9,870,000",\n                     "Friction tax",',
         '    for (const s of [...FRICTION_DOLLAR_STRINGS,\n                     "Friction tax",'),
    ], write)

    run(W / "lib/diagnostic-completion-brand.test.ts", [
        ('        target_service_name: "HR Consulting", inaction_cost_low: 10, inaction_cost_high: 14,\n',
         '        target_service_name: "HR Consulting",\n'),
        ('    expect(result.asset_evidence).toEqual(extra.asset_evidence);\n',
         '    expect(result.asset_evidence).toEqual(extra.asset_evidence);\n    expect(result.friction_receipts).toEqual(extra.friction_receipts);\n'),
        ("      asset_evidence: {\n        strongest_axes: [\"authority\"],\n",
         "      friction_receipts: [{ category: \"Total\", rationale: \"Together, what organizations like yours typically lose is 9.2% of payroll.\" }],\n      asset_evidence: {\n        strongest_axes: [\"authority\"],\n"),
        ('    expect(result.tactical_findings).toEqual([]);\n    expect(result.all_qualified_states).toEqual([]);\n    expect(result.synthesis.executive_summary).toBe("");\n',
         '    expect(result.tactical_findings).toEqual([]);\n    expect(result.all_qualified_states).toEqual([]);\n    expect(result.friction_receipts).toEqual([]);\n    expect(result.synthesis.executive_summary).toBe("");\n'),
    ], write)
    print("WRITE" if write else "DRY RUN")


main()
