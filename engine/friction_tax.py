"""
PRV3 Scoring Engine -- Output Layer
Friction Tax Computation

Computes an estimated financial consequence range for the identified
organizational state cluster. All three calibration axes are now
populated: PAYROLL_BASELINE_GRID (all 54 cells, industry_wage x
headcount_midpoint), ORG_TYPE_SCALARS, and STATE_MULTIPLIERS (all 57
states scored across a 3-criterion attritional rubric -- turnover,
productivity, decision_quality; Legal/Compliance is fully split out to
its own mechanism-aware design, prompts/friction-tax-legal-compliance-
methodology.md, and is no longer part of this rubric's raw score or
multiplier -- see prompts/friction-tax-state-multiplier-methodology.md).
calibration_complete now returns True for any real, recognized
(org_size, industry, org_type, state_ids) combination. ORG_TYPE_SCALARS
and HEADCOUNT_MIDPOINTS were finalized 2026-08-01, STATE_MULTIPLIERS
2026-08-02, rescaled (Option A) and multi-state compounding redesign
implemented 2026-08-03 -- see the source note on each entry and
prompts/friction-tax-multistate-compounding-methodology.md.

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

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

_logger = logging.getLogger(__name__)


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
    "Construction",
    "Transportation & Warehousing",
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
# Keyed by (headcount, industry). All 66 cells now computed (6 headcount
# buckets x 11 industries, grown from the original 54 by the Industry
# Taxonomy Expansion, MOB v4.100):
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
    "Construction": (
        67430.0,
        "BLS OEWS May 2023 mean annual wage: $67,430. Sector 23 "
        "(Construction), All Occupations. Employment 7,921,080. CONFIRMED "
        "exact.",
        "BLS_OEWS_2023_naics2_23",
    ),
    "Transportation & Warehousing": (
        59320.0,
        "BLS OEWS May 2023 mean annual wage: $59,320. Sectors 48-49 "
        "(Transportation and Warehousing), All Occupations. Employment "
        "7,333,400. CONFIRMED exact.",
        "BLS_OEWS_2023_naics2_48-49",
    ),
    "Other": (
        63446.0,
        "BLS OEWS May 2023 employment-weighted mean wage across nine real "
        "components, genuinely excluding every industry already claimed "
        "elsewhere in this grid (rebuilt from the prior single SOC 00-0000 "
        "national-all-occupations lookup, which structurally overlapped with "
        "Construction and Transportation & Warehousing once those became "
        "their own columns): Agriculture, Forestry, Fishing and Hunting "
        "(Sector 11) $43,010 wage / 413,580 employment; Mining, Quarrying, "
        "and Oil and Gas Extraction (Sector 21) $77,020 wage / 571,160 "
        "employment; Utilities (Sector 22) $97,250 wage / 564,750 employment; "
        "Wholesale Trade (Sector 42) $71,410 wage / 6,013,210 employment; "
        "Real Estate and Rental and Leasing (Sector 53) $61,630 wage / "
        "2,388,050 employment; Management of Companies and Enterprises "
        "(Sector 55) $106,640 wage / 2,771,010 employment; Administrative and "
        "Support and Waste Management and Remediation Services (Sector 56) "
        "$52,650 wage / 9,496,560 employment; Arts, Entertainment, and "
        "Recreation (Sector 71) $50,550 wage / 2,523,660 employment; Other "
        "Services except Public Administration (Sector 81) MINUS NAICS 813000 "
        "(Religious, Grantmaking, Civic, Professional, and Similar "
        "Organizations, already claimed by the Nonprofit & Education entry) "
        "-- residual $47,664 wage / 2,951,060 employment, computed by "
        "subtracting 813000's wage bill and employment from Sector 81's full "
        "total ($54,090 wage / 4,316,400 employment) and re-deriving the "
        "residual mean. Weighted mean across all nine = sum(wage x "
        "employment) / sum(employment) = $63,445.66, rounds to $63,446. "
        "Verified independently (two-pass computation, no discrepancy).",
        "BLS_OEWS_2023_other_nine_component_residual",
    ),
}

def get_industry_wage(industry: str) -> Optional[float]:
    """
    Public accessor for _INDUSTRY_WAGE_DATA's per-employee mean annual wage
    (BLS OEWS May 2023), keyed by the same 9 industry categories intake
    already collects (engine/data/intake.py INTAKE_FIELDS["industry"]).
    Returns None on an unrecognized industry -- matches this file's
    existing lookup convention (PAYROLL_BASELINE_GRID.get(),
    ORG_TYPE_SCALARS.get()), not an exception. Category D (free condensed
    diagnostic), this session -- the only consumer of this accessor;
    PAYROLL_BASELINE_GRID's own headcount x industry_wage math is
    untouched, this is a standalone single-value lookup.
    """
    entry = _INDUSTRY_WAGE_DATA.get(industry)
    return entry[0] if entry is not None else None


def resolve_headcount_bucket(headcount: int) -> str:
    """
    Map a precise headcount int (engine/data/intake.py's
    HEADCOUNT_FIELD_SPEC) to its HEADCOUNT_BUCKETS bucket string.
    Boundaries match the field spec's increment schedule exactly.
    Genuinely new -- confirmed via repo-wide grep that no equivalent
    function existed anywhere before this.
    """
    if headcount < 25:
        return "Under 25"
    if headcount < 100:
        return "25-99"
    if headcount < 250:
        return "100-249"
    if headcount < 500:
        return "250-499"
    if headcount < 1000:
        return "500-999"
    return "1000+"


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
# Per-state attritional_fraction applied to the adjusted payroll baseline
# (payroll basis, not revenue -- see prompts/friction-tax-unit-decision.md).
# FINALIZED 2026-08-02, RESCALED 2026-08-03 (Option A) -- all 57 states
# scored across a 3-criterion attritional rubric (turnover/retention,
# productivity/output, decision-quality/velocity), each 0-2, min-max
# interpolated onto [0.05, 0.25] (payroll fraction), replacing the
# original 4-criterion / [1.0, 1.4] design. Legal/Compliance is no longer
# part of this rubric's raw_score or multiplier -- each state's
# StateCriterionScore for "legal" is still recorded below (needed by the
# separate mechanism-aware design, prompts/friction-tax-legal-compliance-
# methodology.md) but is excluded from raw_score's sum. See
# prompts/friction-tax-state-multiplier-methodology.md for full
# methodology and prompts/friction-tax-multistate-compounding-
# methodology.md for how multiple identified states combine.
# Keys: state_id strings matching engine/data/states.py registry (57 states).

@dataclass(frozen=True)
class StateCriterionScore:
    """One 0-2 criterion score and its rationale for a single state."""
    score: int
    rationale: str


@dataclass(frozen=True)
class StateMultiplierEntry:
    """
    One state's standalone attritional_fraction (as if it were the only
    identified state) and its scoring basis. raw_score sums only the 3
    attritional criteria (turnover, productivity, decision_quality);
    criteria still carries all 4 keys including "legal", whose score is
    retained for the separate Legal/Compliance design but excluded from
    raw_score and multiplier.
    """
    multiplier: float
    raw_score: int
    criteria: dict[str, StateCriterionScore]


STATE_MULTIPLIERS: dict[str, StateMultiplierEntry] = {
    "built_to_fail": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="This role shows a documented pattern of repeat departures, each treated by the org as an individual hiring failure rather than a structural one — the modal incumbent burns out and leaves, and the next hire inherits the identical impossible math.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Workarounds and efficiencies mask the obvious signs of under-resourcing, so productivity loss doesn't surface as clearly as the structural gap would predict.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="The modal incumbent is making calls under sustained resource strain, which reliably produces slower or lower-quality decisions than the same person would make in a properly resourced version of the role.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="For the typical mid-level incumbent, exposure centers on wrongful-termination/constructive-discharge risk — performance failures traceable to structural under-resourcing rather than individual conduct.",
            ),
        },
    ),
    "invisible_performance_management": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Underperformance is quietly tolerated rather than addressed, which can nudge strong performers to leave in frustration, but it's a secondary effect, not the state's primary mechanism.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="An underperforming employee stays in place with no formal correction, so the productivity gap they represent persists unaddressed — this is the direct, primary cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="The condition is about documentation, not decision-making itself; the manager's judgment is accurate, just unrecorded, so it doesn't independently degrade decision quality.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="When the org eventually needs to act on cause, the absence of a documented record turns a sound judgment into an unsupportable one — direct wrongful-termination exposure.",
            ),
        },
    ),
    "the_dormant_talent": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="The people with the clearest read on the gap between their potential and their growth are also the ones most able to leave — a direct, named retention risk.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Development stalls across the team while the manager's own output/visibility climbs, meaning the org is not getting the return on talent it's paying for.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Talent that isn't being developed toward its capability produces modestly weaker decisions than a fully-grown team would, though this is more an opportunity cost than an acute failure.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable legal exposure category — this is a talent-development gap, not a compliance or liability issue.",
            ),
        },
    ),
    "the_overloaded_manager": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="One-on-ones have become status updates and development conversations don't happen, which is a direct driver of attrition among people who feel unsupported.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Decisions and coaching queue behind competing demands, producing a moderate drag on team output rather than a dramatic one.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions wait in line behind everything else the manager is carrying, which slows velocity without necessarily making any single decision worse.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No clear liability category — this is a capacity/design problem, not a compliance exposure.",
            ),
        },
    ),
    "the_paper_tiger": StateMultiplierEntry(
        multiplier=0.08333333333333334,
        raw_score=1,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Peers who've watched an obvious performance problem go unaddressed for years may lose confidence in management's standards, a secondary retention drag.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="The underperformer's day-to-day output isn't the primary cost here — it's the paper trail, not the work itself, that's broken.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="This isn't a decision-quality problem; the manager's read has been accurate all along, just never documented.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="When the org tries to act on documented cause and discovers the file doesn't support it, that's a direct, acute wrongful-termination exposure.",
            ),
        },
    ),
    "the_undefined_role": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People in an undefined role absorb constant ambiguity about what's actually expected of them, a recognized driver of voluntary attrition.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Work duplicates in some places and goes unclaimed in others — a direct, structural productivity loss visible in delivery gaps.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions about who owns what get relitigated informally rather than made once, a moderate drag on velocity.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Orphaned work can include compliance-relevant tasks (reporting, safety checks) that nobody clearly owns — a real but secondary exposure.",
            ),
        },
    ),
    "the_unformed_leader": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="Turnover concentrates among the people who had other options — the state's own definition names this as the direct, primary cost.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="The team has quietly lowered what it expects from the organization and adjusted its own output accordingly — a direct productivity effect.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Inconsistent direction produces some downstream decision drag as people guess at priorities, though it's more diffuse than acute.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance exposure category from inconsistent coaching alone.",
            ),
        },
    ),
    "compression_crisis": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Concentrated strain on fewer decision-makers can drive burnout-driven attrition among the remaining managers, a secondary effect.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="What looks efficient on an org chart shows up as strain wherever the work actually gets executed — a moderate, diffuse cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decision-making is concentrated into fewer people than the work requires, directly and significantly slowing or degrading the calls that used to be distributed.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Overloaded decision-makers are more likely to make compliance-relevant errors under strain, a secondary rather than primary exposure.",
            ),
        },
    ),
    "decision_paralysis": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="People who've stopped counting on a decision holding may disengage or leave, a secondary retention effect.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="The org isn't doing everything it should be doing while it cycles through the same conversations without landing — a direct, significant productivity cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="The core mechanism of this state is decisions that don't hold and get relitigated — a direct, significant decision-velocity failure.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category — this is a governance-speed problem, not a liability one.",
            ),
        },
    ),
    "disparate_impact_architecture": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Groups experiencing worse outcomes under a facially neutral policy may leave at higher rates, a secondary and harder-to-isolate effect.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Uneven outcomes can create friction and disengagement among affected groups, a moderate rather than primary cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="The policy itself wasn't a bad decision in isolation — the aggregate pattern is what creates cost, making this more diffuse than acute.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="This is close to textbook disparate-impact exposure — a facially neutral policy producing recognizable group-level outcome differences is a direct, significant legal risk.",
            ),
        },
    ),
    "dueling_narratives": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="People caught between conflicting official accounts may disengage or leave, a secondary effect of the confusion itself.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Reconciling which version of events is accurate consumes time and attention that would otherwise go to the work.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions made on one version of the facts that conflicts with another version circulating elsewhere are a direct, significant velocity/quality risk.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Contradictory internal accounts of the same facts create secondary exposure if either version surfaces in litigation or regulatory inquiry.",
            ),
        },
    ),
    "hr_capture": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who know HR won't protect them from the powerful have direct reason to leave rather than raise a concern and stay.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="This doesn't directly degrade day-to-day work output — its cost shows up in trust and risk, not productivity.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Complaint-handling decisions get shaped by protecting specific leaders rather than the org, a moderate distortion of otherwise normal HR judgment.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="A structurally compromised HR function that treats complaints against leadership differently is a direct, significant retaliation/discrimination exposure.",
            ),
        },
    ),
    "heard_and_ignored": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People stop using the channel once they've tested it and learned nothing changes, and stop trusting the organization enough to stay — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="The channel's failure doesn't directly touch day-to-day productivity — the cost is trust and legal, not output.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions get made without input the channel was supposed to surface, a moderate rather than acute quality cost.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="A reporting mechanism that functions as a formality rather than a corrective one is direct evidence in any future retaliation or failure-to-act claim.",
            ),
        },
    ),
    "invisible_influence_architecture": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="People who don't know who actually has to say yes may become frustrated and disengage, a secondary retention effect.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Time spent discovering the real decision-makers is time not spent on the work itself — a moderate drag.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Formally accountable people are not always the ones actually deciding outcomes — a direct, significant distortion of how decisions actually get made.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category — this is an informal-power problem, not a liability one.",
            ),
        },
    ),
    "leadership_continuity_risk": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="The risk is concentrated in a small number of people rather than broad-based, so the turnover cost is real but narrow.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Day-to-day output isn't degraded while these people remain — the cost is entirely contingent on departure, a moderate ongoing risk rather than an active drag.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="The organization has no defined plan for what happens when any of these people leave — a direct, significant velocity failure the moment it becomes real.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from succession risk alone.",
            ),
        },
    ),
    "paper_shield": StateMultiplierEntry(
        multiplier=0.11666666666666667,
        raw_score=2,
        criteria={
            "turnover": StateCriterionScore(
                score=0,
                rationale="Untested plans don't drive day-to-day departures — this is a dormant risk, not an active retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="No effect on current productivity — the plans exist and nobody is currently relying on them.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="The organization believes it is prepared because the documentation says so, and discovers the gap between documented and actual readiness at exactly the worst moment — a direct, significant decision-quality failure when it matters most.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No active compliance exposure until the plan is actually tested and fails — the risk is real but not yet realized.",
            ),
        },
    ),
    "pay_exposure": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="Each departure the org discovers this reactively through is, by the state's own definition, a preventable one — a direct, primary retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Underpaid employees who haven't yet left may disengage or reduce discretionary effort, a moderate secondary cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="This isn't a decision-quality problem — it's a market-alignment gap that shows up in outcomes, not in how decisions get made.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Persistent pay misalignment can shade into pay-equity exposure depending on whether the gaps correlate with protected characteristics — a secondary, contingent risk.",
            ),
        },
    ),
    "planning_authority_gap": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Planners whose work routinely waits on someone else's approval may become frustrated, a secondary retention effect.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Plans get built and then sit waiting for approval from someone who wasn't part of building them — a direct, significant waste of planning effort.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="The people planning and the people deciding are structurally separated — a direct, significant velocity failure built into the process itself.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from a planning/authority mismatch alone.",
            ),
        },
    ),
    "sequential_decision_blindness": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Individuals affected by the aggregate pattern may leave, though this is secondary to the legal exposure itself.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Coordinating after the fact to understand the pattern consumes time that wouldn't be needed if decisions were coordinated from the start.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="No single decision-maker intended the pattern — each decision was individually defensible, making this more diffuse than an acute quality failure.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="A pattern that looks like retaliation or targeting when viewed in aggregate, even without any single bad-faith decision, is a direct, significant legal exposure.",
            ),
        },
    ),
    "the_exposed": StateMultiplierEntry(
        multiplier=0.11666666666666667,
        raw_score=2,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Employees with real concerns and nowhere to bring them may disengage or leave, a secondary rather than primary effect of the structural gap.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="The absence of an HR function doesn't directly degrade day-to-day work output for most employees.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions with employee-relations implications get made without anyone whose job it is to flag the risk — a moderate quality gap.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="The organization is accumulating liability on a timeline it doesn't know is running — a direct, significant, compounding legal exposure by definition.",
            ),
        },
    ),
    "the_founders_grip": StateMultiplierEntry(
        multiplier=0.25,
        raw_score=6,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="The senior people who couldn't live with the bottleneck have already left — a direct, named retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Work either waits in queue or routes around the bottleneck entirely — a direct, significant productivity loss.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions are being made on information that's weeks old by the time it reaches the one approver — a direct, significant velocity and quality failure.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from decision-bottlenecking alone.",
            ),
        },
    ),
    "the_lost_map": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=0,
                rationale="The people who hold the knowledge aren't necessarily more likely to leave because of this condition — the cost is realized on departure, not before.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="The organization relearns things the expensive way every time someone with unwritten knowledge leaves — a direct, significant productivity cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions get made without institutional context that existed only in someone's head — a direct, significant quality failure once that person is gone.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from undocumented institutional knowledge alone.",
            ),
        },
    ),
    "the_pay_fog": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="Once someone lines up the inconsistencies, the unfairness becomes hard to miss and hard to stay for — a direct retention cost once discovered.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Employees who sense unexplained pay inconsistency may reduce discretionary effort, a moderate secondary cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="Each individual pay decision may have been locally reasonable — the cost is in the aggregate pattern, not in any single decision's quality.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="Inconsistent, indefensible pay logic across the organization is a direct, significant pay-equity exposure once examined in aggregate.",
            ),
        },
    ),
    "the_policy_lag": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Employees navigating a gap between stated and actual policy may become frustrated, a secondary retention effect.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="Practice has already moved on without the documentation — day-to-day work isn't necessarily degraded by the paperwork lag itself.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions get made against outdated written policy that doesn't reflect how the organization actually operates — a direct, significant quality risk.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="A policy that no longer matches practice is direct evidence of a gap between what the org says and does — significant exposure if either version is examined.",
            ),
        },
    ),
    "the_tolerated_violation": StateMultiplierEntry(
        multiplier=0.11666666666666667,
        raw_score=2,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who can accurately describe a known violation that nobody with authority stops it may leave rather than continue tolerating it — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="The violation itself doesn't directly degrade day-to-day output for most of the organization.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="This isn't a decision-quality problem — everyone involved can already describe the violation accurately; the failure is action, not information or judgment.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="A known violation of policy or law that's been allowed to continue is direct, significant, and easily provable exposure.",
            ),
        },
    ),
    "the_unexamined_algorithm": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=0,
                rationale="No direct link between an unaudited algorithm and employee turnover specifically.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Errors, bias, or drift in the system's outputs compound silently until discovered — a direct, significant cost once realized.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="The system is materially influencing consequential decisions with nobody checking whether it's right — a direct, significant quality risk by design.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Algorithmic bias in employment decisions carries real legal exposure, though it's contingent on what the algorithm is actually doing, making it secondary rather than certain.",
            ),
        },
    ),
    "the_uninitiated": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=0,
                rationale="No direct link between organizational inexperience with a specific event type and general turnover.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="The costliest mistakes are the ones nobody on the team knows to watch for — a direct, significant cost specific to this event.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Capable, underprepared leaders make decisions without knowing what they don't know — a direct, significant quality risk during the event itself.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category independent of what the specific unfamiliar event actually is.",
            ),
        },
    ),
    "the_unsolved_problem": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Repeatedly experiencing the same unsolved problem can erode confidence in leadership's ability to fix things, a secondary retention effect.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="The organization pays repeatedly for a resolution that never actually resolves anything — a moderate, recurring cost rather than a single acute one.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Each recurrence gets treated as new rather than diagnosed as a repeat, a moderate quality drag on problem-solving specifically.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Depending on the nature of the recurring problem, unaddressed patterns can accumulate into a documentable pattern of inaction — a secondary, contingent exposure.",
            ),
        },
    ),
    "transition_paralysis": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People operating in a gap with no clear governing authority may leave rather than continue navigating the ambiguity — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Work happens in a structural gap between the old and new systems — a direct, significant productivity loss.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Uncertainty about which authority governs day to day produces moderate decision friction rather than an acute single failure.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from a stalled transition alone.",
            ),
        },
    ),
    "decision_blindness": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People whose critical input was never sought may disengage from a process that visibly excluded them — a direct retention signal.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="The decision itself may need to be revisited once the missing information surfaces, a moderate secondary cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="A significant decision was made without input that would have changed it — this is, by definition, a direct, significant quality failure.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from a single information gap alone.",
            ),
        },
    ),
    "distributed_culture_fragmentation": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=0,
                rationale="No direct link between fragmented norms across locations and increased turnover specifically.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Friction shows up exactly at the seams where teams have to work together — a direct, significant productivity cost at coordination points.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions that assume shared norms fail at the seams between teams operating on different unwritten rules — a direct, significant quality risk.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Fragmented norms can produce inconsistent application of policy across locations, a secondary compliance risk depending on what norms have diverged.",
            ),
        },
    ),
    "silosolation": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Frustration with cross-team friction may contribute to attrition, a secondary rather than primary effect.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Teams optimizing for their own metrics without visibility into downstream effects is a direct, significant productivity cost at the organizational level.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions made with only local visibility, when the work is actually interdependent, are a direct, significant quality risk.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from siloed optimization alone.",
            ),
        },
    ),
    "the_arbitrary_standard": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who notice they're held to a different standard than others have direct reason to leave for a more consistent environment.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Inconsistent application of rules produces moderate disengagement rather than a direct output-level cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="The inconsistency itself is more a fairness pattern than a decision-quality failure, though it can shade into worse decisions under favoritism.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="A non-accidental pattern of who benefits from inconsistent standards is close to a textbook disparate-treatment claim — direct, significant exposure.",
            ),
        },
    ),
    "the_fracture": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People caught on either side of a broken working relationship may choose to leave rather than keep working around it — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Work still moves, but around the fracture rather than through it — a moderate rather than severe productivity loss.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions that would benefit from the broken relationship's coordination now happen without it — a moderate quality drag.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from a broken working relationship alone.",
            ),
        },
    ),
    "the_second_close": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Repeated renegotiation erodes trust and may contribute to disengagement, a secondary rather than primary retention effect.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="The underlying cause was never actually fixed the first time — a direct, significant cost as the same problem consumes attention twice.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="The people involved are less willing to extend trust a second time, a moderate drag on how future decisions in that relationship get made.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from a re-litigated relationship alone.",
            ),
        },
    ),
    "the_suppression_filter": StateMultiplierEntry(
        multiplier=0.25,
        raw_score=6,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who've learned that raising real problems gets filtered into nothing may disengage or leave — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Each layer believes it's protecting leadership from noise, and the aggregate effect is a direct, significant loss of accurate operating information.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Leadership consistently gets the last, most diluted version of the truth — a direct, significant decision-quality failure by design.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="A filtered information environment can become relevant if a known risk was filtered out before it could be acted on — a secondary, contingent exposure.",
            ),
        },
    ),
    "cultural_overtime": StateMultiplierEntry(
        multiplier=0.11666666666666667,
        raw_score=2,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="An unstated expectation of extended hours is a well-documented driver of burnout-related attrition — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="Extended hours may sustain short-term output rather than degrade it, which is part of why the pattern persists undetected.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="No direct link between an hours-culture norm and decision quality specifically.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="The state's own definition names real legal and financial exposure from unpaid/uncompensated overtime patterns — a direct, significant risk.",
            ),
        },
    ),
    "culture_drift": StateMultiplierEntry(
        multiplier=0.25,
        raw_score=6,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who joined for the stated values and now work inside the actual ones may leave once the gap becomes visible — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="What actually gets rewarded no longer matches what's stated, so people optimize for the real incentives — a direct, significant misalignment cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions increasingly reflect the drifted, unstated values rather than the ones the organization would defend publicly — a direct, significant quality risk.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from values drift alone, absent a specific violated policy.",
            ),
        },
    ),
    "groundhog_day": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="Watching the same avoidable mistake recur without correction erodes confidence in leadership and may drive departures — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Recurring mistakes consume rework time, a moderate rather than singular cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Lack of a lessons-learned mechanism produces moderate decision-quality drag on future instances of the same problem.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Depending on the nature of the recurring mistake, a documented pattern of repeat failures can become relevant in a negligence-adjacent claim — a secondary, contingent risk.",
            ),
        },
    ),
    "human_displacement_anxiety": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="Anxiety about being displaced is a well-documented antecedent of voluntary turnover intent in organizational psychology, independent of whether the anxiety is ever acted on by the organization — anxious employees are measurably less likely to stay, which supports a direct score on its own terms rather than through this state's specific description.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="The description doesn't point to a direct output-level effect — the impact is described as engagement and decision-making, not raw productivity.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="The state's own definition names decision-making as directly affected by this anxiety, alongside engagement — a workforce operating under sustained displacement anxiety makes measurably worse or more risk-averse calls, a direct, significant effect regardless of the organization's actual automation plans.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from workforce anxiety alone.",
            ),
        },
    ),
    "identity_erosion": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="The state's own definition names retention and recruiting as where this shows up first — a direct, primary cost.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="No direct link to day-to-day output — the effect is external-facing (recruiting) and retention, not internal productivity.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="A blurred sense of organizational identity can produce moderate inconsistency in decisions that should reflect 'who we are,' though this is diffuse.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from identity ambiguity alone.",
            ),
        },
    ),
    "invisible_burnout": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="The cost surfaces later, all at once, as a resignation that looks sudden but wasn't — a direct, named retention cost by definition.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="The state's own definition is that output looks fine — by design, this doesn't register as a productivity problem until it's too late.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Burned-out people nearing a breaking point may make moderately worse decisions before the resignation, though this isn't the primary signal.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Sudden, unexplained resignations from burnout can carry secondary exposure if they correlate with unaddressed workload complaints on record.",
            ),
        },
    ),
    "leadership_deafness": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who've stopped believing leadership has an accurate picture may disengage from a leadership team they see as out of touch — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Decisions made on inaccurate information waste effort correcting course later, a moderate rather than acute cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions at the top are being made on a version of reality the people closest to the work don't recognize — a direct, significant quality failure.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from an information gap alone.",
            ),
        },
    ),
    "motivational_architecture_failure": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who no longer believe the incentive structure connects to anything real have direct reason to disengage and eventually leave.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Engagement has flattened across the board rather than in any one group — a direct, significant, organization-wide productivity cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="A demotivated workforce can produce moderately weaker decision quality broadly, though this is diffuse rather than tied to specific decisions.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from motivational failure alone.",
            ),
        },
    ),
    "narrative_lock": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People whose lived experience contradicts the official story may leave rather than continue being told they're the problem for saying so.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Energy spent maintaining an outdated narrative is energy not spent addressing the actual facts on the ground — a moderate cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="The organization can't update its own self-story even when facts contradict it — a direct, significant failure of the decision-making process itself.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from a self-narrative gap alone.",
            ),
        },
    ),
    "the_basement_standard": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="The best performers notice the gap first, and leave — the state's own definition names this, though it's specifically the best performers rather than broad turnover.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="The accepted baseline is well below what the organization would say it expects — a direct, significant output-quality gap.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Decisions about what's acceptable get made against a degraded baseline rather than the stated standard — a direct, significant quality risk.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="A documented gap between stated and enforced standards can become relevant in claims tied to inconsistent enforcement — a secondary, contingent exposure.",
            ),
        },
    ),
    "the_broken_compass": StateMultiplierEntry(
        multiplier=0.21666666666666667,
        raw_score=5,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who watch the organization consistently fail to act on its own stated direction may lose confidence and leave — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Strategic clarity without follow-through produces moderate frustration and wasted planning effort rather than a direct output collapse.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="The gap isn't a knowledge problem, it's a courage problem, and it shows up at exactly the moments that matter most — a direct, significant failure at the highest-stakes decisions.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from strategic follow-through failure alone.",
            ),
        },
    ),
    "the_burned_credibility": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who've watched leadership announce and not deliver before have direct reason to discount the organization's future and leave.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="Every new initiative starts already discounted by the audience it needs to buy in, a direct, significant cost to adoption and execution.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="This isn't a decision-quality problem — the decisions themselves may be sound; the cost is in how they're received, not how they're made.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from broken internal promises alone.",
            ),
        },
    ),
    "the_culture_that_wasnt": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="New hires discover the gap almost immediately, before they've built enough tenure to rationalize it — a direct, front-loaded retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Early disillusionment can produce moderate disengagement before someone either adjusts or leaves.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="New hires operating on a mismatched mental model of the organization may make moderately miscalibrated decisions early on.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from a hiring-pitch mismatch alone, absent specific misrepresentation claims.",
            ),
        },
    ),
    "the_diversity_ceiling": StateMultiplierEntry(
        multiplier=0.08333333333333334,
        raw_score=1,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="People below the ceiling can see exactly where it sits, which may contribute to attrition among those affected, though it's a secondary rather than universal effect.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="No direct link to day-to-day output — the pattern shows up in advancement outcomes, not current productivity.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="This isn't a decision-quality problem in the moment — it's a cumulative outcome pattern over many individual decisions.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="A stalled-representation pattern is disparate-impact-adjacent territory, though softer than a policy with clearly documented differential treatment — a real but secondary exposure.",
            ),
        },
    ),
    "the_inside_track": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People outside the favored channel who can name the pattern specifically have direct reason to leave for a more merit-based environment.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Talent outside the inside track may withhold full effort once they conclude advancement doesn't track performance — a moderate cost.",
            ),
            "decision_quality": StateCriterionScore(
                score=0,
                rationale="This isn't primarily a decision-quality problem — the advancement decisions may be locally coherent, just not on the stated criteria.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Favoritism in advancement can shade into disparate-treatment exposure depending on whether the favored group correlates with a protected characteristic — a secondary, contingent risk.",
            ),
        },
    ),
    "the_unlocked_door": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Lapsed security or safety practices signal to employees that it may be unwise or unsafe to stay — perceived organizational safety/security climate is a documented driver of turnover intention, giving this a direct, if moderate, retention effect rather than a diffuse or invented one.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Lapsed security/safety practices carry contingent operational downtime risk — if an incident occurs (theft, injury, breach), the resulting disruption is a real, direct productivity cost, though moderate rather than significant since it's realized only if the incident actually happens, not an active day-to-day drag.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions continue to assume a level of security/safety readiness the organization no longer actually has — a moderate quality gap.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Outdated security/safety practices carry real but currently-dormant legal exposure until an actual incident occurs — moderate, contingent.",
            ),
        },
    ),
    "the_unreported_hazard": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="People who've learned reporting doesn't help and might cost them something may disengage, a secondary rather than primary retention effect.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="No direct link to day-to-day productivity — the cost is concentrated in safety and legal, not output.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Leadership makes decisions without accurate safety information reaching them — a direct, significant quality failure with potentially severe consequences.",
            ),
            "legal": StateCriterionScore(
                score=2,
                rationale="Unreported safety hazards are close to textbook OSHA/negligence exposure once any incident occurs and the reporting gap becomes discoverable — direct, significant.",
            ),
        },
    ),
    "the_untouchable": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Exemption from standards removes the guardrails that would normally check reckless behavior — the untouchable person's unconstrained conduct (volatility, unfair treatment, erratic decisions) directly drives departures among the people who have to work around them, not just general disillusionment from watching favoritism.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Exemption from standards can produce moderate disengagement among people held to the standard the exempted person isn't.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions involving the untouchable person may bend around their exemption, a moderate distortion of otherwise-normal decision-making.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="For the modal instance, the exemption is hidden and cultural — an unwritten pass on ordinary standards rather than a waived legal one — carrying real but moderate exposure. Higher-risk edge cases (harassment, safety, fraud) exist and would justify a 2, but are the exception, not the typical case, per the modal-instance scoring rule.",
            ),
        },
    ),
    "the_wrong_reward": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="People who don't fit the rewarded behavior pattern may become frustrated, a secondary retention effect.",
            ),
            "productivity": StateCriterionScore(
                score=2,
                rationale="People are responding rationally to the real incentives rather than the stated ones, which means effort is being spent on the wrong things — a direct, significant misallocation.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions about who gets recognized/promoted reflect the wrong incentive structure, a moderate distortion rather than an acute single failure.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="If the wrongly-rewarded behavior touches a protected area (e.g., overtime culture, exclusionary conduct), it can carry secondary compliance exposure.",
            ),
        },
    ),
    "wellbeing_theater": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Employees who see through performative wellbeing programming may become more cynical and somewhat more likely to leave, a secondary effect.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Time and budget spent on programming that doesn't address root causes is a moderate, diffuse cost rather than an acute one.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Leadership may believe the underlying problem is being addressed when it isn't, a moderate decision-quality gap about the organization's own condition.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from ineffective wellbeing programming alone.",
            ),
        },
    ),
    "what_nobody_says": StateMultiplierEntry(
        multiplier=0.18333333333333335,
        raw_score=4,
        criteria={
            "turnover": StateCriterionScore(
                score=2,
                rationale="People who've learned what happens to whoever speaks up may eventually leave rather than continue carrying a problem they can't voice — a direct retention cost.",
            ),
            "productivity": StateCriterionScore(
                score=1,
                rationale="Energy spent managing around an unspoken known problem is a moderate, ongoing drag on output.",
            ),
            "decision_quality": StateCriterionScore(
                score=1,
                rationale="Decisions get made without the accurate information that exists but isn't being raised — a moderate quality gap.",
            ),
            "legal": StateCriterionScore(
                score=0,
                rationale="No identifiable compliance category from organizational silence alone, absent a specific underlying violation.",
            ),
        },
    ),
    "the_inner_circle": StateMultiplierEntry(
        multiplier=0.15000000000000002,
        raw_score=3,
        criteria={
            "turnover": StateCriterionScore(
                score=1,
                rationale="Those excluded from the protected in-group face reduced advancement and visibility, driving moderate voluntary attrition; the in-group itself is insulated, limiting the signal's reach.",
            ),
            "productivity": StateCriterionScore(
                score=0,
                rationale="Decisions within the circle can be efficient on their own terms even when damaging elsewhere; no direct organizational output drag scored.",
            ),
            "decision_quality": StateCriterionScore(
                score=2,
                rationale="Core to the state — decisions are consequence-shielded and groupthink-protected by design, the clearest and strongest signal of the three criteria.",
            ),
            "legal": StateCriterionScore(
                score=1,
                rationale="Exclusionary in-group dynamics create moderate disparate-treatment and retaliation exposure for those shut out, though the state's core mechanism is protective self-dealing rather than a direct regulatory or compliance violation.",
            ),
        },
    ),
}

_STATE_MULTIPLIER_CRITERIA_KEYS = {"turnover", "productivity", "decision_quality", "legal"}
_ATTRITIONAL_CRITERIA_KEYS = ("turnover", "productivity", "decision_quality")
# "legal" remains a required key on every state's criteria dict -- its score
# is still recorded (needed by the separate Legal/Compliance mechanism-aware
# design, prompts/friction-tax-legal-compliance-methodology.md) but is no
# longer part of this rubric's raw_score sum or its multiplier -- see
# prompts/friction-tax-state-multiplier-methodology.md.

for _sid, _entry in STATE_MULTIPLIERS.items():
    assert set(_entry.criteria.keys()) == _STATE_MULTIPLIER_CRITERIA_KEYS, (
        f"{_sid}: criteria keys {set(_entry.criteria.keys())} != "
        f"{_STATE_MULTIPLIER_CRITERIA_KEYS}"
    )
    _criteria_sum = sum(_entry.criteria[_k].score for _k in _ATTRITIONAL_CRITERIA_KEYS)
    assert _criteria_sum == _entry.raw_score, (
        f"{_sid}: raw_score {_entry.raw_score} != sum of the 3 attritional "
        f"criteria scores {_criteria_sum} (legal excluded from this sum)"
    )
    for _cname, _c in _entry.criteria.items():
        assert 0 <= _c.score <= 2, f"{_sid}.{_cname}: score {_c.score} out of [0, 2]"
    assert 0.05 <= _entry.multiplier <= 0.25, (
        f"{_sid}: multiplier {_entry.multiplier} out of [0.05, 0.25]"
    )
del _sid, _entry, _criteria_sum, _cname, _c


_R_MIN: float = 0.0
_R_MAX: float = 6.0
_FRACTION_MIN: float = 0.05
_FRACTION_MAX: float = 0.25


# -- Multi-state compounding (Steps 1-3) -------------------------------------------
# prompts/friction-tax-multistate-compounding-methodology.md. K=0.05 CLOSED
# (Pete's final decision) -- breadth range [1, 3], Legal/Compliance fully
# split out (see prompts/friction-tax-legal-compliance-methodology.md), not
# part of this loop.

_MULTI_CHANNEL_SEVERITY_LOADING_K: float = 0.05


def _attritional_fraction(raw_total: float) -> float:
    """
    Frozen [0, 6] -> [0.05, 0.25] linear mapping (Option A rescale,
    prompts/friction-tax-state-multiplier-methodology.md). R_min/R_max are
    fixed theoretical constants, not derived from observed data, so this
    same function serves both a single state's own raw_score (0-6) and a
    multi-state combined_raw_total (Step 1), which can exceed 6 -- in
    which case this extrapolates linearly past 0.25 rather than clamping,
    intentionally.
    """
    return _FRACTION_MIN + (_FRACTION_MAX - _FRACTION_MIN) * ((raw_total - _R_MIN) / (_R_MAX - _R_MIN))

# -- Core computation ---------------------------------------------------------------

def compute_friction_tax(
    state_ids: list[str],
    severity_tier: str,
    org_size: int,
    industry: str,
    org_type: str,
) -> dict:
    """
    Compute a friction tax estimate for a state cluster.

    Parameters:
      state_ids:     list of identified state IDs (from identified_states)
      severity_tier: "Emerging" | "Entrenched" | "Endemic"
      org_size:      IntakeData.headcount value (a precise int, e.g. 150 --
                     resolved internally to its "100-249" bucket via
                     resolve_headcount_bucket() before any lookup)
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
    aggregate each of the 3 attritional criteria across identified states
    via anchor-plus-diminishing-layers (Step 1, geometric decay), (4) map
    the combined criterion total through the same frozen [0, 6] -> [0.05,
    0.25] mapping used for a single state (Step 2, extrapolates linearly
    past 0.25 for combined totals above 6), (5) apply
    multi_channel_severity_loading (Step 3, K=0.05, breadth 1-3, forced to
    1.0 when exactly one state is identified), (6) apply severity_scalar
    (unchanged, LOCKED), (7) low = adjusted_baseline * combined_multiplier
    * multi_channel_severity_loading * severity_scalar, high = low * 1.4
    (unchanged, LOCKED). See prompts/friction-tax-multistate-compounding-
    methodology.md for the full Steps 1-3 design.

    Returns low=None, high=None, calibration_complete=False when any
    required value is missing or the (org_size, industry) pair, org_type,
    or a state_id isn't a recognized key. As of this pass, all three
    calibration axes (PAYROLL_BASELINE_GRID, ORG_TYPE_SCALARS,
    STATE_MULTIPLIERS) are fully populated, so calibration_complete now
    returns True for any real, recognized combination.
    """
    org_size = resolve_headcount_bucket(org_size)
    grid_entry = PAYROLL_BASELINE_GRID.get((org_size, industry))
    payroll_floor = grid_entry.payroll_floor_annual if grid_entry is not None else None
    org_type_entry = ORG_TYPE_SCALARS.get(org_type)
    org_type_scalar = org_type_entry.scalar if org_type_entry is not None else None
    severity_scalar = SEVERITY_SCALAR.get(severity_tier, _DEFAULT_SEVERITY_SCALAR)

    state_entries = [STATE_MULTIPLIERS.get(sid) for sid in state_ids]

    calibration_complete = (
        payroll_floor is not None
        and org_type_scalar is not None
        and bool(state_ids)
        and all(e is not None for e in state_entries)
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

    # Step 1 (Factor A) -- per-criterion aggregation across identified
    # states, anchor-plus-diminishing-layers, geometric decay w_i = 0.5**(i-1).
    # With exactly one identified state this collapses to that state's own
    # criterion scores untouched (single term, weight 1.0) -- verified by
    # tools/test_friction_tax.py's continuity assertions, not just assumed.
    combined_criterion_scores = {
        k: sum(
            (0.5 ** i) * score
            for i, score in enumerate(
                sorted((e.criteria[k].score for e in state_entries), reverse=True)  # type: ignore[union-attr]
            )
        )
        for k in _ATTRITIONAL_CRITERIA_KEYS
    }
    combined_raw_total = sum(combined_criterion_scores.values())

    # Step 2 -- map the combined criterion profile to a payroll-fraction
    # multiplier via the same frozen [0, 6] -> [0.05, 0.25] mapping used
    # for a single state (prompts/friction-tax-state-multiplier-
    # methodology.md). Extrapolates linearly beyond 0.25 if combined_raw_total
    # exceeds 6 -- intentional, per that doc's frozen-range design.
    combined_multiplier = _attritional_fraction(combined_raw_total)

    # Step 3 (Factor B) -- multi-channel severity loading. N=1 guard: with
    # exactly one identified state, loading MUST be exactly 1.0 regardless
    # of how many criteria that state's own scores touch -- explicit, not
    # inferred from the breadth formula, so single-state continuity holds
    # by construction rather than by coincidence.
    breadth = sum(1 for v in combined_criterion_scores.values() if v > 0)
    if len(state_entries) == 1:
        multi_channel_severity_loading = 1.0
    else:
        multi_channel_severity_loading = 1.0 + _MULTI_CHANNEL_SEVERITY_LOADING_K * (breadth - 1)

    low = round(
        adjusted_baseline * combined_multiplier * multi_channel_severity_loading * severity_scalar,
        2,
    )
    high = round(low * 1.4, 2)

    return {
        "low": low,
        "high": high,
        "currency": "USD",
        "org_size_label": org_size,
        "severity_scalar": severity_scalar,
        "calibration_complete": True,
    }


# -- Legal/Compliance -- mechanism-aware exposure (Addenda 1-10) ----------------
# prompts/friction-tax-legal-compliance-methodology.md. Separate from the
# attritional compute_friction_tax() above -- Legal/Compliance scales by
# mechanism (and for Cluster 4, org_type/headcount), not by payroll
# baseline. Standalone function, NOT wired into compute_friction_tax()'s
# return dict, engine/contract.py, or web/lib/types.ts -- that
# integration is separately scoped. Jurisdictional multiplier logic
# (California FEHA/PAGA overrides, OSHA State Plan variation, Addenda
# 6-9) is explicitly NOT implemented here -- deferred per Addendum 9.

# -- Industry non-exempt ratio ----------------------------------------------------
# KNOWN CITATION-ACCURACY GAP, not a resolved sourcing question. The 9
# original entries below (all industries except Construction and
# Transportation & Warehousing) arrived in a single commit (0912a30)
# already citing "BLS CPS cpsaat18c.pdf and cpsaat45.pdf (hourly-paid
# workers by industry)" as their source. Confirmed this session:
# cpsaat45.pdf is NOT a general hourly-paid-by-industry table -- it is
# specifically "Wage and salary workers paid hourly rates with earnings
# at or below the prevailing Federal minimum wage by occupation and
# industry" (a sub-minimum-wage table, national aggregate ~1.0%),
# confirmed consistent across every annual edition checked (2016-2025) --
# no year where this table number meant something else. The 9 ratios
# below (0.557, 0.556, 0.662, etc.) do not match that sub-minimum-wage
# concept at all -- they match the general "percent of workers paid
# hourly" concept instead. Git history shows the ratios and this
# citation arrived together already in final form -- no earlier draft or
# intermediate work product (pulled figures, a numerator/denominator
# calculation) survives anywhere in this repo to confirm what the real
# original source actually was. The values are RETAINED, not
# recomputed, because they independently corroborate against real BLS
# published aggregates: "Other": 0.556 nearly exactly matches BLS's 2024
# national "percent paid hourly" figure of 55.6%. Feeds Cluster 3's
# affected-subgroup calculation: headcount_midpoint x
# INDUSTRY_NON_EXEMPT_RATIO[industry].

INDUSTRY_NON_EXEMPT_RATIO: dict[str, float] = {
    "Manufacturing & Industrial": 0.557,
    "Healthcare & Life Sciences": 0.560,
    "Financial Services": 0.285,
    "Professional Services": 0.227,
    "Retail & Hospitality": 0.662,
    # BLS "Information" sector -- narrower than colloquial "Technology,"
    # likely understates the real ratio.
    "Technology": 0.280,
    # Blends CPS + CES surveys, softer confidence than the others.
    "Government & Public Sector": 0.44,
    # Education component only -- "Nonprofit" is genuinely untracked by
    # BLS (confirmed via a 2024 Senate oversight letter to DOL), not a
    # research gap on this project's end.
    "Nonprofit & Education": 0.135,
    # BLS CPS, 2025: 5,655,000 hourly-paid workers (FRED
    # LEU0204837400A, "Weekly and Hourly Earnings from the CPS" release)
    # / 10,210,000 total at work (cpsaat21.htm, "People at work in
    # nonagricultural industries by class of worker," 2025 annual
    # average). Both figures same survey family (CPS household survey),
    # matching population (private wage and salary workers, Construction
    # industry). Closely corroborates existing Manufacturing figure
    # (0.557). Note: 2025 CPS annual averages are an 11-month average
    # excluding October (federal shutdown) and reflect a mid-year NAICS
    # reclassification -- not strictly comparable to prior years per
    # BLS's own caveat on this table.
    "Construction": 0.554,
    # BLS CPS, 2025: 3,861,000 hourly-paid workers, Transportation &
    # Warehousing specifically (FRED LEU0204838200A) / 9,156,000 total
    # at work, "Transportation and utilities" COMBINED (cpsaat21.htm,
    # 2025 -- this CPS table does not break Transportation & Warehousing
    # out separately from Utilities at any point in its published
    # history, confirmed across multiple years checked this session;
    # this is a genuine limitation of the published table, not a
    # citation gap). KNOWN LIMITATION: this ratio's denominator is
    # broader than its numerator's industry (includes Utilities
    # workers, who are not part of Transportation & Warehousing), which
    # structurally understates the true Transportation & Warehousing-
    # specific ratio. Flagged explicitly, not silently approximated --
    # if this materially affects Cluster 3 exposure figures for
    # Transportation & Warehousing orgs, it should be revisited with CPS
    # microdata directly rather than a published aggregate table.
    "Transportation & Warehousing": 0.422,
    # Real national aggregate, BLS 2025.
    "Other": 0.556,
}

assert set(INDUSTRY_NON_EXEMPT_RATIO.keys()) == set(INDUSTRIES), (
    "INDUSTRY_NON_EXEMPT_RATIO keys must match INDUSTRIES exactly"
)


# -- Mechanism classification -----------------------------------------------------
# All 30 Legal-scoring states, classified into 5 mechanism clusters
# (prompts/friction-tax-legal-compliance-methodology.md, Addenda 1, 2,
# 4). Each state's "legal" score (used below for interpolation/tier
# selection) is NOT duplicated here -- it's read directly from
# STATE_MULTIPLIERS[state_id].criteria["legal"].score, already recorded
# above.

LEGAL_COMPLIANCE_CLUSTER: dict[str, int] = {
    # Cluster 1 -- Individual/isolated claim (4 states)
    "invisible_performance_management": 1,
    "the_paper_tiger": 1,
    "built_to_fail": 1,
    "the_untouchable": 1,
    # Cluster 2 -- Class/systemic discrimination (11 states)
    "disparate_impact_architecture": 2,
    "the_arbitrary_standard": 2,
    "the_pay_fog": 2,
    "pay_exposure": 2,
    "the_diversity_ceiling": 2,
    "the_inside_track": 2,
    "the_unexamined_algorithm": 2,
    "sequential_decision_blindness": 2,
    "the_tolerated_violation": 2,
    "the_wrong_reward": 2,
    "distributed_culture_fragmentation": 2,
    # Cluster 3 -- Wage-and-hour (2 states)
    "cultural_overtime": 3,
    "compression_crisis": 3,
    # Cluster 4 -- Whistleblower/regulatory, org_type-gated at compute
    # time into 4a/4b/4c (6 states)
    "hr_capture": 4,
    "heard_and_ignored": 4,
    "the_policy_lag": 4,
    "the_basement_standard": 4,
    "dueling_narratives": 4,
    "the_suppression_filter": 4,
    # Cluster 5 -- Safety/regulatory (7 states)
    "the_unreported_hazard": 5,
    "the_unlocked_door": 5,
    "invisible_burnout": 5,
    "the_undefined_role": 5,
    "the_unsolved_problem": 5,
    "groundhog_day": 5,
    "the_exposed": 5,
}

_LEGAL_CLUSTER_COUNTS_EXPECTED = {1: 4, 2: 11, 3: 2, 4: 6, 5: 7}

assert len(LEGAL_COMPLIANCE_CLUSTER) == 30, (
    f"LEGAL_COMPLIANCE_CLUSTER must classify all 30 Legal-scoring states, "
    f"found {len(LEGAL_COMPLIANCE_CLUSTER)}"
)
for _cluster_num, _expected_count in _LEGAL_CLUSTER_COUNTS_EXPECTED.items():
    _actual_count = sum(1 for v in LEGAL_COMPLIANCE_CLUSTER.values() if v == _cluster_num)
    assert _actual_count == _expected_count, (
        f"Cluster {_cluster_num}: expected {_expected_count} states, found {_actual_count}"
    )
for _lc_sid, _lc_cluster in LEGAL_COMPLIANCE_CLUSTER.items():
    assert _lc_sid in STATE_MULTIPLIERS, (
        f"LEGAL_COMPLIANCE_CLUSTER references unknown state {_lc_sid!r}"
    )
    _lc_score = STATE_MULTIPLIERS[_lc_sid].criteria["legal"].score
    assert _lc_score in (1, 2), (
        f"{_lc_sid}: classified into Cluster {_lc_cluster} but its recorded "
        f"'legal' score is {_lc_score}, not in {{1, 2}} -- Addendum 10's "
        f"interpolation formula requires the real 1-2 domain"
    )
del _cluster_num, _expected_count, _actual_count, _lc_sid, _lc_cluster, _lc_score


# -- Dollar-curve anchors ----------------------------------------------------------
# Addendum 10: fraction(score) = floor * (ceiling / floor) ** (score - 1),
# score in {1, 2}. score=1 -> floor exactly, score=2 -> ceiling exactly.
# Applies to Clusters 1, 4a, 4b, 5. Cluster 2 uses its own discrete
# tier-selection mechanism (Addendum 2), not this formula.

@dataclass(frozen=True)
class LegalDollarCurve:
    """One cluster's (or sub-track's) floor/ceiling for Addendum 10's formula."""
    floor: float
    ceiling: float


