# Ranker test 01: offline alternative-ranker comparison (pre-registration)

Date: from the git commit timestamp of this file, per the standing date rule.

## Disclosure, recorded before any ranker result exists

- Benchmark 01 scoring HAD ALREADY RUN before this file was committed (commit `f86a781`, 2026-10-01 12:42:22 -0400). The R0 numbers for the 12 benchmark paths were therefore seen before these definitions were frozen: 1 top-3 hit in 12 runs under R0. Experiment 01 under R0 was also known (rank 49, not qualified).
- No R1, R2 or R3 result has been computed on any data, and no R2 or R3 code exists at the time of this commit. The definitions below were written from the engine source and the specification only.
- The RT1 hypothesis is therefore not blind. RT2, RT3 and RT4 are blind to R2 and R3 outcomes.

## Specification (verbatim from the task, not edited)

--- SPECIFICATION ---
Data: the 12 Benchmark 01 answer paths, plus Experiment 01. These are replayed offline through the local engine. Replays must reproduce the live R0 ranking, or that path is excluded and reported.
Rankers:
R0: current production. Weighted cosine on the displaced 8-field vector, 0.05 margin gate.
R1: R0's ordering, with the margin gate at 0.02. Breadth only; top-3 identical to R0.
R2: question-local evidence. For each answered question (core and follow-up), for each state in that question's state_targets, add the chosen option's contribution on that state's primary liability field. Divide each state's total by the number of its wired questions that were answered. Rank by the result. States with no wired question answered score 0.
R3: question-local cosine. Weighted cosine computed per state on a vector accumulated only from answers to that state's wired questions (same displacement scaling per answered count, same salience weights). States with no wired question answered score 0.
The definitions are frozen at commit. No tuning after any result is seen. If a definition cannot be implemented as written, document the minimum change in this doc before computing.
Measures per ranker: top-3 hit, top-5 hit and the target's rank per path (Experiment 01 target: the_unformed_leader). Also the qualifying count (R0, R1), the margin from rank 1 to rank 2, and the rank-1 tie rate.
Hypotheses:
RT1: R0 top-3 hits are 3 or fewer of 13.
RT2: R2 or R3 achieves at least 3 more top-3 hits than R0.
RT3: under R2 and R3, the rank-1 tie rate is lower than under R0.
RT4 (control): R2 and R3 achieve 10 or more of 13 calibration-style hits on 13 calibration profiles drawn by script (one per target state, seeded). This checks the new rankers don't break the cases R0 handles.
--- END ---

## Implementation definitions (frozen at this commit)

Common to all rankers, so that the comparison is on one footing:

- **Replay.** Each path is the logged sequence of (question_id, option_ids) from the saved run file. Experiment 01 is `C:\Users\rizzo\Downloads\prv3-experiment-01-run.json`. The 12 benchmark paths are `C:\Users\rizzo\Downloads\benchmark-01\<persona>-<framing>.json`. Intake is each run's `intake_wire`. Per-answer contributions come from the production function `engine.accumulation.accumulate_answer` (signal reliability coefficient and axis modifiers included), called through `engine.main.accumulate_answers` for R0 and through a scratch `AccumulationSession` per option for R2 and R3. R0 replay must match the live `all_qualified_states` (same state order and scores within 5e-7), otherwise the path is excluded and reported.
- **Targets.** Benchmark paths use the target in `prompts/benchmark-01-preregistration.md`. Experiment 01 uses the_unformed_leader.
- **Rank and ties.** Rank is the position after sorting by score descending with a stable sort over `STATE_PROFILES` insertion order, as `rank_states` does. Because R2 and R3 create many exact ties (including at 0), every ranker also reports a tie-inclusive rank, defined as 1 + the number of states with a strictly higher score at 6 dp. Top-3 and top-5 hits are scored on the stable-sort rank (the primary measure). The tie-inclusive rank is reported alongside and does not change any hypothesis verdict.
- **Rank-1 tie.** Yes when the top two scores are equal at 6 dp. The tie rate is the share of valid paths with a rank-1 tie.
- **Margin.** Score of rank 1 minus score of rank 2. Not comparable across rankers in absolute terms (R2 is on a different scale than a cosine), so it is reported per ranker and never compared across rankers.
- **Qualifying count (R0, R1 only).** Number of states with score >= rank-1 score minus the margin gate (0.05 for R0, 0.02 for R1), with the absolute floor of -0.4 also applied, as `engine.output.check_signal_gate` does.
- **Wired question.** A question whose `state_targets` (from `QUESTION_LIBRARY`) contains the state. A question counts once toward a state's wired-answered count however many options were selected (Q06 multi-select counts once). Only questions actually answered on the path count.
- **Primary liability field.** `STATE_PROFILES[state].primary_dimension` lowercased plus `_liability` (for example Authority gives `authority_liability`). The same mapping `tools/calibration_runner.py` uses (`_DIM_TO_LIABILITY_FIELD`).

