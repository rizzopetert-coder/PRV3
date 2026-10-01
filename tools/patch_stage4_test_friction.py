"""
Friction tax rebuild, Stage 4, tools/test_friction_tax.py (spec Section 8).

Removes the sections for the structures Stage 4 deletes (1 to 21: SEVERITY_SCALAR,
the old compute_friction_tax, PAYROLL_BASELINE_GRID, ORG_TYPE_SCALARS,
STATE_MULTIPLIERS) and replaces them with tests of the two-channel function whose
expected values are hardcoded literals, hand-computed from the spec's inputs, never
derived from the live tables. Legal tests that read STATE_MULTIPLIERS read
STATE_CRITERIA instead (same scores).

Usage: python tools/patch_stage4_test_friction.py --dry-run | --write
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "tools/test_friction_tax.py"

NEW_DOC = '''Verifies:
  1. The cited inputs are the decided values (Gallup 0.70, 0.31, 0.18, 0.42,
     Work Institute 0.333) and the engagement factor is exactly 7.02 percent of
     payroll in every industry, hardcoded, not derived from the tables
  2. Hand-computed fixtures at actual headcount, expected values hardcoded as
     literals from the spec's R3 worked figures (the 10 Section 6b rows)
  3. The 1,000 intake cap withholds every dollar amount and keeps percent of
     payroll, 999 carries both
  4. The headcount guard: int or float of at least 2 prices at the actual N,
     everything else is uncalibrated with no bucket fallback
  5. Channel switch rule against the identified states: channels never stack or
     scale by state count, severity is not an input, excess is null, a state set
     with no dollar channel (paper_shield) returns a null estimate
  6. Every industry has a W and a q, the stored JOLTS rates are the R3 rounded
     values, every input carries a source and a vintage
  7. Engagement floor: an engaged share at or above best practice prices zero,
     never negative
  8. The removed structures are gone (STATE_MULTIPLIERS, PAYROLL_BASELINE_GRID,
     SEVERITY_SCALAR, ORG_TYPE_SCALARS, the 1.4x spread)
  9. Stage 3 wage tables (frozen Legal copy and May 2025 friction wages)
'''

NEW_TESTS = '''# -- 1. Cited inputs, hardcoded ----------------------------------------------------

check("ENGAGEMENT_BEST_PRACTICE == 0.70 (Gallup, 2025)", _ft.ENGAGEMENT_BEST_PRACTICE == 0.70)
check("ENGAGEMENT_US == 0.31 (Gallup, May 2026)", _ft.ENGAGEMENT_US == 0.31)
check("NOT_ENGAGED_COST_SHARE == 0.18 (Gallup, 2020)", _ft.NOT_ENGAGED_COST_SHARE == 0.18)
check("TURNOVER_PREVENTABLE_SHARE == 0.42 (Gallup, July 2024)", _ft.TURNOVER_PREVENTABLE_SHARE == 0.42)
check("TURNOVER_COST_SHARE == 0.333 (Work Institute, 2017)", _ft.TURNOVER_COST_SHARE == 0.333)
check("INTAKE_HEADCOUNT_CAP == 1000 and MIN_PRICED_HEADCOUNT == 2",
      _ft.INTAKE_HEADCOUNT_CAP == 1000 and _ft.MIN_PRICED_HEADCOUNT == 2)

_BOTH = ["the_overloaded_manager"]  # turnover 2, productivity 1, decision_quality 1


def _channels(r):
    return {c["channel"]: c for c in r["estimate"]["typical_baseline"]["channels"]}


_eng_pcts = {
    ind: _channels(compute_friction_tax(_BOTH, 175, ind))["engagement"]["percent_of_payroll"]
    for ind in INDUSTRIES
}
check("engagement is exactly 7.02 percent of payroll in all 11 industries (0.39 x 0.18, hardcoded)",
      set(_eng_pcts.values()) == {7.02} and len(_eng_pcts) == 11, f"got {_eng_pcts}")

# -- 2. Hand-computed fixtures (spec 6b, R3 rounded rates), literals ----------------
# (employees, industry, engagement $, turnover $, total $), whole dollars. Computed
# by hand as P x 0.0702 and P x (monthly x 12 / 100) x 0.42 x 0.333, P = N x W.

_FIXTURES = [
    (12, "Retail & Hospitality", 35401, 28522, 63923),
    (12, "Other", 57264, 30119, 87383),
    (60, "Construction", 303879, 130771, 434650),
    (60, "Government & Public Sector", 338181, 64681, 402863),
    (175, "Technology", 1413144, 439205, 1852349),
    (175, "Professional Services", 1334642, 733889, 2068531),
    (400, "Nonprofit & Education", 2043241, 801127, 2844368),
    (400, "Manufacturing", 1941198, 649734, 2590933),
    (800, "Healthcare & Life Sciences", 3985619, 1905739, 5891358),
    (800, "Transportation & Warehousing", 3612829, 1900237, 5513066),
]
for _n, _ind, _eng, _turn, _tot in _FIXTURES:
    _r = compute_friction_tax(_BOTH, _n, _ind)
    _ch = _channels(_r)
    _total = _r["estimate"]["typical_baseline"]["total"]
    check(
        f"{_n} / {_ind}: engagement ${_eng:,}, turnover ${_turn:,}, total ${_tot:,}",
        round(_ch["engagement"]["amount"]) == _eng
        and round(_ch["turnover"]["amount"]) == _turn
        and round(_total["amount"]) == _tot,
        f"got {_ch['engagement']['amount']}, {_ch['turnover']['amount']}, {_total['amount']}",
    )
_r_retail = compute_friction_tax(_BOTH, 12, "Retail & Hospitality")
check("12 / Retail & Hospitality annual quit rate is 3.37 x 12 = 40.44 percent (R3, rounded monthly rate)",
      _r_retail["annual_quit_rate_percent"] == 40.44, f"got {_r_retail['annual_quit_rate_percent']}")
check("12 / Retail & Hospitality payroll is 12 x 42,024 = 504,288 and the total is 12.6759 percent",
      _r_retail["payroll"] == 504288.0
      and _r_retail["estimate"]["typical_baseline"]["total"]["percent_of_payroll"] == 12.6759,
      f"got {_r_retail['payroll']}, {_r_retail['estimate']['typical_baseline']['total']}")
check("every fixture total is between 8.4 and 12.7 percent of payroll (spec 6b)",
      all(8.3 < compute_friction_tax(_BOTH, 175, ind)["estimate"]["typical_baseline"]["total"]["percent_of_payroll"] < 12.8
          for ind in INDUSTRIES))
_r_fl = compute_friction_tax(_BOTH, 150.5, "Technology")
check("a float headcount prices at the actual N: 150.5 x 115,030 payroll",
      _r_fl["payroll"] == 150.5 * 115030.0 and _r_fl["headcount"] == 150.5, f"got {_r_fl['payroll']}")

# -- 3. The 1,000 intake cap ---------------------------------------------------------

_cap = compute_friction_tax(_BOTH, 1000, "Financial Services")
_cap_ch = _channels(_cap)
check("N = 1000: every amount is null, percent of payroll present on each channel and the total",
      _cap["amounts_withheld"] is True and _cap["payroll"] is None
      and _cap["estimate"]["typical_baseline"]["total"]["amount"] is None
      and _cap_ch["engagement"]["amount"] is None and _cap_ch["turnover"]["amount"] is None
      and _cap_ch["engagement"]["percent_of_payroll"] == 7.02
      and _cap_ch["turnover"]["percent_of_payroll"] == 2.1818
      and _cap["estimate"]["typical_baseline"]["total"]["percent_of_payroll"] == 9.2018,
      f"got {_cap}")
check("N = 1000: no wage or employee-count input is carried, so no dollar figure leaks through inputs",
      all(not any("wage" in i["name"].lower() or i["name"] == "Employees" for i in c["inputs"])
          for c in _cap_ch.values()))
_just = compute_friction_tax(_BOTH, 999, "Financial Services")
check("N = 999 carries both percent and amounts",
      _just["amounts_withheld"] is False and _just["estimate"]["typical_baseline"]["total"]["amount"] is not None
      and all(c["amount"] is not None for c in _channels(_just).values()))
_over = compute_friction_tax(_BOTH, 1200, "Financial Services")
check("N = 1200 (above the intake ceiling) is withheld the same way",
      _over["amounts_withheld"] is True and _over["estimate"]["typical_baseline"]["total"]["amount"] is None)

# -- 4. Headcount guard ----------------------------------------------------------------

for _bad in ("", None, "150", True, False, float("inf"), float("-inf"), float("nan"), 0, -5, 1, 1.9):
    _rb = compute_friction_tax(_BOTH, _bad, "Technology")
    check(f"headcount {_bad!r} is uncalibrated, null estimate, no bucket fallback",
          _rb["estimate"] is None and _rb["calibration_complete"] is False and _rb["headcount"] is None,
          f"got {_rb}")
check("headcount 2 is the smallest priced N", compute_friction_tax(_BOTH, 2, "Technology")["estimate"] is not None)
check("headcount 2.0 (float) prices", compute_friction_tax(_BOTH, 2.0, "Technology")["estimate"] is not None)

# -- 5. Channel switch rule ------------------------------------------------------------

check("only paper_shield (decision_quality only): null estimate, decision-time receipt on, no dollar channel",
      compute_friction_tax(["paper_shield"], 100, "Technology")["estimate"] is None
      and compute_friction_tax(["paper_shield"], 100, "Technology")["decision_time_receipt"] is True
      and compute_friction_tax(["paper_shield"], 100, "Technology")["channels_on"] == [])
_t_only = compute_friction_tax(["the_paper_tiger"], 175, "Technology")  # turnover 1, productivity 0, dq 0
check("a turnover-only state switches on the turnover channel alone, no decision-time receipt",
      _t_only["channels_on"] == ["turnover"] and list(_channels(_t_only)) == ["turnover"]
      and _t_only["decision_time_receipt"] is False)
_p_only = compute_friction_tax(["the_lost_map"], 175, "Technology")  # productivity 2, turnover 0, dq 2
check("a productivity-only state switches on the engagement channel alone, with the decision-time receipt",
      _p_only["channels_on"] == ["engagement"] and list(_channels(_p_only)) == ["engagement"]
      and _p_only["decision_time_receipt"] is True)
_one = compute_friction_tax(["the_overloaded_manager"], 175, "Technology")
_many = compute_friction_tax(
    ["the_overloaded_manager", "decision_paralysis", "the_founders_grip", "the_paper_tiger", "the_lost_map"],
    175, "Technology")
check("multi-state sets do not stack: five states give the same figure as one when both channels are already on",
      _one["estimate"] == _many["estimate"], f"one {_one['estimate']['typical_baseline']['total']} many {_many['estimate']['typical_baseline']['total']}")
check("a channel is on when any identified state scores above 0 on it (turnover-only plus productivity-only = both)",
      compute_friction_tax(["the_paper_tiger", "the_lost_map"], 175, "Technology")["estimate"]
      == _one["estimate"])
check("severity is not an input: the signature is (state_ids, org_size, industry)",
      list(inspect.signature(compute_friction_tax).parameters) == ["state_ids", "org_size", "industry"])
check("excess is null and the result is a point estimate (no low or high)",
      _one["estimate"]["excess"] is None and "low" not in _one and "high" not in _one["estimate"]
      and "low" not in _one["estimate"])
check("an unknown state id gives a null estimate", compute_friction_tax(["not_a_state"], 175, "Technology")["estimate"] is None)
check("a known state mixed with an unknown one gives a null estimate",
      compute_friction_tax(["the_overloaded_manager", "not_a_state"], 175, "Technology")["estimate"] is None)
check("an empty state list gives a null estimate", compute_friction_tax([], 175, "Technology")["estimate"] is None)
check("an unknown industry gives a null estimate", compute_friction_tax(_BOTH, 175, "Not An Industry")["estimate"] is None)

# -- 6. Tables and provenance ----------------------------------------------------------

_Q = {
    "Professional Services": 2.30, "Healthcare & Life Sciences": 2.00, "Financial Services": 1.30,
    "Technology": 1.30, "Manufacturing": 1.40, "Retail & Hospitality": 3.37,
    "Nonprofit & Education": 1.64, "Government & Public Sector": 0.80, "Construction": 1.80,
    "Transportation & Warehousing": 2.20, "Other": 2.20,
}
check("QUITS_MONTHLY_RATE_2025 holds the R3 rounded 2-decimal monthly rates, all 11 industries",
      {k: v[0] for k, v in _ft.QUITS_MONTHLY_RATE_2025.items()} == _Q)
check("every industry has a wage W and a quits rate q",
      all(_ft.get_industry_wage(i) is not None and i in _ft.QUITS_MONTHLY_RATE_2025 for i in INDUSTRIES))
_all_inputs = [i for ind in INDUSTRIES for c in _channels(compute_friction_tax(_BOTH, 175, ind)).values() for i in c["inputs"]]
check("every input carries a name, a value, a source and a vintage",
      all(i["name"] and i["value"] is not None and i["source"] and i["vintage"] for i in _all_inputs))
check("the vintages are the cited ones",
      {"2025", "May 2026", "2020", "July 2024", "2017", "May 2025", "this session"} == {i["vintage"] for i in _all_inputs},
      f"got {sorted({i['vintage'] for i in _all_inputs})}")
check("the engagement inputs are 0.70, 0.31 and 0.18, the turnover inputs include 0.42 and 0.333",
      [i["value"] for i in _channels(_one)["engagement"]["inputs"][:3]] == [0.70, 0.31, 0.18]
      and [i["value"] for i in _channels(_one)["turnover"]["inputs"][1:3]] == [0.42, 0.333])
check("framing constants carry the required wording and none of the forbidden words",
      "what organizations like yours typically lose" == _ft.FRICTION_FRAMING_TOTAL
      and "the gap between organizations like yours and the best-run ones" == _ft.FRICTION_FRAMING_ENGAGEMENT_GAP
      and not any(w in (_ft.FRICTION_FRAMING_TOTAL + _ft.FRICTION_FRAMING_ENGAGEMENT_GAP).lower()
                  for w in ("normal", "acceptable", "full engagement")))

# -- 7. Engagement floor ---------------------------------------------------------------

_saved_us = _ft.ENGAGEMENT_US
_ft.ENGAGEMENT_US = 0.80
_floor = _channels(compute_friction_tax(_BOTH, 175, "Technology"))["engagement"]
_ft.ENGAGEMENT_US = _saved_us
check("E_us at or above E_bp prices zero engagement, never negative",
      _floor["percent_of_payroll"] == 0.0 and _floor["amount"] == 0.0, f"got {_floor}")

# -- 8. Removed structures --------------------------------------------------------------

for _gone in ("STATE_MULTIPLIERS", "PAYROLL_BASELINE_GRID", "SEVERITY_SCALAR", "ORG_TYPE_SCALARS",
              "StateMultiplierEntry", "StateCriterionScore", "PayrollBaselineEntry", "OrgTypeScalarEntry",
              "_attritional_fraction", "_MULTI_CHANNEL_SEVERITY_LOADING_K", "_R_MAX", "_FRACTION_MAX",
              "_DEFAULT_SEVERITY_SCALAR"):
    check(f"{_gone} is removed from engine.friction_tax", not hasattr(_ft, _gone))

'''

EDITS_IMPORT = [
    ("""from engine.friction_tax import (
    SEVERITY_SCALAR,
    STATE_MULTIPLIERS,
    StateCriterionScore,
    StateMultiplierEntry,
    PAYROLL_BASELINE_GRID,
    PayrollBaselineEntry,
    ORG_TYPE_SCALARS,
    OrgTypeScalarEntry,
    HEADCOUNT_BUCKETS,
""", """from engine.friction_tax import (
    HEADCOUNT_BUCKETS,
"""),
    ("import sys\\nfrom pathlib import Path\\n", None),
]


def transform(t: str) -> str:
    # docstring items 1 to 21
    a = t.index("Verifies:\n")
    b = t.index("  22. INDUSTRY_NON_EXEMPT_RATIO")
    t = t[:a] + NEW_DOC + t[b:]
    # imports
    old_imp = EDITS_IMPORT[0][0]
    assert t.count(old_imp) == 1, "import block"
    t = t.replace(old_imp, EDITS_IMPORT[0][1])
    # the _synthetic_entry helper
    a = t.index("def _synthetic_entry(")
    b = t.index('print("=" * 64)\nprint("PRV3 Friction Tax -- Unit Tests")')
    t = t[:a] + t[b:]
    # sections 1 to 21
    a = t.index("# -- 1. SEVERITY_SCALAR values")
    b = t.index("# -- 22-23. INDUSTRY_NON_EXEMPT_RATIO")
    t = t[:a] + NEW_TESTS + "\n" + t[b:]
    # inspect import
    assert t.count("import sys\nfrom pathlib import Path\n") == 1
    t = t.replace("import sys\nfrom pathlib import Path\n", "import inspect\nimport sys\nfrom pathlib import Path\n")
    # Legal tests that read the criteria
    pairs = [
        ("""    if sid not in STATE_MULTIPLIERS
    or STATE_MULTIPLIERS[sid].criteria["legal"].score not in (1, 2)
""", """    if sid not in STATE_CRITERIA
    or STATE_CRITERIA[sid].legal not in (1, 2)
"""),
        ('"Every LEGAL_COMPLIANCE_CLUSTER state exists in STATE_MULTIPLIERS with a \'legal\' score in {1, 2}"',
         '"Every LEGAL_COMPLIANCE_CLUSTER state exists in STATE_CRITERIA with a \'legal\' score in {1, 2}"'),
        ('_co_score = STATE_MULTIPLIERS["cultural_overtime"].criteria["legal"].score',
         '_co_score = STATE_CRITERIA["cultural_overtime"].legal'),
        ('_dn_score = STATE_MULTIPLIERS["dueling_narratives"].criteria["legal"].score',
         '_dn_score = STATE_CRITERIA["dueling_narratives"].legal'),
        ("# convention already used elsewhere in this file for STATE_MULTIPLIERS.",
         "# convention already used elsewhere in this file for STATE_CRITERIA."),
        ('_ft.STATE_MULTIPLIERS["the_arbitrary_standard"].criteria["legal"].score',
         '_ft.STATE_CRITERIA["the_arbitrary_standard"].legal', 2),
        ("_ft.STATE_MULTIPLIERS['the_arbitrary_standard'].criteria['legal'].score",
         "_ft.STATE_CRITERIA['the_arbitrary_standard'].legal", 1),
        ("# monkey-patch targets that table, not STATE_MULTIPLIERS.",
         "# monkey-patch targets that table."),
    ]
    for pair in pairs:
        old, new = pair[0], pair[1]
        want = pair[2] if len(pair) > 2 else 1
        assert t.count(old) == want, f"count {t.count(old)} (want {want}): {old[:70]!r}"
        t = t.replace(old, new)
    # STATE_CRITERIA import
    assert t.count("from engine.data.states import STATE_PROFILES\n") == 1
    t = t.replace("from engine.data.states import STATE_PROFILES\n",
                  "from engine.data.states import STATE_PROFILES\nfrom engine.data.state_criteria import STATE_CRITERIA\n")
    return t


if __name__ == "__main__":
    raw = P.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = transform(raw.replace("\r\n", "\n"))
    print(f"test_friction_tax.py: {len(raw.splitlines())} -> {len(t.splitlines())} lines ({'CRLF' if crlf else 'LF'})")
    if "--write" in sys.argv:
        P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
        print("WROTE")
    else:
        print("DRY RUN")
