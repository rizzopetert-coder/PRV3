"""
CLAUDE.md -- MOB version cross-reference bump v4.324 -> v4.325, per this
session's Section 13b amendment closeout.

Usage:
    python tools/patch_claude_md_v4325.py --dry-run
    python tools/patch_claude_md_v4325.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('CLAUDE.md')

OLD = '| MOB version | v4.324 |'
NEW = '| MOB version | v4.325 |'


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    count = content.count(OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)
    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
