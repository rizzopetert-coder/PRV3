"""
hr_diagnostic chrome audit, items A-D -- route-group split (Gemini-reviewed,
Pete-confirmed). NavBar/MobileMenu/ServiceSidebar move out of the root
layout into app/(site)/layout.tsx, and every PRV3 route folder moves into
(site)/ with it. app/diagnostic/ stays where it is, sibling to (site), so
it never receives the PRV3 chrome at all -- not hidden, not rendered.

Why a route group rather than a brand check inside each component: the
root layout sits ABOVE app/diagnostic/layout.tsx's BrandProvider, so
useBrand() there always returns the default, and reading headers() in the
root layout flips every route Static -> Dynamic (already tried and
rejected, see diagnostic/layout.tsx's own comment). Route groups change no
URLs -- "(site)" is not a path segment.

Move list, confirmed against the live tree (ls web/app), not the earlier
report: about, ask, book, engage, executive-advisory, first-call,
people-tactics-and-strategy, share, training-and-development (the nine in
the brief), PLUS two the brief's list omitted, both of which currently
render inside the chrome and would silently lose it if left at root:
  - page.tsx (the homepage, "/") -- never rendered on hr-dx, where
    middleware rewrites "/" to /diagnostic
  - dev/ (dev-only fixture/preview pages)
Stays at root: diagnostic/ (explicit instruction), api/ (route handlers,
no layout involvement), layout.tsx, globals.css, favicon.ico.

Only relative import in the moved set: first-call/admin/page.tsx ->
./AdminLoginForm, which moves in the same folder. Everything else uses @/.

Root layout keeps exactly what every route needs regardless of group:
<html>/<body>, the font variables, globals.css, the pre-paint theme
script, and the default metadata (diagnostic/layout.tsx's
generateMetadata already overrides it on hr_diagnostic).

Path-dependent tooling fixed in the same pass:
  - tools/sleuth/route_manifest.py: on-disk dynamic-route scan now drops
    "(group)" segments, which Next strips from the URL. Without this,
    "/(site)/share/[id]" would never match the manifest's "/share/[id]".
  - tools/diag_book_toc_glossary_intersection.py: hard-coded
    web/app/book/toc/page.tsx path.

Usage:
    python tools/patch_hrdiagnostic_site_route_group.py --dry-run
    python tools/patch_hrdiagnostic_site_route_group.py --write
"""
import argparse
import pathlib
import subprocess
import sys

APP = pathlib.Path('web/app')
SITE = APP / '(site)'

MOVES = [
    'about',
    'ask',
    'book',
    'dev',
    'engage',
    'executive-advisory',
    'first-call',
    'people-tactics-and-strategy',
    'share',
    'training-and-development',
    'page.tsx',
]

EXPECTED_ROOT_REMAINDER = {'api', 'diagnostic', 'layout.tsx', 'globals.css', 'favicon.ico'}

SITE_LAYOUT_PATH = SITE / 'layout.tsx'
SITE_LAYOUT_CONTENT = '''import { NavBar } from "@/components/NavBar";
import { MobileMenu } from "@/components/MobileMenu";
import { ServiceSidebar } from "@/components/ServiceSidebar";

/**
 * PRV3 site chrome -- NavBar, MobileMenu, ServiceSidebar -- scoped to the
 * (site) route group only. Moved out of the root layout so app/diagnostic/
 * (a sibling of this group, not a child) never receives it: on hr-dx.com
 * none of this markup is sent at all, not rendered-then-hidden. "(site)"
 * is a route group, not a URL segment -- every route under it keeps its
 * exact existing path.
 *
 * Structure matches the previous root-layout <body> contents exactly
 * (fragment, no wrapper element), so the DOM under <body> is unchanged for
 * every route in this group.
 */
export default function SiteLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <NavBar />
      {/* Homepage restructure (2026-08-29) -- mounted as a sibling to
          NavBar, not inside it. NavBar.tsx is explicitly out of scope
          (Pete's instruction, 2026-08-29); MobileMenu is fully
          self-contained (own fixed trigger + overlay), so this is the
          only wiring point needed. */}
      <MobileMenu />
      {/* Persistent service sidebar -- ServiceSidebar owns the flex
          wiring itself. See ServiceSidebar.tsx's own header comment. */}
      <ServiceSidebar>{children}</ServiceSidebar>
    </>
  );
}
'''

