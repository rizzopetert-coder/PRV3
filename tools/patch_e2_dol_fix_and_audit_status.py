"""
PRV3 -- Fix the 4 stale DOL wage-and-hour figures in
research/seven-experiments/experiment-2-employment-litigation-taxonomy.html
(citation-audit.md Section 1 finding: $274M FY2023 figure is stale, and
the liquidated-damages mechanism caveat -- WHD ceased seeking liquidated
damages in pre-litigation administrative settlements as of mid-2025,
PAID self-audit relaunched -- was never written into the actual content).

Also updates research/seven-experiments/citation-audit.md's Section 6
"Still open" item 1: splits out the now-resolved DOL portion, confirms
(via direct repo search this session) that the SEC methodology footnote
and the Unexamined Algorithm insurance-coverage-gap reframe remain
unwritten in any live content, and leaves those two open rather than
closing the whole item.

Usage:
  python tools/patch_e2_dol_fix_and_audit_status.py --dry-run
  python tools/patch_e2_dol_fix_and_audit_status.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================
# research/seven-experiments/experiment-2-employment-litigation-taxonomy.html
# ============================================================

E2 = "research/seven-experiments/experiment-2-employment-litigation-taxonomy.html"

edit(
    E2,
    '<div class="data-item"><div class="data-label">DOL Recovery</div><div class="data-val">$274M FY2023</div></div>',
    '<div class="data-item"><div class="data-label">DOL Recovery</div><div class="data-val">$259M FY2025</div></div>',
)

edit(
    E2,
    '<div class="financial-text">DOL recovered $274M in back wages in FY2023. Wage and hour class actions add liquidated damages equal to back wages owed, plus attorney fees — effective multiplier of 3–4x underlying back wages. California\'s PAGA adds a further multiplier, producing settlements in the tens of millions for organizations with systematic violations. The condition is highly prevalent and the discovery mechanism (class action attorneys) is highly efficient.</div>',
    '<div class="financial-text">DOL recovered $259M in back wages in FY2025. The more consequential 2025 development is structural, not numerical: WHD stopped seeking liquidated damages in pre-litigation administrative settlements as of mid-2025, and relaunched its PAID self-audit program allowing voluntary disclosure without penalty. The 3–4x liquidated-damages multiplier still applies if an employee pursues litigation — it no longer applies to the administrative path most employers actually face.</div>',
)

edit(
    E2,
    '<div class="nc-financial">DOL recovered $274M in back wages FY2023. Class action multiplier: 3–4x back wages owed in liquidated damages and attorney fees. California PAGA adds further exposure.</div>',
    '<div class="nc-financial">DOL recovered $259M in back wages FY2025. Liquidated damages (2–4x back wages) no longer apply to pre-litigation administrative settlements as of mid-2025 — the multiplier now applies only if litigation is pursued.</div>',
)

edit(
    E2,
    "The DOL recovered $274 million.",
    "The DOL recovered $259 million in FY2025 — though the more significant development is procedural: the agency stopped seeking liquidated damages in administrative settlements, reducing the deterrent value of voluntary compliance.",
)


# ============================================================
# research/seven-experiments/citation-audit.md
# ============================================================

edit(
    "research/seven-experiments/citation-audit.md",
    "1. Write the methodology/mechanism footnotes into actual PRV3 content (Section 1's SEC and DOL caveats, Section 2's Unexamined Algorithm reframe) — this audit identifies what needs to change; the content changes themselves are separate execution work.",
    "1. Write the methodology/mechanism footnotes into actual PRV3 content. **DOL portion RESOLVED (2026-08-03):** the mechanism caveat (WHD ceased seeking liquidated damages in pre-litigation administrative settlements as of mid-2025, PAID self-audit relaunched) is now written directly into research/seven-experiments/experiment-2-employment-litigation-taxonomy.html (4 spots: DOL Recovery data label, financial-text prose, candidate summary, closing findings), with the figure updated $274M FY2023 → $259M FY2025 throughout. **Still open:** Section 1's SEC methodology footnote (the $2.7B-adjusted-vs-$17.9B-gross distinction) and Section 2's Unexamined Algorithm reframe (EPLI/D&O insurance-coverage-gap framing — Silent AI, Mobley v. Workday, the EU Product Liability Directive) — confirmed via direct repo search this session that neither has been written into any live content: web/content/book/methodology/the-unexamined-algorithm.md's live /book piece frames the state purely as employment-discrimination exposure, not the insurance-coverage-gap finding this item refers to.",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
