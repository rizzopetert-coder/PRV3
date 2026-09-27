"""
Retire requirements.txt (Pete, 2026-09-27). Dead file: Vercel's prv3-engine
build installs from pyproject.toml (build log: "Installing required
dependencies from pyproject.toml"), the one CI workflow pip-installs
anthropic directly, and no local script, launch config, or doc used it.

  1. requirements.txt deleted (git rm, done outside this script).
  2. MOB Section 15 file-registry row now describes pyproject.toml, keeping
     the S40/S44 history of the file it replaced.
  3. prompts/candidate-future-task-numpy-removal.md retargeted: the
     2026-09-19 finding is kept as written, with a dated note that the file
     to edit is now pyproject.toml.

Not edited, by protocol: prompts/session-handoff-v4.316.md (handoffs are
additive only, never overwritten) and the historical Section 16 mentions in
the MOB (point-in-time records).

Usage:
    python tools/patch_retire_requirements_txt.py --dry-run
    python tools/patch_retire_requirements_txt.py --write
"""
import argparse
import pathlib
import sys

MOB = pathlib.Path('tools/_mob.txt')
DOC = pathlib.Path('prompts/candidate-future-task-numpy-removal.md')
NL = '\r\n'

MOB_PREFIX = r'| \\\*\\\*requirements.txt\\\*\\\* |'
MOB_NEW = (r'| \\\*\\\*pyproject.toml\\\*\\\* | Python deps for the `prv3-engine` Vercel project '
           r'(`[project].dependencies`): fastapi, uvicorn, numpy, anthropic, plus `[tool.vercel] entrypoint = '
           r'"api.engine:app"`. ' "Vercel's" r' Python builder installs from it with its own uv. Created 2026-09-24 '
           r'(`060327a`, full `[project]` table `8289ac7`). Replaced requirements.txt (created S40, anthropic '
           r'added S44 because engine/output_synthesis.py needs it, its absence in S40 made synthesis always fall '
           r'back to the static dict), which was deleted 2026-09-27. |')

DOC_EDITS = [
    ('`requirements.txt` lists exactly four packages: `fastapi`, `uvicorn`, `numpy`, `anthropic`.\n',
     '`requirements.txt` lists exactly four packages: `fastapi`, `uvicorn`, `numpy`, `anthropic`.\n'
     '\n'
     '> **Retargeted 2026-09-27:** the engine\'s dependencies now live in `pyproject.toml`\'s\n'
     '> `[project].dependencies` (the same four packages), which is what Vercel\'s `prv3-engine` build\n'
     '> installs from. `requirements.txt` was deleted 2026-09-27. If this task is picked up, the file to\n'
     '> edit is `pyproject.toml`, not `requirements.txt`.\n',
     'retarget note'),
    ('`numpy` is the single heaviest of the four `requirements.txt` packages by a wide margin\n',
     '`numpy` is the single heaviest of the four engine dependencies (then `requirements.txt`, now\n'
     '`pyproject.toml`) by a wide margin\n',
     'heaviest-package line'),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    mob = MOB.read_bytes().decode('utf-8')
    key = NL + MOB_PREFIX
    if mob.count(key) != 1:
        print(f'ERROR: Section 15 row found {mob.count(key)} times.', file=sys.stderr)
        sys.exit(1)
    start = mob.index(key) + len(NL)
    end = mob.index(NL, start)
    print('BEFORE:', mob[start:end])
    mob = mob[:start] + MOB_NEW + mob[end:]
    print('AFTER: ', MOB_NEW)
    print('[MOB :: Section 15 row] OK')

    doc = DOC.read_text(encoding='utf-8')
    for old, new, label in DOC_EDITS:
        if doc.count(old) != 1:
            print(f'ERROR: doc {label} anchor found {doc.count(old)} times.', file=sys.stderr)
            sys.exit(1)
        doc = doc.replace(old, new, 1)
        print(f'[{DOC} :: {label}] OK')

    for name, text in (('MOB row', MOB_NEW), ('doc', ''.join(n for _, n, _ in DOC_EDITS))):
        print(f'semicolons in new {name} text: {text.count(";")}')

    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    MOB.write_text(mob, encoding='utf-8', newline='')
    DOC.write_text(doc, encoding='utf-8')
    print(f'WROTE: {MOB}, {DOC}')


if __name__ == '__main__':
    main()
