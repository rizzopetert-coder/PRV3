"""
PRV3 -- Category A workflow, Item A4: add an N/A option to Q42.

Q42 ("When a decision needs that one person's approval and they're
unavailable, what happens?") has no way for a respondent to say the
scenario doesn't apply to their org -- flagged in the live usability
test (prompts/diagnostic-usability-findings-2026-08-09.md, Section A.4).

Scoring convention confirmed by precedent, not invented: Q42's own
option A is already `dict(_z)` (all-zero dimensional_contributions),
with an explicit comment on the Q40-49 batch stating this pattern
"guarantees correct _neutral_option() selection for every profile this
question isn't wired to." A genuine "doesn't apply" answer carries the
same "no liability signal here" meaning, so the new option E reuses
that exact convention -- not a new one.

No existing question in the library uses literal "N/A" phrasing
(checked); matching the plainspoken, full-sentence voice used
throughout Q01-Q51 instead of Pete's shorthand suggestion.

Usage:
  python tools/patch_q42_na_option.py --dry-run
  python tools/patch_q42_na_option.py --write
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
# 1. _QDATA -- add option E to Q42's answer_options list.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q42",\n'
    '        "When a decision needs that one person\'s approval and they\'re"\n'
    '        " unavailable, what happens?",\n'
    '        "forced_choice", 42, "late",\n'
    "        [\n"
    '            ("A", "Someone else is empowered to decide, and it holds.", False, None),\n'
    '            ("B", "It waits, but not for long.", False, None),\n'
    '            ("C", "It waits for a while, and people route around it when they can.", False, None),\n'
    '            ("D", "Everything stops until they\'re reachable, no matter how long that takes — there\'s no real delegation, just waiting.", True, None),\n'
    "        ],\n"
    '        ["the_founders_grip"],\n'
    "        True,\n"
    "    ),",
    '        "Q42",\n'
    '        "When a decision needs that one person\'s approval and they\'re"\n'
    '        " unavailable, what happens?",\n'
    '        "forced_choice", 42, "late",\n'
    "        [\n"
    '            ("A", "Someone else is empowered to decide, and it holds.", False, None),\n'
    '            ("B", "It waits, but not for long.", False, None),\n'
    '            ("C", "It waits for a while, and people route around it when they can.", False, None),\n'
    '            ("D", "Everything stops until they\'re reachable, no matter how long that takes — there\'s no real delegation, just waiting.", True, None),\n'
    '            ("E", "This doesn\'t apply to us — there\'s no single person whose approval everything depends on.", False, None),\n'
    "        ],\n"
    '        ["the_founders_grip"],\n'
    "        True,\n"
    "    ),",
)

# ---------------------------------------------------------------------
# 2. _opt_contrib -- add "E": dict(_z) to Q42's entry, matching option
#    A's existing all-zero convention.
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q42": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "authority_liability":  0.25},\n'
    '            "C": {**_z, "authority_liability":  0.50},\n'
    '            "D": {**_z, "authority_liability":  0.75},\n'
    "        },",
    '        "Q42": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "authority_liability":  0.25},\n'
    '            "C": {**_z, "authority_liability":  0.50},\n'
    '            "D": {**_z, "authority_liability":  0.75},\n'
    '            "E": dict(_z),\n'
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
