# PRV3 -- Session 25: Co-Occurrence Matrix

Definition: two states co-occur if both appear in top-5 across an HC profile.
47 HC profiles. Co-occurrence counts are raw (out of 47 max).

---

## Top 20 Most Frequent Co-Occurrence Pairs

| Rank | State A | State B | Count (of 47) | Rate |
|------|---------|---------|--------------|------|
| 1 | built_to_fail | the_paper_tiger | 19 | 40.43% |
| 2 | built_to_fail | the_unformed_leader | 13 | 27.66% |
| 3 | the_paper_tiger | the_unformed_leader | 13 | 27.66% |
| 4 | identity_erosion | leadership_deafness | 13 | 27.66% |
| 5 | identity_erosion | the_culture_that_wasnt | 13 | 27.66% |
| 6 | leadership_deafness | the_culture_that_wasnt | 13 | 27.66% |
| 7 | decision_blindness | the_fracture | 12 | 25.53% |
| 8 | built_to_fail | the_dormant_talent | 11 | 23.40% |
| 9 | built_to_fail | the_undefined_role | 11 | 23.40% |
| 10 | the_dormant_talent | the_paper_tiger | 11 | 23.40% |
| 11 | the_dormant_talent | the_unformed_leader | 11 | 23.40% |
| 12 | the_paper_tiger | the_undefined_role | 11 | 23.40% |
| 13 | the_undefined_role | the_unformed_leader | 10 | 21.28% |
| 14 | built_to_fail | leadership_deafness | 10 | 21.28% |
| 15 | leadership_deafness | the_paper_tiger | 10 | 21.28% |
| 16 | the_dormant_talent | the_undefined_role | 9 | 19.15% |
| 17 | leadership_deafness | the_diversity_ceiling | 9 | 19.15% |
| 18 | the_burned_credibility | the_diversity_ceiling | 9 | 19.15% |
| 19 | decision_blindness | silosolation | 9 | 19.15% |
| 20 | decision_blindness | the_second_close | 9 | 19.15% |

## Named Cluster Co-Occurrence Analysis

Internal rate = avg co-occurrences among cluster-member pairs / 47 profiles.  
Cross rate = avg co-occurrences of cluster members vs non-cluster states / 47 profiles.

| Cluster | Members | Internal rate | Cross rate | Internal > Cross? |
|---------|---------|--------------|------------|-------------------|
| C-Manager | the_unformed_leader, the_overloaded_manager, the_dormant_talent | 0.078 | 0.013 | YES |
| C-Culture | culture_drift, the_culture_that_wasnt, identity_erosion | 0.092 | 0.008 | YES |
| C-Silence | what_nobody_says, the_unreported_hazard, the_unlocked_door | 0.000 | 0.001 | NO |
| C-InfoFlow | leadership_deafness, the_suppression_filter | 0.000 | 0.025 | NO |

## Cluster Detail

### C-Manager
Members: the_unformed_leader, the_overloaded_manager, the_dormant_talent
Internal avg co-occurrence count: 3.67 / 47
Cross avg co-occurrence count: 0.62 / 47

Internal pair counts:
- the_unformed_leader x the_overloaded_manager: 0/47 (0.00%)
- the_unformed_leader x the_dormant_talent: 11/47 (23.40%)
- the_overloaded_manager x the_dormant_talent: 0/47 (0.00%)

### C-Culture
Members: culture_drift, the_culture_that_wasnt, identity_erosion
Internal avg co-occurrence count: 4.33 / 47
Cross avg co-occurrence count: 0.40 / 47

Internal pair counts:
- culture_drift x the_culture_that_wasnt: 0/47 (0.00%)
- culture_drift x identity_erosion: 0/47 (0.00%)
- the_culture_that_wasnt x identity_erosion: 13/47 (27.66%)

### C-Silence
Members: what_nobody_says, the_unreported_hazard, the_unlocked_door
Internal avg co-occurrence count: 0.00 / 47
Cross avg co-occurrence count: 0.06 / 47

Internal pair counts:
- what_nobody_says x the_unreported_hazard: 0/47 (0.00%)
- what_nobody_says x the_unlocked_door: 0/47 (0.00%)
- the_unreported_hazard x the_unlocked_door: 0/47 (0.00%)

### C-InfoFlow
Members: leadership_deafness, the_suppression_filter
Internal avg co-occurrence count: 0.00 / 47
Cross avg co-occurrence count: 1.15 / 47

Internal pair counts:
- leadership_deafness x the_suppression_filter: 0/47 (0.00%)
