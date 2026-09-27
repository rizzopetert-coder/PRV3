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
    aqs = out["private_output"]["all_qualified_states"]
    check(f"[{brand}] top level stays at the pinned 16 fields", len(out) == 16, str(len(out)))
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


# ── 6. Tactical pre-aggregation (deterministic) ─────────────────────────────────
from engine.tactical_synthesis import (
    build_tactical_summary, tactical_totals, synthesize_tactical, TACTICAL_SECTIONS,
    TACTICAL_SYNTHESIS_SYSTEM_PROMPT,
)
from engine.exec_summary import EXEC_SUMMARY_SYSTEM_PROMPT
from engine.output_synthesis import OUTPUT_SYNTHESIS_SYSTEM_PROMPT
tc_log = [
    {"question_id": "Q05", "option_ids": ["C"]},                       # non-TC: ignored
    {"question_id": "TC-HIRE-01", "option_ids": ["A"]},
    {"question_id": "TC-HRPOL-01", "option_ids": ["A"]},
    {"question_id": "TC-HRPOL-02", "option_ids": ["B"]},
    {"question_id": "TC-HRPOL-03", "option_ids": ["C"]},
    {"question_id": "TC-HRPOL-04", "option_ids": ["D"]},
    {"question_id": "TC-NOPE-01", "option_ids": ["A"]},                # unknown section: ignored
]
summ = build_tactical_summary(tc_log)
check("pre-aggregation: sections in report order, only answered ones",
      list(summ) == ["TC-HR_POLICIES", "TC-HIRING_ONBOARDING"], str(list(summ)))
hr = summ["TC-HR_POLICIES"]
check("pre-aggregation: totals and flagged counts", hr["total"] == 4 and hr["flagged_count"] == 3
      and summ["TC-HIRING_ONBOARDING"]["flagged_count"] == 0)
check("pre-aggregation: A solid, B minor, C/D severe",
      [i["severity"] for i in hr["flagged_items"]] == ["minor", "severe", "severe"])
check("pre-aggregation: approved section names",
      [n for _, _, n in TACTICAL_SECTIONS] == ["HR Practices & Policies", "Hiring & Onboarding", "Payroll & Wage-Hour",
      "Compensation Compliance", "Benefits Compliance", "Leave Management", "Workplace Safety", "Records & Privacy",
      "HR Systems & Data", "Performance Management"])
check("tactical_totals", tactical_totals(summ) == {"flagged_count": 3, "total_count": 5, "severe_count": 2,
      "sections_with_gaps": 1, "sections_total": 2}, str(tactical_totals(summ)))
check("pre-aggregation: no TC answers -> {}", build_tactical_summary([{"question_id": "Q05", "option_ids": ["A"]}]) == {})

# ── 7. Three-call flow, with a recording fake anthropic client ──────────────────
import json as _json, time as _time, types as _types, os as _os
CALLS = []
FAIL = set()
DELAY = {"call1": 0.0, "call2": 0.0, "call3": 0.0}
def _which(system):
    return {OUTPUT_SYNTHESIS_SYSTEM_PROMPT: "call1", TACTICAL_SYNTHESIS_SYSTEM_PROMPT: "call2",
            EXEC_SUMMARY_SYSTEM_PROMPT: "call3"}.get(system, "other")
class _Msg:
    def __init__(self, text): self.content = [_types.SimpleNamespace(text=text)]
class _Messages:
    def create(self, **kw):
        which = _which(kw.get("system"))
        CALLS.append((which, kw, _time.monotonic()))
        _time.sleep(DELAY.get(which, 0))
        if which in FAIL:
            raise RuntimeError(f"forced {which} failure")
        if which == "call1":
            return _Msg(_json.dumps({"liability_condition_text": "Decisions stall at the top.",
                "asset_resolution_anchor_text": "Teams still deliver.", "framing_text": "A framing.",
                "observable_indicators": ["a", "b", "c"], "resolution_framing_text": "A path.",
                "headline": "Decisions are starting to stall across the leadership team", "synthesis_confidence": 0.8}))
        if which == "call2":
            ids = [l.split(": ", 1)[1] for l in kw["messages"][0]["content"].splitlines() if l.startswith("section_id: ")]
            return _Msg(_json.dumps({i: f"Finding for {i}; with a semicolon." for i in ids}))
        return _Msg("The organizational finding and the HR review point the same way.")
