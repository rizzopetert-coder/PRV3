"""
engine/friction_tax.py: PARTIAL-state verification workstream, Batch 3.
Flips IN/KS/MN/MO from PARTIAL to CONFIRMED against primary statute
text. IA and MI are explicitly NOT flipped -- their "uncapped" label
is only supported by pattern-consistency with this session's other
independently-confirmed no-punitive-damages states, not by an
independent Iowa/Michigan-specific source check. Per the codebase's own
CONFIRMED definition ("independently verified against primary statute
text this session"), that doesn't meet the bar -- documented as an
explicit working hypothesis instead of a finding, values left
unchanged (no functional effect either way: PARTIAL data can't drive a
dollar-affecting determination, and damages_cap_treatment isn't
consumed by pricing logic yet).

Six anchored edits, applied atomically (all must match or nothing is
written):
  1. IN entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. Indiana Civil Rights Commission v. Alder, 714 N.E.2d 632
     (Ind. 1999) -- ICRC has authority to award uncapped compensatory/
     emotional-distress damages but no authority to award punitive
     damages.
  2. IA entry -- documentation only. confidence stays PARTIAL,
     thresholds and damages_cap_treatment unchanged. Citation extended
     with the pattern-consistency hypothesis, explicitly labeled as a
     lead for a future verification pass, not a confirmed result.
  3. KS entry -- damages_cap_treatment corrected state_specific_tiers
     -> state_specific_flat. K.S.A. §44-1005(k) sets a $2,000 flat cap
     on pain/suffering/humiliation damages specifically, not scaled by
     employer size -- "tiers" never described this state's real
     structure.
  4. MI entry -- documentation only, same treatment as IA. Already
     "uncapped" before this batch; that value is kept, confidence
     stays PARTIAL, citation extended with the same explicit hypothesis
     framing.
  5. MN entry -- threshold and damages_cap_treatment confirmed accurate
     as already modeled, now on verified grounds: the 2024 amendment
     (HF4109) that removed the private-sector punitive cap is
     independently confirmed.
  6. MO entry -- threshold and damages_cap_treatment confirmed accurate
     as already modeled; one precision correction -- the bottom tier is
     "more than five and fewer than 101 employees" (6-100), not "5-100"
     as an earlier pass might have implied, matching the MHRA's own
     6-employee coverage threshold exactly.
  7. CONFIRMED-count assertion -- 22 -> 26 (four states: IN, KS, MN,
     MO -- not IA/MI).

Test-fixture check performed before writing this patch: grepped
tools/test_friction_tax.py for "IN"/"IA"/"KS"/"MI"/"MN"/"MO" -- zero
matches across all six states. No test changes needed beyond the
count-check mirror (which only needs the four CONFIRMED states).

Usage:
    python tools/patch_coverage_threshold_batch3_in_ia_ks_mi_mn_mo.py --dry-run
    python tools/patch_coverage_threshold_batch3_in_ia_ks_mi_mn_mo.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

EDIT_1_OLD = '''    "IN": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="Indiana Civil Rights Law, Ind. Code §22-9-1-2. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_1_NEW = '''    "IN": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="uncapped",  # compensatory/emotional-distress damages available with no statutory cap; ICRC has no authority to award punitive damages -- Indiana Civil Rights Commission v. Alder, 714 N.E.2d 632 (Ind. 1999)
        confidence="CONFIRMED",
        citation="Indiana Civil Rights Law, Ind. Code §22-9-1-2.",
    ),'''

EDIT_2_OLD = '''    "IA": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_tiers",  # compensatory available, but NO punitive damages
        confidence="PARTIAL",
        citation="Iowa Civil Rights Act, Iowa Code §216.6. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_2_NEW = '''    "IA": StateCoverageThreshold(
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

EDIT_3_OLD = '''    "KS": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_tiers",  # $2,000 cap on pain/suffering/humiliation
        confidence="PARTIAL",
        citation="Kansas Act Against Discrimination, K.S.A. §44-1009. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_3_NEW = '''    "KS": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_flat",  # $2,000 flat cap on pain/suffering/humiliation damages specifically, not scaled by employer size, K.S.A. §44-1005(k); no punitive damages authority under KAAD
        confidence="CONFIRMED",
        citation="Kansas Act Against Discrimination, K.S.A. §44-1009; §44-1005(k); Woods v. Midwest Conveyor Co.; Sporleder v. U.S. Bancorp.",
    ),'''

EDIT_4_OLD = '''    "MI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # compensatory uncapped; note NO punitive damages available at all
        confidence="PARTIAL",
        citation="Elliott-Larsen Civil Rights Act, MCL §37.2201. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_4_NEW = '''    "MI": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # compensatory/mental-anguish damages uncapped; punitive/exemplary damages not available under ELCRA unless serving a compensatory purpose
        confidence="PARTIAL",
        citation="Elliott-Larsen Civil Rights Act, MCL §37.2201; §37.2801. \\"Uncapped\\" is consistent with CT/PA/NH/IN's independently-verified no-punitive-damages structures this session, but not independently source-checked for Michigan specifically -- a lead for the next verification pass, not a confirmed result.",
    ),'''

EDIT_5_OLD = '''    "MN": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # treble damages available; $25k punitive cap removed 2024 (HF4109)
        confidence="PARTIAL",
        citation="Minnesota Human Rights Act, Minn. Stat. ch. 363A. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_5_NEW = '''    "MN": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        damages_cap_treatment="uncapped",  # treble damages available; 2024 amendment (HF4109, signed May 15 2024, eff. Aug. 1 2024) removed the prior $25,000 punitive-damages cap for private-sector employers -- a $25,000 cap remains only for claims against political subdivisions
        confidence="CONFIRMED",
        citation="Minnesota Human Rights Act, Minn. Stat. §363A.29.",
    ),'''

EDIT_6_OLD = '''    "MO": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="state_specific_tiers",  # own tiered cap, SB 43 (2017)
        confidence="PARTIAL",
        citation="Missouri Human Rights Act, RSMo §213.010; SB 43 eff. Aug. 28, 2017. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_6_NEW = '''    "MO": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="state_specific_tiers",  # combined compensatory (non-pecuniary)-and-punitive cap: $50,000 (more than 5 and fewer than 101 employees, i.e. 6-100 -- matches MHRA's own 6-employee coverage threshold) / $100,000 (101-200) / $200,000 (201-500) / $500,000 (500+); back pay/front pay not subject to these caps
        confidence="CONFIRMED",
        citation="Missouri Human Rights Act, RSMo §213.010; §213.111(4); SB 43 eff. Aug. 28, 2017.",
    ),'''

EDIT_7_OLD = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 22, (
    "Expected exactly 22 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT)"
)'''

EDIT_7_NEW = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 26, (
    "Expected exactly 26 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO)"
)'''

EDITS = [
    ('IN entry', EDIT_1_OLD, EDIT_1_NEW),
    ('IA entry (documentation only)', EDIT_2_OLD, EDIT_2_NEW),
    ('KS entry', EDIT_3_OLD, EDIT_3_NEW),
    ('MI entry (documentation only)', EDIT_4_OLD, EDIT_4_NEW),
    ('MN entry', EDIT_5_OLD, EDIT_5_NEW),
    ('MO entry', EDIT_6_OLD, EDIT_6_NEW),
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
