import { NextRequest, NextResponse } from "next/server";
import { BRAND_HEADER, resolveBrandForRequest } from "@/lib/brand";

/**
 * hr_diagnostic is walled off to the diagnostic flow only -- no /book,
 * /about, service pages, or any other PRV3 content is reachable on that
 * hostname. principal_resolution (the default -- everything not
 * explicitly hr-dx.com) is completely unaffected: every path
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

// TEMPORARY diagnostic, this session -- remove in the same round as the
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
}

export const config = {
  matcher: [
    // Skip static assets and Next internals -- brand/routing only matter
    // for rendered pages and API routes that read them.
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
