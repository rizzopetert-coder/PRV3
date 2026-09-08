"""
web/lib/types.ts: add unpriced_state_ids, coverage_basis, and
has_partial_jurisdictions to the LegalTailRiskExposure interface.

Usage:
    python tools/patch_legal_coverage_confidence_types.py --dry-run
    python tools/patch_legal_coverage_confidence_types.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/lib/types.ts')

OLD = '''export interface LegalTailRiskExposure {
  low: number;
  high: number;
  currency: string;
  band: LegalTailRiskBand | null;
  caveat: string;
  has_unpriced_conditions: boolean;
}'''

NEW = '''export interface LegalTailRiskExposure {
  low: number;
  high: number;
  currency: string;
  band: LegalTailRiskBand | null;
  caveat: string;
  has_unpriced_conditions: boolean;
  // Restored (was present in the engine's own return dict, dropped at
  // this mapping boundary until this session). State ids contributing
  // real-but-unpriced exposure -- QUALITATIVE_ONLY or DATA_INTEGRITY_GAP
  // in engine/friction_tax.py's LegalPricingStatus.
  unpriced_state_ids: string[];
  // Whether the underlying coverage-threshold determination (Clusters
  // 1, 2, 4b only -- see resolve_coverage_gate() in
  // engine/friction_tax.py) was resolved against a CONFIRMED-confidence
  // jurisdiction ("state_specific"), fell back to a federal statutory
  // threshold with no CONFIRMED jurisdiction present ("federal_baseline"),
  // combined both across a multi-state aggregate ("mixed"), or never
  // asked the coverage question at all -- every priced cluster was 3,
  // 4a, or 4c, or 5, none of which consult jurisdiction (null).
  coverage_basis: "state_specific" | "federal_baseline" | "mixed" | null;
  // True if a PARTIAL-confidence jurisdiction was present alongside a
  // CONFIRMED one and could have changed the coverage determination --
  // see CoverageResult.partial_state_flag in engine/friction_tax.py.
  has_partial_jurisdictions: boolean;
}'''


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
