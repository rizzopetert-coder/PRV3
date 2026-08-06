"""
PRV3 Calibration Harness Patch -- add SEVER-14 to ALL-FR-01/ALL-SI-01's
_SEVERITY_FOLLOW_ON_TARGETS entries.

Confirmed empirically (Track A precedent) that content alone changes
nothing -- generate_answers()'s splice is gated by this table. ALL-FR-01/
ALL-SI-01 need BOTH SEVER-08 (existing) and SEVER-14 (new) to reach
raw 4.00/Endemic, the same two-trigger pattern ATT-DC-01 already uses.

Usage:
  python tools/patch_all_fr_all_si_severity_targets.py --dry-run
  python tools/patch_all_fr_all_si_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

EDITS: list[tuple[str, str]] = [
    (
        '    "ALL-FR-01":  {"SEVER-08": "18mo_plus"},',
        '    "ALL-FR-01":  {"SEVER-08": "18mo_plus", "SEVER-14": "18mo_plus"},',
    ),
    (
        '    "ALL-SI-01":  {"SEVER-08": "18mo_plus"},',
        '    "ALL-SI-01":  {"SEVER-08": "18mo_plus", "SEVER-14": "18mo_plus"},',
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TARGET.read_text(encoding="utf-8")
    for i, (old, new) in enumerate(EDITS, 1):
        count = content.count(old)
        if count != 1:
            print(f"ABORT: edit #{i}: expected exactly 1 match, found {count}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print(f"=== {len(EDITS)} edit(s) would apply cleanly ===")
        print("Dry run complete. Re-run with --write to apply.")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print(f"=== {len(EDITS)} edit(s) written ===")


if __name__ == "__main__":
    main()
