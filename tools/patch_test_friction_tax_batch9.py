"""
tools/test_friction_tax.py: two updates for batch 9 -- final batch of
the PARTIAL-state verification workstream (IA/MI/SC flipped to
CONFIRMED, engine/friction_tax.py). 51 of 51 jurisdictions CONFIRMED
after this batch -- STATE_COVERAGE_THRESHOLDS has zero PARTIAL entries
left.

1. CONFIRMED-count check -- 48 -> 51, list extended to all 51 keys.

2. Test 38 STRUCTURAL CHANGE, not a fourth simple rename. Test 38 has
   been substituted three times this workstream (TX -> AL -> MS -> SC)
   by pointing at whichever real state was still PARTIAL. That pattern
   is no longer available: after this batch, no real PARTIAL state
   exists anywhere in the table for a fourth substitution to point at.
   Rewritten to the same save/mutate/restore monkey-patch convention
   test 39 (a few lines below it in this file) already uses for exactly
   this reason -- test 39 already monkey-patches TX to a synthetic
   PARTIAL entry rather than relying on real seed data, since real
   PARTIAL placeholders default to threshold=15 and can't exercise
   every scenario. Test 38 now does the same: temporarily overwrites
   SC's entry with a synthetic PARTIAL fixture, runs the same two
   checks as before (confidence='FEDERAL_FALLBACK', driving_jurisdiction
   is None, partial_state_flag=True), then restores SC's real
   (post-batch-9) CONFIRMED entry in a finally block. This makes the
   test durable against every future state's CONFIRMED status,
   including SC's own -- no fifth substitution will ever be needed.

Usage:
    python tools/patch_test_friction_tax_batch9.py --dry-run
    python tools/patch_test_friction_tax_batch9.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

EDIT_1_OLD = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 48 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA, MS, NC, OK, AZ, HI, ID, MT, NM, NV, OR, UT, WY)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD", "NH", "NJ", "PA", "RI", "VT", "IN", "KS", "MN", "MO", "NE", "ND", "OH", "SD", "WI", "AL", "AR", "GA", "KY", "LA", "MS", "NC", "OK", "AZ", "HI", "ID", "MT", "NM", "NV", "OR", "UT", "WY"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

EDIT_1_NEW = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 51 CONFIRMED entries -- all 51 jurisdictions, the PARTIAL-state verification workstream is complete (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT, IN, KS, MN, MO, NE, ND, OH, SD, WI, AL, AR, GA, KY, LA, MS, NC, OK, AZ, HI, ID, MT, NM, NV, OR, UT, WY, IA, MI, SC)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD", "NH", "NJ", "PA", "RI", "VT", "IN", "KS", "MN", "MO", "NE", "ND", "OH", "SD", "WI", "AL", "AR", "GA", "KY", "LA", "MS", "NC", "OK", "AZ", "HI", "ID", "MT", "NM", "NV", "OR", "UT", "WY", "IA", "MI", "SC"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

EDIT_2_OLD = '''# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
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
    f"got {_gate_partial_only}",
)'''

EDIT_2_NEW = '''# -- 38. resolve_coverage_gate() -- PARTIAL-only jurisdiction never drives the answer --
# STRUCTURAL CHANGE as of batch 9: this test was substituted three
# times across the workstream (TX -> AL, batch 0; AL -> MS, batch 5;
# MS -> SC, batch 6) by pointing at whichever real state was still
# PARTIAL. As of batch 9, STATE_COVERAGE_THRESHOLDS has zero PARTIAL
# entries left -- all 51 jurisdictions are CONFIRMED -- so no real
# state can serve this purpose anymore. Rewritten to the same
# save/mutate/restore monkey-patch convention test 39 (below) already
# uses for the same underlying reason: temporarily overwrites SC's
# entry with a synthetic PARTIAL fixture, then restores SC's real
# CONFIRMED entry in a finally block. Durable against every future
# state's CONFIRMED status, including SC's own -- no further
# substitution will be needed. Confirms PARTIAL data never produces
# confidence="CONFIRMED" or a driving_jurisdiction, even though it's
# present in the input and does surface as a qualitative flag.

_original_sc_entry_38 = STATE_COVERAGE_THRESHOLDS["SC"]
try:
    _ft.STATE_COVERAGE_THRESHOLDS["SC"] = StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="no_damages_available",
        confidence="PARTIAL",
        citation="Synthetic test fixture -- not real data, restored after this check.",
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
        f"got {_gate_partial_only}",
    )
finally:
    _ft.STATE_COVERAGE_THRESHOLDS["SC"] = _original_sc_entry_38'''

EDITS = [
    ('CONFIRMED-count check', EDIT_1_OLD, EDIT_1_NEW),
    ('test 38: rewritten to monkey-patch convention (workstream complete)', EDIT_2_OLD, EDIT_2_NEW),
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
