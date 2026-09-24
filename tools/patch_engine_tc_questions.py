"""
engine/data/questions.py -- add all 40 TC-* tactical/compliance questions
to QUESTION_LIBRARY, from tactical-compliance-questions-schema-compliant.json
(Downloads, not the repo).

Mechanism confirmed against live source before writing this script, not
assumed:
- sequence_position is never read anywhere outside its own definition/
  construction in questions.py -- confirmed via repo-wide grep. It's
  descriptive metadata; PHASE_1_QUESTION_SEQUENCE's array order is what
  actually drives presentation order (confirmed directly in
  web/lib/session-store.ts's own header comment: Q35-39 were "inserted at
  their own authored sequence_position," i.e. the array is authoritative,
  the field just documents where they conceptually sit). Left None for
  all 40 TC questions -- a supported value (QuestionDefinition.sequence_
  position is Optional[int]).
- checkpoint_segment is likewise never read outside its own definition --
  confirmed via repo-wide grep, not load-bearing for real checkpoint
  logic (Q11/Q19/Q27 Shannon Entropy checkpoints fire off answer-count
  position, not this field). QuestionDefinition.checkpoint_segment is a
  required (non-Optional) str, so it needs a real value -- "tactical" is
  a new label, not one of the 4 existing ones (early/mid/late/
  conditional), since none of those honestly describes an appended
  add-on module. Confirmed safe to introduce: nothing pattern-matches
  against a fixed enum of segment values anywhere in the engine.
- Bare dict(_z) (zero overrides) is the codebase's own existing idiom for
  a genuinely zero-signal option -- confirmed live precedent at Q48-Q51's
  own "A" options (engine/data/questions.py, _opt_contrib). All 160 TC
  option entries (40 questions x 4 options) use this exact form.
- axis_targets / severity_input_mapping / observation_text: left
  unset for every TC option, matching the JSON's null/[] values --
  _build_library()'s assembly loop already defaults these correctly
  (.get(qid, {}).get(option_id, default)) when no entry exists in
  _axis_tags / _severity_input_tags / _observation_text_tags, so nothing
  needs to be added to those three dicts.

"intent" is NOT written into QuestionDefinition -- confirmed it isn't a
real dataclass field. See tools/patch_tactical_question_copy.py (separate
script) for where it actually lives: a new, flagged frontend data layer,
since none existed before this.

Usage:
    python tools/patch_engine_tc_questions.py --dry-run
    python tools/patch_engine_tc_questions.py --write
"""
import argparse
import json
import pathlib
import sys

QUESTIONS_PATH = pathlib.Path('engine/data/questions.py')
JSON_PATH = pathlib.Path(r'C:\Users\rizzo\Downloads\tactical-compliance-questions-schema-compliant.json')

QDATA_CLOSE_ANCHOR = '''        ["the_culture_that_wasnt", "identity_erosion", "culture_drift"],
        False,
    ),
]


# -- Builder'''  # unique text immediately around _QDATA's closing "]"
OPT_CONTRIB_CLOSE_ANCHOR = '''        "Q51": {
            "A": dict(_z),
            "B": {**_z, "attitude_liability":  0.25},
            "C": {**_z, "attitude_liability":  0.50},
            "D": {**_z, "attitude_liability":  0.75},
        },
    }
'''

CONSTANTS_ANCHOR_OLD = 'SEVERITY_FOLLOW_ON_IDS = [f"SEVER-{i:02d}" for i in range(1, 14)]  # SEVER-01 to SEVER-13\n'


def py_str(s: str) -> str:
    """Repr a string as a Python double-quoted literal, matching this
    file's own house style (double quotes throughout _QDATA)."""
    escaped = s.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def build_qdata_block(question_sets: list) -> tuple[str, list[str]]:
    lines = []
    all_ids = []
    for qset in question_sets:
        for q in qset['questions']:
            qid = q['question_id']
            all_ids.append(qid)
            opts = q['options']
            lines.append('    (')
            lines.append(f'        {py_str(qid)},')
            lines.append(f'        {py_str(q["question_text"])},')
            lines.append(f'        "forced_choice", None, "tactical",')
            lines.append('        [')
            for o in opts:
                lines.append(
                    f'            ({py_str(o["option_id"])}, {py_str(o["option_text"])}, False, None),'
                )
            lines.append('        ],')
            lines.append('        [],')
            lines.append('        False,')
            lines.append('    ),')
    return '\n'.join(lines), all_ids


