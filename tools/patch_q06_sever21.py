"""
PRV3 Engine Patch -- the_paper_tiger trigger: Q06 option D + new SEVER-21
follow-on.

Q06 option D (aptitude_liability: 0.6) is the unique max for
the_paper_tiger -- not tied with anything. Every other Q06-wired state
(heard_and_ignored, the_unsolved_problem, decision_blindness,
the_tolerated_violation, the_policy_lag, disparate_impact_architecture)
selects A instead (a separate A/B tie, untouched by this flip). D is not
shared by any other state on Q06 at all -- confirmed directly, the
cleanest blast radius found this session: not just zero external
exposure, zero exposure of any kind.

New follow-on SEVER-21 (next available number after SEVER-20), built to
the established style precedent -- a duration-focused question honestly
following from D's framing, not fabricated to hit a number.

Usage:
  python tools/patch_q06_sever21.py --dry-run
  python tools/patch_q06_sever21.py --write
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
# Q06 option D -- flip severity_trigger, assign SEVER-21
# ============================================================================

edit(
    '            ("D", "A known practice that you\'re aware isn\'t fully compliant but hasn\'t been addressed.", False, None),\n'
    '            ("E", "None of the above.", False, None),',
    '            ("D", "A known practice that you\'re aware isn\'t fully compliant but hasn\'t been addressed.", True, "SEVER-21"),\n'
    '            ("E", "None of the above.", False, None),',
)


# ============================================================================
# New SEVER-21 _QDATA tuple -- inserted right after SEVER-20
# ============================================================================

edit(
    '        ["motivational_architecture_failure", "cultural_overtime"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["motivational_architecture_failure", "cultural_overtime"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-21",\n'
    '        "How long has this practice been going on?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["the_paper_tiger"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-21 entry
# ============================================================================

edit(
    '        "SEVER-20": {  # STRONG -- duration (motivational_architecture_failure / cultural_overtime, Q11-D trigger; 6 other Q11 states deliberately excluded)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-20": {  # STRONG -- duration (motivational_architecture_failure / cultural_overtime, Q11-D trigger; 6 other Q11 states deliberately excluded)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-21": {  # STRONG -- duration (the_paper_tiger, Q06-D trigger; zero blast radius, D unique to this state on Q06)\n'
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
