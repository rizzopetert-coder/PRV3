// Whether a diagnostic session is a test run -- decided once at session
// start and carried through to the anonymized aggregate record, so test
// completions can be excluded when diagnostic-aggregate is analyzed.
//
// Preview deployments write to the same Upstash database as Production
// (confirmed 2026-09-26), so every non-Production session is a test run by
// definition. In Production, a deliberate smoke test opts in with the
// x-prv3-test-run header. The header is an honest-client flag: spoofing it
// only removes the sender's own record from analytics.
export const TEST_RUN_HEADER = "x-prv3-test-run";

export function isTestRun(
  headers: Headers,
  vercelEnv: string | undefined = process.env.VERCEL_ENV,
): boolean {
  if (vercelEnv !== "production") return true;
  return headers.get(TEST_RUN_HEADER) === "1";
}
