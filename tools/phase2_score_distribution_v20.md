# PRV3 Phase 2 Score Distribution v20

## Session 23 · Router Revert: states.py/salience.py Standardized, Architectural Finding Documented · 2026-05-24

---

## Run Configuration

| Field | Value |
|---|---|
| Mode | Signal-driven — generate_answers() per profile type |
| Engine changes | states.py: v19 Track 3 reverted (six HIGH Authority 0.70/0.05→0.60/0.10; the_uninitiated 0.40/0.10→0.45/0.15); salience.py: v19 Track 1 reverted (culture_drift attitude 1.85→2.5); questions.py: Q20 C/D 0.80 retained; accumulation.py: Two-Tier Router added then reverted — full 47-state path restored |
| Metric | Weighted cosine similarity (SALIENCE_PROFILES) — unchanged |
| Profiles run | 142 (47 HC + 1 extreme HC + 47 moderate + 47 weak) |
| Floor multipliers | Authority 1.00×; non-Authority 1.08×; ceiling 0.9650 |
| Baseline source | recalibrate_floor_v20_clean.py — N=1000, seed=42, Q01–Q39, full 47-state path |
| Baseline mean | 0.8968 (v19: 0.8915 — delta +0.0053) |
| culture_drift baseline | 0.9317 (v19: 0.9261 — delta +0.0056); floor 0.9650 (ceiling-capped) |
| the_uninitiated baseline | 0.9432 (v19: 0.9339 — delta +0.0093); floor 0.9432 |
| Six HIGH Authority states | 0.9136 (v19: 0.8751 — delta +0.0385); floor 0.9136 |

---

## Section 1 — Top-Line Result

| Version | Pass | HC | Extreme | Moderate | Weak | Dominant sink |
|---|---|---|---|---|---|---|
| v16 | **17/142** | 0/47 | 0/1 | 4/47 | 13/47 | the_uninitiated (dominant); culture_drift secondary |
| v17 | **18/142** | 0/47 | 0/1 | 7/47 | 11/47 | culture_drift (99); the_uninitiated (12) |
| v18 | **20/142** | 0/47 | 0/1 | 10/47 | 10/47 | culture_drift (60); the_overloaded_manager (48) |
| v19 | **21/142** | 0/47 | 0/1 | 9/47 | 12/47 | culture_drift (50); the_overloaded_manager (48); leadership_continuity_risk (14) |
| v20 | **20/142** | 0/47 | 0/1 | 10/47 | 10/47 | culture_drift (~55); the_overloaded_manager (~45) |

**Net change: −1 from v19.** Moderate +1. Weak −2. HC unchanged at 0/47.
**Hard stop: HC pass count is 0/47 — eighth consecutive version. Router architectural finding documented. See Section 5.**
**2 regressions** (the_exposed −1, the_unsolved_problem −1). **1 gain** (the_uninitiated +1). Net −1.

---

## Section 2 — By-State Results

| State | v20 | v19 | Delta |
|---|---|---|---|
| built_to_fail | 2/3 | 2/3 | — |
| culture_drift | 1/3 | 1/3 | — |
| decision_blindness | 0/3 | 0/3 | — |
| decision_paralysis | 1/3 | 1/3 | — |
| dueling_narratives | 0/3 | 0/3 | — |
| groundhog_day | 0/3 | 0/3 | — |
| heard_and_ignored | 0/3 | 0/3 | — |
| hr_capture | 0/3 | 0/3 | — |
| identity_erosion | 1/3 | 1/3 | — |
| invisible_burnout | 0/3 | 0/3 | — |
| invisible_influence_architecture | 0/3 | 0/3 | — |
| leadership_continuity_risk | 2/3 | 2/3 | — |
| leadership_deafness | 1/3 | 1/3 | — |
| narrative_lock | 0/3 | 0/3 | — |
| paper_shield | 0/3 | 0/3 | — |
| pay_exposure | 0/3 | 0/3 | — |
| silosolation | 1/3 | 1/3 | — |
| the_arbitrary_standard | 0/3 | 0/3 | — |
| the_basement_standard | 0/3 | 0/3 | — |
| the_broken_compass | 0/3 | 0/3 | — |
| the_burned_credibility | 0/3 | 0/3 | — |
| the_culture_that_wasnt | 0/3 | 0/3 | — |
| the_diversity_ceiling | 0/3 | 0/3 | — |
| the_dormant_talent | 1/3 | 1/3 | — |
| the_exposed | 0/3 | 1/3 | **−1** |
| the_founders_grip | 1/3 | 1/3 | — |
| the_fracture | 0/3 | 0/3 | — |
| the_inside_track | 0/3 | 0/3 | — |
| the_lost_map | 0/3 | 0/3 | — |
| the_overloaded_manager | 1/3 | 1/3 | — |
| the_paper_tiger | 0/4 | 0/4 | — |
| the_pay_fog | 0/3 | 0/3 | — |
| the_policy_lag | 1/3 | 1/3 | — |
| the_second_close | 0/3 | 0/3 | — |
| the_suppression_filter | 0/3 | 0/3 | — |
| the_tolerated_violation | 0/3 | 0/3 | — |
| the_undefined_role | 2/3 | 2/3 | — |
| the_unexamined_algorithm | 0/3 | 0/3 | — |
| the_unformed_leader | 2/3 | 2/3 | — |
| the_uninitiated | 2/3 | 1/3 | **+1** |
| the_unlocked_door | 0/3 | 0/3 | — |
| the_unreported_hazard | 0/3 | 0/3 | — |
| the_unsolved_problem | 0/3 | 1/3 | **−1** |
| the_untouchable | 0/3 | 0/3 | — |
| the_wrong_reward | 0/3 | 0/3 | — |
| transition_paralysis | 1/3 | 1/3 | — |
| what_nobody_says | 0/3 | 0/3 | — |

