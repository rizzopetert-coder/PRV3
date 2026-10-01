"""
Friction tax rebuild, Stage 5: tests for condensed_departure_cost() in
tools/test_friction_tax.py, with hardcoded literal fixtures (not derived from the
live wage table): Technology $115,030 x 0.333 and Retail & Hospitality $42,024 x
0.333, plus the unknown-industry behaviour and the retired range.

Usage: python tools/patch_stage5_test_engine.py --dry-run | --write
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/test_friction_tax.py"
ANCHOR = 'print(f"\\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")\nif FAIL:'

BLOCK = '''# -- Stage 5: condensed cost of one departure, a single value ------------------------
# Hand-computed literals: wage x 0.333.  115,030 x 0.333 = 38,304.99 (about $38,305)
# and 42,024 x 0.333 = 13,993.992 (about $13,994).

_cd_tech = _ft.condensed_departure_cost("Technology")
check("condensed_departure_cost Technology: 115,030 x 0.333 = $38,304.99, about $38,305",
      _cd_tech == {"amount": 38304.99, "currency": "USD"} and round(_cd_tech["amount"]) == 38305,
      f"got {_cd_tech}")
_cd_retail = _ft.condensed_departure_cost("Retail & Hospitality")
check("condensed_departure_cost Retail & Hospitality: 42,024 x 0.333 = $13,993.99, about $13,994",
      _cd_retail == {"amount": 13993.99, "currency": "USD"} and round(_cd_retail["amount"]) == 13994,
      f"got {_cd_retail}")
for _bad_ind in ("Not An Industry", "", None, 5, "technology"):
    check(f"condensed_departure_cost({_bad_ind!r}): null amount, USD, no exception",
          _ft.condensed_departure_cost(_bad_ind) == {"amount": None, "currency": "USD"},
          f"got {_ft.condensed_departure_cost(_bad_ind)}")
check("condensed_departure_cost returns a single value, no low or high range",
      set(_cd_tech) == {"amount", "currency"})
check("condensed_departure_cost prices all 11 industries at wage x 0.333 (wages hardcoded above)",
      all(abs(_ft.condensed_departure_cost(k)["amount"] - round(v * 0.333, 2)) < 0.005
          for k, v in _MAY2025_WAGES.items()))

'''

raw = P.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
t = raw.replace("\r\n", "\n")
assert t.count(ANCHOR) == 1, t.count(ANCHOR)
assert "Stage 5: condensed cost" not in t
t = t.replace(ANCHOR, BLOCK + ANCHOR)
print("1 insert ok", "CRLF" if crlf else "LF")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("WROTE")
else:
    print("DRY RUN")
