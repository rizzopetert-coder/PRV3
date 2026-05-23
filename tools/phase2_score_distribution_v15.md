# PRV3 Phase 2 Score Distribution v15

## Session 22 · Authority Drain + state_targets Purge Q01-Q11 + APT-PT-00 Q06 Fix · 2026-05-22

---

## Run Configuration

| Field | Value |
|---|---|
| Mode | Signal-driven — generate_answers() per profile type |
| Engine changes | questions.py: authority drain Q07/Q09/Q16/Q20/Q26/Q29 (_opt_contrib); state_targets purge Q07/Q09; Q06 state_targets + option D vector (APT-PT-00 fix); output.py: _PRECOMPUTED_NOISE_BASELINE v15 |
| Metric | Weighted cosine similarity (SALIENCE_PROFILES) — unchanged from v14 |
| Profiles run | 142 (47 HC + 1 extreme HC + 47 moderate + 47 weak) |
| Floor multipliers | Authority 1.00×; non-Authority 1.08× |
| Baseline source | recalibrate_floor_v15.py — N=1000, seed=42, Q01–Q39, weighted cosine |
| Baseline mean | 0.8937 (v14: 0.8852 — delta +0.0085) |

---

## Section 1 — Top-Line Result

| Version | Pass | HC | Extreme | Moderate | Weak | Dominant sink |
|---|---|---|---|---|---|---|
| v13 | **13/142** | 0/47 | 0/1 | 4/47 | 9/47 | the_uninitiated (~81) |
| v14 | **19/142** | 0/47 | 0/1 | 3/47 | 16/47 | the_uninitiated (~90+) |
| v15 | **15/142** | 0/47 | 0/1 | 3/47 | 12/47 | the_uninitiated (dominant) |

**Net change: −4 from v14.** Weak profile regression (−4). HC, extreme, moderate unchanged. Hard stop condition triggered (below v14). Accepted as-is per Pete's direction — authority drain directionally correct; weak regressions are floor inflation artifacts.

---

## Section 2 — By-State Results

| State | v15 | v14 | Delta |
|---|---|---|---|
| built_to_fail | 1/3 | 1/3 | — |
| culture_drift | 0/3 | 0/3 | — |
| decision_blindness | 0/3 | 0/3 | — |
| decision_paralysis | 2/3 | 2/3 | — |
| dueling_narratives | 0/3 | 0/3 | — |
| groundhog_day | 0/3 | 0/3 | — |
| heard_and_ignored | 0/3 | 0/3 | — |
| hr_capture | 0/3 | 0/3 | — |
| identity_erosion | 0/3 | 0/3 | — |
| invisible_burnout | 0/3 | 1/3 | −1 |
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
| the_burned_credibility | 0/3 | 1/3 | −1 |
| the_culture_that_wasnt | 0/3 | 0/3 | — |
| the_diversity_ceiling | 0/3 | 1/3 | −1 |
| the_dormant_talent | 1/3 | 1/3 | — |
| the_exposed | 1/3 | 1/3 | — |
| the_founders_grip | 1/3 | 1/3 | — |
| the_fracture | 0/3 | 0/3 | — |
| the_inside_track | 0/3 | 0/3 | — |
| the_lost_map | 0/3 | 0/3 | — |
| the_overloaded_manager | 0/3 | 1/3 | −1 |
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

**States at 0/3: 34** (v14: 30). 4 states regressed: invisible_burnout, the_burned_credibility, the_diversity_ceiling, the_overloaded_manager. No new recoveries.

---

## Section 3 — Confusion Matrix Analysis

### Sink summary

| Rank-1 sink | v15 observation | vs v14 |
|---|---|---|
| the_uninitiated | Dominant — majority of non-passing profiles | Unchanged dominant |
| the_unexamined_algorithm | Secondary sink — leadership_continuity_risk, paper_shield, the_policy_lag, the_paper_tiger (x3) | Now capturing APT-PT-00 |
| culture_drift | Tertiary sink — narrative_lock, groundhog_day, the_basement_standard, the_burned_credibility | Minor |
| the_founders_grip | Captures the_unsolved_problem | Minor |

### the_uninitiated

Still dominant. HC=0/47. Authority drain reduced the_uninitiated's noise baseline (0.9659 → 0.9582 — delta −0.0077, largest Authority-primary decrease). Directional progress confirmed at the noise level. HC profiles still accumulate sufficient authority_liability through the question layer to rank the_uninitiated above any correct target state.

### the_paper_tiger APT-PT-00 routing shift

v14: captured by the_uninitiated (4/4). v15: captured by the_unexamined_algorithm (3/4) + the_uninitiated (1/4). The Q06-D aptitude signal (0.60) shifted Paper Tiger's vector toward aptitude dimensions — UEA's salience profile (aptitude=2.5, authority=2.5) captures mixed aptitude/authority vectors before the target state. Net: still 0/4, but sink identity has changed. Requires v16 investigation.

