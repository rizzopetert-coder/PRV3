"""
Two loose ends (Pete, 2026-09-27):
  1. CLAUDE.md Engine Rules: states.py line said "57 states". The registry
     holds 58 (counted directly), matching Key References ("58 (locked)").
     Only that line. The Key References rows "171 profiles across 57 states"
     and "Shannon Entropy max (57 states)" are historical metric labels, left
     as they are.
  2. MOB 13b: the untracked uv.lock note is closed in place. Pete confirmed
     deletion: untracked (Vercel never saw it), Vercel's own uv installs from
     pyproject.toml, no local uv, no references. The file itself is deleted
     outside this script (it is untracked, so git has nothing to record).

Usage:
    python tools/patch_state_count_and_uvlock_close.py --dry-run
    python tools/patch_state_count_and_uvlock_close.py --write
"""
import argparse
import pathlib
import sys

NL = '\r\n'
CLAUDE = pathlib.Path('CLAUDE.md')
MOB = pathlib.Path('tools/_mob.txt')

CLAUDE_OLD = '- `engine/data/states.py` is the authoritative state registry — 57 states' + NL
CLAUDE_NEW = '- `engine/data/states.py` is the authoritative state registry, 58 states' + NL

MOB_PREFIX = '- Untracked `uv.lock` at the repo root (timestamped 2026-09-24 23:39)'
MOB_NEW = ('- CLOSED 2026-09-27 -- untracked `uv.lock` deleted (Pete-confirmed). Not load-bearing: never '
           'committed, so Vercel never saw it (its build log shows its own uv installing from `pyproject.toml`), '
           'uv is not installed locally, and nothing referenced it. Committing a lock file for pinned engine '
           'builds remains an option, not pursued.')


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    claude = CLAUDE.read_bytes().decode('utf-8')
    if claude.count(CLAUDE_OLD) != 1:
        print(f'ERROR: CLAUDE.md states line found {claude.count(CLAUDE_OLD)} times.', file=sys.stderr)
        sys.exit(1)
    claude = claude.replace(CLAUDE_OLD, CLAUDE_NEW, 1)
    print('[CLAUDE.md :: 57 -> 58 states] OK')

    mob = MOB.read_bytes().decode('utf-8')
    key = NL + MOB_PREFIX
    if mob.count(key) != 1:
        print(f'ERROR: MOB uv.lock line found {mob.count(key)} times.', file=sys.stderr)
        sys.exit(1)
    start = mob.index(key) + len(NL)
    end = mob.index(NL, start)
    mob = mob[:start] + MOB_NEW + mob[end:]
    print('[MOB :: 13b uv.lock note closed] OK')

    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    CLAUDE.write_text(claude, encoding='utf-8', newline='')
    MOB.write_text(mob, encoding='utf-8', newline='')
    print(f'WROTE: {CLAUDE}, {MOB}')


if __name__ == '__main__':
    main()
