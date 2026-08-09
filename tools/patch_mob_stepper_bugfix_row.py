"""
PRV3 -- MOB v4.132 -> v4.133: log the nested-render-body anti-pattern
found while root-causing the two live employee-count stepper bugs
fixed in commit 262b99f.

New Section 13a Decision Register row, Tier 3, informational, no
forced check-in: IntakeForm's other two nested helpers (field(),
SignificantEventsField()) carry the identical anti-pattern that
caused the HeadcountStepper bugs, not yet symptomatic, not fixed in
this pass -- scope was HeadcountStepper only, per the two reported
bugs.

Usage:
  python tools/patch_mob_stepper_bugfix_row.py --dry-run
  python tools/patch_mob_stepper_bugfix_row.py --write
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

# ---------------------------------------------------------------------
# 1. New Decision Register row, appended after the current last row
#    (the status-line-staleness running-list row).
# ---------------------------------------------------------------------

NEW_ROW = (
    "| IntakeForm's remaining nested render-body helpers -- same anti-pattern as the "
    "HeadcountStepper bugs, not yet symptomatic | 3 | Informational, no forced check-in | "
    "IntakeForm's other two nested render-body helpers (field(), SignificantEventsField()) "
    "carry the identical nested-declaration-causes-remount-on-every-render anti-pattern that "
    "caused the HeadcountStepper bugs (commit 262b99f) -- both are still declared inside "
    "IntakeForm's function body, so each is redeclared as a new function reference on every "
    "keystroke-driven re-render, and React remounts their underlying DOM on every parent "
    "render exactly as HeadcountStepper's <input> did. Not yet symptomatic -- confirmed via "
    "direct read of both: select dropdowns (field()) and checkboxes "
    "(SignificantEventsField()) aren't sensitive to mid-keystroke remounting the way a "
    "free-text input is, since their interaction model is discrete-click-driven, not "
    "keystroke-buffered. But flagged since the same root cause could resurface if either ever "
    "gains text-input-like behavior. Not fixed in this pass -- scope was HeadcountStepper "
    "only, per the two reported bugs (a literal-escape-sequence rendering bug and the "
    "remount-driven flaky-input bug), not a general refactor of IntakeForm. | This session "
    "(Claude Code) | No forced check-in -- revisit only if field() or SignificantEventsField() "
    "is ever changed to accept free-text keystroke input, or if a similar bug is reported on "
    "either |\n"
)

edit(
    MOB,
    "| Status-line-fixed-but-body-not-swept staleness pattern -- three confirmed instances, "
    "repo sweep complete | 3 | Informational, no forced check-in | Third confirmed instance",
    NEW_ROW.rstrip("\n") + "\n"
    "| Status-line-fixed-but-body-not-swept staleness pattern -- three confirmed instances, "
    "repo sweep complete | 3 | Informational, no forced check-in | Third confirmed instance",
)

# ---------------------------------------------------------------------
# 2. Version bump.
# ---------------------------------------------------------------------

edit(MOB, "\\\\\\#\\\\\\# MOB v4.132", "\\\\\\#\\\\\\# MOB v4.133")
edit(CLAUDE, "| MOB version | v4.132 |", "| MOB version | v4.133 |")


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
