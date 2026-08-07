"""
PRV3 Calibration Harness Patch -- add SEVER-23/SEVER-24 to ATT-GD-01/
ATT-NL-01/ATT-BC-01/ATT-BC-02's _SEVERITY_FOLLOW_ON_TARGETS entries.

ATT-GD-01 (groundhog_day, Endemic-expected) already has an existing
entry ({"SEVER-13": "18mo_plus"}) -- extended in place (not a new
duplicate key) with SEVER-23, its only viable second-trigger candidate
since groundhog_day isn't wired to Q34 at all. Closes to Endemic.

ATT-NL-01 (narrative_lock, Endemic-expected) already has an existing
entry -- extended in place with SEVER-24. Closes to Endemic.

ATT-BC-01 (the_burned_credibility, Endemic-expected) has zero triggers
today -- new entry needs BOTH SEVER-23 and SEVER-24 to reach Endemic.

ATT-BC-02 (the_burned_credibility, Entrenched-expected) has zero
triggers today -- new entry, SEVER-24 alone closes it.

ATT-BC-03 (the_burned_credibility, Emerging-expected) is deliberately
NOT added -- already correct, must stay that way. ATT-GD-02/03 and
ATT-NL-02/03 are also deliberately NOT touched -- both already correctly
reach Entrenched via SEVER-13 alone; a second trigger would incorrectly
overshoot them to Endemic. the_broken_compass (ATT-BCP-01/02/03) is
deliberately NOT added -- confirmed safe via empirical in-memory test
with a positive control, must stay unaffected.

Confirmed empirically (in-memory, non-destructive test with a positive
control) that the earlier ATT-GD-01/ATT-NL-01 collision finding
conflated selection-reroute with severity-firing -- the_broken_compass
is structurally safe by the same per-profile-ID gate protecting every
other external state this session.

Usage:
  python tools/patch_q17_q34_severity_targets.py --dry-run
  python tools/patch_q17_q34_severity_targets.py --write
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
# Extend the existing ATT-GD-01 and ATT-NL-01 entries in place -- avoids
# creating duplicate dict keys elsewhere in the same literal.
# ============================================================================

edit(
    '    "ATT-GD-01":  {"SEVER-13": "18mo_plus"},',
    '    "ATT-GD-01":  {"SEVER-13": "18mo_plus", "SEVER-23": "18mo_plus"},',
)

edit(
    '    "ATT-NL-01":  {"SEVER-13": "18mo_plus"},',
    '    "ATT-NL-01":  {"SEVER-13": "18mo_plus", "SEVER-24": "18mo_plus"},',
)


# ============================================================================
# New entries for ATT-BC-01 / ATT-BC-02 (no existing entries)
# ============================================================================

edit(
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},\n'
    '    "APT-DT-01":  {"SEVER-07": "18mo_plus"},\n'
    '    "AUT-LC-01":  {"SEVER-07": "18mo_plus"},',
    '    "ATT-BC-01":  {"SEVER-23": "18mo_plus", "SEVER-24": "18mo_plus"},\n'
    '    "ATT-BC-02":  {"SEVER-24": "18mo_plus"},\n'
    '    "APT-UL-01":  {"SEVER-07": "18mo_plus"},\n'
    '    "APT-DT-01":  {"SEVER-07": "18mo_plus"},\n'
    '    "AUT-LC-01":  {"SEVER-07": "18mo_plus"},',
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
