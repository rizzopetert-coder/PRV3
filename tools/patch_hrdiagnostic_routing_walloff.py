"""
HRdiagnostic.com Part A -- routing wall-off, supersedes the scoped-layout
approach from the prior pass. Full route inventory confirmed directly
(find web/app -name page.tsx / route.ts) before designing the allowlist,
not assumed.

hr_diagnostic's allowed surface: "/" (rewritten to /diagnostic), "/diagnostic"
itself, and the five Path 1 session API routes (start/answer/narrative/
resume/undo). Everything else -- /book/*, /about/*, /ask, /engage,
/first-call*, the two service pages, /share/*, /diagnostic/condensed (a
separate, shorter diagnostic product, not part of what's being built here
-- flagged as an assumption, not confirmed with Pete), /api/result,
/api/interpret (both Path B/self-select-only), /api/share/*, /api/engage/*,
/api/first-call/*, /api/dev/* -- 404s.

Real content-leak finding, addressed beyond the literal routing ask: /diagnostic
itself has an internal client-side gate choosing between "diagnostic" (Path 1,
the TC-augmented sequential flow) and "self-select" (Path B, PRV3's full
58-state taxonomy browser). Blocking /api/result and /api/interpret at the
routing layer makes self-select fail if chosen, but leaves a visibly broken
button -- DiagnosticGate now hides the self-select option entirely on
hr_diagnostic (useBrand(), already-built Context, no new infrastructure).
Path 1's own PrivateOutput render already sets enableSharing={false}
unconditionally (confirmed at DiagnosticFlow.tsx:895, not brand-related) --
no ShareButton-hiding work needed.

Usage:
    python tools/patch_hrdiagnostic_routing_walloff.py --dry-run
    python tools/patch_hrdiagnostic_routing_walloff.py --write
"""
import argparse
import pathlib
import sys

MIDDLEWARE_PATH = pathlib.Path('web/middleware.ts')
MIDDLEWARE_CONTENT = '''import { NextRequest, NextResponse } from "next/server";
import { BRAND_HEADER, resolveBrand } from "@/lib/brand";

/**
 * hr_diagnostic is walled off to the diagnostic flow only -- no /book,
 * /about, service pages, or any other PRV3 content is reachable on that
 * hostname. principal_resolution (the default -- everything not
 * explicitly hrdiagnostic.com) is completely unaffected: every path
 * falls through to the single NextResponse.next() at the bottom.
 *
 * Allowed on hr_diagnostic: "/" (rewritten to /diagnostic so the
 * diagnostic flow is the entry point directly, not a routing detour),
 * "/diagnostic" itself, and the five Path 1 session API routes. Not
 * confirmed with Pete, flagged as an assumption: /diagnostic/condensed
 * (a separate, shorter diagnostic product) is treated as out of scope
 * and blocked along with everything else, since the TC-* module was
 * specified against PHASE_1_QUESTION_SEQUENCE (Path 1) specifically.
 *
 * /api/result and /api/interpret are Path B (self-select) only --
 * blocking them here is defense-in-depth alongside DiagnosticGate hiding
 * the self-select option on hr_diagnostic (see page.tsx): even if that
 * UI change were ever bypassed, the actual data calls fail closed rather
 * than serving PRV3's full state taxonomy.
 */
const HR_DIAGNOSTIC_ALLOWED_EXACT = new Set([
  "/",
  "/diagnostic",
  "/api/diagnostic/session/start",
  "/api/diagnostic/session/answer",
  "/api/diagnostic/session/narrative",
  "/api/diagnostic/session/resume",
  "/api/diagnostic/session/undo",
]);

export function middleware(request: NextRequest) {
  const brand = resolveBrand(request.headers.get("host"));
  const { pathname } = request.nextUrl;

  if (brand === "hr_diagnostic") {
    if (pathname === "/") {
      const url = request.nextUrl.clone();
      url.pathname = "/diagnostic";
      const rewritten = NextResponse.rewrite(url);
      rewritten.headers.set(BRAND_HEADER, brand);
      return rewritten;
    }
    if (!HR_DIAGNOSTIC_ALLOWED_EXACT.has(pathname)) {
      return new NextResponse(null, { status: 404 });
    }
  }

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set(BRAND_HEADER, brand);
  return NextResponse.next({ request: { headers: requestHeaders } });
}

export const config = {
  matcher: [
    // Skip static assets and Next internals -- brand/routing only matter
    // for rendered pages and API routes that read them.
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
'''

