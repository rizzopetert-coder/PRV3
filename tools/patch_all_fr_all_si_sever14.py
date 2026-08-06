"""
PRV3 Engine Patch -- ALL-FR-01/ALL-SI-01 (the_fracture/silosolation) second
trigger: Q09 option E + new SEVER-14 follow-on.

Q09's options C/D/E are a full-field-identical tie (confirmed prior
session) -- E ("There's a significant unresolved conflict I'm not sure how
to address") reads as the genuinely more severe option than C (currently
selected, "tension that's mostly contained"), but loses only because it's
not first in the tied group. Flipping E's severity_trigger to True lets
the already-shipped Bucket 1 tie-break rule (commit 44e85fc) select it
automatically -- no selection-logic change needed, confirmed mechanism,
not assumed.

Confirmed zero blast radius beyond these two states: Q09's state_targets
is exactly ["the_fracture", "silosolation"], nothing else in the library
targets either state via Q09.

New follow-on SEVER-14 (next available number, SEVER-01 through SEVER-13
already in use), built to the Track A/SEVER-06 style precedent -- a
duration-focused question honestly following from E's "significant
unresolved conflict" framing, not fabricated to hit a number.

Usage:
  python tools/patch_all_fr_all_si_sever14.py --dry-run
  python tools/patch_all_fr_all_si_sever14.py --write
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
# Q09 option E -- flip severity_trigger, assign SEVER-14
# ============================================================================

edit(
    '            ("E", "There\'s a significant unresolved conflict I\'m not sure how to address.", False, None),\n'
    '        ],\n'
    '        ["the_fracture", "silosolation"],',
    '            ("E", "There\'s a significant unresolved conflict I\'m not sure how to address.", True, "SEVER-14"),\n'
    '        ],\n'
    '        ["the_fracture", "silosolation"],',
)


# ============================================================================
# New SEVER-14 _QDATA tuple -- inserted right after SEVER-13
# ============================================================================

edit(
    '        ["narrative_lock", "the_broken_compass"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["narrative_lock", "the_broken_compass"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-14",\n'
    '        "How long has this conflict been present?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — it surfaced in the past six months.", False, None),\n'
    '            ("B", "It\'s been building for a year or more.", False, None),\n'
    '            ("C", "It\'s been unresolved for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been there longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["the_fracture", "silosolation"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-14 entry
# ============================================================================

edit(
    '        "SEVER-13": {  # non-discriminating -- see note above (narrative_lock / the_broken_compass)\n'
    '            "A": {"prior_failed_resolution": True},\n'
    '            "B": {"prior_failed_resolution": True},\n'
    '            "C": {"prior_failed_resolution": True},\n'
    '            "D": {"prior_failed_resolution": True},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-13": {  # non-discriminating -- see note above (narrative_lock / the_broken_compass)\n'
    '            "A": {"prior_failed_resolution": True},\n'
    '            "B": {"prior_failed_resolution": True},\n'
    '            "C": {"prior_failed_resolution": True},\n'
    '            "D": {"prior_failed_resolution": True},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-14": {  # STRONG -- duration (the_fracture / silosolation, Q09-E second trigger)\n'
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
