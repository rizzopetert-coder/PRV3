"""
Pass 2 observation texts (Pete-approved 2026-09-28). Adds 33 asset-valence
texts for the clean surfaceable strength answers (plus Q23-A) and 3
liability-valence texts for the DIST-CM options, and fixes the spaced "--"
in existing texts. The 5 conflict options (Q02-E, Q06-C, Q13-A, Q22-E,
Q32-B) keep their liability text unchanged.

E2: Q21-A uses Pete's revised text. Addition 3: engine/contract.py caps
_build_asset_evidence at 5 quoted lines (highest contribution to a leading
axis first, ties in question order).

Both tag tables in engine/data/questions.py are regenerated in library
order from their current contents plus these additions, so existing entries
are byte-identical and only additions/fixes show in the diff.

Usage (from repo root):
    python tools/patch_pass2_observation_texts.py --dry-run
    python tools/patch_pass2_observation_texts.py --write
    --root <dir>  apply against another checkout (verification worktree)
"""
import argparse
import ast
import difflib
import json
import pathlib
import re
import sys
from collections import Counter

QP = "engine/data/questions.py"

ASSET = {
    ("Q01", "A"): "Decisions here get made by the right people, and they stay made.",
    ("Q02", "A"): "This organization has dedicated HR leadership that operates with real authority.",
    ("Q04", "A"): "People here raise concerns, and there's a process they actually use.",
    ("Q05", "A"): "Underperformance here gets addressed through a process managers actually use.",
    ("Q06", "E"): "None of the legal or HR situations asked about have come up here in three years.",
    ("Q08", "A"): "Important information reaches leadership here reliably, so the picture at the top is accurate.",
    ("Q09", "A"): "The senior team here disagrees productively and still moves forward together.",
    ("Q10", "A"): "This organization's formal processes are current, and people actually use them.",
    ("Q11", "A"): "What this organization says it values shows up in how it actually operates.",
    ("Q12", "A"): "Most managers here develop their people and produce results.",
    ("Q13", "E"): "People here know the direction and trust leadership to execute on it.",
    ("Q14", "A"): "Leadership here is confident pay is competitive and internally consistent.",
    ("Q15", "A"): "People here know what it takes to advance, and advancement is merit-based.",
    ("Q16", "A"): "Diverse talent here advances at the same rate as everyone else.",
    ("Q17", "A"): "When this organization changes something, the change sticks and people invest in it.",
    ("Q18", "A"): "Safety and security are taken seriously here. People report concerns and the organization responds.",
    ("Q19", "A"): "What this organization says publicly matches what it lives internally.",
    ("Q20", "A"): "People here know their mandates, and decisions get made at the right level.",
    ("Q21", "A"): "Decisions here get from idea to final call without stalling.",  # E2, Pete 2026-09-28
    ("Q22", "A"): "This organization's people policies are current and reviewed regularly.",
    ("Q23", "A"): "This organization has built real depth. No single departure would be unmanageable.",
    ("Q24", "A"): "The highest performers here are engaged, and their pace is sustainable.",
    ("Q25", "A"): "This organization develops people on purpose, and it shows in who gets promoted.",
    ("Q26", "A"): "Cross-functional work happens naturally here and produces results.",
    ("Q27B", "A"): "The culture this organization describes is the culture people actually live.",
    ("Q28", "A"): "After an earlier legal or HR matter, this organization made real structural changes.",
    ("Q30", "A"): "Leadership here communicates deliberately, and people are generally informed.",
    ("Q32", "A"): "This organization examines what happened, draws conclusions, and actually changes as a result.",
    ("Q33", "A"): "Operational plans here are current, tested, and match how the organization actually runs.",
    ("Q36", "A"): "Underperformance here usually gets an early, direct conversation, and that resolves most of it.",
    ("Q37", "A"): "When something stops working here, whoever owns it flags it and brings a recommendation.",
    ("Q38", "A"): "If a senior leader left suddenly, someone here is ready to cover the work.",
    ("Q39", "A"): "When someone isn't right for a role, this organization addresses it directly and decides.",
}
LIABILITY = {
    ("DIST-CM-01", "A"): "This manager's role grew significantly, and nothing was taken off their plate.",
    ("DIST-CM-02", "A"): "This manager knows what each person needs to grow but hasn't acted on it.",
    ("DIST-CM-02", "C"): "This manager points to workload or time as the reason development hasn't happened.",
}
# House-dash fixes, for Pete's approval. Q07-A was found beyond the two named.
DASH_FIXES = {
    ("Q02", "C"): "HR is thin here. It's a part-time role or something people share on top of other work.",
    ("Q09", "D"): "There's a senior-level dynamic that's broken the surface, and the rest of the organization has noticed.",
    ("Q07", "A"): "Turnover here doesn't concentrate anywhere obvious. It's spread across the organization.",
}

