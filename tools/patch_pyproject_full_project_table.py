"""
Follow-up fix, same round: adding pyproject.toml (prior commit) fixed the
FastAPI entrypoint detection gap, but exposed a second, real issue --
its mere PRESENCE switches Vercel's Python builder from
`pip install -r requirements.txt` to `uv lock`-based dependency
resolution, which requires a full PEP 621 [project] table. Confirmed via
a real failed build's own error:

    Error: Failed to run "uv lock ...": error: No `project` table found
    in: /vercel/path0/pyproject.toml

Confirmed the correct, documented pattern via Vercel's own docs
(functions/runtimes/python): a [project] table with name, version,
requires-python, and dependencies listed inline -- not a reference to
requirements.txt, which becomes vestigial for Vercel's own build once
pyproject.toml exists at all (kept in the repo regardless -- may still
serve a local dev workflow, not removed here without being asked).

Dependencies mirrored exactly from requirements.txt, unpinned, matching
what already installed cleanly in this session's own venv verification
(fastapi, uvicorn, numpy, anthropic) -- not introducing new version
constraints unprompted.

Usage:
    python tools/patch_pyproject_full_project_table.py --dry-run
    python tools/patch_pyproject_full_project_table.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('pyproject.toml')

OLD_CONTENT = '''[tool.vercel]
entrypoint = "api.engine:app"
'''

NEW_CONTENT = '''[project]
name = "prv3-engine"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi",
    "uvicorn",
    "numpy",
    "anthropic",
]

[tool.vercel]
entrypoint = "api.engine:app"
'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    current = PATH.read_text(encoding='utf-8')
    if current != OLD_CONTENT:
        print('ERROR: pyproject.toml does not match the expected prior content byte-for-byte.', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print('DRY RUN -- old content matches expected byte-for-byte. New content would be:\n')
        print(NEW_CONTENT)
    else:
        PATH.write_text(NEW_CONTENT, encoding='utf-8')
        print('WRITE complete.')
        print(NEW_CONTENT)


if __name__ == '__main__':
    main()
