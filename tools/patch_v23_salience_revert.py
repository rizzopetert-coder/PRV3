"""
PRV3 -- v23 Salience Revert (Session 26)

Reverts engine/data/salience.py -- two entries only, back to Three-Tier standard:

  leadership_deafness:
    attitude_liability / attitude_asset: 1.65 -> 2.5  (primary, Three-Tier)
    authority_liability / authority_asset: 0.65 -> 1.0  (secondary, Three-Tier)
    all other fields: 0.4 (unchanged)

  the_suppression_filter:
    alliance_liability / alliance_asset: 2.85 -> 2.5  (primary, Three-Tier)
    authority_liability / authority_asset: 1.20 -> 1.0  (secondary, Three-Tier)
    all other fields: 0.4 (unchanged)

Usage:
  python tools/patch_v23_salience_revert.py --dry-run
  python tools/patch_v23_salience_revert.py --write
"""

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parents[1]
SALIENCE_PATH = ROOT / "engine" / "data" / "salience.py"


def apply_patch(path: Path, old: str, new: str, label: str, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        print(f"  [ERROR] '{label}' -- old string not found")
        return False
    if count > 1:
        print(f"  [ERROR] '{label}' -- matched {count} times (ambiguous)")
        return False
    new_text = text.replace(old, new, 1)
    if dry_run:
        print(f"  [DRY-RUN] {path.relative_to(ROOT)} -- {label}")
        old_lines = old.splitlines()
        new_lines = new.splitlines()
        for ln in old_lines:
            print(f"    - {ln}")
        for ln in new_lines:
            print(f"    + {ln}")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"  [WRITE]   {path.relative_to(ROOT)} -- {label}")
    return True


def run(dry_run: bool):
    errors = []

    # ── 1. leadership_deafness: revert attitude 1.65->2.5, authority 0.65->1.0 ──
    ok = apply_patch(
        SALIENCE_PATH,
        old="""    "leadership_deafness": {  # v22: primary Attitude 2.5->1.65; authority secondary 1.0->0.65
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.65, "authority_asset": 0.65,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 1.65, "attitude_asset": 1.65,
    },""",
        new="""    "leadership_deafness": {  # v23: revert to Three-Tier -- attitude primary 2.5, authority secondary 1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 1.0, "authority_asset": 1.0,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },""",
        label="leadership_deafness: attitude 1.65->2.5, authority 0.65->1.0",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("leadership_deafness")

    # ── 2. the_suppression_filter: revert alliance 2.85->2.5, authority 1.20->1.0 ─
    ok = apply_patch(
        SALIENCE_PATH,
        old="""    "the_suppression_filter": {  # v22: primary Alliance 2.5->2.85; authority secondary 1.0->1.20
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 1.20, "authority_asset": 1.20,
        "alliance_liability": 2.85, "alliance_asset": 2.85,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },""",
        new="""    "the_suppression_filter": {  # v23: revert to Three-Tier -- alliance primary 2.5, authority secondary 1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 1.0, "authority_asset": 1.0,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },""",
        label="the_suppression_filter: alliance 2.85->2.5, authority 1.20->1.0",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("the_suppression_filter")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    if errors:
        print(f"ERRORS ({len(errors)}) -- patch NOT applied:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        mode = "DRY-RUN" if dry_run else "WRITTEN"
        print(f"All 2 patches {mode} successfully. 1 file affected: engine/data/salience.py")
        if dry_run:
            print("Run with --write to apply.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
