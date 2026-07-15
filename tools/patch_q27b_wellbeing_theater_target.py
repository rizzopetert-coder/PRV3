"""
PRV3 Calibration — Wellbeing Theater, Step 2 (Session 71)

Single targeted edit to engine/data/questions.py: adds "wellbeing_theater" to
Q27B's state_targets list. Q27B asks how the respondent would describe the
current state of the organization's culture (fires when significant_events
does not include an acquisition/merger -- the Q27A/Q27B conditional pair) --
currently targets culture_drift, identity_erosion, and the_culture_that_wasnt.
This wires wellbeing_theater into best_option_for_state()'s gating condition
in generate_answers() (tools/calibration_runner.py), which was previously
always False for this state since no question anywhere listed it in
state_targets (confirmed Session 71 verification pass -- zero hits across all
of questions.py, identical to the pre-Session-69 status of the six states
that session wired).

SUPERSEDES an initial DIST-CC-02 candidate considered and rejected before any
file was touched: tools/calibration_runner.py's _CORE_QUESTION_IDS filter
(line 178-182) excludes any question ID containing "DIST" from
generate_answers()'s answer-generation loop entirely. Wiring DIST-CC-02 would
have produced a clean-looking state_targets edit that generate_answers()
never actually invokes -- structurally inert regardless of the
dimensional_contributions on its options, a stronger trap than the Session
69 Q22/human_displacement_anxiety zero-contribution dead end because it
wouldn't show up as "no signal change," it would show up as no code path
touching the question at all.

Topical fit: wellbeing_theater is "structural mismatch between wellbeing
investment and wellbeing conditions... the stated value and the structural
reality have diverged" (web/data/taxonomy.ts). Q27B's option E -- "The
culture people experience doesn't match what we describe in recruiting" --
is a direct restatement of that stated-value-vs-reality gap, arguably a
tighter match than the original DIST-CC-02 candidate.

Non-zero contribution check (per Session 69's Q22/human_displacement_anxiety
dead-end precedent -- do not wire a question whose relevant field is all
zeros): Q27B's attitude_liability values across options are B=0.50, C=0.50,
D=0.50, E=0.50 (A=0.0, the healthy/F option, correctly zero). Confirmed
non-zero on the state's primary liability field (attitude_liability,
primary_dimension=Attitude per engine/data/states.py). Confirmed Q27B itself
(unlike DIST-CC-02, SEVER-10, and VERIFY-Q27B) IS a member of
_CORE_QUESTION_IDS -- starts with "Q", contains none of SEVER/DIST/FOLLOW.

Duplicate-anchor check (per Session 69 precedent -- VERIFY-Q22 shared Q22's
target-list string): the literal string ["culture_drift", "identity_erosion",
"the_culture_that_wasnt"] appears THREE times in questions.py -- Q27B (the
core question), SEVER-10 (a severity follow-on fired conditionally from
Q27B's B/C/D options), and VERIFY-Q27B (a separate verification probe). Both
other occurrences are themselves excluded from _CORE_QUESTION_IDS (SEVER-10
by the SEVER filter, VERIFY-Q27B by not starting with "Q"), so only Q27B
matters for calibration-suite purposes -- but the anchor below still includes
Q27B's unique option E text through to the target-list line, to guarantee
the source-level string replace touches only the Q27B occurrence and not the
other two, confirmed via a uniqueness grep on the option E string before this
script was written.

No other line touched. dimensional_contributions on Q27B's options are
unchanged -- this patch only adds a state_id to the targeting list, not new
signal values. SEVER-10 and VERIFY-Q27B are untouched.

Usage:
  python tools/patch_q27b_wellbeing_theater_target.py --dry-run
  python tools/patch_q27b_wellbeing_theater_target.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OLD = (
    '("E", "The culture people experience doesn\'t match what we describe in recruiting.", False, None),\n'
    '        ],\n'
    '        ["culture_drift", "identity_erosion", "the_culture_that_wasnt"],'
)
NEW = (
    '("E", "The culture people experience doesn\'t match what we describe in recruiting.", False, None),\n'
    '        ],\n'
    '        ["culture_drift", "identity_erosion", "the_culture_that_wasnt", "wellbeing_theater"],'
)
TARGET_FILE = "engine/data/questions.py"


def apply(dry_run: bool):
    path = REPO_ROOT / TARGET_FILE
    text = path.read_text(encoding="utf-8")

    count = text.count(OLD)
    print("=" * 72)
    print(f"Q27B state_targets PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"File: {TARGET_FILE}")
    print(f"Anchor matches found: {count}")

    if count != 1:
        print(f"\n[ERROR] expected exactly 1 match, found {count}. Nothing changed.")
        sys.exit(1)

    new_text = text.replace(OLD, NEW, 1)

    idx = text.index(OLD)
    line_no = text.count("\n", 0, idx) + 1
    print(f"\nAround line {line_no} (Q27B only — SEVER-10 and VERIFY-Q27B untouched):")
    print("  - " + '["culture_drift", "identity_erosion", "the_culture_that_wasnt"],')
    print("  + " + '["culture_drift", "identity_erosion", "the_culture_that_wasnt", "wellbeing_theater"],')

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
