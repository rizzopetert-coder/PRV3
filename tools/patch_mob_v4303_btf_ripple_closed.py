"""
tools/_mob.txt: close Priority Queue item 2 (built_to_fail's 16-profile
ripple from f88a7c2) with the confirmed root cause. Docs-only record
correction closing an investigation -- no fix, no build.

Bumps MOB version v4.302 -> v4.303 (a Priority Queue item closes with a
confirmed mechanism -- workstream status changes materially). Appends a
new closeout entry after the existing v4.302 entry's own trailing
Priority Queue snapshot, left untouched as a historical record --
matching this file's existing append-only pattern.

Usage:
    python tools/patch_mob_v4303_btf_ripple_closed.py --dry-run
    python tools/patch_mob_v4303_btf_ripple_closed.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = r'\\\#\\\# MOB v4.302'
VERSION_NEW = r'\\\#\\\# MOB v4.303'

TAIL_ANCHOR_OLD = '''11. Quarterly Step-Back -- due next week, per Pete's correction this
    session (not overdue -- the prior "last run August 22" framing
    carried in this queue since MOB v4.279 undercounted; Pete's own
    scheduling correction is authoritative here, not independently
    re-derived this session).'''

NEW_ENTRY = '''

## SESSION CLOSEOUT (2026-09-13, continuation session) -- built_to_fail's
## 16-profile ripple from f88a7c2 root-caused and CLOSED

### One-line summary
Priority Queue item 2 (`built_to_fail`'s 16-profile ripple from
`f88a7c2`, open since MOB v4.301) is now CLOSED. Confirmed local
one-state substitution (Hypothesis A), not a global/systemic scoring
dependency -- report-only, no fix, no build, per this investigation's
own scope.

### Root cause, confirmed with exact evidence
All 16 flipped profiles trace to exactly one displaced state --
`invisible_performance_management` (IPM) -- which was itself
Aptitude-dominant before `f88a7c2` re-authored it onto Authority.
`built_to_fail` (the taxonomy's only other strong Aptitude attractor,
untouched throughout, byte-identical `dimensional_vector`/`SALIENCE_PROFILES`
confirmed directly at both `322ea93` and `f88a7c2`, byte-identical own
score before and after in all 16 cases, e.g. `0.951765` -> `0.951765`)
simply inherited the #1 spot once its sole close competitor moved
off-axis. IPM was ranked #1 and `built_to_fail` #2, by a razor-thin
margin, for all 16 profiles at `322ea93` -- confirmed by pulling full
top-2 rankings at both commits, not just win/loss.

**Ruled out structurally, not just empirically:** `rank_states()`
(`engine/accumulation.py:524-594`) computes every state's score in
isolation against the session's accumulated vector -- no percentile,
softmax, or population-relative step anywhere in the function. One
state's score cannot depend on another state's data by construction,
confirmed by reading the complete function body.

**Not a new mechanism.** `prompts/scd-wcs-remediation-tracker.md`'s
Stage 3 finding already named this exact pattern for one profile
(`the_exposed`) and explicitly declined to chase it further: *"once
Phase 5 moved IPM onto Authority, `built_to_fail` (the taxonomy's other
major Aptitude attractor, untouched throughout) absorbed the vacated
ground... Not chased down further."* This investigation enumerates the
other 15.

**Confirmed no overlap with the already-tracked rank-3 cluster:**
neither `built_to_fail` nor any of the 13 flipped-to states belongs to
the already-diagnosed 8-state rank-3 cluster (Priority Queue item 5).
IPM itself only became a rank-3 member as a side effect of `f88a7c2`
re-authoring it -- confirmed via the tracker's own Stage 3 Step 1
("this membership is newly true as of commit `f88a7c2`"). The rank-3
mechanism and this ripple are unrelated in substance, sharing only a
trigger commit and a triggering state (IPM).

**Two extra rows correctly excluded from this ripple's 16/13 count:**
`ALL-AS-02`/`03` (target `the_arbitrary_standard`) also flip to
`built_to_fail` at `f88a7c2`, but that state was one of the 5 directly
re-authored by that commit -- its own-profile loss is the already-
documented, separate primary_dimension desync mechanism (MOB v4.301),
not part of this ripple.

No fix proposed or applied, per this investigation's explicit scope.
Full working data (top-2 rankings at both commits, per profile) produced
via isolated git worktrees, not committed (scratch, cleaned up).

### On the horizon -- updated Priority Queue
1. `built_to_fail` false-rank-1 baseline drift -- CLOSED (MOB v4.301).
2. `built_to_fail`'s 16-profile ripple from `f88a7c2` -- **CLOSED, this
   session.** Confirmed local one-state substitution (Hypothesis A), not
   a global/systemic scoring dependency. All 16 flipped profiles trace
   to exactly one displaced state -- `invisible_performance_management`
   -- which was itself Aptitude-dominant before `f88a7c2` re-authored it
   onto Authority. `built_to_fail` (the taxonomy's only other strong
   Aptitude attractor, untouched throughout, byte-identical vector/
   salience at both commits, byte-identical score before and after in
   all 16 cases) simply inherited the #1 spot once its sole close
   competitor moved off-axis. Ruled out structurally, not just
   empirically: `rank_states()` (`engine/accumulation.py:524-594`)
   computes every state's score in isolation against the session's
   accumulated vector, with no percentile/softmax/population-relative
   step -- one state's score cannot depend on another's by construction.
   Not a new mechanism -- it's the same pattern
   `prompts/scd-wcs-remediation-tracker.md`'s Stage 3 already named for
   a single profile (`the_exposed`) and explicitly declined to chase
   further; this investigation enumerates the other 15. Confirmed
   neither `built_to_fail` nor any of the 13 flipped-to states belongs
   to the already-tracked 8-state rank-3 cluster (item 5 below) --
   unrelated in substance, sharing only a trigger commit and a
   triggering state.
3. AssemblyPanel/Phase-2-CTA merge (Option C) -- CLOSED (MOB v4.302).
4. `invisible_performance_management`'s thin question-wiring -- CLOSED
   (MOB v4.302). Own-profile calibration capture rate remains 0/3,
   unchanged, tracked under item 5 below, not reopened by that fix.
5. `invisible_performance_management`/`the_founders_grip` vector
   duplicate -- corrected record (MOB v4.302). Confirmed deliberate, not
   an oversight; part of the already-diagnosed 8-state rank-3 cluster
   issue tracked in `prompts/scd-wcs-remediation-tracker.md`; confirmed
   latent, not live. Out of scope to fix in isolation. No urgency.
6. Diagnostic result export (copy-as-text) -- SHIPPED, this session.
   "Copy results" button live on `PrivateOutput.tsx`, comprehensive
   scope, visible to all respondents. See this session's own build entry.
7. Long-screenshot capture on the diagnostic page -- root cause
   unconfirmed, no repro obtainable in this environment. Not worth
   restructuring persistent nav to chase given item 6 above serves the
   actual underlying need more directly. Revisit only if Pete confirms
   the export feature doesn't fully cover the use case.
8. Diagnostic back button -- single-step undo SHIPPED, this session
   (question-by-question path only: `session/undo`, pre-filled
   re-render). Confirmed never built on the self-select path at all --
   still a net-new feature request there, unscoped.
9. `_oh_is_small_employer()` -- built and tested, not wired into any
   pricing branch. Revisit whenever a real compensatory-damages/
   net-worth pricing path for OH is scoped.
10. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) -- documented
    approximation in `_oh_is_small_employer()`'s docstring and OH's
    citation comment. No NAICS-level intake data exists to resolve it
    precisely; revisit only if OH's small-employer routing is ever
    wired into a real pricing path.
11. Quarterly Step-Back -- due next week, per Pete's correction (not
    overdue -- the prior "last run August 22" framing carried in this
    queue since MOB v4.279 undercounted; Pete's own scheduling
    correction is authoritative here, not independently re-derived).'''

EDITS = [
    ('version header 4.302 -> 4.303', VERSION_OLD, VERSION_NEW),
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

    # TAIL_ANCHOR_OLD text is not required to be unique in the file --
    # only that the file's true end matches it, so we know we're
    # appending after the live snapshot and not blind.
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
