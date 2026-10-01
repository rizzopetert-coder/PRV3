"""Ranker test 01, implemented to the definitions frozen in prompts/ranker-test-01-preregistration.md (commit 612f125).
Every figure is generated here from the saved run files or from live calls into the production engine functions.

Frozen-definition map (doc wording -> code):
  R0  current production: weighted cosine on the displaced 8-field vector, 0.05 margin gate
      -> r0_scores(): engine.accumulation.rank_states(vector, N, SALIENCE_PROFILES); qualifying = engine.output.check_signal_gate
  R1  R0 ordering, margin gate 0.02 (breadth only)
      -> r1_qualifying(): same R0 scores, score >= rank-1 - 0.02 and >= SCD_WCS_ALIGNMENT_THRESHOLD
  R2  question-local evidence: per answered question, per state in q.state_targets, add the chosen options' post-pipeline
      contribution on the state's primary liability field, divide by n[s] (wired questions answered), 0.0 when n[s] == 0
      -> r2_scores()
  R3  question-local cosine: per state, vector accumulated only from its wired answered questions, displaced by
      MC_CENTROID_39 * CENTROID_FIELD_SCALARS * (N_s / 42) with N_s = n[s], weighted cosine with the state's own salience
      against its own dimensional_vector, 0.0 when n[s] == 0 or the rank_states guards trip -> r3_scores()

Usage:
  python tools/ranker_test_01.py                         # print the RESULTS section
  python tools/ranker_test_01.py --append --dry-run      # check append-only
  python tools/ranker_test_01.py --append --write        # append to prompts/ranker-test-01-preregistration.md
"""
import argparse
import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
from engine.accumulation import (  # noqa: E402
    AccumulationSession, accumulate_answer, rank_states, MC_CENTROID_39, CENTROID_FIELD_SCALARS,
)
from engine.data.questions import QUESTION_LIBRARY  # noqa: E402
from engine.data.salience import SALIENCE_PROFILES  # noqa: E402
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS  # noqa: E402
from engine.main import accumulate_answers, _locked_intake_to_engine_intake  # noqa: E402
from engine.output import SCD_WCS_ALIGNMENT_THRESHOLD, SCD_WCS_MARGIN_GATE, check_signal_gate  # noqa: E402

PREREG = ROOT / "prompts" / "ranker-test-01-preregistration.md"
EXP01_RUN = Path(r"C:\Users\rizzo\Downloads\prv3-experiment-01-run.json")
EXP01_RES = Path(r"C:\Users\rizzo\Downloads\prv3-experiment-01-result.json")
BENCH_DIR = Path(r"C:\Users\rizzo\Downloads\benchmark-01")
F = list(DIMENSIONAL_FIELDS)
SIDS = list(STATE_PROFILES)  # insertion order = rank_states tiebreak order
R1_GATE = 0.02
TARGETS = {"P1": "the_unformed_leader", "P2": "the_untouchable", "P3": "the_overloaded_manager",
           "P4": "decision_paralysis", "P5": "pay_exposure", "P6": "the_culture_that_wasnt"}
_DIM = {"Aptitude": "aptitude_liability", "Authority": "authority_liability", "Alliance": "alliance_liability", "Attitude": "attitude_liability"}


def answered(run):
    return [(e["request"]["question_id"], e["request"]["option_ids"]) for e in run["exchanges"]
            if e["path"].endswith("/session/answer") and e.get("http_status") == 200]


def load_paths():
    paths = []
    run = json.load(open(EXP01_RUN, encoding="utf-8"))
    res = json.load(open(EXP01_RES, encoding="utf-8"))
    paths.append({"id": "EXP01", "target": "the_unformed_leader", "intake": run["intake_wire"], "answers": answered(run), "live": res["all_qualified_states"]})
    for pid in TARGETS:
        for fr in ("cautious", "strong"):
            r = json.load(open(BENCH_DIR / f"{pid}-{fr}.json", encoding="utf-8"))
            paths.append({"id": f"{pid}-{fr}", "target": TARGETS[pid], "intake": r["intake_wire"], "answers": answered(r), "live": r["result"]["all_qualified_states"]})
    return paths


