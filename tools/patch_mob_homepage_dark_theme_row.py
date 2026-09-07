"""
Patch tools/_mob.txt Section 13a: add a dedicated Decision Register row for
the homepage dark-theme bug -- two real bugs, two Gemini review rounds, own
record per Pete's explicit instruction rather than folded into Section 16
closeout narrative. Bumps MOB version.

Usage:
    python tools/patch_mob_homepage_dark_theme_row.py --dry-run
    python tools/patch_mob_homepage_dark_theme_row.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

ANCHOR = (
    "| No forced check-in -- Pete's call on whether/when to pursue a full "
    "v2-token migration for the homepage. Not blocking anything shipped this session. |"
)

NEW_ROW = (
    "\n| Homepage (`<main class=\"home-scope\">`) stayed locked in Warm's "
    "fixed light palette regardless of theme selection -- background AND "
    "text color both non-reactive, confirmed live "
    "| N/A -- infrastructure/accessibility bug, live-verified, closed "
    "| CLOSED this session -- two independent bugs, two Gemini review "
    "rounds, both fixes verified together across all three themes "
    "| Root cause: `.home-scope`'s three tokens (`--home-paper`, "
    "`--home-field-raise`, `--home-slate`) were isolated into their own "
    "rule during the homepage restructure (~2026-08-29) specifically to "
    "avoid colliding with the real `--slate` token, but never given "
    "`[data-theme=\"dark\"]`/`[data-theme=\"neutral\"]` variants at all. "
    "`data-theme` switched correctly on the NavBar and `body` the whole "
    "time -- only the homepage's own content never inherited it. Confirmed "
    "live via direct browser instrumentation (not assumed from source "
    "alone): `body`'s computed background was genuinely `#171512` in Dark "
    "while `<main>` stayed `#f1f3f1`, a hard, visible seam. "
    "\n\n**Fix, part 1 (--home-slate):** added `[data-theme=\"dark\"]`/"
    "`[data-theme=\"neutral\"] .home-scope` blocks. `--home-paper`/"
    "`--home-field-raise` mirror `--field`/`--field-raise` exactly (no new "
    "color judgment). `--home-slate` Dark (`#5B9BD9`) is a genuinely new "
    "value -- computed 6.19:1 vs `#171512`, 5.65:1 vs `#201E1A` (AA "
    "requires 4.5:1). Neutral needs no override: Warm's existing "
    "`#2458A4` already clears AA against `#FFFFFF` (6.98:1). "
    "**Gemini review round 1** confirmed the contrast math but raised an "
    "architectural objection citing a \"v3 Palette Infrastructure\" (a "
    "claimed shipped, verified 21-color 7-per-theme palette), a "
    "cross-theme `--dusty-blue` token, and a specific \"P-12 scope "
    "discipline\" rule rejecting sub-token proliferation. **Independently "
    "verified and found fabricated in the specific-precision sense:** the "
    "real palette is 16 tokens in an inconsistent 6/5/5 split with "
    "mismatched naming across themes, not a uniform 21-color grid; "
    "`--dusty-blue` exists Dark-only and is explicitly tagged "
    "LARGE/DECORATIVE-ONLY, never small text; `--slate` exists in all "
    "three themes but is gray-green, not blue, in every one; P-12 is real "
    "(`tools/_mob.txt`, \"Scope discipline. Every addition answers: who "
    "does this serve and how?\") but its actual text says nothing about "
    "token architecture -- a real principle name with invented content "
    "attached. Original proposal proceeded as designed. "
    "\n\n**Fix, part 2 (--home-ink):** fixing part 1 exposed a second, "
    "pre-existing, unrelated bug -- `page.tsx`/`WayfindingGrid.tsx` use "
    "the hardcoded `text-charcoal` class (`--color-charcoal: #26241F`, a "
    "separate Session-58-era token, confirmed distinct from `--ink`) for "
    "headline/body text. Once the paper background genuinely went dark, "
    "charcoal-on-`#171512` computed at 1.18:1 -- a severe WCAG failure, "
    "confirmed live, invisible until part 1 was actually fixed. Added "
    "`--home-ink` to `.home-scope`: `#26241F` in Warm/Neutral (zero "
    "visual change, matches the existing charcoal value exactly), "
    "`#EDEAE3` in Dark (a direct copy of the existing, already-reviewed "
    "global `--ink` Dark value, not a new color judgment) -- computed "
    "15.17:1 vs `--home-paper`, 13.85:1 vs `--home-field-raise`, 9.93:1 / "
    "7.86:1 at the opacity-80/70 blends the actual body-copy `<p>` "
    "elements use. Swapped all 10 `text-charcoal` occurrences (8 in "
    "`page.tsx`, 2 in `WayfindingGrid.tsx`, confirmed via grep to be the "
    "entire homepage-scoped set -- `WayfindingGrid` is imported nowhere "
    "else) to `text-(--home-ink)`. **Gemini review round 2** confirmed "
    "the contrast math again but raised a factual claim: that `--ink` "
    "Warm is `#14171A` (true) and that `#26241F`/`--color-charcoal` is a "
    "separate \"legacy v1\" token `text-charcoal` actually maps to "
    "(substantively true, though \"v1\" isn't the file's own literal "
    "term -- it calls it \"the Session 58 palette\"), and that this made "
    "the original `--home-ink` proposal incoherent. **Independently "
    "verified: the underlying facts checked out, but the framing of what "
    "was actually proposed did not** -- the original proposal never "
    "claimed `--ink` Warm was `#26241F`; it kept `--home-ink` Warm "
    "unchanged at the existing charcoal value and only borrowed `--ink`'s "
    "*Dark* value for the dark override. A one-line misreading, not a "
    "substantive error -- logged for accuracy, not treated as a fabrication "
    "on the scale of round 1's invented palette. The real, separate "
    "architectural question round 2 surfaced -- a `globals.css` comment "
    "stating v2 tokens were meant to reach the homepage \"starting with "
    "the Stage 4 homepage proof point\" -- is tracked as its own parked "
    "row below, deliberately not acted on here. "
    "\n\n**Final verification, all three themes, computed styles plus "
    "screenshots, both fixes together:**\n\n"
    "| Theme | `main` background | Headline color | Accent color |\n"
    "|---|---|---|---|\n"
    "| Warm | `#F1F3F1` (unchanged) | `#26241F` (unchanged) | `#2458A4` (unchanged) |\n"
    "| Dark | `#171512` | `#EDEAE3` | `#5B9BD9` |\n"
    "| Neutral | `#FFFFFF` | `#26241F` (no override needed) | `#2458A4` (no override needed) |\n\n"
    "Zero regression in Warm/Neutral, both bugs fixed in Dark. A dev-server "
    "file-watcher/build-cache staleness issue (unrelated to the fix itself) "
    "cost two separate kill/clear-`.next`/restart cycles before the served "
    "CSS actually matched source -- confirmed via raw network fetch each "
    "time, not assumed from a process restart alone. "
    "| This session (Claude Code), 2026-09-07 "
    "| Closed -- no further check-in. If a new theme-reactivity gap "
    "surfaces on the homepage or elsewhere, treat it as a new incident, "
    "not a reopening of this row. |"
)

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.284"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.285"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    for needle, label in [(ANCHOR, 'anchor row end'), (OLD_VERSION_HEADER, 'version header')]:
        count = content.count(needle)
        if count != 1:
            print(f'ERROR: {label} found {count} times, expected exactly 1. Aborting.', file=sys.stderr)
            sys.exit(1)

    idx = content.find(ANCHOR) + len(ANCHOR)
    new_content = content[:idx] + NEW_ROW + content[idx:]
    new_content = new_content.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)

    if args.dry_run:
        print('DRY RUN -- anchor and version header found exactly once, insertion would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
