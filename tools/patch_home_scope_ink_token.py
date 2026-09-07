"""
Patch web/app/globals.css: add --home-ink to .home-scope (Warm/Neutral base)
and [data-theme="dark"] .home-scope. Closes the second half of the homepage
dark-theme bug: page.tsx/WayfindingGrid.tsx use the hardcoded, non-reactive
text-charcoal class (--color-charcoal: #26241F, a separate Session 58 -era
token, confirmed distinct from --ink) for headline/body text. Once
--home-paper correctly went dark (prior patch, this session), charcoal-on-
near-black computed at 1.18:1 contrast -- a severe WCAG failure, confirmed
live in browser. --home-ink #26241F in Warm/Neutral is a zero-visual-change
copy of the existing text-charcoal value; #EDEAE3 in Dark is a direct copy
of the existing, already-reviewed global --ink dark value (not a new color
judgment) -- computed contrast 15.17:1 vs --home-paper dark, 13.85:1 vs
--home-field-raise dark, 9.93:1 / 7.86:1 at the opacity-80/70 blends several
homepage <p> elements actually use. Neutral needs no override: #26241F vs
#FFFFFF computes at 15.5:1, already far above AA.

A Gemini-proposed alternative (swap text-charcoal directly to text-(--ink)
everywhere, accepting Warm's homepage text shifts from #26241F to #14171A)
was independently verified and rejected: --ink and --color-charcoal are
confirmed genuinely distinct tokens (globals.css:30 vs :159), and text-
(--ink) has zero precedent anywhere in the codebase today (grepped, 0
matches) -- adopting it here would introduce an unreviewed, out-of-scope
Warm-theme color change as a side effect of a Dark-theme bug fix, not
"catching up" to an established pattern.

This is a values-only CSS addition plus 10 class-name swaps in the two
files that actually use text-charcoal within .home-scope (page.tsx: 8,
WayfindingGrid.tsx: 2) -- confirmed via grep that WayfindingGrid is
imported only by page.tsx, so no other route is touched.

Usage:
    python tools/patch_home_scope_ink_token.py --dry-run
    python tools/patch_home_scope_ink_token.py --write
"""
import argparse
import pathlib
import sys

CSS_PATH = pathlib.Path('web/app/globals.css')
PAGE_PATH = pathlib.Path('web/app/page.tsx')
GRID_PATH = pathlib.Path('web/components/home/WayfindingGrid.tsx')

CSS_ANCHOR = """.home-scope {
  --home-paper: #F1F3F1;
  --home-field-raise: #E6E9E7;
  --home-slate: #2458A4;
}"""

CSS_REPLACEMENT = """.home-scope {
  --home-paper: #F1F3F1;
  --home-field-raise: #E6E9E7;
  --home-slate: #2458A4;
  /* --home-ink (2026-09-07): closes the second half of the homepage
     dark-theme bug -- page.tsx/WayfindingGrid.tsx use the hardcoded
     text-charcoal class (--color-charcoal, a separate Session 58-era
     token, confirmed distinct from --ink) for headline/body text.
     #26241F here is a zero-visual-change copy of that existing value
     -- Warm/Neutral render identically to before. Dark's value (below)
     is the one that matters: charcoal-on-the-new-correct-dark-paper
     computed at 1.18:1, a severe WCAG failure, confirmed live in
     browser once the paper fix (above) actually started working. */
  --home-ink: #26241F;
}"""

DARK_ANCHOR = """[data-theme="dark"] .home-scope {
  --home-paper: #171512;
  --home-field-raise: #201E1A;
  --home-slate: #5B9BD9;
}"""

DARK_REPLACEMENT = """[data-theme="dark"] .home-scope {
  --home-paper: #171512;
  --home-field-raise: #201E1A;
  --home-slate: #5B9BD9;
  /* = global --ink dark exactly, not a new color -- computed 15.17:1
     vs --home-paper, 13.85:1 vs --home-field-raise, 9.93:1 / 7.86:1 at
     the opacity-80/70 blends the actual body-copy <p> elements use.
     A "swap text-charcoal for text-(--ink) everywhere" alternative was
     considered and rejected: --ink and --color-charcoal are genuinely
     distinct tokens (confirmed, not the same value under two names),
     and text-(--ink) has zero precedent anywhere in this codebase --
     adopting it here would shift Warm's homepage text color as an
     unreviewed side effect of a Dark-theme fix, not match an existing
     pattern. */
  --home-ink: #EDEAE3;
}"""

# text-charcoal -> text-(--home-ink), preserving surrounding classes exactly
TEXT_SWAPS = [
    'text-charcoal',
]


def swap_text_charcoal(content: str) -> tuple[str, int]:
    # Only ever appears as the exact token "text-charcoal" inside a
    # className string in these two files -- safe as a literal replace,
    # verified by grep before this script was written (10 occurrences
    # total: 8 in page.tsx, 2 in WayfindingGrid.tsx).
    count = content.count('text-charcoal')
    return content.replace('text-charcoal', 'text-(--home-ink)'), count


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    css_content = CSS_PATH.read_text(encoding='utf-8')
    page_content = PAGE_PATH.read_text(encoding='utf-8')
    grid_content = GRID_PATH.read_text(encoding='utf-8')

    if css_content.count(CSS_ANCHOR) != 1:
        print(f'ERROR: CSS base anchor found {css_content.count(CSS_ANCHOR)} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    if css_content.count(DARK_ANCHOR) != 1:
        print(f'ERROR: CSS dark anchor found {css_content.count(DARK_ANCHOR)} times, expected 1.', file=sys.stderr)
        sys.exit(1)

    new_css = css_content.replace(CSS_ANCHOR, CSS_REPLACEMENT, 1)
    new_css = new_css.replace(DARK_ANCHOR, DARK_REPLACEMENT, 1)

    new_page, page_count = swap_text_charcoal(page_content)
    new_grid, grid_count = swap_text_charcoal(grid_content)

    if page_count != 8:
        print(f'ERROR: page.tsx has {page_count} text-charcoal occurrences, expected 8. Aborting.', file=sys.stderr)
        sys.exit(1)
    if grid_count != 2:
        print(f'ERROR: WayfindingGrid.tsx has {grid_count} text-charcoal occurrences, expected 2. Aborting.', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print('DRY RUN -- all anchors/counts confirmed exactly as expected.')
        print(f'globals.css: {len(css_content)} -> {len(new_css)} (delta {len(new_css) - len(css_content)})')
        print(f'page.tsx: {page_count} text-charcoal -> text-(--home-ink) swaps')
        print(f'WayfindingGrid.tsx: {grid_count} text-charcoal -> text-(--home-ink) swaps')
        print('--- new .home-scope base block ---')
        print(CSS_REPLACEMENT)
        print('--- new dark block ---')
        print(DARK_REPLACEMENT)
    else:
        CSS_PATH.write_text(new_css, encoding='utf-8')
        PAGE_PATH.write_text(new_page, encoding='utf-8')
        GRID_PATH.write_text(new_grid, encoding='utf-8')
        print('WRITE complete.')
        print(f'globals.css: {len(css_content)} -> {len(new_css)}')
        print(f'page.tsx: {page_count} swaps applied')
        print(f'WayfindingGrid.tsx: {grid_count} swaps applied')


if __name__ == '__main__':
    main()
