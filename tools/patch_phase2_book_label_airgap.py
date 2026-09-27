"""
Phase 2 airgap fix (2026-09-27): the chunk scan found "Read more in The Book"
in hr-dx.com's downloaded scripts, because the label string was written in
PrivateOutput.tsx (a shared, statically loaded component) and passed to the
code-split StateBookLinkPR. The label now lives inside StateBookLinkPR
(PR-only, dynamically imported), and PrivateOutput passes a boolean.

Usage: python tools/patch_phase2_book_label_airgap.py --dry-run | --write
"""
import argparse, pathlib, sys
SB = pathlib.Path('web/components/StateBookLinkPR.tsx')
PO = pathlib.Path('web/components/PrivateOutput.tsx')
SB_EDITS = [
    ('  label,\n}: {\n  id: string;\n  name: string;\n'
     '  // Phase 2: a small secondary link (e.g. inside an expanded condition\n'
     '  // card) instead of the large name link.\n'
     '  label?: string;\n}) {\n  if (label) {\n',
     '  small,\n}: {\n  id: string;\n  name: string;\n'
     '  // Phase 2: a small secondary link inside an expanded condition card\n'
     '  // instead of the large name link. The label text lives here, in this\n'
     '  // PR-only code-split component, so it never reaches an hr-dx bundle.\n'
     '  small?: boolean;\n}) {\n  if (small) {\n    const label = "Read more in The Book";\n',
     'label -> small'),
]
PO_EDITS = [
    ('            : (row) => <StateBookLinkPR id={row.id} name={row.name} label="Read more in The Book" />\n',
     '            : (row) => <StateBookLinkPR id={row.id} name={row.name} small />\n',
     'pass boolean'),
]
def apply(p, eds):
    t = p.read_text(encoding='utf-8')
    for old, new, label in eds:
        if t.count(old) != 1: print(f'ERROR {p} {label} x{t.count(old)}', file=sys.stderr); sys.exit(1)
        t = t.replace(old, new, 1); print(f'[{p} :: {label}] OK')
    return t
def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args(); sb = apply(SB, SB_EDITS); po = apply(PO, PO_EDITS)
    if a.dry_run: print('DRY RUN -- nothing written.'); return
    SB.write_text(sb, encoding='utf-8'); PO.write_text(po, encoding='utf-8'); print('WROTE')
if __name__ == '__main__': main()
