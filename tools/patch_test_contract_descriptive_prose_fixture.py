"""
Fix a pre-existing test-fixture gap in tools/test_contract.py's
make_output() helper -- confirmed via git blame this session (line dates
to d35ca68, 2026-05-04, untouched since, unrelated to tonight's
MC_CENTROID_39 work): its synthetic identified_states entry never
included "descriptive_prose", which engine/contract.py's real
identified_states validation checks for. Surfaced this session only
because the S27 harness's baseline test-suite check is being run for the
first time in a long while.

Usage:
  python tools/patch_test_contract_descriptive_prose_fixture.py --dry-run
  python tools/patch_test_contract_descriptive_prose_fixture.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_CONTRACT_PATH = REPO_ROOT / "tools" / "test_contract.py"

OLD = (
    '    d["identified_states"] = [{"state_id": rank1_state, "state_name": "X",\n'
    '                                "score": 0.9, "distinguishing_language": None}]\n'
)

NEW = (
    '    d["identified_states"] = [{"state_id": rank1_state, "state_name": "X",\n'
    '                                "score": 0.9, "distinguishing_language": None,\n'
    '                                "descriptive_prose": "Test descriptive prose."}]\n'
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
