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
from typing import Literal, Optional

from engine.data.jurisdiction import JURISDICTION_TABLE

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


def resolve_headcount_bucket(headcount) -> Optional[str]:
    """
    Map a precise headcount int (engine/data/intake.py's
    HEADCOUNT_FIELD_SPEC) to its HEADCOUNT_BUCKETS bucket string.
    Boundaries match the field spec's increment schedule exactly.

    Legacy string-headcount tolerance (organization_size string|number
    collapse, 2026-08-29) removed -- Redis confirmed clear of legacy
    string-bucket records before this ran, and the web layer was
    believed at the time to guarantee a real number end to end. That
    guarantee proved false: confirmed live, 2026-09-08, the self-select
    "Take the diagnostic" CTA (web/app/diagnostic/page.tsx) sends
    headcount="" unconditionally, causing a production 500 for every
    request through that path, not just ones touching Legal/Compliance
    clusters -- this function is called at the top of both
    compute_friction_tax() and compute_legal_compliance_exposure(),
    unconditionally, before any per-state logic runs.

    Returns None -- rather than raising -- when headcount isn't a real,
    comparable number (empty string, other non-numeric string, None).
    This does NOT reintroduce the removed string-to-number coercion
    above; a numeric string like "152" is still treated as
    unclassifiable, not parsed. Callers treat None as "cannot classify
    this headcount" and degrade to their own existing no-result shape
    -- see compute_friction_tax()'s calibration_complete=False branch
    and compute_legal_compliance_exposure()'s per-cluster handling,
    immediately after each of their own calls to this function.
    """
    if not isinstance(headcount, (int, float)):
        return None
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
# baseline. WIRED into engine/contract.py's private_output as of commit
# 46c1e0c (2026-08-04, "wire Legal/Compliance tail-risk exposure into
# private output") -- the comment here previously claimed the opposite
# ("NOT wired... that integration is separately scoped") for over a
# month after it stopped being true, and caused the 2026-09-05 Quarterly
# Step-Back to wrongly conclude the module was unwired; corrected here
# after independent verification against live source. As of this
# session, the returned dict also carries coverage_basis and
# has_partial_jurisdictions (see compute_legal_compliance_exposure()'s
# own docstring), distinguishing state-confirmed from federal-fallback
# coverage determinations. Jurisdictional multiplier logic (California
# FEHA/PAGA overrides, OSHA State Plan variation, Addenda 6-9) is
# explicitly NOT implemented here -- deferred per Addendum 9.

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
    status is PRICED. coverage_confidence reflects whether/how the
    state-coverage-threshold gate resolved for this specific cluster --
    "NOT_APPLICABLE" when no coverage question was ever asked (Clusters
    3, 4a, 4c, 5, and every early NOT_APPLICABLE return that doesn't
    consult jurisdiction), never None/null. partial_state_flag mirrors
    CoverageResult.partial_state_flag when the gate actually ran; False
    when coverage_confidence is "NOT_APPLICABLE", since a
    partial-jurisdiction caveat cannot apply to a determination that
    never consulted jurisdictions at all. is_floor (Phase 1,
    prompts/damages-cap-treatment-phase1-spec.md items 3/4) is True
    when the priced dollar_range reflects a generic ceiling standing in
    for a state with no real cap of its own (damages_cap_treatment ==
    "uncapped") or a flat cap that governs only a narrower damage-type
    slice than the figure implies ("state_specific_flat") -- signals
    to a future output layer that the figure should render as a floor,
    not a hard ceiling. False by default so every pre-existing
    construction site needs no change; not yet consumed by any output
    layer, same "no consumer yet" status as damages_cap_treatment
    itself before this build."""
    status: LegalPricingStatus
    dollar_range: Optional[tuple[float, float]]
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool
    is_floor: bool = False


@dataclass(frozen=True)
class LegalCurveLookup:
    """Result of resolving a Cluster 4 sub-track curve. curve is
    populated only when status is PRICED. coverage_confidence/
    partial_state_flag carry the same meaning as LegalPricingResult's
    fields of the same name -- "NOT_APPLICABLE"/False for the 4a
    (Publicly traded) and 4c (Government) early-return branches, which
    never call resolve_coverage_gate(); the real CoverageResult values
    for every 4b fallthrough branch (not-applies, DATA_INTEGRITY_GAP,
    and PRICED alike), since the gate genuinely runs for all three.
    is_floor carries the same meaning as LegalPricingResult's own field
    of that name (Phase 1, prompts/damages-cap-treatment-phase1-spec.md
    items 3/4) -- forwarded into the final LegalPricingResult by
    _single_state_legal_pricing()'s Cluster 4 branch."""
    curve: Optional[LegalDollarCurve]
    status: LegalPricingStatus
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool
    is_floor: bool = False


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


# -- State-aware coverage-threshold gate (Clusters 1, 2, 4b) --------------------
# prompts/state-coverage-threshold-design.md. Gemini-reviewed design,
# revised from an original harassment_any_size boolean into the
# extensible per-claim-type thresholds dict below. Separate mechanism
# from engine/data/jurisdiction.py's JURISDICTION_TABLE/
# resolve_jurisdiction_flags() (transparency/retaliation/procedural
# policy flags) -- zero overlap, that module is untouched by this
# design. JURISDICTION_TABLE is imported here only as the authoritative
# 50-states-plus-DC key set the PARTIAL fill-in below iterates over.

@dataclass(frozen=True)
class StateCoverageThreshold:
    """
    One state's employer-size coverage threshold(s) for anti-discrimination
    claim applicability (ADA/Title VII-type; FMLA is a distinct federal
    threshold, see _FEDERAL_THRESHOLD_BY_CLAIM_TYPE below).

    thresholds:      claim_type -> minimum headcount for coverage to apply.
                      "general" must always be present -- resolve_coverage_gate()
                      falls through to it via thresholds.get(claim_type,
                      thresholds["general"]) for any claim_type without its
                      own override key. Extensible to future claim-type
                      carve-outs (retaliation, pregnancy, etc.) without a
                      schema change -- a claim type with no override simply
                      isn't a key here.
    damages_cap_treatment: "uncapped" | "state_specific_tiers" |
                      "state_specific_flat" | "federal_cap_applies" |
                      "no_damages_available".
                      "uncapped": real compensatory (and/or punitive)
                      damages exist with no ceiling on the amount.
                      "state_specific_tiers": the state has its own
                      independent statutory cap that scales in real tiers
                      by employer size (e.g. TX, TN, CO -- distinct dollar
                      figures at distinct headcount bands).
                      "state_specific_flat": the state has its own
                      independent statutory cap, but it's a single number
                      regardless of employer size (e.g. VA, FL -- not
                      tiered, and not deferring to federal).
                      "federal_cap_applies": no independent state cap
                      exists at all, so the federal Title VII tiered
                      schedule fills the gap by default.
                      "no_damages_available": neither compensatory nor
                      punitive damages are authorized under this
                      state's OWN statute at all -- remedies are
                      limited to equitable/make-whole relief (back pay,
                      front pay, reinstatement, injunctive relief,
                      attorney's fees), e.g. ND, WI.
                      Distinct from "uncapped": that value means real
                      damages exist with no ceiling; this value means no
                      damages exist to cap under STATE law specifically.
                      PHASE 1 UPDATE (prompts/damages-cap-treatment-
                      phase1-spec.md item 2, resolve_damages_treatment()
                      + the Cluster 1/2/4b integration below): the
                      state's own remedy is genuinely zero, but federal
                      law (Title VII/ADA) is a separate, independent
                      channel -- real, non-zero exposure is now priced
                      once headcount clears the federal 15-employee
                      floor (_FEDERAL_DEFAULT_THRESHOLD), with
                      NOT_APPLICABLE (genuinely zero) returned only
                      below it. This corrects the module's original
                      "MUST treat this value as zero exposure, not
                      unconstrained exposure" framing, written before
                      this headcount split was scoped -- that guidance
                      still describes the state's own remedy correctly,
                      it just no longer describes this value as a
                      blanket zero regardless of headcount.
    flat_cap:         Populated only for damages_cap_treatment ==
                      "state_specific_flat" states (FL, ID, KS, VA) --
                      the actual flat dollar figure from each state's
                      own citation, pulled directly from source (Phase
                      1, item 4). Clamped against the generic curve's
                      ceiling (min(curve.ceiling, flat_cap)) in Clusters
                      1 and 4b -- see resolve_damages_treatment() and
                      _resolve_flat_cap() below. None for every other
                      damages_cap_treatment value.
    is_combined_cap:  True only for MD and MO (Phase 2a) -- these two
                      states' own state_specific_tiers dollar figures
                      cap compensatory and punitive damages TOGETHER as
                      one combined number, confirmed directly against
                      each state's own statute text (MD: Md. State
                      Gov't Code Sec20-1013(e)(2); MO: RSMo
                      Sec213.111(4), which explicitly excludes back
                      pay/front pay from the same combined cap). False
                      (the default) for every other state, including
                      the other 7 state_specific_tiers states, whose
                      combined-vs-split structure has NOT been
                      independently verified either way -- False here
                      means "not confirmed combined," not "confirmed
                      split." Not consumed by any pricing logic yet --
                      same precedent as is_floor in Phase 1: encode the
                      statutory truth once confirmed, even before an
                      output layer exists to consume it, so a future
                      "detailed compensatory/punitive breakdown"
                      feature can't silently double-count a combined
                      cap as two independent ones.
    confidence:       "CONFIRMED" (independently verified against primary
                      statute text this session) | "PARTIAL" (not verified
                      this session -- see citation for what the entry
                      actually represents). resolve_coverage_gate() never
                      lets a PARTIAL entry drive a dollar-affecting
                      determination -- see that function's docstring.
    citation:         Primary source, or an explicit note when the entry is
                      an unverified placeholder rather than a researched
                      finding.
    """
    thresholds: dict[str, int]
    damages_cap_treatment: str
    confidence: str
    citation: str
    flat_cap: Optional[float] = None
    is_combined_cap: bool = False