VAL_COMMENT_OLD = (
    "    # observation_valence for every authored observation_text below, wired\n"
    "    # to AnswerOption.observation_valence at build time. Pete-approved\n"
    "    # 2026-09-27: 103 liability, 6 neutral (Q07-A, Q34-A..E), 0 asset --\n"
    "    # none of the authored text is phrased as a strength yet.\n"
)
VAL_COMMENT_NEW = (
    "    # observation_valence for every authored observation_text below, wired\n"
    "    # to AnswerOption.observation_valence at build time. Pete-approved\n"
    "    # 2026-09-27 (103 liability, 6 neutral: Q07-A, Q34-A..E), extended by\n"
    "    # Pass 2 on 2026-09-28: 33 asset (the strength answers that can surface\n"
    "    # as asset evidence) and 3 liability (DIST-CM-01-A, DIST-CM-02-A/C).\n"
    "    # Totals: 106 liability, 6 neutral, 33 asset.\n"
)
TXT_COMMENT_OLD = (
    "    # 0.25 baseline across every field, no salience-differentiating signal\n"
    "    # to author against. The single strength/baseline option per other\n"
    "    # question (the asset/healthy case) is deliberately left unauthored\n"
    "    # throughout, except where a question has no such option (Q07, Q34).\n"
)
TXT_COMMENT_NEW = (
    "    # 0.25 baseline across every field, no salience-differentiating signal\n"
    "    # to author against. Strength answers carry asset-valence text (Pass 2,\n"
    "    # 2026-09-28) wherever _build_asset_evidence can quote them: live-\n"
    "    # reachable, not placeholder-seeded, positive asset signal on a field\n"
    "    # the question's options differ on. Strength answers on unreachable\n"
    "    # questions (Q03A, Q27A, VERIFY-*) stay unauthored.\n"
)

BANNED = {"em-dash": "—", "en-dash": "–", "double hyphen": "--", "semicolon": ";"}

TP = "tools/test_phase1_report_data.py"
TEST_EDITS = [
    (
        'check("valence: all 109 authored texts tagged 103 liability / 6 neutral / 0 asset",\n'
        '      _Counter(o.observation_valence for o in _opts if o.observation_text) == {"liability": 103, "neutral": 6})\n',
        'check("valence: all 145 authored texts tagged 106 liability / 6 neutral / 33 asset (Pass 2)",\n'
        '      _Counter(o.observation_valence for o in _opts if o.observation_text) == {"liability": 106, "neutral": 6, "asset": 33})\n'
        'check("valence: asset text only on options that carry positive asset signal",\n'
        '      all(any(isinstance(v, (int, float)) and v > 0 for f, v in o.dimensional_contributions.items() if f.endswith("_asset"))\n'
        '          for o in _opts if o.observation_valence == "asset"))\n'
        'check("house punctuation: no authored observation_text has an em-dash, en-dash, double hyphen, or semicolon",\n'
        '      not [o.observation_text for o in _opts if o.observation_text\n'
        '           and any(ch in o.observation_text for ch in ("\\u2014", "\\u2013", "--", ";"))])\n',
    ),
    (
        '# With no asset-valence text, strength evidence keeps axes and scores but cites nothing\n'
        'vec_s, log_s = _path(max)\n'
        'ev = _build_asset_evidence(vec_s, log_s, INTAKE)\n'
        'check("asset evidence: strongest_axes and net_scores still populate", ev is not None and ev["strongest_axes"] and ev["net_scores"])\n'
        'check("asset evidence: contributing_signals empty (no asset-valence text authored yet)", ev["contributing_signals"] == [])\n',
        '# Strength path: evidence quotes asset-valence text, and only that (Pass 2)\n'
        'vec_s, log_s = _path(max)\n'
        'ev = _build_asset_evidence(vec_s, log_s, INTAKE)\n'
        'check("asset evidence: strongest_axes and net_scores still populate", ev is not None and ev["strongest_axes"] and ev["net_scores"])\n'
        '_asset_texts = {o.observation_text for o in _opts if o.observation_valence == "asset"}\n'
        'check("asset evidence: strength path quotes asset-valence text only",\n'
        '      bool(ev["contributing_signals"]) and all(s["observation_text"] in _asset_texts for s in ev["contributing_signals"]),\n'
        '      str(ev["contributing_signals"][:3]))\n'
        '_txt = lambda q, o: next(x for x in L[q].answer_options if x.option_id == o).observation_text\n'
        '_got = [s["observation_text"] for s in ev["contributing_signals"]]\n'
        'check("asset evidence: capped at 5 quoted lines, highest contribution first, ties in question order",\n'
        '      _got == [_txt("Q01", "A"), _txt("Q02", "A"), _txt("Q04", "A"), _txt("Q06", "E"), _txt("Q13", "E")], str(_got))\n'
        '# The mixed respondent from the Pass 2 review: strong on six answers, weakest everywhere else.\n'
        '_picks = {"Q01": "A", "Q05": "A", "Q20": "A", "Q21": "A", "Q36": "A", "Q37": "A"}\n'
        '_mlog, _msess = [], AccumulationSession()\n'
        'for _q in seq:\n'
        '    _o = (next(x for x in L[_q].answer_options if x.option_id == _picks[_q]) if _q in _picks\n'
        '          else min(L[_q].answer_options, key=lambda o: sum(o.dimensional_contributions.get(f, 0) for f in AFS)))\n'
        '    _mlog.append({"question_id": _q, "option_ids": [_o.option_id]})\n'
        '    accumulate_answer(_msess, _o, INTAKE, _q)\n'
        '_mev = _build_asset_evidence(_msess.accumulated_vector, _mlog, INTAKE)\n'
        '_mgot = [s["observation_text"] for s in _mev["contributing_signals"]]\n'
        'check("asset evidence: mixed respondent quotes its 4 authority answers, under the cap",\n'
        '      _mev["strongest_axes"] == ["authority"]\n'
        '      and _mgot == [_txt("Q01", "A"), _txt("Q21", "A"), _txt("Q36", "A"), _txt("Q37", "A")], str(_mgot))\n',
    ),
]