class _FakeAnthropic:
    def __init__(self, *a, **k): self.messages = _Messages()
_fake_mod = _types.ModuleType("anthropic"); _fake_mod.Anthropic = _FakeAnthropic
_real_mod = sys.modules.get("anthropic")
INTAKE_WIRE = {"headcount": 175, "industry": "Professional Services", "org_type": "Privately held professional leadership",
               "jurisdictions": ["OH"], "significant_events": ["none"], "principal_role": "Owner / Founder"}
full_log = _log + tc_log
def _complete(log, brand="hr_diagnostic"):
    CALLS.clear()
    sys.modules["anthropic"] = _fake_mod
    try:
        return _m.run_accumulated_engine(vec, INTAKE_WIRE, 40, {}, [], log, brand=brand)
    finally:
        if _real_mod is not None: sys.modules["anthropic"] = _real_mod
        else: sys.modules.pop("anthropic", None)

FAIL.clear()
ok_out = _complete(full_log)
kinds = [c[0] for c in CALLS]
check("success: Call 1, Call 2, and Call 3 all run", sorted(kinds) == ["call1", "call2", "call3"], str(kinds))
check("success: executive_summary populated", ok_out["synthesis"]["executive_summary"] != "")
tf = ok_out["private_output"]["tactical_findings"]
check("success: one finding per answered section, flagged sections have text",
      [f["section_id"] for f in tf] == ["TC-HR_POLICIES", "TC-HIRING_ONBOARDING"]
      and tf[0]["synthesis_text"] and tf[1]["synthesis_text"] == "")
check("findings: house punctuation enforced on model text", ";" not in tf[0]["synthesis_text"])
check("findings: flagged_items never carry answer (option) text",
      all("answer_text" not in i for f in tf for i in f["flagged_items"]))
call1_prompt = next(c[1] for c in CALLS if c[0] == "call1")["messages"][0]["content"]
tc_texts = [L[e["question_id"]].question_text for e in tc_log if e["question_id"] in L]
check("REGRESSION: Call 1 prompt contains no tactical content",
      "TC-" not in call1_prompt and not any(t in call1_prompt for t in tc_texts)
      and not any(n in call1_prompt for _, _, n in TACTICAL_SECTIONS))
call3_prompt = next(c[1] for c in CALLS if c[0] == "call3")["messages"][0]["content"]
check("Call 3 input = Call 1 liability text + raw tactical counts",
      "Decisions stall at the top." in call3_prompt and "3 of 5 answers show a gap" in call3_prompt, call3_prompt)
call2_prompt = next(c[1] for c in CALLS if c[0] == "call2")["messages"][0]["content"]
check("Call 2 input = the pre-aggregation only (no core liability text)", "Decisions stall" not in call2_prompt)

# Concurrency: with 0.5s per call, Step A overlaps and Step B follows
DELAY.update(call1=0.5, call2=0.5, call3=0.5)
_complete(full_log)
t = {c[0]: c[2] for c in CALLS}
check("Step A: Call 2 starts before Call 1 finishes (concurrent)", abs(t["call1"] - t["call2"]) < 0.4, str(t))
check("Step B: Call 3 starts after both finish", t["call3"] - max(t["call1"], t["call2"]) >= 0.45, str(t))
DELAY.update(call1=0.0, call2=0.0, call3=0.0)

def _core(out):
    s = dict(out["synthesis"]); s.pop("executive_summary", None)
    return s
FAIL.clear(); FAIL.add("call2")
c2_out = _complete(full_log)
check("Call 2 failure: tactical_findings [] and no crash", c2_out["private_output"]["tactical_findings"] == [])
check("Call 2 failure: Call 3 skipped, executive_summary ''",
      "call3" not in [c[0] for c in CALLS] and c2_out["synthesis"]["executive_summary"] == "")
