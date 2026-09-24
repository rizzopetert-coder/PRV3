"""
HRdiagnostic.com hostname variant -- Steps 1-3 (hostname detection, layout
metadata, branding fixes). Step 4 (TC-* question integration) is NOT
included here -- tactical-compliance-questions.json does not exist
anywhere in the repo (confirmed via repo-wide search before writing this
script), so there is no source content to add. See the accompanying
report for the wiring design, ready once the file is supplied.

Architecture, and why:

- web/lib/brand.ts: single source of truth for hostname -> brand
  resolution. Both middleware.ts and any future Route Handler that needs
  brand at request time (Step 4's createSession() wiring will need this)
  call resolveBrand() against the same host set, so the mapping can't
  drift between call sites.

- web/middleware.ts: new file. Resolves brand at the edge, forwards it as
  a request header (x-prv3-brand) so Server Components can read it via
  headers() without each one re-parsing Host. Chosen over parallel route
  trees (the other idiomatic Next.js multi-tenant pattern) because it's
  the smaller, MVP-appropriate change matching what was asked -- the
  route-tree-fork approach would let branding stay fully static per
  hostname, but is materially bigger scope than "make this hostname-
  conditional." Flagged as a real trade-off in the report, not silently
  absorbed: reading headers() in generateMetadata() opts the route
  segment into dynamic rendering, which for the ROOT layout means the
  whole site loses static prerendering, not just the two new branding
  paths.

- web/components/BrandContext.tsx: new file. PrivateOutput.tsx and
  ShareableOutput.tsx are both "use client" components (confirmed
  directly) -- they cannot call headers() themselves. layout.tsx (a
  Server Component) resolves brand once and provides it via context;
  both client components consume it with useBrand(). Avoids
  window.location.hostname (a real option, but hydration-unsafe if used
  to conditionally render before the client has mounted).

- web/app/layout.tsx: static `export const metadata` becomes
  `generateMetadata()` reading the middleware-set header (falling back to
  resolveBrand() directly against the Host header if that header is ever
  absent -- defensive, e.g. an edge case in the matcher). RootLayout
  itself becomes async to read the same header once and wrap {children}
  in <BrandProvider>.

- ShareableOutput.tsx / PrivateOutput.tsx: useBrand() consumed, the two
  specific hardcoded-branding spots made conditional. PrivateOutput's
  /book/toc link is suppressed (rendered as plain text) rather than
  replaced with an alternate destination on hr_diagnostic -- Pete's
  instruction was "suppressed or replaced," and suppression is the
  smaller, safer MVP choice given the stated goal (a session that's "not
  supposed to reveal PRV3 exists").

CondensedOutput.tsx: confirmed no changes needed (Pete's own finding,
independently re-confirmed this pass) -- no hardcoded branding, its
/diagnostic CTA is already a relative, hostname-agnostic link.

Usage:
    python tools/patch_hrdiagnostic_hostname_branding.py --dry-run
    python tools/patch_hrdiagnostic_hostname_branding.py --write
"""
import argparse
import pathlib
import sys

# -- New files ----------------------------------------------------------

BRAND_TS_PATH = pathlib.Path('web/lib/brand.ts')
BRAND_TS_CONTENT = '''/**
 * Single source of truth for hostname -> brand resolution. Both
 * middleware.ts (sets the x-prv3-brand request header for downstream
 * Server Components) and any Route Handler that needs brand at request
 * time (e.g. a future POST /api/diagnostic/session/start read, to bake
 * brand into the session record for Step 4's TC-* question gating) call
 * resolveBrand() against the same host set, so the mapping never drifts
 * between call sites.
 */

export type Brand = "principal_resolution" | "hr_diagnostic";

export const BRAND_HEADER = "x-prv3-brand";

const HR_DIAGNOSTIC_HOSTS = new Set([
  "hrdiagnostic.com",
  "www.hrdiagnostic.com",
]);

export function resolveBrand(host: string | null | undefined): Brand {
  if (!host) return "principal_resolution";
  const bare = host.split(":")[0].toLowerCase();
  return HR_DIAGNOSTIC_HOSTS.has(bare) ? "hr_diagnostic" : "principal_resolution";
}
'''

