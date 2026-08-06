"""
PRV3 Calibration Harness Patch -- add SEVER-16 to ATT-UD-01/ATT-UH-01/
ALL-SF-02/ALL-SF-03/ATT-WNS-01/ALL-SF-01's _SEVERITY_FOLLOW_ON_TARGETS
entries.

Confirmed empirically (Track A / ALL-FR-01 / Q02 precedent) that content
alone changes nothing -- generate_answers()'s splice is gated by this
table. ATT-UD-01, ATT-UH-01, ALL-SF-02, ALL-SF-03 (all Entrenched) close
with this single trigger alone. ATT-WNS-01 and ALL-SF-01 (both
Endemic-expected) are genuinely two-trigger cases -- this entry gets each
to raw 2.00/Entrenched only, correctly short of Endemic (3.96), not a
bug. Their second triggers (candidates: Q04 for what_nobody_says;
Q04/Q08/Q12/Q30 for the_suppression_filter) are separate future work.

Usage:
  python tools/patch_q18_severity_targets.py --dry-run
  python tools/patch_q18_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = (
    '    "AUT-HC-02":  {"SEVER-15": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},'
)

NEW = (
    '    "AUT-HC-02":  {"SEVER-15": "18mo_plus"},\n'
    '    # Q18/C second trigger (the_unreported_hazard / the_unlocked_door /\n'
    '    # what_nobody_says / the_suppression_filter) -- ATT-UD-01, ATT-UH-01,\n'
    '    # ALL-SF-02, ALL-SF-03 are single-trigger Entrenched-expected, closed\n'
    '    # by this alone. ATT-WNS-01 and ALL-SF-01 are Endemic-expected and\n'
    '    # genuinely need a second trigger (candidates: Q04 for\n'
    '    # what_nobody_says; Q04/Q08/Q12/Q30 for the_suppression_filter --\n'
    '    # separate future review, not part of this fix) -- correctly land\n'
    '    # short at Entrenched (raw 2.00), not a bug.\n'
    '    "ATT-UD-01":  {"SEVER-16": "18mo_plus"},\n'
    '    "ATT-UH-01":  {"SEVER-16": "18mo_plus"},\n'
    '    "ATT-WNS-01": {"SEVER-16": "18mo_plus"},\n'
    '    "ALL-SF-01":  {"SEVER-16": "18mo_plus"},\n'
    '    "ALL-SF-02":  {"SEVER-16": "18mo_plus"},\n'
    '    "ALL-SF-03":  {"SEVER-16": "18mo_plus"},\n'
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
