# PRV3 Phase 2 Score Distribution v16

## Session 22 · Contrast Injection Q14/Q16/Q22/Q26/Q35/Q36 · 2026-05-23

---

## Run Configuration

| Field | Value |
|---|---|
| Mode | Signal-driven — generate_answers() per profile type |
| Engine changes | questions.py: contrast injection Q14-B/C (−0.30), Q16-B/C (−0.30), Q22-B (−0.35), Q26-C (−0.30), Q35-B (−0.35), Q36-E (−0.40); output.py: _PRECOMPUTED_NOISE_BASELINE v16 |
| Metric | Weighted cosine similarity (SALIENCE_PROFILES) — unchanged from v15 |
| Profiles run | 142 (47 HC + 1 extreme HC + 47 moderate + 47 weak) |
| Floor multipliers | Authority 1.00×; non-Authority 1.08× |
| Baseline source | recalibrate_floor_v16.py — N=1000, seed=42, Q01–Q39, weighted cosine |
| Baseline mean | 0.8962 (v15: 0.8937 — delta +0.0025) |

---

## Section 1 — Top-Line Result

| Version | Pass | HC | Extreme | Moderate | Weak | Dominant sink |
|---|---|---|---|---|---|---|
| v13 | **13/142** | 0/47 | 0/1 | 4/47 | 9/47 | the_uninitiated (~81) |
| v14 | **19/142** | 0/47 | 0/1 | 3/47 | 16/47 | the_uninitiated (~90+) |
| v15 | **15/142** | 0/47 | 0/1 | 3/47 | 12/47 | the_uninitiated (dominant) |
| v16 | **17/142** | 0/47 | 0/1 | 4/47 | 13/47 | the_uninitiated (dominant); culture_drift secondary |

**Net change: +2 from v15.** Moderate +1 (culture_drift recovered). Weak +1 (the_overloaded_manager recovered). HC unchanged at 0/47. No regressions from v15. Gemini expected 20+/47 HC — not achieved.

**Hard stop note:** Handoff specified hard stop if below "v15 (19/142)." v15 actual was 15/142; 19/142 was v14. v16=17 > v15=15 — no regression from v15. Pete decides whether to accept or route to v17.

---

## Section 2 — By-State Results

| State | v16 | v15 | Delta |
|---|---|---|---|
| built_to_fail | 1/3 | 1/3 | — |
| culture_drift | 1/3 | 0/3 | **+1** |
| decision_blindness | 0/3 | 0/3 | — |
| decision_paralysis | 2/3 | 2/3 | — |
| dueling_narratives | 0/3 | 0/3 | — |
| groundhog_day | 0/3 | 0/3 | — |
| heard_and_ignored | 0/3 | 0/3 | — |
| hr_capture | 0/3 | 0/3 | — |
| identity_erosion | 0/3 | 0/3 | — |
| invisible_burnout | 0/3 | 0/3 | — |
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
| the_burned_credibility | 0/3 | 0/3 | — |
| the_culture_that_wasnt | 0/3 | 0/3 | — |
| the_diversity_ceiling | 0/3 | 0/3 | — |
| the_dormant_talent | 1/3 | 1/3 | — |
| the_exposed | 1/3 | 1/3 | — |
| the_founders_grip | 1/3 | 1/3 | — |
| the_fracture | 0/3 | 0/3 | — |
| the_inside_track | 0/3 | 0/3 | — |
| the_lost_map | 0/3 | 0/3 | — |
| the_overloaded_manager | 1/3 | 0/3 | **+1** |
| the_paper_tiger | 0/4 | 0/4 | — |
| the_pay_fog | 0/3 | 0/3 | — |
| the_policy_lag | 1/3 | 1/3 | — |
| the_second_close | 0/3 | 0/3 | — |
| the_suppression_filter | 0/3 | 0/3 | — |
| the_tolerated_violation | 0/3 | 0/3 | — |
| the_undefined_role | 1/3 | 1/3 | — |
| the_unexamined_algorithm | 0/3 | 0/3 | — |
| the_unformed_leader | 1/3 | 1/3 | — |
| the_uninitiated | 2/3 | 2/3 | — |
| the_unlocked_door | 0/3 | 0/3 | — |
| the_unreported_hazard | 0/3 | 0/3 | — |
| the_unsolved_problem | 1/3 | 1/3 | — |
| the_untouchable | 0/3 | 0/3 | — |
| the_wrong_reward | 0/3 | 0/3 | — |
| transition_paralysis | 1/3 | 1/3 | — |
| what_nobody_says | 0/3 | 0/3 | — |

