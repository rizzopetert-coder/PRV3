"""
PRV3 Output Layer -- Friction Tax Unit Tests

Verifies:
  1. The cited inputs are the decided values (Gallup 0.70, 0.31, 0.18, 0.42,
     Work Institute 0.333) and the engagement factor is exactly 7.02 percent of
     payroll in every industry, hardcoded, not derived from the tables
  2. Hand-computed fixtures at actual headcount, expected values hardcoded as
     literals from the spec's R3 worked figures (the 10 Section 6b rows)
  3. The 1,000 intake cap withholds every dollar amount and keeps percent of
     payroll, 999 carries both
  4. The headcount guard: int or float of at least 2 prices at the actual N,
     everything else is uncalibrated with no bucket fallback
  5. Channel switch rule against the identified states: channels never stack or
     scale by state count, severity is not an input, excess is null, a state set
     with no dollar channel (paper_shield) returns a null estimate
  6. Every industry has a W and a q, the stored JOLTS rates are the R3 rounded
     values, every input carries a source and a vintage
  7. Engagement floor: an engaged share at or above best practice prices zero,
     never negative
  8. The removed structures are gone (STATE_MULTIPLIERS, PAYROLL_BASELINE_GRID,
     SEVERITY_SCALAR, ORG_TYPE_SCALARS, the 1.4x spread)
  9. Stage 3 wage tables (frozen Legal copy and May 2025 friction wages)
  22. INDUSTRY_NON_EXEMPT_RATIO: 9 entries matching INDUSTRIES exactly
  23. LEGAL_COMPLIANCE_CLUSTER: all 30 states classified, correct
      per-cluster counts (4/11/2/6/7), every entry present in
      STATE_MULTIPLIERS with a 'legal' score in {1, 2} -- the same
      import-time assertions engine/friction_tax.py itself runs,
      re-verified here as a locked regression check
  24. Score-interpolation formula (Addendum 10) hits floor exactly at
      score=1 and ceiling exactly at score=2, for Clusters 1, 4a, 5
  25. compute_legal_compliance_exposure: N=1 guard -- a single
      Legal-scoring state collapses exactly to its own individual
      range, no aggregation logic engaged
  26. compute_legal_compliance_exposure: cross-cluster addition (no
      breadth premium) against a hand-derived expected sum
  27. compute_legal_compliance_exposure: within-cluster geometric
      decay (w_i = 0.5**(i-1)) against a hand-derived expected value
  28. Cluster 2 discrete tier selection -- score=1 -> Tier 2a
      (compensatory), score=2 -> Tier 2b (punitive)
  29. Cluster 3 per-capita math (affected_workers = headcount_midpoint
      x INDUSTRY_NON_EXEMPT_RATIO x scope_fraction, low/high =
      affected x admin/litigation rate) against a hand-derived value
  30. Cluster 4 org_type routing -- Publicly traded -> 4a, other
      org_types -> 4b keyed by headcount bucket (including the
      100-249 straddle-bucket midpoint convention), Government ->
      None (genuinely no dollar figure, not zero)
  31. compute_legal_compliance_exposure returns None/None when no
      identified state carries priceable Legal/Compliance exposure --
      both a state never classified into any cluster, and a
      classified state whose 'legal' score is monkey-patched to 0
"""

import inspect
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.contract import _SPECIFIC_CAVEAT_TEXT
from engine.friction_tax import (
    HEADCOUNT_BUCKETS,
    INDUSTRIES,
    HEADCOUNT_MIDPOINTS,
    resolve_headcount_bucket,
    compute_friction_tax,
    INDUSTRY_NON_EXEMPT_RATIO,
    LEGAL_COMPLIANCE_CLUSTER,
    compute_legal_compliance_exposure,
    STATE_COVERAGE_THRESHOLDS,
    StateCoverageThreshold,
    CoverageResult,
    resolve_coverage_gate,
    LegalPricingStatus,
    resolve_damages_treatment,
)
from engine.data.states import STATE_PROFILES
from engine.data.state_criteria import STATE_CRITERIA
from engine.data.intake import INTAKE_FIELDS
import engine.friction_tax as _ft

PASS = []
FAIL = []


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Friction Tax -- Unit Tests")
print("=" * 64)


# -- 1. Cited inputs, hardcoded ----------------------------------------------------

check("ENGAGEMENT_BEST_PRACTICE == 0.70 (Gallup, 2025)", _ft.ENGAGEMENT_BEST_PRACTICE == 0.70)
check("ENGAGEMENT_US == 0.31 (Gallup, May 2026)", _ft.ENGAGEMENT_US == 0.31)
check("NOT_ENGAGED_COST_SHARE == 0.18 (Gallup, 2020)", _ft.NOT_ENGAGED_COST_SHARE == 0.18)
check("TURNOVER_PREVENTABLE_SHARE == 0.42 (Gallup, July 2024)", _ft.TURNOVER_PREVENTABLE_SHARE == 0.42)
check("TURNOVER_COST_SHARE == 0.333 (Work Institute, 2017)", _ft.TURNOVER_COST_SHARE == 0.333)
check("INTAKE_HEADCOUNT_CAP == 1000 and MIN_PRICED_HEADCOUNT == 2",
      _ft.INTAKE_HEADCOUNT_CAP == 1000 and _ft.MIN_PRICED_HEADCOUNT == 2)

_BOTH = ["the_overloaded_manager"]  # turnover 2, productivity 1, decision_quality 1


def _channels(r):
    return {c["channel"]: c for c in r["estimate"]["typical_baseline"]["channels"]}


_eng_pcts = {
    ind: _channels(compute_friction_tax(_BOTH, 175, ind))["engagement"]["percent_of_payroll"]
    for ind in INDUSTRIES
}
check("engagement is exactly 7.02 percent of payroll in all 11 industries (0.39 x 0.18, hardcoded)",
      set(_eng_pcts.values()) == {7.02} and len(_eng_pcts) == 11, f"got {_eng_pcts}")

# -- 2. Hand-computed fixtures (spec 6b, R3 rounded rates), literals ----------------
# (employees, industry, engagement $, turnover $, total $), whole dollars. Computed
# by hand as P x 0.0702 and P x (monthly x 12 / 100) x 0.42 x 0.333, P = N x W.

_FIXTURES = [
    (12, "Retail & Hospitality", 35401, 28522, 63923),
    (12, "Other", 57264, 30119, 87383),
    (60, "Construction", 303879, 130771, 434650),
    (60, "Government & Public Sector", 338181, 64681, 402863),
    (175, "Technology", 1413144, 439205, 1852349),
    (175, "Professional Services", 1334642, 733889, 2068531),
    (400, "Nonprofit & Education", 2043241, 801127, 2844368),
    (400, "Manufacturing", 1941198, 649734, 2590933),
    (800, "Healthcare & Life Sciences", 3985619, 1905739, 5891358),
    (800, "Transportation & Warehousing", 3612829, 1900237, 5513066),
]
for _n, _ind, _eng, _turn, _tot in _FIXTURES:
    _r = compute_friction_tax(_BOTH, _n, _ind)
    _ch = _channels(_r)
    _total = _r["estimate"]["typical_baseline"]["total"]
    check(
        f"{_n} / {_ind}: engagement ${_eng:,}, turnover ${_turn:,}, total ${_tot:,}",
        round(_ch["engagement"]["amount"]) == _eng
        and round(_ch["turnover"]["amount"]) == _turn
        and round(_total["amount"]) == _tot,
        f"got {_ch['engagement']['amount']}, {_ch['turnover']['amount']}, {_total['amount']}",
    )
_r_retail = compute_friction_tax(_BOTH, 12, "Retail & Hospitality")
check("12 / Retail & Hospitality annual quit rate is 3.37 x 12 = 40.44 percent (R3, rounded monthly rate)",
      _r_retail["annual_quit_rate_percent"] == 40.44, f"got {_r_retail['annual_quit_rate_percent']}")
check("12 / Retail & Hospitality payroll is 12 x 42,024 = 504,288 and the total is 12.6759 percent",
      _r_retail["payroll"] == 504288.0
      and _r_retail["estimate"]["typical_baseline"]["total"]["percent_of_payroll"] == 12.6759,
      f"got {_r_retail['payroll']}, {_r_retail['estimate']['typical_baseline']['total']}")
check("every fixture total is between 8.4 and 12.7 percent of payroll (spec 6b)",
      all(8.3 < compute_friction_tax(_BOTH, 175, ind)["estimate"]["typical_baseline"]["total"]["percent_of_payroll"] < 12.8
          for ind in INDUSTRIES))
_r_fl = compute_friction_tax(_BOTH, 150.5, "Technology")
check("a float headcount prices at the actual N: 150.5 x 115,030 payroll",
      _r_fl["payroll"] == 150.5 * 115030.0 and _r_fl["headcount"] == 150.5, f"got {_r_fl['payroll']}")

# -- 3. The 1,000 intake cap ---------------------------------------------------------

