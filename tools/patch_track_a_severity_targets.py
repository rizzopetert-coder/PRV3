"""
PRV3 Calibration Harness Patch -- expand _SEVERITY_FOLLOW_ON_TARGETS for
Track A's 10 duration_band additions.

Confirmed empirically (byte-for-byte 172-profile diff, 0 changed) that
adding the new duration_band=18mo_plus options to questions.py alone does
NOT change any calibration output -- generate_answers()'s severity splice
is gated by this table; a profile absent from it never gets a follow-on
answered regardless of what content that follow-on now offers. This is a
real, necessary second step, not automatic -- flagged per Pete's explicit
ask rather than assumed.

33 new/updated entries, matching the Bucket 2 groupings
(tools/diag_severity_bucket2_36profiles.md), all targeting "18mo_plus" --
the new, strongest available option on each follow-on:

  SEVER-13 (9): ATT-BCP-01/02/03, ATT-GD-01/02/03, ATT-NL-01/02/03
  SEVER-08 (6): ALL-FR-01/02, ALL-SI-01/02/03, EXP-DCF-01
  SEVER-11 (5): ALL-DB-01, EXP-SDB-01 (UPDATED from True -- Phase-2-pending,
                Q31 inert, kept for calibration-suite internal consistency
                since SEVER-11 itself is now enriched), AUT-UP-01/02/03 (NEW)
  SEVER-07 (3): APT-UL-01, APT-DT-01, AUT-LC-01
  SEVER-02 (3): APT-BF-01, APT-BF-02, APT-UR-01
  SEVER-10 (3): ATT-CD-01, ATT-IE-01, EXP-WT-01
  SEVER-03 (2): AUT-DP-01, AUT-LM-01
  SEVER-01 (1): AUT-PF-01
  SEVER-01+SEVER-12 (1): ATT-DC-01 -- needs BOTH to reach its locked
                Endemic (raw>=4.00); either alone caps at Entrenched.

SEVER-09 (the_second_close, ALL-SC-01) deliberately excluded -- confirmed
Phase-2-pending (routes via inert Q27A), parked separately, not part of
this batch.

AUT-PS-01/SEVER-05 deliberately NOT added here -- Q23's option D never
wins best_option_for_state() (a real, non-tie dimensional loss, not a tie
this table can route around), so generate_answers() can never select D
regardless of what's in this table. That path is verified exclusively via
tools/test_aut_ps_01_q23_d_forced.py, which bypasses best_option_for_state()
entirely by design -- adding an entry here would be a silent no-op.

Usage:
  python tools/patch_track_a_severity_targets.py --dry-run
  python tools/patch_track_a_severity_targets.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = '''_SEVERITY_FOLLOW_ON_TARGETS: dict[str, dict[str, object]] = {
    "AUT-PL-01":  {"SEVER-04": "18mo_plus"},
    "AUT-UA-01":  {"SEVER-04": "18mo_plus"},
    "ATT-IB-01":  {"SEVER-06": "18mo_plus"},
    "EXP-HDA-01": {"SEVER-06": "18mo_plus"},
    "ALL-DB-01":  {"SEVER-11": True},
    "EXP-SDB-01": {"SEVER-11": True},
}'''

NEW = '''_SEVERITY_FOLLOW_ON_TARGETS: dict[str, dict[str, object]] = {
    "AUT-PL-01":  {"SEVER-04": "18mo_plus"},
    "AUT-UA-01":  {"SEVER-04": "18mo_plus"},
    "ATT-IB-01":  {"SEVER-06": "18mo_plus"},
    "EXP-HDA-01": {"SEVER-06": "18mo_plus"},
    # Track A duration_band additions (10 questions, all confirmed
    # LIVE-REACHABLE except SEVER-11's Q31 path -- see below). ALL-DB-01/
    # EXP-SDB-01 updated from True to "18mo_plus" now that SEVER-11 offers
    # a real duration_band option; still Phase-2-pending (Q31 inert), kept
    # for calibration-suite internal consistency, not live urgency.
    "ALL-DB-01":  {"SEVER-11": "18mo_plus"},
    "EXP-SDB-01": {"SEVER-11": "18mo_plus"},
    "AUT-UP-01":  {"SEVER-11": "18mo_plus"},
    "AUT-UP-02":  {"SEVER-11": "18mo_plus"},
    "AUT-UP-03":  {"SEVER-11": "18mo_plus"},
    "ATT-BCP-01": {"SEVER-13": "18mo_plus"},
    "ATT-BCP-02": {"SEVER-13": "18mo_plus"},
    "ATT-BCP-03": {"SEVER-13": "18mo_plus"},
    "ATT-GD-01":  {"SEVER-13": "18mo_plus"},
    "ATT-GD-02":  {"SEVER-13": "18mo_plus"},
    "ATT-GD-03":  {"SEVER-13": "18mo_plus"},
    "ATT-NL-01":  {"SEVER-13": "18mo_plus"},
    "ATT-NL-02":  {"SEVER-13": "18mo_plus"},
    "ATT-NL-03":  {"SEVER-13": "18mo_plus"},
    "ALL-FR-01":  {"SEVER-08": "18mo_plus"},
    "ALL-FR-02":  {"SEVER-08": "18mo_plus"},
    "ALL-SI-01":  {"SEVER-08": "18mo_plus"},
    "ALL-SI-02":  {"SEVER-08": "18mo_plus"},
    "ALL-SI-03":  {"SEVER-08": "18mo_plus"},
    "EXP-DCF-01": {"SEVER-08": "18mo_plus"},
    "APT-UL-01":  {"SEVER-07": "18mo_plus"},
    "APT-DT-01":  {"SEVER-07": "18mo_plus"},
    "AUT-LC-01":  {"SEVER-07": "18mo_plus"},
    "APT-BF-01":  {"SEVER-02": "18mo_plus"},
    "APT-BF-02":  {"SEVER-02": "18mo_plus"},
    "APT-UR-01":  {"SEVER-02": "18mo_plus"},
    "ATT-CD-01":  {"SEVER-10": "18mo_plus"},
    "ATT-IE-01":  {"SEVER-10": "18mo_plus"},
    "EXP-WT-01":  {"SEVER-10": "18mo_plus"},
    "AUT-DP-01":  {"SEVER-03": "18mo_plus"},
    "AUT-LM-01":  {"SEVER-03": "18mo_plus"},
    "AUT-PF-01":  {"SEVER-01": "18mo_plus"},
    # ATT-DC-01 needs BOTH to reach its locked Endemic (raw>=4.00) -- either
    # alone caps at Entrenched (raw=2.00).
    "ATT-DC-01":  {"SEVER-01": "18mo_plus", "SEVER-12": "18mo_plus"},
}'''


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

    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print("=== Would replace _SEVERITY_FOLLOW_ON_TARGETS (6 keys -> 37 keys) ===")
        print("Dry run complete. Re-run with --write to apply.")
    else:
        TARGET.write_text(new_content, encoding="utf-8")
        print("=== Written: _SEVERITY_FOLLOW_ON_TARGETS now has 37 keys ===")


if __name__ == "__main__":
    main()