# Addition 3 (Pete, 2026-09-28): cap the quoted strength evidence at 5 lines.
CP = "engine/contract.py"
CONTRACT_EDITS = [
    (
        '_ASSET_FIELDS = ("aptitude_asset", "authority_asset", "alliance_asset", "attitude_asset")\n',
        '_ASSET_FIELDS = ("aptitude_asset", "authority_asset", "alliance_asset", "attitude_asset")\n'
        '# Most quoted strength lines asset_evidence carries (Pete, 2026-09-28).\n'
        '_ASSET_EVIDENCE_MAX = 5\n',
    ),
    (
        "            # Strength evidence cites asset-valence text only: problem-phrased\n"
        "            # text on an answer that happens to add asset signal is never a\n"
        "            # strength. None is authored yet, so this is [] for now.\n",
        "            # Strength evidence cites asset-valence text only: problem-phrased\n"
        "            # text on an answer that happens to add asset signal is never a\n"
        "            # strength.\n",
    ),
    (
        "    scored.sort(key=lambda item: item[0], reverse=True)\n"
        "    signals: list = []\n"
        "    seen: set = set()\n"
        "    for _, f, text in scored:\n"
        "        if text in seen:\n"
        "            continue\n"
        "        seen.add(text)\n"
        "        signals.append({\"axis\": f.replace(\"_asset\", \"\"), \"observation_text\": text})\n",
        "    # Highest contribution to a leading axis first. The sort is stable and\n"
        "    # answers_log is in question order, so ties keep question order.\n"
        "    scored.sort(key=lambda item: item[0], reverse=True)\n"
        "    signals: list = []\n"
        "    seen: set = set()\n"
        "    for _, f, text in scored:\n"
        "        if text in seen:\n"
        "            continue\n"
        "        seen.add(text)\n"
        "        signals.append({\"axis\": f.replace(\"_asset\", \"\"), \"observation_text\": text})\n"
        "        if len(signals) == _ASSET_EVIDENCE_MAX:\n"
        "            break\n",
    ),
]


def dict_span(src: str, name: str):
    start = src.index(f"    {name}: dict = {{\n")
    body_start = src.index("{", start)
    end = src.index("\n    }\n", body_start) + len("\n    }\n")
    literal = src[body_start: end - 1].strip()
    return start, end, ast.literal_eval(literal)


def render_valence(d: dict) -> str:
    lines = ["    _observation_valence_tags: dict = {"]
    for qid, opts in d.items():
        inner = ", ".join(f'"{k}": "{v}"' for k, v in opts.items())
        lines.append(f'        "{qid}": {{{inner}}},')
    return "\n".join(lines) + "\n    }\n"


def render_text(d: dict) -> str:
    lines = ["    _observation_text_tags: dict = {"]
    for qid, opts in d.items():
        lines.append(f'        "{qid}": {{')
        for k, v in opts.items():
            lines.append(f'            "{k}": {json.dumps(v, ensure_ascii=False)},')
        lines.append("        },")
    return "\n".join(lines) + "\n    }\n"


