"""
tools/test_friction_tax.py: sections 45-47, tests for damages_cap_treatment
Phase 2a (tools/patch_damages_cap_phase2a_build.py).

45. AR/DE/TN -- confirm still fully generic/unconsumed (is_floor=True,
    is_combined_cap defaults False), demonstrating rather than assuming
    the "zero code changes needed" finding.
46. MD/MO -- is_combined_cap=True confirmed on the data entries; spot
    check a couple of the other 7 tiers states default to False.
47. CO -- Cluster 4b at headcount=14 vs 15 (is_floor True -> False,
    ceiling numerically unchanged); direct _co_drives_federal_tier_
    deferral() tests: CO alone, CO+CA (CA outranks CO), CO+TX (the
    real, documented tie-order behavior).

Usage:
    python tools/patch_test_friction_tax_damages_cap_phase2a.py --dry-run
    python tools/patch_test_friction_tax_damages_cap_phase2a.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

ANCHOR_OLD = '''print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")'''

ANCHOR_NEW = '''# -- 45. AR/DE/TN -- confirmed still fully generic/unconsumed (Phase 2a) --

for _sid in ("AR", "DE", "TN"):
    check(
        f"sanity: {_sid} is state_specific_tiers, CONFIRMED, is_combined_cap defaults False -- "
        "needed for the checks below",
        STATE_COVERAGE_THRESHOLDS[_sid].damages_cap_treatment == "state_specific_tiers"
        and STATE_COVERAGE_THRESHOLDS[_sid].confidence == "CONFIRMED"
        and STATE_COVERAGE_THRESHOLDS[_sid].is_combined_cap is False,
        f"got treatment={STATE_COVERAGE_THRESHOLDS[_sid].damages_cap_treatment!r}, "
        f"confidence={STATE_COVERAGE_THRESHOLDS[_sid].confidence!r}, "
        f"is_combined_cap={STATE_COVERAGE_THRESHOLDS[_sid].is_combined_cap!r}",
    )
    _r_c1 = _ft._single_state_legal_pricing(
        "the_paper_tiger", org_size="Under 25", industry="Professional Services",
        org_type="Founder-led", headcount=20, jurisdictions=[_sid],
    )
    check(
        f"Cluster 1, {_sid} (state_specific_tiers, Phase 2a): still the generic $450,000 ceiling, "
        "is_floor=True -- Phase 2a adds no new pricing logic for AR/DE/TN, their real tier tables "
        "remain unconsumed, same placeholder treatment as any other tiers state",
        _r_c1.status == LegalPricingStatus.PRICED
        and _r_c1.dollar_range == (450_000.0, 450_000.0)
        and _r_c1.is_floor is True,
        f"got {_r_c1}",
    )
    _r_c4b = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 300, [_sid])
    check(
        f"Cluster 4b, {_sid} (state_specific_tiers, Phase 2a): still the generic $200,000 ceiling "
        "('250-499' bucket), is_floor=True -- same reasoning as the Cluster 1 check above",
        _r_c4b.status == LegalPricingStatus.PRICED
        and _r_c4b.curve.ceiling == 200_000.0
        and _r_c4b.is_floor is True,
        f"got {_r_c4b}",
    )


# -- 46. MD/MO is_combined_cap=True; other tiers states default False --

check(
    "MD and MO both is_combined_cap=True -- confirmed directly against each state's own statute "
    "text (Md. State Gov't Code Sec20-1013(e)(2); RSMo Sec213.111(4))",
    STATE_COVERAGE_THRESHOLDS["MD"].is_combined_cap is True
    and STATE_COVERAGE_THRESHOLDS["MO"].is_combined_cap is True,
    f"got MD={STATE_COVERAGE_THRESHOLDS['MD'].is_combined_cap!r}, "
    f"MO={STATE_COVERAGE_THRESHOLDS['MO'].is_combined_cap!r}",
)
check(
    "AR and TX (also state_specific_tiers) both default is_combined_cap=False -- not confirmed "
    "combined, not the same claim as confirmed split",
    STATE_COVERAGE_THRESHOLDS["AR"].is_combined_cap is False
    and STATE_COVERAGE_THRESHOLDS["TX"].is_combined_cap is False,
    f"got AR={STATE_COVERAGE_THRESHOLDS['AR'].is_combined_cap!r}, "
    f"TX={STATE_COVERAGE_THRESHOLDS['TX'].is_combined_cap!r}",
)


# -- 47. CO -- federal-tier-deferral branch, Cluster 4b only --

check(
    "sanity: CO is state_specific_tiers, CONFIRMED -- needed for the checks below",
    STATE_COVERAGE_THRESHOLDS["CO"].damages_cap_treatment == "state_specific_tiers"
    and STATE_COVERAGE_THRESHOLDS["CO"].confidence == "CONFIRMED",
    f"got treatment={STATE_COVERAGE_THRESHOLDS['CO'].damages_cap_treatment!r}, "
    f"confidence={STATE_COVERAGE_THRESHOLDS['CO'].confidence!r}",
)
check(
    "_co_drives_federal_tier_deferral(['CO'], 14) is False -- below the federal 15-employee floor, "
    "CO's own (unmodeled) tiers still govern, not a federal swap",
    _ft._co_drives_federal_tier_deferral(["CO"], 14) is False,
    f"got {_ft._co_drives_federal_tier_deferral(['CO'], 14)!r}",
)
check(
    "_co_drives_federal_tier_deferral(['CO'], 15) is True -- at the federal floor, CO's own statute "
    "defers to the federal Title VII tiers",
    _ft._co_drives_federal_tier_deferral(["CO"], 15) is True,
    f"got {_ft._co_drives_federal_tier_deferral(['CO'], 15)!r}",
)
check(
    "_co_drives_federal_tier_deferral(['CO', 'CA'], 20) is False -- CA (uncapped, rank 5) outranks "
    "CO (state_specific_tiers, rank 3), so CO isn't the driving jurisdiction even though it's present "
    "and headcount clears the floor",
    _ft._co_drives_federal_tier_deferral(["CO", "CA"], 20) is False,
    f"got {_ft._co_drives_federal_tier_deferral(['CO', 'CA'], 20)!r}",
)
check(
    "_co_drives_federal_tier_deferral(['CO', 'TX'], 20) is True -- documents the real, existing "
    "tie-order behavior (both rank 3, CO listed first wins) rather than leaving it unverified; this "
    "is a known, pre-existing limitation (see the function's own docstring), not new behavior",
    _ft._co_drives_federal_tier_deferral(["CO", "TX"], 20) is True,
    f"got {_ft._co_drives_federal_tier_deferral(['CO', 'TX'], 20)!r}",
)
check(
    "_co_drives_federal_tier_deferral(['TX', 'CO'], 20) is False -- same tie, opposite input order, "
    "TX (listed first) wins instead -- confirms the tie-break is genuinely input-order-dependent, not "
    "an accidental CO bias",
    _ft._co_drives_federal_tier_deferral(["TX", "CO"], 20) is False,
    f"got {_ft._co_drives_federal_tier_deferral(['TX', 'CO'], 20)!r}",
)
_r_co_14 = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 14, ["CO"])
check(
    "Cluster 4b, CO alone, headcount=14 (below the federal floor): is_floor=True, generic $200,000 "
    "ceiling -- CO's own tiers haven't yielded to federal yet, still a placeholder",
    _r_co_14.status == LegalPricingStatus.PRICED
    and _r_co_14.curve.ceiling == 200_000.0
    and _r_co_14.is_floor is True,
    f"got {_r_co_14}",
)
_r_co_15 = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 15, ["CO"])
check(
    "Cluster 4b, CO alone, headcount=15 (at the federal floor): is_floor=False now -- same $200,000 "
    "ceiling (Cluster 4b's table already IS the federal table, so the number itself doesn't move), "
    "but it's now Colorado's own real, confirmed answer, not a placeholder",
    _r_co_15.status == LegalPricingStatus.PRICED
    and _r_co_15.curve.ceiling == 200_000.0
    and _r_co_15.is_floor is False,
    f"got {_r_co_15}",
)
_r_co_ca_15 = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 15, ["CO", "CA"])
check(
    "Cluster 4b, CO+CA, headcount=15: is_floor=True -- CA (uncapped) outranks CO here, so the "
    "resolved treatment is 'uncapped', not 'state_specific_tiers', and CO's federal-deferral branch "
    "never engages even though headcount clears the floor and CO is present",
    _r_co_ca_15.status == LegalPricingStatus.PRICED
    and _r_co_ca_15.curve.ceiling == 200_000.0
    and _r_co_ca_15.is_floor is True,
    f"got {_r_co_ca_15}",
)


print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")'''

EDITS = [
    ('sections 45-47 -- Phase 2a (AR/DE/TN, MD/MO, CO)', ANCHOR_OLD, ANCHOR_NEW),
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
