"""
tools/test_friction_tax.py: section 48, tests for damages_cap_treatment
Phase 2b (tools/patch_damages_cap_phase2b_oh_build.py).

1. _oh_is_small_employer() -- the four boundary combinations from Pete's
   task list, tested directly (not just observed indirectly through an
   identical QUALITATIVE_ONLY output, since both branches resolve to the
   same status today -- this is the only way to meaningfully verify the
   routing logic itself is correct).
2. _oh_drives_tiers_result() -- OH alone, OH+CA (CA outranks), OH+TX
   (genuine tie, documents real input-order behavior), mirroring section
   47's CO helper tests.
3. Integration: OH resolves QUALITATIVE_ONLY in Cluster 1, Cluster 2, and
   Cluster 4b -- all three call sites, not assumed from one.
4. compute_legal_compliance_exposure(): has_unpriced_conditions=True,
   unpriced_state_ids contains the diagnostic state_id, low/high/band
   all None -- same shape as the existing Government/hr_capture
   precedent (~1006-1017), confirming OH's new QUALITATIVE_ONLY path
   produces an identical, already-proven-renderable result shape.

Usage:
    python tools/patch_test_friction_tax_damages_cap_phase2b.py --dry-run
    python tools/patch_test_friction_tax_damages_cap_phase2b.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

ANCHOR_OLD = '''print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")'''

ANCHOR_NEW = '''# -- 48. OH -- QUALITATIVE_ONLY, intake-aware routing (Phase 2b) --

# -- 48a. _oh_is_small_employer() -- the four boundary combinations --

check(
    "_oh_is_small_employer(50, 'Professional Services') is True -- headcount alone clears the "
    "<=100 general small-employer threshold",
    _ft._oh_is_small_employer(50, "Professional Services") is True,
    f"got {_ft._oh_is_small_employer(50, 'Professional Services')!r}",
)
check(
    "_oh_is_small_employer(150, 'Manufacturing & Industrial') is True -- exceeds the general "
    "100 threshold but still clears the manufacturing-specific <=500 threshold",
    _ft._oh_is_small_employer(150, "Manufacturing & Industrial") is True,
    f"got {_ft._oh_is_small_employer(150, 'Manufacturing & Industrial')!r}",
)
check(
    "_oh_is_small_employer(150, 'Professional Services') is False -- same headcount as the check "
    "above, but non-manufacturing industry doesn't get the extended 500 threshold, only the 100 one",
    _ft._oh_is_small_employer(150, "Professional Services") is False,
    f"got {_ft._oh_is_small_employer(150, 'Professional Services')!r}",
)
check(
    "_oh_is_small_employer(600, 'Manufacturing & Industrial') is False -- exceeds even the "
    "manufacturing-specific 500 threshold, general branch governs",
    _ft._oh_is_small_employer(600, "Manufacturing & Industrial") is False,
    f"got {_ft._oh_is_small_employer(600, 'Manufacturing & Industrial')!r}",
)
check(
    "_oh_is_small_employer('', 'Manufacturing & Industrial') is False -- non-numeric/unclassifiable "
    "headcount defaults to the general branch's more conservative statutory mechanics",
    _ft._oh_is_small_employer("", "Manufacturing & Industrial") is False,
    f"got {_ft._oh_is_small_employer('', 'Manufacturing & Industrial')!r}",
)

# -- 48b. _oh_drives_tiers_result() -- mirrors section 47's CO helper tests --

check(
    "sanity: OH is state_specific_tiers, CONFIRMED -- needed for the checks below",
    STATE_COVERAGE_THRESHOLDS["OH"].damages_cap_treatment == "state_specific_tiers"
    and STATE_COVERAGE_THRESHOLDS["OH"].confidence == "CONFIRMED",
    f"got treatment={STATE_COVERAGE_THRESHOLDS['OH'].damages_cap_treatment!r}, "
    f"confidence={STATE_COVERAGE_THRESHOLDS['OH'].confidence!r}",
)
check(
    "_oh_drives_tiers_result(['OH']) is True -- OH alone is unambiguously the driving jurisdiction",
    _ft._oh_drives_tiers_result(["OH"]) is True,
    f"got {_ft._oh_drives_tiers_result(['OH'])!r}",
)
check(
    "_oh_drives_tiers_result(['OH', 'CA']) is False -- CA (uncapped, rank 5) outranks OH "
    "(state_specific_tiers, rank 3), so OH isn't the driving jurisdiction even though present",
    _ft._oh_drives_tiers_result(["OH", "CA"]) is False,
    f"got {_ft._oh_drives_tiers_result(['OH', 'CA'])!r}",
)
check(
    "_oh_drives_tiers_result(['OH', 'TX']) is True -- genuine tie (both state_specific_tiers, rank "
    "3), OH listed first wins by the same inherited input-order tie-break as CO's helper",
    _ft._oh_drives_tiers_result(["OH", "TX"]) is True,
    f"got {_ft._oh_drives_tiers_result(['OH', 'TX'])!r}",
)
check(
    "_oh_drives_tiers_result(['TX', 'OH']) is False -- same tie, opposite input order, TX wins "
    "instead -- confirms the tie-break is genuinely input-order-dependent",
    _ft._oh_drives_tiers_result(["TX", "OH"]) is False,
    f"got {_ft._oh_drives_tiers_result(['TX', 'OH'])!r}",
)

# -- 48c. Integration -- Clusters 1, 2, 4b all resolve OH to QUALITATIVE_ONLY --

_r_oh_c1 = _ft._single_state_legal_pricing(
    "the_paper_tiger", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["OH"],
)
check(
    "Cluster 1, OH: QUALITATIVE_ONLY, dollar_range=None -- no longer falls through to the generic "
    "$450,000 placeholder curve",
    _r_oh_c1.status == LegalPricingStatus.QUALITATIVE_ONLY
    and _r_oh_c1.dollar_range is None,
    f"got {_r_oh_c1}",
)
check(
    "sanity: the_arbitrary_standard is a real Cluster 2 state with a non-zero legal score, needed "
    "for the check below",
    _ft.LEGAL_COMPLIANCE_CLUSTER.get("the_arbitrary_standard") == 2
    and _ft.STATE_MULTIPLIERS["the_arbitrary_standard"].criteria["legal"].score > 0,
    f"got cluster={_ft.LEGAL_COMPLIANCE_CLUSTER.get('the_arbitrary_standard')!r}",
)
_r_oh_c2 = _ft._single_state_legal_pricing(
    "the_arbitrary_standard", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["OH"],
)
check(
    "Cluster 2, OH: QUALITATIVE_ONLY, dollar_range=None -- no longer falls through to the fixed "
    "discrete tiers",
    _r_oh_c2.status == LegalPricingStatus.QUALITATIVE_ONLY
    and _r_oh_c2.dollar_range is None,
    f"got {_r_oh_c2}",
)
_r_oh_c4b = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 300, ["OH"])
check(
    "Cluster 4b, OH: QUALITATIVE_ONLY, curve=None -- no longer falls through to the generic "
    "$200,000 ceiling",
    _r_oh_c4b.status == LegalPricingStatus.QUALITATIVE_ONLY
    and _r_oh_c4b.curve is None,
    f"got {_r_oh_c4b}",
)

# -- 48d. compute_legal_compliance_exposure() -- has_unpriced_conditions, same shape as the -- --
# -- existing Government/hr_capture precedent (~1006-1017), proven renderable via that same path --

_r_oh_aggregate = compute_legal_compliance_exposure(
    state_ids=["the_paper_tiger"],
    org_size=20,
    industry="Professional Services",
    org_type="Founder-led",
    jurisdictions=["OH"],
)
check(
    "compute_legal_compliance_exposure(), OH: low/high/band all None, has_unpriced_conditions=True, "
    "unpriced_state_ids=['the_paper_tiger'] -- identical shape to the Government/hr_capture "
    "precedent already proven to reach engine/contract.py's non-null legal_tail_risk_exposure guard "
    "(low is not None or has_unpriced_conditions) and PrivateOutput.tsx's already-status-agnostic "
    "unpriced-state copy",
    _r_oh_aggregate == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": True, "unpriced_state_ids": ["the_paper_tiger"],
        "coverage_basis": None, "has_partial_jurisdictions": False,
    },
    f"got {_r_oh_aggregate}",
)


print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")'''

EDITS = [
    ('section 48 -- Phase 2b (OH)', ANCHOR_OLD, ANCHOR_NEW),
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
