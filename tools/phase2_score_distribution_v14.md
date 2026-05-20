# PRV3 Phase 2 Score Distribution v14

## Session 21 · Weighted Cosine Similarity + Salience Profiles + APT-PT-00 Repair · 2026-05-19

---

## Run Configuration

| Field | Value |
|---|---|
| Mode | Signal-driven — generate_answers() per profile type |
| Engine changes | accumulation.py: _weighted_cosine_similarity() + rank_states() weighted path; engine/data/salience.py: SALIENCE_PROFILES (47 states, 2.5/0.4 binary filter); questions.py: the_paper_tiger added to Q05 + Q12 state_targets (Q06 held); output.py: _PRECOMPUTED_NOISE_BASELINE v14 |
| Metric | Weighted cosine similarity (SALIENCE_PROFILES) |
| Profiles run | 142 (47 HC + 1 extreme HC + 47 moderate + 47 weak) |
| Floor multipliers | Authority 1.00×; non-Authority 1.08× |
| Baseline source | recalibrate_floor_v14.py — N=1000, seed=42, Q01–Q39, weighted cosine |
| Baseline mean | 0.8852 (v13: 0.8012 — delta +0.084) |

---

## Section 1 — Top-Line Result

| Version | Pass | HC | Extreme | Moderate | Weak | Dominant sink |
|---|---|---|---|---|---|---|
| v13 | **13/142** | 0/47 | 0/1 | 4/47 | 9/47 | the_uninitiated (~81) |
| v14 | **19/142** | 0/47 | 0/1 | 3/47 | 16/47 | the_uninitiated (~90+) |

**Net change: +6 from v13.** Weak profile improvement (+7). Moderate regression (−1). HC and extreme unchanged at zero. The_uninitiated dominance increased, not decreased.

---

## Section 2 — By-State Results

| State | v14 | v13 | Delta |
|---|---|---|---|
| built_to_fail | 1/3 | 1/3 | — |
| culture_drift | 0/3 | 1/3 | −1 |
| decision_blindness | 0/3 | 0/3 | — |
| decision_paralysis | 2/3 | 1/3 | +1 |
| dueling_narratives | 0/3 | 0/3 | — |
| groundhog_day | 0/3 | 0/3 | — |
| heard_and_ignored | 0/3 | 0/3 | — |
| hr_capture | 0/3 | 0/3 | — |
| identity_erosion | 0/3 | 0/3 | — |
| invisible_burnout | 1/3 | 0/3 | +1 |
| invisible_influence_architecture | 0/3 | 0/3 | — |
| leadership_continuity_risk | 2/3 | 2/3 | — |
| leadership_deafness | 0/3 | 0/3 | — |
| narrative_lock | 0/3 | 0/3 | — |
| paper_shield | 0/3 | 0/3 | — |
| pay_exposure | 0/3 | 0/3 | — |
| silosolation | 0/3 | 0/3 | — |
| the_arbitrary_standard | 0/3 | 0/3 | — |
| the_basement_standard | 0/3 | 0/3 | — |
| the_broken_compass | 0/3 | 0/3 | — |
| the_burned_credibility | 1/3 | 0/3 | +1 |
| the_culture_that_wasnt | 0/3 | 0/3 | — |
| the_diversity_ceiling | 1/3 | 0/3 | +1 |
| the_dormant_talent | 1/3 | 0/3 | +1 |
| the_exposed | 1/3 | 0/3 | +1 |
| the_founders_grip | 1/3 | 1/3 | — |
| the_fracture | 0/3 | 0/3 | — |
| the_inside_track | 0/3 | 0/3 | — |
| the_lost_map | 0/3 | 0/3 | — |
| the_overloaded_manager | 1/3 | 0/3 | +1 |
| the_paper_tiger | 0/4 | 0/4 | — |
| the_pay_fog | 0/3 | 0/3 | — |
| the_policy_lag | 1/3 | 1/3 | — |
| the_second_close | 0/3 | 0/3 | — |
| the_suppression_filter | 0/3 | 0/3 | — |
| the_tolerated_violation | 0/3 | 0/3 | — |
| the_undefined_role | 1/3 | 1/3 | — |
| the_unexamined_algorithm | 0/3 | 1/3 | −1 |
| the_unformed_leader | 1/3 | 1/3 | — |
| the_uninitiated | 2/3 | 2/3 | — |
| the_unlocked_door | 0/3 | 0/3 | — |
| the_unreported_hazard | 0/3 | 0/3 | — |
| the_unsolved_problem | 1/3 | 0/3 | +1 |
| the_untouchable | 0/3 | 0/3 | — |
| the_wrong_reward | 0/3 | 0/3 | — |
| transition_paralysis | 1/3 | 1/3 | — |
| what_nobody_says | 0/3 | 0/3 | — |

**States at 0/3: 30** (v13: 36). 6 states recovered from 0/3. Gains: invisible_burnout, the_burned_credibility, the_diversity_ceiling, the_dormant_talent, the_exposed, the_overloaded_manager, the_unsolved_problem (+7). Losses: culture_drift, the_unexamined_algorithm (−2).

---

## Section 3 — Confusion Matrix Analysis