# CONFIRMED states -- independently verified against primary statute text
# this session (not aggregator-only), per prompts/state-coverage-threshold-
# design.md.
STATE_COVERAGE_THRESHOLDS: dict[str, StateCoverageThreshold] = {
    "CA": StateCoverageThreshold(
        thresholds={"general": 5, "harassment": 1},
        damages_cap_treatment="uncapped",
        confidence="CONFIRMED",
        citation="Cal. Gov. Code §12926(d), §12940(a)",
    ),
    "NY": StateCoverageThreshold(
        thresholds={"general": 4, "harassment": 1},
        damages_cap_treatment="uncapped",
        confidence="CONFIRMED",
        citation=(
            "NYSHRL, N.Y. Exec. Law §§292, 296, 297; 2019 amendments "
            "S.6577/A.8421 (uncapped incl. punitive, corrects a common but "
            "wrong '$10,000 cap' claim which is housing-only/pre-2019)"
        ),
    ),
    "MA": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="uncapped",
        confidence="CONFIRMED",
        # Fontaine v. Philip Morris (argued Nov 5, 2025) is a PENDING case
        # that could affect punitive-damages doctrine here -- flag for
        # future revisit when decided. "uncapped" above reflects current
        # law only, not a prediction of that case's outcome.
        citation="M.G.L. c. 151B §4; Haddad v. Wal-Mart Stores, Inc., 455 Mass. 91 (2009)",
    ),
    "IL": StateCoverageThreshold(
        thresholds={"general": 1},
        # IHRA allows uncapped compensatory damages but NO punitive
        # damages -- a real nuance distinct from CA/NY/MA/WA's genuine
        # "uncapped" (which includes punitive). Modeled as
        # "federal_cap_applies" here as the closer of the two enum values,
        # not a perfect fit -- flagged rather than silently rounded.
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation=(
            "775 ILCS 5/2-101(B)(1)(a), P.A. 101-0430 eff. July 1 2020 -- "
            "applies to ALL protected categories including race, confirmed "
            "via current statute text correcting an aggregator source that "
            "incorrectly claimed race-discrimination still required 15+ "
            "under stale pre-2020 law"
        ),
    ),
    "WA": StateCoverageThreshold(
        thresholds={"general": 8},
        damages_cap_treatment="uncapped",  # compensatory; no state-specific punitive cap identified
        confidence="CONFIRMED",
        citation="RCW 49.60.040; Blakely v. City of Vancouver",
    ),
    "AK": StateCoverageThreshold(
        thresholds={"general": 1},
        # damages_cap_treatment NOT independently verified this session --
        # confidence="CONFIRMED" above covers the threshold only. Defaulted
        # conservatively per explicit instruction rather than left unset.
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="AS 18.80.300(5): 'employer means a person...who has one or more employees'",
    ),
    "WV": StateCoverageThreshold(
        thresholds={"general": 12},
        # Same caveat as AK immediately above -- damages_cap_treatment
        # unverified this session, defaulted conservatively.
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="W. Va. Code §5-11-3(d); WV CSR 77-7-2",
    ),
}

