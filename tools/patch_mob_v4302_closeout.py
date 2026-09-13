"""
tools/_mob.txt: session closeout -- AssemblyPanel/Phase-2-CTA merge shipped
and pushed, Q05 option E wires invisible_performance_management's second
question and is pushed with a confirmed live round-trip, the
IPM/the_founders_grip vector-duplicate record corrected (Part B), and a
mid-session two-bug investigation (long screenshot, missing back button)
reported plainly with two new unscoped Priority Queue items.

Bumps MOB version v4.301 -> v4.302 (two Priority Queue items close, one
is corrected, two new items open -- workstream status changes
materially). Appends a new closeout entry after the existing v4.301
entry's own trailing Priority Queue snapshot, left untouched as a
historical record -- matching this file's existing append-only pattern.

Usage:
    python tools/patch_mob_v4302_closeout.py --dry-run
    python tools/patch_mob_v4302_closeout.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = r'\\\#\\\# MOB v4.301'
VERSION_NEW = r'\\\#\\\# MOB v4.302'

TAIL_ANCHOR_OLD = '''8. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.'''

NEW_ENTRY = '''

## SESSION CLOSEOUT (2026-09-13, continuation session) -- AssemblyPanel/CTA
## merge + Q05 IPM wiring pushed and live, two new bugs investigated and
## reported (not fixed), IPM/founders_grip duplicate record corrected

### One-line summary
Two builds from this session's earlier report-only investigation (Parts
A/B/C) are now committed, pushed, and live: the AssemblyPanel/Phase-2-CTA
merge (Option C, web-only) and Q05's new option E wiring
`invisible_performance_management`'s second question (engine-touching,
redeploy confirmed READY, live round-trip 401). Mid-session, Pete
reported two new bugs from a real device (Pixel 10 Pro, Chrome mobile);
both were investigated and confirmed unrelated to the pending push --
reported here plainly, neither fixed, per Pete's explicit "propose
nothing, wait" instruction on Bug 1. The IPM/`the_founders_grip`
vector-duplicate record is corrected (Part B).

### Build 1 -- AssemblyPanel/Phase-2-CTA merge (Option C) -- SHIPPED, web-only
Commits `6663a3e` (`SelfSelectionContext.tsx` -- remove
`assemblyTriggerHeight`), `00910a4` (`AssemblyPanel.tsx` -- remove
`ResizeObserver`/`triggerRef`, add `hideMobileTrigger` prop), `e9e8562`
(`page.tsx` -- the merged row itself). Two stacked mobile bars (141.4px
combined, measured live) become one (65px, target was 60-64px). Verified
live at 375px and 320px: drawer opens/closes correctly, CTA
disables/advances correctly, no horizontal overflow. One real regression
caught and fixed before shipping -- a uniform `text-sm` label size
wrapped the longer "select at least two conditions" message at 320px and
inflated the CTA button to 76px; restored the original two-tier
`text-xs`/`text-sm` sizing. Web-only, no API route touched -- no redeploy
required, none run.

**Gemini architecture-gate exception, recorded plainly, not written
around:** this project's standing protocol routes any decision affecting
multiple files or integration behavior through Gemini review before
execution. Build 1 touches three files and changes a cross-component
contract (`SelfSelectionContext`'s shape, `AssemblyPanel`'s props) --
it was built and shipped without that review. Pete confirmed push-as-is
this session given the change's full live functional verification (both
target viewports, both interaction paths) and low architectural stakes
(a mobile layout consolidation with no data-contract or engine surface
touched) -- not a silent skip.

### Build 2 -- Q05 option E, invisible_performance_management's second
### question -- SHIPPED, engine-touching, live-verified
Commits `369c1c9` (`engine/data/questions.py`), `d7d90ff` (its patch
script), `ff813d9` (`tools/test_accumulation.py` section 13, 5 checks),
`9cf694e` (its patch script). Same fix shape as Q35's own option E
(`e8f82a8`): a clean, single-field `authority_liability=0.60`
contribution. Confirmed zero regression to Q05's original 4 options and
6 target states, full 175-profile calibration suite re-run before and
after via an isolated git worktree. `built_to_fail`'s aggregate
unaffected (70). A full-suite winner diff (not just an IPM-scoped check)
surfaced a real, fully-explained side effect: 9 profiles across
`the_paper_tiger`/`the_arbitrary_standard`/IPM now lose to
`the_uninitiated` instead of their prior rivals, with zero change to any
state's own capture rate (0/N before and after, in every case) --
consistent with the already-documented "rank-3 cluster" dynamic (see
Part B below), not a new problem.

**IPM's own-profile capture rate remains 0/3 after this fix -- still
open, not resolved by this build.** This fix closed the wiring-density
gap as scoped (1 of 52 core questions -> 2), it did not make IPM win any
of its own 3 dedicated calibration profiles outright. That is a deeper,
separate calibration question tracked under the rank-3 cluster item,
not reopened or claimed fixed here.

**Two process slips this session, both self-caught before any commit:**
(1) the first attempt at the `questions.py` edit used the Edit tool
directly, bypassing this project's standing dry-run-then-write
patch-script discipline for engine writes -- caught before running any
tests, reverted via `git checkout`, redone as
`tools/patch_q05_ipm_option_e.py`, byte-identical result confirmed. (2) a
`git stash` intended to isolate one file for a before/after comparison
stashed the entire working tree, including Build 1's already-verified
web changes -- caught immediately via `git stash list`, restored via
`git stash pop`, confirmed nothing lost via `git diff --stat` before
continuing. Neither slip reached a commit.

**Live round-trip check, confirmed this session, not carried forward
from a prior push:** deployment
`prv-3-1ncy9mvmm-peter-rizzos-projects.vercel.app` confirmed READY via
`vercel ls prv-3 --prod` (polled from Building to Ready). Live
`POST https://principalresolution.com/api/engine` returned **401
Unauthorized** (`{"detail":"Unauthorized"}`) -- a clean auth rejection,
not a 500, confirming the route itself is live and functioning.

### Part B -- IPM/`the_founders_grip` vector-duplicate record corrected
Confirmed directly: `dimensional_vector` and `SALIENCE_PROFILES` are
byte-identical between the two states, and this is **deliberate, not an
oversight**. The re-authoring commit that created the collision
(`f88a7c2`, 2026-08-25) says so in its own inline comment: *"Dry-run
confirmed clean (Phase 4c): false-rank-1 43 -> 0/175, zero new collision
against the_founders_grip."* The team knew the vectors would become
identical, checked for pairwise damage between these two specific
states, found none, and shipped anyway.

This is one pairing inside an already-diagnosed, already-deferred
**8-state structural issue** ("rank-3 cluster": IPM, `the_founders_grip`,
`the_exposed`, `hr_capture`, `heard_and_ignored`, `the_tolerated_violation`,
`sequential_decision_blindness`, `disparate_impact_architecture`, all
sharing one exact vector/salience shape), fully characterized in
`prompts/scd-wcs-remediation-tracker.md` -- none of the 8 ever wins its
own dedicated profiles outright (0/24 combined), losing instead to
flatter-vector rivals; a real fix would require re-authoring all 8
states' shared vector shape simultaneously, explicitly out of scope to
attempt in isolation for just the IPM/`the_founders_grip` pair.

**Confirmed latent, not live, in the current 175-profile set, checked
directly this pass:** IPM's own 3 profiles and `the_founders_grip`'s own
3 profiles are all won by `the_uninitiated` (per Build 2's confirmed
ripple above). Zero cross-confusion between the two specifically --
neither wins the other's own profiles.

### Mid-session investigation -- two bugs reported from a real device
### (Pixel 10 Pro, Chrome mobile), both reported plainly, neither fixed

**Bug 1 -- native long-screenshot ("Capture more") doesn't work on the
diagnostic page.** Two known mechanisms checked directly against the
live page, not assumed:
- Inner scroll container (would hide content from native capture,
  which scrolls the document): **ruled out.** `html`/`body` both compute
  `overflow-y: visible` at every phase checked, on both diagnostic paths
  (self-select and question-by-question), and
  `document.documentElement.scrollHeight` always exceeds
  `window.innerHeight`. Natural document flow, no trap.
- `position: fixed` elements (known to duplicate/corrupt stitched
  frames): **present, but modest and pre-existing.** Measured live,
  filtering out `display:none` (desktop-only `hidden md:block` elements
  report `position: fixed` via `getComputedStyle` even though they don't
  render on mobile -- a naive check would overcount). Visible count per
  phase: 1 (gate/Phase 1 idle) or 2 (a persistent mobile-menu button
  plus at most one bottom bar) at every other phase, self-select and
  question-by-question paths alike. **Build 1's merge reduced Phase 2's
  count from 3 to 2** -- if this bug relates to fixed elements at all,
  this session's change made it marginally better, not worse.
- Current-Chrome research (web search, not assumed from stale
  knowledge): fixed-element duplication in scrolling capture is a
  well-documented general mechanism (both Chrome DevTools' desktop
  capture and Android's native OS-level "Capture more"), but no
  Chromium-tracker-pinned confirmation was found that this specific low
  count causes total failure on current Chrome versions, as opposed to
  cosmetic duplication -- flagged as a real gap, not papered over.
- No clean repro obtained -- Chrome DevTools device emulation cannot
  trigger Android's native "Capture more" UI at all; this is a real,
  disclosed limitation, not a claimed-clean repro that wasn't run.
- **Not fixed, not scoped for a fix.** The only mechanism confirmed
  present (fixed elements) would require removing or restructuring
  persistent nav/bars to chase -- exactly the category this project
  routes through the Gemini architecture gate first, and not worth it
  given a simpler fix serves Pete's actual underlying need (see new
  Priority Queue item below).

**Bug 2 -- diagnostic back button missing.** Checked both diagnostic
paths directly, not assumed:
- Self-select path (`page.tsx`, what Build 1 touched): **never built.**
  `onPhaseAdvance` is called only with forward values (2, 3, 4, 5) at
  every call site -- zero backward navigation, zero browser-history
  integration, anywhere. Not a regression; this path has never had one.
- Question-by-question path (`DiagnosticFlow.tsx`): this project's own
  record (Section 13a, row "A.3 (back/forward/reset)") shows true
  back-navigation ("edit-and-replay") was **deliberately descoped by
  Pete** in a prior session, not forgotten -- a truncate-and-replay
  design was scoped but never built. What shipped instead: a "Start
  over" reset and a read-only "Review your answers so far" history
  panel, neither of which lets you go back and change an answer.
- **Confirmed a net-new feature request on both surfaces, not a
  regression, and not something this session's AssemblyPanel merge
  touched or broke.** Not fixed, not scoped -- needs product decisions
  (which phase does it return to, does it preserve or clear prior
  selections) before any build. See new Priority Queue item below.

### Test suite / verification, this session in full
`tools/test_accumulation.py`: 44 -> 49. Full 11-script suite: 909 -> 914
(the friction_tax count, 188, is unaffected by either build -- neither
touches Legal/Compliance pricing). `web/`'s vitest: 45/45, unchanged.
`tsc --noEmit`: clean. Vercel deployment confirmed READY, live
`POST /api/engine` round-trip returned 401 (not 500).

### On the horizon -- updated Priority Queue
1. `built_to_fail` false-rank-1 baseline drift -- CLOSED (MOB v4.301).
2. `built_to_fail`'s 16-profile ripple from `f88a7c2` -- confirmed real,
   mechanism NOT identified. 16 of 175 calibration profiles across 13
   states none of which `f88a7c2` directly touched
   (`what_nobody_says`, `culture_drift`, `the_wrong_reward`,
   `distributed_culture_fragmentation`, `compression_crisis`,
   `transition_paralysis`, `pay_exposure`, `the_pay_fog`,
   `the_uninitiated`, `the_unformed_leader`, `cultural_overtime`,
   `the_dormant_talent`, `the_unexamined_algorithm`) flipped toward
   `built_to_fail` at the exact commit that re-authored five completely
   different states' vectors. Needs its own dedicated investigation
   session, not a quick follow-up.
3. AssemblyPanel/Phase-2-CTA merge (Option C) -- CLOSED, this session.
   Shipped, pushed, live-verified at 375px/320px. See Build 1 above.
4. `invisible_performance_management`'s thin question-wiring -- CLOSED,
   this session. Q05 option E is IPM's second wired question (was 1 of
   52 core questions, now 2), shipped and pushed. Note: this closes the
   WIRING-density concern specifically -- IPM's own-profile calibration
   capture rate remains 0/3, unchanged, a separate and deeper question
   tracked under item 5 below, not reopened by this fix.
5. `invisible_performance_management`/`the_founders_grip` vector
   duplicate -- corrected record, this session (see Part B above).
   Confirmed deliberate, not an oversight; part of the already-diagnosed
   8-state rank-3 cluster issue tracked in
   `prompts/scd-wcs-remediation-tracker.md`; confirmed latent, not live,
   as of this session. Out of scope to fix in isolation. No urgency.
6. **NEW -- Diagnostic result export (copy-as-text).** Proposed by
   Claude.ai, not yet scoped or approved for build. Pete's actual need
   behind this session's screenshot bug report was getting diagnostic
   output to Claude for review, not screenshotting per se. A "Copy
   results as text" feature on the output page sidesteps the unconfirmed
   long-screenshot bug (item 7 below) entirely, needs no fixed-position
   or scroll-architecture change, and directly serves the real use case.
7. **NEW -- Long-screenshot capture on the diagnostic page.** Root cause
   unconfirmed, no repro obtainable in this environment (Chrome DevTools
   emulation can't trigger Android's native "Capture more" UI). The one
   mechanism confirmed present (a modest, pre-existing count of
   `position: fixed` elements) is not worth restructuring persistent nav
   to chase given item 6 above serves the actual underlying need more
   directly. Revisit only if Pete confirms the export feature doesn't
   fully cover the use case.
8. **NEW -- Diagnostic back button.** Confirmed never built on either
   diagnostic path this session -- the self-select path never had one;
   the question-by-question path had true back-navigation ("edit-and-
   replay") deliberately descoped in a prior session, pending a
   truncate-and-replay design never built. Net-new feature request,
   needs product scoping (which phase does it return to, does it
   preserve or clear prior selections) before any build.
9. `_oh_is_small_employer()` -- built and tested, not wired into any
   pricing branch. Revisit whenever a real compensatory-damages/
   net-worth pricing path for OH is scoped.
10. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) -- documented
    approximation in `_oh_is_small_employer()`'s docstring and OH's
    citation comment. No NAICS-level intake data exists to resolve it
    precisely; revisit only if OH's small-employer routing is ever
    wired into a real pricing path.
11. Quarterly Step-Back -- due next week, per Pete's correction this
    session (not overdue -- the prior "last run August 22" framing
    carried in this queue since MOB v4.279 undercounted; Pete's own
    scheduling correction is authoritative here, not independently
    re-derived this session).'''

EDITS = [
    ('version header 4.301 -> 4.302', VERSION_OLD, VERSION_NEW),
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

    # TAIL_ANCHOR_OLD text is not required to be unique in the file (this
    # exact Quarterly Step-Back wording repeats in older historical
    # entries) -- only that the file's true end matches it, so we know
    # we're appending after the live snapshot and not blind.
    if not content.rstrip().endswith(TAIL_ANCHOR_OLD.rstrip()):
        errors.append('file does not end with the expected tail anchor -- refusing to append blind.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    new_content = new_content.rstrip('\n') + '\n' + NEW_ENTRY + '\n'

    if args.dry_run:
        print('DRY RUN -- all anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
