"""
tools/test_friction_tax.py: section 49, tests for damages_cap_treatment
Phase 2c (tools/patch_damages_cap_phase2c_me_citation.py).

ME's build is data-population-only, zero engine logic change -- same
shape as Phase 2a's AR/DE/TN (section 45), not CO/OH's dedicated-helper
shape. These tests confirm ME's real, now-documented tier boundaries
(100/101, 200/201, 500/501 employees) do NOT change the current generic
placeholder behavior -- proving stability at exactly the headcounts
that will matter if ME's own tiers are ever modeled for real, and
guarding against a future regression at those specific values.

Usage:
    python tools/patch_test_friction_tax_damages_cap_phase2c.py --dry-run
    python tools/patch_test_friction_tax_damages_cap_phase2c.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

ANCHOR_OLD = '''print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")'''

ANCHOR_NEW = '''# -- 49. ME -- verified tier boundaries confirmed stable, generic/unconsumed (Phase 2c) --

check(
    "sanity: ME is state_specific_tiers, CONFIRMED, is_combined_cap defaults False -- needed for "
    "the checks below",
    STATE_COVERAGE_THRESHOLDS["ME"].damages_cap_treatment == "state_specific_tiers"
    and STATE_COVERAGE_THRESHOLDS["ME"].confidence == "CONFIRMED"
    and STATE_COVERAGE_THRESHOLDS["ME"].is_combined_cap is False,
    f"got treatment={STATE_COVERAGE_THRESHOLDS['ME'].damages_cap_treatment!r}, "
    f"confidence={STATE_COVERAGE_THRESHOLDS['ME'].confidence!r}, "
    f"is_combined_cap={STATE_COVERAGE_THRESHOLDS['ME'].is_combined_cap!r}",
)

# Real employment tier table (5 M.R.S. Sec4613(2)(B)(8)(e)(i)-(iv), verified this
# session): $100,000 (15-100) / $300,000 (101-200) / $500,000 (201-500) /
# $1,000,000 (501+). Boundary headcounts tested at each edge -- neither
# Cluster 1 (headcount-invariant curve) nor Cluster 4b (bucket-based, not
# raw-int-based) currently consumes this real table, so every one of these
# should produce the SAME generic placeholder result, confirming that
# stability explicitly rather than assuming it.
for _hc in (100, 101, 200, 201, 500, 501):
    _r_c1_me = _ft._single_state_legal_pricing(
        "the_paper_tiger", org_size="Under 25", industry="Professional Services",
        org_type="Founder-led", headcount=_hc, jurisdictions=["ME"],
    )
    check(
        f"Cluster 1, ME, headcount={_hc} (a real Sec4613(2)(B)(8) tier boundary): still the "
        "generic $450,000 ceiling, is_floor=True -- Phase 2c adds no new pricing logic, ME's real "
        "tier table remains unconsumed, same placeholder treatment as any other tiers state, "
        "stable across this boundary",
        _r_c1_me.status == LegalPricingStatus.PRICED
        and _r_c1_me.dollar_range == (450_000.0, 450_000.0)
        and _r_c1_me.is_floor is True,
        f"got {_r_c1_me}",
    )

_r_c4b_me = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 300, ["ME"])
check(
    "Cluster 4b, ME (state_specific_tiers, Phase 2c): still the generic $200,000 ceiling "
    "('250-499' bucket), is_floor=True -- same reasoning as the Cluster 1 checks above",
    _r_c4b_me.status == LegalPricingStatus.PRICED
    and _r_c4b_me.curve.ceiling == 200_000.0
    and _r_c4b_me.is_floor is True,
    f"got {_r_c4b_me}",
)

_r_me_aggregate = compute_legal_compliance_exposure(
    state_ids=["the_paper_tiger"],
    org_size=20,
    industry="Professional Services",
    org_type="Founder-led",
    jurisdictions=["ME"],
)
check(
    "compute_legal_compliance_exposure(), ME: PRICED via the generic $450,000 Cluster 1 curve, "
    "no unpriced conditions -- confirms ME's aggregate-level shape is the same well-understood "
    "placeholder-with-is_floor path as any other tiers state, not a QUALITATIVE_ONLY/gap status",
    _r_me_aggregate == {
        "low": 450_000.0, "high": 450_000.0, "currency": "USD", "band": "Moderate",
        "has_unpriced_conditions": False, "unpriced_state_ids": [],
        "coverage_basis": "state_specific", "has_partial_jurisdictions": False,
    },
    f"got {_r_me_aggregate}",
)


print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")'''

EDITS = [
    ('section 49 -- Phase 2c (ME)', ANCHOR_OLD, ANCHOR_NEW),
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
