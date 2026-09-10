"""
web/app/globals.css, web/app/page.tsx, web/components/home/WayfindingGrid.tsx:
fix three confirmed WCAG AA contrast failures found during the homepage
audit (2026-09-10), following the existing --home-slate/paper/field-raise
isolation pattern -- new --home-* names, never shadowing a real v2 token.

All three candidates margin-searched with real contrast math against the
live .home-scope background values, not guessed:

1. CTA button (page.tsx CloserSection) -- was bg-charcoal text-white
   hover:bg-gray-700, all fixed (non-theme-reactive) values.
   --home-cta-bg / --home-cta-text, new tokens.
   Warm/Neutral: bg=#26241F (same look as before, already passing --
   13.90/15.50 contrast), text=#FFFFFF.
   Dark: bg=#5B9BD9 (reuses --home-slate's own Dark value -- already
   vetted, already live on this exact page), text=#26241F (reuses
   --color-charcoal). Mathematically required to flip BOTH bg and text
   simultaneously: WCAG's own formula proves no color can satisfy both
   "clears 4.5:1 against near-black --home-paper Dark (#171512)" and
   "white text still clears 4.5:1 against it" at once (the luminance
   ranges these two constraints require don't overlap) -- a light bg
   with dark text is the only viable shape for a Dark-theme CTA here,
   not an arbitrary color choice. Live-computed: bg vs page 6.19:1
   (was 1.18:1), text vs bg 5.27:1 (was passing already but on the
   wrong axis). Hover state changed from hover:bg-gray-700 (also a
   fixed, non-reactive color, and still only 1.77:1 in Dark) to
   hover:opacity-90, matching WayfindingGrid.tsx's own existing card
   hover convention already used elsewhere on this same page.

2. Footer text (page.tsx) -- was text-gray-400 (#99A1AF fixed), failing
   Warm (2.33:1) and Neutral (2.60:1), passing Dark only by coincidence
   (7.00:1). --home-footer-text, new token, per theme.
   Reuses --home-slate's own literal value in each theme (Warm/Neutral
   #2458A4, Dark #5B9BD9) rather than inventing a new hue -- computed
   6.26:1 (Warm), 6.98:1 (Neutral), 6.19:1 (Dark). Dark's number moves
   from 7.00 to 6.19 -- still comfortably clears AA (4.5:1), not a
   regression into failure, just no longer an accidental higher margin
   from an unrelated gray.

3. Avatar circle (page.tsx VoiceSection) -- bg-(--home-slate) text-white,
   the bg is already theme-reactive but white text was never checked
   against --home-slate's own Dark value, which was tuned for a
   different consumer (body text against the page, not text rendered
   on top of the slate fill itself). Failing Dark at 2.94:1.
   --home-avatar-text, new token, per theme. Warm/Neutral unchanged
   (#FFFFFF, already passing at 6.98:1). Dark: #26241F (reuses
   --color-charcoal, same choice as the CTA text fix above) -- computed
   5.27:1. --home-slate's own value is NOT touched -- its Dark tuning
   has its own already-correct reason (body-text contrast) that must
   not regress.

Usage:
    python tools/patch_homepage_contrast_fixes.py --dry-run
    python tools/patch_homepage_contrast_fixes.py --write
"""
import argparse
import pathlib
import sys

CSS_PATH = pathlib.Path('web/app/globals.css')
PAGE_PATH = pathlib.Path('web/app/page.tsx')
GRID_PATH = pathlib.Path('web/components/home/WayfindingGrid.tsx')

# ---- globals.css edits -----------------------------------------------------

CSS_BASE_OLD = '''.home-scope {
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
}'''

CSS_BASE_NEW = '''.home-scope {
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
  /* --home-cta-bg / --home-cta-text / --home-footer-text /
     --home-avatar-text (2026-09-10): three more fixed, non-reactive
     Tailwind colors found by the same-shaped audit as --home-ink above
     (bg-charcoal/text-white/hover:bg-gray-700 on the CTA button,
     text-gray-400 on the footer, text-white on the avatar circle's
     --home-slate fill). Warm/Neutral values here are zero-visual-change
     copies of what was already rendering -- the Dark overrides below are
     what actually fix each failure. See each token's own margin-search
     detail on the [data-theme="dark"] .home-scope block below. */
  --home-cta-bg: #26241F;
  --home-cta-text: #FFFFFF;
  --home-footer-text: #2458A4;
  --home-avatar-text: #FFFFFF;
}'''

CSS_DARK_OLD = '''  --home-ink: #EDEAE3;
}'''

