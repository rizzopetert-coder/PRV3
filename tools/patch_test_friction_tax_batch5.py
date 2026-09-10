"""
tools/test_friction_tax.py: two updates for batch 5 of the
PARTIAL-state verification workstream (AL/AR/GA/KY/LA flipped to
CONFIRMED, engine/friction_tax.py).

1. CONFIRMED-count check -- 31 -> 36, list extended.
2. Test 38's "still-PARTIAL" example state -- AL, substituted in for
   TX back in Batch 0, is itself flipping to CONFIRMED this batch.
   Second substitution needed: MS, confirmed still PARTIAL with the
   identical threshold (15) AL had, via direct query before choosing
   it (STATE_COVERAGE_THRESHOLDS entries with confidence == "PARTIAL"
   and thresholds["general"] == 15: AL, AZ, GA, MS, NV, NC, OK, SC,
   UT -- AL/GA excluded since both are flipping this batch, MS picked
   from the remainder). Pure rename, no numeric change.

AR/GA/KY/LA (beyond AL) are not referenced anywhere else in this file
(confirmed by grep before writing the engine-side patch).

Usage:
    python tools/patch_test_friction_tax_batch5.py --dry-run
    python tools/patch_test_friction_tax_batch5.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

EDIT_1_OLD = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 31 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD", "NH", "NJ", "PA", "RI", "VT", "IN", "KS", "MN", "MO", "NE", "ND", "OH", "SD", "WI"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

EDIT_1_NEW = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 36 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD", "NH", "NJ", "PA", "RI", "VT", "IN", "KS", "MN", "MO", "NE", "ND", "OH", "SD", "WI", "AL", "AR", "GA", "KY", "LA"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

EDIT_2_OLD = '''# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
# AL is PARTIAL (not one of the 12 CONFIRMED states) -- this test used TX
# for the same purpose until batch 0 of the PARTIAL-state verification
# workstream flipped TX to CONFIRMED (2026-09-09); AL has the identical
# threshold (15) TX had before that, so this is a pure rename, no
# numeric change. Confirms PARTIAL data never produces
# confidence="CONFIRMED" or a driving_jurisdiction, even though it's
# present in the input and does surface as a qualitative flag.

check(
    "sanity: AL is PARTIAL confidence, not CONFIRMED, needed for the check below",
    STATE_COVERAGE_THRESHOLDS["AL"].confidence == "PARTIAL",
    f"got {STATE_COVERAGE_THRESHOLDS['AL'].confidence!r}",
)
_gate_partial_only = resolve_coverage_gate(headcount=20, jurisdictions=["AL"], claim_type="general")
check(
    "resolve_coverage_gate: PARTIAL-only jurisdiction list -> confidence='FEDERAL_FALLBACK', "
    "NOT 'CONFIRMED' -- a PARTIAL state's own number never drives the determination",
    _gate_partial_only.confidence == "FEDERAL_FALLBACK" and _gate_partial_only.driving_jurisdiction is None,
    f"got {_gate_partial_only}",
)
check(
    "resolve_coverage_gate: PARTIAL-only jurisdiction list still raises the qualitative flag, "
    "naming AL specifically, rather than silently using its unverified threshold",
    _gate_partial_only.partial_state_flag is True
    and _gate_partial_only.partial_jurisdictions_considered == ("AL",),
    f"got {_gate_partial_only}",'''

EDIT_2_NEW = '''# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
# MS is PARTIAL (not one of the 36 CONFIRMED states) -- this test used
# AL for the same purpose until batch 5 of the PARTIAL-state
# verification workstream flipped AL to CONFIRMED (2026-09-09); MS has
# the identical threshold (15) AL had before that, so this is a pure
# rename, no numeric change (this test's second substitution --
# originally TX, per batch 0). Confirms PARTIAL data never produces
# confidence="CONFIRMED" or a driving_jurisdiction, even though it's
# present in the input and does surface as a qualitative flag.

check(
    "sanity: MS is PARTIAL confidence, not CONFIRMED, needed for the check below",
    STATE_COVERAGE_THRESHOLDS["MS"].confidence == "PARTIAL",
    f"got {STATE_COVERAGE_THRESHOLDS['MS'].confidence!r}",
)
_gate_partial_only = resolve_coverage_gate(headcount=20, jurisdictions=["MS"], claim_type="general")
check(
    "resolve_coverage_gate: PARTIAL-only jurisdiction list -> confidence='FEDERAL_FALLBACK', "
    "NOT 'CONFIRMED' -- a PARTIAL state's own number never drives the determination",
    _gate_partial_only.confidence == "FEDERAL_FALLBACK" and _gate_partial_only.driving_jurisdiction is None,
    f"got {_gate_partial_only}",
)
check(
    "resolve_coverage_gate: PARTIAL-only jurisdiction list still raises the qualitative flag, "
    "naming MS specifically, rather than silently using its unverified threshold",
    _gate_partial_only.partial_state_flag is True
    and _gate_partial_only.partial_jurisdictions_considered == ("MS",),
    f"got {_gate_partial_only}",'''

EDITS = [
    ('CONFIRMED-count check', EDIT_1_OLD, EDIT_1_NEW),
    ('test 38: AL -> MS rename', EDIT_2_OLD, EDIT_2_NEW),
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
        print(f'DRY RUN -- both anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