MIDDLEWARE_PATH = pathlib.Path('web/middleware.ts')
MIDDLEWARE_CONTENT = '''import { NextRequest, NextResponse } from "next/server";
import { BRAND_HEADER, resolveBrand } from "@/lib/brand";

/**
 * Resolves the incoming Host header to a brand once, at the edge, and
 * forwards it as a request header so Server Components (layout.tsx's
 * generateMetadata, any future page needing brand) can read it via
 * headers() without each one re-parsing Host individually. Route
 * Handlers that already have the real Request object can call
 * resolveBrand() directly against request.headers.get("host") instead,
 * or read this same forwarded header -- both resolve identically since
 * middleware runs first for any matched request.
 *
 * Two hostnames handled today: principalresolution.com (default,
 * existing behavior, unchanged) and hrdiagnostic.com (new). Anything
 * else (localhost during dev, preview deployment URLs) resolves to the
 * default -- matches "existing behavior, unchanged" for everything not
 * explicitly hrdiagnostic.com.
 */
export function middleware(request: NextRequest) {
  const brand = resolveBrand(request.headers.get("host"));
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set(BRAND_HEADER, brand);
  return NextResponse.next({ request: { headers: requestHeaders } });
}

export const config = {
  matcher: [
    // Skip static assets and Next internals -- brand only matters for
    // rendered pages and API routes that read it.
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
'''

BRAND_CONTEXT_PATH = pathlib.Path('web/components/BrandContext.tsx')
BRAND_CONTEXT_CONTENT = '''"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { Brand } from "@/lib/brand";

const BrandContext = createContext<Brand>("principal_resolution");

export function BrandProvider({
  brand,
  children,
}: {
  brand: Brand;
  children: ReactNode;
}) {
  return <BrandContext.Provider value={brand}>{children}</BrandContext.Provider>;
}

export function useBrand(): Brand {
  return useContext(BrandContext);
}
'''

# -- Edits to existing files ----------------------------------------------

LAYOUT_PATH = pathlib.Path('web/app/layout.tsx')

LAYOUT_IMPORTS_OLD = '''import "./globals.css";
import { NavBar } from "@/components/NavBar";
import { MobileMenu } from "@/components/MobileMenu";
import { ServiceSidebar } from "@/components/ServiceSidebar";'''
LAYOUT_IMPORTS_NEW = '''import "./globals.css";
import { headers } from "next/headers";
import { NavBar } from "@/components/NavBar";
import { MobileMenu } from "@/components/MobileMenu";
import { ServiceSidebar } from "@/components/ServiceSidebar";
import { BrandProvider } from "@/components/BrandContext";
import { BRAND_HEADER, resolveBrand, type Brand } from "@/lib/brand";'''

LAYOUT_METADATA_OLD = '''export const metadata: Metadata = {
  title: "Principal Resolution",
  description: "Organizational diagnostic",
};'''
LAYOUT_METADATA_NEW = '''// Static metadata replaced with generateMetadata() so title/description
// can branch on the resolved brand -- see web/lib/brand.ts. Reading
// headers() here opts this route segment into dynamic rendering; for the
// root layout that means the whole site loses static prerendering, not
// just these two hostnames' branding. Flagged, not silently absorbed --
// the alternative (a parallel route tree per hostname, keeping static
// generation) is materially bigger scope than what was asked for here.
async function resolveRequestBrand(): Promise<Brand> {
  const headersList = await headers();
  const forwarded = headersList.get(BRAND_HEADER);
  if (forwarded === "hr_diagnostic" || forwarded === "principal_resolution") {
    return forwarded;
  }
  // Defensive fallback if middleware's header is ever absent.
  return resolveBrand(headersList.get("host"));
}

export async function generateMetadata(): Promise<Metadata> {
  const brand = await resolveRequestBrand();
  if (brand === "hr_diagnostic") {
    return {
      title: "HR Diagnostic",
      description: "Organizational diagnostic",
      // Placeholder -- Pete to supply final favicon/OG assets separately.
      icons: { icon: "/favicon.ico" },
    };
  }
  return {
    title: "Principal Resolution",
    description: "Organizational diagnostic",
  };
}'''

LAYOUT_ROOTLAYOUT_OLD = '''export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return ('''
LAYOUT_ROOTLAYOUT_NEW = '''export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const brand = await resolveRequestBrand();
  return ('''

LAYOUT_CHILDREN_OLD = '''        <ServiceSidebar>{children}</ServiceSidebar>'''
LAYOUT_CHILDREN_NEW = '''        <BrandProvider brand={brand}>
          <ServiceSidebar>{children}</ServiceSidebar>
        </BrandProvider>'''

SHAREABLE_PATH = pathlib.Path('web/components/ShareableOutput.tsx')

SHAREABLE_IMPORT_OLD = '''import type { ShareableOutputPayload } from "@/lib/types";
import { severityAccentTokens } from "@/components/ConstellationField";
import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";'''
SHAREABLE_IMPORT_NEW = '''import type { ShareableOutputPayload } from "@/lib/types";
import { severityAccentTokens } from "@/components/ConstellationField";
import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";
import { useBrand } from "@/components/BrandContext";'''

SHAREABLE_FN_OLD = '''export default function ShareableOutput({ payload }: ShareableOutputProps) {
  const createdDate = new Date(payload.created_at).toLocaleDateString("en-US", {'''
