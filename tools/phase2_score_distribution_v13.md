# PRV3 Phase 2 Score Distribution v13

## Session 20 · state_targets HC gating + the_unexamined_algorithm vector patch · 2026-05-19

---

## Run Configuration

| Field | Value |
|---|---|
| Mode | Signal-driven — generate_answers() per profile type |
| Engine changes | calibration_runner.py: HC/extreme state_targets gating (Change 1); states.py: the_unexamined_algorithm vector patch (Change 2); output.py: _PRECOMPUTED_NOISE_BASELINE v13 |
| Metric | Cosine similarity |
| Profiles run | 142 (47 HC + 1 extreme HC + 47 moderate + 47 weak) |
| Floor multipliers | Authority 1.00×; non-Authority 1.08× |
| Baseline source | recalibrate_floor.py v13 — N=1000, seed=42, Q01–Q39 |
| Baseline mean | 0.8012 (v12: 0.8011 — stable) |
| the_unexamined_algorithm baseline | 0.8996 (v12: 0.8926 — delta +0.0070, only shifted state) |

---

## Section 1 — Top-Line Result

| Version | Pass | HC | Extreme | Moderate | Weak | Dominant sink |
|---|---|---|---|---|---|---|
| v12 | **14/142** | 0/47 | 1/1 | 5/47 | 9/47 | the_unexamined_algorithm |
| v13 | **13/142** | 0/47 | 0/1 | 4/47 | 9/47 | the_uninitiated (NEW) |

