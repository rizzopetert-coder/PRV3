"""
tools/_mob.txt: session closeout for batch 9 (IA/MI/SC) -- this closes
the entire multi-session PARTIAL-state coverage-threshold verification
workstream. 51 of 51 jurisdictions now CONFIRMED.

Two edits:
1. Version header (line 9): v4.293 -> v4.294.
2. Append new Section 16 entry at end of file (verbatim text supplied
   by Pete).

Usage:
    python tools/patch_mob_section16_coverage_workstream_complete.py --dry-run
    python tools/patch_mob_section16_coverage_workstream_complete.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = '\\\\\\#\\\\\\# MOB v4.293'
VERSION_NEW = '\\\\\\#\\\\\\# MOB v4.294'

TAIL_OLD = '''### On the horizon -- updated Priority Queue
1. **New: IA/MI/SC standalone real-verification pass** -- the last
   piece of the coverage-threshold workstream. Not urgent (PARTIAL
   data still can't drive a dollar-affecting determination), but worth
   closing out the workstream properly.
2. Mobile z-index collision (AssemblyPanel vs. phase-transition bars)
   -- still unconfirmed on a real device, unchanged from prior sessions.
3. extreme_high_confidence calibration tier at 0/1 -- unchanged.
4. v2 token migration for the homepage -- unchanged, architectural only.
5. damages_cap_treatment remains unconsumed by any pricing logic --
   worth remembering this whole workstream was future-proofing, not
   fixing a live bug, whenever that future pricing extension gets
   scoped.'''

NEW_ENTRY = '''### On the horizon -- updated Priority Queue
1. **New: IA/MI/SC standalone real-verification pass** -- the last
   piece of the coverage-threshold workstream. Not urgent (PARTIAL
   data still can't drive a dollar-affecting determination), but worth
   closing out the workstream properly.
2. Mobile z-index collision (AssemblyPanel vs. phase-transition bars)
   -- still unconfirmed on a real device, unchanged from prior sessions.
3. extreme_high_confidence calibration tier at 0/1 -- unchanged.
4. v2 token migration for the homepage -- unchanged, architectural only.
5. damages_cap_treatment remains unconsumed by any pricing logic --
   worth remembering this whole workstream was future-proofing, not
   fixing a live bug, whenever that future pricing extension gets
   scoped.

## SESSION CLOSEOUT (2026-09-09, extended continuation session) --
## PARTIAL-STATE COVERAGE-THRESHOLD WORKSTREAM COMPLETE

### One-line summary
The PARTIAL-state legal coverage-threshold verification workstream,
started this session (Batch 0), is complete: 51 of 51 jurisdictions
now CONFIRMED against primary statute text and controlling case law.
IA, MI, and SC -- held back once already for insufficient verification
-- were re-attempted and closed out with real primary sources this
time, not restated hypotheses.

### Final batch (IA, MI, SC)
- IA: uncapped, on Ackelson v. Manley Toy Direct, L.L.C., 832 N.W.2d
  678 (Iowa 2013) -- corrected remedies citation from §216.6 to the
  actual provision, §216.15(9)(a)(8).
- MI: uncapped (unchanged label, now verified), on Eide v. Kelsey-Hayes
  Co., 431 Mich. 26, 427 N.W.2d 488 (1988) -- corrected remedies
  citation from §37.2201 (definitions) to §37.2801 (actual remedies).
- SC: no_damages_available, on §1-13-90(c)(16) -- corrected subsection
  from the first-attempt (d)(9) citation, verified directly against
  current statute text this time.

### Test suite note
Full suite: 837/837, down 1 from the 838 baseline held throughout the
entire workstream -- explained, not a regression. Test 38's
"substitute the current still-PARTIAL example state" pattern
(TX->AL->MS->SC across four prior batches) became structurally
impossible once zero PARTIAL states remained in the table. Rewritten
to the same save/mutate/restore monkey-patch convention test 39 already
used -- synthesizes a temporary PARTIAL entry, asserts against it,
restores the real CONFIRMED data in a finally block. This makes the
test durable independent of any future state's confidence, and
permanently retires the fragile "find a real example" pattern. One
now-meaningless standalone sanity check (confirming a real state's
PARTIAL-ness against live data) was dropped as part of this
restructuring, accounting for the count change.

### Workstream summary, start to finish (all sessions)
- 51 of 51 jurisdictions (50 states + DC) verified against primary
  statute text or controlling case law and flipped to CONFIRMED.
- 9 batches total: Batch 0 (priority: VA/TX/TN/FL/CO) through Batch 8
  (NV/OR/UT/WY), plus this final standalone re-verification pass for
  IA/MI/SC.
- Schema grew from a three-value to a five-value damages_cap_treatment
  enum: uncapped | state_specific_tiers | state_specific_flat |
  federal_cap_applies | no_damages_available. Both additions
  (state_specific_flat, Batch 0; no_damages_available, Batch 4) were
  driven by real states that didn't fit the original three categories,
  and each was scope-checked against all previously-CONFIRMED entries
  when added, to avoid leaving other states mislabeled under the
  narrower schema.
- One architectural near-miss caught before implementation: a
  recommendation to omit AL/GA (no general state anti-discrimination
  law) from the table entirely would have crashed engine import via a
  hard key-set assertion against JURISDICTION_TABLE -- caught, not
  implemented; correct fix was recognizing federal_cap_applies already
  meant exactly what their situation required.
- Every Gemini finding was independently checked against primary
  sources before any confidence flip -- this caught real errors (not
  just imprecision) in multiple states across the workstream: wrong or
  outdated dollar figures, mislabeled damages-cap categories, and at
  least one significant legislative change (Virginia's 2026 threshold
  drop) that Gemini correctly identified and this session verified
  despite falling right at the edge of reliable knowledge.
- Three states (IA, MI, SC) were held back once rather than shipped on
  unverified claims, then correctly re-verified and closed out in this
  final batch -- the discipline of "PARTIAL is a fine outcome, a false
  CONFIRMED is not" held all the way through, including at the very
  end when it would have been easy to just finish with a round number.

### Test suite / verification, this session in full
Full 11-script suite held at 838/838 through every batch this session
except the final one (837/837, explained above -- structural test
improvement, not a regression). tsc --noEmit N/A throughout (Python
engine changes only, no TypeScript touched in this workstream).

### On the horizon -- updated Priority Queue
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

EDITS = [
    ('version header 4.293 -> 4.294', VERSION_OLD, VERSION_NEW),
    ('append Section 16 workstream-complete closeout entry', TAIL_OLD, NEW_ENTRY),
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
