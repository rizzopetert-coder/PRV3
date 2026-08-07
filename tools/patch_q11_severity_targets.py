"""
PRV3 Calibration Harness Patch -- add SEVER-20 to EXP-MAF-02/EXP-MAF-03/
EXP-CO-01/EXP-MAF-01's _SEVERITY_FOLLOW_ON_TARGETS entries.

Confirmed empirically (Track A / ALL-FR-01 / Q02 / Q18 / Q14 / Q19 / Q33
precedent) that content alone changes nothing -- generate_answers()'s
splice is gated by this table. EXP-MAF-02, EXP-MAF-03, EXP-CO-01 are all
single-trigger Entrenched-expected, closed by this alone. EXP-MAF-01 is
Endemic-expected and genuinely needs a second trigger (no candidate
identified, separate future work, not part of this fix) -- correctly
lands short at Entrenched (raw 2.00), not a bug. culture_drift,
the_wrong_reward, the_inside_track, the_arbitrary_standard,
the_basement_standard, and the_broken_compass are deliberately NOT
added -- all six are out of scope for this fix and must stay
unaffected.

Usage:
  python tools/patch_q11_severity_targets.py --dry-run
  python tools/patch_q11_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = (
    '    "AUT-IA-01":  {"SEVER-19": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},'
)

NEW = (
    '    "AUT-IA-01":  {"SEVER-19": "18mo_plus"},\n'
    '    # Q11/D second trigger (motivational_architecture_failure /\n'
    '    # cultural_overtime) -- EXP-MAF-02, EXP-MAF-03, EXP-CO-01 are\n'
    '    # single-trigger Entrenched-expected, closed by this alone.\n'
    '    # EXP-MAF-01 is Endemic-expected and genuinely needs a second\n'
    '    # trigger (no candidate identified, separate future work, not\n'
    '    # part of this fix) -- correctly lands short at Entrenched (raw\n'
    '    # 2.00), not a bug. culture_drift, the_wrong_reward,\n'
    '    # the_inside_track, the_arbitrary_standard, the_basement_standard,\n'
    '    # and the_broken_compass are deliberately NOT added -- out of\n'
    '    # scope for this fix, must stay unaffected.\n'
    '    "EXP-MAF-01": {"SEVER-20": "18mo_plus"},\n'
    '    "EXP-MAF-02": {"SEVER-20": "18mo_plus"},\n'
    '    "EXP-MAF-03": {"SEVER-20": "18mo_plus"},\n'
    '    "EXP-CO-01":  {"SEVER-20": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},'
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TARGET.read_text(encoding="utf-8")
    count = content.count(OLD)
    if count != 1:
        print(f"ABORT: expected exactly 1 match, found {count}")
        sys.exit(1)
    content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print("=== 1 edit would apply cleanly ===")
        print("Dry run complete. Re-run with --write to apply.")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print("=== 1 edit written ===")


if __name__ == "__main__":
    main()
