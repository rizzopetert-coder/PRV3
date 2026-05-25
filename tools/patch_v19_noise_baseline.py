"""
Patch: engine/output.py — update _PRECOMPUTED_NOISE_BASELINE to v19 values.

v19: angular separation — culture_drift salience 1.85 + Q20 amplification +
Authority vector sharpening. Session 23, 2026-05-24.
Monte Carlo N=1000, seed=42, Q01-Q39.

Usage:
  python tools/patch_v19_noise_baseline.py --dry-run
  python tools/patch_v19_noise_baseline.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "output.py"

OLD = (
    '# Precomputed noise baseline — Monte Carlo (N=1000, seed=42, Q01–Q39, 39 sampled).\n'
    '# Weighted cosine similarity metric (SALIENCE_PROFILES), tiered floor multipliers.\n'
    '# v18: three-tier salience architecture + floor ceiling 0.9650. Session 23.\n'
    '# Monte Carlo N=1000, seed=42, Q01-Q39. Date: 2026-05-24.\n'
    '_PRECOMPUTED_NOISE_BASELINE: dict = {\n'
    '    "built_to_fail":                        0.8274,\n'
    '    "culture_drift":                        0.9323,\n'
    '    "decision_blindness":                   0.7363,\n'
    '    "decision_paralysis":                   0.9439,\n'
    '    "dueling_narratives":                   0.9439,\n'
    '    "groundhog_day":                        0.9198,\n'
    '    "heard_and_ignored":                    0.9147,\n'
    '    "hr_capture":                           0.9147,\n'
    '    "identity_erosion":                     0.9137,\n'
    '    "invisible_burnout":                    0.9198,\n'
    '    "invisible_influence_architecture":     0.9338,\n'
    '    "leadership_continuity_risk":           0.9439,\n'
    '    "leadership_deafness":                  0.8965,\n'
    '    "narrative_lock":                       0.9137,\n'
    '    "paper_shield":                         0.9338,\n'
    '    "pay_exposure":                         0.9439,\n'
    '    "silosolation":                         0.7840,\n'
    '    "the_arbitrary_standard":               0.7840,\n'
    '    "the_basement_standard":                0.9198,\n'
    '    "the_broken_compass":                   0.9198,\n'
    '    "the_burned_credibility":               0.9198,\n'
    '    "the_culture_that_wasnt":               0.9137,\n'
    '    "the_diversity_ceiling":                0.9198,\n'
    '    "the_dormant_talent":                   0.8916,\n'
    '    "the_exposed":                          0.9147,\n'
    '    "the_founders_grip":                    0.9147,\n'
    '    "the_fracture":                         0.7363,\n'
    '    "the_inside_track":                     0.9198,\n'
    '    "the_lost_map":                         0.9439,\n'
    '    "the_overloaded_manager":               0.8933,\n'
    '    "the_paper_tiger":                      0.8274,\n'
    '    "the_pay_fog":                          0.9439,\n'
    '    "the_policy_lag":                       0.9439,\n'
    '    "the_second_close":                     0.7840,\n'
    '    "the_suppression_filter":               0.8288,\n'
    '    "the_tolerated_violation":              0.9147,\n'
    '    "the_undefined_role":                   0.8668,\n'
    '    "the_unexamined_algorithm":             0.9432,\n'
    '    "the_unformed_leader":                  0.8916,\n'
    '    "the_uninitiated":                      0.9439,\n'
    '    "the_unlocked_door":                    0.9137,\n'
    '    "the_unreported_hazard":                0.9137,\n'
    '    "the_unsolved_problem":                 0.9147,\n'
    '    "the_untouchable":                      0.8936,\n'
    '    "the_wrong_reward":                     0.9198,\n'
    '    "transition_paralysis":                 0.9439,\n'
    '    "what_nobody_says":                     0.8663,\n'
    '}'
)

NEW = (
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


def run(dry_run: bool):
    text = TARGET.read_text(encoding="utf-8")
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v19_noise_baseline.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    if OLD not in text:
        print("[FAIL] Old block not found — file may have changed. Aborting.")
        sys.exit(1)
    if text.count(OLD) > 1:
        print(f"[FAIL] Old block found multiple times — not unique. Aborting.")
        sys.exit(1)

    if dry_run:
        print("[DRY-RUN] Would apply: _PRECOMPUTED_NOISE_BASELINE v18 -> v19 (47 states)")
        print("Key deltas:")
        print("  culture_drift:          0.9323 -> 0.9261  (floor still 0.9650, ceiling-capped)")
        print("  the_uninitiated:        0.9439 -> 0.9339  (floor 0.9439 -> 0.9339)")
        print("  heard_and_ignored:      0.9147 -> 0.8751  (floor 0.9147 -> 0.8751)")
        print("  hr_capture:             0.9147 -> 0.8751  (floor 0.9147 -> 0.8751)")
        print("  the_exposed:            0.9147 -> 0.8751  (floor 0.9147 -> 0.8751)")
        print("  the_founders_grip:      0.9147 -> 0.8751  (floor 0.9147 -> 0.8751)")
        print("  the_tolerated_violation:0.9147 -> 0.8751  (floor 0.9147 -> 0.8751)")
        print("  the_unsolved_problem:   0.9147 -> 0.8751  (floor 0.9147 -> 0.8751)")
        print("[DRY-RUN COMPLETE] 1 change validated. No file written.")
    else:
        new_text = text.replace(OLD, NEW, 1)
        TARGET.write_text(new_text, encoding="utf-8")
        print("[APPLIED] _PRECOMPUTED_NOISE_BASELINE v18 -> v19 (47 states)")
        print(f"[DONE] {TARGET} written.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
