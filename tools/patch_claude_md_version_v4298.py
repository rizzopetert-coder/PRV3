"""
CLAUDE.md: update the Key References table's MOB version cross-reference,
v4.297 -> v4.298, matching this session's closeout (tools/_mob.txt).

Usage:
    python tools/patch_claude_md_version_v4298.py --dry-run
    python tools/patch_claude_md_version_v4298.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('CLAUDE.md')

VERSION_OLD = '| MOB version | v4.297 |'
VERSION_NEW = '| MOB version | v4.298 |'

EDITS = [
    ('MOB version cross-reference 4.297 -> 4.298', VERSION_OLD, VERSION_NEW),
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
