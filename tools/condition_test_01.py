"""Condition test 01 (5 signatures), implemented to the definitions frozen in prompts/condition-test-01-preregistration.md
(commit 0bf8efb). Every figure is generated here from saved run files, the taxonomy file, or live engine calls.

Usage:
  python tools/condition_test_01.py --membership                         # print the membership-check section
  python tools/condition_test_01.py --membership --append --write        # append it (own commit, before any scoring)
  python tools/condition_test_01.py                                      # print the RESULTS section
  python tools/condition_test_01.py --append --dry-run | --write         # append RESULTS
Part C (data-derived grouping) is registered but is not implemented or computed here.
"""
import argparse
import json
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import tools.ranker_test_01 as rt1  # noqa: E402
import tools.calibration_runner as cr  # noqa: E402
from engine.accumulation import IntakeData, AccumulationEngine, MC_CENTROID_39, CENTROID_FIELD_SCALARS  # noqa: E402
from engine.data.questions import QUESTION_LIBRARY  # noqa: E402
from engine.data.salience import SALIENCE_PROFILES  # noqa: E402
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS  # noqa: E402
from engine.main import _locked_intake_to_engine_intake  # noqa: E402

PREREG = ROOT / "prompts" / "condition-test-01-preregistration.md"
TAXONOMY = ROOT / "web" / "data" / "taxonomy.ts"
F = list(DIMENSIONAL_FIELDS)
SCORERS = ("CR0max", "CR0mean", "CR2pool", "CR3pool")
CLAIMED_SIZES = {"leadership_bottleneck": 9, "culture_erosion": 13, "stunted_growth": 8, "compounding_risks": 20, "information_blindness": 9}
yn = lambda b: "Y" if b else "N"