def _legal_score_fraction(curve: LegalDollarCurve, score: int) -> float:
    return curve.floor * (curve.ceiling / curve.floor) ** (score - 1)


class LegalPricingStatus(Enum):
    """
    Distinguishes why a given state did or didn't contribute a dollar
    range, so callers can tell "real exposure, genuinely unpriced" apart
    from "not applicable at all" and from "a data problem" -- all three
    previously collapsed to a bare None.
    """
    PRICED = "priced"
    NOT_APPLICABLE = "not_applicable"
    QUALITATIVE_ONLY = "qualitative_only"
    DATA_INTEGRITY_GAP = "data_integrity_gap"


@dataclass(frozen=True)
class LegalPricingResult:
    """One state's pricing outcome. dollar_range is populated only when
    status is PRICED."""
    status: LegalPricingStatus
    dollar_range: Optional[tuple[float, float]]


@dataclass(frozen=True)
class LegalCurveLookup:
    """Result of resolving a Cluster 4 sub-track curve. curve is
    populated only when status is PRICED."""
    curve: Optional[LegalDollarCurve]
    status: LegalPricingStatus


# Cluster 1 -- Individual/isolated claim (Addendum 1).
_CLUSTER_1_CURVE = LegalDollarCurve(floor=50_000.0, ceiling=450_000.0)

