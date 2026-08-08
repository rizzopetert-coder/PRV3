"""
PRV3 — Accumulated Vector Centroid Diagnostic (Session 24; MC_CENTROID_39
recalibration Step 2, this session)

Captures the raw 8-field accumulated vector at the point just before
rank_states() is called, for each of N=1000 noise simulations.

Computes per-field mean and std dev across all simulations.
Originally used to verify Gemini's Orthant Centroid Displacement proposal;
reused this session to regenerate MC_CENTROID_39 against the expanded
live question sequence (Q40-Q51 added, 32 -> 44).

No engine files are modified. Read-only diagnostic.

QUESTION SOURCE, changed this session: reads PHASE_1_QUESTION_SEQUENCE
directly out of web/lib/session-store.ts (regex-extracted at run time,
not hand-transcribed) rather than regenerating a nominal "Q01..Q39" range.
The original range-based approach silently under-counted -- "Q03" and
"Q27" were never real QUESTION_LIBRARY keys (only "Q03A"/"Q03B" and
"Q27A"/"Q27B" are), so the original MC_CENTROID_39 was actually built
from 37 real questions per simulation, not 39, despite the name. Reading
the real live sequence directly avoids reintroducing that class of gap,
and every extracted ID is validated against QUESTION_LIBRARY before the
simulation runs -- fails loudly on a mismatch rather than silently
skipping, unlike the original.

Usage:
  python tools/diag_v21_accumulated_centroid.py
"""

import math
import random
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(REPO_ROOT))

from engine.data.questions import _build_library
from engine.data.states import DIMENSIONAL_FIELDS

N_SIMULATIONS = 1000
RANDOM_SEED = 42

SESSION_STORE_PATH = REPO_ROOT / "web" / "lib" / "session-store.ts"

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


def load_live_question_sequence() -> list[str]:
    """
    Extract PHASE_1_QUESTION_SEQUENCE directly from web/lib/session-store.ts
    (the real, live source of truth), rather than hand-transcribing a copy
    that could drift. Validates every extracted ID resolves to a real
    QUESTION_LIBRARY entry with real answer_options -- aborts loudly on any
    mismatch instead of silently skipping (the bug found in the original
    Q01-Q39 range-based approach, which silently dropped Q03/Q27).
    """
    text = SESSION_STORE_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"PHASE_1_QUESTION_SEQUENCE:\s*readonly string\[\]\s*=\s*\[(.*?)\];",
        text,
        re.DOTALL,
    )
    if not match:
        raise RuntimeError(
            f"PHASE_1_QUESTION_SEQUENCE pattern not found in {SESSION_STORE_PATH}"
        )
    ids = re.findall(r'"([A-Z0-9]+)"', match.group(1))
    if not ids:
        raise RuntimeError("PHASE_1_QUESTION_SEQUENCE matched but no IDs extracted")

    lib = _build_library()
    missing = [qid for qid in ids if lib.get(qid) is None or not lib[qid].answer_options]
    if missing:
        raise RuntimeError(
            f"PHASE_1_QUESTION_SEQUENCE contains IDs with no valid QUESTION_LIBRARY "
            f"entry: {missing} -- aborting rather than silently skipping them"
        )
    return ids


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
    question_ids = load_live_question_sequence()
    means, stds = run_centroid_diagnostic(question_ids)

    print(f"\nPRV3 — Accumulated Vector Centroid Diagnostic")
    print(f"N={N_SIMULATIONS}, seed={RANDOM_SEED}, "
          f"{len(question_ids)} live questions from PHASE_1_QUESTION_SEQUENCE "
          f"(web/lib/session-store.ts, read live)")
    print(f"Question IDs: {question_ids}")
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
