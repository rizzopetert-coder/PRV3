"""
engine/friction_tax.py: resolve_headcount_bucket() -- stop raising on
an unusable headcount (empty string, non-numeric, None, etc.), return
None instead. Both real callers already degrade correctly through
existing logic once this stops throwing:

  - compute_friction_tax(): PAYROLL_BASELINE_GRID.get((None, industry))
    misses -> payroll_floor=None -> calibration_complete=False -> its
    own existing branch returns the {"low": None, ...} no-estimate
    shape. No other change needed there.
  - compute_legal_compliance_exposure()'s Cluster 4b ceiling lookup:
    _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(None) misses -> existing
    DATA_INTEGRITY_GAP path, unchanged.

Root cause: a live production 500 confirmed 2026-09-08 -- the
self-select "Take the diagnostic" CTA (web/app/diagnostic/page.tsx,
untouched by this fix) sends headcount: "" to /api/result for ANY
selection, not just Cluster 1/2/4b legal-scoring states, since this
function is called unconditionally at the top of both
compute_friction_tax() and compute_legal_compliance_exposure().

Usage:
    python tools/patch_headcount_guard_bucket.py --dry-run
    python tools/patch_headcount_guard_bucket.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

OLD = '''def resolve_headcount_bucket(headcount: int) -> str:
    """
    Map a precise headcount int (engine/data/intake.py's
    HEADCOUNT_FIELD_SPEC) to its HEADCOUNT_BUCKETS bucket string.
    Boundaries match the field spec's increment schedule exactly.

    Legacy string-headcount tolerance (organization_size string|number
    collapse, 2026-08-29) removed -- Redis confirmed clear of legacy
    string-bucket records before this ran, and the web layer now
    guarantees a real number end to end.
    """
    if headcount < 25:
        return "Under 25"
    if headcount < 100:
        return "25-99"
    if headcount < 250:
        return "100-249"
    if headcount < 500:
        return "250-499"
    if headcount < 1000:
        return "500-999"
    return "1000+"'''

NEW = '''def resolve_headcount_bucket(headcount) -> Optional[str]:
    """
    Map a precise headcount int (engine/data/intake.py's
    HEADCOUNT_FIELD_SPEC) to its HEADCOUNT_BUCKETS bucket string.
    Boundaries match the field spec's increment schedule exactly.

    Legacy string-headcount tolerance (organization_size string|number
    collapse, 2026-08-29) removed -- Redis confirmed clear of legacy
    string-bucket records before this ran, and the web layer was
    believed at the time to guarantee a real number end to end. That
    guarantee proved false: confirmed live, 2026-09-08, the self-select
    "Take the diagnostic" CTA (web/app/diagnostic/page.tsx) sends
    headcount="" unconditionally, causing a production 500 for every
    request through that path, not just ones touching Legal/Compliance
    clusters -- this function is called at the top of both
    compute_friction_tax() and compute_legal_compliance_exposure(),
    unconditionally, before any per-state logic runs.

    Returns None -- rather than raising -- when headcount isn't a real,
    comparable number (empty string, other non-numeric string, None).
    This does NOT reintroduce the removed string-to-number coercion
    above; a numeric string like "152" is still treated as
    unclassifiable, not parsed. Callers treat None as "cannot classify
    this headcount" and degrade to their own existing no-result shape
    -- see compute_friction_tax()'s calibration_complete=False branch
    and compute_legal_compliance_exposure()'s per-cluster handling,
    immediately after each of their own calls to this function.
    """
    if not isinstance(headcount, (int, float)):
        return None
    if headcount < 25:
        return "Under 25"
    if headcount < 100:
        return "25-99"
    if headcount < 250:
        return "100-249"
    if headcount < 500:
        return "250-499"
    if headcount < 1000:
        return "500-999"
    return "1000+"'''


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
