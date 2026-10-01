"""Condition test 01, Part C (data-derived condition count), implemented to the "Part C definitions (frozen before
computation)" section of prompts/condition-test-01-preregistration.md (commit 4b3bc61). Every figure is generated here from
saved run files or live engine calls.

Usage:
  python tools/condition_test_01c.py                      # print the Part C RESULTS section
  python tools/condition_test_01c.py --append --dry-run   # check append-only
  python tools/condition_test_01c.py --append --write     # append to the pre-registration
"""
import argparse
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import tools.condition_test_01 as ct  # noqa: E402
import tools.ranker_test_01 as rt1  # noqa: E402
import tools.calibration_runner as cr  # noqa: E402
from engine.accumulation import IntakeData, AccumulationEngine, MC_CENTROID_39, CENTROID_FIELD_SCALARS  # noqa: E402
from engine.data.questions import QUESTION_LIBRARY, DISTINGUISHER_CLUSTER_PREFIXES  # noqa: E402
from engine.data.salience import SALIENCE_PROFILES  # noqa: E402
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS  # noqa: E402
from engine.main import _locked_intake_to_engine_intake  # noqa: E402

PREREG = ROOT / "prompts" / "condition-test-01-preregistration.md"
F = list(DIMENSIONAL_FIELDS)
SIDS = list(STATE_PROFILES)
IDX = {s: i for i, s in enumerate(SIDS)}
yn = lambda b: "Y" if b else "N"
KS = list(range(3, 11))


# ---------------- data ----------------
def load_profiles():
    rows = []
    for tc in cr.ALL_PROFILES:
        idata = IntakeData(**tc.intake)
        eng = AccumulationEngine(idata)
        answers = []
        for a in (tc.answers or cr.generate_answers(tc)):
            answers.append((a.question_id, list(a.selected_option_ids)))
            q = QUESTION_LIBRARY[a.question_id]
            for oid in a.selected_option_ids:
                eng.apply_answer(next(o for o in q.answer_options if o.option_id == oid), a.question_id)
        s0 = {r.state_id: r.score for r in eng.rank(SALIENCE_PROFILES)}
        order = [s for s, _ in rt1.ordered(s0)]
        d = ct.per_run_data(idata, answers, s0)
        rows.append({"id": tc.test_id, "pt": tc.profile_type, "target": tc.target_state, "order": order, "d": d})
    return rows


# ---------------- confusability and clustering ----------------
def confusability(profiles):
    by_t = defaultdict(list)
    for p in profiles:
        by_t[p["target"]].append(p)
    c = {}
    for a in SIDS:
        ps = by_t.get(a, [])
        for b in SIDS:
            if a == b:
                continue
            c[(a, b)] = (sum(1 for p in ps if p["order"].index(b) < p["order"].index(a)) / len(ps)) if ps else 0.0
    s = {(a, b): (c[(a, b)] + c[(b, a)]) / 2 for a in SIDS for b in SIDS if a != b}
    return s, {a: len(by_t.get(a, [])) for a in SIDS}


def identical_groups():
    g = defaultdict(list)
    for sid in SIDS:
        key = (tuple(round(STATE_PROFILES[sid].dimensional_vector.as_dict()[f], 9) for f in F),
               tuple(round(SALIENCE_PROFILES.get(sid, {}).get(f, 1.0), 9) for f in F))
        g[key].append(sid)
    return [v for v in g.values() if len(v) > 1]


def build_units(groups):
    grouped = {s: i for i, g in enumerate(groups) for s in g}
    units, seen = [], set()
    for sid in SIDS:
        if sid in seen:
            continue
        if sid in grouped:
            mem = list(groups[grouped[sid]])
        else:
            mem = [sid]
        for m in mem:
            seen.add(m)
        units.append(mem)
    return units


