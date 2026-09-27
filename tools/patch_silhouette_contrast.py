"""
Condensed report: make the locked constellation silhouette readable (Pete,
2026-09-27). It was the chart's lightest grid grey (#e5e7eb) at 60% opacity,
nearly invisible on paper. Now #9ca3af (gray-400) at 70%: clearly visible,
still unmistakably a placeholder (dashed guide diamonds, no fill, no shape,
no points), and still lighter than any real plotted data.

Usage: python tools/patch_silhouette_contrast.py --dry-run | --write
"""
import argparse, pathlib, sys

CO = pathlib.Path('web/components/CondensedOutput.tsx')
EDITS = [
    ('        className="w-full h-auto opacity-60"\n',
     '        className="w-full h-auto opacity-70"\n', 'opacity 60 -> 70'),
    ('        <g stroke="#e5e7eb" strokeWidth="1" fill="none">\n',
     '        <g stroke="#9ca3af" strokeWidth="1" fill="none">\n', 'stroke #e5e7eb -> #9ca3af'),
]


def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args(); t = CO.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        if t.count(old) != 1:
            print(f'ERROR {label} x{t.count(old)}', file=sys.stderr); sys.exit(1)
        t = t.replace(old, new, 1); print(f'[{CO} :: {label}] OK')
    if a.dry_run:
        print('DRY RUN -- nothing written.'); return
    CO.write_text(t, encoding='utf-8'); print('WROTE', CO)


if __name__ == '__main__':
    main()