_cap = compute_friction_tax(_BOTH, 1000, "Financial Services")
_cap_ch = _channels(_cap)
check("N = 1000: every amount is null, percent of payroll present on each channel and the total",
      _cap["amounts_withheld"] is True and _cap["payroll"] is None
      and _cap["estimate"]["typical_baseline"]["total"]["amount"] is None
      and _cap_ch["engagement"]["amount"] is None and _cap_ch["turnover"]["amount"] is None
      and _cap_ch["engagement"]["percent_of_payroll"] == 7.02
      and _cap_ch["turnover"]["percent_of_payroll"] == 2.1818
      and _cap["estimate"]["typical_baseline"]["total"]["percent_of_payroll"] == 9.2018,
      f"got {_cap}")
check("N = 1000: no wage or employee-count input is carried, so no dollar figure leaks through inputs",
      all(not any("wage" in i["name"].lower() or i["name"] == "Employees" for i in c["inputs"])
          for c in _cap_ch.values()))
_just = compute_friction_tax(_BOTH, 999, "Financial Services")
check("N = 999 carries both percent and amounts",
      _just["amounts_withheld"] is False and _just["estimate"]["typical_baseline"]["total"]["amount"] is not None
      and all(c["amount"] is not None for c in _channels(_just).values()))
_over = compute_friction_tax(_BOTH, 1200, "Financial Services")
check("N = 1200 (above the intake ceiling) is withheld the same way",
      _over["amounts_withheld"] is True and _over["estimate"]["typical_baseline"]["total"]["amount"] is None)

# -- 4. Headcount guard ----------------------------------------------------------------

for _bad in ("", None, "150", True, False, float("inf"), float("-inf"), float("nan"), 0, -5, 1, 1.9):
    _rb = compute_friction_tax(_BOTH, _bad, "Technology")
    check(f"headcount {_bad!r} is uncalibrated, null estimate, no bucket fallback",
          _rb["estimate"] is None and _rb["calibration_complete"] is False and _rb["headcount"] is None,
          f"got {_rb}")
check("headcount 2 is the smallest priced N", compute_friction_tax(_BOTH, 2, "Technology")["estimate"] is not None)
check("headcount 2.0 (float) prices", compute_friction_tax(_BOTH, 2.0, "Technology")["estimate"] is not None)

# -- 5. Channel switch rule ------------------------------------------------------------

check("only paper_shield (decision_quality only): null estimate, decision-time receipt on, no dollar channel",
      compute_friction_tax(["paper_shield"], 100, "Technology")["estimate"] is None
      and compute_friction_tax(["paper_shield"], 100, "Technology")["decision_time_receipt"] is True
      and compute_friction_tax(["paper_shield"], 100, "Technology")["channels_on"] == [])
_t_only = compute_friction_tax(["the_paper_tiger"], 175, "Technology")  # turnover 1, productivity 0, dq 0
check("a turnover-only state switches on the turnover channel alone, no decision-time receipt",
      _t_only["channels_on"] == ["turnover"] and list(_channels(_t_only)) == ["turnover"]
      and _t_only["decision_time_receipt"] is False)
_p_only = compute_friction_tax(["the_lost_map"], 175, "Technology")  # productivity 2, turnover 0, dq 2
check("a productivity-only state switches on the engagement channel alone, with the decision-time receipt",
      _p_only["channels_on"] == ["engagement"] and list(_channels(_p_only)) == ["engagement"]
      and _p_only["decision_time_receipt"] is True)
_one = compute_friction_tax(["the_overloaded_manager"], 175, "Technology")
_many = compute_friction_tax(
    ["the_overloaded_manager", "decision_paralysis", "the_founders_grip", "the_paper_tiger", "the_lost_map"],
    175, "Technology")
check("multi-state sets do not stack: five states give the same figure as one when both channels are already on",
      _one["estimate"] == _many["estimate"], f"one {_one['estimate']['typical_baseline']['total']} many {_many['estimate']['typical_baseline']['total']}")
check("a channel is on when any identified state scores above 0 on it (turnover-only plus productivity-only = both)",
      compute_friction_tax(["the_paper_tiger", "the_lost_map"], 175, "Technology")["estimate"]
      == _one["estimate"])
check("severity is not an input: the signature is (state_ids, org_size, industry)",
      list(inspect.signature(compute_friction_tax).parameters) == ["state_ids", "org_size", "industry"])
check("excess is null and the result is a point estimate (no low or high)",
      _one["estimate"]["excess"] is None and "low" not in _one and "high" not in _one["estimate"]
      and "low" not in _one["estimate"])
check("an unknown state id gives a null estimate", compute_friction_tax(["not_a_state"], 175, "Technology")["estimate"] is None)
check("a known state mixed with an unknown one gives a null estimate",
      compute_friction_tax(["the_overloaded_manager", "not_a_state"], 175, "Technology")["estimate"] is None)
check("an empty state list gives a null estimate", compute_friction_tax([], 175, "Technology")["estimate"] is None)
check("an unknown industry gives a null estimate", compute_friction_tax(_BOTH, 175, "Not An Industry")["estimate"] is None)

# -- 6. Tables and provenance ----------------------------------------------------------

_Q = {
    "Professional Services": 2.30, "Healthcare & Life Sciences": 2.00, "Financial Services": 1.30,
    "Technology": 1.30, "Manufacturing": 1.40, "Retail & Hospitality": 3.37,
    "Nonprofit & Education": 1.64, "Government & Public Sector": 0.80, "Construction": 1.80,
    "Transportation & Warehousing": 2.20, "Other": 2.20,
}
check("QUITS_MONTHLY_RATE_2025 holds the R3 rounded 2-decimal monthly rates, all 11 industries",
      {k: v[0] for k, v in _ft.QUITS_MONTHLY_RATE_2025.items()} == _Q)
check("every industry has a wage W and a quits rate q",
      all(_ft.get_industry_wage(i) is not None and i in _ft.QUITS_MONTHLY_RATE_2025 for i in INDUSTRIES))
_all_inputs = [i for ind in INDUSTRIES for c in _channels(compute_friction_tax(_BOTH, 175, ind)).values() for i in c["inputs"]]
check("every input carries a name, a value, a source and a vintage",
      all(i["name"] and i["value"] is not None and i["source"] and i["vintage"] for i in _all_inputs))
check("the vintages are the cited ones",
      {"2025", "May 2026", "2020", "July 2024", "2017", "May 2025", "this session"} == {i["vintage"] for i in _all_inputs},
      f"got {sorted({i['vintage'] for i in _all_inputs})}")
check("the engagement inputs are 0.70, 0.31 and 0.18, the turnover inputs include 0.42 and 0.333",
      [i["value"] for i in _channels(_one)["engagement"]["inputs"][:3]] == [0.70, 0.31, 0.18]
      and [i["value"] for i in _channels(_one)["turnover"]["inputs"][1:3]] == [0.42, 0.333])
check("framing constants carry the required wording and none of the forbidden words",
      "what organizations like yours typically lose" == _ft.FRICTION_FRAMING_TOTAL
      and "the gap between organizations like yours and the best-run ones" == _ft.FRICTION_FRAMING_ENGAGEMENT_GAP
      and not any(w in (_ft.FRICTION_FRAMING_TOTAL + _ft.FRICTION_FRAMING_ENGAGEMENT_GAP).lower()
                  for w in ("normal", "acceptable", "full engagement")))

# -- 7. Engagement floor ---------------------------------------------------------------

_saved_us = _ft.ENGAGEMENT_US
_ft.ENGAGEMENT_US = 0.80
_floor = _channels(compute_friction_tax(_BOTH, 175, "Technology"))["engagement"]
_ft.ENGAGEMENT_US = _saved_us
check("E_us at or above E_bp prices zero engagement, never negative",
      _floor["percent_of_payroll"] == 0.0 and _floor["amount"] == 0.0, f"got {_floor}")

# -- 8. Removed structures --------------------------------------------------------------

for _gone in ("STATE_MULTIPLIERS", "PAYROLL_BASELINE_GRID", "SEVERITY_SCALAR", "ORG_TYPE_SCALARS",
              "StateMultiplierEntry", "StateCriterionScore", "PayrollBaselineEntry", "OrgTypeScalarEntry",
              "_attritional_fraction", "_MULTI_CHANNEL_SEVERITY_LOADING_K", "_R_MAX", "_FRACTION_MAX",
              "_DEFAULT_SEVERITY_SCALAR"):
    check(f"{_gone} is removed from engine.friction_tax", not hasattr(_ft, _gone))


# -- 22-23. INDUSTRY_NON_EXEMPT_RATIO / LEGAL_COMPLIANCE_CLUSNTER import-time -----
# assertions, re-verified here as a locked regression check (engine/
# friction_tax.py itself asserts these at import time -- if either table
# were ever edited without updating the other, these tests fail loudly
# here too, not just on next import).

