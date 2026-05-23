"""
Patch: engine/output.py — _PRECOMPUTED_NOISE_BASELINE update to v15 (Session 22)

Replaces v14 baseline (weighted cosine, mean=0.8852) with v15 baseline
(weighted cosine via SALIENCE_PROFILES, N=1000, seed=42, Q01-Q39, mean=0.8937).

Usage:
  python tools/patch_baseline_v15.py --dry-run
  python tools/patch_baseline_v15.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "output.py"

OLD_COMMENT_AND_BASELINE = (
    "# Weighted cosine similarity metric (SALIENCE_PROFILES), tiered floor multipliers.\n"
    "# v14: weighted cosine baseline. Session 21.\n"
    "# Monte Carlo N=1000, seed=42, Q01-Q39. Date: 2026-05-19.\n"
    "_PRECOMPUTED_NOISE_BASELINE: dict = {\n"
    '    "built_to_fail":                        0.7780,\n'
    '    "culture_drift":                        0.8962,\n'
    '    "decision_blindness":                   0.6852,\n'
    '    "decision_paralysis":                   0.9659,\n'
    '    "dueling_narratives":                   0.9659,\n'
    '    "groundhog_day":                        0.8879,\n'
    '    "heard_and_ignored":                    0.9589,\n'
    '    "hr_capture":                           0.9589,\n'
    '    "identity_erosion":                     0.8778,\n'
    '    "invisible_burnout":                    0.8879,\n'
    '    "invisible_influence_architecture":     0.9096,\n'
    '    "leadership_continuity_risk":           0.9659,\n'
    '    "leadership_deafness":                  0.8778,\n'
    '    "narrative_lock":                       0.8778,\n'
    '    "paper_shield":                         0.9096,\n'
    '    "pay_exposure":                         0.9659,\n'
    '    "silosolation":                         0.7384,\n'
    '    "the_arbitrary_standard":               0.7384,\n'
    '    "the_basement_standard":                0.8879,\n'
    '    "the_broken_compass":                   0.8879,\n'
    '    "the_burned_credibility":               0.8879,\n'
    '    "the_culture_that_wasnt":               0.8778,\n'
    '    "the_diversity_ceiling":                0.8879,\n'
    '    "the_dormant_talent":                   0.8733,\n'
    '    "the_exposed":                          0.9589,\n'
    '    "the_founders_grip":                    0.9589,\n'
    '    "the_fracture":                         0.6852,\n'
    '    "the_inside_track":                     0.8879,\n'
    '    "the_lost_map":                         0.9659,\n'
    '    "the_overloaded_manager":               0.8561,\n'
    '    "the_paper_tiger":                      0.7780,\n'
    '    "the_pay_fog":                          0.9659,\n'
    '    "the_policy_lag":                       0.9659,\n'
    '    "the_second_close":                     0.7384,\n'
    '    "the_suppression_filter":               0.8072,\n'
    '    "the_tolerated_violation":              0.9589,\n'
    '    "the_undefined_role":                   0.8242,\n'
    '    "the_unexamined_algorithm":             0.9612,\n'
    '    "the_unformed_leader":                  0.8733,\n'
    '    "the_uninitiated":                      0.9659,\n'
    '    "the_unlocked_door":                    0.8778,\n'
    '    "the_unreported_hazard":                0.8778,\n'
    '    "the_unsolved_problem":                 0.9589,\n'
    '    "the_untouchable":                      0.8560,\n'
    '    "the_wrong_reward":                     0.8879,\n'
    '    "transition_paralysis":                 0.9659,\n'
    '    "what_nobody_says":                     0.8778,\n'
    "}"
)

NEW_COMMENT_AND_BASELINE = (
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


def main():
    dry_run = "--write" not in sys.argv
    mode = "DRY-RUN" if dry_run else "WRITE"

    print(f"\n{'='*64}")
    print(f"patch_baseline_v15.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'='*64}\n")

    if not TARGET.exists():
        print("[ERROR] Target file not found.")
        sys.exit(1)

    content = TARGET.read_text(encoding="utf-8")

    if OLD_COMMENT_AND_BASELINE not in content:
        print("[ERROR] v14 baseline block not found — may already be updated or file has changed.")
        sys.exit(1)

    count = content.count(OLD_COMMENT_AND_BASELINE)
    if count > 1:
        print(f"[ERROR] Ambiguous match ({count}x). Aborting.")
        sys.exit(1)

    if dry_run:
        print("  [DRY-RUN] Would replace: v14 _PRECOMPUTED_NOISE_BASELINE with v15 values")
        print("  [DRY-RUN] Comment: 'v14: weighted cosine baseline. Session 21.' -> 'v15: authority drain... Session 22.'")
        print("  [DRY-RUN] Mean: 0.8852 -> 0.8937 | Range: 0.6852-0.9659 -> 0.7112-0.9589")
        print(f"\n[DRY-RUN COMPLETE] 1 change validated. Run with --write to apply.")
    else:
        new_content = content.replace(OLD_COMMENT_AND_BASELINE, NEW_COMMENT_AND_BASELINE)
        TARGET.write_text(new_content, encoding="utf-8")
        print("  [APPLIED] _PRECOMPUTED_NOISE_BASELINE updated to v15 values")
        print(f"\n[DONE] {TARGET} written.")

    sys.exit(0)


if __name__ == "__main__":
    main()
