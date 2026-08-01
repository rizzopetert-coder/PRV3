"""
PRV3 Output Layer -- Friction Tax Unit Tests

Verifies:
  1. SEVERITY_SCALAR: correct values for all three tiers
  2. compute_friction_tax: calibration_complete=False when grid + org_type scalar are CALIBRATION TARGET
  3. compute_friction_tax: calibration_complete=False for empty state list
  4. compute_friction_tax: correct structure when calibrated (mocked values)
  5. compute_friction_tax: high = low * 1.4
  6. compute_friction_tax: correct severity scalar applied
  7. compute_friction_tax: multi-state averaging computes a real arithmetic mean
  8. compute_friction_tax: calibration_complete False when only the payroll grid cell is populated
  9. compute_friction_tax: calibration_complete False when only the org_type scalar is populated
  10. PAYROLL_BASELINE_GRID: exactly 54 cells (6 headcount x 9 industry), all combinations present
  11. ORG_TYPE_SCALARS: exactly 6 entries matching IntakeData.org_type
  12. STATE_MULTIPLIERS: all state IDs match engine state registry
  13. STATE_MULTIPLIERS: all values are None (CALIBRATION TARGET) at this stage
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
    HEADCOUNT_BUCKETS,
    INDUSTRIES,
    compute_friction_tax,
)
from engine.data.states import STATE_PROFILES
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


# -- 2. calibration_complete False when CALIBRATION TARGET inputs --------------

result = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "calibration_complete False when payroll grid + org_type scalar are None",
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
    org_type="Founder-led",
)
check(
    "calibration_complete False for empty state_ids",
    result_empty["calibration_complete"] is False,
    f"got {result_empty['calibration_complete']}",
)


# -- 4-6. Correct computation when fully calibrated (mocked via monkey-patch) --

_GRID_KEY = ("100-249", "Professional Services")
_original_entry = _ft.PAYROLL_BASELINE_GRID[_GRID_KEY]
_original_org_type_scalar = _ft.ORG_TYPE_SCALARS.get("Founder-led")
_original_multiplier = STATE_MULTIPLIERS.get("decision_paralysis")

# Temporarily set calibration values for testing. PayrollBaselineEntry is
# frozen -- whole-entry replacement, not field mutation, matching how a
# real calibration pass would populate this table.
_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = PayrollBaselineEntry(
    payroll_floor_annual=1_000_000.0, source="test", citation_id="test"
)
_ft.ORG_TYPE_SCALARS["Founder-led"] = 1.0
_ft.STATE_MULTIPLIERS["decision_paralysis"] = 0.1

result_cal = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)

check(
    "calibration_complete True when values set",
    result_cal["calibration_complete"] is True,
    f"got {result_cal['calibration_complete']}",
)
check(
    "low computed correctly (payroll_floor * org_type_scalar * multiplier * severity_scalar)",
    result_cal["low"] == round(1_000_000.0 * 1.0 * 0.1 * 1.0, 2),
    f"expected {round(1_000_000.0 * 1.0 * 0.1 * 1.0, 2)}, got {result_cal['low']}",
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
    org_type="Founder-led",
)
expected_endemic_low = round(1_000_000.0 * 1.0 * 0.1 * 1.4, 2)
check(
    "Endemic severity scalar 1.4 applied to low",
    result_endemic["low"] == expected_endemic_low,
    f"expected {expected_endemic_low}, got {result_endemic['low']}",
)


# -- 7. Multi-state averaging computes a real arithmetic mean -------------------
# Flagged in prompts/friction-tax-architecture-decision.md as a genuine gap:
# all prior test calls used single-element state_ids lists, so the
# averaging logic (verified by direct code read) had zero test coverage
# for the multi-state case.

_original_multiplier_2 = STATE_MULTIPLIERS.get("the_exposed")
_ft.STATE_MULTIPLIERS["the_exposed"] = 0.3
# decision_paralysis is still 0.1, set above

result_multi = compute_friction_tax(
    state_ids=["decision_paralysis", "the_exposed"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
expected_mean = (0.1 + 0.3) / 2
expected_multi_low = round(1_000_000.0 * 1.0 * expected_mean * 1.0, 2)
check(
    "multi-state averaging: mean_multiplier is the real arithmetic mean of both states",
    result_multi["low"] == expected_multi_low,
    f"expected {expected_multi_low} (mean={expected_mean}), got {result_multi['low']}",
)

# Restore
_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = _original_entry
_ft.ORG_TYPE_SCALARS["Founder-led"] = _original_org_type_scalar
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_multiplier
_ft.STATE_MULTIPLIERS["the_exposed"] = _original_multiplier_2


# -- 8. calibration_complete False when only the payroll grid cell is set ------

_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = PayrollBaselineEntry(
    payroll_floor_annual=1_000_000.0, source="test", citation_id="test"
)
# ORG_TYPE_SCALARS["Founder-led"] left at its real (None) value
result_partial_1 = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "calibration_complete False when grid is set but org_type scalar is still None",
    result_partial_1["calibration_complete"] is False,
    f"got {result_partial_1['calibration_complete']}",
)
_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = _original_entry


# -- 9. calibration_complete False when only the org_type scalar is set --------

_ft.ORG_TYPE_SCALARS["Founder-led"] = 1.0
# PAYROLL_BASELINE_GRID left at its real (None payroll_floor_annual) value
result_partial_2 = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "calibration_complete False when org_type scalar is set but grid cell is still None",
    result_partial_2["calibration_complete"] is False,
    f"got {result_partial_2['calibration_complete']}",
)
_ft.ORG_TYPE_SCALARS["Founder-led"] = _original_org_type_scalar


# -- 10. PAYROLL_BASELINE_GRID completeness -------------------------------------

expected_keys = {(hc, ind) for hc in HEADCOUNT_BUCKETS for ind in INDUSTRIES}
check(
    "PAYROLL_BASELINE_GRID has exactly 54 cells (6 headcount x 9 industry)",
    len(PAYROLL_BASELINE_GRID) == 54,
    f"got {len(PAYROLL_BASELINE_GRID)}",
)
check(
    "PAYROLL_BASELINE_GRID keys exactly match all (headcount, industry) combinations",
    set(PAYROLL_BASELINE_GRID.keys()) == expected_keys,
    f"missing: {expected_keys - set(PAYROLL_BASELINE_GRID.keys())}, "
    f"extra: {set(PAYROLL_BASELINE_GRID.keys()) - expected_keys}",
)
check(
    "All PAYROLL_BASELINE_GRID payroll_floor_annual values are None (CALIBRATION TARGET)",
    all(entry.payroll_floor_annual is None for entry in PAYROLL_BASELINE_GRID.values()),
    "found a non-None payroll_floor_annual before calibration",
)


# -- 11. ORG_TYPE_SCALARS completeness ------------------------------------------

_EXPECTED_ORG_TYPES = {
    "Founder-led", "PE or VC-backed", "Privately held professional leadership",
    "Nonprofit", "Publicly traded", "Government",
}
check(
    "ORG_TYPE_SCALARS has exactly 6 entries matching IntakeData.org_type",
    set(ORG_TYPE_SCALARS.keys()) == _EXPECTED_ORG_TYPES,
    f"got {set(ORG_TYPE_SCALARS.keys())}",
)
check(
    "All ORG_TYPE_SCALARS values are None (CALIBRATION TARGET)",
    all(v is None for v in ORG_TYPE_SCALARS.values()),
    f"non-None values: {{k: v for k, v in ORG_TYPE_SCALARS.items() if v is not None}}",
)


# -- 12. STATE_MULTIPLIERS keys match state registry ----------------------------

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


# -- 13. All multipliers are None (CALIBRATION TARGET) --------------------------

non_none = {k: v for k, v in STATE_MULTIPLIERS.items() if v is not None}
check(
    "All STATE_MULTIPLIERS are None (CALIBRATION TARGET)",
    len(non_none) == 0,
    f"non-None values: {non_none}",
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
