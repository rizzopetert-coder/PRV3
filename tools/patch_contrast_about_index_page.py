"""
web/app/about/page.tsx: fix a real, structural WCAG AA contrast
failure -- the page's own root background never adapts to Dark/Neutral
theme at all, unlike every other page in this file family.

Root cause, confirmed by reading the file, not assumed: `bg-paper`
maps to `--color-paper`, a fixed, non-theme-reactive value
(#F6F3ED, hardcoded once in globals.css's `@theme inline` block, never
redefined per [data-theme]). Its three sibling sub-pages
(StoryPageContent.tsx, MethodPageContent.tsx, ServicesPageContent.tsx)
each carry an explicit "Dark/Neutral rollout (this session)" comment
and use `bg-background` -- which DOES react correctly per theme
(verified live: renders #FFFFFF in Neutral). This page has no such
comment and shows no sign of ever going through that rollout -- reads
as a real oversight (the rollout touched the three sub-pages, missed
the parent index page), not a deliberate choice like the sibling
files' gray-400 eyebrow labels (which ARE explicitly documented as
intentional and are NOT touched by this or any other patch in this
pass).

Live-measured impact: text-oxide-text (Dark: #C9825C) rendered against
this page's frozen #F6F3ED background, regardless of active theme,
measured 2.77:1 -- failing 4.5:1. The text color itself is correct
(verified separately: oxide-text clears AA comfortably, 5.42-7.23:1,
against each theme's OWN correct background) -- the background is the
actual bug.

Also fixes the h1's `text-charcoal` -> `text-ink`, the same static-v1-
token issue already found and fixed on book/toc/page.tsx's h1 (same
root cause, same fix, different file).

Usage:
    python tools/patch_contrast_about_index_page.py --dry-run
    python tools/patch_contrast_about_index_page.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/app/about/page.tsx')

ANCHORS = [
    (
        '<main className="bg-paper min-h-screen">',
        '<main className="bg-background min-h-screen">',
    ),
    (
        '<h1 className="font-display text-3xl text-charcoal mb-4">About</h1>',
        '<h1 className="font-display text-3xl text-ink mb-4">About</h1>',
    ),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    new_content = content
    for old, new in ANCHORS:
        count = new_content.count(old)
        if count != 1:
            print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
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
