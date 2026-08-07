"""
PRV3 Engine Patch -- motivational_architecture_failure/cultural_overtime
second trigger: Q11 option D + new SEVER-20 follow-on.

Unlike every prior Bucket 3 fix this session, Q11's option D isn't part
of a tied pair at all -- D (attitude_liability: 0.75) is the unique max
on Q11, not shared with any other option. It already wins outright for
every Attitude-primary state wired to Q11: culture_drift,
the_wrong_reward, the_inside_track, the_basement_standard,
the_broken_compass, cultural_overtime, and motivational_architecture_
failure. Only the_arbitrary_standard (Alliance-primary) is untouched --
it selects A on a different field entirely. Flipping D's trigger is a
true no-op on selection for all 6 "other" states in state_targets: no
tie-break mechanism involved, no reroute, nothing to prove safe beyond
"the answer doesn't change."

Confirmed blast radius: Q11 is the only question wired to either
motivational_architecture_failure or cultural_overtime, live or inert.
the_basement_standard/the_wrong_reward/the_inside_track also select D
here but each has Q05 as a second candidate question -- explicitly out
of scope for this fix (Q05 not touched), noted as a leverage bonus for
a future round. the_broken_compass already selects D today (unchanged
by this flip) and is deliberately NOT added to
_SEVERITY_FOLLOW_ON_TARGETS -- it's the already-correctly-calibrated
state that blocked the ATT-GD-01/ATT-NL-01 fix earlier this session,
must stay untouched.

New follow-on SEVER-20 (next available number after SEVER-19), built to
the established style precedent -- a duration-focused question honestly
following from D's framing, not fabricated to hit a number.

Usage:
  python tools/patch_q11_sever20.py --dry-run
  python tools/patch_q11_sever20.py --write
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
# Q11 option D -- flip severity_trigger, assign SEVER-20
# ============================================================================

edit(
    '            ("D", "What gets rewarded and what we say we value are two different things — and people know it.", False, None),\n'
    '            ("E", "Our values are stated but they don\'t really govern anything.", False, None),\n'
    '        ],\n'
    '        ["culture_drift", "the_wrong_reward", "the_inside_track",\n'
    '         "the_arbitrary_standard", "the_basement_standard", "the_broken_compass",\n'
    '         "cultural_overtime", "motivational_architecture_failure"],',
    '            ("D", "What gets rewarded and what we say we value are two different things — and people know it.", True, "SEVER-20"),\n'
    '            ("E", "Our values are stated but they don\'t really govern anything.", False, None),\n'
    '        ],\n'
    '        ["culture_drift", "the_wrong_reward", "the_inside_track",\n'
    '         "the_arbitrary_standard", "the_basement_standard", "the_broken_compass",\n'
    '         "cultural_overtime", "motivational_architecture_failure"],',
)


# ============================================================================
# New SEVER-20 _QDATA tuple -- inserted right after SEVER-19
# ============================================================================

edit(
    '        ["invisible_influence_architecture"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["invisible_influence_architecture"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-20",\n'
    '        "How long has this been the case?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["motivational_architecture_failure", "cultural_overtime"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-20 entry
# ============================================================================

edit(
    '        "SEVER-19": {  # STRONG -- duration (invisible_influence_architecture, Q33-D trigger; paper_shield/leadership_continuity_risk deliberately excluded)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-19": {  # STRONG -- duration (invisible_influence_architecture, Q33-D trigger; paper_shield/leadership_continuity_risk deliberately excluded)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-20": {  # STRONG -- duration (motivational_architecture_failure / cultural_overtime, Q11-D trigger; 6 other Q11 states deliberately excluded)\n'
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