SHAREABLE_FN_NEW = '''export default function ShareableOutput({ payload }: ShareableOutputProps) {
  const brand = useBrand();
  const createdDate = new Date(payload.created_at).toLocaleDateString("en-US", {'''

SHAREABLE_HEADER_OLD = '''        <span className="text-[12px] font-medium text-charcoal">
          Principal Resolution
        </span>'''
SHAREABLE_HEADER_NEW = '''        <span className="text-[12px] font-medium text-charcoal">
          {brand === "hr_diagnostic" ? "HR Diagnostic" : "Principal Resolution"}
        </span>'''

PRIVATE_PATH = pathlib.Path('web/components/PrivateOutput.tsx')

PRIVATE_IMPORT_OLD = '''import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";
import { firstSentence, buildCoreCluster, joinNames } from "@/lib/output-text";'''
PRIVATE_IMPORT_NEW = '''import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";
import { firstSentence, buildCoreCluster, joinNames } from "@/lib/output-text";
import { useBrand } from "@/components/BrandContext";'''

PRIVATE_FN_OLD = '''}: PrivateOutputProps) {
  const liabilityText = payload.synthesis.liability_condition_text;'''
PRIVATE_FN_NEW = '''}: PrivateOutputProps) {
  const brand = useBrand();
  const liabilityText = payload.synthesis.liability_condition_text;'''

PRIVATE_LINK_OLD = '''                <a
                  href={`/book/toc#${stateIdToSlug(s.id)}`}
                  className="font-display text-lg text-charcoal hover:underline"
                >
                  {s.name}
                </a>'''
PRIVATE_LINK_NEW = '''                {brand === "hr_diagnostic" ? (
                  <span className="font-display text-lg text-charcoal">
                    {s.name}
                  </span>
                ) : (
                  <a
                    href={`/book/toc#${stateIdToSlug(s.id)}`}
                    className="font-display text-lg text-charcoal hover:underline"
                  >
                    {s.name}
                  </a>
                )}'''

NEW_FILES = [
    (BRAND_TS_PATH, BRAND_TS_CONTENT),
    (MIDDLEWARE_PATH, MIDDLEWARE_CONTENT),
    (BRAND_CONTEXT_PATH, BRAND_CONTEXT_CONTENT),
]

EDITS = [
    (LAYOUT_PATH, [
        (LAYOUT_IMPORTS_OLD, LAYOUT_IMPORTS_NEW, 'imports'),
        (LAYOUT_METADATA_OLD, LAYOUT_METADATA_NEW, 'metadata -> generateMetadata'),
        (LAYOUT_ROOTLAYOUT_OLD, LAYOUT_ROOTLAYOUT_NEW, 'RootLayout signature'),
        (LAYOUT_CHILDREN_OLD, LAYOUT_CHILDREN_NEW, 'BrandProvider wrap'),
    ]),
    (SHAREABLE_PATH, [
        (SHAREABLE_IMPORT_OLD, SHAREABLE_IMPORT_NEW, 'import'),
        (SHAREABLE_FN_OLD, SHAREABLE_FN_NEW, 'useBrand() call'),
        (SHAREABLE_HEADER_OLD, SHAREABLE_HEADER_NEW, 'header-bar text'),
    ]),
    (PRIVATE_PATH, [
        (PRIVATE_IMPORT_OLD, PRIVATE_IMPORT_NEW, 'import'),
        (PRIVATE_FN_OLD, PRIVATE_FN_NEW, 'useBrand() call'),
        (PRIVATE_LINK_OLD, PRIVATE_LINK_NEW, '/book/toc link suppression'),
    ]),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    print('=== NEW FILES ===\\n')
    for path, content in NEW_FILES:
        if path.exists():
            print(f'ERROR: {path} already exists -- expected a new file.', file=sys.stderr)
            sys.exit(1)
        print(f'--- {path} ---')
        print(content)
        print()

    print('=== EDITS ===\\n')
    file_contents = {}
    for path, edits in EDITS:
        content = path.read_text(encoding='utf-8')
        new_content = content
        for old, new, label in edits:
            count = new_content.count(old)
            if count != 1:
                print(f'ERROR: {path} :: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
                sys.exit(1)
            new_content = new_content.replace(old, new, 1)
            print(f'[{path} :: {label}]')
            print(f'OLD:\\n{old}')
            print(f'NEW:\\n{new}')
            print()
        file_contents[path] = new_content

    if args.dry_run:
        print('DRY RUN -- all anchors found, all edits would apply cleanly. Nothing written.')
    else:
        for path, content in NEW_FILES:
            path.write_text(content, encoding='utf-8')
            print(f'WROTE (new): {path}')
        for path, content in file_contents.items():
            path.write_text(content, encoding='utf-8')
            print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
