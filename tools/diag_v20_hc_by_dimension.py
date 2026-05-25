"""
Diagnostic: v20 HC pass breakdown by dimension.
Reports HC passes and sink analysis per primary_dimension group.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.accumulation import AccumulationEngine, IntakeData, identify_dominant_dimension
from engine.data.questions import QUESTION_LIBRARY
from engine.data.states import STATE_PROFILES
from engine.data.salience import SALIENCE_PROFILES
from engine.accumulation import rank_states
from engine.output import OutputEngine, compute_noise_baseline
from tools.calibration_runner import ALL_PROFILES, generate_answers

_NOISE_BASELINE = compute_noise_baseline(random_seed=42)

hc_profiles = [p for p in ALL_PROFILES if p.profile_type == "high_confidence"]

dims = ["Authority", "Aptitude", "Alliance", "Attitude"]
results_by_dim = {d: {"pass": 0, "total": 0, "misses": []} for d in dims}

for tc in hc_profiles:
    intake = IntakeData(**tc.intake)
    acc_engine = AccumulationEngine(intake)
    answers = generate_answers(tc)
    for ans in answers:
        q = QUESTION_LIBRARY.get(ans.question_id)
        if q is None:
            continue
        for opt_id in ans.selected_option_ids:
            opt = next((o for o in q.answer_options if o.option_id == opt_id), None)
            if opt is None:
                continue
            acc_engine.apply_answer(opt, ans.question_id)

    target_dim = STATE_PROFILES[tc.target_state].primary_dimension
    dominant_dim, magnitudes = identify_dominant_dimension(acc_engine.accumulated_vector)

    # Router path
    rankings = rank_states(acc_engine.accumulated_vector, SALIENCE_PROFILES, dominant_dim)

    from engine.severity import SeverityEngine
    from engine.contract import SessionData, assemble_output
    sev_engine = SeverityEngine()
    sev_result = sev_engine.score()
    out_engine = OutputEngine()
    out_engine.set_noise_baseline(baseline=_NOISE_BASELINE)
    out_pkg = out_engine.build(rankings, sev_result)
    session = SessionData(
        session_id=SessionData.new_session_id(),
        intake=intake,
        final_rankings=rankings,
        accumulated_vector=acc_engine.accumulated_vector,
        output_package=out_pkg,
        severity_result=sev_result,
    )
    output = assemble_output(session)

    dist = output.get("state_distribution", [])
    rank1 = next((e["state_id"] for e in dist if e.get("rank") == 1), "insufficient_signal")
    passed = rank1 == tc.target_state

    results_by_dim[target_dim]["total"] += 1
    if passed:
        results_by_dim[target_dim]["pass"] += 1
    else:
        results_by_dim[target_dim]["misses"].append({
            "test_id": tc.test_id,
            "target": tc.target_state,
            "target_dim": target_dim,
            "router_dim": dominant_dim,
            "rank1": rank1,
            "rank1_dim": STATE_PROFILES.get(rank1, {}) and STATE_PROFILES[rank1].primary_dimension if rank1 in STATE_PROFILES else "?",
        })

print("\nv20 HC Pass Count — by primary dimension")
print("=" * 64)
total_pass = 0
total_hc = 0
for dim in dims:
    r = results_by_dim[dim]
    total_pass += r["pass"]
    total_hc += r["total"]
    flag = "" if r["pass"] == r["total"] else f"  ({r['total'] - r['pass']} failed)"
    print(f"  {dim:<12}  {r['pass']}/{r['total']}{flag}")
print(f"  {'TOTAL':<12}  {total_pass}/{total_hc}")

print()
for dim in dims:
    r = results_by_dim[dim]
    if not r["misses"]:
        continue
    print(f"\n{dim} failures ({len(r['misses'])}):")
    # Summarize router_dim and sink
    router_mismatch = sum(1 for m in r["misses"] if m["router_dim"] != dim)
    print(f"  Router dim mismatch (routed away from {dim}): {router_mismatch}/{len(r['misses'])}")

    # Sink summary
    sinks = {}
    for m in r["misses"]:
        sinks[m["rank1"]] = sinks.get(m["rank1"], 0) + 1
    for sink, cnt in sorted(sinks.items(), key=lambda x: -x[1]):
        sink_dim = STATE_PROFILES[sink].primary_dimension if sink in STATE_PROFILES else "?"
        print(f"  -> {sink:<44} x{cnt}  [{sink_dim}]")
