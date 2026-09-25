"""
Phase 3 -- the bridge. Adds the 8-route engine proxy to web/next.config.ts's
rewrites(), alongside the existing /services rewrite (not removed or
reordered). Project A (this app, Root Directory "web") no longer has a
vercel.json in scope -- this rewrite is now the only mechanism that routes
/api/{engine,accumulate,checkpoint,complete,condensed-complete,
question-copy,narrative-prompt,narrative-process} to Project B (the
separate Python engine deployment), via ENGINE_BASE_URL.

Pattern confirmed net-new, no collision: ENGINE_BASE_URL does not exist
anywhere in Project A's current env vars (checked live via `vercel env ls`
this session -- only ENGINE_URL, NEXT_PUBLIC_ENGINE_URL, ENGINE_SECRET,
ANTHROPIC_API_KEY, UPSTASH_REDIS_REST_URL/TOKEN exist today). ENGINE_URL
itself is untouched -- it's a different, existing contract scoped only to
invokeEngine()'s own internal fetch, not this Next.js-level rewrite.

Usage:
    python tools/patch_nextconfig_engine_bridge.py --dry-run
    python tools/patch_nextconfig_engine_bridge.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/next.config.ts')

OLD = '''const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/services", destination: "/about/services" },
    ];
  },
};'''

NEW = '''const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/services", destination: "/about/services" },
      // Phase 3 (multi-project migration) -- proxies the 8 Python engine
      // routes to Project B (separate Vercel project, api/engine.py's
      // FastAPI app), since this project's Root Directory is now "web"
      // and no longer has any vercel.json routing in scope. ENGINE_BASE_URL
      // is Project B's own deployment URL (auto-generated for now, the
      // engine.principalresolution.com subdomain comes later per the
      // phased plan -- not wired yet, deliberately, to avoid stacking two
      // domain changes at once).
      {
        source: "/api/:path(engine|accumulate|checkpoint|complete|condensed-complete|question-copy|narrative-prompt|narrative-process)",
        destination: `${process.env.ENGINE_BASE_URL}/api/:path`,
      },
    ];
  },
};'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    count = content.count(OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found, edit would apply cleanly. Nothing written.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')


if __name__ == '__main__':
    main()
