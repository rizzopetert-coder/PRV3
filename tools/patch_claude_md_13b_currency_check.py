"""
CLAUDE.md -- two changes, folded into one pass since MOB v4.324 (the
version this targets) is not yet committed:

1. Key References table: MOB version v4.323 -> v4.324.
2. Closeout Protocol: new Step 1a -- Section 13b Currency Check, inserted
   between Step 1 (Diary Write) and Step 2 (Update MOB) so the check
   shapes the Section 16 entry Step 2 writes, not just follows it.
   Matches this doc's own existing lettered-substep convention (2a/2b
   already exist for the same reason -- a sub-step that must land before
   the next numbered step, without renumbering everything after it).

Root cause this closes: Section 13b sat unrewritten 2026-09-07 ->
2026-09-23 while all four of its numbered items closed underneath it --
nothing in the protocol ever checked whether 13b needed a rewrite,
only whether the mechanics of a rewrite (once triggered) were followed
correctly.

Usage:
    python tools/patch_claude_md_13b_currency_check.py --dry-run
    python tools/patch_claude_md_13b_currency_check.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('CLAUDE.md')

VERSION_OLD = '| MOB version | v4.323 |'
VERSION_NEW = '| MOB version | v4.324 |'

STEP_OLD = '''If the write fails, do not silently omit it — log `[DIARY WRITE GAP: <reason>]` at the top of the Section 16 entry and proceed with closeout.

### Step 2 — Update MOB'''

STEP_NEW = '''If the write fails, do not silently omit it — log `[DIARY WRITE GAP: <reason>]` at the top of the Section 16 entry and proceed with closeout.

### Step 1a — Section 13b Currency Check
Confirm Section 13b (Session Priority Queue) reflects every closure, new open item, and resequencing landed this session. If anything closed that 13b still lists as active, or anything opened that 13b doesn't carry, update 13b in the same closeout pass and name the change in the Section 16 entry. If 13b needs no change, state that explicitly in the Section 16 entry ("13b checked, no change") rather than omitting it.

### Step 2 — Update MOB'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    new_content = content

    for old, new, label in [
        (VERSION_OLD, VERSION_NEW, 'version line'),
        (STEP_OLD, STEP_NEW, 'Step 1a insertion'),
    ]:
        count = new_content.count(old)
        if count != 1:
            print(f'ERROR: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
            sys.exit(1)
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print('DRY RUN -- both anchors found exactly once, replacements would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
