"""
PRV3 Engine Patch -- the_untouchable/the_basement_standard/the_inside_
track (Q05/C, new SEVER-25) and leadership_deafness/the_suppression_
filter (Q08/C, new SEVER-26) triggers.

Content calls made by Pete: Q05 option C ("It depends on who the person
is. Some people are held accountable and some aren't.") and Q08 option C
("By the time problems reach us they're already crises -- we're
frequently surprised.") -- both already the winning option for every
state that reaches them, true no-op flips, same shape as Q14/Q18/Q19.

Q05's state_targets includes the_arbitrary_standard (confirmed dead-end,
doesn't reach C or D at all) and the_paper_tiger (also dead on this
specific field -- already closed via its own Q06/D trigger, unrelated).
Neither is affected by this flip either way.

Usage:
  python tools/patch_q05_q08_sever25_26.py --dry-run
  python tools/patch_q05_q08_sever25_26.py --write
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
# Q05 option C -- flip severity_trigger, assign SEVER-25
# ============================================================================

edit(
    '            ("C", "It depends on who the person is. Some people are held accountable and some aren\'t.", False, None),\n'
    '            ("D", "Not much. Underperformance tends to get tolerated.", False, None),\n'
    '        ],\n'
    '        ["the_basement_standard", "the_untouchable", "the_inside_track",\n'
    '         "the_arbitrary_standard", "the_wrong_reward", "the_paper_tiger"],',
    '            ("C", "It depends on who the person is. Some people are held accountable and some aren\'t.", True, "SEVER-25"),\n'
    '            ("D", "Not much. Underperformance tends to get tolerated.", False, None),\n'
    '        ],\n'
    '        ["the_basement_standard", "the_untouchable", "the_inside_track",\n'
    '         "the_arbitrary_standard", "the_wrong_reward", "the_paper_tiger"],',
)


# ============================================================================
# Q08 option C -- flip severity_trigger, assign SEVER-26
# ============================================================================

edit(
    '            ("C", "By the time problems reach us they\'re already crises — we\'re frequently surprised.", False, None),\n'
    '            ("D", "I think there\'s a gap. What I hear informally is different from what comes through formal channels.", False, None),\n'
    '        ],\n'
    '        ["leadership_deafness", "the_suppression_filter"],',
    '            ("C", "By the time problems reach us they\'re already crises — we\'re frequently surprised.", True, "SEVER-26"),\n'
    '            ("D", "I think there\'s a gap. What I hear informally is different from what comes through formal channels.", False, None),\n'
    '        ],\n'
    '        ["leadership_deafness", "the_suppression_filter"],',
)


# ============================================================================
# New SEVER-25 / SEVER-26 _QDATA tuples -- inserted right after SEVER-24
# ============================================================================

edit(
    '        ["narrative_lock", "the_burned_credibility"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["narrative_lock", "the_burned_credibility"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-25",\n'
    '        "How long has this been the case?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["the_untouchable", "the_basement_standard", "the_inside_track"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-26",\n'
    '        "How long has this been happening?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["leadership_deafness", "the_suppression_filter"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-25 / SEVER-26 entries
# ============================================================================

edit(
    '        "SEVER-24": {  # STRONG -- duration (narrative_lock / the_burned_credibility, Q34-C trigger; the_broken_compass deliberately excluded, already-winning true no-op confirmed empirically)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-24": {  # STRONG -- duration (narrative_lock / the_burned_credibility, Q34-C trigger; the_broken_compass deliberately excluded, already-winning true no-op confirmed empirically)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-25": {  # STRONG -- duration (the_untouchable / the_basement_standard / the_inside_track, Q05-C trigger; content call by Pete)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-26": {  # STRONG -- duration (leadership_deafness / the_suppression_filter, Q08-C trigger; content call by Pete)\n'
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
