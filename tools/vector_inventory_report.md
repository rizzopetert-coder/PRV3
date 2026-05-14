# PRV3 Vector Inventory — Session 16
## Cluster State Audit + Authority HIGH State Inventory
## 2026-05-13

---

## Cluster State Inventory

All states with `signal_weight == "cluster"`.
At baseline = all 8 fields exactly 0.25. Near-baseline = max field < 0.35.

| State ID | State name | Primary dim | cluster_id | apt_l | apt_a | aut_l | aut_a | all_l | all_a | att_l | att_a | At baseline? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| the_suppression_filter | The Suppression Filter | Alliance | C-InfoFlow | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| the_dormant_talent | The Dormant Talent | Aptitude | C-Manager | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| the_overloaded_manager | The Overloaded Manager | Aptitude | C-Manager | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| the_unformed_leader | The Unformed Leader | Aptitude | C-Manager | 0.45 | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | differentiated |
| culture_drift | Culture Drift | Attitude | C-Culture | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| identity_erosion | Identity Erosion | Attitude | C-Culture | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| leadership_deafness | Leadership Deafness | Attitude | C-InfoFlow | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| the_culture_that_wasnt | The Culture That Wasn't | Attitude | C-Culture | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| the_unlocked_door | The Unlocked Door | Attitude | C-Silence | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| the_unreported_hazard | The Unreported Hazard | Attitude | C-Silence | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |
| what_nobody_says | What Nobody Says | Attitude | C-Silence | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | YES — centroid trap |

### Cluster State Summary

- Total cluster states: **11**
- At all-0.25 baseline (centroid traps): **10**
  - the_suppression_filter, the_dormant_talent, the_overloaded_manager, culture_drift, identity_erosion, leadership_deafness, the_culture_that_wasnt, the_unlocked_door, the_unreported_hazard, what_nobody_says
- Near-baseline (max field < 0.35): **0**
  - none
- Already differentiated (max field >= 0.35): **1**
  - the_unformed_leader

---

## Authority HIGH Vector Inventory

All states with `primary_dimension == 'Authority'` and `signal_weight == 'high'`.

| State ID | apt_l | apt_a | aut_l | aut_a | all_l | all_a | att_l | att_a | cluster_id | resolution_family | liability_axes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| heard_and_ignored | 0.25 | 0.25 | 0.60 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — | Intervention + Executive Counsel | Legal & Compliance; Governance & Authority; Cultural & Behavioral |
| hr_capture | 0.25 | 0.25 | 0.60 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — | Intervention + Executive Counsel | Legal & Compliance; Governance & Authority; Cultural & Behavioral |
| the_exposed | 0.25 | 0.25 | 0.60 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — | Intervention + Stability Support | Legal & Compliance; Governance & Authority; Financial & Economic |
| the_founders_grip | 0.25 | 0.25 | 0.60 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — | Intervention + Executive Counsel | Governance & Authority; Talent & Retention; Strategic |
| the_tolerated_violation | 0.25 | 0.25 | 0.60 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — | Intervention + Executive Counsel | Legal & Compliance; Cultural & Behavioral; Financial & Economic |
| the_unsolved_problem | 0.25 | 0.25 | 0.60 | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 | — | Intervention + Roadmap | Legal & Compliance; Financial & Economic; Cultural & Behavioral |

### Authority HIGH — Full State Metadata

**heard_and_ignored** (Heard & Ignored)
- resolution_family: Intervention + Executive Counsel
- liability_axes: ['Legal & Compliance', 'Governance & Authority', 'Cultural & Behavioral']
- asset_axes: ['Governance Discipline', 'Relational Trust']
- severity_range: Entrenched – Endemic
- vector: aptitude_liability=0.25, aptitude_asset=0.25, authority_liability=0.60, authority_asset=0.25, alliance_liability=0.25, alliance_asset=0.25, attitude_liability=0.25, attitude_asset=0.25

**hr_capture** (HR Capture)
- resolution_family: Intervention + Executive Counsel
- liability_axes: ['Legal & Compliance', 'Governance & Authority', 'Cultural & Behavioral']
- asset_axes: ['Governance Discipline', 'Relational Trust']
- severity_range: Entrenched – Endemic
- vector: aptitude_liability=0.25, aptitude_asset=0.25, authority_liability=0.60, authority_asset=0.25, alliance_liability=0.25, alliance_asset=0.25, attitude_liability=0.25, attitude_asset=0.25

