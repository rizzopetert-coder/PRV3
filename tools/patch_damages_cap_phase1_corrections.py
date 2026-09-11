"""
engine/friction_tax.py: two corrections to the damages_cap_treatment
Phase 1 build, both found in review before commit.

1. state_specific_tiers gets the same is_floor=True treatment as
   uncapped, in both Cluster 1 and Cluster 4b (Cluster 2 stays exempt,
   per its existing structural exemption -- fixed discrete tiers, no
   curve to flag). Restores item 5's original intent (an explicit
   caveat signal for the 9 state_specific_tiers states, since Phase 1
   has no real schema for their tiered/formula data yet) that was
   dropped in a compressed instruction, not missed independently.

2. _DAMAGES_TREATMENT_PRIORITY's tie between state_specific_tiers and
   state_specific_flat (both rank 3) meant a multi-jurisdiction
   selection containing both could silently suppress the flat state's
   real, working clamp depending on input order alone -- confirmed as
   a real bug, not a theoretical one, since strict `>` in
   resolve_damages_treatment()'s loop makes the FIRST-encountered
   tied value win. Broken deterministically in favor of
   state_specific_flat (it has a real, working clamp mechanism today
   via _resolve_flat_cap(); state_specific_tiers has none until Phase
   2) -- renumbered the whole table to a clean 5/4/3/2/1 sequence
   rather than using a fractional rank, keeping the dict's own
   dict[str, int] annotation honest. Docstring's prior claim ("this
   function doesn't need to break a tie between the two shapes") was
   wrong and is corrected to explain the new deterministic ranking.

Usage:
    python tools/patch_damages_cap_phase1_corrections.py --dry-run
    python tools/patch_damages_cap_phase1_corrections.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

# ---- Correction 2: priority table + docstring ------------------------------

PRIORITY_OLD = '''_DAMAGES_TREATMENT_PRIORITY: dict[str, int] = {
    "uncapped": 4,
    "state_specific_tiers": 3,
    "state_specific_flat": 3,
    "federal_cap_applies": 2,
    "no_damages_available": 1,
}


def resolve_damages_treatment(jurisdictions: list[str]) -> str:
    """
    Highest-exposure-wins damages_cap_treatment across the CONFIRMED-
    confidence jurisdictions in the input: uncapped > state_specific_tiers
    / state_specific_flat (peers -- both mean "a real independent state
    cap exists"; this function doesn't need to break a tie between the
    two shapes, since a caller cares whether a cap exists and how it's
    shaped, not which shape wins a multi-state tie) > federal_cap_applies
    > no_damages_available.'''

PRIORITY_NEW = '''_DAMAGES_TREATMENT_PRIORITY: dict[str, int] = {
    "uncapped": 5,
    "state_specific_flat": 4,
    "state_specific_tiers": 3,
    "federal_cap_applies": 2,
    "no_damages_available": 1,
}


def resolve_damages_treatment(jurisdictions: list[str]) -> str:
    """
    Highest-exposure-wins damages_cap_treatment across the CONFIRMED-
    confidence jurisdictions in the input: uncapped > state_specific_flat
    > state_specific_tiers > federal_cap_applies > no_damages_available.

    CORRECTED (found in review before commit): state_specific_tiers and
    state_specific_flat were originally ranked as peers (both mean "a
    real independent state cap exists," with a comment claiming no tie-
    break was needed since a caller only cares whether a cap exists,
    not which shape wins). That was wrong -- with strict `>` deciding
    ties by input order, a multi-jurisdiction selection containing both
    a tiers state and a flat state could silently suppress the flat
    state's real, working clamp depending on which jurisdiction
    happened to be listed first, a real bug, not a theoretical one.
    state_specific_flat now ranks strictly above state_specific_tiers,
    deterministically: it has a real, working clamp mechanism today
    (_resolve_flat_cap(), Phase 1 item 4), while state_specific_tiers
    has no mechanism at all until Phase 2 (item 5, no schema exists yet
    for tiered/formula cap data) -- a caller should get the treatment
    whose downstream clamp actually functions, not whichever state
    happened to be listed first.'''

# ---- Correction 1: is_floor, Cluster 1 -------------------------------------

CLUSTER1_ISFLOOR_OLD = '''        v = _legal_score_fraction(curve, score)
        is_floor = treatment == "uncapped" or flat_cap is not None
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
            is_floor=is_floor)'''

CLUSTER1_ISFLOOR_NEW = '''        v = _legal_score_fraction(curve, score)
        is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
            is_floor=is_floor)'''

# ---- Correction 1: is_floor, Cluster 4b ------------------------------------

CLUSTER4B_ISFLOOR_OLD = '''    flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
    final_ceiling = ceiling if flat_cap is None else min(ceiling, flat_cap)
    is_floor = treatment == "uncapped" or flat_cap is not None'''

CLUSTER4B_ISFLOOR_NEW = '''    flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
    final_ceiling = ceiling if flat_cap is None else min(ceiling, flat_cap)
    is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None'''

EDITS = [
    ('priority table renumbered + docstring corrected', PRIORITY_OLD, PRIORITY_NEW),
    ('Cluster 1 is_floor includes state_specific_tiers', CLUSTER1_ISFLOOR_OLD, CLUSTER1_ISFLOOR_NEW),
    ('Cluster 4b is_floor includes state_specific_tiers', CLUSTER4B_ISFLOOR_OLD, CLUSTER4B_ISFLOOR_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
