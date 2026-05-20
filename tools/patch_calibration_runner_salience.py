"""
Patch: tools/calibration_runner.py — wire SALIENCE_PROFILES into ranking calls (Session 21)

Changes:
  1. Add import: from engine.data.salience import SALIENCE_PROFILES
  2. run_profile_synthetic(): rank_states(synthetic_vector) -> rank_states(synthetic_vector, SALIENCE_PROFILES)
  3. run_profile(): acc_engine.rank() -> acc_engine.rank(SALIENCE_PROFILES)

Usage:
  python tools/patch_calibration_runner_salience.py --dry-run
  python tools/patch_calibration_runner_salience.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parent / "calibration_runner.py"

CHANGES = [
    {
        "description": "Add SALIENCE_PROFILES import after states import",
        "old": "from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS",
        "new": (
            "from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS\n"
            "from engine.data.salience import SALIENCE_PROFILES"
        ),
    },
    {
        "description": "run_profile_synthetic(): pass SALIENCE_PROFILES to rank_states()",
        "old": "    rankings  = rank_states(synthetic_vector)",
        "new": "    rankings  = rank_states(synthetic_vector, SALIENCE_PROFILES)",
    },
    {
        "description": "run_profile(): pass SALIENCE_PROFILES to acc_engine.rank()",
        "old": "    rankings = acc_engine.rank()",
        "new": "    rankings = acc_engine.rank(SALIENCE_PROFILES)",
    },
]


def apply(content: str, dry_run: bool) -> tuple[str, list[str]]:
    log = []
    for change in CHANGES:
        old = change["old"]
        new = change["new"]
        desc = change["description"]
        if old not in content:
            log.append(f"  [ERROR] Not found: {desc}")
            continue
        count = content.count(old)
        if count > 1:
            log.append(f"  [ERROR] Ambiguous match ({count}x): {desc}")
            continue
        if dry_run:
            log.append(f"  [DRY-RUN] Would apply: {desc}")
        else:
            content = content.replace(old, new)
            log.append(f"  [APPLIED] {desc}")
    return content, log


def main():
    dry_run = "--write" not in sys.argv
    mode = "DRY-RUN" if dry_run else "WRITE"

    print(f"\n{'='*64}")
    print(f"patch_calibration_runner_salience.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'='*64}\n")

    if not TARGET.exists():
        print("[ERROR] Target file not found.")
        sys.exit(1)

    content = TARGET.read_text(encoding="utf-8")
    new_content, log = apply(content, dry_run)

    errors = [l for l in log if "[ERROR]" in l]
    for line in log:
        print(line)

    if errors:
        print(f"\n[ABORT] {len(errors)} error(s). No changes written.")
        sys.exit(1)

    if not dry_run:
        TARGET.write_text(new_content, encoding="utf-8")
        print(f"\n[DONE] {TARGET} written.")
    else:
        print(f"\n[DRY-RUN COMPLETE] {len(CHANGES)} change(s) validated. Run with --write to apply.")

    sys.exit(0)


if __name__ == "__main__":
    main()
