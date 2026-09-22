"""
Session closeout, 2026-09-22 (terminal Claude Code). Three writes to
tools/_mob.txt, plus CLAUDE.md's version cross-reference:

1. Section 8 correction: the "Visual identity -- LOCKED Session 58"
   line still says JetBrains Mono for --font-mono. Confirmed stale
   (this session, and independently already on record from 2026-08-14 --
   see Section 13a's "book-toc-build-scope.md's 'JetBrains Mono'
   reference" row, which traced the swap via git log to commit 2d063f7,
   2026-07-21, and left it as "Pete's call whether to correct"). Tonight
   Pete made that call for this specific locked-spec line. Not a silent
   edit: the original S58 text is left in place (JetBrains Mono really
   was locked and live at S58), a dated correction note is appended
   pointing at the real current token and the existing Section 13a trace,
   rather than rewriting history or re-deriving the git archaeology a
   second time.

2. Section 16: full closeout entry for tonight -- sleuth built end to
   end (route manifest, crawler, four rule engines, CLI, report
   renderer), the two real fixes it drove (ServiceSidebar contrast,
   coaching-as-noun reword x3), the two items filed in Section 13
   (contrast debt, teaser triplication) earlier this session, and the
   Section 8 correction above.

3. Version stamp: v4.320 -> v4.322 (+2, not +1) -- two separable
   material items closed tonight: sleuth's build (a new, substantial
   engineering capability, plus the real fixes it directly drove) as
   one workstream tick, and the Section 8 locked-spec correction as a
   distinct second tick (correcting a LOCKED record is its own kind of
   event, not folded into the tooling workstream it happened to be
   caught during).

CLAUDE.md: Key References table's "MOB version" row, v4.320 -> v4.322.

Usage:
    python tools/patch_mob_session_closeout_20260922.py --dry-run
    python tools/patch_mob_session_closeout_20260922.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')
CLAUDE_PATH = pathlib.Path('CLAUDE.md')

SECTION8_ANCHOR = 'layout.tsx JetBrains_Mono wired; all gray-* classes replaced with token equivalents across 18 files (S58, commit 0e13fa4).'

SECTION8_CORRECTION = ' **CORRECTED 2026-09-22:** --font-mono is IBM Plex Mono, not JetBrains Mono -- superseded via commit 2d063f7 ("Add visual identity v2 tokens, typography, and theme switcher," 2026-07-21, Visual Identity v2/OD-07 Stage 1), whose own commit message confirms JetBrains Mono was dead code before the swap (never rendered live). This S58 record is left otherwise unedited -- JetBrains Mono genuinely was locked and live at S58, this note marks where that changed, not a rewrite of what was true then. Full trace already on record, not re-derived here: Section 13a, "book-toc-build-scope.md\'s \'JetBrains Mono\' reference" row (2026-08-14) found the identical stale claim in that doc a month before this correction and left it as Pete\'s call whether to correct -- resolved here for this Section 8 locked-spec line specifically, tonight, Pete\'s explicit instruction. Independently re-confirmed this session via tools/sleuth\'s own tokens.py build (font allowlist read live from web/app/layout.tsx).'

TAIL_ANCHOR = 'MOB v4.320.\n'

NEW_SECTION16_ENTRY = '''---

## SESSION CLOSEOUT (2026-09-22, terminal Claude Code) -- sleuth built
## end to end, ServiceSidebar contrast fix, coaching-as-noun reword,
## Section 8 visual-identity correction

**One-line summary:** `tools/sleuth` (a new site-integrity crawler for principalresolution.com) designed, built, tested, and fully committed this session -- route manifest, Node/Playwright BFS crawler, four rule engines (structural/brand/content/candidate), CLI, report renderer. Used immediately against the live local site, which surfaced and drove two real fixes (a genuine WCAG AA contrast failure on `ServiceSidebar.tsx`, and a coaching-as-noun brand-voice flag reworded across its three hardcoded locations). Two follow-up items filed in Section 13 rather than fixed (pre-existing contrast debt elsewhere, teaser-sentence triplication). One stale locked-spec correction applied to Section 8 (JetBrains Mono -> IBM Plex Mono, referencing the existing 2026-08-14 Section 13a trace rather than re-deriving it). MOB v4.320 -> v4.322.

### 1. sleuth built end to end

Four deliverables per the original build brief, adjusted where the brief's assumptions didn't match live source (confirmed with Pete before building, not silently substituted -- full record in `tools/sleuth/README.md`'s "What changed from the original build brief, and why" section):

- **Route manifest** (`route_manifest.py`): sourced from a real `next build`'s `.next/prerender-manifest.json` rather than hand-parsed `web/app/**/page.tsx` -- `/book/*` alone has four separate dynamic-route generators (`[type]/[slug]`, `dimension`, `pillar`, `state`), each pulling from a different data source; reading Next's own resolved output avoids reimplementing all four in Python and risking drift.
- **Crawler** (`crawler/crawl.mjs`): Node, not Python -- reuses the project's already-installed `web/node_modules/playwright` (Chromium binaries already downloaded) via `createRequire` anchored at `web/package.json`, rather than a redundant second Playwright+Chromium install. Forces the requested `--theme` via `context.addInitScript()` seeding the site's real `localStorage["prv3-theme"]` key -- caught mid-build that without this, `--theme` had no actual effect and every crawl silently rendered Warm regardless of what was requested; verified post-fix via raw computed-style inspection that all three themes now genuinely render.
- **Four rule engines** (`rules/`): structural (404s, redirect loops, orphan routes, dead ends), brand (font-family, locked-color, rust-reservation, axe-core contrast/ARIA), content (semicolons, "--" em-dash placeholders, internal "PCD" acronym, shadow-model name/entity leaks), candidate (banned jargon extracted live from `engine/output_synthesis.py`'s system prompt, appositive em-dash heuristic, coaching-as-noun heuristic, `/book` em-dash-per-piece cap). Two real bugs caught and fixed during the build's own testing, not left for a future session to find: the rust-reservation check initially matched computed color and immediately false-positived on every ordinary `--oxide-text` element site-wide, because `--oxide-text` and `--urgency`/`--urgency-text` are the literal same hex value in Warm and Dark (confirmed in `globals.css`'s own comment) -- redesigned to key off the literal `bg-rust`/`text-rust` class name instead; orphan detection wasn't applying its own exclusion list, so `/dev/*` and `/favicon.ico` showed up as false orphans on the first full-site test.
- **CLI + report** (`cli.py`, `report.py`): exit code non-zero on any deterministic-tier finding, zero if only candidate-tier flags, per the brief.

Known, documented gaps (also printed in every `sleuth_report.md`, not hidden): no coined-term (P-10) scan -- no enumerated term list exists anywhere in this repo to check against, so it's honestly omitted rather than faked with a noisy heuristic; brand-color check uses a flat union of every locked color across all themes/scopes rather than strict per-theme cascade resolution (the real palette turned out to be a fully theme-reactive, tiered v2/v3 system, not the 4-color set originally assumed); the appositive-em-dash and coaching-as-noun checks are heuristic-only, candidate tier by design, needing human/AI review rather than precise detection.

**Verified:** ran end to end against the live local dev server across a 5-page smoke test, a 15-page capped run, and a full 107-of-121-page run (twice -- once before, once after the fixes below), plus a dedicated Dark-theme and Neutral-theme run confirming the `--theme` fix. All four rule engines confirmed producing real findings, not synthetic ones: a genuine semicolon in a published `/book` piece, a real missing-form-label accessibility gap on `/first-call`, 11 plausible orphan routes, and the two fixes below.

**Committed and pushed**, five commits covering the full tool (`candidate.py` and its first report landed earlier in the session under a fix-specific commit; the rest landed as one grouped push): core infrastructure, the crawler, the three remaining rule engines, and CLI/report/README.

### 2. ServiceSidebar WCAG AA contrast fix, driven by sleuth's own findings

sleuth's full-site crawl surfaced 4 contrast failures recurring on both `/` and `/book` -- root-caused precisely before fixing anything: axe-core separates the real AA check (`color-contrast`, 4.5:1 minimum) from the stricter AAA check (`color-contrast-enhanced`, 7:1). The **only** genuine AA failure was the four service boxes' teaser paragraph, dimmed with `opacity-80` on top of an already-borderline `--slate`-on-`--field` pairing (measured 3.14:1 Warm / 3.29:1 Neutral, both under the 4.5:1 minimum). The plain `text-(--slate)` nav links and sidebar title/CTA text that also showed up in the same violation groups only fail the *stricter* AAA check (4.53-6.84:1 -- real AA passes already), which wasn't asked for and wasn't touched -- nudging `--slate` itself would be a global token change rippling through every consumer of that token sitewide, a materially bigger and riskier change than the scoped fix. Fix: dropped `opacity-80` from the teaser `<p>` in `web/components/ServiceSidebar.tsx`. Verified live: the real AA finding is gone on every page the component renders on (confirmed via a fresh full-site recrawl, not just the one page checked first). `tsc --noEmit` clean, `eslint` clean.

### 3. Coaching-as-noun brand-voice reword, driven by sleuth's own findings

sleuth's candidate-tier check flagged "individual coaching" (a noun-phrase usage) in the Training & Development teaser sentence. Investigated before rewording: the sentence exists as three independently hardcoded copies, not one shared source -- `ServiceSidebar.tsx`'s SERVICES array, `training-and-development/page.tsx`'s H1 (a literal duplicate, not an import), and `ServicesPageContent.tsx`'s own separate, older services array (confirmed live and linked from `NavBar.tsx`'s About dropdown before editing it, not dead code). Pete's approved reword -- "individual coaching, group sessions, or work co-led with your own leaders" -> "we coach individuals, run group sessions, or work co-led with your own leaders," keeping "coach" a verb throughout -- applied to all three locations, per-file commits. A separate, genuinely independent sentence in the same page's body copy ("individual coaching through a specific transition") was left untouched, correctly still flagged -- only the one sentence Pete named was in scope. Consolidating the three hardcoded copies into one shared source was explicitly left undone, filed in Section 13 as its own item rather than actioned as scope creep.

### 4. Section 8 visual-identity correction

The "Visual identity -- LOCKED Session 58" line's font-mono reference (JetBrains Mono) has been stale since commit 2d063f7 (2026-07-21, Visual Identity v2/OD-07 Stage 1) swapped it for IBM Plex Mono -- already found and traced once before, 2026-08-14 (Section 13a), and left open as Pete's call whether to correct. Independently re-confirmed this session via `tools/sleuth`'s own `tokens.py` build (font allowlist read live from `web/app/layout.tsx`). Corrected tonight per Pete's explicit instruction: a dated note appended to the Section 8 line, not a silent rewrite -- the original S58 text stays in place (accurate as of when it was written), the note marks where it changed and points at the existing Section 13a trace rather than re-deriving it.

**Files changed, git-confirmed (all pushed to `main`):** `tools/sleuth/` (14 files, new), `web/components/ServiceSidebar.tsx` (two commits: contrast fix, coaching reword), `web/app/training-and-development/page.tsx` (coaching reword), `web/components/ServicesPageContent.tsx` (coaching reword), `tools/_mob.txt` (Section 13 open items, this closeout's Section 8/16/version-bump pass), `CLAUDE.md` (MOB version cross-reference), plus new patch scripts for each MOB write. Two scratch patch scripts used earlier in the session (`patch_service_sidebar_teaser_contrast_fix.py`, `patch_coaching_sentence_reword.py`) were deleted, never committed -- one-time scripts, not reusable tooling in the `scdwcs_validator.py` sense.

**Open items carried forward, unchanged unless noted:** `gh` CLI still not installed; local dev Upstash Redis credentials missing; Function Storage remediation not executed; Dropbox Sign provisioning unconfirmed; attorney-review gate and pilot-mechanism recommendation unchanged; next Quarterly Step-Back due **2026-10-03**. **New, filed in Section 13 earlier this session:** 92 pre-existing WCAG AA contrast failures (`.text-gray-400`/`.text-gray-500`, eyebrow-label text) across `/about/*` and every `/book/memo|case_pattern/*` piece -- unrelated to tonight's ServiceSidebar fix, not touched, likely another single shared-component fix candidate; the Training & Development teaser's three-way hardcoded duplication, reworded in place but not consolidated.

**Anything Pete should know at next session start:** `tools/sleuth` is a real, working, committed tool -- `python tools/sleuth/cli.py --base-url <url> --theme <warm|dark|neutral>` -- and its own README documents every gap and design tradeoff made building it. The 92-failure contrast debt and the coined-term (P-10) gap are the two most likely next things to pick up if continuing this thread. All work tonight is committed and pushed to `main` individually, not batched -- git log from the sleuth-build commits through this closeout's own commits covers the full arc.

MOB v4.322.
'''

CLAUDE_OLD = '| MOB version | v4.320 |'
CLAUDE_NEW = '| MOB version | v4.322 |'


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    mob_content = MOB_PATH.read_text(encoding='utf-8')

    count_s8 = mob_content.count(SECTION8_ANCHOR)
    if count_s8 != 1:
        print(f'ERROR: SECTION8_ANCHOR found {count_s8} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    count_tail = mob_content.count(TAIL_ANCHOR)
    if count_tail != 1:
        print(f'ERROR: TAIL_ANCHOR found {count_tail} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)
    if not mob_content.endswith(TAIL_ANCHOR):
        print('ERROR: TAIL_ANCHOR is not at the true end of the file -- refusing to guess.', file=sys.stderr)
        sys.exit(1)

    new_mob_content = mob_content.replace(SECTION8_ANCHOR, SECTION8_ANCHOR + SECTION8_CORRECTION, 1)
    new_mob_content = new_mob_content + '\n' + NEW_SECTION16_ENTRY

    claude_content = CLAUDE_PATH.read_text(encoding='utf-8')
    count_claude = claude_content.count(CLAUDE_OLD)
    if count_claude != 1:
        print(f'ERROR: CLAUDE_OLD found {count_claude} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)
    new_claude_content = claude_content.replace(CLAUDE_OLD, CLAUDE_NEW, 1)

    if args.dry_run:
        print('DRY RUN -- all anchors found exactly once, both files would write cleanly.')
        print(f'_mob.txt: old length {len(mob_content)}, new length {len(new_mob_content)}, delta {len(new_mob_content) - len(mob_content)}')
        print(f'CLAUDE.md: old length {len(claude_content)}, new length {len(new_claude_content)}, delta {len(new_claude_content) - len(claude_content)}')
    else:
        MOB_PATH.write_text(new_mob_content, encoding='utf-8')
        CLAUDE_PATH.write_text(new_claude_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'_mob.txt: old length {len(mob_content)}, new length {len(new_mob_content)}, delta {len(new_mob_content) - len(mob_content)}')
        print(f'CLAUDE.md: old length {len(claude_content)}, new length {len(new_claude_content)}, delta {len(new_claude_content) - len(claude_content)}')


if __name__ == '__main__':
    main()
