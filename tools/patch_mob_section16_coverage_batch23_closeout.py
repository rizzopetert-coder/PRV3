"""
Patch tools/_mob.txt: append the Section 16 closeout entry for this
continuation session (PARTIAL coverage-threshold verification, Batches
0-3 all shipped, 26/44 states CONFIRMED) verbatim as provided, and bump
the MOB version header v4.291 -> v4.292.

Usage:
    python tools/patch_mob_section16_coverage_batch23_closeout.py --dry-run
    python tools/patch_mob_section16_coverage_batch23_closeout.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

ENTRY = r"""
## SESSION CLOSEOUT (2026-09-08, continuation session)

### One-line summary
Four full verification batches shipped tonight: Batch 0 (VA/TX/TN/FL/CO),
Batch 1 (CT/DE/DC/ME/MD), Batch 2 (NH/NJ/PA/RI/VT), Batch 3 (IN/KS/MN/MO,
IA/MI correctly held back). 26 of 44 PARTIAL states now CONFIRMED and
live in production. One schema gap found and fixed (state_specific_flat
added to the four-value enum). One case where the verification standard
itself was applied to a shipping decision, not just to individual facts
-- IA/MI held at PARTIAL because the classification itself, not just a
sub-detail, was unverified this session.

### Shipped and closed this session

1. **Batch 0 (VA/TX/TN/FL/CO)** -- see prior Section 16 entry, unchanged.
2. **Batch 1 (CT/DE/DC/ME/MD)** -- see prior Section 16 entry, unchanged.
3. **Batch 2 (NH/NJ/PA/RI/VT) verified and CONFIRMED, zero corrections
   needed.** All five independently confirmed against primary sources.
   Notable: NJ's previously-flagged-but-unresolved punitive-damages-cap
   question got a genuinely definitive answer (N.J.S.A. 2A:15-5.14(c)
   explicitly excludes LAD claims from the general Punitive Damages Act
   cap). PA's Hoy v. Angelone citation (554 Pa. 134, 720 A.2d 745, 1998)
   confirmed exact. One near-miss on MD in a prior batch, resolved in
   Gemini's favor after deeper digging -- not repeated here, just noted
   as the discipline that carried forward.
4. **Batch 3 (IN/KS/MN/MO CONFIRMED; IA/MI held at PARTIAL).** Four
   states independently verified: IN (Indiana Civil Rights Commission
   v. Alder, 714 N.E.2d 632, 1999, exact citation/holding), KS ($2,000
   flat cap under K.S.A. §44-1005(k), corrected from state_specific_tiers
   to state_specific_flat), MN (HF4109, signed May 15 2024, effective
   August 1 2024, removed the $25k private-employer punitive cap --
   confirmed across 8+ sources), MO (RSMo §213.111(4) tier structure
   confirmed exact via direct statute text, with a precision correction:
   the bottom bracket is literally "more than five" employees, i.e.
   6-100 matching MHRA's own coverage threshold, not "5-100" as first
   summarized).
   **IA and MI deliberately held at PARTIAL** -- their `uncapped`
   classification was only verified by pattern-consistency with other
   states' independently-confirmed no-punitive-damages structures this
   session, not by direct primary-source verification of Iowa/Michigan
   specifically. This is categorically different from ME's situation in
   Batch 1 (there the core classification was independently verified,
   only a granular sub-detail was open) -- here the classification
   itself was the unverified part, which doesn't meet the CONFIRMED bar
   as documented. Citations updated to record the pattern-consistency
   observation explicitly as a working hypothesis for a future
   verification pass, not a finding. No functional cost to holding these
   back: PARTIAL data still can't drive a dollar-affecting determination,
   and damages_cap_treatment isn't consumed by pricing logic yet.

### Live verification
All four batches: production deploy confirmed Ready after each push.
damages_cap_treatment isn't consumed by any pricing logic yet (by
design), so deploy-Ready confirmation was sufficient each time, no live
payload round-trip needed.

### Test suite
Full 11-script suite: 838/838 after all four batches, unchanged total
throughout. CONFIRMED-count assertion progression: 7 -> 12 (Batch 0)
-> 17 (Batch 1) -> 22 (Batch 2) -> 26 (Batch 3, four states not six).
Grep-before-touching discipline held every batch -- only Batch 0 found
an actual fixture dependency (TX hardcoded as a "still-PARTIAL" example,
substituted with AL); every other batch confirmed zero fixture
references before proceeding.

### Named exceptions -- not gaps to rediscover later
- IA and MI: `uncapped` is a working hypothesis backed by pattern-
  consistency, not an independently verified finding. Worth a real
  primary-source pass before treating as settled, even though currently
  labeled PARTIAL (not CONFIRMED) precisely so this isn't forgotten.
- ME's intermediate damages-cap tier breakpoints (Batch 1): still only
  partially independently verified, flagged in-code, unchanged this
  session.

### On the horizon -- updated Priority Queue
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
"""

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.291"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.292"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    count = content.count(OLD_VERSION_HEADER)
    if count != 1:
        print(f'ERROR: version header found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content + ENTRY
    new_content = new_content.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)

    if args.dry_run:
        print('DRY RUN -- version header found exactly once, append would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
