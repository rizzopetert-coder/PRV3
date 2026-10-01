"""
Friction tax rebuild, Stage 5, engine side (spec Section 10 step 6, Phase 0 addendum
R2): the condensed "cost of one departure" figure becomes a single value, the
industry wage (OEWS May 2025, get_industry_wage) x 0.333 (the Work Institute cost per
voluntary exit, TURNOVER_COST_SHARE), replacing the 0.50 to 0.75 range.

  engine/friction_tax.py  condensed_departure_cost(industry) -> {"amount", "currency"}
  api/engine.py           /api/condensed-complete returns condensed_departure_cost and
                          no longer returns condensed_financial_range

The spec does not name the new field, condensed_departure_cost is this stage's name.
amount is None for an unrecognized industry, same convention as get_industry_wage().

Usage: python tools/patch_stage5_engine.py --dry-run | --write
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
FT = R / "engine/friction_tax.py"
API = R / "api/engine.py"

FT_ANCHOR = """    entry = _INDUSTRY_WAGE_DATA.get(industry)
    return entry[0] if entry is not None else None
"""
FT_NEW = FT_ANCHOR + '''

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
'''

API_EDITS = [
    ("from engine.friction_tax import get_industry_wage\n",
     "from engine.friction_tax import condensed_departure_cost\n"),
    ("""        wage = get_industry_wage(industry)
        result["condensed_financial_range"] = (
            {"low": round(wage * 0.50, 2), "high": round(wage * 0.75, 2), "currency": "USD"}
            if wage is not None
            else {"low": None, "high": None, "currency": "USD"}
        )
""", """        result["condensed_departure_cost"] = condensed_departure_cost(industry)
"""),
    ("""    # response -- the
    # get_industry_wage() lookup is a pure function, no reason to split""", None),
]


def apply(path, edits, write):
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    for e in edits:
        if e[1] is None:
            continue
        assert t.count(e[0]) == 1, f"{path.name}: count {t.count(e[0])}: {e[0][:70]!r}"
        t = t.replace(e[0], e[1])
    print(f"{path.name}: ok ({'CRLF' if crlf else 'LF'})")
    if write:
        path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))


w = "--write" in sys.argv
apply(FT, [(FT_ANCHOR, FT_NEW)], w)
apply(API, API_EDITS, w)
print("WRITE" if w else "DRY RUN")
