"""
Patch: engine/data/states.py — Authority vector sharpening (Track 3, v19)

Changes:
1. the_uninitiated: vector compression (authority_liability 0.45->0.40, all others 0.15->0.10)
2. Six HIGH Authority states: authority_liability 0.60->0.70, all other 7 fields 0.10->0.05
   States: the_founders_grip, the_exposed, hr_capture, heard_and_ignored,
           the_tolerated_violation, the_unsolved_problem

v19: Session 23, 2026-05-24.

Usage:
  python tools/patch_v19_track3_authority_vectors.py --dry-run
  python tools/patch_v19_track3_authority_vectors.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "states.py"

CHANGES = [
    (
        "the_uninitiated: authority_liability 0.45->0.40, all others 0.15->0.10",
        (
            'STATE_PROFILES["the_uninitiated"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.15,\n'
            '    aptitude_asset=0.15,\n'
            '    authority_liability=0.45,\n'
            '    authority_asset=0.15,\n'
            '    alliance_liability=0.15,\n'
            '    alliance_asset=0.15,\n'
            '    attitude_liability=0.15,\n'
            '    attitude_asset=0.15,\n'
            ')\n'
        ),
        (
            'STATE_PROFILES["the_uninitiated"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.10,\n'
            '    aptitude_asset=0.10,\n'
            '    authority_liability=0.40,\n'
            '    authority_asset=0.10,\n'
            '    alliance_liability=0.10,\n'
            '    alliance_asset=0.10,\n'
            '    attitude_liability=0.10,\n'
            '    attitude_asset=0.10,\n'
            ')\n'
        ),
    ),
    (
        "the_founders_grip: authority_liability 0.60->0.70, all other 7 fields 0.10->0.05",
        (
            'STATE_PROFILES["the_founders_grip"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.10,\n'
            '    aptitude_asset=0.10,\n'
            '    authority_liability=0.60,\n'
            '    authority_asset=0.10,\n'
            '    alliance_liability=0.10,\n'
            '    alliance_asset=0.10,\n'
            '    attitude_liability=0.10,\n'
            '    attitude_asset=0.10,\n'
            ')\n'
        ),
        (
            'STATE_PROFILES["the_founders_grip"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.05,\n'
            '    aptitude_asset=0.05,\n'
            '    authority_liability=0.70,\n'
            '    authority_asset=0.05,\n'
            '    alliance_liability=0.05,\n'
            '    alliance_asset=0.05,\n'
            '    attitude_liability=0.05,\n'
            '    attitude_asset=0.05,\n'
            ')\n'
        ),
    ),
    (
        "the_exposed: authority_liability 0.60->0.70, all other 7 fields 0.10->0.05",
        (
            'STATE_PROFILES["the_exposed"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.10,\n'
            '    aptitude_asset=0.10,\n'
            '    authority_liability=0.60,\n'
            '    authority_asset=0.10,\n'
            '    alliance_liability=0.10,\n'
            '    alliance_asset=0.10,\n'
            '    attitude_liability=0.10,\n'
            '    attitude_asset=0.10,\n'
            ')\n'
        ),
        (
            'STATE_PROFILES["the_exposed"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.05,\n'
            '    aptitude_asset=0.05,\n'
            '    authority_liability=0.70,\n'
            '    authority_asset=0.05,\n'
            '    alliance_liability=0.05,\n'
            '    alliance_asset=0.05,\n'
            '    attitude_liability=0.05,\n'
            '    attitude_asset=0.05,\n'
            ')\n'
        ),
    ),
    (
        "hr_capture: authority_liability 0.60->0.70, all other 7 fields 0.10->0.05",
        (
            'STATE_PROFILES["hr_capture"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.10,\n'
            '    aptitude_asset=0.10,\n'
            '    authority_liability=0.60,\n'
            '    authority_asset=0.10,\n'
            '    alliance_liability=0.10,\n'
            '    alliance_asset=0.10,\n'
            '    attitude_liability=0.10,\n'
            '    attitude_asset=0.10,\n'
            ')\n'
        ),
        (
            'STATE_PROFILES["hr_capture"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.05,\n'
            '    aptitude_asset=0.05,\n'
            '    authority_liability=0.70,\n'
            '    authority_asset=0.05,\n'
            '    alliance_liability=0.05,\n'
            '    alliance_asset=0.05,\n'
            '    attitude_liability=0.05,\n'
            '    attitude_asset=0.05,\n'
            ')\n'
        ),
    ),
    (
        "heard_and_ignored: authority_liability 0.60->0.70, all other 7 fields 0.10->0.05",
        (
            'STATE_PROFILES["heard_and_ignored"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.10,\n'
            '    aptitude_asset=0.10,\n'
            '    authority_liability=0.60,\n'
            '    authority_asset=0.10,\n'
            '    alliance_liability=0.10,\n'
            '    alliance_asset=0.10,\n'
            '    attitude_liability=0.10,\n'
            '    attitude_asset=0.10,\n'
            ')\n'
        ),
        (
            'STATE_PROFILES["heard_and_ignored"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.05,\n'
            '    aptitude_asset=0.05,\n'
            '    authority_liability=0.70,\n'
            '    authority_asset=0.05,\n'
            '    alliance_liability=0.05,\n'
            '    alliance_asset=0.05,\n'
            '    attitude_liability=0.05,\n'
            '    attitude_asset=0.05,\n'
            ')\n'
        ),
    ),
    (
        "the_tolerated_violation: authority_liability 0.60->0.70, all other 7 fields 0.10->0.05",
        (
            'STATE_PROFILES["the_tolerated_violation"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.10,\n'
            '    aptitude_asset=0.10,\n'
            '    authority_liability=0.60,\n'
            '    authority_asset=0.10,\n'
            '    alliance_liability=0.10,\n'
            '    alliance_asset=0.10,\n'
            '    attitude_liability=0.10,\n'
            '    attitude_asset=0.10,\n'
            ')\n'
        ),
        (
            'STATE_PROFILES["the_tolerated_violation"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.05,\n'
            '    aptitude_asset=0.05,\n'
            '    authority_liability=0.70,\n'
            '    authority_asset=0.05,\n'
            '    alliance_liability=0.05,\n'
            '    alliance_asset=0.05,\n'
            '    attitude_liability=0.05,\n'
            '    attitude_asset=0.05,\n'
            ')\n'
        ),
    ),
    (
        "the_unsolved_problem: authority_liability 0.60->0.70, all other 7 fields 0.10->0.05",
        (
            'STATE_PROFILES["the_unsolved_problem"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.10,\n'
            '    aptitude_asset=0.10,\n'
            '    authority_liability=0.60,\n'
            '    authority_asset=0.10,\n'
            '    alliance_liability=0.10,\n'
            '    alliance_asset=0.10,\n'
            '    attitude_liability=0.10,\n'
            '    attitude_asset=0.10,\n'
            ')\n'
        ),
        (
            'STATE_PROFILES["the_unsolved_problem"].dimensional_vector = DimensionalVector(\n'
            '    aptitude_liability=0.05,\n'
            '    aptitude_asset=0.05,\n'
            '    authority_liability=0.70,\n'
            '    authority_asset=0.05,\n'
            '    alliance_liability=0.05,\n'
            '    alliance_asset=0.05,\n'
            '    attitude_liability=0.05,\n'
            '    attitude_asset=0.05,\n'
            ')\n'
        ),
    ),
]


def run(dry_run: bool):
    text = TARGET.read_text(encoding="utf-8")
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v19_track3_authority_vectors.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    validated = []
    for label, old, new in CHANGES:
        if old not in text:
            print(f"[FAIL] '{label}' — old block not found. Aborting.")
            sys.exit(1)
        if text.count(old) > 1:
            print(f"[FAIL] '{label}' — old block not unique. Aborting.")
            sys.exit(1)
        validated.append((label, old, new))

    if dry_run:
        print("Proposed 8-field vectors (all 7 states):\n")
        print(f"  {'State':<30}  {'Field':<22}  {'Current':>8}  {'Proposed':>9}")
        print(f"  {'-'*30}  {'-'*22}  {'-'*8}  {'-'*9}")
        specs = [
            ("the_uninitiated",        "authority_liability", 0.45, 0.40),
            ("the_uninitiated",        "authority_asset",     0.15, 0.10),
            ("the_uninitiated",        "aptitude_liability",  0.15, 0.10),
            ("the_uninitiated",        "aptitude_asset",      0.15, 0.10),
            ("the_uninitiated",        "alliance_liability",  0.15, 0.10),
            ("the_uninitiated",        "alliance_asset",      0.15, 0.10),
            ("the_uninitiated",        "attitude_liability",  0.15, 0.10),
            ("the_uninitiated",        "attitude_asset",      0.15, 0.10),
            ("the_founders_grip",      "authority_liability", 0.60, 0.70),
            ("the_founders_grip",      "all other 7 fields",  0.10, 0.05),
            ("the_exposed",            "authority_liability", 0.60, 0.70),
            ("the_exposed",            "all other 7 fields",  0.10, 0.05),
            ("hr_capture",             "authority_liability", 0.60, 0.70),
            ("hr_capture",             "all other 7 fields",  0.10, 0.05),
            ("heard_and_ignored",      "authority_liability", 0.60, 0.70),
            ("heard_and_ignored",      "all other 7 fields",  0.10, 0.05),
            ("the_tolerated_violation","authority_liability", 0.60, 0.70),
            ("the_tolerated_violation","all other 7 fields",  0.10, 0.05),
            ("the_unsolved_problem",   "authority_liability", 0.60, 0.70),
            ("the_unsolved_problem",   "all other 7 fields",  0.10, 0.05),
        ]
        for state, field, cur, prop in specs:
            changed = "  <--" if cur != prop else ""
            print(f"  {state:<30}  {field:<22}  {cur:>8.2f}  {prop:>9.2f}{changed}")
        print()
        for label, _, _ in validated:
            print(f"  [DRY-RUN] Would apply: {label}")
        print(f"\n[DRY-RUN COMPLETE] {len(validated)} change(s) validated. No file written.")
    else:
        for label, old, new in validated:
            text = text.replace(old, new, 1)
            print(f"  [APPLIED] {label}")
        TARGET.write_text(text, encoding="utf-8")
        print(f"\n[DONE] {TARGET} written. {len(validated)} change(s) applied.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
