"""
Rewrite the repo-root vercel.json to be Project B (Python engine)-only.

Project A (the Next.js app, Root Directory now "web") no longer needs
anything from this file -- its own routing bridge lives in
web/next.config.ts's rewrites() (Phase 3, separate patch). This file is
now exclusively Project B's config surface (Root Directory ".").

Changes from the old legacy config:
- Drops "builds" entirely -- Vercel's zero-config Python detection for
  api/engine.py already confirmed sufficient to reach engine/ (via its own
  sys.path bridge), verified empirically this session (repeated successful
  production invocations with no explicit builds/includeFiles directive).
- Keeps all 8 /api/* -> api/engine.py mappings, using modern `rewrites`
  syntax (source/destination) instead of the legacy `routes` (src/dest) --
  api/engine.py's FastAPI app defines internal routes for 7 of these paths
  that differ from the file's own default zero-config path (/api/engine),
  so explicit mapping is required for all 8, not optional.
- Drops the "/(.*) -> /web/$1" catch-all entirely -- Project B serves API
  routes only, no frontend content is relevant to it.
- Adds a `functions` block for api/engine.py: maxDuration 300 (matches the
  MOB's previously-verified Hobby+Fluid ceiling), no memory override
  (ride the platform default, already proven working), no includeFiles
  (confirmed unnecessary above).

Usage:
    python tools/patch_vercel_json_project_b_python_only.py --dry-run
    python tools/patch_vercel_json_project_b_python_only.py --write
"""
import argparse
import json
import pathlib
import sys

PATH = pathlib.Path('vercel.json')

OLD_CONTENT = '''{
  "builds": [
    {
      "src": "web/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "api/engine.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/engine",
      "dest": "/api/engine.py"
    },
    {
      "src": "/api/accumulate",
      "dest": "/api/engine.py"
    },
    {
      "src": "/api/checkpoint",
      "dest": "/api/engine.py"
    },
    {
      "src": "/api/complete",
      "dest": "/api/engine.py"
    },
    {
      "src": "/api/question-copy",
      "dest": "/api/engine.py"
    },
    {
      "src": "/api/condensed-complete",
      "dest": "/api/engine.py"
    },
    {
      "src": "/api/narrative-prompt",
      "dest": "/api/engine.py"
    },
    {
      "src": "/api/narrative-process",
      "dest": "/api/engine.py"
    },
    {
      "src": "/(.*)",
      "dest": "/web/$1"
    }
  ]
}
'''

NEW_DATA = {
    "$schema": "https://openapi.vercel.sh/vercel.json",
    "rewrites": [
        {"source": "/api/engine", "destination": "/api/engine.py"},
        {"source": "/api/accumulate", "destination": "/api/engine.py"},
        {"source": "/api/checkpoint", "destination": "/api/engine.py"},
        {"source": "/api/complete", "destination": "/api/engine.py"},
        {"source": "/api/question-copy", "destination": "/api/engine.py"},
        {"source": "/api/condensed-complete", "destination": "/api/engine.py"},
        {"source": "/api/narrative-prompt", "destination": "/api/engine.py"},
        {"source": "/api/narrative-process", "destination": "/api/engine.py"},
    ],
    "functions": {
        "api/engine.py": {
            "maxDuration": 300
        }
    },
}


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    current = PATH.read_text(encoding='utf-8')
    if current != OLD_CONTENT:
        print('ERROR: vercel.json does not match the expected pre-migration content byte-for-byte.', file=sys.stderr)
        print('Refusing to overwrite -- confirm the file has not changed since this script was written.', file=sys.stderr)
        sys.exit(1)

    new_content = json.dumps(NEW_DATA, indent=2) + '\n'

    if args.dry_run:
        print('DRY RUN -- old content matches expected byte-for-byte. New content would be:\n')
        print(new_content)
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(new_content)


if __name__ == '__main__':
    main()