check(
    "INDUSTRY_NON_EXEMPT_RATIO has exactly 11 entries matching INDUSTRIES",
    set(INDUSTRY_NON_EXEMPT_RATIO.keys()) == set(INDUSTRIES),
    f"got {set(INDUSTRY_NON_EXEMPT_RATIO.keys())}",
)
_EXPECTED_NON_EXEMPT_RATIOS = {
    "Manufacturing": 0.557,
    "Healthcare & Life Sciences": 0.560,
    "Financial Services": 0.285,
    "Professional Services": 0.227,
    "Retail & Hospitality": 0.662,
    "Technology": 0.280,
    "Government & Public Sector": 0.44,
    "Nonprofit & Education": 0.135,
    "Construction": 0.554,
    "Transportation & Warehousing": 0.422,
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
    if sid not in STATE_CRITERIA
    or STATE_CRITERIA[sid].legal not in (1, 2)
]
check(
    "Every LEGAL_COMPLIANCE_CLUSTER state exists in STATE_CRITERIA with a 'legal' score in {1, 2}",
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
    org_size=152,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "N=1 guard: single Legal-scoring state (built_to_fail, Cluster 1, score=1) collapses to its own floor exactly",
    _r_n1 == {
        "low": 50_000.0, "high": 50_000.0, "currency": "USD", "band": "Minor",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "federal_baseline", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_n1}",
)


# -- 26. Cross-cluster addition (no breadth premium) -----------------------------
# built_to_fail (Cluster 1, score=1 -> $50,000) + the_unreported_hazard
# (Cluster 5, score=2 -> ceiling $165,514) -- different clusters, each is
# the only member of its own cluster in this profile, so each contributes
# at full weight; across-cluster combination is simple addition.

_r_cross = compute_legal_compliance_exposure(
    state_ids=["built_to_fail", "the_unreported_hazard"],
    org_size=152,
    industry="Professional Services",
    org_type="Founder-led",
)
_expected_cross = round(50_000.0 + 165_514.0, 2)
check(
    "Cross-cluster addition: built_to_fail (C1, $50,000) + the_unreported_hazard (C5, $165,514) sums directly, no breadth premium",
    _r_cross == {
        "low": _expected_cross, "high": _expected_cross, "currency": "USD", "band": "Moderate",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "federal_baseline", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"expected low=high={_expected_cross}, got {_r_cross}",
)


# -- 27. Within-cluster geometric decay ------------------------------------------
# built_to_fail (C1, score=1 -> $50,000) + the_paper_tiger (C1, score=2 ->
# $450,000), both Cluster 1 -- higher one (the_paper_tiger) contributes at
# full weight, built_to_fail decays to 0.5x: 450000*1.0 + 50000*0.5.

_r_decay = compute_legal_compliance_exposure(
    state_ids=["built_to_fail", "the_paper_tiger"],
    org_size=152,
    industry="Professional Services",
    org_type="Founder-led",
)
_expected_decay = round(450_000.0 * 1.0 + 50_000.0 * 0.5, 2)
check(
    "Within-cluster decay: the_paper_tiger ($450,000) full weight + built_to_fail ($50,000) at 0.5x, both Cluster 1",
    _r_decay == {
        "low": _expected_decay, "high": _expected_decay, "currency": "USD", "band": "Moderate",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "federal_baseline", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"expected low=high={_expected_decay}, got {_r_decay}",
)


# -- 28. Cluster 2 discrete tier selection ---------------------------------------

_r_tier_2b = compute_legal_compliance_exposure(
    state_ids=["disparate_impact_architecture"],
    org_size=152,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Cluster 2: disparate_impact_architecture (score=2) selects Tier 2b ($25,000-31,000), not the log-scale formula",
    _r_tier_2b == {
        "low": 25_000.0, "high": 31_000.0, "currency": "USD", "band": "Minor",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "federal_baseline", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_tier_2b}",
)
_r_tier_2a = compute_legal_compliance_exposure(
    state_ids=["pay_exposure"],
    org_size=152,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Cluster 2: pay_exposure (score=1) selects Tier 2a ($1,800-2,500)",
    _r_tier_2a == {
        "low": 1_800.0, "high": 2_500.0, "currency": "USD", "band": "Minor",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "federal_baseline", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_tier_2a}",
)


# -- 29. Cluster 3 per-capita math ------------------------------------------------
# cultural_overtime, real legal score=2 (Manufacturing,
# 250-499 headcount): affected = headcount_midpoint x non_exempt_ratio x
# scope_fraction(score=2 -> 0.75); low/high = affected x admin/litigation
# rate.

_co_score = STATE_CRITERIA["cultural_overtime"].legal
_co_midpoint = HEADCOUNT_MIDPOINTS["250-499"].employees_per_firm
_co_ratio = INDUSTRY_NON_EXEMPT_RATIO["Manufacturing"]
_co_affected = _co_midpoint * _co_ratio * (0.75 if _co_score == 2 else 0.25)
_co_expected_low = round(_co_affected * 1_465.0, 2)
_co_expected_high = round(_co_affected * 2_930.0, 2)
_r_cluster3 = compute_legal_compliance_exposure(
    state_ids=["cultural_overtime"],
    org_size=328,
    industry="Manufacturing",
    org_type="Founder-led",
)
check(
    "Cluster 3 per-capita math: cultural_overtime (Manufacturing, 250-499) matches hand-derived "
    "headcount_midpoint x non_exempt_ratio x scope_fraction x per-worker rate",
    _r_cluster3 == {
        "low": _co_expected_low, "high": _co_expected_high, "currency": "USD", "band": "Moderate",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"expected low={_co_expected_low}, high={_co_expected_high}, got {_r_cluster3}",
)


# -- 30. Cluster 4 org_type routing (4a / 4b / Government -> None) --------------

_r_4a = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],
    org_size=152,
    industry="Professional Services",
    org_type="Publicly traded",
)
check(
    "Cluster 4, org_type='Publicly traded' routes to 4a: hr_capture (score=2) -> ceiling $33,000,000",
    _r_4a == {
        "low": 33_000_000.0, "high": 33_000_000.0, "currency": "USD", "band": "Significant",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_4a}",
)
_r_4b = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],
    org_size=328,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Cluster 4, org_type='Founder-led' routes to 4b: hr_capture (score=2), 250-499 bucket -> $200,000 statutory cap",
    _r_4b == {
        "low": 200_000.0, "high": 200_000.0, "currency": "USD", "band": "Moderate",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "federal_baseline", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_4b}",
)
_dn_score = STATE_CRITERIA["dueling_narratives"].legal
check(
    "sanity: dueling_narratives real legal score is 1, needed for the 4b floor check below",
    _dn_score == 1,
    f"got {_dn_score}",
)
_r_4b_floor = compute_legal_compliance_exposure(
    state_ids=["dueling_narratives"],
    org_size=328,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Cluster 4b floor: dueling_narratives (score=1) -> $25,000 EEOC mediation floor, regardless of headcount bucket",
    _r_4b_floor == {
        "low": 25_000.0, "high": 25_000.0, "currency": "USD", "band": "Minor",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "federal_baseline", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_4b_floor}",
)
_r_4c = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],
    org_size=152,
    industry="Professional Services",
    org_type="Government",
)
check(
    "Cluster 4, org_type='Government' routes to 4c: no dollar figure -- None, not zero, "
    "and now surfaced via has_unpriced_conditions/unpriced_state_ids rather than silently vanishing",
    _r_4c == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": True, "unpriced_state_ids": ["hr_capture"], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_4c}",
)


# -- 31. No priceable Legal/Compliance exposure -> None/None --------------------

_r_never_classified = compute_legal_compliance_exposure(
    state_ids=["the_dormant_talent"],
    org_size=152,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "the_dormant_talent (never classified into any Legal/Compliance cluster) -> None/None",
    _r_never_classified == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_never_classified}",
)

import dataclasses as _dc
# Legal reads engine/data/state_criteria.py STATE_CRITERIA (Stage 1), so the
# monkey-patch targets that table.
_original_btf = _ft.STATE_CRITERIA["built_to_fail"]
_ft.STATE_CRITERIA["built_to_fail"] = _dc.replace(_original_btf, legal=0)
_r_zero_score = compute_legal_compliance_exposure(
    state_ids=["built_to_fail"],
    org_size=152,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "built_to_fail classified into Cluster 1 but monkey-patched to legal score=0 -> None/None, not a floor value",
    _r_zero_score == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_zero_score}",
)
_ft.STATE_CRITERIA["built_to_fail"] = _original_btf

check(
    "compute_legal_compliance_exposure returns None/None for an empty state_ids list",
    compute_legal_compliance_exposure([], 152, "Professional Services", "Founder-led")
    == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    "expected None/None for empty state_ids",
)



# -- 32. _legal_exposure_band() -- exact boundary-threshold behavior -------------
# Confirms the real inequality direction matches Addendum 11's "Under $100K" /
# "$100K-$500K" / "$500K-$2M" / "$2M+" wording -- each cutoff value itself
# lands in the HIGHER band, not the lower one.