def option_contrib(intake_data, qid, oid):
    """Post-pipeline contribution of one option (role coefficient and axis modifiers included), via accumulate_answer."""
    q = QUESTION_LIBRARY[qid]
    opt = next(o for o in q.answer_options if o.option_id == oid)
    s = AccumulationSession()
    accumulate_answer(s, opt, intake_data, qid)
    return s.accumulated_vector


# ---------------- rankers ----------------
def r0_scores(intake, answers):
    vec = {f: 0.0 for f in F}
    for qid, opts in answers:
        vec = accumulate_answers(vec, qid, opts, intake)["accumulated_vector"]
    rk = rank_states(vec, len(answers), SALIENCE_PROFILES)
    return {r.state_id: r.score for r in rk}, [r.state_id for r in rk]


def wired_answers(intake_data, answers):
    """{state: [(qid, [per-option contribution dicts])]}, one entry per wired answered question (a question counts once)."""
    out = {s: [] for s in SIDS}
    for qid, opts in answers:
        q = QUESTION_LIBRARY[qid]
        contribs = [option_contrib(intake_data, qid, o) for o in opts]
        for s in (q.state_targets or []):
            if s in out:
                out[s].append((qid, contribs))
    return out


def r2_scores(wired):
    sc, n = {}, {}
    for s in SIDS:
        n[s] = len(wired[s])
        fld = _DIM[STATE_PROFILES[s].primary_dimension]
        total = sum(c[fld] for _, contribs in wired[s] for c in contribs)
        sc[s] = total / n[s] if n[s] > 0 else 0.0
    return sc, n


def r3_scores(wired):
    sc = {}
    for s in SIDS:
        Ns = len(wired[s])
        if Ns == 0:
            sc[s] = 0.0
            continue
        v = np.zeros(len(F))
        for _, contribs in wired[s]:
            for c in contribs:
                v += np.array([c[f] for f in F])
        mu = np.array([MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS.get(f, 1.0) * (Ns / 42.0) for f in F])
        A = v - mu
        if np.linalg.norm(A) < 1e-5:
            sc[s] = 0.0
            continue
        B = np.array([STATE_PROFILES[s].dimensional_vector.as_dict().get(f, 0.0) for f in F])
        sw = SALIENCE_PROFILES.get(s, {f: 1.0 for f in F})
        W = np.array([sw.get(f, 1.0) for f in F])
        num = float(np.sum(W * A * B))
        den = float(np.sqrt(np.sum(W * A ** 2)) * np.sqrt(np.sum(W * B ** 2)))
        sc[s] = num / den if den > 1e-5 else 0.0
    return sc


def r0_qualifying(scores_sorted):
    r1 = scores_sorted[0][1]
    return sum(1 for _, v in scores_sorted if check_signal_gate(v, rank_1_score=r1))


def r1_qualifying(scores_sorted):
    r1 = scores_sorted[0][1]
    return sum(1 for _, v in scores_sorted if v >= SCD_WCS_ALIGNMENT_THRESHOLD and v >= r1 - R1_GATE)


def ordered(scores):
    """Stable sort, score descending, ties in STATE_PROFILES insertion order (as rank_states does)."""
    return sorted(((s, scores[s]) for s in SIDS), key=lambda kv: -kv[1])


def summarize(scores, target):
    o = ordered(scores)
    ids = [s for s, _ in o]
    ts = scores[target]
    tie_rank = 1 + sum(1 for _, v in o if round(v, 6) > round(ts, 6))
    return {"ordered": o, "rank": ids.index(target) + 1, "tie_rank": tie_rank, "score": ts,
            "top3": ids.index(target) + 1 <= 3, "top5": ids.index(target) + 1 <= 5,
            "margin": o[0][1] - o[1][1], "r1_tie": round(o[0][1], 6) == round(o[1][1], 6)}