**R2.** For each answered question q on the path and each state s in `q.state_targets`: add to `total[s]` the sum, over the options selected for q, of that option's post-pipeline contribution on s's primary liability field. Let `n[s]` = the number of q on the path with s in `q.state_targets`. R2 score for s = `total[s] / n[s]` when `n[s] > 0`, else 0.0. Rank by score.

**R3.** For each state s with `n[s] > 0` (defined as in R2): build `v_s` by accumulating all 8 fields of every selected option's post-pipeline contribution, over only those questions q with s in `q.state_targets`. Let `N_s = n[s]` (number of wired questions answered, not the number of options). The displaced vector is `A_d = v_s - mu`, where `mu[f] = MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS[f] * (N_s / 42)` (the `rank_states` formula with N replaced by `N_s`). The score is the weighted cosine of `A_d` against s's own `dimensional_vector`, using s's own `SALIENCE_PROFILES[s]` weights (the `rank_states` formula). A score of 0.0 is assigned when `n[s] == 0`, when `||A_d|| < 1e-5`, or when the denominator is <= 1e-5 (the `rank_states` guards).

**Interpretation choices where the specification was ambiguous, fixed here and not revisited:**
1. "same displacement scaling per answered count" in R3 is read as `N_s`, the count of answers applied to that state's local vector, which is how `rank_states` defines N for its own vector. The alternative reading (total path answers) is NOT used.
2. "chosen option's contribution" in R2 is the post-pipeline contribution (after role coefficient and axis modifiers), the same value R0 accumulates, not the raw option weight.
3. No change to the specification was needed to implement R0, R1, R2 or R3. No minimum-change amendment is recorded.