# All remaining jurisdictions (50 states + DC minus the 7 CONFIRMED above) --
# PARTIAL confidence throughout. Sourced from research/jurisdiction-research-
# headcount.md, a 50-state survey produced this same session via secondary
# aggregators (Justia, Blanchard & Walker) and law-firm summaries -- real,
# specific per-state figures, genuinely more informative than a uniform
# placeholder, but explicitly NOT independently verified against primary
# statute text the way the 7 CONFIRMED states above were. That source
# document's own Caveats section says outright: "these should be
# statute-verified before use in a paid product" -- confidence="PARTIAL"
# here is not a formality, resolve_coverage_gate() structurally prevents any
# of these numbers from driving a dollar-affecting determination on their
# own (see that function's docstring). Several rows carry a real internal
# conflict flagged in the source doc itself (Alaska 1 vs 2, West Virginia 12
# vs 15 -- both cross-validate against the CONFIRMED AK/WV entries above,
# which independently landed on the same lower figures via primary
# statute text) -- not resolved further here.
STATE_COVERAGE_THRESHOLDS.update({
    "AL": StateCoverageThreshold(
        thresholds={"general": 15},  # no general state anti-discrimination law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="No general private-sector state anti-discrimination law exists in Alabama -- federal Title VII (15+) governs entirely. Alabama Age Discrimination in Employment Act (AADEA), Code of Ala. §25-1-21, is a narrow age-only carve-out at 20+ employees.",
    ),
    "AZ": StateCoverageThreshold(
        thresholds={"general": 15, "harassment": 1},  # sexual harassment covers all employers
        damages_cap_treatment="no_damages_available",  # A.R.S. §41-1481(G) -- remedies limited to injunctions, reinstatement, back pay, front pay; no compensatory or punitive damages authorized
        confidence="CONFIRMED",
        citation="Arizona Civil Rights Act, A.R.S. §41-1461(6)(a); §41-1463; §41-1481(G).",
    ),
    "AR": StateCoverageThreshold(
        thresholds={"general": 9},
        damages_cap_treatment="state_specific_tiers",  # $15,000 (fewer than 15 employees) / $50,000 (15-100) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+), Ark. Code §16-123-107(c)(2)(B)
        confidence="CONFIRMED",
        citation="Arkansas Civil Rights Act, Ark. Code §16-123-107(c)(2)(B).",
    ),
    "CO": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes / no minimum
        damages_cap_treatment="state_specific_tiers",  # $10,000 (1-4 employees) / $25,000 (5-14 employees), then federal Title VII tiers apply at 15+, C.R.S. §24-34-405(3)(d)(I) and (II)(A)/(II)(B)
        confidence="CONFIRMED",
        citation="CADA, C.R.S. §24-34-402; POWR Act (SB 23-172) eff. Aug. 7, 2023.",
    ),
    "CT": StateCoverageThreshold(
        thresholds={"general": 1},  # lowered from 3+ eff. Oct. 1, 2022
        damages_cap_treatment="uncapped",  # compensatory uncapped; punitive damages not authorized under CFEPA at all -- Tomick v. UPS, 324 Conn. 470 (2016), Connecticut Supreme Court
        confidence="CONFIRMED",
        citation="CFEPA, Conn. Gen. Stat. §46a-51(10), §46a-104; P.A. 22-82.",
    ),
    "DE": StateCoverageThreshold(
        thresholds={"general": 4},  # disability coverage synced to this general threshold by Chapter 381 (SB 185, 2014) -- no longer a separate 15-employee line
        damages_cap_treatment="state_specific_tiers",  # $50,000 (4-14 employees) / $75,000 (15-100) / $175,000 (101-200) / $300,000 (201-500) / $500,000 (500+), 19 Del. C. §715(c) (SB 145, 2024, Chapter 203)
        confidence="CONFIRMED",
        citation="19 Del. C. §710(6); §722(3), as amended by Chapter 381 (SB 185, 2014).",
    ),
    "DC": StateCoverageThreshold(
        thresholds={"general": 1},
        damages_cap_treatment="uncapped",  # compensatory AND punitive, no statutory ceiling on either
        confidence="CONFIRMED",
        citation="DC Human Rights Act, D.C. Code §2-1401.02(10), §2-1403.16.",
    ),
    "FL": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="state_specific_flat",  # flat $100,000 punitive cap, no size-based tiers, Fla. Stat. §760.11(5) (confirmed consistent across a decade of statute versions)
        confidence="CONFIRMED",
        citation="Florida Civil Rights Act, Fla. Stat. §760.10.",
        flat_cap=100_000.0,
    ),
    "GA": StateCoverageThreshold(
        thresholds={"general": 15},  # no general private-sector state law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="No general private-sector state anti-discrimination law exists in Georgia -- federal Title VII (15+) governs entirely. Georgia Equal Employment for Persons with Disabilities Code, O.C.G.A. §34-6A-4, is a narrow disability-only carve-out at 15+ employees.",
    ),
    "HI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # HRS §378-5 / §368-17(b) -- court actions (post right-to-sue) allow unlimited compensatory (including emotional distress) and punitive damages; Hawaii does not incorporate Title VII's federal caps
        confidence="CONFIRMED",
        citation="HRS §378-1; §378-2; §378-5; §368-17(b).",
    ),
    "ID": StateCoverageThreshold(
        thresholds={"general": 5},
        damages_cap_treatment="state_specific_flat",  # Idaho Code §67-5908(3)(e) -- punitive damages capped at a flat $1,000 per willful violation, a single statutory ceiling, not employer-size tiers; actual/economic damages available separately, uncapped by this provision
        confidence="CONFIRMED",
        citation="Idaho Human Rights Act, Idaho Code §67-5902(6); §67-5908(3)(e).",
        flat_cap=1_000.0,
    ),
    "IN": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="uncapped",  # compensatory/emotional-distress damages available with no statutory cap; ICRC has no authority to award punitive damages -- Indiana Civil Rights Commission v. Alder, 714 N.E.2d 632 (Ind. 1999)
        confidence="CONFIRMED",
        citation="Indiana Civil Rights Law, Ind. Code §22-9-1-2.",
    ),
    "IA": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="uncapped",  # Ackelson v. Manley Toy Direct, L.L.C., 832 N.W.2d 678 (Iowa 2013) -- Iowa Supreme Court affirmed (unanimously, reaffirming 1986 precedent) that punitive damages are not permitted under the ICRA
        confidence="CONFIRMED",
        citation="Iowa Civil Rights Act, Iowa Code §216.15(9)(a)(8); Ackelson v. Manley Toy Direct, L.L.C., 832 N.W.2d 678 (Iowa 2013).",
    ),
    "KS": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_flat",  # $2,000 flat cap on pain/suffering/humiliation damages specifically, not scaled by employer size, K.S.A. §44-1005(k); no punitive damages authority under KAAD
        confidence="CONFIRMED",
        citation="Kansas Act Against Discrimination, K.S.A. §44-1009; §44-1005(k); Woods v. Midwest Conveyor Co.; Sporleder v. U.S. Bancorp.",
        flat_cap=2_000.0,
    ),
    "KY": StateCoverageThreshold(
        thresholds={"general": 8},  # 15+ for disability & pregnancy accommodation specifically
        damages_cap_treatment="uncapped",  # back pay, front pay, injunctive relief, and uncapped compensatory damages (emotional distress/humiliation) available under KRS §344.450; the remedy provision doesn't list punitive damages, and courts applying it (e.g. Timmons v. Wal-Mart Stores, following the Grzyb line of reasoning) have confirmed punitive damages aren't recoverable -- statutory-construction consensus, not one clean controlling holding like IN's Alder or PA's Hoy
        confidence="CONFIRMED",
        citation="Kentucky Civil Rights Act, KRS §344.450.",
    ),
    "LA": StateCoverageThreshold(
        thresholds={"general": 20},  # pregnancy 25+; federal 15+ is effectively lower either way
        damages_cap_treatment="uncapped",  # compensatory damages, back pay, benefits, attorney's fees available with no statutory cap under La. R.S. §23:303(A); Louisiana's civil-law doctrine bars punitive damages generally absent express statutory authorization (Chauvin v. Exxon Mobil, 2014-0808 (La. 12/9/14); Ross v. Conoco, Inc., 2002-0299 (La. 10/15/02)), and the LEDL provides none
        confidence="CONFIRMED",
        citation="Louisiana Employment Discrimination Law, La. R.S. §23:303(A); §23:332; §23:342 (pregnancy).",
    ),
    "ME": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        # <15 employees: "civil penal damages" only (not traditional
        # compensatory/punitive), tiered $20,000 (1st order) / $50,000
        # (2nd order) / $100,000 (3rd+ order). 15+ employees: traditional
        # compensatory and punitive damages, tiered up to $500,000 at the
        # top employer-size bracket -- exceeds Title VII's $300,000
        # federal maximum. Only the <15 tiers and the $500,000 ceiling
        # were independently verified this session -- intermediate
        # 15+-employee tier breakpoints were NOT verified; confirm
        # against 5 M.R.S. §4613(2)(B)(7)-(8) directly before relying on
        # them for anything beyond the applicability gate this field
        # doesn't yet drive.
        damages_cap_treatment="state_specific_tiers",
        confidence="CONFIRMED",
        citation="Maine Human Rights Act, 5 M.R.S. §4572; §4613(2)(B)(7)-(8).",
    ),
    "MD": StateCoverageThreshold(
        thresholds={"general": 15, "harassment": 1},  # confirmed harassment carve-out, HB 679 (2019)
        # Confirmed via §20-1013(e)(2): this is a COMBINED compensatory-
        # and-punitive cap, not compensatory-only with punitive uncapped
        # separately -- easy to misread from a partial reading of
        # §20-1009 alone; resolved this session, not just data entry.
        damages_cap_treatment="state_specific_tiers",  # $50,000 (15-100 employees) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (501+), Md. State Gov't Code §20-1009(b)(3)
        confidence="CONFIRMED",
        citation="Md. State Gov't Code §20-601(d), §20-611, §20-1009(b)(3), §20-1013(e)(2).",
        is_combined_cap=True,
    ),
    "MI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # Eide v. Kelsey-Hayes Co., 431 Mich. 26, 427 N.W.2d 488 (1988) -- Michigan Supreme Court held "exemplary damages" for mental anguish/distress/humiliation are available and uncapped, but are strictly compensatory in nature; traditional punitive damages designed to punish are not available under ELCRA
        confidence="CONFIRMED",
        citation="Elliott-Larsen Civil Rights Act, MCL §37.2801(1); §37.2801(3); Eide v. Kelsey-Hayes Co., 431 Mich. 26, 427 N.W.2d 488 (1988).",
    ),
    "MN": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # treble damages available; 2024 amendment (HF4109, signed May 15 2024, eff. Aug. 1 2024) removed the prior $25,000 punitive-damages cap for private-sector employers -- a $25,000 cap remains only for claims against political subdivisions
        confidence="CONFIRMED",
        citation="Minnesota Human Rights Act, Minn. Stat. §363A.29.",
    ),
    "MS": StateCoverageThreshold(
        thresholds={"general": 15},  # no state anti-discrimination law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="No comprehensive state anti-discrimination statute for private employers, confirmed directly against primary source text (9 independent sources); narrow existing carve-outs (military service, equal pay) don't provide general coverage. Federal 15+ threshold governs the applicable claim.",
    ),
    "MO": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="state_specific_tiers",  # combined compensatory (non-pecuniary)-and-punitive cap: $50,000 (more than 5 and fewer than 101 employees, i.e. 6-100 -- matches MHRA's own 6-employee coverage threshold) / $100,000 (101-200) / $200,000 (201-500) / $500,000 (500+); back pay/front pay not subject to these caps
        confidence="CONFIRMED",
        citation="Missouri Human Rights Act, RSMo §213.010; §213.111(4); SB 43 eff. Aug. 28, 2017.",
        is_combined_cap=True,
    ),
    "MT": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum / all sizes
        # MCA §39-2-912(1) exempts discrimination-based discharges from
        # the WDEA entirely (which would otherwise cap damages at 4
        # years wages/benefits and bar punitive) -- discrimination
        # claims proceed exclusively under the MHRA. Under MCA
        # §49-2-506(1)(b)/(2) and §49-2-509(2): punitive damages
        # barred, but compensatory damages (pecuniary harm,
        # pain/suffering, emotional distress) are authorized and
        # uncapped by any statutory schedule.
        damages_cap_treatment="uncapped",
        confidence="CONFIRMED",
        citation="Montana Human Rights Act, MCA §49-2-101(11); §49-2-506(1)(b); §49-2-509(2); Wrongful Discharge from Employment Act, MCA §39-2-912(1).",
    ),
    "NE": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="uncapped",  # punitive damages constitutionally barred in Nebraska (Neb. Const. Art. VII, §5; O'Brien v. Cessna Aircraft Co., 298 Neb. 109 (2017)); compensatory damages under Neb. Rev. Stat. §48-1119(4) have no statutory cap
        confidence="CONFIRMED",
        citation="Nebraska Fair Employment Practice Act, Neb. Rev. Stat. §48-1119(4); Neb. Const. Art. VII, §5; O'Brien v. Cessna Aircraft Co., 298 Neb. 109 (2017).",
    ),
    "NV": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",  # NRS §613.432 incorporates the federal Title VII remedy framework, so compensatory/punitive damages are available but subject to federal §1981a tiered caps
        confidence="CONFIRMED",
        citation="Nevada Fair Employment Practices Act, NRS §613.310(2); §613.432.",
    ),
    "NH": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="uncapped",  # RSA 354-A:21-a authorizes uncapped "enhanced compensatory damages" for willful/reckless violations; RSA 354-A isn't one of RSA 507:16's narrow punitive-damages carve-outs (RSA 359-D:11, RSA 570-A:11)
        confidence="CONFIRMED",
        citation="RSA ch. 354-A; RSA 354-A:21-a; RSA 507:16.",
    ),
    "NJ": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        # N.J.S.A. §2A:15-5.14(c) explicitly excludes "P.L.1945, c.169
        # (C.10:5-1 et seq.)" (the LAD) from the general Punitive
        # Damages Act's 5x-compensatory/$350,000 cap -- both
        # compensatory and punitive remain genuinely uncapped under
        # NJLAD specifically. Resolves the prior "flagged, not
        # resolved" open question.
        damages_cap_treatment="uncapped",
        confidence="CONFIRMED",
        citation="NJLAD, N.J.S.A. §10:5-5, §10:5-3; N.J.S.A. §2A:15-5.14(c).",
    ),
    "NM": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="uncapped",  # NMSA 1978, §28-1-13(D) -- actual damages including emotional distress available and uncapped; punitive damages not authorized under NMHRA; Title VII's federal caps don't apply to state claims
        confidence="CONFIRMED",
        citation="New Mexico Human Rights Act, NMSA 1978, §28-1-2(B); §28-1-13(D).",
    ),
    "NC": StateCoverageThreshold(
        # NCEEPA covers employers with 15+ employees but provides no
        # private right of action -- the statute's own public-policy
        # declaration can support a common-law wrongful-discharge claim
        # instead, which isn't headcount-gated the way this table
        # models. federal_cap_applies remains the structurally correct
        # treatment for the actual statutory discrimination framework.
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="North Carolina Equal Employment Practices Act, N.C. Gen. Stat. §143-422.2(a).",
    ),
    "ND": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum
        damages_cap_treatment="no_damages_available",  # N.D.C.C. §14-02.4-20, direct statute text: "Neither the department nor an administrative hearing officer may order compensatory or punitive damages under this chapter" -- remedies limited to back pay (2-year cap), injunctions, and equitable relief
        confidence="CONFIRMED",
        citation="North Dakota Human Rights Act, N.D.C.C. ch. 14-02.4; §14-02.4-20.",
    ),
    "OH": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_tiers",  # H.B. 352 (Employment Law Uniformity Act), eff. Apr. 15, 2021, codified Ohio's Tort Reform Act caps onto R.C. ch. 4112 claims. R.C. 2315.18: non-economic compensatory capped at the greater of $250,000 or 3x economic loss, max $350,000. R.C. 2315.21: punitive capped at 2x compensatory, or for "small employers" (<=100 employees, 500 for manufacturing) at 10% of net worth up to $350,000
        confidence="CONFIRMED",
        citation="Ohio Civil Rights Act, R.C. ch. 4112; R.C. 2315.18; R.C. 2315.21; H.B. 352 eff. Apr. 15, 2021.",
    ),
    "OK": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="no_damages_available",  # 25 O.S. §1350, added 2011 (Laws 2011, c. 270, §11, eff. Nov. 1, 2011) -- subsection (A) abolished all common-law remedies for employment discrimination (previously available via the Burk tort, which allowed unlimited compensatory/punitive damages); subsection (G), confirmed via direct statute text, limits the statutory remedy to injunctive relief, reinstatement, back pay, and liquidated damages equal to back pay -- no compensatory damages for emotional distress, no punitive damages authorized anywhere in the section
        confidence="CONFIRMED",
        citation="Oklahoma Anti-Discrimination Act, 25 O.S. §1301; 25 O.S. §1350 (added by Laws 2011, c. 270, §11, eff. Nov. 1, 2011).",
    ),
    "OR": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum
        damages_cap_treatment="uncapped",  # Zweizig v. Rote, 368 Or. 79 (2021) -- Oregon Supreme Court held the $500,000 noneconomic damages cap in ORS 31.710(1) (civil actions for "bodily injury") does NOT apply to unlawful employment practice claims under ORS 659A.030 seeking purely emotional injury damages -- genuinely uncapped
        confidence="CONFIRMED",
        citation="ORS §659A.001(4)(a); §659A.030; Zweizig v. Rote, 368 Or. 79 (2021).",
    ),
    "PA": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="uncapped",  # compensatory (including emotional distress) uncapped; punitive damages not recoverable under the PHRA at all -- Hoy v. Angelone, 554 Pa. 134, 720 A.2d 745 (Pa. 1998), Pennsylvania Supreme Court
        confidence="CONFIRMED",
        citation="Pennsylvania Human Relations Act, 43 P.S. §954.",
    ),
    "RI": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="uncapped",  # R.I. Gen. Laws §28-5-24 (compensatory) and §28-5-29.1 (punitive, on a malice/reckless-indifference showing) -- neither imposes a dollar cap or employer-size tier
        confidence="CONFIRMED",
        citation="RI Fair Employment Practices Act, R.I. Gen. Laws §28-5-24; §28-5-29.1.",
    ),
    "SC": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="no_damages_available",  # S.C. Code Ann. §1-13-90(c)(16) -- remedies limited to an order that the discriminatory practice be discontinued, plus affirmative action (hiring, reinstatement, upgrading) with or without back pay; no compensatory damages for emotional distress, no punitive damages authorized anywhere in the section
        confidence="CONFIRMED",
        citation="SC Human Affairs Law, S.C. Code §1-13-30; §1-13-90(c)(16).",
    ),
    "SD": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum
        damages_cap_treatment="uncapped",  # compensatory damages available with no statutory cap for a general employment discrimination claim under §20-13-10 (SDCL §20-13-35.1). Punitive damages ARE authorized under §21-3-2, but only for a distinct, narrower set of HRA sections (§§20-13-20 to 20-13-21.2, 20-13-23.4, 20-13-23.7, 20-13-26) that appear housing-related, not general employment discrimination -- do not read this as "no punitive damages under this chapter" broadly
        confidence="CONFIRMED",
        citation="SD Human Relations Act, SDCL ch. 20-13; §20-13-10; §20-13-35.1; §21-3-2.",
    ),
    "TN": StateCoverageThreshold(
        thresholds={"general": 8},
        damages_cap_treatment="state_specific_tiers",  # $25,000 (8-14 employees) / $50,000 (15-100) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+), T.C.A. §4-21-313(a)
        confidence="CONFIRMED",
        citation="Tennessee Human Rights Act, T.C.A. §4-21-102.",
    ),
    "TX": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="state_specific_tiers",  # $50,000 (<101 employees) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+), Tex. Lab. Code §21.2585(d) -- §21.2585(f) removes this cap entirely for sexual-assault and sex-based-harassment/retaliation claims specifically, not currently modeled by claim type
        confidence="CONFIRMED",
        citation="Texas Labor Code ch. 21 / Texas Commission on Human Rights Act.",
    ),
    "UT": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="no_damages_available",  # Utah Code §34A-5-107 is the exclusive remedy for employment discrimination in Utah, confirmed via direct statute text referencing its own "exclusive remedy provision" -- no private right of action in state court; remedies limited to equitable relief (cease-and-desist, reinstatement, back pay), no compensatory or punitive damages authorized
        confidence="CONFIRMED",
        citation="Utah Antidiscrimination Act, Utah Code §34A-5-102(1)(i)(D); §34A-5-107.",
    ),
    "VT": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum / all sizes
        damages_cap_treatment="uncapped",  # 21 V.S.A. §495b(b) authorizes compensatory and punitive damages with no statutory limit of any kind
        confidence="CONFIRMED",
        citation="Vermont Fair Employment Practices Act, 21 V.S.A. §495; §495b(b).",
    ),
    "VA": StateCoverageThreshold(
        thresholds={"general": 5},
        damages_cap_treatment="state_specific_flat",  # flat $350,000 punitive cap, Va. Code §8.01-38.1 (confirmed unchanged)
        confidence="CONFIRMED",
        citation="Va. Code §2.2-3905, as amended by SB 637 (Va. Acts ch. 950, 2026), eff. July 1, 2026 -- Virginia Human Rights Act employer threshold now 5, applying uniformly across all protected classes and claim types; the prior 5-20-employee age-discrimination-only carve-out is repealed entirely, not just the general threshold.",
        flat_cap=350_000.0,
    ),
    "WI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="no_damages_available",  # 2011 Wisconsin Act 219 repealed the 2009 amendment (Act 20) that had briefly allowed compensatory/punitive damages under WFEA -- current remedies under Wis. Stat. §111.39(4)(c) limited to back pay, front pay, reinstatement, and attorney's fees; neither compensatory nor punitive damages available
        confidence="CONFIRMED",
        citation="Wisconsin Fair Employment Act, Wis. Stat. §111.31 et seq.; §111.39(4)(c); 2011 Wisconsin Act 219.",
    ),
    "WY": StateCoverageThreshold(
        thresholds={"general": 2},  # unusually low figure, confirmed correct via direct statute text, independently corroborated by 6 sources
        damages_cap_treatment="no_damages_available",  # Wyo. Stat. §27-9-106(g) -- remedies limited to affirmative action (hiring, reinstatement, upgrading) with or without back pay; no compensatory or punitive damages authorized anywhere in the section
        confidence="CONFIRMED",
        citation="Wyoming Fair Employment Practices Act, Wyo. Stat. §27-9-102(b); §27-9-106(g).",
    ),
})

