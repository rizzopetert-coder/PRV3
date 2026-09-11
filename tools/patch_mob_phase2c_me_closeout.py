"""
tools/_mob.txt: Phase 2c (ME) built, pushed, and live-verified this
session -- closes out the ENTIRE damages_cap_treatment Phase 2
initiative (2a shipped this session's earlier work, 2b shipped this
session's prior closeout, 2c shipped now). Corrects the Priority
Queue's ME line (was "gated on primary-source re-verification") to
reflect what was actually done -- that re-verification happened this
session and resolved cleanly.

Bumps MOB version v4.299 -> v4.300 (locked decision + workstream status
change) and appends a new Section 16 entry. Does not edit the v4.299
entry in place -- that record was accurate for its time.

Usage:
    python tools/patch_mob_phase2c_me_closeout.py --dry-run
    python tools/patch_mob_phase2c_me_closeout.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = '\\\\\\#\\\\\\# MOB v4.299'
VERSION_NEW = '\\\\\\#\\\\\\# MOB v4.300'

ANCHOR_OLD = '''8. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.'''

ANCHOR_NEW = '''8. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.

## SESSION CLOSEOUT (2026-09-11, continuation session) -- damages_cap_treatment
## Phase 2c (ME) built and shipped, closing the full Phase 2 initiative

### One-line summary
`damages_cap_treatment` Phase 2c (ME), listed gated at the prior
closeout on primary-source re-verification of its own flagged 15+
employee tier breakpoints, was re-verified directly against
mainelegislature.org this session and built -- data population only,
zero engine logic change, same shape as Phase 2a's AR/DE/TN. This
closes the entire `damages_cap_treatment` Phase 2 initiative: 2a (7
states) shipped earlier this session, 2b (OH) shipped at the prior
closeout, 2c (ME) shipped now. All 9 `state_specific_tiers` states from
the original Phase 1 deferral are now either fully resolved
(`QUALITATIVE_ONLY` for OH) or carry an accurate, source-verified
citation comment documenting their real statutory mechanics even where
the dollar figures themselves remain unconsumed by pricing logic
(AR/DE/TN/TX/MD/MO/CO/ME).

### 1. damages_cap_treatment Phase 2c (ME) -- built, shipped, live
**Confirmed before building, not assumed:** ME's entry sat at the exact
generic `state_specific_tiers` fallthrough Pete flagged as the expected
"before" state (the same situation OH was in before its own build) --
run against the live pipeline, `PRICED` via the generic curve with
`is_floor=True`, same as AR/DE/TN/TX today. This confirmed the build
needed zero engine logic changes -- data population into the
already-shipped architecture, not a new mechanism, matching Phase 2a's
AR/DE/TN precedent rather than CO/OH's dedicated-helper precedent.

**Two corrections to the prior citation/comment, both confirmed
against primary source (mainelegislature.org, current through Oct. 1,
2025, last amended PL 2023, c. 263, Sec1) this session, not the prior
phrasing:**
1. 5 M.R.S. Sec4613(2)(B)(7) and (8) are two separate remedies, not one
   joint provision -- the prior citation cited them together as
   "(7)-(8)". (7) is civil penal damages (non-employment/<=14-employee
   cases, tiered by violation order, not headcount). (8) is the real
   employment tier table (15+ employees, tiered by headcount). Split
   into two separately-labeled citations.
2. The prior comment stated the top employment bracket as "$500,000" --
   that was actually the 201-500 tier's own figure; the real top
   bracket (501+) is **$1,000,000**. The prior verification pass
   stopped one tier short. Corrected against the full, current
   (8)(e)(i)-(iv) table: $100,000 (15-100) / $300,000 (101-200) /
   $500,000 (201-500) / $1,000,000 (501+).

**Two unmodeled carve-outs added, stated by the statute itself, not
invented** -- `is_floor=True` (already automatic for every
`state_specific_tiers` state) is the existing caveat mechanism for
both, same semantics as TX's own claim-type carve-out: (8)(f) (the cap
does not limit recovery under 42 U.S.C. Sec1981, itself uncapped --
real stacking exposure) and (8)(h) (the tier caps do not apply to
claims unlawful solely due to disparate impact).

**Tests:** six boundary-headcount checks at ME's real tier edges
(100/101, 200/201, 500/501) confirming the generic placeholder behavior
stays stable across every one of them, one Cluster 4b check, one full
aggregate-shape check. Suite: `tools/test_friction_tax.py` 179 -> 188.
Full 11-script suite (every script's real count summed directly): 900
-> 909.

Commits `d7a775d` (citation correction) + `404c2f8` (patch script) +
`92f7262` (tests) + `1b89507` (patch script). Pushed, live -- API
redeploy confirmed READY, live round trip returned 401 (clean auth
rejection, not 500).

### Test suite / verification, this session in full
`tools/test_friction_tax.py`: 179 -> 188. Full 11-script suite: 900 ->
909, all passing. API redeploy confirmed READY, live round trip
returned 401.

### On the horizon -- updated Priority Queue
1. `built_to_fail` false-rank-1 baseline drift (52/175 Phase-9-recorded
   -> 80/175 measured live in a prior session) -- unexplained, needs
   its own dedicated investigation.
2. AssemblyPanel/Phase-2-CTA merge (Option C) -- design pass to reduce
   stacked bottom UI on mobile, not urgent, current fix fully
   functional.
3. `invisible_performance_management`'s thin question-wiring -- low
   priority, revisit if the moderate-tier calibration bar ever
   tightens.
4. `invisible_performance_management`/`the_founders_grip` vector
   duplicate -- latent taxonomy question, no urgency.
5. `_oh_is_small_employer()` -- built and tested, not wired into any
   pricing branch. Revisit whenever a real compensatory-damages/
   net-worth pricing path for OH is scoped.
6. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) -- documented
   approximation in `_oh_is_small_employer()`'s docstring and OH's
   citation comment. No NAICS-level intake data exists to resolve it
   precisely; revisit only if OH's small-employer routing is ever wired
   into a real pricing path.
7. Quarterly Step-Back -- last run August 22, now multiple sessions
   overdue. Flag prominently at next session open, don't let this keep
   sliding.

(`damages_cap_treatment` Phase 2 -- 2a, 2b, and 2c -- is now fully
shipped and dropped from this list entirely.)'''

EDITS = [
    ('version header 4.299 -> 4.300', VERSION_OLD, VERSION_NEW),
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
