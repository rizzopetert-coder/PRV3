"""
engine/friction_tax.py: _single_state_legal_pricing()'s Cluster 3
branch -- guard against a None org_size bucket (headcount couldn't be
classified by resolve_headcount_bucket()). Without this guard,
_cluster_3_affected_workers() silently returns 0.0 for a None bucket
(HEADCOUNT_MIDPOINTS.get(None) misses), producing a fabricated
dollar_range=(0.0, 0.0) PRICED result for a real Cluster 3
legal-scoring state -- indistinguishable from "genuinely priced at
zero risk."

Pete's call (2026-09-08): QUALITATIVE_ONLY, not NOT_APPLICABLE -- this
is real, non-zero legal exposure the Principal should still see named
(the state's Cluster 3 condition genuinely applies), just unpriceable
in dollars without a valid headcount. NOT_APPLICABLE would silently
hide real exposure. Lands in unpriced_state_ids like any other
QUALITATIVE_ONLY state, same as Cluster 4c/Government already does.
No _logger.warning() -- that specifically signals an internal
data-integrity problem (DATA_INTEGRITY_GAP's own case); this is a bad/
missing input, not a lookup table gap.

Usage:
    python tools/patch_headcount_guard_cluster3.py --dry-run
    python tools/patch_headcount_guard_cluster3.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

OLD = '''    if cluster == 3:
        affected = _cluster_3_affected_workers(org_size, industry, score)
        r = (
            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,
            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,
        )
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)'''

NEW = '''    if cluster == 3:
        # org_size is None when resolve_headcount_bucket() couldn't
        # classify the request's headcount. Real, non-zero exposure
        # still applies (this state's Cluster 3 condition is real) --
        # QUALITATIVE_ONLY, not NOT_APPLICABLE, so it's still named
        # for the Principal rather than silently hidden. Checked here,
        # before _cluster_3_affected_workers() -- that function's own
        # midpoint_entry-is-None fallback returns 0.0, which would
        # otherwise produce a fabricated dollar_range=(0.0, 0.0)
        # PRICED result, indistinguishable from genuinely-zero risk.
        if org_size is None:
            return LegalPricingResult(status=LegalPricingStatus.QUALITATIVE_ONLY, dollar_range=None,
                coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
        affected = _cluster_3_affected_workers(org_size, industry, score)
        r = (
            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,
            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,
        )
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)'''


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
