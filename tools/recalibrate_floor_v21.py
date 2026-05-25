"""
PRV3 Signal Floor Recalibration — v21 SCD-WCS (Session 24)

Extended to capture per-state mean AND std_dev for statistical floor design.

SCD-WCS: Session vector displaced by MC_CENTROID_39 * (N/39). Profile undisplaced.

N=1000, seed=42, Q01-Q39 (39 questions per simulation). Full 47-state path.

Output: full per-state mean/std_dev table + k=2.33 floor values.
Pete reviews this output before any engine/output.py changes.

Hard stop conditions:
  - Global mean is negative → stop, report
  - All std_devs are zero (no variance) → stop, report

Usage:
  python tools/recalibrate_floor_v21.py
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import _build_library
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.salience import SALIENCE_PROFILES
from engine.accumulation import rank_states

N_SIMULATIONS = 1000
RANDOM_SEED = 42
K_FACTOR = 2.33  # 99th percentile of normal distribution


def run_recalibration(question_ids):
    """
    Run N_SIMULATIONS noise simulations. Return per-state (mean, std_dev) dict.
    Tracks per-simulation scores per state for variance computation.
    """
    random.seed(RANDOM_SEED)
    lib = _build_library()

    # Collect per-simulation scores per state
    score_lists = {sid: [] for sid in STATE_PROFILES}

    for _ in range(N_SIMULATIONS):
        accumulated = {f: 0.0 for f in DIMENSIONAL_FIELDS}
        for qid in question_ids:
            q = lib.get(qid)
            if q is None or not q.answer_options:
                continue
            option = random.choice(q.answer_options)
            for f in DIMENSIONAL_FIELDS:
                accumulated[f] += option.dimensional_contributions.get(f, 0.0)
        rankings = rank_states(accumulated, len(question_ids), SALIENCE_PROFILES)
        for r in rankings:
            score_lists[r.state_id].append(r.score)

    # Compute per-state mean and population std_dev
    result = {}
    for sid, scores in score_lists.items():
        n = len(scores)
        mean = sum(scores) / n
        variance = sum((s - mean) ** 2 for s in scores) / n
        std_dev = math.sqrt(variance)
        result[sid] = {"mean": mean, "std_dev": std_dev}

    return result


if __name__ == "__main__":
    question_ids = [f"Q{i:02d}" for i in range(1, 40)]
    stats = run_recalibration(question_ids)

    # Aggregate stats
    all_means = [v["mean"] for v in stats.values()]
    all_stds = [v["std_dev"] for v in stats.values()]
    global_mean = sum(all_means) / len(all_means)
    global_std = sum(all_stds) / len(all_stds)

    # k=2.33 floor per state
    floors = {sid: stats[sid]["mean"] + K_FACTOR * stats[sid]["std_dev"]
              for sid in stats}
    floor_values = list(floors.values())
    n_negative_floors = sum(1 for f in floor_values if f < 0.0)

    print(f"\nPRV3 -- SCD-WCS Noise Baseline v21")
    print(f"N={N_SIMULATIONS}, seed={RANDOM_SEED}, Q01-Q39, SCD-WCS + SALIENCE_PROFILES")
    print(f"=" * 72)
    print(f"\n{'State':<44} {'Mean':>8}  {'Std Dev':>8}  {'Floor(k=2.33)':>14}")
    print(f"{'-' * 44} {'-' * 8}  {'-' * 8}  {'-' * 14}")
    for sid in sorted(stats.keys()):
        m = stats[sid]["mean"]
        s = stats[sid]["std_dev"]
        f = floors[sid]
        neg_flag = " ***" if f < 0.0 else ""
        print(f"  {sid:<42} {m:>8.4f}  {s:>8.4f}  {f:>14.4f}{neg_flag}")

    print(f"\n{'Global mean:':<30} {global_mean:.4f}")
    print(f"{'Global mean std_dev:':<30} {global_std:.4f}")
    print(f"{'k=2.33 floor range:':<30} {min(floor_values):.4f} -- {max(floor_values):.4f}")
    print(f"{'Negative floor states:':<30} {n_negative_floors}")

    # Hard stop checks
    print(f"\nHard stop checks:")
    stop = False
    if global_mean < 0.0:
        print(f"  [HARD STOP] Global mean is negative ({global_mean:.4f}). Report to Pete.")
        stop = True
    else:
        print(f"  Global mean: {global_mean:.4f} (positive, OK)")

    if all(s == 0.0 for s in all_stds):
        print(f"  [HARD STOP] All std_devs are zero -- no variance in noise distribution.")
        stop = True
    else:
        nonzero = sum(1 for s in all_stds if s > 0.0)
        print(f"  Std_devs: {nonzero}/47 non-zero (OK)")

    if stop:
        sys.exit(1)

    print(f"\n-- Report complete. Return this table to Pete before any engine/output.py changes. --")

    # Emit the _SCD_WCS_NOISE_MAP block for reference
    print(f"\n_SCD_WCS_NOISE_MAP block (for patch_v21_floor_system.py):")
    print(f"_SCD_WCS_NOISE_MAP = {{")
    for sid in sorted(stats.keys()):
        m = stats[sid]["mean"]
        s = stats[sid]["std_dev"]
        print(f'    "{sid}":{" " * (44 - len(sid))}{{"mean": {m:.6f}, "std_dev": {s:.6f}}},')
    print(f"}}")
