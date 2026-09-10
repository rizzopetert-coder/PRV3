"""
engine/friction_tax.py: batch 9 -- final batch of the PARTIAL-state
verification workstream (IA/MI/SC flipped to CONFIRMED). Closes the
workstream entirely: 51 of 51 jurisdictions CONFIRMED.

All three thresholds unchanged -- confirmed accurate as modeled.

IA: damages_cap_treatment corrected state_specific_tiers -> uncapped.
Iowa Code §216.15(9)(a)(8) -- the actual remedies section (not §216.6,
which was the wrong citation) -- authorizes actual/compensatory
damages with no statutory tiers or ceiling. Ackelson v. Manley Toy
Direct, L.L.C., 832 N.W.2d 678 (Iowa 2013) -- Iowa Supreme Court
affirmed (unanimously, reaffirming 1986 precedent) that punitive
damages are not permitted under the ICRA.

MI: damages_cap_treatment unchanged (uncapped), now on verified
grounds. MCL §37.2801(1)/(3) -- the actual remedies section (§37.2201
was confirmed to be definitions only, as suspected). Eide v.
Kelsey-Hayes Co., 431 Mich. 26, 427 N.W.2d 488 (1988) -- Michigan
Supreme Court held "exemplary damages" for mental anguish/distress/
humiliation are available and uncapped, but are strictly compensatory
in nature -- traditional punitive damages designed to punish are not
available under ELCRA.

SC: damages_cap_treatment corrected federal_cap_applies ->
no_damages_available. S.C. Code Ann. §1-13-90(c)(16) -- corrected
subsection from the (d)(9) first cited two batches ago, verified
directly against current Justia statute text this time. Remedies
limited to: order that the discriminatory practice be discontinued,
plus affirmative action (hiring, reinstatement, upgrading) with or
without back pay. No compensatory damages for emotional distress, no
punitive damages authorized anywhere in the section.

CONFIRMED-count assertion: 48 -> 51 (confirmed via direct query of
STATE_COVERAGE_THRESHOLDS before writing this script -- current
CONFIRMED=48, PARTIAL=3: IA, MI, SC. After this batch, PARTIAL pool is
empty -- all 51 jurisdictions CONFIRMED, closing the workstream.)

Usage:
    python tools/patch_coverage_threshold_batch9_ia_mi_sc.py --dry-run
    python tools/patch_coverage_threshold_batch9_ia_mi_sc.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

IA_OLD = '''    "IA": StateCoverageThreshold(
        thresholds={"general": 4},
        # Likely mislabeled -- the "no punitive damages" fact pattern
        # (see citation) matches this session's independently-confirmed
        # uncapped states, not a genuine tiered structure. NOT corrected
        # here: only pattern-consistency, not an independent Iowa
        # source check, this session. See citation.
        damages_cap_treatment="state_specific_tiers",
        confidence="PARTIAL",
        citation="Iowa Civil Rights Act, Iowa Code §216.6; §216.15. \\"Uncapped\\" is consistent with CT/PA/NH/IN's independently-verified no-punitive-damages structures this session, but not independently source-checked for Iowa specifically -- a lead for the next verification pass, not a confirmed result.",
    ),'''

IA_NEW = '''    "IA": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="uncapped",  # Ackelson v. Manley Toy Direct, L.L.C., 832 N.W.2d 678 (Iowa 2013) -- Iowa Supreme Court affirmed (unanimously, reaffirming 1986 precedent) that punitive damages are not permitted under the ICRA
        confidence="CONFIRMED",
        citation="Iowa Civil Rights Act, Iowa Code §216.15(9)(a)(8); Ackelson v. Manley Toy Direct, L.L.C., 832 N.W.2d 678 (Iowa 2013).",
    ),'''

MI_OLD = '''    "MI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # compensatory/mental-anguish damages uncapped; punitive/exemplary damages not available under ELCRA unless serving a compensatory purpose
        confidence="PARTIAL",
        citation="Elliott-Larsen Civil Rights Act, MCL §37.2201; §37.2801. \\"Uncapped\\" is consistent with CT/PA/NH/IN's independently-verified no-punitive-damages structures this session, but not independently source-checked for Michigan specifically -- a lead for the next verification pass, not a confirmed result.",
    ),'''

MI_NEW = '''    "MI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # Eide v. Kelsey-Hayes Co., 431 Mich. 26, 427 N.W.2d 488 (1988) -- Michigan Supreme Court held "exemplary damages" for mental anguish/distress/humiliation are available and uncapped, but are strictly compensatory in nature; traditional punitive damages designed to punish are not available under ELCRA
        confidence="CONFIRMED",
        citation="Elliott-Larsen Civil Rights Act, MCL §37.2801(1); §37.2801(3); Eide v. Kelsey-Hayes Co., 431 Mich. 26, 427 N.W.2d 488 (1988).",
    ),'''

SC_OLD = '''    "SC": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="SC Human Affairs Law, S.C. Code §1-13-30. Gemini's finding (no_damages_available per S.C. Code §1-13-90(d)(9)) was not independently verified against primary source text this session -- the statute's existence and general procedural structure were confirmed, but the specific remedies subsection Gemini cited was not directly located and confirmed. Working hypothesis for a future verification pass, same treatment as IA/MI.",
    ),'''

SC_NEW = '''    "SC": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="no_damages_available",  # S.C. Code Ann. §1-13-90(c)(16) -- remedies limited to an order that the discriminatory practice be discontinued, plus affirmative action (hiring, reinstatement, upgrading) with or without back pay; no compensatory damages for emotional distress, no punitive damages authorized anywhere in the section
        confidence="CONFIRMED",
        citation="SC Human Affairs Law, S.C. Code §1-13-30; §1-13-90(c)(16).",
    ),'''

COUNT_OLD = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 48, (
    "Expected exactly 48 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA, MS, NC, OK, AZ, HI, ID, MT, NM, NV, OR, UT, WY)"
)'''

COUNT_NEW = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 51, (
    "Expected exactly 51 CONFIRMED states -- all of STATE_COVERAGE_THRESHOLDS, the PARTIAL-state verification workstream is complete (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA, MS, NC, OK, AZ, HI, ID, MT, NM, NV, OR, UT, WY, IA, MI, SC)"
)'''

EDITS = [
    ('IA -> CONFIRMED + uncapped', IA_OLD, IA_NEW),
    ('MI -> CONFIRMED', MI_OLD, MI_NEW),
    ('SC -> CONFIRMED + no_damages_available', SC_OLD, SC_NEW),
    ('CONFIRMED-count assertion 48 -> 51 (workstream complete)', COUNT_OLD, COUNT_NEW),
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
