"""
prompts/scd-wcs-remediation-tracker.md: correct the_paper_tiger's row.
"Still occasionally loses to built_to_fail on built_to_fail's own
turf" is stale -- live measurement (this session's diagnosis pass,
tools/_scdwcs_paper_tiger_rank23_diagnostic.py) confirms 0/3
own-profile capture (APT-PT-00/01/02 all currently lose to
built_to_fail), not an occasional single loss. Same self-correction
convention already used elsewhere in this file (e.g. built_to_fail's
own 41 -> 52 drift note on the row directly above this one). No other
change to the row -- appends one correction sentence to the existing
Notes cell only.

Usage:
    python tools/patch_tracker_paper_tiger_occasional_correction.py --dry-run
    python tools/patch_tracker_paper_tiger_occasional_correction.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('prompts/scd-wcs-remediation-tracker.md')

OLD = "Still occasionally loses to `built_to_fail` on `built_to_fail`'s own turf — expected, untouched by this fix. |"

NEW = (
    "Still occasionally loses to `built_to_fail` on `built_to_fail`'s own turf — expected, untouched by this fix. "
    "**CORRECTION, 2026-09-10, this session — the \"occasionally\" framing above is stale.** "
    "Live measurement confirms **0/3 own-profile capture**, not occasional: all three of "
    "`the_paper_tiger`'s own dedicated profiles (`APT-PT-00`/`01`/`02`) currently lose to "
    "`built_to_fail` at rank 23-24, a wide margin (gap ~0.33-0.36), not a near-miss tie. "
    "Same underlying mechanism as before -- `built_to_fail`'s sharply-concentrated vector "
    "systematically outscores flatter rivals via the WCS formula's quadratic-denominator "
    "effect, the identical mechanism this tracker's rank-3/`the_uninitiated` row already "
    "proved -- not a new problem, just a more precise measurement of an already-diagnosed "
    "one. Full detail: `tools/_scdwcs_paper_tiger_rank23_diagnostic.py` (untracked scratch). |"
)


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
