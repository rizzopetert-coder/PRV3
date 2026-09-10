"""
tools/test_friction_tax.py: two updates for batch 6 of the
PARTIAL-state verification workstream (MS/NC/OK flipped to CONFIRMED,
SC held at PARTIAL, engine/friction_tax.py).

1. CONFIRMED-count check -- 36 -> 39, list extended.
2. Test 38's "still-PARTIAL" example state -- MS, substituted in for AL
   back in batch 5, is itself flipping to CONFIRMED this batch. Third
   substitution needed: SC, confirmed still PARTIAL this batch with the
   identical threshold (15) MS had, via direct query before choosing it.

NC/OK (beyond MS) are not referenced anywhere else in this file
(confirmed by grep before writing the engine-side patch).

Usage:
    python tools/patch_test_friction_tax_batch6.py --dry-run
    python tools/patch_test_friction_tax_batch6.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

EDIT_1_OLD = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 36 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD", "NH", "NJ", "PA", "RI", "VT", "IN", "KS", "MN", "MO", "NE", "ND", "OH", "SD", "WI", "AL", "AR", "GA", "KY", "LA"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

EDIT_1_NEW = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 39 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA, MS, NC, OK)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD", "NH", "NJ", "PA", "RI", "VT", "IN", "KS", "MN", "MO", "NE", "ND", "OH", "SD", "WI", "AL", "AR", "GA", "KY", "LA", "MS", "NC", "OK"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

EDIT_2_OLD = '''# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
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

EDIT_2_NEW = '''# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
# SC is PARTIAL (not one of the 39 CONFIRMED states) -- this test used
# MS for the same purpose until batch 6 of the PARTIAL-state
# verification workstream flipped MS to CONFIRMED (2026-09-10); SC has
# the identical threshold (15) MS had before that, so this is a pure
# rename, no numeric change (this test's third substitution --
# originally TX per batch 0, then AL per batch 5). Confirms PARTIAL data
# never produces confidence="CONFIRMED" or a driving_jurisdiction, even
# though it's present in the input and does surface as a qualitative
# flag.

check(
    "sanity: SC is PARTIAL confidence, not CONFIRMED, needed for the check below",
    STATE_COVERAGE_THRESHOLDS["SC"].confidence == "PARTIAL",
    f"got {STATE_COVERAGE_THRESHOLDS['SC'].confidence!r}",
)
_gate_partial_only = resolve_coverage_gate(headcount=20, jurisdictions=["SC"], claim_type="general")
check(
    "resolve_coverage_gate: PARTIAL-only jurisdiction list -> confidence='FEDERAL_FALLBACK', "
    "NOT 'CONFIRMED' -- a PARTIAL state's own number never drives the determination",
    _gate_partial_only.confidence == "FEDERAL_FALLBACK" and _gate_partial_only.driving_jurisdiction is None,
    f"got {_gate_partial_only}",
)
check(
    "resolve_coverage_gate: PARTIAL-only jurisdiction list still raises the qualitative flag, "
    "naming SC specifically, rather than silently using its unverified threshold",
    _gate_partial_only.partial_state_flag is True
    and _gate_partial_only.partial_jurisdictions_considered == ("SC",),
    f"got {_gate_partial_only}",'''

EDITS = [
    ('CONFIRMED-count check', EDIT_1_OLD, EDIT_1_NEW),
    ('test 38: MS -> SC rename', EDIT_2_OLD, EDIT_2_NEW),
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
