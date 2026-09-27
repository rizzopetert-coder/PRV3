"""
MOB 13b: log the fast_forward driver's answer-steering gap as its own open
item (Pete, 2026-09-27). Separate scope from the closeout -- driver tuning,
not a defect in the hr-dx pathway logic (which vitest and
tools/test_hr_diagnostic_brand.py already pin).

Inserted as a new "Open, not sequenced" bullet directly after the existing
`tools/diagnostic_fast_forward.py` bullet. No other 13b line is touched --
the stale bullets closed this session are left for the next closeout.
MOB is CRLF, so bytes are read and the insert uses CRLF.

Usage:
    python tools/patch_mob_13b_driver_steering.py --dry-run
    python tools/patch_mob_13b_driver_steering.py --write
"""
import argparse
import pathlib
import sys

MOB = pathlib.Path('tools/_mob.txt')
ANCHOR_PREFIX = '- `tools/diagnostic_fast_forward.py` -- rework-or-retire still undecided'
NEW_BULLET = (
    '- `tools/diagnostic_fast_forward.py` answer-steering is too weak to reach most hr-dx pathways live '
    '(found 2026-09-27, own item, not closeout scope). Across 10 tagged Production sessions on hr-dx.com '
    'targeting `the_undefined_role`, `the_unformed_leader`, `leadership_deafness`, `the_overloaded_manager` '
    'and `the_uninitiated` at Entrenched and Endemic, every run landed on one of three states: `built_to_fail` '
    '(Roadmap + Intervention, hr_pathway urgent) or `the_unsolved_problem`/`the_dormant_talent` below the '
    'routing threshold (no pathway, generic drawer). Target severity missed on every run (all Emerging). '
    'So the structure, capability and leadership drawer pathways, and the plain "HR Consulting" Executive '
    'Advisory AI context, are verified by tests only, not live. The pathway logic itself is not in question '
    '(vitest pins routing to pathway, tools/test_hr_diagnostic_brand.py pins the context strings). Next step, '
    'if wanted: tune the driver\'s answer selection per target state so a live session can reach each family.'
)


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    mob = MOB.read_bytes().decode('utf-8')
    if mob.count(ANCHOR_PREFIX) != 1:
        print(f'ERROR: anchor found {mob.count(ANCHOR_PREFIX)} times.', file=sys.stderr)
        sys.exit(1)
    if 'answer-steering is too weak' in mob:
        print('ERROR: item already present.', file=sys.stderr)
        sys.exit(1)
    start = mob.index(ANCHOR_PREFIX)
    end = mob.index('\r\n', start)
    mob = mob[:end] + '\r\n' + NEW_BULLET + mob[end:]
    print('[MOB :: 13b driver answer-steering item] OK')
    print('Inserted after:', ANCHOR_PREFIX)
    print('New bullet:', NEW_BULLET)
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    MOB.write_text(mob, encoding='utf-8', newline='')
    print(f'WROTE: {MOB}')


if __name__ == '__main__':
    main()
