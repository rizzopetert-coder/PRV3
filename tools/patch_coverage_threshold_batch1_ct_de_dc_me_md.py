"""
engine/friction_tax.py: PARTIAL-state verification workstream, Batch 1.
Flips CT/DE/DC/ME/MD from PARTIAL to CONFIRMED against primary statute
text (independently verified by Pete this session). First batch where
every entry's threshold and damages_cap_treatment checked out as
already-modeled or needed only a damages_cap_treatment correction --
no thresholds were wrong this time.

Six anchored edits, applied atomically (all must match or nothing is
written):
  1. CT entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. CFEPA doesn't authorize punitive damages at all (Tomick
     v. UPS, 324 Conn. 470 (2016)); compensatory damages have no
     statutory cap. This isn't "no independent state cap, federal
     schedule fills the gap" (what federal_cap_applies means) -- it's
     "no cap exists, period," which is what uncapped means, same as
     CA/NY/MA/WA/DC.
  2. DE entry -- threshold comment corrected (the old "15+ for
     disability specifically" carve-out was repealed by a 2014
     amendment that synced disability coverage to the general
     4-employee threshold; the 4 itself was already correct).
     damages_cap_treatment corrected federal_cap_applies ->
     state_specific_tiers (a real independent 5-tier cap, 19 Del. C.
     §715(c)).
  3. DC entry -- threshold and damages_cap_treatment confirmed accurate
     as already modeled (uncapped, both compensatory and punitive).
  4. ME entry -- damages_cap_treatment corrected federal_cap_applies ->
     state_specific_tiers (a real independent tiered structure, two
     distinct damages regimes split at the 15-employee line). Only the
     <15-employee tiers and the 15+-employee ceiling were independently
     verified this session -- the intermediate 15+-employee tier
     breakpoints were not, and the entry's own comment says so
     explicitly rather than implying full verification.
  5. MD entry -- threshold and damages_cap_treatment confirmed accurate
     as already modeled; a real ambiguity resolved this session (the
     cap is combined compensatory-and-punitive, not compensatory-only
     with punitive separately uncapped -- easy to misread from a
     partial statute reading) is now stated explicitly in the entry's
     own comment so it doesn't need re-discovering later.
  6. CONFIRMED-count assertion -- 12 -> 17, state list extended.

Test-fixture check performed before writing this patch: grepped
tools/test_friction_tax.py for "CT"/"DE"/"DC"/"ME"/"MD" -- zero
matches, none of these five states are used anywhere in the test
suite (unlike Batch 0's TX, which needed a fixture substitution). No
test changes needed this batch.

Usage:
    python tools/patch_coverage_threshold_batch1_ct_de_dc_me_md.py --dry-run
    python tools/patch_coverage_threshold_batch1_ct_de_dc_me_md.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

EDIT_1_OLD = '''    "CT": StateCoverageThreshold(
        thresholds={"general": 1},  # lowered from 3+ eff. Oct. 1, 2022
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="CFEPA, Conn. Gen. Stat. §46a-51(10); P.A. 22-82. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_1_NEW = '''    "CT": StateCoverageThreshold(
        thresholds={"general": 1},  # lowered from 3+ eff. Oct. 1, 2022
        damages_cap_treatment="uncapped",  # compensatory uncapped; punitive damages not authorized under CFEPA at all -- Tomick v. UPS, 324 Conn. 470 (2016), Connecticut Supreme Court
        confidence="CONFIRMED",
        citation="CFEPA, Conn. Gen. Stat. §46a-51(10), §46a-104; P.A. 22-82.",
    ),'''

EDIT_2_OLD = '''    "DE": StateCoverageThreshold(
        thresholds={"general": 4},  # 15+ for disability specifically -- general figure used here
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="19 Del. C. §711; §724 (disability, 15+). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_2_NEW = '''    "DE": StateCoverageThreshold(
        thresholds={"general": 4},  # disability coverage synced to this general threshold by Chapter 381 (SB 185, 2014) -- no longer a separate 15-employee line
        damages_cap_treatment="state_specific_tiers",  # $50,000 (4-14 employees) / $75,000 (15-100) / $175,000 (101-200) / $300,000 (201-500) / $500,000 (500+), 19 Del. C. §715(c) (SB 145, 2024, Chapter 203)
        confidence="CONFIRMED",
        citation="19 Del. C. §710(6); §722(3), as amended by Chapter 381 (SB 185, 2014).",
    ),'''

EDIT_3_OLD = '''    "DC": StateCoverageThreshold(
        thresholds={"general": 1},
        damages_cap_treatment="uncapped",  # compensatory AND punitive, no statutory ceiling
        confidence="PARTIAL",
        citation="DC Human Rights Act, D.C. Code §2-1401 et seq. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_3_NEW = '''    "DC": StateCoverageThreshold(
        thresholds={"general": 1},
        damages_cap_treatment="uncapped",  # compensatory AND punitive, no statutory ceiling on either
        confidence="CONFIRMED",
        citation="DC Human Rights Act, D.C. Code §2-1401.02(10), §2-1403.16.",
    ),'''

EDIT_4_OLD = '''    "ME": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes; federal-style damages caps apply only at 15+
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="Maine Human Rights Act, 5 M.R.S. §4572. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_4_NEW = '''    "ME": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        # <15 employees: "civil penal damages" only (not traditional
        # compensatory/punitive), tiered $20,000 (1st order) / $50,000
        # (2nd order) / $100,000 (3rd+ order). 15+ employees: traditional
        # compensatory and punitive damages, tiered up to $500,000 at the
        # top employer-size bracket -- exceeds Title VII's $300,000
        # federal maximum. Only the <15 tiers and the $500,000 ceiling
        # were independently verified this session -- intermediate
        # 15+-employee tier breakpoints were NOT verified; confirm
        # against 5 M.R.S. §4613(2)(B)(7)-(8) directly before relying on
        # them for anything beyond the applicability gate this field
        # doesn't yet drive.
        damages_cap_treatment="state_specific_tiers",
        confidence="CONFIRMED",
        citation="Maine Human Rights Act, 5 M.R.S. §4572; §4613(2)(B)(7)-(8).",
    ),'''

EDIT_5_OLD = '''    "MD": StateCoverageThreshold(
        thresholds={"general": 15, "harassment": 1},  # confirmed harassment carve-out, HB 679 (2019)
        damages_cap_treatment="state_specific_tiers",  # own tiered cap $50k/$100k/$200k/$300k by size
        confidence="PARTIAL",
        citation="Md. State Gov't Code §20-601(d), §20-611, §20-1009(b)(3), §20-1013. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_5_NEW = '''    "MD": StateCoverageThreshold(
        thresholds={"general": 15, "harassment": 1},  # confirmed harassment carve-out, HB 679 (2019)
        # Confirmed via §20-1013(e)(2): this is a COMBINED compensatory-
        # and-punitive cap, not compensatory-only with punitive uncapped
        # separately -- easy to misread from a partial reading of
        # §20-1009 alone; resolved this session, not just data entry.
        damages_cap_treatment="state_specific_tiers",  # $50,000 (15-100 employees) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (501+), Md. State Gov't Code §20-1009(b)(3)
        confidence="CONFIRMED",
        citation="Md. State Gov't Code §20-601(d), §20-611, §20-1009(b)(3), §20-1013(e)(2).",
    ),'''

EDIT_6_OLD = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 12, (
    "Expected exactly 12 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO)"
)'''

EDIT_6_NEW = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 17, (
    "Expected exactly 17 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD)"
)'''

EDITS = [
    ('CT entry', EDIT_1_OLD, EDIT_1_NEW),
    ('DE entry', EDIT_2_OLD, EDIT_2_NEW),
    ('DC entry', EDIT_3_OLD, EDIT_3_NEW),
    ('ME entry', EDIT_4_OLD, EDIT_4_NEW),
    ('MD entry', EDIT_5_OLD, EDIT_5_NEW),
    ('CONFIRMED-count assertion', EDIT_6_OLD, EDIT_6_NEW),
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
