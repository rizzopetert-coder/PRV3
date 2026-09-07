"""
Patch tools/_mob.txt Section 13a:
- Row 2 (Preview Redis credential exposure): update status to reflect this
  session's findings (CLI path confirmed, blocked on Pete's own action).
- Row 3 (ssoProtection discrepancy): update status to RESOLVED with full
  root-cause findings.
- Bump MOB version header v4.280 -> v4.281 (Section 13a status changed
  materially per the MOB's own versioning rule).

Usage:
    python tools/patch_mob_ssoprotection_redis_resolution.py --dry-run
    python tools/patch_mob_ssoprotection_redis_resolution.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

OLD_ROW2 = (
    "| Preview environment's Upstash Redis credentials are plaintext-retrievable via `vercel env pull`, unlike Production's "
    "| N/A -- infrastructure/security hygiene, not a Tier 1-4 workflow item "
    "| Open, surfaced by the 2026-09-05 Quarterly Step-Back, not investigated further this session "
    "| Confirmed directly: `vercel env pull --environment=production` returns literal `\"[SENSITIVE]\"` for `UPSTASH_REDIS_REST_URL`/`TOKEN` (correct, expected masking). The equivalent `--environment=preview` pull returns both values in real plaintext -- confirmed by direct comparison, not assumed. Preview points to a genuinely separate Redis instance from Production (split during a Session 71 fix), so this is not a direct production-data exposure, but it is a real asymmetry in how the two environments' credentials are protected in Vercel's own dashboard -- worth a deliberate look (flag Preview's vars as Sensitive too, matching Production's posture) rather than leaving as an accident of which environment happened to get flagged first. Not fixed here -- flagged, per the Step-Back's own \"surfaced but not acted on\" list. "
    "| This session (Claude Code), 2026-09-05 "
    "| No forced check-in -- Pete's call on whether/when to flag Preview's credentials as Sensitive in the Vercel dashboard. |"
)

NEW_ROW2 = (
    "| Preview environment's Upstash Redis credentials are plaintext-retrievable via `vercel env pull`, unlike Production's "
    "| N/A -- infrastructure/security hygiene, not a Tier 1-4 workflow item "
    "| Open, mechanism and fix path fully confirmed this session -- blocked on Pete supplying the live credential value, not on tooling "
    "| Re-confirmed directly (fresh `vercel env pull --environment=preview` and `--environment=production`, redacted length-check only, actual values never printed or persisted): Production's `UPSTASH_REDIS_REST_URL`/`TOKEN` (plus `ANTHROPIC_API_KEY`/`ENGINE_SECRET`) pull back as literal `[SENSITIVE]`; Preview's pull back as real plaintext -- exactly as the Step-Back found, now independently reproduced. CLI capability confirmed via `vercel env update <name> preview --sensitive` and `vercel env add <name> preview --force --sensitive` (both flags real, confirmed against live `--help` output, not assumed). Vercel's own docs (fetched live this session, not memory) confirm there is no value-free path either way, dashboard included: \"To mark an existing environment variable as sensitive, remove and re-add it.\" This session's own attempt to complete the fix end-to-end (extracting the plaintext value into a shell variable to feed back into `vercel env update`) was blocked by the coding sandbox's own safety classifier -- correctly, since routinely handling live production/preview secrets isn't something this session's environment should do by default. Locally-pulled plaintext files created during verification were deleted immediately, before this row was written. "
    "| This session (Claude Code), 2026-09-06 "
    "| No forced check-in -- Pete's call on when to run `vercel env update UPSTASH_REDIS_REST_URL preview --sensitive` and the same for `_TOKEN`, pasting the current value (from Upstash's own dashboard, not round-tripped through an AI session) at the prompt for each. |"
)

OLD_ROW3 = (
    "| `prv-3`'s live `ssoProtection` config (`\"all_except_custom_domains\"`) doesn't match observed unauthenticated live access "
    "| N/A -- infrastructure fact, unresolved, not a Tier 1-4 workflow item "
    "| Open, genuinely unreconciled, not guessed at "
    "| Direct check this session: `vercel project protection prv-3` (and the raw `/v9/projects/<id>` API) both show `ssoProtection: {\"deploymentType\": \"all_except_custom_domains\"}` -- a real, non-null, active-looking setting. Direct live check: `curl https://prv-3.vercel.app/` returns a clean, unauthenticated HTTP 200, no auth redirect or challenge of any kind. These two facts don't obviously reconcile. Possible explanation not confirmed: Hobby-tier plans may not actually enforce this protection type regardless of the stored config value -- this is a guess, not a finding, and is explicitly not asserted as the answer. Neither the config value nor the observed behavior should be treated as the full truth about production's real access-control posture until this is actually reconciled (e.g. by checking Vercel's own plan-tier documentation directly, or testing whether a request without the Vercel session cookie is ever actually blocked anywhere). "
    "| This session (Claude Code), 2026-09-05 "
    "| No forced check-in -- worth resolving before anyone relies on either the config or the observed behavior alone as ground truth for production's access posture. |"
)

NEW_ROW3 = (
    "| `prv-3`'s live `ssoProtection` config (`\"all_except_custom_domains\"`) doesn't match observed unauthenticated live access "
    "| N/A -- infrastructure fact, now fully reconciled "
    "| RESOLVED this session -- confirmed root cause, not a misconfiguration "
    "| Reconciled via direct empirical A/B test, not assumed or guessed: a bare unauthenticated `curl` (no cookies, no bypass headers) to `https://prv-3.vercel.app/` returns a clean HTTP 200 with real page content, reproduced against both a CDN-cached static route (`X-Vercel-Cache: HIT`) and a dynamic serverless route (`/api/engine`, `X-Vercel-Cache: MISS`, hit origin, real `405` function response) -- ruling out a CDN-cache-bypass explanation, since the dynamic route proves the request reaches the actual function with no challenge either way. The identical unauthenticated `curl` against a real PREVIEW deployment URL (a `target: null` deployment from a research-refresh branch) returns a genuine `302` redirect to `vercel.com/sso-api` with a `_vercel_sso_nonce` cookie set -- the real Vercel Authentication challenge, confirming protection is live and functioning, just scoped away from production. Root cause, confirmed against Vercel's own docs fetched live this session (not memory, not the guess this row previously carried): `all_except_custom_domains` is the API's internal name for the dashboard's \"Standard Protection\" scope, which by design exempts whichever domain is the project's current production domain -- not \"custom domains you might add later\" specifically. Direct quote: \"On the Hobby plan, Vercel Authentication with Standard Protection is available. This protects your preview deployments and deployment URLs, but your production domain remains publicly accessible. To protect production domains, you need a Pro or Enterprise plan.\" Team plan confirmed Hobby via the Vercel API's own team listing. The \"Pete's own authenticated session bypassing it\" false positive is explicitly ruled out -- every test this session used a bare unauthenticated `curl`, no cookies or headers of any kind. This also corrects a real, standing internal contradiction: an earlier MOB entry (session ~2026-08-27, Section 16, tied to the vercel.json outage fix) asserted \"Vercel's Deployment Protection (SSO gate) currently blocks public access -- confirmed expected, not a bug\" -- the exact opposite of the now-confirmed truth. That earlier claim was incorrect at the time it was written, not a description of a since-changed setting. Section 13b's Priority Queue items 1 and 3 both still carry the now-stale \"unresolved\" framing from the Step-Back and should be corrected at the next Priority Queue rewrite (session closeout), not assumed fixed by this row alone. No change was made to the `ssoProtection` setting itself, per instruction -- the only way to actually close the production-exposure gap is upgrading the team to Pro or Enterprise and switching the deployment-protection scope to \"All Deployments,\" a paid, billing-level decision for Pete, not executed here. "
    "| This session (Claude Code), 2026-09-06 "
    "| Closed as a mystery -- reopens only if Pete decides to act on the underlying exposure (upgrade plan + change scope), which would be a new, separate decision, not a re-investigation of this row. |"
)

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.280"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.281"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    checks = [
        (OLD_ROW2, 'row2 (Redis)'),
        (OLD_ROW3, 'row3 (ssoProtection)'),
        (OLD_VERSION_HEADER, 'version header'),
    ]
    for needle, label in checks:
        count = content.count(needle)
        if count != 1:
            print(f'ERROR: {label} found {count} times, expected exactly 1. Aborting.', file=sys.stderr)
            sys.exit(1)

    new_content = content.replace(OLD_ROW2, NEW_ROW2, 1)
    new_content = new_content.replace(OLD_ROW3, NEW_ROW3, 1)
    new_content = new_content.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)

    if args.dry_run:
        print('DRY RUN -- all 3 anchors found exactly once, replacements would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
