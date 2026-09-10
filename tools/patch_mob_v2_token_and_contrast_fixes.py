"""
tools/_mob.txt: closes the v2 token migration architectural question
(Section 13a, 2026-09-07 row) and logs the three newly-found-and-fixed
homepage contrast bugs (CTA button, footer text, avatar circle) as
their own closed Section 13a entry, same detail standard as the Sept 7
homepage dark-theme fix entry. Also removes the now-closed v2 token
migration item from the active Priority Queue and bumps the MOB
version (real shipped code + a resolved architectural question).

Four edits:
1. Version header: v4.294 -> v4.295.
2. Close the existing v2 token migration Section 13a row (line 1416)
   -- status and next-check-in columns updated in place, per the
   file's own established self-correction convention.
3. Insert a new Section 13a row for the three contrast-bug fixes,
   directly after the Sept 7 homepage dark-theme row it extends.
4. Append a new Section 16 closeout entry with an updated Priority
   Queue (v2 token migration item removed, remaining items
   renumbered).

Usage:
    python tools/patch_mob_v2_token_and_contrast_fixes.py --dry-run
    python tools/patch_mob_v2_token_and_contrast_fixes.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

# ---- Edit 1: version header -------------------------------------------------

VERSION_OLD = '\\\\\\#\\\\\\# MOB v4.294'
VERSION_NEW = '\\\\\\#\\\\\\# MOB v4.295'

# ---- Edit 2: close the existing v2 token migration row ---------------------

ROW_STATUS_OLD = '| Parked, flagged not resolved -- surfaced while fixing the homepage dark-theme bug (this session) |'
ROW_STATUS_NEW = '| RESOLVED 2026-09-10 -- re-examined and confirmed correctly settled, not reopened |'

ROW_TAIL_OLD = 'per Pete\'s direct instruction. | This session (Claude Code), 2026-09-07 | No forced check-in -- Pete\'s call on whether/when to pursue a full v2-token migration for the homepage. Not blocking anything shipped this session. |'

ROW_TAIL_NEW = '''per Pete's direct instruction. **RE-EXAMINED 2026-09-10, this session, per Pete's explicit instruction to close this out properly:** live-verified via `getComputedStyle` (not source-reading alone) across all three themes that `--home-ink` does NOT mirror `--ink` in Warm or Neutral -- Warm: `--home-ink` `#26241F` vs. `--ink` `#14171A` (different colors); Neutral: `--home-ink` `#26241F` (inherited, no override) vs. `--ink` `#34383C` (different colors); only Dark genuinely matches (`#EDEAE3` both). Confirms the Sept 7 rejection was based on a real, still-valid fact, not a stale assumption -- `--home-ink` was deliberately authored to match `--color-charcoal` (the token actually already in use sitewide), not `--ink`, and adopting `--ink` now would still be an unreviewed, real color shift in two of three themes. **v2 token migration (`--home-ink`/`--ink`) re-examined 2026-09-10 -- confirmed correctly settled as isolated in the Sept 7 session; no action needed.** | This session (Claude Code), 2026-09-07; re-examined and closed 2026-09-10 (Claude Code) | Closed -- no further check-in. Reopens only if Pete decides to deliberately migrate the homepage onto v2 tokens as a new, separate design decision, not a re-investigation of this row. |'''

# ---- Edit 3: new Section 13a row for the three contrast-bug fixes ----------

NEW_ROW_ANCHOR_OLD = '''Zero regression in Warm/Neutral, both bugs fixed in Dark. A dev-server file-watcher/build-cache staleness issue (unrelated to the fix itself) cost two separate kill/clear-`.next`/restart cycles before the served CSS actually matched source -- confirmed via raw network fetch each time, not assumed from a process restart alone. | This session (Claude Code), 2026-09-07 | Closed -- no further check-in. If a new theme-reactivity gap surfaces on the homepage or elsewhere, treat it as a new incident, not a reopening of this row. |'''

NEW_ROW_ANCHOR_NEW = NEW_ROW_ANCHOR_OLD + '''

| Homepage full contrast audit (following the Sept 7 dark-theme fix and the same-session v2-token re-examination) found three more fixed, non-theme-reactive Tailwind colors, all confirmed WCAG AA failures -- CTA button, footer text, avatar circle text | N/A -- infrastructure/accessibility bug, live-verified, closed | CLOSED this session -- three separate fixes, all margin-searched (not guessed) and live-verified via `getComputedStyle` plus canvas-normalized contrast computation across all three themes | Full audit of `page.tsx`/`WayfindingGrid.tsx` for hardcoded `bg-*`/`text-*`/`border-*`/`hover:*` utilities not backed by a `--home-*` or existing reactive token, requested after the Sept 7 fix and the same-session v2-token re-examination both surfaced the general pattern. First verification pass caught its own bug before reporting: Tailwind v4 emits `lab()` color functions, not plain `rgb()` -- a first regex-based parser misread `lab()` channel values as raw RGB, producing garbage numbers (e.g. a false `#420108` reading for `text-gray-400`); caught and replaced with a canvas-`getImageData` normalization (draws each computed color to a 1x1 canvas, reads back real RGB, robust to any CSS color-function format) before any real numbers were reported or acted on.

**Bug 1 -- CTA button** (`page.tsx` `CloserSection`, was `bg-charcoal text-white hover:bg-gray-700`, all three fixed non-reactive values): computed 1.18:1 button-vs-page contrast in Dark (`#26241F` on `#171512`, both near-black) -- a severe failure, confirmed visually via screenshot (the button box has no visible boundary against the page; only its white text is legible). WCAG's own contrast formula proves this can't be patched with a lighter background alone while keeping white text: the luminance range required for "bg clears 4.5:1 against `#171512`" (>= ~0.207) and the range required for "white text still clears 4.5:1 against that same bg" (<= ~0.183) don't overlap -- a light bg with dark text is the only mathematically viable shape for a Dark-theme CTA here, not a stylistic choice. New tokens `--home-cta-bg`/`--home-cta-text`: Warm/Neutral unchanged (`#26241F`/`#FFFFFF`, zero visual change, already passing at 13.90:1/15.50:1). Dark: `#5B9BD9` (reuses `--home-slate`'s own already-vetted Dark value, not a new hue) / `#26241F` (reuses `--color-charcoal`) -- computed 6.19:1 button-vs-page, 5.27:1 text-vs-button, both clearing 4.5:1 with real margin. Hover state changed from `hover:bg-gray-700` (also fixed/non-reactive, and only 1.77:1 in Dark even as a hover state) to `hover:opacity-90`, matching `WayfindingGrid.tsx`'s own existing card-hover convention already used elsewhere on this same page.

**Bug 2 -- Footer text** (`page.tsx`, was `text-gray-400`, real resolved value `#99A1AF`, fixed/non-reactive): failing Warm (2.33:1) and Neutral (2.60:1), passing Dark only by coincidence (7.00:1) -- the opposite failure direction from the CTA, since a mid-gray reads fine against near-black Dark but poorly against the light Warm/Neutral backgrounds. New token `--home-footer-text`, per theme, reuses `--home-slate`'s own literal value in each theme rather than inventing a new hue (Warm/Neutral `#2458A4`, Dark `#5B9BD9`) -- computed 6.26:1 (Warm), 6.98:1 (Neutral), 6.19:1 (Dark). Dark's margin moves from 7.00 to 6.19 -- still comfortably clears AA, not a regression into failure, just no longer an accidental higher margin from an unrelated gray.

**Bug 3 -- Avatar circle text** (`page.tsx` `VoiceSection`, `bg-(--home-slate) text-white`) -- the background here was already theme-reactive, but white text was never checked against `--home-slate`'s own Dark value, which was tuned for a different consumer (body-text-against-page contrast, per that token's own Sept 6 comment) -- computed 2.94:1 with white text, a real failure found by the "nothing else" audit, not named in the original ask. New token `--home-avatar-text`, per theme: Warm/Neutral unchanged (`#FFFFFF`, already passing at 6.98:1). Dark: `#26241F` (same `--color-charcoal` reuse as the CTA text fix) -- computed 5.27:1. `--home-slate`'s own value is untouched -- its Dark tuning's original reason still holds, this only adds a second, independent consumer-appropriate text color on top of it.

**Verification:** all nine live-measured numbers (3 fixes x 3 themes) match the margin-searched candidates exactly, confirmed via `getComputedStyle` plus the corrected canvas-based contrast computation, not source-level assertion. `tsc --noEmit` clean. Screenshots captured for all three themes at page-top (confirming theme-switching itself renders correctly) plus a pre-fix Dark-theme screenshot of the CTA specifically, visually confirming the 1.18:1 failure before the fix landed -- below-the-fold post-fix screenshots of the three specific elements could not be captured this session (the Browser pane was in a hidden state that blocks any scroll-dependent repaint, a `computer scroll`/`scrollIntoView` action either times out or returns a stale blank frame; confirmed reproducible, not a one-off, and confirmed NOT a contrast/render bug in the app itself via `get_page_text` showing full correct content and `getComputedStyle` returning the exact expected live values regardless) -- the numeric `getComputedStyle` verification is the authoritative evidence for this entry, screenshots are supplementary where obtainable. Files changed: `web/app/globals.css` (four new tokens across the base and `[data-theme="dark"] .home-scope` blocks -- Neutral needs no override, inherits the base values exactly like `--home-slate` already does), `web/app/page.tsx` (three className updates -- avatar text, CTA bg/text/hover, footer text). `WayfindingGrid.tsx` needed no change -- the earlier full audit confirmed no other hardcoded, non-reactive color utilities exist there beyond `--home-ink`, already fixed Sept 7. | This session (Claude Code), 2026-09-10 | Closed -- no further check-in. If a new non-reactive color surfaces on the homepage or elsewhere, treat it as a new incident, not a reopening of this row. |'''

# ---- Edit 4: append new Section 16 closeout entry --------------------------

TAIL_OLD = '''### On the horizon -- updated Priority Queue
1. Mobile z-index collision (AssemblyPanel vs. phase-transition bars)
   -- still unconfirmed on a real device, unchanged from prior sessions.
2. extreme_high_confidence calibration tier at 0/1 -- unchanged.
3. v2 token migration for the homepage -- unchanged, architectural only.
4. damages_cap_treatment remains unconsumed by any pricing logic --
   the entire workstream was future-proofing data quality ahead of a
   pricing extension, not fixing a live bug. Worth remembering when
   that extension eventually gets scoped: the five-value enum, the
   AL/GA key-set constraint, and every state's specific citation are
   all sitting there ready to build on.'''

TAIL_NEW = '''### On the horizon -- updated Priority Queue
1. Mobile z-index collision (AssemblyPanel vs. phase-transition bars)
   -- still unconfirmed on a real device, unchanged from prior sessions.
2. extreme_high_confidence calibration tier at 0/1 -- unchanged.
3. v2 token migration for the homepage -- unchanged, architectural only.
4. damages_cap_treatment remains unconsumed by any pricing logic --
   the entire workstream was future-proofing data quality ahead of a
   pricing extension, not fixing a live bug. Worth remembering when
   that extension eventually gets scoped: the five-value enum, the
   AL/GA key-set constraint, and every state's specific citation are
   all sitting there ready to build on.

## SESSION CLOSEOUT (2026-09-10, continuation session) -- homepage v2
## token question closed, three contrast bugs found and fixed

### One-line summary
The v2 token migration architectural question (Section 13a, 2026-09-07
row) is re-examined and closed: `--home-ink`'s isolation from `--ink`
was confirmed correct, live, not a stale assumption. A follow-on full
contrast audit of the homepage found and fixed three more real WCAG AA
failures -- CTA button, footer text, avatar circle -- none of them
previously documented, all three margin-searched (not guessed) and
live-verified.

### v2 token migration -- closed
Live `getComputedStyle` measurement across all three themes confirmed
`--home-ink` matches `--ink` only in Dark (`#EDEAE3` both); Warm and
Neutral genuinely differ (`--home-ink` mirrors `--color-charcoal`, a
separate Session-58-era token, in both). The Sept 7 rejection of
swapping to `text-(--ink)` was correct and remains correct -- see the
updated Section 13a row for full detail. No code changed by this part
-- documentation closure only.

### Three contrast bugs found and fixed
Full detail in the new Section 13a row (same entry as the closure
above, added directly after it). Summary: CTA button was 1.18:1 in
Dark (mathematically required both a new bg AND a new text color,
proven via the WCAG formula itself, not a style choice); footer text
was failing Warm (2.33:1) and Neutral (2.60:1), the opposite failure
direction from the CTA; avatar circle text was 2.94:1 in Dark, a
second-order bug where `--home-slate`'s Dark value was correctly tuned
for one consumer (body text) but never checked against a second
(white text rendered on top of it as a fill). Four new tokens:
`--home-cta-bg`, `--home-cta-text`, `--home-footer-text`,
`--home-avatar-text` -- same `.home-scope`/`[data-theme] .home-scope`
isolation pattern as `--home-slate`/`--home-paper`/`--home-field-raise`,
no bare names shadowing a real v2 token.

### Verification
All nine live-measured numbers (3 fixes x 3 themes) match the
margin-searched candidates exactly. `tsc --noEmit` clean. Screenshots
obtained for all three themes at page-top, plus one pre-fix Dark-theme
screenshot of the CTA specifically; below-the-fold post-fix screenshots
of the three fixed elements could not be captured this session -- the
Browser pane was in a hidden state that blocks scroll-dependent
repaint, confirmed reproducible and confirmed unrelated to the app
itself (`get_page_text` and `getComputedStyle` both returned full,
correct live values regardless). The numeric verification is the
authoritative evidence here, not the screenshots.

### Not yet pushed
Both fixes are live-production-facing UI changes -- held for a
separate push confirmation after this documentation pass, per the
standing exception for production-facing surfaces not yet re-tested
live.

### On the horizon -- updated Priority Queue
1. Mobile z-index collision (AssemblyPanel vs. phase-transition bars)
   -- still unconfirmed on a real device, unchanged from prior sessions.
2. extreme_high_confidence calibration tier at 0/1 -- STALE, flagged not
   corrected this pass: this was fixed earlier this same day (batch of
   primary_dimension label-bug fixes to the_paper_tiger/invisible_
   performance_management/the_arbitrary_standard, engine/data/states.py)
   but never got its own MOB Section 16 entry -- out of scope for this
   pass, worth a dedicated documentation catch-up.
3. damages_cap_treatment remains unconsumed by any pricing logic --
   the entire workstream was future-proofing data quality ahead of a
   pricing extension, not fixing a live bug. Worth remembering when
   that extension eventually gets scoped: the five-value enum, the
   AL/GA key-set constraint, and every state's specific citation are
   all sitting there ready to build on.'''

EDITS = [
    ('version header 4.294 -> 4.295', VERSION_OLD, VERSION_NEW),
    ('close v2 token migration row: status column', ROW_STATUS_OLD, ROW_STATUS_NEW),
    ('close v2 token migration row: tail columns', ROW_TAIL_OLD, ROW_TAIL_NEW),
    ('insert new Section 13a row: 3 contrast bugs', NEW_ROW_ANCHOR_OLD, NEW_ROW_ANCHOR_NEW),
    ('append Section 16 closeout entry', TAIL_OLD, TAIL_NEW),
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