**Net change: −1 from v12.** Pass rate declined. The_unexamined_algorithm was partially resolved as dominant sink but `the_uninitiated` has emerged as the new dominant sink, capturing approximately 81 profiles at rank-1 (vs UEA's ~41).

---

## Section 2 — By-State Results

| State | v13 | Notes |
|---|---|---|
| built_to_fail | 1/3 | |
| culture_drift | 1/3 | |
| decision_blindness | 0/3 | |
| decision_paralysis | 1/3 | |
| dueling_narratives | 0/3 | |
| groundhog_day | 0/3 | |
| heard_and_ignored | 0/3 | |
| hr_capture | 0/3 | |
| identity_erosion | 0/3 | |
| invisible_burnout | 0/3 | |
| invisible_influence_architecture | 0/3 | |
| leadership_continuity_risk | 2/3 | Moderate + weak pass via top-3/above-floor; HC at rank-3 |
| leadership_deafness | 0/3 | |
| narrative_lock | 0/3 | |
| paper_shield | 0/3 | |
| pay_exposure | 0/3 | |
| silosolation | 0/3 | |
| the_arbitrary_standard | 0/3 | |
| the_basement_standard | 0/3 | |
| the_broken_compass | 0/3 | |
| the_burned_credibility | 0/3 | |
| the_culture_that_wasnt | 0/3 | |
| the_diversity_ceiling | 0/3 | |
| the_dormant_talent | 0/3 | |
| the_exposed | 0/3 | |
| the_founders_grip | 1/3 | |
| the_fracture | 0/3 | |
| the_inside_track | 0/3 | |
| the_lost_map | 0/3 | |
| the_overloaded_manager | 0/3 | |
| the_paper_tiger | 0/4 | Regression: APT-PT-00 extreme was passing in v12; now rank-41 |
| the_pay_fog | 0/3 | |
| the_policy_lag | 1/3 | |
| the_second_close | 0/3 | |
| the_suppression_filter | 0/3 | |
| the_tolerated_violation | 0/3 | |
| the_undefined_role | 1/3 | |
| the_unexamined_algorithm | 1/3 | Same as v12 |
| the_unformed_leader | 1/3 | |
| the_uninitiated | 2/3 | Moderate + weak pass; HC at rank-2 |
| the_unlocked_door | 0/3 | |
| the_unreported_hazard | 0/3 | |
| the_unsolved_problem | 0/3 | |
| the_untouchable | 0/3 | |
| the_wrong_reward | 0/3 | |
| transition_paralysis | 1/3 | |
| what_nobody_says | 0/3 | |

**States at 0/3: 36 (same count as v12).** No state recovered from 0/3.

---

## Section 3 — Confusion Matrix Analysis

### Sink summary

| Rank-1 sink | Profiles captured | vs v12 |
|---|---|---|
| the_uninitiated | ~81 | NEW dominant sink (was ~5 in v12) |
| the_unexamined_algorithm | ~41 | Reduced from ~90+ in v12 |
| culture_drift | ~9 | Minor sink (Attitude cluster) |

### the_uninitiated capture pattern
The_uninitiated (MEDIUM Authority, auth_l=0.45, all others=0.15) captures almost all Attitude, Alliance, and non-UEA Aptitude states. It also captures many Authority MEDIUM and LOW states. Affected states include all Alliance (ALL), most Attitude (ATT), and several Aptitude (APT) states. The_uninitiated wins because even neutral options on non-state_targets questions accumulate enough authority_liability signal to match its flat MEDIUM vector.

### the_unexamined_algorithm capture pattern (residual)
Still capturing Authority HIGH and MEDIUM states that accumulate mixed auth+apt signal: invisible_influence_architecture (x3 — all), hr_capture (x2), heard_and_ignored (x2), the_exposed (x2), the_founders_grip (x2), leadership_continuity_risk (x2), paper_shield (x2), the_pay_fog (x2), the_policy_lag (x2), the_undefined_role (x2), the_unsolved_problem (x2), the_overloaded_manager (x2), the_unformed_leader (x2), the_paper_tiger (x3 — now rank-41). Change 1 reduced UEA's capture from ~90+ to ~41 — partial success.

### culture_drift as minor sink
groundhog_day (x2), narrative_lock (x2), the_broken_compass (x2), the_burned_credibility (x1), the_unformed_leader (x1), the_unreported_hazard (x1), the_untouchable (x2), transition_paralysis (x1). Attitude intra-cluster confusion — expected at this calibration stage.

---

## Section 4 — Dimensional Error Analysis

The dimensional error table exposes the structural issue clearly:

- **~80% of misclassified profiles have `predicted_dominant = authority_liability`**, regardless of their own primary dimension (Attitude, Alliance, Aptitude).
- All Alliance states route to authority_liability (ALL-DB at rank-47 — lowest ranked of any state).
- All Aptitude states except the_paper_tiger (rank-45) route to authority_liability.
- All Attitude states route to authority_liability, with a few routing to attitude_liability (culture_drift, the_broken_compass, the_untouchable — the Attitude cluster sinks).

This is the core structural problem: the question library accumulates authority_liability signal structurally across all profile types, because Authority-dimension questions dominate the Q01–Q39 library. Even with state_targets gating on HC profiles, the residual authority signal from neutral-option answers on non-state_targets questions is sufficient to rank the_uninitiated (MEDIUM Authority) above the true target state.

---

## Section 5 — Regression from v12

### APT-PT-00 regression (extreme HC → rank-41)
`the_paper_tiger` extreme profile was passing in v12. In v13 it falls to rank-41 with `predicted_dominant = authority_liability`. Root cause: HC state_targets gating (Change 1) reduced aptitude signal on non-state_targets questions. The paper_tiger's state_targets coverage in the question library may be insufficient to accumulate enough aptitude_liability relative to the authority background signal. The vector patch (Change 2) did not affect the_paper_tiger directly but the overall authority dominance increase (via the_uninitiated emergence) pushed it lower.

### Moderate regression (5→4)
One moderate profile that was passing top-3 in v12 is now outside top-3. The exact state cannot be confirmed without v12 state-by-state data, but the pattern is consistent: HC gating on non-state_targets questions reduced target-state signal for HC and moderate profiles across the board.

---

## Section 6 — Path C Assessment

### What worked
- Change 1 (HC state_targets gating): Reduced the_unexamined_algorithm's capture from ~90+ profiles to ~41. Paper_shield is confirmed resolved (no longer appears as dominant sink). This is structural progress.
- Change 2 (UEA vector patch): UEA's own 1/3 profile count held. The vector concentration (0.50/0.35) did not create new problems for UEA itself. Monte Carlo baseline shift (+0.0070) was expected and confirmed stable.

### What did not work
- HC gating did not improve pass rate — it redistributed captured profiles from UEA to the_uninitiated rather than resolving them.
- The overall pass rate declined from 14/142 to 13/142.
- Zero states recovered from 0/3.

### New dominant sink: the_uninitiated
The_uninitiated (MEDIUM Authority, auth_l=0.45) is now the dominant sink at ~81 profiles. Its MEDIUM flat vector is a geometric attractor for any accumulated vector with authority_liability content — which is nearly every profile in the question library. This is the same geometric sink pattern observed in v9 (before the tier standardization addressed centroid traps). The tier standardization differentiated UEA and paper_shield, but did not address the_uninitiated's MEDIUM geometric position.

### Implication for v14
The authority_liability structural dominance in the question library is the root cause — not vector configuration of individual states. Path C changes are complete per spec; the v14 direction requires a Gemini brief on the authority leakage mechanism before any engine changes. The_uninitiated's role as a MEDIUM-authority geometric attractor is the v14 gate item.

---

## Section 7 — Open Items Carried to v14

| Item | Status |
|---|---|
| the_uninitiated dominant sink — Gemini brief required before v14 engine changes | PRIORITY — NEW GATE ITEM |
| Authority leakage Q07/Q09/Q11/Q15/Q16/Q20/Q26/Q29 | Lower priority — context now elevated given authority dominance finding |
| the_paper_tiger APT-PT-00 regression — rank-41 in v13 | Queued |
| Intake candidates 1c/2b — committed (71d6a86), deferred for Phase 2 resolution | Queued |
| recalibrate_floor.py display fix — cosmetic 1.15× label | Queued |
| VERIFY-Q25 copy review | Queued |
| Q23-A test profiles SEVER-05 paths | Queued |
| Negative accumulated values runtime assertion | Queued |
| Construction and Logistics intake industry expansion | Queued |
| The Dormant Talent Signal Map correction (lists Attitude/Alliance; states.py=Aptitude) | Queued |
