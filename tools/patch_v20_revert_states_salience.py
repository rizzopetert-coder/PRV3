"""
Patch: v20 revert — states.py (7 states) + salience.py (culture_drift)

Reverts v19 Track 1 and Track 3 changes before v20 router implementation.
questions.py (Track 2 Q20 amplification) is NOT reverted — retained for v20.

Reverts:
  states.py:
    the_uninitiated:         authority_liability 0.40->0.45, all other 7 fields 0.10->0.15
    the_founders_grip:       authority_liability 0.70->0.60, all other 7 fields 0.05->0.10
    the_exposed:             authority_liability 0.70->0.60, all other 7 fields 0.05->0.10
    hr_capture:              authority_liability 0.70->0.60, all other 7 fields 0.05->0.10
    heard_and_ignored:       authority_liability 0.70->0.60, all other 7 fields 0.05->0.10
    the_tolerated_violation: authority_liability 0.70->0.60, all other 7 fields 0.05->0.10
    the_unsolved_problem:    authority_liability 0.70->0.60, all other 7 fields 0.05->0.10
  salience.py:
    culture_drift: attitude_liability/asset 1.85->2.5

v20: Session 23, 2026-05-24.

Usage:
  python tools/patch_v20_revert_states_salience.py --dry-run
  python tools/patch_v20_revert_states_salience.py --write
"""

import sys
from pathlib import Path

STATES_TARGET  = Path(__file__).parents[1] / "engine" / "data" / "states.py"
SALIENCE_TARGET = Path(__file__).parents[1] / "engine" / "data" / "salience.py"

STATES_CHANGES = [
    (
        "the_uninitiated: authority_liability 0.40->0.45, all other 7 fields 0.10->0.15",
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
    ),
    (
        "the_founders_grip: authority_liability 0.70->0.60, all other 7 fields 0.05->0.10",
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
    ),
    (
        "the_exposed: authority_liability 0.70->0.60, all other 7 fields 0.05->0.10",
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
    ),
    (
        "hr_capture: authority_liability 0.70->0.60, all other 7 fields 0.05->0.10",
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
    ),
    (
        "heard_and_ignored: authority_liability 0.70->0.60, all other 7 fields 0.05->0.10",
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
    ),
    (
        "the_tolerated_violation: authority_liability 0.70->0.60, all other 7 fields 0.05->0.10",
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
    ),
    (
        "the_unsolved_problem: authority_liability 0.70->0.60, all other 7 fields 0.05->0.10",
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
    ),
]

SALIENCE_OLD = (
    '    "culture_drift": {  # Tier 2 v18: authority secondary 2.5->1.0; v19: attitude primary 2.5->1.85\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 1.85, "attitude_asset": 1.85,\n'
    '    },\n'
)

SALIENCE_NEW = (
    '    "culture_drift": {  # Tier 2 v18: authority secondary 2.5->1.0; v19 revert: attitude primary 1.85->2.5\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
    '    },\n'
)


