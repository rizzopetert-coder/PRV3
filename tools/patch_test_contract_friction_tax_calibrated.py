"""
Fix a second, separate stale assertion in tools/test_contract.py --
unrelated to tonight's MC_CENTROID_39 work and to the descriptive_prose
fixture fix. private_output.friction_tax_estimate was asserted to be
None ("CALIBRATION TARGET" in the check's own name), written before
Friction Tax calibration was complete. Confirmed via direct call to
engine/friction_tax.py's compute_friction_tax() this session:
calibration_complete=True for the test's real scenario (the_unformed_
leader / Emerging / 250 headcount / Technology), so
engine/contract.py's assemble_output() now genuinely returns a real
{low, high, currency} dict, not None -- the test was never updated after
Friction Tax calibration (Sets 1-3) shipped.

Usage:
  python tools/patch_test_contract_friction_tax_calibrated.py --dry-run
  python tools/patch_test_contract_friction_tax_calibrated.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_CONTRACT_PATH = REPO_ROOT / "tools" / "test_contract.py"

OLD = (
    'check("private_output.friction_tax_estimate is None (CALIBRATION TARGET)",\n'
    '      priv["friction_tax_estimate"] is None)\n'
)

NEW = (
    '# Friction Tax calibration (Sets 1-3) is complete as of this session --\n'
    '# was previously asserted None ("CALIBRATION TARGET"); now checks the\n'
    '# real computed structure instead.\n'
    'fte = priv["friction_tax_estimate"]\n'
    'check("private_output.friction_tax_estimate is a calibrated {low, high, currency} dict",\n'
    '      isinstance(fte, dict)\n'
    '      and isinstance(fte.get("low"), (int, float))\n'
    '      and isinstance(fte.get("high"), (int, float))\n'
    '      and fte.get("low") <= fte.get("high")\n'
    '      and isinstance(fte.get("currency"), str),\n'
    '      f"got {fte!r}")\n'
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TEST_CONTRACT_PATH.read_text(encoding="utf-8")
    count = content.count(OLD)
    if count != 1:
        print(f"ABORT: expected exactly 1 match for anchor, found {count}")
        sys.exit(1)
    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print("=== tools/test_contract.py: 1 edit would apply cleanly ===")
    else:
        TEST_CONTRACT_PATH.write_text(new_content, encoding="utf-8")
        print("=== tools/test_contract.py: 1 edit written ===")


if __name__ == "__main__":
    main()
