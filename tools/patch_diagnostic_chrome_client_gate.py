"""
Round-two chrome work, corrected before commit: principalresolution.com's
/diagnostic gets the PRV3 chrome back WITHOUT the chrome's JS chunk reaching
hr-dx.com.

The uncommitted round-two version rendered chrome from app/diagnostic/
layout.tsx via a STATIC `import { SiteChrome }` in that server layout. The
brand-conditional render was correct, but Next bundles by import graph, so
the chrome chunk (all four PR tier names, "Principal Resolution", nav
labels) loaded on hr-dx /diagnostic too -- confirmed by chunk scan at the
time. next/dynamic from the server layout did not split it: this Next
version's own docs (node_modules/next/dist/docs/01-app/02-guides/
lazy-loading.md) say code splitting is not supported when a Server
Component dynamically imports a Client Component.

Fix: the layout keeps resolving brand server-side, but renders a small
CLIENT component, DiagnosticChrome, which reads brand from BrandContext and
loads SiteChrome via next/dynamic. From a client component that is a real
split -- the same mechanism verified by chunk scan for item E/G
(0643e8e) -- so the chunk is only fetched when principal_resolution renders.

Usage:
    python tools/patch_diagnostic_chrome_client_gate.py --dry-run
    python tools/patch_diagnostic_chrome_client_gate.py --write
"""
import argparse
import pathlib
import sys

NEW_FILE = pathlib.Path('web/components/DiagnosticChrome.tsx')
NEW_CONTENT = '''"use client";

import type { ReactNode } from "react";
import dynamic from "next/dynamic";
import { useBrand } from "@/components/BrandContext";

// PRV3 site chrome for /diagnostic on principal_resolution only.
// Code-split via next/dynamic from THIS client component: a static import
// (or next/dynamic from the server layout, which Next does not split) puts
// the chrome chunk -- PR service tier names, nav labels -- into what
// hr-dx.com's /diagnostic downloads even though it never renders there.
const SiteChrome = dynamic(() =>
  import("@/components/SiteChrome").then((m) => m.SiteChrome),
);

export default function DiagnosticChrome({ children }: { children: ReactNode }) {
  const brand = useBrand();
  if (brand === "principal_resolution") {
    return <SiteChrome>{children}</SiteChrome>;
  }
  return <>{children}</>;
}
'''

LAYOUT = pathlib.Path('web/app/diagnostic/layout.tsx')
EDITS = [
    ('import { SiteChrome } from "@/components/SiteChrome";\n',
     'import DiagnosticChrome from "@/components/DiagnosticChrome";\n',
     'import'),
    ('  // PRV3 chrome for principal_resolution only. app/diagnostic/ sits\n'
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
     '  // PRV3 chrome for principal_resolution only. app/diagnostic/ sits\n'
     '  // outside the (site) route group, so this is the only place it can\n'
     '  // come from here -- and hr_diagnostic must never receive it, not even\n'
     '  // as a downloaded chunk. DiagnosticChrome (client) makes the brand\n'
     '  // decision and code-splits the chrome; see its header comment.\n'
     '  return (\n'
     '    <BrandProvider brand={brand}>\n'
     '      <DiagnosticChrome>{children}</DiagnosticChrome>\n'
     '    </BrandProvider>\n'
     '  );\n',
     'render via client gate'),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    if NEW_FILE.exists():
        print(f'ERROR: {NEW_FILE} already exists.', file=sys.stderr)
        sys.exit(1)
    text = LAYOUT.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        if text.count(old) != 1:
            print(f'ERROR: {LAYOUT} :: {label} anchor found {text.count(old)} times.', file=sys.stderr)
            sys.exit(1)
        text = text.replace(old, new, 1)
        print(f'[{LAYOUT} :: {label}] OK')
    if 'from "@/components/SiteChrome"' in text:
        print('ERROR: layout still statically imports SiteChrome.', file=sys.stderr)
        sys.exit(1)
    print(f'=== NEW {NEW_FILE} ===\n{NEW_CONTENT}')

    if args.dry_run:
        print('DRY RUN -- anchors found, no static SiteChrome import left in layout. Nothing written.')
        return
    NEW_FILE.write_text(NEW_CONTENT, encoding='utf-8')
    LAYOUT.write_text(text, encoding='utf-8')
    print(f'WROTE: {NEW_FILE}\nWROTE (edited): {LAYOUT}')


if __name__ == '__main__':
    main()