check(
    "_legal_exposure_band(None) -> None",
    _ft._legal_exposure_band(None) is None,
    f"got {_ft._legal_exposure_band(None)}",
)
check(
    "_legal_exposure_band(0.0) -> Minor (zero floor, still a real number)",
    _ft._legal_exposure_band(0.0) == "Minor",
    f"got {_ft._legal_exposure_band(0.0)}",
)
check(
    "_legal_exposure_band(99_999.99) -> Minor (just under $100K)",
    _ft._legal_exposure_band(99_999.99) == "Minor",
    f"got {_ft._legal_exposure_band(99_999.99)}",
)
check(
    "_legal_exposure_band(100_000.0) -> Moderate ($100K itself, not Minor)",
    _ft._legal_exposure_band(100_000.0) == "Moderate",
    f"got {_ft._legal_exposure_band(100_000.0)}",
)
check(
    "_legal_exposure_band(499_999.99) -> Moderate (just under $500K)",
    _ft._legal_exposure_band(499_999.99) == "Moderate",
    f"got {_ft._legal_exposure_band(499_999.99)}",
)
check(
    "_legal_exposure_band(500_000.0) -> Elevated ($500K itself, not Moderate)",
    _ft._legal_exposure_band(500_000.0) == "Elevated",
    f"got {_ft._legal_exposure_band(500_000.0)}",
)
check(
    "_legal_exposure_band(1_999_999.99) -> Elevated (just under $2M)",
    _ft._legal_exposure_band(1_999_999.99) == "Elevated",
    f"got {_ft._legal_exposure_band(1_999_999.99)}",
)
check(
    "_legal_exposure_band(2_000_000.0) -> Significant ($2M itself, not Elevated)",
    _ft._legal_exposure_band(2_000_000.0) == "Significant",
    f"got {_ft._legal_exposure_band(2_000_000.0)}",
)
check(
    "_legal_exposure_band(50_000_000.0) -> Significant (well above $2M)",
    _ft._legal_exposure_band(50_000_000.0) == "Significant",
    f"got {_ft._legal_exposure_band(50_000_000.0)}",
)


# -- resolve_headcount_bucket() boundary tests -----------------------------------
# Every real HEADCOUNT_BUCKETS boundary, both sides. Pete's original list also
# named "15" -- not a bucket boundary (that's the ADA coverage threshold, unrelated
# to HEADCOUNT_BUCKETS' 25/100/250/500/1000 edges), so no check exists for it.
for _hc, _expected in [
    (1, "Under 25"),
    (24, "Under 25"),
    (25, "25-99"),
    (99, "25-99"),
    (100, "100-249"),
    (249, "100-249"),
    (250, "250-499"),
    (499, "250-499"),
    (500, "500-999"),
    (999, "500-999"),
    (1000, "1000+"),
    (50_000, "1000+"),
]:
    check(
        f"resolve_headcount_bucket({_hc}) -> {_expected!r}",
        resolve_headcount_bucket(_hc) == _expected,
        f"got {resolve_headcount_bucket(_hc)!r}",
    )


# -- 33. STATE_COVERAGE_THRESHOLDS -- structural checks --------------------------
# Independently re-verified here, not just trusted from friction_tax.py's own
# import-time assertions -- same standing convention as test 23 for
# LEGAL_COMPLIANCE_CLUSTER.

from engine.data.jurisdiction import JURISDICTION_TABLE as _JURISDICTION_TABLE_CHECK

check(
    "STATE_COVERAGE_THRESHOLDS covers exactly the same 50-states-plus-DC key set as JURISDICTION_TABLE",
    set(STATE_COVERAGE_THRESHOLDS.keys()) == set(_JURISDICTION_TABLE_CHECK.keys()),
    f"symmetric difference: {set(STATE_COVERAGE_THRESHOLDS.keys()) ^ set(_JURISDICTION_TABLE_CHECK.keys())}",
)
check(
    "STATE_COVERAGE_THRESHOLDS has exactly 51 CONFIRMED entries -- all 51 jurisdictions, the PARTIAL-state verification workstream is complete (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA, MS, NC, OK, AZ, HI, ID, MT, NM, NV, OR, UT, WY, IA, MI, SC)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD", "NH", "NJ", "PA", "RI", "VT", "IN", "KS", "MN", "MO", "NE", "ND", "OH", "SD", "WI", "AL", "AR", "GA", "KY", "LA", "MS", "NC", "OK", "AZ", "HI", "ID", "MT", "NM", "NV", "OR", "UT", "WY", "IA", "MI", "SC"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)
check(
    "every non-CONFIRMED entry is confidence='PARTIAL' (no third confidence value exists)",
    all(v.confidence in ("CONFIRMED", "PARTIAL") for v in STATE_COVERAGE_THRESHOLDS.values()),
    "found an entry with an unexpected confidence value",
)
check(
    "every entry's thresholds dict has a 'general' key -- resolve_coverage_gate()'s fallback depends on it existing everywhere",
    all("general" in v.thresholds for v in STATE_COVERAGE_THRESHOLDS.values()),
    "found an entry missing the required 'general' threshold key",
)
check(
    "CA carries both 'general' (5) and 'harassment' (1) thresholds, distinct values",
    STATE_COVERAGE_THRESHOLDS["CA"].thresholds == {"general": 5, "harassment": 1},
    f"got {STATE_COVERAGE_THRESHOLDS['CA'].thresholds}",
)
check(
    "every entry has a non-empty citation string",
    all(v.citation.strip() != "" for v in STATE_COVERAGE_THRESHOLDS.values()),
    "found an entry with an empty citation",
)


# -- 34. resolve_coverage_gate() -- single CONFIRMED-state resolution ------------

_gate_ny_covered = resolve_coverage_gate(headcount=6, jurisdictions=["NY"], claim_type="general")
check(
    "resolve_coverage_gate: NY general threshold=4, headcount=6 -> applies=True, driven by NY",
    _gate_ny_covered == CoverageResult(
        applies=True, threshold=4, claim_type="general",
        driving_jurisdiction="NY", confidence="CONFIRMED",
        partial_state_flag=False, partial_jurisdictions_considered=(),
    ),
    f"got {_gate_ny_covered}",
)
_gate_ny_not_covered = resolve_coverage_gate(headcount=3, jurisdictions=["NY"], claim_type="general")
check(
    "resolve_coverage_gate: NY general threshold=4, headcount=3 -> applies=False",
    _gate_ny_not_covered.applies is False and _gate_ny_not_covered.threshold == 4,
    f"got {_gate_ny_not_covered}",
)


# -- 35. resolve_coverage_gate() -- multi-state most-protective-wins -------------
# CA=5, MA=6, WV=12 (general) -- minimum is CA's 5, regardless of list order.

_gate_multi_a = resolve_coverage_gate(headcount=5, jurisdictions=["CA", "MA", "WV"], claim_type="general")
check(
    "resolve_coverage_gate: multi-state most-protective-wins picks CA (threshold=5), lowest of {5,6,12}",
    _gate_multi_a.threshold == 5 and _gate_multi_a.driving_jurisdiction == "CA" and _gate_multi_a.applies is True,
    f"got {_gate_multi_a}",
)
_gate_multi_b = resolve_coverage_gate(headcount=5, jurisdictions=["WV", "MA", "CA"], claim_type="general")
check(
    "resolve_coverage_gate: most-protective-wins result is order-independent (same 3 states, reversed order)",
    _gate_multi_b == _gate_multi_a,
    f"got {_gate_multi_b}, expected {_gate_multi_a}",
)


# -- 36. resolve_coverage_gate() -- federal fallback when no CONFIRMED state present, incl. empty input --

_gate_federal_uncovered = resolve_coverage_gate(headcount=10, jurisdictions=[], claim_type="general")
check(
    "resolve_coverage_gate: empty jurisdictions -> federal threshold=15, headcount=10 -> applies=False",
    _gate_federal_uncovered == CoverageResult(
        applies=False, threshold=15, claim_type="general",
        driving_jurisdiction=None, confidence="FEDERAL_FALLBACK",
        partial_state_flag=False, partial_jurisdictions_considered=(),
    ),
    f"got {_gate_federal_uncovered}",
)
_gate_federal_covered = resolve_coverage_gate(headcount=20, jurisdictions=[], claim_type="general")
check(
    "resolve_coverage_gate: empty jurisdictions -> federal threshold=15, headcount=20 -> applies=True",
    _gate_federal_covered.applies is True and _gate_federal_covered.confidence == "FEDERAL_FALLBACK",
    f"got {_gate_federal_covered}",
)
_gate_fmla = resolve_coverage_gate(headcount=40, jurisdictions=[], claim_type="fmla")
check(
    "resolve_coverage_gate: claim_type='fmla' federal fallback is 50, not 15 -- headcount=40 -> applies=False",
    _gate_fmla.threshold == 50 and _gate_fmla.applies is False,
    f"got {_gate_fmla}",
)


# -- 37. resolve_coverage_gate() -- claim_type changes the resolved threshold ----
# CA: general=5, harassment=1. Same headcount (3), different claim_type ->
# different applies outcome.

