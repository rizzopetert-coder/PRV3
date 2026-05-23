# PRV3 Phase 2 Score Distribution v17

## Session 23 · Signal Amplification + Neutral Drain · 2026-05-23

---

## Run Configuration

| Field | Value |
|---|---|
| Mode | Signal-driven — generate_answers() per profile type |
| Engine changes | questions.py: signal amp Q07-B(0.80), Q11-D(0.75), Q15-D(0.75), Q26-C(0.80), Q35-B(0.80), Q36-E(0.80); neutral drain Q01-B(−0.15), Q13-E(−0.15), Q28-B(−0.15); output.py: _PRECOMPUTED_NOISE_BASELINE v17 |
| Metric | Weighted cosine similarity (SALIENCE_PROFILES) — unchanged from v16 |
| Profiles run | 142 (47 HC + 1 extreme HC + 47 moderate + 47 weak) |
| Floor multipliers | Authority 1.00×; non-Authority 1.08× |
| Baseline source | recalibrate_floor_v17.py — N=1000, seed=42, Q01–Q39, weighted cosine |
| Baseline mean | 0.8968 (v16: 0.8945 — delta +0.0023) |
| the_uninitiated baseline | 0.9439 (v16: 0.9503 — delta −0.0064) |
| culture_drift baseline | 0.9318 (v16: 0.9272 — delta +0.0046) |

---

## Section 1 — Top-Line Result

| Version | Pass | HC | Extreme | Moderate | Weak | Dominant sink |
|---|---|---|---|---|---|---|
| v13 | **13/142** | 0/47 | 0/1 | 4/47 | 9/47 | the_uninitiated (~81) |
| v14 | **19/142** | 0/47 | 0/1 | 3/47 | 16/47 | the_uninitiated (~90+) |
| v15 | **15/142** | 0/47 | 0/1 | 3/47 | 12/47 | the_uninitiated (dominant) |
| v16 | **17/142** | 0/47 | 0/1 | 4/47 | 13/47 | the_uninitiated (dominant); culture_drift secondary |
| v17 | **18/142** | 0/47 | 0/1 | 7/47 | 11/47 | culture_drift (99 captures); the_uninitiated secondary (12) |

**Net change: +1 from v16.** Moderate +3. Weak −2. HC unchanged at 0/47.
**Hard stop triggered:** culture_drift is now dominant sink with 99 rank-1 captures vs the_uninitiated's 12. Handoff condition: "flag immediately."
**5 regressions** from v16 (decision_paralysis −1, leadership_continuity_risk −1, the_exposed −1, the_uninitiated −1, the_unsolved_problem −1). **6 gains** (built_to_fail +1, culture_drift +1, silosolation +1, the_burned_credibility +1, the_undefined_role +1, the_unformed_leader +1). Gemini target 11+/47 HC: not achieved.

---

## Section 2 — By-State Results

| State | v17 | v16 | Delta |
|---|---|---|---|
| built_to_fail | 2/3 | 1/3 | **+1** |
| culture_drift | 2/3 | 1/3 | **+1** |
| decision_blindness | 0/3 | 0/3 | — |
| decision_paralysis | 1/3 | 2/3 | **−1** |
| dueling_narratives | 0/3 | 0/3 | — |
| groundhog_day | 0/3 | 0/3 | — |
| heard_and_ignored | 0/3 | 0/3 | — |
| hr_capture | 0/3 | 0/3 | — |
| identity_erosion | 0/3 | 0/3 | — |
| invisible_burnout | 0/3 | 0/3 | — |
| invisible_influence_architecture | 0/3 | 0/3 | — |
| leadership_continuity_risk | 1/3 | 2/3 | **−1** |
| leadership_deafness | 0/3 | 0/3 | — |
| narrative_lock | 0/3 | 0/3 | — |
| paper_shield | 0/3 | 0/3 | — |
| pay_exposure | 0/3 | 0/3 | — |
| silosolation | 1/3 | 0/3 | **+1** |
| the_arbitrary_standard | 0/3 | 0/3 | — |
| the_basement_standard | 0/3 | 0/3 | — |
| the_broken_compass | 0/3 | 0/3 | — |
| the_burned_credibility | 1/3 | 0/3 | **+1** |
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
| the_undefined_role | 2/3 | 1/3 | **+1** |
| the_unexamined_algorithm | 0/3 | 0/3 | — |
| the_unformed_leader | 2/3 | 1/3 | **+1** |
| the_uninitiated | 1/3 | 2/3 | **−1** |
| the_unlocked_door | 0/3 | 0/3 | — |
| the_unreported_hazard | 0/3 | 0/3 | — |
| the_unsolved_problem | 0/3 | 1/3 | **−1** |
| the_untouchable | 0/3 | 0/3 | — |
| the_wrong_reward | 0/3 | 0/3 | — |
| transition_paralysis | 1/3 | 1/3 | — |
| what_nobody_says | 0/3 | 0/3 | — |

