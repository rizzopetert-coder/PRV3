"""
tools/test_friction_tax.py: update the two fixtures broken by batch 0
of the PARTIAL-state verification workstream (VA/TX/TN/FL/CO flipped
to CONFIRMED, engine/friction_tax.py).

1. "exactly 7 CONFIRMED" check -- now 12, list extended.
2. Test 38 ("PARTIAL-only jurisdiction never drives the answer") used
   TX as its real-data example of a PARTIAL state. TX is now CONFIRMED,
   so this test no longer demonstrates what it claims to. Substituted
   with AL, a genuinely still-PARTIAL state with the identical
   threshold (15) TX had before this batch -- a pure rename, no
   numeric values change, confirmed via direct read of AL's current
   entry before writing this patch.

Test 39 ("PARTIAL state present but NOT the deciding factor") also
references TX, but temporarily monkey-patches TX's entry to a
synthetic PARTIAL one for the duration of that one test (save/mutate/
restore), so it's unaffected by TX's real confidence value and needs
no change -- confirmed by its own two checks passing in the failing
run this patch fixes, before this patch was written.

Usage:
    python tools/patch_test_friction_tax_batch0_fixtures.py --dry-run
    python tools/patch_test_friction_tax_batch0_fixtures.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

EDIT_1_OLD = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 7 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

EDIT_1_NEW = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 12 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

EDIT_2_OLD = '''# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
# TX is PARTIAL (not one of the 7 CONFIRMED states). Confirms PARTIAL data
# never produces confidence="CONFIRMED" or a driving_jurisdiction, even
# though it's present in the input and does surface as a qualitative flag.

check(
    "sanity: TX is PARTIAL confidence, not CONFIRMED, needed for the check below",
    STATE_COVERAGE_THRESHOLDS["TX"].confidence == "PARTIAL",
    f"got {STATE_COVERAGE_THRESHOLDS['TX'].confidence!r}",
)
_gate_partial_only = resolve_coverage_gate(headcount=20, jurisdictions=["TX"], claim_type="general")
check(
    "resolve_coverage_gate: PARTIAL-only jurisdiction list -> confidence='FEDERAL_FALLBACK', "
    "NOT 'CONFIRMED' -- a PARTIAL state's own number never drives the determination",
    _gate_partial_only.confidence == "FEDERAL_FALLBACK" and _gate_partial_only.driving_jurisdiction is None,
    f"got {_gate_partial_only}",
)
check(
    "resolve_coverage_gate: PARTIAL-only jurisdiction list still raises the qualitative flag, "
    "naming TX specifically, rather than silently using its unverified threshold",
    _gate_partial_only.partial_state_flag is True
    and _gate_partial_only.partial_jurisdictions_considered == ("TX",),
    f"got {_gate_partial_only}",
)'''

EDIT_2_NEW = '''# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
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
    f"got {_gate_partial_only}",
)'''

EDITS = [
    ('12-CONFIRMED count check', EDIT_1_OLD, EDIT_1_NEW),
    ('test 38: TX -> AL rename', EDIT_2_OLD, EDIT_2_NEW),
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
