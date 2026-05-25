"""
Patch: engine/data/salience.py — culture_drift attitude primary 2.5 -> 1.85

Track 1: Angular separation — reduce culture_drift attitude salience from 2.5
to 1.85. Authority secondary (1.0) and all other fields (0.4) unchanged.

v19: Session 23, 2026-05-24.

Usage:
  python tools/patch_v19_track1_culture_drift_salience.py --dry-run
  python tools/patch_v19_track1_culture_drift_salience.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "salience.py"

OLD = (
    '    "culture_drift": {  # Tier 2 v18: authority secondary 2.5->1.0\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
    '    },\n'
)

NEW = (
    '    "culture_drift": {  # Tier 2 v18: authority secondary 2.5->1.0; v19: attitude primary 2.5->1.85\n'
    '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
    '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
    '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
    '        "attitude_liability": 1.85, "attitude_asset": 1.85,\n'
    '    },\n'
)


def run(dry_run: bool):
    text = TARGET.read_text(encoding="utf-8")
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v19_track1_culture_drift_salience.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    if OLD not in text:
        print("[FAIL] Old block not found. Aborting.")
        sys.exit(1)
    if text.count(OLD) > 1:
        print("[FAIL] Old block not unique. Aborting.")
        sys.exit(1)

    print("culture_drift salience — current vs proposed:")
    print("  attitude_liability:  2.5  ->  1.85")
    print("  attitude_asset:      2.5  ->  1.85")
    print("  authority_liability: 1.0  ->  1.0  (unchanged)")
    print("  authority_asset:     1.0  ->  1.0  (unchanged)")
    print("  all other 4 fields:  0.4  ->  0.4  (unchanged)")

    if dry_run:
        print(f"\n[DRY-RUN] Would apply: culture_drift attitude_liability/asset 2.5 -> 1.85")
        print("[DRY-RUN COMPLETE] 1 change validated. No file written.")
    else:
        new_text = text.replace(OLD, NEW, 1)
        TARGET.write_text(new_text, encoding="utf-8")
        print(f"\n[APPLIED] culture_drift attitude_liability/asset 2.5 -> 1.85")
        print(f"[DONE] {TARGET} written.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
