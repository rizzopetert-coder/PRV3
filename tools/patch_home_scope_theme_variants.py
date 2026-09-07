"""
Patch web/app/globals.css: add [data-theme="dark"] .home-scope and
[data-theme="neutral"] .home-scope overrides. Closes the gap where
<main class="home-scope bg-(--home-paper)"> stayed locked in Warm's fixed
light palette (--home-paper/--home-field-raise/--home-slate) regardless of
theme, while the NavBar and body correctly switched -- confirmed live via
browser instrumentation this session, pre-existing since the homepage
restructure (~2026-08-29), unrelated to any other work this session.

--home-paper/--home-field-raise mirror --field/--field-raise exactly (pure
surface tones, no new color judgment). --home-slate dark (#5B9BD9) is the
one new value: computed WCAG contrast 6.19:1 vs #171512, 5.65:1 vs #201E1A
(AA requires 4.5:1). Neutral needs no --home-slate override -- Warm's
existing #2458A4 already clears AA against #FFFFFF (6.98:1, computed).

A Gemini-proposed alternative (reuse an existing "v3 Palette Infrastructure"
/ --dusty-blue / P-12 scope-discipline citation) was independently verified
against live source and did not hold up: no 21-color 7-per-theme palette
exists (actual: 16 tokens, 6/5/5 split, inconsistent naming); --dusty-blue
exists Dark-only and is explicitly tagged LARGE/DECORATIVE-ONLY, never small
text; --slate exists in all three themes but is gray-green, not blue; P-12
(tools/_mob.txt:129) is real but its actual text ("Scope discipline. Every
addition answers: who does this serve and how?") says nothing about token
architecture. No existing token covers this use case -- new values are the
correct fix.

Usage:
    python tools/patch_home_scope_theme_variants.py --dry-run
    python tools/patch_home_scope_theme_variants.py --write
"""
import argparse
import pathlib
import sys

CSS_PATH = pathlib.Path('web/app/globals.css')

ANCHOR = """.home-scope {
  --home-paper: #F1F3F1;
  --home-field-raise: #E6E9E7;
  --home-slate: #2458A4;
}
"""

REPLACEMENT = """.home-scope {
  --home-paper: #F1F3F1;
  --home-field-raise: #E6E9E7;
  --home-slate: #2458A4;
}

/* .home-scope dark/neutral variants (2026-09-06) -- closes the gap where
   <main class="home-scope"> stayed locked in this fixed light palette
   across all three themes: data-theme switched correctly on the NavBar
   and body, but homepage content never inherited it, confirmed live via
   browser instrumentation (glaring in Dark, near-invisible but
   structurally identical in Neutral, since #F1F3F1 sits close to
   Neutral's own #FFFFFF). Pre-existing since the homepage restructure
   session (~2026-08-29), unrelated to any later work.

   --home-paper/--home-field-raise mirror --field/--field-raise exactly --
   pure surface tones with no brand-color meaning, so reusing the
   already-reviewed values carries no new judgment. --home-slate is the
   one new color: Warm's #2458A4 already clears AA against Neutral's
   #FFFFFF (6.98:1, computed), so Neutral needs no override here. Dark
   needs a lightened blue for legibility against #171512 -- #5B9BD9
   computed at 6.19:1 vs #171512 and 5.65:1 vs #201E1A (AA requires
   4.5:1), same hue family as Warm's value, same lighten-for-dark
   approach already used for --slate's own Warm->Dark shift above.

   No existing token covers this: --dusty-blue is Dark-only (line ~113)
   and explicitly tagged LARGE/DECORATIVE-ONLY -- never small text, which
   is what these chart-axis labels are; --slate exists in all three
   themes but is gray-green, not blue, in every one of them. Confirmed
   directly against source, not assumed -- a proposed alternative citing
   a "v3 Palette Infrastructure" and a specific P-12 scope-discipline
   rule did not survive independent verification: the real palette is 16
   tokens in an inconsistent 6/5/5 split, not a uniform 21-color grid,
   and P-12's actual text (tools/_mob.txt) is a generic design question
   with nothing about token architecture. */
[data-theme="dark"] .home-scope {
  --home-paper: #171512;
  --home-field-raise: #201E1A;
  --home-slate: #5B9BD9;
}

[data-theme="neutral"] .home-scope {
  --home-paper: #FFFFFF;
  --home-field-raise: #EFE6D0;
}
"""


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = CSS_PATH.read_text(encoding='utf-8')

    count = content.count(ANCHOR)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected exactly 1. Aborting.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(ANCHOR, REPLACEMENT, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
        print('--- new block ---')
        print(REPLACEMENT)
    else:
        CSS_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
