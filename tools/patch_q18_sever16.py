"""
PRV3 Engine Patch -- the_unlocked_door/the_unreported_hazard/
the_suppression_filter/what_nobody_says second trigger: Q18 option C +
new SEVER-16 follow-on.

Q18's options C/D are a full-field-identical tie (both {alliance_liability:
0.25, attitude_liability: 0.5}). Unlike Q02/Q09, C is already the winning
option for all four states via plain max() -- no tie-break mechanism
involved, this is a direct flip of the already-selected option. C
("We've had incidents that I think could have been prevented if people
had spoken up earlier") describes realized harm, read as more severe than
D's ongoing-but-unconfirmed-harm framing ("Security is a known gap --
people work around protocols") -- honest pick, not the tie-break pattern.

Confirmed blast radius: Q18's state_targets is exactly
["the_unreported_hazard", "the_unlocked_door", "what_nobody_says",
"the_suppression_filter"], nothing else in the library targets any of
these four via Q18. the_unlocked_door and the_unreported_hazard have no
other question wired to them at all, live or inert.

New follow-on SEVER-16 (next available number after SEVER-15), built to
the SEVER-14/SEVER-15 style precedent -- a duration-focused question
honestly following from C's framing, not fabricated to hit a number.

Usage:
  python tools/patch_q18_sever16.py --dry-run
  python tools/patch_q18_sever16.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "engine" / "data" / "questions.py"

EDITS: list[tuple[str, str]] = []


def edit(old: str, new: str):
    EDITS.append((old, new))


# ============================================================================
# Q18 option C -- flip severity_trigger, assign SEVER-16
# ============================================================================

edit(
    '            ("C", "We\'ve had incidents that I think could have been prevented if people had spoken up earlier.", False, None),\n'
    '            ("D", "Security is a known gap — people work around protocols rather than following them.", False, None),\n'
    '            ("E", "Safety and security aren\'t significant concerns for our type of work.", False, None),\n'
    '        ],\n'
    '        ["the_unreported_hazard", "the_unlocked_door", "what_nobody_says", "the_suppression_filter"],',
    '            ("C", "We\'ve had incidents that I think could have been prevented if people had spoken up earlier.", True, "SEVER-16"),\n'
    '            ("D", "Security is a known gap — people work around protocols rather than following them.", False, None),\n'
    '            ("E", "Safety and security aren\'t significant concerns for our type of work.", False, None),\n'
    '        ],\n'
    '        ["the_unreported_hazard", "the_unlocked_door", "what_nobody_says", "the_suppression_filter"],',
)


# ============================================================================
# New SEVER-16 _QDATA tuple -- inserted right after SEVER-15
# ============================================================================

edit(
    '        ["the_exposed", "hr_capture", "planning_authority_gap"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["the_exposed", "hr_capture", "planning_authority_gap"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-16",\n'
    '        "How long has this been happening?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been happening for a year or more.", False, None),\n'
    '            ("C", "It\'s been happening for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been happening longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["the_unreported_hazard", "the_unlocked_door", "what_nobody_says", "the_suppression_filter"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-16 entry
# ============================================================================

edit(
    '        "SEVER-15": {  # STRONG -- duration (the_exposed / planning_authority_gap / hr_capture, Q02-D trigger)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-15": {  # STRONG -- duration (the_exposed / planning_authority_gap / hr_capture, Q02-D trigger)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-16": {  # STRONG -- duration (the_unreported_hazard / the_unlocked_door / what_nobody_says / the_suppression_filter, Q18-C trigger)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
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
        print(f"=== {len(EDITS)} edit(s) would apply cleanly to engine/data/questions.py ===")
        print("\nDry run complete. Re-run with --write to apply.")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print(f"=== {len(EDITS)} edit(s) written to engine/data/questions.py ===")


if __name__ == "__main__":
    main()
