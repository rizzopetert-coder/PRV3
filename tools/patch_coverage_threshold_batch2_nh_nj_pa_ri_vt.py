"""
engine/friction_tax.py: PARTIAL-state verification workstream, Batch 2.
Flips NH/NJ/PA/RI/VT from PARTIAL to CONFIRMED against primary statute
text. Second clean batch -- every state lands on "uncapped," but for
five genuinely distinct legal reasons (not a coincidence to
second-guess): NH's enhanced-compensatory-damages statute plus no
punitive carve-out, NJ's explicit LAD exclusion from the general
Punitive Damages Act cap, PA's punitive damages simply not being
recoverable under the PHRA at all, RI's two damages statutes carrying
no cap language, VT's damages statute stating no limit outright.

Six anchored edits, applied atomically (all must match or nothing is
written):
  1. NH entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. RSA 354-A:21-a authorizes uncapped "enhanced
     compensatory damages" for willful/reckless violations; RSA 354-A
     isn't one of RSA 507:16's narrow punitive-damages carve-outs.
  2. NJ entry -- the old "flagged, not resolved" comment is now
     resolved: N.J.S.A. §2A:15-5.14(c) explicitly excludes the LAD from
     the general Punitive Damages Act's 5x-compensatory/$350,000 cap.
     damages_cap_treatment stays uncapped, now for a verified reason
     rather than an assumption.
  3. PA entry -- damages_cap_treatment corrected state_specific_tiers
     -> uncapped. Hoy v. Angelone, 554 Pa. 134, 720 A.2d 745 (Pa. 1998)
     -- Pennsylvania Supreme Court held punitive damages aren't
     recoverable under the PHRA at all; compensatory has no cap or
     tier structure, so "tiers" never described this state's real
     situation.
  4. RI entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. Neither R.I. Gen. Laws §28-5-24 (compensatory) nor
     §28-5-29.1 (punitive) imposes a dollar cap or employer-size tier.
  5. VT entry -- damages_cap_treatment corrected federal_cap_applies ->
     uncapped. 21 V.S.A. §495b(b) authorizes compensatory and punitive
     damages with no statutory limit of any kind.
  6. CONFIRMED-count assertion -- 17 -> 22, state list extended.

Test-fixture check performed before writing this patch: grepped
tools/test_friction_tax.py for "NH"/"NJ"/"PA"/"RI"/"VT" -- zero
matches, none of these five states are used anywhere in the test
suite. No test changes needed beyond the count-check mirror.

Usage:
    python tools/patch_coverage_threshold_batch2_nh_nj_pa_ri_vt.py --dry-run
    python tools/patch_coverage_threshold_batch2_nh_nj_pa_ri_vt.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

EDIT_1_OLD = '''    "NH": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="RSA ch. 354-A (secondary source). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_1_NEW = '''    "NH": StateCoverageThreshold(
        thresholds={"general": 6},
        damages_cap_treatment="uncapped",  # RSA 354-A:21-a authorizes uncapped "enhanced compensatory damages" for willful/reckless violations; RSA 354-A isn't one of RSA 507:16's narrow punitive-damages carve-outs (RSA 359-D:11, RSA 570-A:11)
        confidence="CONFIRMED",
        citation="RSA ch. 354-A; RSA 354-A:21-a; RSA 507:16.",
    ),'''

EDIT_2_OLD = '''    "NJ": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        # UNCAPPED compensatory + punitive under NJLAD itself, but the
        # general NJ Punitive Damages Act cap (greater of 5x compensatory or
        # $350,000) may apply to the punitive component -- flagged, not
        # resolved, in the source document too.
        damages_cap_treatment="uncapped",
        confidence="PARTIAL",
        citation="NJLAD, N.J.S.A. §10:5-5, §10:5-3. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_2_NEW = '''    "NJ": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        # N.J.S.A. §2A:15-5.14(c) explicitly excludes "P.L.1945, c.169
        # (C.10:5-1 et seq.)" (the LAD) from the general Punitive
        # Damages Act's 5x-compensatory/$350,000 cap -- both
        # compensatory and punitive remain genuinely uncapped under
        # NJLAD specifically. Resolves the prior "flagged, not
        # resolved" open question.
        damages_cap_treatment="uncapped",
        confidence="CONFIRMED",
        citation="NJLAD, N.J.S.A. §10:5-5, §10:5-3; N.J.S.A. §2A:15-5.14(c).",
    ),'''

EDIT_3_OLD = '''    "PA": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_tiers",  # compensatory available, but PHRA bars punitive entirely
        confidence="PARTIAL",
        citation="Pennsylvania Human Relations Act, 43 P.S. §954. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_3_NEW = '''    "PA": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="uncapped",  # compensatory (including emotional distress) uncapped; punitive damages not recoverable under the PHRA at all -- Hoy v. Angelone, 554 Pa. 134, 720 A.2d 745 (Pa. 1998), Pennsylvania Supreme Court
        confidence="CONFIRMED",
        citation="Pennsylvania Human Relations Act, 43 P.S. §954.",
    ),'''

EDIT_4_OLD = '''    "RI": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="RI Fair Employment Practices Act, R.I. Gen. Laws §28-5-6 (secondary source). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_4_NEW = '''    "RI": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="uncapped",  # R.I. Gen. Laws §28-5-24 (compensatory) and §28-5-29.1 (punitive, on a malice/reckless-indifference showing) -- neither imposes a dollar cap or employer-size tier
        confidence="CONFIRMED",
        citation="RI Fair Employment Practices Act, R.I. Gen. Laws §28-5-24; §28-5-29.1.",
    ),'''

EDIT_5_OLD = '''    "VT": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum / all sizes
        damages_cap_treatment="federal_cap_applies",
        confidence="PARTIAL",
        citation="Vermont Fair Employment Practices Act, 21 V.S.A. §495. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_5_NEW = '''    "VT": StateCoverageThreshold(
        thresholds={"general": 1},  # no minimum / all sizes
        damages_cap_treatment="uncapped",  # 21 V.S.A. §495b(b) authorizes compensatory and punitive damages with no statutory limit of any kind
        confidence="CONFIRMED",
        citation="Vermont Fair Employment Practices Act, 21 V.S.A. §495; §495b(b).",
    ),'''

EDIT_6_OLD = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 17, (
    "Expected exactly 17 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD)"
)'''

EDIT_6_NEW = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 22, (
    "Expected exactly 22 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT)"
)'''

EDITS = [
    ('NH entry', EDIT_1_OLD, EDIT_1_NEW),
    ('NJ entry', EDIT_2_OLD, EDIT_2_NEW),
    ('PA entry', EDIT_3_OLD, EDIT_3_NEW),
    ('RI entry', EDIT_4_OLD, EDIT_4_NEW),
    ('VT entry', EDIT_5_OLD, EDIT_5_NEW),
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
