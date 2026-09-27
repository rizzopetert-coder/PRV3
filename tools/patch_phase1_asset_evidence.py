"""
Phase 1 (report redesign), commit 2: asset evidence (Pete, 2026-09-27,
Gemini-reviewed spec, verified 2026-09-27: the four *_asset fields in
accumulated_vector are respondent-specific, but every SEVER-* follow-on
and Q03B / Q03A-D-FOLLOW add a fixed amount to all four whatever the
answer -- the question library's own placeholder seeding).

New private_output["asset_evidence"] = {strongest_axes, contributing_signals,
net_scores}, OMITTED entirely (no key) when all four net scores are 0.0.

  - Baseline questions: derived from QUESTION_LIBRARY, not hardcoded --
    questions whose options all carry identical, nonzero asset
    contributions (today: the 28 SEVER-* follow-ons, Q03A-D-FOLLOW, Q03B).
  - Baseline inflation: the respondent's answers to those questions are
    replayed through accumulate_answer(), so the subtraction is exactly what
    they added after role scaling. Equals count x 0.25 per axis while role
    coefficients are 1.0 (today), and stays exact once they're calibrated.
  - net = max(0.0, raw - inflation) per axis.
  - strongest_axes: every axis tied at the highest net score.
  - contributing_signals: {axis, observation_text} for answers (non-TC,
    non-baseline) whose replayed contribution to a strongest axis is > 0
    on a question whose options actually differ on that axis, AUTHORED
    observation_text only, never raw option_text. Ranked by contribution,
    deduplicated by text.
  - net_scores: the four net values, additive, so Phase 3 can show the math.

Silent until Phase 3 (web passes it through, no UI reads it).

Usage:
    python tools/patch_phase1_asset_evidence.py --dry-run
    python tools/patch_phase1_asset_evidence.py --write
"""
import argparse
import pathlib
import sys

CT = pathlib.Path('engine/contract.py')

HELPERS = '''
# ── Phase 1 asset evidence ──────────────────────────────────────────────────

_ASSET_FIELDS = ("aptitude_asset", "authority_asset", "alliance_asset", "attitude_asset")


def _derive_asset_baseline_question_ids() -> frozenset:
    """Questions whose options all carry the same nonzero asset values, so
    answering them adds asset signal whatever the answer (the question
    library's placeholder seeding). Derived, not hardcoded."""
    ids = set()
    for qid, q in QUESTION_LIBRARY.items():
        vectors = {
            tuple(round(o.dimensional_contributions.get(f, 0.0), 6) for f in _ASSET_FIELDS)
            for o in q.answer_options
        }
        if len(vectors) == 1 and any(next(iter(vectors))):
            ids.add(qid)
    return frozenset(ids)


_ASSET_BASELINE_QUESTION_IDS = _derive_asset_baseline_question_ids()


def _answer_dependent(question, field: str) -> bool:
    """True when the question's options actually differ on this field."""
    return len({round(o.dimensional_contributions.get(field, 0.0), 6) for o in question.answer_options}) > 1


def _selected_options(entry):
    if not isinstance(entry, dict):
        return None, []
    question = QUESTION_LIBRARY.get(entry.get("question_id"))
    option_ids = entry.get("option_ids")
    if question is None or not isinstance(option_ids, list):
        return None, []
    return question, [o for o in question.answer_options if o.option_id in option_ids]


def _build_asset_evidence(accumulated_vector: dict, answers_log: list, intake_data) -> Optional[dict]:
    """
    Where this respondent's own answers show strength. None (key omitted)
    when every net asset score is 0.0. See tools/patch_phase1_asset_evidence.py
    for the full rule set.
    """
    baseline = AccumulationSession()
    for entry in answers_log or []:
        if not isinstance(entry, dict) or entry.get("question_id") not in _ASSET_BASELINE_QUESTION_IDS:
            continue
        _, options = _selected_options(entry)
        for option in options:
            accumulate_answer(baseline, option, intake_data, entry.get("question_id"))

    net = {
        f: max(0.0, accumulated_vector.get(f, 0.0) - baseline.accumulated_vector.get(f, 0.0))
        for f in _ASSET_FIELDS
    }
    top = max(net.values())
    if top <= 1e-9:
        return None
    leading = [f for f in _ASSET_FIELDS if abs(net[f] - top) <= 1e-9]

    scored: list = []
    for entry in answers_log or []:
        question_id = entry.get("question_id") if isinstance(entry, dict) else None
        if not question_id or question_id.startswith("TC-") or question_id in _ASSET_BASELINE_QUESTION_IDS:
            continue
        question, options = _selected_options(entry)
        for option in options:
            if not option.observation_text:
                continue
            scratch = AccumulationSession()
            accumulate_answer(scratch, option, intake_data, question_id)
            for f in leading:
                amount = scratch.accumulated_vector.get(f, 0.0)
                if amount > 0 and _answer_dependent(question, f):
                    scored.append((amount, f, option.observation_text))

    scored.sort(key=lambda item: item[0], reverse=True)
    signals: list = []
    seen: set = set()
    for _, f, text in scored:
        if text in seen:
            continue
        seen.add(text)
        signals.append({"axis": f.replace("_asset", ""), "observation_text": text})

    return {
        "strongest_axes": [f.replace("_asset", "") for f in leading],
        "contributing_signals": signals,
        "net_scores": {f.replace("_asset", ""): round(net[f], 4) for f in _ASSET_FIELDS},
    }


def assemble_output(
'''

EDITS = [
    ('\n\ndef assemble_output(\n', '\n' + HELPERS, 'asset helpers'),
    ('    private_output = {\n'
     '        "opening_text":            priv.state_name if priv else "",\n',
     '    asset_evidence = _build_asset_evidence(\n'
     '        session.accumulated_vector, answers_log or [], session.intake,\n'
     '    )\n'
     '    private_output = {\n'
     '        "opening_text":            priv.state_name if priv else "",\n',
     'compute asset evidence'),
    ('        "urgency_window":        urgency_window_obj,\n'
     '    }\n',
     '        "urgency_window":        urgency_window_obj,\n'
     '    }\n'
     '    # Omitted entirely, not an empty object, when there is no net\n'
     '    # asset signal (Phase 1 spec).\n'
     '    if asset_evidence is not None:\n'
     '        private_output["asset_evidence"] = asset_evidence\n',
     'attach asset evidence'),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    t = CT.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        n = t.count(old)
        if n != 1:
            print(f'ERROR: {label} anchor found {n} times.', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{CT} :: {label}] OK')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    CT.write_text(t, encoding='utf-8')
    print(f'WROTE: {CT}')


if __name__ == '__main__':
    main()