def upgma(units, s):
    n = len(units)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                D[i, j] = 1.0 - float(np.mean([s[(a, b)] for a in units[i] for b in units[j]]))
    clusters = {i: [i] for i in range(n)}
    snapshots = {}
    merges = []
    while len(clusters) > min(KS):
        best = None
        keys = sorted(clusters, key=lambda k: min(clusters[k]))
        for x in range(len(keys)):
            for y in range(x + 1, len(keys)):
                X, Y = clusters[keys[x]], clusters[keys[y]]
                dist = round(float(np.mean([D[u, v] for u in X for v in Y])), 12)
                cand = (dist, min(X), min(Y), keys[x], keys[y])
                if best is None or cand < best:
                    best = cand
        dist, _, _, kx, ky = best
        clusters[kx] = clusters[kx] + clusters[ky]
        del clusters[ky]
        merges.append((len(clusters), dist))
        if len(clusters) in KS:
            snapshots[len(clusters)] = [sorted(v) for v in clusters.values()]
    snapshots.setdefault(n, [[i] for i in range(n)]) if n in KS else None
    return snapshots, merges


def conditions_for_k(snapshot, units):
    conds = []
    for cl in snapshot:
        members = sorted((s for u in cl for s in units[u]), key=lambda s: IDX[s])
        conds.append(members)
    conds.sort(key=lambda m: IDX[m[0]])
    return conds


# ---------------- scoring (CR3pool on arbitrary member lists, as defined in Part B) ----------------
def cr3pool(members, d):
    qcontrib = {}
    for s in members:
        for qid, contribs in d["wired"][s]:
            qcontrib[qid] = contribs
    if not qcontrib:
        return 0.0
    v = np.zeros(len(F))
    for contribs in qcontrib.values():
        for cc in contribs:
            v += np.array([cc[f] for f in F])
    N = len(qcontrib)
    mu = np.array([MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS.get(f, 1.0) * (N / 42.0) for f in F])
    A = v - mu
    if np.linalg.norm(A) < 1e-5:
        return 0.0
    B = np.mean([[STATE_PROFILES[s].dimensional_vector.as_dict().get(f, 0.0) for f in F] for s in members], axis=0)
    W = np.mean([[SALIENCE_PROFILES.get(s, {}).get(f, 1.0) for f in F] for s in members], axis=0)
    num = float(np.sum(W * A * B))
    den = float(np.sqrt(np.sum(W * A ** 2)) * np.sqrt(np.sum(W * B ** 2)))
    return num / den if den > 1e-5 else 0.0


def judge_groups(conds, d, target):
    scores = [cr3pool(m, d) for m in conds]
    order = sorted(range(len(conds)), key=lambda i: -scores[i])
    tgt = next(i for i, m in enumerate(conds) if target in m)
    return {"lead": order[0], "top1": order[0] == tgt, "top2": tgt in order[:2], "margin": scores[order[0]] - scores[order[1]]}


def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for t in range(i, j + 1):
                r[order[t]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    sx = sum((a - mx) ** 2 for a in rx)
    sy = sum((b - my) ** 2 for b in ry)
    if sx == 0 or sy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy) ** 0.5


# ---------------- live-reachable questions (as in the Diagnostic audit) ----------------
def live_set():
    src = (ROOT / "web" / "lib" / "session-store.ts").read_text(encoding="utf-8")
    blk = src.split("export const PHASE_1_QUESTION_SEQUENCE", 1)[1].split("];", 1)[0]
    blk = re.sub(r"//[^\n]*", "", blk)
    core = re.findall(r'"([A-Z0-9\-]+)"', blk)
    reach = set(core) | {"Q28", "Q45"}
    changed = True
    while changed:
        changed = False
        for qid in list(reach):
            q = QUESTION_LIBRARY.get(qid)
            if q is None:
                continue
            for o in q.answer_options:
                if o.severity_trigger and o.severity_follow_on_id and o.severity_follow_on_id not in reach:
                    reach.add(o.severity_follow_on_id)
                    changed = True
    dist = {qid for pfx in DISTINGUISHER_CLUSTER_PREFIXES.values() for qid in QUESTION_LIBRARY if qid.startswith(pfx)}
    return core, reach | dist


