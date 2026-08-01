"""
PRV3 Output Layer -- Friction Tax Unit Tests

Verifies:
  1. SEVERITY_SCALAR: correct values for all three tiers
  2. compute_friction_tax: calibration_complete=False on a real, unmocked
     call (grid cell still a CALIBRATION TARGET; org_type scalar is now
     real/populated)
  3. compute_friction_tax: calibration_complete=False for empty state list
  4. compute_friction_tax: correct structure when calibrated (mocked
     grid + state multiplier; org_type scalar is REAL, "Government" at
     1.05, not monkey-patched -- proves the scalar is actually applied,
     not just defaulted to a no-op 1.0)
  5. compute_friction_tax: high = low * 1.4
  6. compute_friction_tax: correct severity scalar applied
  7. compute_friction_tax: multi-state averaging computes a real
     arithmetic mean
  8. compute_friction_tax: calibration_complete False when only the
     payroll grid cell is populated (org_type scalar forced back to None
     for this one test)
  9. compute_friction_tax: calibration_complete False when the org_type
     scalar is real/populated but the grid cell is still None (no
     monkey-patching needed -- this is real current behavior)
  10. PAYROLL_BASELINE_GRID: exactly 54 cells (6 headcount x 9 industry),
      all combinations present; payroll_floor_annual None everywhere;
      exactly 36 cells (6 sourced industries x 6 buckets) carry a source/
      citation_id, the other 18 remain fully unsourced
  11. ORG_TYPE_SCALARS: exactly 6 entries matching IntakeData.org_type,
      each with the correct finalized scalar value and a non-empty
      source note
  12. STATE_MULTIPLIERS: all state IDs match engine state registry
  13. STATE_MULTIPLIERS: all values are None (CALIBRATION TARGET) at this stage
  14. compute_friction_tax: calibration_complete is False across the
      full real 6x9x6 (headcount x industry x org_type) combination
      space -- exhaustive, not spot-checked
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
    org_type="Founder-led",
)
check(
    "calibration_complete False on a real call (grid cell still a CALIBRATION TARGET)",
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


# -- 4-6. Correct computation when fully calibrated (mocked grid + state) ------
# org_type="Government" uses its REAL finalized scalar (1.05), not a
# monkey-patched value -- proves the scalar is genuinely multiplied in,
# not just defaulted to a no-op 1.0 that would pass either way.

_GRID_KEY = ("100-249", "Professional Services")
_original_entry = _ft.PAYROLL_BASELINE_GRID[_GRID_KEY]
_original_multiplier = STATE_MULTIPLIERS.get("decision_paralysis")

_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = PayrollBaselineEntry(
    payroll_floor_annual=1_000_000.0, source="test", citation_id="test"
)
_ft.STATE_MULTIPLIERS["decision_paralysis"] = 0.1

result_cal = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)

check(
    "calibration_complete True when values set",
    result_cal["calibration_complete"] is True,
    f"got {result_cal['calibration_complete']}",
)
check(
    "low computed correctly (payroll_floor * real Government scalar 1.05 * multiplier * severity_scalar)",
    result_cal["low"] == round(1_000_000.0 * 1.05 * 0.1 * 1.0, 2),
    f"expected {round(1_000_000.0 * 1.05 * 0.1 * 1.0, 2)}, got {result_cal['low']}",
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
expected_endemic_low = round(1_000_000.0 * 1.05 * 0.1 * 1.4, 2)
check(
    "Endemic severity scalar 1.4 applied to low",
    result_endemic["low"] == expected_endemic_low,
    f"expected {expected_endemic_low}, got {result_endemic['low']}",
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
    org_type="Founder-led",  # real scalar 1.00, keeps this test focused on averaging
)
expected_mean = (0.1 + 0.3) / 2
expected_multi_low = round(1_000_000.0 * 1.00 * expected_mean * 1.0, 2)
check(
    "multi-state averaging: mean_multiplier is the real arithmetic mean of both states",
    result_multi["low"] == expected_multi_low,
    f"expected {expected_multi_low} (mean={expected_mean}), got {result_multi['low']}",
)

# Restore
_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = _original_entry
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_multiplier
_ft.STATE_MULTIPLIERS["the_exposed"] = _original_multiplier_2


# -- 8. calibration_complete False when only the payroll grid cell is set ------
# All 6 real ORG_TYPE_SCALARS are now populated, so there's no longer a
# real org_type left at None to use for this scenario -- Founder-led is
# temporarily forced back to None to construct it, then restored.

_original_founder_led_entry = _ft.ORG_TYPE_SCALARS["Founder-led"]
_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = PayrollBaselineEntry(
    payroll_floor_annual=1_000_000.0, source="test", citation_id="test"
)
_ft.ORG_TYPE_SCALARS["Founder-led"] = OrgTypeScalarEntry(
    scalar=None, source="test", citation_id=None
)
result_partial_1 = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Founder-led",
)
check(
    "calibration_complete False when grid is set but org_type scalar is forced back to None",
    result_partial_1["calibration_complete"] is False,
    f"got {result_partial_1['calibration_complete']}",
)
_ft.PAYROLL_BASELINE_GRID[_GRID_KEY] = _original_entry
_ft.ORG_TYPE_SCALARS["Founder-led"] = _original_founder_led_entry


# -- 9. calibration_complete False when org_type is real but grid is still None -
# No monkey-patching needed -- this is real, current, unmodified behavior.

result_partial_2 = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="100-249",
    industry="Professional Services",
    org_type="Government",
)
check(
    "calibration_complete False when org_type scalar is real (Government, populated) but grid cell is still None",
    result_partial_2["calibration_complete"] is False,
    f"got {result_partial_2['calibration_complete']}",
)


# -- 10. PAYROLL_BASELINE_GRID completeness and sourcing ------------------------

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
    "All PAYROLL_BASELINE_GRID payroll_floor_annual values are still None (CALIBRATION TARGET)",
    all(entry.payroll_floor_annual is None for entry in PAYROLL_BASELINE_GRID.values()),
    "found a non-None payroll_floor_annual before headcount midpoints resolve",
)

_SOURCED_INDUSTRIES = {
    "Professional Services", "Healthcare & Life Sciences", "Financial Services",
    "Technology", "Government & Public Sector", "Other",
}
_UNSOURCED_INDUSTRIES = set(INDUSTRIES) - _SOURCED_INDUSTRIES
sourced_cells = [
    entry for (hc, ind), entry in PAYROLL_BASELINE_GRID.items()
    if ind in _SOURCED_INDUSTRIES
]
unsourced_cells = [
    entry for (hc, ind), entry in PAYROLL_BASELINE_GRID.items()
    if ind in _UNSOURCED_INDUSTRIES
]
check(
    "36 cells (6 sourced industries x 6 headcount buckets) carry a source note",
    len(sourced_cells) == 36 and all(e.source is not None and e.citation_id is not None for e in sourced_cells),
    f"got {len(sourced_cells)} cells, "
    f"{sum(1 for e in sourced_cells if e.source is None)} missing source",
)
check(
    "18 cells (3 unsourced industries x 6 headcount buckets) remain fully unsourced",
    len(unsourced_cells) == 18 and all(e.source is None and e.citation_id is None for e in unsourced_cells),
    f"got {len(unsourced_cells)} cells, "
    f"{sum(1 for e in unsourced_cells if e.source is not None)} unexpectedly sourced",
)


# -- 11. ORG_TYPE_SCALARS completeness and correctness --------------------------

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


# -- 14. calibration_complete False across the full real 6x9x6 space -----------
# Exhaustive, not spot-checked -- confirms no (headcount, industry,
# org_type) combination accidentally clears the gate given today's real,
# unmodified data (a real state_id is used so the state_ids/state-
# multiplier half of the gate is also genuinely exercised, not just
# trivially satisfied by an empty list).

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


# -- Results ---------------------------------------------------------------------

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
