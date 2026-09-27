"""
MOB Section 16: short addendum after the v4.327 closeout (Pete, 2026-09-27),
same style as the v4.326 addendum, closing the log gap for the three commits
that landed after that closeout. Log entry only, MOB version unchanged.

Usage:
    python tools/patch_mob_addendum_v4327.py --dry-run
    python tools/patch_mob_addendum_v4327.py --write
"""
import argparse
import pathlib
import sys

MOB = pathlib.Path('tools/_mob.txt')
NL = '\r\n'
END_ANCHOR = 'MOB v4.327.'
ADDENDUM = (
    '**Addendum (2026-09-27, same session, post-closeout):** three loose ends closed. `bd89664`: CLAUDE.md\'s '
    'Engine Rules line calling `engine/data/questions.py` "intentionally empty" replaced with current fact '
    '(141 entries). The line dated from the empty scaffold (`c79179b`, MOB v1.4) and had been stale since '
    'Session 9, not since the 2026-09-24 TC-* work. `0e1d9fb`: the Engine Rules state count corrected from 57 '
    'to 58 (registry counted directly), and the untracked `uv.lock` deleted with its 13b note closed in place. '
    '`210936a`: `requirements.txt` retired, since Vercel\'s `prv3-engine` build installs from `pyproject.toml`, '
    'with the Section 15 row and the numpy-removal task doc retargeted to `pyproject.toml`. Production build of '
    '`210936a` confirmed installing from `pyproject.toml`, and a tagged Production session returned '
    '`is_fallback: false`. MOB version unchanged (v4.327).'
)


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    mob = MOB.read_bytes().decode('utf-8')
    if not mob.rstrip(NL).endswith(END_ANCHOR):
        print('ERROR: MOB does not end with the v4.327 closeout line.', file=sys.stderr)
        sys.exit(1)
    if 'three loose ends closed. `bd89664`' in mob:
        print('ERROR: addendum already present.', file=sys.stderr)
        sys.exit(1)
    new = mob.rstrip(NL) + NL + NL + ADDENDUM + NL
    print('[MOB :: v4.327 addendum appended] OK')
    print(ADDENDUM)
    print('semicolons:', ADDENDUM.count(';'), '| lines before/after:', len(mob.split(NL)), len(new.split(NL)))
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    MOB.write_text(new, encoding='utf-8', newline='')
    print(f'WROTE: {MOB}')


if __name__ == '__main__':
    main()