# Defensive fallback only -- every jurisdiction is expected to be covered by
# either the CONFIRMED block above or the PARTIAL block immediately above;
# this loop should be a no-op in practice (asserted below) and exists only
# so a future JURISDICTION_TABLE addition can't silently produce a KeyError
# deep inside resolve_coverage_gate() instead of a clear signal here.
#
# This is also why a state with no general private-sector anti-
# discrimination law (e.g. AL, GA) can't simply be OMITTED from this
# dict to represent "federal governs entirely." Two mechanisms make
# that actively broken, not just risky: (1) the assert immediately
# below requires this dict's key set to exactly match
# JURISDICTION_TABLE's, so removing an entry crashes the whole module
# at import time, not just a rare code path; (2) even without that
# assert, this fallback loop would silently re-create the omitted
# entry as an unresearched-looking PARTIAL placeholder, actively
# mislabeling a real, confirmed finding. resolve_coverage_gate()'s own
# .get(jid) lookup is safe on a missing key -- that's a separate
# question from whether removal is a good idea (2026-09-09
# investigation, AL/GA). The correct representation for "no state law
# exists" is to KEEP the entry with damages_cap_treatment=
# "federal_cap_applies" and confidence="CONFIRMED" once independently
# verified -- see AL/GA's own entries above.
for _jid in JURISDICTION_TABLE:
    if _jid not in STATE_COVERAGE_THRESHOLDS:
        _logger.warning(
            "STATE_COVERAGE_THRESHOLDS has no entry for jurisdiction %r -- "
            "added via fallback default, needs real research", _jid,
        )
        STATE_COVERAGE_THRESHOLDS[_jid] = StateCoverageThreshold(
            thresholds={"general": 15},
            damages_cap_treatment="federal_cap_applies",
            confidence="PARTIAL",
            citation="No entry authored -- fallback default, needs research.",
        )
