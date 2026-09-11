"""
engine/data/questions.py: add option E to Q35, giving
invisible_performance_management a genuine positive authority_liability
pick.

Root cause (diagnosed this session): Q35's existing 4 options (A-D)
were authored for its 3 originally-Aptitude-dominant wired states
(built_to_fail, the_undefined_role, the_overloaded_manager) and carry
zero positive authority_liability anywhere -- A/C/D contribute 0.0,
B is actively negative (-0.35). invisible_performance_management was
added to Q35's state_targets before the SCD-WCS re-authoring flipped
its dimensional_vector from Aptitude to Authority-dominant
(authority_liability=0.60); Q35's options were never revisited after
that flip, leaving this state's only wired question structurally
unable to produce correct-direction signal for it.

Fix: add a 5th option (E) carrying authority_liability=0.60 only (no
side-effect contributions on other fields, kept deliberately clean) --
same "add a contrast/state-specific option" pattern already used for
Q34's option E and Q36's option E. Doesn't touch A-D, so
best_option_for_state() for the other 3 wired states (which all
maximize aptitude_liability, still winning at option B's 0.80) is
unaffected -- confirmed by direct check after writing, not assumed.

Two anchors: the option-text tuple list (engine/data/questions.py's
_QDATA), and the per-option dimensional_contributions dict
(_opt_contrib["Q35"]) -- both must carry "E" or QuestionDefinition
construction would KeyError on `_opt_contrib[qid][o[0]]`.

Usage:
    python tools/patch_q35_authority_option.py --dry-run
    python tools/patch_q35_authority_option.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/data/questions.py')

OPTIONS_OLD = '''        [
            ("A", "We talk about what the person needs to do differently.", False, None),
            ("B", "We talk about whether the role itself is set up to let them succeed.", False, None),
            ("C", "We talk about whether this is the right role for this person.", False, None),
            ("D", "We don't usually have that conversation until something forces it.", False, None),
        ],
        ["built_to_fail", "the_undefined_role", "the_overloaded_manager", "invisible_performance_management"],
        False,
    ),'''

OPTIONS_NEW = '''        [
            ("A", "We talk about what the person needs to do differently.", False, None),
            ("B", "We talk about whether the role itself is set up to let them succeed.", False, None),
            ("C", "We talk about whether this is the right role for this person.", False, None),
            ("D", "We don't usually have that conversation until something forces it.", False, None),
            ("E", "We talk about it regularly and it seems to land, but none of it gets written down.", False, None),
        ],
        ["built_to_fail", "the_undefined_role", "the_overloaded_manager", "invisible_performance_management"],
        False,
    ),'''

CONTRIB_OLD = '''        "Q35": {  # Contrast B v16; amplify B v17.
            "A": {**_z, "aptitude_liability": 0.25},
            "B": {**_z, "aptitude_liability": 0.80, "authority_liability": -0.35},  # contrast v16, amplify v17
            "C": {**_z, "aptitude_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.40},
        },'''

CONTRIB_NEW = '''        "Q35": {  # Contrast B v16; amplify B v17. Option E added this session --
                  # invisible_performance_management's only wired question had
                  # zero positive-authority options anywhere (a leftover from
                  # before the SCD-WCS re-authoring flipped this state from
                  # Aptitude to Authority-dominant); E gives it a real,
                  # correctly-directed pick, kept single-field/clean so it
                  # can't be confused for a contrast against A-D's own logic.
            "A": {**_z, "aptitude_liability": 0.25},
            "B": {**_z, "aptitude_liability": 0.80, "authority_liability": -0.35},  # contrast v16, amplify v17
            "C": {**_z, "aptitude_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.40},
            "E": {**_z, "authority_liability": 0.60},
        },'''

EDITS = [
    ('Q35 option-text tuple -- add option E', OPTIONS_OLD, OPTIONS_NEW),
    ('Q35 dimensional_contributions -- add option E', CONTRIB_OLD, CONTRIB_NEW),
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
