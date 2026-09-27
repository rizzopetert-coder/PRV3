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

# ── 4. Asset evidence: baseline subtraction, zero floor, omission, signals ─────
from engine.contract import _build_asset_evidence, _ASSET_BASELINE_QUESTION_IDS
from engine.accumulation import AccumulationSession, accumulate_answer
import re
sever = {k for k in L if k.startswith("SEVER-")}
check("baseline set = the fixed-value questions: 28 SEVER-* plus Q03B and Q03A-D-FOLLOW",
      _ASSET_BASELINE_QUESTION_IDS - sever == {"Q03B", "Q03A-D-FOLLOW"}
      and len(_ASSET_BASELINE_QUESTION_IDS & sever) == 28,
      str(sorted(_ASSET_BASELINE_QUESTION_IDS - sever)))
_vecs = lambda k: {tuple(o.dimensional_contributions.get(f, 0) for f in ["aptitude_asset", "authority_asset", "alliance_asset", "attitude_asset"])
                   for o in L[k].answer_options}
check("SEVER-* left out of the baseline either vary by answer (SEVER-05) or carry no asset signal (SEVER-30/31/32)",
      all(len(_vecs(k)) > 1 or _vecs(k) == {(0, 0, 0, 0)} for k in sever - _ASSET_BASELINE_QUESTION_IDS))
ZERO = {f: 0.0 for f in ["aptitude_liability", "aptitude_asset", "authority_liability", "authority_asset",
                         "alliance_liability", "alliance_asset", "attitude_liability", "attitude_asset"]}
base_log = [{"question_id": "Q03B", "option_ids": [L["Q03B"].answer_options[0].option_id]},
            {"question_id": "SEVER-01", "option_ids": [L["SEVER-01"].answer_options[0].option_id]}]
# Only baseline inflation present (0.25 x 2 per axis): everything nets to zero -> omitted
v = dict(ZERO, aptitude_asset=0.5, authority_asset=0.5, alliance_asset=0.5, attitude_asset=0.5)
check("all-zero net -> None (asset_evidence omitted)", _build_asset_evidence(v, base_log, INTAKE) is None)
# Raw below the inflation floors at zero, never negative
v = dict(ZERO, aptitude_asset=0.1, authority_asset=1.5, alliance_asset=0.5, attitude_asset=0.5)
ev = _build_asset_evidence(v, base_log, INTAKE)
check("net scores floor at 0.0 and subtract the replayed baseline exactly",
      ev is not None and ev["net_scores"] == {"aptitude": 0.0, "authority": 1.0, "alliance": 0.0, "attitude": 0.0},
      str(ev and ev["net_scores"]))
check("strongest axis identified", ev is not None and ev["strongest_axes"] == ["authority"])
v = dict(ZERO, authority_asset=1.0, attitude_asset=1.0)
check("ties: every axis at the top net score is included",
      _build_asset_evidence(v, [], INTAKE)["strongest_axes"] == ["authority", "attitude"])

# Real answer paths over the live core sequence
_src = open("web/lib/session-store.ts", encoding="utf-8").read().split("export const PHASE_1_QUESTION_SEQUENCE", 1)[1]
seq = [q for q in re.findall(r'"([A-Z0-9-]+)"', _src[:_src.index("];")]) if q in L]
AFS = ["aptitude_asset", "authority_asset", "alliance_asset", "attitude_asset"]
def _path(pick):
    log, sess = [], AccumulationSession()
    for q in seq:
        o = pick(L[q].answer_options, key=lambda o: sum(o.dimensional_contributions.get(f, 0) for f in AFS))
        log.append({"question_id": q, "option_ids": [o.option_id]})
        accumulate_answer(sess, o, INTAKE, q)
    return sess.accumulated_vector, log
vec, log = _path(max)
ev = _build_asset_evidence(vec, log, INTAKE)
obs = {o.observation_text for q in L.values() for o in q.answer_options if o.observation_text}
check("strength path produces evidence", ev is not None and bool(ev["strongest_axes"]), str(ev))
check("contributing signals are authored observation_text only",
      all(sig["observation_text"] in obs for sig in ev["contributing_signals"]))
check("contributing signals only support a strongest axis",
      all(sig["axis"] in ev["strongest_axes"] for sig in ev["contributing_signals"]))
check("contributing signals are deduplicated",
      len({s["observation_text"] for s in ev["contributing_signals"]}) == len(ev["contributing_signals"]))