del _jid

assert set(STATE_COVERAGE_THRESHOLDS.keys()) == set(JURISDICTION_TABLE.keys()), (
    "STATE_COVERAGE_THRESHOLDS must cover exactly the same 50-states-plus-DC "
    "key set as JURISDICTION_TABLE"
)
assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 51, (
    "Expected exactly 51 CONFIRMED states -- all of STATE_COVERAGE_THRESHOLDS, the PARTIAL-state verification workstream is complete (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA, MS, NC, OK, AZ, HI, ID, MT, NM, NV, OR, UT, WY, IA, MI, SC)"
)


# Federal ADA/Title VII employer-count threshold (15) applies to any
# claim_type that isn't an explicit FMLA-type claim (50-employee federal
# threshold). Harassment claims are still governed by the federal
# 15-employee threshold at the FEDERAL level -- only specific STATE laws
# (e.g. California, at any size) lower or remove it for harassment
# specifically, which is why "harassment" is a key inside a CONFIRMED
# state's own thresholds dict above, not a second federal number here.
_FEDERAL_THRESHOLD_BY_CLAIM_TYPE: dict[str, int] = {
    "fmla": 50,
}
_FEDERAL_DEFAULT_THRESHOLD = 15  # ADA / Title VII, and the default for any other claim_type


def _federal_threshold(claim_type: str) -> int:
    return _FEDERAL_THRESHOLD_BY_CLAIM_TYPE.get(claim_type, _FEDERAL_DEFAULT_THRESHOLD)


