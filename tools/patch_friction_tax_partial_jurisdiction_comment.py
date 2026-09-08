"""
engine/friction_tax.py: extend the "# NOT_APPLICABLE: silently excluded"
comment in compute_legal_compliance_exposure()'s aggregation loop with
the structural-unreachability finding for resolve_coverage_gate()'s
CONFIRMED-branch partial_state_flag, so a future reader doesn't
re-discover this the hard way. As specified in last check's report,
landed exactly as drafted.

Usage:
    python tools/patch_friction_tax_partial_jurisdiction_comment.py --dry-run
    python tools/patch_friction_tax_partial_jurisdiction_comment.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

OLD = "        # NOT_APPLICABLE: silently excluded, unchanged from before.\n"

NEW = (
    "        # NOT_APPLICABLE: silently excluded, unchanged from before. Note:\n"
    "        # this is also why resolve_coverage_gate()'s CONFIRMED-branch\n"
    "        # partial_state_flag can never surface here -- that branch only sets\n"
    "        # partial_state_flag=True when applies=False, and applies=False on a\n"
    "        # Cluster 1/2/4b state always resolves to status=NOT_APPLICABLE\n"
    "        # above, so the signal is discarded right here. The only reachable\n"
    "        # path to has_partial_jurisdictions=True in this aggregate is\n"
    "        # FEDERAL_FALLBACK, whose partial_state_flag is set unconditionally\n"
    "        # regardless of applies (confirmed live, 2026-09-08: built_to_fail +\n"
    '        # jurisdictions=["TX"] (PARTIAL only, no CONFIRMED jurisdiction) ->\n'
    '        # coverage_basis="federal_baseline", has_partial_jurisdictions=true).\n'
)


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
