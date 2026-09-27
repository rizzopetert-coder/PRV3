"""
observation_valence, Pass 1 (Pete, 2026-09-27, Gemini-reviewed, one atomic
change). Fixes asset evidence surfacing problem-phrased text as a strength
("Safety and security concerns here have gone unaddressed..." shown as the
respondent's strength, every live session), and repeated receipts.

engine/data/questions.py
  - AnswerOption.observation_valence: Optional[Literal["asset", "liability",
    "neutral"]] = None. Defaulted: every field after option_text already has
    a default, so a non-default field would fail at import.
  - _observation_valence_tags: explicit tags for all 109 authored
    observation_text entries, as approved (103 liability, 6 neutral, 0 asset
    -- none of the authored text is phrased as a strength). Neutral: Q07-A,
    Q34-A..E. Wired at build time like _observation_text_tags.
  - PROBLEM_CONTEXT_VALENCES = {"liability", "neutral"}: the one shared
    definition of "fit to cite as evidence of a problem".

Selection, all four observation_text readers:
  - contract._build_asset_evidence(): valence == "asset" only (neutral and
    liability excluded). With no asset-valence text authored yet,
    contributing_signals is [] for every respondent; strongest_axes and
    net_scores are unchanged.
  - contract._top_observation_texts() (driving_factors receipts),
    contract._build_friction_tax_ledger() (top_contributing_answers), and
    main._build_signal_map_context() (Call 1 input): valence in
    PROBLEM_CONTEXT_VALENCES only.
  - Receipt variety: friction and legal receipts each pick, per condition,
    the highest-ranked answer not already used by an earlier condition in
    the same receipt list. When every qualifying answer is already used,
    the top one is reused rather than dropped.

get_question_copy() is an allowlist (question_id, question_text, format,
option_id, option_text), so observation_valence is excluded by
construction, like observation_text. Docstring updated to say so.

Usage:
    python tools/patch_observation_valence.py --dry-run
    python tools/patch_observation_valence.py --write
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

QS = pathlib.Path('engine/data/questions.py')
CT = pathlib.Path('engine/contract.py')
MN = pathlib.Path('engine/main.py')

APPROVED_NEUTRAL = {("Q07", "A"), ("Q34", "A"), ("Q34", "B"), ("Q34", "C"), ("Q34", "D"), ("Q34", "E")}


def render_valence_dict() -> str:
    from engine.data.questions import QUESTION_LIBRARY
    by_q: dict = {}
    for qid, q in QUESTION_LIBRARY.items():
        for o in q.answer_options:
            if o.observation_text:
                by_q.setdefault(qid, []).append(
                    (o.option_id, "neutral" if (qid, o.option_id) in APPROVED_NEUTRAL else "liability")
                )
    total = sum(len(v) for v in by_q.values())
    neutral = sum(1 for v in by_q.values() for _, val in v if val == "neutral")
    if (total, neutral) != (109, 6):
        print(f'ERROR: expected 109 authored (6 neutral), found {total} ({neutral}).', file=sys.stderr)
        sys.exit(1)
    lines = [
        '    # observation_valence for every authored observation_text below, wired',
        '    # to AnswerOption.observation_valence at build time. Pete-approved',
        '    # 2026-09-27: 103 liability, 6 neutral (Q07-A, Q34-A..E), 0 asset --',
        '    # none of the authored text is phrased as a strength yet.',
        '    _observation_valence_tags: dict = {',
    ]
    for qid, pairs in by_q.items():
        inner = ", ".join(f'"{oid}": "{val}"' for oid, val in pairs)
        lines.append(f'        "{qid}": {{{inner}}},')
    lines.append('    }')
    return "\n".join(lines) + "\n"


def qs_edits(valence_block: str) -> list:
    return [
        ('from typing import Optional\n', 'from typing import Literal, Optional\n', 'Literal import'),
        ('    observation_text: Optional[str] = None\n',
         '    observation_text: Optional[str] = None\n'
         '\n'
         '    # What observation_text is evidence of: "liability" (a problem),\n'
         '    # "asset" (a strength), or "neutral" (descriptive). Report readers\n'
         '    # filter on it: asset evidence cites "asset" only, problem-context\n'
         '    # readers cite PROBLEM_CONTEXT_VALENCES only. None when\n'
         '    # observation_text is None. See _observation_valence_tags.\n'
         '    observation_valence: Optional[Literal["asset", "liability", "neutral"]] = None\n',
         'observation_valence field'),
        ('# -- Question definition -------------------------------------------------------\n',
         '# Valences fit to cite as evidence of a problem (driving_factors receipts,\n'
         '# the friction ledger, the synthesis signal map). Asset evidence uses\n'
         '# "asset" only.\n'
         'PROBLEM_CONTEXT_VALENCES = frozenset({"liability", "neutral"})\n'
         '\n'
         '\n'
         '# -- Question definition -------------------------------------------------------\n',
         'PROBLEM_CONTEXT_VALENCES'),
        ('                    observation_text=_observation_text_tags.get(qid, {}).get(o[0]),\n',
         '                    observation_text=_observation_text_tags.get(qid, {}).get(o[0]),\n'
         '                    observation_valence=_observation_valence_tags.get(qid, {}).get(o[0]),\n',
         'wire valence at build'),
        ('    # Sparse per-option observation_text, wired to AnswerOption.observation_text\n',
         valence_block + '\n'
         '    # Sparse per-option observation_text, wired to AnswerOption.observation_text\n',
         'valence tags dict'),
    ]


CT_EDITS = [
    ('from engine.data.questions import QUESTION_LIBRARY\n',
     'from engine.data.questions import QUESTION_LIBRARY, PROBLEM_CONTEXT_VALENCES\n',
     'import'),
    ('        for _, option in scored:\n'
     '            if option.observation_text:\n'
     '                top_contributing_answers.append(option.observation_text)\n',
     '        for _, option in scored:\n'
     '            if option.observation_text and option.observation_valence in PROBLEM_CONTEXT_VALENCES:\n'
     '                top_contributing_answers.append(option.observation_text)\n',
     'ledger filter'),
    ('def _top_observation_texts(\n'
     '    state_id: str, answers_log: list, intake_data, limit: int = 1,\n'
     ') -> list:\n',
     'def _top_observation_texts(\n'
     '    state_id: str, answers_log: list, intake_data, limit: Optional[int] = 1,\n'
     ') -> list:\n',
     'limit None = all'),
    ('    separate rather than refactoring the ledger. Unauthored options are\n'
     '    skipped, never replaced with raw option_text.\n'
     '    """\n',
     '    separate rather than refactoring the ledger. Unauthored options are\n'
     '    skipped, never replaced with raw option_text. Only problem-context\n'
     '    valences (PROBLEM_CONTEXT_VALENCES) are cited. limit=None returns the\n'
     '    full ranking.\n'
     '    """\n',
     'docstring'),
    ('            if option is None or not option.observation_text:\n'
     '                continue\n'
     '            scratch = AccumulationSession()\n'
     '            accumulate_answer(scratch, option, intake_data, entry.get("question_id"))\n'
     '            weight = sum(\n',
     '            if (\n'
     '                option is None or not option.observation_text\n'
     '                or option.observation_valence not in PROBLEM_CONTEXT_VALENCES\n'
     '            ):\n'
     '                continue\n'
     '            scratch = AccumulationSession()\n'
     '            accumulate_answer(scratch, option, intake_data, entry.get("question_id"))\n'
     '            weight = sum(\n',
     'receipt valence filter'),
    ('        if text not in texts:\n'
     '            texts.append(text)\n'
     '        if len(texts) == limit:\n'
     '            break\n'
     '    return texts\n',
     '        if text not in texts:\n'
     '            texts.append(text)\n'
     '        if limit is not None and len(texts) == limit:\n'
     '            break\n'
     '    return texts\n'
     '\n'
     '\n'
     'def _pick_distinct(ranked: list, used: set) -> Optional[str]:\n'
     '    """The highest-ranked text not already cited by an earlier condition in\n'
     '    the same receipt list. Falls back to the top one when every candidate\n'
     '    is already used (reused rather than dropped). Records the pick."""\n'
     '    if not ranked:\n'
     '        return None\n'
     '    pick = next((t for t in ranked if t not in used), ranked[0])\n'
     '    used.add(pick)\n'
     '    return pick\n',
     'limit None + _pick_distinct'),
    ('        _receipt("Organization type", org_type_text),\n'
     '    ]\n',
     '        _receipt("Organization type", org_type_text),\n'
     '    ]\n'
     '    used_answers: set = set()\n',
     'friction used set'),
    ('        observed = _top_observation_texts(s["state_id"], answers_log, intake_data)\n'
     '        receipts.append(_receipt(\n'
     '            "Condition",\n'
     '            f"{s[\'state_name\']} adds cost through {_join_words(channels)}.",\n'
     '            observed[0] if observed else None,\n'
     '        ))\n',
     '        receipts.append(_receipt(\n'
     '            "Condition",\n'
     '            f"{s[\'state_name\']} adds cost through {_join_words(channels)}.",\n'
     '            _pick_distinct(\n'
     '                _top_observation_texts(s["state_id"], answers_log, intake_data, limit=None),\n'
     '                used_answers,\n'
     '            ),\n'
     '        ))\n',
     'friction variety'),
    ('    names = {s["state_id"]: s["state_name"] for s in identified_states}\n'
     '    receipts = []\n'
     '    for b in breakdown:\n',
     '    names = {s["state_id"]: s["state_name"] for s in identified_states}\n'
     '    receipts = []\n'
     '    used_answers: set = set()\n'
     '    for b in breakdown:\n',
     'legal used set'),
    ('        observed = _top_observation_texts(b["state_id"], answers_log, intake_data)\n'
     '        receipts.append(_receipt(\n'
     '            _LEGAL_CLUSTER_LABELS.get(b["cluster"], "Legal exposure"),\n'
     '            rationale + ".",\n'
     '            observed[0] if observed else None,\n'
     '        ))\n',
     '        receipts.append(_receipt(\n'
     '            _LEGAL_CLUSTER_LABELS.get(b["cluster"], "Legal exposure"),\n'
     '            rationale + ".",\n'
     '            _pick_distinct(\n'
     '                _top_observation_texts(b["state_id"], answers_log, intake_data, limit=None),\n'
     '                used_answers,\n'
     '            ),\n'
     '        ))\n',
     'legal variety'),
    ('        for option in options:\n'
     '            if not option.observation_text:\n'
     '                continue\n'
     '            scratch = AccumulationSession()\n'
     '            accumulate_answer(scratch, option, intake_data, question_id)\n'
     '            for f in leading:\n',
     '        for option in options:\n'
     '            # Strength evidence cites asset-valence text only: problem-phrased\n'
     '            # text on an answer that happens to add asset signal is never a\n'
     '            # strength. None is authored yet, so this is [] for now.\n'
     '            if not option.observation_text or option.observation_valence != "asset":\n'
     '                continue\n'
     '            scratch = AccumulationSession()\n'
     '            accumulate_answer(scratch, option, intake_data, question_id)\n'
     '            for f in leading:\n',
     'asset evidence: asset only'),
]