DIAGNOSTIC_LAYOUT_PATH = pathlib.Path('web/app/diagnostic/layout.tsx')
DIAGNOSTIC_LAYOUT_CONTENT = '''import type { Metadata } from "next";
import { headers } from "next/headers";
import { BRAND_HEADER, resolveBrand, type Brand } from "@/lib/brand";
import { BrandProvider } from "@/components/BrandContext";

/**
 * Brand-aware metadata and BrandProvider scoped to the /diagnostic route
 * segment only (supersedes the root-layout approach from the prior pass,
 * which forced the whole site into dynamic rendering -- confirmed via a
 * real build, every one of 36 routes flipped Static -> Dynamic). /diagnostic
 * was already client-rendered/stateful and never a static route to begin
 * with, so scoping brand detection here costs nothing additional -- the
 * rest of the site keeps its existing static generation unchanged.
 */
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
}

export default async function DiagnosticLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const brand = await resolveRequestBrand();
  return <BrandProvider brand={brand}>{children}</BrandProvider>;
}
'''

DIAGNOSTIC_PAGE_PATH = pathlib.Path('web/app/diagnostic/page.tsx')

PAGE_IMPORT_OLD = '''import { Suspense, useState } from "react";'''
PAGE_IMPORT_NEW = '''import { Suspense, useState } from "react";
import { useBrand } from "@/components/BrandContext";'''

GATE_FN_OLD = '''function DiagnosticGate({
  onChoose,
}: {
  onChoose: (path: DiagnosticPath) => void;
}) {
  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => onChoose("diagnostic")}
          className="text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
        >
          <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
            Take the diagnostic.
          </h2>
          <p className="font-ui text-sm text-gray-600">
            Answer questions. Get a complete read of what your organization is
            carrying.
          </p>
        </button>
        <button
          onClick={() => onChoose("self-select")}
          className="text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
        >
          <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
            Start by recognizing.
          </h2>
          <p className="font-ui text-sm text-gray-600">
            Select what looks familiar. See what it means together.
          </p>
        </button>
      </div>
    </div>
  );
}'''
GATE_FN_NEW = '''function DiagnosticGate({
  onChoose,
}: {
  onChoose: (path: DiagnosticPath) => void;
}) {
  // hr_diagnostic: self-select (Path B) is blocked at the routing layer
  // (/api/result, /api/interpret both 404 on that hostname -- see
  // middleware.ts) since it exposes PRV3's full 58-state taxonomy, which
  // this hostname must never reveal. Hiding the option here too, rather
  // than leaving a button that would otherwise fail visibly if clicked.
  const brand = useBrand();
  const diagnosticOnly = brand === "hr_diagnostic";

  return (
    <div className="max-w-2xl mx-auto px-6 py-16">
      <div
        className={
          diagnosticOnly
            ? "grid grid-cols-1 gap-4"
            : "grid grid-cols-1 md:grid-cols-2 gap-4"
        }
      >
        <button
          onClick={() => onChoose("diagnostic")}
          className="text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
        >
          <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
            Take the diagnostic.
          </h2>
          <p className="font-ui text-sm text-gray-600">
            Answer questions. Get a complete read of what your organization is
            carrying.
          </p>
        </button>
        {!diagnosticOnly && (
          <button
            onClick={() => onChoose("self-select")}
            className="text-left p-6 rounded-xl border border-gray-200 bg-white hover:border-charcoal transition-all duration-300 animate-fade-up"
          >
            <h2 className="font-display text-lg font-semibold text-charcoal mb-2">
              Start by recognizing.
            </h2>
            <p className="font-ui text-sm text-gray-600">
              Select what looks familiar. See what it means together.
            </p>
          </button>
        )}
      </div>
    </div>
  );
}'''

EDITS = [
    (DIAGNOSTIC_PAGE_PATH, [
        (PAGE_IMPORT_OLD, PAGE_IMPORT_NEW, 'import useBrand'),
        (GATE_FN_OLD, GATE_FN_NEW, 'DiagnosticGate: hide self-select on hr_diagnostic'),
    ]),
]

NEW_FILES = [
    (MIDDLEWARE_PATH, MIDDLEWARE_CONTENT),
    (DIAGNOSTIC_LAYOUT_PATH, DIAGNOSTIC_LAYOUT_CONTENT),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    print('=== FILES (overwrite middleware.ts / new diagnostic/layout.tsx) ===\\n')
    for path, content in NEW_FILES:
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
            print(f'WROTE: {path}')
        for path, content in file_contents.items():
            path.write_text(content, encoding='utf-8')
            print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
