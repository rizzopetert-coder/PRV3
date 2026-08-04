"""
PRV3 -- Fix a numbering gap left by the prior Priority Queue renumber
(commit 332916f). That patch's old-string match for the list stopped
at the "seven-experiments" item and never captured the pre-existing
"10. Infrastructure housekeeping..." line after it -- so the list now
reads 1-8 then jumps straight to "10.", skipping 9. Caught while
reading the queue back for Pete. Simple fix: 10 -> 9, no content change.

Usage:
  python tools/patch_mob_priority_queue_renumber_fix.py --dry-run
  python tools/patch_mob_priority_queue_renumber_fix.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.95",
    "\\\\\\#\\\\\\# MOB v4.96",
)

edit(
    "tools/_mob.txt",
    "10. Infrastructure housekeeping, opportunistic/lower priority:",
    "9. Infrastructure housekeeping, opportunistic/lower priority:",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
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
