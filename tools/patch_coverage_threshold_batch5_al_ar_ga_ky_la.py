"""
engine/friction_tax.py: PARTIAL-state verification workstream, Batch 5.
Flips AL/AR/GA/KY/LA from PARTIAL to CONFIRMED against primary statute
text. AL and GA raised a real modeling question first (see the removal
investigation below) -- resolved as "keep both entries, correct
values already," not the removal Gemini originally recommended.

Nine anchored edits, applied atomically (all must match or nothing is
written):
  1. Structural comment near the defensive fallback loop -- documents
     why a state with no general anti-discrimination law (AL, GA)
     can't simply be omitted from STATE_COVERAGE_THRESHOLDS. Two
     independent mechanisms make removal actively broken, not just
     risky: (a) a hard assert immediately below requires this dict's
     key set to exactly match JURISDICTION_TABLE's, so removing an
     entry crashes the whole module at import time; (b) even without
     that assert, the fallback loop itself would silently re-create
     the omitted entry as an unresearched-looking PARTIAL placeholder,
     actively mislabeling a real, confirmed finding. resolve_
     coverage_gate()'s own STATE_COVERAGE_THRESHOLDS.get(jid) lookup
     was independently confirmed safe first, but that's a separate
     question from whether removal is a good idea -- it isn't, for the
     reasons above.
  2. AL entry -- confidence corrected PARTIAL -> CONFIRMED. thresholds
     and damages_cap_treatment values unchanged (already accurate: no
     general private-sector state anti-discrimination law exists,
     federal Title VII governs entirely -- exactly what
     federal_cap_applies means). Citation upgraded to state the real
     finding directly rather than reading like an unresearched
     placeholder, while preserving the real narrow carve-out (AADEA,
     age-only, 20+ employees).
  3. AR entry -- damages_cap_treatment confirmed accurate as already
     modeled (state_specific_tiers); tier figures added, Ark. Code
     §16-123-107(c)(2)(B).
  4. GA entry -- same treatment as AL. Citation upgraded, preserving
     the real narrow carve-out (disability-only, 15+ employees,
     O.C.G.A. §34-6A-4).
  5. KY entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. KRS §344.450's remedy provision doesn't list punitive
     damages, and courts applying it have confirmed punitive damages
     aren't recoverable -- framed as statutory-construction consensus
     (Timmons v. Wal-Mart Stores, following the Grzyb line of
     reasoning), not one clean controlling holding like IN's Alder or
     PA's Hoy.
  6. LA entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. La. R.S. §23:303(A) authorizes uncapped compensatory
     damages; Louisiana's civil-law doctrine bars punitive damages
     generally absent express statutory authorization (Chauvin v.
     Exxon Mobil; Ross v. Conoco, Inc.), and the LEDL provides none.
  7. CONFIRMED-count assertion -- 31 -> 36, five states added.

Test-fixture check performed before writing this patch: grepped
tools/test_friction_tax.py for "AL"/"AR"/"GA"/"KY"/"LA" -- AL is
referenced in test 38 (the same test Batch 0 substituted TX -> AL for,
as its live example of a still-PARTIAL state). AL is flipping to
CONFIRMED this batch, so test 38 needs a second substitution --
handled in a companion tools/test_friction_tax.py patch, substituting
MS (still PARTIAL, identical threshold=15, confirmed by direct query
before choosing it). AR/GA/KY/LA: zero other references.

Usage:
    python tools/patch_coverage_threshold_batch5_al_ar_ga_ky_la.py --dry-run
    python tools/patch_coverage_threshold_batch5_al_ar_ga_ky_la.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

EDIT_1_OLD = '''# Defensive fallback only -- every jurisdiction is expected to be covered by
# either the CONFIRMED block above or the PARTIAL block immediately above;
# this loop should be a no-op in practice (asserted below) and exists only
# so a future JURISDICTION_TABLE addition can't silently produce a KeyError
# deep inside resolve_coverage_gate() instead of a clear signal here.'''

EDIT_1_NEW = '''# Defensive fallback only -- every jurisdiction is expected to be covered by
# either the CONFIRMED block above or the PARTIAL block immediately above;
# this loop should be a no-op in practice (asserted below) and exists only
# so a future JURISDICTION_TABLE addition can't silently produce a KeyError
# deep inside resolve_coverage_gate() instead of a clear signal here.
#
# This is also why a state with no general private-sector anti-
# discrimination law (e.g. AL, GA) can't simply be OMITTED from this
# dict to represent "federal governs entirely." Two mechanisms make
# that actively broken, not just risky: (1) the assert immediately
# below requires this dict's key set to exactly match
# JURISDICTION_TABLE's, so removing an entry crashes the whole module
# at import time, not just a rare code path; (2) even without that
# assert, this fallback loop would silently re-create the omitted
# entry as an unresearched-looking PARTIAL placeholder, actively
# mislabeling a real, confirmed finding. resolve_coverage_gate()'s own
# .get(jid) lookup is safe on a missing key -- that's a separate
# question from whether removal is a good idea (2026-09-09
# investigation, AL/GA). The correct representation for "no state law
# exists" is to KEEP the entry with damages_cap_treatment=
# "federal_cap_applies" and confidence="CONFIRMED" once independently
# verified -- see AL/GA's own entries above.'''

EDIT_2_OLD = '''    "AL": StateCoverageThreshold(
        thresholds={"general": 15},  # no general state anti-discrimination law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="No general state law (age-only state law is 20+, Code of Ala. §25-1-21); federal 15+ governs other traits. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_2_NEW = '''    "AL": StateCoverageThreshold(
        thresholds={"general": 15},  # no general state anti-discrimination law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="No general private-sector state anti-discrimination law exists in Alabama -- federal Title VII (15+) governs entirely. Alabama Age Discrimination in Employment Act (AADEA), Code of Ala. §25-1-21, is a narrow age-only carve-out at 20+ employees.",
    ),'''

EDIT_3_OLD = '''    "AR": StateCoverageThreshold(
        thresholds={"general": 9},
        damages_cap_treatment="state_specific_tiers",  # capped based on employer size
        confidence="PARTIAL",
        citation="Arkansas Civil Rights Act, Ark. Code §16-123-107. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_3_NEW = '''    "AR": StateCoverageThreshold(
        thresholds={"general": 9},
        damages_cap_treatment="state_specific_tiers",  # $15,000 (fewer than 15 employees) / $50,000 (15-100) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+), Ark. Code §16-123-107(c)(2)(B)
        confidence="CONFIRMED",
        citation="Arkansas Civil Rights Act, Ark. Code §16-123-107(c)(2)(B).",
    ),'''

EDIT_4_OLD = '''    "GA": StateCoverageThreshold(
        thresholds={"general": 15},  # no general private-sector state law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="No general private-sector state law; disability 15+ (§34-6A-4). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_4_NEW = '''    "GA": StateCoverageThreshold(
        thresholds={"general": 15},  # no general private-sector state law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="No general private-sector state anti-discrimination law exists in Georgia -- federal Title VII (15+) governs entirely. Georgia Equal Employment for Persons with Disabilities Code, O.C.G.A. §34-6A-4, is a narrow disability-only carve-out at 15+ employees.",
    ),'''

EDIT_5_OLD = '''    "KY": StateCoverageThreshold(
        thresholds={"general": 8},  # 15+ for disability & pregnancy accommodation specifically
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="KRS §344.040. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_5_NEW = '''    "KY": StateCoverageThreshold(
        thresholds={"general": 8},  # 15+ for disability & pregnancy accommodation specifically
        damages_cap_treatment="uncapped",  # back pay, front pay, injunctive relief, and uncapped compensatory damages (emotional distress/humiliation) available under KRS §344.450; the remedy provision doesn't list punitive damages, and courts applying it (e.g. Timmons v. Wal-Mart Stores, following the Grzyb line of reasoning) have confirmed punitive damages aren't recoverable -- statutory-construction consensus, not one clean controlling holding like IN's Alder or PA's Hoy
        confidence="CONFIRMED",
        citation="Kentucky Civil Rights Act, KRS §344.450.",
    ),'''

EDIT_6_OLD = '''    "LA": StateCoverageThreshold(
        thresholds={"general": 20},  # pregnancy 25+; federal 15+ is effectively lower either way
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="La. R.S. §23:332; §23:342 (pregnancy). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_6_NEW = '''    "LA": StateCoverageThreshold(
        thresholds={"general": 20},  # pregnancy 25+; federal 15+ is effectively lower either way
        damages_cap_treatment="uncapped",  # compensatory damages, back pay, benefits, attorney's fees available with no statutory cap under La. R.S. §23:303(A); Louisiana's civil-law doctrine bars punitive damages generally absent express statutory authorization (Chauvin v. Exxon Mobil, 2014-0808 (La. 12/9/14); Ross v. Conoco, Inc., 2002-0299 (La. 10/15/02)), and the LEDL provides none
        confidence="CONFIRMED",
        citation="Louisiana Employment Discrimination Law, La. R.S. §23:303(A); §23:332; §23:342 (pregnancy).",
    ),'''

EDIT_7_OLD = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 31, (
    "Expected exactly 31 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI)"
)'''

EDIT_7_NEW = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 36, (
    "Expected exactly 36 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA)"
)'''

EDITS = [
    ('structural comment: why AL/GA cannot be omitted', EDIT_1_OLD, EDIT_1_NEW),
    ('AL entry', EDIT_2_OLD, EDIT_2_NEW),
    ('AR entry', EDIT_3_OLD, EDIT_3_NEW),
    ('GA entry', EDIT_4_OLD, EDIT_4_NEW),
    ('KY entry', EDIT_5_OLD, EDIT_5_NEW),
    ('LA entry', EDIT_6_OLD, EDIT_6_NEW),
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
