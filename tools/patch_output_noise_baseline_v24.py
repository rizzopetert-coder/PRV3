"""
PRV3 — Patch _PRECOMPUTED_NOISE_BASELINE in engine/output.py

Recalibrates the per-state mean SCD-WCS scores under v24 CENTROID_FIELD_SCALARS.
N=1000, seed=42, Q01-Q39, Session 27.

Usage:
    python tools/patch_output_noise_baseline_v24.py --dry-run   # print diff only
    python tools/patch_output_noise_baseline_v24.py --write     # apply change
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
OUTPUT_PATH  = PROJECT_ROOT / "engine" / "output.py"

# Per-state mean SCD-WCS scores — v24 parameters, recalibrate_floor_v21.py
# N=1000, seed=42, Q01-Q39, CENTROID_FIELD_SCALARS v24, Session 27.
NEW_BASELINE = {
    "built_to_fail":                        0.8512,
    "culture_drift":                        0.8840,
    "decision_blindness":                   0.7700,
    "decision_paralysis":                   0.9199,
    "dueling_narratives":                   0.9199,
    "groundhog_day":                        0.8597,
    "heard_and_ignored":                    0.8911,
    "hr_capture":                           0.8911,
    "identity_erosion":                     0.8717,
    "invisible_burnout":                    0.8597,
    "invisible_influence_architecture":     0.9153,
    "leadership_continuity_risk":           0.9199,
    "leadership_deafness":                  0.7851,
    "narrative_lock":                       0.8717,
    "paper_shield":                         0.9153,
    "pay_exposure":                         0.9199,
    "silosolation":                         0.8059,
    "the_arbitrary_standard":               0.8059,
    "the_basement_standard":                0.8597,
    "the_broken_compass":                   0.8597,
    "the_burned_credibility":               0.8597,
    "the_culture_that_wasnt":               0.8717,
    "the_diversity_ceiling":                0.8597,
    "the_dormant_talent":                   0.8898,
    "the_exposed":                          0.8911,
    "the_founders_grip":                    0.8911,
    "the_fracture":                         0.7700,
    "the_inside_track":                     0.8597,
    "the_lost_map":                         0.9199,
    "the_overloaded_manager":               0.8942,
    "the_paper_tiger":                      0.8512,
    "the_pay_fog":                          0.9199,
    "the_policy_lag":                       0.9199,
    "the_second_close":                     0.8059,
    "the_suppression_filter":               0.8381,
    "the_tolerated_violation":              0.8911,
    "the_undefined_role":                   0.8783,
    "the_unexamined_algorithm":             0.9271,
    "the_unformed_leader":                  0.8898,
    "the_uninitiated":                      0.9199,
    "the_unlocked_door":                    0.8717,
    "the_unreported_hazard":                0.8717,
    "the_unsolved_problem":                 0.8911,
    "the_untouchable":                      0.8201,
    "the_wrong_reward":                     0.8597,
    "transition_paralysis":                 0.9199,
    "what_nobody_says":                     0.8412,
}

COMMENT_LINE = (
    "# Precomputed noise baseline — RETIRED v21 (SCD-WCS absolute threshold replaces multiplicative floor).\n"
    "# Kept for score_lift_pct computation in apply_signal_floor(). Do not use for floor gating.\n"
    "# v24: SCD-WCS, CENTROID_FIELD_SCALARS focus-damped, SALIENCE_PROFILES, full 47-state path. Session 27.\n"
)

def build_new_block() -> str:
    lines = [COMMENT_LINE]
    lines.append("_PRECOMPUTED_NOISE_BASELINE: dict = {\n")
    for sid, val in NEW_BASELINE.items():
        padding = " " * (40 - len(f'"{sid}"'))
        lines.append(f'    "{sid}":{padding}{val:.4f},\n')
    lines.append("}\n")
    return "".join(lines)

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--dry-run", "--write"):
        print("Usage: python patch_output_noise_baseline_v24.py [--dry-run | --write]")
        sys.exit(1)

    content = OUTPUT_PATH.read_text(encoding="utf-8")

    # Match from the comment block through the closing } of the dict
    pattern = (
        r"# Precomputed noise baseline.*?"
        r"_PRECOMPUTED_NOISE_BASELINE: dict = \{.*?\}\n"
    )
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("[ERROR] Could not locate _PRECOMPUTED_NOISE_BASELINE block in engine/output.py")
        sys.exit(1)

    old_block = match.group(0)
    new_block = build_new_block()

    if sys.argv[1] == "--dry-run":
        print("[DRY RUN] engine/output.py — _PRECOMPUTED_NOISE_BASELINE update")
        print(f"\nOLD comment: {old_block.splitlines()[0]}")
        print(f"NEW comment: {new_block.splitlines()[0]}")
        print(f"\nOLD sample values (first 5 states):")
        for line in old_block.splitlines()[3:8]:
            print(f"  {line}")
        print(f"\nNEW sample values (first 5 states):")
        for line in new_block.splitlines()[4:9]:
            print(f"  {line}")
        print(f"\nTotal states in old block: {old_block.count('0.')}")
        print(f"Total states in new block: {len(NEW_BASELINE)} (expected 47)")
        print(f"\n[DRY RUN COMPLETE] Run with --write to apply.")
        return

    # Wet run
    new_content = content.replace(old_block, new_block)
    if new_content == content:
        print("[ERROR] Replacement had no effect — block text mismatch.")
        sys.exit(1)
    OUTPUT_PATH.write_text(new_content, encoding="utf-8")
    print(f"[WRITTEN] engine/output.py — _PRECOMPUTED_NOISE_BASELINE updated (v24, Session 27)")

if __name__ == "__main__":
    main()
