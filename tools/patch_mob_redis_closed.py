"""
Patch tools/_mob.txt Section 13a: close out the Preview Redis credential
exposure row now that both UPSTASH_REDIS_REST_URL and _TOKEN are confirmed
Sensitive-masked in Preview. Bumps MOB version v4.282 -> v4.283.

Usage:
    python tools/patch_mob_redis_closed.py --dry-run
    python tools/patch_mob_redis_closed.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

ANCHOR_START = "| Preview environment's Upstash Redis credentials are plaintext-retrievable via `vercel env pull`, unlike Production's "
ANCHOR_END = "pasting the current value (from Upstash's own dashboard, not round-tripped through an AI session) at the prompt for each. |"

NEW_ROW = (
    "| Preview environment's Upstash Redis credentials are plaintext-retrievable via `vercel env pull`, unlike Production's "
    "| N/A -- infrastructure/security hygiene, not a Tier 1-4 workflow item "
    "| CLOSED this session -- both variables confirmed Sensitive-masked, live-verified "
    "| Pete ran `vercel env update UPSTASH_REDIS_REST_TOKEN preview --sensitive` and `vercel env update UPSTASH_REDIS_REST_URL preview --sensitive` himself, pasting each value from Upstash's own dashboard at the interactive prompt -- neither value was ever seen, typed, or held by this session. TOKEN's first run hit a stale/invalid CLI token mid-command, which triggered an automatic `vercel login` device-flow re-auth; TOKEN completed successfully in the same breath (confirmed via a fresh redacted `vercel env pull`, length-check only). URL's first attempt failed with \"No Environment Variable found matching the specified criteria\" -- root-caused as a transient session hiccup immediately following the forced re-login, not a real problem: a direct test this session (`vercel env update UPSTASH_REDIS_REST_URL PREVIEW --sensitive` and again with lowercase `preview`) showed both find the variable correctly, ruling out the case-sensitivity theory. Pete re-ran the URL update once things settled and it succeeded. Final verification, this session, redacted pull (no value ever printed): both `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` now return `[SENSITIVE]` for `--environment=preview`, matching Production's posture exactly. Flagged separately, not a Vercel-side fix: the TOKEN value was pasted directly into the chat transcript during troubleshooting -- marking it Sensitive in Vercel stops future reads through Vercel's own tooling, it does not undo that exposure, so this is logged as a live open question for Pete on whether to rotate that credential at Upstash regardless of the masking fix landing. "
    "| This session (Claude Code), 2026-09-06 "
    "| Closed -- no further check-in on the masking asymmetry itself. Separate, still-open question for Pete: whether to rotate the Upstash Redis token given it was pasted into this session's chat transcript. |"
)

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.282"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.283"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    start = content.find(ANCHOR_START)
    if start == -1:
        print('ERROR: row start anchor not found.', file=sys.stderr)
        sys.exit(1)
    end_marker_idx = content.find(ANCHOR_END, start)
    if end_marker_idx == -1:
        print('ERROR: row end anchor not found after start.', file=sys.stderr)
        sys.exit(1)
    end = end_marker_idx + len(ANCHOR_END)

    old_row = content[start:end]
    if content.count(old_row) != 1:
        print(f'ERROR: old row text found {content.count(old_row)} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    version_count = content.count(OLD_VERSION_HEADER)
    if version_count != 1:
        print(f'ERROR: version header found {version_count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(old_row, NEW_ROW, 1)
    new_content = new_content.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)

    if args.dry_run:
        print('DRY RUN -- row and version header found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
