"""
PRV3 -- Friction Tax code restructure (Part A of the friction-tax
restructure + pipeline-wiring-investigation task).

Rewrites engine/friction_tax.py and tools/test_friction_tax.py in full,
per the Gemini-approved, Pete-approved architecture in
prompts/friction-tax-architecture-decision.md (2026-07-29):

  - Retires the flat 5-key _ORG_SIZE_BANDS dict (legacy "1_to_25"-style
    keys that never matched IntakeData.headcount's real values) in favor
    of PAYROLL_BASELINE_GRID: dict[tuple[str, str], PayrollBaselineEntry],
    keyed by (headcount, industry) using IntakeData's real string values
    directly -- 54 cells (6 headcount buckets x 9 industries), confirmed
    against the live engine/data/intake.py INTAKE_FIELDS before writing.
  - Adds ORG_TYPE_SCALARS: dict[str, Optional[float]], 6 entries matching
    IntakeData.org_type -- a standalone multiplicative scalar, not a
    third grid axis.
  - compute_friction_tax() gains industry/org_type params; internal
    sequence: grid lookup -> org_type scalar -> existing unchanged
    multi-state averaging -> existing unchanged severity_scalar ->
    existing unchanged low/high math (high = low * 1.4).
  - STATE_MULTIPLIERS (57 states) untouched -- separate axis, not part
    of this restructure.
  - _resolve_band()/_FALLBACK_BAND retired (superseded by the grid's own
    .get() lookup, which returns None cleanly on an unrecognized key --
    no separate fallback dict needed once the keys are real, already-
    readable IntakeData strings).
  - test_friction_tax.py rewritten: monkey-patch mechanism changed from
    mutating _ORG_SIZE_BANDS dict values in place to replacing whole
    PAYROLL_BASELINE_GRID entries (dataclass is frozen, so field mutation
    isn't possible -- whole-entry replacement is the correct pattern and
    also better matches how a real calibration pass would populate this
    table). New coverage: multi-state averaging with two genuinely
    different multiplier values (the flagged test gap), calibration_
    complete's two-stage AND gate tested independently (grid alone vs.
    org_type scalar alone), and grid/org_type-scalar completeness checks
    analogous to the existing STATE_MULTIPLIERS coverage check.

Usage:
  python tools/patch_friction_tax_restructure.py --dry-run
  python tools/patch_friction_tax_restructure.py --write
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
FRICTION_TAX_PY = REPO_ROOT / "engine" / "friction_tax.py"
TEST_FRICTION_TAX_PY = REPO_ROOT / "tools" / "test_friction_tax.py"

NEW_FRICTION_TAX = '''"""
PRV3 Scoring Engine -- Output Layer
Friction Tax Computation

Computes an estimated financial consequence range for the identified
organizational state cluster. All calibration values are flagged
CALIBRATION TARGET until Pete populates from source research.

Output: {"low": float, "high": float, "currency": "USD"}
  high = low * 1.4  (range spread, LOCKED)

Severity scalars (LOCKED):
  EMERGING:    0.6
  ENTRENCHED:  1.0
  ENDEMIC:     1.4

