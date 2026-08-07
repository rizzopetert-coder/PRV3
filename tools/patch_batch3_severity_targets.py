"""
PRV3 Calibration Harness Patch -- _SEVERITY_FOLLOW_ON_TARGETS additions
for the 3 CLEAN Bucket 3 groups approved this round:

1. the_paper_tiger (Q06/D, new SEVER-21) -- APT-PT-00/01/02/03.
2. hr_capture/heard_and_ignored/what_nobody_says/leadership_deafness
   (Q04/D, new SEVER-22):
     - AUT-HC-01, ATT-WNS-01 -- extend existing entries with SEVER-22
       as a genuine SECOND trigger (both already have a first: SEVER-15
       and SEVER-16 respectively), closing both to Endemic.
     - AUT-HI-01/02, ATT-LD-01/02/03 -- new entries, first trigger.
       AUT-HI-01/ATT-LD-01 (Endemic-expected) correctly land short at
       Entrenched, pending a second trigger, separate future work.
3. the_basement_standard/the_inside_track/the_wrong_reward -- reuse the
   already-existing SEVER-20 (from the Q11 fix) via new entries, no new
   content. ATT-BS-01/ATT-IT-01 (Endemic-expected) correctly land short
   at Entrenched pending a second trigger, separate future work.

Usage:
  python tools/patch_batch3_severity_targets.py --dry-run
  python tools/patch_batch3_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

EDITS: list[tuple[str, str]] = []


def edit(old: str, new: str):
    EDITS.append((old, new))


# ============================================================================
# Extend AUT-HC-01 and ATT-WNS-01 with a genuine second trigger (SEVER-22)
# ============================================================================

edit(
    '    "AUT-HC-01":  {"SEVER-15": "18mo_plus"},',
    '    "AUT-HC-01":  {"SEVER-15": "18mo_plus", "SEVER-22": "18mo_plus"},',
)

edit(
    '    "ATT-WNS-01": {"SEVER-16": "18mo_plus"},',
    '    "ATT-WNS-01": {"SEVER-16": "18mo_plus", "SEVER-22": "18mo_plus"},',
)


# ============================================================================
# New entries -- appended after the existing Q11/SEVER-20 block
# ============================================================================

edit(
    '    "EXP-CO-01":  {"SEVER-20": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},',
    '    "EXP-CO-01":  {"SEVER-20": "18mo_plus"},\n'
    '    # Q06/D second trigger (the_paper_tiger) -- APT-PT-00/01/02/03 are\n'
    '    # single-trigger Entrenched-expected, closed by this alone. Zero\n'
    '    # blast radius -- D is unique to the_paper_tiger on Q06.\n'
    '    "APT-PT-00":  {"SEVER-21": "18mo_plus"},\n'
    '    "APT-PT-01":  {"SEVER-21": "18mo_plus"},\n'
    '    "APT-PT-02":  {"SEVER-21": "18mo_plus"},\n'
    '    "APT-PT-03":  {"SEVER-21": "18mo_plus"},\n'
    '    # Q04/D first trigger (heard_and_ignored / leadership_deafness) --\n'
    '    # AUT-HI-02, ATT-LD-02, ATT-LD-03 are single-trigger\n'
    '    # Entrenched-expected, closed by this alone. AUT-HI-01, ATT-LD-01\n'
    '    # are Endemic-expected and genuinely need a second trigger (no\n'
    '    # candidate identified, separate future work) -- correctly land\n'
    '    # short at Entrenched, not a bug.\n'
    '    "AUT-HI-01":  {"SEVER-22": "18mo_plus"},\n'
    '    "AUT-HI-02":  {"SEVER-22": "18mo_plus"},\n'
    '    "ATT-LD-01":  {"SEVER-22": "18mo_plus"},\n'
    '    "ATT-LD-02":  {"SEVER-22": "18mo_plus"},\n'
    '    "ATT-LD-03":  {"SEVER-22": "18mo_plus"},\n'
    '    # Q11/D second/first trigger (the_basement_standard /\n'
    '    # the_inside_track / the_wrong_reward), reusing the existing\n'
    '    # SEVER-20 -- no new content, pure table addition. ATT-BS-02/03,\n'
    '    # ATT-IT-02/03, ATT-WR-01 are single-trigger Entrenched-expected,\n'
    '    # closed by this alone. ATT-BS-01, ATT-IT-01 are Endemic-expected\n'
    '    # and genuinely need a second trigger (candidate: Q05, pending\n'
    '    # Pete\'s content call on C vs D, separate future work) --\n'
    '    # correctly land short at Entrenched, not a bug.\n'
    '    "ATT-BS-01":  {"SEVER-20": "18mo_plus"},\n'
    '    "ATT-BS-02":  {"SEVER-20": "18mo_plus"},\n'
    '    "ATT-BS-03":  {"SEVER-20": "18mo_plus"},\n'
    '    "ATT-IT-01":  {"SEVER-20": "18mo_plus"},\n'
    '    "ATT-IT-02":  {"SEVER-20": "18mo_plus"},\n'
    '    "ATT-IT-03":  {"SEVER-20": "18mo_plus"},\n'
    '    "ATT-WR-01":  {"SEVER-20": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},',
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TARGET.read_text(encoding="utf-8")

    for i, (old, new) in enumerate(EDITS, 1):
        count = content.count(old)
        if count != 1:
            print(f"ABORT: edit #{i}: expected exactly 1 match, found {count}")
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print(f"=== {len(EDITS)} edit(s) would apply cleanly ===")
        print("\nDry run complete. Re-run with --write to apply.")
    else:
        TARGET.write_text(content, encoding="utf-8")
        print(f"=== {len(EDITS)} edit(s) written ===")


if __name__ == "__main__":
    main()
