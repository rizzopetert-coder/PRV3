"""
PRV3 Engine Patch -- compression_crisis/pay_exposure second trigger:
Q14 option D + new SEVER-17 follow-on.

Q14's options D/E are a full-field-identical tie (both
{aptitude_liability: 0.25, authority_liability: 0.5}). Like Q18, D
already wins outright via plain max() for all three states wired to
Q14 -- no tie-break mechanism needed, this is a direct flip of the
already-selected option. D ("We have concerns about both -- consistency
and competitiveness are issues") is a concrete, admitted problem, read
as more severe than E's unassessed "haven't looked closely enough to
know" -- honest pick, not fabricated.

Confirmed blast radius: Q14's state_targets is exactly ["pay_exposure",
"the_pay_fog", "compression_crisis"]. the_pay_fog is a separate,
already-known open gap (WIRED_INSUFFICIENT via its own Q16/SEVER-01,
AUT-PF-01) and is deliberately NOT added to
_SEVERITY_FOLLOW_ON_TARGETS for SEVER-17 -- out of scope for this fix.
Since D was already the winning option for the_pay_fog too, this flip
is a true no-op on its selection: its answer stays D, word-for-word,
only the internal severity_trigger flag changes, and with no follow-on
targets entry it gets zero severity contribution from it either.

New follow-on SEVER-17 (next available number after SEVER-16), built to
the SEVER-14/15/16 style precedent -- a duration-focused question
honestly following from D's framing, not fabricated to hit a number.

Usage:
  python tools/patch_q14_sever17.py --dry-run
  python tools/patch_q14_sever17.py --write
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
# Q14 option D -- flip severity_trigger, assign SEVER-17
# ============================================================================

edit(
    '            ("D", "We have concerns about both — consistency and competitiveness are issues.", False, None),\n'
    '            ("E", "Honestly, we haven\'t looked closely enough to know.", False, None),\n'
    '        ],\n'
    '        ["pay_exposure", "the_pay_fog", "compression_crisis"],',
    '            ("D", "We have concerns about both — consistency and competitiveness are issues.", True, "SEVER-17"),\n'
    '            ("E", "Honestly, we haven\'t looked closely enough to know.", False, None),\n'
    '        ],\n'
    '        ["pay_exposure", "the_pay_fog", "compression_crisis"],',
)


# ============================================================================
# New SEVER-17 _QDATA tuple -- inserted right after SEVER-16
# ============================================================================

edit(
    '        ["the_unreported_hazard", "the_unlocked_door", "what_nobody_says", "the_suppression_filter"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["the_unreported_hazard", "the_unlocked_door", "what_nobody_says", "the_suppression_filter"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-17",\n'
    '        "How long has this been the case?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["pay_exposure", "compression_crisis"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-17 entry
# ============================================================================

edit(
    '        "SEVER-16": {  # STRONG -- duration (the_unreported_hazard / the_unlocked_door / what_nobody_says / the_suppression_filter, Q18-C trigger)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-16": {  # STRONG -- duration (the_unreported_hazard / the_unlocked_door / what_nobody_says / the_suppression_filter, Q18-C trigger)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-17": {  # STRONG -- duration (compression_crisis / pay_exposure, Q14-D trigger; the_pay_fog deliberately excluded)\n'
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
