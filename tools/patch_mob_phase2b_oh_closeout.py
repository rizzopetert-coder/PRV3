"""
tools/_mob.txt: Phase 2b (OH) built, pushed, and live-verified this
session -- corrects v4.298's Priority Queue framing (gated on
economic_loss/net_worth) to reflect what was actually built
(QUALITATIVE_ONLY, no schema change needed). Also documents the
mid-session test-count tracking correction (7 of 11 suite scripts'
real pass counts were never being summed into the reported "full suite
total" across the first three Phase 2b checkpoints this session --
nothing was ever failing, the reported totals just undercounted).

Bumps MOB version v4.298 -> v4.299 (locked decision + workstream status
change) and appends a new Section 16 entry. Does NOT edit v4.298's own
entry in place -- that record was accurate for its time (Phase 2b was
genuinely gated when it was written); this is normal supersession from
later work in a new session block, not a correction of an error.

Usage:
    python tools/patch_mob_phase2b_oh_closeout.py --dry-run
    python tools/patch_mob_phase2b_oh_closeout.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = '\\\\\\#\\\\\\# MOB v4.298'
VERSION_NEW = '\\\\\\#\\\\\\# MOB v4.299'

ANCHOR_OLD = '''7. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.'''

ANCHOR_NEW = '''7. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.

## SESSION CLOSEOUT (2026-09-11, continuation session) -- damages_cap_treatment
## Phase 2b (OH) built and shipped, direct engine/contract.py test added,
## mid-session test-count tracking corrected

### One-line summary
Two workstreams this session. (1) `damages_cap_treatment` Phase 2b (OH),
listed gated at the prior closeout, was investigated fresh (the
`economic_loss`/`net_worth` gating framing didn't survive contact with
live code) and built: OH now resolves `QUALITATIVE_ONLY` in Clusters 1,
2, and 4b, with no intake schema change and no UI change needed --
confirmed both `unpriced_state_ids` and `PrivateOutput.tsx`'s
unpriced-state copy already existed. A follow-up pass added a direct
`engine/contract.py`-level test of the `legal_tail_risk_exposure` guard
via a real `SessionData`/OH fixture, closing a gap the first build pass
had only confirmed by shape-matching to an existing precedent rather
than testing directly. (2) A mid-session correction: the "full suite
total" reported at each of this workstream's first three checkpoints
only ever summed 4 of the 11 standing test scripts -- the other 7 were
passing the entire time, just never counted. Corrected once discovered;
the real, complete total confirmed this session is below.

### 1. damages_cap_treatment Phase 2b (OH) -- built, shipped, live
**Superseded framing, confirmed before any code was written.** The
original Phase 2b framing (`prompts/damages-cap-treatment-phase2-spec.md`,
as of v4.298) said OH was blocked on `economic_loss`/`net_worth`
becoming real intake fields. Investigated directly against live code
before treating that as settled: `economic_loss` was never really the
blocker, since no cluster in `engine/friction_tax.py` computes a
compensatory-damages figure at all -- there was nothing to multiply
`economic_loss` against even if the field existed. And OH's own
`STATE_COVERAGE_THRESHOLDS` entry was never actually gated -- run
against the live pipeline, it resolved `PRICED` via the generic curve
every other un-built `state_specific_tiers` state falls through to, not
`DATA_INTEGRITY_GAP`/`NOT_APPLICABLE` as first assumed.

Separately verified specific claims from a Gemini architecture review
before treating any of them as cleared for build: `unpriced_state_ids`
is real (confirmed by direct grep, not assumed); `PrivateOutput.tsx`'s
quoted UI copy was close but not verbatim (colon vs. period, a real
structural difference); Cluster 4c (Government) is **not** the only
`QUALITATIVE_ONLY` consumer -- Cluster 3's unclassifiable-headcount
branch (`engine/friction_tax.py` ~3325-3337) is a second, structurally
different one, and the closer precedent for OH (real exposure that
can't currently be resolved to a number, vs. no data existing by
design); the intake-aware routing gate's mechanics (raw `headcount` int
available before bucketing, both threshold values genuinely
selectable) checked out.

**Built:** OH resolves `QUALITATIVE_ONLY` in all three clusters that
consult `resolve_damages_treatment()` (1, 2, 4b -- confirmed this
applies identically to all three, unlike CO's Phase 2a fix, which only
belonged in Cluster 4b). New `_oh_drives_tiers_result()` helper mirrors
`_co_drives_federal_tier_deferral()`'s shape. OH's citation comment
rewritten to state both of R.C. 2315.21's statutory branches plainly.
No intake schema change, no UI change -- proven by reaching the exact
same code path the Government/`hr_capture` case already exercises.

**`_oh_is_small_employer()` built, tested, and intentionally NOT wired
into any pricing branch.** R.C. 2315.21(D)(2)(b)'s own gate (`<=100`
full-time employees generally, `<=500` if NAICS-manufacturing-
classified) -- both of that statute's branches resolve to the identical
`QUALITATIVE_ONLY` result today, so calling this helper from the
pricing path would compute a real answer and discard it. It's a
standalone, directly-tested piece of correct logic, ready for whenever
a real compensatory-damages/net-worth pricing path is built and
actually needs it.

**NAICS-vs-"Manufacturing & Industrial" mapping gap: documented
approximation, not a blocker.** This app's `"Manufacturing & Industrial"`
`INTAKE_FIELDS["industry"]` bucket is not identical to Ohio's real
NAICS-manufacturing test -- may sweep in adjacent non-manufacturing
industrial activity (utilities, mining) that wouldn't actually qualify
under the statute. No NAICS-level intake data exists to resolve this
precisely. Flagged in `_oh_is_small_employer()`'s own docstring and in
`STATE_COVERAGE_THRESHOLDS["OH"]`'s citation comment -- doesn't block
anything today, since the helper isn't consumed by any pricing branch
yet, but will need resolving (or living with) whenever it is.

**Direct `engine/contract.py` test added, closing a gap the first build
pass had left inferred rather than proven.** `engine/contract.py` had
no test file of its own listed in this workstream's original scope --
confirmed one already exists (`tools/test_contract.py`, one of the 11
standing suite scripts) and is the right home, not a new file. Built a
dedicated `SessionData` fixture (`jurisdictions=["OH"]`,
`"the_paper_tiger"` as the identified state) and confirmed
`engine/contract.py:574`'s `legal_tail_risk_exposure` guard (`low is
not None or has_unpriced_conditions`) renders non-null for OH's real
`QUALITATIVE_ONLY` result directly through `assemble_output()`, rather
than inferring it from the already-proven Government/`hr_capture` shape
as the prior pass had done.

Suite: `tools/test_friction_tax.py` 164 -> 179. `tools/test_contract.py`
144 (was already at 140, +4 from this session's addition). Commits
`afcddfe` (engine build) + `06dfb0a` (patch script) + `723d7cb`
(friction_tax tests) + `7c1efe7` (patch script) + `aac4b41` (contract
test) + `874e6e3` (patch script) + `b92ffeb` (spec rewrite) + `9821b85`
(patch script). Pushed, live -- API redeploy confirmed READY (commit
`9821b85`), live round trip returned 401 (clean auth rejection, not
500).

### 2. Mid-session test-count tracking correction
Running each of the 11 standing suite scripts individually (rather than
tailing their last 3 lines, which is all that had been done at every
prior checkpoint) surfaced that 7 of them print a real numeric pass
count that had never been captured: `test_narrative.py` (70),
`test_checkpoint.py` (58), `test_contract.py` (144 as of this session),
`test_accumulation.py` (43), `test_output.py` (112), `test_severity.py`
(75), `test_aut_ps_01_q23_d_forced.py` (8). Every "full suite total"
reported at this workstream's first three checkpoints (896, and the
881/861/857 baselines it built on) only ever summed the 4 scripts that
print `"PASS: N FAIL: N"` in that exact format (`test_main.py`,
`test_output_synthesis.py`, `test_resolution_families.py`,
`test_friction_tax.py`) -- the other 7 were correctly running and
passing at every single one of those checkpoints, just silently
contributing 0 to the running total instead of their real counts.

**Nothing was ever actually broken or unverified.** Every script
genuinely ran and genuinely passed at every checkpoint this session --
only the specific numbers quoted as "full suite totals" understated
what was really being confirmed. The real, complete total across all
11 scripts, confirmed this session: **900 passed, 0 failed.**

### Test suite / verification, this session in full
`tools/test_friction_tax.py`: 164 -> 179. `tools/test_contract.py`: 140
-> 144. Full 11-script suite, every script's real count now captured
and summed directly (not inferred or partially tracked): **900 passed,
0 failed.** Both engine-touching pushes this session (Phase 2b build,
the `test_contract.py` addition touches no engine file but rides the
same deploy) triggered an automatic Vercel API redeploy, confirmed
READY, live round trip returned 401.

### On the horizon -- updated Priority Queue
1. `damages_cap_treatment` Phase 2c (ME) -- gated on primary-source
   re-verification of 5 M.R.S. Sec4613(2)(B)(7)-(8)'s 15+ employee tier
   breakpoints, already internally flagged as unverified in ME's own
   existing code comment. (Phase 2b/OH is now built and shipped --
   dropped from this list.)
2. `built_to_fail` false-rank-1 baseline drift (52/175 Phase-9-recorded ->
   80/175 measured live in a prior session) -- unexplained, needs its
   own dedicated investigation.
3. AssemblyPanel/Phase-2-CTA merge (Option C) -- design pass to reduce
   stacked bottom UI on mobile, not urgent, current fix fully functional.
4. `invisible_performance_management`'s thin question-wiring -- low
   priority, revisit if the moderate-tier calibration bar ever tightens.
5. `invisible_performance_management`/`the_founders_grip` vector
   duplicate -- latent taxonomy question, no urgency.
6. `_oh_is_small_employer()` -- built and tested, not wired into any
   pricing branch. Revisit whenever a real compensatory-damages/
   net-worth pricing path for OH is scoped.
7. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) -- documented
   approximation in `_oh_is_small_employer()`'s docstring and OH's
   citation comment. No NAICS-level intake data exists to resolve it
   precisely; revisit only if OH's small-employer routing is ever wired
   into a real pricing path.
8. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.'''

EDITS = [
    ('version header 4.298 -> 4.299', VERSION_OLD, VERSION_NEW),
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
