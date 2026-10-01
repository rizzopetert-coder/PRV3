"""
Stage 3 tests for tools/test_friction_tax.py: the frozen Legal wage table, the
May 2025 friction wage table, get_industry_wage(), and proof that Legal reads the
frozen table and not the refreshed one. Appended before the final summary.

Usage: python tools/patch_stage3_wage_tests.py --dry-run | --write
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/test_friction_tax.py"
ANCHOR = 'print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")\nif FAIL:'

BLOCK = '''# -- Stage 3 (R1): frozen Legal wage table and the May 2025 friction wage table --

_MAY2023_WAGES = {
    "Professional Services": 102670.0, "Healthcare & Life Sciences": 67320.0,
    "Financial Services": 94150.0, "Technology": 108110.0, "Manufacturing": 64440.0,
    "Retail & Hospitality": 39651.0, "Nonprofit & Education": 57770.0,
    "Government & Public Sector": 74410.0, "Construction": 67430.0,
    "Transportation & Warehousing": 59320.0, "Other": 63446.0,
}
_MAY2025_WAGES = {
    "Professional Services": 108640.0, "Healthcare & Life Sciences": 70969.0,
    "Financial Services": 100842.0, "Technology": 115030.0, "Manufacturing": 69131.0,
    "Retail & Hospitality": 42024.0, "Nonprofit & Education": 72765.0,
    "Government & Public Sector": 80290.0, "Construction": 72146.0,
    "Transportation & Warehousing": 64331.0, "Other": 67977.0,
}
check(
    "_LEGAL_WAGE_DATA_MAY2023 holds exactly the 11 May 2023 wages, unchanged (Legal byte-identity, R1)",
    {k: v[0] for k, v in _ft._LEGAL_WAGE_DATA_MAY2023.items()} == _MAY2023_WAGES,
    f"got {({k: v[0] for k, v in _ft._LEGAL_WAGE_DATA_MAY2023.items()})}",
)
check(
    "_LEGAL_WAGE_DATA_MAY2023 entries are all May 2023 sourced",
    all("May 2023" in v[1] and v[2].startswith("BLS_OEWS_2023") for v in _ft._LEGAL_WAGE_DATA_MAY2023.values()),
)
check(
    "_INDUSTRY_WAGE_DATA holds exactly the 11 verified May 2025 wages (spec Section 3)",
    {k: v[0] for k, v in _ft._INDUSTRY_WAGE_DATA.items()} == _MAY2025_WAGES,
    f"got {({k: v[0] for k, v in _ft._INDUSTRY_WAGE_DATA.items()})}",
)
check(
    "_INDUSTRY_WAGE_DATA keys equal INDUSTRIES and the frozen table's keys",
    set(_ft._INDUSTRY_WAGE_DATA) == set(INDUSTRIES) == set(_ft._LEGAL_WAGE_DATA_MAY2023),
)
check(
    "every May 2025 entry carries provenance (oesm25in4.zip, nat3d_M2025_dl.xlsx) and a BLS_OEWS_2025 citation id",
    all("oesm25in4.zip" in v[1] and "nat3d_M2025_dl.xlsx" in v[1] and v[2].startswith("BLS_OEWS_2025")
        for v in _ft._INDUSTRY_WAGE_DATA.values()),
)
check(
    "the two privately owned entries name the owner file (Decision 12)",
    "nat3d_owner_M2025_dl.xlsx" in _ft._INDUSTRY_WAGE_DATA["Healthcare & Life Sciences"][1]
    and "nat3d_owner_M2025_dl.xlsx" in _ft._INDUSTRY_WAGE_DATA["Nonprofit & Education"][1],
)
check(
    "get_industry_wage returns the May 2025 wage for all 11 industries and None for an unknown one",
    all(_ft.get_industry_wage(k) == v for k, v in _MAY2025_WAGES.items())
    and _ft.get_industry_wage("Not An Industry") is None,
)

_oh_args = dict(org_size="Under 25", industry="Professional Services", org_type="Founder-led",
                headcount=20, jurisdictions=["OH"])
_oh_before = _ft._single_state_legal_pricing("the_paper_tiger", **_oh_args)
_saved_new = _ft._INDUSTRY_WAGE_DATA["Professional Services"]
_ft._INDUSTRY_WAGE_DATA["Professional Services"] = (1.0,) + _saved_new[1:]
_oh_new_changed = _ft._single_state_legal_pricing("the_paper_tiger", **_oh_args)
_ft._INDUSTRY_WAGE_DATA["Professional Services"] = _saved_new
check(
    "Legal's Ohio compensatory formula ignores _INDUSTRY_WAGE_DATA (changing it does not move the Legal figure)",
    _oh_new_changed.dollar_range == _oh_before.dollar_range == (189487.75199999998, 189487.75199999998),
    f"before {_oh_before.dollar_range} after {_oh_new_changed.dollar_range}",
)
_saved_frozen = _ft._LEGAL_WAGE_DATA_MAY2023["Professional Services"]
_ft._LEGAL_WAGE_DATA_MAY2023["Professional Services"] = (1.0,) + _saved_frozen[1:]
_oh_frozen_changed = _ft._single_state_legal_pricing("the_paper_tiger", **_oh_args)
_ft._LEGAL_WAGE_DATA_MAY2023["Professional Services"] = _saved_frozen
check(
    "Legal's Ohio compensatory formula does read _LEGAL_WAGE_DATA_MAY2023 (teeth for the check above)",
    _oh_frozen_changed.dollar_range != _oh_before.dollar_range,
    f"got {_oh_frozen_changed.dollar_range}",
)


'''

raw = P.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
t = raw.replace("\r\n", "\n")
assert t.count(ANCHOR) == 1, f"anchor count {t.count(ANCHOR)}"
assert "Stage 3 (R1)" not in t
t = t.replace(ANCHOR, BLOCK + ANCHOR)
print("1 insert ok", "CRLF" if crlf else "LF")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("WROTE")
else:
    print("DRY RUN")
