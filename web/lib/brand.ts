/**
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
  "hr-dx.com",
  "www.hr-dx.com",
]);

export function resolveBrand(host: string | null | undefined): Brand {
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
}
