"""
PRV3 Engine Patch -- invisible_influence_architecture second trigger:
Q33 option D + new SEVER-19 follow-on.

Q33's options C/D are a full-field-identical tie (both
{aptitude_liability: 0.25, authority_liability: 0.5}). Unlike Q14/Q18/
Q19, C already wins outright for all three states wired to Q33, but D --
the UNSELECTED option -- is the honest severity pick here: D ("We don't
have this infrastructure in place") describes total absence, more
severe than C's "Thin -- documentation exists but isn't actively
maintained." This is the Q02/Q09 shape (flip the losing tied option,
rely on the already-shipped Bucket 1 tie-break rule, commit 44e85fc),
not the Q14/Q18/Q19 "flip the already-winning option" shape.

Confirmed blast radius: Q33's state_targets is exactly ["paper_shield",
"invisible_influence_architecture", "leadership_continuity_risk"]. Both
externals are already-known, already-tracked items with their own
separate levers: paper_shield (AUT-PS-01, already Bucket-1-closed via
Q23/SEVER-05) and leadership_continuity_risk (AUT-LC-01, already known
WIRED_INSUFFICIENT via Q25/SEVER-07, already in
_SEVERITY_FOLLOW_ON_TARGETS for that). Both deliberately excluded from
_SEVERITY_FOLLOW_ON_TARGETS for SEVER-19. Since C and D are
dimensionally identical, the tie-break reroute from C to D changes zero
dimensional_contributions/ranking output for either external -- only
their Q33 answer-selection label changes (C -> D), not their scoring.

New follow-on SEVER-19 (next available number after SEVER-18), built to
the established style precedent -- a duration-focused question honestly
following from D's framing, not fabricated to hit a number.

Usage:
  python tools/patch_q33_sever19.py --dry-run
  python tools/patch_q33_sever19.py --write
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
# Q33 option D -- flip severity_trigger, assign SEVER-19
# ============================================================================

edit(
    '            ("C", "Thin — we have some documentation but it\'s not something we maintain actively.", False, None),\n'
    '            ("D", "We don\'t have this infrastructure in place.", False, None),\n'
    '        ],\n'
    '        ["paper_shield", "invisible_influence_architecture", "leadership_continuity_risk"],',
    '            ("C", "Thin — we have some documentation but it\'s not something we maintain actively.", False, None),\n'
    '            ("D", "We don\'t have this infrastructure in place.", True, "SEVER-19"),\n'
    '        ],\n'
    '        ["paper_shield", "invisible_influence_architecture", "leadership_continuity_risk"],',
)


# ============================================================================
# New SEVER-19 _QDATA tuple -- inserted right after SEVER-18
# ============================================================================

edit(
    '        ["dueling_narratives"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["dueling_narratives"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-19",\n'
    '        "How long has this infrastructure been missing?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this changed in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["invisible_influence_architecture"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-19 entry
# ============================================================================

edit(
    '        "SEVER-18": {  # STRONG -- duration (dueling_narratives, Q19-C trigger; the_pay_fog/the_policy_lag deliberately excluded)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-18": {  # STRONG -- duration (dueling_narratives, Q19-C trigger; the_pay_fog/the_policy_lag deliberately excluded)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-19": {  # STRONG -- duration (invisible_influence_architecture, Q33-D trigger; paper_shield/leadership_continuity_risk deliberately excluded)\n'
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
