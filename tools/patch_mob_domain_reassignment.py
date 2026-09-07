"""
Patch tools/_mob.txt Section 13a: add a new Decision Register row logging the
principalresolution.com domain reassignment from prv-2 to prv-3, live-verified.
Bumps MOB version v4.281 -> v4.282 (new Decision Register entry = material
workstream status change per the MOB's own versioning rule).

Usage:
    python tools/patch_mob_domain_reassignment.py --dry-run
    python tools/patch_mob_domain_reassignment.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

# Anchor: the last row currently in the Decision Register (item 4, Legal/
# Compliance wiring) -- explicitly out of scope, untouched. Insert the new
# row immediately after it.
ANCHOR_ROW_END = (
    "output-contract change requiring the standing live-production round-trip check once undertaken. |"
)

NEW_ROW = (
    "\n| `principalresolution.com` (and `www.principalresolution.com`) reassigned from `prv-2` to `prv-3` "
    "| N/A -- infrastructure move, live-verified, closed "
    "| CLOSED this session -- reassigned and live-verified, not just API-confirmed "
    "| Reassignment done via `vercel domains add <domain> prv-3 --force` for both the apex and `www` domain, run individually for each -- confirmed via `--help` first to be the correct single operation for moving a domain between two projects in the same team, deliberately not `vercel domains remove` (which releases a domain from the Vercel team entirely, a materially different and unwanted operation). Pre-move check confirmed real dependencies before touching anything: `principalresolution.com` was serving prv-2's own live, distinct marketing site (title \"Principal Resolution // Direct Institutional Partnership,\" a 17-memo content library, `/states` page, last deployed 2026-04-26 -- over 4 months stale vs. prv-3's daily cadence) and carried live Google Workspace email (MX to `smtp.google.com`, valid SPF, a `google-site-verification` TXT record). Pete confirmed explicitly: proceed with an A/CNAME-only approach (no nameserver delegation, to leave MX/SPF/TXT at Porkbun untouched), and accepted the content swap (prv-2's memo library and `/states` page going dark in favor of prv-3's current homepage) with no porting requested. Post-reassignment, Vercel's own `vercel domains verify` API reported both domains `\"configured-correctly\"` / `\"ipStatus\": \"no-change\"` immediately, with zero Porkbun DNS edits -- because prv-2 and prv-3 share the same Vercel team's edge network, so routing follows Vercel's internal project-domain mapping (what `--force` changed) rather than the specific DNS record value at the registrar. This was flagged as an API-level claim needing a real check, not trusted alone. Live-verified: a bare unauthenticated `curl` to both `https://principalresolution.com/` and `https://www.principalresolution.com/` returned `HTTP 200` with `Content-Length: 22640` and `Etag: \"8f5582c5bdb4e3f52978d17eb20254c2\"` -- byte-for-byte identical to `prv-3.vercel.app`'s own root captured earlier this session, and matching content directly (title \"Principal Resolution\", h1 \"What looks like a people problem is usually structural\") -- confirmed absent: prv-2's old title and memo slugs (e.g. `anatomy-of-resentment`), found via direct grep, zero matches. Email spot-checked post-cutover via fresh `nslookup`: MX (`smtp.google.com`), SPF, and the site-verification TXT record all unchanged from the pre-move baseline, confirming the project-level reassignment never touched Porkbun's actual DNS zone. Fallback DNS records (only if ever genuinely needed, not required by the above): `A @ 216.198.79.1`, `A @ 64.29.17.1`, `CNAME www a2a030cc294e1eb1.vercel-dns-017.com.` -- pulled from Vercel's own `domains verify` response, not memory. "
    "| This session (Claude Code), 2026-09-06 "
    "| Closed -- no further check-in. Reopens only if Pete decides prv-2's old memo-library/`/states` content should be ported into prv-3, which would be new, separate content work, not a re-investigation of this row. |"
)

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.281"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.282"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    for needle, label in [(ANCHOR_ROW_END, 'anchor row end'), (OLD_VERSION_HEADER, 'version header')]:
        count = content.count(needle)
        if count != 1:
            print(f'ERROR: {label} found {count} times, expected exactly 1. Aborting.', file=sys.stderr)
            sys.exit(1)

    idx = content.find(ANCHOR_ROW_END) + len(ANCHOR_ROW_END)
    new_content = content[:idx] + NEW_ROW + content[idx:]
    new_content = new_content.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)

    if args.dry_run:
        print('DRY RUN -- anchor and version header found exactly once, insertion would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
        print('--- context around insertion point ---')
        print(new_content[idx-80:idx+400])
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
