"""
Phase 1 report-redesign engine data (2026-09-27): show-your-work exports,
asset evidence, qualifying states, service cost comparison, tactical
pre-aggregation, and the three-call synthesis flow. Grows per commit.

Run: python tools/test_phase1_report_data.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1; print(f"  PASS  {name}")
    else:
        failed += 1; print(f"  FAIL  {name}" + (f" -- {detail}" if detail else ""))

from engine.friction_tax import (
    compute_friction_tax, compute_legal_compliance_exposure, compute_legal_per_state_breakdown,
)
from engine.contract import (
    _friction_driving_factors, _legal_driving_factors, _top_observation_texts,
)
from engine.accumulation import IntakeData

INTAKE = IntakeData(headcount=175, industry="Professional Services",
                    org_type="Privately held professional leadership",
                    jurisdictions=["OH"], significant_events=[], principal_role="Owner / Founder")

# ── 1. Show-your-work: friction components reproduce low/high exactly ──────────
for ids, tier in ((["built_to_fail"], "Emerging"), (["built_to_fail", "the_uninitiated", "the_founders_grip"], "Entrenched")):
    r = compute_friction_tax(ids, tier, 175, INTAKE.industry, INTAKE.org_type)
    c = r["components"]
    recomputed = round(c["adjusted_baseline"] * c["combined_multiplier"] * c["multi_channel_severity_loading"] * c["severity_scalar"], 2)
    check(f"friction components reproduce low ({len(ids)} state)", recomputed == r["low"], f"{recomputed} vs {r['low']}")
    check(f"friction adjusted_baseline = payroll_floor x org_type_scalar ({len(ids)} state)",
          abs(c["adjusted_baseline"] - c["payroll_floor"] * c["org_type_scalar"]) < 1e-6)
unc = compute_friction_tax(["built_to_fail"], "Emerging", 175, "Professional Services", "")
check("friction: uncalibrated result has no components", "components" not in unc)

# ── 2. Legal per_state_breakdown weights reproduce the totals ───────────────────
from engine.friction_tax import LEGAL_COMPLIANCE_CLUSTER
legal_ids = [s for s in LEGAL_COMPLIANCE_CLUSTER][:8]
lr = compute_legal_compliance_exposure(legal_ids, 175, INTAKE.industry, INTAKE.org_type, ["OH"])
bd = compute_legal_per_state_breakdown(legal_ids, 175, INTAKE.industry, INTAKE.org_type, ["OH"])
check("legal: total result keeps its exact pinned key set", "per_state_breakdown" not in lr)
if lr["low"] is not None:
    check("legal: sum(weight*low) == low", abs(sum(b["weight"] * b["low"] for b in bd) - lr["low"]) < 0.05,
          f"{sum(b['weight'] * b['low'] for b in bd)} vs {lr['low']}")
    check("legal: sum(weight*high) == high", abs(sum(b["weight"] * b["high"] for b in bd) - lr["high"]) < 0.05)
check("legal: breakdown only covers priced states", all(b["state_id"] not in lr["unpriced_state_ids"] for b in bd))
one = compute_legal_compliance_exposure(["built_to_fail"], 175, INTAKE.industry, INTAKE.org_type, ["OH"])
one_bd = compute_legal_per_state_breakdown(["built_to_fail"], 175, INTAKE.industry, INTAKE.org_type, ["OH"])
check("legal N=1: single entry at weight 1.0 matching the total",
      len(one_bd) == 1 and one_bd[0]["weight"] == 1.0 and one_bd[0]["low"] == one["low"], str(one_bd))
check("legal: nothing priced -> empty breakdown", compute_legal_per_state_breakdown([], 175, INTAKE.industry, INTAKE.org_type, ["OH"]) == [])

# ── 3. Receipts ─────────────────────────────────────────────────────────────────
states = [{"state_id": s, "state_name": s.replace("_", " ").title()} for s in ["built_to_fail", "the_uninitiated"]]
fr = compute_friction_tax([s["state_id"] for s in states], "Entrenched", 175, INTAKE.industry, INTAKE.org_type)
receipts = _friction_driving_factors(fr, states, "Entrenched", INTAKE, [])
check("friction receipts built", len(receipts) >= 5, str(len(receipts)))
check("friction receipts: no triggering_answer with an empty answers_log",
      all("triggering_answer" not in r for r in receipts))
check("friction receipts: no semicolons or em-dashes",
      all(";" not in r["rationale"] and "—" not in r["rationale"] for r in receipts))
check("friction receipts: uncalibrated -> []", _friction_driving_factors(unc, states, "Emerging", INTAKE, []) == [])
lreceipts = _legal_driving_factors(bd, [{"state_id": s, "state_name": s} for s in legal_ids], INTAKE, [])
check("legal receipts: one per priced state (+ total when several)",
      len(lreceipts) == len(bd) + (1 if len(bd) > 1 else 0), f"{len(lreceipts)} vs {len(bd)}")

# triggering_answer only ever comes from authored observation_text
from engine.data.questions import QUESTION_LIBRARY as L
authored = [(k, o) for k, q in L.items() for o in q.answer_options if o.observation_text]
log = [{"question_id": k, "option_ids": [o.option_id]} for k, o in authored[:40]]
texts = _top_observation_texts("built_to_fail", log, INTAKE, limit=5)
all_obs = {o.observation_text for _, o in authored}
check("triggering answers are authored observation_text only", all(t in all_obs for t in texts))
unauthored = [(k, o) for k, q in L.items() for o in q.answer_options if not o.observation_text and not k.startswith("TC-")][:30]
check("unauthored answers never produce a triggering answer",
      _top_observation_texts("built_to_fail", [{"question_id": k, "option_ids": [o.option_id]} for k, o in unauthored], INTAKE, 5) == [])

print(f"\nRESULT: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