@dataclass(frozen=True)
class CoverageResult:
    """
    Result of resolve_coverage_gate(). driving_jurisdiction is populated
    only when confidence == "CONFIRMED" -- None means the federal fallback
    threshold was used (no CONFIRMED jurisdiction in the input list).

    partial_state_flag is True in two distinct situations, both signaled
    the same way (Gate steps 5 and 6 of the design doc) since either one
    means "do not present this determination with full confidence":
      - confidence == "CONFIRMED" but a PARTIAL-confidence jurisdiction was
        also present in the input, AND that PARTIAL jurisdiction's own
        threshold would have flipped `applies` if it had been counted
        alongside the CONFIRMED jurisdictions (step 5) -- i.e. a real,
        unverified possibility that the true legal answer differs from
        what PRV3 is confident enough to state.
      - confidence == "FEDERAL_FALLBACK" because no CONFIRMED jurisdiction
        was present at all (jurisdictions was empty, or contained only
        PARTIAL-confidence states) -- the federal number is used for the
        numeric gate, but state law in the client's actual jurisdiction(s)
        was never independently verified and may lower the real threshold
        (step 6). This case fires even when partial_jurisdictions_considered
        is empty (a genuinely empty jurisdictions list carries the same
        "unverified" caveat, just with no specific state to name).

    partial_jurisdictions_considered lists the PARTIAL-confidence
    jurisdiction codes actually found in the input (empty tuple if none) --
    lets a caller compose a specific message ("state law in NJ was not
    independently verified") rather than a generic one.
    """
    applies: bool
    threshold: int
    claim_type: str
    driving_jurisdiction: Optional[str]
    confidence: str  # "CONFIRMED" | "FEDERAL_FALLBACK"
    partial_state_flag: bool
    partial_jurisdictions_considered: tuple[str, ...]


def resolve_coverage_gate(
    headcount: int,
    jurisdictions: list[str],
    claim_type: str = "general",
) -> CoverageResult:
    """
    Determines whether ADA/Title VII/FMLA-type coverage applies for a given
    headcount and set of operating jurisdictions, using the most-protective
    (lowest) threshold across every CONFIRMED-confidence jurisdiction in the
    input -- mirrors engine/data/jurisdiction.py's existing
    highest-restriction pattern (same shape, a different table; that module
    is not touched by this function).

    Resolution order:
      1. For each jurisdiction in the input with confidence == "CONFIRMED",
         look up thresholds.get(claim_type, thresholds["general"]).
      2. Take the MINIMUM threshold across all CONFIRMED jurisdictions found.
      3-6. If no CONFIRMED jurisdiction is present (input empty, contains
         only unrecognized codes, or contains only PARTIAL-confidence
         states), fall back to the federal threshold for `claim_type`
         (_federal_threshold()) and report confidence="FEDERAL_FALLBACK".
         PARTIAL-confidence thresholds are NEVER used to compute the
         numeric gate directly -- only to populate partial_state_flag /
         partial_jurisdictions_considered so a caller can add a qualitative
         caveat. See CoverageResult's docstring for the two distinct cases
         this flag covers.

    Aggregate-headcount limitation (explicit, not silently assumed away):
    PRV3 collects only aggregate national headcount, not per-state employee
    counts (IntakeData.headcount is a single org-wide int). This gate
    necessarily compares that aggregate against the most-protective
    threshold across selected jurisdictions -- this can overstate coverage
    if a specific claim would legally arise from a single low-count
    location rather than the org's total headcount. Whether state coverage
    thresholds count aggregate or in-state-only headcount is itself
    state-specific and UNRESEARCHED this session -- do not assume either
    counting method is correct. Tracked as an explicit open item in
    prompts/friction-tax-legal-compliance-methodology.md's Next Steps and
    prompts/state-coverage-threshold-design.md.
    """
    # Guard: an unusable headcount (empty string, other non-numeric
    # string, None) can't drive either comparison branch below. Rather
    # than let a raw `>=` against a non-number raise, short-circuit to
    # "coverage cannot be determined" -- applies=False, same as a
    # real headcount that doesn't clear the threshold. Every caller
    # (clusters 1, 2, 4b) already turns applies=False into
    # LegalPricingStatus.NOT_APPLICABLE. Confirmed live, 2026-09-08:
    # this is what the self-select "Take the diagnostic" CTA
    # (web/app/diagnostic/page.tsx) sends today for any request.
    if not isinstance(headcount, (int, float)):
        threshold = _federal_threshold(claim_type)
        return CoverageResult(
            applies=False,
            threshold=threshold,
            claim_type=claim_type,
            driving_jurisdiction=None,
            confidence="FEDERAL_FALLBACK",
            partial_state_flag=False,
            partial_jurisdictions_considered=(),
        )

    confirmed_entries: list[tuple[str, int]] = []
    partial_entries: list[tuple[str, int]] = []
    for jid in jurisdictions:
        entry = STATE_COVERAGE_THRESHOLDS.get(jid)
        if entry is None:
            continue
        threshold = entry.thresholds.get(claim_type, entry.thresholds["general"])
        if entry.confidence == "CONFIRMED":
            confirmed_entries.append((jid, threshold))
        else:
            partial_entries.append((jid, threshold))

    partial_jids = tuple(jid for jid, _t in partial_entries)

    if confirmed_entries:
        driving_jurisdiction, threshold = min(confirmed_entries, key=lambda pair: pair[1])
        applies = headcount >= threshold
        partial_state_flag = False
        if partial_entries:
            combined_threshold = min([threshold] + [t for _jid, t in partial_entries])
            if (headcount >= combined_threshold) != applies:
                partial_state_flag = True
        return CoverageResult(
            applies=applies,
            threshold=threshold,
            claim_type=claim_type,
            driving_jurisdiction=driving_jurisdiction,
            confidence="CONFIRMED",
            partial_state_flag=partial_state_flag,
            partial_jurisdictions_considered=partial_jids,
        )

    threshold = _federal_threshold(claim_type)
    return CoverageResult(
        applies=headcount >= threshold,
        threshold=threshold,
        claim_type=claim_type,
        driving_jurisdiction=None,
        confidence="FEDERAL_FALLBACK",
        partial_state_flag=bool(partial_entries),
        partial_jurisdictions_considered=partial_jids,
    )


# -- Damages-cap-treatment resolution (Phase 1) -------------------------------
# prompts/damages-cap-treatment-phase1-spec.md. Highest-exposure-wins
# resolution across an org's selected jurisdictions, paralleling
# resolve_coverage_gate()'s own "most-protective wins" pattern but for
# damages_cap_treatment rather than coverage-threshold applicability --
# a related but genuinely separate question (this determines the SHAPE
# of dollar exposure once coverage already applies, not whether it
# applies at all).

_DAMAGES_TREATMENT_PRIORITY: dict[str, int] = {
    "uncapped": 5,
    "state_specific_flat": 4,
    "state_specific_tiers": 3,
    "federal_cap_applies": 2,
    "no_damages_available": 1,
}


