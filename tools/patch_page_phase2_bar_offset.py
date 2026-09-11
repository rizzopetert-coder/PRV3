"""
web/app/diagnostic/page.tsx: offset the Phase 2 transition bar's bottom
position by AssemblyPanel's live-measured mobile trigger height.

Completes the mobile Phase 2 collision fix (see
tools/patch_assembly_trigger_height_context.py and
tools/patch_assembly_panel_trigger_height.py for the other two
pieces). Only the Phase 2 bar (showPhase2Bar, i.e. currentPhase === 2,
the only phase where AssemblyPanel's mobile trigger renders
simultaneously) gets the offset -- Phase 1's bar (showPhase1Bar) is
untouched, since AssemblyPanel doesn't render before currentPhase 2 and
has no collision to fix.

assemblyTriggerHeight is 0 whenever the mobile trigger isn't actually
rendered (desktop, where it's `md:hidden`), so the inline style is a
no-op there -- the existing `bottom-0` Tailwind class already covers
that case, inline style just overrides it to the same effective value
when the measured height is 0.

Usage:
    python tools/patch_page_phase2_bar_offset.py --dry-run
    python tools/patch_page_phase2_bar_offset.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/app/diagnostic/page.tsx')

DESTRUCTURE_OLD = '''  const { selectedStateIds, selectedSignatureIds } = useSelfSelection();'''

DESTRUCTURE_NEW = '''  const { selectedStateIds, selectedSignatureIds, assemblyTriggerHeight } = useSelfSelection();'''

BAR_OLD = '''      {/* Phase 2 → Phase 3 transition bar */}
      {showPhase2Bar && (
        <div className="fixed bottom-0 left-0 right-0 z-30 bg-white border-t border-gray-200 px-6 py-4 flex justify-between items-center animate-fade-up">'''

BAR_NEW = '''      {/* Phase 2 → Phase 3 transition bar */}
      {showPhase2Bar && (
        <div
          className="fixed bottom-0 left-0 right-0 z-30 bg-white border-t border-gray-200 px-6 py-4 flex justify-between items-center animate-fade-up"
          style={{ bottom: assemblyTriggerHeight }}
        >'''

EDITS = [
    ('destructure assemblyTriggerHeight', DESTRUCTURE_OLD, DESTRUCTURE_NEW),
    ('Phase 2 bar bottom offset', BAR_OLD, BAR_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
