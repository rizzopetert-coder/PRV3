"""
Patch: engine/data/questions.py — Q20 options C and D aptitude_liability 0.60 -> 0.80

Track 2: Q20 amplification. authority_liability=0.00 (implicit via _z) unchanged.

v19: Session 23, 2026-05-24.

Usage:
  python tools/patch_v19_track2_q20_amplification.py --dry-run
  python tools/patch_v19_track2_q20_amplification.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

OLD = (
    '        "Q20": {  # Aptitude HIGH (built_to_fail). Authority drain v15.\n'
    '            "A": {**_z, "aptitude_asset":     0.40},                    # F\n'
    '            "B": {**_z, "aptitude_liability": 0.25},                    # A\n'
    '            "C": {**_z, "aptitude_liability": 0.60},                    # P\n'
    '            "D": {**_z, "aptitude_liability": 0.60},                    # P\n'
    '        },\n'
)

NEW = (
    '        "Q20": {  # Aptitude HIGH (built_to_fail). Authority drain v15. v19: C/D 0.60->0.80.\n'
    '            "A": {**_z, "aptitude_asset":     0.40},                    # F\n'
    '            "B": {**_z, "aptitude_liability": 0.25},                    # A\n'
    '            "C": {**_z, "aptitude_liability": 0.80},                    # P\n'
    '            "D": {**_z, "aptitude_liability": 0.80},                    # P\n'
    '        },\n'
)


def run(dry_run: bool):
    text = TARGET.read_text(encoding="utf-8")
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v19_track2_q20_amplification.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    if OLD not in text:
        print("[FAIL] Old block not found. Aborting.")
        sys.exit(1)
    if text.count(OLD) > 1:
        print("[FAIL] Old block not unique. Aborting.")
        sys.exit(1)

    print("Q20 options C and D — current vs proposed:")
    print("  C: aptitude_liability  0.60  ->  0.80")
    print("  C: authority_liability 0.00  ->  0.00  (locked, implicit via _z)")
    print("  D: aptitude_liability  0.60  ->  0.80")
    print("  D: authority_liability 0.00  ->  0.00  (locked, implicit via _z)")
    print("  A, B: unchanged")

    if dry_run:
        print(f"\n[DRY-RUN] Would apply: Q20-C/D aptitude_liability 0.60 -> 0.80")
        print("[DRY-RUN COMPLETE] 1 change validated. No file written.")
    else:
        new_text = text.replace(OLD, NEW, 1)
        TARGET.write_text(new_text, encoding="utf-8")
        print(f"\n[APPLIED] Q20-C/D aptitude_liability 0.60 -> 0.80")
        print(f"[DONE] {TARGET} written.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
