"""
prompts/session-handoff-v4.298.md: remove the "Flag for Pete" section --
the Group 2 push confirmation (homepage contrast fixes) it described as
an unresolved carry-forward was actually resolved earlier the same
calendar day (2026-09-10): visually confirmed in Dark theme and pushed
as part of a 14-commit batch before the VoiceSection copy update.
Corresponding tools/_mob.txt correction: patch_mob_group2_push_confirmed.py.

Usage:
    python tools/patch_handoff_v4298_group2_resolved.py --dry-run
    python tools/patch_handoff_v4298_group2_resolved.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('prompts/session-handoff-v4.298.md')

OLD = '''- **If running the overdue Quarterly Step-Back:** no specific files —
  full project assessment per the dual-sourced format (CLAUDE.md's own
  Quarterly Step-Back section).

## Flag for Pete (not silently resolved)

The prior queue (v4.297) carried a still-open item — "Group 2 push
confirmation (homepage contrast fixes), committed, needs Pete's visual
check in Dark theme before pushing" — that does not appear in this
session's given Priority Queue list. Nothing this session touched that
work. Carrying it forward here rather than silently dropping it; flagged
in the closeout report for Pete to confirm whether it's resolved,
superseded, or should stay on the active queue.'''

NEW = '''- **If running the overdue Quarterly Step-Back:** no specific files —
  full project assessment per the dual-sourced format (CLAUDE.md's own
  Quarterly Step-Back section).'''

EDITS = [
    ('remove resolved Flag for Pete section', OLD, NEW),
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