**States at 0/3: 33** (v16: 33). 2 recoveries (silosolation, the_burned_credibility). 2 new zeros (the_exposed, the_unsolved_problem). Net 0 change in zero count.

---

## Section 3 — Confusion Matrix Analysis

### Sink summary

| Rank-1 sink | v17 observation | vs v16 |
|---|---|---|
| culture_drift | **Dominant — 99 total captures across 45 states** | Elevated from secondary (~16) to primary |
| the_uninitiated | Secondary — 12 captures (6 HC + 6 moderate) | Sharply reduced from dominant |
| built_to_fail | Tertiary — captures the_paper_tiger (x3), the_undefined_role (x2) | Unchanged from v16 |
| the_overloaded_manager | Captures the_dormant_talent (x2), the_unexamined_algorithm (x2), the_unformed_leader (x2) | Unchanged role |
| the_suppression_filter | Captures the_fracture (x2) | Unchanged from v16 |
| the_unformed_leader | Captures the_second_close (x2) | Unchanged |
| the_unexamined_algorithm | Captures the_policy_lag (x2) | Unchanged |

### culture_drift — new dominant sink (HARD STOP)

v16: secondary sink (~16 captures, primarily Attitude/Alliance cluster). v17: primary sink, 99 captures across 45 of 47 states.

**Capture by profile type:** HC 26, moderate 29, weak 44. Notably, 26 HC profiles now route to culture_drift (up from ~0 in v16).

**Root cause — v17 neutral drain:** Reducing authority_liability on Q01-B (0.25→−0.15), Q13-E (new −0.15), Q28-B (0.25→−0.15) reduced authority accumulation on neutral traversals for all profiles. The accumulated vector shifted away from the_uninitiated's Authority-dominant pattern. culture_drift has salience weight 2.5 on BOTH authority_liability AND attitude_liability — it is the next geometric attractor when authority accumulation decreases but attitude accumulation stays flat or rises. The neutral drain moved profiles out of the_uninitiated basin and into culture_drift's basin.

**Signal amplification contribution:** Raising Q07-B/Q26-C (alliance), Q11-D/Q15-D (attitude), Q35-B/Q36-E (aptitude) increased non-authority signal for HC profiles. Combined with reduced authority accumulation, the ratio of attitude/alliance to authority content increased. culture_drift's high attitude salience (2.5) absorbed this shift.

**culture_drift floor note:** culture_drift v17 noise baseline is 0.9318 (non-Authority × 1.08 = floor 1.0063). This floor exceeds maximum cosine similarity. In a production context, culture_drift as rank-1 would always fall through to the OutputEngine's multi-state or insufficient_signal routing. The calibration captures it as rank-1 in the raw cosine ranking before floor application.

### the_uninitiated — compressed from dominant to secondary

v16: dominant (~80+ captures). v17: 12 captures (6 HC + 6 moderate). The neutral drain succeeded in removing the_uninitiated as the geometric attractor. However, the displaced profiles moved to culture_drift rather than their correct targets.

### HC routing — unchanged at 0/47

HC profiles now route primarily to culture_drift (26 captures) rather than the_uninitiated. The problem structure is the same: primary dimension signal is insufficient to clear the correct state's floor when a dimensional neighbor (culture_drift) captures the cosine ranking. The signal amplification raised the best-option liability values (0.80 Aptitude/Alliance, 0.75 Attitude), but the neutral traversal questions for the 30+ non-target questions still accumulate enough Attitude+Authority mixture to align with culture_drift's broad salience profile.

---

## Section 4 — What Worked / What Did Not

### What worked

