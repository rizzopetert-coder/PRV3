"""
RESOLUTION_FALLBACK_COPY (PR backup copy), Pete-authored, 2026-09-27. One
commit, nine changes:
  - 2 new compound entries, the two families that had no authored backup
    copy and fell back to the generic text (surfaced once multi-state
    results started routing, 9c55695):
      ("People Tactics & Strategy + Executive Advisory", None)  4 states
      ("Executive Advisory + People Tactics & Strategy", None)  1 state
  - 7 existing entries: the " — " connective replaced per Pete's exact text.
Also: tools/test_hr_diagnostic_brand.py drops its PR_BACKUP_UNAUTHORED
special case (both compounds are now authored, so they must name a PR tier
like every other family), and tools/test_phase1_report_data.py gains a check
that no em-dash remains anywhere in RESOLUTION_FALLBACK_COPY.

The script edits by unique " — " fragment (several entries are split across
concatenated literals), then imports the edited module in a subprocess and
asserts every changed or new value equals Pete's exact string before writing.

Usage:
    python tools/patch_pr_backup_copy_compounds.py --dry-run
    python tools/patch_pr_backup_copy_compounds.py --write
"""
import argparse
import pathlib
import subprocess
import sys
import tempfile

RF = pathlib.Path('engine/resolution_families.py')
HT = pathlib.Path('tools/test_hr_diagnostic_brand.py')
PT = pathlib.Path('tools/test_phase1_report_data.py')

DASH_FIXES = [
    ('directly — expert', 'directly: expert'),
    ('structural redesign — expert', 'structural redesign: expert'),
    ('getting it right — available', 'getting it right, available'),
    # Split across two literals: "...is that read " + "— confidential, ..."
    ('that read "\n        "— confidential', 'that read"\n        ": confidential'),
    ('clarity possible — for', 'clarity possible: for'),
    ('follows — so what', 'follows, so what'),
    ('follows — because', 'follows, because'),
]

NEW_ENTRIES_ANCHOR = (
    '    ("Training & Development + First Call", None): (\n'
    '        "First Call addresses what is live. Training & Development addresses what the organization needs to be "\n'
    '        "able to do once it is through."\n'
    '    ),\n'
    '}\n'
)
NEW_ENTRIES = (
    '    ("Training & Development + First Call", None): (\n'
    '        "First Call addresses what is live. Training & Development addresses what the organization needs to be "\n'
    '        "able to do once it is through."\n'
    '    ),\n'
    '    # Pete-authored 2026-09-27: the two compounds that had no backup copy.\n'
    '    ("People Tactics & Strategy + Executive Advisory", None): (\n'
    '        "People Tactics & Strategy redesigns the structure behind this. Executive Advisory gives you a "\n'
    '        "confidential, outside read on leading through it."\n'
    '    ),\n'
    '    ("Executive Advisory + People Tactics & Strategy", None): (\n'
    '        "Executive Advisory gives you clarity on what leading through this actually requires. People Tactics & "\n'
    '        "Strategy addresses the structure underneath it."\n'
    '    ),\n'
    '}\n'
)

EXPECTED = {
    ("People Tactics & Strategy + Executive Advisory", None):
        "People Tactics & Strategy redesigns the structure behind this. Executive Advisory gives you a confidential, outside read on leading through it.",
    ("Executive Advisory + People Tactics & Strategy", None):
        "Executive Advisory gives you clarity on what leading through this actually requires. People Tactics & Strategy addresses the structure underneath it.",
    ("People Tactics & Strategy", "Entrenched"):
        "The conditions producing this live in how your organization is designed, not in the people navigating it. People Tactics & Strategy addresses that level directly: expert, targeted, and aimed at the architecture rather than the symptoms.",
    ("People Tactics & Strategy", "Endemic"):
        "When a condition becomes the environment, adjusting what happens inside it is not enough. People Tactics & Strategy is the structural redesign: expert work at the level where the problem actually lives.",
    ("Executive Advisory", "Emerging"):
        "Yes, it is what it sounds like. A confidential relationship with someone who has no stake in the outcome except getting it right, available before you need it urgently.",
    ("Executive Advisory", "Entrenched"):
        "The honest read on your situation is not available inside the building. Executive Advisory is that read: confidential, direct, and without the organizational politics attached to every word.",
    ("Executive Advisory", "Endemic"):
        "When you are close enough to something long enough, you lose the ability to see it clearly. Executive Advisory is the ongoing relationship that makes clarity possible: for the decisions that matter most and cannot be discussed with anyone inside the organization.",
    ("First Call + People Tactics & Strategy", None):
        "First Call handles what is active. People Tactics & Strategy follows, so what produced it does not reassemble.",
    ("People Tactics & Strategy + Training & Development", None):
        "People Tactics & Strategy redesigns the environment. Training & Development follows, because capability built inside a broken structure does not hold.",
}

