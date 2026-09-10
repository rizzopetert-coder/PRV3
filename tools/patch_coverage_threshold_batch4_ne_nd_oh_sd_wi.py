"""
engine/friction_tax.py: PARTIAL-state verification workstream, Batch 4.
Flips NE/ND/OH/SD/WI from PARTIAL to CONFIRMED against primary statute
text. All five facts independently verified this session -- no
IA/MI-style holdback needed.

Adds a fifth damages_cap_treatment value, no_damages_available: ND and
WI's statutes authorize neither compensatory nor punitive damages at
all (remedies limited to equitable/make-whole relief), a categorically
different situation from "uncapped" (real damages exist, no ceiling).
Reusing "uncapped" for these two would vacuously read as true ("no cap
exists" is trivially correct when the underlying amount is zero) but
would mislead a future reader -- or a future pricing extension -- into
treating these states as unconstrained-exposure rather than
zero-exposure, the opposite direction of error from Batch 0's flat-cap
gap but the same shape of problem: an existing value technically
doesn't lie, but doesn't tell the truth either.

Scoped cross-check performed before writing this patch (same standard
as Batch 0's state_specific_flat addition): every currently-CONFIRMED
entry labeled "uncapped" (CA, NY, MA, WA, CT, DC, IN, MN, NH, NJ, PA,
RI, VT) read directly from source -- all describe real, available
compensatory (and often punitive) damages, none describe a zero-
damages situation. NE and SD (this batch) also confirmed to have real
uncapped compensatory damages, not zero. No existing entry needs to
move to the new value.

Eight anchored edits, applied atomically (all must match or nothing is
written):
  1. StateCoverageThreshold docstring -- documents the fifth value and
     the exact misread it exists to prevent, including an explicit
     instruction that a future pricing extension must treat it as zero
     exposure, not unconstrained exposure.
  2. NE entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. Punitive damages constitutionally barred in Nebraska
     (Neb. Const. Art. VII, §5; O'Brien v. Cessna Aircraft Co., 298
     Neb. 109 (2017)); compensatory damages under Neb. Rev. Stat.
     §48-1119(4) have no statutory cap.
  3. ND entry -- damages_cap_treatment corrected federal_cap_applies ->
     no_damages_available. N.D.C.C. §14-02.4-20's direct statute text
     bars the department/hearing officer from ordering compensatory or
     punitive damages under the chapter at all.
  4. OH entry -- damages_cap_treatment corrected federal_cap_applies ->
     state_specific_tiers. H.B. 352 (2021) codified Ohio's Tort Reform
     Act caps onto R.C. ch. 4112 claims -- real tiered/formula-based
     caps on both compensatory and punitive damages.
  5. SD entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. Compensatory damages uncapped for a general employment
     discrimination claim; punitive damages ARE authorized under a
     distinct, narrower set of HRA sections that appear housing-
     related, not general employment discrimination -- scoped
     precisely in the comment rather than overstated as "no punitive
     damages under this chapter" broadly.
  6. WI entry -- damages_cap_treatment corrected state_specific_tiers
     -> no_damages_available. 2011 Wisconsin Act 219 repealed the 2009
     amendment that had briefly allowed compensatory/punitive damages
     under WFEA -- current remedies are back pay, front pay,
     reinstatement, and attorney's fees only. "Tiers" never described
     this state's real (now-repealed) situation.
  7. CONFIRMED-count assertion -- 26 -> 31, all five states added.

Test-fixture check performed before writing this patch: grepped
tools/test_friction_tax.py for "NE"/"ND"/"OH"/"SD"/"WI" -- zero matches.
No test changes needed beyond the count-check mirror.

Usage:
    python tools/patch_coverage_threshold_batch4_ne_nd_oh_sd_wi.py --dry-run
    python tools/patch_coverage_threshold_batch4_ne_nd_oh_sd_wi.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

EDIT_1_OLD = '''    damages_cap_treatment: "uncapped" | "state_specific_tiers" |
                      "state_specific_flat" | "federal_cap_applies".
                      "uncapped": no damages cap at all. "state_specific_
                      tiers": the state has its own independent statutory
                      cap that scales in real tiers by employer size (e.g.
                      TX, TN, CO -- distinct dollar figures at distinct
                      headcount bands). "state_specific_flat": the state
                      has its own independent statutory cap, but it's a
                      single number regardless of employer size (e.g. VA,
                      FL -- not tiered, and not deferring to federal).
                      "federal_cap_applies": no independent state cap
                      exists at all, so the federal Title VII tiered
                      schedule fills the gap by default. Captured for a
                      future pricing extension (adjusting Cluster 1/2/4b's
                      dollar ceiling by state) -- NOT yet consumed by
                      resolve_coverage_gate() or the Cluster 1/2/4b
                      integration below, which only gates applicability,
                      not dollar amount. See the design doc's "Next steps."'''

EDIT_1_NEW = '''    damages_cap_treatment: "uncapped" | "state_specific_tiers" |
                      "state_specific_flat" | "federal_cap_applies" |
                      "no_damages_available".
                      "uncapped": real compensatory (and/or punitive)
                      damages exist with no ceiling on the amount.
                      "state_specific_tiers": the state has its own
                      independent statutory cap that scales in real tiers
                      by employer size (e.g. TX, TN, CO -- distinct dollar
                      figures at distinct headcount bands).
                      "state_specific_flat": the state has its own
                      independent statutory cap, but it's a single number
                      regardless of employer size (e.g. VA, FL -- not
                      tiered, and not deferring to federal).
                      "federal_cap_applies": no independent state cap
                      exists at all, so the federal Title VII tiered
                      schedule fills the gap by default.
                      "no_damages_available": neither compensatory nor
                      punitive damages are authorized under this statute
                      at all -- remedies are limited to equitable/make-
                      whole relief (back pay, front pay, reinstatement,
                      injunctive relief, attorney's fees), e.g. ND, WI.
                      Distinct from "uncapped": that value means real
                      damages exist with no ceiling; this value means no
                      damages exist to cap in the first place. A future
                      pricing extension MUST treat this value as zero
                      exposure, not unconstrained exposure -- conflating
                      it with "uncapped" would overstate a state's real
                      exposure, the exact misread this value exists to
                      prevent. Captured for a future pricing extension
                      (adjusting Cluster 1/2/4b's dollar ceiling by
                      state) -- NOT yet consumed by resolve_coverage_gate()
                      or the Cluster 1/2/4b integration below, which only
                      gates applicability, not dollar amount. See the
                      design doc's "Next steps."'''

EDIT_2_OLD = '''    "NE": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="Nebraska Fair Employment Practice Act (secondary source). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_2_NEW = '''    "NE": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="uncapped",  # punitive damages constitutionally barred in Nebraska (Neb. Const. Art. VII, §5; O'Brien v. Cessna Aircraft Co., 298 Neb. 109 (2017)); compensatory damages under Neb. Rev. Stat. §48-1119(4) have no statutory cap
        confidence="CONFIRMED",
        citation="Nebraska Fair Employment Practice Act, Neb. Rev. Stat. §48-1119(4); Neb. Const. Art. VII, §5; O'Brien v. Cessna Aircraft Co., 298 Neb. 109 (2017).",
    ),'''

EDIT_3_OLD = '''    "ND": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="North Dakota Human Rights Act, N.D.C.C. ch. 14-02.4 (secondary source). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_3_NEW = '''    "ND": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum
        damages_cap_treatment="no_damages_available",  # N.D.C.C. §14-02.4-20, direct statute text: "Neither the department nor an administrative hearing officer may order compensatory or punitive damages under this chapter" -- remedies limited to back pay (2-year cap), injunctions, and equitable relief
        confidence="CONFIRMED",
        citation="North Dakota Human Rights Act, N.D.C.C. ch. 14-02.4; §14-02.4-20.",
    ),'''

EDIT_4_OLD = '''    "OH": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="Ohio Civil Rights Act, R.C. ch. 4112. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_4_NEW = '''    "OH": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_tiers",  # H.B. 352 (Employment Law Uniformity Act), eff. Apr. 15, 2021, codified Ohio's Tort Reform Act caps onto R.C. ch. 4112 claims. R.C. 2315.18: non-economic compensatory capped at the greater of $250,000 or 3x economic loss, max $350,000. R.C. 2315.21: punitive capped at 2x compensatory, or for "small employers" (<=100 employees, 500 for manufacturing) at 10% of net worth up to $350,000
        confidence="CONFIRMED",
        citation="Ohio Civil Rights Act, R.C. ch. 4112; R.C. 2315.18; R.C. 2315.21; H.B. 352 eff. Apr. 15, 2021.",
    ),'''

EDIT_5_OLD = '''    "SD": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="SD Human Relations Act, SDCL ch. 20-13 (secondary source). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_5_NEW = '''    "SD": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum
        damages_cap_treatment="uncapped",  # compensatory damages available with no statutory cap for a general employment discrimination claim under §20-13-10 (SDCL §20-13-35.1). Punitive damages ARE authorized under §21-3-2, but only for a distinct, narrower set of HRA sections (§§20-13-20 to 20-13-21.2, 20-13-23.4, 20-13-23.7, 20-13-26) that appear housing-related, not general employment discrimination -- do not read this as "no punitive damages under this chapter" broadly
        confidence="CONFIRMED",
        citation="SD Human Relations Act, SDCL ch. 20-13; §20-13-10; §20-13-35.1; §21-3-2.",
    ),'''

EDIT_6_OLD = '''    "WI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="state_specific_tiers",  # historically limited remedies, compensatory/punitive both restricted
        confidence="PARTIAL",
        citation="Wisconsin Fair Employment Act, Wis. Stat. §111.31 et seq. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_6_NEW = '''    "WI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="no_damages_available",  # 2011 Wisconsin Act 219 repealed the 2009 amendment (Act 20) that had briefly allowed compensatory/punitive damages under WFEA -- current remedies under Wis. Stat. §111.39(4)(c) limited to back pay, front pay, reinstatement, and attorney's fees; neither compensatory nor punitive damages available
        confidence="CONFIRMED",
        citation="Wisconsin Fair Employment Act, Wis. Stat. §111.31 et seq.; §111.39(4)(c); 2011 Wisconsin Act 219.",
    ),'''

EDIT_7_OLD = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 26, (
    "Expected exactly 26 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO)"
)'''

EDIT_7_NEW = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 31, (
    "Expected exactly 31 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI)"
)'''

EDITS = [
    ('docstring: fifth damages_cap_treatment value', EDIT_1_OLD, EDIT_1_NEW),
    ('NE entry', EDIT_2_OLD, EDIT_2_NEW),
    ('ND entry', EDIT_3_OLD, EDIT_3_NEW),
    ('OH entry', EDIT_4_OLD, EDIT_4_NEW),
    ('SD entry', EDIT_5_OLD, EDIT_5_NEW),
    ('WI entry', EDIT_6_OLD, EDIT_6_NEW),
    ('CONFIRMED-count assertion', EDIT_7_OLD, EDIT_7_NEW),
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
