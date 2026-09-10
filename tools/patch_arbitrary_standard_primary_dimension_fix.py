"""
engine/data/states.py: correct the_arbitrary_standard's
primary_dimension from "Alliance" to "Authority".

Same bug class as the_paper_tiger's and invisible_performance_
management's fixes: primary_dimension was never updated alongside the
SCD-WCS full re-authoring program's dimensional_vector correction
(Phase 2 Batch 2, 2026-08-24, staged Phase 5, 2026-08-25). The vector's
own comment is explicit: "this state's text is Authority-centered...
Ends the mechanical tier-template tie" -- authority_liability=0.35 is
the vector's real, deliberate dominant field (vs. alliance_liability=
0.25), but primary_dimension still reads the pre-re-authoring
"Alliance" value.

Usage:
    python tools/patch_arbitrary_standard_primary_dimension_fix.py --dry-run
    python tools/patch_arbitrary_standard_primary_dimension_fix.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/data/states.py')

OLD = '''_reg(_profile(
    state_id="the_arbitrary_standard",
    state_name="The Arbitrary Standard",
    primary_dimension="Alliance",
    signal_weight="medium",'''

NEW = '''_reg(_profile(
    state_id="the_arbitrary_standard",
    state_name="The Arbitrary Standard",
    # Corrected from "Alliance" (this session): same bug class as
    # the_paper_tiger's and invisible_performance_management's fixes
    # earlier this session -- the SCD-WCS full re-authoring program
    # (Phase 2 Batch 2, 2026-08-24, staged Phase 5, 2026-08-25) already
    # moved dimensional_vector to authority_liability=0.35 dominant
    # ("this state's text is Authority-centered... Ends the mechanical
    # tier-template tie", see that vector's own comment below), but
    # primary_dimension was never updated alongside it.
    primary_dimension="Authority",
    signal_weight="medium",'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    count = content.count(OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
