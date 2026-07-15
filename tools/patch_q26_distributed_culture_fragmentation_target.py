"""
PRV3 Calibration — Distributed Culture Fragmentation, Step 4 (Session 71)

Single targeted edit to engine/data/questions.py: adds
"distributed_culture_fragmentation" to Q26's state_targets list. Q26 asks how
well different parts of the organization work together when they need to --
currently targets silosolation and the_fracture. This wires
distributed_culture_fragmentation into best_option_for_state()'s gating
condition in generate_answers() (tools/calibration_runner.py), which was
previously always False for this state since no question anywhere listed it
in state_targets (confirmed Session 71 verification pass -- zero hits across
all of questions.py, identical to the pre-Session-69 status of the six states
that session wired).

Topical fit: distributed_culture_fragmentation is "the organization's culture
has fractured along location lines... different experiences, different
leadership relationships, and different career trajectories" (Culture Drift
applied to a geographic dimension -- web/data/taxonomy.ts). Q26's option D --
"Functions operate independently -- collaboration is the exception rather
than the rule" -- captures the same structural fragmentation, one level up
from the specific geographic framing.

Non-zero contribution check (per Session 69's Q22/human_displacement_anxiety
dead-end precedent -- do not wire a question whose relevant field is all
zeros): Q26's alliance_liability values across options are B=0.25, C=0.80,
D=0.60 (A=0.0, the healthy/F option, correctly zero). Confirmed non-zero on
the state's primary liability field (alliance_liability,
primary_dimension=Alliance per engine/data/states.py -- distributed_culture_
fragmentation is classified Alliance despite its "culture" framing, per the
locked Session 65 taxonomy).

Duplicate-anchor check (per Session 69 precedent -- VERIFY-Q22 shared Q22's
target-list string): the literal string ["silosolation", "the_fracture"] was
grepped across questions.py and appears THREE times -- Q26 (the core
question), SEVER-08 (a severity follow-on question fired conditionally from
Q26's C/D options), and VERIFY-Q26 (a separate verification probe). The
anchor below includes Q26's unique option D text (the only "Functions operate
independently" phrasing across all three questions) through to the
target-list line, to match only the Q26 occurrence -- confirmed via a
uniqueness grep on the option D string before this script was written.

No other line touched. dimensional_contributions on Q26's options are
unchanged -- this patch only adds a state_id to the targeting list, not new
signal values. SEVER-08 and VERIFY-Q26 are untouched.

Usage:
  python tools/patch_q26_distributed_culture_fragmentation_target.py --dry-run
  python tools/patch_q26_distributed_culture_fragmentation_target.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

OLD = (
    '("D", "Functions operate independently — collaboration is the exception rather than the rule.", True, "SEVER-08"),\n'
    '        ],\n'
    '        ["silosolation", "the_fracture"],'
)
NEW = (
    '("D", "Functions operate independently — collaboration is the exception rather than the rule.", True, "SEVER-08"),\n'
    '        ],\n'
    '        ["silosolation", "the_fracture", "distributed_culture_fragmentation"],'
)
TARGET_FILE = "engine/data/questions.py"


def apply(dry_run: bool):
    path = REPO_ROOT / TARGET_FILE
    text = path.read_text(encoding="utf-8")

    count = text.count(OLD)
    print("=" * 72)
    print(f"Q26 state_targets PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"File: {TARGET_FILE}")
    print(f"Anchor matches found: {count}")

    if count != 1:
        print(f"\n[ERROR] expected exactly 1 match, found {count}. Nothing changed.")
        sys.exit(1)

    new_text = text.replace(OLD, NEW, 1)

    idx = text.index(OLD)
    line_no = text.count("\n", 0, idx) + 1
    print(f"\nAround line {line_no} (Q26 only — SEVER-08 and VERIFY-Q26 untouched):")
    print("  - " + '["silosolation", "the_fracture"],')
    print("  + " + '["silosolation", "the_fracture", "distributed_culture_fragmentation"],')

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
