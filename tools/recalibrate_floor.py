"""
PRV3 Signal Floor Recalibration — Session 16

Recomputes the noise baseline via Monte Carlo against the current library
(Q01–Q39, _opt_contrib-populated). Reports per-state floors for Pete's
confirmation before any engine writes.

Does not modify engine/output.py. Read-and-report only.
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import _build_library
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.accumulation import rank_states

SIGNAL_FLOOR_MULTIPLIER = 1.15  # locked
N_SIMULATIONS = 1000
RANDOM_SEED = 42


def run_recalibration(question_ids):
    """
    question_ids: list of question_id strings to sample from (Q01–Q39 per Gemini spec).
    Returns (noise_baseline dict, signal_floors dict).
    """
    random.seed(RANDOM_SEED)
    lib = _build_library()

    score_totals = {sid: 0.0 for sid in STATE_PROFILES}

    for _ in range(N_SIMULATIONS):
        accumulated = {f: 0.0 for f in DIMENSIONAL_FIELDS}
        for qid in question_ids:
            q = lib.get(qid)
            if q is None or not q.answer_options:
                continue
            option = random.choice(q.answer_options)
            for f in DIMENSIONAL_FIELDS:
                accumulated[f] += option.dimensional_contributions.get(f, 0.0)
        rankings = rank_states(accumulated)
        for r in rankings:
            score_totals[r.state_id] += r.score

    noise_baseline = {sid: score_totals[sid] / N_SIMULATIONS for sid in STATE_PROFILES}
    signal_floors = {sid: v * SIGNAL_FLOOR_MULTIPLIER for sid, v in noise_baseline.items()}
    return noise_baseline, signal_floors


if __name__ == "__main__":
    question_ids = [f"Q{i:02d}" for i in range(1, 40)]  # Q01–Q39
    baseline, floors = run_recalibration(question_ids)

    mean_baseline = sum(baseline.values()) / len(baseline)
    mean_floor = sum(floors.values()) / len(floors)
    min_floor = min(floors.values())
    max_floor = max(floors.values())

    print(f"\nSignal Floor Recalibration — Session 16")
    print(f"========================================")
    print(f"Simulations:       {N_SIMULATIONS}")
    print(f"Random seed:       {RANDOM_SEED}")
    print(f"Questions sampled: Q01–Q39 ({len(question_ids)} questions)")
    print(f"\nAggregate results:")
    print(f"  Old floor (MOB reference):  0.6737")
    print(f"  New mean noise baseline:    {mean_baseline:.4f}")
    print(f"  New mean signal floor:      {mean_floor:.4f}  (baseline × 1.15)")
    print(f"  Floor range:                {min_floor:.4f} – {max_floor:.4f}")
    print(f"\nPer-state floors (all 47 states):")
    for sid in sorted(floors.keys()):
        name = STATE_PROFILES[sid].state_name if sid in STATE_PROFILES else sid
        b = baseline[sid]
        f = floors[sid]
        print(f"  {sid:<45} baseline={b:.4f}  floor={f:.4f}")
