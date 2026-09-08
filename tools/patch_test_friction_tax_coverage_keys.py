"""
tools/test_friction_tax.py: add coverage_basis/has_partial_jurisdictions
to the 20 dict-equality fixtures that predate compute_legal_compliance_
exposure()'s two new return keys. Values below were confirmed by hand
against each test's actual computed output (test_friction_tax.py run
with the coverage_confidence changes applied, before this patch) --
not guessed. Line numbers verified against current source immediately
before writing this script; each line's exact current text is checked
before replacement, so a mismatch aborts rather than silently
mispatching.

Touches ONLY these 20 lines' trailing comma + new keys. No other test
logic changed.

Usage:
    python tools/patch_test_friction_tax_coverage_keys.py --dry-run
    python tools/patch_test_friction_tax_coverage_keys.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/test_friction_tax.py')

# (line number [1-indexed], exact expected current line content,
#  coverage_basis value as it should appear in source, has_partial_jurisdictions)
EDITS = [
    (843,  '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "federal_baseline", False),
    (866,  '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "federal_baseline", False),
    (888,  '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "federal_baseline", False),
    (906,  '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "federal_baseline", False),
    (920,  '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "federal_baseline", False),
    (949,  '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (967,  '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (981,  '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "federal_baseline", False),
    (1001, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "federal_baseline", False),
    (1016, '        "has_unpriced_conditions": True, "unpriced_state_ids": ["hr_capture"],\n', None, False),
    (1034, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (1056, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (1067, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (1361, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (1376, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "federal_baseline", False),
    (1390, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (1405, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (1420, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', None, False),
    (1435, '        "has_unpriced_conditions": True, "unpriced_state_ids": ["hr_capture"],\n', None, False),
    (1451, '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n', "state_specific", False),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    lines = PATH.read_text(encoding='utf-8').splitlines(keepends=True)

    errors = []
    new_lines_preview = []
    for lineno, expected, coverage_basis, has_partial in EDITS:
        idx = lineno - 1
        actual = lines[idx]
        if actual != expected:
            errors.append(
                f'Line {lineno}: expected {expected!r}, found {actual!r}. Aborting.'
            )
            continue
        cb_repr = 'None' if coverage_basis is None else f'"{coverage_basis}"'
        new_line = actual.rstrip('\n').rstrip() + \
            f' "coverage_basis": {cb_repr}, "has_partial_jurisdictions": {has_partial},\n'
        new_lines_preview.append((lineno, new_line))

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} target lines matched expected content exactly.')
        for lineno, new_line in new_lines_preview:
            print(f'  line {lineno} -> {new_line.rstrip()}')
    else:
        for lineno, new_line in new_lines_preview:
            lines[lineno - 1] = new_line
        PATH.write_text(''.join(lines), encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} lines updated.')


if __name__ == '__main__':
    main()