def evaluate(path):
    idata = _locked_intake_to_engine_intake(path["intake"])
    s0, order0 = r0_scores(path["intake"], path["answers"])
    wired = wired_answers(idata, path["answers"])
    s2, n = r2_scores(wired)
    s3 = r3_scores(wired)
    return {"s0": s0, "s2": s2, "s3": s3, "n": n, "N": len(path["answers"]),
            "R0": summarize(s0, path["target"]), "R2": summarize(s2, path["target"]), "R3": summarize(s3, path["target"]),
            "q0": r0_qualifying(ordered(s0)), "q1": r1_qualifying(ordered(s0))}


def replay_ok(path, ev):
    live = path["live"]
    o = ev["R0"]["ordered"]
    ids_ok = [s for s, _ in o[: len(live)]] == [x["state_id"] for x in live]
    diff = max(abs(v - x["score"]) for (_, v), x in zip(o, live))
    return ids_ok and diff < 5e-7, diff


def pf(x, d=4):
    return f"{x:.{d}f}"


def build():
    L = []
    w = L.append
    paths = load_paths()
    evals, valid, excl = {}, [], []
    for p in paths:
        ev = evaluate(p)
        ok, diff = replay_ok(p, ev)
        evals[p["id"]] = (ev, ok, diff)
        (valid if ok else excl).append(p)
    w("")
    w("## RESULTS")
    w("")
    w("Produced by `tools/ranker_test_01.py` (committed with this section) to the definitions frozen at `612f125`. The text above this section is unchanged. Every figure is generated by the script from the saved run files (`prv3-experiment-01-run.json`, `prv3-experiment-01-result.json`, `benchmark-01/<persona>-<framing>.json`) and live calls into the production engine functions.")
    w("")
    w("### Replay check (R0 against the live ranking)")
    w("")
    w("| Path | Answers | Live qualified states | State order identical | Max abs score diff | Valid |")
    w("|---|---:|---:|:-:|---:|:-:|")
    for p in paths:
        ev, ok, diff = evals[p["id"]]
        o = ev["R0"]["ordered"][: len(p["live"])]
        same = [s for s, _ in o] == [x["state_id"] for x in p["live"]]
        w(f"| {p['id']} | {ev['N']} | {len(p['live'])} | {'Y' if same else 'N'} | {diff:.9f} | {'Y' if ok else 'EXCLUDED'} |")
    w("")
    w(f"Valid paths: {len(valid)} of {len(paths)}. Exclusions: {', '.join(p['id'] for p in excl) or 'none'}.")
    w("")
    # (a)
    w("### (a) Per path: target rank, hits, rank-1 ties, qualifying counts")
    w("")
    w("Rank is the stable-sort position (primary, used for hits). Tie-incl is 1 + the number of states with a strictly higher score at 6 dp.")
    w("")
    w("| Path | Target | R0 rank | R0 tie-incl | R2 rank | R2 tie-incl | R3 rank | R3 tie-incl | Top-3 R0/R2/R3 | Top-5 R0/R2/R3 | Rank-1 tie R0/R2/R3 | R0 qualifying | R1 qualifying |")
    w("|---|---|---:|---:|---:|---:|---:|---:|:-:|:-:|:-:|---:|---:|")
    yn = lambda b: "Y" if b else "N"
    for p in valid:
        ev = evals[p["id"]][0]
        a, b, c = ev["R0"], ev["R2"], ev["R3"]
        w(f"| {p['id']} | {p['target']} | {a['rank']} | {a['tie_rank']} | {b['rank']} | {b['tie_rank']} | {c['rank']} | {c['tie_rank']} | {yn(a['top3'])}/{yn(b['top3'])}/{yn(c['top3'])} | {yn(a['top5'])}/{yn(b['top5'])}/{yn(c['top5'])} | {yn(a['r1_tie'])}/{yn(b['r1_tie'])}/{yn(c['r1_tie'])} | {ev['q0']} | {ev['q1']} |")
    w("")
    w("Target score and rank 1 to rank 2 margin per ranker (margins are not comparable across rankers):")
    w("")
    w("| Path | Target score R0 / R2 / R3 | Margin R0 / R2 / R3 |")
    w("|---|---|---|")
    for p in valid:
        ev = evals[p["id"]][0]
        a, b, c = ev["R0"], ev["R2"], ev["R3"]
        w(f"| {p['id']} | {pf(a['score'], 6)} / {pf(b['score'], 6)} / {pf(c['score'], 6)} | {pf(a['margin'], 6)} / {pf(b['margin'], 6)} / {pf(c['margin'], 6)} |")
    w("")
    # (b)
    w("### (b) Top 5 states under R2 and under R3, with scores")
    w("")
    for p in valid:
        ev = evals[p["id"]][0]
        w(f"**{p['id']}** (target {p['target']}, N answers {ev['N']})")
        w("")
        w("| # | R2 state | R2 score | n | R3 state | R3 score | n |")
        w("|---:|---|---:|---:|---|---:|---:|")
        o2, o3 = ev["R2"]["ordered"][:5], ev["R3"]["ordered"][:5]
        for i in range(5):
            w(f"| {i+1} | {o2[i][0]} | {pf(o2[i][1], 6)} | {ev['n'][o2[i][0]]} | {o3[i][0]} | {pf(o3[i][1], 6)} | {ev['n'][o3[i][0]]} |")
        w("")
    # (c)
    w("### (c) n[s], wired questions answered, for the target and for each top-3 state under R2")
    w("")
    w("n[s] is the same under R3. The number of questions that wire each state in the whole library is shown as 'wired total'.")
    w("")
    wired_total = {s: sum(1 for q in QUESTION_LIBRARY.values() if s in (q.state_targets or [])) for s in SIDS}
    w("| Path | State | Role | n answered | wired total | R2 score | R2 rank |")
    w("|---|---|---|---:|---:|---:|---:|")
    for p in valid:
        ev = evals[p["id"]][0]
        ids2 = [s for s, _ in ev["R2"]["ordered"]]
        rows = [(p["target"], "target")] + [(s, f"R2 top-{i+1}") for i, (s, _) in enumerate(ev["R2"]["ordered"][:3])]
        for s, role in rows:
            w(f"| {p['id']} | {s} | {role} | {ev['n'][s]} | {wired_total[s]} | {pf(ev['s2'][s], 6)} | {ids2.index(s) + 1} |")
    w("")
    # RT4
    sel = random.Random(20261001).sample(sorted(STATE_PROFILES), 13)
    from tools.calibration_runner import generate_answers
    from engine.test_suite import TestCase
    base_intake = json.load(open(EXP01_RUN, encoding="utf-8"))["intake_wire"]
    idata_cal = {"significant_events": base_intake["significant_events"]}
    rt4 = []
    for t in sel:
        tc = TestCase(test_id="RT4-" + t, description="", profile_type="high_confidence", target_state=t,
                      intake=idata_cal, answers=[], expected=None)
        ans = [(a.question_id, list(a.selected_option_ids)) for a in generate_answers(tc)]
        pth = {"id": "RT4-" + t, "target": t, "intake": base_intake, "answers": ans}
        ev = evaluate(pth)
        rt4.append((pth, ev))
    w("### RT4 control: 13 calibration-style profiles")
    w("")
    w(f"Targets drawn with `random.Random(20261001).sample(sorted(STATE_PROFILES), 13)`. Answers from `tools.calibration_runner.generate_answers` (high_confidence, no severity follow-ons), intake = the Experiment 01 wire intake (`generate_answers` reads only its significant_events). A hit is target stable-sort rank 3 or better.")
    w("")
    w("| Target | Answers | R0 rank | R2 rank | R3 rank | Hit R0 | Hit R2 | Hit R3 | n[target] |")
    w("|---|---:|---:|---:|---:|:-:|:-:|:-:|---:|")
    for pth, ev in rt4:
        w(f"| {pth['target']} | {ev['N']} | {ev['R0']['rank']} | {ev['R2']['rank']} | {ev['R3']['rank']} | {yn(ev['R0']['top3'])} | {yn(ev['R2']['top3'])} | {yn(ev['R3']['top3'])} | {ev['n'][pth['target']]} |")
    rt4h = {k: sum(ev[k]["top3"] for _, ev in rt4) for k in ("R0", "R2", "R3")}
    w("")
    w(f"RT4 hits: R0 {rt4h['R0']} of 13 (reference only), R2 {rt4h['R2']} of 13, R3 {rt4h['R3']} of 13.")
    w("")
    # (d)
    nv = len(valid)
    hits = {k: sum(evals[p["id"]][0][k]["top3"] for p in valid) for k in ("R0", "R2", "R3")}
    hits5 = {k: sum(evals[p["id"]][0][k]["top5"] for p in valid) for k in ("R0", "R2", "R3")}
    tie = {k: sum(evals[p["id"]][0][k]["r1_tie"] for p in valid) for k in ("R0", "R2", "R3")}
    w("### (d) Hypotheses, scored per the arithmetic in the pre-registration")
    w("")
    w(f"Valid paths: {nv}. Top-3 hits: R0 {hits['R0']}, R2 {hits['R2']}, R3 {hits['R3']}. Top-5 hits: R0 {hits5['R0']}, R2 {hits5['R2']}, R3 {hits5['R3']}. Rank-1 ties: R0 {tie['R0']}, R2 {tie['R2']}, R3 {tie['R3']} (rates {tie['R0']/nv:.3f}, {tie['R2']/nv:.3f}, {tie['R3']/nv:.3f}).")
    w("")
    rt1 = "HOLDS" if hits["R0"] <= 3 else "FAILS"
    w(f"- **RT1** (R0 top-3 hits are 3 or fewer of {nv}): **{rt1}**. R0 hits = {hits['R0']}. (Not blind: the R0 benchmark numbers were seen before the definitions were frozen, as disclosed.)")
    d2, d3 = hits["R2"] - hits["R0"], hits["R3"] - hits["R0"]
    rt2 = "HOLDS" if max(d2, d3) >= 3 else "FAILS"
    w(f"- **RT2** (R2 or R3 achieves at least 3 more top-3 hits than R0): **{rt2}**. R2 minus R0 = {d2:+d}, R3 minus R0 = {d3:+d}.")
    t2, t3 = tie["R2"] / nv < tie["R0"] / nv, tie["R3"] / nv < tie["R0"] / nv
    rt3 = "HOLDS" if (t2 and t3) else ("PARTIAL" if (t2 or t3) else "FAILS")
    w(f"- **RT3** (rank-1 tie rate lower under R2 and R3 than under R0): **{rt3}**. Rates R0 {tie['R0']/nv:.3f}, R2 {tie['R2']/nv:.3f}, R3 {tie['R3']/nv:.3f}. R2 lower: {yn(t2)}. R3 lower: {yn(t3)}.")
    c2, c3 = rt4h["R2"] >= 10, rt4h["R3"] >= 10
    rt4v = "HOLDS" if (c2 and c3) else ("PARTIAL" if (c2 or c3) else "FAILS")
    w(f"- **RT4** (R2 and R3 each reach 10 or more of 13 on the calibration-style profiles): **{rt4v}**. R2 {rt4h['R2']} of 13 ({'met' if c2 else 'not met'}), R3 {rt4h['R3']} of 13 ({'met' if c3 else 'not met'}).")
    w("")
    w("Registered caveats stand as written above (R2 and RT4 are near-circular by construction, rank ties are broken by registry order, R0 numbers were seen before freezing).")
    w("")
    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    section = build()
    if not a.append:
        sys.stdout.reconfigure(encoding="utf-8")
        print(section)
        sys.exit(0)
    raw = PREREG.read_bytes()
    crlf = b"\r\n" in raw
    old = raw.decode("utf-8")
    base = old.rstrip("\r\n")
    assert "\n## RESULTS" not in base, "RESULTS section already present"
    new_text = base.replace("\r\n", "\n") + "\n" + section
    new = new_text.replace("\n", "\r\n") if crlf else new_text
    assert new.startswith(base), "existing text must be unchanged"
    print(f"append-only ok: {len(old)} -> {len(new)} chars, newline {'CRLF' if crlf else 'LF'}")
    if a.write:
        PREREG.write_bytes(new.encode("utf-8"))
        print("WROTE")
    else:
        print("DRY RUN")
