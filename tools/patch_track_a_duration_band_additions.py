"""
PRV3 Engine Patch -- Track A: add duration_band=18mo_plus option E to all
10 confirmed LIVE-REACHABLE severity follow-on questions.

Pete-drafted content (Claude.ai). Style precedent: SEVER-06 ("It's been the
operating mode for as long as I can remember"). Each new option:
severity_trigger=False, no follow_on, severity_input_mapping=
{'duration_band': '18mo_plus'} (added via _severity_input_tags, the
mechanism the builder function actually reads -- NOT part of the _QDATA
option tuple itself).

SEVER-05 is the one exception requiring a THIRD edit: it has a per-option
_opt_contrib override (unlike the other 9, which fall back to the
question-level _seed/_uniform default automatically) -- omitting an "E"
entry there would KeyError at import time (dict(_opt_contrib[qid][o[0]])).
New option E's dimensional_contributions matched to SEVER-05's existing
"Weak" category (C/D: {authority_asset: -0.30, authority_liability: 0.30})
since the new text ("operating on assumption... hasn't been tested") is
semantically the same untested/unverified category as C/D, not A/B's
tested/documented "Strong" category. Flagged for confirmation, not
silently decided -- a real content judgment, not a mechanical default.

Usage:
  python tools/patch_track_a_duration_band_additions.py --dry-run
  python tools/patch_track_a_duration_band_additions.py --write
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
# _QDATA -- new option E on each question's answer_options list
# ============================================================================

edit(
    '            ("D", "I\'m not sure leadership has seen it the same way I\'m describing it.", False, None),\n'
    '        ],\n'
    '        ["the_diversity_ceiling"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-02",',
    '            ("D", "I\'m not sure leadership has seen it the same way I\'m describing it.", False, None),\n'
    '            ("E", "It\'s been recognized in some form for years without real traction.", False, None),\n'
    '        ],\n'
    '        ["the_diversity_ceiling"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-02",',
)

edit(
    '            ("D", "It\'s pervasive — this is how the organization operates generally.", False, None),\n'
    '        ],\n'
    '        ["built_to_fail", "the_undefined_role", "decision_paralysis"],',
    '            ("D", "It\'s pervasive — this is how the organization operates generally.", False, None),\n'
    '            ("E", "It\'s been this way for as long as I can remember — not a recent shift.", False, None),\n'
    '        ],\n'
    '        ["built_to_fail", "the_undefined_role", "decision_paralysis"],',
)

edit(
    '            ("D", "It\'s become normal — people have built workarounds rather than expecting it to change.", False, None),\n'
    '        ],\n'
    '        ["decision_paralysis"],',
    '            ("D", "It\'s become normal — people have built workarounds rather than expecting it to change.", False, None),\n'
    '            ("E", "It\'s been this way for as long as I can remember.", False, None),\n'
    '        ],\n'
    '        ["decision_paralysis"],',
)

edit(
    '            ("D", "Honestly, we assume it but I\'m not sure we\'ve verified it.", False, None),\n'
    '        ],\n'
    '        ["paper_shield", "leadership_continuity_risk"],',
    '            ("D", "Honestly, we assume it but I\'m not sure we\'ve verified it.", False, None),\n'
    '            ("E", "We\'ve been operating on assumption for a long time — this hasn\'t really been tested or reviewed in years.", False, None),\n'
    '        ],\n'
    '        ["paper_shield", "leadership_continuity_risk"],',
)

edit(
    '            ("D", "We lose our best people regularly to organizations that offer what we can\'t.", False, None),\n'
    '        ],\n'
    '        ["the_dormant_talent", "leadership_continuity_risk"],',
    '            ("D", "We lose our best people regularly to organizations that offer what we can\'t.", False, None),\n'
    '            ("E", "This has been true for years — we\'ve been losing people to this same gap for a long time.", False, None),\n'
    '        ],\n'
    '        ["the_dormant_talent", "leadership_continuity_risk"],',
)

edit(
    '            ("D", "I\'m not sure.", False, None),\n'
    '        ],\n'
    '        ["silosolation", "the_fracture"],',
    '            ("D", "I\'m not sure.", False, None),\n'
    '            ("E", "It\'s been this way for as long as anyone can remember — nobody experiences it as new.", False, None),\n'
    '        ],\n'
    '        ["silosolation", "the_fracture"],',
)

edit(
    '            ("D", "It\'s visible at every level and nobody is sure how to change it.", False, None),\n'
    '        ],\n'
    '        ["culture_drift", "identity_erosion", "the_culture_that_wasnt"],',
    '            ("D", "It\'s visible at every level and nobody is sure how to change it.", False, None),\n'
    '            ("E", "It\'s been this way long enough that it feels like just how we operate.", False, None),\n'
    '        ],\n'
    '        ["culture_drift", "identity_erosion", "the_culture_that_wasnt"],',
)

edit(
    '            ("D", "Not really — we settled and moved on without examining what caused it.", False, None),\n'
    '        ],\n'
    '        ["the_unsolved_problem"],',
    '            ("D", "Not really — we settled and moved on without examining what caused it.", False, None),\n'
    '            ("E", "It\'s been an open question for as long as I can remember — we\'ve never really pinned it down.", False, None),\n'
    '        ],\n'
    '        ["the_unsolved_problem"],',
)

edit(
    '            ("D", "I genuinely don\'t know — we haven\'t examined it closely enough.", False, None),\n'
    '        ],\n'
    '        ["the_diversity_ceiling"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-13",',
    '            ("D", "I genuinely don\'t know — we haven\'t examined it closely enough.", False, None),\n'
    '            ("E", "This has been the pattern for years, not something new.", False, None),\n'
    '        ],\n'
    '        ["the_diversity_ceiling"],\n'
    '        False,\n'
    '    ),\n'
    '    (\n'
    '        "SEVER-13",',
)

edit(
    '            ("D", "The findings were addressed in how we talked about them but not in what we did.", False, None),\n'
    '        ],\n'
    '        ["narrative_lock", "the_broken_compass"],',
    '            ("D", "The findings were addressed in how we talked about them but not in what we did.", False, None),\n'
    '            ("E", "It\'s simply how things work here — this has been the pattern for years, not a one-time lapse.", False, None),\n'
    '        ],\n'
    '        ["narrative_lock", "the_broken_compass"],',
)


# ============================================================================
# _severity_input_tags -- full-block replacement (some D-values duplicate
# across blocks, e.g. SEVER-02/03/10 and SEVER-11/13, so the D-line alone
# isn't a safe anchor -- anchoring on the full unique block instead)
# ============================================================================

edit(
    '        "SEVER-01": {  # STRONG -- awareness/naming (the_diversity_ceiling)\n'
    '            "A": {"named_condition": True},\n'
    '            "B": {"named_condition": True},\n'
    '            "C": {"named_condition": False},\n'
    '            "D": {"named_condition": False},\n'
    '        },',
    '        "SEVER-01": {  # STRONG -- awareness/naming (the_diversity_ceiling)\n'
    '            "A": {"named_condition": True},\n'
    '            "B": {"named_condition": True},\n'
    '            "C": {"named_condition": False},\n'
    '            "D": {"named_condition": False},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)

edit(
    '        "SEVER-02": {  # STRONG -- breadth (built_to_fail / the_undefined_role / decision_paralysis)\n'
    '            "A": {"population_band": "under_10pct"},\n'
    '            "B": {"population_band": "under_10pct"},\n'
    '            "C": {"population_band": "10_30pct"},\n'
    '            "D": {"population_band": "30pct_plus"},\n'
    '        },',
    '        "SEVER-02": {  # STRONG -- breadth (built_to_fail / the_undefined_role / decision_paralysis)\n'
    '            "A": {"population_band": "under_10pct"},\n'
    '            "B": {"population_band": "under_10pct"},\n'
    '            "C": {"population_band": "10_30pct"},\n'
    '            "D": {"population_band": "30pct_plus"},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)

edit(
    '        "SEVER-03": {  # STRONG -- breadth (decision_paralysis)\n'
    '            "A": {"population_band": "under_10pct"},\n'
    '            "B": {"population_band": "10_30pct"},\n'
    '            "C": {"population_band": "30pct_plus"},\n'
    '            "D": {"population_band": "30pct_plus"},\n'
    '        },',
    '        "SEVER-03": {  # STRONG -- breadth (decision_paralysis)\n'
    '            "A": {"population_band": "under_10pct"},\n'
    '            "B": {"population_band": "10_30pct"},\n'
    '            "C": {"population_band": "30pct_plus"},\n'
    '            "D": {"population_band": "30pct_plus"},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)

edit(
    '        "SEVER-05": {  # MODERATE -- verification confidence, reinterpreted as named_condition\n'
    '            "A": {"named_condition": True},          # tested and confirmed\n'
    '            "B": {"named_condition": True},           # documented and reviewed\n'
    '            "C": {"named_condition": False},          # unconfirmed\n'
    '            "D": {"named_condition": False},          # assumed, unverified\n'
    '        },',
    '        "SEVER-05": {  # MODERATE -- verification confidence, reinterpreted as named_condition\n'
    '            "A": {"named_condition": True},          # tested and confirmed\n'
    '            "B": {"named_condition": True},           # documented and reviewed\n'
    '            "C": {"named_condition": False},          # unconfirmed\n'
    '            "D": {"named_condition": False},          # assumed, unverified\n'
    '            "E": {"duration_band": "18mo_plus"},      # untested/unverified for years -- Weak category\n'
    '        },',
)

edit(
    '        "SEVER-07": {  # STRONG -- realized turnover as financial indicator (the_dormant_talent / leadership_continuity_risk)\n'
    '            "A": {"financial_indicators": False},\n'
    '            "B": {"financial_indicators": False},\n'
    '            "C": {"financial_indicators": True},      # real departures already occurred\n'
    '            "D": {"financial_indicators": True},\n'
    '        },',
    '        "SEVER-07": {  # STRONG -- realized turnover as financial indicator (the_dormant_talent / leadership_continuity_risk)\n'
    '            "A": {"financial_indicators": False},\n'
    '            "B": {"financial_indicators": False},\n'
    '            "C": {"financial_indicators": True},      # real departures already occurred\n'
    '            "D": {"financial_indicators": True},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)

edit(
    '        "SEVER-08": {  # WEAK -- root-cause diagnosis, reinterpreted as named_condition (silosolation / the_fracture)\n'
    '            "A": {"named_condition": True},\n'
    '            "B": {"named_condition": True},\n'
    '            "C": {"named_condition": True},\n'
    '            "D": {"named_condition": False},          # "I\'m not sure" -- no diagnosis given\n'
    '        },',
    '        "SEVER-08": {  # WEAK -- root-cause diagnosis, reinterpreted as named_condition (silosolation / the_fracture)\n'
    '            "A": {"named_condition": True},\n'
    '            "B": {"named_condition": True},\n'
    '            "C": {"named_condition": True},\n'
    '            "D": {"named_condition": False},          # "I\'m not sure" -- no diagnosis given\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)

edit(
    '        "SEVER-10": {  # MODERATE -- awareness breadth, reinterpreted as population_band (culture_drift / identity_erosion / the_culture_that_wasnt)\n'
    '            "A": {"population_band": "under_10pct"},\n'
    '            "B": {"population_band": "under_10pct"},\n'
    '            "C": {"population_band": "10_30pct"},\n'
    '            "D": {"population_band": "30pct_plus"},\n'
    '        },',
    '        "SEVER-10": {  # MODERATE -- awareness breadth, reinterpreted as population_band (culture_drift / identity_erosion / the_culture_that_wasnt)\n'
    '            "A": {"population_band": "under_10pct"},\n'
    '            "B": {"population_band": "under_10pct"},\n'
    '            "C": {"population_band": "10_30pct"},\n'
    '            "D": {"population_band": "30pct_plus"},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)

edit(
    '        "SEVER-11": {  # STRONG -- root-cause resolution outcome (the_unsolved_problem)\n'
    '            "A": {"prior_failed_resolution": False},  # identified and addressed\n'
    '            "B": {"prior_failed_resolution": True},\n'
    '            "C": {"prior_failed_resolution": True},\n'
    '            "D": {"prior_failed_resolution": True},\n'
    '        },',
    '        "SEVER-11": {  # STRONG -- root-cause resolution outcome (the_unsolved_problem)\n'
    '            "A": {"prior_failed_resolution": False},  # identified and addressed\n'
    '            "B": {"prior_failed_resolution": True},\n'
    '            "C": {"prior_failed_resolution": True},\n'
    '            "D": {"prior_failed_resolution": True},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)

edit(
    '        "SEVER-12": {  # WEAK -- only 1 of 4 options discriminates (the_diversity_ceiling)\n'
    '            "A": {"financial_indicators": False},\n'
    '            "B": {"financial_indicators": False},\n'
    '            "C": {"financial_indicators": True},      # realized attrition\n'
    '            "D": {"financial_indicators": False},\n'
    '        },',
    '        "SEVER-12": {  # WEAK -- only 1 of 4 options discriminates (the_diversity_ceiling)\n'
    '            "A": {"financial_indicators": False},\n'
    '            "B": {"financial_indicators": False},\n'
    '            "C": {"financial_indicators": True},      # realized attrition\n'
    '            "D": {"financial_indicators": False},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)

edit(
    '        "SEVER-13": {  # non-discriminating -- see note above (narrative_lock / the_broken_compass)\n'
    '            "A": {"prior_failed_resolution": True},\n'
    '            "B": {"prior_failed_resolution": True},\n'
    '            "C": {"prior_failed_resolution": True},\n'
    '            "D": {"prior_failed_resolution": True},\n'
    '        },',
    '        "SEVER-13": {  # non-discriminating -- see note above (narrative_lock / the_broken_compass)\n'
    '            "A": {"prior_failed_resolution": True},\n'
    '            "B": {"prior_failed_resolution": True},\n'
    '            "C": {"prior_failed_resolution": True},\n'
    '            "D": {"prior_failed_resolution": True},\n'
    '            "E": {"duration_band": "18mo_plus"},\n'
    '        },',
)


# ============================================================================
# _opt_contrib -- SEVER-05 only, needed to avoid KeyError at import time
# ============================================================================

edit(
    '        "SEVER-05": {  # Q23-A probe. Weak response = retroactive base downgrade.\n'
    '            "A": {**_z},                                                           # Strong — tested; Q23-A base stands\n'
    '            "B": {**_z},                                                           # Strong — documented; Q23-A base stands\n'
    '            "C": {**_z, "authority_asset": -0.30, "authority_liability": 0.30},    # Weak — retroactive downgrade\n'
    '            "D": {**_z, "authority_asset": -0.30, "authority_liability": 0.30},    # Weak — retroactive downgrade\n'
    '        },',
    '        "SEVER-05": {  # Q23-A probe. Weak response = retroactive base downgrade.\n'
    '            "A": {**_z},                                                           # Strong — tested; Q23-A base stands\n'
    '            "B": {**_z},                                                           # Strong — documented; Q23-A base stands\n'
    '            "C": {**_z, "authority_asset": -0.30, "authority_liability": 0.30},    # Weak — retroactive downgrade\n'
    '            "D": {**_z, "authority_asset": -0.30, "authority_liability": 0.30},    # Weak — retroactive downgrade\n'
    '            "E": {**_z, "authority_asset": -0.30, "authority_liability": 0.30},    # Weak — untested for years, same category as C/D\n'
    '        },',
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
