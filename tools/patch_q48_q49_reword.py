"""
PRV3 -- Track 2 completion: Q48 stem reword (text-only) and Q49 stem
reword + new N/A-style option E, same pattern as A4's Q42 fix. Both
apply the newly-locked appositive-list house style.

Every old-text value verified directly against the live repo before
writing this script, not assumed. Same safe category as Track 1/A4:
question_text is display-copy only; the new Q49 option E is all-zero
(dict(_z)), matching the precedent already established for Q42's own
added N/A option this session.

Usage:
  python tools/patch_q48_q49_reword.py --dry-run
  python tools/patch_q48_q49_reword.py --write
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

# ---------------------------------------------------------------------
# 1. Q48 -- question_text only, options unchanged.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q48",\n'
    '        "Has this pattern in the data ever been raised internally"\n'
    '        " — through HR, legal, or leadership?",\n'
    '        "forced_choice", 48, "late",',
    '        "Q48",\n'
    '        "Think of a pattern in your data that could suggest unequal treatment"\n'
    '        " (such as pay, promotion, or discipline). Has that pattern ever been"\n'
    '        " raised internally, through HR, legal, or leadership?",\n'
    '        "forced_choice", 48, "late",',
)

# ---------------------------------------------------------------------
# 2. Q49 -- question_text, plus new option E.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q49",\n'
    '        "Has anyone tried to fix or refresh the reward system,"\n'
    '        " and what happened?",\n'
    '        "forced_choice", 49, "late",\n'
    "        [\n"
    '            ("A", "Yes, and it made a real difference.", False, None),\n'
    '            ("B", "Yes, but it hasn\'t landed yet — too early to tell.", False, None),\n'
    '            ("C", "There\'s been talk about it, but no real change has followed.", False, None),\n'
    '            ("D", "It\'s been tried more than once, and nothing has changed — people have stopped believing another attempt will be any different.", True, None),\n'
    "        ],\n"
    '        ["motivational_architecture_failure"],\n'
    "        True,\n"
    "    ),",
    '        "Q49",\n'
    '        "Think of your organization\'s reward or incentive system (such as"\n'
    '        " bonuses, raises, or recognition) — whatever actually drives who gets"\n'
    '        " rewarded. Has anyone tried to fix or refresh it, and what happened?",\n'
    '        "forced_choice", 49, "late",\n'
    "        [\n"
    '            ("A", "Yes, and it made a real difference.", False, None),\n'
    '            ("B", "Yes, but it hasn\'t landed yet — too early to tell.", False, None),\n'
    '            ("C", "There\'s been talk about it, but no real change has followed.", False, None),\n'
    '            ("D", "It\'s been tried more than once, and nothing has changed — people have stopped believing another attempt will be any different.", True, None),\n'
    '            ("E", "No, nothing\'s been done to address it.", False, None),\n'
    "        ],\n"
    '        ["motivational_architecture_failure"],\n'
    "        True,\n"
    "    ),",
)

# ---------------------------------------------------------------------
# 3. _opt_contrib["Q49"] -- add "E": dict(_z), matching Q42's own
#    added N/A option convention.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q49": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "attitude_liability":  0.25},\n'
    '            "C": {**_z, "attitude_liability":  0.50},\n'
    '            "D": {**_z, "attitude_liability":  0.75},\n'
    "        },",
    '        "Q49": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "attitude_liability":  0.25},\n'
    '            "C": {**_z, "attitude_liability":  0.50},\n'
    '            "D": {**_z, "attitude_liability":  0.75},\n'
    "            \"E\": dict(_z),\n"
    "        },",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 200 chars): {old[:200]!r}")
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
