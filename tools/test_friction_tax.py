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


# -- Results ---------------------------------------------------------------------

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
