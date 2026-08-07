"""
PRV3 Engine Patch -- Q06 option A trigger (content call confirmed by
Pete, A already selected/already the correct severity read) + Q01
option D trigger (the_founders_grip, tie-break reroute).

Q06/A: currently has no severity_trigger. A/B are full-field-identical
(both {aptitude_liability: 0.25, authority_liability: 0.6,
attitude_liability: 0.3}), and A already wins outright for all 6
Authority-primary states wired to Q06 (heard_and_ignored,
the_unsolved_problem, decision_blindness, the_tolerated_violation,
the_policy_lag, disparate_impact_architecture) -- true no-op flip, same
shape as Q14/Q18/Q19. New SEVER-27 follow-on grounded in A's "external
legal claim, EEOC charge, or regulatory inquiry" framing.

Q01/D: C/D/E are full-field-identical (all {authority_liability: 0.6}).
All 4 states wired to Q01 currently select C. Flipping D relies on the
already-shipped Bucket 1 tie-break rule (commit 44e85fc) to reroute all
4 from C to D -- same mechanism as Q02/Q33, not the simpler no-op
pattern. decision_paralysis, the_lost_map, and sequential_decision_
blindness (the other 3 Q01 states, already-known/already-tracked items
with their own separate levers) are unaffected regardless: C/D/E
dimensional identity means zero ranking change, and none are added to
the new follow-on target. New SEVER-28 follow-on grounded in D's "slow
and effortful, takes more than it should" framing.

Usage:
  python tools/patch_q06a_q01d_sever27_28.py --dry-run
  python tools/patch_q06a_q01d_sever27_28.py --write
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
# Q01 option D -- flip severity_trigger, assign SEVER-28
# ============================================================================

edit(
    '            ("D", "It\'s slow and effortful. Getting to a decision takes more than it should.", False, None),\n'
    '            ("E", "It\'s unclear who has authority for what. Decisions happen but the accountability is hard to pin down.", False, None),\n'
    '        ],\n'
    '        ["decision_paralysis", "the_lost_map", "the_founders_grip", "sequential_decision_blindness"],',
    '            ("D", "It\'s slow and effortful. Getting to a decision takes more than it should.", True, "SEVER-28"),\n'
    '            ("E", "It\'s unclear who has authority for what. Decisions happen but the accountability is hard to pin down.", False, None),\n'
    '        ],\n'
    '        ["decision_paralysis", "the_lost_map", "the_founders_grip", "sequential_decision_blindness"],',
)


# ============================================================================
# Q06 option A -- flip severity_trigger, assign SEVER-27
# ============================================================================

edit(
    '            ("A", "An external legal claim, EEOC charge, or regulatory inquiry.", False, None),\n'
    '            ("B", "A monetary settlement involving an employment matter.", False, None),',
    '            ("A", "An external legal claim, EEOC charge, or regulatory inquiry.", True, "SEVER-27"),\n'
    '            ("B", "A monetary settlement involving an employment matter.", False, None),',
)


# ============================================================================
# New SEVER-27 / SEVER-28 _QDATA tuples -- inserted right after SEVER-26
# ============================================================================

edit(
    '        ["leadership_deafness", "the_suppression_filter"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["leadership_deafness", "the_suppression_filter"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-27",\n'
    '        "How long ago did this happen?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — within the past six months.", False, None),\n'
    '            ("B", "It\'s been a year or more.", False, None),\n'
    '            ("C", "It\'s happened repeatedly over a long period.", False, None),\n'
    '            ("D", "I\'m not sure — it may go back further than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["the_tolerated_violation", "disparate_impact_architecture"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-28",\n'
    '        "How long has this been the case?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["the_founders_grip"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-27 / SEVER-28 entries
# ============================================================================

edit(
    '        "SEVER-26": {  # STRONG -- duration (leadership_deafness / the_suppression_filter, Q08-C trigger; content call by Pete)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-26": {  # STRONG -- duration (leadership_deafness / the_suppression_filter, Q08-C trigger; content call by Pete)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-27": {  # STRONG -- duration (the_tolerated_violation / disparate_impact_architecture, Q06-A trigger; content call by Pete, A already-winning. heard_and_ignored/the_unsolved_problem/decision_blindness/the_policy_lag also reach A but are deliberately excluded -- already closed/tracked via other levers, out of scope for this fix)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-28": {  # STRONG -- duration (the_founders_grip, Q01-D trigger; decision_paralysis/the_lost_map/sequential_decision_blindness deliberately excluded, tie-break reroute confirmed safe -- dimensionally identical, not opted in)\n'
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