def load_taxonomy():
    js = ("import {states, signatures} from './web/data/taxonomy.ts';"
          "console.log(JSON.stringify({states, signatures}));")
    out = subprocess.run(["node", "--input-type=module", "-e", js], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise SystemExit("node failed to evaluate taxonomy.ts: " + out.stderr[:500])
    return json.loads(out.stdout)


TAX = load_taxonomy()
SIGS = [s["id"] for s in TAX["signatures"]]
TSTATE = {s["id"]: s for s in TAX["states"]}


def state_side_sets():
    """signature id -> set of state ids, from State.signatureId + secondarySignatureIds."""
    d = {sid: set() for sid in SIGS}
    for s in TAX["states"]:
        for sig in [s["signatureId"]] + list(s.get("secondarySignatureIds") or []):
            d.setdefault(sig, set()).add(s["id"])
    return d


def membership_section():
    L = []
    w = L.append
    ids = [s["id"] for s in TAX["states"]]
    reg = set(STATE_PROFILES)
    side_state = state_side_sets()
    side_sig = {s["id"]: set(s["stateIds"]) for s in TAX["signatures"]}
    w("")
    w("## Membership check (run after the pre-registration commit, before any scoring)")
    w("")
    w("Produced by `tools/condition_test_01.py --membership`. `taxonomy.ts` is evaluated with Node, the engine registry is `engine.data.states.STATE_PROFILES`. Nothing was fixed.")
    w("")
    w(f"- `taxonomy.ts` `states[]` entries: {len(ids)} ({len(set(ids))} distinct ids). Engine registry states: {len(reg)}.")
    w(f"- In the registry but absent from `taxonomy.ts` states: {sorted(reg - set(ids)) or 'none'}.")
    w(f"- In `taxonomy.ts` states but absent from the registry: {sorted(set(ids) - reg) or 'none'}.")
    dup = [k for k, v in Counter(ids).items() if v > 1]
    w(f"- Duplicate ids in `states[]`: {dup or 'none'}.")
    bad_primary = [s["id"] for s in TAX["states"] if s["signatureId"] not in SIGS]
    bad_sec = [(s["id"], x) for s in TAX["states"] for x in (s.get("secondarySignatureIds") or []) if x not in SIGS]
    w(f"- States whose `signatureId` is not a signature id: {bad_primary or 'none'}. Secondary ids that are not a signature id: {bad_sec or 'none'}.")
    sig_ids_all = set().union(*side_sig.values())
    w(f"- State ids listed in `Signature.stateIds` that are absent from `states[]`: {sorted(sig_ids_all - set(ids)) or 'none'}. `states[]` ids that appear in no `Signature.stateIds`: {sorted(set(ids) - sig_ids_all) or 'none'}.")
    w("")
    w("Two-representation comparison, per signature (State side = `signatureId` plus `secondarySignatureIds`, Signature side = `stateIds`):")
    w("")
    w("| Signature | Spec-claimed size | State-side size | Signature-side size | In State side only | In Signature side only |")
    w("|---|---:|---:|---:|---|---|")
    any_diff = False
    for sig in SIGS:
        a, b = side_state.get(sig, set()), side_sig.get(sig, set())
        a_only, b_only = sorted(a - b), sorted(b - a)
        any_diff |= bool(a_only or b_only)
        w(f"| {sig} | {CLAIMED_SIZES.get(sig, 'n/a')} | {len(a)} | {len(b)} | {', '.join(a_only) or '-'} | {', '.join(b_only) or '-'} |")
    w("")
    multi = [(s["id"], [s["signatureId"]] + list(s.get("secondarySignatureIds") or [])) for s in TAX["states"] if s.get("secondarySignatureIds")]
    w(f"- States with secondary signatures: {len(multi)}: " + "; ".join(f"{i} in {', '.join(sg)}" for i, sg in multi) + ".")
    tot_state = sum(len(v) for v in side_state.values())
    tot_sig = sum(len(v) for v in side_sig.values())
    w(f"- Total memberships: State side {tot_state}, Signature side {tot_sig}. Signature-size sum claimed in the specification: {sum(CLAIMED_SIZES.values())}.")
    w(f"- Result: the two representations {'DIFFER' if any_diff or (reg ^ set(ids)) else 'MATCH'} " + ("(see the rows above). Scoring uses the State side, as frozen." if (any_diff or (reg ^ set(ids))) else "and cover all registry states."))
    w("")
    return "\n".join(L)


def cond_members():
    s = state_side_sets()
    return {c: sorted(x for x in s.get(c, set()) if x in STATE_PROFILES) for c in SIGS}


MEMBERS = cond_members()
TARGET_SET = lambda t: [c for c in SIGS if t in MEMBERS[c]]


# ---------------- scoring ----------------
def per_run_data(idata, answers, r0_scores):
    wired = rt1.wired_answers(idata, answers)
    _, n = rt1.r2_scores(wired)
    s2, _ = rt1.r2_scores(wired)
    return {"r0": r0_scores, "wired": wired, "n": n, "r2": s2}


def condition_scores(d):
    out = {k: {} for k in SCORERS}
    for c, mem in MEMBERS.items():
        out["CR0max"][c] = max(d["r0"][s] for s in mem) if mem else 0.0
        out["CR0mean"][c] = sum(d["r0"][s] for s in mem) / len(mem) if mem else 0.0
        # CR2pool
        tot, pairs = 0.0, 0
        qcontrib = {}
        for s in mem:
            fld = rt1._DIM[STATE_PROFILES[s].primary_dimension]
            for qid, contribs in d["wired"][s]:
                tot += sum(cc[fld] for cc in contribs)
                pairs += 1
                qcontrib[qid] = contribs
        out["CR2pool"][c] = tot / pairs if pairs else 0.0
        # CR3pool
        if not qcontrib:
            out["CR3pool"][c] = 0.0
            continue
        v = np.zeros(len(F))
        for contribs in qcontrib.values():
            for cc in contribs:
                v += np.array([cc[f] for f in F])
        N = len(qcontrib)
        mu = np.array([MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS.get(f, 1.0) * (N / 42.0) for f in F])
        A = v - mu
        if np.linalg.norm(A) < 1e-5:
            out["CR3pool"][c] = 0.0
            continue
        B = np.mean([[STATE_PROFILES[s].dimensional_vector.as_dict().get(f, 0.0) for f in F] for s in mem], axis=0)
        W = np.mean([[SALIENCE_PROFILES.get(s, {}).get(f, 1.0) for f in F] for s in mem], axis=0)
        num = float(np.sum(W * A * B))
        den = float(np.sqrt(np.sum(W * A ** 2)) * np.sqrt(np.sum(W * B ** 2)))
        out["CR3pool"][c] = num / den if den > 1e-5 else 0.0
    return out


def order_conds(scores):
    return sorted(((c, scores[c]) for c in SIGS), key=lambda kv: -kv[1])


def judge(scores, tset):
    o = order_conds(scores)
    return {"o": o, "top1": o[0][0] in tset, "top2": any(c in tset for c, _ in o[:2]), "margin": o[0][1] - o[1][1],
            "tie": round(o[0][1], 6) == round(o[1][1], 6), "lead": o[0][0]}


def evaluate_paths():
    paths = [p for p in rt1.load_paths() if p["id"] != "EXP01"]
    rows, excl = [], []
    for p in paths:
        s0, _ = rt1.r0_scores(p["intake"], p["answers"])
        o = rt1.ordered(s0)
        live = p["live"]
        ok = [s for s, _ in o[: len(live)]] == [x["state_id"] for x in live] and max(abs(v - x["score"]) for (_, v), x in zip(o, live)) < 5e-7
        tset = TARGET_SET(p["target"])
        if not ok or not tset:
            excl.append((p["id"], "replay mismatch" if not ok else "target in no condition"))
            continue
        idata = _locked_intake_to_engine_intake(p["intake"])
        d = per_run_data(idata, p["answers"], s0)
        cs = condition_scores(d)
        rows.append({"id": p["id"], "target": p["target"], "tset": tset, "d": d, "cs": cs, "j": {k: judge(cs[k], tset) for k in SCORERS}})
    return rows, excl


def evaluate_profiles():
    rows, excl = [], []
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
        tset = TARGET_SET(tc.target_state)
        if not tset:
            excl.append((tc.test_id, "target in no condition"))
            continue
        d = per_run_data(idata, answers, s0)
        cs = condition_scores(d)
        rows.append({"id": tc.test_id, "pt": tc.profile_type, "target": tc.target_state, "tset": tset, "cs": cs, "j": {k: judge(cs[k], tset) for k in SCORERS}})
    return rows, excl


def build():
    L = []
    w = L.append
    prow, pexcl = evaluate_paths()
    qrow, qexcl = evaluate_profiles()
    w("")
    w("## RESULTS")
    w("")
    w("Produced by `tools/condition_test_01.py` (committed with this section) to the definitions frozen at `0bf8efb`. The text above this section is unchanged. Every figure is generated by the script. Part C (data-derived grouping) is not computed.")
    w("")
    w("Conditions (State-side membership restricted to engine registry states): " + "; ".join(f"{c} {len(MEMBERS[c])}" for c in SIGS) + ".")
    w(f"Valid paths: {len(prow)} of 12. Exclusions: {pexcl or 'none'}. Valid profiles: {len(qrow)} of {len(list(cr.ALL_PROFILES))}. Exclusions: {qexcl or 'none'}.")
    w("")
    npaths, nprof = len(prow), len(qrow)
    chance_p = sum(len(r["tset"]) / len(SIGS) for r in prow)
    chance_q = sum(len(r["tset"]) / len(SIGS) for r in qrow)
    pts = [pt for pt in cr.PROFILE_TYPES if any(r["pt"] == pt for r in qrow)]
    w("### Summary per scorer")
    w("")
    w("| Scorer | Paths top-1 | Paths top-2 | Profiles top-1 | Profiles top-2 | " + " | ".join(f"{pt} top-1/top-2" for pt in pts) + " |")
    w("|---|---:|---:|---:|---:|" + "---:|" * len(pts))
    summ = {}
    for k in SCORERS:
        p1, p2 = sum(r["j"][k]["top1"] for r in prow), sum(r["j"][k]["top2"] for r in prow)
        q1, q2 = sum(r["j"][k]["top1"] for r in qrow), sum(r["j"][k]["top2"] for r in qrow)
        summ[k] = (p1, p2, q1, q2)
        per = " | ".join(f"{sum(r['j'][k]['top1'] for r in qrow if r['pt'] == pt)}/{sum(r['j'][k]['top2'] for r in qrow if r['pt'] == pt)} of {sum(1 for r in qrow if r['pt'] == pt)}" for pt in pts)
        w(f"| {k} | {p1} of {npaths} | {p2} of {npaths} | {q1} of {nprof} | {q2} of {nprof} | {per} |")
    w(f"| chance (top-1, uniform over {len(SIGS)}) | {chance_p:.2f} | n/a | {chance_q:.1f} | n/a | |")
    w("")
    # per path tables
    for k in SCORERS:
        w(f"### {k}: per path (top 2 conditions with scores)")
        w("")
        w("| Path | Target | Target's conditions | Rank-1 condition (score) | Rank-2 condition (score) | Margin 1-2 | Tie | Top-1 | Top-2 |")
        w("|---|---|---|---|---|---:|:-:|:-:|:-:|")
        for r in prow:
            j = r["j"][k]
            w(f"| {r['id']} | {r['target']} | {', '.join(r['tset'])} | {j['o'][0][0]} ({j['o'][0][1]:.4f}) | {j['o'][1][0]} ({j['o'][1][1]:.4f}) | {j['margin']:.4f} | {yn(j['tie'])} | {yn(j['top1'])} | {yn(j['top2'])} |")
        w("")
    # lead frequency
    w("### How often each condition leads")
    w("")
    w("| Scorer | Set | " + " | ".join(SIGS) + " | Max share |")
    w("|---|---|" + "---:|" * len(SIGS) + "---:|")
    leadq = {}
    for k in SCORERS:
        for label, rows in (("paths", prow), ("profiles", qrow)):
            cnt = Counter(r["j"][k]["lead"] for r in rows)
            if label == "profiles":
                leadq[k] = cnt
            w(f"| {k} | {label} | " + " | ".join(str(cnt.get(c, 0)) for c in SIGS) + f" | {max(cnt.values())/len(rows):.2f} |")
    w("")
    # best scorer
    order = list(SCORERS)
    best = sorted(order, key=lambda k: (-summ[k][0], -summ[k][2], order.index(k)))[0]
    w("### Best scorer and hypotheses")
    w("")
    w(f"Best scorer (most path top-1, ties by profile top-1): **{best}** (paths top-1 {summ[best][0]}, profiles top-1 {summ[best][2]}).")
    w("")
    s1 = summ[best][0] >= 8 and summ[best][0] > summ["CR0max"][0]
    w(f"- **S1** (best scorer path top-1 at least 8 and strictly above CR0max): **{'HOLDS' if s1 else 'FAILS'}**. Best {summ[best][0]} of {npaths}, CR0max {summ['CR0max'][0]}.")
    w(f"- **S2** (best scorer path top-2 at least 10): **{'HOLDS' if summ[best][1] >= 10 else 'FAILS'}**. Best {summ[best][1]} of {npaths}.")
    w(f"- **S3** (best scorer profile top-1 at least 120 of 175): **{'HOLDS' if summ[best][2] >= 120 else 'FAILS'}**. Best {summ[best][2]} of {nprof}.")
    top = leadq[best].most_common(1)[0]
    w(f"- **S4** (no condition leads more than 87 of the 175 profiles under the best scorer): **{'HOLDS' if top[1] <= 87 else 'FAILS'}**. Largest lead: {top[0]} with {top[1]} of {nprof} ({100*top[1]/nprof:.1f} percent).")
    w("")
    # candidate symptoms
    w(f"### Candidate symptoms: member states of the rank-1 condition with wired evidence (best scorer {best})")
    w("")
    w("n = wired questions answered on that path. R2 = the Ranker Test 01 question-local score. Sorted by R2 score.")
    w("")
    w("| Path | Rank-1 condition | In target's set | Member states with wired evidence (n, R2) |")
    w("|---|---|:-:|---|")
    for r in prow:
        lead = r["j"][best]["lead"]
        mem = [(s, r["d"]["n"][s], r["d"]["r2"][s]) for s in MEMBERS[lead] if r["d"]["n"][s] >= 1]
        mem.sort(key=lambda t: -t[2])
        w(f"| {r['id']} | {lead} | {yn(lead in r['tset'])} | " + ("; ".join(f"{s} ({n}, {sc:.3f})" for s, n, sc in mem) or "none") + " |")
    w("")
    return "\n".join(L)


def append_section(section, marker):
    raw = PREREG.read_bytes()
    crlf = b"\r\n" in raw
    old = raw.decode("utf-8")
    base = old.rstrip("\r\n")
    assert marker not in base, f"{marker} already present"
    new_text = base.replace("\r\n", "\n") + "\n" + section
    new = new_text.replace("\n", "\r\n") if crlf else new_text
    assert new.startswith(base), "existing text must be unchanged"
    print(f"append-only ok: {len(old)} -> {len(new)} chars, newline {'CRLF' if crlf else 'LF'}")
    return new


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--membership", action="store_true")
    ap.add_argument("--append", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    section = membership_section() if a.membership else build()
    marker = "\n## Membership check" if a.membership else "\n## RESULTS"
    if not a.append:
        sys.stdout.reconfigure(encoding="utf-8")
        print(section)
        sys.exit(0)
    new = append_section(section, marker)
    if a.write:
        PREREG.write_bytes(new.encode("utf-8"))
        print("WROTE")
    else:
        print("DRY RUN")
