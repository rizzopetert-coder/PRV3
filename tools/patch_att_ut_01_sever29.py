"""
PRV3 Calibration Harness Patch -- add SEVER-29 to ATT-UT-01's
_SEVERITY_FOLLOW_ON_TARGETS entry.

ATT-UT-01 (the_untouchable, Endemic-expected) already has SEVER-25
(Q05/C) as its first trigger. SEVER-29 (Q12/D) gives it the genuine
second trigger it needs, closing to Endemic. leadership_deafness
(ATT-LD-01/02/03) deliberately NOT added -- already fully closed via
Q04+Q08, out of scope, must stay unaffected.

Usage:
  python tools/patch_att_ut_01_sever29.py --dry-run
  python tools/patch_att_ut_01_sever29.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = '    "ATT-UT-01":  {"SEVER-25": "18mo_plus"},'
NEW = '    "ATT-UT-01":  {"SEVER-25": "18mo_plus", "SEVER-29": "18mo_plus"},'


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