def build():
    L = []
    w = L.append
    prof = load_profiles()
    s_conf, n_prof = confusability(prof)
    groups = identical_groups()
    units = build_units(groups)
    snaps, merges = upgma(units, s_conf)
    paths, pexcl = ct.evaluate_paths()
    npaths = len(paths)
    w("")
    w("## Part C RESULTS")
    w("")
    w("Produced by `tools/condition_test_01c.py` (committed with this section) to the definitions frozen at `4b3bc61`. The text above this section is unchanged. Every figure is generated by the script.")
    w("")
    w(f"Confusability built from {len(prof)} calibration profiles ({min(n_prof.values())} to {max(n_prof.values())} profiles per target state). Identical-vector groups: {len(groups)} groups, {sum(len(g) for g in groups)} states, entered as {len(groups)} units. Units total: {len(units)}. Valid paths: {npaths} of 12 (exclusions: {pexcl or 'none'}).")
    w("")
    w("Highest-merge-distance steps from the dendrogram (clusters remaining after the merge, merge distance): " + ", ".join(f"{k} clusters at {dist:.4f}" for k, dist in merges[-9:]) + ".")
    w("")
    # per k evaluation
    results = {}
    for k in KS:
        conds = conditions_for_k(snaps[k], units)
        pj = [judge_groups(conds, r["d"], r["target"]) for r in paths]
        qj = [judge_groups(conds, p["d"], p["target"]) for p in prof]
        results[k] = {"conds": conds, "pj": pj, "qj": qj,
                      "p1": sum(j["top1"] for j in pj), "p2": sum(j["top2"] for j in pj), "q1": sum(j["top1"] for j in qj),
                      "q2": sum(j["top2"] for j in qj)}
    # 5-signature reference (Part B code path)
    ref_p = [ct.judge(ct.condition_scores(r["d"])["CR3pool"], r["tset"]) for r in paths]
    ref_q = []
    for p in prof:
        tset = ct.TARGET_SET(p["target"])
        ref_q.append(ct.judge(ct.condition_scores(p["d"])["CR3pool"], tset))
    ref = {"p1": sum(j["top1"] for j in ref_p), "p2": sum(j["top2"] for j in ref_p), "q1": sum(j["top1"] for j in ref_q),
           "chance1": sum(len(r["tset"]) / len(ct.SIGS) for r in paths)}
    ref_lead_q = Counter(j["lead"] for j in ref_q)
    w("### Accuracy against k (CR3pool applied to each k's groups)")
    w("")
    w("Held-out paths are the 12 respondent paths. Profile top-1 is in-sample (the clustering used those profiles) and carries no hypothesis.")
    w("")
    w("| Conditions | Paths top-1 | Paths top-2 | Chance top-1 | Chance top-2 | Profiles top-1 (in-sample) | Profiles top-2 (in-sample) | Largest condition share of profile leads | Sink (>87 of 175) |")
    w("|---|---:|---:|---:|---:|---:|---:|---:|:-:|")
    sinks = {}
    for k in KS:
        r = results[k]
        leads = Counter(j["lead"] for j in r["qj"])
        top = leads.most_common(1)[0]
        sinks[k] = [i for i, c in leads.items() if c > 87]
        w(f"| k = {k} | {r['p1']} of {npaths} | {r['p2']} of {npaths} | {npaths / k:.2f} | {npaths * min(2, k) / k:.2f} | {r['q1']} of {len(prof)} | {r['q2']} of {len(prof)} | {top[1]} of {len(prof)} ({100 * top[1] / len(prof):.1f}%) | {yn(bool(sinks[k]))} |")
    leadmax = ref_lead_q.most_common(1)[0]
    w(f"| 5 signatures (reference, CR3pool) | {ref['p1']} of {npaths} | {ref['p2']} of {npaths} | {ref['chance1']:.2f} | n/a | {ref['q1']} of {len(prof)} | n/a | {leadmax[1]} of {len(prof)} ({100 * leadmax[1] / len(prof):.1f}%) | {yn(leadmax[1] > 87)} |")
    w("")
    w("### Membership for each k")
    w("")
    for k in KS:
        w(f"**k = {k}**")
        w("")
        for i, m in enumerate(results[k]["conds"]):
            w(f"- C{i + 1} ({len(m)} states, leads {Counter(j['lead'] for j in results[k]['pj']).get(i, 0)} paths and {Counter(j['lead'] for j in results[k]['qj']).get(i, 0)} profiles{', SINK' if i in sinks[k] else ''}): {', '.join(m)}")
        w("")
    # hypotheses
    p1s = [results[k]["p1"] for k in KS]
    rho = spearman([float(k) for k in KS], [float(x) for x in p1s])
    k1 = results[10]["p1"] < results[3]["p1"] and rho < 0
    big = [k for k in KS if results[k]["p1"] >= 9]
    k2 = bool(big) and 4 <= max(big) <= 7
    k3 = results[5]["p1"] > ref["p1"]
    w("### Hypotheses, scored per the frozen arithmetic")
    w("")
    w(f"- **K1** (paths top-1 falls as k rises: lower at k = 10 than k = 3, and Spearman correlation below 0): **{'HOLDS' if k1 else 'FAILS'}**. Paths top-1 by k = 3 to 10: {p1s}. Spearman rho = {rho:.3f}.")
    w(f"- **K2** (the largest k with paths top-1 of 9 or more lies in 4 to 7): **{'HOLDS' if k2 else 'FAILS'}**. k values with 9 or more: {big or 'none'}.")
    w(f"- **K3** (at k = 5, paths top-1 strictly above the 5-signature CR3pool result): **{'HOLDS' if k3 else 'FAILS'}**. k = 5: {results[5]['p1']} of {npaths}, 5 signatures: {ref['p1']} of {npaths}.")
    w("")
    # descriptive table
    w("### Descriptive: the target's wired live questions on the paths missed at every level (P1, P2, P5)")
    w("")
    core, live = live_set()
    w(f"Live set: {len(core)} core questions plus follow-ups and distinguishers reachable from them, {len(live)} questions in all. For each question wired to the target and in the live set: the answer the persona gave, that answer's post-pipeline contribution on the target's primary liability field, and the largest contribution available on that field in the question (option id). 'not served' means the question was not asked on this path.")
    w("")
    w("| Path | Target (primary liability field) | Question | Answer given | Contribution of the answer | Best available on this field | Best option |")
    w("|---|---|---|---|---:|---:|---|")
    allp = {p["id"]: p for p in rt1.load_paths() if p["id"] != "EXP01"}
    for pid in ("P1-cautious", "P1-strong", "P2-cautious", "P2-strong", "P5-cautious", "P5-strong"):
        p = allp[pid]
        t = p["target"]
        fld = rt1._DIM[STATE_PROFILES[t].primary_dimension]
        idata = _locked_intake_to_engine_intake(p["intake"])
        ans = dict(p["answers"])
        wq = [q for q in sorted(live, key=lambda x: (x not in core, core.index(x) if x in core else 0, x))
              if t in (QUESTION_LIBRARY[q].state_targets or [])]
        for qid in wq:
            q = QUESTION_LIBRARY[qid]
            best_v, best_o = max(((rt1.option_contrib(idata, qid, o.option_id)[fld], o.option_id) for o in q.answer_options), key=lambda x: x[0])
            if qid in ans:
                parts = []
                tot = 0.0
                for oid in ans[qid]:
                    txt = next(o.option_text for o in q.answer_options if o.option_id == oid)
                    parts.append(f"{oid}: {txt[:70]}")
                    tot += rt1.option_contrib(idata, qid, oid)[fld]
                w(f"| {pid} | {t} ({fld}) | {qid} | {'; '.join(parts)} | {tot:+.2f} | {best_v:+.2f} | {best_o} |")
            else:
                w(f"| {pid} | {t} ({fld}) | {qid} | not served | n/a | {best_v:+.2f} | {best_o} |")
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
    new = ct.append_section(section, "\n## Part C RESULTS")
    if a.write:
        PREREG.write_bytes(new.encode("utf-8"))
        print("WROTE")
    else:
        print("DRY RUN")
