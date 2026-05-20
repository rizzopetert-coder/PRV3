"""Validate salience profile state coverage before write."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS

proposed_ids = [
    "built_to_fail", "the_paper_tiger", "the_undefined_role",
    "the_unformed_leader", "the_dormant_talent", "the_overloaded_manager",
    "the_founders_grip", "the_exposed", "hr_capture", "heard_and_ignored",
    "the_tolerated_violation", "the_unsolved_problem",
    "the_uninitiated", "leadership_continuity_risk", "decision_paralysis",
    "the_policy_lag", "dueling_narratives", "transition_paralysis",
    "the_lost_map", "pay_exposure", "the_pay_fog",
    "the_unexamined_algorithm", "paper_shield", "invisible_influence_architecture",
    "the_fracture", "decision_blindness",
    "the_second_close", "silosolation", "the_arbitrary_standard",
    "the_suppression_filter",
    "the_untouchable",
    "the_diversity_ceiling", "the_burned_credibility", "invisible_burnout",
    "the_basement_standard", "the_inside_track", "groundhog_day",
    "the_wrong_reward", "the_broken_compass",
    "narrative_lock", "what_nobody_says", "leadership_deafness",
    "identity_erosion", "the_culture_that_wasnt", "the_unreported_hazard",
    "the_unlocked_door", "culture_drift",
]

registry_ids = set(STATE_PROFILES.keys())
proposed_set  = set(proposed_ids)
missing       = registry_ids - proposed_set
extra         = proposed_set - registry_ids
duplicates    = [x for x in proposed_ids if proposed_ids.count(x) > 1]

print(f"STATE_PROFILES count : {len(registry_ids)}")
print(f"Proposed count       : {len(proposed_ids)}")
print(f"Missing from proposed: {sorted(missing) if missing else 'none'}")
print(f"Extra in proposed    : {sorted(extra) if extra else 'none'}")
print(f"Duplicates           : {duplicates if duplicates else 'none'}")

if missing or extra or duplicates:
    print("\n[FAIL] Coverage mismatch.")
    sys.exit(1)
else:
    print("\n[PASS] All 47 states covered, no extras, no duplicates.")
    sys.exit(0)
