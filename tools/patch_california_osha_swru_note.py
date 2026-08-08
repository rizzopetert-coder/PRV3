"""
PRV3 -- adds one new, genuinely-not-previously-recorded data point to
Addendum 9's existing California actual-average-penalty entry
(prompts/friction-tax-legal-compliance-methodology.md): the FY2023
Comprehensive FAME Report's separate per-inspection-with-violations
average ($5,906.03 CA vs. $8,861.84 national), distinct from the
per-serious-violation SAMM 8 figure already recorded (California
$8,777.88 total). California's figure is LOWER than the national
average on this measure specifically because its SWRU (serious/
willful/repeat/unclassified) classification rate is unusually low
relative to other states -- the opposite direction from the
per-violation figure, which is why the two measures must not be
conflated as if they were describing the same thing from two angles.

Everything else in Addendum 9 and the Priority Queue is confirmed
already correct and complete -- this session verified the full
existing entry (source, all 5 SAMM 8 rows, the deliberate flat-format
departure note, the FY2009 supersession note) matches byte-for-byte
what was freshly re-supplied, and found it was already resolved in an
earlier session (tools/patch_california_osha_backfill.py, 2026-08-05).
No other change made.

Usage:
  python tools/patch_california_osha_swru_note.py --dry-run
  python tools/patch_california_osha_swru_note.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_PATH = REPO_ROOT / "prompts" / "friction-tax-legal-compliance-methodology.md"

OLD = (
    "California's total figure ($8,777.88) exceeds the total-row national FRL range\n"
    "($2,718.91-$4,531.51) considerably -- flagged in the report's own text as an over-FRL\n"
    "finding. Worth noting as context for why California's figure runs so far above Oregon\n"
    "($604), South Carolina ($2,019), and Michigan ($1,217.24) -- not a data-quality concern,\n"
    "a genuine jurisdictional outlier consistent with California's existing cross-cluster\n"
    "outlier status (Addendum 6). Supersedes the prior $5,503.41 FY2009 figure (U.S. DOL/OSHA\n"
    "Region IX FAME Report for California, FY2009, Table 5/SAMM 10) -- that figure predated\n"
    "this replacement by sixteen years and is no longer current; retained here only as\n"
    "superseded history, not as an alternate current value.\n"
)

NEW = (
    "California's total figure ($8,777.88) exceeds the total-row national FRL range\n"
    "($2,718.91-$4,531.51) considerably -- flagged in the report's own text as an over-FRL\n"
    "finding. Worth noting as context for why California's figure runs so far above Oregon\n"
    "($604), South Carolina ($2,019), and Michigan ($1,217.24) -- not a data-quality concern,\n"
    "a genuine jurisdictional outlier consistent with California's existing cross-cluster\n"
    "outlier status (Addendum 6). Supersedes the prior $5,503.41 FY2009 figure (U.S. DOL/OSHA\n"
    "Region IX FAME Report for California, FY2009, Table 5/SAMM 10) -- that figure predated\n"
    "this replacement by sixteen years and is no longer current; retained here only as\n"
    "superseded history, not as an alternate current value.\n"
    "\n"
    "**Separate measure, do not conflate with the SAMM 8 figure above:** the same FY2023\n"
    "Comprehensive FAME Report also gives an average penalty PER INSPECTION WITH VIOLATIONS\n"
    "ISSUED (not per-serious-violation) of $5,906.03 for California, versus an $8,861.84\n"
    "national average -- LOWER than the national figure, the opposite direction from the\n"
    "per-violation measure above. This is not a contradiction: California's SWRU (serious/\n"
    "willful/repeat/unclassified) classification rate is unusually low relative to other\n"
    "states, which pulls the per-inspection average down even though the per-violation\n"
    "average runs well above the national FRL range. Recorded here for completeness only --\n"
    "the per-serious-violation SAMM 8 figure above remains the relevant measure for this\n"
    "methodology's actual-average-penalty backfill purposes.\n"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = DOC_PATH.read_text(encoding="utf-8")
    count = content.count(OLD)
    if count != 1:
        print(f"ABORT: expected exactly 1 match for anchor, found {count}")
        sys.exit(1)
    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print("=== prompts/friction-tax-legal-compliance-methodology.md: SWRU note would be added ===")
    else:
        DOC_PATH.write_text(new_content, encoding="utf-8")
        print("=== prompts/friction-tax-legal-compliance-methodology.md: SWRU note written ===")


if __name__ == "__main__":
    main()
