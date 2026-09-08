"""
web/app/api/result/route.ts: widen ResultRequest.headcount from
`string` to `number | string`. Same rationale as the matching
EnginePayload["intake"] change in web/lib/engine-client.ts -- see that
patch script's docstring.

Usage:
    python tools/patch_headcount_type_widen_result_route.py --dry-run
    python tools/patch_headcount_type_widen_result_route.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/app/api/result/route.ts')

OLD = '''interface ResultRequest {
  selectedStateIds: string[];
  intake: {
    headcount: string;
    industry: string;
    orgType: string;
    jurisdictions: string[];
    significantEvents: string[];
    principalRole: string;
  };
}'''

NEW = '''interface ResultRequest {
  selectedStateIds: string[];
  intake: {
    // number | string -- see the matching EnginePayload["intake"]
    // change in web/lib/engine-client.ts for the full rationale.
    headcount: number | string;
    industry: string;
    orgType: string;
    jurisdictions: string[];
    significantEvents: string[];
    principalRole: string;
  };
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
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