_gate_ca_general = resolve_coverage_gate(headcount=3, jurisdictions=["CA"], claim_type="general")
_gate_ca_harassment = resolve_coverage_gate(headcount=3, jurisdictions=["CA"], claim_type="harassment")
check(
    "resolve_coverage_gate: CA headcount=3, claim_type='general' (threshold=5) -> applies=False",
    _gate_ca_general.threshold == 5 and _gate_ca_general.applies is False,
    f"got {_gate_ca_general}",
)
check(
    "resolve_coverage_gate: CA headcount=3, claim_type='harassment' (threshold=1) -> applies=True -- "
    "same state, same headcount, different claim_type flips the outcome",
    _gate_ca_harassment.threshold == 1 and _gate_ca_harassment.applies is True,
    f"got {_gate_ca_harassment}",
)


# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
# STRUCTURAL CHANGE as of batch 9: this test was substituted three
# times across the workstream (TX -> AL, batch 0; AL -> MS, batch 5;
# MS -> SC, batch 6) by pointing at whichever real state was still
# PARTIAL. As of batch 9, STATE_COVERAGE_THRESHOLDS has zero PARTIAL
# entries left -- all 51 jurisdictions are CONFIRMED -- so no real
# state can serve this purpose anymore. Rewritten to the same
# save/mutate/restore monkey-patch convention test 39 (below) already
# uses for the same underlying reason: temporarily overwrites SC's
# entry with a synthetic PARTIAL fixture, then restores SC's real
# CONFIRMED entry in a finally block. Durable against every future
# state's CONFIRMED status, including SC's own -- no further
# substitution will be needed. Confirms PARTIAL data never produces
# confidence="CONFIRMED" or a driving_jurisdiction, even though it's
# present in the input and does surface as a qualitative flag.

_original_sc_entry_38 = STATE_COVERAGE_THRESHOLDS["SC"]
try:
    _ft.STATE_COVERAGE_THRESHOLDS["SC"] = StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="no_damages_available",
        confidence="PARTIAL",
        citation="Synthetic test fixture -- not real data, restored after this check.",
    )
    _gate_partial_only = resolve_coverage_gate(headcount=20, jurisdictions=["SC"], claim_type="general")
    check(
        "resolve_coverage_gate: PARTIAL-only jurisdiction list -> confidence='FEDERAL_FALLBACK', "
        "NOT 'CONFIRMED' -- a PARTIAL state's own number never drives the determination",
        _gate_partial_only.confidence == "FEDERAL_FALLBACK" and _gate_partial_only.driving_jurisdiction is None,
        f"got {_gate_partial_only}",
    )
    check(
        "resolve_coverage_gate: PARTIAL-only jurisdiction list still raises the qualitative flag, "
        "naming SC specifically, rather than silently using its unverified threshold",
        _gate_partial_only.partial_state_flag is True
        and _gate_partial_only.partial_jurisdictions_considered == ("SC",),
        f"got {_gate_partial_only}",
    )
finally:
    _ft.STATE_COVERAGE_THRESHOLDS["SC"] = _original_sc_entry_38


# -- 39. resolve_coverage_gate() -- PARTIAL state present but NOT the deciding factor --
# Real seed data can't exercise this (every PARTIAL placeholder defaults to
# 15, which can never be lower than a CONFIRMED state's own threshold, so it
# can never flip a CONFIRMED-driven outcome) -- temporarily monkey-patches
# TX's entry to a synthetic lower threshold, same save/mutate/restore
# convention already used elsewhere in this file for STATE_CRITERIA.

_original_tx_entry = STATE_COVERAGE_THRESHOLDS["TX"]
try:
    _ft.STATE_COVERAGE_THRESHOLDS["TX"] = StateCoverageThreshold(
        thresholds={"general": 3},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="Synthetic test fixture -- not real data, restored after this check.",
    )
    # WV (CONFIRMED, threshold=12) alone: headcount=10 -> applies=False.
    # If TX's synthetic threshold=3 had been trusted too: min(12,3)=3 ->
    # headcount=10 -> applies=True. The two disagree -> partial_state_flag
    # must be True, while the RETURNED applies/threshold/driving_jurisdiction
    # still reflect WV/CONFIRMED-only (12/False), never TX's number.
    _gate_flip_candidate = resolve_coverage_gate(headcount=10, jurisdictions=["WV", "TX"], claim_type="general")
    check(
        "resolve_coverage_gate: CONFIRMED-driven answer (WV, threshold=12, applies=False) is unaffected by "
        "the PARTIAL state's own (synthetic, lower) threshold",
        _gate_flip_candidate.applies is False
        and _gate_flip_candidate.threshold == 12
        and _gate_flip_candidate.driving_jurisdiction == "WV"
        and _gate_flip_candidate.confidence == "CONFIRMED",
        f"got {_gate_flip_candidate}",
    )
    check(
        "resolve_coverage_gate: partial_state_flag=True -- TX's (synthetic) threshold, if counted, "
        "would have flipped applies from False to True, even though WV's real CONFIRMED answer is what's returned",
        _gate_flip_candidate.partial_state_flag is True
        and _gate_flip_candidate.partial_jurisdictions_considered == ("TX",),
        f"got {_gate_flip_candidate}",
    )
finally:
    _ft.STATE_COVERAGE_THRESHOLDS["TX"] = _original_tx_entry

check(
    "TX's real entry was restored cleanly after the monkey-patch above",
    STATE_COVERAGE_THRESHOLDS["TX"] == _original_tx_entry,
    f"got {STATE_COVERAGE_THRESHOLDS['TX']}",
)


# -- 40. Integration -- coverage gate actually wired into Clusters 1, 2, 4b ------
# Confirms the end-to-end wiring through compute_legal_compliance_exposure(),
# not just the standalone resolve_coverage_gate() function in isolation.

_r_c1_blocked = compute_legal_compliance_exposure(
    state_ids=["built_to_fail"],  # Cluster 1
    org_size=10,  # below the federal threshold (15), no jurisdictions given
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Integration, Cluster 1: built_to_fail at headcount=10 with no jurisdictions (federal fallback=15) "
    "-> genuinely None/None, not a reduced figure -- coverage gate blocks it before pricing",
    _r_c1_blocked == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_c1_blocked}",
)
_r_c1_covered = compute_legal_compliance_exposure(
    state_ids=["built_to_fail"],
    org_size=20,  # above the federal threshold
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Integration, Cluster 1 positive control: same state at headcount=20 (covered) prices normally "
    "at its real floor ($50,000) -- the gate blocks only genuinely uncovered orgs, not everyone",
    _r_c1_covered == {
        "low": 50_000.0, "high": 50_000.0, "currency": "USD", "band": "Minor",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "federal_baseline", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_c1_covered}",
)
_r_c2_blocked = compute_legal_compliance_exposure(
    state_ids=["pay_exposure"],  # Cluster 2
    org_size=10,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Integration, Cluster 2: pay_exposure at headcount=10 with no jurisdictions -> None/None",
    _r_c2_blocked == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_c2_blocked}",
)
_r_c4b_blocked = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],  # Cluster 4, Founder-led -> 4b
    org_size=10,
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "Integration, Cluster 4b: hr_capture at headcount=10 with no jurisdictions -> None/None -- coverage "
    "gate runs before the existing headcount-bucket pricing-ceiling lookup, per the spec",
    _r_c4b_blocked == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_c4b_blocked}",
)
_r_c4a_unaffected = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],
    org_size=10,  # same tiny headcount
    industry="Professional Services",
    org_type="Publicly traded",  # 4a -- coverage gate does not apply here
)
check(
    "Integration, Cluster 4a unaffected: 'Publicly traded' routes to 4a regardless of headcount -- "
    "the coverage gate is scoped to 4b only, confirmed by this still pricing at the real $33M ceiling",
    _r_c4a_unaffected == {
        "low": 33_000_000.0, "high": 33_000_000.0, "currency": "USD", "band": "Significant",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_c4a_unaffected}",
)
_r_c4c_unaffected = compute_legal_compliance_exposure(
    state_ids=["hr_capture"],
    org_size=10,
    industry="Professional Services",
    org_type="Government",  # 4c -- coverage gate does not apply here either
)
check(
    "Integration, Cluster 4c unaffected: 'Government' still routes to QUALITATIVE_ONLY regardless of "
    "headcount -- the coverage gate is scoped to 4b only, not the whole of Cluster 4",
    _r_c4c_unaffected == {
        "low": None, "high": None, "currency": "USD", "band": None,
        "has_unpriced_conditions": True, "unpriced_state_ids": ["hr_capture"], "coverage_basis": None, "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_c4c_unaffected}",
)
_r_c1_ny_covered = compute_legal_compliance_exposure(
    state_ids=["built_to_fail"],
    org_size=5,  # below federal 15, but NY's own general threshold is 4
    industry="Professional Services",
    org_type="Founder-led",
    jurisdictions=["NY"],
)
check(
    "Integration: headcount=5 fails the federal threshold (15) but clears NY's real threshold (4) when "
    "jurisdictions=['NY'] is actually passed through from intake -- prices normally",
    _r_c1_ny_covered == {
        "low": 50_000.0, "high": 50_000.0, "currency": "USD", "band": "Minor",
        "has_unpriced_conditions": False, "unpriced_state_ids": [], "coverage_basis": "state_specific", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": False,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_c1_ny_covered}",
)


# -- 41. resolve_damages_treatment() -- one real state per value, plus fallback --

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
_r_va_noop = _ft._cluster_4_curve_for_org_type("Founder-led", "1000+", 1000, ["VA"], "Professional Services")
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
)
_r_c4b_uncapped = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 300, ["CA"], "Professional Services")
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
    and _ft.STATE_CRITERIA["the_arbitrary_standard"].legal > 0,
    f"got cluster={_ft.LEGAL_COMPLIANCE_CLUSTER.get('the_arbitrary_standard')!r}, "
    f"score={_ft.STATE_CRITERIA['the_arbitrary_standard'].legal!r}",
)
check(
    "Cluster 2, CA (uncapped): is_floor is NOT set (stays False) -- Cluster 2's dollar values are two "
    "fixed discrete tiers, not a curve with a floor/ceiling, so the floor-not-ceiling question doesn't "
    "apply regardless of damages_cap_treatment",
    _r_c2_no_floor.status == LegalPricingStatus.PRICED and _r_c2_no_floor.is_floor is False,
    f"got {_r_c2_no_floor}",
)