CSS_DARK_NEW = '''  --home-ink: #EDEAE3;
  /* --home-cta-bg / --home-cta-text (2026-09-10): CTA button was
     bg-charcoal text-white, computed at 1.18:1 button-vs-page in Dark --
     a severe failure (both near-black). WCAG's own contrast formula
     proves no single color can clear 4.5:1 against this near-black
     --home-paper (#171512) while ALSO letting white text clear 4.5:1
     against it -- the two luminance ranges required don't overlap, so a
     light bg + dark text is the only viable shape, not a stylistic
     choice. #5B9BD9 reuses --home-slate's own Dark value (already
     vetted, already live on this page's avatar/labels) rather than
     inventing a new hue -- computed 6.19:1 vs --home-paper. #26241F
     reuses --color-charcoal as the text color -- computed 5.27:1
     against the new bg. Both clear 4.5:1 with real margin. */
  --home-cta-bg: #5B9BD9;
  --home-cta-text: #26241F;
  /* --home-footer-text (2026-09-10): text-gray-400 (#99A1AF, fixed)
     happened to clear Dark by coincidence (7.00:1) while failing Warm
     and Neutral -- see the base .home-scope block's own comment for the
     full failure detail. Reuses --home-slate's own Dark value here too,
     for the same "intentionally quiet, not a mismatched gray" reason as
     Warm/Neutral -- computed 6.19:1 vs --home-paper, still comfortably
     clears AA (4.5:1), not a regression into failure. */
  --home-footer-text: #5B9BD9;
  /* --home-avatar-text (2026-09-10): the avatar circle's bg is already
     theme-reactive (--home-slate), but white text was never checked
     against --home-slate's OWN Dark value, which was tuned for a
     different consumer (body-text-against-page contrast, see that
     token's own comment above) -- computed 2.94:1 with white text, a
     real failure. #26241F (same --color-charcoal reuse as the CTA text
     fix above) computes at 5.27:1. --home-slate's own value is
     untouched -- its Dark tuning's original reason still holds. */
  --home-avatar-text: #26241F;
}'''

# ---- page.tsx edits ---------------------------------------------------------

PAGE_AVATAR_OLD = '''        <div className="w-10 h-10 rounded-full bg-(--home-slate) text-white flex items-center justify-center font-display text-lg shrink-0">'''
PAGE_AVATAR_NEW = '''        <div className="w-10 h-10 rounded-full bg-(--home-slate) text-(--home-avatar-text) flex items-center justify-center font-display text-lg shrink-0">'''

PAGE_CTA_OLD = '''      <Link
        href="/diagnostic"
        className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 hover:bg-gray-700 transition-colors"
      >
        Begin the diagnostic →
      </Link>'''
PAGE_CTA_NEW = '''      <Link
        href="/diagnostic"
        className="inline-block bg-(--home-cta-bg) text-(--home-cta-text) font-ui text-sm font-medium px-6 py-3 hover:opacity-90 transition-opacity"
      >
        Begin the diagnostic →
      </Link>'''

PAGE_FOOTER_OLD = '''        <p className="font-ui text-sm text-gray-400 text-center">
          Principal Resolution.
        </p>'''
PAGE_FOOTER_NEW = '''        <p className="font-ui text-sm text-(--home-footer-text) text-center">
          Principal Resolution.
        </p>'''

EDITS = [
    ('globals.css base .home-scope: add 4 new tokens', CSS_PATH, CSS_BASE_OLD, CSS_BASE_NEW),
    ('globals.css [data-theme="dark"] .home-scope: add 4 new tokens', CSS_PATH, CSS_DARK_OLD, CSS_DARK_NEW),
    ('page.tsx: avatar circle text color', PAGE_PATH, PAGE_AVATAR_OLD, PAGE_AVATAR_NEW),
    ('page.tsx: CTA button bg/text/hover', PAGE_PATH, PAGE_CTA_OLD, PAGE_CTA_NEW),
    ('page.tsx: footer text color', PAGE_PATH, PAGE_FOOTER_OLD, PAGE_FOOTER_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    contents = {}
    errors = []
    for label, path, old, new in EDITS:
        if path not in contents:
            contents[path] = path.read_text(encoding='utf-8')
        count = contents[path].count(old)
        if count != 1:
            errors.append(f'"{label}" ({path}): anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_contents = dict(contents)
    for label, path, old, new in EDITS:
        new_contents[path] = new_contents[path].replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        for path in contents:
            delta = len(new_contents[path]) - len(contents[path])
            print(f'  {path}: old length {len(contents[path])}, new length {len(new_contents[path])}, delta {delta:+d}')
    else:
        for path in contents:
            path.write_text(new_contents[path], encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied across {len(contents)} files.')
        for path in contents:
            delta = len(new_contents[path]) - len(contents[path])
            print(f'  {path}: old length {len(contents[path])}, new length {len(new_contents[path])}, delta {delta:+d}')


if __name__ == '__main__':
    main()
