"""
PRV3 Scoring Engine -- Output Layer
Friction Tax Computation (two-channel rebuild, Stage 4)

prompts/friction-tax-rebuild-build-spec.md and its Phase 0 addendum. Replaces the
grid x org-type scalar x state fraction x breadth x severity model, which had no
cited magnitude, with two dollar channels built from cited inputs:

  Engagement  P x max(0, E_bp - E_us) x 0.18   (7.02 percent of payroll)
  Turnover    P x q x 0.42 x 0.333             (q = JOLTS monthly quits rate x 12)

P = headcount x W, W = BLS OEWS May 2025 all-occupation mean wage for the engine
industry (_INDUSTRY_WAGE_DATA). Identified states only switch channels on (a state
criterion score above 0, engine/data/state_criteria.py), channels never stack or
scale by state count, severity does not move the figure, and the result is a point
estimate. Decision time is a written receipt with no dollar value. Legal/Compliance
is a separate mechanism below and reads _LEGAL_WAGE_DATA_MAY2023, not the refreshed
wages.

Source research and decisions 1 to 18: prompts/friction-tax-rebuild-source-
verification.md. Headcount guard: N must be an int or float, not a bool, finite and
at least 2, anything else is uncalibrated. At the 1,000 intake cap dollars are
withheld and only percent of payroll is shown.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional

from engine.data.jurisdiction import JURISDICTION_TABLE
from engine.data.state_criteria import STATE_CRITERIA

_logger = logging.getLogger(__name__)


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
    "Manufacturing",
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
# citation. Read by Legal (cluster 3 affected-worker math) and
# resolve_headcount_bucket(), no longer by the friction figure.

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


# FROZEN COPY, read ONLY by Legal/Compliance (friction tax rebuild, R1, Pete
# 2026-09-30). Legal's Ohio compensatory-damages formula
# (_oh_compensatory_damages_pricing) prices off this May 2023 table, and Legal
# outputs must stay byte-identical to the Phase 0 baseline
# (tools/capture_legal_baseline.py --check) while friction wages move to May
# 2025 in _INDUSTRY_WAGE_DATA below. Do not edit these values. Moving Legal to
# May 2025 wages is a separate future decision that deliberately changes the
# Legal baseline, not part of the friction rebuild.
#
# Real BLS OEWS May 2023 mean annual wage figures, by industry, as
# (wage, source, citation_id) tuples. 6 are single-sector lookups; 2
# (Retail & Hospitality, Nonprofit & Education) are employment-weighted
# means across multiple real BLS components, documented plainly below
# rather than presented as a single sector pull.
_LEGAL_WAGE_DATA_MAY2023: dict[str, tuple[float, str, str]] = {
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
    "Manufacturing": (
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

# BLS OEWS May 2025 mean annual wage W by engine industry, as (wage, source,
# citation_id) tuples. Each is the employment-weighted mean of the 3-digit NAICS
# all-occupation A_MEAN values over the industry mapping committed in
# prompts/friction-tax-rebuild-source-verification.md Section 2b, with the
# privately owned rows for NAICS 611 and 622 (Decision 12). Files: oesm25in4.zip,
# nat3d_M2025_dl.xlsx and nat3d_owner_M2025_dl.xlsx. Verified against the primary
# files 2026-09-30 (all 11 match prompts/friction-tax-rebuild-build-spec.md
# Section 3). Read by get_industry_wage() and compute_friction_tax(),
# NOT by Legal/Compliance, which reads _LEGAL_WAGE_DATA_MAY2023 above.
_INDUSTRY_WAGE_DATA: dict[str, tuple[float, str, str]] = {
    "Professional Services": (
        108640.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS 541 (Professional, Scientific, and Technical "
        "Services). Total employment 10,800,470. Recomputed and re-verified "
        "against the primary file on 2026-09-30. Mean annual wage: $108,640.",
        "BLS_OEWS_2025_naics3_541",
    ),
    "Healthcare & Life Sciences": (
        70969.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS 621, 622, 623 and 624. Total employment 22,889,480. "
        "Recomputed and re-verified against the primary file on 2026-09-30. "
        "NAICS 622 uses the privately owned rows (OWN_CODE 5) from "
        "nat3d_owner_M2025_dl.xlsx (5,570,850 employees at $89,460), state and "
        "local hospitals excluded (Decision 12). Mean annual wage: $70,969.",
        "BLS_OEWS_2025_hc_621_624_private622",
    ),
    "Financial Services": (
        100842.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS sector 52 (Finance and Insurance). Total employment "
        "6,281,650. Recomputed and re-verified against the primary file on "
        "2026-09-30. Mean annual wage: $100,842.",
        "BLS_OEWS_2025_naics2_52",
    ),
    "Technology": (
        115030.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS sector 51 (Information). Total employment 2,879,630. "
        "Recomputed and re-verified against the primary file on 2026-09-30. "
        "Sector 51 is broader than ideal for a Technology label (includes "
        "telecom, broadcasting, publishing), carried over from the May 2023 "
        "entry. Mean annual wage: $115,030.",
        "BLS_OEWS_2025_sector51_information",
    ),
    "Manufacturing": (
        69131.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS sectors 31-33. Total employment 12,654,340. "
        "Recomputed and re-verified against the primary file on 2026-09-30. "
        "Mean annual wage: $69,131.",
        "BLS_OEWS_2025_naics2_31-33",
    ),
    "Retail & Hospitality": (
        42024.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS sectors 44-45 plus 721 (Accommodation) and 722 (Food "
        "Services and Drinking Places). Total employment 29,780,010. Recomputed "
        "and re-verified against the primary file on 2026-09-30. 721 carries "
        "ownership code 57 with no privately owned row published, left as "
        "published and disclosed. Mean annual wage: $42,024.",
        "BLS_OEWS_2025_retail_hospitality_weighted",
    ),
    "Nonprofit & Education": (
        72765.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS 611 (privately owned rows, OWN_CODE 5, from "
        "nat3d_owner_M2025_dl.xlsx: 3,344,880 employees at $73,400) plus 813 "
        "(1,429,400 employees at $71,280). Total employment 4,774,280. "
        "Recomputed and re-verified against the primary file on 2026-09-30. "
        "State and local schools are excluded (Decision 12). Mean annual wage: "
        "$72,765.",
        "BLS_OEWS_2025_nonprofit_education_611private_813",
    ),
    "Government & Public Sector": (
        80290.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over the OEWS government designation (999000, all ownership). "
        "Total employment 10,242,890. Recomputed and re-verified against the "
        "primary file on 2026-09-30. Federal, state and local government "
        "excluding state and local schools, hospitals and the Postal Service. "
        "Mean annual wage: $80,290.",
        "BLS_OEWS_2025_sector99_government",
    ),
    "Construction": (
        72146.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS sector 23. Total employment 8,298,380. Recomputed "
        "and re-verified against the primary file on 2026-09-30. Mean annual "
        "wage: $72,146.",
        "BLS_OEWS_2025_naics2_23",
    ),
    "Transportation & Warehousing": (
        64331.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS sectors 48-49. Total employment 7,448,650. "
        "Recomputed and re-verified against the primary file on 2026-09-30. 491 "
        "(Postal Service) is a federal ownership row with no private row "
        "published, left as published and disclosed. Mean annual wage: $64,331.",
        "BLS_OEWS_2025_naics2_48-49",
    ),
    "Other": (
        67977.0,
        "BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, "
        "3-digit NAICS, all occupations 00-0000), employment-weighted mean of "
        "A_MEAN over NAICS sectors 11, 21, 22, 42, 53, 55, 56 and 71, plus 811 "
        "and 812 (sector 81 less 813). Total employment 27,796,970. Recomputed "
        "and re-verified against the primary file on 2026-09-30. 713 carries "
        "ownership code 57 with no privately owned row published, left as "
        "published and disclosed. Mean annual wage: $67,977.",
        "BLS_OEWS_2025_other_residual",
    ),
}

def get_industry_wage(industry: str) -> Optional[float]:
    """
    Public accessor for _INDUSTRY_WAGE_DATA's per-employee mean annual wage
    (BLS OEWS May 2025), keyed by the same 11 industry categories intake
    already collects (engine/data/intake.py INTAKE_FIELDS["industry"]).
    Returns None on an unrecognized industry -- matches this file's
    existing lookup convention (dict .get(), not an exception). Category D
    (free condensed diagnostic) reads it through api/engine.py, and
    compute_friction_tax() reads the same table for W.
    """
    entry = _INDUSTRY_WAGE_DATA.get(industry)
    return entry[0] if entry is not None else None


def condensed_departure_cost(industry: str) -> dict:
    """
    The condensed diagnostic's cost of one departure, a single value: the industry
    wage (OEWS May 2025, get_industry_wage) x TURNOVER_COST_SHARE (0.333, Work
    Institute, 2017 Retention Report). Replaces the 0.50 to 0.75 range. amount is
    None for an unrecognized industry (get_industry_wage returns None), never an
    exception. Shown only behind FRICTION_DOLLARS_VISIBLE on the web.
    """
    wage = get_industry_wage(industry) if isinstance(industry, str) else None
    return {
        "amount": round(wage * TURNOVER_COST_SHARE, 2) if wage is not None else None,
        "currency": "USD",
    }


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


# -- Friction tax: two dollar channels -------------------------------------------
# Inputs, vintages and decisions: prompts/friction-tax-rebuild-source-
# verification.md Section 5 and decisions 1 to 18, build spec Section 2.

# Engagement channel. 0.70 is the average engaged share in Gallup's best-practice
# organizations and 0.31 the U.S. engaged share, both from the Gallup Global
# Indicator: Employee Engagement (gallup.com/394373). 0.18 of salary is Gallup's
# cost of a not-engaged employee (2020 article, "Increase Productivity at the
# Lowest Possible Cost"). Decision 18 prices the gap to best practice, not full
# engagement.
ENGAGEMENT_BEST_PRACTICE: float = 0.70
ENGAGEMENT_US: float = 0.31
NOT_ENGAGED_COST_SHARE: float = 0.18

# Turnover channel. 0.42 is the Gallup preventable share of voluntary exits (July
# 2024, self-reported by leavers). 0.333 is the Work Institute cost per voluntary
# exit as a share of salary (2017 Retention Report, low-wage derivation).
TURNOVER_PREVENTABLE_SHARE: float = 0.42
TURNOVER_COST_SHARE: float = 0.333

# Intake clamps headcount to 1 through 1,000 (web/components/DiagnosticFlow.tsx),
# so an organization of 1,000 or more is priced as 1,000 and its dollars would be
# understated. At or above the cap only percent of payroll is returned
# (Decisions 15 and 17). A solo principal has no workforce the sources measure.
INTAKE_HEADCOUNT_CAP: int = 1000
MIN_PRICED_HEADCOUNT: int = 2

# BLS JOLTS Table 22, annual average quits rate, 2025 column, stored as the
# rounded 2-decimal MONTHLY rate in percent (R3). The table's own footnote defines
# it as an average monthly rate, so q = monthly x 12 / 100. Two rows are weighted
# by OEWS May 2025 employment and rounded to 2 decimals. Verified against the
# primary release on 2026-09-30.
QUITS_MONTHLY_RATE_2025: dict[str, tuple[float, str]] = {
    "Professional Services": (2.30, "JOLTS Table 22, Professional and business services"),
    "Healthcare & Life Sciences": (2.00, "JOLTS Table 22, Health care and social assistance"),
    "Financial Services": (1.30, "JOLTS Table 22, Finance and insurance"),
    "Technology": (1.30, "JOLTS Table 22, Information"),
    "Manufacturing": (1.40, "JOLTS Table 22, Manufacturing"),
    "Retail & Hospitality": (
        3.37,
        "JOLTS Table 22, Retail trade 2.6 and Accommodation and food services 4.2 "
        "weighted by OEWS May 2025 employment (15,503,420 and 14,276,590)",
    ),
    "Nonprofit & Education": (
        1.64,
        "JOLTS Table 22, Private educational services 1.4 and Other services 2.2 "
        "(standing in for NAICS 813) weighted by OEWS May 2025 employment "
        "(3,344,880 and 1,429,400)",
    ),
    "Government & Public Sector": (0.80, "JOLTS Table 22, Government"),
    "Construction": (1.80, "JOLTS Table 22, Construction"),
    "Transportation & Warehousing": (
        2.20, "JOLTS Table 22, Transportation, warehousing, and utilities",
    ),
    "Other": (2.20, "JOLTS Table 22, Total private (Decision 9)"),
}

# Wording the surfaces must carry (build spec Section 2 framing rule). The total
# reads as what organizations like the client typically lose, the engagement line
# as the gap to the best-run ones. Neither reads as normal or acceptable, and the
# comparison is never full engagement.
FRICTION_FRAMING_TOTAL = "what organizations like yours typically lose"
FRICTION_FRAMING_ENGAGEMENT_GAP = "the gap between organizations like yours and the best-run ones"

# Decision-time receipt (no dollar value). McKinsey, "Decision making in the age of
# urgency", April 2019, survey Feb 2018, n=1,259.
DECISION_TIME_SHARE_OF_TIME: float = 0.37
DECISION_TIME_INEFFECTIVE_SHARE: float = 0.58


def _priceable_headcount(org_size) -> Optional[float]:
    """The headcount when it can be priced, else None. Must be an int or float,
    not a bool (bool is an int subclass), finite and at least 2. Strings, None,
    NaN, infinity, zero, negatives and 1 return None. No bucket fallback."""
    if isinstance(org_size, bool) or not isinstance(org_size, (int, float)):
        return None
    if org_size != org_size or org_size in (float("inf"), float("-inf")):
        return None
    if org_size < MIN_PRICED_HEADCOUNT:
        return None
    return org_size


def _channel_inputs(rate_inputs: list, headcount, wage, withheld: bool, industry: str) -> list:
    inputs = list(rate_inputs)
    if not withheld:
        inputs.append({
            "name": f"Average annual wage, {industry}", "value": wage,
            "source": "BLS OEWS national industry file, all occupations",
            "vintage": "May 2025",
        })
        inputs.append({
            "name": "Employees", "value": headcount, "source": "Intake", "vintage": "this session",
        })
    return inputs


def compute_friction_tax(state_ids: list[str], org_size, industry: str) -> dict:
    """
    The typical friction cost for a state set, as two dollar channels.

    state_ids: identified state ids. org_size: IntakeData.headcount. industry:
    IntakeData.industry.

    Returns:
      {
        "calibration_complete": bool,   # True only when "estimate" is not None
        "currency": "USD",
        "estimate": {"currency", "typical_baseline": {"total": {"amount",
                     "percent_of_payroll"}, "channels": [{"channel", "amount",
                     "percent_of_payroll", "inputs": [{"name", "value", "source",
                     "vintage"}]}]}, "excess": None} or None,
        "channels_on": ["engagement", "turnover"] subset, in that order,
        "decision_time_receipt": bool,  # any state scores above 0 on decision_quality
        "headcount": the priced headcount or None,
        "wage": W or None,
        "payroll": P or None,           # None at the cap
        "amounts_withheld": bool,       # True at or above the intake cap
        "annual_quit_rate_percent": float or None,
      }

    percent_of_payroll is on every channel and the total whenever the estimate is
    not None. amount is None at or above INTAKE_HEADCOUNT_CAP. The estimate is None
    when a state id is unknown, the headcount cannot be priced, the industry is not
    recognized, or no identified state switches on a dollar channel (for example
    only paper_shield). A channel is on when any identified state scores above 0 on
    its criterion, and channels are never stacked or scaled by state count.
    Severity is not an input.
    """
    criteria = [STATE_CRITERIA.get(sid) for sid in state_ids]
    states_ok = bool(state_ids) and all(c is not None for c in criteria)
    engagement_on = states_ok and any(c.productivity > 0 for c in criteria)
    turnover_on = states_ok and any(c.turnover > 0 for c in criteria)
    decision_time_on = states_ok and any(c.decision_quality > 0 for c in criteria)
    channels_on = [n for n, on in (("engagement", engagement_on), ("turnover", turnover_on)) if on]

    headcount = _priceable_headcount(org_size)
    wage = get_industry_wage(industry)
    quits = QUITS_MONTHLY_RATE_2025.get(industry)
    result = {
        "calibration_complete": False,
        "currency": "USD",
        "estimate": None,
        "channels_on": channels_on,
        "decision_time_receipt": decision_time_on,
        "headcount": headcount,
        "wage": wage,
        "payroll": None,
        "amounts_withheld": False,
        "annual_quit_rate_percent": None,
    }
    if not states_ok or headcount is None or wage is None or quits is None or not channels_on:
        return result

    withheld = headcount >= INTAKE_HEADCOUNT_CAP
    payroll = headcount * wage
    q = quits[0] * 12 / 100
    result["annual_quit_rate_percent"] = round(q * 100, 4)
    result["amounts_withheld"] = withheld
    result["payroll"] = None if withheld else payroll

    channels = []
    total_fraction = 0.0
    total_amount = 0.0

    def add(channel: str, fraction: float, rate_inputs: list) -> None:
        nonlocal total_fraction, total_amount
        raw_amount = payroll * fraction
        total_fraction += fraction
        total_amount += raw_amount
        channels.append({
            "channel": channel,
            "amount": None if withheld else round(raw_amount, 2),
            "percent_of_payroll": round(fraction * 100, 4),
            "inputs": _channel_inputs(rate_inputs, headcount, wage, withheld, industry),
        })

    if engagement_on:
        gap = max(0.0, ENGAGEMENT_BEST_PRACTICE - ENGAGEMENT_US)
        add("engagement", gap * NOT_ENGAGED_COST_SHARE, [
            {"name": "Engaged share in best-practice organizations", "value": ENGAGEMENT_BEST_PRACTICE,
             "source": "Gallup Global Indicator: Employee Engagement (gallup.com/394373)", "vintage": "2025"},
            {"name": "Engaged share of U.S. employees", "value": ENGAGEMENT_US,
             "source": "Gallup Global Indicator: Employee Engagement (gallup.com/394373)", "vintage": "May 2026"},
            {"name": "Cost of a not-engaged employee, share of salary", "value": NOT_ENGAGED_COST_SHARE,
             "source": "Gallup, Increase Productivity at the Lowest Possible Cost", "vintage": "2020"},
        ])
    if turnover_on:
        add("turnover", q * TURNOVER_PREVENTABLE_SHARE * TURNOVER_COST_SHARE, [
            {"name": "Annual quits rate", "value": round(q, 6),
             "source": quits[1] + ", monthly rate x 12", "vintage": "2025"},
            {"name": "Preventable share of voluntary exits", "value": TURNOVER_PREVENTABLE_SHARE,
             "source": "Gallup, 42% of Employee Turnover Is Preventable but Often Ignored (self-reported by leavers)",
             "vintage": "July 2024"},
            {"name": "Cost of a voluntary exit, share of salary", "value": TURNOVER_COST_SHARE,
             "source": "Work Institute Retention Report (low-wage derivation applied to all salaries)",
             "vintage": "2017"},
        ])

    result["estimate"] = {
        "currency": "USD",
        "typical_baseline": {
            "total": {
                "amount": None if withheld else round(total_amount, 2),
                "percent_of_payroll": round(total_fraction * 100, 4),
            },
            "channels": channels,
        },
        "excess": None,
    }
    result["calibration_complete"] = True
    return result


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
    "Manufacturing": 0.557,
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
# STATE_CRITERIA[state_id].legal (engine/data/state_criteria.py).

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
    assert _lc_sid in STATE_CRITERIA, (
        f"LEGAL_COMPLIANCE_CLUSTER references unknown state {_lc_sid!r}"
    )
    _lc_score = STATE_CRITERIA[_lc_sid].legal
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
    itself before this build.

    may_overstate_for_uncollected_net_worth (Priority Queue item 9,
    this session -- Ohio's R.C. 2315.21 compensatory-damages build) is
    the opposite direction from is_floor, deliberately kept as its own
    field rather than an inverted reuse of is_floor: the small-employer/
    individual-defendant branch's real statutory cap is
    min(2x compensatory, 10% of net worth, $350,000), but net_worth
    isn't collected at intake, so this codebase computes
    min(2x compensatory, $350,000) -- a figure that can be HIGHER than
    the real cap for a low-net-worth organization, not lower. Reusing
    is_floor here (even inverted) would make one field mean opposite
    things depending on which branch set it. False by default so every
    pre-existing construction site needs no change; set True only by
    Ohio's small-employer branch. Not yet consumed by any output layer
    -- same "no consumer yet" status is_floor itself already carries;
    UI-facing framing is explicitly out of scope for this build.

    specific_caveat_jurisdiction (is_floor scoping follow-up, this
    session) is the 2-letter jurisdiction id that drove a
    state_specific_flat or state_specific_tiers result, when one of
    the two has a specific, verified caveat sentence written for it
    (contract.py's _SPECIFIC_CAVEAT_TEXT) -- None otherwise, including
    for jurisdictions in those two categories with no specific caveat
    written. An identifier only, not prose -- same convention as every
    other field here; the actual sentences live in contract.py.
    """
    status: LegalPricingStatus
    dollar_range: Optional[tuple[float, float]]
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool
    is_floor: bool = False
    may_overstate_for_uncollected_net_worth: bool = False
    specific_caveat_jurisdiction: Optional[str] = None


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
    _single_state_legal_pricing()'s Cluster 4 branch.
    may_overstate_for_uncollected_net_worth carries the same meaning as
    LegalPricingResult's own field of that name (Priority Queue item 9,
    this session) -- forwarded the same way, for Ohio's Cluster 4b
    small-employer branch specifically. specific_caveat_jurisdiction
    carries the same meaning as LegalPricingResult's own field of that
    name -- forwarded the same way, into the Cluster 4 dispatch's
    final LegalPricingResult."""
    curve: Optional[LegalDollarCurve]
    status: LegalPricingStatus
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool
    is_floor: bool = False
    may_overstate_for_uncollected_net_worth: bool = False
    specific_caveat_jurisdiction: Optional[str] = None


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
        # 5 M.R.S. Sec4613(2)(B)(7) and (8) are TWO SEPARATE remedies,
        # not one joint provision -- confirmed directly against
        # mainelegislature.org this session, current through Oct. 1,
        # 2025 (last amended PL 2023, c. 263, Sec1). Corrects this
        # entry's own prior citation, which cited them jointly as
        # "(7)-(8)" -- that conflation is fixed in the citation field
        # below.
        #
        # (7): "civil penal damages" (not traditional compensatory/
        # punitive) for non-employment cases, or employment cases with
        # <=14 employees, tiered by VIOLATION ORDER, not headcount --
        # $20,000 (1st order) / $50,000 (2nd order) / $100,000 (3rd+
        # order).
        #
        # (8)(e)(i)-(iv): the real employment tier table, for
        # "intentional employment discrimination with respondents who
        # have more than 14 employees" (15+), tiered by HEADCOUNT --
        # $100,000 (15-100) / $300,000 (101-200) / $500,000 (201-500) /
        # $1,000,000 (501+). Corrects this entry's own prior comment,
        # which stated the top bracket as "$500,000" -- that was the
        # 201-500 tier's own figure, not the true 501+ ceiling; the
        # prior verification pass stopped one tier short.
        #
        # Two unmodeled carve-outs, stated by the statute itself, not
        # invented -- is_floor=True (already automatic for every
        # state_specific_tiers state) is the existing caveat mechanism
        # for both, same "may understate the real answer" semantics
        # TX's own is_floor=True already carries for its claim-type
        # carve-out:
        #   (8)(f): this cap does NOT limit recovery under 42 U.S.C.
        #   Sec1981, which has no statutory cap of its own -- real
        #   potential for a complaining party's actual recovery to
        #   exceed this table's figure via stacking.
        #   (8)(h): the tier caps do not apply to claims unlawful
        #   solely due to disparate impact.
        damages_cap_treatment="state_specific_tiers",
        confidence="CONFIRMED",
        citation="Maine Human Rights Act, 5 M.R.S. §4572; §4613(2)(B)(7) (civil penal damages, non-employment/<=14-employee cases, a distinct provision); §4613(2)(B)(8) (employment tier table, 15+ employees).",
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
        # H.B. 352 (Employment Law Uniformity Act), eff. Apr. 15, 2021,
        # codified Ohio's Tort Reform Act caps onto R.C. ch. 4112 claims.
        # General employer: punitive damages capped at 2x compensatory
        # damages, no dollar ceiling, no net-worth alternative (R.C.
        # 2315.21(D)(2)). Small employer (<=100 FT employees, or <=500 if
        # NAICS-manufacturing-classified) or individual defendant: capped
        # at the LESSER of 2x compensatory OR 10% of net worth at time of
        # tort, up to $350,000 (R.C. 2315.21(D)(2)(b)). Wired to PRICED
        # (Priority Queue item 9, this session) -- see
        # _oh_compensatory_damages_pricing() for the real formula:
        # compensatory base = _LEGAL_WAGE_DATA_MAY2023 x
        # _JURISDICTION_MULTIPLIER_DATA["OH"] (prompts/oh-compensatory-
        # damages-pricing-plan.md). The small-employer/individual-
        # defendant branch omits the "OR 10% of net worth" alternative
        # entirely -- net_worth still isn't collected at intake -- so its
        # computed figure can OVERSTATE the real cap for a low-net-worth
        # organization; flagged via
        # LegalPricingResult.may_overstate_for_uncollected_net_worth, not
        # silently accepted. Small-employer routing (see
        # _oh_is_small_employer()) uses this app's "Manufacturing"
        # industry bucket as an approximation of Ohio's NAICS-
        # manufacturing test. Renamed from "Manufacturing & Industrial"
        # this session (Priority Queue item 10) to close most of the
        # ambiguity flagged here previously -- "Industrial" no longer
        # actively invites mining/utilities orgs into this bucket, since
        # those carry their own separate wage entries under "Other" now.
        # Self-selection accuracy still isn't guaranteed (a business can
        # misjudge its own NAICS classification regardless of label
        # wording); flagged here, not resolved, since no NAICS-level
        # intake data exists to resolve it precisely.
        damages_cap_treatment="state_specific_tiers",
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


def _resolve_flat_cap(jurisdictions: list[str]) -> Optional[tuple[float, str]]:
    """
    (value, winning jurisdiction id) for the MAXIMUM flat_cap among
    CONFIRMED state_specific_flat jurisdictions in the input -- extends
    resolve_damages_treatment()'s own highest-exposure-wins principle
    down to the actual dollar figure, needed because that function
    returns a category string, not a specific state; with more than
    one state_specific_flat jurisdiction selected, something has to
    pick which state's own flat_cap governs.

    Tie-break is MAXIMUM VALUE, not input order -- pre-existing,
    already-shipped behavior (Phase 1 item 4), unchanged by adding the
    jurisdiction id to the return value; the returned jid is whichever
    entry actually produced the returned max value, tracked in the
    same pass, not a separately re-derived identity. Deliberately
    different from _state_specific_tiers_driver()'s first-encountered-
    wins rule below -- the two are governed by different, independently
    proven rules and must not be homogenized.

    None if no CONFIRMED state_specific_flat jurisdiction is present in
    the input, or if one is present but its flat_cap is unpopulated (a
    data gap, not expected once all 4 real flat_cap states are
    populated).
    """
    best: Optional[float] = None
    best_jid: Optional[str] = None
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
            best_jid = jid
    return (best, best_jid) if best is not None else None


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


def _oh_drives_tiers_result(jurisdictions: list[str]) -> bool:
    """
    True only when Ohio is the SPECIFIC jurisdiction
    resolve_damages_treatment() would resolve a state_specific_tiers
    result from -- same re-derivation of that function's own priority
    loop as _co_drives_federal_tier_deferral() above, same reason
    (resolve_damages_treatment() returns only a category string, not
    which jurisdiction won, and a blanket check on the resolved
    treatment string alone would also fire for TX, AR, etc.).

    Unlike CO's helper, this carries no headcount gate -- Ohio's real
    formula applies at every headcount (Priority Queue item 9, this
    session -- previously QUALITATIVE_ONLY at every headcount, before
    that formula was wired in); headcount only selects which of R.C.
    2315.21's two statutory branches would govern (see
    _oh_is_small_employer() below), a question this function doesn't
    answer.

    Same known limitation as _co_drives_federal_tier_deferral(),
    inherited not introduced: a tie between two state_specific_tiers
    jurisdictions resolves by input order, not disambiguated here.
    """
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
    return best_jid == "OH"


def _state_specific_tiers_driver(jurisdictions: list[str]) -> Optional[str]:
    """
    The SPECIFIC jurisdiction resolve_damages_treatment() would resolve
    a state_specific_tiers result from, or None if no state_specific_
    tiers jurisdiction wins (whether none is present, or a higher-
    ranked category -- uncapped or state_specific_flat -- wins
    instead). Same re-derivation of resolve_damages_treatment()'s own
    priority loop as _oh_drives_tiers_result()/
    _co_drives_federal_tier_deferral() above, kept standalone rather
    than consolidated with either -- those two answer a narrower
    yes/no question about one specific state; this one needs the
    actual winning jurisdiction id, for the AR/MD/TN per-state caveat
    lookup (is_floor scoping follow-up, this session).

    Tie-break is FIRST-ENCOUNTERED-IN-INPUT-LIST-WINS, identical to
    the loop this re-derives -- proven directly by the existing
    _oh_drives_tiers_result(['OH','TX']) vs (['TX','OH']) test pair
    (tools/test_friction_tax.py), which this function's own loop shape
    reproduces exactly, not reinvented. Deliberately NOT the same
    tie-break as _resolve_flat_cap() (maximum value, order-
    independent) -- the two are governed by different, independently
    proven rules and must not be homogenized.
    """
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
    if best_jid is None:
        return None
    winning_entry = STATE_COVERAGE_THRESHOLDS[best_jid]
    return best_jid if winning_entry.damages_cap_treatment == "state_specific_tiers" else None


# -- Jurisdiction litigation-risk multiplier (Priority Queue item 9, this
# session's OH compensatory-damages pricing build) --------------------------
# Relative jurisdiction-risk signal derived from EEOC charge-filing
# frequency, normalized by BLS QCEW employment -- explicitly NOT a
# dollar-based settlement/verdict-size signal (that distinction is load-
# bearing, not incidental -- see prompts/oh-compensatory-damages-pricing-
# plan.md's "Decided, 2026-09-15" entry). Multiplier = (state's own EEOC
# Table E1b FY2025 Total Charges / BLS QCEW 2025 Private+State+Local
# employment) / 57.4765 (the size-weighted national aggregate rate across
# all 50 states, not a mean of the 50 state rates), clamped to [0.25, 2.30]
# -- floor grounded in a raw-charge-count reliability gap (WY at 38 charges
# to NE at 157 charges, not a percentile or ratio-value cutoff picked in
# isolation), ceiling grounded in the real non-DC maximum (AR, 2.2691) plus
# headroom, not an arbitrary round number. DC excluded entirely (its rate is
# a structural artifact of ~25% of its employment being federal, excluded
# from this denominator by design -- not sample noise and not reliable
# litigation-risk signal). Full derivation, every intermediate number, and
# the two explicitly-superseded first-pass bounds (0.8-1.2, which clamped
# 40 of 51 jurisdictions): prompts/oh-compensatory-damages-pricing-plan.md.
#
# Currently consumed by Ohio's own R.C. 2315.21 compensatory-damages
# formula only (Stage 2 of this build, _single_state_legal_pricing()) --
# built as a full 50-state table rather than an OH-only value because the
# plan doc's own "Not decided / open" section leaves OH-only-vs-
# jurisdiction-agnostic as a genuine open architecture question for a
# future Gemini pass, not resolved here.

_JURISDICTION_MULTIPLIER_DATA: dict[str, tuple[float, str, str]] = {
    "AK": (
        0.4545,
        "EEOC Table E1b FY2025 Total Charges: 83. BLS QCEW 2025 annual "
        "Private+State+Local employment: 317,705. Rate 26.125 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.4545 raw multiplier. Unclamped, "
        "falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_AK",
    ),
    "AL": (
        1.7777,
        "EEOC Table E1b FY2025 Total Charges: 2,107. BLS QCEW 2025 annual "
        "Private+State+Local employment: 2,062,121. Rate 102.176 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.7777 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_AL",
    ),
    "AR": (
        2.2691,
        "EEOC Table E1b FY2025 Total Charges: 1,675. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,284,297. Rate 130.422 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 2.2691 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_AR",
    ),
    "AZ": (
        1.0623,
        "EEOC Table E1b FY2025 Total Charges: 1,940. BLS QCEW 2025 annual "
        "Private+State+Local employment: 3,177,231. Rate 61.059 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.0623 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_AZ",
    ),
    "CA": (
        0.4601,
        "EEOC Table E1b FY2025 Total Charges: 4,750. BLS QCEW 2025 annual "
        "Private+State+Local employment: 17,962,398. Rate 26.444 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.4601 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_CA",
    ),
    "CO": (
        0.7911,
        "EEOC Table E1b FY2025 Total Charges: 1,290. BLS QCEW 2025 annual "
        "Private+State+Local employment: 2,836,914. Rate 45.472 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.7911 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_CO",
    ),
    "CT": (
        0.3513,
        "EEOC Table E1b FY2025 Total Charges: 338. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,673,769. Rate 20.194 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.3513 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_CT",
    ),
    "DE": (
        1.1356,
        "EEOC Table E1b FY2025 Total Charges: 310. BLS QCEW 2025 annual "
        "Private+State+Local employment: 474,967. Rate 65.268 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 1.1356 raw multiplier. Unclamped, "
        "falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_DE",
    ),
    "FL": (
        1.2098,
        "EEOC Table E1b FY2025 Total Charges: 6,784. BLS QCEW 2025 annual "
        "Private+State+Local employment: 9,756,081. Rate 69.536 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.2098 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_FL",
    ),
    "GA": (
        2.2074,
        "EEOC Table E1b FY2025 Total Charges: 6,064. BLS QCEW 2025 annual "
        "Private+State+Local employment: 4,779,581. Rate 126.873 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 2.2074 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_GA",
    ),
    "HI": (
        0.6223,
        "EEOC Table E1b FY2025 Total Charges: 218. BLS QCEW 2025 annual "
        "Private+State+Local employment: 609,478. Rate 35.768 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.6223 raw multiplier. Unclamped, "
        "falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_HI",
    ),
    "IA": (
        0.3015,
        "EEOC Table E1b FY2025 Total Charges: 267. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,540,614. Rate 17.331 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.3015 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_IA",
    ),
    "ID": (
        0.2500,
        "EEOC Table E1b FY2025 Total Charges: 54. BLS QCEW 2025 annual "
        "Private+State+Local employment: 860,258. Rate 6.277 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.1092 raw multiplier. Clamped at "
        "the 0.25 floor (raw ratio 0.1092) -- fewer than 100 raw EEOC charges for "
        "the fiscal year, below this multiplier's reliability threshold. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_ID",
    ),
    "IL": (
        1.5051,
        "EEOC Table E1b FY2025 Total Charges: 5,180. BLS QCEW 2025 annual "
        "Private+State+Local employment: 5,987,775. Rate 86.510 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.5051 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_IL",
    ),
    "IN": (
        1.0359,
        "EEOC Table E1b FY2025 Total Charges: 1,876. BLS QCEW 2025 annual "
        "Private+State+Local employment: 3,150,977. Rate 59.537 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.0359 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_IN",
    ),
    "KS": (
        0.9388,
        "EEOC Table E1b FY2025 Total Charges: 759. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,406,687. Rate 53.957 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.9388 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_KS",
    ),
    "KY": (
        0.7163,
        "EEOC Table E1b FY2025 Total Charges: 805. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,955,240. Rate 41.171 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.7163 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_KY",
    ),
    "LA": (
        1.2266,
        "EEOC Table E1b FY2025 Total Charges: 1,337. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,896,463. Rate 70.500 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.2266 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_LA",
    ),
    "MA": (
        0.3374,
        "EEOC Table E1b FY2025 Total Charges: 696. BLS QCEW 2025 annual "
        "Private+State+Local employment: 3,589,352. Rate 19.391 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.3374 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_MA",
    ),
    "MD": (
        1.4340,
        "EEOC Table E1b FY2025 Total Charges: 2,146. BLS QCEW 2025 annual "
        "Private+State+Local employment: 2,603,713. Rate 82.421 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.4340 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_MD",
    ),
    "ME": (
        0.2500,
        "EEOC Table E1b FY2025 Total Charges: 58. BLS QCEW 2025 annual "
        "Private+State+Local employment: 633,951. Rate 9.149 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.1592 raw multiplier. Clamped at "
        "the 0.25 floor (raw ratio 0.1592) -- fewer than 100 raw EEOC charges for "
        "the fiscal year, below this multiplier's reliability threshold. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_ME",
    ),
    "MI": (
        0.9937,
        "EEOC Table E1b FY2025 Total Charges: 2,486. BLS QCEW 2025 annual "
        "Private+State+Local employment: 4,352,688. Rate 57.114 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.9937 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_MI",
    ),
    "MN": (
        0.6442,
        "EEOC Table E1b FY2025 Total Charges: 1,078. BLS QCEW 2025 annual "
        "Private+State+Local employment: 2,911,560. Rate 37.025 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.6442 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_MN",
    ),
    "MO": (
        1.3822,
        "EEOC Table E1b FY2025 Total Charges: 2,259. BLS QCEW 2025 annual "
        "Private+State+Local employment: 2,843,602. Rate 79.441 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.3822 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_MO",
    ),
    "MS": (
        1.9724,
        "EEOC Table E1b FY2025 Total Charges: 1,300. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,146,746. Rate 113.364 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.9724 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_MS",
    ),
    "MT": (
        0.2500,
        "EEOC Table E1b FY2025 Total Charges: 37. BLS QCEW 2025 annual "
        "Private+State+Local employment: 498,739. Rate 7.419 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.1291 raw multiplier. Clamped at "
        "the 0.25 floor (raw ratio 0.1291) -- fewer than 100 raw EEOC charges for "
        "the fiscal year, below this multiplier's reliability threshold. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_MT",
    ),
    "NC": (
        1.5271,
        "EEOC Table E1b FY2025 Total Charges: 4,266. BLS QCEW 2025 annual "
        "Private+State+Local employment: 4,860,387. Rate 87.771 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.5271 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_NC",
    ),
    "ND": (
        0.4096,
        "EEOC Table E1b FY2025 Total Charges: 99. BLS QCEW 2025 annual "
        "Private+State+Local employment: 420,491. Rate 23.544 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.4096 raw multiplier. Unclamped, "
        "falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_ND",
    ),
    "NE": (
        0.2720,
        "EEOC Table E1b FY2025 Total Charges: 157. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,004,397. Rate 15.631 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.2720 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_NE",
    ),
    "NH": (
        0.2500,
        "EEOC Table E1b FY2025 Total Charges: 82. BLS QCEW 2025 annual "
        "Private+State+Local employment: 680,142. Rate 12.056 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.2098 raw multiplier. Clamped at "
        "the 0.25 floor (raw ratio 0.2098) -- fewer than 100 raw EEOC charges for "
        "the fiscal year, below this multiplier's reliability threshold. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_NH",
    ),
    "NJ": (
        0.6447,
        "EEOC Table E1b FY2025 Total Charges: 1,569. BLS QCEW 2025 annual "
        "Private+State+Local employment: 4,234,240. Rate 37.055 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.6447 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_NJ",
    ),
    "NM": (
        1.0376,
        "EEOC Table E1b FY2025 Total Charges: 505. BLS QCEW 2025 annual "
        "Private+State+Local employment: 846,777. Rate 59.638 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 1.0376 raw multiplier. Unclamped, "
        "falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_NM",
    ),
    "NV": (
        1.5698,
        "EEOC Table E1b FY2025 Total Charges: 1,396. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,547,223. Rate 90.226 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.5698 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_NV",
    ),
    "NY": (
        0.7427,
        "EEOC Table E1b FY2025 Total Charges: 4,132. BLS QCEW 2025 annual "
        "Private+State+Local employment: 9,679,488. Rate 42.688 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.7427 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_NY",
    ),
    "OH": (
        0.9228,
        "EEOC Table E1b FY2025 Total Charges: 2,892. BLS QCEW 2025 annual "
        "Private+State+Local employment: 5,452,486. Rate 53.040 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.9228 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_OH",
    ),
    "OK": (
        1.0597,
        "EEOC Table E1b FY2025 Total Charges: 1,004. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,648,462. Rate 60.905 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.0597 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_OK",
    ),
    "OR": (
        0.3596,
        "EEOC Table E1b FY2025 Total Charges: 405. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,959,447. Rate 20.669 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.3596 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_OR",
    ),
    "PA": (
        1.3832,
        "EEOC Table E1b FY2025 Total Charges: 4,732. BLS QCEW 2025 annual "
        "Private+State+Local employment: 5,952,205. Rate 79.500 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.3832 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_PA",
    ),
    "RI": (
        0.6598,
        "EEOC Table E1b FY2025 Total Charges: 185. BLS QCEW 2025 annual "
        "Private+State+Local employment: 487,812. Rate 37.924 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.6598 raw multiplier. Unclamped, "
        "falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_RI",
    ),
    "SC": (
        0.8969,
        "EEOC Table E1b FY2025 Total Charges: 1,177. BLS QCEW 2025 annual "
        "Private+State+Local employment: 2,283,169. Rate 51.551 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.8969 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_SC",
    ),
    "SD": (
        0.4689,
        "EEOC Table E1b FY2025 Total Charges: 121. BLS QCEW 2025 annual "
        "Private+State+Local employment: 449,014. Rate 26.948 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.4689 raw multiplier. Unclamped, "
        "falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_SD",
    ),
    "TN": (
        1.5951,
        "EEOC Table E1b FY2025 Total Charges: 2,942. BLS QCEW 2025 annual "
        "Private+State+Local employment: 3,209,041. Rate 91.678 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.5951 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_TN",
    ),
    "TX": (
        1.1726,
        "EEOC Table E1b FY2025 Total Charges: 9,360. BLS QCEW 2025 annual "
        "Private+State+Local employment: 13,887,434. Rate 67.399 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.1726 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_TX",
    ),
    "UT": (
        0.4174,
        "EEOC Table E1b FY2025 Total Charges: 408. BLS QCEW 2025 annual "
        "Private+State+Local employment: 1,700,830. Rate 23.988 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.4174 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_UT",
    ),
    "VA": (
        1.2152,
        "EEOC Table E1b FY2025 Total Charges: 2,767. BLS QCEW 2025 annual "
        "Private+State+Local employment: 3,961,540. Rate 69.847 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 1.2152 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_VA",
    ),
    "VT": (
        0.2500,
        "EEOC Table E1b FY2025 Total Charges: 30. BLS QCEW 2025 annual "
        "Private+State+Local employment: 301,478. Rate 9.951 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.1731 raw multiplier. Clamped at "
        "the 0.25 floor (raw ratio 0.1731) -- fewer than 100 raw EEOC charges for "
        "the fiscal year, below this multiplier's reliability threshold. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_VT",
    ),
    "WA": (
        0.8512,
        "EEOC Table E1b FY2025 Total Charges: 1,724. BLS QCEW 2025 annual "
        "Private+State+Local employment: 3,523,948. Rate 48.922 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.8512 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_WA",
    ),
    "WI": (
        0.5979,
        "EEOC Table E1b FY2025 Total Charges: 1,002. BLS QCEW 2025 annual "
        "Private+State+Local employment: 2,915,609. Rate 34.367 per 100,000, "
        "divided by the 57.4765 national aggregate rate = 0.5979 raw multiplier. "
        "Unclamped, falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_WI",
    ),
    "WV": (
        0.3429,
        "EEOC Table E1b FY2025 Total Charges: 132. BLS QCEW 2025 annual "
        "Private+State+Local employment: 669,784. Rate 19.708 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.3429 raw multiplier. Unclamped, "
        "falls inside the 0.25 to 2.30 band. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_WV",
    ),
    "WY": (
        0.2500,
        "EEOC Table E1b FY2025 Total Charges: 38. BLS QCEW 2025 annual "
        "Private+State+Local employment: 274,439. Rate 13.846 per 100,000, divided "
        "by the 57.4765 national aggregate rate = 0.2409 raw multiplier. Clamped at "
        "the 0.25 floor (raw ratio 0.2409) -- fewer than 100 raw EEOC charges for "
        "the fiscal year, below this multiplier's reliability threshold. See "
        "prompts/oh-compensatory-damages-pricing-plan.md, Appendix (finalized "
        "2026-09-15e), for full derivation.",
        "EEOC_QCEW_2025_WY",
    ),
}


def _oh_is_small_employer(headcount, industry: str) -> bool:
    """
    Ohio's own small-employer/individual-defendant gate, R.C.
    2315.21(D)(2)(b): <=100 full-time employees generally, <=500 if
    NAICS-manufacturing-classified. Uses this app's "Manufacturing"
    INTAKE_FIELDS["industry"] bucket as an approximation of the real
    NAICS test. Renamed from "Manufacturing & Industrial" this session
    (Priority Queue item 10) specifically to close the ambiguity this
    docstring used to flag here: the word "Industrial" no longer
    actively invites mining/utilities orgs (which carry their own
    separate wage entries under "Other") to self-select into this
    bucket. Still not a guarantee -- a business can misjudge its own
    NAICS classification regardless of label wording, so self-selection
    accuracy against the real NAICS 31-33 test remains approximate,
    just no longer actively misleading. No NAICS-level intake data
    exists to resolve this precisely; flagged here and in
    STATE_COVERAGE_THRESHOLDS["OH"]'s own citation comment, not
    resolved by this helper.

    Non-numeric headcount (unclassifiable input) returns False -- the
    general branch's statutory mechanics are the more conservative
    default to name when headcount can't be confirmed at all.

    Called by _oh_compensatory_damages_pricing() (Priority Queue item 9,
    this session) to route between R.C. 2315.21's two branches, now that
    a real compensatory-damages base exists (_JURISDICTION_MULTIPLIER_DATA
    x _LEGAL_WAGE_DATA_MAY2023) for both branches to apply their multiplier
    to. Previously deliberately uncalled -- both branches resolved to
    the identical QUALITATIVE_ONLY LegalPricingResult, so invoking this
    helper would have computed a real answer and then discarded it.
    """
    if not isinstance(headcount, (int, float)):
        return False
    if headcount <= 100:
        return True
    return industry == "Manufacturing" and headcount <= 500


# R.C. 2315.21(D)(2)(b) -- the small-employer/individual-defendant hard
# ceiling. Confirmed real statutory figure, not a placeholder.
_OH_SMALL_EMPLOYER_CAP: float = 350_000.0


def _oh_compensatory_damages_pricing(
    industry: str,
    headcount,
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"],
    partial_state_flag: bool,
) -> LegalPricingResult:
    """
    Ohio's own R.C. 2315.21 compensatory-damages formula (Priority Queue
    item 9, this session). Shared by all three call sites that can reach
    Ohio's state_specific_tiers treatment -- Clusters 1, 2, and 4b (via
    _cluster_4_curve_for_org_type(), which wraps this into a flat
    LegalDollarCurve -- see that call site) -- since the underlying legal
    question (which of R.C. 2315.21's two branches applies, and for how
    much) doesn't depend on which Legal-scoring taxonomy state triggered
    the check.

    compensatory_base = _LEGAL_WAGE_DATA_MAY2023[industry]'s real BLS OEWS wage
    x _JURISDICTION_MULTIPLIER_DATA["OH"]'s EEOC/QCEW-derived litigation-
    risk multiplier (prompts/oh-compensatory-damages-pricing-plan.md).
    "OH" is hardcoded, not looked up from a jurisdictions list -- this
    function is only ever reached once _oh_drives_tiers_result() has
    already confirmed Ohio specifically governs, so the multiplier for
    the governing jurisdiction is always Ohio's own.

    General employer (_oh_is_small_employer() False): 2x compensatory,
    uncapped -- is_floor=True, standard semantics (this figure may
    understate the real answer, same as every other "uncapped" treatment
    in this file).

    Small employer/individual defendant (True): 2x compensatory, hard-
    capped at _OH_SMALL_EMPLOYER_CAP. The real statutory cap is
    min(2x compensatory, 10% of net worth, $350,000) -- net_worth isn't
    collected at intake, so this omits that third term entirely. The
    result is is_floor=False (this is a hard ceiling, not a floor) AND
    may_overstate_for_uncollected_net_worth=True (a low-net-worth
    organization's real cap could be lower than what's computed here --
    the opposite direction from every other is_floor=True caveat in this
    file, which is exactly why this is its own field, not a reused one).

    coverage_confidence/partial_state_flag are threaded through from the
    caller's own already-resolved coverage gate (or Cluster 4b's own
    lookup) rather than hardcoded to "NOT_APPLICABLE"/False -- the prior
    QUALITATIVE_ONLY early-returns this replaces discarded that real
    information because there was no dollar figure to caveat with it;
    now that this is PRICED, every other PRICED branch in this function
    threads it through, and Ohio shouldn't be the one exception.

    Returns DATA_INTEGRITY_GAP if industry isn't a recognized
    _LEGAL_WAGE_DATA_MAY2023 key -- should never happen against real
    IntakeData.industry values (confirmed against the live
    engine/data/intake.py INTAKE_FIELDS list), so this signals a real
    data problem rather than an intentional design outcome, same
    convention as every other DATA_INTEGRITY_GAP in this file.
    """
    wage_entry = _LEGAL_WAGE_DATA_MAY2023.get(industry)
    if wage_entry is None:
        _logger.warning(
            "OH compensatory-damages pricing data-integrity gap: "
            "unrecognized industry=%r has no _LEGAL_WAGE_DATA_MAY2023 entry",
            industry,
        )
        return LegalPricingResult(status=LegalPricingStatus.DATA_INTEGRITY_GAP, dollar_range=None,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    compensatory_base = wage_entry[0] * _JURISDICTION_MULTIPLIER_DATA["OH"][0]
    if _oh_is_small_employer(headcount, industry):
        v = min(2.0 * compensatory_base, _OH_SMALL_EMPLOYER_CAP)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=coverage_confidence, partial_state_flag=partial_state_flag,
            is_floor=False, may_overstate_for_uncollected_net_worth=True)
    v = 2.0 * compensatory_base
    return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
        coverage_confidence=coverage_confidence, partial_state_flag=partial_state_flag,
        is_floor=True)


def _cluster_4_curve_for_org_type(
    org_type: str, org_size: str, headcount: int, jurisdictions: list[str], industry: str,
) -> LegalCurveLookup:
    """
    industry (Priority Queue item 9, this session) is used only by the
    Ohio state_specific_tiers branch below, to look up
    _LEGAL_WAGE_DATA_MAY2023 for _oh_compensatory_damages_pricing(). Every
    other branch in this function is industry-independent, unchanged.

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
    if treatment == "state_specific_tiers" and _oh_drives_tiers_result(jurisdictions):
        # Ohio's real formula, wired in (Priority Queue item 9, this
        # session). Returned before the ceiling lookup below, same shape
        # as before this build -- Ohio's own formula is independent of
        # Cluster 4b's headcount-bracket ceiling table entirely.
        # Converted from _oh_compensatory_damages_pricing()'s
        # LegalPricingResult into this function's own LegalCurveLookup
        # shape via a flat curve (floor == ceiling): _legal_score_fraction
        # (curve, score) = floor * (ceiling/floor)**(score-1) collapses to
        # exactly `floor` for any score when floor == ceiling (that ratio
        # is 1, and 1**anything == 1) -- confirmed by reading
        # _legal_score_fraction()'s own body, not assumed -- so this
        # formula's dollar figure reaches the final LegalPricingResult
        # unscaled by score, matching Clusters 1/2's own unscaled
        # dollar_range=(v, v).
        oh_result = _oh_compensatory_damages_pricing(
            industry, headcount, coverage.confidence, coverage.partial_state_flag,
        )
        if oh_result.status != LegalPricingStatus.PRICED:
            return LegalCurveLookup(
                curve=None, status=oh_result.status,
                coverage_confidence=oh_result.coverage_confidence,
                partial_state_flag=oh_result.partial_state_flag,
            )
        oh_v = oh_result.dollar_range[0]
        return LegalCurveLookup(
            curve=LegalDollarCurve(floor=oh_v, ceiling=oh_v),
            status=LegalPricingStatus.PRICED,
            coverage_confidence=oh_result.coverage_confidence,
            partial_state_flag=oh_result.partial_state_flag,
            is_floor=oh_result.is_floor,
            may_overstate_for_uncollected_net_worth=oh_result.may_overstate_for_uncollected_net_worth,
        )
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)
    if ceiling is None:
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.DATA_INTEGRITY_GAP,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        )
    flat_cap_result = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
    flat_cap = flat_cap_result[0] if flat_cap_result is not None else None
    final_ceiling = ceiling if flat_cap is None else min(ceiling, flat_cap)
    is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None
    specific_caveat_jurisdiction = flat_cap_result[1] if flat_cap_result is not None else None
    if specific_caveat_jurisdiction is None and treatment == "state_specific_tiers":
        specific_caveat_jurisdiction = _state_specific_tiers_driver(jurisdictions)
    return LegalCurveLookup(
        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=final_ceiling),
        status=LegalPricingStatus.PRICED,
        coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        is_floor=is_floor,
        specific_caveat_jurisdiction=specific_caveat_jurisdiction,
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
    entry = STATE_CRITERIA.get(state_id)
    if entry is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    score = entry.legal
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
        if treatment == "state_specific_tiers" and _oh_drives_tiers_result(jurisdictions):
            # Ohio's real formula, wired in (Priority Queue item 9, this
            # session) -- see _oh_compensatory_damages_pricing()'s own
            # docstring for the full formula, the small-employer net-
            # worth caveat, and why coverage_confidence/partial_state_flag
            # are threaded through here rather than hardcoded.
            return _oh_compensatory_damages_pricing(
                industry, headcount, coverage.confidence, coverage.partial_state_flag,
            )
        flat_cap_result = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
        flat_cap = flat_cap_result[0] if flat_cap_result is not None else None
        curve = _CLUSTER_1_CURVE if flat_cap is None else LegalDollarCurve(
            floor=_CLUSTER_1_CURVE.floor, ceiling=min(_CLUSTER_1_CURVE.ceiling, flat_cap),
        )
        v = _legal_score_fraction(curve, score)
        is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None
        specific_caveat_jurisdiction = flat_cap_result[1] if flat_cap_result is not None else None
        if specific_caveat_jurisdiction is None and treatment == "state_specific_tiers":
            specific_caveat_jurisdiction = _state_specific_tiers_driver(jurisdictions)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
            is_floor=is_floor, specific_caveat_jurisdiction=specific_caveat_jurisdiction)
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
        if treatment == "state_specific_tiers" and _oh_drives_tiers_result(jurisdictions):
            # Same reasoning as Cluster 1 above -- Ohio's real formula,
            # wired in (Priority Queue item 9, this session). See
            # _oh_compensatory_damages_pricing()'s own docstring.
            return _oh_compensatory_damages_pricing(
                industry, headcount, coverage.confidence, coverage.partial_state_flag,
            )
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
        lookup = _cluster_4_curve_for_org_type(org_type, org_size, headcount, jurisdictions, industry)
        if lookup.curve is None:
            return LegalPricingResult(status=lookup.status, dollar_range=None,
                coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)
        v = _legal_score_fraction(lookup.curve, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag,
            is_floor=lookup.is_floor,
            may_overstate_for_uncollected_net_worth=lookup.may_overstate_for_uncollected_net_worth,
            specific_caveat_jurisdiction=lookup.specific_caveat_jurisdiction)
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

    has_uncollected_net_worth_caveat (Priority Queue item 9, this
    session's UI-framing follow-up) is True if any contributing PRICED
    state set LegalPricingResult.may_overstate_for_uncollected_net_worth
    -- today, only Ohio's small-employer/individual-defendant branch
    (_oh_compensatory_damages_pricing()) ever sets that field. Same OR-
    across-contributing-states aggregation shape as
    has_partial_jurisdictions immediately below it, deliberately not
    combined with that flag -- they signal opposite things
    (has_partial_jurisdictions: the figure may UNDERSTATE, an
    unverified jurisdiction could set a higher bar; this: the figure
    may OVERSTATE, a real statutory alternative isn't computed) and
    is_floor's own propagation is explicitly out of scope for this
    pass, per Pete's call -- it touches 32 states' already-shipped
    results, not just Ohio, and deserves its own separately-scoped
    task.
    """
    headcount = org_size
    jurisdictions = jurisdictions or []
    org_size = resolve_headcount_bucket(org_size)
    per_state_ranges: dict[str, tuple[float, float]] = {}
    unpriced_state_ids: list[str] = []
    coverage_confidences: set[str] = set()
    has_partial_jurisdictions = False
    has_uncollected_net_worth_caveat = False
    specific_caveat_jurisdiction: Optional[str] = None
    for sid in state_ids:
        result = _single_state_legal_pricing(
            sid, org_size, industry, org_type, headcount, jurisdictions
        )
        if result.status == LegalPricingStatus.PRICED:
            per_state_ranges[sid] = result.dollar_range
            if result.may_overstate_for_uncollected_net_worth:
                has_uncollected_net_worth_caveat = True
            if specific_caveat_jurisdiction is None and result.specific_caveat_jurisdiction is not None:
                # First non-None wins -- not a real ambiguity: jurisdictions
                # is a single session-level input feeding the same pure
                # resolvers for every contributing state, so any two
                # non-None values here are guaranteed identical (verified
                # this session before this patch was written).
                specific_caveat_jurisdiction = result.specific_caveat_jurisdiction
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
            "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,
            "specific_caveat_jurisdiction": specific_caveat_jurisdiction,
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
            "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,
            "specific_caveat_jurisdiction": specific_caveat_jurisdiction,
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
        "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,
        "specific_caveat_jurisdiction": specific_caveat_jurisdiction,
    }


def compute_legal_per_state_breakdown(
    state_ids: list[str],
    org_size: int,
    industry: str,
    org_type: str,
    jurisdictions: Optional[list[str]] = None,
) -> list[dict]:
    """
    The per-state figures behind compute_legal_compliance_exposure()'s
    total (Phase 1 show-your-work). One entry per PRICED state:
    {"state_id", "cluster", "low", "high", "weight"}. Priced by the same
    _single_state_legal_pricing() call with the same inputs, and weighted
    exactly as that function aggregates: N=1 -> 1.0, otherwise 0.5**i within
    each cluster ranked by low (highest first, stable on ties like its own
    sort), so sum(weight * low) == its returned low. Unpriced and
    not-applicable states are excluded, same as the total.
    """
    headcount = org_size
    jurisdictions = jurisdictions or []
    org_size = resolve_headcount_bucket(org_size)
    per_state_ranges: dict[str, tuple[float, float]] = {}
    for sid in state_ids:
        result = _single_state_legal_pricing(
            sid, org_size, industry, org_type, headcount, jurisdictions
        )
        if result.status == LegalPricingStatus.PRICED:
            per_state_ranges[sid] = result.dollar_range

    if len(per_state_ranges) == 1:
        (sid, (low, high)), = per_state_ranges.items()
        return [{
            "state_id": sid, "cluster": LEGAL_COMPLIANCE_CLUSTER[sid],
            "low": round(low, 2), "high": round(high, 2), "weight": 1.0,
        }]

    breakdown: list[dict] = []
    by_cluster_ids: dict[int, list[str]] = {}
    for sid in per_state_ranges:
        by_cluster_ids.setdefault(LEGAL_COMPLIANCE_CLUSTER[sid], []).append(sid)
    for cluster, sids in by_cluster_ids.items():
        ranked = sorted(sids, key=lambda s: per_state_ranges[s][0], reverse=True)
        for i, sid in enumerate(ranked):
            low, high = per_state_ranges[sid]
            breakdown.append({
                "state_id": sid, "cluster": cluster,
                "low": round(low, 2), "high": round(high, 2), "weight": 0.5 ** i,
            })
    return breakdown