# Cluster 2 -- Class/systemic discrimination, two discrete tiers (Addendum 2).
# NOT the log-scale formula -- score selects a tier outright.
_CLUSTER_2_TIER_2A = (1_800.0, 2_500.0)   # compensatory-only, score=1
_CLUSTER_2_TIER_2B = (25_000.0, 31_000.0)  # punitive-inclusive, score=2

# Cluster 3 -- Wage-and-hour, per-worker rates (Addendum 4, locked).
# Score modulates affected-worker SCOPE (Addendum 10's 25%/75%, design
# judgment, not sourced), not these two rates.
_CLUSTER_3_ADMIN_RATE_PER_WORKER = 1_465.0
_CLUSTER_3_LITIGATION_RATE_PER_WORKER = 2_930.0
_CLUSTER_3_SCOPE_FRACTION_BY_SCORE: dict[int, float] = {1: 0.25, 2: 0.75}

# Cluster 4a -- SEC/Dodd-Frank, org_type == "Publicly traded" (Addendum 5,
# ceiling corrected in Addendum 10 to the real average-total-organizational-
# sanction midpoint, NOT the $279M historic outlier).
_CLUSTER_4A_CURVE = LegalDollarCurve(floor=25_000.0, ceiling=33_000_000.0)

# Cluster 4b -- general private-sector retaliation (Addendum 5's real
# Title VII/ADA statutory bracket table, 42 U.S.C. Sec 1981a(b)(3)).
# 100-249's ceiling is the midpoint of its own $50K-$100K straddle range,
# per Addendum 10's stated consistency convention with Cluster 4a's
# midpoint approach -- flagged there as a design choice, not something
# Pete specified for this exact sub-case.
_CLUSTER_4B_FLOOR = 25_000.0
_CLUSTER_4B_CEILING_BY_HEADCOUNT: dict[str, float] = {
    "Under 25": 50_000.0,
    "25-99": 50_000.0,
    "100-249": 75_000.0,
    "250-499": 200_000.0,
    "500-999": 300_000.0,
    "1000+": 300_000.0,
}

