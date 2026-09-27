"""
Condensed report: cap the locked "N more conditions surfaced" count (Pete,
2026-09-27, cutoff 3 confirmed). Across 32 real condensed sessions N was
either 1-5 or 10-47 (nothing in between): problem-heavy answers push the
condensed engine's qualifying count into the tens, which isn't meaningful
signal from 9 answers. Real count for 1-3, "Several more conditions
surfaced" above that. The row stays hidden at 0.

Usage: python tools/patch_condensed_count_cap.py --dry-run | --write
"""
import argparse, pathlib, sys
CO = pathlib.Path('web/components/CondensedOutput.tsx')
EDITS = [
    ('interface CondensedOutputProps {\n',
     '// Above this, the count reads as noise for a 9-answer sample (real sessions\n'
     '// gave either 1-5 or 10-47 additional conditions), so the locked row says\n'
     '// "Several more" instead of a number. Pete-confirmed 2026-09-27.\n'
     'const LOCKED_COUNT_CAP = 3;\n'
     '\n'
     'function moreConditionsText(more: number): string | undefined {\n'
     '  if (more <= 0) return undefined;\n'
     '  if (more > LOCKED_COUNT_CAP) return "Several more conditions surfaced, unlock the full diagnostic";\n'
     '  return `${more} more condition${more === 1 ? "" : "s"} surfaced, unlock the full diagnostic`;\n'
     '}\n'
     '\n'
     'interface CondensedOutputProps {\n',
     'cap helper'),
    ('        lockedRow={\n'
     '          more > 0\n'
     '            ? `${more} more condition${more === 1 ? "" : "s"} surfaced, unlock the full diagnostic`\n'
     '            : undefined\n'
     '        }\n',
     '        lockedRow={moreConditionsText(more)}\n',
     'use helper'),
]
def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args(); t = CO.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        if t.count(old) != 1: print(f'ERROR {label} x{t.count(old)}', file=sys.stderr); sys.exit(1)
        t = t.replace(old, new, 1); print(f'[{CO} :: {label}] OK')
    if a.dry_run: print('DRY RUN -- nothing written.'); return
    CO.write_text(t, encoding='utf-8'); print('WROTE', CO)
if __name__ == '__main__': main()