# -- 45. AR/DE/TN -- confirmed still fully generic/unconsumed (Phase 2a) --

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
    _r_c4b = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 300, [_sid], "Professional Services")
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
_r_co_14 = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 14, ["CO"], "Professional Services")
check(
    "Cluster 4b, CO alone, headcount=14 (below the federal floor): is_floor=True, generic $200,000 "
    "ceiling -- CO's own tiers haven't yielded to federal yet, still a placeholder",
    _r_co_14.status == LegalPricingStatus.PRICED
    and _r_co_14.curve.ceiling == 200_000.0
    and _r_co_14.is_floor is True,
    f"got {_r_co_14}",
)
_r_co_15 = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 15, ["CO"], "Professional Services")
check(
    "Cluster 4b, CO alone, headcount=15 (at the federal floor): is_floor=False now -- same $200,000 "
    "ceiling (Cluster 4b's table already IS the federal table, so the number itself doesn't move), "
    "but it's now Colorado's own real, confirmed answer, not a placeholder",
    _r_co_15.status == LegalPricingStatus.PRICED
    and _r_co_15.curve.ceiling == 200_000.0
    and _r_co_15.is_floor is False,
    f"got {_r_co_15}",
)
_r_co_ca_15 = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 15, ["CO", "CA"], "Professional Services")
check(
    "Cluster 4b, CO+CA, headcount=15: is_floor=True -- CA (uncapped) outranks CO here, so the "
    "resolved treatment is 'uncapped', not 'state_specific_tiers', and CO's federal-deferral branch "
    "never engages even though headcount clears the floor and CO is present",
    _r_co_ca_15.status == LegalPricingStatus.PRICED
    and _r_co_ca_15.curve.ceiling == 200_000.0
    and _r_co_ca_15.is_floor is True,
    f"got {_r_co_ca_15}",
)


# -- 48. OH -- real R.C. 2315.21 formula, PRICED (Phase 2b wiring, superseded this session -- --
# -- Priority Queue item 9 -- by _oh_compensatory_damages_pricing()) --

# -- 48a. _oh_is_small_employer() -- the four boundary combinations --

check(
    "_oh_is_small_employer(50, 'Professional Services') is True -- headcount alone clears the "
    "<=100 general small-employer threshold",
    _ft._oh_is_small_employer(50, "Professional Services") is True,
    f"got {_ft._oh_is_small_employer(50, 'Professional Services')!r}",
)
check(
    "_oh_is_small_employer(150, 'Manufacturing') is True -- exceeds the general "
    "100 threshold but still clears the manufacturing-specific <=500 threshold",
    _ft._oh_is_small_employer(150, "Manufacturing") is True,
    f"got {_ft._oh_is_small_employer(150, 'Manufacturing')!r}",
)
check(
    "_oh_is_small_employer(150, 'Professional Services') is False -- same headcount as the check "
    "above, but non-manufacturing industry doesn't get the extended 500 threshold, only the 100 one",
    _ft._oh_is_small_employer(150, "Professional Services") is False,
    f"got {_ft._oh_is_small_employer(150, 'Professional Services')!r}",
)
check(
    "_oh_is_small_employer(600, 'Manufacturing') is False -- exceeds even the "
    "manufacturing-specific 500 threshold, general branch governs",
    _ft._oh_is_small_employer(600, "Manufacturing") is False,
    f"got {_ft._oh_is_small_employer(600, 'Manufacturing')!r}",
)
check(
    "_oh_is_small_employer('', 'Manufacturing') is False -- non-numeric/unclassifiable "
    "headcount defaults to the general branch's more conservative statutory mechanics",
    _ft._oh_is_small_employer("", "Manufacturing") is False,
    f"got {_ft._oh_is_small_employer('', 'Manufacturing')!r}",
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

# -- 48c. Integration -- Clusters 1, 2, 4b all resolve OH to PRICED (Priority Queue item 9, -- --
# -- this session -- was QUALITATIVE_ONLY before _oh_compensatory_damages_pricing() was wired --
# -- in; expected dollar figures independently derived, not copied from implementation output: --
# -- compensatory_base = _LEGAL_WAGE_DATA_MAY2023["Professional Services"][0] (102,670.0) x --
# -- _JURISDICTION_MULTIPLIER_DATA["OH"][0] (0.9228) = 94,743.876; 2x = 189,487.752, which is --
# -- under the $350,000 small-employer cap either way, so headcount=20 (small, capped) and --
# -- headcount=300 (general, uncapped) happen to produce the same number here by coincidence --
# -- of this specific industry/multiplier combination, not because the two branches collapse --
# -- to one -- their status/is_floor/may_overstate_for_uncollected_net_worth fields differ. --

_r_oh_c1 = _ft._single_state_legal_pricing(
    "the_paper_tiger", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["OH"],
)
check(
    "Cluster 1, OH, headcount=20 (small employer): PRICED, dollar_range=(189487.752, 189487.752) "
    "(2x compensatory, capped at $350,000 -- doesn't bind here), coverage_confidence threaded "
    "through as real CONFIRMED (not hardcoded NOT_APPLICABLE), is_floor=False, "
    "may_overstate_for_uncollected_net_worth=True (net_worth alternative not computed)",
    _r_oh_c1.status == LegalPricingStatus.PRICED
    and _r_oh_c1.dollar_range == (189487.75199999998, 189487.75199999998)
    and _r_oh_c1.coverage_confidence == "CONFIRMED"
    and _r_oh_c1.partial_state_flag is False
    and _r_oh_c1.is_floor is False
    and _r_oh_c1.may_overstate_for_uncollected_net_worth is True,
    f"got {_r_oh_c1}",
)
check(
    "sanity: the_arbitrary_standard is a real Cluster 2 state with a non-zero legal score, needed "
    "for the check below",
    _ft.LEGAL_COMPLIANCE_CLUSTER.get("the_arbitrary_standard") == 2
    and _ft.STATE_CRITERIA["the_arbitrary_standard"].legal > 0,
    f"got cluster={_ft.LEGAL_COMPLIANCE_CLUSTER.get('the_arbitrary_standard')!r}",
)
_r_oh_c2 = _ft._single_state_legal_pricing(
    "the_arbitrary_standard", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["OH"],
)
check(
    "Cluster 2, OH, headcount=20 (small employer): PRICED, same dollar_range and flags as Cluster "
    "1 above -- Ohio's formula is cluster-independent, doesn't fall through to the fixed discrete "
    "tiers",
    _r_oh_c2.status == LegalPricingStatus.PRICED
    and _r_oh_c2.dollar_range == (189487.75199999998, 189487.75199999998)
    and _r_oh_c2.coverage_confidence == "CONFIRMED"
    and _r_oh_c2.is_floor is False
    and _r_oh_c2.may_overstate_for_uncollected_net_worth is True,
    f"got {_r_oh_c2}",
)
_r_oh_c4b = _ft._cluster_4_curve_for_org_type(
    "Founder-led", "250-499", 300, ["OH"], "Professional Services",
)
check(
    "Cluster 4b, OH, headcount=300 (general employer -- 300 > 100, not Manufacturing): "
    "PRICED, flat curve floor==ceiling==189487.752 (2x compensatory, uncapped -- "
    "same number as the small-employer case above by coincidence of this industry/multiplier "
    "combo, not because the branches collapse), is_floor=True (standard 'uncapped' semantics, no "
    "direction mismatch), may_overstate_for_uncollected_net_worth=False (general-employer branch "
    "never sets it) -- no longer falls through to the generic $200,000 ceiling",
    _r_oh_c4b.status == LegalPricingStatus.PRICED
    and _r_oh_c4b.curve is not None
    and _r_oh_c4b.curve.floor == 189487.75199999998
    and _r_oh_c4b.curve.ceiling == 189487.75199999998
    and _r_oh_c4b.is_floor is True
    and _r_oh_c4b.may_overstate_for_uncollected_net_worth is False,
    f"got {_r_oh_c4b}",
)
check(
    "Cluster 4b, OH, headcount=300: _legal_score_fraction(curve, score) collapses to exactly "
    "curve.floor regardless of score when floor == ceiling -- confirms the flat-curve trick "
    "actually bypasses score-scaling in the real code path, not just in isolated theory",
    _ft._legal_score_fraction(_r_oh_c4b.curve, 1) == 189487.75199999998
    and _ft._legal_score_fraction(_r_oh_c4b.curve, 4) == 189487.75199999998,
    f"got score=1: {_ft._legal_score_fraction(_r_oh_c4b.curve, 1)}, "
    f"score=4: {_ft._legal_score_fraction(_r_oh_c4b.curve, 4)}",
)

# -- 48d. compute_legal_compliance_exposure() -- OH now PRICED, same shape/rounding as any --
# -- other real single-state PRICED result (round(x, 2), band from _legal_exposure_band()) --

_r_oh_aggregate = compute_legal_compliance_exposure(
    state_ids=["the_paper_tiger"],
    org_size=20,
    industry="Professional Services",
    org_type="Founder-led",
    jurisdictions=["OH"],
)
check(
    "compute_legal_compliance_exposure(), OH, headcount=20: low=high=189487.75 (rounded), "
    "band='Moderate' ($100,000-$500,000), has_unpriced_conditions=False, unpriced_state_ids=[], "
    "coverage_basis='state_specific' (CONFIRMED-only), has_partial_jurisdictions=False, "
    "has_uncollected_net_worth_caveat=True (headcount=20 is the small-employer branch) -- was "
    "the all-None/has_unpriced_conditions=True shape before this session's build",
    _r_oh_aggregate == {
        "low": 189487.75, "high": 189487.75, "currency": "USD", "band": "Moderate",
        "has_unpriced_conditions": False, "unpriced_state_ids": [],
        "coverage_basis": "state_specific", "has_partial_jurisdictions": False,
        "has_uncollected_net_worth_caveat": True,
        "specific_caveat_jurisdiction": None,
    },
    f"got {_r_oh_aggregate}",
)


# -- 49. ME -- verified tier boundaries confirmed stable, generic/unconsumed (Phase 2c) --

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

_r_c4b_me = _ft._cluster_4_curve_for_org_type("Founder-led", "250-499", 300, ["ME"], "Professional Services")
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
        "has_uncollected_net_worth_caveat": False,
        # ME is state_specific_tiers and drives this result, but ME has no
        # entry in contract.py's _SPECIFIC_CAVEAT_TEXT (only AR/MD/TN do)
        # -- friction_tax.py itself doesn't filter by "has a caveat", it
        # reports the winning jurisdiction id unconditionally whenever
        # state_specific_flat/tiers governs, so this is "ME", not None.
        # The None-vs-text split happens one layer up, in contract.py.
        "specific_caveat_jurisdiction": "ME",
    },
    f"got {_r_me_aggregate}",
)


