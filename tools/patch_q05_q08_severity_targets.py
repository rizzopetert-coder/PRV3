"""
PRV3 Calibration Harness Patch -- add SEVER-25/SEVER-26 to the relevant
_SEVERITY_FOLLOW_ON_TARGETS entries.

SEVER-25 (Q05/C):
  - ATT-UT-01/02/03 (the_untouchable) -- new entries, first trigger.
    ATT-UT-02/03 (Entrenched) close outright. ATT-UT-01 (Endemic) lands
    correctly short pending a second trigger (Q12, still a pending
    content call, not part of this fix).
  - ATT-BS-01, ATT-IT-01 (Endemic-expected) -- extended in place with
    their genuine SECOND trigger (both already have SEVER-20 from the
    Q11 fix), closing both to Endemic.
  - Deliberately NOT added: ATT-BS-02/03, ATT-IT-02/03, ATT-WR-01 --
    all three already correctly closed via SEVER-20 alone; a second
    trigger would incorrectly overshoot them to Endemic.

SEVER-26 (Q08/C):
  - ATT-LD-01, ALL-SF-01 (both Endemic-expected) -- extended in place
    with their genuine SECOND trigger (already have SEVER-22 and
    SEVER-16 respectively), closing both to Endemic.
  - Deliberately NOT added: ATT-LD-02/03, ALL-SF-02/03 -- already
    correctly closed via their first trigger alone; a second trigger
    would incorrectly overshoot them to Endemic.

Usage:
  python tools/patch_q05_q08_severity_targets.py --dry-run
  python tools/patch_q05_q08_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

EDITS: list[tuple[str, str]] = []


def edit(old: str, new: str):
    EDITS.append((old, new))


# ============================================================================
# Extend existing entries in place -- avoids duplicate dict keys
# ============================================================================

edit(
    '    "ALL-SF-01":  {"SEVER-16": "18mo_plus"},',
    '    "ALL-SF-01":  {"SEVER-16": "18mo_plus", "SEVER-26": "18mo_plus"},',
)

edit(
    '    "ATT-LD-01":  {"SEVER-22": "18mo_plus"},',
    '    "ATT-LD-01":  {"SEVER-22": "18mo_plus", "SEVER-26": "18mo_plus"},',
)

edit(
    '    "ATT-BS-01":  {"SEVER-20": "18mo_plus"},',
    '    "ATT-BS-01":  {"SEVER-20": "18mo_plus", "SEVER-25": "18mo_plus"},',
)

edit(
    '    "ATT-IT-01":  {"SEVER-20": "18mo_plus"},',
    '    "ATT-IT-01":  {"SEVER-20": "18mo_plus", "SEVER-25": "18mo_plus"},',
)


# ============================================================================
# New entries -- the_untouchable (first trigger via Q05/C)
# ============================================================================

edit(
    '    "ATT-BC-01":  {"SEVER-23": "18mo_plus", "SEVER-24": "18mo_plus"},\n'
    '    "ATT-BC-02":  {"SEVER-24": "18mo_plus"},',
    '    "ATT-BC-01":  {"SEVER-23": "18mo_plus", "SEVER-24": "18mo_plus"},\n'
    '    "ATT-BC-02":  {"SEVER-24": "18mo_plus"},\n'
    '    "ATT-UT-01":  {"SEVER-25": "18mo_plus"},\n'
    '    "ATT-UT-02":  {"SEVER-25": "18mo_plus"},\n'
    '    "ATT-UT-03":  {"SEVER-25": "18mo_plus"},',
)


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
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print(f"=== {len(EDITS)} edit(s) would apply cleanly ===")
        print("\nDry run complete. Re-run with --write to apply.")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print(f"=== {len(EDITS)} edit(s) written ===")


if __name__ == "__main__":
    main()