check("Call 2 failure: Call 1 result identical, no fallback", _core(c2_out) == _core(ok_out) and not c2_out["synthesis"]["is_fallback"])

FAIL.clear(); FAIL.add("call3")
c3_out = _complete(full_log)
check("Call 3 failure: executive_summary '' only", c3_out["synthesis"]["executive_summary"] == ""
      and c3_out["private_output"]["tactical_findings"] == tf and _core(c3_out) == _core(ok_out))

FAIL.clear(); FAIL.add("call1")
c1_out = _complete(full_log)
check("Call 1 failure (fallback): Call 3 skipped, tactical findings still delivered",
      c1_out["synthesis"]["is_fallback"] and "call3" not in [c[0] for c in CALLS]
      and c1_out["synthesis"]["executive_summary"] == "" and c1_out["private_output"]["tactical_findings"] == tf)

FAIL.clear()
pr_out = _complete(_log, brand="principal_resolution")
check("no TC answers: Call 2 and Call 3 never run, findings [], summary ''",
      [c[0] for c in CALLS] == ["call1"] and pr_out["private_output"]["tactical_findings"] == []
      and pr_out["synthesis"]["executive_summary"] == "")

# Non-production debug hook, ignored in production
_os.environ["PRV3_DEBUG_FAIL_CALL"] = "tactical"
_os.environ["VERCEL_ENV"] = "preview"
sys.modules["anthropic"] = _fake_mod
try:
    f_prev = synthesize_tactical(summ)
    _os.environ["VERCEL_ENV"] = "production"
    f_prod = synthesize_tactical(summ)
finally:
    _os.environ.pop("PRV3_DEBUG_FAIL_CALL", None); _os.environ.pop("VERCEL_ENV", None)
    if _real_mod is not None: sys.modules["anthropic"] = _real_mod
check("debug hook forces a Call 2 failure outside production", f_prev[0] == [] and f_prev[1] is False)
check("debug hook is ignored in production", f_prod[1] is True)


# ── 8. observation_valence (Pass 1) ─────────────────────────────────────────────
from collections import Counter as _Counter
from engine.data.questions import PROBLEM_CONTEXT_VALENCES
from engine.contract import _pick_distinct, _build_friction_tax_ledger
_opts = [o for q in L.values() for o in q.answer_options]
check("valence: all 109 authored texts tagged 103 liability / 6 neutral / 0 asset",
      _Counter(o.observation_valence for o in _opts if o.observation_text) == {"liability": 103, "neutral": 6})
check("valence: no text without a valence, no valence without text",
      not any(bool(o.observation_text) != bool(o.observation_valence) for o in _opts))
check("valence: neutral set is exactly Q07-A and Q34-A..E",
      {(k, o.option_id) for k, q in L.items() for o in q.answer_options if o.observation_valence == "neutral"}
      == {("Q07", "A"), ("Q34", "A"), ("Q34", "B"), ("Q34", "C"), ("Q34", "D"), ("Q34", "E")})
check("PROBLEM_CONTEXT_VALENCES = liability + neutral", PROBLEM_CONTEXT_VALENCES == {"liability", "neutral"})

# With no asset-valence text, strength evidence keeps axes and scores but cites nothing
vec_s, log_s = _path(max)
ev = _build_asset_evidence(vec_s, log_s, INTAKE)
check("asset evidence: strongest_axes and net_scores still populate", ev is not None and ev["strongest_axes"] and ev["net_scores"])
check("asset evidence: contributing_signals empty (no asset-valence text authored yet)", ev["contributing_signals"] == [])
q18e = next(o for o in L["Q18"].answer_options if o.option_id == "E")
ev_q18 = _build_asset_evidence(dict(ZERO, attitude_asset=1.0), [{"question_id": "Q18", "option_ids": ["E"]}], INTAKE)
check("the 'safety concerns as strength' bug is gone (Q18-E never cited as a strength)",
      ev_q18 is not None and all(s["observation_text"] != q18e.observation_text for s in ev_q18["contributing_signals"]))

