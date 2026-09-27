"""
tools/test_resolution_families.py: RESOLUTION_FALLBACK_COPY now has 21
entries (12 single + 9 compound) after the two Pete-authored compound entries
(2026-09-27). Updates the pinned count, nothing else.

Usage: python tools/patch_resolution_families_test_count.py --dry-run | --write
"""
import argparse, pathlib, sys
T = pathlib.Path('tools/test_resolution_families.py')
OLD = ('    "RESOLUTION_FALLBACK_COPY has 19 entries (12 single + 7 compound)",\n'
       '    len(RESOLUTION_FALLBACK_COPY) == 19,\n')
NEW = ('    "RESOLUTION_FALLBACK_COPY has 21 entries (12 single + 9 compound)",\n'
       '    len(RESOLUTION_FALLBACK_COPY) == 21,\n')
def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args(); t = T.read_text(encoding='utf-8')
    if t.count(OLD) != 1: print('ERROR anchor', file=sys.stderr); sys.exit(1)
    t = t.replace(OLD, NEW, 1); print(f'[{T} :: count 19 -> 21] OK')
    if a.dry_run: print('DRY RUN -- nothing written.'); return
    T.write_text(t, encoding='utf-8'); print('WROTE', T)
if __name__ == '__main__': main()
