"""
web/components/AssemblyPanel.tsx: measure the mobile Drawer.Trigger's
real rendered height via ref + ResizeObserver, publish it to
SelfSelectionContext via setAssemblyTriggerHeight.

Part of the mobile Phase 2 collision fix (see
tools/patch_assembly_trigger_height_context.py for the context-side
half). Uses getBoundingClientRect() rather than ResizeObserver's own
contentRect, since contentRect is content-box only (excludes the
trigger's own padding/border) and the Phase 2 bar needs the full
border-box height to clear it without a gap.

Height resets to 0 on unmount so a stale measurement can't linger in
context if AssemblyPanel unmounts (leaving Phase 2-4 range) and later
remounts.

Usage:
    python tools/patch_assembly_panel_trigger_height.py --dry-run
    python tools/patch_assembly_panel_trigger_height.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/components/AssemblyPanel.tsx')

IMPORT_OLD = '''"use client";

import { Drawer } from "vaul";
import { signatures, getStatesForSignature } from "@/data/taxonomy";
import { useSelfSelection } from "@/context/SelfSelectionContext";'''

IMPORT_NEW = '''"use client";

import { useEffect, useRef } from "react";
import { Drawer } from "vaul";
import { signatures, getStatesForSignature } from "@/data/taxonomy";
import { useSelfSelection } from "@/context/SelfSelectionContext";'''

BODY_OLD = '''export default function AssemblyPanel() {
  const { selectedStateIds, activeSheet, setActiveSheet } = useSelfSelection();
  const count = selectedStateIds.size;

  return ('''

BODY_NEW = '''export default function AssemblyPanel() {
  const { selectedStateIds, activeSheet, setActiveSheet, setAssemblyTriggerHeight } =
    useSelfSelection();
  const count = selectedStateIds.size;
  const triggerRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const el = triggerRef.current;
    if (!el) return;

    const observer = new ResizeObserver(() => {
      setAssemblyTriggerHeight(el.getBoundingClientRect().height);
    });
    observer.observe(el);

    return () => {
      observer.disconnect();
      setAssemblyTriggerHeight(0);
    };
  }, [setAssemblyTriggerHeight]);

  return ('''

TRIGGER_OLD = '''          <Drawer.Trigger asChild>
            <button
              onClick={() => setActiveSheet("assembly")}
              className="fixed bottom-0 left-0 right-0 z-40 bg-paper border-t border-gray-200 px-5 py-4 flex items-center justify-between text-sm font-medium text-charcoal"
            >'''

TRIGGER_NEW = '''          <Drawer.Trigger asChild>
            <button
              ref={triggerRef}
              onClick={() => setActiveSheet("assembly")}
              className="fixed bottom-0 left-0 right-0 z-40 bg-paper border-t border-gray-200 px-5 py-4 flex items-center justify-between text-sm font-medium text-charcoal"
            >'''

EDITS = [
    ('react hooks import', IMPORT_OLD, IMPORT_NEW),
    ('ref + ResizeObserver setup', BODY_OLD, BODY_NEW),
    ('ref attached to trigger button', TRIGGER_OLD, TRIGGER_NEW),
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