def run(dry_run: bool):
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v20_revert_states_salience.py — {mode}")
    print(f"{'=' * 72}\n")

    # --- Validate states.py ---
    states_text = STATES_TARGET.read_text(encoding="utf-8")
    validated_states = []
    for label, old, new in STATES_CHANGES:
        if old not in states_text:
            print(f"[FAIL] states.py — '{label}' — old block not found. Aborting.")
            sys.exit(1)
        if states_text.count(old) > 1:
            print(f"[FAIL] states.py — '{label}' — old block not unique. Aborting.")
            sys.exit(1)
        validated_states.append((label, old, new))

    # --- Validate salience.py ---
    salience_text = SALIENCE_TARGET.read_text(encoding="utf-8")
    if SALIENCE_OLD not in salience_text:
        print("[FAIL] salience.py — culture_drift old block not found. Aborting.")
        sys.exit(1)
    if salience_text.count(SALIENCE_OLD) > 1:
        print("[FAIL] salience.py — culture_drift old block not unique. Aborting.")
        sys.exit(1)

    # --- Report ---
    print("states.py — 7 states (current -> proposed):\n")
    print(f"  {'State':<28}  {'Field':<22}  {'Current':>8}  {'Proposed':>9}")
    print(f"  {'-'*28}  {'-'*22}  {'-'*8}  {'-'*9}")
    specs = [
        ("the_uninitiated",        "authority_liability", 0.40, 0.45),
        ("the_uninitiated",        "authority_asset",     0.10, 0.15),
        ("the_uninitiated",        "aptitude_liability",  0.10, 0.15),
        ("the_uninitiated",        "aptitude_asset",      0.10, 0.15),
        ("the_uninitiated",        "alliance_liability",  0.10, 0.15),
        ("the_uninitiated",        "alliance_asset",      0.10, 0.15),
        ("the_uninitiated",        "attitude_liability",  0.10, 0.15),
        ("the_uninitiated",        "attitude_asset",      0.10, 0.15),
        ("the_founders_grip",      "authority_liability", 0.70, 0.60),
        ("the_founders_grip",      "all other 7 fields",  0.05, 0.10),
        ("the_exposed",            "authority_liability", 0.70, 0.60),
        ("the_exposed",            "all other 7 fields",  0.05, 0.10),
        ("hr_capture",             "authority_liability", 0.70, 0.60),
        ("hr_capture",             "all other 7 fields",  0.05, 0.10),
        ("heard_and_ignored",      "authority_liability", 0.70, 0.60),
        ("heard_and_ignored",      "all other 7 fields",  0.05, 0.10),
        ("the_tolerated_violation","authority_liability", 0.70, 0.60),
        ("the_tolerated_violation","all other 7 fields",  0.05, 0.10),
        ("the_unsolved_problem",   "authority_liability", 0.70, 0.60),
        ("the_unsolved_problem",   "all other 7 fields",  0.05, 0.10),
    ]
    for state, field, cur, prop in specs:
        marker = "  <--" if cur != prop else ""
        print(f"  {state:<28}  {field:<22}  {cur:>8.2f}  {prop:>9.2f}{marker}")

    print()
    print("salience.py — culture_drift (current -> proposed):\n")
    print(f"  {'Field':<22}  {'Current':>8}  {'Proposed':>9}")
    print(f"  {'-'*22}  {'-'*8}  {'-'*9}")
    print(f"  {'attitude_liability':<22}  {1.85:>8.2f}  {2.5:>9.2f}  <--")
    print(f"  {'attitude_asset':<22}  {1.85:>8.2f}  {2.5:>9.2f}  <--")
    print(f"  {'authority_liability':<22}  {1.0:>8.2f}  {1.0:>9.2f}")
    print(f"  {'authority_asset':<22}  {1.0:>8.2f}  {1.0:>9.2f}")
    print(f"  {'all other 4 fields':<22}  {0.4:>8.2f}  {0.4:>9.2f}")

    print()
    print("questions.py: NOT reverted — Q20 C/D amplification 0.80 retained for v20.")

    if dry_run:
        print()
        for label, _, _ in validated_states:
            print(f"  [DRY-RUN] Would apply states.py: {label}")
        print(f"  [DRY-RUN] Would apply salience.py: culture_drift attitude 1.85->2.5")
        print(f"\n[DRY-RUN COMPLETE] {len(validated_states) + 1} change(s) validated. No files written.")
    else:
        for label, old, new in validated_states:
            states_text = states_text.replace(old, new, 1)
            print(f"  [APPLIED] states.py: {label}")
        STATES_TARGET.write_text(states_text, encoding="utf-8")
        print(f"  [DONE] {STATES_TARGET} written.")

        salience_text = salience_text.replace(SALIENCE_OLD, SALIENCE_NEW, 1)
        print(f"  [APPLIED] salience.py: culture_drift attitude 1.85->2.5")
        SALIENCE_TARGET.write_text(salience_text, encoding="utf-8")
        print(f"  [DONE] {SALIENCE_TARGET} written.")

        print(f"\n[COMPLETE] {len(validated_states) + 1} change(s) applied across 2 files.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
