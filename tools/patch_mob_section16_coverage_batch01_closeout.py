"""
Patch tools/_mob.txt: append the Section 16 closeout entry for this
continuation session (PARTIAL coverage-threshold verification workstream
kickoff, Batch 0 and Batch 1 shipped) verbatim as provided, and bump
the MOB version header v4.290 -> v4.291.

Usage:
    python tools/patch_mob_section16_coverage_batch01_closeout.py --dry-run
    python tools/patch_mob_section16_coverage_batch01_closeout.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

ENTRY = r"""
## SESSION CLOSEOUT (2026-09-08, continuation session)

### One-line summary
Kicked off the PARTIAL-state legal coverage-threshold verification
workstream (44 states total, batched into 9 groups). Completed and
shipped Batch 0 (VA/TX/TN/FL/CO) and Batch 1 (CT/DE/DC/ME/MD) --
10 of 44 states now CONFIRMED, live in production. One real schema gap
found and fixed along the way; multiple Gemini findings independently
verified against primary statute text, not just accepted on citation
strength.

### Shipped and closed this session

1. **Batching plan established for all 44 PARTIAL states**, 9 batches:
   Batch 0 (priority, design-doc-flagged: VA/TX/TN/FL/CO), then 8
   regional batches of ~5 states each covering the remaining 39.
   Documented in full for continuation next session.

2. **Batch 0 (VA/TX/TN/FL/CO) verified and CONFIRMED.** VA: threshold
   corrected 6->5 employees, reflecting a real 2026 legislative change
   (SB 637, signed by Gov. Spanberger, effective July 1 2026) that
   applies uniformly across all claim types, not just unlawful
   discharge -- independently verified against 8 sources including
   LegiScan's actual bill text. TX/TN/CO: confirmed accurate as already
   modeled, citations upgraded to primary statute text with full tier
   detail. FL: damages_cap_treatment corrected from a tiered-cap label
   to a flat-cap label -- surfaced a real schema gap (the enum only had
   three values, none of which accurately described either FL's or
   VA's actual flat-cap structure). New fourth enum value added
   (state_specific_flat), applied to both VA and FL, docstring updated.
   Scoped cross-check confirmed no other CONFIRMED or Batch-0 entry had
   the same mislabeling.

3. **Batch 1 (CT/DE/DC/ME/MD) verified and CONFIRMED.** CT: damages
   treatment corrected from federal_cap_applies to uncapped -- Conn.
   Gen. Stat. §46a-104 doesn't authorize punitive damages under CFEPA
   at all (Tomick v. UPS, 324 Conn. 470 (2016), Connecticut Supreme
   Court), a different and more specific finding than "federal fills
   the gap." DE: damages treatment corrected from federal_cap_applies
   to a real independent 5-tier state structure (SB 145, 2024) --
   $50k/$75k/$175k/$300k/$500k -- the old label was simply wrong, not
   just imprecise. DC/MD confirmed accurate as already modeled. ME
   confirmed with an explicit caveat preserved in-code: only the
   $20k/$50k/$100k small-employer civil-penal tiers and the $500k
   top-tier ceiling were independently verified; intermediate tier
   breakpoints for the 15+-employee compensatory/punitive schedule
   were not, and that gap is stated plainly rather than implied away
   by the CONFIRMED flip.

4. **One near-miss chased down, not waved through.** MD's damages-cap
   characterization ("combined compensatory and punitive") initially
   looked possibly wrong against one source fragment suggesting
   punitive damages might be separately uncapped. Dug further: §20-1013
   (e)(2) explicitly confirms the combined-cap reading is correct. Worth
   recording as a case where extra verification effort confirmed
   Gemini's original claim rather than catching an error -- the
   discipline paid for itself either way.

### Live verification
Both batches: full production deploy confirmed Ready after each push
(dpl_9... for Batch 0's engine changes carried the site anyway;
dpl_BrxqiRrymCMA2jMpDfaN5GJVjL1c, commit dbc111b, for Batch 1).
damages_cap_treatment isn't consumed by any pricing logic yet (by
design, per the governing design doc), so no user-facing behavior
changed -- deploy-Ready confirmation was sufficient, no live payload
round-trip needed this time, unlike the UI-facing work earlier tonight.

### Test suite
Full 11-script suite: 838/838 after both batches, unchanged total.
Two real test-fixture dependencies found and fixed, not just a stale
count each time:
- Batch 0: test 38 hardcoded TX as a "still-PARTIAL" example state --
  substituted AL (identical threshold, zero numeric change) since TX
  became CONFIRMED.
- Batch 1: no fixture referenced any of the five states directly
  (confirmed by grep before touching anything) -- only the CONFIRMED-
  count mirror needed updating.
CONFIRMED-count assertion: 7 -> 12 (Batch 0) -> 17 (Batch 1).

### Named exceptions -- not gaps to rediscover later
- ME's intermediate damages-cap tier breakpoints (between the
  independently-verified $20k/$50k/$100k floor tiers and the $500k
  ceiling) are CONFIRMED in confidence label but not fully
  independently verified in every intermediate number -- flagged
  explicitly in-code, worth a closer look if this field is ever wired
  into real pricing logic.
- `gh` unavailable in this environment -- noted, not blocking, not
  chased further.

### On the horizon -- updated Priority Queue
1. **PARTIAL coverage-threshold verification, Batches 2-8** (39 states
   remaining): 2 (NH/NJ/PA/RI/VT), 3 (IA/IN/KS/MI/MN/MO), 4 (NE/ND/OH/
   SD/WI), 5 (AL/AR/GA/KY/LA), 6 (MS/NC/OK/SC), 7 (AZ/HI/ID/MT/NM),
   8 (NV/OR/UT/WY). Batch 0 and 1 complete, both live.
2. Possible mobile z-index collision (AssemblyPanel vs. phase-transition
   bars) -- still unconfirmed on a real device, unchanged from last
   session.
3. extreme_high_confidence calibration tier at 0/1 -- unchanged.
4. v2 token migration for the homepage -- unchanged, architectural only.
"""

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.290"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.291"


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
