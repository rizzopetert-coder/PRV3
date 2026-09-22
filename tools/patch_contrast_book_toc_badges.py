"""
web/app/book/toc/page.tsx: swap the state-card signature badges from the
static v1 `text-slate border-slate` (hardcoded blue #4A6B85, doesn't
react to theme) to the theme-reactive v2 `--slate` token, per Pete's
explicit direction -- consistent with how the rest of the token system
behaves, including this same file's own filter-chip badges two lines
away (line 590-591, `border-(--slate) bg-(--slate)`).

Real background confirmed live (DOM walk, not assumed): these badges
sit inside a StateCard's own `bg-field` container, not the page's
outer background -- #E9E7E2 (Warm), #171512 (Dark), #FFFFFF (Neutral).

Resulting color per theme, confirmed live via actual axe-core
measurement against that real background (not hand-calculated ratios --
this component's 10px font is even smaller than ContextOrientation's,
where anti-aliasing made hand math unreliable, so this was verified
empirically by temporarily applying the real CSS variable and re-
running axe fresh, not trusted from arithmetic alone):

  Warm:    #5C6B66 (a muted green-gray) on #E9E7E2 -- clears AA
  Dark:    #8FA39C (a lighter blue-green) on #171512 -- clears AA
  Neutral: #6E7276 (a neutral gray) on #FFFFFF -- clears AA

Visual identity note, not a fix decision (Pete already made the call
this fixes): this changes the badges' color from a fixed blue
(#4A6B85) in every theme to a different hue per theme -- green-gray in
Warm, blue-green in Dark, neutral gray in Neutral. Not just "darker
blue," a real hue shift. Flagged here so the actual resulting colors
are visible in the diff, not asserting Pete hasn't already weighed
this -- he has, this docstring just makes the tradeoff legible.

Usage:
    python tools/patch_contrast_book_toc_badges.py --dry-run
    python tools/patch_contrast_book_toc_badges.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/app/book/toc/page.tsx')

OLD = '''              className="font-mono text-[10px] uppercase tracking-wide text-slate border border-slate rounded-full px-2 py-0.5"'''
NEW = '''              className="font-mono text-[10px] uppercase tracking-wide text-(--slate) border border-(--slate) rounded-full px-2 py-0.5"'''


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
