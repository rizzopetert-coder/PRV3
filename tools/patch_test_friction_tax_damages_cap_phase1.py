"""
tools/test_friction_tax.py: new tests for the damages_cap_treatment
Phase 1 build (prompts/damages-cap-treatment-phase1-spec.md).

Covers: resolve_damages_treatment() for one real state per each of the
5 damages_cap_treatment values (a genuine federal_cap_applies state,
IL, not AZ -- AZ is no_damages_available as of this session's earlier
fix), the empty-list and no-CONFIRMED-entry fallback, and a genuine
multi-state tie (order-independent, confirming highest-exposure-wins,
not first-in-list); the no_damages_available headcount>=15 vs <15
branch, using WY (real coverage threshold=2, so headcount=14 clears
WY's own threshold but must still fail the federal 15-employee floor
-- distinguishes the new branch from the pre-existing coverage gate,
which a state whose own threshold is already >=15 could not do);
the flat-cap clamp actually binding for ID under Cluster 1 (score=2
diagnostic state -- _legal_score_fraction's own formula means score=2
always returns exactly curve.ceiling, so the clamp is directly
visible in the returned dollar_range); and VA's Cluster 4b no-op
explicitly asserted, not assumed (ceiling stays the generic $300,000
because VA's $350,000 cap is above it, while is_floor is still True).

Uses the private functions directly via the _ft module alias
(_ft._single_state_legal_pricing, _ft._cluster_4_curve_for_org_type),
matching this file's own established convention for testing internals
precisely -- compute_legal_compliance_exposure()'s own aggregate
output dict does not surface is_floor (a real, flagged-not-fixed gap;
see the session report), so the aggregate function can't be used to
test items 3/4 directly.

Usage:
    python tools/patch_test_friction_tax_damages_cap_phase1.py --dry-run
    python tools/patch_test_friction_tax_damages_cap_phase1.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

IMPORT_OLD = '''    STATE_COVERAGE_THRESHOLDS,
    StateCoverageThreshold,
    CoverageResult,
    resolve_coverage_gate,
    LegalPricingStatus,
)'''

IMPORT_NEW = '''    STATE_COVERAGE_THRESHOLDS,
    StateCoverageThreshold,
    CoverageResult,
    resolve_coverage_gate,
    LegalPricingStatus,
    resolve_damages_treatment,
)'''

TAIL_OLD = '''# -- Results ---------------------------------------------------------------------

print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")'''

TAIL_NEW = '''# -- 41. resolve_damages_treatment() -- one real state per value, plus fallback --

check(
    "sanity: CA is uncapped, TX is state_specific_tiers, FL is state_specific_flat, "
    "IL is federal_cap_applies, OK is no_damages_available -- needed for the checks below",
    (
        STATE_COVERAGE_THRESHOLDS["CA"].damages_cap_treatment == "uncapped"
        and STATE_COVERAGE_THRESHOLDS["TX"].damages_cap_treatment == "state_specific_tiers"
        and STATE_COVERAGE_THRESHOLDS["FL"].damages_cap_treatment == "state_specific_flat"
        and STATE_COVERAGE_THRESHOLDS["IL"].damages_cap_treatment == "federal_cap_applies"
        and STATE_COVERAGE_THRESHOLDS["OK"].damages_cap_treatment == "no_damages_available"
    ),
    f"got {[STATE_COVERAGE_THRESHOLDS[s].damages_cap_treatment for s in ('CA', 'TX', 'FL', 'IL', 'OK')]}",
)
check(
    "resolve_damages_treatment(['CA']) == 'uncapped'",
    resolve_damages_treatment(["CA"]) == "uncapped",
    f"got {resolve_damages_treatment(['CA'])!r}",
)
check(
    "resolve_damages_treatment(['TX']) == 'state_specific_tiers'",
    resolve_damages_treatment(["TX"]) == "state_specific_tiers",
    f"got {resolve_damages_treatment(['TX'])!r}",
)
check(
    "resolve_damages_treatment(['FL']) == 'state_specific_flat'",
    resolve_damages_treatment(["FL"]) == "state_specific_flat",
    f"got {resolve_damages_treatment(['FL'])!r}",
)
check(
    "resolve_damages_treatment(['IL']) == 'federal_cap_applies'",
    resolve_damages_treatment(["IL"]) == "federal_cap_applies",
    f"got {resolve_damages_treatment(['IL'])!r}",
)
check(
    "resolve_damages_treatment(['OK']) == 'no_damages_available'",
    resolve_damages_treatment(["OK"]) == "no_damages_available",
    f"got {resolve_damages_treatment(['OK'])!r}",
)
check(
    "resolve_damages_treatment([]) falls back to 'federal_cap_applies' -- no verified state law in "
    "play means federal law is what actually governs",
    resolve_damages_treatment([]) == "federal_cap_applies",
    f"got {resolve_damages_treatment([])!r}",
)
check(
    "resolve_damages_treatment(['ZZ']) (unrecognized code, no CONFIRMED entry found) also falls back "
    "to 'federal_cap_applies'",
    resolve_damages_treatment(["ZZ"]) == "federal_cap_applies",
    f"got {resolve_damages_treatment(['ZZ'])!r}",
)
check(
    "resolve_damages_treatment(['FL', 'CA']) == 'uncapped' -- highest-exposure-wins picks CA over "
    "FL's state_specific_flat, order given as flat-then-uncapped",
    resolve_damages_treatment(["FL", "CA"]) == "uncapped",
    f"got {resolve_damages_treatment(['FL', 'CA'])!r}",
)
check(
    "resolve_damages_treatment(['CA', 'FL']) == 'uncapped' too -- confirms order-independence, not a "
    "first-in-list artifact from the previous check",
    resolve_damages_treatment(["CA", "FL"]) == "uncapped",
    f"got {resolve_damages_treatment(['CA', 'FL'])!r}",
)


# -- 42. no_damages_available federal-floor branch (Cluster 1, headcount>=15 vs <15) --

check(
    "sanity: WY's own coverage threshold is 2 (well below 15) and is no_damages_available -- needed "
    "so headcount=14 below tests the NEW federal-floor branch specifically, not the pre-existing "
    "coverage gate (which WY's own low threshold would already clear at headcount=14)",
    STATE_COVERAGE_THRESHOLDS["WY"].thresholds["general"] == 2
    and STATE_COVERAGE_THRESHOLDS["WY"].damages_cap_treatment == "no_damages_available",
    f"got threshold={STATE_COVERAGE_THRESHOLDS['WY'].thresholds['general']!r}, "
    f"treatment={STATE_COVERAGE_THRESHOLDS['WY'].damages_cap_treatment!r}",
)
_r_ndamb_below = _ft._single_state_legal_pricing(
    "the_paper_tiger", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=14, jurisdictions=["WY"],
)
check(
    "Cluster 1, no_damages_available + headcount=14 (< federal 15-employee floor): NOT_APPLICABLE, "
    "dollar_range=None, coverage_confidence='CONFIRMED' -- genuinely zero exposure, not unpriced-but-real",
    _r_ndamb_below.status == LegalPricingStatus.NOT_APPLICABLE
    and _r_ndamb_below.dollar_range is None
    and _r_ndamb_below.coverage_confidence == "CONFIRMED",
    f"got {_r_ndamb_below}",
)
_r_ndamb_at = _ft._single_state_legal_pricing(
    "the_paper_tiger", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=15, jurisdictions=["WY"],
)
check(
    "Cluster 1, no_damages_available + headcount=15 (clears the federal floor exactly): PRICED "
    "normally against the existing generic Cluster 1 curve, same as any federal_cap_applies state",
    _r_ndamb_at.status == LegalPricingStatus.PRICED
    and _r_ndamb_at.dollar_range == (450_000.0, 450_000.0),
    f"got {_r_ndamb_at}",
)


# -- 43. state_specific_flat clamp -- binds for ID under Cluster 1, does NOT bind for VA under Cluster 4b --

check(
    "sanity: ID flat_cap=$1,000, VA flat_cap=$350,000 -- needed for the two checks below",
    STATE_COVERAGE_THRESHOLDS["ID"].flat_cap == 1_000.0
    and STATE_COVERAGE_THRESHOLDS["VA"].flat_cap == 350_000.0,
    f"got ID={STATE_COVERAGE_THRESHOLDS['ID'].flat_cap!r}, VA={STATE_COVERAGE_THRESHOLDS['VA'].flat_cap!r}",
)
_r_id_clamp = _ft._single_state_legal_pricing(
    "the_paper_tiger", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["ID"],
)
check(
    "Cluster 1, ID (state_specific_flat, $1,000 cap): the generic $450,000 ceiling is clamped down to "
    "ID's real $1,000 cap -- the clamp actually binds here, confirmed by the returned dollar_range, "
    "not assumed. is_floor=True (the figure reflects only ID's punitive-specific cap, not full exposure)",
    _r_id_clamp.status == LegalPricingStatus.PRICED
    and _r_id_clamp.dollar_range == (1_000.0, 1_000.0)
    and _r_id_clamp.is_floor is True,
    f"got {_r_id_clamp}",
)
_r_va_noop = _ft._cluster_4_curve_for_org_type("Founder-led", "1000+", 1000, ["VA"])
check(
    "Cluster 4b, VA (state_specific_flat, $350,000 cap) at the '1000+' bucket (generic ceiling "
    "$300,000): the clamp is a genuine NO-OP here -- min(300000, 350000) = 300000, confirmed "
    "explicitly by the returned curve, not assumed just because the other 3 states' clamps bind. "
    "is_floor is still True, since the underlying ambiguity (does the generic ceiling reflect VA's "
    "real total exposure?) doesn't depend on whether the clamp happened to change the number",
    _r_va_noop.status == LegalPricingStatus.PRICED
    and _r_va_noop.curve.ceiling == 300_000.0
    and _r_va_noop.is_floor is True,
    f"got {_r_va_noop}",
)


# -- 44. uncapped is_floor flag -- Cluster 1 and Cluster 4b both, ceiling itself unchanged --

_r_c1_uncapped = _ft._single_state_legal_pricing(
    "the_paper_tiger", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["CA"],
)
check(
    "Cluster 1, CA (uncapped): is_floor=True, dollar_range unaffected (still the generic $450,000 "
    "ceiling -- CA has no cap of its own to clamp to, the figure is a floor, not a hard ceiling)",
    _r_c1_uncapped.status == LegalPricingStatus.PRICED
    and _r_c1_uncapped.dollar_range == (450_000.0, 450_000.0)
    and _r_c1_uncapped.is_floor is True,
    f"got {_r_c1_uncapped}",
)
_r_c4b_uncapped = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 300, ["CA"])
check(
    "Cluster 4b, CA (uncapped), '250-499' bucket: is_floor=True, ceiling unchanged at the generic "
    "$200,000 (same figure as this file's own pre-existing hr_capture/250-499 test, confirming this "
    "change doesn't alter the ceiling itself, only adds the flag)",
    _r_c4b_uncapped.status == LegalPricingStatus.PRICED
    and _r_c4b_uncapped.curve.ceiling == 200_000.0
    and _r_c4b_uncapped.is_floor is True,
    f"got {_r_c4b_uncapped}",
)
_r_c2_no_floor = _ft._single_state_legal_pricing(
    "the_arbitrary_standard", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["CA"],
)
check(
    "sanity: the_arbitrary_standard is a real Cluster 2 state with a non-zero legal score, needed for "
    "the check below",
    _ft.LEGAL_COMPLIANCE_CLUSTER.get("the_arbitrary_standard") == 2
    and _ft.STATE_MULTIPLIERS["the_arbitrary_standard"].criteria["legal"].score > 0,
    f"got cluster={_ft.LEGAL_COMPLIANCE_CLUSTER.get('the_arbitrary_standard')!r}, "
    f"score={_ft.STATE_MULTIPLIERS['the_arbitrary_standard'].criteria['legal'].score!r}",
)
check(
    "Cluster 2, CA (uncapped): is_floor is NOT set (stays False) -- Cluster 2's dollar values are two "
    "fixed discrete tiers, not a curve with a floor/ceiling, so the floor-not-ceiling question doesn't "
    "apply regardless of damages_cap_treatment",
    _r_c2_no_floor.status == LegalPricingStatus.PRICED and _r_c2_no_floor.is_floor is False,
    f"got {_r_c2_no_floor}",
)


print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")'''

EDITS = [
    ('import resolve_damages_treatment', IMPORT_OLD, IMPORT_NEW),
    ('append damages_cap_treatment Phase 1 tests', TAIL_OLD, TAIL_NEW),
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
