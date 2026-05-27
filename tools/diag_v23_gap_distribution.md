# PRV3 v23 Gap Distribution Diagnostic

Session 26 read-only. 48 HC profiles under v23 engine state.
Engine: v23 (salience revert + leadership_deafness vector reshape + cluster cleanup)

## Per-Profile Gap Analysis (47 HC Profiles)

Sorted by gap ascending (smallest gap first).

| Target State | Target Rank | Target Score | Rank-1 State | Rank-1 Score | Gap |
|---|---|---|---|---|---|
| built_to_fail | 1 | 0.1030 | built_to_fail | 0.1030 | 0.0000 |
| the_paper_tiger | 2 | -0.1061 | built_to_fail | -0.1061 | 0.0000 |
| the_paper_tiger | 2 | -0.1061 | built_to_fail | -0.1061 | 0.0000 |
| the_fracture | 1 | -0.0878 | the_fracture | -0.0878 | 0.0000 |
| the_inside_track | 5 | -0.4668 | the_diversity_ceiling | -0.4668 | 0.0000 |
| the_wrong_reward | 8 | -0.5837 | leadership_deafness | -0.5836 | 0.0001 |
| the_diversity_ceiling | 2 | -0.5490 | leadership_deafness | -0.5449 | 0.0041 |
| leadership_deafness | 14 | -0.5797 | identity_erosion | -0.5754 | 0.0043 |
| the_unsolved_problem | 7 | -0.7099 | culture_drift | -0.7047 | 0.0052 |
| the_unreported_hazard | 7 | -0.6796 | the_fracture | -0.6700 | 0.0096 |
| the_unlocked_door | 8 | -0.6796 | the_fracture | -0.6700 | 0.0096 |
| the_dormant_talent | 4 | -0.5840 | built_to_fail | -0.5689 | 0.0150 |
| identity_erosion | 2 | -0.7070 | leadership_deafness | -0.6838 | 0.0232 |
| the_culture_that_wasnt | 3 | -0.7070 | leadership_deafness | -0.6838 | 0.0232 |
| the_basement_standard | 5 | -0.4669 | leadership_deafness | -0.4401 | 0.0268 |
| decision_blindness | 18 | -0.7819 | built_to_fail | -0.7486 | 0.0333 |
| the_second_close | 3 | -0.6881 | the_fracture | -0.6436 | 0.0445 |
| invisible_burnout | 19 | -0.7187 | the_fracture | -0.6731 | 0.0456 |
| culture_drift | 10 | -0.7586 | leadership_deafness | -0.6962 | 0.0624 |
| the_suppression_filter | 6 | -0.6240 | the_fracture | -0.5614 | 0.0626 |
| the_untouchable | 16 | -0.6617 | leadership_deafness | -0.5988 | 0.0630 |
| what_nobody_says | 17 | -0.7124 | leadership_deafness | -0.6441 | 0.0683 |
| silosolation | 4 | -0.1591 | the_fracture | -0.0899 | 0.0692 |
| the_broken_compass | 12 | -0.5722 | leadership_deafness | -0.4937 | 0.0785 |
| the_founders_grip | 37 | -0.7924 | built_to_fail | -0.7120 | 0.0804 |
| the_burned_credibility | 14 | -0.6217 | the_fracture | -0.5379 | 0.0838 |
| decision_paralysis | 16 | -0.7926 | the_fracture | -0.7039 | 0.0887 |
| the_arbitrary_standard | 26 | -0.7197 | identity_erosion | -0.6282 | 0.0915 |
| narrative_lock | 19 | -0.6739 | leadership_deafness | -0.5788 | 0.0950 |
| the_unformed_leader | 4 | -0.4609 | built_to_fail | -0.3388 | 0.1221 |
| groundhog_day | 8 | -0.5916 | leadership_deafness | -0.4682 | 0.1234 |
| the_undefined_role | 3 | -0.2466 | built_to_fail | -0.1228 | 0.1238 |
| heard_and_ignored | 33 | -0.8865 | built_to_fail | -0.7463 | 0.1402 |
| the_lost_map | 26 | -0.7097 | the_fracture | -0.5542 | 0.1555 |
| invisible_influence_architecture | 31 | -0.8628 | built_to_fail | -0.6877 | 0.1751 |
| the_uninitiated | 32 | -0.8859 | built_to_fail | -0.7107 | 0.1752 |
| the_overloaded_manager | 6 | -0.6364 | built_to_fail | -0.4513 | 0.1851 |
| pay_exposure | 39 | -0.8273 | built_to_fail | -0.6395 | 0.1878 |
| the_exposed | 42 | -0.9302 | built_to_fail | -0.7372 | 0.1930 |
| the_pay_fog | 40 | -0.8117 | built_to_fail | -0.6001 | 0.2117 |
| the_tolerated_violation | 45 | -0.9372 | leadership_deafness | -0.7223 | 0.2150 |
| dueling_narratives | 36 | -0.8487 | built_to_fail | -0.6334 | 0.2154 |
| transition_paralysis | 37 | -0.8712 | leadership_deafness | -0.6335 | 0.2377 |
| the_unexamined_algorithm | 41 | -0.8480 | built_to_fail | -0.5851 | 0.2629 |
| hr_capture | 32 | -0.9090 | the_diversity_ceiling | -0.5897 | 0.3193 |
| leadership_continuity_risk | 38 | -0.8742 | built_to_fail | -0.5257 | 0.3485 |
| paper_shield | 30 | -0.8803 | built_to_fail | -0.4796 | 0.4006 |
| the_policy_lag | 33 | -0.7491 | built_to_fail | -0.2068 | 0.5424 |

## Top-Cluster Pass Rate by Delta Window

Target state within Delta of rank-1 score.

| Delta_margin | Profiles passing | Pass rate |
|---|---|---|
| 0.05 | 18 / 48 | 38% |
| 0.10 | 29 / 48 | 60% |
| 0.20 | 39 / 48 | 81% |
| 0.30 | 44 / 48 | 92% |
| 0.50 | 47 / 48 | 98% |
| 1.00 | 48 / 48 | 100% |

## Score Range Summary

Rank-1 scores across 47 HC profiles:
  Min: -0.7486  Max: 0.1030  Mean: -0.5319

Target-state scores across 47 HC profiles:
  Min: -0.9372  Max: 0.1030  Mean: -0.6449

Gap distribution:
  Min gap: 0.0000  Max gap: 0.5424  Mean gap: 0.1130
  Profiles with gap = 0.000 (target is rank-1): 5 / 48
  Profiles with gap <= 0.050: 18 / 48
  Profiles with gap <= 0.100: 29 / 48
  Profiles with gap <= 0.200: 39 / 48

## Rank-1 Captures by State (across 47 HC profiles)

| State | Rank-1 count |
|---|---|
| built_to_fail | 20 |
| leadership_deafness | 13 |
| the_fracture | 10 |
| the_diversity_ceiling | 2 |
| identity_erosion | 2 |
| culture_drift | 1 |
