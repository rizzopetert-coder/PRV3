"""
tools/test_hr_diagnostic_brand.py: account for the two compound families with
no authored PR backup copy (2026-09-27). The multi-state resolution-family fix
(lead state's family) made every family's example state route for the first
time. Before it, multi-state examples returned "" and were skipped. Two
compounds, "Roadmap + Executive Counsel" (4 states) and "Executive Counsel +
Roadmap" (1 state), have no authored PR backup copy and correctly fall back to
the generic copy, which names no tier. That is a content gap (Pete's call to
author), not a regression, so the check names those two explicitly and still
requires every other family to name a PR tier.

Usage: python tools/patch_hr_brand_test_unauthored_compounds.py --dry-run | --write
"""
import argparse, pathlib, sys
T = pathlib.Path('tools/test_hr_diagnostic_brand.py')
EDITS = [
    ('PR_TERMS = (\n',
     '# Compound families with no authored PR backup copy (2026-09-27, logged for\n'
     '# Pete to author): their fallback is the generic copy, which names no tier.\n'
     'PR_BACKUP_UNAUTHORED = {"Roadmap + Executive Counsel", "Executive Counsel + Roadmap"}\n'
     '\n'
     'PR_TERMS = (\n',
     'unauthored set'),
    ('        check(f"[{routing}] PR default still names a PR tier", any(t in ps["resolution_framing_text"] for t in PR_TERMS[:4]))\n',
     '        if routing in PR_BACKUP_UNAUTHORED:\n'
     '            check(f"[{routing}] PR default uses the generic copy (no authored compound copy yet)",\n'
     '                  not any(t in ps["resolution_framing_text"] for t in PR_TERMS[:4]))\n'
     '        else:\n'
     '            check(f"[{routing}] PR default still names a PR tier", any(t in ps["resolution_framing_text"] for t in PR_TERMS[:4]))\n',
     'check'),
]
def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args(); t = T.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        if t.count(old) != 1: print(f'ERROR {label} x{t.count(old)}', file=sys.stderr); sys.exit(1)
        t = t.replace(old, new, 1); print(f'[{T} :: {label}] OK')
    if a.dry_run: print('DRY RUN -- nothing written.'); return
    T.write_text(t, encoding='utf-8'); print('WROTE', T)
if __name__ == '__main__': main()