# Cluster 5 -- Safety/regulatory, statutory-max curve ONLY (Addendum 10 --
# actual-average curve deferred alongside the paused jurisdictional
# research, Addendum 9).
_CLUSTER_5_CURVE = LegalDollarCurve(floor=16_550.0, ceiling=165_514.0)


def _cluster_4_curve_for_org_type(
    org_type: str, org_size: str
) -> LegalCurveLookup:
    """
    Addendum 5's three org_type-gated sub-tracks. Status is
    QUALITATIVE_ONLY for "Government" (4c) -- genuinely no dollar figure
    (thin MSPB data), a real, expected outcome, not a data problem.
    Status is DATA_INTEGRITY_GAP for any unrecognized org_size in the 4b
    bracket table -- that should never happen against real IntakeData
    values, so it signals something is wrong, unlike the Government
    case. "PE or VC-backed" defaults to 4b -- the possible 4a edge case
    (a registered investment adviser/broker-dealer) isn't determinable
    from org_type alone, per Addendum 5, and isn't resolved here.
    """
    if org_type == "Publicly traded":
        return LegalCurveLookup(curve=_CLUSTER_4A_CURVE, status=LegalPricingStatus.PRICED)
    if org_type == "Government":
        return LegalCurveLookup(curve=None, status=LegalPricingStatus.QUALITATIVE_ONLY)
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)
    if ceiling is None:
        return LegalCurveLookup(curve=None, status=LegalPricingStatus.DATA_INTEGRITY_GAP)
    return LegalCurveLookup(
        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=ceiling),
        status=LegalPricingStatus.PRICED,
    )


