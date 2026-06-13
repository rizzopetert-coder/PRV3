"""
PRV3 Output Layer — Friction Tax Unit Tests

Verifies:
  1. SEVERITY_SCALAR: correct values for all three tiers
  2. compute_friction_tax: returns calibration_complete=False when CALIBRATION TARGET inputs
  3. compute_friction_tax: returns calibration_complete=False for empty state list
  4. compute_friction_tax: correct structure when calibrated (mocked values)
  5. compute_friction_tax: high = low * 1.4
  6. compute_friction_tax: correct severity scalar applied
  7. _resolve_band: returns fallback for unknown headcount string
  8. _resolve_band: returns correct label for known band
  9. STATE_MULTIPLIERS: all 47 state IDs match engine state registry
  10. STATE_MULTIPLIERS: all values are None (CALIBRATION TARGET) at this stage
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.friction_tax import (
    SEVERITY_SCALAR,
    STATE_MULTIPLIERS,
    _ORG_SIZE_BANDS,
    _resolve_band,
    compute_friction_tax,
)
from engine.data.states import STATE_PROFILES

PASS = []
FAIL = []


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Friction Tax — Unit Tests")
print("=" * 64)


# ── 1. SEVERITY_SCALAR values ──────────────────────────────────────────────────

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


# ── 2. calibration_complete False when CALIBRATION TARGET inputs ───────────────

result = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="101_to_500",
)
check(
    "calibration_complete False when band_low is None",
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


# ── 3. calibration_complete False for empty state list ────────────────────────

result_empty = compute_friction_tax(
    state_ids=[],
    severity_tier="Entrenched",
    org_size="101_to_500",
)
check(
    "calibration_complete False for empty state_ids",
    result_empty["calibration_complete"] is False,
    f"got {result_empty['calibration_complete']}",
)


# ── 4-6. Correct computation when fully calibrated (mocked via monkey-patch) ──

import engine.friction_tax as _ft

_original_band = _ORG_SIZE_BANDS.get("101_to_500", {}).get("band_low")
_original_multiplier = STATE_MULTIPLIERS.get("decision_paralysis")

# Temporarily set calibration values for testing
_ft._ORG_SIZE_BANDS["101_to_500"]["band_low"] = 1_000_000.0
_ft.STATE_MULTIPLIERS["decision_paralysis"] = 0.1

result_cal = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Entrenched",
    org_size="101_to_500",
)

# Restore
_ft._ORG_SIZE_BANDS["101_to_500"]["band_low"] = _original_band
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_multiplier

check(
    "calibration_complete True when values set",
    result_cal["calibration_complete"] is True,
    f"got {result_cal['calibration_complete']}",
)
check(
    "low computed correctly (band_low * multiplier * severity_scalar)",
    result_cal["low"] == round(1_000_000.0 * 0.1 * 1.0, 2),
    f"expected {round(1_000_000.0 * 0.1 * 1.0, 2)}, got {result_cal['low']}",
)
check(
    "high == low * 1.4",
    result_cal["high"] == round(result_cal["low"] * 1.4, 2),
    f"expected {round(result_cal['low'] * 1.4, 2)}, got {result_cal['high']}",
)

# Severity scalar applied correctly — Endemic should produce 1.4x
_ft._ORG_SIZE_BANDS["101_to_500"]["band_low"] = 1_000_000.0
_ft.STATE_MULTIPLIERS["decision_paralysis"] = 0.1

result_endemic = compute_friction_tax(
    state_ids=["decision_paralysis"],
    severity_tier="Endemic",
    org_size="101_to_500",
)
expected_endemic_low = round(1_000_000.0 * 0.1 * 1.4, 2)
check(
    "Endemic severity scalar 1.4 applied to low",
    result_endemic["low"] == expected_endemic_low,
    f"expected {expected_endemic_low}, got {result_endemic['low']}",
)

_ft._ORG_SIZE_BANDS["101_to_500"]["band_low"] = _original_band
_ft.STATE_MULTIPLIERS["decision_paralysis"] = _original_multiplier


# ── 7. _resolve_band fallback ─────────────────────────────────────────────────

fallback = _resolve_band("not_a_real_band")
check(
    "_resolve_band returns fallback label for unknown band",
    fallback["label"] == "Unknown",
    f"got label={fallback['label']}",
)

# ── 8. _resolve_band known band ───────────────────────────────────────────────

known = _resolve_band("101_to_500")
check(
    "_resolve_band returns correct label for known band",
    "101" in known["label"] or "Mid" in known["label"],
    f"got label={known['label']}",
)


# ── 9. STATE_MULTIPLIERS keys match state registry ────────────────────────────

registry_ids = set(STATE_PROFILES.keys())
multiplier_ids = set(STATE_MULTIPLIERS.keys())
missing_from_multipliers = registry_ids - multiplier_ids
extra_in_multipliers = multiplier_ids - registry_ids

check(
    "STATE_MULTIPLIERS covers all 47 registry state IDs",
    len(missing_from_multipliers) == 0,
    f"missing: {missing_from_multipliers}",
)
check(
    "STATE_MULTIPLIERS has no extra IDs not in registry",
    len(extra_in_multipliers) == 0,
    f"extra: {extra_in_multipliers}",
)


# ── 10. All multipliers are None (CALIBRATION TARGET) ────────────────────────

non_none = {k: v for k, v in STATE_MULTIPLIERS.items() if v is not None}
check(
    "All STATE_MULTIPLIERS are None (CALIBRATION TARGET)",
    len(non_none) == 0,
    f"non-None values: {non_none}",
)


# ── Results ───────────────────────────────────────────────────────────────────

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
