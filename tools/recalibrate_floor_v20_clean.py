"""
PRV3 Signal Floor Recalibration — v20 clean (Session 23)

Full 47-state path (no router). Correct baseline for v20 engine state:
  states.py: reverted (the_uninitiated 0.45/0.15, six HIGH Authority 0.60/0.10)
  salience.py: reverted (culture_drift attitude 2.5)
  questions.py: Q20 C/D at 0.80 (retained from v19)
  accumulation.py: full 47-state rank_states() — no router

N=1000, seed=42, Q01-Q39. Read-and-report only.

Usage:
  python tools/recalibrate_floor_v20_clean.py
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

# v19 baseline for delta reporting
V19_BASELINE = {
    "built_to_fail":                        0.8333,
    "culture_drift":                        0.9261,
    "decision_blindness":                   0.7346,
    "decision_paralysis":                   0.9432,
    "dueling_narratives":                   0.9432,
    "groundhog_day":                        0.9188,
    "heard_and_ignored":                    0.8751,
    "hr_capture":                           0.8751,
    "identity_erosion":                     0.9129,
    "invisible_burnout":                    0.9188,
    "invisible_influence_architecture":     0.9332,
    "leadership_continuity_risk":           0.9432,
    "leadership_deafness":                  0.8960,
    "narrative_lock":                       0.9129,
    "paper_shield":                         0.9332,
    "pay_exposure":                         0.9432,
    "silosolation":                         0.7826,
    "the_arbitrary_standard":               0.7826,
    "the_basement_standard":                0.9188,
    "the_broken_compass":                   0.9188,
    "the_burned_credibility":               0.9188,
    "the_culture_that_wasnt":               0.9129,
    "the_diversity_ceiling":                0.9188,
    "the_dormant_talent":                   0.8943,
    "the_exposed":                          0.8751,
    "the_founders_grip":                    0.8751,
    "the_fracture":                         0.7346,
    "the_inside_track":                     0.9188,
    "the_lost_map":                         0.9432,
    "the_overloaded_manager":               0.8961,
    "the_paper_tiger":                      0.8333,
    "the_pay_fog":                          0.9432,
    "the_policy_lag":                       0.9432,
    "the_second_close":                     0.7826,
    "the_suppression_filter":               0.8279,
    "the_tolerated_violation":              0.8751,
    "the_undefined_role":                   0.8710,
    "the_unexamined_algorithm":             0.9433,
    "the_unformed_leader":                  0.8943,
    "the_uninitiated":                      0.9339,
    "the_unlocked_door":                    0.9129,
    "the_unreported_hazard":                0.9129,
    "the_unsolved_problem":                 0.8751,
    "the_untouchable":                      0.8923,
    "the_wrong_reward":                     0.9188,
    "transition_paralysis":                 0.9432,
    "what_nobody_says":                     0.8653,
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
                accumulated[f] += option.dimensional_contributions.get(f, 0.0)
        rankings = rank_states(accumulated, SALIENCE_PROFILES)
        for r in rankings:
            score_totals[r.state_id] += r.score

    return {sid: score_totals[sid] / N_SIMULATIONS for sid in STATE_PROFILES}


if __name__ == "__main__":
    question_ids = [f"Q{i:02d}" for i in range(1, 40)]
    baseline = run_recalibration(question_ids)

    mean_baseline = sum(baseline.values()) / len(baseline)
    v19_mean = sum(V19_BASELINE.values()) / len(V19_BASELINE)

    shifted = {
        sid: (baseline[sid], V19_BASELINE.get(sid, 0.0),
              baseline[sid] - V19_BASELINE.get(sid, 0.0))
        for sid in baseline
        if abs(baseline[sid] - V19_BASELINE.get(sid, 0.0)) > 0.0005
    }

    print(f"\nSignal Floor Recalibration — v20 clean (full 47-state path, Session 23)")
    print(f"=" * 64)
    print(f"Simulations:       {N_SIMULATIONS}")
    print(f"Random seed:       {RANDOM_SEED}")
    print(f"Questions sampled: Q01-Q39 ({len(question_ids)} questions)")
    print(f"Engine state:      states.py reverted + salience.py reverted + Q20 0.80")
    print(f"Metric:            Weighted cosine (SALIENCE_PROFILES), full 47-state path")
    print(f"\nAggregate:")
    print(f"  v19 mean: {v19_mean:.4f}  |  v20 clean mean: {mean_baseline:.4f}  |  delta: {mean_baseline - v19_mean:+.4f}")
    print(f"  range: {min(baseline.values()):.4f} – {max(baseline.values()):.4f}")

    print(f"\nKey states (v19 -> v20 clean):")
    for sid in ["culture_drift", "the_uninitiated", "heard_and_ignored",
                "the_exposed", "the_founders_grip", "the_overloaded_manager"]:
        v = baseline[sid]
        p = V19_BASELINE.get(sid, 0.0)
        print(f"  {sid:<44} v19={p:.4f}  v20={v:.4f}  delta={v-p:+.4f}")

    print(f"\nAll shifted states (delta > 0.0005, {len(shifted)} states):")
    for sid in sorted(shifted.keys()):
        v20, v19, delta = shifted[sid]
        sign = "+" if delta >= 0 else ""
        print(f"  {sid:<45} v19={v19:.4f}  v20={v20:.4f}  delta={sign}{delta:.4f}")

    print(f"\nFull per-state v20 clean baseline (for engine/output.py update):")
    print(f"_PRECOMPUTED_NOISE_BASELINE: dict = {{")
    for sid in sorted(baseline.keys()):
        print(f'    "{sid}":{" " * (45 - len(sid))}{baseline[sid]:.4f},')
    print(f"}}")
