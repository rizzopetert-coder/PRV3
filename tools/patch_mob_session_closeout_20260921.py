"""
Session closeout, 2026-09-21 (terminal Claude Code). Three writes:

1. tools/_mob.txt Section 14 (Locked Decisions Log): new row for the
   Gemini cross-assistant operational bridge -- a genuine new
   architectural/governance decision (Pete's explicit authorization),
   not just a Section 12 tooling note. Per CLAUDE.md's closeout rule
   ("If a new architectural decision was locked this session: confirm
   it is reflected in both the relevant spec section... and Section 14
   before logging"), this mirrors the Section 12 subsection already
   committed this session (commit 77cce33) into the Locked Decisions
   Log too. Inserted immediately after the most recent existing row
   (2026-09-20, commercial-name correction + route renaming), before
   Section 14's closing rule.

2. tools/_mob.txt Section 16 (Session Log): one closeout entry
   covering all four items from tonight -- landing page body copy
   (3 pages), ServiceSidebar left-move + gap spacing + same-session
   scroll-fix regression, the Gemini cross-assistant bridge, and the
   diagnostic_question_audit.py stale-data catch. Appended at the true
   end of the file, replacing the final "MOB v4.317." stamp with the
   new entry followed by "MOB v4.320.".

3. CLAUDE.md: Key References table's "MOB version" row, v4.317 ->
   v4.320.

Version bump: v4.317 -> v4.320 (+3, not the usual +1) -- three
material items locked tonight (landing pages closing an open item,
ServiceSidebar's redesign+regression-fix as one workstream, and the
new cross-assistant bridge architecture), per Pete's explicit
instruction that this isn't a minor-bump session. The
diagnostic_question_audit finding is informational/flagged-not-acted-
on and does not itself add a tick, consistent with "leave unchanged
for session log entries only" for non-decision content.

Anchors are short unique substrings taken from the live file (verified
via direct byte inspection before writing this script), not hand-
retyped copies of the surrounding paragraphs -- both existing sections
carry long prose rows where a retyped anchor would be an easy place to
introduce a silent mismatch.

Usage:
    python tools/patch_mob_session_closeout_20260921.py --dry-run
    python tools/patch_mob_session_closeout_20260921.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')
CLAUDE_PATH = pathlib.Path('CLAUDE.md')

SECTION14_ANCHOR = 'zero em dashes. | This session (Claude Code), 2026-09-20 | MOB v4.317 |\n'

SECTION14_NEW_ROW = '''
| **Cross-assistant operational bridge -- Gemini's role expanded to persistent operational assistant** | LOCKED, Pete's explicit authorization, 2026-09-21: beyond its existing audit/propose role on structural architectural decisions (CLAUDE.md, "Architectural Decisions"), Gemini now monitors inbound prospect leads and maintains two Google Docs journals as a standing operational function. **Principal Resolution — Practice Journal** (Gemini-maintained): day-to-day practice pulse, client pipeline status, inbound triage state -- explicitly NOT a technical source of truth; service names, pricing, and architecture remain defined in the MOB/engine and are only referenced there, never redefined there. **The Home Journal** (Gemini-maintained): household/family operational log, entirely out of PRV3 scope, noted here only because the same assistant now holds both. **Taxonomy error caught and corrected same day:** the Practice Journal pulled a stale, incorrect 5-tier service taxonomy on creation (Stability Support, Executive Counsel, The Intervention, The Roadmap, Development) that did not match the confirmed 4-service set (People Tactics & Strategy, Training & Development, First Call, Executive Advisory) -- corrected on the Gemini side, then independently verified by Pete directly against the live document, not taken on Gemini's report alone. One residual noted for separate cleanup, not yet fixed: the Journal's Intake Protocols line still says "five engagement tiers." Full detail: Section 12, "Cross-assistant operational bridge (2026-09-21)" subsection. | This session (Claude Code), 2026-09-21 | MOB v4.320 |
'''

TAIL_ANCHOR = 'not started this session by design.\n\nMOB v4.317.\n'

NEW_SECTION16_ENTRY = '''not started this session by design.

MOB v4.317.

---

## SESSION CLOSEOUT (2026-09-21, terminal Claude Code) -- landing page
## body copy shipped, ServiceSidebar left-move + gap-spacing + scroll-fix
## regression, Gemini cross-assistant bridge established

**One-line summary:** Four distinct items closed out and pushed to `main` individually this session -- the three service landing pages' body copy, `ServiceSidebar`'s left-side move plus real box-to-box spacing (with a same-session regression found and fixed), the Gemini cross-assistant operational bridge (Practice Journal + Home Journal, Pete's explicit authorization) documented in Section 12 and mirrored into Section 14, and a stale-audit-data catch on `diagnostic_question_audit.py`'s reported figures before they could be written into a permanent record. MOB v4.317 -> v4.320 -- three material items locked, not a single-workstream tick.

### 1. Landing page body copy shipped (People Tactics & Strategy, Training & Development, Executive Advisory)

Closes the explicit open item carried from the prior closeout ("full body copy for the four landing pages... an explicit separate follow-up pass, not started this session by design"). Placeholder "Full detail on this page is coming soon." replaced in all three files with Pete's locked copy plus a "Take the diagnostic ->" CTA link to `/diagnostic`. Eyebrow and H1 (the `ServiceSidebar.tsx` teaser sentences) confirmed byte-identical to before. Markup matched existing site conventions rather than inventing new patterns: `space-y-4` paragraph stacking (`web/app/about/page.tsx`'s own pattern), CTA styled `underline hover:opacity-90 transition-opacity` (this site's established inline-text-link convention, confirmed in both `components/ServicesPageContent.tsx`'s "Learn more ->" link and `web/app/page.tsx`'s inline links). Each file's stale header comment ("full body copy is an explicit separate follow-up pass") corrected to point at this closeout instead. One deliberate content decision: Training & Development's "co-led -- your own leaders" em dash is Pete's own confirmed-intentional text, left exactly as supplied, not a standing no-em-dash-rule violation. **Verified:** `tsc --noEmit` clean, `eslint` clean, `next build` succeeds, all three routes prerender as static content. Commits: `bdd5624`, `7604da5`, `fcce77f` (one per page) + `a8c4f40` (patch script). Pushed after Pete's explicit go-ahead following a live-review pause (production has no Preview environment).

### 2. ServiceSidebar left-side move + real gap spacing, and a same-session regression found and fixed

**Move + spacing:** `<aside>` reordered to render before `{children}` (was children-then-aside), `border-l` -> `border-r` since it now divides sidebar-from-content on its right edge. Box separator changed from an effective 1px hairline (`border-b border-line`) to a real visible 8px background-colored gap (`border-b-8 border-field`) -- token checked first, not assumed: `border-field` matches the aside's own `bg-field` exactly (the v2 token, redefined per-theme in `:root`/`[data-theme="dark"]`/`[data-theme="neutral"]`), while `--color-paper` (the other candidate) is a fixed, non-theme-reactive value that would not have tracked Dark/Neutral. `py-6` added (boxes read cramped once the gap ate into the flex-1 vertical rhythm). `/diagnostic`'s collapsed trigger flipped to match: `justify-end`/`right-6` -> `justify-start`/`left-6`. Live-verified across Warm/Dark/Neutral on both layout branches via computed styles, not just screenshots.

**Regression found same session, fixed same session:** the `py-6` + 8px-gap change pushed Executive Advisory (the last box) below the fold on standard-height screens -- the `<aside>` is `h-screen` with `flex-1` children and no scroll behavior, so once combined min-content height exceeded viewport height, flex had nowhere to shrink to. Confirmed live at 1512x786: Executive Advisory's header did not render in view at all. **Fix:** `overflow-y-auto` added to the `<aside>`. Re-verified at three viewport heights, all three themes -- not just the one that regressed: 1512x786 (the reported case) and 1366x768 both overflow and are now reachable by scrolling within the sidebar (confirmed via computed styles -- `scrollHeight` 920 > `clientHeight` 786/768, `overflow-y: auto` -- and by scrolling the aside to its max and checking Executive Advisory's header `getBoundingClientRect()` lands fully inside the viewport); 1512x1000 fits without scrolling (`scrollHeight === clientHeight`, no scrollbar), confirming no regression in the case that already worked. `tsc --noEmit` clean, `eslint` clean, `next build` succeeds. Commits: `ade8ead` (move+spacing) + `18cf23d` (patch script); `53545d4` (scroll fix) + `adf9a34` (patch script). Both pairs pushed after Pete's go-ahead.

### 3. Gemini cross-assistant operational bridge established, MOB Section 12 + Section 14 addition

Pete's explicit authorization, 2026-09-21: Gemini's role expanded beyond audit/propose on structural decisions to a persistent operational assistant -- monitoring inbound prospect leads and maintaining two Google Docs journals (the Principal Resolution Practice Journal; the Home Journal, entirely out of PRV3 scope). Documented as a new subsection under Section 12 (Session Continuity), not Section 13a (Decision Register) -- this is operational/tooling infrastructure, the same category as the rest of Section 12's content, not a scoped Tier 3 decision with a status/blocker/check-in shape. Mirrored into Section 14 (Locked Decisions Log) this same pass, per the closeout rule that a new architectural decision must be reflected in both places.

The Practice Journal pulled a stale, incorrect 5-tier service taxonomy on creation (Stability Support, Executive Counsel, The Intervention, The Roadmap, Development) that did not match the confirmed 4-service set (People Tactics & Strategy, Training & Development, First Call, Executive Advisory). Corrected same-day on the Gemini side; the MOB entry itself was revised once already mid-review, from an initial "correction in progress" draft to "corrected," after Pete independently verified the live document directly and confirmed the fix, the source-of-truth rule, and the MOB/Journal demarcation were already live, not pending. One residual noted for separate cleanup, not yet fixed: the Journal's Intake Protocols line still says "five engagement tiers." One wording change applied to Pete's supplied draft text, flagged rather than silently made: a `--` placeholder became a colon, per the standing no-em-dash-placeholder rule -- internal MOB prose, not externally-authored locked copy, so the standing style rule applied rather than being preserved-and-flagged the way locked marketing copy was earlier this session. Commits: `77cce33` (MOB Section 12 addition) + `372df7e` (patch script). Pushed.

### 4. Stale audit data caught before being written into a permanent record

Closeout instructions asked this entry to log `diagnostic_question_audit.py`'s reviewed output as "22 unreachable questions... flagged, not yet acted on." Before writing that number into a permanent diary/MOB entry, re-ran the tool fresh against current `engine/data/questions.py` rather than transcribing the figure as given -- it did not match. The committed `tools/diagnostic_question_audit_output.md` was last regenerated 2026-08-11 and had gone stale relative to two later engine fixes that were never folded back into it: `e8f82a8` (2026-09-10, wired Q35's stale branch, which also pulled Q36-Q39 along with it into reachable/CORE) and `369c1c9` (2026-09-13, added Q05's missing option, clearing its flag). Pete confirmed the "22" came from reading that stale file in an old, unclosed browser tab, not a fresh run. **Actual current state, verified live this session:** 17 unreachable (not 22), CORE 47 (not 42), 94/101 questions carry at least one flag (near-universal missing doesn't-apply option still holds). `SEVER-09` is confirmed genuine in both the stale and fresh runs -- its only parent, `Q27A`, is itself unreachable, so `SEVER-09` has never had a live trigger path. **Flagged, not acted on** -- Pete's call whether/when to wire `Q27A`'s branch or retire `SEVER-09`. Per Pete's explicit instruction, the freshly-regenerated audit output file was reverted (`git checkout --`), not committed -- this was a stale-data discovery made via an old browser tab, not a deliverable for this pass, and the committed `.md` file remains at its 2026-08-11 state for now.

**Files changed, git-confirmed (all listed above already pushed to `main`):** `web/app/people-tactics-and-strategy/page.tsx`, `web/app/training-and-development/page.tsx`, `web/app/executive-advisory/page.tsx`, `web/components/ServiceSidebar.tsx` (two separate commits), `tools/_mob.txt` (Section 12 addition, plus this closeout's Section 14/16/version-bump pass), `CLAUDE.md` (MOB version cross-reference), plus four new patch scripts (`tools/patch_service_landing_body_copy.py`, `tools/patch_service_sidebar_left_gap.py`, `tools/patch_service_sidebar_scroll_fix.py`, `tools/patch_mob_cross_assistant_bridge.py`) and this closeout's own (`tools/patch_mob_session_closeout_20260921.py`).

**Open items carried forward, unchanged unless noted:** `gh` CLI still not installed (Windows UAC install issue, needs Pete interactively); local dev Upstash Redis credentials missing (informational, production already has them); Function Storage remediation not executed; Dropbox Sign provisioning still unconfirmed; attorney-review gate and pilot-mechanism recommendation unchanged; next Quarterly Step-Back due **2026-10-03**, unchanged. **New open items:** `SEVER-09` has no live trigger path (parent `Q27A` unreachable) -- flagged this session, no urgency assigned, Pete's call; Practice Journal's Intake Protocols line still says "five engagement tiers" -- residual cleanup from item 3, not yet fixed; `tools/diagnostic_question_audit_output.md` remains stale on disk (2026-08-11 figures) -- a future session should regenerate and commit it deliberately, not in passing.

**Anything Pete should know at next session start:** all four items above are committed and pushed to `main` individually (not batched into one closeout commit) -- git log from `bdd5624` through this closeout's own commits covers the full arc. The stale-audit catch in item 4 is worth remembering as a small case study, not just a footnote: a number read off a cached artifact (an old browser tab showing a `.md` file 11 days out of date) almost went into a permanent record uncorrected, caught only because this session re-ran the underlying tool against live code before writing anything down -- the same discipline the Quarterly Step-Back protocol exists to enforce more broadly, here applying at the scale of a single session-closeout entry. Working tree confirmed clean at closeout except the pre-existing, untouched salience-pilot/gemini scratch file pile (same set flagged at every check this session).

MOB v4.320.
'''

CLAUDE_OLD = '| MOB version | v4.317 |'
CLAUDE_NEW = '| MOB version | v4.320 |'


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    mob_content = MOB_PATH.read_text(encoding='utf-8')

    count_s14 = mob_content.count(SECTION14_ANCHOR)
    if count_s14 != 1:
        print(f'ERROR: SECTION14_ANCHOR found {count_s14} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    count_tail = mob_content.count(TAIL_ANCHOR)
    if count_tail != 1:
        print(f'ERROR: TAIL_ANCHOR found {count_tail} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)
    if not mob_content.endswith(TAIL_ANCHOR):
        print('ERROR: TAIL_ANCHOR is not at the true end of the file -- refusing to guess.', file=sys.stderr)
        sys.exit(1)

    new_mob_content = mob_content.replace(SECTION14_ANCHOR, SECTION14_ANCHOR + SECTION14_NEW_ROW, 1)
    new_mob_content = new_mob_content[: -len(TAIL_ANCHOR)] + NEW_SECTION16_ENTRY

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
