"""
PRV3 Signal Floor Recalibration — v18 (Session 23)

Recomputes noise baseline in weighted cosine space using SALIENCE_PROFILES.
N=1000, seed=42, Q01-Q39. Read-and-report only — does not modify engine/output.py.

Run after v18 three-tier salience write. Salience changes alter SALIENCE_PROFILES
weights, which changes the weighted cosine scores produced by rank_states().
The new baseline must be captured before running Phase 2 calibration.

Usage:
  python tools/recalibrate_floor_v18.py
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

# v17 baseline for delta reporting
V17_BASELINE = {
    "built_to_fail":                        0.8274,
    "culture_drift":                        0.9318,
    "decision_blindness":                   0.7363,
    "decision_paralysis":                   0.9439,
    "dueling_narratives":                   0.9439,
    "groundhog_day":                        0.9198,
    "heard_and_ignored":                    0.9147,
    "hr_capture":                           0.9147,
    "identity_erosion":                     0.9020,
    "invisible_burnout":                    0.9198,
    "invisible_influence_architecture":     0.9163,
    "leadership_continuity_risk":           0.9439,
    "leadership_deafness":                  0.9020,
    "narrative_lock":                       0.9020,
    "paper_shield":                         0.9163,
    "pay_exposure":                         0.9439,
    "silosolation":                         0.7840,
    "the_arbitrary_standard":               0.7840,
    "the_basement_standard":                0.9198,
    "the_broken_compass":                   0.9198,
    "the_burned_credibility":               0.9198,
    "the_culture_that_wasnt":               0.9020,
    "the_diversity_ceiling":                0.9198,
    "the_dormant_talent":                   0.8955,
    "the_exposed":                          0.9147,
    "the_founders_grip":                    0.9147,
    "the_fracture":                         0.7363,
    "the_inside_track":                     0.9198,
    "the_lost_map":                         0.9439,
    "the_overloaded_manager":               0.8988,
    "the_paper_tiger":                      0.8274,
    "the_pay_fog":                          0.9439,
    "the_policy_lag":                       0.9439,
    "the_second_close":                     0.7840,
    "the_suppression_filter":               0.8487,
    "the_tolerated_violation":              0.9147,
    "the_undefined_role":                   0.8668,
    "the_unexamined_algorithm":             0.9488,
    "the_unformed_leader":                  0.8955,
    "the_uninitiated":                      0.9439,
    "the_unlocked_door":                    0.9020,
    "the_unreported_hazard":                0.9020,
    "the_unsolved_problem":                 0.9147,
    "the_untouchable":                      0.8936,
    "the_wrong_reward":                     0.9198,
    "transition_paralysis":                 0.9439,
    "what_nobody_says":                     0.9020,
}


def run_recalibration(question_ids):
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
                val = option.dimensional_contributions.get(f, 0.0)
                accumulated[f] += val
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
        sid: (baseline[sid], V17_BASELINE.get(sid, 0.0),
              baseline[sid] - V17_BASELINE.get(sid, 0.0))
        for sid in baseline
        if abs(baseline[sid] - V17_BASELINE.get(sid, 0.0)) > 0.005
    }

    print(f"\nSignal Floor Recalibration — v18 (weighted cosine, Session 23)")
    print(f"=" * 64)
    print(f"Simulations:       {N_SIMULATIONS}")
    print(f"Random seed:       {RANDOM_SEED}")
    print(f"Questions sampled: Q01-Q39 ({len(question_ids)} questions)")
    print(f"Metric:            Weighted cosine (SALIENCE_PROFILES)")
    print(f"\nAggregate results:")
    print(f"  v17 mean baseline: {sum(V17_BASELINE.values()) / len(V17_BASELINE):.4f}")
    print(f"  v18 mean baseline: {mean_baseline:.4f}")
    print(f"  v18 range:         {min_val:.4f} - {max_val:.4f}")
    print(f"\nculture_drift: v17={V17_BASELINE.get('culture_drift', 0):.4f}  "
          f"v18={baseline.get('culture_drift', 0):.4f}  "
          f"delta={baseline.get('culture_drift', 0) - V17_BASELINE.get('culture_drift', 0):+.4f}")
    print(f"the_uninitiated: v17={V17_BASELINE.get('the_uninitiated', 0):.4f}  "
          f"v18={baseline.get('the_uninitiated', 0):.4f}  "
          f"delta={baseline.get('the_uninitiated', 0) - V17_BASELINE.get('the_uninitiated', 0):+.4f}")
    print(f"\nStates shifted >0.005 from v17 ({len(shifted)} states):")
    if shifted:
        for sid in sorted(shifted.keys()):
            v18, v17, delta = shifted[sid]
            sign = "+" if delta >= 0 else ""
            print(f"  {sid:<45} v17={v17:.4f}  v18={v18:.4f}  delta={sign}{delta:.4f}")
    else:
        print("  None")

    print(f"\nFull per-state v18 baseline (for engine/output.py update):")
    print(f"_PRECOMPUTED_NOISE_BASELINE: dict = {{")
    for sid in sorted(baseline.keys()):
        print(f'    "{sid}":{" " * (45 - len(sid))}{baseline[sid]:.4f},')
    print(f"}}")