# asset-valence text IS cited as strength; problem readers never cite it
_target = next(o for o in L["Q13"].answer_options if o.option_id == "A")     # carries asset signal
_axis = next(f for f in ["aptitude_asset", "authority_asset", "alliance_asset", "attitude_asset"]
             if _target.dimensional_contributions.get(f, 0) > 0)
_saved = _target.observation_valence
_target.observation_valence = "asset"
try:
    ev_a = _build_asset_evidence(dict(ZERO, **{_axis: 1.0}), [{"question_id": "Q13", "option_ids": ["A"]}], INTAKE)
    check("asset-valence text is cited as a strength", ev_a is not None and
          [s["observation_text"] for s in ev_a["contributing_signals"]] == [_target.observation_text], str(ev_a))
    _log13 = [{"question_id": "Q13", "option_ids": ["A"]}]
    check("receipts never cite asset-valence text",
          all(_target.observation_text not in _top_observation_texts(sid, _log13, INTAKE, limit=None)
              for sid in ["built_to_fail", "the_broken_compass", "leadership_deafness", "the_uninitiated"]))
    _led = _build_friction_tax_ledger([{"state_id": "the_broken_compass", "state_name": "x"}],
                                      [{"state_id": "the_broken_compass", "tier": "Emerging"}], _log13, INTAKE)
    check("ledger top_contributing_answers never cite asset-valence text",
          all(_target.observation_text not in r["top_contributing_answers"] for r in _led))
    check("Call 1 signal map never cites asset-valence text",
          _target.observation_text not in _m._build_signal_map_context(_log13, INTAKE, "the_broken_compass"))
finally:
    _target.observation_valence = _saved
check("signal map still cites the same text when it is problem-context",
      _target.observation_text in _m._build_signal_map_context([{"question_id": "Q13", "option_ids": ["A"]}], INTAKE, "the_broken_compass")
      or _top_observation_texts("the_broken_compass", [{"question_id": "Q13", "option_ids": ["A"]}], INTAKE) == [])

# Receipt variety: a repeat is allowed only when a condition has no unused alternative
check("_pick_distinct prefers an unused answer", _pick_distinct(["a", "b"], {"a"}) == "b")
check("_pick_distinct reuses the top answer when all are used", _pick_distinct(["a"], {"a"}) == "a")
check("_pick_distinct: nothing ranked -> None", _pick_distinct([], set()) is None)
vec_p, log_p = _path(min)
many = ["built_to_fail", "the_overloaded_manager", "the_undefined_role", "the_unsolved_problem", "the_unformed_leader"]
st5 = [{"state_id": s, "state_name": s} for s in many]
fr5 = compute_friction_tax(many, "Emerging", 175, INTAKE.industry, INTAKE.org_type)
rc = [r for r in _friction_driving_factors(fr5, st5, "Emerging", INTAKE, log_p) if r["category"] == "Condition"]
picked = [r.get("triggering_answer") for r in rc]
ok, used = True, set()
for s, pick in zip(many, picked):
    ranked = _top_observation_texts(s, log_p, INTAKE, limit=None)
    if pick is None:
        ok = ok and not ranked
        continue
    if any(t not in used for t in ranked) and pick in used:
        ok = False
    used.add(pick)
check("friction receipts vary: a condition only repeats an answer when it has no unused alternative", ok, str(picked))
check("friction receipts: more than one distinct triggering answer across 5 conditions",
      len({p for p in picked if p}) > 1, str(picked))


# ── 9. Lead resolution family in both routing modes ─────────────────────────────
from engine.contract import lead_resolution_family
from engine.output import route_output, QualifiedState
from engine.data.states import STATE_PROFILES as _SP
def _qs(sid, score, rank):
    return QualifiedState(rank=rank, state_id=sid, state_name=sid, score=score, noise_baseline=0.0, signal_floor=0.0,
                          cleared_floor=True, score_lift_pct=0.0, resolution_family=_SP[sid].resolution_family)