vec, log = _path(min)
ev_min = _build_asset_evidence(vec, log, INTAKE)
check("weakest path: Q03B floor removed, little or no net evidence",
      ev_min is None or max(ev_min["net_scores"].values()) <= 0.25, str(ev_min and ev_min["net_scores"]))

# Through run_accumulated_engine/assemble_output: no key at all when net is zero
import engine.main as _m
class _NoSynth:
    def __init__(self, *a, **k): pass
    def synthesize(self, **k): return None
_orig = _m.OutputSynthesisEngine
_m.OutputSynthesisEngine = _NoSynth
try:
    out = _m.run_accumulated_engine(
        dict(ZERO, authority_liability=3.0, attitude_liability=2.0),
        {"headcount": 175, "industry": "Professional Services", "org_type": "Privately held professional leadership",
         "jurisdictions": ["OH"], "significant_events": ["none"], "principal_role": "Owner / Founder"},
        20, {}, [], base_log)
finally:
    _m.OutputSynthesisEngine = _orig
check("assemble_output omits asset_evidence (no key) when all net scores are zero",
      "asset_evidence" not in out["private_output"], str(out["private_output"].get("asset_evidence")))


# ── 5. all_qualified_states + service_cost_comparison ───────────────────────────
def _run(brand, vector):
    _m.OutputSynthesisEngine = _NoSynth
    try:
        return _m.run_accumulated_engine(
            vector,
            {"headcount": 175, "industry": "Professional Services", "org_type": "Privately held professional leadership",
             "jurisdictions": ["OH"], "significant_events": ["none"], "principal_role": "Owner / Founder"},
            40, {}, [], [], brand=brand)
    finally:
        _m.OutputSynthesisEngine = _orig

# A realistic path vector: weakest-asset (problem-heavy) answers across the core sequence
vec, _log = _path(min)
for brand in ("principal_resolution", "hr_diagnostic"):
    out = _run(brand, vec)
    aqs = out["all_qualified_states"]
    ids_ = [s["state_id"] for s in out["identified_states"]]
    check(f"[{brand}] all_qualified_states is score-descending", [s["score"] for s in aqs] == sorted((s["score"] for s in aqs), reverse=True))
    check(f"[{brand}] identified_states is a prefix-consistent subset of all_qualified_states",
          all(i in [s["state_id"] for s in aqs] for i in ids_))
    if out["output_type"] == "single_state":
        check(f"[{brand}] single mode: identified_states keeps only the lead", len(ids_) == 1)
    scc = out["private_output"].get("service_cost_comparison")
    check(f"[{brand}] service_cost_comparison present with null estimates and empty note",
          scc is not None and scc["service_estimate_low"] is None and scc["service_estimate_high"] is None
          and scc["pricing_model_note"] == "", str(scc))
    fte = out["private_output"]["friction_tax_estimate"]; lte = out["private_output"]["legal_tail_risk_exposure"]
    exp_low = (fte["low"] if fte else 0) + (lte["low"] if lte and lte["low"] is not None else 0)
    check(f"[{brand}] inaction cost = priced friction + priced legal", scc and abs((scc["inaction_cost_low"] or 0) - exp_low) < 0.05,
          f"{scc and scc['inaction_cost_low']} vs {exp_low}")
    routing = out["private_output"]["resolution_routing"]
    if brand == "hr_diagnostic":
        check("[hr_diagnostic] target_service_name is HR Consulting (or empty with no routing)",
              scc["target_service_name"] == ("HR Consulting" if routing else ""), scc["target_service_name"])
    else:
        from engine.resolution_families import translate_resolution_family
        check("[principal_resolution] target_service_name is the commercial family name",
              scc["target_service_name"] == translate_resolution_family(routing), scc["target_service_name"])

# Single mode with several above-floor states: the field carries them all, dollars unchanged
from engine.output import route_output, QualifiedState
qs = [QualifiedState(rank=i + 1, state_id=s, state_name=s, score=sc, noise_baseline=0.0, signal_floor=0.0,
                     cleared_floor=True, score_lift_pct=0.0, resolution_family="")
      for i, (s, sc) in enumerate([("built_to_fail", 0.9), ("the_uninitiated", 0.4), ("the_founders_grip", 0.35)])]
r = route_output(qs)
check("single mode keeps every above-floor state in routing.qualified_states (the source of all_qualified_states)",
      r.mode == "single" and len(r.qualified_states) == 3, f"{r.mode} {len(r.qualified_states)}")


print(f"\nRESULT: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
