"""
PRV3 Output Layer -- Friction Tax Unit Tests

Verifies:
  1. SEVERITY_SCALAR: correct values for all three tiers
  2. compute_friction_tax: calibration_complete=False on a real, unmocked
     call -- STATE_MULTIPLIERS is now the sole CALIBRATION TARGET gate,
     grid + org_type are both real/populated for every valid combination
  3. compute_friction_tax: calibration_complete=False for empty state list
  4. compute_friction_tax: correct structure when calibrated (grid +
     org_type are REAL, unmocked -- only STATE_MULTIPLIERS is monkey-
     patched. Expected value is computed from the real, live
     PAYROLL_BASELINE_GRID entry, not a hardcoded duplicate number)
  5. compute_friction_tax: high = low * 1.4
  6. compute_friction_tax: correct severity scalar applied
  7. compute_friction_tax: multi-state averaging computes a real
     arithmetic mean (grid + org_type real, only two state multipliers
     monkey-patched)
  8. compute_friction_tax: calibration_complete False when the grid cell
     is forced back to None (org_type real, state_multiplier mocked)
  9. compute_friction_tax: calibration_complete False when the org_type
     scalar is forced back to None (grid real, state_multiplier mocked)
  10. PAYROLL_BASELINE_GRID: exactly 54 cells, all combinations present,
      every cell's payroll_floor_annual independently recomputed and
      verified against industry_wage x headcount_midpoint
  11. PAYROLL_BASELINE_GRID: all 9 industries (not just 6) carry a
      source/citation_id
  12. ORG_TYPE_SCALARS: exactly 6 entries matching IntakeData.org_type,
      each with the correct finalized scalar value and a non-empty
      source note
  13. STATE_MULTIPLIERS: all state IDs match engine state registry
  14. STATE_MULTIPLIERS: all values are None (CALIBRATION TARGET) at this stage
  15. compute_friction_tax: calibration_complete is False across the
      full real 6x9x6 (headcount x industry x org_type) combination
      space with real, unmodified data -- exhaustive, not spot-checked
  16. compute_friction_tax: POSITIVE confirmation -- temporarily
      populating one real STATE_MULTIPLIERS entry (grid + org_type
      already real, nothing else mocked) makes calibration_complete
      genuinely flip True, proving the gate can fire and isn't
      coincidentally or incorrectly always False
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.friction_tax import (
    SEVERITY_SCALAR,
    STATE_MULTIPLIERS,
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


# -- 2. calibration_complete False on a real, unmocked call --------------------

result = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
check(
    "calibration_complete False on a real call (STATE_MULTIPLIERS is the sole remaining gate)",
    result["calibration_complete"] is False,
    f"got calibration_complete={result['calibration_complete']}",
)
check(
    "low is None when calibration incomplete",
    result["low"] is None,
    f"got low={result['low']}",
)
check(
    "high is None when calibration incomplete",
    result["high"] is None,
    f"got high={result['high']}",
)
check(
    "currency is USD regardless of calibration",
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


# -- 4-6. Correct computation when fully calibrated -----------------------------
# Grid and org_type are REAL and unmocked -- only STATE_MULTIPLIERS is
# monkey-patched. Expected values are derived from the live, real
# PAYROLL_BASELINE_GRID entry, not a hardcoded duplicate number, so this
# test can't silently drift from the real data.

_GRID_KEY = ("100-249", "Professional Services")
_real_grid_entry = PAYROLL_BASELINE_GRID[_GRID_KEY]
_real_org_type_scalar = ORG_TYPE_SCALARS["Government"].scalar

check(
    "sanity: real grid cell used for tests 4-9 is genuinely populated",
    _real_grid_entry.payroll_floor_annual is not None,
    "expected PAYROLL_BASELINE_GRID to be fully populated after this task",
)

_original_multiplier = STATE_MULTIPLIERS.get("decision_paralysis")
_ft.STATE_MULTIPLIERS["decision_paralysis"] = 0.1

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
_expected_low = round(_real_grid_entry.payroll_floor_annual * _real_org_type_scalar * 0.1 * 1.0, 2)
check(
    "low computed correctly (real payroll_floor_annual * real Government scalar * multiplier * severity_scalar)",
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
_expected_endemic_low = round(_real_grid_entry.payroll_floor_annual * _real_org_type_scalar * 0.1 * 1.4, 2)
check(
    "Endemic severity scalar 1.4 applied to low",
    result_endemic["low"] == _expected_endemic_low,
    f"expected {_expected_endemic_low}, got {result_endemic['low']}",
)


# -- 7. Multi-state averaging computes a real arithmetic mean -------------------

_original_multiplier_2 = STATE_MULTIPLIERS.get("the_exposed")
_ft.STATE_MULTIPLIERS["the_exposed"] = 0.3
# decision_paralysis is still 0.1, set above

result_multi = compute_friction_tax(
    state_ids=["decision_paralysis", "the_exposed"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
_expected_mean = (0.1 + 0.3) / 2
_expected_multi_low = round(_real_grid_entry.payroll_floor_annual * _real_org_type_scalar * _expected_mean * 1.0, 2)
check(
    "multi-state averaging: mean_multiplier is the real arithmetic mean of both states",
    result_multi["low"] == _expected_multi_low,
    f"expected {_expected_multi_low} (mean={_expected_mean}), got {result_multi['low']}",
)

_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_multiplier
_ft.STATE_MULTIPLIERS["the_exposed"] = _original_multiplier_2


# -- 8. calibration_complete False when the grid cell is forced to None --------
# Grid is real everywhere by default now -- force this one cell's
# payroll_floor_annual to None to construct the "grid missing" scenario.

_original_grid_entry = _ft.PAYROLL_BASELINE_GRID[_GRID_KEY]
_ft.STATE_MULTIPLIERS["decision_paralysis"] = 0.1
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


# -- 9. calibration_complete False when the org_type scalar is forced to None --

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


# -- 10. PAYROLL_BASELINE_GRID: all 54 cells independently recomputed ----------

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


# -- 11. All 9 industries now carry a source/citation_id ------------------------

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


# -- 12. ORG_TYPE_SCALARS completeness and correctness --------------------------

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


# -- 13. STATE_MULTIPLIERS keys match state registry ----------------------------

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


# -- 14. All multipliers are None (CALIBRATION TARGET) --------------------------

non_none = {k: v for k, v in STATE_MULTIPLIERS.items() if v is not None}
check(
    "All STATE_MULTIPLIERS are None (CALIBRATION TARGET)",
    len(non_none) == 0,
    f"non-None values: {non_none}",
)


# -- 15. calibration_complete False across the full real 6x9x6 space -----------
# Exhaustive, not spot-checked. Grid and org_type are now real/populated
# for every combination -- this confirms STATE_MULTIPLIERS being fully
# None is still sufficient, alone, to keep calibration_complete False
# everywhere real data is used.

_any_unexpectedly_complete = []
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
            if r["calibration_complete"] is not False:
                _any_unexpectedly_complete.append((hc, ind, ot))

check(
    "calibration_complete is False for all 324 real (headcount, industry, org_type) combinations",
    len(_any_unexpectedly_complete) == 0,
    f"unexpectedly complete: {_any_unexpectedly_complete}",
)


# -- 16. POSITIVE confirmation: the gate genuinely can flip True ---------------
# Grid and org_type are real and untouched here -- only one real
# STATE_MULTIPLIERS entry is temporarily populated. If this doesn't flip
# calibration_complete to True, the gate itself is broken, not just
# "correctly incomplete."

_original_multiplier_positive = STATE_MULTIPLIERS.get("decision_paralysis")
_ft.STATE_MULTIPLIERS["decision_paralysis"] = 0.2
result_positive = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="500-999",
    industry="Technology",
    org_type="Nonprofit",
)
check(
    "calibration_complete genuinely flips True with real grid + org_type + one real state_multiplier",
    result_positive["calibration_complete"] is True,
    f"got {result_positive['calibration_complete']} -- gate may be broken, not just incomplete",
)
check(
    "positive-confirmation result produces a real, non-None low/high",
    result_positive["low"] is not None and result_positive["high"] is not None,
    f"got low={result_positive['low']}, high={result_positive['high']}",
)
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_multiplier_positive


# -- Results ---------------------------------------------------------------------

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
