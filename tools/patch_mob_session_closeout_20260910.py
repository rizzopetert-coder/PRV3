"""
tools/_mob.txt: full session closeout, five workstreams (the_paper_tiger
tracker correction, extreme_high_confidence root-cause fix, v2 token
migration re-examination + 3 new contrast-bug fixes, damages_cap_treatment
Phase 1 spec, EXP-IPM-02 flag). Bumps MOB version and appends a new
Section 16 entry with an updated Priority Queue.

Usage:
    python tools/patch_mob_session_closeout_20260910.py --dry-run
    python tools/patch_mob_session_closeout_20260910.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = '\\\\\\#\\\\\\# MOB v4.296'
VERSION_NEW = '\\\\\\#\\\\\\# MOB v4.297'

TAIL_OLD = '''### On the horizon -- updated Priority Queue
1. Mobile z-index collision (AssemblyPanel vs. phase-transition bars)
   -- still unconfirmed on a real device, unchanged from prior sessions.
2. damages_cap_treatment remains unconsumed by any pricing logic --
   the entire workstream was future-proofing data quality ahead of a
   pricing extension, not fixing a live bug. Worth remembering when
   that extension eventually gets scoped: the five-value enum, the
   AL/GA key-set constraint, and every state's specific citation are
   all sitting there ready to build on.
3. extreme_high_confidence calibration tier -- CLOSED 2026-09-10, no
   longer on this list. See Section 13a's retroactive entry for full
   detail (root cause, fix, before/after suite numbers, built_to_fail
   false-rank-1 re-census).'''

TAIL_NEW = '''### On the horizon -- updated Priority Queue
1. Mobile z-index collision (AssemblyPanel vs. phase-transition bars)
   -- still unconfirmed on a real device, unchanged from prior sessions.
2. damages_cap_treatment remains unconsumed by any pricing logic --
   the entire workstream was future-proofing data quality ahead of a
   pricing extension, not fixing a live bug. Worth remembering when
   that extension eventually gets scoped: the five-value enum, the
   AL/GA key-set constraint, and every state's specific citation are
   all sitting there ready to build on.
3. extreme_high_confidence calibration tier -- CLOSED 2026-09-10, no
   longer on this list. See Section 13a's retroactive entry for full
   detail (root cause, fix, before/after suite numbers, built_to_fail
   false-rank-1 re-census).

## SESSION CLOSEOUT (2026-09-10, continuation session) -- extreme_high_confidence
## root cause fixed, v2 token question closed + 3 contrast bugs fixed,
## damages_cap_treatment Phase 1 fully scoped

### One-line summary
Five workstreams this session: (1) a stale tracker line corrected to
reflect live data; (2) extreme_high_confidence's real root cause found
and fixed -- a label bug, not an architecture gap, across three states;
(3) the v2 token migration question re-examined and confirmed correctly
settled, which surfaced a diligence audit finding and fixing three real,
previously-unknown WCAG AA contrast failures on the homepage; (4) a
future pricing extension (damages_cap_treatment) fully scoped end to end
across two Gemini review rounds and CC's own independent verification,
ready for a build session but not built; (5) one new, low-priority
calibration gap flagged for later. Two of five workstreams are live and
pushed; one (the homepage contrast fixes) is committed but held for a
visual confirmation; one (the spec) is documentation only; one (the
tracker correction) is documentation only and already pushed.

### 1. the_paper_tiger tracker correction -- pushed
`prompts/scd-wcs-remediation-tracker.md`'s own row previously read
"still occasionally loses to `built_to_fail` on `built_to_fail`'s own
turf" -- stale. Live measurement showed 0/3 own-profile capture, not
occasional: all three of `the_paper_tiger`'s own dedicated profiles
(`APT-PT-00`/`01`/`02`) were losing to `built_to_fail`. Corrected in
place, same self-correction convention already used elsewhere in that
file. Commit `cd32629`, pushed (Group 1).

### 2. extreme_high_confidence root cause found and fixed -- pushed
**Not an architecture gap, as the Priority Queue had been framing it.**
Root cause: a stale `primary_dimension` field, left unsynced with
`dimensional_vector` during the SCD-WCS full re-authoring program
(Phase 2/Phase 5, 2026-08-24/25). `tools/calibration_runner.py`'s
`best_option_for_state()`/`_build_synthetic_vector()` both key off
`profile.primary_dimension` to decide which dimension's answer options
to maximize for a state's own wired questions -- with the stale label,
three states were generating answers that maximized the wrong
dimension entirely.

Three states fixed, all corrected to `primary_dimension="Authority"`:
`the_paper_tiger`, `invisible_performance_management`,
`the_arbitrary_standard`. Confirmed concretely before fixing, not just
reasoned about: `the_paper_tiger`'s own `Q06` picked an option carrying
`authority_liability=0.00` instead of the correct `0.60`; `Q36` picked
an option carrying `authority_liability=-0.40` (actively negative)
instead of a neutral `0.00` pick.

Full 175-profile suite, across two batches: **166/175 -> 169/175 ->
170/175**. `extreme_high_confidence`: 0/1 -> **1/1**. `high_confidence`:
56/58 -> **58/58 (OK)**. A full registry-wide audit (all 58 states'
`primary_dimension` checked against their `dimensional_vector`'s actual
dominant field) confirmed these three were the only mismatches in the
entire taxonomy, and the only ones the re-authoring program touched
that needed a fix (`the_second_close`/`silosolation`, also touched by
that program, were already correctly labeled).

**Separately, re-tested and confirmed the 2026-08-28 `built_to_fail`
salience-suppression park still holds.** Ran the same full-hierarchy
false-rank-1 census methodology (Phase 8/9's own standard) after these
fixes landed: `invisible_performance_management`'s own false-rank-1
count against `built_to_fail` specifically is **unchanged at 3/3** --
the label fix let it pass one more profile via the calibration suite's
tolerance window, not by genuinely beating `built_to_fail`. The fixes
did not reopen that question.

Commit `49f8796` (the fix) + `cd32629`-adjacent audit-trail scripts,
pushed (Group 1).

### 3. v2 token migration re-examined and closed; 3 new contrast bugs found and fixed -- PUSH HELD
`--home-ink`/`--ink` re-examined per the Sept 7 Section 13a row's open
question. Confirmed live via `getComputedStyle` (not source-reading
alone): the Sept 7 rejection was correct and still holds --
`--home-ink` was deliberately authored to match `--color-charcoal`
(the token already in use sitewide), not `--ink`, and `--ink`/
`--color-charcoal` are genuinely different colors in Warm (`#14171A`
vs. `#26241F`) and Neutral (`#34383C`  vs. `#26241F`) -- only Dark
happens to match. No code change needed for this piece; closed as a
documentation-only re-confirmation.

**While investigating, a full audit of the homepage's hardcoded,
non-theme-reactive Tailwind colors found three real, previously-unknown
WCAG AA failures**, none flagged by any prior session: CTA button
(`bg-charcoal text-white hover:bg-gray-700`, 1.18:1 button-vs-page
contrast in Dark, both near-black); footer text (`text-gray-400`,
2.33:1 in Warm / 2.60:1 in Neutral -- the opposite failure direction
from the CTA); avatar circle text (`text-white` on `bg-(--home-slate)`,
2.94:1 in Dark -- `--home-slate`'s Dark value was correctly tuned for a
different consumer, body text against the page, and never checked
against white text rendered on top of it as a fill).

All three fixed via four new tokens, same `.home-scope`/`[data-theme]
.home-scope` isolation pattern as `--home-slate`/`--home-paper`/
`--home-field-raise`: `--home-cta-bg`, `--home-cta-text`,
`--home-footer-text`, `--home-avatar-text`. All candidates
margin-searched, not guessed, and live-verified via `getComputedStyle`
plus canvas-normalized contrast computation (a first regex-based
parser misread Tailwind v4's `lab()` color output as raw RGB, caught
and corrected before any number was reported or acted on). `tsc
--noEmit` clean.

Commits `6af546c`/`9f8c16e` (the fixes), `0d985aa`/`5c82240` (MOB/
CLAUDE.md updates for this and item 2 above), plus associated patch
scripts -- **all committed, PUSH HELD.** Below-the-fold screenshots of
the three fixed elements could not be captured this session (the
Browser pane was in a hidden state that blocks scroll-dependent
repaint, confirmed reproducible and confirmed not an app problem via
`get_page_text`/`getComputedStyle` both returning correct live values
regardless) -- the standing production-facing-UI exception applies
until a visual check confirms the fix in Dark theme specifically,
where the failure was most severe.

### 4. damages_cap_treatment Phase 1 -- fully scoped, not built
Two rounds of Gemini architecture review, both independently
fact-checked against live code rather than accepted at face value.
Caught one real overclaim: Gemini's proposal described a federal-floor
branch for `no_damages_available` states as reusable existing logic --
confirmed directly (grep + attribute-access search) that
`damages_cap_treatment` is not read anywhere in `friction_tax.py`
outside its own data rows; that branch is net-new work, not a reuse.
Also caught and corrected an incomplete state list Gemini's review
used as illustrative examples (named 6 of 7 `no_damages_available`
states, omitting WI; named 5-6 `uncapped` states when the real list is
23).

**CC's own proactive finding, not raised by either review:** the
flat-cap clamp originally proposed for FL/ID/KS/VA
(`min(curve.ceiling, flat_cap)`) risked materially understating real
exposure, not overstating it -- confirmed directly from ID's own
existing statute comment, which states economic/actual damages are
"available separately, uncapped by" its $1,000 punitive-only cap. The
same structural risk plausibly applies to FL/KS/VA (each caps a
different narrow damage type) but isn't independently confirmed for
those three from what exists in the codebase today.

**Final resolution, Pete's decisions on both open items:** (a) Cluster
4b's existing federal ceiling table stays applied to the 23 `uncapped`
states' claims unchanged -- display only gets a "+" and a clarifying
note (real exposure may exceed the shown figure), no new pricing
mechanism; (b) the FL/ID/KS/VA flat-cap clamp stays exactly as
specified, with the same "+"/note display treatment applied uniformly
to all four (not just ID, since FL/KS/VA's real scope is unconfirmed
either way). Both are output-layer instructions for whenever
Legal/Compliance dollar output is wired to a client surface -- it isn't
today, per `state-coverage-threshold-design.md`'s own
output-generation-constraint section.

**Final spec: `prompts/damages-cap-treatment-phase1-spec.md`, 192
lines** (plus two follow-on resolution passes) -- fully resolved, zero
open blockers. Full scope: new `resolve_damages_treatment()`
jurisdiction-resolution helper (highest-exposure-wins ordering); new
`no_damages_available` federal-floor branch (headcount >= 15 -> treat
as `federal_cap_applies`, price normally; < 15 -> `NOT_APPLICABLE`,
`dollar_range=None`); the two display-layer resolutions above; and
`state_specific_tiers` (9 states: AR/CO/DE/MD/ME/MO/OH/TN/TX)
explicitly deferred to Phase 2 -- no schema exists yet for tiered or
formula-based cap data, and Ohio specifically needs a real formula
(a compensatory/punitive dual-track calculation with a small-employer
carve-out), not a lookup table.

**Nothing built.** Spec is ready for a future build session. Spec file
itself, plus its two resolution-pass patch scripts, held uncommitted
pending this closeout's own commit pass (see git status below).

### 5. New flagged item, not fixed
`EXP-IPM-02` (the moderate-tier profile for
`invisible_performance_management`) fails on the same magnitude/
concentration issue class `the_paper_tiger`'s own former `APT-PT-02`
failure did -- confirmed as a separate, pre-existing issue, untouched
by any of this session's fixes (item 2's fix resolved `EXP-IPM-01`,
the high_confidence profile, but not this one). No urgency -- moderate
tier, not blocking the extreme_high_confidence closure -- but worth its
own look eventually.

### Test suite / verification, this session in full
`tools/calibration_runner.py --dim --verbose`: 166/175 -> 170/175
across item 2's two batches, confirmed live at each step, not assumed.
`tsc --noEmit` clean for the homepage contrast fixes (item 3). No
engine test suite changes this session outside the calibration runner
(item 2 touches only `engine/data/states.py`'s `primary_dimension`
fields, no `tools/test_friction_tax.py` fixture depends on that field).

### On the horizon -- updated Priority Queue
1. Mobile z-index collision (AssemblyPanel vs. phase-transition bars)
   -- still unconfirmed on a real device, untouched this session, was
   next in Pete's stated order but not reached.
2. damages_cap_treatment Phase 1 build -- spec is ready
   (`prompts/damages-cap-treatment-phase1-spec.md`), zero open
   blockers. This is now a "when Pete wants to build it" item, not a
   "when someone scopes it" item.
3. Group 2 push confirmation (homepage contrast fixes) -- committed,
   needs Pete's visual check in Dark theme before pushing. See item 3
   above for the full detail on why screenshots couldn't be captured
   this session.
4. EXP-IPM-02 moderate-tier magnitude weakness -- new this session, low
   priority, same issue class as `the_paper_tiger`'s former `APT-PT-02`.
5. Quarterly Step-Back -- last run August 22, due ~September 5, now
   significantly overdue (session date 2026-09-10). Flag prominently at
   next session open.'''

EDITS = [
    ('version header 4.296 -> 4.297', VERSION_OLD, VERSION_NEW),
    ('append Section 16 closeout entry + Priority Queue', TAIL_OLD, TAIL_NEW),
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