Payroll baseline architecture (approved 2026-07-29, Gemini-proposed,
Pete-approved -- see prompts/friction-tax-architecture-decision.md):
  PAYROLL_BASELINE_GRID is keyed by (headcount, industry), 54 cells (6
  IntakeData.headcount buckets x 9 IntakeData.industry categories,
  confirmed against the live engine/data/intake.py INTAKE_FIELDS).
  ORG_TYPE_SCALARS applies as a standalone multiplicative scalar on top
  of the grid lookup, not a third grid axis (5 x 9 x 6 = 270 cells was
  rejected as not researchable -- see prompts/friction-tax-band-
  segmentation.md). This supersedes the older flat headcount-only
  _ORG_SIZE_BANDS structure and its legacy key format ("1_to_25" etc.,
  which never matched IntakeData.headcount's real values). See also
  prompts/friction-tax-unit-decision.md (payroll basis, not revenue).

Source research flagged:
  McKinsey & Company -- leadership dysfunction cost benchmarks
  SHRM -- HR failure / turnover cost studies
  Gallup -- engagement / productivity loss quantification
  Peer-reviewed literature -- organizational dysfunction financial impact

Spec reference: PRV3 Output Layer Brief -- Step 2
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# -- Severity scalars (LOCKED) --------------------------------------------------

SEVERITY_SCALAR: dict[str, float] = {
    "Emerging":    0.6,
    "Entrenched":  1.0,
    "Endemic":     1.4,
}

_DEFAULT_SEVERITY_SCALAR: float = 1.0


# -- Payroll baseline grid -------------------------------------------------------
# Keyed by (headcount, industry), using IntakeData's real string values
# directly (engine/data/intake.py's INTAKE_FIELDS) -- not a separate
# internal bucket format. 6 headcount buckets x 9 industries = 54 cells.
# CALIBRATION TARGET -- all payroll_floor_annual values require population
# from source research. Payroll basis, not revenue -- see
# prompts/friction-tax-unit-decision.md.

HEADCOUNT_BUCKETS: tuple[str, ...] = (
    "Under 25", "25-99", "100-249", "250-499", "500-999", "1000+",
)

INDUSTRIES: tuple[str, ...] = (
    "Professional Services",
    "Healthcare & Life Sciences",
    "Financial Services",
    "Technology",
    "Manufacturing & Industrial",
    "Retail & Hospitality",
    "Nonprofit & Education",
    "Government & Public Sector",
    "Other",
)


@dataclass(frozen=True)
class PayrollBaselineEntry:
    """One cell of the payroll baseline grid."""
    payroll_floor_annual: Optional[float]  # CALIBRATION TARGET
    source: Optional[str]                  # named benchmark/study, None until populated
    citation_id: Optional[str]             # cross-reference key into a future citations table


PAYROLL_BASELINE_GRID: dict[tuple[str, str], PayrollBaselineEntry] = {
    (headcount, industry): PayrollBaselineEntry(
        payroll_floor_annual=None,
        source=None,
        citation_id=None,
    )
    for headcount in HEADCOUNT_BUCKETS
    for industry in INDUSTRIES
}


# -- Org type scalar --------------------------------------------------------------
# Standalone multiplicative scalar applied to the grid lookup result, not a
# third grid axis. Keys match IntakeData.org_type / engine/data/intake.py's
# INTAKE_FIELDS["org_type"]. CALIBRATION TARGET -- all values require
# population from source research.

ORG_TYPE_SCALARS: dict[str, Optional[float]] = {
    "Founder-led":                            None,  # CALIBRATION TARGET
    "PE or VC-backed":                        None,  # CALIBRATION TARGET
    "Privately held professional leadership": None,  # CALIBRATION TARGET
    "Nonprofit":                               None,  # CALIBRATION TARGET
    "Publicly traded":                        None,  # CALIBRATION TARGET
    "Government":                              None,  # CALIBRATION TARGET
}


# -- State multiplier table -------------------------------------------------------
# Per-state friction multiplier applied to the adjusted payroll baseline
# (payroll basis, not revenue -- see prompts/friction-tax-unit-decision.md).
# All values CALIBRATION TARGET -- populated from source research.
# Keys: state_id strings matching engine/data/states.py registry (57 states).

STATE_MULTIPLIERS: dict[str, Optional[float]] = {
    "the_unformed_leader":              None,  # CALIBRATION TARGET
    "the_overloaded_manager":           None,  # CALIBRATION TARGET
    "the_dormant_talent":               None,  # CALIBRATION TARGET
    "built_to_fail":                    None,  # CALIBRATION TARGET
    "the_undefined_role":               None,  # CALIBRATION TARGET
    "the_paper_tiger":                  None,  # CALIBRATION TARGET
    "the_founders_grip":                None,  # CALIBRATION TARGET
    "the_exposed":                      None,  # CALIBRATION TARGET
    "the_uninitiated":                  None,  # CALIBRATION TARGET
    "leadership_continuity_risk":       None,  # CALIBRATION TARGET
    "hr_capture":                       None,  # CALIBRATION TARGET
    "decision_paralysis":               None,  # CALIBRATION TARGET
    "the_policy_lag":                   None,  # CALIBRATION TARGET
    "the_unexamined_algorithm":         None,  # CALIBRATION TARGET
    "heard_and_ignored":                None,  # CALIBRATION TARGET
    "the_tolerated_violation":          None,  # CALIBRATION TARGET
    "dueling_narratives":               None,  # CALIBRATION TARGET
    "the_unsolved_problem":             None,  # CALIBRATION TARGET
    "transition_paralysis":             None,  # CALIBRATION TARGET
    "paper_shield":                     None,  # CALIBRATION TARGET
    "the_lost_map":                     None,  # CALIBRATION TARGET
    "invisible_influence_architecture": None,  # CALIBRATION TARGET
    "pay_exposure":                     None,  # CALIBRATION TARGET
    "the_pay_fog":                      None,  # CALIBRATION TARGET
    "the_fracture":                     None,  # CALIBRATION TARGET
    "the_second_close":                 None,  # CALIBRATION TARGET
    "silosolation":                     None,  # CALIBRATION TARGET
    "the_suppression_filter":           None,  # CALIBRATION TARGET
    "the_arbitrary_standard":           None,  # CALIBRATION TARGET
    "decision_blindness":               None,  # CALIBRATION TARGET
    "the_untouchable":                  None,  # CALIBRATION TARGET
    "what_nobody_says":                 None,  # CALIBRATION TARGET
    "leadership_deafness":              None,  # CALIBRATION TARGET
    "the_diversity_ceiling":            None,  # CALIBRATION TARGET
    "culture_drift":                    None,  # CALIBRATION TARGET
    "identity_erosion":                 None,  # CALIBRATION TARGET
    "the_culture_that_wasnt":           None,  # CALIBRATION TARGET
    "the_burned_credibility":           None,  # CALIBRATION TARGET
    "invisible_burnout":                None,  # CALIBRATION TARGET
    "the_basement_standard":            None,  # CALIBRATION TARGET
    "the_inside_track":                 None,  # CALIBRATION TARGET
    "narrative_lock":                   None,  # CALIBRATION TARGET
    "groundhog_day":                    None,  # CALIBRATION TARGET
    "the_wrong_reward":                 None,  # CALIBRATION TARGET
    "the_unreported_hazard":            None,  # CALIBRATION TARGET
    "the_unlocked_door":                None,  # CALIBRATION TARGET
    "the_broken_compass":               None,  # CALIBRATION TARGET

    # -- Taxonomy expansion (Session 67) -----------------------------------------
    "invisible_performance_management":  None,  # CALIBRATION TARGET
    "compression_crisis":                None,  # CALIBRATION TARGET
    "sequential_decision_blindness":     None,  # CALIBRATION TARGET
    "disparate_impact_architecture":     None,  # CALIBRATION TARGET
    "planning_authority_gap":            None,  # CALIBRATION TARGET
    "distributed_culture_fragmentation": None,  # CALIBRATION TARGET
    "wellbeing_theater":                 None,  # CALIBRATION TARGET
    "human_displacement_anxiety":        None,  # CALIBRATION TARGET
    "motivational_architecture_failure": None,  # CALIBRATION TARGET
    "cultural_overtime":                 None,  # CALIBRATION TARGET
}

_DEFAULT_MULTIPLIER: float = 0.0


# -- Core computation ---------------------------------------------------------------

def compute_friction_tax(
    state_ids: list[str],
    severity_tier: str,
    org_size: str,
    industry: str,
    org_type: str,
) -> dict:
    """
    Compute a friction tax estimate for a state cluster.

    Parameters:
      state_ids:     list of identified state IDs (from identified_states)
      severity_tier: "Emerging" | "Entrenched" | "Endemic"
      org_size:      IntakeData.headcount value (e.g. "100-249")
      industry:      IntakeData.industry value
      org_type:      IntakeData.org_type value

    Returns:
      {
        "low": float | None,
        "high": float | None,     # low * 1.4 when calibrated
        "currency": "USD",
        "org_size_label": str,
        "severity_scalar": float,
        "calibration_complete": bool,
      }

    Sequence: (1) look up (org_size, industry) in PAYROLL_BASELINE_GRID,
    (2) apply ORG_TYPE_SCALARS[org_type] to the grid result, (3) compute
    mean_multiplier via the existing, unchanged averaging logic across
    state_ids, (4) apply severity_scalar (unchanged, LOCKED), (5)
    low = adjusted_baseline * mean_multiplier * severity_scalar,
    high = low * 1.4 (unchanged, LOCKED).

    Returns low=None, high=None, calibration_complete=False when any
    required value is a CALIBRATION TARGET or the (org_size, industry)
    pair isn't a recognized grid cell. Downstream renderer treats this as
    "estimate pending calibration."
    """
    grid_entry = PAYROLL_BASELINE_GRID.get((org_size, industry))
    payroll_floor = grid_entry.payroll_floor_annual if grid_entry is not None else None
    org_type_scalar = ORG_TYPE_SCALARS.get(org_type)
    severity_scalar = SEVERITY_SCALAR.get(severity_tier, _DEFAULT_SEVERITY_SCALAR)

    state_multiplier_values = [
        STATE_MULTIPLIERS.get(sid, _DEFAULT_MULTIPLIER)
        for sid in state_ids
    ]

    calibration_complete = (
        payroll_floor is not None
        and org_type_scalar is not None
        and bool(state_ids)
        and all(v is not None for v in state_multiplier_values)
    )

    if not calibration_complete:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "org_size_label": org_size,
            "severity_scalar": severity_scalar,
            "calibration_complete": False,
        }

    adjusted_baseline = payroll_floor * org_type_scalar  # type: ignore[operator]
    mean_multiplier = sum(state_multiplier_values) / len(state_multiplier_values)  # type: ignore[arg-type]

    low = round(adjusted_baseline * mean_multiplier * severity_scalar, 2)
    high = round(low * 1.4, 2)

    return {
        "low": low,
        "high": high,
        "currency": "USD",
        "org_size_label": org_size,
        "severity_scalar": severity_scalar,
        "calibration_complete": True,
    }
'''

NEW_TEST_FRICTION_TAX = '''"""
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

print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
'''


def _print_diff(label: str, old: str, new: str) -> None:
    print(f"--- {label} ---")
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{label}",
        tofile=f"b/{label}",
    )
    sys.stdout.writelines(diff)
    print()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    old_ft = FRICTION_TAX_PY.read_text(encoding="utf-8")
    old_test = TEST_FRICTION_TAX_PY.read_text(encoding="utf-8")

    _print_diff("engine/friction_tax.py", old_ft, NEW_FRICTION_TAX)
    _print_diff("tools/test_friction_tax.py", old_test, NEW_TEST_FRICTION_TAX)

    if args.dry_run:
        print("DRY RUN -- no files written.")
        return

    FRICTION_TAX_PY.write_text(NEW_FRICTION_TAX, encoding="utf-8")
    TEST_FRICTION_TAX_PY.write_text(NEW_TEST_FRICTION_TAX, encoding="utf-8")
    print("WROTE engine/friction_tax.py")
    print("WROTE tools/test_friction_tax.py")


if __name__ == "__main__":
    main()
