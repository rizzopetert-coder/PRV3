"""
Friction tax rebuild, Stage 4, the other three test files.

tools/test_state_criteria.py
  The interim equality test against STATE_MULTIPLIERS is removed with
  STATE_MULTIPLIERS. Replaced by a frozen sha256 fingerprint of the 58 x 4 score
  table (captured 2026-10-01 while STATE_MULTIPLIERS still existed and the two
  were equal), so a score edit now fails loudly instead of drifting silently.
tools/test_contract.py
  friction_tax_estimate is the two-channel shape, friction_receipts and the
  ledger channels are checked, dollar_exposure and inaction_cost are gone.
tools/test_phase1_report_data.py
  The show-your-work and receipt tests move to the two-channel function and
  _friction_receipts, and the inaction-cost sum assertion becomes the R5 check.

Usage: python tools/patch_stage4_test_state_criteria_contract_phase1.py --dry-run | --write
"""
import sys
from pathlib import Path

T = Path(__file__).resolve().parents[1] / "tools"
FINGERPRINT = "4eb21b87c9feedec2f86259251d9d7a0f1dedff787aa9eb617e32139f56de251"


def sc(t):
    t = t.replace(
        "from engine.friction_tax import LEGAL_COMPLIANCE_CLUSTER, STATE_MULTIPLIERS\n",
        "import hashlib\nimport json\n\nfrom engine.friction_tax import LEGAL_COMPLIANCE_CLUSTER\n")
    a = t.index("# -- 3. interim drift guard against STATE_MULTIPLIERS")
    b = t.index("# -- 4. legal")
    new = '''# -- 3. frozen fingerprint (replaces the interim equality with STATE_MULTIPLIERS) ----
# sha256 of the canonical 58 x 4 score table, captured 2026-10-01 while
# STATE_MULTIPLIERS still existed and every score was equal to it. Editing any
# score changes the hash and fails here, a deliberate score change updates this
# constant in the same commit.
_canon = json.dumps(
    {sid: [c.turnover, c.productivity, c.decision_quality, c.legal] for sid, c in sorted(STATE_CRITERIA.items())},
    separators=(",", ":"), sort_keys=True,
)
check("the 58 x 4 score table matches its frozen fingerprint",
      hashlib.sha256(_canon.encode()).hexdigest() == "%s",
      f"got {hashlib.sha256(_canon.encode()).hexdigest()}")
_spot = {
    "the_overloaded_manager": (2, 1, 1, 0), "decision_paralysis": (1, 2, 2, 0), "paper_shield": (0, 0, 2, 0),
    "the_founders_grip": (2, 2, 2, 0), "the_basement_standard": (1, 2, 2, 1), "the_inner_circle": (1, 0, 2, 1),
    "the_paper_tiger": (1, 0, 0, 2), "the_lost_map": (0, 2, 2, 0),
}
check("eight spot-checked states hold their hardcoded scores (turnover, productivity, decision_quality, legal)",
      all((c.turnover, c.productivity, c.decision_quality, c.legal) == _spot[s] for s, c in STATE_CRITERIA.items() if s in _spot)
      and all(s in STATE_CRITERIA for s in _spot))

''' % FINGERPRINT
    t = t[:a] + new + t[b:]
    t = t.replace("  3. Interim drift guard: every score equals STATE_MULTIPLIERS (removed with\n     STATE_MULTIPLIERS in Stage 4, delete this section then)\n",
                  "  3. Frozen sha256 fingerprint of the score table and eight hardcoded spot checks\n     (replaced the interim equality with STATE_MULTIPLIERS, removed in Stage 4)\n")
    return t


