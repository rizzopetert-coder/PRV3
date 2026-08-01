"""
PRV3 -- Friction Tax data population: Set 1 (ORG_TYPE_SCALARS, final) +
Set 2 (PAYROLL_BASELINE_GRID, sourced but not finalized).

Rewrites engine/friction_tax.py and tools/test_friction_tax.py in full.

SCOPE NOTE, flagged rather than silently done: ORG_TYPE_SCALARS did not
previously carry source/citation fields (unlike PAYROLL_BASELINE_GRID,
which got PayrollBaselineEntry in the restructure). Pete's task
explicitly authorized adding matching fields if the structure didn't
already support them ("add matching fields if it doesn't already carry
them"), so this adds a new OrgTypeScalarEntry dataclass mirroring
PayrollBaselineEntry's shape. This is a real, if small, change to
compute_friction_tax()'s internal ORG_TYPE_SCALARS access (unwrapping
.scalar from the entry instead of reading a bare float) -- not just data
population, contrary to the task's "no logic changes" framing. Flagged
in the dry-run report; test suite fully updated to match.

Set 1: all 6 ORG_TYPE_SCALARS finalized (5 at 1.00 parity, Government at
1.05), each with a real source note -- including the "no defensible
source found, defaulted to parity" cases, which are themselves a
documented research finding, not an absence of one.

Set 2: PAYROLL_BASELINE_GRID's payroll_floor_annual stays None for all
54 cells (headcount midpoints are a separate, unresolved research item --
the original SUSB-derived midpoint claim was fabricated, flagged
separately, not fixed here). 6 of 9 industries (Professional Services,
Healthcare & Life Sciences, Financial Services, Technology, Government &
Public Sector, Other) get their source/citation_id populated across all
6 headcount-bucket cells with a confirmed BLS OEWS May 2023 wage figure.
The remaining 3 industries (Manufacturing & Industrial, Retail &
Hospitality, Nonprofit & Education) are left completely untouched --
unverified or mismatched claims, not written under a misrepresentative
label.

Net effect on calibration_complete: still False for every real session,
for every (headcount, industry, org_type) combination -- payroll_floor_
annual remains None everywhere and STATE_MULTIPLIERS remains entirely
None (Set 3, untouched). Verified by an exhaustive test over the full
6x9x6 combination space, not spot-checked.

Usage:
  python tools/patch_friction_tax_data_population.py --dry-run
  python tools/patch_friction_tax_data_population.py --write
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
organizational state cluster. PAYROLL_BASELINE_GRID's payroll_floor_
annual values and STATE_MULTIPLIERS remain CALIBRATION TARGET until
further source research resolves them. ORG_TYPE_SCALARS was finalized
2026-08-01 -- see the source note on each entry (some are a documented
"no defensible differential found, defaulted to parity" finding, not an
absence of research).

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

Payroll baseline formula (not yet computable): payroll_floor_annual =
industry_wage x headcount_midpoint. Industry wage figures are populated
below for 6 of 9 industries (source/citation_id only -- see each
PAYROLL_BASELINE_GRID entry). Headcount midpoints are a separate,
unresolved research item -- an earlier midpoint set (12/62/174.5/374.5/
749.5/1500 for the 6 buckets) cited Census SUSB size-class data that does
not actually support those figures (SUSB distributions are bottom-skewed
toward the smallest firms; they do not support a "1500 median enterprise
size" for the open-ended "1000+" bucket). 1500 remains Pete's working
placeholder for that bucket specifically, not a cited or final value.

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
# payroll_floor_annual is CALIBRATION TARGET for all 54 cells -- the
# formula (industry_wage x headcount_midpoint) can't resolve until
# headcount midpoints are researched (see module docstring). 6 of 9
# industries below carry a confirmed BLS OEWS May 2023 wage figure in
# their source/citation_id fields, ready to compute once midpoints
# resolve. Payroll basis, not revenue -- see
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
    payroll_floor_annual: Optional[float]  # CALIBRATION TARGET -- pending headcount midpoints
    source: Optional[str]                  # named benchmark/study, None until populated
    citation_id: Optional[str]             # cross-reference key into a future citations table


# Confirmed BLS OEWS May 2023 mean annual wage figures, by industry.
# (source, citation_id) tuples -- payroll_floor_annual is populated
# separately once headcount midpoints resolve, not here. Industries not
# listed here (Manufacturing & Industrial, Retail & Hospitality,
# Nonprofit & Education) had unverified or mismatched claims and are
# deliberately left unsourced this pass -- see module docstring.
_INDUSTRY_WAGE_SOURCES: dict[str, tuple[str, str]] = {
    "Professional Services": (
        "BLS OEWS May 2023 mean annual wage: $102,670. naics4_541000. CONFIRMED exact.",
        "BLS_OEWS_2023_naics4_541000",
    ),
    "Healthcare & Life Sciences": (
        "BLS OEWS May 2023 mean annual wage: $67,320. naics2_62. CONFIRMED exact.",
        "BLS_OEWS_2023_naics2_62",
    ),
    "Financial Services": (
        "BLS OEWS May 2023 mean annual wage: $94,150. naics2_52. Corrected from an "
        "initial $86,120 claim, which did not match published BLS data.",
        "BLS_OEWS_2023_naics2_52",
    ),
    "Technology": (
        "BLS OEWS May 2023 mean annual wage: $108,110. Sector 51 'Information.' "
        "Corrected from an initial $117,900 claim, which was actually NAICS 513000 "
        "'Publishing Industries,' not Technology. Note: Sector 51 'Information' is "
        "broader than ideal for a 'Technology' label (includes telecom, "
        "broadcasting, publishing) -- a narrower NAICS 541500 'Computer Systems "
        "Design and Related Services' figure would be more representative but was "
        "not independently confirmed this pass. Usable now, worth refining later.",
        "BLS_OEWS_2023_sector51_information",
    ),
    "Government & Public Sector": (
        "BLS OEWS May 2023 mean annual wage: $74,410. Sector 99 (Federal/State/"
        "Local Government, excl. schools/hospitals/USPS). Corrected from an "
        "initial $68,140 claim, which used the wrong sector concept "
        "(Census/NAICS 'Sector 92' Public Administration is not BLS OEWS's "
        "government designation) and appears to have pulled the wrong data cell "
        "entirely (matched the 'Legislators' detailed-occupation figure, not a "
        "sector aggregate).",
        "BLS_OEWS_2023_sector99_government",
    ),
    "Other": (
        "BLS OEWS May 2023 national estimate, All Occupations (SOC 00-0000): "
        "$65,470. CONFIRMED exact.",
        "BLS_OEWS_2023_national_all_occupations",
    ),
}

PAYROLL_BASELINE_GRID: dict[tuple[str, str], PayrollBaselineEntry] = {
    (headcount, industry): PayrollBaselineEntry(
        payroll_floor_annual=None,
        source=_INDUSTRY_WAGE_SOURCES.get(industry, (None, None))[0],
        citation_id=_INDUSTRY_WAGE_SOURCES.get(industry, (None, None))[1],
    )
    for headcount in HEADCOUNT_BUCKETS
    for industry in INDUSTRIES
}


# -- Org type scalar --------------------------------------------------------------
# Standalone multiplicative scalar applied to the grid lookup result, not a
# third grid axis. Keys match IntakeData.org_type / engine/data/intake.py's
# INTAKE_FIELDS["org_type"]. FINALIZED 2026-08-01 -- all 6 entries carry a
# real source note. Several are a documented "no defensible public
# differential found, defaulted to parity" research finding rather than a
# proven multiplier -- see each entry's source field for the correction
# history where an initial claim didn't hold up.

@dataclass(frozen=True)
class OrgTypeScalarEntry:
    """One entry of the org type scalar table."""
    scalar: Optional[float]
    source: Optional[str]
    citation_id: Optional[str]


ORG_TYPE_SCALARS: dict[str, OrgTypeScalarEntry] = {
    "Founder-led": OrgTypeScalarEntry(
        scalar=1.00,
        source=(
            "No defensible public source found (Aon Radford Global Technology & "
            "Life Sciences Compensation Survey is proprietary/paywalled, cannot "
            "verify content). Defaulted to parity per no-citable-differential "
            "convention."
        ),
        citation_id=None,
    ),
    "PE or VC-backed": OrgTypeScalarEntry(
        scalar=1.00,
        source=(
            "No defensible source found. Cited PitchBook 'Portfolio Company "
            "Compensation Benchmark Report' does not appear to exist under that "
            "name -- PitchBook's actual product (Thelander-PitchBook Investment "
            "Firm Compensation Survey) measures investment-firm staff pay, not "
            "portfolio-company workforce. Defaulted to parity."
        ),
        citation_id=None,
    ),
    "Privately held professional leadership": OrgTypeScalarEntry(
        scalar=1.00,
        source="Definitional baseline, 1.00 by construction.",
        citation_id=None,
    ),
    "Nonprofit": OrgTypeScalarEntry(
        scalar=1.00,
        source=(
            "Corrected from an initial 0.90 claim (misattributed to 'BLS OEWS "
            "Non-Profit Wage Ratios', which does not appear to be a real BLS "
            "product). Actual data (BLS Monthly Labor Review, 2024, 'Nonprofit "
            "earnings and sectoral employment in the United States since 1994') "
            "shows nonprofit wages near-parity to for-profit, higher on a raw "
            "basis in many fields. Corrected to parity."
        ),
        citation_id="BLS_MLR_2024_nonprofit_earnings",
    ),
    "Publicly traded": OrgTypeScalarEntry(
        scalar=1.00,
        source=(
            "Corrected from an initial 1.10 claim. Cited source (Mueller, "
            "Ouimet & Simintzi, NBER Working Paper No. 20876 -- note: "
            "originally miscited as No. 20820 -- published American Economic "
            "Review 2017) is a real paper but studies within-firm pay "
            "inequality by firm size, not a public-vs-private wage premium. "
            "No valid replacement source found this pass. Defaulted to parity "
            "pending future research."
        ),
        citation_id=None,
    ),
    "Government": OrgTypeScalarEntry(
        scalar=1.05,
        source=(
            "Corrected from an initial 1.17 claim. Source (CBO, 'Comparing the "
            "Compensation of Federal and Private-Sector Employees in 2022', "
            "April 2024) is real; its actual headline finding is federal "
            "employees average ~5% higher total compensation overall (varies "
            "significantly by education level -- 36% higher at high-school-only "
            "level, 15% higher at bachelor's level, lower at advanced-degree "
            "level). Corrected to the report's actual overall finding, 1.05."
        ),
        citation_id="CBO_2024_federal_private_comp",
    ),
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
    (2) apply ORG_TYPE_SCALARS[org_type].scalar to the grid result, (3)
    compute mean_multiplier via the existing, unchanged averaging logic
    across state_ids, (4) apply severity_scalar (unchanged, LOCKED), (5)
    low = adjusted_baseline * mean_multiplier * severity_scalar,
    high = low * 1.4 (unchanged, LOCKED).

    Returns low=None, high=None, calibration_complete=False when any
    required value is a CALIBRATION TARGET or the (org_size, industry)
    pair isn't a recognized grid cell. Downstream renderer treats this as
    "estimate pending calibration."
    """
    grid_entry = PAYROLL_BASELINE_GRID.get((org_size, industry))
    payroll_floor = grid_entry.payroll_floor_annual if grid_entry is not None else None
    org_type_entry = ORG_TYPE_SCALARS.get(org_type)
    org_type_scalar = org_type_entry.scalar if org_type_entry is not None else None
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
