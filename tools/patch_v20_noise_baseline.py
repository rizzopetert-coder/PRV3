"""
Patch: engine/output.py — update _PRECOMPUTED_NOISE_BASELINE to v20 values.

v20: Two-Tier Hierarchical Router. Dimension-conditional Monte Carlo.
N=1000, seed=42, Q01-Q39. Session 23, 2026-05-24.

Alliance states (decision_blindness, silosolation, the_arbitrary_standard,
the_fracture, the_second_close, the_suppression_filter): 0.0000 — Alliance
never dominant in random noise. Floor = 0.0 (always clears when router selects).

Aptitude states: based on 5 observations only (Aptitude dominant in 5/1000 runs).

Usage:
  python tools/patch_v20_noise_baseline.py --dry-run
  python tools/patch_v20_noise_baseline.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "output.py"

OLD = (
    '# Precomputed noise baseline — Monte Carlo (N=1000, seed=42, Q01–Q39, 39 sampled).\n'
    '# Weighted cosine similarity metric (SALIENCE_PROFILES), tiered floor multipliers.\n'
    '# v19: culture_drift salience 1.85 + Q20 amplification + Authority vector sharpening. Session 23.\n'
    '# Monte Carlo N=1000, seed=42, Q01-Q39. Date: 2026-05-24.\n'
    '_PRECOMPUTED_NOISE_BASELINE: dict = {\n'
    '    "built_to_fail":                        0.8333,\n'
    '    "culture_drift":                        0.9261,\n'
    '    "decision_blindness":                   0.7346,\n'
    '    "decision_paralysis":                   0.9432,\n'
    '    "dueling_narratives":                   0.9432,\n'
    '    "groundhog_day":                        0.9188,\n'
    '    "heard_and_ignored":                    0.8751,\n'
    '    "hr_capture":                           0.8751,\n'
    '    "identity_erosion":                     0.9129,\n'
    '    "invisible_burnout":                    0.9188,\n'
    '    "invisible_influence_architecture":     0.9332,\n'
    '    "leadership_continuity_risk":           0.9432,\n'
    '    "leadership_deafness":                  0.8960,\n'
    '    "narrative_lock":                       0.9129,\n'
    '    "paper_shield":                         0.9332,\n'
    '    "pay_exposure":                         0.9432,\n'
    '    "silosolation":                         0.7826,\n'
    '    "the_arbitrary_standard":               0.7826,\n'
    '    "the_basement_standard":                0.9188,\n'
    '    "the_broken_compass":                   0.9188,\n'
    '    "the_burned_credibility":               0.9188,\n'
    '    "the_culture_that_wasnt":               0.9129,\n'
    '    "the_diversity_ceiling":                0.9188,\n'
    '    "the_dormant_talent":                   0.8943,\n'
    '    "the_exposed":                          0.8751,\n'
    '    "the_founders_grip":                    0.8751,\n'
    '    "the_fracture":                         0.7346,\n'
    '    "the_inside_track":                     0.9188,\n'
    '    "the_lost_map":                         0.9432,\n'
    '    "the_overloaded_manager":               0.8961,\n'
    '    "the_paper_tiger":                      0.8333,\n'
    '    "the_pay_fog":                          0.9432,\n'
    '    "the_policy_lag":                       0.9432,\n'
    '    "the_second_close":                     0.7826,\n'
    '    "the_suppression_filter":               0.8279,\n'
    '    "the_tolerated_violation":              0.8751,\n'
    '    "the_undefined_role":                   0.8710,\n'
    '    "the_unexamined_algorithm":             0.9433,\n'
    '    "the_unformed_leader":                  0.8943,\n'
    '    "the_uninitiated":                      0.9339,\n'
    '    "the_unlocked_door":                    0.9129,\n'
    '    "the_unreported_hazard":                0.9129,\n'
    '    "the_unsolved_problem":                 0.8751,\n'
    '    "the_untouchable":                      0.8923,\n'
    '    "the_wrong_reward":                     0.9188,\n'
    '    "transition_paralysis":                 0.9432,\n'
    '    "what_nobody_says":                     0.8653,\n'
    '}'
)

NEW = (
    '# Precomputed noise baseline — Monte Carlo (N=1000, seed=42, Q01–Q39, 39 sampled).\n'
    '# Weighted cosine similarity metric (SALIENCE_PROFILES), tiered floor multipliers.\n'
    '# v20: two-tier hierarchical router, dimension-conditional MC. Session 23.\n'
    '# Alliance states: 0.0000 (Alliance never dominant in random noise — floor = 0.0).\n'
    '# Aptitude states: 5 observations (Aptitude dominant in 5/1000 runs).\n'
    '# Monte Carlo N=1000, seed=42, Q01-Q39. Date: 2026-05-24.\n'
    '_PRECOMPUTED_NOISE_BASELINE: dict = {\n'
    '    "built_to_fail":                        0.9300,\n'
    '    "culture_drift":                        0.9441,\n'
    '    "decision_blindness":                   0.0000,\n'
    '    "decision_paralysis":                   0.9463,\n'
    '    "dueling_narratives":                   0.9463,\n'
    '    "groundhog_day":                        0.9420,\n'
    '    "heard_and_ignored":                    0.9178,\n'
    '    "hr_capture":                           0.9178,\n'
    '    "identity_erosion":                     0.9259,\n'
    '    "invisible_burnout":                    0.9420,\n'
    '    "invisible_influence_architecture":     0.9351,\n'
    '    "leadership_continuity_risk":           0.9463,\n'
    '    "leadership_deafness":                  0.9244,\n'
    '    "narrative_lock":                       0.9259,\n'
    '    "paper_shield":                         0.9351,\n'
    '    "pay_exposure":                         0.9463,\n'
    '    "silosolation":                         0.0000,\n'
    '    "the_arbitrary_standard":               0.0000,\n'
    '    "the_basement_standard":                0.9420,\n'
    '    "the_broken_compass":                   0.9420,\n'
    '    "the_burned_credibility":               0.9420,\n'
    '    "the_culture_that_wasnt":               0.9259,\n'
    '    "the_diversity_ceiling":                0.9420,\n'
    '    "the_dormant_talent":                   0.9203,\n'
    '    "the_exposed":                          0.9178,\n'
    '    "the_founders_grip":                    0.9178,\n'
    '    "the_fracture":                         0.0000,\n'
    '    "the_inside_track":                     0.9420,\n'
    '    "the_lost_map":                         0.9463,\n'
    '    "the_overloaded_manager":               0.9213,\n'
    '    "the_paper_tiger":                      0.9300,\n'
    '    "the_pay_fog":                          0.9463,\n'
    '    "the_policy_lag":                       0.9463,\n'
    '    "the_second_close":                     0.0000,\n'
    '    "the_suppression_filter":               0.0000,\n'
    '    "the_tolerated_violation":              0.9178,\n'
    '    "the_undefined_role":                   0.9266,\n'
    '    "the_unexamined_algorithm":             0.9462,\n'
    '    "the_unformed_leader":                  0.9203,\n'
    '    "the_uninitiated":                      0.9463,\n'
    '    "the_unlocked_door":                    0.9259,\n'
    '    "the_unreported_hazard":                0.9259,\n'
    '    "the_unsolved_problem":                 0.9178,\n'
    '    "the_untouchable":                      0.9289,\n'
    '    "the_wrong_reward":                     0.9420,\n'
    '    "transition_paralysis":                 0.9463,\n'
    '    "what_nobody_says":                     0.8796,\n'
    '}'
)


def run(dry_run: bool):
    text = TARGET.read_text(encoding="utf-8")
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v20_noise_baseline.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    if OLD not in text:
        print("[FAIL] Old block not found — file may have changed. Aborting.")
        sys.exit(1)
    if text.count(OLD) > 1:
        print("[FAIL] Old block found multiple times — not unique. Aborting.")
        sys.exit(1)

    if dry_run:
        print("[DRY-RUN] Would apply: _PRECOMPUTED_NOISE_BASELINE v19 -> v20 (47 states)")
        print("Key deltas (v19 -> v20):")
        print("  culture_drift:          0.9261 -> 0.9441  (+0.0180)")
        print("  the_uninitiated:        0.9339 -> 0.9463  (+0.0124)")
        print("  heard_and_ignored:      0.8751 -> 0.9178  (+0.0427)")
        print("  the_exposed:            0.8751 -> 0.9178  (+0.0427)")
        print("  the_founders_grip:      0.8751 -> 0.9178  (+0.0427)")
        print("  decision_blindness:     0.7346 -> 0.0000  (Alliance — no obs)")
        print("  silosolation:           0.7826 -> 0.0000  (Alliance — no obs)")
        print("  the_arbitrary_standard: 0.7826 -> 0.0000  (Alliance — no obs)")
        print("  the_fracture:           0.7346 -> 0.0000  (Alliance — no obs)")
        print("  the_second_close:       0.7826 -> 0.0000  (Alliance — no obs)")
        print("  the_suppression_filter: 0.8279 -> 0.0000  (Alliance — no obs)")
        print("[DRY-RUN COMPLETE] 1 change validated. No file written.")
    else:
        new_text = text.replace(OLD, NEW, 1)
        TARGET.write_text(new_text, encoding="utf-8")
        print("[APPLIED] _PRECOMPUTED_NOISE_BASELINE v19 -> v20 (47 states)")
        print(f"[DONE] {TARGET} written.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
