"""
Debug-only hr_diagnostic brand override, gated to never fire in Production.

Adds resolveBrandForRequest() to web/lib/brand.ts -- resolveBrand() itself
is untouched. Honored only when process.env.VERCEL_ENV !== "production"
(Vercel's own auto-injected var, same convention already established at
web/lib/dev-diagnostic-preview.ts's isPreviewEnvironment(),
web/app/api/dev/diagnostic-preview/route.ts, and
web/app/api/engage/initiate/route.ts's testMode -- confirmed via direct
grep of existing usage, not assumed) AND the request carries header
x-debug-brand: hr_diagnostic exactly (not a boolean, so it's
self-documenting in request logs).

Exists because resolveBrand(host) is called from three independent places
(middleware.ts, diagnostic/layout.tsx's fallback, session/start/route.ts)
-- an override added to only one of them (e.g. middleware) would make
routing/metadata look right while session/start/route.ts still built the
wrong question_sequence, since it resolves brand independently rather than
reading middleware's BRAND_HEADER. All three now call
resolveBrandForRequest() instead, so a debug override is consistent
everywhere brand actually matters.

Purpose: lets the real TC-* end-to-end walkthrough run against a live
Vercel Preview deployment without any DNS/domain change, now that Host-
header spoofing was confirmed to fail at Vercel's edge routing layer
(DEPLOYMENT_NOT_FOUND, verified this session) for any hostname not
registered as a real alias for the deployment.

Usage:
    python tools/patch_hrdiagnostic_debug_brand_override.py --dry-run
    python tools/patch_hrdiagnostic_debug_brand_override.py --write
"""
import argparse
import pathlib
import sys

# ---------------------------------------------------------------------------
# web/lib/brand.ts -- add resolveBrandForRequest(), resolveBrand() untouched.
# ---------------------------------------------------------------------------
BRAND_PATH = pathlib.Path('web/lib/brand.ts')

BRAND_OLD = '''export function resolveBrand(host: string | null | undefined): Brand {
  if (!host) return "principal_resolution";
  const bare = host.split(":")[0].toLowerCase();
  return HR_DIAGNOSTIC_HOSTS.has(bare) ? "hr_diagnostic" : "principal_resolution";
}'''
BRAND_NEW = '''export function resolveBrand(host: string | null | undefined): Brand {
  if (!host) return "principal_resolution";
  const bare = host.split(":")[0].toLowerCase();
  return HR_DIAGNOSTIC_HOSTS.has(bare) ? "hr_diagnostic" : "principal_resolution";
}

// Debug-only override for testing the hr_diagnostic path against a live
// Vercel Preview deployment without a DNS/domain change -- Host-header
// spoofing fails against real Vercel infrastructure (edge routing rejects
// any Host not registered as a real alias for the deployment, confirmed
// directly, before the request ever reaches this code). Gated on
// VERCEL_ENV, Vercel's own auto-injected var ("production" | "preview" |
// "development", no custom var needed) -- same convention already used at
// web/lib/dev-diagnostic-preview.ts's isPreviewEnvironment(),
// web/app/api/dev/diagnostic-preview/route.ts, and
// web/app/api/engage/initiate/route.ts's testMode. Inlined here rather
// than importing isPreviewEnvironment() from dev-diagnostic-preview.ts --
// core brand resolution depending on a dev-preview-specific utility file
// is the wrong dependency direction. Exact header value required (not a
// boolean) so it's self-documenting in request logs. Never reachable in
// Production regardless of header value.
const DEBUG_BRAND_HEADER = "x-debug-brand";

export function resolveBrandForRequest(headers: Headers): Brand {
  if (
    process.env.VERCEL_ENV !== "production" &&
    headers.get(DEBUG_BRAND_HEADER) === "hr_diagnostic"
  ) {
    return "hr_diagnostic";
  }
  return resolveBrand(headers.get("host"));
}'''

# ---------------------------------------------------------------------------
# web/middleware.ts
# ---------------------------------------------------------------------------
MIDDLEWARE_PATH = pathlib.Path('web/middleware.ts')

