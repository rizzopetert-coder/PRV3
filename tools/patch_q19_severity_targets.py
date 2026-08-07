"""
PRV3 Calibration Harness Patch -- add SEVER-18 to AUT-DN-01's
_SEVERITY_FOLLOW_ON_TARGETS entry.

Confirmed empirically (Track A / ALL-FR-01 / Q02 / Q18 / Q14 precedent)
that content alone changes nothing -- generate_answers()'s splice is
gated by this table. AUT-DN-01 is single-trigger Entrenched-expected,
closed by this alone. the_pay_fog (AUT-PF-01) and the_policy_lag
(AUT-PL-01) are deliberately NOT added -- both are separate,
already-known/already-tracked items with their own levers, out of scope
for this fix, must stay unaffected.

Usage:
  python tools/patch_q19_severity_targets.py --dry-run
  python tools/patch_q19_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = (
    '    "AUT-PE-01":  {"SEVER-17": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},'
)

NEW = (
    '    "AUT-PE-01":  {"SEVER-17": "18mo_plus"},\n'
    '    # Q19/C second trigger (dueling_narratives) -- AUT-DN-01 is\n'
    '    # single-trigger Entrenched-expected, closed by this alone.\n'
    '    # the_pay_fog (AUT-PF-01) and the_policy_lag (AUT-PL-01) are\n'
    '    # deliberately NOT added here -- both are separate,\n'
    '    # already-known/already-tracked items with their own levers, out\n'
    '    # of scope for this fix, must stay unaffected.\n'
    '    "AUT-DN-01":  {"SEVER-18": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},'
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TARGET.read_text(encoding="utf-8")
    count = content.count(OLD)
    if count != 1:
        print(f"ABORT: expected exactly 1 match, found {count}")
        sys.exit(1)
    content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print("=== 1 edit would apply cleanly ===")
        print("Dry run complete. Re-run with --write to apply.")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print("=== 1 edit written ===")


if __name__ == "__main__":
    main()
