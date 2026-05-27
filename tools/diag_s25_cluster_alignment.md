# PRV3 -- Session 25: Cluster Alignment Check

Named clusters vs empirical co-occurrence. 47 HC profiles. Top-5 window.

---

## Named Cluster Internal vs Cross Co-Occurrence

Internal co-occurrence rate: fraction of profiles where any two cluster members both appear in top-5.  
Cross co-occurrence rate: cluster members appearing in top-5 alongside non-cluster states (average).

### C-Manager (the_unformed_leader, the_overloaded_manager, the_dormant_talent)

- Profiles with >= 2 cluster members in top-5: 11/47 (23.40%)
- Profiles with all 3 cluster members in top-5: 0/47 (0.00%)

Pair-level counts:
- the_unformed_leader x the_overloaded_manager: 0/47 (0.00%)
- the_unformed_leader x the_dormant_talent: 11/47 (23.40%)
- the_overloaded_manager x the_dormant_talent: 0/47 (0.00%)

Appearance in non-member HC profiles (top-5 frequency):
- the_unformed_leader: appears in 10/36 non-cluster profiles (27.78%)
- the_overloaded_manager: appears in 0/36 non-cluster profiles (0.00%)
- the_dormant_talent: appears in 8/36 non-cluster profiles (22.22%)

### C-Culture (culture_drift, the_culture_that_wasnt, identity_erosion)

- Profiles with >= 2 cluster members in top-5: 13/47 (27.66%)
- Profiles with all 3 cluster members in top-5: 0/47 (0.00%)

Pair-level counts:
- culture_drift x the_culture_that_wasnt: 0/47 (0.00%)
- culture_drift x identity_erosion: 0/47 (0.00%)
- the_culture_that_wasnt x identity_erosion: 13/47 (27.66%)

Appearance in non-member HC profiles (top-5 frequency):
- culture_drift: appears in 2/36 non-cluster profiles (5.56%)
- the_culture_that_wasnt: appears in 7/36 non-cluster profiles (19.44%)
- identity_erosion: appears in 7/36 non-cluster profiles (19.44%)

### C-Silence (what_nobody_says, the_unreported_hazard, the_unlocked_door)

- Profiles with >= 2 cluster members in top-5: 0/47 (0.00%)
- Profiles with all 3 cluster members in top-5: 0/47 (0.00%)

Pair-level counts:
- what_nobody_says x the_unreported_hazard: 0/47 (0.00%)
- what_nobody_says x the_unlocked_door: 0/47 (0.00%)
- the_unreported_hazard x the_unlocked_door: 0/47 (0.00%)

Appearance in non-member HC profiles (top-5 frequency):
- what_nobody_says: appears in 0/36 non-cluster profiles (0.00%)
- the_unreported_hazard: appears in 3/36 non-cluster profiles (8.33%)
- the_unlocked_door: appears in 0/36 non-cluster profiles (0.00%)

### C-InfoFlow (leadership_deafness, the_suppression_filter)

- Profiles with >= 2 cluster members in top-5: 0/47 (0.00%)

Pair-level counts:
- leadership_deafness x the_suppression_filter: 0/47 (0.00%)

Appearance in non-member HC profiles (top-5 frequency):
- leadership_deafness: appears in 23/36 non-cluster profiles (63.89%)
- the_suppression_filter: appears in 0/36 non-cluster profiles (0.00%)

## Known Dominant Sink Appearance Rates

For each known dominant sink, how often does it appear in top-5 rankings across HC profiles where it is NOT the target state?

| Sink State | Non-target profiles | Appears in top-5 | Rate |
|---|---|---|---|
| leadership_deafness | 46 | 30 | 65.22% |
| built_to_fail | 46 | 18 | 39.13% |
| the_fracture | 46 | 11 | 23.91% |

## Sink Dominance Detail

### leadership_deafness
Appears in top-5 for 30/46 non-target profiles:

