"""
Patch tools/_mob.txt Section 13a: add a new parked/for-later Decision
Register row noting a real architectural question surfaced while fixing
the homepage dark-theme bug, deliberately not acted on this session per
Pete's explicit instruction. Bumps MOB version.

Usage:
    python tools/patch_mob_v2_migration_parked_item.py --dry-run
    python tools/patch_mob_v2_migration_parked_item.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

ANCHOR = (
    "Closed -- no further check-in. Reopens only if Pete decides prv-2's old "
    "memo-library/`/states` content should be ported into prv-3, which would "
    "be new, separate content work, not a re-investigation of this row. |"
)

NEW_ROW = (
    "\n| A `globals.css` comment states the v2 token system (`--ink`/`--field`/"
    "etc.) was introduced \"starting with the Stage 4 homepage proof point, "
    "not before\" -- implying the homepage may have been intended as the "
    "first route to fully adopt v2 tokens, including for text color "
    "| N/A -- architectural question, not a Tier 1-4 workflow item, deliberately not acted on "
    "| Parked, flagged not resolved -- surfaced while fixing the homepage dark-theme bug (this session) "
    "| Confirmed directly: [globals.css:13](web/app/globals.css) states the v2 layer "
    "\"is wired into markup starting with the Stage 4 homepage proof point, not "
    "before.\" While fixing the homepage's dark-theme background bug this "
    "session, a related text-contrast bug was found and fixed via a new, "
    "isolated `--home-ink` token (mirroring `--ink`'s existing per-theme "
    "values) rather than migrating the homepage's `text-charcoal` usage onto "
    "`--ink` directly. That alternative was considered and rejected for this "
    "fix specifically: `text-(--ink)` has zero precedent anywhere in the "
    "codebase today (grepped, 0 matches), and adopting it would have shifted "
    "Warm theme's homepage text color as an unreviewed side effect of a "
    "Dark-theme bug fix, out of scope for what was asked. Whether the "
    "homepage should eventually migrate fully onto v2 tokens (retiring the "
    "Session-58-era `text-charcoal`/`--color-charcoal` there) is a real, "
    "separate architectural question this comment raises but does not "
    "answer -- explicitly flagged, not decided, not actioned, per Pete's "
    "direct instruction. "
    "| This session (Claude Code), 2026-09-07 "
    "| No forced check-in -- Pete's call on whether/when to pursue a full "
    "v2-token migration for the homepage. Not blocking anything shipped this session. |"
)

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.283"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.284"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    for needle, label in [(ANCHOR, 'anchor row end'), (OLD_VERSION_HEADER, 'version header')]:
        count = content.count(needle)
        if count != 1:
            print(f'ERROR: {label} found {count} times, expected exactly 1. Aborting.', file=sys.stderr)
            sys.exit(1)

    idx = content.find(ANCHOR) + len(ANCHOR)
    new_content = content[:idx] + NEW_ROW + content[idx:]
    new_content = new_content.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)

    if args.dry_run:
        print('DRY RUN -- anchor and version header found exactly once, insertion would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
