"""
PRV3 Calibration Harness Patch -- add SEVER-27/SEVER-28 to the relevant
_SEVERITY_FOLLOW_ON_TARGETS entries.

SEVER-27 (Q06/A, content call confirmed by Pete): AUT-TV-01/02
(the_tolerated_violation) and EXP-DIA-01/02/03 (disparate_impact_
architecture) -- the two states this fix was scoped to unblock.
heard_and_ignored, the_unsolved_problem, decision_blindness, and
the_policy_lag also reach A on Q06 but are deliberately NOT added --
all four are already closed or already tracked via other levers, out
of scope for this fix.

SEVER-28 (Q01/D, the_founders_grip): AUT-FG-01/02, both new entries,
first trigger. AUT-FG-02 (Entrenched) closes outright. AUT-FG-01
(Endemic) lands correctly short pending a second trigger (no candidate
identified, separate future work).

Usage:
  python tools/patch_q06a_q01d_severity_targets.py --dry-run
  python tools/patch_q06a_q01d_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = (
    '    "ATT-UT-03":  {"SEVER-25": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},'
)

NEW = (
    '    "ATT-UT-03":  {"SEVER-25": "18mo_plus"},\n'
    '    # Q06/A trigger (the_tolerated_violation / disparate_impact_\n'
    '    # architecture) -- content call confirmed by Pete, A already the\n'
    '    # winning option. AUT-TV-02, EXP-DIA-02, EXP-DIA-03 (Entrenched)\n'
    '    # close outright. AUT-TV-01, EXP-DIA-01 (Endemic) land correctly\n'
    '    # short pending a second trigger (no candidate identified, separate\n'
    '    # future work). heard_and_ignored, the_unsolved_problem,\n'
    '    # decision_blindness, the_policy_lag deliberately NOT added --\n'
    '    # already closed/tracked via other levers, out of scope.\n'
    '    "AUT-TV-01":  {"SEVER-27": "18mo_plus"},\n'
    '    "AUT-TV-02":  {"SEVER-27": "18mo_plus"},\n'
    '    "EXP-DIA-01": {"SEVER-27": "18mo_plus"},\n'
    '    "EXP-DIA-02": {"SEVER-27": "18mo_plus"},\n'
    '    "EXP-DIA-03": {"SEVER-27": "18mo_plus"},\n'
    '    # Q01/D trigger (the_founders_grip) -- AUT-FG-02 (Entrenched)\n'
    '    # closes outright. AUT-FG-01 (Endemic) lands correctly short\n'
    '    # pending a second trigger, no candidate identified.\n'
    '    "AUT-FG-01":  {"SEVER-28": "18mo_plus"},\n'
    '    "AUT-FG-02":  {"SEVER-28": "18mo_plus"},\n'
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
