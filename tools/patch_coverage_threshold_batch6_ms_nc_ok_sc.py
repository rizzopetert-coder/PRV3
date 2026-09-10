"""
engine/friction_tax.py: batch 6 of the PARTIAL-state verification
workstream (MS/NC/OK flipped to CONFIRMED, SC held at PARTIAL with an
updated citation).

MS: thresholds/damages_cap_treatment unchanged (general: 15,
federal_cap_applies) -- confirmed accurate as modeled. Citation upgraded
to cite the "no comprehensive state anti-discrimination statute for
private employers" finding directly (9 independent sources), noting the
narrow existing carve-outs (military service, equal pay) that don't
provide general coverage.

NC: thresholds/damages_cap_treatment unchanged (general: 15,
federal_cap_applies). N.C. Gen. Stat. §143-422.2(a) -- NCEEPA covers
employers with 15+ employees but provides no private right of action;
the statute's own public-policy declaration can support a common-law
wrongful-discharge claim instead, which isn't headcount-gated.
federal_cap_applies remains the structurally correct treatment for the
actual statutory discrimination framework.

OK: damages_cap_treatment corrected federal_cap_applies ->
no_damages_available. 25 O.S. §1350, added 2011 (Laws 2011, c. 270,
§11, eff. Nov. 1, 2011) -- subsection (A) abolished all common-law
remedies for employment discrimination (previously available via the
Burk tort, which allowed unlimited compensatory/punitive damages);
subsection (G), confirmed via direct statute text, limits the statutory
remedy to injunctive relief, reinstatement, back pay, and liquidated
damages equal to back pay -- no compensatory damages for emotional
distress, no punitive damages authorized anywhere in the section.

SC: LEFT AT PARTIAL, no changes to thresholds or damages_cap_treatment.
Citation updated to note Gemini's no_damages_available finding (S.C.
Code §1-13-90(d)(9)) was not independently verified against primary
source text this session -- same treatment as IA/MI.

CONFIRMED-count assertion: 36 -> 39 (MS, NC, OK -- SC stays PARTIAL).

Usage:
    python tools/patch_coverage_threshold_batch6_ms_nc_ok_sc.py --dry-run
    python tools/patch_coverage_threshold_batch6_ms_nc_ok_sc.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

MS_OLD = '''    "MS": StateCoverageThreshold(
        thresholds={"general": 15},  # no state anti-discrimination law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="No state anti-discrimination law; federal 15+ governs. research/jurisdiction-research-headcount.md.",
    ),'''

MS_NEW = '''    "MS": StateCoverageThreshold(
        thresholds={"general": 15},  # no state anti-discrimination law -- federal governs
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="No comprehensive state anti-discrimination statute for private employers, confirmed directly against primary source text (9 independent sources); narrow existing carve-outs (military service, equal pay) don't provide general coverage. Federal 15+ threshold governs the applicable claim.",
    ),'''

NC_OLD = '''    "NC": StateCoverageThreshold(
        # No private right of action under NC's state anti-discrimination
        # statute at all -- only a common-law wrongful-discharge claim
        # exists, which isn't headcount-gated the way this table models.
        # Federal threshold used here since that's the applicable
        # statutory framework for an actual discrimination claim.
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="No private right of action under state statute; common-law wrongful-discharge available regardless of size. research/jurisdiction-research-headcount.md.",
    ),'''

NC_NEW = '''    "NC": StateCoverageThreshold(
        # NCEEPA covers employers with 15+ employees but provides no
        # private right of action -- the statute's own public-policy
        # declaration can support a common-law wrongful-discharge claim
        # instead, which isn't headcount-gated the way this table
        # models. federal_cap_applies remains the structurally correct
        # treatment for the actual statutory discrimination framework.
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",
        confidence="CONFIRMED",
        citation="North Carolina Equal Employment Practices Act, N.C. Gen. Stat. §143-422.2(a).",
    ),'''

OK_OLD = '''    "OK": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="Oklahoma Anti-Discrimination Act, 25 O.S. §1301 (secondary source). research/jurisdiction-research-headcount.md.",
    ),'''

OK_NEW = '''    "OK": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="no_damages_available",  # 25 O.S. §1350, added 2011 (Laws 2011, c. 270, §11, eff. Nov. 1, 2011) -- subsection (A) abolished all common-law remedies for employment discrimination (previously available via the Burk tort, which allowed unlimited compensatory/punitive damages); subsection (G), confirmed via direct statute text, limits the statutory remedy to injunctive relief, reinstatement, back pay, and liquidated damages equal to back pay -- no compensatory damages for emotional distress, no punitive damages authorized anywhere in the section
        confidence="CONFIRMED",
        citation="Oklahoma Anti-Discrimination Act, 25 O.S. §1301; 25 O.S. §1350 (added by Laws 2011, c. 270, §11, eff. Nov. 1, 2011).",
    ),'''

SC_OLD = '''    "SC": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="SC Human Affairs Law, S.C. Code §1-13-30 (secondary source). research/jurisdiction-research-headcount.md.",
    ),'''

SC_NEW = '''    "SC": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="SC Human Affairs Law, S.C. Code §1-13-30. Gemini's finding (no_damages_available per S.C. Code §1-13-90(d)(9)) was not independently verified against primary source text this session -- the statute's existence and general procedural structure were confirmed, but the specific remedies subsection Gemini cited was not directly located and confirmed. Working hypothesis for a future verification pass, same treatment as IA/MI.",
    ),'''

COUNT_OLD = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 36, (
    "Expected exactly 36 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA)"
)'''

COUNT_NEW = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 39, (
    "Expected exactly 39 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA, MS, NC, OK)"
)'''

EDITS = [
    ('MS -> CONFIRMED', MS_OLD, MS_NEW),
    ('NC -> CONFIRMED', NC_OLD, NC_NEW),
    ('OK -> CONFIRMED + no_damages_available', OK_OLD, OK_NEW),
    ('SC citation update, stays PARTIAL', SC_OLD, SC_NEW),
    ('CONFIRMED-count assertion 36 -> 39', COUNT_OLD, COUNT_NEW),
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