ROOT_LAYOUT_PATH = APP / 'layout.tsx'
ROOT_EDITS = [
    (
        'import "./globals.css";\n'
        'import { NavBar } from "@/components/NavBar";\n'
        'import { MobileMenu } from "@/components/MobileMenu";\n'
        'import { ServiceSidebar } from "@/components/ServiceSidebar";\n',
        'import "./globals.css";\n',
        'drop chrome imports',
    ),
    (
        '          localStorage before React hydrates. ThemeSwitcher (OD-07) is\n'
        '          mounted in NavBar.tsx, sitewide global chrome as of this pass --\n'
        '          no longer dormant. suppressHydrationWarning above is required\n',
        '          localStorage before React hydrates. ThemeSwitcher (OD-07) is\n'
        '          mounted in NavBar.tsx, which now lives in app/(site)/layout.tsx\n'
        '          (not on /diagnostic) -- this script stays here so a stored\n'
        '          theme still applies on every route. suppressHydrationWarning above is required\n',
        'theme script comment',
    ),
    (
        '      <body className="min-h-full flex flex-col">\n'
        '        <NavBar />\n'
        '        {/* Homepage restructure (this session) -- mounted as a sibling to\n'
        '            NavBar, not inside it. NavBar.tsx is explicitly out of scope\n'
        '            (Pete\'s instruction, 2026-08-29); MobileMenu is fully\n'
        '            self-contained (own fixed trigger + overlay), so this is the\n'
        '            only wiring point needed. */}\n'
        '        <MobileMenu />\n'
        '        {/* Persistent service sidebar (this session) -- ServiceSidebar owns\n'
        '            the flex wiring itself (row w/ right column normally, column\n'
        '            w/ a thin top strip on /diagnostic) since the two modes need\n'
        '            genuinely different structure, not just a different sidebar\n'
        '            child. See ServiceSidebar.tsx\'s own header comment, including\n'
        '            why the /diagnostic trigger is in-flow rather than `fixed`. */}\n'
        '        <ServiceSidebar>{children}</ServiceSidebar>\n'
        '      </body>\n',
        '      <body className="min-h-full flex flex-col">\n'
        '        {/* Minimal shell only. PRV3 site chrome (NavBar, MobileMenu,\n'
        '            ServiceSidebar) lives in app/(site)/layout.tsx so\n'
        '            app/diagnostic/ -- a sibling of (site), never a child --\n'
        '            never receives it. That is what keeps hr-dx.com free of\n'
        '            PRV3 branding without making this layout read headers()\n'
        '            (which would flip every route Static -> Dynamic). */}\n'
        '        {children}\n'
        '      </body>\n',
        'body -> children only',
    ),
]

TOOL_EDITS = [
    (
        pathlib.Path('tools/sleuth/route_manifest.py'),
        '        rel = page.relative_to(APP_DIR).parent\n'
        '        parts = [p for p in rel.parts if p != "."]\n',
        '        rel = page.relative_to(APP_DIR).parent\n'
        '        # "(group)" folders are Next route groups -- stripped from the\n'
        '        # URL, so dropped here too or "/(site)/share/[id]" would never\n'
        '        # match the manifest\'s "/share/[id]".\n'
        '        parts = [p for p in rel.parts\n'
        '                 if p != "." and not (p.startswith("(") and p.endswith(")"))]\n',
        'sleuth route-group segments',
    ),
    (
        pathlib.Path('tools/diag_book_toc_glossary_intersection.py'),
        '    path = REPO_ROOT / "web" / "app" / "book" / "toc" / "page.tsx"\n',
        '    path = REPO_ROOT / "web" / "app" / "(site)" / "book" / "toc" / "page.tsx"\n',
        'book/toc path',
    ),
    (
        pathlib.Path('tools/diag_book_toc_glossary_intersection.py'),
        '  7. web/app/book/toc/page.tsx ',
        '  7. web/app/(site)/book/toc/page.tsx ',
        'book/toc docstring path',
    ),
]


def apply_edits(path: pathlib.Path, text: str, edits) -> str:
    for old, new, label in edits:
        count = text.count(old)
        if count != 1:
            print(f'ERROR: {path} :: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
            sys.exit(1)
        text = text.replace(old, new, 1)
        print(f'[{path} :: {label}]')
        print(f'OLD:\n{old}')
        print(f'NEW:\n{new}')
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    if SITE.exists():
        print(f'ERROR: {SITE} already exists.', file=sys.stderr)
        sys.exit(1)

    live = {p.name for p in APP.iterdir()}
    missing = [m for m in MOVES if m not in live]
    if missing:
        print(f'ERROR: expected in web/app but missing: {missing}', file=sys.stderr)
        sys.exit(1)
    remainder = live - set(MOVES)
    if remainder != EXPECTED_ROOT_REMAINDER:
        print(f'ERROR: unaccounted entries at web/app root: {sorted(remainder ^ EXPECTED_ROOT_REMAINDER)}', file=sys.stderr)
        sys.exit(1)

    print('=== MOVES (git mv) ===')
    for m in MOVES:
        print(f'  web/app/{m} -> web/app/(site)/{m}')
    print(f'  stays at root: {sorted(remainder)}\n')

    print(f'=== NEW FILE {SITE_LAYOUT_PATH} ===\n{SITE_LAYOUT_CONTENT}')

    print('=== EDITS ===')
    root_new = apply_edits(ROOT_LAYOUT_PATH, ROOT_LAYOUT_PATH.read_text(encoding='utf-8'), ROOT_EDITS)
    tool_texts = {}
    for path, old, new, label in TOOL_EDITS:
        base = tool_texts.get(path, path.read_text(encoding='utf-8'))
        tool_texts[path] = apply_edits(path, base, [(old, new, label)])

    if args.dry_run:
        print('DRY RUN -- tree matches expectations, all anchors found. Nothing moved or written.')
        return

    SITE.mkdir()
    for m in MOVES:
        subprocess.run(['git', 'mv', str(APP / m), str(SITE / m)], check=True)
        print(f'MOVED: web/app/{m}')
    SITE_LAYOUT_PATH.write_text(SITE_LAYOUT_CONTENT, encoding='utf-8')
    print(f'WROTE: {SITE_LAYOUT_PATH}')
    ROOT_LAYOUT_PATH.write_text(root_new, encoding='utf-8')
    print(f'WROTE (edited): {ROOT_LAYOUT_PATH}')
    for path, text in tool_texts.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