- **+1 net improvement from v16.** No net floor regression on test suite (402/402 pass).
- **the_uninitiated unseated as dominant sink.** 80+ → 12 captures. The neutral drain on Q01-B/Q13-E/Q28-B reduced Authority accumulation as designed.
- **Moderate +3 net gain.** silosolation, the_burned_credibility new; culture_drift, built_to_fail, the_undefined_role, the_unformed_leader increased. Moderate-tier profiles with lower signal-to-noise thresholds benefited from signal amplification.
- **Signal amplification shifted HC routing.** HC profiles are no longer routing exclusively to the_uninitiated. They now route to culture_drift — wrong, but different wrong. Indicates the primary dimension signal is now stronger relative to authority, as designed.
- **402/402 tests pass.** Engine structurally valid.
- **S18 and v16 contrast fields confirmed invariant.**

### What did not work

- **HC routing: unchanged at 0/47.** Gemini target 11+/47: not achieved.
- **culture_drift dominance: hard stop.** Neutral drain succeeded at reducing authority accumulation but introduced culture_drift as a new geometric attractor. culture_drift's dual Authority+Attitude salience profile (2.5 each) makes it a broad absorber when the accumulated vector has a mixed authority+attitude content.
- **5 regressions from v16.** decision_paralysis, leadership_continuity_risk, the_exposed, the_uninitiated, the_unsolved_problem all lost a passing profile. All 5 regressions traced to culture_drift capture.

---

## Section 5 — Root Cause Assessment

**Two-move strategy diagnosis:** The v17 strategy correctly identified the two problems (insufficient primary signal, excessive authority accumulation) but the interaction was not anticipated. Reducing authority accumulation (neutral drain) moves the cosine vector away from the_uninitiated but into culture_drift's basin because culture_drift has equal salience weight on Authority and Attitude. Any vector with a moderate authority component and even a small attitude component will cosine-align with culture_drift.

**The arithmetic of culture_drift capture:** culture_drift state vector: authority_liability=0.25, attitude_liability=0.35. Salience weights: authority 2.5, attitude 2.5. A profile accumulating ~2.0 authority_liability and ~0.5 attitude_liability will get a high weighted cosine score against culture_drift because both salient dimensions are present in proportion to the state vector.

Before v17 (v16 neutral traversals): authority accumulation ~2.40. Attitude accumulation from neutral traversal ~0.50–0.80. the_uninitiated dominated because authority was so high that the pure authority match won. After v17 neutral drain: authority ~2.10 (−0.30 from three questions). Attitude accumulation unchanged. The reduction in authority moved the vector into culture_drift's mixed-attractor basin.

**What would break the culture_drift lock:** Either (a) reduce culture_drift's authority salience weight (architectural change), (b) install negative attitude signal on the same neutral drain questions to prevent attitude accumulation, or (c) install positive primary-dimension signal strong enough to clear the target state's floor before culture_drift captures the rank-1 position. The v17 signal amplification (0.80/0.75) is a step toward (c) but the target state's floor also rose with the new baseline, leaving relative separation unchanged.

---

## Section 6 — Open Items Carried to v18

| Item | Status |
|---|---|
| HC routing failure — 0/47 across v13–v17 | PRIORITY. culture_drift now dominant sink. Neutral drain displaced the_uninitiated but culture_drift absorbed displaced profiles. v18 brief required. |
| culture_drift dominant sink — hard stop | NEW PRIORITY. 99 captures. Root cause: culture_drift dual Authority+Attitude salience (2.5 each) absorbs mixed vectors. Requires targeted architectural response. |
| 5 regressions from v16 | decision_paralysis, leadership_continuity_risk, the_exposed, the_uninitiated, the_unsolved_problem. All from culture_drift capture. |
| APT-PT-00 (the_paper_tiger) — still 0/4 | Routing to built_to_fail (x3). No regression from v16. |
| the_fracture — still 0/3 | Routing to the_suppression_filter (x2) + culture_drift (x1). No change from partial v16 progress. |
| Q06 neutral drain — skipped v17 | Neutral pick shift hard stop not resolved. Carries to v18. |
| recalibrate_floor.py cosmetic 1.15× label fix | Queued. |
| VERIFY-Q25 copy review | Queued. |
| Q23-A test profiles SEVER-05 paths | Queued. |
| Negative accumulated values runtime assertion | Queued. |
| Construction and Logistics intake expansion | Queued. |
| The Dormant Talent Signal Map correction | Queued. |
