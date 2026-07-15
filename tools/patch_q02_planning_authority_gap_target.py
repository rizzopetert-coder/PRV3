"""
PRV3 Calibration — Planning Authority Gap, Step 1 (Session 71)

Single targeted edit to engine/data/questions.py: adds "planning_authority_gap"
to Q02's state_targets list. Q02 asks how the respondent would describe their
HR function right now -- currently targets the_exposed and hr_capture. This
wires planning_authority_gap into best_option_for_state()'s gating condition in
generate_answers() (tools/calibration_runner.py), which was previously always
False for this state since no question anywhere listed it in state_targets
(confirmed Session 71 verification pass -- zero hits across all of
questions.py, identical to the pre-Session-69 status of the six states that
session wired).

Topical fit: planning_authority_gap is "HR has the capability to do strategic
workforce planning and lacks the organizational authority and credibility to
have its output treated as strategic input" (web/data/taxonomy.ts). Q02's
option B -- "Adequate -- HR handles what it needs to but it's not a strategic
function" -- is a direct restatement of that condition.

Non-zero contribution check (per Session 69's Q22/human_displacement_anxiety
dead-end precedent -- do not wire a question whose relevant field is all
zeros): Q02's authority_liability values across options are B=0.25, C=0.60,
D=0.60, E=0.30 (A=0.0, the healthy/F option, correctly zero). Confirmed
non-zero on the state's primary liability field (authority_liability,
primary_dimension=Authority per engine/data/states.py).

Duplicate-anchor check (per Session 69 precedent -- VERIFY-Q22 shared Q22's
target-list string): the literal string ["the_exposed", "hr_capture"] was
grepped across questions.py and appears exactly once. No disambiguation
needed.

No other line touched. dimensional_contributions on Q02's options are
unchanged -- this patch only adds a state_id to the targeting list, not new
signal values.

Usage:
  python tools/patch_q02_planning_authority_gap_target.py --dry-run
  python tools/patch_q02_planning_authority_gap_target.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OLD = '["the_exposed", "hr_capture"],'
NEW = '["the_exposed", "hr_capture", "planning_authority_gap"],'
TARGET_FILE = "engine/data/questions.py"


def apply(dry_run: bool):
    path = REPO_ROOT / TARGET_FILE
    text = path.read_text(encoding="utf-8")

    count = text.count(OLD)
    print("=" * 72)
    print(f"Q02 state_targets PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
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