**States at 0/3: 32** (v19: 31). 1 recovery (the_uninitiated). 2 new zeros (the_exposed, the_unsolved_problem).

---

## Section 3 — Router Experiment Summary (v20 intermediate)

The Two-Tier Hierarchical Router was implemented, tested, and reverted within this session. Key findings from the intermediate router run (13/142):

### Router result: 13/142 (HC 1/47 — regression from v19 21/142)

| Dimension | HC profiles | HC passes | Primary failure mode |
|---|---|---|---|
| Authority | 18 | 0/18 | 6/18 routed to wrong dim; 12/18 correct dim but intra-Auth sinks (the_uninitiated ×6, paper_shield ×4) |
| Attitude | 17 | 1/17 | Correct routing; culture_drift captured 15/16 within Attitude pool |
| Aptitude | 6 | 0/6 | 5/6 routed to Attitude (wrong dim) |
| Alliance | 6 | 0/6 | 6/6 routed to Authority or Attitude (wrong dim) |

### Dimension routing diagnostic (generate_answers() accumulated vectors)

Alliance + Aptitude HC profiles (12 profiles): 11/12 produce wrong-dimension dominant vectors.
- Alliance HC: Authority dominant (×3) or Attitude dominant (×3) — 0/6 correct
- Aptitude HC: Attitude dominant (×4), Authority (×1) — 1/6 correct (the_undefined_role only)

Root cause: 39-question traversal loads Authority and Attitude signal as background from neutral options across all questions. With only 6 Aptitude states and 6 Alliance states, there are fewer targeted questions to overcome the background loading. Authority dominates in 91.5% of random noise runs.

---

## Section 4 — Root Cause Assessment

**Intra-dimensional sink dominance is the primary unsolved constraint.** The router proved that narrowing competition does not help when the sink is the strongest state within its own dimension pool. culture_drift captured 15/17 Attitude HC profiles in within-dimension competition — worse than its rate in full-ranking.

**The floor-clearing problem is solved — the rank-ordering problem is not.** From v18 diagnostic (still valid v20): target scores range 0.87–0.98, sinks score 0.92–0.98. Margin 0.01–0.03 for most HC profiles. Incremental parameter adjustments move this by ±0.005 per step — insufficient at scale.

**v19 Track 3 (Authority vector sharpening) was a net negative net.** Reverting it (v20 states.py standardization) costs the_exposed and the_unsolved_problem but these were floor-lowering gains, not cosine rank-ordering gains. The states are better positioned at 0.60/0.10 (standard) than at 0.70/0.05 (sharpened) for the router architecture that is coming.

---

## Section 5 — Router Architectural Finding (verbatim for Gemini handoff)

The Two-Tier Hierarchical Router was implemented and tested in v20. It failed to improve HC routing for two reasons: (1) intra-dimensional sink dominance — culture_drift captured 15/17 Attitude HC profiles within the Attitude-only competition pool, proving that narrowing the competition space does not resolve sink dominance when the sink is the strongest state in its own dimension; (2) question library signal insufficiency — 11/12 Alliance and Aptitude HC profiles produced wrong-dimension dominant vectors under generate_answers(), routing them to Authority or Attitude competition pools. The router is a valid architectural concept but requires either (a) a mechanism to suppress or score-penalize known intra-dimensional sinks, or (b) question library signal sufficient to produce correct dimension-dominant vectors for all four dimensions before the router can function. Both are prerequisites for the router to work. The full 47-state path is restored in v20.

---

## Section 6 — Open Items Carried to v21

| Item | Status |
|---|---|
| HC routing failure — 0/47 across v13–v20 | PRIORITY. Hard stop. Eight versions at 0/47. Intra-dimensional sink dominance is the active constraint. |
| Router prerequisites — two unmet before re-attempt | (a) sink suppression/penalization mechanism; (b) question library signal sufficient for all 4 dimensions |
| culture_drift intra-dimensional dominance | Captures 15/17 Attitude HC within Attitude pool. Primary Attitude sink. |
| the_overloaded_manager co-dominant sink — ~45 captures | Unchanged. Aptitude primary salience (2.5) not addressed. |
| the_uninitiated intra-Authority sink — 6+ captures | Captures HC Authority profiles. Intra-Authority routing problem. |
| paper_shield intra-Authority sink — 4+ captures | Secondary intra-Authority sink. |
| APT-PT-00 (the_paper_tiger) — still 0/4 | Routing to built_to_fail (×3) + culture_drift (×1). |
| the_fracture — still 0/3 | Routing to the_suppression_filter (×2) + the_overloaded_manager (×1). |
| Mode 2 floor deficits (Track 4) — deferred | the_arbitrary_standard, what_nobody_says, the_dormant_talent, the_overloaded_manager. |
| Q06 neutral drain | Skipped v17–v20. Carries to v21. |
| VERIFY-Q25 copy review | Queued. |
| Q23-A SEVER-05 paths | Queued. |
| Negative accumulated values assertion | Queued. |
| Construction and Logistics intake expansion | Queued. |
| The Dormant Talent Signal Map correction | Queued. |
