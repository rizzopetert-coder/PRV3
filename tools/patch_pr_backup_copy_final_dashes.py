"""
RESOLUTION_FALLBACK_COPY: the last four em-dashes (Pete's exact text,
2026-09-27). After this the table has zero em-dashes, and the table check in
tools/test_phase1_report_data.py drops its four named exceptions: any
em-dash anywhere in the table now fails the suite.

Two of the four strings straddle concatenated literals ("...that presence "
+ "— engaged..."), so the edit is by fragment, and the edited module is then
imported and every changed value checked against Pete's exact text before
anything is written.

Usage:
    python tools/patch_pr_backup_copy_final_dashes.py --dry-run
    python tools/patch_pr_backup_copy_final_dashes.py --write
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

RF = pathlib.Path('engine/resolution_families.py')
PT = pathlib.Path('tools/test_phase1_report_data.py')

FRAGMENTS = [
    ('addresses it directly — not off-the-shelf', 'addresses it directly: not off-the-shelf'),
    ('works against that — targeted', 'works against that: targeted'),
    ('First Call is that presence "\n        "— engaged',
     'First Call is that presence"\n        ": engaged'),
    ('immersive engagement "\n        "— inside',
     'immersive engagement"\n        ": inside'),
]

EXPECTED = {
    ("Training & Development", "Emerging"):
        "There is a capability gap. Training & Development addresses it directly: not off-the-shelf training, but targeted work on the specific skills and practices the diagnostic identified.",
    ("Training & Development", "Entrenched"):
        "The gap has had time to become normal. Training & Development works against that: targeted, practical, and built around what your people actually need to be able to do, not a general program applied to a specific problem.",
    ("First Call", "Emerging"):
        "The situation requires someone in it, not advising from outside it. First Call is that presence: engaged with what is happening while there is still room to shape it.",
    ("First Call", "Endemic"):
        "This does not respond to a plan or a program. First Call is direct, immersive engagement: inside the situation, not above it, for as long as it takes.",
}

PT_OLD = (
    '# Four single-service entries still carry " — " (not in the 2026-09-27 fix\n'
    '# list, flagged to Pete for copy). Any other em-dash is a regression.\n'
    '_DASH_KNOWN = {("Training & Development", "Emerging"), ("Training & Development", "Entrenched"),\n'
    '               ("First Call", "Emerging"), ("First Call", "Endemic")}\n'
    'check("no em-dash in RESOLUTION_FALLBACK_COPY beyond the 4 flagged entries",\n'
    '      {k for k, v in RESOLUTION_FALLBACK_COPY.items() if "\\u2014" in v} <= _DASH_KNOWN,\n'
    '      str(sorted({k for k, v in RESOLUTION_FALLBACK_COPY.items() if "\\u2014" in v} - _DASH_KNOWN)))\n'
)
PT_NEW = (
    '# Zero exceptions since 2026-09-27 (Pete\'s final four fixes).\n'
    'check("no em-dash anywhere in RESOLUTION_FALLBACK_COPY",\n'
    '      not [k for k, v in RESOLUTION_FALLBACK_COPY.items() if "\\u2014" in v],\n'
    '      str(sorted(k for k, v in RESOLUTION_FALLBACK_COPY.items() if "\\u2014" in v)))\n'
)


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    rf = RF.read_text(encoding='utf-8')
    for old, new in FRAGMENTS:
        if rf.count(old) != 1:
            print(f'ERROR: fragment x{rf.count(old)}: {old!r}', file=sys.stderr)
            sys.exit(1)
        rf = rf.replace(old, new, 1)
        print(f'[{RF} :: {old!r}] OK')

    with tempfile.TemporaryDirectory() as td:
        path = pathlib.Path(td) / 'rf_check.py'
        path.write_text(rf, encoding='utf-8')
        code = (
            'import json, importlib.util\n'
            f'spec = importlib.util.spec_from_file_location("rf_check", {str(path)!r})\n'
            'm = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n'
            'print(json.dumps({"|".join(str(x) for x in k): v for k, v in m.RESOLUTION_FALLBACK_COPY.items()}))\n'
        )
        out = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True,
                             encoding='utf-8', cwd=str(pathlib.Path.cwd()))
        if out.returncode != 0:
            print('ERROR importing edited module:\n' + out.stderr, file=sys.stderr)
            sys.exit(1)
        table = json.loads(out.stdout)
    bad = [k for k, v in EXPECTED.items() if table.get('|'.join(str(x) for x in k)) != v]
    dashes = [k for k, v in table.items() if '—' in v]
    if bad or dashes:
        print(f'ERROR: mismatches {bad}, em-dashes left {dashes}', file=sys.stderr)
        sys.exit(1)
    print(f'[verify] all 4 values match exactly, zero em-dashes across {len(table)} entries')

    pt = PT.read_text(encoding='utf-8')
    if pt.count(PT_OLD) != 1:
        print(f'ERROR: test block x{pt.count(PT_OLD)}', file=sys.stderr)
        sys.exit(1)
    pt = pt.replace(PT_OLD, PT_NEW, 1)
    print(f'[{PT} :: zero-exception em-dash check] OK')

    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    RF.write_text(rf, encoding='utf-8')
    PT.write_text(pt, encoding='utf-8')
    print('WROTE')


if __name__ == '__main__':
    main()
