"""
PRV3 Engine Patch -- the_untouchable second trigger: Q12 option D + new
SEVER-29 follow-on.

Q12's options C/D are a full-field-identical tie ({attitude_liability:
0.6}). the_untouchable and leadership_deafness both currently select C
(the only two Attitude-primary states on Q12, list-order winner).
Flipping D relies on the already-shipped Bucket 1 tie-break rule
(commit 44e85fc) to reroute both from C to D -- same mechanism as
Q02/Q33. leadership_deafness is unaffected in severity regardless: its
math is already fully closed (Q04+Q08, ATT-LD-01/02/03), and it will
NOT be added to the new SEVER-29 target entry. C/D dimensional identity
means zero ranking change for it either.

D ("There are specific managers who are a real problem -- not the whole
layer, but concentrated issues") is a closer thematic fit for
the_untouchable (concentrated, specific individuals) than C's capacity/
workload framing -- content call confirmed by Pete.

New follow-on SEVER-29 (next available number after SEVER-28), built to
the established style precedent.

Usage:
  python tools/patch_q12d_sever29.py --dry-run
  python tools/patch_q12d_sever29.py --write
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
# Q12 option D -- flip severity_trigger, assign SEVER-29
# ============================================================================

edit(
    '            ("D", "There are specific managers who are a real problem — not the whole layer, but concentrated issues.", False, None),\n'
    '            ("E", "I don\'t have great visibility into how managers are actually performing.", False, None),\n'
    '        ],\n'
    '        ["the_unformed_leader", "the_overloaded_manager", "the_dormant_talent",\n'
    '         "the_untouchable", "leadership_deafness", "the_suppression_filter",\n'
    '         "the_paper_tiger"],',
    '            ("D", "There are specific managers who are a real problem — not the whole layer, but concentrated issues.", True, "SEVER-29"),\n'
    '            ("E", "I don\'t have great visibility into how managers are actually performing.", False, None),\n'
    '        ],\n'
    '        ["the_unformed_leader", "the_overloaded_manager", "the_dormant_talent",\n'
    '         "the_untouchable", "leadership_deafness", "the_suppression_filter",\n'
    '         "the_paper_tiger"],',
)


# ============================================================================
# New SEVER-29 _QDATA tuple -- inserted right after SEVER-28
# ============================================================================

edit(
    '        ["the_founders_grip"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["the_founders_grip"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-29",\n'
    '        "How long has this been the case?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["the_untouchable"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-29 entry
# ============================================================================

edit(
    '        "SEVER-28": {  # STRONG -- duration (the_founders_grip, Q01-D trigger; decision_paralysis/the_lost_map/sequential_decision_blindness deliberately excluded, tie-break reroute confirmed safe -- dimensionally identical, not opted in)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-28": {  # STRONG -- duration (the_founders_grip, Q01-D trigger; decision_paralysis/the_lost_map/sequential_decision_blindness deliberately excluded, tie-break reroute confirmed safe -- dimensionally identical, not opted in)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-29": {  # STRONG -- duration (the_untouchable, Q12-D trigger; leadership_deafness deliberately excluded, tie-break reroute confirmed safe -- dimensionally identical, already-closed via Q04+Q08, not opted in)\n'
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
