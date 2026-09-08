"""
web/components/DiagnosticFlow.tsx: export HeadcountStepper and
JURISDICTION_OPTIONS for reuse by SelfSelectIntakeModal.tsx. Same
reuse rationale INDUSTRY_OPTIONS already carries (its own export
comment, just above JURISDICTION_OPTIONS) -- the exact same real
options a respondent already sees here, not a second hand-maintained
list.

Usage:
    python tools/patch_export_headcount_stepper_jurisdiction_options.py --dry-run
    python tools/patch_export_headcount_stepper_jurisdiction_options.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/components/DiagnosticFlow.tsx')

OLD_STEPPER = '''// Hoisted to module scope (was nested inside IntakeForm) -- a nested
// function component is redeclared on every parent render, which made
// React remount this <input> (destroying and recreating the DOM node)
// on every keystroke, racing against the browser's native input
// handling. Closes over nothing from IntakeForm's scope (HEADCOUNT_MAX
// and stepHeadcount are already module-level), so hoisting is a pure
// move, zero logic change.
function HeadcountStepper({'''

NEW_STEPPER = '''// Hoisted to module scope (was nested inside IntakeForm) -- a nested
// function component is redeclared on every parent render, which made
// React remount this <input> (destroying and recreating the DOM node)
// on every keystroke, racing against the browser's native input
// handling. Closes over nothing from IntakeForm's scope (HEADCOUNT_MAX
// and stepHeadcount are already module-level), so hoisting is a pure
// move, zero logic change.
//
// Exported for reuse by SelfSelectIntakeModal.tsx (self-select flow
// headcount collection) -- the exact same increment schedule and input
// handling, not a second hand-maintained stepper.
export function HeadcountStepper({'''

OLD_JURISDICTIONS = '''const JURISDICTION_OPTIONS = [
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
  "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
  "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
  "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
  "WV", "WI", "WY",
];'''

NEW_JURISDICTIONS = '''// Exported for reuse by SelfSelectIntakeModal.tsx -- same rationale as
// INDUSTRY_OPTIONS's own export comment above: the exact same 51 real
// jurisdiction codes a respondent already sees here, not a second
// hand-maintained list that could drift.
export const JURISDICTION_OPTIONS = [
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI",
  "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN",
  "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH",
  "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA",
  "WV", "WI", "WY",
];'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    errors = []
    for label, old in [('HeadcountStepper', OLD_STEPPER), ('JURISDICTION_OPTIONS', OLD_JURISDICTIONS)]:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')
    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(OLD_STEPPER, NEW_STEPPER, 1).replace(OLD_JURISDICTIONS, NEW_JURISDICTIONS, 1)

    if args.dry_run:
        print('DRY RUN -- both anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