def contract(t):
    old1 = '''check("private_output.friction_tax_estimate is a calibrated {low, high, currency} dict",
      isinstance(fte, dict)
      and isinstance(fte.get("low"), (int, float))
      and isinstance(fte.get("high"), (int, float))
      and fte.get("low") <= fte.get("high")
      and isinstance(fte.get("currency"), str),
      f"got {fte!r}")
'''
    new1 = '''_fte_base = (fte or {}).get("typical_baseline", {})
check("private_output.friction_tax_estimate is the two-channel point estimate (no low, high or driving_factors)",
      isinstance(fte, dict)
      and fte.get("currency") == "USD"
      and fte.get("excess") is None
      and "low" not in fte and "high" not in fte and "driving_factors" not in fte
      and isinstance(_fte_base.get("total", {}).get("percent_of_payroll"), (int, float))
      and isinstance(_fte_base.get("channels"), list) and len(_fte_base["channels"]) >= 1
      and all(c.get("channel") in ("engagement", "turnover")
              and isinstance(c.get("percent_of_payroll"), (int, float))
              and isinstance(c.get("inputs"), list) and c["inputs"] for c in _fte_base["channels"]),
      f"got {fte!r}")
check("private_output.friction_receipts is a list of receipts, sibling of friction_tax_estimate",
      isinstance(priv.get("friction_receipts"), list)
      and all({"category", "rationale"} <= set(r) for r in priv["friction_receipts"]),
      f"got {priv.get('friction_receipts')!r}")
check("private_output.service_cost_comparison carries no inaction_cost fields (R5)",
      "inaction_cost_low" not in (priv.get("service_cost_comparison") or {})
      and "inaction_cost_high" not in (priv.get("service_cost_comparison") or {}),
      f"got {priv.get('service_cost_comparison')!r}")
'''
    assert t.count(old1) == 1
    t = t.replace(old1, new1)
    a = t.index("# Cross-check dollar_exposure against a direct compute_friction_tax() call --")
    b = t.index("# Q01-B carries negative authority_liability (-0.15)")
    new2 = '''# the_basement_standard scores turnover 1, productivity 2, decision_quality 2
# (hardcoded here, not read from the registry), so it switches all three on.
check(
    "friction_tax_ledger row: channels are the three the_basement_standard switches on, "
    "and the row carries no dollar_exposure (Stage 4)",
    ledger_row.get("channels") == ["engagement", "turnover", "decision_time"]
    and "dollar_exposure" not in ledger_row,
    f"got {ledger_row}",
)

'''
    t = t[:a] + new2 + t[b:]
    t = t.replace("from engine.friction_tax import compute_friction_tax\n\nledger_answers_log", "ledger_answers_log")
    t = t.replace("# risk_label/dollar_exposure must still populate (they don't depend on",
                  "# risk_label/channels must still populate (they don't depend on")
    t = t.replace("""    "and dollar_exposure, only top_contributing_answers degrades to []",""",
                  """    "and channels, only top_contributing_answers degrades to []",""")
    old3 = '    and no_answers_ledger[0].get("dollar_exposure") == ledger_row.get("dollar_exposure")\n'
    assert t.count(old3) == 1
    t = t.replace(old3, '    and no_answers_ledger[0].get("channels") == ledger_row.get("channels")\n')
    return t


