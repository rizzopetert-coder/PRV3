"""
Route-group split follow-up (commit f855d0a) -- restores PRV3 site chrome in
the two places the split removed it from on principalresolution.com, without
putting any of it back on hr-dx.com.

1. principalresolution.com/diagnostic: app/diagnostic/ is a sibling of
   (site), so it lost NavBar/MobileMenu/ServiceSidebar. diagnostic/layout.tsx
   already resolves brand server-side (it is already dynamic), so it now
   wraps children in the chrome for principal_resolution only. hr_diagnostic
   gets children alone, exactly as before this patch. ServiceSidebar's own
   pathname check still picks its thin-strip variant on /diagnostic.

2. 404 pages: no app/not-found.tsx existed, so every 404 (unmatched URLs AND
   notFound() calls from (site) pages, e.g. a bad /book/state/ slug) fell
   through to Next's built-in not-found, rendered inside the root layout --
   which carried the chrome before the split and no longer does. New
   app/not-found.tsx renders the chrome itself. It stays static (no
   headers() read), so the route table is unchanged. hr-dx.com never
   reaches it: middleware.ts returns a bare, body-less 404 for every path
   outside its allowlist, and no allowlisted route calls notFound() --
   verified empirically after this patch, not assumed.

The three chrome components move into one shared wrapper,
components/SiteChrome.tsx, used by all three call sites ((site)/layout.tsx,
diagnostic/layout.tsx, not-found.tsx) so the composition can't drift.

Usage:
    python tools/patch_hrdiagnostic_chrome_restore.py --dry-run
    python tools/patch_hrdiagnostic_chrome_restore.py --write
"""
import argparse
import pathlib
import sys

NEW_FILES = [
    (
        pathlib.Path('web/components/SiteChrome.tsx'),
        '''import type { ReactNode } from "react";
import { NavBar } from "@/components/NavBar";
import { MobileMenu } from "@/components/MobileMenu";
import { ServiceSidebar } from "@/components/ServiceSidebar";

/**
 * PRV3 site chrome -- NavBar, MobileMenu, ServiceSidebar -- as one unit.
 * Rendered by app/(site)/layout.tsx, by app/diagnostic/layout.tsx for
 * principal_resolution only, and by app/not-found.tsx. Never rendered on
 * hr-dx.com: nothing on that brand's allowed surface reaches any of the
 * three call sites with chrome enabled.
 *
 * Fragment, no wrapper element, so the DOM under <body> matches the
 * pre-split root layout exactly.
 */
export function SiteChrome({ children }: { children: ReactNode }) {
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
          wiring itself, including its thin-strip variant on /diagnostic.
          See ServiceSidebar.tsx's own header comment. */}
      <ServiceSidebar>{children}</ServiceSidebar>
    </>
  );
}
''',
    ),
    (
        pathlib.Path('web/app/(site)/layout.tsx'),
        '''import { SiteChrome } from "@/components/SiteChrome";

/**
 * PRV3 site chrome scoped to the (site) route group. Moved out of the root
 * layout so app/diagnostic/ (a sibling of this group, not a child) only
 * gets it where its own layout opts in -- principal_resolution only, never
 * hr-dx.com. "(site)" is a route group, not a URL segment -- every route
 * under it keeps its exact existing path.
 */
export default function SiteLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <SiteChrome>{children}</SiteChrome>;
}
''',
    ),
    (
        pathlib.Path('web/app/not-found.tsx'),
        '''import Link from "next/link";
import { SiteChrome } from "@/components/SiteChrome";

/**
 * Root not-found -- catches unmatched URLs and notFound() calls from (site)
 * pages. Renders the PRV3 chrome itself because the root layout no longer
 * does (route-group split). Static, no headers() read: hr-dx.com never
 * reaches this page, since middleware.ts answers every path outside its
 * allowlist with a bare, body-less 404 before Next's router runs, and no
 * allowlisted hr-dx route calls notFound().
 */
export default function NotFound() {
  return (
    <SiteChrome>
      <main className="min-h-screen bg-paper px-6 py-10 md:px-10 md:py-14">
        <p className="text-sm text-gray-500 mb-4">
          This page could not be found.
        </p>
        <Link href="/" className="font-ui text-sm text-charcoal hover:underline">
          Back to the home page
        </Link>
      </main>
    </SiteChrome>
  );
}
''',
    ),
]

EDITS = [
    (
        pathlib.Path('web/app/diagnostic/layout.tsx'),
        'import { BrandProvider } from "@/components/BrandContext";\n',
        'import { BrandProvider } from "@/components/BrandContext";\n'
        'import { SiteChrome } from "@/components/SiteChrome";\n',
        'import SiteChrome',
    ),
    (
        pathlib.Path('web/app/diagnostic/layout.tsx'),
        '  const brand = await resolveRequestBrand();\n'
        '  return <BrandProvider brand={brand}>{children}</BrandProvider>;\n',
        '  const brand = await resolveRequestBrand();\n'
        '  // PRV3 chrome for principal_resolution only. app/diagnostic/ sits\n'
        '  // outside the (site) route group, so this is the only place it can\n'
        '  // come from here -- and hr_diagnostic must never receive it.\n'
        '  return (\n'
        '    <BrandProvider brand={brand}>\n'
        '      {brand === "principal_resolution" ? (\n'
        '        <SiteChrome>{children}</SiteChrome>\n'
        '      ) : (\n'
        '        children\n'
        '      )}\n'
        '    </BrandProvider>\n'
        '  );\n',
        'brand-conditional chrome',
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
    if pathlib.Path('web/app/not-found.tsx').exists():
        print('ERROR: web/app/not-found.tsx already exists.', file=sys.stderr)
        sys.exit(1)

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
        path.write_text(content, encoding='utf-8')
        print(f'WROTE: {path}')
    for path, text in edited.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
