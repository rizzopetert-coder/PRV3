"""
PRV3 Signal Floor Recalibration — v20 (Session 23)

Recomputes noise baseline using the Two-Tier Hierarchical Router path.
N=1000, seed=42, Q01-Q39. Read-and-report only — does not modify engine/output.py.

Dimension-conditional Monte Carlo:
  For each simulation run, identify_dominant_dimension() is called on the
  accumulated random vector. rank_states() is then called with that dominant_dimension,
  producing router-filtered scores. Each state's baseline is computed as the mean of
  its cosine similarity score across runs where the router would have selected
  that state's primary_dimension — i.e., runs where the state was actually competing.

  States in dimensions that never dominate in N runs receive 0.0 (flagged).

This matches the router path used by run_profile() in calibration_runner.py.
Non-router path (dominant_dimension=None) is no longer the calibration path for v20+.

Run after v20 router implementation write. Router changes which states compete
per profile, which changes the effective noise baseline per state.

Usage:
  python tools/recalibrate_floor_v20.py
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import _build_library
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.salience import SALIENCE_PROFILES
from engine.accumulation import rank_states, identify_dominant_dimension

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
    score_counts = {sid: 0   for sid in STATE_PROFILES}
    dim_counts   = {}  # how many runs each dimension was dominant

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

        dominant_dim, _ = identify_dominant_dimension(accumulated)
        dim_counts[dominant_dim] = dim_counts.get(dominant_dim, 0) + 1

        # Router-filtered ranking — only states in dominant_dim compete
        rankings = rank_states(accumulated, SALIENCE_PROFILES, dominant_dim)
        for r in rankings:
            score_totals[r.state_id] += r.score
            score_counts[r.state_id] += 1

    # Dimension-conditional mean: score only from eligible runs
    noise_baseline = {}
    for sid in STATE_PROFILES:
        count = score_counts[sid]
        noise_baseline[sid] = score_totals[sid] / count if count > 0 else 0.0

    return noise_baseline, score_counts, dim_counts


if __name__ == "__main__":
    question_ids = [f"Q{i:02d}" for i in range(1, 40)]
    baseline, score_counts, dim_counts = run_recalibration(question_ids)

    mean_baseline = sum(baseline.values()) / len(baseline)
    min_val = min(baseline.values())
    max_val = max(baseline.values())

    shifted = {
        sid: (baseline[sid], V19_BASELINE.get(sid, 0.0),
              baseline[sid] - V19_BASELINE.get(sid, 0.0))
        for sid in baseline
        if abs(baseline[sid] - V19_BASELINE.get(sid, 0.0)) > 0.005
    }

    zero_obs = [sid for sid, v in baseline.items() if v == 0.0]

    print(f"\nSignal Floor Recalibration — v20 (two-tier router, Session 23)")
    print(f"=" * 64)
    print(f"Simulations:       {N_SIMULATIONS}")
    print(f"Random seed:       {RANDOM_SEED}")
    print(f"Questions sampled: Q01-Q39 ({len(question_ids)} questions)")
    print(f"Metric:            Weighted cosine (SALIENCE_PROFILES) + router filter")
    print(f"\nDimension dominance distribution ({N_SIMULATIONS} runs):")
    for dim in ["Authority", "Aptitude", "Alliance", "Attitude"]:
        n = dim_counts.get(dim, 0)
        states_in_dim = sum(1 for p in STATE_PROFILES.values() if p.primary_dimension == dim)
        print(f"  {dim:<12} dominant in {n:4d} runs  ({n/N_SIMULATIONS*100:.1f}%)  "
              f"{states_in_dim} states competing")

    print(f"\nAggregate results:")
    v19_mean = sum(V19_BASELINE.values()) / len(V19_BASELINE)
    print(f"  v19 mean baseline: {v19_mean:.4f}")
    print(f"  v20 mean baseline: {mean_baseline:.4f}")
    print(f"  v20 range:         {min_val:.4f} - {max_val:.4f}")

    print(f"\nKey state deltas (v19 -> v20):")
    for sid in ["culture_drift", "the_uninitiated", "the_overloaded_manager",
                "heard_and_ignored", "the_exposed", "the_founders_grip"]:
        v20 = baseline.get(sid, 0.0)
        v19 = V19_BASELINE.get(sid, 0.0)
        n = score_counts.get(sid, 0)
        print(f"  {sid:<44} v19={v19:.4f}  v20={v20:.4f}  delta={v20-v19:+.4f}  n={n}")

    if zero_obs:
        print(f"\n[WARN] States with 0 observations (no eligible runs): {zero_obs}")

    print(f"\nStates shifted >0.005 from v19 ({len(shifted)} states):")
    if shifted:
        for sid in sorted(shifted.keys()):
            v20, v19, delta = shifted[sid]
            n = score_counts.get(sid, 0)
            sign = "+" if delta >= 0 else ""
            print(f"  {sid:<45} v19={v19:.4f}  v20={v20:.4f}  delta={sign}{delta:.4f}  n={n}")
    else:
        print("  None")

    print(f"\nObservation counts per state (runs where state's dim was dominant):")
    for dim in ["Authority", "Aptitude", "Alliance", "Attitude"]:
        sids = sorted(sid for sid, p in STATE_PROFILES.items() if p.primary_dimension == dim)
        n_runs = dim_counts.get(dim, 0)
        print(f"  [{dim} — {n_runs} runs]")
        for sid in sids:
            print(f"    {sid:<45} n={score_counts[sid]}")

    print(f"\nFull per-state v20 baseline (for engine/output.py update):")
    print(f"_PRECOMPUTED_NOISE_BASELINE: dict = {{")
    for sid in sorted(baseline.keys()):
        print(f'    "{sid}":{" " * (45 - len(sid))}{baseline[sid]:.4f},')
    print(f"}}")
