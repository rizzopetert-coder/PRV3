"""
web/lib/engine-client.ts: widen EnginePayload["intake"].headcount from
`string` to `number | string`. Prerequisite for SelfSelectIntakeModal --
resolve_headcount_bucket()'s isinstance(headcount, (int, float)) guard
(this session's earlier fix) cannot distinguish a real numeric string
("60") from garbage ("", "abc") -- both fail the isinstance check and
silently degrade to null/NOT_APPLICABLE. A genuine JS number survives
JSON serialization as a Python int/float and passes the guard
correctly; a string never can, regardless of its content. Existing
blank-intake call sites (headcount: "" in app/diagnostic/page.tsx's
current default, dev/diagnostic-preview's fixture) stay valid
unchanged under the widened type.

Usage:
    python tools/patch_headcount_type_widen_engine_client.py --dry-run
    python tools/patch_headcount_type_widen_engine_client.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/lib/engine-client.ts')

OLD = '''export interface EnginePayload {
  selectedStateIds: string[];
  intake: {
    headcount: string;
    industry: string;
    orgType: string;
    jurisdictions: string[];
    significantEvents: string[];
    principalRole: string;
  };'''

NEW = '''export interface EnginePayload {
  selectedStateIds: string[];
  intake: {
    // number | string: a real headcount (SelfSelectIntakeModal) must
    // arrive as a genuine JS number -- resolve_headcount_bucket()'s
    // isinstance(headcount, (int, float)) guard (engine/friction_tax.py)
    // cannot tell a valid numeric string from garbage, and silently
    // degrades both to null/NOT_APPLICABLE. string is kept for the
    // existing blank-intake sentinel ("") used where no real headcount
    // was ever collected.
    headcount: number | string;
    industry: string;
    orgType: string;
    jurisdictions: string[];
    significantEvents: string[];
    principalRole: string;
  };'''


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