MW_IMPORT_OLD = 'import { BRAND_HEADER, resolveBrand } from "@/lib/brand";'
MW_IMPORT_NEW = 'import { BRAND_HEADER, resolveBrandForRequest } from "@/lib/brand";'

MW_CALL_OLD = '  const brand = resolveBrand(request.headers.get("host"));'
MW_CALL_NEW = '  const brand = resolveBrandForRequest(request.headers);'

MIDDLEWARE_EDITS = [
    (MW_IMPORT_OLD, MW_IMPORT_NEW, 'import resolveBrandForRequest'),
    (MW_CALL_OLD, MW_CALL_NEW, 'use resolveBrandForRequest'),
]

# ---------------------------------------------------------------------------
# web/app/diagnostic/layout.tsx
# ---------------------------------------------------------------------------
LAYOUT_PATH = pathlib.Path('web/app/diagnostic/layout.tsx')

LAYOUT_IMPORT_OLD = 'import { BRAND_HEADER, resolveBrand, type Brand } from "@/lib/brand";'
LAYOUT_IMPORT_NEW = 'import { BRAND_HEADER, resolveBrandForRequest, type Brand } from "@/lib/brand";'

LAYOUT_CALL_OLD = '''  // Defensive fallback if middleware's header is ever absent.
  return resolveBrand(headersList.get("host"));'''
LAYOUT_CALL_NEW = '''  // Defensive fallback if middleware's header is ever absent -- also
  // covers the debug override consistently, not just the plain Host path.
  return resolveBrandForRequest(headersList);'''

LAYOUT_EDITS = [
    (LAYOUT_IMPORT_OLD, LAYOUT_IMPORT_NEW, 'import resolveBrandForRequest'),
    (LAYOUT_CALL_OLD, LAYOUT_CALL_NEW, 'use resolveBrandForRequest'),
]

# ---------------------------------------------------------------------------
# web/app/api/diagnostic/session/start/route.ts
# ---------------------------------------------------------------------------
START_ROUTE_PATH = pathlib.Path('web/app/api/diagnostic/session/start/route.ts')

START_IMPORT_OLD = 'import { resolveBrand } from "@/lib/brand";'
START_IMPORT_NEW = 'import { resolveBrandForRequest } from "@/lib/brand";'

START_CALL_OLD = '  const brand = resolveBrand(request.headers.get("host"));'
START_CALL_NEW = '  const brand = resolveBrandForRequest(request.headers);'

START_ROUTE_EDITS = [
    (START_IMPORT_OLD, START_IMPORT_NEW, 'import resolveBrandForRequest'),
    (START_CALL_OLD, START_CALL_NEW, 'use resolveBrandForRequest'),
]

ALL_FILE_EDITS = [
    (MIDDLEWARE_PATH, MIDDLEWARE_EDITS),
    (LAYOUT_PATH, LAYOUT_EDITS),
    (START_ROUTE_PATH, START_ROUTE_EDITS),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    brand_content = BRAND_PATH.read_text(encoding='utf-8')
    if brand_content.count(BRAND_OLD) != 1:
        print(f'ERROR: brand.ts anchor found {brand_content.count(BRAND_OLD)} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    new_brand_content = brand_content.replace(BRAND_OLD, BRAND_NEW, 1)
    print('[web/lib/brand.ts :: resolveBrandForRequest()] (1 occurrence)')

    file_contents = {BRAND_PATH: new_brand_content}

    for path, edits in ALL_FILE_EDITS:
        content = path.read_text(encoding='utf-8')
        new_content = content
        for old, new, label in edits:
            count = new_content.count(old)
            if count != 1:
                print(f'ERROR: {path} :: {label} anchor found {count} times, expected 1.', file=sys.stderr)
                sys.exit(1)
            new_content = new_content.replace(old, new, 1)
            print(f'[{path} :: {label}] (1 occurrence)')
        file_contents[path] = new_content

    if args.dry_run:
        print('\\nDRY RUN -- all anchors found, all edits would apply cleanly. Nothing written.')
    else:
        for path, content in file_contents.items():
            path.write_text(content, encoding='utf-8')
            print(f'WROTE: {path}')


if __name__ == '__main__':
    main()
