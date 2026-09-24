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
  "hrdiagnostic.com",
  "www.hrdiagnostic.com",
]);

export function resolveBrand(host: string | null | undefined): Brand {
  if (!host) return "principal_resolution";
  const bare = host.split(":")[0].toLowerCase();
  return HR_DIAGNOSTIC_HOSTS.has(bare) ? "hr_diagnostic" : "principal_resolution";
}
