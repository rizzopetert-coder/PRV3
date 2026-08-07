"""
PRV3 Calibration Harness Patch -- extend AUT-HI-01 with SEVER-27 as its
genuine second trigger.

Pure table-entry extension, no new content. AUT-HI-01 (heard_and_ignored,
Endemic-expected) already has SEVER-22 (Q04/D) as its first trigger.
SEVER-27 already exists and is already Pete-approved content (Q06/A,
"external legal claim, EEOC charge, or regulatory inquiry" framing),
currently opted in only for AUT-TV-01/02 and EXP-DIA-01/02/03.
heard_and_ignored already selects A on Q06 for real (Authority-primary,
authority_liability: 0.6) -- confirmed reachable, not a new mechanism.

Usage:
  python tools/patch_aut_hi_01_sever27.py --dry-run
  python tools/patch_aut_hi_01_sever27.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = '    "AUT-HI-01":  {"SEVER-22": "18mo_plus"},'
NEW = '    "AUT-HI-01":  {"SEVER-22": "18mo_plus", "SEVER-27": "18mo_plus"},'


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
