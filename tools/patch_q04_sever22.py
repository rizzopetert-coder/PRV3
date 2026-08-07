"""
PRV3 Engine Patch -- hr_capture/heard_and_ignored/what_nobody_says/
leadership_deafness trigger: Q04 option D + new SEVER-22 follow-on.

Q04 option D (authority_liability: 0.6) is the unique max -- not tied
with anything (B/C both sit at 0.25). hr_capture, heard_and_ignored,
what_nobody_says, and leadership_deafness all already select D --
confirmed directly, true no-op flip for every one of them. the_
suppression_filter (the 5th Q04-wired state) selects A instead,
completely unaffected.

This single flip does four different things:
  - AUT-HC-01 (hr_capture, currently short at Entrenched via Q02/
    SEVER-15): genuine SECOND trigger, closes to Endemic.
  - ATT-WNS-01 (what_nobody_says, currently short at Entrenched via
    Q18/SEVER-16): same story, closes to Endemic.
  - AUT-HI-02, ATT-LD-02, ATT-LD-03 (Entrenched-expected): close
    outright on this single trigger.
  - AUT-HI-01, ATT-LD-01 (Endemic-expected): first trigger, land
    correctly short at Entrenched pending a second (separate future
    work, not part of this fix).

New follow-on SEVER-22 (next available number after SEVER-21), built to
the established style precedent.

Usage:
  python tools/patch_q04_sever22.py --dry-run
  python tools/patch_q04_sever22.py --write
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
# Q04 option D -- flip severity_trigger, assign SEVER-22
# ============================================================================

edit(
    '            ("D", "Not much happens. People have learned that raising concerns doesn\'t produce results.", False, None),\n'
    '        ],\n'
    '        ["hr_capture", "heard_and_ignored", "what_nobody_says",\n'
    '         "the_suppression_filter", "leadership_deafness"],',
    '            ("D", "Not much happens. People have learned that raising concerns doesn\'t produce results.", True, "SEVER-22"),\n'
    '        ],\n'
    '        ["hr_capture", "heard_and_ignored", "what_nobody_says",\n'
    '         "the_suppression_filter", "leadership_deafness"],',
)


# ============================================================================
# New SEVER-22 _QDATA tuple -- inserted right after SEVER-21
# ============================================================================

edit(
    '        ["the_paper_tiger"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["the_paper_tiger"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-22",\n'
    '        "How long has this been happening?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["hr_capture", "heard_and_ignored", "what_nobody_says", "leadership_deafness"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-22 entry
# ============================================================================

edit(
    '        "SEVER-21": {  # STRONG -- duration (the_paper_tiger, Q06-D trigger; zero blast radius, D unique to this state on Q06)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-21": {  # STRONG -- duration (the_paper_tiger, Q06-D trigger; zero blast radius, D unique to this state on Q06)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-22": {  # STRONG -- duration (hr_capture / heard_and_ignored / what_nobody_says / leadership_deafness, Q04-D trigger; the_suppression_filter deliberately excluded, doesn\'t reach D)\n'
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