def resolve_damages_treatment(jurisdictions: list[str]) -> str:
    """
    Highest-exposure-wins damages_cap_treatment across the CONFIRMED-
    confidence jurisdictions in the input: uncapped > state_specific_flat
    > state_specific_tiers > federal_cap_applies > no_damages_available.

    CORRECTED (found in review before commit): state_specific_tiers and
    state_specific_flat were originally ranked as peers (both mean "a
    real independent state cap exists," with a comment claiming no tie-
    break was needed since a caller only cares whether a cap exists,
    not which shape wins). That was wrong -- with strict `>` deciding
    ties by input order, a multi-jurisdiction selection containing both
    a tiers state and a flat state could silently suppress the flat
    state's real, working clamp depending on which jurisdiction
    happened to be listed first, a real bug, not a theoretical one.
    state_specific_flat now ranks strictly above state_specific_tiers,
    deterministically: it has a real, working clamp mechanism today
    (_resolve_flat_cap(), Phase 1 item 4), while state_specific_tiers
    has no mechanism at all until Phase 2 (item 5, no schema exists yet
    for tiered/formula cap data) -- a caller should get the treatment
    whose downstream clamp actually functions, not whichever state
    happened to be listed first.

    PARTIAL-confidence entries never drive this determination -- same
    discipline as resolve_coverage_gate(), though every entry in
    STATE_COVERAGE_THRESHOLDS is CONFIRMED as of the completed
    PARTIAL-state verification workstream (2026-09-10), so this is a
    defensive convention match today, not a live behavior difference.

    Empty input, or a jurisdictions list with no CONFIRMED entry found,
    falls back to "federal_cap_applies" -- the real-world-correct
    default (no verified state law in play means federal law is what
    actually governs). Confirmed NOT a literal code-level match to
    resolve_coverage_gate()'s own "FEDERAL_FALLBACK" convention before
    this function was written, not assumed: that function has no
    damages_cap_treatment-shaped return value to mirror. Same
    underlying real-world legal reasoning, different data shape.
    """
    best: Optional[str] = None
    best_rank = -1
    for jid in jurisdictions:
        entry = STATE_COVERAGE_THRESHOLDS.get(jid)
        if entry is None or entry.confidence != "CONFIRMED":
            continue
        rank = _DAMAGES_TREATMENT_PRIORITY.get(entry.damages_cap_treatment, -1)
        if rank > best_rank:
            best_rank = rank
            best = entry.damages_cap_treatment
    return best if best is not None else "federal_cap_applies"


def _resolve_flat_cap(jurisdictions: list[str]) -> Optional[float]:
    """
    Maximum flat_cap among CONFIRMED state_specific_flat jurisdictions
    in the input -- extends resolve_damages_treatment()'s own
    highest-exposure-wins principle down to the actual dollar figure,
    needed because that function returns a category string, not a
    specific state; with more than one state_specific_flat jurisdiction
    selected, something has to pick which state's own flat_cap governs.
    None if no CONFIRMED state_specific_flat jurisdiction is present in
    the input, or if one is present but its flat_cap is unpopulated (a
    data gap, not expected once all 4 real flat_cap states are
    populated).
    """
    best: Optional[float] = None
    for jid in jurisdictions:
        entry = STATE_COVERAGE_THRESHOLDS.get(jid)
        if entry is None or entry.confidence != "CONFIRMED":
            continue
        if entry.damages_cap_treatment != "state_specific_flat":
            continue
        if entry.flat_cap is None:
            continue
        if best is None or entry.flat_cap > best:
            best = entry.flat_cap
    return best


def _co_drives_federal_tier_deferral(jurisdictions: list[str], headcount) -> bool:
    """
    True only when Colorado is the SPECIFIC jurisdiction
    resolve_damages_treatment() would resolve a state_specific_tiers
    result from, AND headcount has cleared the federal 15-employee
    floor Colorado's own statute defers to at that point (C.R.S.
    Sec24-34-405(3)(d)(II)(A)/(II)(B)) -- Colorado's own comment is the
    only one among all 9 state_specific_tiers states that describes
    deferring to federal Title VII tiers at any headcount; the other 8
    keep their own (unmodeled) tiers at every headcount. Cannot be a
    blanket check on the resolved treatment string alone -- that would
    also fire for a jurisdictions list whose real driving state is TX,
    AR, etc. (also state_specific_tiers, but non-deferring).

    Re-derives resolve_damages_treatment()'s own priority-resolution
    loop rather than changing that function's return contract to
    additionally expose the winning jurisdiction -- three existing call
    sites and the test suite depend on it returning a bare string.

    Known limitation, not fixed here: if two state_specific_tiers
    jurisdictions tie for best_rank (e.g. CO and TX both selected),
    resolve_damages_treatment()'s own strict `>` comparison means
    whichever is encountered FIRST in the input list wins -- this
    function inherits that same input-order dependency rather than
    resolving it, since disambiguating which specific tiers state
    governs a multi-tiers-state selection is a pre-existing gap this
    Phase 2a build didn't create and isn't scoped to fix.
    """
    if not isinstance(headcount, (int, float)) or headcount < _FEDERAL_DEFAULT_THRESHOLD:
        return False
    best_jid: Optional[str] = None
    best_rank = -1
    for jid in jurisdictions:
        entry = STATE_COVERAGE_THRESHOLDS.get(jid)
        if entry is None or entry.confidence != "CONFIRMED":
            continue
        rank = _DAMAGES_TREATMENT_PRIORITY.get(entry.damages_cap_treatment, -1)
        if rank > best_rank:
            best_rank = rank
            best_jid = jid
    return best_jid == "CO"


