"""
PRV3 -- MOB v4.134 -> v4.135: log Structure 3 (diagnostic Q37/38/39
core-to-splice conversion) as parked alongside A5, per Gemini
architecture review + this session's own verification.

New Section 13a Decision Register row, Tier 3, informational, linking
to the existing A5 row.

Usage:
  python tools/patch_mob_structure3_park.py --dry-run
  python tools/patch_mob_structure3_park.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MOB = "tools/_mob.txt"
CLAUDE = "CLAUDE.md"

NEW_ROW = (
    "| Structure 3 (diagnostic Q37/38/39 core-to-splice conversion) parked alongside A5 | 3 | "
    "Parked, not scheduled | Structure 3 (diagnostic Q37/38/39 core-to-splice conversion) parked "
    "alongside A5 (Q16/Q29 duplicate removal) -- both require the same MC_CENTROID-style "
    "recalibration effort (core question count change triggers engine/accumulation.py:539's "
    "scale = N / 44.0 coupling). Confirmed via Gemini architecture review + this session's own A5 "
    "regression test, not assumed. See prompts/diagnostic-usability-findings-2026-08-09.md, "
    "B-addendum-3, for full detail. Structures 1 and 2 (same review) cleared independently, no "
    "calibration risk, proceeding separately. | This session (Claude Code) | Not scheduled -- Pete "
    "to reopen alongside A5 when ready to commit to the recalibration effort |\n"
)

edit(
    MOB,
    "| Q16/Q29 duplicate question -- removal attempted and reverted, parked | 3 | Parked, not scheduled |",
    NEW_ROW.rstrip("\n") + "\n"
    "| Q16/Q29 duplicate question -- removal attempted and reverted, parked | 3 | Parked, not scheduled |",
)

edit(MOB, "\\\\\\#\\\\\\# MOB v4.134", "\\\\\\#\\\\\\# MOB v4.135")
edit(CLAUDE, "| MOB version | v4.134 |", "| MOB version | v4.135 |")


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