def merge(existing: dict, additions: dict, order: list) -> dict:
    out = {q: dict(o) for q, o in existing.items()}
    for (qid, oid), val in additions.items():
        out.setdefault(qid, {})[oid] = val
    pos = {q: i for i, q in enumerate(order)}
    merged = {}
    for qid in sorted(out, key=lambda q: pos[q]):
        merged[qid] = dict(sorted(out[qid].items()))
    return merged


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = pathlib.Path(args.root).resolve()
    sys.path.insert(0, str(root))
    from engine.data.questions import QUESTION_LIBRARY as L

    order = list(L)
    src = (root / QP).read_text(encoding="utf-8")
    ok = True

    # 1. Targets exist, are unauthored (except dash fixes), and asset targets carry asset signal.
    for (qid, oid) in {**ASSET, **LIABILITY, **DASH_FIXES}:
        opt = next((o for o in L[qid].answer_options if o.option_id == oid), None)
        if opt is None:
            print(f"[FAIL] {qid}-{oid} does not exist"); ok = False; continue
        if (qid, oid) in DASH_FIXES:
            if "--" not in (opt.observation_text or ""):
                print(f"[FAIL] {qid}-{oid} has no '--' to fix"); ok = False
        elif opt.observation_text:
            print(f"[FAIL] {qid}-{oid} already authored: {opt.observation_text!r}"); ok = False
        if (qid, oid) in ASSET and not any(
            isinstance(v, (int, float)) and v > 0
            for f, v in opt.dimensional_contributions.items() if f.endswith("_asset")
        ):
            print(f"[FAIL] {qid}-{oid} carries no positive asset signal"); ok = False

    # 2. House punctuation on every new or rewritten text.
    for key, text in {**ASSET, **LIABILITY, **DASH_FIXES}.items():
        hits = [n for n, ch in BANNED.items() if ch in text]
        if hits:
            print(f"[FAIL] {key[0]}-{key[1]} contains {hits}: {text!r}"); ok = False
    print(f"[CHECK] punctuation: {len(ASSET) + len(LIABILITY) + len(DASH_FIXES)} texts scanned for "
          "em-dash, en-dash, double hyphen, semicolon")

    vs, ve, vdict = dict_span(src, "_observation_valence_tags")
    ts, te, tdict = dict_span(src, "_observation_text_tags")
    new_v = merge(vdict, {**{k: "asset" for k in ASSET}, **{k: "liability" for k in LIABILITY}}, order)
    new_t = merge(tdict, {**ASSET, **LIABILITY, **DASH_FIXES}, order)

    # 3. Consistency and counts.
    vkeys = {(q, o) for q, d in new_v.items() for o in d}
    tkeys = {(q, o) for q, d in new_t.items() for o in d}
    if vkeys != tkeys:
        print(f"[FAIL] text/valence key mismatch: {sorted(vkeys ^ tkeys)}"); ok = False
    counts = Counter(v for d in new_v.values() for v in d.values())
    print(f"[CHECK] valence counts after patch: {dict(counts)} (total {sum(counts.values())})")
    if counts != Counter({"liability": 106, "neutral": 6, "asset": 33}):
        print("[FAIL] expected 106 liability / 6 neutral / 33 asset"); ok = False
    remaining = [f"{q}-{o}" for q, d in new_t.items() for o, t in d.items()
                 if any(ch in t for ch in BANNED.values())]
    print(f"[CHECK] authored texts still carrying banned punctuation after patch: {remaining or 'none'}")

    if not ok:
        print("Aborting, nothing written."); return 1

    new_src = src[:ts] + render_text(new_t) + src[te:]
    new_src = new_src[:vs] + render_valence(new_v) + new_src[ve:] if vs < ts else None
    if new_src is None:
        print("[FAIL] unexpected table order"); return 1
    for old, new in ((VAL_COMMENT_OLD, VAL_COMMENT_NEW), (TXT_COMMENT_OLD, TXT_COMMENT_NEW)):
        if new_src.count(old) != 1:
            print("[FAIL] comment anchor not found"); return 1
        new_src = new_src.replace(old, new, 1)

    tsrc = (root / TP).read_text(encoding="utf-8")
    new_tsrc = tsrc
    for old, new in TEST_EDITS:
        if new_tsrc.count(old) != 1:
            print(f"[FAIL] {TP}: test anchor not found"); return 1
        new_tsrc = new_tsrc.replace(old, new, 1)

    csrc = (root / CP).read_text(encoding="utf-8")
    new_csrc = csrc
    for old, new in CONTRACT_EDITS:
        if new_csrc.count(old) != 1:
            print(f"[FAIL] {CP}: anchor not found"); return 1
        new_csrc = new_csrc.replace(old, new, 1)

    files = ((QP, src, new_src), (CP, csrc, new_csrc), (TP, tsrc, new_tsrc))
    if args.dry_run:
        for rel, a, b in files:
            sys.stdout.writelines(difflib.unified_diff(
                a.splitlines(True), b.splitlines(True), f"a/{rel}", f"b/{rel}"))
        print("\nDry run only, nothing written.")
    else:
        for rel, _, b in files:
            (root / rel).write_text(b, encoding="utf-8")
            print(f"[WROTE] {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