_multi = route_output([_qs("built_to_fail", 0.50, 1), _qs("the_uninitiated", 0.49, 2)])
check("multi-state routing: family comes from the lead state, not empty",
      _multi.mode == "multi" and lead_resolution_family(_multi, None) == _SP["built_to_fail"].resolution_family,
      f"{_multi.mode} {lead_resolution_family(_multi, None)!r}")
_single = route_output([_qs("built_to_fail", 0.9, 1)])
check("single-state routing: unchanged (private block wins when set)",
      lead_resolution_family(_single, type("P", (), {"resolution_family": "Roadmap"})()) == "Roadmap")
check("nothing qualified: empty family", lead_resolution_family(route_output([]), None) == "")
# End to end: the multi-state path vector now yields a non-empty routing
_m.OutputSynthesisEngine = _NoSynth
try:
    _o = _m.run_accumulated_engine(vec_p, INTAKE_WIRE, 40, {}, [], log_p, brand="principal_resolution")
finally:
    _m.OutputSynthesisEngine = _orig
check("run_accumulated_engine: multi-state result has a real resolution_routing",
      _o["output_type"] != "multi_state" or _o["private_output"]["resolution_routing"] != "",
      f"{_o['output_type']} {_o['private_output']['resolution_routing']!r}")
check("service_cost_comparison names the service on a multi-state PR result",
      _o["output_type"] != "multi_state" or _o["private_output"]["service_cost_comparison"]["target_service_name"] != "")


# ── 10. Executive summary length ─────────────────────────────────────────────────
from engine.exec_summary import _limit_sentences, EXEC_SUMMARY_SYSTEM_PROMPT
five = "One thing. Two things here. Three is fine. Four is too many. Five is right out."
check("exec summary guard keeps at most 3 sentences",
      _limit_sentences(five) == "One thing. Two things here. Three is fine.", _limit_sentences(five))
check("exec summary guard leaves 2-3 sentences untouched",
      _limit_sentences("A short one. And a second.") == "A short one. And a second.")
check("exec summary guard does not split on decimals or a lowercase continuation",
      _limit_sentences("Costs rose 2.5 times. Then e.g. more. Three. Four.") == "Costs rose 2.5 times. Then e.g. more. Three.",
      _limit_sentences("Costs rose 2.5 times. Then e.g. more. Three. Four."))
check("exec summary prompt states the strict length",
      "exactly 2 or 3 sentences" in EXEC_SUMMARY_SYSTEM_PROMPT and "70 words" in EXEC_SUMMARY_SYSTEM_PROMPT)

# ── 11. PR backup copy: every family authored, no em-dashes ─────────────────────
from engine.resolution_families import RESOLUTION_FALLBACK_COPY, translate_resolution_family
from engine.data.states import STATE_PROFILES as _SP2
# Zero exceptions since 2026-09-27 (Pete's final four fixes).
check("no em-dash anywhere in RESOLUTION_FALLBACK_COPY",
      not [k for k, v in RESOLUTION_FALLBACK_COPY.items() if "\u2014" in v],
      str(sorted(k for k, v in RESOLUTION_FALLBACK_COPY.items() if "\u2014" in v)))
_compounds = {translate_resolution_family(p.resolution_family) for p in _SP2.values() if " + " in p.resolution_family}
check("every compound family in the taxonomy has authored PR backup copy",
      all((c, None) in RESOLUTION_FALLBACK_COPY for c in _compounds),
      str(sorted(c for c in _compounds if (c, None) not in RESOLUTION_FALLBACK_COPY)))

# ── 12. Causation override: displayed pathway == synthesis family ───────────────
import engine.contract as _ct
from engine.contract import effective_resolution_family
from engine.resolution_families import STATE_CAUSATION_OVERRIDES, translate_resolution_family as _tr
_orig_ccp = _ct.compute_causation_pattern
def _force_pattern(p):
    _ct.compute_causation_pattern = lambda vec, routing: {"pattern": p, "dispersion": 0.0, "qualified_state_count": 1}
