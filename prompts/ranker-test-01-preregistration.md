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