**States at 0/3: 33** (v15: 34). 2 recoveries: culture_drift, the_overloaded_manager. 0 new regressions.

---

## Section 3 — Confusion Matrix Analysis

### Sink summary

| Rank-1 sink | v16 observation | vs v15 |
|---|---|---|
| the_uninitiated | Dominant — majority of non-passing profiles | Unchanged dominant |
| culture_drift | Strong secondary — captures ~16 profiles across Attitude/Alliance cluster | Elevated from minor in v15 |
| the_overloaded_manager | Tertiary — captures the_paper_tiger (x3), the_undefined_role (x2) | New prominence |
| paper_shield | Captures the_fracture (x2) | New sink for the_fracture |

### the_uninitiated

Still dominant. HC=0/47 unchanged. the_uninitiated noise baseline: v15=0.9582 → v16=0.9503 (−0.0079 — third consecutive compression). Floor movement confirmed directional but HC profiles still accumulate sufficient authority_liability from primary Authority questions (Q01, Q02, Q03, Q04, Q06, Q11, Q13, Q21, Q23, Q28) to rank the_uninitiated above all correct targets.

Contrast injection (Q14-B/C, Q22-B) reduces authority accumulation on neutral traversals. Effect at noise level confirmed. Effect at HC routing level: insufficient — HC profiles do not traverse Q14/Q22 neutrally; they use best_option_for_state() on those questions when their target state appears in state_targets. For HC profiles targeting non-Authority states, the neutral drain fires on Q14 and Q22, but primary Authority accumulation from Q01/Q02/Q04/Q06/Q11 overwhelms it.

### culture_drift — new strong secondary sink

v15: minor sink (groundhog_day x2, identity_erosion x1). v16: captures ~16 profiles including invisible_burnout, the_culture_that_wasnt, the_diversity_ceiling, the_inside_track, the_suppression_filter, the_unlocked_door, the_unreported_hazard, the_unformed_leader, the_wrong_reward, groundhog_day, identity_erosion, transition_paralysis, what_nobody_says. Culture_drift's noise baseline: v15=0.9170 → v16=0.9272 (+0.0102 — increased). The contrast injection shifted noise distribution toward Attitude/Alliance dimensions, elevating culture_drift (MEDIUM Attitude flat vector) as a secondary attractor.

### the_paper_tiger APT-PT-00 routing shift

v15: → the_unexamined_algorithm (x3) + the_uninitiated (x1). v16: → the_overloaded_manager (x3) + culture_drift (x1). UEA no longer capturing. Q36-E aptitude injection (−0.40) reduced the mixed apt/auth blend that was routing to UEA. Paper Tiger now routes to the_overloaded_manager — both Aptitude states with overlapping aptitude_liability salience. Still 0/4.

### the_fracture — new sink: paper_shield

v15: → the_uninitiated (3/3). v16: → paper_shield (x2) + the_uninitiated (x1). paper_shield capturing Alliance+Authority mixed vectors. Q26-C contrast (−0.30 authority) reduced authority accumulation for the_fracture HC, shifting routing away from the_uninitiated but not to the_fracture itself. Ongoing — 0/3.

---

## Section 4 — What Worked / What Did Not

### What worked

- **+2 net improvement from v15.** culture_drift 0/3 → 1/3; the_overloaded_manager 0/3 → 1/3. No regressions.
- **the_uninitiated baseline compressed third consecutive version.** v14=0.9659 → v15=0.9582 → v16=0.9503 (−0.0079 each step). The geometric attractor floor is moving.
- **APT-PT-00 routing shifted away from UEA.** Q36-E injection decoupled Paper Tiger from the_unexamined_algorithm. New sink (the_overloaded_manager) is Aptitude-proximate — progress.
- **the_fracture shifted from the_uninitiated (3/3) to paper_shield (2/3) + uninitiated (1/3).** Q26-C contrast reduced authority capture for the_fracture.
- **402 tests: 0 failures.** Engine structurally valid after all writes.
- **0 regressions from v15.** All 15 v15 passes held.