def build_opt_contrib_block(question_sets: list) -> str:
    lines = []
    for qset in question_sets:
        for q in qset['questions']:
            qid = q['question_id']
            lines.append(f'        {py_str(qid)}: {{')
            for o in q['options']:
                lines.append(f'            {py_str(o["option_id"])}: dict(_z),')
            lines.append('        },')
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    if not JSON_PATH.exists():
        print(f'ERROR: {JSON_PATH} not found.', file=sys.stderr)
        sys.exit(1)

    data = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    question_sets = data['question_sets']

    total_q = sum(len(qs['questions']) for qs in question_sets)
    if total_q != 40:
        print(f'ERROR: expected 40 questions, found {total_q}.', file=sys.stderr)
        sys.exit(1)
    for qset in question_sets:
        for q in qset['questions']:
            for o in q['options']:
                if o['dimensional_contributions'] != 'ZERO':
                    print(
                        f'ERROR: {q["question_id"]}/{o["option_id"]} has non-ZERO '
                        f'dimensional_contributions in source JSON -- refusing to '
                        f'silently substitute a real value.',
                        file=sys.stderr,
                    )
                    sys.exit(1)

    qdata_block, all_ids = build_qdata_block(question_sets)
    opt_contrib_block = build_opt_contrib_block(question_sets)

    content = QUESTIONS_PATH.read_text(encoding='utf-8')
    original_len = len(content)

    # 1) Insert new _QDATA tuples right before the list's closing "]".
    count = content.count(QDATA_CLOSE_ANCHOR)
    if count != 1:
        print(f'ERROR: _QDATA closing anchor found {count} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    qdata_replacement = (
        '''        ["the_culture_that_wasnt", "identity_erosion", "culture_drift"],
        False,
    ),
'''
        + '    # -- Tactical & Compliance module (TC-*), hrdiagnostic.com only --------\n'
        + '    # 40 questions across 10 sections, all zero-signal (dict(_z) on every\n'
        + '    # option -- see _opt_contrib below), state_targets=[] for all. Source:\n'
        + '    # tactical-compliance-questions-schema-compliant.json.\n'
        + qdata_block + '\n'
        + ''']


# -- Builder'''
    )
    new_content = content.replace(QDATA_CLOSE_ANCHOR, qdata_replacement, 1)

    # 2) Insert new _opt_contrib entries right before its closing "}".
    count2 = new_content.count(OPT_CONTRIB_CLOSE_ANCHOR)
    if count2 != 1:
        print(f'ERROR: _opt_contrib closing anchor found {count2} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    opt_insertion = (
        OPT_CONTRIB_CLOSE_ANCHOR[:-len('    }\n')]
        + '        # -- Tactical & Compliance module (TC-*) -- bare dict(_z) on every\n'
        + '        # option, same idiom as Q48-Q51\'s own zero-signal "A" options above.\n'
        + opt_contrib_block + '\n'
        + '    }\n'
    )
    new_content = new_content.replace(OPT_CONTRIB_CLOSE_ANCHOR, opt_insertion, 1)

    # 3) TACTICAL_QUESTION_IDS constant, next to the existing ID-list constants.
    id_list_str = ', '.join(py_str(i) for i in all_ids)
    tc_constant = (
        f'{CONSTANTS_ANCHOR_OLD}'
        f'TACTICAL_QUESTION_IDS = [{id_list_str}]  # TC-* module, hrdiagnostic.com only, 40 total\n'
    )
    count3 = new_content.count(CONSTANTS_ANCHOR_OLD)
    if count3 != 1:
        print(f'ERROR: constants anchor found {count3} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    new_content = new_content.replace(CONSTANTS_ANCHOR_OLD, tc_constant, 1)

    if args.dry_run:
        print('DRY RUN -- all anchors found, all insertions would apply cleanly.')
        print(f'Old length: {original_len}, new length: {len(new_content)}, delta: {len(new_content) - original_len}')
        print(f'40 question IDs: {all_ids}')
    else:
        QUESTIONS_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {original_len}, new length: {len(new_content)}, delta: {len(new_content) - original_len}')


if __name__ == '__main__':
    main()
