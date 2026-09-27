"""
Intake "Other" significant-event textarea loses focus on every keystroke
(Pete, 2026-09-27 bug report 4, functional blocker).

Root cause: SignificantEventsField was declared INSIDE IntakeForm's body.
Every keystroke calls onChange -> DiagnosticFlow's setIntake -> IntakeForm
re-renders -> a brand-new SignificantEventsField function is created ->
React sees a different component type at that position and unmounts and
remounts the whole subtree, textarea included, so focus is lost after one
character.

Fix: hoist SignificantEventsField, unchanged apart from indentation, to
module scope directly above IntakeForm. It only closes over its own props
and the module-level SIGNIFICANT_EVENT_OPTIONS, so no behavior changes.
A codebase scan found no other component declared inside a component.

Usage:
    python tools/patch_intake_other_field_focus.py --dry-run
    python tools/patch_intake_other_field_focus.py --write
"""
import argparse
import pathlib
import sys

P = pathlib.Path('web/components/DiagnosticFlow.tsx')
BLOCK_START = '  // None/other-events mutual exclusivity: checking "none" clears any other\n'
BLOCK_END_MARKER = '\n  return (\n    <div className="max-w-md mx-auto px-6 py-16">\n'
INSERT_BEFORE = '// ── Intake form ─'
HOIST_NOTE = (
    '// Module scope, not nested inside IntakeForm: a component declared inside\n'
    '// another component\'s body gets a new identity on every render, so React\n'
    '// remounts it and the "Other" textarea lost focus after each keystroke.\n'
)


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    text = P.read_text(encoding='utf-8')
    for anchor, label in ((BLOCK_START, 'block start'), (BLOCK_END_MARKER, 'block end'), (INSERT_BEFORE, 'insert point')):
        if text.count(anchor) != 1:
            print(f'ERROR: {label} found {text.count(anchor)} times.', file=sys.stderr)
            sys.exit(1)
    start = text.index(BLOCK_START)
    end = text.index(BLOCK_END_MARKER)
    block = text[start:end]
    if not block.rstrip().endswith('  }') or 'function SignificantEventsField' not in block:
        print('ERROR: extracted block has an unexpected shape.', file=sys.stderr)
        sys.exit(1)
    lines = block.rstrip('\n').split('\n')
    if any(l and not l.startswith('  ') for l in lines):
        print('ERROR: a block line is not indented by 2 spaces.', file=sys.stderr)
        sys.exit(1)
    dedented = '\n'.join(l[2:] if l else l for l in lines) + '\n'
    # remove from IntakeForm (and the blank line before `return (`)
    text = text[:start] + text[end + 1:]
    ins = text.index(INSERT_BEFORE)
    text = text[:ins] + HOIST_NOTE + dedented + '\n' + text[ins:]
    print(f'[{P}] SignificantEventsField hoisted to module scope ({len(lines)} lines) OK')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    P.write_text(text, encoding='utf-8')
    print(f'WROTE: {P}')


if __name__ == '__main__':
    main()
