"""
Patch: engine/output.py — add SIGNAL_FLOOR_CEILING = 0.9650 constant and cap
compute_signal_floors() at min(baseline × multiplier, 0.9650).

v18: three-tier salience + floor ceiling. Session 23, 2026-05-24.

Usage:
  python tools/patch_v18_floor_ceiling.py --dry-run
  python tools/patch_v18_floor_ceiling.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "output.py"

# ── Change 1: add SIGNAL_FLOOR_CEILING constant after SIGNAL_FLOOR_MULTIPLIER_DEFAULT ──

OLD_CONST = (
    'SIGNAL_FLOOR_MULTIPLIER_AUTHORITY: float = 1.00   # LOCKED Session 16\n'
    'SIGNAL_FLOOR_MULTIPLIER_DEFAULT:   float = 1.08   # Updated Session 17 — cosine-space correction from 1.15\n'
)

NEW_CONST = (
    'SIGNAL_FLOOR_MULTIPLIER_AUTHORITY: float = 1.00   # LOCKED Session 16\n'
    'SIGNAL_FLOOR_MULTIPLIER_DEFAULT:   float = 1.08   # Updated Session 17 — cosine-space correction from 1.15\n'
    'SIGNAL_FLOOR_CEILING:              float = 0.9650 # Added Session 23 v18 — caps floor so no state is permanently ungatable\n'
)

# ── Change 2: update compute_signal_floors() to apply ceiling ──

OLD_FUNC = (
    'def compute_signal_floors(noise_baseline: dict) -> dict:\n'
    '    """\n'
    '    Compute per-state signal floor using tiered multipliers.\n'
    '    Authority states: floor = baseline × 1.00 (cosine geometry; floor = noise mean)\n'
    '    All other states: floor = baseline × 1.15 (standard separation threshold)\n'
    '    Session 16: tiered multiplier locked. SIGNAL_FLOOR_MULTIPLIER_AUTHORITY and\n'
    '    SIGNAL_FLOOR_MULTIPLIER_DEFAULT replace the prior single constant.\n'
    '    Spec reference: Section VI.1 — LOCKED\n'
    '    """\n'
    '    from engine.data.states import STATE_PROFILES\n'
    '    floors = {}\n'
    '    for state_id, baseline_score in noise_baseline.items():\n'
    '        profile = STATE_PROFILES.get(state_id)\n'
    '        if profile and profile.primary_dimension == "Authority":\n'
    '            floors[state_id] = baseline_score * SIGNAL_FLOOR_MULTIPLIER_AUTHORITY\n'
    '        else:\n'
    '            floors[state_id] = baseline_score * SIGNAL_FLOOR_MULTIPLIER_DEFAULT\n'
    '    return floors\n'
)

NEW_FUNC = (
    'def compute_signal_floors(noise_baseline: dict) -> dict:\n'
    '    """\n'
    '    Compute per-state signal floor using tiered multipliers.\n'
    '    Authority states: floor = baseline × 1.00 (cosine geometry; floor = noise mean)\n'
    '    All other states: floor = baseline × 1.08 (standard separation threshold)\n'
    '    Session 16: tiered multiplier locked. SIGNAL_FLOOR_MULTIPLIER_AUTHORITY and\n'
    '    SIGNAL_FLOOR_MULTIPLIER_DEFAULT replace the prior single constant.\n'
    '    Session 23 v18: floor capped at SIGNAL_FLOOR_CEILING (0.9650) so no state\n'
    '    is permanently ungatable (e.g. culture_drift at 1.0063 before this fix).\n'
    '    Spec reference: Section VI.1 — LOCKED\n'
    '    """\n'
    '    from engine.data.states import STATE_PROFILES\n'
    '    floors = {}\n'
    '    for state_id, baseline_score in noise_baseline.items():\n'
    '        profile = STATE_PROFILES.get(state_id)\n'
    '        if profile and profile.primary_dimension == "Authority":\n'
    '            raw = baseline_score * SIGNAL_FLOOR_MULTIPLIER_AUTHORITY\n'
    '        else:\n'
    '            raw = baseline_score * SIGNAL_FLOOR_MULTIPLIER_DEFAULT\n'
    '        floors[state_id] = min(raw, SIGNAL_FLOOR_CEILING)\n'
    '    return floors\n'
)

CHANGES = [
    ("SIGNAL_FLOOR_CEILING constant after multipliers", OLD_CONST, NEW_CONST),
    ("compute_signal_floors(): apply SIGNAL_FLOOR_CEILING cap", OLD_FUNC, NEW_FUNC),
]


def run(dry_run: bool):
    text = TARGET.read_text(encoding="utf-8")
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v18_floor_ceiling.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    validated = []
    for label, old, new in CHANGES:
        if old not in text:
            print(f"[FAIL] '{label}' — old block not found. Aborting.")
            sys.exit(1)
        count = text.count(old)
        if count > 1:
            print(f"[FAIL] '{label}' — old block found {count} times (not unique). Aborting.")
            sys.exit(1)
        validated.append((label, old, new))

    for label, old, new in validated:
        if dry_run:
            print(f"  [DRY-RUN] Would apply: {label}")
        else:
            text = text.replace(old, new, 1)
            print(f"  [APPLIED] {label}")

    if dry_run:
        print(f"\n[DRY-RUN COMPLETE] {len(validated)} change(s) validated. No file written.")
    else:
        TARGET.write_text(text, encoding="utf-8")
        print(f"\n[DONE] {TARGET} written. {len(validated)} change(s) applied.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
