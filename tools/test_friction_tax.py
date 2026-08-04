"""
PRV3 Output Layer -- Friction Tax Unit Tests

Verifies:
  1. SEVERITY_SCALAR: correct values for all three tiers
  2. compute_friction_tax: calibration_complete=True on a real, fully
     unmocked call -- all three calibration axes (grid, org_type,
     STATE_MULTIPLIERS) are now populated. Expected low/high computed
     from real, live values, not hardcoded
  3. compute_friction_tax: calibration_complete=False for empty state list
  4. compute_friction_tax: single-state case computed correctly against a
     synthetic fixture whose criteria scores (not a bare multiplier) drive
     the expected attritional_fraction -- the new design reads
     STATE_MULTIPLIERS[sid].criteria directly, not .multiplier, so a
     fixture must set real criteria scores to be meaningful
  5. compute_friction_tax: high = low * 1.4
  6. compute_friction_tax: correct severity scalar applied
  7. compute_friction_tax: single-state continuity -- the new Step 1-3
     aggregation path, with exactly one identified state, must collapse
     EXACTLY (bit-for-bit) to that state's own stored STATE_MULTIPLIERS
     entry, across several real states, not just reasoned about
  8. compute_friction_tax: N=1 guard -- multi_channel_severity_loading
     must be exactly 1.0 for a single identified state even when that
     state's own criteria scores span all 3 attritional criteria (the
     case most likely to accidentally trigger loading if the guard were
     missing)
  9. compute_friction_tax: multi-state Step 1 (per-criterion geometric
     decay aggregation) computed against hand-derived expected values,
     not just "did it run"
  10. compute_friction_tax: multi-state Step 3 (multi_channel_severity_
      loading, K=0.05, breadth 1-3) computed against hand-derived expected
      values, including a case where one criterion stays at zero across
      every identified state (breadth < 3)
  11. compute_friction_tax: extrapolation beyond R_max=6 when multiple
      high-scoring states are stacked -- combined_multiplier must exceed
      0.25 rather than clamp, per the frozen-range design
  12. compute_friction_tax: calibration_complete False when the grid cell
      is forced back to None (org_type real, state_multiplier mocked)
  13. compute_friction_tax: calibration_complete False when the org_type
      scalar is forced back to None (grid real, state_multiplier mocked)
  14. PAYROLL_BASELINE_GRID: exactly 54 cells, all combinations present,
      every cell's payroll_floor_annual independently recomputed and
      verified against industry_wage x headcount_midpoint
  15. PAYROLL_BASELINE_GRID: all 9 industries (not just 6) carry a
      source/citation_id
  16. ORG_TYPE_SCALARS: exactly 6 entries matching IntakeData.org_type,
      each with the correct finalized scalar value and a non-empty
      source note
  17. STATE_MULTIPLIERS: all state IDs match engine state registry
  18. STATE_MULTIPLIERS: all 57 values are populated StateMultiplierEntry
      records with a real multiplier in [0.05, 0.25] (Option A rescale)
  19. STATE_MULTIPLIERS: every entry's criteria dict still carries all 4
      keys including "legal" (needed by the separate Legal/Compliance
      design), but raw_score sums only the 3 attritional criteria --
      verified against several real states with a nonzero legal score,
      not assumed
  20. compute_friction_tax: calibration_complete is True across the
      full real 6x9x6 (headcount x industry x org_type) combination
      space with real, unmodified data -- exhaustive, not spot-checked
  21. compute_friction_tax: state_ids mixing one real, populated state
      with one unrecognized state_id must still yield
      calibration_complete=False
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

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.friction_tax import (
    SEVERITY_SCALAR,
    STATE_MULTIPLIERS,
    StateCriterionScore,
    StateMultiplierEntry,
    PAYROLL_BASELINE_GRID,
    PayrollBaselineEntry,
    ORG_TYPE_SCALARS,
    OrgTypeScalarEntry,
    HEADCOUNT_BUCKETS,
    INDUSTRIES,
    HEADCOUNT_MIDPOINTS,
    compute_friction_tax,
    INDUSTRY_NON_EXEMPT_RATIO,
    LEGAL_COMPLIANCE_CLUSTER,
    compute_legal_compliance_exposure,
)
from engine.data.states import STATE_PROFILES
from engine.data.intake import INTAKE_FIELDS
import engine.friction_tax as _ft

PASS = []
FAIL = []


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


def _synthetic_entry(turnover: int, productivity: int, decision_quality: int, legal: int = 0) -> StateMultiplierEntry:
    """
    Synthetic StateMultiplierEntry for monkey-patching -- not real
    calibration data. The new compute_friction_tax() reads criteria
    scores directly (Steps 1-3), not the stored .multiplier field, so a
    useful test fixture must set real criteria scores. .multiplier /
    raw_score are still derived via the real formula (not hardcoded) so
    that a single-state continuity check against this fixture is
    meaningful rather than a placeholder.
    """
    raw = turnover + productivity + decision_quality
    return StateMultiplierEntry(
        multiplier=_ft._attritional_fraction(raw),
        raw_score=raw,
        criteria={
            "turnover": StateCriterionScore(score=turnover, rationale="test fixture, not real calibration data"),
            "productivity": StateCriterionScore(score=productivity, rationale="test fixture, not real calibration data"),
            "decision_quality": StateCriterionScore(score=decision_quality, rationale="test fixture, not real calibration data"),
            "legal": StateCriterionScore(score=legal, rationale="test fixture, not real calibration data"),
        },
    )


print("=" * 64)
print("PRV3 Friction Tax -- Unit Tests")
print("=" * 64)


# -- 1. SEVERITY_SCALAR values --------------------------------------------------

check(
    "SEVERITY_SCALAR[Emerging] == 0.6",
    SEVERITY_SCALAR.get("Emerging") == 0.6,
    f"got {SEVERITY_SCALAR.get('Emerging')}",
)
check(
    "SEVERITY_SCALAR[Entrenched] == 1.0",
    SEVERITY_SCALAR.get("Entrenched") == 1.0,
    f"got {SEVERITY_SCALAR.get('Entrenched')}",
)
check(
    "SEVERITY_SCALAR[Endemic] == 1.4",
    SEVERITY_SCALAR.get("Endemic") == 1.4,
    f"got {SEVERITY_SCALAR.get('Endemic')}",
)


# -- 2. calibration_complete True on a real, fully unmocked call ---------------
# All three axes (grid, org_type, STATE_MULTIPLIERS) are real -- nothing
# monkey-patched. Expected low/high derived from the real, live stored
# multiplier (which itself IS the single-state continuity value under the
# new design).

result = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
_real_grid_entry_t2 = PAYROLL_BASELINE_GRID[("100-249", "Professional Services")]
_real_org_type_scalar_t2 = ORG_TYPE_SCALARS["Government"].scalar
_real_multiplier_t2 = STATE_MULTIPLIERS["decision_paralysis"].multiplier
_expected_low_t2 = round(
    _real_grid_entry_t2.payroll_floor_annual * _real_org_type_scalar_t2 * _real_multiplier_t2 * 1.0,
    2,
)
check(
    "calibration_complete True on a real, fully unmocked call (all three axes now populated)",
    result["calibration_complete"] is True,
    f"got calibration_complete={result['calibration_complete']}",
)
check(
    "low computed correctly on a real, fully unmocked call",
    result["low"] == _expected_low_t2,
    f"expected {_expected_low_t2}, got low={result['low']}",
)
check(
    "high == low * 1.4 on a real, fully unmocked call",
    result["high"] == round(_expected_low_t2 * 1.4, 2),
    f"expected {round(_expected_low_t2 * 1.4, 2)}, got high={result['high']}",
)
check(
    "currency is USD",
    result["currency"] == "USD",
    f"got currency={result['currency']}",
)


# -- 3. calibration_complete False for empty state list -------------------------

result_empty = compute_friction_tax(
    state_ids=[],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
check(
    "calibration_complete False for empty state_ids",
    result_empty["calibration_complete"] is False,
    f"got {result_empty['calibration_complete']}",
)


# -- 4-6. Correct computation when fully calibrated (single state) -------------
# Grid and org_type are REAL and unmocked -- only STATE_MULTIPLIERS is
# monkey-patched, with real criteria scores (not a bare multiplier, which
# the new code no longer reads at runtime).

_GRID_KEY = ("100-249", "Professional Services")
_real_grid_entry = PAYROLL_BASELINE_GRID[_GRID_KEY]
_real_org_type_scalar = ORG_TYPE_SCALARS["Government"].scalar

check(
    "sanity: real grid cell used for tests 4-13 is genuinely populated",
    _real_grid_entry.payroll_floor_annual is not None,
    "expected PAYROLL_BASELINE_GRID to be fully populated after this task",
)

_original_multiplier = STATE_MULTIPLIERS.get("decision_paralysis")
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _synthetic_entry(turnover=1, productivity=2, decision_quality=0)
_fixture_fraction = _ft._attritional_fraction(3)  # 1+2+0 = 3

result_cal = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)

check(
    "calibration_complete True when STATE_MULTIPLIERS is the only thing populated",
    result_cal["calibration_complete"] is True,
    f"got {result_cal['calibration_complete']}",
)
_expected_low = round(_real_grid_entry.payroll_floor_annual * _real_org_type_scalar * _fixture_fraction * 1.0, 2)
check(
    "low computed correctly (real payroll_floor_annual * real Government scalar * attritional_fraction(3) * severity_scalar)",
    result_cal["low"] == _expected_low,
    f"expected {_expected_low}, got {result_cal['low']}",
)
check(
    "high == low * 1.4",
    result_cal["high"] == round(result_cal["low"] * 1.4, 2),
    f"expected {round(result_cal['low'] * 1.4, 2)}, got {result_cal['high']}",
)

# Severity scalar applied correctly -- Endemic should produce 1.4x
result_endemic = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Endemic",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
_expected_endemic_low = round(_real_grid_entry.payroll_floor_annual * _real_org_type_scalar * _fixture_fraction * 1.4, 2)
check(
    "Endemic severity scalar 1.4 applied to low",
    result_endemic["low"] == _expected_endemic_low,
    f"expected {_expected_endemic_low}, got {result_endemic['low']}",
)

_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_multiplier


# -- 7. Single-state continuity across several real states ---------------------
# CRITICAL per the locked design: with exactly one identified state, the
# new Step 1-3 aggregation path MUST collapse EXACTLY to that state's own
# stored STATE_MULTIPLIERS entry -- verified directly against several real
# states spanning different raw_score values, not reasoned about.

_continuity_sample = [
    "identity_erosion", "compression_crisis", "invisible_performance_management",
    "the_burned_credibility", "planning_authority_gap", "the_founders_grip",
    "culture_drift", "paper_shield", "the_diversity_ceiling", "the_suppression_filter",
]
_continuity_mismatches = []
for _sid in _continuity_sample:
    _entry = STATE_MULTIPLIERS[_sid]
    _r = compute_friction_tax(
        state_ids=[_sid],
        severity_tier="Entrenched",
        org_size="100-249",
        industry="Technology",
        org_type="Founder-led",
    )
    _grid = PAYROLL_BASELINE_GRID[("100-249", "Technology")]
    _expected = round(_grid.payroll_floor_annual * 1.0 * _entry.multiplier * 1.0, 2)
    if _r["low"] != _expected:
        _continuity_mismatches.append((_sid, _r["low"], _expected))
check(
    "single-state continuity: compute_friction_tax collapses exactly to STATE_MULTIPLIERS[sid].multiplier "
    f"across {len(_continuity_sample)} real states",
    len(_continuity_mismatches) == 0,
    f"mismatches: {_continuity_mismatches}",
)


# -- 8. N=1 guard -- loading forced to 1.0 even when all 3 criteria are nonzero -

# the_founders_grip: turnover=2, productivity=2, decision_quality=2 -- the
# case most likely to accidentally trigger multi_channel_severity_loading
# if the N=1 guard were missing or buggy (breadth would naturally be 3).
_grip_entry = STATE_MULTIPLIERS["the_founders_grip"]
_r_guard = compute_friction_tax(
    state_ids=["the_founders_grip"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Technology",
    org_type="Founder-led",
)
_grid_guard = PAYROLL_BASELINE_GRID[("100-249", "Technology")]
_expected_guard = round(_grid_guard.payroll_floor_annual * 1.0 * _grip_entry.multiplier * 1.0 * 1.0, 2)
check(
    "N=1 guard: multi_channel_severity_loading forced to 1.0 for a single state whose own scores span all 3 criteria",
    _r_guard["low"] == _expected_guard,
    f"expected {_expected_guard} (loading=1.0 forced), got {_r_guard['low']} "
    f"(would be {round(_expected_guard * 1.05, 2)} if loading incorrectly applied at breadth=3)",
)


# -- 9-10. Multi-state Step 1 (geometric decay) + Step 3 (breadth loading) -----
# Hand-derived expected values, not just "did it run without error."

_original_a = STATE_MULTIPLIERS.get("decision_paralysis")
_original_b = STATE_MULTIPLIERS.get("the_exposed")

# Case A: breadth < 3 -- decision_quality stays at 0 for both synthetic
# states, so it must NOT count toward breadth or contribute to the
# combined total.
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _synthetic_entry(turnover=2, productivity=1, decision_quality=0)
_ft.STATE_MULTIPLIERS["the_exposed"] = _synthetic_entry(turnover=1, productivity=2, decision_quality=0)

result_multi_a = compute_friction_tax(
    state_ids=["decision_paralysis", "the_exposed"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
# Step 1: turnover scores [2,1] desc -> 2*1.0 + 1*0.5 = 2.5
#         productivity scores [2,1] desc -> 2*1.0 + 1*0.5 = 2.5
#         decision_quality scores [0,0] -> 0.0
_combined_a = 2.5 + 2.5 + 0.0
_fraction_a = _ft._attritional_fraction(_combined_a)
# Step 3: breadth = 2 (decision_quality is 0 for both, excluded); N=2 so
# the N=1 guard does NOT apply -- loading = 1.0 + 0.05*(2-1) = 1.05
_loading_a = 1.0 + 0.05 * (2 - 1)
_expected_multi_a = round(_real_grid_entry.payroll_floor_annual * _real_org_type_scalar * _fraction_a * _loading_a * 1.0, 2)
check(
    "multi-state Step 1 + Step 3: breadth=2 (one criterion at zero across both states, correctly excluded), "
    "geometric decay 1.0/0.5 weights match hand-derived combined_criterion_score",
    result_multi_a["low"] == _expected_multi_a,
    f"expected {_expected_multi_a} (combined_raw_total={_combined_a}, loading={_loading_a}), got {result_multi_a['low']}",
)

# Case B: breadth = 3 -- every criterion nonzero on at least one state.
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _synthetic_entry(turnover=2, productivity=1, decision_quality=1)
_ft.STATE_MULTIPLIERS["the_exposed"] = _synthetic_entry(turnover=1, productivity=2, decision_quality=1)

result_multi_b = compute_friction_tax(
    state_ids=["decision_paralysis", "the_exposed"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
# turnover [2,1] -> 2.5 ; productivity [2,1] -> 2.5 ; decision_quality [1,1] -> 1*1.0 + 1*0.5 = 1.5
_combined_b = 2.5 + 2.5 + 1.5
_fraction_b = _ft._attritional_fraction(_combined_b)
_loading_b = 1.0 + 0.05 * (3 - 1)  # breadth=3, N=2 -- guard does not apply
_expected_multi_b = round(_real_grid_entry.payroll_floor_annual * _real_org_type_scalar * _fraction_b * _loading_b * 1.0, 2)
check(
    "multi-state Step 1 + Step 3: breadth=3 (all criteria nonzero across the pair), "
    "multi_channel_severity_loading == 1.10 (K=0.05, breadth 3)",
    result_multi_b["low"] == _expected_multi_b,
    f"expected {_expected_multi_b} (combined_raw_total={_combined_b}, loading={_loading_b}), got {result_multi_b['low']}",
)

_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_a
_ft.STATE_MULTIPLIERS["the_exposed"] = _original_b


# -- 11. Extrapolation beyond R_max=6 -------------------------------------------
# Three synthetic states, all maxed at 2/2/2, stacked -- combined_raw_total
# must exceed 6 and the resulting fraction must exceed 0.25 rather than
# clamp, per the frozen-range design (prompts/friction-tax-multistate-
# compounding-methodology.md).

_original_c = STATE_MULTIPLIERS.get("the_dormant_talent")
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _synthetic_entry(turnover=2, productivity=2, decision_quality=2)
_ft.STATE_MULTIPLIERS["the_exposed"] = _synthetic_entry(turnover=2, productivity=2, decision_quality=2)
_ft.STATE_MULTIPLIERS["the_dormant_talent"] = _synthetic_entry(turnover=2, productivity=2, decision_quality=2)

result_extrap = compute_friction_tax(
    state_ids=["decision_paralysis", "the_exposed", "the_dormant_talent"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
# each criterion: scores [2,2,2] -> 2*1.0 + 2*0.5 + 2*0.25 = 2 + 1 + 0.5 = 3.5
_combined_extrap = 3.5 * 3  # = 10.5, exceeds R_max=6
_fraction_extrap = _ft._attritional_fraction(_combined_extrap)
_loading_extrap = 1.0 + 0.05 * (3 - 1)  # breadth=3
_expected_extrap = round(_real_grid_entry.payroll_floor_annual * _real_org_type_scalar * _fraction_extrap * _loading_extrap * 1.0, 2)
check(
    "combined_raw_total exceeds R_max=6 when 3 high-scoring states stack (extrapolation case)",
    _combined_extrap > 6,
    f"combined_raw_total={_combined_extrap}, expected > 6",
)
check(
    "attritional_fraction extrapolates above 0.25 rather than clamping",
    _fraction_extrap > 0.25,
    f"got {_fraction_extrap}, expected > 0.25",
)
check(
    "low computed correctly using the extrapolated (unclamped) fraction",
    result_extrap["low"] == _expected_extrap,
    f"expected {_expected_extrap}, got {result_extrap['low']}",
)

_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_a
_ft.STATE_MULTIPLIERS["the_exposed"] = _original_b
_ft.STATE_MULTIPLIERS["the_dormant_talent"] = _original_c


# -- 12. calibration_complete False when the grid cell is forced to None -------
# Grid is real everywhere by default now -- force this one cell's
# payroll_floor_annual to None to construct the "grid missing" scenario.

_original_grid_entry = _ft.PAYROLL_BASELINE_GRID[_GRID_KEY]
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _synthetic_entry(turnover=1, productivity=0, decision_quality=0)
_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = PayrollBaselineEntry(
    payroll_floor_annual=None, source="test", citation_id="test"
)
result_partial_1 = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
check(
    "calibration_complete False when grid cell is forced to None (org_type and state_multiplier real/mocked)",
    result_partial_1["calibration_complete"] is False,
    f"got {result_partial_1['calibration_complete']}",
)
_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = _original_grid_entry


# -- 13. calibration_complete False when the org_type scalar is forced to None -

_original_founder_led_entry = _ft.ORG_TYPE_SCALARS["Founder-led"]
_ft.ORG_TYPE_SCALARS["Founder-led"] = OrgTypeScalarEntry(
    scalar=None, source="test", citation_id=None
)
result_partial_2 = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "calibration_complete False when org_type scalar is forced to None (grid and state_multiplier real/mocked)",
    result_partial_2["calibration_complete"] is False,
    f"got {result_partial_2['calibration_complete']}",
)
_ft.ORG_TYPE_SCALARS["Founder-led"] = _original_founder_led_entry
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_multiplier


# -- 14. PAYROLL_BASELINE_GRID: all 54 cells independently recomputed ----------

_all_correct = True
_mismatches = []
for (hc, ind), entry in PAYROLL_BASELINE_GRID.items():
    wage = _ft._INDUSTRY_WAGE_DATA[ind][0]
    midpoint = HEADCOUNT_MIDPOINTS[hc].employees_per_firm
    expected = round(wage * midpoint, 2)
    if entry.payroll_floor_annual != expected:
        _all_correct = False
        _mismatches.append((hc, ind, entry.payroll_floor_annual, expected))

check(
    "PAYROLL_BASELINE_GRID has exactly 54 cells (6 headcount x 9 industry)",
    len(PAYROLL_BASELINE_GRID) == 54,
    f"got {len(PAYROLL_BASELINE_GRID)}",
)
expected_keys = {(hc, ind) for hc in HEADCOUNT_BUCKETS for ind in INDUSTRIES}
check(
    "PAYROLL_BASELINE_GRID keys exactly match all (headcount, industry) combinations",
    set(PAYROLL_BASELINE_GRID.keys()) == expected_keys,
    f"missing: {expected_keys - set(PAYROLL_BASELINE_GRID.keys())}, "
    f"extra: {set(PAYROLL_BASELINE_GRID.keys()) - expected_keys}",
)
check(
    "All 54 payroll_floor_annual values are non-None and match industry_wage x headcount_midpoint",
    _all_correct,
    f"mismatches: {_mismatches}",
)


# -- 15. All 9 industries now carry a source/citation_id ------------------------

_by_industry_sourced = {
    ind: all(
        PAYROLL_BASELINE_GRID[(hc, ind)].source is not None
        and PAYROLL_BASELINE_GRID[(hc, ind)].citation_id is not None
        for hc in HEADCOUNT_BUCKETS
    )
    for ind in INDUSTRIES
}
check(
    "All 9 industries carry a source/citation_id across all 6 headcount buckets",
    all(_by_industry_sourced.values()),
    f"unsourced industries: {[k for k, v in _by_industry_sourced.items() if not v]}",
)


# -- 16. ORG_TYPE_SCALARS completeness and correctness --------------------------

_EXPECTED_ORG_TYPE_SCALARS = {
    "Founder-led": 1.00,
    "PE or VC-backed": 1.00,
    "Privately held professional leadership": 1.00,
    "Nonprofit": 1.00,
    "Publicly traded": 1.00,
    "Government": 1.05,
}
check(
    "ORG_TYPE_SCALARS has exactly 6 entries matching IntakeData.org_type",
    set(ORG_TYPE_SCALARS.keys()) == set(_EXPECTED_ORG_TYPE_SCALARS.keys()),
    f"got {set(ORG_TYPE_SCALARS.keys())}",
)
check(
    "ORG_TYPE_SCALARS keys exactly match the live INTAKE_FIELDS['org_type'] list",
    set(ORG_TYPE_SCALARS.keys()) == set(INTAKE_FIELDS["org_type"]),
    f"MOB/intake mismatch: {set(ORG_TYPE_SCALARS.keys()) ^ set(INTAKE_FIELDS['org_type'])}",
)
for org_type, expected_scalar in _EXPECTED_ORG_TYPE_SCALARS.items():
    entry = ORG_TYPE_SCALARS.get(org_type)
    check(
        f"ORG_TYPE_SCALARS[{org_type!r}].scalar == {expected_scalar}",
        entry is not None and entry.scalar == expected_scalar,
        f"got {entry.scalar if entry else None}",
    )
check(
    "All ORG_TYPE_SCALARS entries carry a non-empty source note",
    all(e.source is not None and len(e.source) > 0 for e in ORG_TYPE_SCALARS.values()),
    "found an entry with no source note",
)


# -- 17. STATE_MULTIPLIERS keys match state registry ----------------------------

registry_ids = set(STATE_PROFILES.keys())
multiplier_ids = set(STATE_MULTIPLIERS.keys())
missing_from_multipliers = registry_ids - multiplier_ids
extra_in_multipliers = multiplier_ids - registry_ids

check(
    "STATE_MULTIPLIERS covers all registry state IDs",
    len(missing_from_multipliers) == 0,
    f"missing: {missing_from_multipliers}",
)
check(
    "STATE_MULTIPLIERS has no extra IDs not in registry",
    len(extra_in_multipliers) == 0,
    f"extra: {extra_in_multipliers}",
)


# -- 18. All 57 multipliers are populated in [0.05, 0.25] (Option A rescale) ---

non_populated = {k: v for k, v in STATE_MULTIPLIERS.items() if v is None}
check(
    "All STATE_MULTIPLIERS are populated (no CALIBRATION TARGET placeholders remain)",
    len(non_populated) == 0,
    f"still-None entries: {non_populated}",
)
check(
    "STATE_MULTIPLIERS has exactly 57 entries",
    len(STATE_MULTIPLIERS) == 57,
    f"got {len(STATE_MULTIPLIERS)}",
)
check(
    "Every STATE_MULTIPLIERS value is a StateMultiplierEntry with a real multiplier in [0.05, 0.25] (Option A)",
    all(
        isinstance(v, StateMultiplierEntry) and v.multiplier is not None and 0.05 <= v.multiplier <= 0.25
        for v in STATE_MULTIPLIERS.values()
    ),
    "found a non-StateMultiplierEntry value or an out-of-range multiplier",
)


# -- 19. criteria dict still carries "legal", excluded from raw_score ----------
# Legal/Compliance is split out to its own design (prompts/friction-tax-
# legal-compliance-methodology.md) but its score must still be recorded
# per state, not deleted -- verified against several real states with a
# nonzero legal score, not assumed.

_legal_sample = ["hr_capture", "the_paper_tiger", "disparate_impact_architecture", "cultural_overtime"]
_legal_check_failures = []
for _sid in _legal_sample:
    _entry = STATE_MULTIPLIERS[_sid]
    if "legal" not in _entry.criteria:
        _legal_check_failures.append((_sid, "legal key missing"))
        continue
    if _entry.criteria["legal"].score <= 0:
        _legal_check_failures.append((_sid, f"expected nonzero legal score, got {_entry.criteria['legal'].score}"))
    _three_criterion_sum = (
        _entry.criteria["turnover"].score
        + _entry.criteria["productivity"].score
        + _entry.criteria["decision_quality"].score
    )
    if _entry.raw_score != _three_criterion_sum:
        _legal_check_failures.append(
            (_sid, f"raw_score {_entry.raw_score} != 3-criterion sum {_three_criterion_sum} "
                   f"(legal={_entry.criteria['legal'].score} correctly excluded)")
        )
check(
    "criteria dict retains a nonzero 'legal' score where expected, but raw_score sums only the 3 attritional criteria",
    len(_legal_check_failures) == 0,
    f"failures: {_legal_check_failures}",
)

check(
    "every STATE_MULTIPLIERS criteria dict has exactly the 4 keys (turnover, productivity, decision_quality, legal)",
    all(
        set(v.criteria.keys()) == {"turnover", "productivity", "decision_quality", "legal"}
        for v in STATE_MULTIPLIERS.values()
    ),
    "found a state with a criteria dict missing or adding a key",
)


# -- 20. calibration_complete True across the full real 6x9x6 space ------------
# Exhaustive, not spot-checked. All three calibration axes are now real
# and populated for every combination -- confirms calibration_complete
# genuinely returns True everywhere real data is used, not just in the
# single spot-checked case from test 2.

_any_unexpectedly_incomplete = []
for hc in HEADCOUNT_BUCKETS:
    for ind in INDUSTRIES:
        for ot in ORG_TYPE_SCALARS.keys():
            r = compute_friction_tax(
                state_ids=["decision_paralysis"],
                severity_tier="Entrenched",
                org_size=hc,
                industry=ind,
                org_type=ot,
            )
            if r["calibration_complete"] is not True:
                _any_unexpectedly_incomplete.append((hc, ind, ot))

check(
    "calibration_complete is True for all 324 real (headcount, industry, org_type) combinations",
    len(_any_unexpectedly_incomplete) == 0,
    f"unexpectedly incomplete: {_any_unexpectedly_incomplete}",
)


# -- 21. Mixed known/unknown state_ids -- calibration_complete stays False -----
# Covers a genuine edge case: a state_ids list mixing one real, populated
# state with one unrecognized state_id must still yield
# calibration_complete=False -- the unrecognized id resolves to None and
# the all(e is not None ...) check must catch it even when mixed with
# real values, not just when every id in the list is unrecognized.

result_mixed = compute_friction_tax(
    state_ids=["decision_paralysis", "not_a_real_state"],
    severity_tier="Entrenched",
    org_size="500-999",
    industry="Technology",
    org_type="Nonprofit",
)
check(
    "calibration_complete False when state_ids mixes one real state with one unrecognized state",
    result_mixed["calibration_complete"] is False,
    f"got {result_mixed['calibration_complete']}",
)
check(
    "low/high are None when any state_id in the list is unrecognized",
    result_mixed["low"] is None and result_mixed["high"] is None,
    f"got low={result_mixed['low']}, high={result_mixed['high']}",
)


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


# -- Results ---------------------------------------------------------------------

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
