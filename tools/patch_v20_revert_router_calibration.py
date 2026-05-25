"""
Patch: tools/calibration_runner.py — revert use_router=True (v20 revert)

Restores acc_engine.rank(SALIENCE_PROFILES) without use_router=True.

v20: Session 23, 2026-05-24.

Usage:
  python tools/patch_v20_revert_router_calibration.py --dry-run
  python tools/patch_v20_revert_router_calibration.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "tools" / "calibration_runner.py"

OLD = '    rankings = acc_engine.rank(SALIENCE_PROFILES, use_router=True)\n'
NEW = '    rankings = acc_engine.rank(SALIENCE_PROFILES)\n'


def run(dry_run: bool):
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v20_revert_router_calibration.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    text = TARGET.read_text(encoding="utf-8")

    if OLD not in text:
        print("[FAIL] Old line not found. Aborting.")
        sys.exit(1)
    if text.count(OLD) > 1:
        print("[FAIL] Old line not unique. Aborting.")
        sys.exit(1)

    print(f"  OLD: {OLD.strip()}")
    print(f"  NEW: {NEW.strip()}")

    if dry_run:
        print(f"\n[DRY-RUN] Would apply: restore acc_engine.rank(SALIENCE_PROFILES)")
        print("[DRY-RUN COMPLETE] 1 revert validated. No file written.")
    else:
        new_text = text.replace(OLD, NEW, 1)
        TARGET.write_text(new_text, encoding="utf-8")
        print(f"\n[APPLIED] restore acc_engine.rank(SALIENCE_PROFILES)")
        print(f"[DONE] {TARGET} written.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
