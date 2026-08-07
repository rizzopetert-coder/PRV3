"""
PRV3 Engine Patch -- the_burned_credibility/groundhog_day/narrative_lock
second (or first) trigger: Q17 option B + Q34 option C, new SEVER-23/24
follow-ons.

Confirmed empirically this session (in-memory, non-destructive test with
a positive control) that the earlier ATT-GD-01/ATT-NL-01 collision
finding conflated selection-reroute with severity-firing. Q17's B/C/D/E
and Q34's C/D are full-field-identical tied groups, and the_broken_
compass already selects B on Q17 and C on Q34 -- flipping those already-
selected options is a true no-op for it, same shape as Q14/Q18/Q19, not
the tie-break-reroute shape. Severity splicing is gated strictly by
_SEVERITY_FOLLOW_ON_TARGETS keyed per test_id (confirmed directly in
generate_answers()); the_broken_compass's test_ids (ATT-BCP-01/02/03)
are deliberately never added, so it gets zero severity contribution
regardless of the trigger flags.

Q17/B: "We start strong but struggle to sustain -- initiatives fade
before they take hold." Already the winning option for every
Attitude-primary state on Q17 (the_burned_credibility, groundhog_day,
the_broken_compass, narrative_lock).

Q34/C: "It's a cultural issue -- it's about how people behave and what
the organization accepts." Already the winning option for the_broken_
compass, narrative_lock, and the_burned_credibility on Q34. groundhog_day
is NOT wired to Q34 at all (state_targets = the_broken_compass/
narrative_lock/the_burned_credibility only) -- Q17 is its only viable
second-trigger candidate.

Usage:
  python tools/patch_q17_q34_sever23_24.py --dry-run
  python tools/patch_q17_q34_sever23_24.py --write
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
# Q17 option B -- flip severity_trigger, assign SEVER-23
# ============================================================================

edit(
    '            ("B", "We start strong but struggle to sustain — initiatives fade before they take hold.", False, None),\n'
    '            ("C", "People participate but don\'t really invest — there\'s a wait-and-see quality to how change lands.", False, None),\n'
    '            ("D", "We keep addressing the same problems with different approaches and getting the same result.", False, None),\n'
    '            ("E", "We know what needs to change and we talk about it — but we don\'t actually move.", False, None),\n'
    '        ],\n'
    '        ["the_burned_credibility", "groundhog_day", "the_broken_compass", "narrative_lock"],',
    '            ("B", "We start strong but struggle to sustain — initiatives fade before they take hold.", True, "SEVER-23"),\n'
    '            ("C", "People participate but don\'t really invest — there\'s a wait-and-see quality to how change lands.", False, None),\n'
    '            ("D", "We keep addressing the same problems with different approaches and getting the same result.", False, None),\n'
    '            ("E", "We know what needs to change and we talk about it — but we don\'t actually move.", False, None),\n'
    '        ],\n'
    '        ["the_burned_credibility", "groundhog_day", "the_broken_compass", "narrative_lock"],',
)


# ============================================================================
# Q34 option C -- flip severity_trigger, assign SEVER-24
# ============================================================================

edit(
    '            ("C", "It\'s a cultural issue — it\'s about how people behave and what the organization accepts.", False, None),\n'
    '            ("D", "A leadership issue — the will or capability to act on what we know isn\'t there.", False, None),\n'
    '            ("E", "I\'m not sure — the problem is real but I can\'t cleanly categorize it.", False, None),\n'
    '        ],\n'
    '        ["the_broken_compass", "narrative_lock", "the_burned_credibility"],',
    '            ("C", "It\'s a cultural issue — it\'s about how people behave and what the organization accepts.", True, "SEVER-24"),\n'
    '            ("D", "A leadership issue — the will or capability to act on what we know isn\'t there.", False, None),\n'
    '            ("E", "I\'m not sure — the problem is real but I can\'t cleanly categorize it.", False, None),\n'
    '        ],\n'
    '        ["the_broken_compass", "narrative_lock", "the_burned_credibility"],',
)


# ============================================================================
# New SEVER-23 / SEVER-24 _QDATA tuples -- inserted right after SEVER-22
# ============================================================================

edit(
    '        ["hr_capture", "heard_and_ignored", "what_nobody_says", "leadership_deafness"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
    '        ["hr_capture", "heard_and_ignored", "what_nobody_says", "leadership_deafness"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-23",\n'
    '        "How long has this pattern of stalled initiatives been going on?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["groundhog_day", "the_burned_credibility"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-24",\n'
    '        "How long has this cultural pattern been present?",\n'
    '        "forced_choice", None, "conditional",\n'
    '        [\n'
    '            ("A", "It\'s recent — this started in the past six months.", False, None),\n'
    '            ("B", "It\'s been this way for a year or more.", False, None),\n'
    '            ("C", "It\'s been this way for as long as I can remember.", False, None),\n'
    '            ("D", "I\'m not sure — it may have been this way longer than I\'ve recognized.", False, None),\n'
    '        ],\n'
    '        ["narrative_lock", "the_burned_credibility"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "Q35",',
)


# ============================================================================
# _severity_input_tags -- new SEVER-23 / SEVER-24 entries
# ============================================================================

edit(
    '        "SEVER-22": {  # STRONG -- duration (hr_capture / heard_and_ignored / what_nobody_says / leadership_deafness, Q04-D trigger; the_suppression_filter deliberately excluded, doesn\'t reach D)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '    }',
    '        "SEVER-22": {  # STRONG -- duration (hr_capture / heard_and_ignored / what_nobody_says / leadership_deafness, Q04-D trigger; the_suppression_filter deliberately excluded, doesn\'t reach D)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-23": {  # STRONG -- duration (groundhog_day / the_burned_credibility, Q17-B trigger; the_broken_compass deliberately excluded, already-winning true no-op confirmed empirically)\n'
    '            "A": {"duration_band": "0_6mo"},\n'
    '            "B": {"duration_band": "6_18mo"},\n'
    '            "C": {"duration_band": "18mo_plus"},\n'
    '            "D": {"duration_band": "18mo_plus"},\n'
    '        },\n'
    '        "SEVER-24": {  # STRONG -- duration (narrative_lock / the_burned_credibility, Q34-C trigger; the_broken_compass deliberately excluded, already-winning true no-op confirmed empirically)\n'
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
