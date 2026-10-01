"""
Friction tax rebuild, Stage 5, web side: the condensed figure is a single value.

  web/lib/engine-client.ts   CondensedCompleteResult carries condensed_departure_cost
                             (new) and the retired condensed_financial_range as an
                             optional legacy field
  web/lib/types.ts           CondensedOutputPayload.departure_cost replaces financial_range
  web/app/api/diagnostic/condensed/answer/route.ts
                             builds departure_cost through departureCostFromEngine()
  web/components/CondensedOutput.tsx
                             reads departureCostAmount(), and the visible branch (only if
                             FRICTION_DOLLARS_VISIBLE ever flips) carries new copy that
                             matches wage x 0.333 and the Work Institute basis, marked
                             UNREVIEWED. The hidden branch is unchanged.

FRICTION_DOLLARS_VISIBLE is not touched.

Usage: python tools/patch_stage5_web.py --dry-run | --write
"""
import sys
from pathlib import Path

W = Path(__file__).resolve().parents[1] / "web"


def run(path: Path, edits, write: bool) -> None:
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    for old, new in edits:
        assert t.count(old) == 1, f"{path.name}: count {t.count(old)}: {old[:80]!r}"
        t = t.replace(old, new)
    print(f"{path.name}: {len(edits)} edits ok ({'CRLF' if crlf else 'LF'})")
    if write:
        path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


def main():
    write = "--write" in sys.argv

    run(W / "lib/engine-client.ts", [
        ("""export interface CondensedFinancialRange {
  low: number | null;
  high: number | null;
  currency: "USD";
}
""", """// The retired 0.50 to 0.75 range (Stage 5). Only the previous deploy's engine still
// returns it, readers ignore it (lib/condensed-departure-cost.ts).
export interface CondensedFinancialRange {
  low: number | null;
  high: number | null;
  currency: "USD";
}

// The single value that replaced it: industry wage x 0.333, null for an
// unrecognized industry.
export interface CondensedDepartureCost {
  amount: number | null;
  currency: "USD";
}
"""),
        ("  condensed_financial_range: CondensedFinancialRange;\n}\n",
         "  // Stage 5. Optional because the two projects deploy separately, so a result can\n"
         "  // come from the previous engine with only the legacy range, or neither.\n"
         "  condensed_departure_cost?: CondensedDepartureCost;\n"
         "  condensed_financial_range?: CondensedFinancialRange;\n}\n"),
        ("// actually returns, plus condensed_financial_range merged in by the\n",
         "// actually returns, plus condensed_departure_cost merged in by the\n"),
    ], write)

    run(W / "lib/types.ts", [
        ("// friction_tax_estimate (a different mechanic -- get_industry_wage()-based\n// financial_range instead).",
         "// friction_tax_estimate (a different mechanic -- get_industry_wage()-based\n// departure_cost instead, wage x 0.333)."),
        ("""  financial_range: {
    low: number | null;
    high: number | null;
    currency: "USD";
  };
}
""", """  // The cost of one departure, a single value (Stage 5): the industry wage x 0.333.
  // amount is null for an unrecognized industry. Replaced financial_range, a
  // 0.50 to 0.75 range. Rendered only behind FRICTION_DOLLARS_VISIBLE.
  departure_cost: {
    amount: number | null;
    currency: "USD";
  };
}
"""),
    ], write)

    run(W / "app/api/diagnostic/condensed/answer/route.ts", [
        ("import { translateResolutionFamily } from \"@/lib/resolution-family\";\n",
         "import { translateResolutionFamily } from \"@/lib/resolution-family\";\nimport { departureCostFromEngine } from \"@/lib/condensed-departure-cost\";\n"),
        ("    financial_range: engineResult.condensed_financial_range,\n",
         "    departure_cost: departureCostFromEngine(engineResult),\n"),
    ], write)

    run(W / "components/CondensedOutput.tsx", [
        ('import { formatUsdRange, FRICTION_DOLLARS_VISIBLE } from "@/lib/output-text";\n',
         'import { formatUsd, FRICTION_DOLLARS_VISIBLE } from "@/lib/output-text";\nimport { departureCostAmount } from "@/lib/condensed-departure-cost";\n'),
        ("  const { low, high } = payload.financial_range;\n  const hasFinancialRange = low !== null && high !== null;\n",
         "  // Tolerant of the new single value, the old range payload and a missing value.\n  const departureCost = departureCostAmount(payload);\n"),
        ("        {hasFinancialRange ? (\n          <p className=\"text-sm text-charcoal\">\n            {formatUsdRange(low!, high!)}{\" \"}\n            <span className=\"text-gray-400\">\n              (roughly 50–75% of one departing employee&apos;s estimated salary)\n            </span>\n          </p>\n",
         "        {/* UNREVIEWED COPY (Stage 5 draft, needs Pete's review before any flag flip):\n            the parenthetical states the basis of the figure, the industry average wage\n            x 0.333 (Work Institute). */}\n        {departureCost !== null ? (\n          <p className=\"text-sm text-charcoal\">\n            {formatUsd(departureCost)}{\" \"}\n            <span className=\"text-gray-400\">\n              (about one third of one employee&apos;s annual pay at the average wage in your\n              industry, based on the Work Institute&apos;s estimate of what one voluntary\n              departure costs)\n            </span>\n          </p>\n"),
    ], write)
    print("WRITE" if write else "DRY RUN")


main()
