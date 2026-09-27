"""
TC-HRPOL-01 question text: remove the spaced double hyphen (Pete,
2026-09-27). House style: no em-dashes or dash stand-ins as connective
tissue, rephrase with a comma first. Pattern follows the earlier core
question house-style pass (e7d71f7), which rephrased dash asides with
commas.

Before: When was your employee handbook last substantively revised -- not
        reformatted, actually reviewed against current law and current
        practice?
After:  When was your employee handbook last substantively revised, meaning
        actually reviewed against current law and current practice, not
        just reformatted?

No test asserts on this string. The vitest mock fixture that echoes it
(web/lib/diagnostic-completion.test.ts) is updated to mirror the source.
The other 20 spaced-dash instances across 14 more TC-* questions and
options are NOT touched here, flagged to Pete as a copy decision.

Usage:
    python tools/patch_tc_hrpol01_house_style.py --dry-run
    python tools/patch_tc_hrpol01_house_style.py --write
"""
import argparse
import pathlib
import sys

OLD = ('When was your employee handbook last substantively revised -- not reformatted, actually reviewed '
       'against current law and current practice?')
NEW = ('When was your employee handbook last substantively revised, meaning actually reviewed against '
       'current law and current practice, not just reformatted?')
FILES = [pathlib.Path('engine/data/questions.py'), pathlib.Path('web/lib/diagnostic-completion.test.ts')]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    edited = {}
    for p in FILES:
        t = p.read_text(encoding='utf-8')
        if t.count(OLD) != 1:
            print(f'ERROR: {p}: text found {t.count(OLD)} times.', file=sys.stderr)
            sys.exit(1)
        edited[p] = t.replace(OLD, NEW, 1)
        print(f'[{p}] OK')
    print('BEFORE:', OLD)
    print('AFTER: ', NEW)
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    for p, t in edited.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE: {p}')


if __name__ == '__main__':
    main()
