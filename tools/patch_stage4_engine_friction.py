"""
Friction tax rebuild, Stage 4, engine/friction_tax.py (spec Section 10 step 5 as
amended by the Phase 0 addendum).

Removes: SEVERITY_SCALAR, PayrollBaselineEntry, PAYROLL_BASELINE_GRID,
OrgTypeScalarEntry, ORG_TYPE_SCALARS, StateCriterionScore, StateMultiplierEntry,
STATE_MULTIPLIERS (and its import-time asserts), the magnitude constants
(_R_MIN/_R_MAX/_FRACTION_MIN/_FRACTION_MAX/_MULTI_CHANNEL_SEVERITY_LOADING_K),
_attritional_fraction, and the old compute_friction_tax with its 1.4x spread.

Adds: the two-channel compute_friction_tax(state_ids, org_size, industry), its
input constants, the JOLTS 2025 monthly quits rates (R3, rounded 2-decimal values)
and the headcount guard (Decisions 10 and 13) and cap (Decisions 15 and 17).

Kept: HEADCOUNT_MIDPOINTS, HEADCOUNT_BUCKETS, resolve_headcount_bucket (Legal),
INDUSTRIES, _LEGAL_WAGE_DATA_MAY2023, _INDUSTRY_WAGE_DATA, get_industry_wage.

Usage: python tools/patch_stage4_engine_friction.py --dry-run | --write
"""
import sys
from pathlib import Path

FT = Path(__file__).resolve().parents[1] / "engine/friction_tax.py"

NEW_DOCSTRING = '''"""
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
'''

NEW_BLOCK = '''# -- Friction tax: two dollar channels -------------------------------------------
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


'''


def cut(text: str, start: str, end: str, replacement: str = "") -> str:
    assert text.count(start) == 1, f"start marker count {text.count(start)}: {start[:60]!r}"
    i = text.index(start)
    j = text.index(end, i)
    assert text.count(end) >= 1
    return text[:i] + replacement + text[j:]


def transform(t: str) -> str:
    # module docstring
    end_doc = '"""\n\nfrom __future__ import annotations'
    assert t.startswith('"""\nPRV3 Scoring Engine -- Output Layer\nFriction Tax Computation')
    k = t.index(end_doc)
    t = NEW_DOCSTRING + t[k + 4:]
    # severity scalars
    t = cut(t, "# -- Severity scalars (LOCKED)", "# -- Headcount and industry bucket keys")
    # payroll grid dataclass
    t = cut(t, "# -- Payroll baseline grid ---", "# FROZEN COPY, read ONLY by Legal/Compliance")
    # grid, org type scalar, state multipliers, old compute_friction_tax
    t = cut(t, "PAYROLL_BASELINE_GRID: dict[tuple[str, str], PayrollBaselineEntry] = {",
            "# -- Legal/Compliance -- mechanism-aware exposure (Addenda 1-10)", NEW_BLOCK)
    return t


if __name__ == "__main__":
    raw = FT.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = transform(raw.replace("\r\n", "\n"))
    print(f"friction_tax.py: {len(raw.splitlines())} -> {len(t.splitlines())} lines ({'CRLF' if crlf else 'LF'})")
    if "--write" in sys.argv:
        FT.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
        print("WROTE")
    else:
        print("DRY RUN")
