"""
PRV3 -- Friction Tax: populate all 54 payroll_floor_annual cells (Set 2
complete). This is the last CALIBRATION TARGET gap in
PAYROLL_BASELINE_GRID.

DISCREPANCY FOUND AND FLAGGED, not silently resolved: the handoff stated
Retail & Hospitality's weighted-mean wage as "$39,650 (rounds from
39,651.xx)". Independently recomputed from the same three raw BLS
components: sum(wage x employment) / sum(employment) =
1,170,020,225,400 / 29,507,970 = 39,650.99..., which rounds to $39,651,
not $39,650. Using $39,651 (the independently verified figure) below.
Nonprofit & Education's stated $57,770 was independently reverified and
matches exactly (57,770.08 -> $57,770).

Structural change required, not just data population: PAYROLL_BASELINE_GRID
previously only stored source/citation text (the wage figure lived only
inside descriptive strings, never as a usable number) and was built
before HEADCOUNT_MIDPOINTS existed in the file. To actually compute
payroll_floor_annual = industry_wage x headcount_midpoint, this rewrite:
  1. Moves the HeadcountMidpointEntry/HEADCOUNT_MIDPOINTS block earlier
     in the file, before PAYROLL_BASELINE_GRID (a real dependency now,
     not just a documentation reference).
  2. Renames _INDUSTRY_WAGE_SOURCES to _INDUSTRY_WAGE_DATA, adding the
     actual wage float as a third tuple element (wage, source,
     citation_id) instead of leaving it embedded only in descriptive
     text -- now all 9 industries, the 3 new ones (Manufacturing &
     Industrial, Retail & Hospitality, Nonprofit & Education) with full
     source notes including weighted-average methodology for the two
     computed industries.
  3. PAYROLL_BASELINE_GRID's dict comprehension now computes
     payroll_floor_annual = round(wage * employees_per_firm, 2) for all
     54 cells instead of hardcoding None.

Test suite substantially reworked to match the new reality: grid and
org_type are now BOTH real/populated for every valid combination --
STATE_MULTIPLIERS (Set 3, untouched) is the only remaining CALIBRATION
TARGET gate. Includes a new positive-confirmation test that temporarily
populates one real STATE_MULTIPLIERS entry and confirms calibration_
complete genuinely flips True (proving the gate isn't just coincidentally
or incorrectly always False), alongside the exhaustive real-data check
confirming it's False everywhere today.

Usage:
  python tools/patch_friction_tax_grid_completion.py --dry-run
  python tools/patch_friction_tax_grid_completion.py --write
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
organizational state cluster. PAYROLL_BASELINE_GRID is fully populated
(payroll_floor_annual = industry_wage x headcount_midpoint for all 54
cells, both real and sourced). STATE_MULTIPLIERS remains the sole
CALIBRATION TARGET gate -- calibration_complete is still False for every
real session until that research pass lands. ORG_TYPE_SCALARS and
HEADCOUNT_MIDPOINTS were finalized 2026-08-01 -- see the source note on
each entry.

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

Payroll baseline formula: payroll_floor_annual = industry_wage x
headcount_midpoint. All 9 industry wages are real BLS OEWS May 2023
figures (6 single-sector lookups, 2 employment-weighted averages across
multiple BLS components -- Retail & Hospitality, Nonprofit & Education --
see each _INDUSTRY_WAGE_DATA entry for the full methodology and
component sources). Headcount midpoints (HEADCOUNT_MIDPOINTS, below) are
real, firm-count-weighted mean employees-per-firm values computed from
Census SUSB 2022 detailed-size data, replacing the earlier fabricated
SUSB-citation midpoint set (12/62/174.5/374.5/749.5/1500).

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


# -- Headcount and industry bucket keys -----------------------------------------
# IntakeData's real string values directly (engine/data/intake.py's
# INTAKE_FIELDS) -- not a separate internal bucket format.

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


# -- Headcount midpoints ----------------------------------------------------------
# Firm-count-weighted mean employees-per-firm for each headcount bucket.
# Source: Census SUSB 2022 Annual Data,
# us_state_naics_detailedsizes_2022.xlsx ("US & states detailed sizes"),
# national All-Industries Total row -- fetched and computed directly from
# the real file (2026-08-01), replacing the earlier fabricated SUSB
# citation. Defined before PAYROLL_BASELINE_GRID -- a real input to the
# payroll_floor_annual formula, not just a documentation reference.

@dataclass(frozen=True)
class HeadcountMidpointEntry:
    """Firm-count-weighted mean employees per firm for one headcount bucket."""
    employees_per_firm: Optional[float]
    source: Optional[str]
    citation_id: Optional[str]


HEADCOUNT_MIDPOINTS: dict[str, HeadcountMidpointEntry] = {
    "Under 25": HeadcountMidpointEntry(
        employees_per_firm=4.28,
        source=(
            "Census SUSB 2022 Annual Data, "
            "us_state_naics_detailedsizes_2022.xlsx ('US & states detailed "
            "sizes'), national All-Industries Total row, firm-count-weighted "
            "mean employees per firm. Brackets used: <5, 5-9, 10-14, 15-19, "
            "20-24 employees (whole brackets, no splitting needed -- real "
            "bracket boundaries align exactly at the 24/25 cutoff)."
        ),
        citation_id="SUSB_2022_detailedsizes_under25",
    ),
    "25-99": HeadcountMidpointEntry(
        employees_per_firm=45.10,
        source=(
            "Census SUSB 2022 Annual Data, "
            "us_state_naics_detailedsizes_2022.xlsx ('US & states detailed "
            "sizes'), national All-Industries Total row, firm-count-weighted "
            "mean employees per firm. Brackets used: 25-29, 30-34, 35-39, "
            "40-49, 50-74, 75-99 employees (whole brackets, no splitting "
            "needed -- real bracket boundaries align exactly at the 99/100 "
            "cutoff)."
        ),
        citation_id="SUSB_2022_detailedsizes_25to99",
    ),
    "100-249": HeadcountMidpointEntry(
        employees_per_firm=151.53,
        source=(
            "Census SUSB 2022 Annual Data, "
            "us_state_naics_detailedsizes_2022.xlsx ('US & states detailed "
            "sizes'), national All-Industries Total row, firm-count-weighted "
            "mean employees per firm. Brackets used: 100-149, 150-199 "
            "employees (whole), plus the 200-299 bracket split 50/50 by "
            "uniform-distribution assumption across its two sub-ranges "
            "(200-249 used here, 250-299 used in the 250-499 bucket below) "
            "-- the real brackets do not break at 249/250, so this bracket "
            "required proportional splitting."
        ),
        citation_id="SUSB_2022_detailedsizes_100to249",
    ),
    "250-499": HeadcountMidpointEntry(
        employees_per_firm=327.50,
        source=(
            "Census SUSB 2022 Annual Data, "
            "us_state_naics_detailedsizes_2022.xlsx ('US & states detailed "
            "sizes'), national All-Industries Total row, firm-count-weighted "
            "mean employees per firm. Brackets used: the 200-299 bracket "
            "split 50/50 by uniform-distribution assumption (250-299 half "
            "used here, 200-249 half used in the 100-249 bucket above), "
            "plus 300-399, 400-499 employees (whole)."
        ),
        citation_id="SUSB_2022_detailedsizes_250to499",
    ),
    "500-999": HeadcountMidpointEntry(
        employees_per_firm=692.43,
        source=(
            "Census SUSB 2022 Annual Data, "
            "us_state_naics_detailedsizes_2022.xlsx ('US & states detailed "
            "sizes'), national All-Industries Total row, firm-count-weighted "
            "mean employees per firm. Brackets used: 500-749, 750-999 "
            "employees (whole brackets, no splitting needed -- these two "
            "real brackets exactly span 500-999)."
        ),
        citation_id="SUSB_2022_detailedsizes_500to999",
    ),
    "1000+": HeadcountMidpointEntry(
        employees_per_firm=2027.26,
        source=(
            "Census SUSB 2022 Annual Data, "
            "us_state_naics_detailedsizes_2022.xlsx ('US & states detailed "
            "sizes'), national All-Industries Total row, firm-count-weighted "
            "mean employees per firm. Brackets used: 1,000-1,499, "
            "1,500-1,999, 2,000-2,499, 2,500-4,999 employees. The 5,000+ "
            "open bracket was deliberately excluded (Pete's Option 2 call) "
            "-- including it pulled the mean to approximately 6,230, "
            "dominated by a small number of mega-corporations, "
            "unrepresentative of this platform's realistic client base. "
            "This value represents firms in the 1,000-4,999 range only, "
            "not the full open-ended 1000+ population."
        ),
        citation_id="SUSB_2022_detailedsizes_1000to4999",
    ),
}


# -- Payroll baseline grid -------------------------------------------------------
# Keyed by (headcount, industry). All 54 cells now computed:
# payroll_floor_annual = industry_wage x headcount_midpoint. Payroll
# basis, not revenue -- see prompts/friction-tax-unit-decision.md.

@dataclass(frozen=True)
class PayrollBaselineEntry:
    """One cell of the payroll baseline grid."""
    payroll_floor_annual: Optional[float]  # industry_wage x headcount_midpoint, both real
    source: Optional[str]                  # named benchmark/study
    citation_id: Optional[str]             # cross-reference key into a future citations table


# Real BLS OEWS May 2023 mean annual wage figures, by industry, as
# (wage, source, citation_id) tuples. 6 are single-sector lookups; 2
# (Retail & Hospitality, Nonprofit & Education) are employment-weighted
# means across multiple real BLS components, documented plainly below
# rather than presented as a single sector pull.
_INDUSTRY_WAGE_DATA: dict[str, tuple[float, str, str]] = {
    "Professional Services": (
        102670.0,
        "BLS OEWS May 2023 mean annual wage: $102,670. naics4_541000. CONFIRMED exact.",
        "BLS_OEWS_2023_naics4_541000",
    ),
    "Healthcare & Life Sciences": (
        67320.0,
        "BLS OEWS May 2023 mean annual wage: $67,320. naics2_62. CONFIRMED exact.",
        "BLS_OEWS_2023_naics2_62",
    ),
    "Financial Services": (
        94150.0,
        "BLS OEWS May 2023 mean annual wage: $94,150. naics2_52. Corrected from an "
        "initial $86,120 claim, which did not match published BLS data.",
        "BLS_OEWS_2023_naics2_52",
    ),
    "Technology": (
        108110.0,
        "BLS OEWS May 2023 mean annual wage: $108,110. Sector 51 'Information.' "
        "Corrected from an initial $117,900 claim, which was actually NAICS 513000 "
        "'Publishing Industries,' not Technology. Note: Sector 51 'Information' is "
        "broader than ideal for a 'Technology' label (includes telecom, "
        "broadcasting, publishing) -- a narrower NAICS 541500 'Computer Systems "
        "Design and Related Services' figure would be more representative but was "
        "not independently confirmed this pass. Usable now, worth refining later.",
        "BLS_OEWS_2023_sector51_information",
    ),
    "Manufacturing & Industrial": (
        64440.0,
        "BLS OEWS May 2023 mean annual wage: $64,440. Sectors 31-33 (Manufacturing), "
        "All Occupations. CONFIRMED exact match to original claim.",
        "BLS_OEWS_2023_naics2_31-33",
    ),
    "Retail & Hospitality": (
        39651.0,
        "BLS OEWS May 2023 employment-weighted mean wage across three real "
        "components (not a single sector lookup): Retail Trade (Sectors 44-45) "
        "$42,720 wage / 15,580,040 employment; Food Services and Drinking Places "
        "(NAICS 722000) $35,220 wage / 12,002,830 employment; Accommodation "
        "(NAICS 721000) $42,440 wage / 1,925,100 employment. Weighted mean = "
        "sum(wage x employment) / sum(employment) = 1,170,020,225,400 / "
        "29,507,970 = $39,650.99, rounds to $39,651. Corrected from an initial "
        "$39,650 figure supplied for this task -- independently reverified and "
        "found to round up, not down.",
        "BLS_OEWS_2023_retail_hospitality_weighted",
    ),
    "Nonprofit & Education": (
        57770.0,
        "BLS OEWS May 2023 employment-weighted mean wage across two real "
        "components: Educational Services (Sector 61) $56,710 wage / 13,149,990 "
        "employment; Religious, Grantmaking, Civic, Professional, and Similar "
        "Organizations (NAICS 813000) $67,980 wage / 1,365,340 employment. "
        "Weighted mean = sum(wage x employment) / sum(employment) = "
        "838,551,746,100 / 14,515,330 = $57,770.08, rounds to $57,770. "
        "Independently reverified, matches the figure supplied for this task "
        "exactly.",
        "BLS_OEWS_2023_nonprofit_education_weighted",
    ),
    "Government & Public Sector": (
        74410.0,
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
        65470.0,
        "BLS OEWS May 2023 national estimate, All Occupations (SOC 00-0000): "
        "$65,470. CONFIRMED exact.",
        "BLS_OEWS_2023_national_all_occupations",
    ),
}

PAYROLL_BASELINE_GRID: dict[tuple[str, str], PayrollBaselineEntry] = {
    (headcount, industry): PayrollBaselineEntry(
        payroll_floor_annual=round(
            _INDUSTRY_WAGE_DATA[industry][0]
            * HEADCOUNT_MIDPOINTS[headcount].employees_per_firm,
            2,
        ),
        source=_INDUSTRY_WAGE_DATA[industry][1],
        citation_id=_INDUSTRY_WAGE_DATA[industry][2],
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
    "estimate pending calibration." As of this pass, PAYROLL_BASELINE_GRID
    and ORG_TYPE_SCALARS are fully populated -- STATE_MULTIPLIERS is the
    sole remaining gate.
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
