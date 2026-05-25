"""
PRV3 — Absolute Threshold Floor Patch (Session 24 v21)

Replaces the multiplicative noise_baseline floor system in engine/output.py
with a fixed SCD-WCS absolute alignment threshold (T=0.25).

Changes to engine/output.py:
  1. Mark SIGNAL_FLOOR_MULTIPLIER_AUTHORITY, SIGNAL_FLOOR_MULTIPLIER_DEFAULT,
     SIGNAL_FLOOR_CEILING as RETIRED v21. Add SCD_WCS_ALIGNMENT_THRESHOLD = 0.2500.
  2. Mark _PRECOMPUTED_NOISE_BASELINE header as RETIRED v21 (data retained
     for score_lift_pct computation).
  3. Add check_signal_gate(state_id, session_scores) -> bool after
     compute_signal_floors().
  4. Update apply_signal_floor(): make noise_baseline optional, use
     check_signal_gate() for cleared, set signal_floor = SCD_WCS_ALIGNMENT_THRESHOLD.

Usage:
  python tools/patch_v21_absolute_threshold.py --dry-run
  python tools/patch_v21_absolute_threshold.py --write
"""

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parents[1]
OUTPUT_PATH = ROOT / "engine" / "output.py"


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
        for ln in old_lines[:6]:
            print(f"    - {ln}")
        for ln in new_lines[:6]:
            print(f"    + {ln}")
        if len(old_lines) > 6:
            print(f"    ... ({len(old_lines)} lines total -> {len(new_lines)} lines)")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"  [WRITE]   {path.relative_to(ROOT)} -- {label}")
    return True


