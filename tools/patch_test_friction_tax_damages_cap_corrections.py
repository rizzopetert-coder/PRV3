"""
tools/test_friction_tax.py: tests for the two damages_cap_treatment
Phase 1 corrections (tools/patch_damages_cap_phase1_corrections.py).

1. resolve_damages_treatment(["TX", "FL"]) / (["FL", "TX"]) -- a
   genuine tie between state_specific_tiers (TX) and state_specific_flat
   (FL), both orders, confirming the corrected deterministic ranking
   (flat now strictly outranks tiers). The prior order-independence
   test (CA/FL) never actually exercised a tie -- uncapped always beat
   flat regardless of rank values, so it couldn't have caught the bug
   the priority-table fix addresses. This one can.
2. TX (state_specific_tiers) under Cluster 1: is_floor is now True,
   restoring item 5's original caveat-signal intent.

Usage:
    python tools/patch_test_friction_tax_damages_cap_corrections.py --dry-run
    python tools/patch_test_friction_tax_damages_cap_corrections.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

TIE_ANCHOR_OLD = '''check(
    "resolve_damages_treatment(['CA', 'FL']) == 'uncapped' too -- confirms order-independence, not a "
    "first-in-list artifact from the previous check",
    resolve_damages_treatment(["CA", "FL"]) == "uncapped",
    f"got {resolve_damages_treatment(['CA', 'FL'])!r}",
)'''

TIE_ANCHOR_NEW = '''check(
    "resolve_damages_treatment(['CA', 'FL']) == 'uncapped' too -- confirms order-independence, not a "
    "first-in-list artifact from the previous check",
    resolve_damages_treatment(["CA", "FL"]) == "uncapped",
    f"got {resolve_damages_treatment(['CA', 'FL'])!r}",
)
check(
    "sanity: TX is state_specific_tiers with no flat_cap -- needed for the genuine tie check below",
    STATE_COVERAGE_THRESHOLDS["TX"].damages_cap_treatment == "state_specific_tiers"
    and STATE_COVERAGE_THRESHOLDS["TX"].flat_cap is None,
    f"got treatment={STATE_COVERAGE_THRESHOLDS['TX'].damages_cap_treatment!r}, "
    f"flat_cap={STATE_COVERAGE_THRESHOLDS['TX'].flat_cap!r}",
)
check(
    "resolve_damages_treatment(['TX', 'FL']) == 'state_specific_flat' -- a genuine tie (TX=tiers, "
    "FL=flat, previously equal rank), correction: flat now strictly outranks tiers since it has a "
    "real, working clamp mechanism today and tiers doesn't. This is the actual tie the CA/FL checks "
    "above never exercised, since uncapped always outranked flat regardless of the tiers/flat rank "
    "values -- the bug this corrects couldn't have been caught by that pair",
    resolve_damages_treatment(["TX", "FL"]) == "state_specific_flat",
    f"got {resolve_damages_treatment(['TX', 'FL'])!r}",
)
check(
    "resolve_damages_treatment(['FL', 'TX']) == 'state_specific_flat' too -- genuine order-independence "
    "on the actual tied pair, not assumed from the uncapped/flat checks above",
    resolve_damages_treatment(["FL", "TX"]) == "state_specific_flat",
    f"got {resolve_damages_treatment(['FL', 'TX'])!r}",
)'''

ISFLOOR_ANCHOR_OLD = '''check(
    "Cluster 1, CA (uncapped): is_floor=True, dollar_range unaffected (still the generic $450,000 "
    "ceiling -- CA has no cap of its own to clamp to, the figure is a floor, not a hard ceiling)",
    _r_c1_uncapped.status == LegalPricingStatus.PRICED
    and _r_c1_uncapped.dollar_range == (450_000.0, 450_000.0)
    and _r_c1_uncapped.is_floor is True,
    f"got {_r_c1_uncapped}",
)'''

ISFLOOR_ANCHOR_NEW = '''check(
    "Cluster 1, CA (uncapped): is_floor=True, dollar_range unaffected (still the generic $450,000 "
    "ceiling -- CA has no cap of its own to clamp to, the figure is a floor, not a hard ceiling)",
    _r_c1_uncapped.status == LegalPricingStatus.PRICED
    and _r_c1_uncapped.dollar_range == (450_000.0, 450_000.0)
    and _r_c1_uncapped.is_floor is True,
    f"got {_r_c1_uncapped}",
)
_r_c1_tiers = _ft._single_state_legal_pricing(
    "the_paper_tiger", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["TX"],
)
check(
    "CORRECTION: Cluster 1, TX (state_specific_tiers): is_floor is now True -- restores item 5's "
    "original caveat-signal intent (no schema exists yet for TX's own real tiered cap, so the generic "
    "$450,000 ceiling shown is a placeholder, not a verified figure, same reasoning as uncapped states)",
    _r_c1_tiers.status == LegalPricingStatus.PRICED
    and _r_c1_tiers.dollar_range == (450_000.0, 450_000.0)
    and _r_c1_tiers.is_floor is True,
    f"got {_r_c1_tiers}",
)'''

EDITS = [
    ('resolve_damages_treatment TX/FL genuine tie', TIE_ANCHOR_OLD, TIE_ANCHOR_NEW),
    ('Cluster 1 TX is_floor now True', ISFLOOR_ANCHOR_OLD, ISFLOOR_ANCHOR_NEW),
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