### Weak regressions — root cause

Four states regressed from v14 1/3 → v15 0/3: all were weak-profile passes cleared by above-floor criterion. The v15 authority drain shifted random noise composition from authority toward Attitude/Aptitude/Alliance dimensions, raising baseline floors for those states by +0.014 to +0.025. States at the floor margin in v14 lost clearance.

Affected floors (non-Authority 1.08× multiplier applied):
- invisible_burnout: 0.8879 × 1.08 = 0.9589 → 0.9063 × 1.08 = 0.9788
- the_burned_credibility: same tier — same progression
- the_diversity_ceiling: same
- the_overloaded_manager: 0.8561 × 1.08 = 0.9246 → 0.8814 × 1.08 = 0.9519

---

## Section 4 — What Worked / What Did Not

### What worked

- **Authority drain confirmed directionally correct.** the_uninitiated's noise baseline decreased (−0.0077). The drain reduced authority_liability in random noise, compressing the uninitiated's geometric advantage. This is the first version where the_uninitiated's floor moved downward.
- **402 tests: 0 failures.** All engine sections structurally valid after question library edits.
- **No NaN, no negative similarity scores, no negative field values.**
- **APT-PT-00 sink identity shifted.** Paper Tiger now routes to UEA rather than the_uninitiated — the Q06-D aptitude signal activated. Progress on the signal path, not yet on routing destination.

### What did not work

- **HC routing: unchanged.** 0/47 HC in v13, v14, v15. The question library intervention did not break HC capture. The_uninitiated remains rank-1 for HC profiles across all non-uninitiated states.
- **Weak regression (−4).** Baseline floor inflation from the authority drain pushed 4 marginal states below detection threshold.
- **APT-PT-00: still 0/4.** New sink (UEA) captures Paper Tiger instead of the_uninitiated — different attractor, same failure mode.
- **Gemini 60+ target: not reached.** 15/142 is below v14.

---

## Section 5 — Root Cause Assessment

The authority drain confirmed what v14 suspected: the intervention is working at the noise level. The_uninitiated's baseline is now 0.9582, down from 0.9659 — the signal floor for the dominant sink compressed. But the HC profiles accumulate enough authority_liability through the question layer (particularly Q01, Q02, Q03A, Q04, Q06, Q11, Q13, Q21, Q22, Q23, Q28) to still rank the_uninitiated above all correct targets.

The question library still carries substantial authority_liability accumulation from questions with authority_liability as primary or strong secondary signal. The six-question drain (Q07/Q09/Q16/Q20/Q26/Q29) removed signal from questions that were co-contributors, not from the primary authority-liability sources.

The HC session blocker is: HC profiles accumulate authority_liability from primary Authority questions (Q01, Q02, Q04, Q06, Q11 etc.), and no corresponding non-Authority signal is being accumulated in sufficient magnitude to overtop it at the weighted cosine ranking step.

The v16 Gemini question: given that drain on secondary authority co-signals (Q07/Q09/Q16/Q20/Q26/Q29) did not break HC routing, what is the structural intervention that will generate sufficient non-Authority signal contrast for HC profiles? The drain proved correct in direction. The magnitude is insufficient.

---

## Section 6 — Open Items Carried to v16

| Item | Status |
|---|---|
| HC routing failure — 0/47 across v13/v14/v15 | PRIORITY. Gemini v16 brief required. Question library primary authority signal sources (Q01/Q02/Q04/Q06/Q11/Q13/Q21/Q22/Q23/Q28) not yet addressed. |
| APT-PT-00 new sink: UEA — 0/4 | Queued. UEA's salience (apt=2.5, auth=2.5) captures mixed apt/auth Paper Tiger vectors. Q06-D aptitude signal confirmed active but insufficient. |
| Weak regressions — 4 states lost | Likely self-correcting as library signal adds. Monitor in v16 run. Pete accepted as-is. |
| the_unexamined_algorithm — 0/3 persists (v13 reg.) | Queued. Floor 0.9589 in v15 (was 0.9612 in v14 — slight improvement). |
| culture_drift — 0/3 persists (v14 reg.) | Queued. |
| Q05 the_paper_tiger state_targets flag | Pete retained. Revisit if Q06 fix proves insufficient in v16. |
| recalibrate_floor.py display fix — cosmetic 1.15× label | Queued. |
| VERIFY-Q25 copy review | Queued. |
| Q23-A test profiles SEVER-05 paths | Queued. |
| Negative accumulated values runtime assertion | Queued. |
| Construction and Logistics intake industry expansion | Queued. |
| The Dormant Talent Signal Map correction | Queued. |
