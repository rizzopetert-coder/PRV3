"""
Patch: tools/calibration_runner.py — enable use_router=True in run_profile() (v20)

One change: in run_profile(), the acc_engine.rank() call gains use_router=True
so the Two-Tier Hierarchical Router is active for all Phase 2 calibration runs.

run_profile_synthetic() calls rank_states() directly (not via AccumulationEngine)
and is NOT changed — synthetic injection bypasses the router path by design.

v20: Session 23, 2026-05-24.

Usage:
  python tools/patch_v20_router_calibration.py --dry-run
  python tools/patch_v20_router_calibration.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "tools" / "calibration_runner.py"

OLD = '    rankings = acc_engine.rank(SALIENCE_PROFILES)\n'
NEW = '    rankings = acc_engine.rank(SALIENCE_PROFILES, use_router=True)\n'


def run(dry_run: bool):
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v20_router_calibration.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    text = TARGET.read_text(encoding="utf-8")

    if OLD not in text:
        print("[FAIL] Old line not found. Aborting.")
        sys.exit(1)
    if text.count(OLD) > 1:
        print("[FAIL] Old line not unique. Aborting.")
        sys.exit(1)

    print("run_profile() — acc_engine.rank() call:")
    print(f"  OLD: {OLD.strip()}")
    print(f"  NEW: {NEW.strip()}")
    print()
    print("run_profile_synthetic() — calls rank_states() directly — NOT changed.")

    if dry_run:
        print(f"\n[DRY-RUN] Would apply: run_profile() acc_engine.rank use_router=True")
        print("[DRY-RUN COMPLETE] 1 change validated. No file written.")
    else:
        new_text = text.replace(OLD, NEW, 1)
        TARGET.write_text(new_text, encoding="utf-8")
        print(f"\n[APPLIED] run_profile() acc_engine.rank use_router=True")
        print(f"[DONE] {TARGET} written.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
