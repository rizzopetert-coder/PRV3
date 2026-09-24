"""
TEMPORARY diagnostic: add x-debug-mw-host / x-debug-mw-brand response
headers to middleware.ts, echoing back the RAW request.headers.get("host")
value exactly as Edge Middleware receives it, and the brand
resolveBrandForRequest() computes from it -- on all 3 return paths (the
"/" rewrite, the 404 wall-off, and the normal next() fallthrough), since
which branch actually fires for hr-dx.com in Production is itself part of
what's unknown right now.

No normalization applied to the logged host value -- if there's a case
difference, trailing character, port, or anything else unusual, it needs
to be visible verbatim. No logic change to brand resolution or routing --
purely observability, added on top of the existing return statements.

Purpose: middleware's brand-conditional wall-off/rewrite isn't firing for
hr-dx.com in Production (confirmed via /api/result returning the same 400
on both domains -- a route that's never cached, ruling out the earlier
caching bug as the cause here), while the exact same resolveBrandForRequest()
function correctly resolves hr_diagnostic when called from Node-runtime
call sites (session/start/route.ts, diagnostic/layout.tsx) for the
identical Host. middleware.ts runs on Edge Runtime -- a different
execution environment -- so the leading hypothesis is some divergence in
what Edge Middleware actually receives as the Host header for this
project's specific deployment configuration, not a resolveBrand() logic
bug. This diagnostic will show the raw value directly rather than
continuing to infer from symptoms.

Must be removed in the same round as the real fix once identified -- not
left standing per Pete's explicit instruction.

Usage:
    python tools/patch_middleware_debug_diagnostic.py --dry-run
    python tools/patch_middleware_debug_diagnostic.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/middleware.ts')

OLD = '''export function middleware(request: NextRequest) {
  const brand = resolveBrandForRequest(request.headers);
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
}'''

NEW = '''// TEMPORARY diagnostic, this session -- remove in the same round as the
// real fix, once the raw host divergence (if any) between Edge Middleware
// and Node-runtime call sites is identified. Echoes the exact,
// unnormalized values back as response headers on every return path, so
// the raw string is visible directly rather than inferred from behavior.
function withDebugHeaders(response: NextResponse, rawHost: string | null, brand: string): NextResponse {
  response.headers.set("x-debug-mw-host", rawHost ?? "(null)");
  response.headers.set("x-debug-mw-brand", brand);
  return response;
}

export function middleware(request: NextRequest) {
  const rawHost = request.headers.get("host");
  const brand = resolveBrandForRequest(request.headers);
  const { pathname } = request.nextUrl;

  if (brand === "hr_diagnostic") {
    if (pathname === "/") {
      const url = request.nextUrl.clone();
      url.pathname = "/diagnostic";
      const rewritten = NextResponse.rewrite(url);
      rewritten.headers.set(BRAND_HEADER, brand);
      return withDebugHeaders(rewritten, rawHost, brand);
    }
    if (!HR_DIAGNOSTIC_ALLOWED_EXACT.has(pathname)) {
      return withDebugHeaders(new NextResponse(null, { status: 404 }), rawHost, brand);
    }
  }

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set(BRAND_HEADER, brand);
  return withDebugHeaders(
    NextResponse.next({ request: { headers: requestHeaders } }),
    rawHost,
    brand,
  );
}'''


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
