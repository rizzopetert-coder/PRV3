"""
tools/_mob.txt: small correction, not a new closeout -- MOB stays at
v4.298. "Group 2 push confirmation (homepage contrast fixes)" was
resolved (visually confirmed in Dark theme, pushed) earlier in the same
2026-09-10 session that later closed as v4.298, but the v4.297 entry's
own item 3 still read "PUSH HELD" and the historical Priority Queue
snapshot at the end of that entry still listed it as needing
confirmation. Both corrected in place.

Usage:
    python tools/patch_mob_group2_push_confirmed.py --dry-run
    python tools/patch_mob_group2_push_confirmed.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

TITLE_OLD = '### 3. v2 token migration re-examined and closed; 3 new contrast bugs found and fixed -- PUSH HELD'
TITLE_NEW = '### 3. v2 token migration re-examined and closed; 3 new contrast bugs found and fixed -- pushed'

CLOSING_OLD = '''Commits `6af546c`/`9f8c16e` (the fixes), `0d985aa`/`5c82240` (MOB/
CLAUDE.md updates for this and item 2 above), plus associated patch
scripts -- **all committed, PUSH HELD.** Below-the-fold screenshots of
the three fixed elements could not be captured this session (the
Browser pane was in a hidden state that blocks scroll-dependent
repaint, confirmed reproducible and confirmed not an app problem via
`get_page_text`/`getComputedStyle` both returning correct live values
regardless) -- the standing production-facing-UI exception applies
until a visual check confirms the fix in Dark theme specifically,
where the failure was most severe.'''

CLOSING_NEW = '''Commits `6af546c`/`9f8c16e` (the fixes), `0d985aa`/`5c82240` (MOB/
CLAUDE.md updates for this and item 2 above), plus associated patch
scripts -- **all committed, PUSH HELD at the time this entry was first
written.** Below-the-fold screenshots of the three fixed elements could
not be captured this session (the Browser pane was in a hidden state
that blocks scroll-dependent repaint, confirmed reproducible and
confirmed not an app problem via `get_page_text`/`getComputedStyle`
both returning correct live values regardless) -- the standing
production-facing-UI exception applies until a visual check confirms
the fix in Dark theme specifically, where the failure was most severe.

**RESOLVED, same calendar day (2026-09-10), later continuation
session:** visually confirmed in Dark theme -- CTA button, footer text,
and avatar circle all clean -- and pushed as part of a 14-commit batch
earlier in that session, before the VoiceSection copy update. The
push-hold above is historical -- this workstream is closed.'''

QUEUE_OLD = '''3. Group 2 push confirmation (homepage contrast fixes) -- committed,
   needs Pete's visual check in Dark theme before pushing. See item 3
   above for the full detail on why screenshots couldn't be captured
   this session.'''

QUEUE_NEW = '''3. ~~Group 2 push confirmation (homepage contrast fixes)~~ --
   RESOLVED same calendar day, later continuation session: visually
   confirmed in Dark theme and pushed. See item 3 above (amended) for
   detail. No longer an active queue item.'''

EDITS = [
    ('item 3 title -- PUSH HELD -> pushed', TITLE_OLD, TITLE_NEW),
    ('item 3 closing paragraph -- resolution note appended', CLOSING_OLD, CLOSING_NEW),
    ('historical Priority Queue item 3 -- marked resolved', QUEUE_OLD, QUEUE_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
