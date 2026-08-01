"""
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
PAYROLL_BASELINE_GRID entry). Headcount midpoints (HEADCOUNT_MIDPOINTS,
below) are now finalized -- real, firm-count-weighted mean employees-per-
firm values computed from Census SUSB 2022 detailed-size data, replacing
the earlier fabricated SUSB-citation midpoint set (12/62/174.5/374.5/
749.5/1500, which cited Census SUSB size-class data that did not
actually support those figures). payroll_floor_annual itself is still
not computable -- multiplying HEADCOUNT_MIDPOINTS against the sourced
industry wages is a separate follow-on task.

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


# -- Headcount midpoints ----------------------------------------------------------
# Firm-count-weighted mean employees-per-firm for each headcount bucket.
# Source: Census SUSB 2022 Annual Data,
# us_state_naics_detailedsizes_2022.xlsx ("US & states detailed sizes"),
# national All-Industries Total row -- fetched and computed directly from
# the real file (2026-08-01), replacing the earlier fabricated SUSB
# citation. Not yet wired into compute_friction_tax() -- payroll_floor_
# annual still requires this value multiplied by an industry wage figure,
# a separate follow-on task once both sides exist.

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