### Sink summary

| Rank-1 sink | Profiles captured | vs v13 |
|---|---|---|
| the_uninitiated | ~90+ | Increased from ~81 |
| the_unexamined_algorithm | ~8 | Reduced from ~41 |
| culture_drift | ~5 | Reduced |
| the_founders_grip | ~3 | Minor |

### the_uninitiated capture pattern
Still dominant. HC/extreme/moderate/weak profiles from Attitude, Alliance, Aptitude, and non-UEA Authority states all route to the_uninitiated. The salience weight transformation did not reduce its geometric dominance — it may have increased it by amplifying authority_liability signal relative to the off-axis noise in all accumulated vectors. The_uninitiated's 2.5× weight on authority_liability (both axes) makes it the highest-scoring state for any accumulated vector with authority content, regardless of the target state's dimension.

### Weak profile improvement
16/47 weak profiles now pass (v13: 9/47). Weak profiles use _neutral_option() throughout — accumulated vectors are small and relatively uniform. In weighted cosine space, small uniform vectors produce different similarity distributions than in unweighted space. States whose salience profiles align with where neutral accumulation concentrates are now clearing their floor thresholds. This is the source of the +7 weak improvement.

### the_paper_tiger APT-PT-00
Still 0/4, now captured entirely by the_uninitiated (x4). The Q05 and Q12 state_targets additions were applied but did not provide sufficient aptitude signal to overcome the uninitiated's authority geometric dominance. APT-PT-00 remains regressed from v12.

### the_unexamined_algorithm regression
Dropped from 1/3 (v13) to 0/3 (v14). The vector (auth_l=0.50, apt_l=0.35) gives UEA both authority and aptitude salience weights at 2.5, but the accumulated vector under state_targets gating appears to be insufficient to clear UEA's floor (0.9612) in weighted space. Queued for investigation.

---

## Section 4 — What Worked / What Did Not

### What worked
- **Weak profile recovery (+7):** 9/47 → 16/47. Salience weights changed the noise distribution in a way that benefits weak profiles. 6 states recovered from 0/3.
- **402 tests: 0 failures.** All engine sections structurally valid after the weighted cosine refactor.
- **No NaN, no negative similarity scores.** Weighted cosine implementation is numerically stable.
- **Hard stop conditions: none triggered.** 19 > 13, no universal floor-out.

### What did not work
- **HC improvement: zero.** 0/47 HC in v13 → 0/47 HC in v14. The salience weights did not break the uninitiated sink for HC profiles.
- **Moderate regression (−1).** 4/47 → 3/47. Salience weight transformation shifted the floor upward and may have pushed one moderate profile below its threshold.
- **Gemini's 60+ target: not reached.** 19/142 is well below.
- **The_uninitiated dominance: unchanged/increased.** The root cause is in the question library, not the scoring metric.

---

## Section 5 — Root Cause Assessment

Gemini's Hypothesis B (scoring architecture) was executed as specified. The weighted cosine transformation is confirmed implemented and numerically correct. It improved weak profiles and is a valid architectural addition. But it did not resolve the HC routing failure.

The_uninitiated's dominance in v14 confirms what Gemini's Hypothesis C (compound problem) implies: the scoring architecture change alone is insufficient. The question library's structural authority accumulation is the primary driver. Even with per-state salience down-weighting of off-axis signal at ranking time, the HC profiles for non-Authority states accumulate enough authority_liability from neutral-option answers on non-state_targets questions to rank the_uninitiated (MEDIUM Authority, auth_l=0.45) above the true target state.

The distinction between Hypothesis B (metric) and Hypothesis A (question library) was not fully resolved by this run. The result suggests Hypothesis A (question library contrast injection or authority-question rebalancing) must be addressed in v15.

---

## Section 6 — Open Items Carried to v15

| Item | Status |
|---|---|
| the_uninitiated dominant sink — HC routing failure persists | PRIORITY — v15 gate. Gemini brief required. Hypothesis A (question library) must be addressed. |
| the_paper_tiger APT-PT-00 — 0/4, rank-1 uninitiated in v14 | Queued. Q05 + Q12 additions insufficient — may need Q06 revisit or vector adjustment. |
| the_unexamined_algorithm regression — 1/3 (v13) → 0/3 (v14) | New regression. Floor 0.9612 may be too high in weighted space. Queued. |
| culture_drift regression — 1/3 (v13) → 0/3 (v14) | Minor regression. Queued. |
| Authority leakage Q07/Q09/Q11/Q15/Q16/Q20/Q26/Q29 | Context now critical given persistent HC failure. Elevated priority for Gemini v15 brief. |
| Q06 state_targets for the_paper_tiger — held Session 21 | Queued for Gemini review. Pete flag: Authority-primary question, cross-axis risk. |
| recalibrate_floor.py display fix — cosmetic 1.15× label | Queued. |
| VERIFY-Q25 copy review | Queued. |
| Q23-A test profiles SEVER-05 paths | Queued. |
| Negative accumulated values runtime assertion | Queued. |
| Construction and Logistics intake industry expansion | Queued. |
| The Dormant Talent Signal Map correction | Queued. |
