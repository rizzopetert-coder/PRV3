"""
Fix: Vercel's native FastAPI framework preset (prv3-engine, now that the
legacy vercel.json builds array is gone) can't find api/engine.py's
FastAPI app via zero-config detection -- confirmed via a real failed
build's own error message this session:

    Error: No FastAPI entrypoint found in default locations, but found
    potential entrypoints:
      api/engine.py (variable: app)

    Add this to your pyproject.toml:
    [tool.vercel]
    entrypoint = "api.engine:app"

Creates pyproject.toml at the repo root -- confirmed correct location by
checking requirements.txt's own location (repo root), which
prv3-engine's Root Directory "." already resolves Python config from
correctly today. Confirmed no pyproject.toml exists anywhere in the repo
already (repo-wide find, this session) -- nothing to merge into, this is
a new file for a single, narrow purpose (Vercel's own entrypoint
declaration), not a general Python project config file.

Usage:
    python tools/patch_pyproject_fastapi_entrypoint.py --dry-run
    python tools/patch_pyproject_fastapi_entrypoint.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('pyproject.toml')

CONTENT = '''[tool.vercel]
entrypoint = "api.engine:app"
'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    if PATH.exists():
        print(f'ERROR: {PATH} already exists -- refusing to overwrite blindly.', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f'DRY RUN -- {PATH} does not exist yet, would create it with:\n')
        print(CONTENT)
    else:
        PATH.write_text(CONTENT, encoding='utf-8')
        print(f'WROTE: {PATH}')
        print(CONTENT)


if __name__ == '__main__':
    main()