# -- 50. specific_caveat_jurisdiction -- 7 per-state caveats (is_floor scoping --
# follow-up, this session). Verifies the two deliberately-different tie-break
# rules stay different, the field propagates correctly through both Cluster 1
# and Cluster 4b, and the None-unpacking path added to _resolve_flat_cap()'s
# two call sites is safe.

# (a) FL+VA together: _resolve_flat_cap()'s own tie-break is MAXIMUM VALUE,
# order-independent -- pre-existing, already-shipped behavior for FL/ID/KS/VA,
# unchanged by adding the jurisdiction id to the return value.
check(
    "_resolve_flat_cap(['FL','VA']) == (350000.0, 'VA') -- VA's $350,000 beats "
    "FL's $100,000 by value, FL listed first",
    _ft._resolve_flat_cap(["FL", "VA"]) == (350_000.0, "VA"),
    f"got {_ft._resolve_flat_cap(['FL', 'VA'])!r}",
)
check(
    "_resolve_flat_cap(['VA','FL']) == (350000.0, 'VA') -- same result with VA "
    "listed first, confirming the tie-break is genuinely value-based, not "
    "input-order (contrast with (c) below)",
    _ft._resolve_flat_cap(["VA", "FL"]) == (350_000.0, "VA"),
    f"got {_ft._resolve_flat_cap(['VA', 'FL'])!r}",
)

# (b) specific_caveat_jurisdiction correctly reports VA as the winner in the
# FL+VA case, threaded through a real Cluster 1 pricing call. the_paper_tiger
# (legal score=2) reaches _CLUSTER_1_CURVE's ceiling exactly, so VA's $350,000
# flat_cap visibly clamps the curve (450,000 -> 350,000) as well as winning
# the jurisdiction id -- both effects verified in the same assertion.
_r_fl_va = _ft._single_state_legal_pricing(
    "the_paper_tiger", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["FL", "VA"],
)
check(
    "Cluster 1, FL+VA: dollar_range=(350000,350000) (VA's flat_cap clamps the "
    "curve ceiling down from 450,000), is_floor=True, "
    "specific_caveat_jurisdiction='VA'",
    _r_fl_va.status == LegalPricingStatus.PRICED
    and _r_fl_va.dollar_range == (350_000.0, 350_000.0)
    and _r_fl_va.is_floor is True
    and _r_fl_va.specific_caveat_jurisdiction == "VA",
    f"got {_r_fl_va}",
)

# (c) AR+TX together: _state_specific_tiers_driver()'s tie-break is FIRST-
# ENCOUNTERED-IN-INPUT-LIST-WINS, proven via the same pattern as the existing
# _oh_drives_tiers_result(['OH','TX']) vs (['TX','OH']) test pair above --
# deliberately the OPPOSITE rule from (a)/(resolve_flat_cap)'s value-based tie-break.
check(
    "_state_specific_tiers_driver(['AR','TX']) == 'AR' -- genuine tie (both "
    "state_specific_tiers, rank 3), AR listed first wins by input order",
    _ft._state_specific_tiers_driver(["AR", "TX"]) == "AR",
    f"got {_ft._state_specific_tiers_driver(['AR', 'TX'])!r}",
)
check(
    "_state_specific_tiers_driver(['TX','AR']) == 'TX' -- same tie, opposite "
    "input order, TX wins instead -- confirms input-order dependence, not "
    "value-based like _resolve_flat_cap()",
    _ft._state_specific_tiers_driver(["TX", "AR"]) == "TX",
    f"got {_ft._state_specific_tiers_driver(['TX', 'AR'])!r}",
)
_r_ar_tx = _ft._single_state_legal_pricing(
    "built_to_fail", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["AR", "TX"],
)
_r_tx_ar = _ft._single_state_legal_pricing(
    "built_to_fail", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=["TX", "AR"],
)
check(
    "Cluster 1, AR+TX (AR first): specific_caveat_jurisdiction='AR' (AR is one "
    "of the 3 tiers-caveat states)",
    _r_ar_tx.specific_caveat_jurisdiction == "AR",
    f"got {_r_ar_tx.specific_caveat_jurisdiction!r}",
)
check(
    "Cluster 1, TX+AR (TX first): specific_caveat_jurisdiction='TX' -- an "
    "identifier is still reported even though TX has no entry in "
    "_SPECIFIC_CAVEAT_TEXT; the None-vs-text split happens in contract.py, "
    "not friction_tax.py (verified in (e) below)",
    _r_tx_ar.specific_caveat_jurisdiction == "TX",
    f"got {_r_tx_ar.specific_caveat_jurisdiction!r}",
)

# (d) each of the 7 states in isolation produces its own correct caveat text
# end-to-end through the friction_tax.py -> contract.py dict chain.
_EXPECTED_CAVEAT_SUBSTRINGS = {
    "FL": "capped at $100,000 under Fla. Stat. Sec 760.11(5)",
    "ID": "capped at $1,000 per violation under Idaho Code Sec 67-5908(3)(e)",
    "KS": "capped at $2,000 under K.S.A. Sec 44-1005(k)",
    "VA": "capped at $350,000 under Va. Code Sec 8.01-38.1",
    "AR": "Arkansas law doesn't cap damages for retaliation claims",
    "MD": "Howard, Montgomery, and Prince George's counties",
    "TN": "Tennessee law doesn't cap damages for race-discrimination claims",
}
for _jid, _substring in _EXPECTED_CAVEAT_SUBSTRINGS.items():
    _r_solo = _ft._single_state_legal_pricing(
        "the_paper_tiger", org_size="Under 25", industry="Professional Services",
        org_type="Founder-led", headcount=20, jurisdictions=[_jid],
    )
    _resolved_text = _SPECIFIC_CAVEAT_TEXT.get(_r_solo.specific_caveat_jurisdiction)
    check(
        f"{_jid} in isolation: specific_caveat_jurisdiction='{_jid}', and "
        f"_SPECIFIC_CAVEAT_TEXT['{_jid}'] resolves to real text containing "
        f"the verified citation/statute substring",
        _r_solo.specific_caveat_jurisdiction == _jid
        and _resolved_text is not None
        and _substring in _resolved_text,
        f"got specific_caveat_jurisdiction={_r_solo.specific_caveat_jurisdiction!r}, "
        f"resolved_text={_resolved_text!r}",
    )

