"""
web/components/ServiceSidebar.tsx: fix a regression from the previous
patch (left-side move + 8px gaps + py-6). The <aside> is `h-screen`
with `flex flex-col` children sized by `flex-1` -- once the four boxes'
combined min-content height (padding + gaps + two-line teaser copy)
exceeds the viewport height, flex has nowhere to shrink to and the
last item (Executive Advisory) gets pushed below the fold with no way
to reach it. Verified live at 1512x786: Executive Advisory's header
doesn't render in view at all.

Fix: add overflow-y-auto to the <aside> so it scrolls internally
instead of silently clipping. shrink-0 (on the aside itself, sizing it
against the flex-1 main content area) is unrelated and untouched --
this only affects how the aside handles ITS OWN children exceeding its
own fixed h-screen height.

No other changes.

Usage:
    python tools/patch_service_sidebar_scroll_fix.py --dry-run
    python tools/patch_service_sidebar_scroll_fix.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/components/ServiceSidebar.tsx')

OLD = '''      <aside className="hidden md:flex md:flex-col w-72 shrink-0 border-r border-line bg-field sticky top-0 h-screen">'''
NEW = '''      <aside className="hidden md:flex md:flex-col w-72 shrink-0 border-r border-line bg-field sticky top-0 h-screen overflow-y-auto">'''


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
