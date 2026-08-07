"""
PRV3 Engine Patch -- dueling_narratives second trigger: Q19 option C +
new SEVER-18 follow-on.

Q19's options C/D are a full-field-identical tie (both
{aptitude_liability: 0.25, authority_liability: 0.5, attitude_liability:
0.25}). Like Q14/Q18, C already wins outright via plain max() for all
three states wired to Q19 -- no tie-break mechanism needed, this is a
direct flip of the already-selected option. C ("There's a meaningful gap
-- our external narrative is ahead of our internal reality") is an
acknowledged, admitted problem, read as more severe than D's unassessed
"I don't think we've really looked at whether they align" -- honest
pick, not fabricated.

Confirmed blast radius: Q19's state_targets is exactly
["dueling_narratives", "the_pay_fog", "the_policy_lag"]. Both externals
are already-known, already-tracked items with their own separate levers:
the_pay_fog (AUT-PF-01, WIRED_INSUFFICIENT via Q16/SEVER-01) and
the_policy_lag (AUT-PL-01, already correctly Entrenched via a
pre-existing SEVER-04 trigger unrelated to Q19). Both deliberately
excluded from _SEVERITY_FOLLOW_ON_TARGETS for SEVER-18. Since C already
won for both externals too, this flip is a true no-op on their
selection: same answer, word-for-word, only the option-level trigger
flag changes.

New follow-on SEVER-18 (next available number after SEVER-17), built to
the established SEVER-14/15/16/17 style precedent -- a duration-focused
question honestly following from C's framing, not fabricated to hit a
number.

Usage:
  python tools/patch_q19_sever18.py --dry-run
  python tools/patch_q19_sever18.py --write
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
# Q19 option C -- flip severity_trigger, assign SEVER-18
# ============================================================================

edit(
    '            ("C", "There\'s a meaningful gap — our external narrative is ahead of our internal reality.", False, None),\n'
    '            ("D", "I don\'t think we\'ve really looked at whether they align.", False, None),\n'
    '        ],\n'
    '        ["dueling_narratives", "the_pay_fog", "the_policy_lag"],',
    '            ("C", "There\'s a meaningful gap — our external narrative is ahead of our internal reality.", True, "SEVER-18"),\n'
    '            ("D", "I don\'t think we\'ve really looked at whether they align.", False, None),\n'
    '        ],\n'
    '        ["dueling_narratives", "the_pay_fog", "the_policy_lag"],',
)


# ============================================================================
# New SEVER-18 _QDATA tuple -- inserted right after SEVER-17
# ============================================================================

edit(
    '        ["pay_exposure", "compression_crisis"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["pay_exposure", "compression_crisis"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-18",\n'
    '        "How long has this gap been present?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["dueling_narratives"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-18 entry
# ============================================================================

edit(
    '        "SEVER-17": {  # STRONG -- duration (compression_crisis / pay_exposure, Q14-D trigger; the_pay_fog deliberately excluded)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-17": {  # STRONG -- duration (compression_crisis / pay_exposure, Q14-D trigger; the_pay_fog deliberately excluded)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-18": {  # STRONG -- duration (dueling_narratives, Q19-C trigger; the_pay_fog/the_policy_lag deliberately excluded)\n'
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
