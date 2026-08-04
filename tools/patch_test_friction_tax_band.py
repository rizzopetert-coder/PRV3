"""
PRV3 -- Add a "band" key to the 13 compute_legal_compliance_exposure()
assertions in tools/test_friction_tax.py, matching the new
_legal_exposure_band() output added to all three of that function's
return paths.

Usage:
  python tools/patch_test_friction_tax_band.py --dry-run
  python tools/patch_test_friction_tax_band.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


TEST_FILE = "tools/test_friction_tax.py"

edit(
    TEST_FILE,
    '        "low": 50_000.0, "high": 50_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": 50_000.0, "high": 50_000.0, "currency": "USD", "band": "Minor",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": _expected_cross, "high": _expected_cross, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": _expected_cross, "high": _expected_cross, "currency": "USD", "band": "Moderate",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": _expected_decay, "high": _expected_decay, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": _expected_decay, "high": _expected_decay, "currency": "USD", "band": "Moderate",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": 25_000.0, "high": 31_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": 25_000.0, "high": 31_000.0, "currency": "USD", "band": "Minor",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": 1_800.0, "high": 2_500.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": 1_800.0, "high": 2_500.0, "currency": "USD", "band": "Minor",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": _co_expected_low, "high": _co_expected_high, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": _co_expected_low, "high": _co_expected_high, "currency": "USD", "band": "Moderate",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": 33_000_000.0, "high": 33_000_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": 33_000_000.0, "high": 33_000_000.0, "currency": "USD", "band": "Significant",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": 200_000.0, "high": 200_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": 200_000.0, "high": 200_000.0, "currency": "USD", "band": "Moderate",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": 25_000.0, "high": 25_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '        "low": 25_000.0, "high": 25_000.0, "currency": "USD", "band": "Minor",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '        "low": None, "high": None, "currency": "USD",\n'
    '        "has_unpriced_conditions": True, "unpriced_state_ids": ["hr_capture"],',
    '        "low": None, "high": None, "currency": "USD", "band": None,\n'
    '        "has_unpriced_conditions": True, "unpriced_state_ids": ["hr_capture"],',
)
edit(
    TEST_FILE,
    '    _r_never_classified == {\n'
    '        "low": None, "high": None, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '    _r_never_classified == {\n'
    '        "low": None, "high": None, "currency": "USD", "band": None,\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '    _r_zero_score == {\n'
    '        "low": None, "high": None, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '    _r_zero_score == {\n'
    '        "low": None, "high": None, "currency": "USD", "band": None,\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)
edit(
    TEST_FILE,
    '    == {\n'
    '        "low": None, "high": None, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
    '    == {\n'
    '        "low": None, "high": None, "currency": "USD", "band": None,\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