def _cluster_3_affected_workers(org_size: str, industry: str, score: int) -> float:
    """
    Addendum 4 (locked scope-modulated design) + Addendum 10 (25%/75%
    scope percentages). Base subgroup = headcount midpoint x industry
    non-exempt ratio; score narrows/broadens the affected slice.
    """
    midpoint_entry = HEADCOUNT_MIDPOINTS.get(org_size)
    if midpoint_entry is None or midpoint_entry.employees_per_firm is None:
        return 0.0
    ratio = INDUSTRY_NON_EXEMPT_RATIO.get(industry)
    if ratio is None:
        return 0.0
    subgroup = midpoint_entry.employees_per_firm * ratio
    scope_fraction = _CLUSTER_3_SCOPE_FRACTION_BY_SCORE.get(score, 0.0)
    return subgroup * scope_fraction


def _single_state_legal_pricing(
    state_id: str,
    org_size: str,
    industry: str,
    org_type: str,
) -> LegalPricingResult:
    """
    One Legal-scoring state's pricing outcome in isolation. status is
    NOT_APPLICABLE (dollar_range=None) if the state isn't Legal-scoring
    at all or its "legal" score is 0 (no exposure) -- both silent,
    unchanged from the prior bare-None behavior. For Cluster 4, status
    is forwarded directly from _cluster_4_curve_for_org_type()
    (QUALITATIVE_ONLY for Government, DATA_INTEGRITY_GAP for an
    unrecognized org_size), distinguishing real-but-unpriced exposure
    from a genuine data gap -- previously both collapsed to None here
    too.
    """
    cluster = LEGAL_COMPLIANCE_CLUSTER.get(state_id)
    if cluster is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)
    entry = STATE_MULTIPLIERS.get(state_id)
    if entry is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)
    score = entry.criteria["legal"].score
    if score == 0:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)

    if cluster == 1:
        v = _legal_score_fraction(_CLUSTER_1_CURVE, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))
    if cluster == 2:
        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r)
    if cluster == 3:
        affected = _cluster_3_affected_workers(org_size, industry, score)
        r = (
            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,
            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,
        )
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r)
    if cluster == 4:
        lookup = _cluster_4_curve_for_org_type(org_type, org_size)
        if lookup.curve is None:
            return LegalPricingResult(status=lookup.status, dollar_range=None)
        v = _legal_score_fraction(lookup.curve, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))
    if cluster == 5:
        v = _legal_score_fraction(_CLUSTER_5_CURVE, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))
    return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)


