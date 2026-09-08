"""
engine/contract.py: add coverage_basis, has_partial_jurisdictions, and
restore unpriced_state_ids to the legal_tail_risk_exposure mapping.

Usage:
    python tools/patch_legal_coverage_confidence_contract.py --dry-run
    python tools/patch_legal_coverage_confidence_contract.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/contract.py')

OLD = '''    legal_tail_risk_exposure = (
        {
            "low":                     legal_result["low"],
            "high":                    legal_result["high"],
            "currency":                legal_result["currency"],
            "band":                    legal_result["band"],
            "caveat":                  LEGAL_TAIL_RISK_CAVEAT_TEXT,
            "has_unpriced_conditions": legal_result["has_unpriced_conditions"],
        }
        if legal_result["low"] is not None or legal_result["has_unpriced_conditions"]
        else None
    )'''

NEW = '''    legal_tail_risk_exposure = (
        {
            "low":                       legal_result["low"],
            "high":                      legal_result["high"],
            "currency":                  legal_result["currency"],
            "band":                      legal_result["band"],
            "caveat":                    LEGAL_TAIL_RISK_CAVEAT_TEXT,
            "has_unpriced_conditions":   legal_result["has_unpriced_conditions"],
            "unpriced_state_ids":        legal_result["unpriced_state_ids"],
            "coverage_basis":            legal_result["coverage_basis"],
            "has_partial_jurisdictions": legal_result["has_partial_jurisdictions"],
        }
        if legal_result["low"] is not None or legal_result["has_unpriced_conditions"]
        else None
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
        print('--- new block ---')
        print(NEW)
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