**the_exposed** (The Exposed)
- resolution_family: Intervention + Stability Support
- liability_axes: ['Legal & Compliance', 'Governance & Authority', 'Financial & Economic']
- asset_axes: ['Governance Discipline', 'Relational Trust']
- severity_range: Emerging – Entrenched
- vector: aptitude_liability=0.25, aptitude_asset=0.25, authority_liability=0.60, authority_asset=0.25, alliance_liability=0.25, alliance_asset=0.25, attitude_liability=0.25, attitude_asset=0.25

**the_founders_grip** (The Founder's Grip)
- resolution_family: Intervention + Executive Counsel
- liability_axes: ['Governance & Authority', 'Talent & Retention', 'Strategic']
- asset_axes: ['Governance Discipline', 'Adaptive Capacity']
- severity_range: Entrenched – Endemic
- vector: aptitude_liability=0.25, aptitude_asset=0.25, authority_liability=0.60, authority_asset=0.25, alliance_liability=0.25, alliance_asset=0.25, attitude_liability=0.25, attitude_asset=0.25

**the_tolerated_violation** (The Tolerated Violation)
- resolution_family: Intervention + Executive Counsel
- liability_axes: ['Legal & Compliance', 'Cultural & Behavioral', 'Financial & Economic']
- asset_axes: ['Governance Discipline', 'Accountability Architecture']
- severity_range: Entrenched – Endemic
- vector: aptitude_liability=0.25, aptitude_asset=0.25, authority_liability=0.60, authority_asset=0.25, alliance_liability=0.25, alliance_asset=0.25, attitude_liability=0.25, attitude_asset=0.25

**the_unsolved_problem** (The Unsolved Problem)
- resolution_family: Intervention + Roadmap
- liability_axes: ['Legal & Compliance', 'Financial & Economic', 'Cultural & Behavioral']
- asset_axes: ['Adaptive Capacity', 'Governance Discipline']
- severity_range: Entrenched – Entrenched
- vector: aptitude_liability=0.25, aptitude_asset=0.25, authority_liability=0.60, authority_asset=0.25, alliance_liability=0.25, alliance_asset=0.25, attitude_liability=0.25, attitude_asset=0.25

---

## Inter-State Contrast Analysis (Authority HIGH)

Pairwise cosine similarity between all Authority HIGH state profile vectors.
cosine > 0.99 = near-identical (flagged **IDENTICAL**).
cosine > 0.95 = very similar (flagged **BUNCHED**).

| State A | State B | Cosine similarity | Flag |
|---|---|---|---|
| heard_and_ignored | hr_capture | 1.000000 | **IDENTICAL** |
| heard_and_ignored | the_exposed | 1.000000 | **IDENTICAL** |
| heard_and_ignored | the_founders_grip | 1.000000 | **IDENTICAL** |
| heard_and_ignored | the_tolerated_violation | 1.000000 | **IDENTICAL** |
| heard_and_ignored | the_unsolved_problem | 1.000000 | **IDENTICAL** |
| hr_capture | the_exposed | 1.000000 | **IDENTICAL** |
| hr_capture | the_founders_grip | 1.000000 | **IDENTICAL** |
| hr_capture | the_tolerated_violation | 1.000000 | **IDENTICAL** |
| hr_capture | the_unsolved_problem | 1.000000 | **IDENTICAL** |
| the_exposed | the_founders_grip | 1.000000 | **IDENTICAL** |
| the_exposed | the_tolerated_violation | 1.000000 | **IDENTICAL** |
| the_exposed | the_unsolved_problem | 1.000000 | **IDENTICAL** |
| the_founders_grip | the_tolerated_violation | 1.000000 | **IDENTICAL** |
| the_founders_grip | the_unsolved_problem | 1.000000 | **IDENTICAL** |
| the_tolerated_violation | the_unsolved_problem | 1.000000 | **IDENTICAL** |

Total pairs: 15
Near-identical (> 0.99): **15**
Very similar / bunched (> 0.95): **15**

---

*PRV3 Principal Brief governs. Pete confirms everything.*
*Vector inventory executed Session 16 · 2026-05-13*