def run(dry_run: bool):
    errors = []

    # ── 1. Mark multiplier constants RETIRED, add SCD_WCS_ALIGNMENT_THRESHOLD ──
    ok = apply_patch(
        OUTPUT_PATH,
        old="""# Tiered signal floor multipliers — Session 16
# Authority states: 1.00x (floor = noise baseline; cosine geometry disadvantage accepted)
# All other dimensions: 1.15x (standard separation threshold, unchanged)
SIGNAL_FLOOR_MULTIPLIER_AUTHORITY: float = 1.00   # LOCKED Session 16
SIGNAL_FLOOR_MULTIPLIER_DEFAULT:   float = 1.08   # Updated Session 17 — cosine-space correction from 1.15
SIGNAL_FLOOR_CEILING:              float = 0.9650 # Added Session 23 v18 — caps floor so no state is permanently ungatable""",
        new="""# Tiered signal floor multipliers — RETIRED v21 (absolute threshold replaces multiplicative floor)
# Kept for backward compatibility with compute_signal_floors() and legacy tests.
SIGNAL_FLOOR_MULTIPLIER_AUTHORITY: float = 1.00   # RETIRED v21
SIGNAL_FLOOR_MULTIPLIER_DEFAULT:   float = 1.08   # RETIRED v21
SIGNAL_FLOOR_CEILING:              float = 0.9650 # RETIRED v21

# SCD-WCS absolute alignment threshold — v21
# All 47 states use a single geometric threshold: score > 0.25 clears the floor.
# Geometric interpretation: cosine similarity > 0.25 (~75.5 degrees alignment required).
# CALIBRATION TARGET -- set via Phase 2 calibration analysis.
SCD_WCS_ALIGNMENT_THRESHOLD: float = 0.2500""",
        label="mark multiplier constants RETIRED, add SCD_WCS_ALIGNMENT_THRESHOLD",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("multiplier constants / SCD_WCS_ALIGNMENT_THRESHOLD")

    # ── 2. Mark _PRECOMPUTED_NOISE_BASELINE header RETIRED ────────────────────
    ok = apply_patch(
        OUTPUT_PATH,
        old="""# Precomputed noise baseline — Monte Carlo (N=1000, seed=42, Q01–Q39, 39 sampled).
# Weighted cosine similarity metric (SALIENCE_PROFILES), tiered floor multipliers.
# v20: states.py/salience.py reverted, Q20 0.80 retained, full 47-state path. Session 23.
# Monte Carlo N=1000, seed=42, Q01-Q39. Date: 2026-05-24.
_PRECOMPUTED_NOISE_BASELINE: dict = {""",
        new="""# Precomputed noise baseline — RETIRED v21 (SCD-WCS absolute threshold replaces multiplicative floor).
# Kept for score_lift_pct computation in apply_signal_floor(). Do not use for floor gating.
# v20: WCS metric, SALIENCE_PROFILES, full 47-state path. Session 23.
_PRECOMPUTED_NOISE_BASELINE: dict = {""",
        label="mark _PRECOMPUTED_NOISE_BASELINE header RETIRED v21",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("_PRECOMPUTED_NOISE_BASELINE header")

    # ── 3. Add check_signal_gate() after compute_signal_floors() ──────────────
    ok = apply_patch(
        OUTPUT_PATH,
        old="""        floors[state_id] = min(raw, SIGNAL_FLOOR_CEILING)
    return floors


# ── Output data structures ─────────────────────────────────────────────────────""",
        new="""        floors[state_id] = min(raw, SIGNAL_FLOOR_CEILING)
    return floors


def check_signal_gate(state_id: str, session_scores: dict) -> bool:
    \"\"\"
    Return True if the state's session score clears the SCD-WCS alignment threshold.
    session_scores: dict mapping state_id -> score (from rank_states()).
    \"\"\"
    return session_scores.get(state_id, 0.0) > SCD_WCS_ALIGNMENT_THRESHOLD


# ── Output data structures ─────────────────────────────────────────────────────""",
        label="add check_signal_gate() after compute_signal_floors()",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("check_signal_gate() insertion")

    # ── 4. Update apply_signal_floor() ────────────────────────────────────────
    ok = apply_patch(
        OUTPUT_PATH,
        old="""def apply_signal_floor(
    rankings: list,
    noise_baseline: dict,
) -> list:
    \"\"\"
    Evaluate all ranked states against the signal floor.

    For each state: floor = noise_baseline[state_id] × tiered multiplier
    (1.00 Authority, 1.15 all others). State clears floor if score > floor.

    Returns list[QualifiedState] for ALL ranked states (cleared_floor flag
    distinguishes qualifying states). Ordered by rank (ascending).

    Spec reference: Section VI.1 — LOCKED
    \"\"\"
    floors = compute_signal_floors(noise_baseline)
    result = []
    for r in rankings:
        sid = r.state_id
        profile = STATE_PROFILES.get(sid)
        baseline = noise_baseline.get(sid, 0.0)
        floor = floors.get(sid, 0.0)
        cleared = r.score > floor
        lift = ((r.score / baseline) - 1.0) * 100.0 if baseline > 0.0 else 0.0
        result.append(QualifiedState(
            rank=r.rank,
            state_id=sid,
            state_name=profile.state_name if profile else sid,
            score=r.score,
            noise_baseline=baseline,
            signal_floor=floor,
            cleared_floor=cleared,
            score_lift_pct=lift,
            resolution_family=profile.resolution_family if profile else "",
        ))
    return result""",
        new="""def apply_signal_floor(
    rankings: list,
    noise_baseline: Optional[dict] = None,
) -> list:
    \"\"\"
    Evaluate all ranked states against the SCD-WCS absolute alignment threshold.

    State clears floor if score > SCD_WCS_ALIGNMENT_THRESHOLD (0.25).
    noise_baseline: optional dict used only for score_lift_pct computation.
      If None, uses _PRECOMPUTED_NOISE_BASELINE.

    Returns list[QualifiedState] for ALL ranked states (cleared_floor flag
    distinguishes qualifying states). Ordered by rank (ascending).

    Spec reference: Section VI.1 — v21 absolute threshold
    \"\"\"
    baseline_map = noise_baseline if noise_baseline is not None else _PRECOMPUTED_NOISE_BASELINE
    session_scores = {r.state_id: r.score for r in rankings}
    result = []
    for r in rankings:
        sid = r.state_id
        profile = STATE_PROFILES.get(sid)
        baseline = baseline_map.get(sid, 0.0)
        cleared = check_signal_gate(sid, session_scores)
        lift = ((r.score / baseline) - 1.0) * 100.0 if baseline > 0.0 else 0.0
        result.append(QualifiedState(
            rank=r.rank,
            state_id=sid,
            state_name=profile.state_name if profile else sid,
            score=r.score,
            noise_baseline=baseline,
            signal_floor=SCD_WCS_ALIGNMENT_THRESHOLD,
            cleared_floor=cleared,
            score_lift_pct=lift,
            resolution_family=profile.resolution_family if profile else "",
        ))
    return result""",
        label="update apply_signal_floor() -- absolute threshold, optional noise_baseline",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("apply_signal_floor() body")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    if errors:
        print(f"ERRORS ({len(errors)}) -- patch NOT applied:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        mode = "DRY-RUN" if dry_run else "WRITTEN"
        print(f"All 4 patches {mode} successfully. 1 file affected: engine/output.py")
        if dry_run:
            print("Run with --write to apply.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