MN_EDITS = [
    ('from engine.data.questions import QUESTION_LIBRARY\n',
     'from engine.data.questions import QUESTION_LIBRARY, PROBLEM_CONTEXT_VALENCES\n',
     'import'),
    ('    for _, option in scored:\n'
     '        if option.observation_text:\n'
     '            observations.append(option.observation_text)\n'
     '        if len(observations) == 7:\n',
     '    for _, option in scored:\n'
     '        if option.observation_text and option.observation_valence in PROBLEM_CONTEXT_VALENCES:\n'
     '            observations.append(option.observation_text)\n'
     '        if len(observations) == 7:\n',
     'signal map filter'),
    ('    question_text and option_id/option_text pairs -- explicitly excludes\n'
     '    dimensional_contributions, axis_targets, severity_trigger, and\n'
     '    severity_follow_on_id.',
     '    question_text and option_id/option_text pairs -- explicitly excludes\n'
     '    dimensional_contributions, axis_targets, severity_trigger,\n'
     '    severity_follow_on_id, observation_text, and observation_valence (an\n'
     '    allowlist, so any new internal field is excluded by construction).',
     'get_question_copy docstring'),
]


def apply(path, edits):
    t = path.read_text(encoding='utf-8')
    for old, new, label in edits:
        n = t.count(old)
        if n != 1:
            print(f'ERROR: {path} :: {label} anchor found {n} times.', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')
    return t


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    block = render_valence_dict()
    out = {QS: apply(QS, qs_edits(block)), CT: apply(CT, CT_EDITS), MN: apply(MN, MN_EDITS)}
    if args.dry_run:
        print('--- rendered valence dict (first lines) ---')
        print("\n".join(block.splitlines()[:9]))
        print('DRY RUN -- nothing written.')
        return
    for p, t in out.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE: {p}')


if __name__ == '__main__':
    main()
