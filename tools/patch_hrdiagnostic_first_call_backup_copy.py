"""
hr_diagnostic backup copy -- First Call (engine Intervention) entry reworded
per Pete, 2026-09-26: the old closing clause read as ominous rather than
urgent in a cold, unmediated context (no consultant present to soften it).
The other three hr_diagnostic entries are approved as written, unchanged.

Also pins the exact approved strings in tools/test_hr_diagnostic_brand.py
(the existing assertion only compared against the table, so it could not
catch a wording regression) and asserts the old clause is gone.

Usage:
    python tools/patch_hrdiagnostic_first_call_backup_copy.py --dry-run
    python tools/patch_hrdiagnostic_first_call_backup_copy.py --write
"""
import argparse
import pathlib
import sys

NEW_COPY = (
    "What the diagnostic found needs attention now, not later. HR Consulting can engage directly "
    "and help shape next steps before the situation develops further."
)

EDITS = [
    (pathlib.Path('engine/resolution_families.py'),
     '    "Intervention": (\n'
     '        "What the diagnostic found is active now and should not wait. HR Consulting engages directly "\n'
     '        "and promptly, while there is still room to shape the outcome."\n'
     '    ),\n',
     '    "Intervention": (\n'
     '        "What the diagnostic found needs attention now, not later. HR Consulting can engage directly "\n'
     '        "and help shape next steps before the situation develops further."\n'
     '    ),\n',
     'First Call backup copy'),
    (pathlib.Path('tools/test_hr_diagnostic_brand.py'),
     'check("urgency copy wins for any compound with Intervention",\n'
     '      get_fallback_synthesis(hr_diagnostic_synthesis_family("Executive Counsel + Intervention"), "Entrenched")["resolution_framing_text"]\n'
     '      == HR_DIAGNOSTIC_FALLBACK_COPY["Intervention"])\n',
     'check("urgency copy wins for any compound with Intervention",\n'
     '      get_fallback_synthesis(hr_diagnostic_synthesis_family("Executive Counsel + Intervention"), "Entrenched")["resolution_framing_text"]\n'
     '      == HR_DIAGNOSTIC_FALLBACK_COPY["Intervention"])\n'
     '\n'
     '# Exact approved wording (Pete, 2026-09-26) -- pinned so a wording\n'
     '# regression fails here, not just a table mismatch.\n'
     'APPROVED_HR_BACKUP_COPY = {\n'
     '    "Roadmap": "The conditions producing this live in how the organization is designed, not in the people working inside it. HR Consulting addresses that structure directly, targeted at what the diagnostic found rather than at the symptoms.",\n'
     '    "Development": "There is a capability gap. HR Consulting addresses it through Employee Training & Education and Learning & Development Consulting, built around the specific skills and practices the diagnostic identified.",\n'
     '    "Executive Counsel": "The decisions this situation requires sit at the leadership level. HR Consulting supports them through Employee Development, Coaching & Performance Management, with an outside perspective that is hard to get from inside the organization.",\n'
     '    "Intervention": "What the diagnostic found needs attention now, not later. HR Consulting can engage directly and help shape next steps before the situation develops further.",\n'
     '}\n'
     'for fam, want in APPROVED_HR_BACKUP_COPY.items():\n'
     '    check(f"backup copy for {fam} is the exact approved string", HR_DIAGNOSTIC_FALLBACK_COPY[fam] == want, HR_DIAGNOSTIC_FALLBACK_COPY[fam])\n'
     'check("Intervention compound backup renders the corrected First Call copy",\n'
     '      get_fallback_synthesis(hr_diagnostic_synthesis_family("Roadmap + Intervention"), "Endemic")["resolution_framing_text"]\n'
     '      == APPROVED_HR_BACKUP_COPY["Intervention"])\n'
     'check("old First Call closing clause is gone from every backup entry",\n'
     '      all("room to shape the outcome" not in c and "should not wait" not in c\n'
     '          for c in HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT.values()))\n',
     'pin approved strings'),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    if ';' in NEW_COPY or '—' in NEW_COPY:
        print('ERROR: new copy contains a semicolon or em-dash.', file=sys.stderr)
        sys.exit(1)

    edited = {}
    for path, old, new, label in EDITS:
        text = edited.get(path, path.read_text(encoding='utf-8'))
        count = text.count(old)
        if count != 1:
            print(f'ERROR: {path} :: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
            sys.exit(1)
        edited[path] = text.replace(old, new, 1)
        print(f'[{path} :: {label}]\nOLD:\n{old}\nNEW:\n{new}')

    if args.dry_run:
        print('DRY RUN -- all anchors found, all edits would apply cleanly. Nothing written.')
        return
    for path, text in edited.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
