"""
PRV3 -- Add Legal/Compliance test coverage to tools/test_friction_tax.py
for the engine implementation just written (INDUSTRY_NON_EXEMPT_RATIO,
LEGAL_COMPLIANCE_CLUSTER, compute_legal_compliance_exposure -- Addenda
1, 2, 3, 4, 5, 10). Covers exactly the cases verified in the dry-run:
formula floor/ceiling exactness (Clusters 1, 4a, 5), N=1 guard,
cross-cluster addition, within-cluster decay, Cluster 2 tier selection,
Cluster 3 per-capita math, Cluster 4 org_type routing (4a/4b/None for
Government), score=0 exclusion (both "never classified" and "classified
but monkey-patched to 0"), and the import-time table assertions.

Usage:
  python tools/patch_test_friction_tax_legal_compliance.py --dry-run
  python tools/patch_test_friction_tax_legal_compliance.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


TEST_FILE = "tools/test_friction_tax.py"

# ---------------------------------------------------------------------
# 1. Docstring -- new enumerated items
# ---------------------------------------------------------------------

edit(
    TEST_FILE,
    "  21. compute_friction_tax: state_ids mixing one real, populated state\n"
    "      with one unrecognized state_id must still yield\n"
    "      calibration_complete=False\n"
    '"""',
    "  21. compute_friction_tax: state_ids mixing one real, populated state\n"
    "      with one unrecognized state_id must still yield\n"
    "      calibration_complete=False\n"
    "  22. INDUSTRY_NON_EXEMPT_RATIO: 9 entries matching INDUSTRIES exactly\n"
    "  23. LEGAL_COMPLIANCE_CLUSTER: all 30 states classified, correct\n"
    "      per-cluster counts (4/11/2/6/7), every entry present in\n"
    "      STATE_MULTIPLIERS with a 'legal' score in {1, 2} -- the same\n"
    "      import-time assertions engine/friction_tax.py itself runs,\n"
    "      re-verified here as a locked regression check\n"
    "  24. Score-interpolation formula (Addendum 10) hits floor exactly at\n"
    "      score=1 and ceiling exactly at score=2, for Clusters 1, 4a, 5\n"
    "  25. compute_legal_compliance_exposure: N=1 guard -- a single\n"
    "      Legal-scoring state collapses exactly to its own individual\n"
    "      range, no aggregation logic engaged\n"
    "  26. compute_legal_compliance_exposure: cross-cluster addition (no\n"
    "      breadth premium) against a hand-derived expected sum\n"
    "  27. compute_legal_compliance_exposure: within-cluster geometric\n"
    "      decay (w_i = 0.5**(i-1)) against a hand-derived expected value\n"
    "  28. Cluster 2 discrete tier selection -- score=1 -> Tier 2a\n"
    "      (compensatory), score=2 -> Tier 2b (punitive)\n"
    "  29. Cluster 3 per-capita math (affected_workers = headcount_midpoint\n"
    "      x INDUSTRY_NON_EXEMPT_RATIO x scope_fraction, low/high =\n"
    "      affected x admin/litigation rate) against a hand-derived value\n"
    "  30. Cluster 4 org_type routing -- Publicly traded -> 4a, other\n"
    "      org_types -> 4b keyed by headcount bucket (including the\n"
    "      100-249 straddle-bucket midpoint convention), Government ->\n"
    "      None (genuinely no dollar figure, not zero)\n"
    "  31. compute_legal_compliance_exposure returns None/None when no\n"
    "      identified state carries priceable Legal/Compliance exposure --\n"
    "      both a state never classified into any cluster, and a\n"
    "      classified state whose 'legal' score is monkey-patched to 0\n"
    '"""',
)

# ---------------------------------------------------------------------
# 2. Imports
# ---------------------------------------------------------------------

edit(
    TEST_FILE,
    "from engine.friction_tax import (\n"
    "    SEVERITY_SCALAR,\n"
    "    STATE_MULTIPLIERS,\n"
    "    StateCriterionScore,\n"
    "    StateMultiplierEntry,\n"
    "    PAYROLL_BASELINE_GRID,\n"
    "    PayrollBaselineEntry,\n"
    "    ORG_TYPE_SCALARS,\n"
    "    OrgTypeScalarEntry,\n"
    "    HEADCOUNT_BUCKETS,\n"
    "    INDUSTRIES,\n"
    "    HEADCOUNT_MIDPOINTS,\n"
    "    compute_friction_tax,\n"
    ")",
    "from engine.friction_tax import (\n"
    "    SEVERITY_SCALAR,\n"
    "    STATE_MULTIPLIERS,\n"
    "    StateCriterionScore,\n"
    "    StateMultiplierEntry,\n"
    "    PAYROLL_BASELINE_GRID,\n"
    "    PayrollBaselineEntry,\n"
    "    ORG_TYPE_SCALARS,\n"
    "    OrgTypeScalarEntry,\n"
    "    HEADCOUNT_BUCKETS,\n"
    "    INDUSTRIES,\n"
    "    HEADCOUNT_MIDPOINTS,\n"
    "    compute_friction_tax,\n"
    "    INDUSTRY_NON_EXEMPT_RATIO,\n"
    "    LEGAL_COMPLIANCE_CLUSTER,\n"
    "    compute_legal_compliance_exposure,\n"
    ")",
)