_single_uninit = route_output([_qs("the_uninitiated", 0.9, 1)])
try:
    _force_pattern("diffuse")
    check("helper: the_uninitiated + diffuse resolves to the override (Development)",
          effective_resolution_family(_single_uninit, None, {}) == "Development")
    _force_pattern("single_point")
    check("helper: no override for a pattern the state doesn't list",
          effective_resolution_family(_single_uninit, None, {}) == "Intervention")
finally:
    _ct.compute_causation_pattern = _orig_ccp

# End to end: whatever the lead and pattern, Call 1's family == the displayed routing
def _call1_family(out_calls):
    p = next(c[1] for c in out_calls if c[0] == "call1")["messages"][0]["content"]
    return p.split("resolution_family:")[1].splitlines()[0].strip()
_checked = 0
_fired = []  # (sid, pattern, vec) where the override changed the family
for _pattern in ("diffuse", "single_point"):
    for sid in STATE_CAUSATION_OVERRIDES:
        vec_s = {f: float(getattr(_SP[sid].dimensional_vector, f)) * 3.0 for f in _SP[sid].dimensional_vector.__dataclass_fields__} \
            if hasattr(_SP[sid].dimensional_vector, "__dataclass_fields__") else None
        if vec_s is None:
            continue
        _force_pattern(_pattern)
        try:
            FAIL.clear(); CALLS.clear()
            sys.modules["anthropic"] = _fake_mod
            try:
                _out = _m.run_accumulated_engine(vec_s, INTAKE_WIRE, 27, {}, [], [], brand="principal_resolution")
            finally:
                if _real_mod is not None: sys.modules["anthropic"] = _real_mod
                else: sys.modules.pop("anthropic", None)
        finally:
            _ct.compute_causation_pattern = _orig_ccp
        _routing = _out["private_output"]["resolution_routing"]
        if not _routing or not any(c[0] == "call1" for c in CALLS):
            continue
        from engine.output_synthesis import _family_as_prose
        if _call1_family(CALLS) != _family_as_prose(_tr(_routing)):
            check(f"[{sid} / {_pattern}] Call 1 family matches the displayed pathway", False,
                  f"call1={_call1_family(CALLS)!r} displayed={_tr(_routing)!r}")
        _checked += 1
        _lead = _SP[sid].resolution_family
        if _routing != _lead and STATE_CAUSATION_OVERRIDES[sid].get(_pattern) == _routing:
            _fired.append((sid, _pattern, vec_s))
check(f"end to end: Call 1's family equals the displayed pathway for every override state and pattern ({_checked} runs)",
      _checked > 0)
check(f"end to end: the override actually re-routed some runs ({len(_fired)}), so the check has teeth",
      len(_fired) > 0, str([(s, p) for s, p, _ in _fired]))
# Fallback path uses the displayed family too, on a run where the override fired
_fb_sid, _fb_pattern, _fb_vec = _fired[0]
_force_pattern(_fb_pattern)
try:
    FAIL.clear(); FAIL.add("call1"); CALLS.clear()
    sys.modules["anthropic"] = _fake_mod
    try:
        _fo = _m.run_accumulated_engine(_fb_vec, INTAKE_WIRE, 27, {}, [], [], brand="principal_resolution")
    finally:
        if _real_mod is not None: sys.modules["anthropic"] = _real_mod
        else: sys.modules.pop("anthropic", None)
finally:
    _ct.compute_causation_pattern = _orig_ccp
    FAIL.clear()
from engine.data.fallback_synthesis import get_fallback_synthesis
_disp = _tr(_fo["private_output"]["resolution_routing"])
check(f"fallback path ({_fb_sid} / {_fb_pattern}): backup copy is the displayed (overridden) family's copy",
      _fo["synthesis"]["is_fallback"] and
      _fo["synthesis"]["resolution_framing_text"] == get_fallback_synthesis(_disp, _fo["severity"]["tier"])["resolution_framing_text"],
      f"displayed={_disp!r}")

print(f"\nRESULT: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
