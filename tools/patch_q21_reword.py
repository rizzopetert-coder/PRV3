"""
PRV3 -- Q21 wording differentiation from Q01 (Pete's decision, both
questions kept, wording adjusted so they read less alike). Same safe
category as Track 1: question_text is display-copy only, zero
dimensional_contributions changes.

Usage:
  python tools/patch_q21_reword.py --dry-run
  python tools/patch_q21_reword.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


Q = "engine/data/questions.py"

edit(
    Q,
    '        "Q21",\n'
    '        "When consequential decisions need to move through your organization, what typically happens?",\n'
    '        "forced_choice", 21, "late",',
    '        "Q21",\n'
    '        "As a decision works its way through your organization — from idea to"\n'
    '        " final call — what usually happens along the way?",\n'
    '        "forced_choice", 21, "late",',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
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