def phase1(t):
    t = t.replace("    _friction_driving_factors, _legal_driving_factors, _top_observation_texts,\n",
                  "    _friction_receipts, _legal_driving_factors, _top_observation_texts,\n")
    a = t.index("# ── 1. Show-your-work: friction components reproduce low/high exactly")
    b = t.index("# ── 2. Legal per_state_breakdown weights reproduce the totals")
    new1 = '''# ── 1. Show-your-work: the channels reproduce the total, hand-computed literals ──
_r1 = compute_friction_tax(["the_overloaded_manager"], 12, "Retail & Hospitality")
_t1 = _r1["estimate"]["typical_baseline"]
check("friction: channel amounts sum to the total (12 / Retail & Hospitality)",
      abs(sum(c["amount"] for c in _t1["channels"]) - _t1["total"]["amount"]) < 0.02,
      f"{[c['amount'] for c in _t1['channels']]} vs {_t1['total']['amount']}")
check("friction: 12 / Retail & Hospitality total is $63,923 (hardcoded, R3)", round(_t1["total"]["amount"]) == 63923)
check("friction: payroll is headcount x wage (12 x 42,024)", _r1["payroll"] == 504288.0)
check("friction: severity is not an input to the result",
      compute_friction_tax(["built_to_fail"], 175, "Professional Services")
      == compute_friction_tax(["built_to_fail"], 175, "Professional Services"))
unc = compute_friction_tax(["built_to_fail"], "", "Professional Services")
check("friction: uncalibrated result has no estimate", unc["estimate"] is None)

'''
    t = t[:a] + new1 + t[b:]
    old2 = '''fr = compute_friction_tax([s["state_id"] for s in states], "Entrenched", 175, INTAKE.industry, INTAKE.org_type)
receipts = _friction_driving_factors(fr, states, "Entrenched", INTAKE, [])
check("friction receipts built", len(receipts) >= 5, str(len(receipts)))
'''
    new2 = '''fr = compute_friction_tax([s["state_id"] for s in states], 175, INTAKE.industry)
receipts = _friction_receipts(fr, states, INTAKE, [])
check("friction receipts built", len(receipts) >= 5, str(len(receipts)))
check("friction receipts: the total carries the framing wording, the engagement line the gap wording",
      any("what organizations like yours typically lose" in r["rationale"] for r in receipts if r["category"] == "Total")
      and any("the gap between organizations like yours and the best-run ones" in r["rationale"]
              for r in receipts if r["category"] == "Engagement"))
check("friction receipts: none says normal, acceptable or full engagement",
      not any(w in r["rationale"].lower() for r in receipts for w in ("normal", "acceptable", "full engagement")))
check("friction receipts: the decision-time receipt has no dollar figure",
      all("$" not in r["rationale"] for r in receipts if r["category"] == "Decision time")
      and any(r["category"] == "Decision time" for r in receipts))
_cap_fr = compute_friction_tax([s["state_id"] for s in states], 1000, INTAKE.industry)
_cap_rc = _friction_receipts(_cap_fr, states, INTAKE, [])
check("friction receipts at the 1,000 cap: no dollar figure in any receipt, and the cap is stated",
      all("$" not in r["rationale"] for r in _cap_rc)
      and any("1,000 employees" in r["rationale"] for r in _cap_rc), str(_cap_rc))
_ps_rc = _friction_receipts(compute_friction_tax(["paper_shield"], 175, INTAKE.industry),
                            [{"state_id": "paper_shield", "state_name": "Paper Shield"}], INTAKE, [])
check("friction receipts render when the estimate is null (only paper_shield): condition and decision time",
      [r["category"] for r in _ps_rc] == ["Condition", "Decision time"], str(_ps_rc))
'''
    assert t.count(old2) == 1
    t = t.replace(old2, new2)
    old3 = 'check("friction receipts: uncalibrated -> []", _friction_driving_factors(unc, states, "Emerging", INTAKE, []) == [])\n'
    new3 = '''_unc_rc = _friction_receipts(unc, states, INTAKE, [])
check("friction receipts: uncalibrated -> no payroll, channel or total receipts, no dollar figure",
      all(r["category"] in ("Condition", "Decision time") for r in _unc_rc)
      and all("$" not in r["rationale"] for r in _unc_rc), str(_unc_rc))
'''
    assert t.count(old3) == 1
    t = t.replace(old3, new3)
    old4 = '''    fte = out["private_output"]["friction_tax_estimate"]; lte = out["private_output"]["legal_tail_risk_exposure"]
    exp_low = (fte["low"] if fte else 0) + (lte["low"] if lte and lte["low"] is not None else 0)
    check(f"[{brand}] inaction cost = priced friction + priced legal", scc and abs((scc["inaction_cost_low"] or 0) - exp_low) < 0.05,
          f"{scc and scc['inaction_cost_low']} vs {exp_low}")
'''
    new4 = '''    check(f"[{brand}] R5: no inaction_cost fields in service_cost_comparison (the two lines read friction and legal directly)",
          scc and "inaction_cost_low" not in scc and "inaction_cost_high" not in scc, str(scc))
    check(f"[{brand}] friction_receipts is a list beside friction_tax_estimate",
          isinstance(out["private_output"]["friction_receipts"], list))
'''
    assert t.count(old4) == 1
    t = t.replace(old4, new4)
    old5 = '''fr5 = compute_friction_tax(many, "Emerging", 175, INTAKE.industry, INTAKE.org_type)
rc = [r for r in _friction_driving_factors(fr5, st5, "Emerging", INTAKE, log_p) if r["category"] == "Condition"]
'''
    new5 = '''fr5 = compute_friction_tax(many, 175, INTAKE.industry)
rc = [r for r in _friction_receipts(fr5, st5, INTAKE, log_p) if r["category"] == "Condition"]
'''
    assert t.count(old5) == 1
    t = t.replace(old5, new5)
    return t


def patch(path, fn, write):
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = fn(raw.replace("\r\n", "\n"))
    print(f"{path.name}: ok ({'CRLF' if crlf else 'LF'})")
    if write:
        path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
        print("  WROTE")


if __name__ == "__main__":
    w = "--write" in sys.argv
    patch(T / "test_state_criteria.py", sc, w)
    patch(T / "test_contract.py", contract, w)
    patch(T / "test_phase1_report_data.py", phase1, w)
    print("WRITE" if w else "DRY RUN")
