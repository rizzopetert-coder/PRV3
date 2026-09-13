"""
tools/test_accumulation.py: section 13, tests for Q05's new option E
(tools/patch_q05_ipm_option_e.py) -- invisible_performance_management's
second wired question.

Confirms: option E exists with the expected text and a clean,
single-field authority_liability=0.60 dimensional_contributions (same
shape as Q35's own option E); invisible_performance_management is now
in Q05's state_targets; and options A-D are byte-identical to their
pre-fix values (zero regression to Q05's 6 existing target states'
own wiring).

Usage:
    python tools/patch_test_accumulation_q05e.py --dry-run
    python tools/patch_test_accumulation_q05e.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_accumulation.py')

ANCHOR_OLD = '''# ── Summary ────────────────────────────────────────────────────────────────────
print("\\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")'''

ANCHOR_NEW = '''# ── 13. Q05-E wiring — invisible_performance_management's second question ────
print("\\n13. Q05-E wiring — invisible_performance_management's second question")

q05_opts = {o.option_id: o for o in QUESTION_LIBRARY["Q05"].answer_options}

check("Q05 now has 5 options (A-E), option E present",
      set(q05_opts.keys()) == {"A", "B", "C", "D", "E"},
      f"got {sorted(q05_opts.keys())}")

check("Q05-E option text matches the fix's intended wording",
      q05_opts["E"].option_text ==
      "It gets recognized and handled well in the moment, but none of it gets written down.",
      f"got {q05_opts['E'].option_text!r}")

_q05e_expected = {f: 0.0 for f in DIMENSIONAL_FIELDS}
_q05e_expected["authority_liability"] = 0.60
check("Q05-E dimensional_contributions: clean single-field authority_liability=0.60, "
      "same shape as Q35's own option E -- can't be confused for a contrast against "
      "A-D's own Attitude-axis logic",
      q05_opts["E"].dimensional_contributions == _q05e_expected,
      f"got {q05_opts['E'].dimensional_contributions}")

check("invisible_performance_management is now in Q05's state_targets",
      "invisible_performance_management" in QUESTION_LIBRARY["Q05"].state_targets,
      f"got {QUESTION_LIBRARY['Q05'].state_targets}")

check("Q05's original 6 target states are still present, unchanged",
      set(QUESTION_LIBRARY["Q05"].state_targets) >= {
          "the_basement_standard", "the_untouchable", "the_inside_track",
          "the_arbitrary_standard", "the_wrong_reward", "the_paper_tiger",
      },
      f"got {QUESTION_LIBRARY['Q05'].state_targets}")

_q05_ad_expected = {
    "A": {**{f: 0.0 for f in DIMENSIONAL_FIELDS}, "attitude_asset": 0.40},
    "B": {**{f: 0.0 for f in DIMENSIONAL_FIELDS}, "attitude_liability": 0.25},
    "C": {**{f: 0.0 for f in DIMENSIONAL_FIELDS}, "attitude_liability": 0.60},
    "D": {**{f: 0.0 for f in DIMENSIONAL_FIELDS}, "attitude_liability": 0.60},
}
check("Q05's original options A-D are byte-identical to their pre-fix values -- "
      "zero regression to the 6 states already wired to this question",
      all(q05_opts[oid].dimensional_contributions == want
          for oid, want in _q05_ad_expected.items()),
      f"got {[(oid, q05_opts[oid].dimensional_contributions) for oid in _q05_ad_expected]}")


# ── Summary ────────────────────────────────────────────────────────────────────
print("\\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")'''

EDITS = [
    ('section 13 -- Q05-E wiring', ANCHOR_OLD, ANCHOR_NEW),
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
