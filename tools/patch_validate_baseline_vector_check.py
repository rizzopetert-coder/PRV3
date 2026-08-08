"""
PRV3 -- Fix validate.py's stale "all dimensional vectors at 0.25 baseline"
check (Section 13b Priority Queue item, cluster_id/baseline-vector pair).

Independently re-verified before writing this patch, not taken on faith
from the Claude.ai investigation that proposed it:
  - Grep-confirmed all 58 STATE_PROFILES entries in engine/data/states.py
    carry an explicit `STATE_PROFILES["<id>"].dimensional_vector =
    DimensionalVector(...)` override line (0 missing).
  - Direct runtime check confirmed 0 of 58 states have all 8
    DIMENSIONAL_FIELDS still equal to BASELINE_VALUE (0.25) -- every
    state has a real calibrated override on at least one field.

The current check (bad_vectors = states with ANY non-baseline field,
asserting that list is empty) is testing a pre-Phase-1-calibration
invariant that can structurally never pass again now that every state
has been calibrated. Flipped to its intended purpose: catch a future
state added to STATE_PROFILES without a real calibration override
(i.e. one that is still fully baseline on every field).

Confirmed test-harness-only change -- engine/data/states.py and every
other production module are untouched.

Usage:
  python tools/patch_validate_baseline_vector_check.py --dry-run
  python tools/patch_validate_baseline_vector_check.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


V = "engine/data/validate.py"

edit(
    V,
    "# Dimensional vectors all at baseline\n"
    "bad_vectors = [\n"
    "    sid for sid, p in STATE_PROFILES.items()\n"
    "    if any(getattr(p.dimensional_vector, f) != BASELINE_VALUE for f in DIMENSIONAL_FIELDS)\n"
    "]\n"
    'check("All dimensional vectors at 0.25 baseline", not bad_vectors,\n'
    '      f"non-baseline: {bad_vectors}")',
    "# No state should remain fully at baseline post-calibration (catches a\n"
    "# future state added to STATE_PROFILES without a real calibration override)\n"
    "fully_baseline_vectors = [\n"
    "    sid for sid, p in STATE_PROFILES.items()\n"
    "    if all(getattr(p.dimensional_vector, f) == BASELINE_VALUE for f in DIMENSIONAL_FIELDS)\n"
    "]\n"
    'check("No state\'s dimensional vector remains fully at 0.25 baseline", not fully_baseline_vectors,\n'
    '      f"still fully baseline: {fully_baseline_vectors}")',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