def _legal_exposure_band(low: Optional[float]) -> Optional[str]:
    """
    Addendum 11's qualitative severity band for the shareable output --
    no dollar figure exposed publicly (a specific number in a shareable
    artifact could function as documented notice of a contingent
    liability). Applied to "low" only. Boundaries are a first pass, not
    yet stress-tested against real multi-cluster worked examples
    (Addendum 11's own open item #3) -- treat as provisional until that
    check runs.
    """
    if low is None:
        return None
    if low < 100_000.0:
        return "Minor"
    if low < 500_000.0:
        return "Moderate"
    if low < 2_000_000.0:
        return "Elevated"
    return "Significant"


# Architecture note (confirmed via a real worked-example plausibility
# pass, 2026-08-04, Gemini structural review): this function's dollar
# output is deliberately headcount-independent -- Legal/Compliance
# claims don't scale with org size the way attritional costs do
# (Addendum 1's original rationale for rejecting a payroll-fraction
# mapping here). One real consequence, confirmed with actual numbers,
# not theoretical: a severe multi-cluster profile on a very small org
# (e.g. "Under 25" headcount) can produce a low figure that exceeds
# that org's own total payroll baseline -- by a wide margin at the
# extreme tail (observed up to ~2.5x payroll stacking every real
# Legal-scoring state at once, and far higher for the structurally
# valid but practically unlikely combination of a tiny headcount with
# org_type == "Publicly traded", since Cluster 4a's ceiling is not
# headcount-scaled either). This is an accepted, understood property
# of the design, not a bug -- Legal/Compliance is priced by mechanism
# and severity, not by ability to pay. Cluster 4's org_type gating
# (Addendum 5) is the other half of this picture: the SAME severity
# profile can differ by >20x between "Publicly traded" (Cluster 4a,
# SEC-anchored, ceiling $33M) and every other org_type (Cluster 4b,
# Title VII-capped, max $300K) -- also intentional, and the main
# driver of when the "Significant" band (_legal_exposure_band()
# above) is actually reachable in practice for a realistic profile.
def compute_legal_compliance_exposure(
    state_ids: list[str],
    org_size: int,
    industry: str,
    org_type: str,
) -> dict:
    """
    Cross-state aggregation (Addendum 3): within-cluster geometric decay
    (w_i = 0.5**(i-1), reusing the attritional Step 1 shape -- ranked by
    each state's own low end, highest first), across-cluster simple
    addition (no breadth premium -- Addendum 3's explicit, justified
    departure from the attritional design's Factor B). N=1 guard: exactly
    one Legal-scoring state in the profile collapses the output to that
    state's own individual range, no aggregation logic engaged.

    Jurisdictional multipliers (California FEHA/PAGA overrides, OSHA
    State Plan variation, Addenda 6-9) are NOT applied here -- deferred,
    per Addendum 9. Cluster 5 uses the statutory-max curve only (Addendum
    10) -- actual-average deferred alongside that same paused research.

    NOT_APPLICABLE states (not Legal-scoring, or a "legal" score of 0)
    are silently excluded, unchanged from before this status system
    existed. QUALITATIVE_ONLY states (real exposure, genuinely no dollar
    figure -- Cluster 4c/Government) and DATA_INTEGRITY_GAP states (a
    lookup that should have succeeded didn't) are both collected into
    unpriced_state_ids; a DATA_INTEGRITY_GAP additionally logs a
    warning, since it signals a real data problem rather than an
    intentional design outcome. The N=1 guard above triggers on exactly
    one PRICED state -- QUALITATIVE_ONLY/DATA_INTEGRITY_GAP states never
    enter the aggregation, regardless of how many are also present.

    Returns {"low": float | None, "high": float | None, "currency": "USD",
    "has_unpriced_conditions": bool, "unpriced_state_ids": list[str]}.
    low/high are None if no identified state carries real, priceable
    Legal/Compliance exposure -- has_unpriced_conditions can still be
    True in that case if every identified Legal-scoring state was
    QUALITATIVE_ONLY/DATA_INTEGRITY_GAP.
    """
    org_size = resolve_headcount_bucket(org_size)
    per_state_ranges: dict[str, tuple[float, float]] = {}
    unpriced_state_ids: list[str] = []
    for sid in state_ids:
        result = _single_state_legal_pricing(sid, org_size, industry, org_type)
        if result.status == LegalPricingStatus.PRICED:
            per_state_ranges[sid] = result.dollar_range
        elif result.status == LegalPricingStatus.QUALITATIVE_ONLY:
            unpriced_state_ids.append(sid)
        elif result.status == LegalPricingStatus.DATA_INTEGRITY_GAP:
            unpriced_state_ids.append(sid)
            _logger.warning(
                "Legal/Compliance pricing data-integrity gap for state_id=%r "
                "(org_size=%r, industry=%r, org_type=%r) -- expected a "
                "priceable curve but none was found",
                sid, org_size, industry, org_type,
            )
        # NOT_APPLICABLE: silently excluded, unchanged from before.

    has_unpriced_conditions = bool(unpriced_state_ids)

    if not per_state_ranges:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "band": _legal_exposure_band(None),
            "has_unpriced_conditions": has_unpriced_conditions,
            "unpriced_state_ids": unpriced_state_ids,
        }

    if len(per_state_ranges) == 1:
        low, high = next(iter(per_state_ranges.values()))
        rounded_low = round(low, 2)
        return {
            "low": rounded_low,
            "high": round(high, 2),
            "currency": "USD",
            "band": _legal_exposure_band(rounded_low),
            "has_unpriced_conditions": has_unpriced_conditions,
            "unpriced_state_ids": unpriced_state_ids,
        }

    by_cluster: dict[int, list[tuple[float, float]]] = {}
    for sid, r in per_state_ranges.items():
        by_cluster.setdefault(LEGAL_COMPLIANCE_CLUSTER[sid], []).append(r)

    total_low = 0.0
    total_high = 0.0
    for ranges in by_cluster.values():
        ranges_sorted = sorted(ranges, key=lambda r: r[0], reverse=True)
        total_low += sum((0.5 ** i) * low for i, (low, _high) in enumerate(ranges_sorted))
        total_high += sum((0.5 ** i) * high for i, (_low, high) in enumerate(ranges_sorted))

    rounded_total_low = round(total_low, 2)
    return {
        "low": rounded_total_low,
        "high": round(total_high, 2),
        "currency": "USD",
        "band": _legal_exposure_band(rounded_total_low),
        "has_unpriced_conditions": has_unpriced_conditions,
        "unpriced_state_ids": unpriced_state_ids,
    }