def _cluster_4_curve_for_org_type(
    org_type: str, org_size: str, headcount: int, jurisdictions: list[str]
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

    Coverage gate (state-coverage-threshold-design.md) applies only to
    4b -- 4a (Publicly traded, SEC-anchored) and 4c (Government) are out
    of scope for the ADA/Title VII/FMLA coverage question entirely, so
    the gate runs after those two are ruled out, not before. Status is
    NOT_APPLICABLE (not DATA_INTEGRITY_GAP) when the org's headcount
    falls below the resolved coverage threshold -- this is a real,
    expected "genuinely not covered" outcome, not a data problem.
    """
    if org_type == "Publicly traded":
        return LegalCurveLookup(
            curve=_CLUSTER_4A_CURVE, status=LegalPricingStatus.PRICED,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False,
        )
    if org_type == "Government":
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.QUALITATIVE_ONLY,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False,
        )
    coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
    if not coverage.applies:
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.NOT_APPLICABLE,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        )
    treatment = resolve_damages_treatment(jurisdictions)
    if treatment == "no_damages_available" and headcount < _FEDERAL_DEFAULT_THRESHOLD:
        # Same federal-floor branch as Clusters 1/2 above -- state law
        # bars damages outright and federal coverage doesn't
        # independently attach below its own 15-employee floor. Phase
        # 1, prompts/damages-cap-treatment-phase1-spec.md item 2.
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.NOT_APPLICABLE,
            coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag,
        )
    if treatment == "state_specific_tiers" and _co_drives_federal_tier_deferral(jurisdictions, headcount):
        # Colorado's own statute explicitly defers to the federal Title
        # VII tier table at 15+ employees -- swap in that treatment
        # label for the rest of this resolution. Cluster 4b's ceiling
        # table below IS that same federal bracket table already (per
        # its own comment), so the ceiling VALUE doesn't change here --
        # only is_floor does, since the number is now Colorado's own
        # real, confirmed answer at this headcount, not a placeholder.
        # Inverted shape vs. the no_damages_available branch above:
        # that one returns early BELOW its threshold; this one lets
        # normal resolution continue with a corrected label ABOVE one.
        # Phase 2a, prompts/damages-cap-treatment-phase2-spec.md.
        treatment = "federal_cap_applies"
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)
    if ceiling is None:
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.DATA_INTEGRITY_GAP,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        )
    flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
    final_ceiling = ceiling if flat_cap is None else min(ceiling, flat_cap)
    is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None
    return LegalCurveLookup(
        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=final_ceiling),
        status=LegalPricingStatus.PRICED,
        coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        is_floor=is_floor,
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
    headcount: int,
    jurisdictions: list[str],
) -> LegalPricingResult:
    """
    One Legal-scoring state's pricing outcome in isolation. status is
    NOT_APPLICABLE (dollar_range=None) if the state isn't Legal-scoring
    at all, its "legal" score is 0 (no exposure), or (Clusters 1, 2, 4b
    only) the state-coverage-threshold gate determines the org's
    headcount doesn't meet the applicable ADA/Title VII coverage
    threshold for its operating jurisdiction(s) -- all silently
    collapsed to the same status, matching the existing "not applicable
    at all" semantics rather than inventing a new one. For Cluster 4,
    status is forwarded directly from _cluster_4_curve_for_org_type()
    (QUALITATIVE_ONLY for Government, DATA_INTEGRITY_GAP for an
    unrecognized org_size, NOT_APPLICABLE for the 4b coverage gate),
    distinguishing real-but-unpriced exposure from a genuine data gap
    from genuinely-not-covered.

    Coverage gate uses claim_type="general" for Clusters 1 and 2 --
    per-state claim-type mapping (e.g. which of these 30 states
    represents a harassment claim specifically, which could resolve to
    a lower threshold in a CONFIRMED state) is not resolved here; that
    would be new clinical judgment beyond this build's scope, not
    inferred from the taxonomy. See state-coverage-threshold-design.md.
    """
    cluster = LEGAL_COMPLIANCE_CLUSTER.get(state_id)
    if cluster is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    entry = STATE_MULTIPLIERS.get(state_id)
    if entry is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    score = entry.criteria["legal"].score
    if score == 0:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)

    if cluster == 1:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
        treatment = resolve_damages_treatment(jurisdictions)
        if treatment == "no_damages_available" and headcount < _FEDERAL_DEFAULT_THRESHOLD:
            # State law bars damages outright and federal coverage
            # doesn't independently attach below its own 15-employee
            # floor -- genuinely no exposure to price, not an
            # unpriced-but-real one. Phase 1, prompts/damages-cap-
            # treatment-phase1-spec.md item 2.
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag)
        flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
        curve = _CLUSTER_1_CURVE if flat_cap is None else LegalDollarCurve(
            floor=_CLUSTER_1_CURVE.floor, ceiling=min(_CLUSTER_1_CURVE.ceiling, flat_cap),
        )
        v = _legal_score_fraction(curve, score)
        is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
            is_floor=is_floor)
    if cluster == 2:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
        treatment = resolve_damages_treatment(jurisdictions)
        if treatment == "no_damages_available" and headcount < _FEDERAL_DEFAULT_THRESHOLD:
            # Same federal-floor branch as Cluster 1 above. Cluster 2's
            # dollar values are two fixed discrete tiers, not a curve --
            # no clamp or is_floor applies here, structurally exempt
            # from items 3/4, only item 2's applicability question
            # reaches Cluster 2.
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag)
        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
    if cluster == 3:
        # org_size is None when resolve_headcount_bucket() couldn't
        # classify the request's headcount. Real, non-zero exposure
        # still applies (this state's Cluster 3 condition is real) --
        # QUALITATIVE_ONLY, not NOT_APPLICABLE, so it's still named
        # for the Principal rather than silently hidden. Checked here,
        # before _cluster_3_affected_workers() -- that function's own
        # midpoint_entry-is-None fallback returns 0.0, which would
        # otherwise produce a fabricated dollar_range=(0.0, 0.0)
        # PRICED result, indistinguishable from genuinely-zero risk.
        if org_size is None:
            return LegalPricingResult(status=LegalPricingStatus.QUALITATIVE_ONLY, dollar_range=None,
                coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
        affected = _cluster_3_affected_workers(org_size, industry, score)
        r = (
            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,
            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,
        )
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    if cluster == 4:
        lookup = _cluster_4_curve_for_org_type(org_type, org_size, headcount, jurisdictions)
        if lookup.curve is None:
            return LegalPricingResult(status=lookup.status, dollar_range=None,
                coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)
        v = _legal_score_fraction(lookup.curve, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag,
            is_floor=lookup.is_floor)
    if cluster == 5:
        v = _legal_score_fraction(_CLUSTER_5_CURVE, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
        coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)


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
    jurisdictions: Optional[list[str]] = None,
) -> dict:
    """
    Cross-state aggregation (Addendum 3): within-cluster geometric decay
    (w_i = 0.5**(i-1), reusing the attritional Step 1 shape -- ranked by
    each state's own low end, highest first), across-cluster simple
    addition (no breadth premium -- Addendum 3's explicit, justified
    departure from the attritional design's Factor B). N=1 guard: exactly
    one Legal-scoring state in the profile collapses the output to that
    state's own individual range, no aggregation logic engaged.

    jurisdictions (IntakeData.jurisdictions -- a list of 2-letter state
    codes, defaults to None/treated as []) feeds the state-coverage-
    threshold gate (state-coverage-threshold-design.md) for Clusters 1,
    2, and 4b only -- see resolve_coverage_gate() and
    _single_state_legal_pricing(). Defaulting to None/[] rather than
    requiring the caller to always pass it keeps every pre-existing call
    site (tests, calibration_runner.py) working unchanged: an empty
    jurisdictions list falls through to the federal threshold (15),
    identical behavior to "coverage always applies" for any org_size
    used anywhere in this project's real test/calibration data (all well
    above 15).

    California FEHA/PAGA-specific damages-cap treatment and OSHA State
    Plan variation (Addenda 6-9) are still NOT applied here -- deferred,
    per Addendum 9, unaffected by the coverage-threshold gate above
    (a distinct question: whether coverage applies at all, not how much
    a covered claim is worth). Cluster 5 uses the statutory-max curve
    only (Addendum 10) -- actual-average deferred alongside that same
    paused research.

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
    headcount = org_size
    jurisdictions = jurisdictions or []
    org_size = resolve_headcount_bucket(org_size)
    per_state_ranges: dict[str, tuple[float, float]] = {}
    unpriced_state_ids: list[str] = []
    coverage_confidences: set[str] = set()
    has_partial_jurisdictions = False
    for sid in state_ids:
        result = _single_state_legal_pricing(
            sid, org_size, industry, org_type, headcount, jurisdictions
        )
        if result.status == LegalPricingStatus.PRICED:
            per_state_ranges[sid] = result.dollar_range
            if result.coverage_confidence != "NOT_APPLICABLE":
                coverage_confidences.add(result.coverage_confidence)
                if result.partial_state_flag:
                    has_partial_jurisdictions = True
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
        # NOT_APPLICABLE: silently excluded, unchanged from before. Note:
        # this is also why resolve_coverage_gate()'s CONFIRMED-branch
        # partial_state_flag can never surface here -- that branch only sets
        # partial_state_flag=True when applies=False, and applies=False on a
        # Cluster 1/2/4b state always resolves to status=NOT_APPLICABLE
        # above, so the signal is discarded right here. The only reachable
        # path to has_partial_jurisdictions=True in this aggregate is
        # FEDERAL_FALLBACK, whose partial_state_flag is set unconditionally
        # regardless of applies (confirmed live, 2026-09-08: built_to_fail +
        # jurisdictions=["TX"] (PARTIAL only, no CONFIRMED jurisdiction) ->
        # coverage_basis="federal_baseline", has_partial_jurisdictions=true).

    has_unpriced_conditions = bool(unpriced_state_ids)

    # coverage_basis: excludes NOT_APPLICABLE entirely (a state priced only
    # via Clusters 3/4a/4c/5 never asked the coverage question, so it
    # contributes nothing to this determination). None when no PRICED
    # result ever consulted the coverage gate at all.
    if not coverage_confidences:
        coverage_basis = None
    elif coverage_confidences == {"CONFIRMED"}:
        coverage_basis = "state_specific"
    elif coverage_confidences == {"FEDERAL_FALLBACK"}:
        coverage_basis = "federal_baseline"
    else:
        coverage_basis = "mixed"

    if not per_state_ranges:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "band": _legal_exposure_band(None),
            "has_unpriced_conditions": has_unpriced_conditions,
            "unpriced_state_ids": unpriced_state_ids,
            "coverage_basis": coverage_basis,
            "has_partial_jurisdictions": has_partial_jurisdictions,
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
            "coverage_basis": coverage_basis,
            "has_partial_jurisdictions": has_partial_jurisdictions,
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
        "coverage_basis": coverage_basis,
        "has_partial_jurisdictions": has_partial_jurisdictions,
    }
