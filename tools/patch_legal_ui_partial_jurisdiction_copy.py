"""
web/components/PrivateOutput.tsx: correct the has_partial_jurisdictions
secondary caveat copy in Block 4d.

The original copy ("alongside a confirmed one") described the
CONFIRMED-branch source of partial_state_flag, which is structurally
unreachable in the aggregate has_partial_jurisdictions signal --
confirmed by direct code trace (engine/friction_tax.py: the CONFIRMED
branch only sets partial_state_flag=True when applies=False, and
applies=False on a Cluster 1/2/4b state always resolves to
status=NOT_APPLICABLE, which the aggregation loop in
compute_legal_compliance_exposure() silently excludes before ever
reading partial_state_flag). The only reachable path is
FEDERAL_FALLBACK, where there is by definition no confirmed
jurisdiction at all. Live-confirmed 2026-09-08: built_to_fail +
jurisdictions=["TX"] (PARTIAL only) -> coverage_basis="federal_baseline",
has_partial_jurisdictions=true.

Usage:
    python tools/patch_legal_ui_partial_jurisdiction_copy.py --dry-run
    python tools/patch_legal_ui_partial_jurisdiction_copy.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/components/PrivateOutput.tsx')

OLD = '''          {legalHasPrice && legal.has_partial_jurisdictions && (
            <p className="text-[11px] text-gray-400 mt-1 mb-2 leading-relaxed">
              An unverified-confidence jurisdiction is present alongside a
              confirmed one here and could change this determination.
            </p>
          )}'''

NEW = '''          {legalHasPrice && legal.has_partial_jurisdictions && (
            <p className="text-[11px] text-gray-400 mt-1 mb-2 leading-relaxed">
              State law in this jurisdiction was not independently
              verified and may set a different threshold than what's
              reflected here.
            </p>
          )}'''


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
