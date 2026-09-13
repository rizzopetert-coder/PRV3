"""
engine/data/questions.py: add option E to Q05, wiring
invisible_performance_management's second question. Same fix shape as
Q35's own option E (commit e8f82a8, tools/patch script b4a28e9) -- a
clean, single-field authority_liability=0.60 pick that can't be confused
for a contrast against Q05's existing A-D Attitude-axis logic.

Q05 ("When someone in your organization stands out because of their
underperformance, what happens?") had zero Authority-axis signal across
its 4 existing options -- all four are pure Attitude
(attitude_asset=0.40 / attitude_liability=0.25 or 0.60), the same "zero
positive-authority options anywhere" gap Q35 had before its own fix.
Topically near-identical to Q35 (same underperformance-conversation
domain), with an open E slot -- confirmed via direct inspection this
session (Part C of the investigation this build follows from), not
assumed.

Two edits:
1. _QDATA's Q05 tuple: add option E's (id, text, severity_trigger,
   severity_follow_on_id) and add invisible_performance_management to
   Q05's state_targets.
2. _build_library()'s per-option dimensional_contributions dict
   (_opt_contrib["Q05"]): add "E": single-field authority_liability=0.60,
   mirroring _opt_contrib["Q35"]["E"]'s exact shape.

Usage:
    python tools/patch_q05_ipm_option_e.py --dry-run
    python tools/patch_q05_ipm_option_e.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/data/questions.py')

TUPLE_OLD = '''            ("A", "It gets addressed. There's a process and managers use it.", False, None),
            ("B", "It gets addressed eventually, but it takes longer than it should.", False, None),
            ("C", "It depends on who the person is. Some people are held accountable and some aren't.", True, "SEVER-25"),
            ("D", "Not much. Underperformance tends to get tolerated.", False, None),
        ],
        ["the_basement_standard", "the_untouchable", "the_inside_track",
         "the_arbitrary_standard", "the_wrong_reward", "the_paper_tiger"],
        False,
    ),'''

TUPLE_NEW = '''            ("A", "It gets addressed. There's a process and managers use it.", False, None),
            ("B", "It gets addressed eventually, but it takes longer than it should.", False, None),
            ("C", "It depends on who the person is. Some people are held accountable and some aren't.", True, "SEVER-25"),
            ("D", "Not much. Underperformance tends to get tolerated.", False, None),
            ("E", "It gets recognized and handled well in the moment, but none of it gets written down.", False, None),
        ],
        ["the_basement_standard", "the_untouchable", "the_inside_track",
         "the_arbitrary_standard", "the_wrong_reward", "the_paper_tiger",
         "invisible_performance_management"],
        False,
    ),'''

CONTRIB_OLD = '''        "Q05": {  # Attitude HIGH (the_untouchable). Single-seeded.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.60},                    # P
            "D": {**_z, "attitude_liability": 0.60},                    # P
        },'''

CONTRIB_NEW = '''        "Q05": {  # Attitude HIGH (the_untouchable). Single-seeded.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.60},                    # P
            "D": {**_z, "attitude_liability": 0.60},                    # P
            # Option E added this session -- invisible_performance_management's
            # second wired question (was 1/52 core questions, Q35 only).
            # Same fix shape as Q35's own option E: single-field, clean
            # authority_liability pick, can't be confused for a contrast
            # against A-D's own Attitude-axis logic.
            "E": {**_z, "authority_liability": 0.60},
        },'''

EDITS = [
    ('Q05 _QDATA tuple -- option E + IPM state_targets', TUPLE_OLD, TUPLE_NEW),
    ('Q05 _opt_contrib -- option E dimensional_contributions', CONTRIB_OLD, CONTRIB_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