| Target profile | Sink rank | Sink score |
|---|---|---|
| the_tolerated_violation | 1 | -0.7273 |
| heard_and_ignored | 1 | -0.7284 |
| transition_paralysis | 1 | -0.6112 |
| dueling_narratives | 1 | -0.6274 |
| the_arbitrary_standard | 1 | -0.6165 |
| the_untouchable | 1 | -0.5611 |
| the_diversity_ceiling | 1 | -0.5149 |
| invisible_burnout | 1 | -0.6538 |
| the_basement_standard | 1 | -0.4534 |
| the_inside_track | 1 | -0.4505 |
| narrative_lock | 1 | -0.5987 |
| groundhog_day | 1 | -0.5450 |
| the_wrong_reward | 1 | -0.5445 |
| the_broken_compass | 1 | -0.5318 |
| what_nobody_says | 1 | -0.6128 |
| the_unreported_hazard | 1 | -0.6372 |
| the_unlocked_door | 1 | -0.6372 |
| culture_drift | 1 | -0.7065 |
| identity_erosion | 1 | -0.6577 |
| the_culture_that_wasnt | 1 | -0.6577 |
| the_unsolved_problem | 2 | -0.7096 |
| the_dormant_talent | 3 | -0.5755 |
| the_founders_grip | 3 | -0.7123 |
| the_exposed | 3 | -0.7594 |
| the_uninitiated | 3 | -0.7709 |
| pay_exposure | 3 | -0.6607 |
| the_pay_fog | 3 | -0.6106 |
| invisible_influence_architecture | 3 | -0.7364 |
| decision_blindness | 3 | -0.7486 |
| the_burned_credibility | 3 | -0.5670 |

### built_to_fail
Appears in top-5 for 18/46 non-target profiles:

| Target profile | Sink rank | Sink score |
|---|---|---|
| the_unformed_leader | 1 | -0.3388 |
| the_overloaded_manager | 1 | -0.4513 |
| the_dormant_talent | 1 | -0.5689 |
| the_undefined_role | 1 | -0.1228 |
| the_paper_tiger | 1 | -0.1061 |
| the_founders_grip | 1 | -0.7120 |
| the_exposed | 1 | -0.7372 |
| the_uninitiated | 1 | -0.7107 |
| leadership_continuity_risk | 1 | -0.5257 |
| the_policy_lag | 1 | -0.2068 |
| pay_exposure | 1 | -0.6395 |
| the_pay_fog | 1 | -0.6001 |
| the_unexamined_algorithm | 1 | -0.5851 |
| paper_shield | 1 | -0.4796 |
| invisible_influence_architecture | 1 | -0.6877 |
| decision_blindness | 1 | -0.7486 |
| heard_and_ignored | 2 | -0.7463 |
| dueling_narratives | 2 | -0.6334 |

### the_fracture
Appears in top-5 for 11/46 non-target profiles:

| Target profile | Sink rank | Sink score |
|---|---|---|
| decision_paralysis | 1 | -0.7039 |
| the_lost_map | 1 | -0.5542 |
| the_second_close | 1 | -0.6436 |
| silosolation | 1 | -0.0899 |
| the_suppression_filter | 1 | -0.5614 |
| the_burned_credibility | 1 | -0.5379 |
| invisible_burnout | 2 | -0.6731 |
| narrative_lock | 2 | -0.6271 |
| the_unreported_hazard | 2 | -0.6700 |
| the_unlocked_door | 2 | -0.6700 |
| the_broken_compass | 3 | -0.5719 |

## Most Frequent Top-5 Appearances Across All 47 HC Profiles

(Including as the target state itself.)

| State | Top-5 appearances (of 47) | Rate |
|---|---|---|
| leadership_deafness | 31 | 65.96% |
| built_to_fail | 19 | 40.43% |
| the_paper_tiger | 19 | 40.43% |
| the_unformed_leader | 13 | 27.66% |
| the_culture_that_wasnt | 13 | 27.66% |
| identity_erosion | 13 | 27.66% |
| decision_blindness | 12 | 25.53% |
| the_fracture | 12 | 25.53% |
| the_undefined_role | 11 | 23.40% |
| the_dormant_talent | 11 | 23.40% |
| the_diversity_ceiling | 10 | 21.28% |
| the_second_close | 10 | 21.28% |
| the_burned_credibility | 9 | 19.15% |
| silosolation | 9 | 19.15% |
| invisible_burnout | 8 | 17.02% |
| the_basement_standard | 7 | 14.89% |
| narrative_lock | 7 | 14.89% |
| the_unreported_hazard | 7 | 14.89% |
| the_arbitrary_standard | 6 | 12.77% |
| culture_drift | 2 | 4.26% |
