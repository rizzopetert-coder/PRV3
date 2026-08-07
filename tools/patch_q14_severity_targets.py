"""
PRV3 Calibration Harness Patch -- add SEVER-17 to EXP-CC-01/AUT-PE-01's
_SEVERITY_FOLLOW_ON_TARGETS entries.

Confirmed empirically (Track A / ALL-FR-01 / Q02 / Q18 precedent) that
content alone changes nothing -- generate_answers()'s splice is gated by
this table. Both EXP-CC-01 (compression_crisis) and AUT-PE-01
(pay_exposure) are Entrenched-expected, single-trigger, closed by this
alone. the_pay_fog's AUT-PF-01 is DELIBERATELY excluded -- it's a
separate, already-known open gap (WIRED_INSUFFICIENT via its own Q16/
SEVER-01), out of scope for this fix and must stay that way.

Usage:
  python tools/patch_q14_severity_targets.py --dry-run
  python tools/patch_q14_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = (
    '    "ALL-SF-03":  {"SEVER-16": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},'
)

NEW = (
    '    "ALL-SF-03":  {"SEVER-16": "18mo_plus"},\n'
    '    # Q14/D second trigger (compression_crisis / pay_exposure) --\n'
    '    # EXP-CC-01 and AUT-PE-01 are single-trigger Entrenched-expected,\n'
    '    # closed by this alone. the_pay_fog (AUT-PF-01) is deliberately NOT\n'
    '    # added here -- it is a separate, already-known open gap\n'
    '    # (WIRED_INSUFFICIENT via its own Q16/SEVER-01), out of scope for\n'
    '    # this fix, must stay unaffected.\n'
    '    "EXP-CC-01":  {"SEVER-17": "18mo_plus"},\n'
    '    "AUT-PE-01":  {"SEVER-17": "18mo_plus"},\n'
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
