"""
web/context/SelfSelectionContext.tsx: add assemblyTriggerHeight state +
setAssemblyTriggerHeight action.

Fix for the mobile Phase 2 collision (AssemblyPanel's fixed bottom-0 z-40
Drawer.Trigger fully covering the Phase 2 transition bar's z-30 CTA,
confirmed live via elementFromPoint() returning the trigger, not the
CTA, at the CTA's own center point). AssemblyPanel measures its own
trigger's real rendered height via ResizeObserver and publishes it here;
page.tsx reads it back to offset the Phase 2 bar's bottom position by
that live measurement, not a hardcoded pixel value -- so the fix stays
correct if the trigger's copy or padding changes later.

Uses the existing state-plus-setter pattern already in this context
(mirrors setActiveSheet) rather than introducing a new mechanism
(callback prop, separate context, etc).

Usage:
    python tools/patch_assembly_trigger_height_context.py --dry-run
    python tools/patch_assembly_trigger_height_context.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/context/SelfSelectionContext.tsx')

STATE_OLD = '''interface SelfSelectionState {
  selectedStateIds: Set<string>;
  selectedSignatureIds: Set<string>;
  // 'assembly' | signatureId | null
  activeSheet: string | null;
}

interface SelfSelectionActions {
  toggleState: (stateId: string, signatureId: string) => void;
  toggleSignature: (signatureId: string, stateIds: string[]) => void;
  setActiveSheet: (sheet: string | null) => void;
  clearAll: () => void;
}'''

STATE_NEW = '''interface SelfSelectionState {
  selectedStateIds: Set<string>;
  selectedSignatureIds: Set<string>;
  // 'assembly' | signatureId | null
  activeSheet: string | null;
  // Live rendered height (px) of AssemblyPanel's mobile Drawer.Trigger,
  // measured via ResizeObserver. Used by the Phase 2 transition bar to
  // offset its own bottom position so the two fixed bars stack instead
  // of overlapping. 0 when the trigger isn't rendered (desktop, or
  // AssemblyPanel unmounted).
  assemblyTriggerHeight: number;
}

interface SelfSelectionActions {
  toggleState: (stateId: string, signatureId: string) => void;
  toggleSignature: (signatureId: string, stateIds: string[]) => void;
  setActiveSheet: (sheet: string | null) => void;
  setAssemblyTriggerHeight: (height: number) => void;
  clearAll: () => void;
}'''

PROVIDER_OLD = '''  const [activeSheet, setActiveSheetState] = useState<string | null>(null);'''

PROVIDER_NEW = '''  const [activeSheet, setActiveSheetState] = useState<string | null>(null);
  const [assemblyTriggerHeight, setAssemblyTriggerHeightState] = useState<number>(0);'''

SETTER_OLD = '''  const setActiveSheet = useCallback((sheet: string | null) => {
    setActiveSheetState(sheet);
  }, []);'''

SETTER_NEW = '''  const setActiveSheet = useCallback((sheet: string | null) => {
    setActiveSheetState(sheet);
  }, []);

  const setAssemblyTriggerHeight = useCallback((height: number) => {
    setAssemblyTriggerHeightState(height);
  }, []);'''

VALUE_OLD = '''      selectedStateIds,
      selectedSignatureIds,
      activeSheet,
      toggleState,
      toggleSignature,
      setActiveSheet,
      clearAll,
    }}>'''

VALUE_NEW = '''      selectedStateIds,
      selectedSignatureIds,
      activeSheet,
      assemblyTriggerHeight,
      toggleState,
      toggleSignature,
      setActiveSheet,
      setAssemblyTriggerHeight,
      clearAll,
    }}>'''

EDITS = [
    ('state/actions interfaces', STATE_OLD, STATE_NEW),
    ('provider useState', PROVIDER_OLD, PROVIDER_NEW),
    ('setAssemblyTriggerHeight callback', SETTER_OLD, SETTER_NEW),
    ('provider value object', VALUE_OLD, VALUE_NEW),
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