# (e) states with NO specific caveat correctly get None throughout, no crash
# on the None-unpacking path added to both _resolve_flat_cap() call sites.
check(
    "_resolve_flat_cap([]) is None -- empty input, no crash unpacking a bare "
    "None as a tuple",
    _ft._resolve_flat_cap([]) is None,
    f"got {_ft._resolve_flat_cap([])!r}",
)
check(
    "_state_specific_tiers_driver([]) is None -- empty input",
    _ft._state_specific_tiers_driver([]) is None,
    f"got {_ft._state_specific_tiers_driver([])!r}",
)
for _jid, _label in (
    ("NY", "uncapped"),
    ("DE", "state_specific_tiers, no specific caveat written"),
    ("CO", "state_specific_tiers, no specific caveat written"),
    ("MO", "state_specific_tiers, no specific caveat written"),
    ("TX", "state_specific_tiers, no specific caveat written"),
):
    _r_none = _ft._single_state_legal_pricing(
        "built_to_fail", org_size="Under 25", industry="Professional Services",
        org_type="Founder-led", headcount=20, jurisdictions=[_jid],
    )
    check(
        f"{_jid} ({_label}) via Cluster 1: no crash, status=PRICED, "
        f"specific_caveat_jurisdiction is {'not None' if _jid in ('DE','CO','MO','TX') else 'None'} "
        f"and _SPECIFIC_CAVEAT_TEXT.get(...) is None (no text written for this state)",
        _r_none.status == LegalPricingStatus.PRICED
        and _SPECIFIC_CAVEAT_TEXT.get(_r_none.specific_caveat_jurisdiction) is None,
        f"got specific_caveat_jurisdiction={_r_none.specific_caveat_jurisdiction!r}",
    )
_r_empty_jurisdictions = _ft._single_state_legal_pricing(
    "built_to_fail", org_size="Under 25", industry="Professional Services",
    org_type="Founder-led", headcount=20, jurisdictions=[],
)
check(
    "empty jurisdictions list: no crash, specific_caveat_jurisdiction is None "
    "(treatment defaults to federal_cap_applies, neither flat_cap nor tiers "
    "branch fires)",
    _r_empty_jurisdictions.specific_caveat_jurisdiction is None,
    f"got {_r_empty_jurisdictions.specific_caveat_jurisdiction!r}",
)
# Same None-unpacking safety, Cluster 4b path (the other of the two call sites).
_r_4b_none = _ft._cluster_4_curve_for_org_type(
    "Founder-led", "250-499", 300, [], "Professional Services",
)
check(
    "Cluster 4b, empty jurisdictions: no crash, specific_caveat_jurisdiction is None",
    _r_4b_none.status == LegalPricingStatus.PRICED
    and _r_4b_none.specific_caveat_jurisdiction is None,
    f"got {_r_4b_none}",
)
_r_4b_va = _ft._cluster_4_curve_for_org_type(
    "Founder-led", "250-499", 300, ["VA"], "Professional Services",
)
check(
    "Cluster 4b, VA: no crash unpacking the (value, jid) tuple, "
    "specific_caveat_jurisdiction='VA'",
    _r_4b_va.status == LegalPricingStatus.PRICED
    and _r_4b_va.specific_caveat_jurisdiction == "VA",
    f"got {_r_4b_va}",
)


# -- Stage 3 (R1): frozen Legal wage table and the May 2025 friction wage table --

_MAY2023_WAGES = {
    "Professional Services": 102670.0, "Healthcare & Life Sciences": 67320.0,
    "Financial Services": 94150.0, "Technology": 108110.0, "Manufacturing": 64440.0,
    "Retail & Hospitality": 39651.0, "Nonprofit & Education": 57770.0,
    "Government & Public Sector": 74410.0, "Construction": 67430.0,
    "Transportation & Warehousing": 59320.0, "Other": 63446.0,
}
_MAY2025_WAGES = {
    "Professional Services": 108640.0, "Healthcare & Life Sciences": 70969.0,
    "Financial Services": 100842.0, "Technology": 115030.0, "Manufacturing": 69131.0,
    "Retail & Hospitality": 42024.0, "Nonprofit & Education": 72765.0,
    "Government & Public Sector": 80290.0, "Construction": 72146.0,
    "Transportation & Warehousing": 64331.0, "Other": 67977.0,
}
check(
    "_LEGAL_WAGE_DATA_MAY2023 holds exactly the 11 May 2023 wages, unchanged (Legal byte-identity, R1)",
    {k: v[0] for k, v in _ft._LEGAL_WAGE_DATA_MAY2023.items()} == _MAY2023_WAGES,
    f"got {({k: v[0] for k, v in _ft._LEGAL_WAGE_DATA_MAY2023.items()})}",
)
check(
    "_LEGAL_WAGE_DATA_MAY2023 entries are all May 2023 sourced",
    all("May 2023" in v[1] and v[2].startswith("BLS_OEWS_2023") for v in _ft._LEGAL_WAGE_DATA_MAY2023.values()),
)
check(
    "_INDUSTRY_WAGE_DATA holds exactly the 11 verified May 2025 wages (spec Section 3)",
    {k: v[0] for k, v in _ft._INDUSTRY_WAGE_DATA.items()} == _MAY2025_WAGES,
    f"got {({k: v[0] for k, v in _ft._INDUSTRY_WAGE_DATA.items()})}",
)
check(
    "_INDUSTRY_WAGE_DATA keys equal INDUSTRIES and the frozen table's keys",
    set(_ft._INDUSTRY_WAGE_DATA) == set(INDUSTRIES) == set(_ft._LEGAL_WAGE_DATA_MAY2023),
)
check(
    "every May 2025 entry carries provenance (oesm25in4.zip, nat3d_M2025_dl.xlsx) and a BLS_OEWS_2025 citation id",
    all("oesm25in4.zip" in v[1] and "nat3d_M2025_dl.xlsx" in v[1] and v[2].startswith("BLS_OEWS_2025")
        for v in _ft._INDUSTRY_WAGE_DATA.values()),
)
check(
    "the two privately owned entries name the owner file (Decision 12)",
    "nat3d_owner_M2025_dl.xlsx" in _ft._INDUSTRY_WAGE_DATA["Healthcare & Life Sciences"][1]
    and "nat3d_owner_M2025_dl.xlsx" in _ft._INDUSTRY_WAGE_DATA["Nonprofit & Education"][1],
)
check(
    "get_industry_wage returns the May 2025 wage for all 11 industries and None for an unknown one",
    all(_ft.get_industry_wage(k) == v for k, v in _MAY2025_WAGES.items())
    and _ft.get_industry_wage("Not An Industry") is None,
)

_oh_args = dict(org_size="Under 25", industry="Professional Services", org_type="Founder-led",
                headcount=20, jurisdictions=["OH"])
_oh_before = _ft._single_state_legal_pricing("the_paper_tiger", **_oh_args)
_saved_new = _ft._INDUSTRY_WAGE_DATA["Professional Services"]
_ft._INDUSTRY_WAGE_DATA["Professional Services"] = (1.0,) + _saved_new[1:]
_oh_new_changed = _ft._single_state_legal_pricing("the_paper_tiger", **_oh_args)
_ft._INDUSTRY_WAGE_DATA["Professional Services"] = _saved_new
check(
    "Legal's Ohio compensatory formula ignores _INDUSTRY_WAGE_DATA (changing it does not move the Legal figure)",
    _oh_new_changed.dollar_range == _oh_before.dollar_range == (189487.75199999998, 189487.75199999998),
    f"before {_oh_before.dollar_range} after {_oh_new_changed.dollar_range}",
)
_saved_frozen = _ft._LEGAL_WAGE_DATA_MAY2023["Professional Services"]
_ft._LEGAL_WAGE_DATA_MAY2023["Professional Services"] = (1.0,) + _saved_frozen[1:]
_oh_frozen_changed = _ft._single_state_legal_pricing("the_paper_tiger", **_oh_args)
_ft._LEGAL_WAGE_DATA_MAY2023["Professional Services"] = _saved_frozen
check(
    "Legal's Ohio compensatory formula does read _LEGAL_WAGE_DATA_MAY2023 (teeth for the check above)",
    _oh_frozen_changed.dollar_range != _oh_before.dollar_range,
    f"got {_oh_frozen_changed.dollar_range}",
)


print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
