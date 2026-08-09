"""
PRV3 -- MOB v4.133 -> v4.134: log Category A workflow item A5 (Q16/Q29
duplicate removal) as parked, not scheduled, per Pete's explicit
decision after the regression this session confirmed it needs its own
scoped MC_CENTROID_39-class recalibration effort.

New Section 13a Decision Register row, Tier 3.

Usage:
  python tools/patch_mob_a5_park_q29.py --dry-run
  python tools/patch_mob_a5_park_q29.py --write
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
    "| Q16/Q29 duplicate question -- removal attempted and reverted, parked | 3 | "
    "Parked, not scheduled | Q16/Q29 duplicate question (confirmed 2026-08-09, "
    "prompts/diagnostic-usability-findings-2026-08-09.md Section A.5) -- removal "
    "attempted and reverted. Root cause: engine/accumulation.py:539's rank_states() "
    "hardcodes scale = N / 44.0, the same MC_CENTROID_39 question-count coupling that "
    "required a full Monte Carlo recalibration arc when Q40-51 was added (32->44). "
    "Removing Q29 (44->43) reproduces the identical problem in reverse -- regression "
    "confirmed: 170/175->163/175, 58/58->57/58 HC (ATT-UT-01/the_untouchable newly "
    "failing). Reverted cleanly, working tree back to true baseline, confirmed via git "
    "checkout. Needs its own scoped recalibration effort (Monte Carlo regen + "
    "CENTROID_FIELD_SCALARS reconvergence for N=43) before Q29 can be safely removed -- "
    "not a quick fix, comparable scope to the original MC_CENTROID_39 arc. Not "
    "scheduled -- Pete to reopen when ready to commit to that effort. Q16/Q29 duplicate "
    "remains live in the meantime -- known and logged, not silently present. | This "
    "session (Claude Code) | Not scheduled -- Pete to reopen when ready to commit to "
    "the recalibration effort |\n"
)

edit(
    MOB,
    "| IntakeForm's remaining nested render-body helpers -- same anti-pattern as the "
    "HeadcountStepper bugs, not yet symptomatic | 3 | Informational, no forced check-in "
    "| IntakeForm's other two nested render-body helpers",
    NEW_ROW.rstrip("\n") + "\n"
    "| IntakeForm's remaining nested render-body helpers -- same anti-pattern as the "
    "HeadcountStepper bugs, not yet symptomatic | 3 | Informational, no forced check-in "
    "| IntakeForm's other two nested render-body helpers",
)

edit(MOB, "\\\\\\#\\\\\\# MOB v4.133", "\\\\\\#\\\\\\# MOB v4.134")
edit(CLAUDE, "| MOB version | v4.133 |", "| MOB version | v4.134 |")


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