HT_EDITS = [
    ('# Compound families with no authored PR backup copy (2026-09-27, logged for\n'
     '# Pete to author): their fallback is the generic copy, which names no tier.\n'
     'PR_BACKUP_UNAUTHORED = {"Roadmap + Executive Counsel", "Executive Counsel + Roadmap"}\n'
     '\n', '', 'drop unauthored set'),
    ('        if routing in PR_BACKUP_UNAUTHORED:\n'
     '            check(f"[{routing}] PR default uses the generic copy (no authored compound copy yet)",\n'
     '                  not any(t in ps["resolution_framing_text"] for t in PR_TERMS[:4]))\n'
     '        else:\n'
     '            check(f"[{routing}] PR default still names a PR tier", any(t in ps["resolution_framing_text"] for t in PR_TERMS[:4]))\n',
     '        check(f"[{routing}] PR default still names a PR tier", any(t in ps["resolution_framing_text"] for t in PR_TERMS[:4]))\n',
     'restore plain check'),
]

PT_TEST = '''
# ── 11. PR backup copy: every family authored, no em-dashes ─────────────────────
from engine.resolution_families import RESOLUTION_FALLBACK_COPY, translate_resolution_family
from engine.data.states import STATE_PROFILES as _SP2
# Four single-service entries still carry " — " (not in the 2026-09-27 fix
# list, flagged to Pete for copy). Any other em-dash is a regression.
_DASH_KNOWN = {("Training & Development", "Emerging"), ("Training & Development", "Entrenched"),
               ("First Call", "Emerging"), ("First Call", "Endemic")}
check("no em-dash in RESOLUTION_FALLBACK_COPY beyond the 4 flagged entries",
      {k for k, v in RESOLUTION_FALLBACK_COPY.items() if "\\u2014" in v} <= _DASH_KNOWN,
      str(sorted({k for k, v in RESOLUTION_FALLBACK_COPY.items() if "\\u2014" in v} - _DASH_KNOWN)))
_compounds = {translate_resolution_family(p.resolution_family) for p in _SP2.values() if " + " in p.resolution_family}
check("every compound family in the taxonomy has authored PR backup copy",
      all((c, None) in RESOLUTION_FALLBACK_COPY for c in _compounds),
      str(sorted(c for c in _compounds if (c, None) not in RESOLUTION_FALLBACK_COPY)))
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    rf = RF.read_text(encoding='utf-8')
    for old, new in DASH_FIXES:
        if rf.count(old) != 1:
            print(f'ERROR: fragment x{rf.count(old)}: {old!r}', file=sys.stderr)
            sys.exit(1)
        rf = rf.replace(old, new, 1)
        print(f'[{RF} :: {old!r} -> {new!r}] OK')
    if rf.count(NEW_ENTRIES_ANCHOR) != 1:
        print('ERROR: new-entry anchor not found once.', file=sys.stderr)
        sys.exit(1)
    rf = rf.replace(NEW_ENTRIES_ANCHOR, NEW_ENTRIES, 1)
    print(f'[{RF} :: 2 new compound entries] OK')

    # Verify the edited module's actual values against Pete's exact text.
    with tempfile.TemporaryDirectory() as td:
        pkg = pathlib.Path(td) / 'engine'
        pkg.mkdir()
        (pkg / '__init__.py').write_text('', encoding='utf-8')
        (pkg / 'resolution_families.py').write_text(rf, encoding='utf-8')
        code = (
            'import json, sys\n'
            f'sys.path.insert(0, {td!r})\n'
            'import importlib.util\n'
            f'spec = importlib.util.spec_from_file_location("rf_check", {str(pkg / "resolution_families.py")!r})\n'
            'm = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n'
            'print(json.dumps({"|".join(str(x) for x in k): v for k, v in m.RESOLUTION_FALLBACK_COPY.items()}))\n'
        )
        out = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, encoding='utf-8',
                             cwd=str(pathlib.Path.cwd()))
        if out.returncode != 0:
            print('ERROR importing edited module:\n' + out.stderr, file=sys.stderr)
            sys.exit(1)
        import json
        table = json.loads(out.stdout)
    bad = []
    for key, text in EXPECTED.items():
        got = table.get("|".join(str(x) for x in key))
        if got != text:
            bad.append((key, got))
    changed_dashes = [k for k in EXPECTED if '—' in table.get("|".join(str(x) for x in k), '')]
    if bad or changed_dashes:
        print(f'ERROR: mismatches {bad} dashes in changed entries {changed_dashes}', file=sys.stderr)
        sys.exit(1)
    remaining = sorted(k for k, v in table.items() if '—' in v)
    print(f'[verify] all 9 values match exactly. Entries still carrying an em-dash '
          f'(not in the fix list, flagged): {remaining}')

    ht = HT.read_text(encoding='utf-8')
    for old, new, label in HT_EDITS:
        if ht.count(old) != 1:
            print(f'ERROR: {HT} :: {label} x{ht.count(old)}', file=sys.stderr)
            sys.exit(1)
        ht = ht.replace(old, new, 1)
        print(f'[{HT} :: {label}] OK')
    pt = PT.read_text(encoding='utf-8')
    i = pt.index('RESULT: {passed} passed')
    ls = pt.rindex('\n', 0, i) + 1
    pt = pt[:ls] + PT_TEST.lstrip('\n') + '\n' + pt[ls:]
    print(f'[{PT} :: backup copy checks] OK')

    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    RF.write_text(rf, encoding='utf-8')
    HT.write_text(ht, encoding='utf-8')
    PT.write_text(pt, encoding='utf-8')
    print('WROTE')


if __name__ == '__main__':
    main()
