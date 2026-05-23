"""
PRV3 Signal Floor Recalibration — v15 (Session 22)

Recomputes the noise baseline in weighted cosine space using SALIENCE_PROFILES.
N=1000, seed=42, Q01-Q39. Read-and-report only — does not modify engine/output.py.

Run after Steps 1-3 (authority drain + state_targets purge + Q06 Paper Tiger fix).

Usage:
  python tools/recalibrate_floor_v15.py
"""

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

# v14 baseline for delta reporting
V14_BASELINE = {
    "built_to_fail":                        0.7780,
    "culture_drift":                        0.8962,
    "decision_blindness":                   0.6852,
    "decision_paralysis":                   0.9659,
    "dueling_narratives":                   0.9659,
    "groundhog_day":                        0.8879,
    "heard_and_ignored":                    0.9589,
    "hr_capture":                           0.9589,
    "identity_erosion":                     0.8778,
    "invisible_burnout":                    0.8879,
    "invisible_influence_architecture":     0.9096,
    "leadership_continuity_risk":           0.9659,
    "leadership_deafness":                  0.8778,
    "narrative_lock":                       0.8778,
    "paper_shield":                         0.9096,
    "pay_exposure":                         0.9659,
    "silosolation":                         0.7384,
    "the_arbitrary_standard":               0.7384,
    "the_basement_standard":                0.8879,
    "the_broken_compass":                   0.8879,
    "the_burned_credibility":               0.8879,
    "the_culture_that_wasnt":               0.8778,
    "the_diversity_ceiling":                0.8879,
    "the_dormant_talent":                   0.8733,
    "the_exposed":                          0.9589,
    "the_founders_grip":                    0.9589,
    "the_fracture":                         0.6852,
    "the_inside_track":                     0.8879,
    "the_lost_map":                         0.9659,
    "the_overloaded_manager":               0.8561,
    "the_paper_tiger":                      0.7780,
    "the_pay_fog":                          0.9659,
    "the_policy_lag":                       0.9659,
    "the_second_close":                     0.7384,
    "the_suppression_filter":               0.8072,
    "the_tolerated_violation":              0.9589,
    "the_undefined_role":                   0.8242,
    "the_unexamined_algorithm":             0.9612,
    "the_unformed_leader":                  0.8733,
    "the_uninitiated":                      0.9659,
    "the_unlocked_door":                    0.8778,
    "the_unreported_hazard":                0.8778,
    "the_unsolved_problem":                 0.9589,
    "the_untouchable":                      0.8560,
    "the_wrong_reward":                     0.8879,
    "transition_paralysis":                 0.9659,
    "what_nobody_says":                     0.8778,
}


def run_recalibration(question_ids):
    """
    Monte Carlo in weighted cosine space.
    Returns noise_baseline dict: {state_id: mean_weighted_cosine_score}.
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
        rankings = rank_states(accumulated, SALIENCE_PROFILES)
        for r in rankings:
            score_totals[r.state_id] += r.score

    noise_baseline = {sid: score_totals[sid] / N_SIMULATIONS for sid in STATE_PROFILES}
    return noise_baseline


if __name__ == "__main__":
    question_ids = [f"Q{i:02d}" for i in range(1, 40)]
    baseline = run_recalibration(question_ids)

    mean_baseline = sum(baseline.values()) / len(baseline)
    min_val = min(baseline.values())
    max_val = max(baseline.values())

    shifted = {
        sid: (baseline[sid], V14_BASELINE.get(sid, 0.0),
              baseline[sid] - V14_BASELINE.get(sid, 0.0))
        for sid in baseline
        if abs(baseline[sid] - V14_BASELINE.get(sid, 0.0)) > 0.01
    }

    print(f"\nSignal Floor Recalibration — v15 (weighted cosine, Session 22)")
    print(f"=" * 64)
    print(f"Simulations:       {N_SIMULATIONS}")
    print(f"Random seed:       {RANDOM_SEED}")
    print(f"Questions sampled: Q01-Q39 ({len(question_ids)} questions)")
    print(f"Metric:            Weighted cosine (SALIENCE_PROFILES)")
    print(f"\nAggregate results:")
    print(f"  v14 mean baseline: {sum(V14_BASELINE.values()) / len(V14_BASELINE):.4f}")
    print(f"  v15 mean baseline: {mean_baseline:.4f}")
    print(f"  v15 range:         {min_val:.4f} - {max_val:.4f}")
    print(f"\nStates shifted >0.01 from v14 ({len(shifted)} states):")
    if shifted:
        for sid in sorted(shifted.keys()):
            v15, v14, delta = shifted[sid]
            sign = "+" if delta >= 0 else ""
            print(f"  {sid:<45} v14={v14:.4f}  v15={v15:.4f}  delta={sign}{delta:.4f}")
    else:
        print("  None")

    print(f"\nFull per-state v15 baseline (for engine/output.py update):")
    print(f"_PRECOMPUTED_NOISE_BASELINE: dict = {{")
    for sid in sorted(baseline.keys()):
        print(f'    "{sid}":{" " * (45 - len(sid))}{baseline[sid]:.4f},')
    print(f"}}")
