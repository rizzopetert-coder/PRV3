"""
tools/_mob.txt: session closeout for the PARTIAL-state coverage-
threshold verification workstream's completion (Batches 1-8 this
session; Batch 0 shipped earlier the same session).

Two edits:
1. Version header (line 9): v4.292 -> v4.293.
2. Append new Section 16 entry at end of file (verbatim text supplied
   by Pete).

Usage:
    python tools/patch_mob_section16_coverage_batch18_closeout.py --dry-run
    python tools/patch_mob_section16_coverage_batch18_closeout.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

VERSION_OLD = '\\\\\\#\\\\\\# MOB v4.292'
VERSION_NEW = '\\\\\\#\\\\\\# MOB v4.293'

TAIL_OLD = '''### On the horizon -- updated Priority Queue
1. **PARTIAL coverage-threshold verification, Batches 4-8** (18 states
   remaining, since IA/MI stay in the PARTIAL pool despite being
   attempted): 4 (NE/ND/OH/SD/WI), 5 (AL/AR/GA/KY/LA), 6 (MS/NC/OK/SC),
   7 (AZ/HI/ID/MT/NM), 8 (NV/OR/UT/WY). Plus IA and MI specifically, as
   a real (not pattern-inferred) verification pass whenever convenient
   -- could be folded into whichever future batch is most efficient,
   or done standalone.
2. Possible mobile z-index collision (AssemblyPanel vs. phase-transition
   bars) -- still unconfirmed on a real device, unchanged.
3. extreme_high_confidence calibration tier at 0/1 -- unchanged.
4. v2 token migration for the homepage -- unchanged, architectural only.'''

NEW_ENTRY = '''### On the horizon -- updated Priority Queue
1. **PARTIAL coverage-threshold verification, Batches 4-8** (18 states
   remaining, since IA/MI stay in the PARTIAL pool despite being
   attempted): 4 (NE/ND/OH/SD/WI), 5 (AL/AR/GA/KY/LA), 6 (MS/NC/OK/SC),
   7 (AZ/HI/ID/MT/NM), 8 (NV/OR/UT/WY). Plus IA and MI specifically, as
   a real (not pattern-inferred) verification pass whenever convenient
   -- could be folded into whichever future batch is most efficient,
   or done standalone.
2. Possible mobile z-index collision (AssemblyPanel vs. phase-transition
   bars) -- still unconfirmed on a real device, unchanged.
3. extreme_high_confidence calibration tier at 0/1 -- unchanged.
4. v2 token migration for the homepage -- unchanged, architectural only.

## SESSION CLOSEOUT (2026-09-08/09, extended continuation session)

### One-line summary
Completed all 8 remaining batches of the PARTIAL-state legal coverage-
threshold verification workstream tonight (Batches 1-8; Batch 0 shipped
earlier this session). 48 of 51 jurisdictions now CONFIRMED against
primary statute text and controlling case law, live in production.
Three states (IA, MI, SC) deliberately held at PARTIAL -- their
findings existed but couldn't be independently verified to the same
standard, so they weren't shipped on an unverified claim. Two schema
additions (state_specific_flat, no_damages_available) and one major
saved mistake: a Gemini architectural recommendation to omit two
states entirely would have crashed engine import via a hard key-set
assertion -- caught and corrected before any code was written.

### Batches shipped this session (in order)

**Batch 1 (CT/DE/DC/ME/MD):** all 5 confirmed, zero corrections needed.
NJ's previously-flagged punitive-damages-cap question resolved
definitively (N.J.S.A. 2A:15-5.14(c) excludes LAD claims from the
general cap).

**Batch 2 (NH/NJ/PA/RI/VT):** all 5 confirmed, zero corrections needed
-- all five landed on "uncapped" for distinct legal reasons. PA's
Hoy v. Angelone citation confirmed exact.

**Batch 3 (IN/KS/MN/MO confirmed; IA/MI held at PARTIAL):** IA and MI's
classifications were only pattern-inferred, not independently verified
-- held back rather than shipped on inference. MN's HF4109 (2024,
removed private-employer punitive cap) confirmed exact including date.
MO's tier figures confirmed with a precision fix (bottom bracket is
"more than five" employees, i.e. 6-100, not "5-100").

**Batch 4 (NE/ND/OH/SD/WI):** all 5 confirmed. OH's H.B. 352 (2021)
tort-reform overhaul confirmed with exact dollar figures. New fifth
enum value added: no_damages_available, for states where no
compensatory or punitive damages exist at all (distinct from
"uncapped," which means real damages with no ceiling) -- applied to
ND and WI after a scoped cross-check of all existing CONFIRMED
"uncapped" entries found no other mislabeling.

**Batch 5 (AL/AR/GA/KY/LA):** all 5 confirmed. AL and GA raised a real
architectural question -- Gemini recommended omitting both from
STATE_COVERAGE_THRESHOLDS since neither has a general private-sector
anti-discrimination statute. CAUGHT AND CORRECTED before implementation:
a hard module-load assertion requires the table to cover the exact
same key set as JURISDICTION_TABLE (50 states + DC), and a silent
auto-fill fallback would re-insert a generic unresearched placeholder
for any missing entry -- removing AL/GA would have crashed engine
import entirely. Correct fix: both states' existing federal_cap_applies
values were already accurate (that's literally what "no independent
state law, federal fills the gap" means) -- just needed the confidence
flip and a real citation. Documented in a code comment for future
readers.

**Batch 6 (MS/NC/OK confirmed; SC held at PARTIAL):** MS followed the
same AL/GA shape (no general state law). OK's 25 O.S. §1350 (2011)
abolished all common-law remedies -- confirmed via complete statute
text after an initial concern (a case reference to "OADA damage caps")
resolved in Gemini's favor rather than contradicting it. SC's specific
remedies-subsection citation could not be independently located --
held at PARTIAL rather than shipped unverified.

**Batch 7 (AZ/HI/ID/MT/NM):** all 5 confirmed. ID's specific $1,000
punitive-damages figure (unusually low, high fabrication risk) verified
exactly via 7+ sources including a federal court filing quoting the
statute directly and a real case (Paterson v. State) showing an actual
$1,000 award applied. MT's Human Rights Act vs. Wrongful Discharge Act
exemption (MCA §39-2-912(1)) confirmed via direct statute text.

**Batch 8 (NV/OR/UT/WY) -- final regular batch:** all 4 confirmed. OR's
Zweizig v. Rote, 368 Or. 79 (2021) confirmed exact -- Oregon Supreme
Court held the general noneconomic damages cap doesn't apply to
employment discrimination claims seeking purely emotional injury
damages. WY's unusually low 2-employee threshold confirmed exact.

### Final state: 48 CONFIRMED, 3 PARTIAL (IA, MI, SC)
All three held PARTIAL states have Gemini findings on record (IA/MI:
uncapped, pattern-inferred not independently verified; SC:
no_damages_available, statute existence confirmed but specific
remedies-subsection text not located) -- documented as working
hypotheses for a future real-verification pass, not treated as gaps to
silently rediscover.

### Schema evolution this session
damages_cap_treatment grew from a three-value to a five-value enum
across the full workstream: uncapped | state_specific_tiers |
state_specific_flat (added Batch 0, for real single-number state caps
mismodeled as tiers) | federal_cap_applies | no_damages_available
(added Batch 4, for states where no compensatory or punitive damages
of any kind exist under the state statute). Both additions were driven
by real states that didn't fit the existing categories, not
speculative -- and each was scope-checked against all previously-
CONFIRMED entries before being applied, to avoid leaving other states
mislabeled under the old, narrower schema.

### Test suite
Full 11-script suite: 838/838 after every batch tonight, unchanged
total throughout all 8 batches. CONFIRMED-count assertion progression,
each confirmed by direct file query before writing (not computed from
running arithmetic, after Batch 7 established that discipline):
36 (Batch 4 end, from last session's close) -> 39 (Batch 5) -> 39
(Batch 6, +3 not +4, SC held back) -> 44 (Batch 7) -> 48 (Batch 8).
Test fixture dependencies caught and fixed at each point a state's
CONFIRMED flip broke an existing "still-PARTIAL example" fixture:
TX->AL (Batch 0), AL->MS (Batch 5), MS->SC (Batch 6, caught proactively
within the same batch before the state it referenced flipped).

### Named exceptions -- not gaps to rediscover later
- IA, MI, SC: findings exist, independent verification doesn't (yet).
  Real next step is a standalone research pass, not folded into a
  future numbered batch.
- ME's intermediate damages-cap tier breakpoints (Batch 1, from
  earlier this session): still only partially independently verified.
- Several states' Gemini findings this session were accepted on strong
  structural-consistency grounds rather than individually re-verified
  case-by-case (documented per-batch above where this happened) --
  distinguished explicitly from the deeper case-by-case verification
  given to the highest-risk/most-specific claims each batch.

### On the horizon -- updated Priority Queue
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

EDITS = [
    ('version header 4.292 -> 4.293', VERSION_OLD, VERSION_NEW),
    ('append Section 16 closeout entry', TAIL_OLD, NEW_ENTRY),
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
