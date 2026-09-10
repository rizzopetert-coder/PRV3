"""
tools/_mob.txt: retroactive Section 13a + Section 16 entry for the
extreme_high_confidence fix (previously only a footnote in the
homepage entry's Priority Queue). Removes the item from the Priority
Queue entirely since it's now closed, not just flagged stale.

Three edits:
1. Version header: v4.295 -> v4.296.
2. New Section 13a row, inserted directly after the just-closed v2
   token migration row (chronologically first among today's work).
3. Priority Queue: remove item 2 (extreme_high_confidence), renumber
   remaining items, in the tail Section 16 entry.

Usage:
    python tools/patch_mob_extreme_hc_retroactive_entry.py --dry-run
    python tools/patch_mob_extreme_hc_retroactive_entry.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = '\\\\\\#\\\\\\# MOB v4.295'
VERSION_NEW = '\\\\\\#\\\\\\# MOB v4.296'

ROW_ANCHOR_OLD = '''Closed -- no further check-in. Reopens only if Pete decides to deliberately migrate the homepage onto v2 tokens as a new, separate design decision, not a re-investigation of this row. |'''

NEW_ROW = '''

| `extreme_high_confidence` calibration tier stuck at 0/1 -- root cause found: stale `primary_dimension` on 3 states, not a signal-generation or vector problem | N/A -- infrastructure/calibration bug, live-verified, closed | CLOSED this session -- root-caused, fixed, and re-verified via 2 full 175-profile suite reruns | `tools/calibration_runner.py`'s `best_option_for_state()`/`_build_synthetic_vector()` both key off `profile.primary_dimension` (via `_DIM_TO_LIABILITY_FIELD`) to decide which dimension's answer options to maximize for a state's own wired questions. `the_paper_tiger`'s `primary_dimension` still read `"Aptitude"`, stale since before the SCD-WCS full re-authoring program deliberately moved its `dimensional_vector` to Authority-dominant (Phase 2/5, 2026-08-24/25) -- the label field was never updated alongside the vector. Confirmed concretely, not just reasoned about: on `the_paper_tiger`'s own wired question `Q06`, the buggy code picked an option carrying `authority_liability=0.00` instead of the correct authority-maximizing option's `0.60`; on `Q36` it picked an option carrying `authority_liability=-0.40` (actively negative) instead of a neutral `0.00` pick -- a full `1.00` of authority signal the state's own generated answers were never delivering.

**Fix, batch 1 (`the_paper_tiger` alone):** `primary_dimension` corrected `"Aptitude"` -> `"Authority"` in `engine/data/states.py`. Full 175-profile suite: **166/175 -> 169/175** (+3). `extreme_high_confidence`: **0/1 -> 1/1**. `high_confidence`: 56/58 -> 57/58. `moderate`: 52/58 -> 53/58. `the_paper_tiger`'s own by-state count: 1/4 -> 4/4 (`APT-PT-00`/`01`/`02` all newly passing; `APT-PT-03`, weak, was already passing).

**Full-registry audit, same session:** checked all 58 states' `primary_dimension` against their `dimensional_vector`'s actual dominant liability field (no ties in either case found). Two more real instances of the exact same bug, both from the identical SCD-WCS re-authoring program: `invisible_performance_management` (declared `"Aptitude"`, vector dominant `authority_liability=0.60`, that state's own vector comment explicitly says "Full axis flip... the entire deficiency described is evidentiary/documentation weight (Authority)") and `the_arbitrary_standard` (declared `"Alliance"`, vector dominant `authority_liability=0.35` vs. `alliance_liability=0.25`, that state's own comment: "this state's text is Authority-centered... Ends the mechanical tier-template tie"). Cross-checked directly against the program's own vector-comment tags (2026-08-24/25 dates) to confirm completeness, not just the blanket 58-state sweep: exactly 5 states total were touched by that program (`the_paper_tiger`, `invisible_performance_management`, `the_arbitrary_standard`, plus `the_second_close`/`silosolation`, both already correctly labeled, no fix needed).

**Fix, batch 2 (`invisible_performance_management` + `the_arbitrary_standard`):** both corrected to `"Authority"`. Full 175-profile suite: **169/175 -> 170/175** (+1). `high_confidence` reached full pass (`OK`, 58/58). `invisible_performance_management`'s own by-state count: 1/3 -> 2/3 (`EXP-IPM-01` newly passing; `EXP-IPM-02`, moderate, still fails its own separate prominence-criterion issue, same magnitude/concentration class as `the_paper_tiger`'s `APT-PT-02`, untouched by this fix). `the_arbitrary_standard`: 3/3 both before and after (was already passing via cluster-window tolerance; the fix changed which rival it's tolerance-close to, not its pass status).

**Net across both batches: 166/175 -> 170/175, `extreme_high_confidence` 0/1 -> OK (1/1).** `tsc --noEmit` N/A (Python engine changes only).

**`built_to_fail` false-rank-1 re-census, confirming the 2026-08-28 salience park still holds:** re-ran `build_confusion_matrix()`'s full-hierarchy false-rank-1 count (same Phase 8/9 methodology) after both fixes landed. Total dropped 80/175 -> 73/175 -- but `invisible_performance_management`'s OWN false-rank-1 count against `built_to_fail` specifically is **unchanged at 3/3**, confirmed via the confusion matrix (`invisible_performance_management -> built_to_fail x3, correct 0/3`), identical before and after the label fix. The label bug let `invisible_performance_management` pass one more profile via the calibration suite's own tolerance window, not by genuinely beating `built_to_fail` -- same "legitimate pass, not real recapture" pattern already established for `the_paper_tiger`. **Confirms the tracker's `built_to_fail`-dominance explanation for `invisible_performance_management` still holds** -- the label bug was a real, separate, compounding problem, not the actual root cause the 2026-08-28 park was about. No reason to reopen that park based on this finding. Full detail: `prompts/scd-wcs-remediation-tracker.md`'s own `the_paper_tiger` row (corrected same session, see that row's own entry) and the four `tools/_scdwcs_*.py`/`tools/patch_*.py` scratch/patch scripts from this work (committed as their own audit trail). | This session (Claude Code), 2026-09-10 | Closed -- no further check-in. If `EXP-IPM-02`'s own prominence-criterion failure or any other state's `primary_dimension` mismatch surfaces later, treat it as a new incident, not a reopening of this row. |'''

TAIL_OLD = '''### On the horizon -- updated Priority Queue
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
   false-rank-1 re-census).'''

EDITS = [
    ('version header 4.295 -> 4.296', VERSION_OLD, VERSION_NEW),
    ('insert new Section 13a row: extreme_high_confidence fix', ROW_ANCHOR_OLD, ROW_ANCHOR_OLD + NEW_ROW),
    ('Priority Queue: remove closed extreme_high_confidence item', TAIL_OLD, TAIL_NEW),
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
