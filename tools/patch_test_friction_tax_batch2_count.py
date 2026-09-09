"""
tools/test_friction_tax.py: update the CONFIRMED-count check for batch
2 of the PARTIAL-state verification workstream (NH/NJ/PA/RI/VT flipped
to CONFIRMED, engine/friction_tax.py) -- 17 -> 22, list extended.

No other fixture in this file references NH/NJ/PA/RI/VT (confirmed by
grep before writing the engine-side patch), so this is the only test
change batch 2 needs.

Usage:
    python tools/patch_test_friction_tax_batch2_count.py --dry-run
    python tools/patch_test_friction_tax_batch2_count.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

OLD = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 17 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''

NEW = '''check(
    "STATE_COVERAGE_THRESHOLDS has exactly 22 CONFIRMED entries (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO, CT, DE, DC, ME, MD, NH, NJ, PA, RI, VT)",
    {jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == "CONFIRMED"}
    == {"CA", "NY", "MA", "IL", "WA", "AK", "WV", "VA", "TX", "TN", "FL", "CO", "CT", "DE", "DC", "ME", "MD", "NH", "NJ", "PA", "RI", "VT"},
    f"got {sorted(jid for jid, v in STATE_COVERAGE_THRESHOLDS.items() if v.confidence == 'CONFIRMED')}",
)'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    count = content.count(OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
