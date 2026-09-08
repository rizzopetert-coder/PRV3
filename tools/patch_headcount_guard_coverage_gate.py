"""
engine/friction_tax.py: resolve_coverage_gate() -- guard the raw
headcount comparison. An unusable headcount (empty string, other
non-numeric string, None) short-circuits to applies=False,
confidence="FEDERAL_FALLBACK", driving_jurisdiction=None, threshold=
the normal federal default for claim_type, before either the
CONFIRMED or FEDERAL_FALLBACK comparison branch ever runs a `>=`
against it. Every existing caller already treats applies=False as
LegalPricingStatus.NOT_APPLICABLE (clusters 1, 2, and 4b) -- no
downstream changes needed beyond this function.

Usage:
    python tools/patch_headcount_guard_coverage_gate.py --dry-run
    python tools/patch_headcount_guard_coverage_gate.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

OLD = '''    confirmed_entries: list[tuple[str, int]] = []
    partial_entries: list[tuple[str, int]] = []
    for jid in jurisdictions:'''

NEW = '''    # Guard: an unusable headcount (empty string, other non-numeric
    # string, None) can't drive either comparison branch below. Rather
    # than let a raw `>=` against a non-number raise, short-circuit to
    # "coverage cannot be determined" -- applies=False, same as a
    # real headcount that doesn't clear the threshold. Every caller
    # (clusters 1, 2, 4b) already turns applies=False into
    # LegalPricingStatus.NOT_APPLICABLE. Confirmed live, 2026-09-08:
    # this is what the self-select "Take the diagnostic" CTA
    # (web/app/diagnostic/page.tsx) sends today for any request.
    if not isinstance(headcount, (int, float)):
        threshold = _federal_threshold(claim_type)
        return CoverageResult(
            applies=False,
            threshold=threshold,
            claim_type=claim_type,
            driving_jurisdiction=None,
            confidence="FEDERAL_FALLBACK",
            partial_state_flag=False,
            partial_jurisdictions_considered=(),
        )

    confirmed_entries: list[tuple[str, int]] = []
    partial_entries: list[tuple[str, int]] = []
    for jid in jurisdictions:'''


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
