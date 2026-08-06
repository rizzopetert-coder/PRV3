"""
PRV3 Engine Patch -- the_exposed/planning_authority_gap/hr_capture second
trigger: Q02 option D + new SEVER-15 follow-on.

Q02's options C/D are a full-field-identical tie (confirmed this session,
same mechanism as Q09's C/D/E) -- D ("Absent -- we don't have a dedicated
HR function right now") reads as the genuinely more severe option than C
(currently selected, "Thin -- part-time or shared responsibility"), losing
only because it's not first in the tied group. Flipping D's
severity_trigger to True lets the already-shipped Bucket 1 tie-break rule
(commit 44e85fc) select it automatically for all three states wired to
Q02 -- no selection-logic change needed, confirmed mechanism, not assumed.

Confirmed blast radius: Q02's state_targets is exactly ["the_exposed",
"hr_capture", "planning_authority_gap"], nothing else in the library
targets any of these three via Q02, and no other question is wired to
the_exposed or planning_authority_gap at all.

New follow-on SEVER-15 (next available number after SEVER-14), built to
the SEVER-14 style precedent -- a duration-focused question honestly
following from D's "Absent" framing, not fabricated to hit a number.

Usage:
  python tools/patch_q02_sever15.py --dry-run
  python tools/patch_q02_sever15.py --write
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
# Q02 option D -- flip severity_trigger, assign SEVER-15
# ============================================================================

edit(
    '            ("D", "Absent — we don\'t have a dedicated HR function right now.", False, None),\n'
    '            ("E", "We have HR but I sometimes wonder whether it\'s truly independent.", False, None),\n'
    '        ],\n'
    '        ["the_exposed", "hr_capture", "planning_authority_gap"],',
    '            ("D", "Absent — we don\'t have a dedicated HR function right now.", True, "SEVER-15"),\n'
    '            ("E", "We have HR but I sometimes wonder whether it\'s truly independent.", False, None),\n'
    '        ],\n'
    '        ["the_exposed", "hr_capture", "planning_authority_gap"],',
)


# ============================================================================
# New SEVER-15 _QDATA tuple -- inserted right after SEVER-14
# ============================================================================

edit(
    '        ["the_fracture", "silosolation"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["the_fracture", "silosolation"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-15",\n'
    '        "How long has your organization been without a dedicated HR function?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this changed in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["the_exposed", "hr_capture", "planning_authority_gap"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-15 entry
# ============================================================================

edit(
    '        "SEVER-14": {  # STRONG -- duration (the_fracture / silosolation, Q09-E second trigger)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-14": {  # STRONG -- duration (the_fracture / silosolation, Q09-E second trigger)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-15": {  # STRONG -- duration (the_exposed / planning_authority_gap / hr_capture, Q02-D trigger)\n'
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
