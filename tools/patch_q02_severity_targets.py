"""
PRV3 Calibration Harness Patch -- add SEVER-15 to AUT-EX-01/EXP-PAG-01/
AUT-HC-01/AUT-HC-02's _SEVERITY_FOLLOW_ON_TARGETS entries.

Confirmed empirically (Track A / ALL-FR-01 precedent) that content alone
changes nothing -- generate_answers()'s splice is gated by this table.
AUT-EX-01 (Entrenched), EXP-PAG-01 (Entrenched), and AUT-HC-02
(Entrenched) close with this single trigger alone. AUT-HC-01
(Endemic-expected) is genuinely a two-trigger case -- this entry gets it
to raw 2.00/Entrenched only, correctly short of Endemic (3.96), not a
bug. Its second trigger (candidate: Q04) is separate future work, not
part of this fix.

Usage:
  python tools/patch_q02_severity_targets.py --dry-run
  python tools/patch_q02_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = (
    '    "EXP-DCF-01": {"SEVER-08": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},'
)

NEW = (
    '    "EXP-DCF-01": {"SEVER-08": "18mo_plus"},\n'
    '    # Q02/D second trigger (the_exposed / planning_authority_gap /\n'
    '    # hr_capture) -- AUT-EX-01, EXP-PAG-01, AUT-HC-02 are single-trigger\n'
    '    # Entrenched-expected, closed by this alone. AUT-HC-01 is\n'
    '    # Endemic-expected and genuinely needs a second trigger (candidate:\n'
    '    # Q04, separate future review, not part of this fix) -- correctly\n'
    '    # lands short at Entrenched (raw 2.00), not a bug.\n'
    '    "AUT-EX-01":  {"SEVER-15": "18mo_plus"},\n'
    '    "EXP-PAG-01": {"SEVER-15": "18mo_plus"},\n'
    '    "AUT-HC-01":  {"SEVER-15": "18mo_plus"},\n'
    '    "AUT-HC-02":  {"SEVER-15": "18mo_plus"},\n'
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
