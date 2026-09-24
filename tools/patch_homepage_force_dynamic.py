"""
Fix: hr-dx.com's bare root URL ("/") shows the wrong (principal_resolution)
homepage instead of being rewritten to /diagnostic.

Root cause, confirmed directly this session: "/" is a fully static
prerendered page (Cache-Control: s-maxage=31536000 per Next.js's
cdn-caching.md doc). Vercel's CDN caches it ONCE at the deployment level,
not per-domain -- confirmed via byte-identical ETag between
principalresolution.com/ and hr-dx.com/ -- and serves that cached HTML to
every domain attached to the deployment, bypassing middleware.ts's
per-Host rewrite decision entirely on a cache hit. Next.js's own docs
(cdn-caching.md) state middleware should run before the CDN cache and
recommend "configure the cache layer to bypass caching for routes that
depend on proxy.js [middleware] decisions" -- Vercel's CDN config isn't
something this session can touch directly, so the fix instead makes
Next.js itself mark "/" non-cacheable (force-dynamic), guaranteeing
middleware re-evaluates fresh on every request to this one route.

export const dynamic = "force-dynamic" does NOT work here -- confirmed
empirically (built with it added, route stayed "○ /" static, no error or
warning). Route Segment Config exports are a Server Component mechanism;
web/app/page.tsx is `"use client"`, so the export is silently ignored.

Fix: split page.tsx into a thin Server Component wrapper (this file,
forces dynamic rendering by calling headers(), same mechanism already
proven in web/app/diagnostic/layout.tsx's resolveRequestBrand()) and a
new Client Component (web/components/home/HomeClient.tsx, the entire
existing page content, byte-for-byte, unchanged) that it renders. Scoped
to exactly this one leaf route -- page.tsx has no descendants, so this
does not cascade to any other route the way the earlier root-layout
headers() mistake did (that forced all 36 routes dynamic; this forces
exactly 1).

Usage:
    python tools/patch_homepage_force_dynamic.py --dry-run
    python tools/patch_homepage_force_dynamic.py --write
"""
import argparse
import pathlib
import sys

PAGE_PATH = pathlib.Path('web/app/page.tsx')
HOME_CLIENT_PATH = pathlib.Path('web/components/home/HomeClient.tsx')

NEW_PAGE_CONTENT = '''import { headers } from "next/headers";
import HomeClient from "@/components/home/HomeClient";

// Forces "/" to be dynamically rendered per-request (Cache-Control:
// private, no-cache, no-store -- never CDN-cached) so middleware.ts's
// Host-based rewrite (hr_diagnostic -> /diagnostic) is re-evaluated on
// every request. Without this, Vercel's CDN caches "/" once at the
// deployment level and serves the identical cached HTML to every domain
// attached to the deployment, bypassing middleware's per-Host decision
// entirely -- confirmed directly this session (byte-identical ETag
// between hr-dx.com/ and principalresolution.com/). headers()'s return
// value is unused -- calling it is what triggers dynamic rendering, the
// same mechanism already used in web/app/diagnostic/layout.tsx's
// resolveRequestBrand(). Scoped to this one leaf route only -- page.tsx
// has no descendants, so this does not cascade to any other route.
export default async function Home() {
  await headers();
  return <HomeClient />;
}
'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    original = PAGE_PATH.read_text(encoding='utf-8')

    marker = 'export default function Home() {'
    if original.count(marker) != 1:
        print(f'ERROR: expected exactly 1 occurrence of "{marker}" in {PAGE_PATH}, found {original.count(marker)}.', file=sys.stderr)
        sys.exit(1)

    home_client_content = original.replace(marker, 'export default function HomeClient() {', 1)

    print(f'[{HOME_CLIENT_PATH}] -- full existing page.tsx content, default export renamed Home -> HomeClient')
    print(f'[{PAGE_PATH}] -- replaced with thin Server Component wrapper (headers() + HomeClient)')

    if args.dry_run:
        print('\nDRY RUN -- anchor found, both writes would apply cleanly. Nothing written.')
        print(f'HomeClient.tsx would be {len(home_client_content)} chars.')
        print(f'page.tsx would be {len(NEW_PAGE_CONTENT)} chars (was {len(original)}).')
    else:
        HOME_CLIENT_PATH.write_text(home_client_content, encoding='utf-8')
        PAGE_PATH.write_text(NEW_PAGE_CONTENT, encoding='utf-8')
        print('WROTE both files.')


if __name__ == '__main__':
    main()
