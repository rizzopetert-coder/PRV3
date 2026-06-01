"""
PRV3 — Accumulated Vector Centroid Diagnostic (Session 24)

Captures the raw 8-field accumulated vector at the point just before
rank_states() is called, for each of N=1000 noise simulations.

Computes per-field mean and std dev across all simulations.
Used to verify Gemini's Orthant Centroid Displacement proposal.

No engine files are modified. Read-only diagnostic.

Usage:
  python tools/diag_v21_accumulated_centroid.py
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import _build_library
from engine.data.states import DIMENSIONAL_FIELDS

N_SIMULATIONS = 1000
RANDOM_SEED = 42

FIELDS = [
    "aptitude_liability",
    "aptitude_asset",
    "authority_liability",
    "authority_asset",
    "alliance_liability",
    "alliance_asset",
    "attitude_liability",
    "attitude_asset",
]


def run_centroid_diagnostic(question_ids):
    random.seed(RANDOM_SEED)
    lib = _build_library()

    all_vectors = []

    for _ in range(N_SIMULATIONS):
        accumulated = {f: 0.0 for f in DIMENSIONAL_FIELDS}
        for qid in question_ids:
            q = lib.get(qid)
            if q is None or not q.answer_options:
                continue
            option = random.choice(q.answer_options)
            for f in DIMENSIONAL_FIELDS:
                accumulated[f] += option.dimensional_contributions.get(f, 0.0)
        all_vectors.append({f: accumulated[f] for f in FIELDS})

    # per-field mean
    means = {}
    for f in FIELDS:
        means[f] = sum(v[f] for v in all_vectors) / N_SIMULATIONS

    # per-field std dev (population)
    stds = {}
    for f in FIELDS:
        variance = sum((v[f] - means[f]) ** 2 for v in all_vectors) / N_SIMULATIONS
        stds[f] = math.sqrt(variance)

    return means, stds


if __name__ == "__main__":
    question_ids = [f"Q{i:02d}" for i in range(1, 40)]
    means, stds = run_centroid_diagnostic(question_ids)

    print(f"\nPRV3 — Accumulated Vector Centroid Diagnostic")
    print(f"N={N_SIMULATIONS}, seed={RANDOM_SEED}, Q01–Q39, v20 clean baseline")
    print(f"=" * 60)
    print(f"\n{'Field':<28} {'Mean':>8}  {'Std Dev':>8}")
    print(f"{'-' * 28} {'-' * 8}  {'-' * 8}")
    for f in FIELDS:
        print(f"  {f:<26} {means[f]:>8.4f}  {stds[f]:>8.4f}")

    all_means = list(means.values())
    global_mean = sum(all_means) / len(all_means)
    max_field = max(means, key=means.get)
    min_field = min(means, key=means.get)

    print(f"\n{'Global mean (all fields):':<30} {global_mean:.4f}")
    print(f"{'Max field mean:':<30} {means[max_field]:.4f}  ({max_field})")
    print(f"{'Min field mean:':<30} {means[min_field]:.4f}  ({min_field})")
    print(f"{'Max/min ratio:':<30} {means[max_field] / means[min_field]:.3f}x")
    print(f"{'Gemini proposed centroid:':<30} 0.1500")
    print(f"{'Delta from Gemini centroid:':<30} {global_mean - 0.15:+.4f}")

    print(f"\nDimensional skew check (liability means):")
    for dim in ["aptitude", "authority", "alliance", "attitude"]:
        f = f"{dim}_liability"
        delta = means[f] - global_mean
        print(f"  {f:<28} {means[f]:.4f}  (delta from global mean: {delta:+.4f})")
