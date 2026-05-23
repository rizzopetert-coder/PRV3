"""
Patch: engine/output.py — _PRECOMPUTED_NOISE_BASELINE update to v16 (Session 22)

Replaces v15 baseline (weighted cosine, mean=0.8937) with v16 baseline
(weighted cosine via SALIENCE_PROFILES, N=1000, seed=42, Q01-Q39, mean=0.8962).

Usage:
  python tools/patch_baseline_v16.py --dry-run
  python tools/patch_baseline_v16.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "output.py"

OLD_COMMENT_AND_BASELINE = (
    "# Weighted cosine similarity metric (SALIENCE_PROFILES), tiered floor multipliers.\n"
    "# v15: authority drain Q07/Q09/Q16/Q20/Q26/Q29 + state_targets purge + APT-PT-00 Q06. Session 22.\n"
    "# Monte Carlo N=1000, seed=42, Q01-Q39. Date: 2026-05-22.\n"
    "_PRECOMPUTED_NOISE_BASELINE: dict = {\n"
    '    "built_to_fail":                        0.8081,\n'
    '    "culture_drift":                        0.9170,\n'
    '    "decision_blindness":                   0.7112,\n'
    '    "decision_paralysis":                   0.9582,\n'
    '    "dueling_narratives":                   0.9582,\n'
    '    "groundhog_day":                        0.9063,\n'
    '    "heard_and_ignored":                    0.9402,\n'
    '    "hr_capture":                           0.9402,\n'
    '    "identity_erosion":                     0.8919,\n'
    '    "invisible_burnout":                    0.9063,\n'
    '    "invisible_influence_architecture":     0.9157,\n'
    '    "leadership_continuity_risk":           0.9582,\n'
    '    "leadership_deafness":                  0.8919,\n'
    '    "narrative_lock":                       0.8919,\n'
    '    "paper_shield":                         0.9157,\n'
    '    "pay_exposure":                         0.9582,\n'
    '    "silosolation":                         0.7623,\n'
    '    "the_arbitrary_standard":               0.7623,\n'
    '    "the_basement_standard":                0.9063,\n'
    '    "the_broken_compass":                   0.9063,\n'
    '    "the_burned_credibility":               0.9063,\n'
    '    "the_culture_that_wasnt":               0.8919,\n'
    '    "the_diversity_ceiling":                0.9063,\n'
    '    "the_dormant_talent":                   0.8879,\n'
    '    "the_exposed":                          0.9402,\n'
    '    "the_founders_grip":                    0.9402,\n'
    '    "the_fracture":                         0.7112,\n'
    '    "the_inside_track":                     0.9063,\n'
    '    "the_lost_map":                         0.9582,\n'
    '    "the_overloaded_manager":               0.8814,\n'
    '    "the_paper_tiger":                      0.8081,\n'
    '    "the_pay_fog":                          0.9582,\n'
    '    "the_policy_lag":                       0.9582,\n'
    '    "the_second_close":                     0.7623,\n'
    '    "the_suppression_filter":               0.8292,\n'
    '    "the_tolerated_violation":              0.9402,\n'
    '    "the_undefined_role":                   0.8506,\n'
    '    "the_unexamined_algorithm":             0.9589,\n'
    '    "the_unformed_leader":                  0.8879,\n'
    '    "the_uninitiated":                      0.9582,\n'
    '    "the_unlocked_door":                    0.8919,\n'
    '    "the_unreported_hazard":                0.8919,\n'
    '    "the_unsolved_problem":                 0.9402,\n'
    '    "the_untouchable":                      0.8769,\n'
    '    "the_wrong_reward":                     0.9063,\n'
    '    "transition_paralysis":                 0.9582,\n'
    '    "what_nobody_says":                     0.8919,\n'
    "}"
)

NEW_COMMENT_AND_BASELINE = (
    "# Weighted cosine similarity metric (SALIENCE_PROFILES), tiered floor multipliers.\n"
    "# v16: contrast injection Q14/Q16/Q22/Q26/Q35/Q36. Session 22.\n"
    "# Monte Carlo N=1000, seed=42, Q01-Q39. Date: 2026-05-23.\n"
    "_PRECOMPUTED_NOISE_BASELINE: dict = {\n"
    '    "built_to_fail":                        0.8209,\n'
    '    "culture_drift":                        0.9272,\n'
    '    "decision_blindness":                   0.7252,\n'
    '    "decision_paralysis":                   0.9503,\n'
    '    "dueling_narratives":                   0.9503,\n'
    '    "groundhog_day":                        0.9155,\n'
    '    "heard_and_ignored":                    0.9250,\n'
    '    "hr_capture":                           0.9250,\n'
    '    "identity_erosion":                     0.8988,\n'
    '    "invisible_burnout":                    0.9155,\n'
    '    "invisible_influence_architecture":     0.9167,\n'
    '    "leadership_continuity_risk":           0.9503,\n'
    '    "leadership_deafness":                  0.8988,\n'
    '    "narrative_lock":                       0.8988,\n'
    '    "paper_shield":                         0.9167,\n'
    '    "pay_exposure":                         0.9503,\n'
    '    "silosolation":                         0.7750,\n'
    '    "the_arbitrary_standard":               0.7750,\n'
    '    "the_basement_standard":                0.9155,\n'
    '    "the_broken_compass":                   0.9155,\n'
    '    "the_burned_credibility":               0.9155,\n'
    '    "the_culture_that_wasnt":               0.8988,\n'
    '    "the_diversity_ceiling":                0.9155,\n'
    '    "the_dormant_talent":                   0.8936,\n'
    '    "the_exposed":                          0.9250,\n'
    '    "the_founders_grip":                    0.9250,\n'
    '    "the_fracture":                         0.7252,\n'
    '    "the_inside_track":                     0.9155,\n'
    '    "the_lost_map":                         0.9503,\n'
    '    "the_overloaded_manager":               0.8932,\n'
    '    "the_paper_tiger":                      0.8209,\n'
    '    "the_pay_fog":                          0.9503,\n'
    '    "the_policy_lag":                       0.9503,\n'
    '    "the_second_close":                     0.7750,\n'
    '    "the_suppression_filter":               0.8411,\n'
    '    "the_tolerated_violation":              0.9250,\n'
    '    "the_undefined_role":                   0.8617,\n'
    '    "the_unexamined_algorithm":             0.9533,\n'
    '    "the_unformed_leader":                  0.8936,\n'
    '    "the_uninitiated":                      0.9503,\n'
    '    "the_unlocked_door":                    0.8988,\n'
    '    "the_unreported_hazard":                0.8988,\n'
    '    "the_unsolved_problem":                 0.9250,\n'
    '    "the_untouchable":                      0.8877,\n'
    '    "the_wrong_reward":                     0.9155,\n'
    '    "transition_paralysis":                 0.9503,\n'
    '    "what_nobody_says":                     0.8988,\n'
    "}"
)


def main():
    dry_run = "--write" not in sys.argv
    mode = "DRY-RUN" if dry_run else "WRITE"

    print(f"\n{'='*64}")
    print(f"patch_baseline_v16.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'='*64}\n")

    if not TARGET.exists():
        print("[ERROR] Target file not found.")
        sys.exit(1)

    content = TARGET.read_text(encoding="utf-8")

    if OLD_COMMENT_AND_BASELINE not in content:
        print("[ERROR] v15 baseline block not found — may already be updated or file has changed.")
        sys.exit(1)

    count = content.count(OLD_COMMENT_AND_BASELINE)
    if count > 1:
        print(f"[ERROR] Ambiguous match ({count}x). Aborting.")
        sys.exit(1)

    if dry_run:
        print("  [DRY-RUN] Would replace: v15 _PRECOMPUTED_NOISE_BASELINE with v16 values")
        print("  [DRY-RUN] Comment: 'v15: authority drain...' -> 'v16: contrast injection Q14/Q16/Q22/Q26/Q35/Q36'")
        print("  [DRY-RUN] Mean: 0.8937 -> 0.8962 | the_uninitiated: 0.9582 -> 0.9503 (delta -0.0079)")
        print(f"\n[DRY-RUN COMPLETE] 1 change validated. Run with --write to apply.")
    else:
        new_content = content.replace(OLD_COMMENT_AND_BASELINE, NEW_COMMENT_AND_BASELINE)
        TARGET.write_text(new_content, encoding="utf-8")
        print("  [APPLIED] _PRECOMPUTED_NOISE_BASELINE updated to v16 values")
        print(f"\n[DONE] {TARGET} written.")

    sys.exit(0)


if __name__ == "__main__":
    main()
