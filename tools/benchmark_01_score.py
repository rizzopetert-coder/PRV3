"""Benchmark 01 scorer. Computes every measure in prompts/benchmark-01-preregistration.md from the 12 saved run files
and prints (or appends) a RESULTS section. No figure is hand-typed: everything is read from the saved run JSON, or
recomputed by replaying the logged answers through the production engine functions.

Usage:
  python tools/benchmark_01_score.py                       # print the RESULTS section
  python tools/benchmark_01_score.py --append --dry-run    # check the append is append-only, print sizes
  python tools/benchmark_01_score.py --append --write      # append to prompts/benchmark-01-preregistration.md

Inputs: C:\\Users\\rizzo\\Downloads\\benchmark-01\\<persona>-<framing>.json (log + result), tools/benchmark_01_labels.json
(executive summary labels, written by Claude Code from the verbatim summaries, to be checked by Claude.ai).
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.main import accumulate_answers  # noqa: E402
from engine.accumulation import rank_states  # noqa: E402
from engine.data.salience import SALIENCE_PROFILES  # noqa: E402
from engine.data.states import DIMENSIONAL_FIELDS  # noqa: E402
from engine.output import SCD_WCS_MARGIN_GATE  # noqa: E402

RUNS_DIR = Path(r"C:\Users\rizzo\Downloads\benchmark-01")
LABELS = ROOT / "tools" / "benchmark_01_labels.json"
PREREG = ROOT / "prompts" / "benchmark-01-preregistration.md"
TIER_ORDER = {"Emerging": 0, "Entrenched": 1, "Endemic": 2}

PERSONAS = {
    "P1": ("Granite Ridge Components", "the_unformed_leader", ["the_unreported_hazard"], None),
    "P2": ("Halvorsen & Pike LLP", "the_untouchable", [], "the_arbitrary_standard"),
    "P3": ("Brightwater Family Health", "the_overloaded_manager", [], "compression_crisis"),
    "P4": ("Lakeshore Learning Alliance", "decision_paralysis", [], "planning_authority_gap"),
    "P5": ("Northloop Analytics", "pay_exposure", [], None),
    "P6": ("Coastline Hospitality Group", "the_culture_that_wasnt", [], "dueling_narratives"),
}
FRAMINGS = ("cautious", "strong")


def load(pid, framing):
    p = RUNS_DIR / f"{pid}-{framing}.json"
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def replay_rank(run):
    """Replay the logged answers through the production engine. Returns (all 58 rankings, answer count)."""
    vec = {f: 0.0 for f in DIMENSIONAL_FIELDS}
    n = 0
    for e in run["exchanges"]:
        if e["path"].endswith("/session/answer") and e.get("http_status") == 200:
            vec = accumulate_answers(vec, e["request"]["question_id"], e["request"]["option_ids"], run["intake_wire"])["accumulated_vector"]
            n += 1
    return rank_states(vec, n, SALIENCE_PROFILES), n


def measures(pid, framing, run):
    name, target, also, lenient = PERSONAS[pid]
    m = {"pid": pid, "framing": framing, "target": target, "status": None}
    if run is None or run["outcome"] is None or run["outcome"]["status"] != "COMPLETE":
        m["status"] = "NO RESULT" if run is None else (run["outcome"] or {}).get("status", "NO OUTCOME")
        m["halt"] = (run or {}).get("outcome", {}) and run["outcome"].get("reason")
        return m
    m["status"] = "COMPLETE"
    res = run["result"]
    q = res["all_qualified_states"]
    rk, n = replay_rank(run)
    # the replay must reproduce the live qualified list
    live_ids = [s["state_id"] for s in q]
    m["replay_ok"] = [r.state_id for r in rk[: len(q)]] == live_ids and max(abs(r.score - s["score"]) for r, s in zip(rk, q)) < 5e-7
    rank = {r.state_id: r.rank for r in rk}
    score = {r.state_id: r.score for r in rk}
    m["answers"] = n
    m["lead"] = q[0]["state_id"]
    m["target_rank"] = rank[target]
    m["target_score"] = score[target]
    m["target_qualified"] = target in live_ids
    m["top3"] = rank[target] <= 3
    m["top5"] = rank[target] <= 5
    m["also_ranks"] = {a: rank[a] for a in also}
    m["lenient_top3"] = m["top3"] or (lenient is not None and rank[lenient] <= 3)
    m["lenient_rank"] = rank[lenient] if lenient else None
    m["qualifying"] = len(q)
    top, last = q[0]["score"], q[-1]["score"]
    m["spread_pct"] = 100.0 * (top - last) / top
    m["distinct"] = len({round(s["score"], 6) for s in q})
    m["margin"] = q[0]["score"] - q[1]["score"] if len(q) > 1 else None
    m["r1_tie"] = len(q) > 1 and round(q[0]["score"], 6) == round(q[1]["score"], 6)
    sev = {e["state_id"]: e for e in res["severity_by_state"]}
    m["lead_tier"] = sev.get(q[0]["state_id"], {}).get("tier", "Emerging")
    tiers = [sev.get(s["state_id"], {}).get("tier", "Emerging") for s in q[:5]]
    m["top5_max_tier"] = max(tiers, key=lambda t: TIER_ORDER[t])
    m["top5_tiers"] = tiers
    lg = res["legal_tail_risk_exposure"]
    m["legal_low"], m["legal_high"], m["legal_band"] = lg["low"], lg["high"], lg["band"]
    m["summary"] = (res.get("synthesis") or {}).get("executive_summary", "")
    m["family"] = res.get("resolution_family")
    m["narrative_skipped"] = run["outcome"].get("narrative_skipped")
    return m


def pf(x, d=6):
    return "n/a" if x is None else f"{x:.{d}f}"


def build():
    M = {(pid, f): measures(pid, f, load(pid, f)) for pid in PERSONAS for f in FRAMINGS}
    labels = json.load(open(LABELS, encoding="utf-8")) if LABELS.exists() else {}
    L = []
    w = L.append
    w("")
    w("## RESULTS")
    w("")
    w("Produced by `tools/benchmark_01_score.py` from the 12 saved runs in `C:\\Users\\rizzo\\Downloads\\benchmark-01\\<persona>-<framing>.json` (each holds the full request and response log and the completion payload). Target ranks and scores are replayed from the logged answers through the production engine functions (`accumulate_answers`, `rank_states`) and are checked against the live `all_qualified_states` (the `Replay` column). The pre-registration text above this section is unchanged. No figure below is hand-typed.")
    w("")
    ok = [k for k, m in M.items() if m["status"] == "COMPLETE"]
    bad = [(k, m) for k, m in M.items() if m["status"] != "COMPLETE"]
    w(f"Runs complete: {len(ok)} of 12. Runs not complete: {len(bad)}.")
    for k, m in bad:
        w(f"- **{k[0]}-{k[1]}: {m['status']}**: {m.get('halt')}")
    w("")
    w("### Per-run measures")
    w("")
    w("| Run | Target | Target rank (of 58) | Target score | Top-3 | Top-5 | Lenient top-3 | Lead state | Qualifying | Spread % | Distinct scores | Margin r1-r2 | R1 tie | Lead tier | Top-5 highest tier | Legal total (low-high) | Replay |")
    w("|---|---|---:|---:|:-:|:-:|:-:|---|---:|---:|---:|---:|:-:|---|---|---|:-:|")
    for pid in PERSONAS:
        for f in FRAMINGS:
            m = M[(pid, f)]
            if m["status"] != "COMPLETE":
                w(f"| {pid}-{f} | {m['target']} | {m['status']} | | | | | | | | | | | | | | |")
                continue
            tq = "" if m["target_qualified"] else " (not qualified)"
            w(f"| {pid}-{f} | {m['target']} | {m['target_rank']}{tq} | {pf(m['target_score'])} | {'Y' if m['top3'] else 'N'} | {'Y' if m['top5'] else 'N'} | {'Y' if m['lenient_top3'] else 'N'} | {m['lead']} | {m['qualifying']} | {m['spread_pct']:.2f} | {m['distinct']} | {pf(m['margin'])} | {'Y' if m['r1_tie'] else 'N'} | {m['lead_tier']} | {m['top5_max_tier']} | ${m['legal_low']:,.0f}-${m['legal_high']:,.0f} ({m['legal_band']}) | {'ok' if m['replay_ok'] else 'MISMATCH'} |")
    w("")
    w("Also-report (P1): the_unreported_hazard rank per run: " + "; ".join(f"{f}: {M[('P1', f)].get('also_ranks', {}).get('the_unreported_hazard', 'n/a')}" for f in FRAMINGS) + ". Lenient-state ranks: " + "; ".join(f"{pid}-{f}: {PERSONAS[pid][3]} {M[(pid, f)].get('lenient_rank')}" for pid in PERSONAS if PERSONAS[pid][3] for f in FRAMINGS if M[(pid, f)]["status"] == "COMPLETE") + ".")
    w("")
    w("### Per persona: cautious versus strong")
    w("")
    w("| Persona | Target | Cautious rank | Strong rank | Rank delta (strong minus cautious) | Cautious score | Strong score | Score delta | Top-3 cautious | Top-3 strong | Top-3 flips | Lead cautious | Lead strong | Qualifying c / s |")
    w("|---|---|---:|---:|---:|---:|---:|---:|:-:|:-:|:-:|---|---|---|")
    rank_diff = flips = both = 0
    for pid in PERSONAS:
        c, s = M[(pid, "cautious")], M[(pid, "strong")]
        if c["status"] != "COMPLETE" or s["status"] != "COMPLETE":
            w(f"| {pid} | {PERSONAS[pid][1]} | incomplete | | | | | | | | | | | |")
            continue
        both += 1
        rd = s["target_rank"] - c["target_rank"]
        rank_diff += rd != 0
        fl = c["top3"] != s["top3"]
        flips += fl
        w(f"| {pid} | {c['target']} | {c['target_rank']} | {s['target_rank']} | {rd:+d} | {pf(c['target_score'])} | {pf(s['target_score'])} | {s['target_score']-c['target_score']:+.6f} | {'Y' if c['top3'] else 'N'} | {'Y' if s['top3'] else 'N'} | {'FLIP' if fl else '-'} | {c['lead']} | {s['lead']} | {c['qualifying']} / {s['qualifying']} |")
    w("")
    w("### Aggregates")
    w("")
    done = [M[k] for k in ok]
    ranks = [m["target_rank"] for m in done]
    w(f"- Target rank over {len(done)} runs: min {min(ranks)}, median {statistics.median(ranks)}, mean {statistics.mean(ranks):.2f}, max {max(ranks)}.")
    w(f"- Top-3 hits: {sum(m['top3'] for m in done)} of {len(done)}. Top-5 hits: {sum(m['top5'] for m in done)}. Lenient top-3 hits: {sum(m['lenient_top3'] for m in done)}. Target qualified at all: {sum(m['target_qualified'] for m in done)}.")
    qs = [m["qualifying"] for m in done]
    w(f"- Qualifying count: min {min(qs)}, median {statistics.median(qs)}, mean {statistics.mean(qs):.1f}, max {max(qs)}. Runs with 25 or more: {sum(x >= 25 for x in qs)} of {len(done)}.")
    sp = [m["spread_pct"] for m in done]
    w(f"- Spread rank 1 to last qualifying, % of top score: min {min(sp):.2f}, median {statistics.median(sp):.2f}, max {max(sp):.2f}.")
    mg = [m["margin"] for m in done if m["margin"] is not None]
    w(f"- Margin rank 1 to rank 2: min {min(mg):.6f}, median {statistics.median(mg):.6f}, max {max(mg):.6f}. Rank-1 ties: {sum(m['r1_tie'] for m in done)} of {len(done)}.")
    w(f"- Lead tiers: " + ", ".join(f"{t} {sum(m['lead_tier'] == t for m in done)}" for t in TIER_ORDER) + ". Top-5 highest tier: " + ", ".join(f"{t} {sum(m['top5_max_tier'] == t for m in done)}" for t in TIER_ORDER) + ".")
    leads = {}
    for m in done:
        leads[m["lead"]] = leads.get(m["lead"], 0) + 1
    w(f"- Lead state frequency across runs: " + ", ".join(f"{k} {v}" for k, v in sorted(leads.items(), key=lambda kv: -kv[1])) + ".")
    ll = [m["legal_low"] for m in done]
    w(f"- Legal total (low end): min ${min(ll):,.0f}, median ${statistics.median(ll):,.0f}, max ${max(ll):,.0f}.")
    w(f"- Replay matched the live qualified list in {sum(m['replay_ok'] for m in done)} of {len(done)} runs. Narrative skipped in {sum(bool(m['narrative_skipped']) for m in done)} of {len(done)} runs.")
    w("")
    w("### Executive summaries, verbatim, with Claude Code's labels (Claude.ai to check)")
    w("")
    w("Label rule: NAMES if the summary states the persona's registered dominant problem in substance. The label and its reasoning are Claude Code's judgment, not computed, and are stored in `tools/benchmark_01_labels.json`.")
    w("")
    names_c = 0
    for pid, (nm, target, _, _) in PERSONAS.items():
        for f in FRAMINGS:
            m = M[(pid, f)]
            if m["status"] != "COMPLETE":
                continue
            lab = labels.get(f"{pid}-{f}", {"label": "UNLABELLED", "why": ""})
            if f == "cautious" and lab["label"] == "NAMES":
                names_c += 1
            w(f"**{pid}-{f}** ({nm}, target {target}, lead {m['lead']}, pathway {m['family']})")
            w("")
            w(f"> {m['summary'] if m['summary'] else '(empty summary)'}")
            w("")
            w(f"Label: **{lab['label']}**. {lab['why']}")
            w("")
    # ---- hypotheses ----
    w("### B1 to B6 scored against the registered wording")
    w("")
    hits3 = sum(m["top3"] for m in done)
    n = len(done)
    complete = n == 12
    b1i = "HOLDS" if hits3 >= 10 else "FAILS"
    b1e = "HOLDS" if hits3 <= 3 else "FAILS"
    note = "" if complete else f" (only {n} of 12 runs completed, so these are provisional)"
    w(f"- **B1-ideal** (top-3 hits in 10 or more of 12): **{b1i}**. Top-3 hits = {hits3} of {n}.{note}")
    w(f"- **B1-engine** (top-3 hits in 3 or fewer of 12): **{b1e}**. Top-3 hits = {hits3} of {n}.{note}")
    p2a = rank_diff >= 4
    p2b = flips >= 1
    b2 = "HOLDS" if (p2a and p2b) else ("PARTIAL" if (p2a or p2b) else "FAILS")
    w(f"- **B2 Framing**: **{b2}**. Target rank differs between framings in {rank_diff} of {both} personas (registered threshold 4 or more: {'met' if p2a else 'not met'}). Personas whose top-3 status flips: {flips} (registered at least one: {'met' if p2b else 'not met'}).")
    b3n = sum(x >= 25 for x in qs)
    b3 = "HOLDS" if b3n >= 10 else "FAILS"
    w(f"- **B3 Breadth**: **{b3}**. Runs with 25 or more qualifying conditions: {b3n} of {n} (registered 10 or more of 12). Counts: {sorted(qs)}.")
    cau = [M[(p, 'cautious')] for p in PERSONAS if M[(p, 'cautious')]["status"] == "COMPLETE"]
    stg = [M[(p, 'strong')] for p in PERSONAS if M[(p, 'strong')]["status"] == "COMPLETE"]
    b4a = len(cau) == 6 and all(m["lead_tier"] == "Emerging" for m in cau)
    b4n = sum(TIER_ORDER[m["top5_max_tier"]] >= 1 for m in stg)
    b4b = b4n >= 3
    b4 = "HOLDS" if (b4a and b4b) else ("PARTIAL" if (b4a or b4b) else "FAILS")
    w(f"- **B4 Severity**: **{b4}**. Cautious runs with an Emerging lead: {sum(m['lead_tier'] == 'Emerging' for m in cau)} of {len(cau)} (registered all 6: {'met' if b4a else 'not met'}). Strong runs with an Entrenched-or-higher condition in the top 5: {b4n} of {len(stg)} (registered 3 or more: {'met' if b4b else 'not met'}).")
    b5 = "HOLDS" if names_c >= 4 else "FAILS"
    unl = [k for k, v in labels.items() if v["label"] == "UNLABELLED"]
    w(f"- **B5 Synthesis**: **{b5}**. Cautious summaries labelled NAMES: {names_c} of {len(cau)} (registered 4 or more). Labels are Claude Code's judgment, flagged for Claude.ai to check. Cautious labels marked borderline: " + (", ".join(k for k in labels if k.endswith("cautious") and labels[k].get("borderline")) or "none") + ".")
    p1c = M[("P1", "cautious")]
    if p1c["status"] == "COMPLETE":
        b6 = "HOLDS" if p1c["target_rank"] > 10 else "FAILS"
        w(f"- **B6 Narrative effect (P1)**: **{b6}**. P1-cautious the_unformed_leader rank {p1c['target_rank']} of 58 (registered: still outside the top 10).")
    else:
        w("- **B6**: not scoreable (P1-cautious did not complete).")
    w("")
    w("Registered confounds stand as written above.")
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
