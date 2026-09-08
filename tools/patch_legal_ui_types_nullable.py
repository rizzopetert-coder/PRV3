"""
web/lib/types.ts: LegalTailRiskExposure.low and .high widened from
`number` to `number | null`. This reflects real engine behavior --
compute_legal_compliance_exposure() (engine/friction_tax.py) returns
low=None when every identified Legal-scoring state is QUALITATIVE_ONLY
or DATA_INTEGRITY_GAP (no PRICED state at all), and contract.py's
assemble_output() still constructs the legal_tail_risk_exposure dict
in that case whenever has_unpriced_conditions is True.

Grepped web/ for `legal_tail_risk_exposure(\??)\.(low|high)` before
writing this patch -- zero call sites read .low/.high off this field
directly outside PrivateOutput.tsx's new Block 4d (which is written to
handle the null case), so this widening is safe with no other-file
follow-on required.

Usage:
    python tools/patch_legal_ui_types_nullable.py --dry-run
    python tools/patch_legal_ui_types_nullable.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/lib/types.ts')

OLD = '''export interface LegalTailRiskExposure {
  low: number;
  high: number;
  currency: string;'''

NEW = '''export interface LegalTailRiskExposure {
  // null when every identified Legal-scoring state is QUALITATIVE_ONLY
  // or DATA_INTEGRITY_GAP -- no PRICED state at all -- while
  // has_unpriced_conditions is still true. See unpriced_state_ids below.
  low: number | null;
  high: number | null;
  currency: string;'''


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
