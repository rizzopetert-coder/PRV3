"""
prv3-engine routing fix -- remove the `rewrites` block from the root
vercel.json (used only by the prv3-engine project; prv-3's Root Directory is
`web`, so this file is outside its build). Keeps `$schema` and
`functions.api/engine.py.maxDuration` unchanged.

Why (live evidence, 2026-09-26, branch engine dpl_EhcXcAB4DGF8feeSMosEhv56tr1y):
every engine route was rewritten to /api/engine.py, and the FastAPI app then
received the rewritten path -- POST /api/question-copy, /api/complete and
/api/engine.py all returned FastAPI's own 404 {"detail":"Not Found"}, logged
by the engine as `POST /api/engine.py 404`. Meanwhile GET /openapi.json (no
rewrite) reached the app at its real path and listed /api/engine,
/api/accumulate, ... -- prv3-engine's zero-config FastAPI routing already
serves the app at original paths, so the rewrites are what break it.

Main is unaffected: main's vercel.json is the legacy `builds`/`routes`
monolith config, and Production stays frozen per the approved plan.

Usage:
    python tools/patch_engine_vercel_json_drop_rewrites.py --dry-run
    python tools/patch_engine_vercel_json_drop_rewrites.py --write
"""
import argparse
import json
import pathlib
import sys

PATH = pathlib.Path('vercel.json')


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    original = PATH.read_text(encoding='utf-8')
    data = json.loads(original)
    if 'rewrites' not in data:
        print('ERROR: no rewrites block present -- already applied?', file=sys.stderr)
        sys.exit(1)
    if set(data) != {'$schema', 'rewrites', 'functions'}:
        print(f'ERROR: unexpected top-level keys {sorted(data)} -- refusing to guess.', file=sys.stderr)
        sys.exit(1)
    if data['functions'] != {'api/engine.py': {'maxDuration': 300}}:
        print(f'ERROR: functions block is not the expected one: {data["functions"]}', file=sys.stderr)
        sys.exit(1)

    removed = data.pop('rewrites')
    new_text = json.dumps(data, indent=2) + '\n'

    print(f'Removing {len(removed)} rewrites:')
    for r in removed:
        print(f'  {r["source"]} -> {r["destination"]}')
    print(f'\n=== NEW {PATH} ===\n{new_text}')

    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    PATH.write_text(new_text, encoding='utf-8')
    print(f'WROTE: {PATH}')


if __name__ == '__main__':
    main()