# ---------------------------------------------------------------------
# 3. New test section, inserted before "-- Results --"
# ---------------------------------------------------------------------

NEW_TESTS = '''
# -- 22-23. INDUSTRY_NON_EXEMPT_RATIO / LEGAL_COMPLIANCE_CLUSNTER import-time -----
# assertions, re-verified here as a locked regression check (engine/
# friction_tax.py itself asserts these at import time -- if either table
# were ever edited without updating the other, these tests fail loudly
# here too, not just on next import).

check(
    "INDUSTRY_NON_EXEMPT_RATIO has exactly 9 entries matching INDUSTRIES",
    set(INDUSTRY_NON_EXEMPT_RATIO.keys()) == set(INDUSTRIES),
    f"got {set(INDUSTRY_NON_EXEMPT_RATIO.keys())}",
)
_EXPECTED_NON_EXEMPT_RATIOS = {
    "Manufacturing & Industrial": 0.557,
    "Healthcare & Life Sciences": 0.560,
    "Financial Services": 0.285,
    "Professional Services": 0.227,
    "Retail & Hospitality": 0.662,
    "Technology": 0.280,
    "Government & Public Sector": 0.44,
    "Nonprofit & Education": 0.135,
    "Other": 0.556,
}
check(
    "INDUSTRY_NON_EXEMPT_RATIO values match the sourced BLS figures exactly",
    INDUSTRY_NON_EXEMPT_RATIO == _EXPECTED_NON_EXEMPT_RATIOS,
    f"got {INDUSTRY_NON_EXEMPT_RATIO}",
)

check(
    "LEGAL_COMPLIANCE_CLUSTER classifies exactly 30 states",
    len(LEGAL_COMPLIANCE_CLUSTER) == 30,
    f"got {len(LEGAL_COMPLIANCE_CLUSTER)}",
)
_EXPECTED_CLUSTER_COUNTS = {1: 4, 2: 11, 3: 2, 4: 6, 5: 7}
_actual_cluster_counts = {
    n: sum(1 for v in LEGAL_COMPLIANCE_CLUSTER.values() if v == n) for n in range(1, 6)
}
check(
    "LEGAL_COMPLIANCE_CLUSTER per-cluster counts match Addendum 4's final table (4/11/2/6/7)",
    _actual_cluster_counts == _EXPECTED_CLUSTER_COUNTS,
    f"got {_actual_cluster_counts}",
)
_unclassified_or_bad_score = [
    sid for sid in LEGAL_COMPLIANCE_CLUSTER
    if sid not in STATE_MULTIPLIERS
    or STATE_MULTIPLIERS[sid].criteria["legal"].score not in (1, 2)
]
check(
    "Every LEGAL_COMPLIANCE_CLUSTER state exists in STATE_MULTIPLIERS with a 'legal' score in {1, 2}",
    len(_unclassified_or_bad_score) == 0,
    f"failures: {_unclassified_or_bad_score}",
)


# -- 24. Score-interpolation formula exactness (Addendum 10) --------------------
# Clusters 1, 4a, 5 -- floor exactly at score=1, ceiling exactly at score=2.

check(
    "Cluster 1 formula: score=1 -> floor $50,000 exactly",
    _ft._legal_score_fraction(_ft._CLUSTER_1_CURVE, 1) == 50_000.0,
    f"got {_ft._legal_score_fraction(_ft._CLUSTER_1_CURVE, 1)}",
)
check(
    "Cluster 1 formula: score=2 -> ceiling $450,000 exactly",
    _ft._legal_score_fraction(_ft._CLUSTER_1_CURVE, 2) == 450_000.0,
    f"got {_ft._legal_score_fraction(_ft._CLUSTER_1_CURVE, 2)}",
)
check(
    "Cluster 4a formula: score=1 -> floor $25,000 exactly",
    _ft._legal_score_fraction(_ft._CLUSTER_4A_CURVE, 1) == 25_000.0,
    f"got {_ft._legal_score_fraction(_ft._CLUSTER_4A_CURVE, 1)}",
)
check(
    "Cluster 4a formula: score=2 -> ceiling $33,000,000 exactly (midpoint of $16.5M-$49.5M, not the $279M outlier)",
    _ft._legal_score_fraction(_ft._CLUSTER_4A_CURVE, 2) == 33_000_000.0,
    f"got {_ft._legal_score_fraction(_ft._CLUSTER_4A_CURVE, 2)}",
)
check(
    "Cluster 5 formula: score=1 -> floor $16,550 exactly",
    _ft._legal_score_fraction(_ft._CLUSTER_5_CURVE, 1) == 16_550.0,
    f"got {_ft._legal_score_fraction(_ft._CLUSTER_5_CURVE, 1)}",
)
check(
    "Cluster 5 formula: score=2 -> ceiling $165,514 exactly (statutory-max only, actual-average deferred)",
    _ft._legal_score_fraction(_ft._CLUSTER_5_CURVE, 2) == 165_514.0,
    f"got {_ft._legal_score_fraction(_ft._CLUSTER_5_CURVE, 2)}",
)
check(
    "_CLUSTER_4B_CEILING_BY_HEADCOUNT covers all 6 HEADCOUNT_BUCKETS",
    set(_ft._CLUSTER_4B_CEILING_BY_HEADCOUNT.keys()) == set(HEADCOUNT_BUCKETS),
    f"got {set(_ft._CLUSTER_4B_CEILING_BY_HEADCOUNT.keys())}",
)
check(
    "Cluster 4b's 100-249 ceiling is $75,000 (midpoint of the real $50K-$100K straddle range, Addendum 10 convention)",
    _ft._CLUSTER_4B_CEILING_BY_HEADCOUNT["100-249"] == 75_000.0,
    f"got {_ft._CLUSTER_4B_CEILING_BY_HEADCOUNT['100-249']}",
)


# -- 25. N=1 guard -- compute_legal_compliance_exposure ---------------------------
# built_to_fail: Cluster 1, real legal score=1 -> individual range is
# exactly (floor, floor) = (50000, 50000), no aggregation engaged.

_r_n1 = compute_legal_compliance_exposure(
    state_ids=["built_to_fail"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "N=1 guard: single Legal-scoring state (built_to_fail, Cluster 1, score=1) collapses to its own floor exactly",
    _r_n1 == {"low": 50_000.0, "high": 50_000.0, "currency": "USD"},
    f"got {_r_n1}",
)


# -- 26. Cross-cluster addition (no breadth premium) -----------------------------
# built_to_fail (Cluster 1, score=1 -> $50,000) + the_unreported_hazard
# (Cluster 5, score=2 -> ceiling $165,514) -- different clusters, each is
# the only member of its own cluster in this profile, so each contributes
# at full weight; across-cluster combination is simple addition.

_r_cross = compute_legal_compliance_exposure(
    state_ids=["built_to_fail", "the_unreported_hazard"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
_expected_cross = round(50_000.0 + 165_514.0, 2)
check(
    "Cross-cluster addition: built_to_fail (C1, $50,000) + the_unreported_hazard (C5, $165,514) sums directly, no breadth premium",
    _r_cross == {"low": _expected_cross, "high": _expected_cross, "currency": "USD"},
    f"expected low=high={_expected_cross}, got {_r_cross}",
)


# -- 27. Within-cluster geometric decay ------------------------------------------
# built_to_fail (C1, score=1 -> $50,000) + the_paper_tiger (C1, score=2 ->
# $450,000), both Cluster 1 -- higher one (the_paper_tiger) contributes at
# full weight, built_to_fail decays to 0.5x: 450000*1.0 + 50000*0.5.

_r_decay = compute_legal_compliance_exposure(
    state_ids=["built_to_fail", "the_paper_tiger"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
_expected_decay = round(450_000.0 * 1.0 + 50_000.0 * 0.5, 2)
check(
    "Within-cluster decay: the_paper_tiger ($450,000) full weight + built_to_fail ($50,000) at 0.5x, both Cluster 1",
    _r_decay == {"low": _expected_decay, "high": _expected_decay, "currency": "USD"},
    f"expected low=high={_expected_decay}, got {_r_decay}",
)


# -- 28. Cluster 2 discrete tier selection ---------------------------------------

_r_tier_2b = compute_legal_compliance_exposure(
    state_ids=["disparate_impact_architecture"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Cluster 2: disparate_impact_architecture (score=2) selects Tier 2b ($25,000-31,000), not the log-scale formula",
    _r_tier_2b == {"low": 25_000.0, "high": 31_000.0, "currency": "USD"},
    f"got {_r_tier_2b}",
)
_r_tier_2a = compute_legal_compliance_exposure(
    state_ids=["pay_exposure"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Cluster 2: pay_exposure (score=1) selects Tier 2a ($1,800-2,500)",
    _r_tier_2a == {"low": 1_800.0, "high": 2_500.0, "currency": "USD"},
    f"got {_r_tier_2a}",
)


# -- 29. Cluster 3 per-capita math ------------------------------------------------
# cultural_overtime, real legal score=2 (Manufacturing & Industrial,
# 250-499 headcount): affected = headcount_midpoint x non_exempt_ratio x
# scope_fraction(score=2 -> 0.75); low/high = affected x admin/litigation
# rate.

_co_score = STATE_MULTIPLIERS["cultural_overtime"].criteria["legal"].score
_co_midpoint = HEADCOUNT_MIDPOINTS["250-499"].employees_per_firm
_co_ratio = INDUSTRY_NON_EXEMPT_RATIO["Manufacturing & Industrial"]
_co_affected = _co_midpoint * _co_ratio * (0.75 if _co_score == 2 else 0.25)
_co_expected_low = round(_co_affected * 1_465.0, 2)
_co_expected_high = round(_co_affected * 2_930.0, 2)
_r_cluster3 = compute_legal_compliance_exposure(
    state_ids=["cultural_overtime"],
    org_size="250-499",
    industry="Manufacturing & Industrial",
    org_type="Founder-led",
)
check(
    "Cluster 3 per-capita math: cultural_overtime (Manufacturing, 250-499) matches hand-derived "
    "headcount_midpoint x non_exempt_ratio x scope_fraction x per-worker rate",
    _r_cluster3 == {"low": _co_expected_low, "high": _co_expected_high, "currency": "USD"},
    f"expected low={_co_expected_low}, high={_co_expected_high}, got {_r_cluster3}",
)


# -- 30. Cluster 4 org_type routing (4a / 4b / Government -> None) --------------

_r_4a = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Publicly traded",
)
check(
    "Cluster 4, org_type='Publicly traded' routes to 4a: hr_capture (score=2) -> ceiling $33,000,000",
    _r_4a == {"low": 33_000_000.0, "high": 33_000_000.0, "currency": "USD"},
    f"got {_r_4a}",
)
_r_4b = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],
    org_size="250-499",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Cluster 4, org_type='Founder-led' routes to 4b: hr_capture (score=2), 250-499 bucket -> $200,000 statutory cap",
    _r_4b == {"low": 200_000.0, "high": 200_000.0, "currency": "USD"},
    f"got {_r_4b}",
)
_dn_score = STATE_MULTIPLIERS["dueling_narratives"].criteria["legal"].score
check(
    "sanity: dueling_narratives real legal score is 1, needed for the 4b floor check below",
    _dn_score == 1,
    f"got {_dn_score}",
)
_r_4b_floor = compute_legal_compliance_exposure(
    state_ids=["dueling_narratives"],
    org_size="250-499",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Cluster 4b floor: dueling_narratives (score=1) -> $25,000 EEOC mediation floor, regardless of headcount bucket",
    _r_4b_floor == {"low": 25_000.0, "high": 25_000.0, "currency": "USD"},
    f"got {_r_4b_floor}",
)
_r_4c = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
check(
    "Cluster 4, org_type='Government' routes to 4c: no dollar figure -- None, not zero",
    _r_4c == {"low": None, "high": None, "currency": "USD"},
    f"got {_r_4c}",
)


# -- 31. No priceable Legal/Compliance exposure -> None/None --------------------

_r_never_classified = compute_legal_compliance_exposure(
    state_ids=["the_dormant_talent"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "the_dormant_talent (never classified into any Legal/Compliance cluster) -> None/None",
    _r_never_classified == {"low": None, "high": None, "currency": "USD"},
    f"got {_r_never_classified}",
)

_original_btf = STATE_MULTIPLIERS.get("built_to_fail")
_ft.STATE_MULTIPLIERS["built_to_fail"] = _synthetic_entry(
    turnover=_original_btf.criteria["turnover"].score,
    productivity=_original_btf.criteria["productivity"].score,
    decision_quality=_original_btf.criteria["decision_quality"].score,
    legal=0,
)
_r_zero_score = compute_legal_compliance_exposure(
    state_ids=["built_to_fail"],
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "built_to_fail classified into Cluster 1 but monkey-patched to legal score=0 -> None/None, not a floor value",
    _r_zero_score == {"low": None, "high": None, "currency": "USD"},
    f"got {_r_zero_score}",
)
_ft.STATE_MULTIPLIERS["built_to_fail"] = _original_btf

check(
    "compute_legal_compliance_exposure returns None/None for an empty state_ids list",
    compute_legal_compliance_exposure([], "100-249", "Professional Services", "Founder-led")
    == {"low": None, "high": None, "currency": "USD"},
    "expected None/None for empty state_ids",
)


# -- Results ---------------------------------------------------------------------'''

edit(
    TEST_FILE,
    "\n# -- Results ---------------------------------------------------------------------",
    NEW_TESTS,
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