**RT4 control, exact procedure.**
- Targets: `random.Random(20261001).sample(sorted(STATE_PROFILES), 13)`.
- For each target t, build a `high_confidence` profile with the existing harness function `tools.calibration_runner.generate_answers` on a `TestCase` with `test_id = "RT4-" + t` (so no severity follow-ons are spliced), `profile_type = "high_confidence"`, `target_state = t`, and the intake equal to the Experiment 01 wire intake. The answers are the harness's own (best option on the target's primary liability field where the target is wired, a neutral option elsewhere).
- Replay each profile through the same accumulate and ranking code as the other paths. The R0 numbers use the same replay.
- A "calibration-style hit" is the target at stable-sort rank 3 or better under the ranker. This is the existing calibration top-3 notion, not the 0.35 cluster window.
- Disclosed property: the harness picks answers by exactly the quantity R2 sums (the option with the highest contribution on the target's primary liability field), so a high R2 RT4 result is close to guaranteed and does not by itself validate R2. It still detects a broken implementation.
- RT4 passes for a ranker when it scores 10 or more of 13 under the rule above. R0's RT4 count is reported for reference and is not a hypothesis.

**Hypothesis arithmetic, fixed.**
- Hits are counted over the valid paths. If any path is excluded, the denominator in RT1 ("of 13") is the valid count and the threshold of 3 is unchanged.
- RT1 holds when R0 top-3 hits <= 3. RT2 holds when (max of R2 and R3 top-3 hits) - (R0 top-3 hits) >= 3, counting R2 and R3 each against R0 and reporting both. RT3 holds when the rank-1 tie rate under R2 is lower than under R0 AND the tie rate under R3 is lower than under R0 (both required, each reported). RT4 holds when both R2 and R3 reach 10 or more of 13. Each is scored HOLDS or FAILS, with PARTIAL only where one of two rankers meets a two-ranker condition.
- The script is to be committed under `tools/ranker_test_01.py`. Its output appends a RESULTS section to this file. The text above that section is not edited.

## RESULTS

Produced by `tools/ranker_test_01.py` (committed with this section) to the definitions frozen at `612f125`. The text above this section is unchanged. Every figure is generated by the script from the saved run files (`prv3-experiment-01-run.json`, `prv3-experiment-01-result.json`, `benchmark-01/<persona>-<framing>.json`) and live calls into the production engine functions.

### Replay check (R0 against the live ranking)

| Path | Answers | Live qualified states | State order identical | Max abs score diff | Valid |
|---|---:|---:|:-:|---:|:-:|
| EXP01 | 54 | 38 | Y | 0.000000418 | Y |
| P1-cautious | 54 | 38 | Y | 0.000000418 | Y |
| P1-strong | 57 | 37 | Y | 0.000000401 | Y |
| P2-cautious | 51 | 7 | Y | 0.000000383 | Y |
| P2-strong | 56 | 24 | Y | 0.000000465 | Y |
| P3-cautious | 52 | 5 | Y | 0.000000088 | Y |
| P3-strong | 54 | 7 | Y | 0.000000404 | Y |
| P4-cautious | 53 | 14 | Y | 0.000000471 | Y |
| P4-strong | 54 | 14 | Y | 0.000000463 | Y |
| P5-cautious | 51 | 5 | Y | 0.000000438 | Y |
| P5-strong | 52 | 17 | Y | 0.000000464 | Y |
| P6-cautious | 52 | 7 | Y | 0.000000460 | Y |
| P6-strong | 55 | 10 | Y | 0.000000475 | Y |

Valid paths: 13 of 13. Exclusions: none.

### (a) Per path: target rank, hits, rank-1 ties, qualifying counts

Rank is the stable-sort position (primary, used for hits). Tie-incl is 1 + the number of states with a strictly higher score at 6 dp.

| Path | Target | R0 rank | R0 tie-incl | R2 rank | R2 tie-incl | R3 rank | R3 tie-incl | Top-3 R0/R2/R3 | Top-5 R0/R2/R3 | Rank-1 tie R0/R2/R3 | R0 qualifying | R1 qualifying |
|---|---|---:|---:|---:|---:|---:|---:|:-:|:-:|:-:|---:|---:|
| EXP01 | the_unformed_leader | 49 | 49 | 33 | 33 | 26 | 26 | N/N/N | N/N/N | N/N/N | 38 | 16 |
| P1-cautious | the_unformed_leader | 49 | 49 | 33 | 33 | 26 | 26 | N/N/N | N/N/N | N/N/N | 38 | 16 |
| P1-strong | the_unformed_leader | 48 | 48 | 35 | 35 | 22 | 22 | N/N/N | N/N/N | N/N/N | 37 | 17 |
| P2-cautious | the_untouchable | 56 | 56 | 14 | 14 | 4 | 4 | N/N/N | N/N/Y | N/Y/N | 7 | 4 |
| P2-strong | the_untouchable | 40 | 40 | 9 | 9 | 5 | 5 | N/N/N | N/N/Y | N/N/N | 24 | 9 |
| P3-cautious | the_overloaded_manager | 4 | 4 | 4 | 4 | 8 | 8 | N/N/N | Y/Y/N | N/N/N | 5 | 3 |
| P3-strong | the_overloaded_manager | 5 | 5 | 5 | 5 | 16 | 16 | N/N/N | Y/Y/N | N/Y/N | 7 | 4 |
| P4-cautious | decision_paralysis | 5 | 3 | 4 | 4 | 8 | 8 | N/N/N | Y/Y/N | N/N/N | 14 | 2 |
| P4-strong | decision_paralysis | 5 | 3 | 2 | 2 | 2 | 2 | N/Y/Y | Y/Y/Y | N/N/N | 14 | 13 |
| P5-cautious | pay_exposure | 30 | 23 | 57 | 56 | 57 | 57 | N/N/N | N/N/N | N/N/N | 5 | 3 |
| P5-strong | pay_exposure | 14 | 7 | 57 | 56 | 57 | 57 | N/N/N | N/N/N | N/N/N | 17 | 3 |
| P6-cautious | the_culture_that_wasnt | 15 | 14 | 2 | 1 | 11 | 10 | N/Y/N | N/Y/N | N/Y/N | 7 | 4 |
| P6-strong | the_culture_that_wasnt | 2 | 1 | 4 | 3 | 10 | 9 | Y/N/N | Y/Y/N | Y/Y/N | 10 | 6 |

Target score and rank 1 to rank 2 margin per ranker (margins are not comparable across rankers):

| Path | Target score R0 / R2 / R3 | Margin R0 / R2 / R3 |
|---|---|---|
| EXP01 | 0.894330 / 0.225000 / 0.839230 | 0.000125 / 0.008750 / 0.005915 |
| P1-cautious | 0.894330 / 0.225000 / 0.839230 | 0.000125 / 0.008750 / 0.005915 |
| P1-strong | 0.903498 / 0.225000 / 0.871074 | 0.000322 / 0.114583 / 0.001376 |
| P2-cautious | 0.559004 / 0.250000 / 0.949626 | 0.004741 / 0.000000 / 0.007832 |
| P2-strong | 0.824801 / 0.425000 / 0.985224 | 0.002717 / 0.125000 / 0.002776 |
| P3-cautious | 0.845632 / 0.291667 / 0.886299 | 0.002839 / 0.060000 / 0.025770 |
| P3-strong | 0.874887 / 0.387500 / 0.795329 | 0.008998 / 0.000000 / 0.025770 |
| P4-cautious | 0.798249 / 0.371250 / 0.894378 | 0.018643 / 0.235000 / 0.006397 |
| P4-strong | 0.919368 / 0.476667 / 0.976355 | 0.014019 / 0.183333 / 0.021628 |
| P5-cautious | 0.523583 / -0.055000 / -0.971631 | 0.011188 / 0.060000 / 0.088937 |
| P5-strong | 0.709390 / -0.055000 / -0.971631 | 0.015565 / 0.060000 / 0.032613 |
| P6-cautious | 0.498041 / 0.500000 / 0.769246 | 0.009084 / 0.000000 / 0.008310 |
| P6-strong | 0.798260 / 0.450000 / 0.822238 | 0.000000 / 0.000000 / 0.042419 |

### (b) Top 5 states under R2 and under R3, with scores

**EXP01** (target the_unformed_leader, N answers 54)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | the_tolerated_violation | 0.508750 | 4 | the_tolerated_violation | 0.997637 | 4 |
| 2 | wellbeing_theater | 0.500000 | 1 | disparate_impact_architecture | 0.991722 | 3 |
| 3 | human_displacement_anxiety | 0.500000 | 1 | invisible_burnout | 0.981787 | 2 |
| 4 | heard_and_ignored | 0.467500 | 2 | heard_and_ignored | 0.969337 | 2 |
| 5 | invisible_burnout | 0.450000 | 2 | the_fracture | 0.957483 | 3 |

**P1-cautious** (target the_unformed_leader, N answers 54)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | the_tolerated_violation | 0.508750 | 4 | the_tolerated_violation | 0.997637 | 4 |
| 2 | wellbeing_theater | 0.500000 | 1 | disparate_impact_architecture | 0.991722 | 3 |
| 3 | human_displacement_anxiety | 0.500000 | 1 | invisible_burnout | 0.981787 | 2 |
| 4 | heard_and_ignored | 0.467500 | 2 | heard_and_ignored | 0.969337 | 2 |
| 5 | invisible_burnout | 0.450000 | 2 | the_fracture | 0.957483 | 3 |

**P1-strong** (target the_unformed_leader, N answers 57)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | the_tolerated_violation | 0.646250 | 4 | the_untouchable | 0.996914 | 3 |
| 2 | heard_and_ignored | 0.531667 | 3 | the_unreported_hazard | 0.995538 | 2 |
| 3 | wellbeing_theater | 0.500000 | 1 | the_unlocked_door | 0.995538 | 2 |
| 4 | human_displacement_anxiety | 0.500000 | 1 | the_tolerated_violation | 0.995453 | 4 |
| 5 | invisible_burnout | 0.450000 | 2 | disparate_impact_architecture | 0.991722 | 3 |

**P2-cautious** (target the_untouchable, N answers 51)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | the_fracture | 0.513333 | 3 | invisible_burnout | 0.981787 | 2 |
| 2 | silosolation | 0.513333 | 3 | the_fracture | 0.973955 | 3 |
| 3 | human_displacement_anxiety | 0.500000 | 1 | the_tolerated_violation | 0.971782 | 3 |
| 4 | the_tolerated_violation | 0.458333 | 3 | the_untouchable | 0.949626 | 2 |
| 5 | invisible_burnout | 0.450000 | 2 | built_to_fail | 0.944523 | 6 |

**P2-strong** (target the_untouchable, N answers 56)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | the_wrong_reward | 0.675000 | 2 | hr_capture | 0.995403 | 3 |
| 2 | the_tolerated_violation | 0.550000 | 3 | cultural_overtime | 0.992627 | 2 |
| 3 | the_basement_standard | 0.533333 | 3 | motivational_architecture_failure | 0.992606 | 3 |
| 4 | the_fracture | 0.513333 | 3 | the_inside_track | 0.986003 | 4 |
| 5 | silosolation | 0.513333 | 3 | the_untouchable | 0.985224 | 4 |

**P3-cautious** (target the_overloaded_manager, N answers 52)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | human_displacement_anxiety | 0.600000 | 1 | invisible_burnout | 0.989878 | 2 |
| 2 | invisible_burnout | 0.540000 | 2 | the_untouchable | 0.964108 | 2 |
| 3 | the_untouchable | 0.510000 | 2 | the_dormant_talent | 0.953513 | 5 |
| 4 | the_overloaded_manager | 0.291667 | 6 | built_to_fail | 0.951738 | 6 |
| 5 | invisible_influence_architecture | 0.275000 | 1 | the_unformed_leader | 0.941920 | 6 |

**P3-strong** (target the_overloaded_manager, N answers 54)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | wellbeing_theater | 0.600000 | 1 | invisible_burnout | 0.989878 | 2 |
| 2 | human_displacement_anxiety | 0.600000 | 1 | the_untouchable | 0.964108 | 2 |
| 3 | invisible_burnout | 0.540000 | 2 | the_tolerated_violation | 0.957266 | 3 |
| 4 | the_untouchable | 0.510000 | 2 | the_fracture | 0.956222 | 3 |
| 5 | the_overloaded_manager | 0.387500 | 4 | built_to_fail | 0.951738 | 6 |

**P4-cautious** (target decision_paralysis, N answers 53)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | sequential_decision_blindness | 0.660000 | 1 | sequential_decision_blindness | 0.965677 | 1 |
| 2 | groundhog_day | 0.425000 | 2 | the_founders_grip | 0.959280 | 3 |
| 3 | the_founders_grip | 0.403333 | 3 | the_fracture | 0.955692 | 3 |
| 4 | decision_paralysis | 0.371250 | 4 | the_lost_map | 0.947535 | 4 |
| 5 | the_lost_map | 0.371250 | 4 | the_broken_compass | 0.943288 | 5 |

**P4-strong** (target decision_paralysis, N answers 54)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | sequential_decision_blindness | 0.660000 | 1 | the_founders_grip | 0.997983 | 4 |
| 2 | decision_paralysis | 0.476667 | 6 | decision_paralysis | 0.976355 | 6 |
| 3 | the_tolerated_violation | 0.458333 | 3 | the_tolerated_violation | 0.971782 | 3 |
| 4 | the_founders_grip | 0.440000 | 4 | sequential_decision_blindness | 0.965677 | 1 |
| 5 | the_lost_map | 0.440000 | 4 | the_fracture | 0.955692 | 3 |

**P5-cautious** (target pay_exposure, N answers 51)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | human_displacement_anxiety | 0.600000 | 1 | invisible_burnout | 0.989878 | 2 |
| 2 | invisible_burnout | 0.540000 | 2 | human_displacement_anxiety | 0.900941 | 1 |
| 3 | leadership_continuity_risk | 0.316250 | 4 | leadership_continuity_risk | 0.893215 | 4 |
| 4 | motivational_architecture_failure | 0.300000 | 2 | motivational_architecture_failure | 0.866847 | 2 |
| 5 | the_exposed | 0.275000 | 1 | the_exposed | 0.864485 | 1 |

**P5-strong** (target pay_exposure, N answers 52)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | human_displacement_anxiety | 0.600000 | 1 | invisible_burnout | 0.989878 | 2 |
| 2 | invisible_burnout | 0.540000 | 2 | the_tolerated_violation | 0.957266 | 3 |
| 3 | motivational_architecture_failure | 0.450000 | 2 | motivational_architecture_failure | 0.929110 | 2 |
| 4 | the_tolerated_violation | 0.366667 | 3 | human_displacement_anxiety | 0.900941 | 1 |
| 5 | leadership_continuity_risk | 0.363000 | 5 | the_exposed | 0.864485 | 1 |

**P6-cautious** (target the_culture_that_wasnt, N answers 52)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | identity_erosion | 0.500000 | 1 | the_burned_credibility | 0.874694 | 4 |
| 2 | the_culture_that_wasnt | 0.500000 | 1 | dueling_narratives | 0.866384 | 1 |
| 3 | wellbeing_theater | 0.500000 | 1 | the_diversity_ceiling | 0.865296 | 2 |
| 4 | culture_drift | 0.375000 | 2 | cultural_overtime | 0.865296 | 1 |
| 5 | dueling_narratives | 0.275000 | 1 | leadership_continuity_risk | 0.851789 | 5 |

**P6-strong** (target the_culture_that_wasnt, N answers 55)

| # | R2 state | R2 score | n | R3 state | R3 score | n |
|---:|---|---:|---:|---|---:|---:|
| 1 | the_diversity_ceiling | 0.500000 | 2 | dueling_narratives | 0.992413 | 2 |
| 2 | wellbeing_theater | 0.500000 | 1 | the_inside_track | 0.949994 | 3 |
| 3 | identity_erosion | 0.450000 | 3 | the_tolerated_violation | 0.922514 | 3 |
| 4 | the_culture_that_wasnt | 0.450000 | 3 | the_diversity_ceiling | 0.899290 | 2 |
| 5 | dueling_narratives | 0.412500 | 2 | the_pay_fog | 0.885335 | 3 |

### (c) n[s], wired questions answered, for the target and for each top-3 state under R2

n[s] is the same under R3. The number of questions that wire each state in the whole library is shown as 'wired total'.

| Path | State | Role | n answered | wired total | R2 score | R2 rank |
|---|---|---|---:|---:|---:|---:|
| EXP01 | the_unformed_leader | target | 4 | 7 | 0.225000 | 33 |
| EXP01 | the_tolerated_violation | R2 top-1 | 4 | 4 | 0.508750 | 1 |
| EXP01 | wellbeing_theater | R2 top-2 | 1 | 1 | 0.500000 | 2 |
| EXP01 | human_displacement_anxiety | R2 top-3 | 1 | 1 | 0.500000 | 3 |
| P1-cautious | the_unformed_leader | target | 4 | 7 | 0.225000 | 33 |
| P1-cautious | the_tolerated_violation | R2 top-1 | 4 | 4 | 0.508750 | 1 |
| P1-cautious | wellbeing_theater | R2 top-2 | 1 | 1 | 0.500000 | 2 |
| P1-cautious | human_displacement_anxiety | R2 top-3 | 1 | 1 | 0.500000 | 3 |
| P1-strong | the_unformed_leader | target | 4 | 7 | 0.225000 | 35 |
| P1-strong | the_tolerated_violation | R2 top-1 | 4 | 4 | 0.646250 | 1 |
| P1-strong | heard_and_ignored | R2 top-2 | 3 | 3 | 0.531667 | 2 |
| P1-strong | wellbeing_theater | R2 top-3 | 1 | 1 | 0.500000 | 3 |
| P2-cautious | the_untouchable | target | 2 | 4 | 0.250000 | 14 |
| P2-cautious | the_fracture | R2 top-1 | 3 | 7 | 0.513333 | 1 |
| P2-cautious | silosolation | R2 top-2 | 3 | 7 | 0.513333 | 2 |
| P2-cautious | human_displacement_anxiety | R2 top-3 | 1 | 1 | 0.500000 | 3 |
| P2-strong | the_untouchable | target | 4 | 4 | 0.425000 | 9 |
| P2-strong | the_wrong_reward | R2 top-1 | 2 | 2 | 0.675000 | 1 |
| P2-strong | the_tolerated_violation | R2 top-2 | 3 | 4 | 0.550000 | 2 |
| P2-strong | the_basement_standard | R2 top-3 | 3 | 3 | 0.533333 | 3 |
| P3-cautious | the_overloaded_manager | target | 6 | 6 | 0.291667 | 4 |
| P3-cautious | human_displacement_anxiety | R2 top-1 | 1 | 1 | 0.600000 | 1 |
| P3-cautious | invisible_burnout | R2 top-2 | 2 | 3 | 0.540000 | 2 |
| P3-cautious | the_untouchable | R2 top-3 | 2 | 4 | 0.510000 | 3 |
| P3-strong | the_overloaded_manager | target | 4 | 6 | 0.387500 | 5 |
| P3-strong | wellbeing_theater | R2 top-1 | 1 | 1 | 0.600000 | 1 |
| P3-strong | human_displacement_anxiety | R2 top-2 | 1 | 1 | 0.600000 | 2 |
| P3-strong | invisible_burnout | R2 top-3 | 2 | 3 | 0.540000 | 3 |
| P4-cautious | decision_paralysis | target | 4 | 8 | 0.371250 | 4 |
| P4-cautious | sequential_decision_blindness | R2 top-1 | 1 | 2 | 0.660000 | 1 |
| P4-cautious | groundhog_day | R2 top-2 | 2 | 4 | 0.425000 | 2 |
| P4-cautious | the_founders_grip | R2 top-3 | 3 | 6 | 0.403333 | 3 |
| P4-strong | decision_paralysis | target | 6 | 8 | 0.476667 | 2 |
| P4-strong | sequential_decision_blindness | R2 top-1 | 1 | 2 | 0.660000 | 1 |
| P4-strong | decision_paralysis | R2 top-2 | 6 | 8 | 0.476667 | 2 |
| P4-strong | the_tolerated_violation | R2 top-3 | 3 | 4 | 0.458333 | 3 |
| P5-cautious | pay_exposure | target | 1 | 2 | -0.055000 | 57 |
| P5-cautious | human_displacement_anxiety | R2 top-1 | 1 | 1 | 0.600000 | 1 |
| P5-cautious | invisible_burnout | R2 top-2 | 2 | 3 | 0.540000 | 2 |
| P5-cautious | leadership_continuity_risk | R2 top-3 | 4 | 8 | 0.316250 | 3 |
| P5-strong | pay_exposure | target | 1 | 2 | -0.055000 | 57 |
| P5-strong | human_displacement_anxiety | R2 top-1 | 1 | 1 | 0.600000 | 1 |
| P5-strong | invisible_burnout | R2 top-2 | 2 | 3 | 0.540000 | 2 |
| P5-strong | motivational_architecture_failure | R2 top-3 | 2 | 3 | 0.450000 | 3 |
| P6-cautious | the_culture_that_wasnt | target | 1 | 5 | 0.500000 | 2 |
| P6-cautious | identity_erosion | R2 top-1 | 1 | 6 | 0.500000 | 1 |
| P6-cautious | the_culture_that_wasnt | R2 top-2 | 1 | 5 | 0.500000 | 2 |
| P6-cautious | wellbeing_theater | R2 top-3 | 1 | 1 | 0.500000 | 3 |
| P6-strong | the_culture_that_wasnt | target | 3 | 5 | 0.450000 | 4 |
| P6-strong | the_diversity_ceiling | R2 top-1 | 2 | 5 | 0.500000 | 1 |
| P6-strong | wellbeing_theater | R2 top-2 | 1 | 1 | 0.500000 | 2 |
| P6-strong | identity_erosion | R2 top-3 | 3 | 6 | 0.450000 | 3 |

### RT4 control: 13 calibration-style profiles

Targets drawn with `random.Random(20261001).sample(sorted(STATE_PROFILES), 13)`. Answers from `tools.calibration_runner.generate_answers` (high_confidence, no severity follow-ons), intake = the Experiment 01 wire intake (`generate_answers` reads only its significant_events). A hit is target stable-sort rank 3 or better.

| Target | Answers | R0 rank | R2 rank | R3 rank | Hit R0 | Hit R2 | Hit R3 | n[target] |
|---|---:|---:|---:|---:|:-:|:-:|:-:|---:|
| invisible_influence_architecture | 49 | 20 | 3 | 21 | N | Y | N | 1 |
| narrative_lock | 49 | 17 | 3 | 18 | N | Y | N | 3 |
| planning_authority_gap | 49 | 11 | 4 | 18 | N | N | N | 1 |
| the_untouchable | 49 | 21 | 3 | 1 | N | Y | Y | 2 |
| the_exposed | 49 | 18 | 3 | 2 | N | Y | Y | 1 |
| the_inside_track | 49 | 7 | 5 | 7 | N | N | N | 3 |
| the_tolerated_violation | 50 | 6 | 1 | 1 | N | Y | Y | 3 |
| the_paper_tiger | 49 | 23 | 9 | 13 | N | N | N | 6 |
| silosolation | 49 | 6 | 3 | 26 | N | Y | N | 3 |
| distributed_culture_fragmentation | 49 | 3 | 1 | 17 | Y | Y | N | 1 |
| the_lost_map | 49 | 15 | 3 | 9 | N | Y | N | 4 |
| groundhog_day | 49 | 9 | 3 | 6 | N | Y | N | 2 |
| human_displacement_anxiety | 49 | 17 | 4 | 7 | N | N | N | 1 |

RT4 hits: R0 1 of 13 (reference only), R2 9 of 13, R3 3 of 13.

### (d) Hypotheses, scored per the arithmetic in the pre-registration

Valid paths: 13. Top-3 hits: R0 1, R2 2, R3 1. Top-5 hits: R0 5, R2 6, R3 3. Rank-1 ties: R0 1, R2 4, R3 0 (rates 0.077, 0.308, 0.000).

- **RT1** (R0 top-3 hits are 3 or fewer of 13): **HOLDS**. R0 hits = 1. (Not blind: the R0 benchmark numbers were seen before the definitions were frozen, as disclosed.)
- **RT2** (R2 or R3 achieves at least 3 more top-3 hits than R0): **FAILS**. R2 minus R0 = +1, R3 minus R0 = +0.
- **RT3** (rank-1 tie rate lower under R2 and R3 than under R0): **PARTIAL**. Rates R0 0.077, R2 0.308, R3 0.000. R2 lower: N. R3 lower: Y.
- **RT4** (R2 and R3 each reach 10 or more of 13 on the calibration-style profiles): **FAILS**. R2 9 of 13 (not met), R3 3 of 13 (not met).

Registered caveats stand as written above (R2 and RT4 are near-circular by construction, rank ties are broken by registry order, R0 numbers were seen before freezing).
