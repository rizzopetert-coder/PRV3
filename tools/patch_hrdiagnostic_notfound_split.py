"""
Correction to patch_hrdiagnostic_chrome_restore.py's not-found design, found
by its own post-write verification (not assumed).

What went wrong: a chrome-carrying ROOT app/not-found.tsx is embedded in
every route's RSC payload -- the root layout's not-found boundary ships with
each page, including hr-dx.com/ and /diagnostic. The HTML text stayed clean
(NavBar etc. are client components, referenced by id, not rendered), but the
payload referenced NavBar/MobileMenu/ServiceSidebar, so hr-dx browsers
downloaded JS chunks containing every PRV3 service tier name and "Principal
Resolution". A root not-found cannot carry chrome without breaking the
airgap.

Fix -- three files, standard Next pattern for a route-group-specific 404:
  - app/not-found.tsx: chrome-free, brand-neutral. Still embedded everywhere,
    now harmlessly. Only reached directly by URLs no route matches at all,
    which (site)/[...missing] below now absorbs on principalresolution.com.
  - app/(site)/not-found.tsx: renders inside the (site) layout, so it gets
    the chrome from there. Catches notFound() from any (site) page (e.g. a
    bad /book/state/ slug).
  - app/(site)/[...missing]/page.tsx: catch-all that calls notFound(), so an
    unmatched principalresolution.com URL lands in (site)/not-found.tsx with
    chrome instead of the bare root one. Lowest-priority match -- every real
    route still wins. On hr-dx.com middleware.ts 404s unknown paths before
    Next's router runs, so this is never reached there. Adds one dynamic
    entry (/[...missing]) to the build's route table -- the only route-table
    change in this round, deliberate.
  - tools/sleuth/route_manifest.py: /[...missing] added to EXCLUDED_PREFIXES
    so sleuth's on-disk dynamic-route cross-check doesn't warn about it.

Usage:
    python tools/patch_hrdiagnostic_notfound_split.py --dry-run
    python tools/patch_hrdiagnostic_notfound_split.py --write
"""
import argparse
import pathlib
import sys

NEW_FILES = [
    (
        pathlib.Path('web/app/not-found.tsx'),
        '''import Link from "next/link";

/**
 * Root not-found -- deliberately chrome-free and brand-neutral. Next embeds
 * the root not-found tree in EVERY route's RSC payload, hr-dx.com's
 * /diagnostic included, so any client component referenced here (NavBar,
 * ServiceSidebar...) would ship its JS chunk -- and every PRV3 service name
 * in it -- to hr-dx browsers even though nothing renders. principal
 * resolution.com's 404s with chrome come from app/(site)/not-found.tsx,
 * fed by the app/(site)/[...missing] catch-all.
 */
export default function NotFound() {
  return (
    <main className="min-h-screen bg-paper px-6 py-10 md:px-10 md:py-14">
      <p className="text-sm text-gray-500 mb-4">
        This page could not be found.
      </p>
      <Link href="/" className="font-ui text-sm text-charcoal hover:underline">
        Back to the home page
      </Link>
    </main>
  );
}
''',
    ),
    (
        pathlib.Path('web/app/(site)/not-found.tsx'),
        '''import Link from "next/link";

/**
 * (site) not-found -- renders inside app/(site)/layout.tsx, so it carries
 * the PRV3 chrome from there. Catches notFound() from any (site) page, plus
 * every unmatched principalresolution.com URL via the [...missing]
 * catch-all beside it. Never reachable on hr-dx.com (middleware.ts 404s
 * every non-allowlisted path first), and unlike the root not-found it is
 * not embedded in /diagnostic's payload -- /diagnostic sits outside (site).
 */
export default function SiteNotFound() {
  return (
    <main className="min-h-screen bg-paper px-6 py-10 md:px-10 md:py-14">
      <p className="text-sm text-gray-500 mb-4">
        This page could not be found.
      </p>
      <Link href="/" className="font-ui text-sm text-charcoal hover:underline">
        Back to the home page
      </Link>
    </main>
  );
}
''',
    ),
    (
        pathlib.Path('web/app/(site)/[...missing]/page.tsx'),
        '''import { notFound } from "next/navigation";

/**
 * Catch-all for URLs no real route matches, so they render
 * app/(site)/not-found.tsx (with PRV3 chrome) instead of the chrome-free
 * root not-found. Lowest-priority match: every real route, static or
 * dynamic, still wins. hr-dx.com never reaches it -- middleware.ts answers
 * every non-allowlisted path with a bare 404 before Next's router runs.
 */
export default function MissingPage() {
  notFound();
}
''',
    ),
]

EDITS = [
    (
        pathlib.Path('tools/sleuth/route_manifest.py'),
        '    "/first-call/admin",\n)\n',
        '    "/first-call/admin",\n'
        '    # app/(site)/[...missing] -- 404 catch-all, calls notFound()\n'
        '    # unconditionally, never a real page.\n'
        '    "/[...missing]",\n'
        ')\n',
        'sleuth exclude catch-all',
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    for path, content in NEW_FILES:
        state = 'OVERWRITE' if path.exists() else 'NEW'
        print(f'=== {state} {path} ===\n{content}')

    edited = {}
    for path, old, new, label in EDITS:
        text = edited.get(path, path.read_text(encoding='utf-8'))
        count = text.count(old)
        if count != 1:
            print(f'ERROR: {path} :: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
            sys.exit(1)
        edited[path] = text.replace(old, new, 1)
        print(f'[{path} :: {label}]\nOLD:\n{old}\nNEW:\n{new}')

    if args.dry_run:
        print('DRY RUN -- all anchors found, all edits would apply cleanly. Nothing written.')
        return

    for path, content in NEW_FILES:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        print(f'WROTE: {path}')
    for path, text in edited.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
