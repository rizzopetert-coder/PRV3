"""
PRV3 Calibration — Invisible Performance Management, Step 3 (Session 71)

Single targeted edit to engine/data/questions.py: adds
"invisible_performance_management" to Q35's state_targets list. Q35 asks what
the conversation usually sounds like when someone in a key role isn't
performing -- currently targets built_to_fail, the_undefined_role, and
the_overloaded_manager. This wires invisible_performance_management into
best_option_for_state()'s gating condition in generate_answers()
(tools/calibration_runner.py), which was previously always False for this
state since no question anywhere listed it in state_targets (confirmed
Session 71 verification pass -- zero hits across all of questions.py,
identical to the pre-Session-69 status of the six states that session wired).

Topical fit: invisible_performance_management is renamed from the profiles
doc's clinical name (see engine/data/states.py the_paper_tiger block comment,
"Renamed from clinical name: Invisible Performance Management") but is its own
distinct registered state (state_id=invisible_performance_management,
primary_dimension=Aptitude) -- performance issues that go unaddressed or
unresolved. Q35 is squarely about whether underperformance conversations
happen and what they focus on.

Non-zero contribution check (per Session 69's Q22/human_displacement_anxiety
dead-end precedent -- do not wire a question whose relevant field is all
zeros): Q35's aptitude_liability values across options are A=0.25, B=0.80,
C=0.40, D=0.40. All non-zero -- Q35 has no "healthy" F-style option coded to
zero. Confirmed non-zero on the state's primary liability field
(aptitude_liability, primary_dimension=Aptitude per engine/data/states.py).

Duplicate-anchor check (per Session 69 precedent -- VERIFY-Q22 shared Q22's
target-list string): the literal string ["built_to_fail",
"the_undefined_role", "the_overloaded_manager"] was grepped across
questions.py and appears exactly once. No disambiguation needed.

No other line touched. dimensional_contributions on Q35's options are
unchanged -- this patch only adds a state_id to the targeting list, not new
signal values.

Usage:
  python tools/patch_q35_invisible_performance_management_target.py --dry-run
  python tools/patch_q35_invisible_performance_management_target.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OLD = '["built_to_fail", "the_undefined_role", "the_overloaded_manager"],'
NEW = '["built_to_fail", "the_undefined_role", "the_overloaded_manager", "invisible_performance_management"],'
TARGET_FILE = "engine/data/questions.py"


def apply(dry_run: bool):
    path = REPO_ROOT / TARGET_FILE
    text = path.read_text(encoding="utf-8")

    count = text.count(OLD)
    print("=" * 72)
    print(f"Q35 state_targets PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"File: {TARGET_FILE}")
    print(f"Anchor matches found: {count}")

    if count != 1:
        print(f"\n[ERROR] expected exactly 1 match, found {count}. Nothing changed.")
        sys.exit(1)

    new_text = text.replace(OLD, NEW, 1)

    idx = text.index(OLD)
    line_no = text.count("\n", 0, idx) + 1
    print(f"\nLine {line_no}:")
    print(f"  - {OLD}")
    print(f"  + {NEW}")

    if dry_run:
        print("\nDry run OK. No file written.")
        return

    path.write_text(new_text, encoding="utf-8")
    print("\nFile written.")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