### What did not work

- **HC routing: unchanged.** 0/47 HC across v13–v16. Gemini expected 20+/47. Contrast injection at neutral traversal points (Q14-B/C, Q22-B) did not fire for HC profiles — HC profiles use best_option_for_state() on questions where their target state is in state_targets, bypassing the neutral drain. The drain only fires on neutral-traversal profiles (moderate/weak partially, non-target-state questions).
- **culture_drift baseline inflation.** culture_drift noise baseline rose +0.0102 (to 0.9272). This is now the highest non-Authority baseline in the library. culture_drift (MEDIUM Attitude) is capturing Attitude/Alliance cluster states that the contrast injection shifted away from the_uninitiated.
- **Gemini 20+/47 HC target: not reached.** 0/47.

---

## Section 5 — Root Cause Assessment

The contrast injection confirmed a structural design constraint: HC profiles do not traverse questions neutrally on the authority primary path. For HC profiles targeting non-Authority states:
- On Q14: their target state is NOT in Q14's state_targets → they use _neutral_option() → Q14-B (authority_liability=−0.05). The drain fires.
- On Q22: same → Q22-B (authority_liability=−0.10). The drain fires.
- On Q26: the_fracture/silosolation HC → Q26-C (alliance_liability=0.60, authority_liability=−0.30). The drain fires.
- On Q35/Q36: Aptitude HC → B/E best-option picks with authority drain. The drain fires.

But HC profiles for non-Authority states also traverse the PRIMARY Authority questions (Q01, Q02, Q04, Q06, Q11, Q13, Q21, Q23, Q28) via _neutral_option(). These questions carry authority_liability=0.25–0.60 on their neutral options, and those values are not drained. The cumulative authority_liability from 8+ primary Authority neutral answers overwhelms the 3–5 contrast drains installed.

**The arithmetic:** Primary Authority neutral accumulation ≈ 8 questions × ~0.30 avg = ~2.40 authority_liability. Contrast drains installed: Q14-B(−0.05) + Q22-B(−0.10) + Q26-C(−0.30) + Q35-B(−0.35) + Q36-E(−0.40) = −1.20 total. Net authority still strongly positive for non-Authority HC profiles, sustaining the_uninitiated's geometric advantage.

The v17 question: the drain magnitude installed (−1.20 total) is approximately half the primary authority accumulation load (~2.40). To break HC routing, either: (a) primary Authority questions must have their neutral options drained further, or (b) the non-Authority signal must be amplified. The contrast approach is correct in mechanism; magnitude is insufficient.

---

## Section 6 — Open Items Carried to v17

| Item | Status |
|---|---|
| HC routing failure — 0/47 across v13–v16 | PRIORITY. Contrast injection directionally correct but magnitude insufficient (~−1.20 drain vs ~+2.40 primary authority accumulation). v17 brief required. |
| culture_drift secondary sink elevation | New. Noise baseline 0.9272 (highest non-Authority). May need targeted state separation or culture_drift floor reduction. |
| APT-PT-00 — still 0/4; new sink the_overloaded_manager | Routing shifted from UEA → overloaded_manager. Aptitude-proximate but wrong. |
| the_fracture — 0/3; new partial shift to paper_shield | Progress: 3/3 uninitiated → 2/3 paper_shield + 1/3 uninitiated. Needs further Alliance signal injection. |
| the_unexamined_algorithm — 0/3 persists | Queued. |
| recalibrate_floor.py cosmetic 1.15× label fix | Queued. |
| VERIFY-Q25 copy review | Queued. |
| Q23-A test profiles SEVER-05 paths | Queued. |
| Negative accumulated values runtime assertion | Queued. |
| Construction and Logistics intake industry expansion | Queued. |
| The Dormant Talent Signal Map correction | Queued. |
