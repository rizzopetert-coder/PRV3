"""
tools/_mob.txt: full session closeout, five workstreams (VoiceSection
homepage copy, damages_cap_treatment Phase 1 built, damages_cap_treatment
Phase 2 spec + Phase 2a built, mobile z-index collision fixed, EXP-IPM-02
calibration bug fixed). Bumps MOB version v4.297 -> v4.298 and appends a
new Section 16 entry with an updated Priority Queue.

Usage:
    python tools/patch_mob_session_closeout_20260910b.py --dry-run
    python tools/patch_mob_session_closeout_20260910b.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = '\\\\\\#\\\\\\# MOB v4.297'
VERSION_NEW = '\\\\\\#\\\\\\# MOB v4.298'

ANCHOR_OLD = '''5. Quarterly Step-Back -- last run August 22, due ~September 5, now
   significantly overdue (session date 2026-09-10). Flag prominently at
   next session open.'''

ANCHOR_NEW = '''5. Quarterly Step-Back -- last run August 22, due ~September 5, now
   significantly overdue (session date 2026-09-10). Flag prominently at
   next session open.

## SESSION CLOSEOUT (2026-09-10, continuation session) -- damages_cap_treatment
## Phase 1 + Phase 2a built and shipped, mobile z-index collision fixed,
## EXP-IPM-02 calibration bug fixed, homepage VoiceSection copy shipped

### One-line summary
Five workstreams this session, all shipped and live: (1) a 4-paragraph
homepage VoiceSection copy update; (2) damages_cap_treatment Phase 1 --
scoped at the prior closeout, actually built this session across two
rounds (initial build, then a corrections round after diff review caught
two real gaps); (3) damages_cap_treatment Phase 2 -- a spec written after
finding real heterogeneity across the 9 state_specific_tiers states, then
Phase 2a (7 of those 9) built and shipped, with Phase 2b/2c explicitly
parked, not abandoned; (4) the mobile Phase 2 CTA collision (flagged
unconfirmed at the prior closeout) root-caused, fixed, and verified live
on both local and production; (5) EXP-IPM-02, a low-priority calibration
gap flagged at the prior closeout, root-caused to a genuinely new bug
class (stale question wiring, not a repeat of the primary_dimension label
bug) and fixed. All five shipped, committed, pushed, and live -- the two
engine-touching items (damages_cap_treatment, EXP-IPM-02) each triggered
an automatic API redeploy, confirmed READY and live-round-trip-verified
(401 clean auth rejection, not 500) after every push.

### 1. VoiceSection homepage copy update -- pushed, live
Restructured from 3 paragraphs to 4. Added an inline link to
`/book/methodology/symptoms-states-and-why-the-distinction-matters` on
"deeper conditions." Three named leadership behaviors (consistency,
accountability, strong communication) given the hero's existing
`font-semibold text-(--home-slate)` emphasis treatment, rather than a new
style. Verified live in both themes before pushing. Commit `87ccb57`
(copy) + `bfe93fc` (patch-script audit trail).

### 2. damages_cap_treatment Phase 1 -- built, corrected, shipped
Scoped at the prior closeout (v4.297) as a spec only; actually built this
session. `resolve_damages_treatment()` and `_resolve_flat_cap()` helpers;
a `no_damages_available` federal-floor branch (headcount >= 15 prices
normally, < 15 returns genuinely NOT_APPLICABLE); an `is_floor` flag
(originally `uncapped` + `state_specific_flat`, extended to
`state_specific_tiers` in the corrections round below); a `flat_cap`
clamp for FL/ID/KS/VA.

Two build rounds, not one -- a corrections round followed after Pete's
own diff review caught two real gaps the initial build missed: (a)
`state_specific_tiers` states weren't getting `is_floor=True`, dropping
part of the spec's own original intent; (b) a silent, input-order-
dependent tie-break bug in the priority table between
`state_specific_tiers` and `state_specific_flat` -- fixed by ranking flat
strictly higher, since it has a real working clamp mechanism and tiers
doesn't yet.

Suite: `tools/test_friction_tax.py` 120 -> 140 (initial build) -> 144
(corrections). Full 11-script suite: 857 -> 861. Commits `07325f3` (build)
+ `2ef8278`/`59e2733` (patch scripts) + `06f1e6a` (corrections, engine) +
`c69a2f5` (corrections, tests). Pushed, live -- API redeploy confirmed
READY, live round trip returned 401 (clean auth rejection, not 500).

### 3. damages_cap_treatment Phase 2 -- spec written, Phase 2a built and shipped
Phase 1's own summary treated the 9 `state_specific_tiers` states as one
homogeneous deferred group. They aren't. The Phase 2 spec
(`prompts/damages-cap-treatment-phase2-spec.md`) found real, distinct
heterogeneity: MD/MO cap compensatory and punitive TOGETHER, not
independently; TX has an unmodeled claim-type carve-out (sexual-
assault/harassment-retaliation removes its cap entirely, not represented
by this codebase's `claim_type` distinction); CO defers to the federal
Title VII tier table at headcount >= 15, not a self-contained state
table; OH is a genuine formula needing intake fields (`economic_loss`,
`net_worth`) that don't exist in the current intake schema; ME has an
internally-flagged, never-independently-verified sub-detail (its own 15+
employee tier breakpoints).

Gemini-reviewed. Two of Gemini's cited justifications were checked
against source and corrected before the spec was finalized, not accepted
at face value: "credibility over calculation" is real, verbatim text, but
it lives in Section 5's Financial Consequence Architecture, not among the
P-01-P-12 Locked Principles Gemini implied it was numbered under; a
"Verification Before Build" named discipline does not exist anywhere in
this codebase's documentation (confirmed by direct grep) -- the real,
narrower analogue is the existing PARTIAL/CONFIRMED data-confidence
distinction.

Phase 2a (7 states: AR, DE, TN, MD, MO, TX, CO) built and shipped. New
`is_combined_cap` field on `StateCoverageThreshold`, `True` for MD/MO
only. TX confirmed to already get `is_floor=True` automatically -- no
code needed, since `is_floor` is computed generically from the resolved
treatment category, not stored per-state, and Phase 1's corrections
already covered `state_specific_tiers` broadly. CO's federal-deferral
wired via a new, narrow `_co_drives_federal_tier_deferral()` helper,
reusing the existing `_FEDERAL_DEFAULT_THRESHOLD`,
`_CLUSTER_4B_CEILING_BY_HEADCOUNT`, and `resolve_headcount_bucket()` --
no new data mechanism invented, only new connecting logic.

Same diff-review-before-build discipline as Phase 1: reviewing the plan
against live code before writing caught 3 real spec-vs-code mismatches
(TX needed nothing; CO's fix belongs in Cluster 4b only, since Cluster
1's curve is a different, unrelated generic methodology, not the federal
table CO's statute defers to; `resolve_headcount_bucket()` already runs
upstream in `compute_legal_compliance_exposure()`, no need to call it
again inside the cluster functions) plus one genuinely new gap
(`resolve_damages_treatment()` doesn't expose which jurisdiction won a
multi-state resolution, needed for CO's state-specific check -- solved
with a small new helper rather than changing that function's existing
return contract).

Suite: `tools/test_friction_tax.py` 144 -> 164. Full 11-script suite: 861
-> 881. Commits `7f96739` (spec doc) + `7361aaf` (Phase 2a build) +
`54e5013`/`6707290` (patch scripts). Pushed, live -- API redeploy
confirmed READY, live round trip returned 401.

**Phase 2b (OH) and Phase 2c (ME) remain explicitly parked, not
abandoned** -- gated on intake-schema expansion (`economic_loss`,
`net_worth`) and primary-source re-verification of 5 M.R.S.
Sec4613(2)(B)(7)-(8)'s 15+ tier breakpoints, respectively. See Priority
Queue below.

### 4. Mobile z-index collision (AssemblyPanel vs. Phase 2 transition bar) -- fixed, pushed, live
Flagged unconfirmed at the prior closeout; root-caused and fixed this
session. `AssemblyPanel`'s mobile Drawer.Trigger (`fixed bottom-0
left-0 right-0 z-40`) and the Phase 2 transition bar (`fixed bottom-0
left-0 right-0 z-30`) both render simultaneously at `currentPhase ===
2` on mobile, same position, no vertical offset -- the trigger's higher
z-index fully covered the Phase 2 CTA. Confirmed live via
`elementFromPoint()` at the CTA's own center returning the trigger, not
the CTA -- genuinely click-unreachable, not just visually crowded,
before the fix.

Fixed via runtime-measured Option A (Pete's explicit choice among the
options presented): a `ResizeObserver` on `AssemblyPanel`'s mobile
trigger publishes its live height through `SelfSelectionContext` --
reusing the context's existing state-plus-setter pattern (mirroring
`activeSheet`/`setActiveSheet`), no new state-management mechanism. The
Phase 2 bar offsets its own bottom position by that live measurement, so
it stays correct if the trigger's copy or padding ever changes, rather
than a hardcoded pixel value.

Verified at 375px and 320px, both locally and on production: zero
overlap, `elementFromPoint()` correctly resolves to the CTA itself
post-fix, Phase 1's bar confirmed unchanged (no inline style, same rect,
since `AssemblyPanel` never renders before Phase 2). `tsc --noEmit`
clean. Commit `85587c7` (fix) + `daf50b4`/`a4d94af`/`b8ef1a3` (patch
scripts). Pushed, live -- no API redeploy (web/ only, no Python route
bundling).

### 5. EXP-IPM-02 (invisible_performance_management, moderate tier) -- fixed, pushed, live
Flagged low-priority at the prior closeout as "same issue class as
`the_paper_tiger`'s former `APT-PT-02`." It wasn't. First check (the
right one to run before assuming magnitude): `invisible_performance_
management`'s `primary_dimension` still correctly matches its
`dimensional_vector`'s dominant field -- confirmed clean, no regression
from the earlier label-bug fix.

Real root cause was a different, previously-unaudited bug class: `Q35`,
this state's only wired calibration question, had zero positive-
authority options anywhere across its 4 existing options -- a stale
leftover from before the SCD-WCS re-authoring flipped this state from
Aptitude to Authority-dominant, sitting in a data structure
(`engine/data/questions.py`'s per-question `state_targets`/
`dimensional_contributions`) the earlier `primary_dimension` audit never
checked. A registry-wide audit confirmed this bug is isolated -- `the_
paper_tiger`'s and `the_arbitrary_standard`'s own question wiring (the
other two states fixed alongside this one in the earlier label bug) both
checked clean, no recurrence of the same failure mode.

Fixed by adding a new option (`E`) to `Q35` carrying a correct, clean
`authority_liability: +0.60`, following the existing `Q34`/`Q36`
precedent for state-specific contrast options. Confirmed directly, not
assumed: `Q35`'s other 3 wired states (`built_to_fail`, `the_undefined_
role`, `the_overloaded_manager`) still resolve to option B exactly as
before.

Suite: 170/175 -> 171/175. Honest result, not oversold: score 0.556 ->
0.770, rank 49 -> 41 of ~58. Now clears the moderate-tier prominence
margin comfortably (by 0.134), but is NOT rank-1 and NOT structurally
strong -- the state still has only 1 wired question in the entire
calibration library, an independent, still-unaddressed thin-signal
weakness (see Priority Queue). Commit `e8f82a8` (fix) + `b4a28e9` (patch
script). Pushed, live -- API redeploy confirmed READY (via `engine.main`'s
transitive import of `engine.data.questions`, not a direct import), live
round trip returned 401.

### New flagged items, not fixed this session
- `built_to_fail`'s false-rank-1 baseline drift: Phase 9 recorded 52/175,
  this session's own live measurement (incidental, during the EXP-IPM-02
  investigation) found 80/175. Unexplained, independent of anything fixed
  this session. Worth its own dedicated investigation.
- `invisible_performance_management` and `the_founders_grip` share a
  byte-identical `dimensional_vector` AND `salience_weights` -- confirmed
  real, not a coincidence. Not the cause of any current failure (only
  `invisible_performance_management`'s own profiles were failing), but a
  latent taxonomy question: two states mathematically indistinguishable
  to the scoring engine. Worth a look whenever that area is revisited.
- `invisible_performance_management`'s thin question-wiring (1 of 52 core
  questions) -- EXP-IPM-02 now passes on margin, not distinctiveness.
  Likely to resurface if the moderate-tier bar tightens or a stricter
  profile targeting this state is ever added.
- AssemblyPanel/Phase-2-CTA merge (Option C from the mobile z-index
  investigation): combine the trigger and the CTA into one row instead of
  stacking two, to reduce the ~142px of stacked bottom UI the shipped fix
  introduces. A deliberate future design pass, not urgent -- the shipped
  fix is fully functional as-is.

### Test suite / verification, this session in full
`tools/test_friction_tax.py`: 120 -> 140 -> 144 (Phase 1 build +
corrections) -> 164 (Phase 2a). Full 11-script suite: 857 -> 861 (Phase
1) -> 881 (Phase 2a). `tools/calibration_runner.py --verbose`: 170/175 ->
171/175 (EXP-IPM-02 fix). `tsc --noEmit` clean for the mobile z-index
fix. Every engine-touching push (Phase 1, Phase 2a, EXP-IPM-02) triggered
an automatic Vercel API redeploy via `api/engine.py`'s import chain --
each confirmed READY and live-round-trip-verified (POST `/api/engine`
against production returning 401, a clean auth rejection, not a 500)
before being reported done.

### On the horizon -- updated Priority Queue
1. `damages_cap_treatment` Phase 2b (OH) -- gated on intake-schema
   expansion (`economic_loss`, `net_worth` fields don't exist yet). Not
   actionable until that expansion is scoped.
2. `damages_cap_treatment` Phase 2c (ME) -- gated on primary-source
   re-verification of 5 M.R.S. Sec4613(2)(B)(7)-(8)'s 15+ employee tier
   breakpoints, already internally flagged as unverified in ME's own
   existing code comment.
3. `built_to_fail` false-rank-1 baseline drift (52/175 Phase-9-recorded ->
   80/175 measured live this session) -- unexplained, needs its own
   dedicated investigation.
4. AssemblyPanel/Phase-2-CTA merge (Option C) -- design pass to reduce
   stacked bottom UI on mobile, not urgent, current fix fully functional.
5. `invisible_performance_management`'s thin question-wiring -- low
   priority, revisit if the moderate-tier calibration bar ever tightens.
6. `invisible_performance_management`/`the_founders_grip` vector
   duplicate -- latent taxonomy question, no urgency.
7. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.'''

EDITS = [
    ('version header 4.297 -> 4.298', VERSION_OLD, VERSION_NEW),
    ('append Section 16 closeout entry + Priority Queue', ANCHOR_OLD, ANCHOR_NEW),
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
