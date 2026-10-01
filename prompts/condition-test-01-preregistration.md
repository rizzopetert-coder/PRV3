# Condition test 01: how many conditions can the engine separate (pre-registration)

Date: from the git commit timestamp of this file, per the standing date rule.

## Disclosure, recorded before any condition-level value exists

- No condition score, hit, margin or lead count has been computed for any path or profile at the time of this commit, and no script for this test exists.
- Claude Code has seen the state-level R0, R2 and R3 results for the 12 respondent paths and the 175 profiles (Ranker Tests 01 and 02), including each path's target state. It has not tabulated which signature any target belongs to. While reading `web/data/taxonomy.ts` to write these definitions it saw the type definitions and the first screen of `states[]` entries (the first dozen or so `signatureId` values, which include the_unformed_leader in stunted_growth). It ran no membership check and no count yet.
- The membership check that the task requires is run after this commit, and its outcome is appended to this file in a separate append-only commit before any scoring.
- The second specification block below (the data-derived grouping, "Part C") is registered here verbatim because its own text asks to be added to this file before any computation. It is NOT computed in this task. Its implementation definitions are NOT frozen here and will be committed separately, before any Part C computation, in this file or in a `01b` file.

## Specification (verbatim from the task, not edited)

--- SPECIFICATION ---

CONDITION TEST 01, PART C: HOW MANY CONDITIONS CAN THE ENGINE SEPARATE? (exploratory, pre-registered)

Add to prompts/condition-test-01-preregistration.md before any computation. If that file is already committed, write prompts/condition-test-01b-preregistration.md instead. Commit it alone and push.

--- SPECIFICATION ---
Question: the 5 signatures were designed for the self-select browsing experience, not for what the engine can separate. Treat them as the baseline. This part derives the count from the data.
Method:
1. Confusability matrix, built from the 175 calibration profiles only: for each pair of states (a, b), the share of profiles targeting a where b ranks above a under R0, plus the reverse. Symmetrise.
2. Hard constraint: the 6 identical-vector groups (37 states) are never split. Each group enters as one unit.
3. Agglomerative clustering on confusability (average linkage) for k = 3 to 10, with each condition's membership listed per k. No tuning after results are seen.
4. Evaluate each k on the 12 respondent paths, held out from the clustering. Use the best scorer from Part B, applied to that k's groups. Report top-1 and top-2 hits and the chance baseline per k.
5. For each k, report how often each condition leads on the paths and the profiles, and flag any condition that leads more than 50% of profiles (a sink).
Outputs: an accuracy-against-k table, the membership per k, and the sink flags. The 5-signature result sits beside them as a reference row.
Hypotheses (Claude.ai's predictions):
K1: top-1 accuracy on the paths falls as k rises, not necessarily monotonically.
K2: the largest k with top-1 of 9 or more of 12 on the paths falls between 4 and 7.
K3: at the k nearest 5, the data-derived grouping beats the 5 signatures on top-1 on the paths.
Disclosure: the groupings derive from engine confusions on engine-generated answers, so they inherit the engine's biases (for example, the built_to_fail sink). They are candidates for Pete's clinical review, not a taxonomy. Twelve paths is a small held-out set, so the per-k accuracies carry wide uncertainty.
--- END ---

Question: can the engine tell broader conditions apart? The candidate conditions are the 5 existing signatures in web/data/taxonomy.ts. Overlap is allowed: a state belongs to its primary signature and to every secondarySignatureId.
Data: 12 distinct respondent paths (Experiment 01 and P1-cautious share answers, so count them once), plus the 175 calibration profiles. A path's target condition set is every signature the target state belongs to.
Hit rules:
- top-1 hit: the rank-1 condition is in the target's set.
- top-2 hit: either of the top 2 conditions is in it.
Condition scorers (computed from the same replays as Ranker Tests 01/02):
CR0max: condition score = max R0 score among its member states.
CR0mean: mean R0 score of its members.
CR2pool: pooled question-local evidence. Over every answered question q, and every member s in q.state_targets: add the chosen option(s)' post-pipeline contribution on s's primary liability field. Divide by the number of (q, s) pairs counted. 0 if none.
CR3pool: a vector accumulated from answers to every question wired to any member, displaced as in R3 with N = the number of such questions answered. Weighted cosine against the mean of the members' dimensional_vectors, with the members' mean salience weights. 0 on the R3 guards.
Report per scorer:
- top-1 and top-2 hits on the 12 paths and the 175 profiles (the latter per profile type and overall)
- the chance baseline: the expected top-1 hits if rank 1 were uniform over the 5 conditions, computed from each target's set size
- the margin between conditions 1 and 2 on each path
- how often each condition leads, on the paths and on the profiles
Hypotheses (Claude.ai's predictions):
S1: the best condition scorer's top-1 is at least 8 of 12 on the paths, and beats CR0max.
S2: the best scorer's top-2 is at least 10 of 12 on the paths.
S3: the best scorer's top-1 is at least 120 of 175 on the profiles.
S4: under the best scorer, no single condition leads more than 50% of the 175 profiles.
"Best scorer" is fixed as the one with the most top-1 hits on the 12 paths, ties broken by the profiles.
Disclosure: Claude.ai has seen the 12 paths' target states and the signature sizes (Leadership Bottleneck 9, Culture Erosion 13, Stunted Growth 8, Compounding Risks 20, Information Blindness 9), but not which signature each target belongs to.
--- END ---

## Implementation definitions for the 5-signature test (frozen at this commit)

- **Membership source.** The `State` side of `web/data/taxonomy.ts`: a state belongs to the signature in its `signatureId` and to every id in its `secondarySignatureIds`. The `Signature.stateIds` side is read only for the membership check (run after this commit) and is not used for scoring, whatever that check finds. A state absent from `taxonomy.ts` belongs to no condition: it contributes to no condition's score, and a path or profile whose target is absent is excluded and reported. Taxonomy is read by evaluating the file with Node, not by hand-copying.
- **Conditions and order.** The 5 signatures in the order of the exported `signatures` array. Ties between conditions break by that order (stable sort, score descending). A tie at rank 1 is reported as a tie flag and the stable-order condition is the one counted as rank 1.
- **Paths.** The 12 distinct paths: P1-cautious through P6-strong (12 files in `C:\Users\rizzo\Downloads\benchmark-01\`). Experiment 01 is dropped because its answers equal P1-cautious. Loading, R0 replay and validity (live order and scores within 5e-7) follow `tools/ranker_test_01.py`. A path failing validity is excluded and reported. Targets are the benchmark targets in `prompts/benchmark-01-preregistration.md`.
- **Profiles.** The 175 profiles of `tools.calibration_runner.ALL_PROFILES`, answered and accumulated as in `tools/ranker_test_02.py` (`test_case.answers`, else `generate_answers`, intake `IntakeData(**test_case.intake)`). Target = `test_case.target_state`.
- **Target set.** Every signature the target state belongs to under the membership source above.
- **Hits.** Top-1: the rank-1 condition is in the target set. Top-2: either of the first two conditions is in the target set.
- **R0 scores.** `engine.accumulation.rank_states` over all 58 states with `SALIENCE_PROFILES`. CR0max and CR0mean take the max and the arithmetic mean of the R0 scores of the member states present in the engine registry.
- **Per-option contribution.** The post-pipeline contribution (role coefficient and axis modifiers included), via `engine.accumulation.accumulate_answer`, as in `tools/ranker_test_01.py`.
- **CR2pool.** For each answered question q and each member s with s in `QUESTION_LIBRARY[q].state_targets`: add, over the options selected for q, the post-pipeline contribution on the field `primary_dimension.lower() + "_liability"` of s. The denominator is the number of such (q, s) pairs, each counted once however many options were selected. Score 0.0 when there are no pairs. Members are counted separately: a question wired to two members of the same condition contributes two pairs.
- **CR3pool.** Let Q = the distinct answered questions wired to at least one member. If Q is empty the score is 0.0. Otherwise the vector is the sum, over every selected option of every question in Q, of all 8 post-pipeline contributions. N = |Q|. Displacement `mu[f] = MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS[f] * (N / 42)`. The profile vector is the arithmetic mean of the members' `dimensional_vector` values, the weights the arithmetic mean of the members' `SALIENCE_PROFILES` weights, field by field, over all members present in the registry (wired or not). Score = weighted cosine as in `rank_states`, 0.0 when the displaced norm is below 1e-5 or the denominator is at most 1e-5.
- **Chance baseline.** For each path or profile, |target set| / 5. The baseline is the sum over paths or profiles (expected top-1 hits if rank 1 were uniform over the 5 conditions).
- **Margin.** Condition-1 score minus condition-2 score per path, per scorer. Margins are not compared across scorers.
- **Lead frequency.** For each scorer, how many paths and how many profiles each condition leads (stable order on ties).
- **Best scorer.** The scorer with the most top-1 hits on the 12 valid paths. Ties are broken by top-1 hits on the 175 profiles. If still tied, the order CR0max, CR0mean, CR2pool, CR3pool.
- **Hypothesis arithmetic.** S1 holds when the best scorer's path top-1 is at least 8 AND is strictly greater than CR0max's path top-1 (so S1 fails if the best scorer is CR0max itself). S2 holds when the best scorer's path top-2 is at least 10. S3 holds when the best scorer's profile top-1 is at least 120 of 175. S4 holds when no condition leads more than 87 of the 175 profiles (50 percent is 87.5) under the best scorer. Each is HOLDS or FAILS.
- **Extra output, no hypothesis.** For each of the 12 paths and each scorer: the top 2 conditions with their scores. For the best scorer: the member states of the rank-1 condition with wired evidence on that path (n[s] at least 1 wired question answered, as defined in `prompts/ranker-test-01-preregistration.md`), with n[s] and the state's R2 score. These are the candidate symptoms a report would name.
- **Output.** The script is committed as `tools/condition_test_01.py` and appends a RESULTS section to this file. The text above that section is not edited. A "Membership check" section is appended first, in its own commit, before any scoring.

## Membership check (run after the pre-registration commit, before any scoring)

Produced by `tools/condition_test_01.py --membership`. `taxonomy.ts` is evaluated with Node, the engine registry is `engine.data.states.STATE_PROFILES`. Nothing was fixed.

- `taxonomy.ts` `states[]` entries: 58 (58 distinct ids). Engine registry states: 58.
- In the registry but absent from `taxonomy.ts` states: none.
- In `taxonomy.ts` states but absent from the registry: none.
- Duplicate ids in `states[]`: none.
- States whose `signatureId` is not a signature id: none. Secondary ids that are not a signature id: none.
- State ids listed in `Signature.stateIds` that are absent from `states[]`: none. `states[]` ids that appear in no `Signature.stateIds`: none.

Two-representation comparison, per signature (State side = `signatureId` plus `secondarySignatureIds`, Signature side = `stateIds`):

| Signature | Spec-claimed size | State-side size | Signature-side size | In State side only | In Signature side only |
|---|---:|---:|---:|---|---|
| leadership_bottleneck | 9 | 9 | 9 | - | - |
| culture_erosion | 13 | 14 | 14 | - | - |
| stunted_growth | 8 | 8 | 8 | - | - |
| compounding_risks | 20 | 20 | 20 | - | - |
| information_blindness | 9 | 9 | 9 | - | - |

- States with secondary signatures: 2: leadership_continuity_risk in leadership_bottleneck, stunted_growth; narrative_lock in culture_erosion, information_blindness.
- Total memberships: State side 60, Signature side 60. Signature-size sum claimed in the specification: 59.
- Result: the two representations MATCH and cover all registry states.

## RESULTS

Produced by `tools/condition_test_01.py` (committed with this section) to the definitions frozen at `0bf8efb`. The text above this section is unchanged. Every figure is generated by the script. Part C (data-derived grouping) is not computed.

Conditions (State-side membership restricted to engine registry states): leadership_bottleneck 9; culture_erosion 14; stunted_growth 8; compounding_risks 20; information_blindness 9.
Valid paths: 12 of 12. Exclusions: none. Valid profiles: 175 of 175. Exclusions: none.

### Summary per scorer

| Scorer | Paths top-1 | Paths top-2 | Profiles top-1 | Profiles top-2 | high_confidence top-1/top-2 | extreme_high_confidence top-1/top-2 | moderate top-1/top-2 | weak top-1/top-2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CR0max | 6 of 12 | 9 of 12 | 41 of 175 | 76 of 175 | 13/27 of 58 | 0/0 of 1 | 14/25 of 58 | 14/24 of 58 |
| CR0mean | 5 of 12 | 10 of 12 | 68 of 175 | 117 of 175 | 22/40 of 58 | 1/1 of 1 | 25/39 of 58 | 20/37 of 58 |
| CR2pool | 6 of 12 | 7 of 12 | 80 of 175 | 113 of 175 | 29/39 of 58 | 1/1 of 1 | 26/38 of 58 | 24/35 of 58 |
| CR3pool | 6 of 12 | 6 of 12 | 93 of 175 | 125 of 175 | 33/45 of 58 | 1/1 of 1 | 29/39 of 58 | 30/40 of 58 |
| chance (top-1, uniform over 5) | 2.40 | n/a | 36.2 | n/a | |

### CR0max: per path (top 2 conditions with scores)

| Path | Target | Target's conditions | Rank-1 condition (score) | Rank-2 condition (score) | Margin 1-2 | Tie | Top-1 | Top-2 |
|---|---|---|---|---|---:|:-:|:-:|:-:|
| P1-cautious | the_unformed_leader | stunted_growth | compounding_risks (0.9639) | leadership_bottleneck (0.9638) | 0.0001 | N | N | N |
| P1-strong | the_unformed_leader | stunted_growth | compounding_risks (0.9773) | leadership_bottleneck (0.9770) | 0.0003 | N | N | N |
| P2-cautious | the_untouchable | information_blindness | culture_erosion (0.8700) | information_blindness (0.8653) | 0.0047 | N | N | Y |
| P2-strong | the_untouchable | information_blindness | information_blindness (0.9586) | culture_erosion (0.9559) | 0.0027 | N | Y | Y |
| P3-cautious | the_overloaded_manager | stunted_growth | stunted_growth (0.8798) | compounding_risks (0.8699) | 0.0099 | N | Y | Y |
| P3-strong | the_overloaded_manager | stunted_growth | stunted_growth (0.9057) | information_blindness (0.8948) | 0.0108 | N | Y | Y |
| P4-cautious | decision_paralysis | leadership_bottleneck | leadership_bottleneck (0.8220) | compounding_risks (0.8034) | 0.0186 | N | Y | Y |
| P4-strong | decision_paralysis | leadership_bottleneck | leadership_bottleneck (0.9340) | compounding_risks (0.9200) | 0.0140 | N | Y | Y |
| P5-cautious | pay_exposure | compounding_risks | stunted_growth (0.6661) | compounding_risks (0.6270) | 0.0391 | N | N | Y |
| P5-strong | pay_exposure | compounding_risks | leadership_bottleneck (0.7533) | compounding_risks (0.7362) | 0.0172 | N | N | Y |
| P6-cautious | the_culture_that_wasnt | culture_erosion | information_blindness (0.5836) | stunted_growth (0.5745) | 0.0091 | N | N | N |
| P6-strong | the_culture_that_wasnt | culture_erosion | culture_erosion (0.7983) | compounding_risks (0.7983) | 0.0000 | Y | Y | Y |

### CR0mean: per path (top 2 conditions with scores)

| Path | Target | Target's conditions | Rank-1 condition (score) | Rank-2 condition (score) | Margin 1-2 | Tie | Top-1 | Top-2 |
|---|---|---|---|---|---:|:-:|:-:|:-:|
| P1-cautious | the_unformed_leader | stunted_growth | leadership_bottleneck (0.9322) | information_blindness (0.9267) | 0.0055 | N | N | N |
| P1-strong | the_unformed_leader | stunted_growth | leadership_bottleneck (0.9403) | information_blindness (0.9397) | 0.0006 | N | N | N |
| P2-cautious | the_untouchable | information_blindness | leadership_bottleneck (0.7437) | information_blindness (0.7398) | 0.0038 | N | N | Y |
| P2-strong | the_untouchable | information_blindness | culture_erosion (0.9161) | information_blindness (0.8984) | 0.0176 | N | N | Y |
| P3-cautious | the_overloaded_manager | stunted_growth | stunted_growth (0.7538) | culture_erosion (0.6017) | 0.1520 | N | Y | Y |
| P3-strong | the_overloaded_manager | stunted_growth | stunted_growth (0.8332) | culture_erosion (0.8003) | 0.0330 | N | Y | Y |
| P4-cautious | decision_paralysis | leadership_bottleneck | leadership_bottleneck (0.6890) | compounding_risks (0.6766) | 0.0123 | N | Y | Y |
| P4-strong | decision_paralysis | leadership_bottleneck | compounding_risks (0.8258) | leadership_bottleneck (0.8231) | 0.0027 | N | N | Y |
| P5-cautious | pay_exposure | compounding_risks | stunted_growth (0.5745) | compounding_risks (0.4882) | 0.0863 | N | N | Y |
| P5-strong | pay_exposure | compounding_risks | compounding_risks (0.6345) | stunted_growth (0.6321) | 0.0023 | N | Y | Y |
| P6-cautious | the_culture_that_wasnt | culture_erosion | stunted_growth (0.4960) | culture_erosion (0.4372) | 0.0588 | N | N | Y |
| P6-strong | the_culture_that_wasnt | culture_erosion | culture_erosion (0.7416) | information_blindness (0.6902) | 0.0513 | N | Y | Y |

### CR2pool: per path (top 2 conditions with scores)

| Path | Target | Target's conditions | Rank-1 condition (score) | Rank-2 condition (score) | Margin 1-2 | Tie | Top-1 | Top-2 |
|---|---|---|---|---|---:|:-:|:-:|:-:|
| P1-cautious | the_unformed_leader | stunted_growth | culture_erosion (0.3243) | stunted_growth (0.2709) | 0.0533 | N | N | Y |
| P1-strong | the_unformed_leader | stunted_growth | culture_erosion (0.3243) | information_blindness (0.2948) | 0.0294 | N | N | N |
| P2-cautious | the_untouchable | information_blindness | culture_erosion (0.1903) | leadership_bottleneck (0.1652) | 0.0251 | N | N | N |
| P2-strong | the_untouchable | information_blindness | culture_erosion (0.3271) | leadership_bottleneck (0.2116) | 0.1155 | N | N | N |
| P3-cautious | the_overloaded_manager | stunted_growth | stunted_growth (0.2471) | information_blindness (0.1240) | 0.1230 | N | Y | Y |
| P3-strong | the_overloaded_manager | stunted_growth | stunted_growth (0.2429) | culture_erosion (0.1979) | 0.0449 | N | Y | Y |
| P4-cautious | decision_paralysis | leadership_bottleneck | leadership_bottleneck (0.2590) | information_blindness (0.1735) | 0.0855 | N | Y | Y |
| P4-strong | decision_paralysis | leadership_bottleneck | leadership_bottleneck (0.3015) | information_blindness (0.1840) | 0.1174 | N | Y | Y |
| P5-cautious | pay_exposure | compounding_risks | stunted_growth (0.1514) | leadership_bottleneck (0.1228) | 0.0285 | N | N | N |
| P5-strong | pay_exposure | compounding_risks | stunted_growth (0.1719) | leadership_bottleneck (0.1406) | 0.0313 | N | N | N |
| P6-cautious | the_culture_that_wasnt | culture_erosion | culture_erosion (0.1944) | leadership_bottleneck (0.0954) | 0.0990 | N | Y | Y |
| P6-strong | the_culture_that_wasnt | culture_erosion | culture_erosion (0.2515) | leadership_bottleneck (0.0954) | 0.1561 | N | Y | Y |

### CR3pool: per path (top 2 conditions with scores)

| Path | Target | Target's conditions | Rank-1 condition (score) | Rank-2 condition (score) | Margin 1-2 | Tie | Top-1 | Top-2 |
|---|---|---|---|---|---:|:-:|:-:|:-:|
| P1-cautious | the_unformed_leader | stunted_growth | compounding_risks (0.9480) | leadership_bottleneck (0.9480) | 0.0001 | N | N | N |
| P1-strong | the_unformed_leader | stunted_growth | compounding_risks (0.9769) | information_blindness (0.9736) | 0.0033 | N | N | N |
| P2-cautious | the_untouchable | information_blindness | culture_erosion (0.8720) | stunted_growth (0.8433) | 0.0287 | N | N | N |
| P2-strong | the_untouchable | information_blindness | culture_erosion (0.9614) | compounding_risks (0.9507) | 0.0107 | N | N | N |
| P3-cautious | the_overloaded_manager | stunted_growth | stunted_growth (0.9297) | information_blindness (0.6210) | 0.3087 | N | Y | Y |
| P3-strong | the_overloaded_manager | stunted_growth | stunted_growth (0.9257) | culture_erosion (0.8270) | 0.0987 | N | Y | Y |
| P4-cautious | decision_paralysis | leadership_bottleneck | leadership_bottleneck (0.9434) | information_blindness (0.6928) | 0.2506 | N | Y | Y |
| P4-strong | decision_paralysis | leadership_bottleneck | leadership_bottleneck (0.9885) | stunted_growth (0.7601) | 0.2284 | N | Y | Y |
| P5-cautious | pay_exposure | compounding_risks | stunted_growth (0.8473) | leadership_bottleneck (0.6841) | 0.1632 | N | N | N |
| P5-strong | pay_exposure | compounding_risks | stunted_growth (0.8540) | leadership_bottleneck (0.8147) | 0.0393 | N | N | N |
| P6-cautious | the_culture_that_wasnt | culture_erosion | culture_erosion (0.7847) | information_blindness (0.5763) | 0.2083 | N | Y | Y |
| P6-strong | the_culture_that_wasnt | culture_erosion | culture_erosion (0.9322) | compounding_risks (0.7157) | 0.2165 | N | Y | Y |

### How often each condition leads

| Scorer | Set | leadership_bottleneck | culture_erosion | stunted_growth | compounding_risks | information_blindness | Max share |
|---|---|---:|---:|---:|---:|---:|---:|
| CR0max | paths | 3 | 2 | 3 | 2 | 2 | 0.25 |
| CR0max | profiles | 37 | 7 | 121 | 7 | 3 | 0.69 |
| CR0mean | paths | 4 | 2 | 4 | 2 | 0 | 0.33 |
| CR0mean | profiles | 0 | 12 | 100 | 63 | 0 | 0.57 |
| CR2pool | paths | 2 | 6 | 4 | 0 | 0 | 0.50 |
| CR2pool | profiles | 18 | 52 | 92 | 9 | 4 | 0.53 |
| CR3pool | paths | 2 | 4 | 4 | 2 | 0 | 0.33 |
| CR3pool | profiles | 50 | 25 | 17 | 34 | 49 | 0.29 |

### Best scorer and hypotheses

Best scorer (most path top-1, ties by profile top-1): **CR3pool** (paths top-1 6, profiles top-1 93).

- **S1** (best scorer path top-1 at least 8 and strictly above CR0max): **FAILS**. Best 6 of 12, CR0max 6.
- **S2** (best scorer path top-2 at least 10): **FAILS**. Best 6 of 12.
- **S3** (best scorer profile top-1 at least 120 of 175): **FAILS**. Best 93 of 175.
- **S4** (no condition leads more than 87 of the 175 profiles under the best scorer): **HOLDS**. Largest lead: leadership_bottleneck with 50 of 175 (28.6 percent).

### Candidate symptoms: member states of the rank-1 condition with wired evidence (best scorer CR3pool)

n = wired questions answered on that path. R2 = the Ranker Test 01 question-local score. Sorted by R2 score.

| Path | Rank-1 condition | In target's set | Member states with wired evidence (n, R2) |
|---|---|:-:|---|
| P1-cautious | compounding_risks | N | the_tolerated_violation (4, 0.509); heard_and_ignored (2, 0.468); disparate_impact_architecture (3, 0.403); dueling_narratives (1, 0.275); the_policy_lag (5, 0.253); the_unlocked_door (1, 0.250); the_unreported_hazard (1, 0.250); paper_shield (3, 0.167); the_unexamined_algorithm (2, 0.165); the_unsolved_problem (2, 0.125); the_paper_tiger (6, 0.110); the_pay_fog (3, 0.073); decision_blindness (1, 0.000); invisible_performance_management (2, 0.000); sequential_decision_blindness (1, 0.000); the_arbitrary_standard (4, 0.000); the_exposed (1, 0.000); compression_crisis (1, -0.055); pay_exposure (1, -0.055) |
| P1-strong | compounding_risks | N | the_tolerated_violation (4, 0.646); heard_and_ignored (3, 0.532); disparate_impact_architecture (3, 0.403); the_unlocked_door (2, 0.375); the_unreported_hazard (2, 0.375); dueling_narratives (1, 0.275); the_policy_lag (5, 0.253); paper_shield (3, 0.167); the_unexamined_algorithm (2, 0.165); the_unsolved_problem (2, 0.125); the_paper_tiger (6, 0.110); the_pay_fog (3, 0.073); decision_blindness (1, 0.000); invisible_performance_management (2, 0.000); sequential_decision_blindness (1, 0.000); the_arbitrary_standard (4, 0.000); the_exposed (1, 0.000); compression_crisis (1, -0.055); pay_exposure (1, -0.055) |
| P2-cautious | culture_erosion | N | human_displacement_anxiety (1, 0.500); identity_erosion (3, 0.267); the_culture_that_wasnt (3, 0.267); culture_drift (4, 0.263); cultural_overtime (1, 0.250); the_basement_standard (2, 0.250); the_wrong_reward (2, 0.250); the_inside_track (3, 0.167); motivational_architecture_failure (2, 0.125); the_inner_circle (2, 0.125); narrative_lock (3, 0.083); the_burned_credibility (3, 0.083); distributed_culture_fragmentation (1, 0.000); wellbeing_theater (1, 0.000) |
| P2-strong | culture_erosion | N | the_wrong_reward (2, 0.675); the_basement_standard (3, 0.533); cultural_overtime (2, 0.500); human_displacement_anxiety (1, 0.500); the_inside_track (4, 0.400); culture_drift (4, 0.388); the_inner_circle (2, 0.375); motivational_architecture_failure (3, 0.333); identity_erosion (3, 0.267); the_culture_that_wasnt (3, 0.267); narrative_lock (3, 0.083); the_burned_credibility (3, 0.083); distributed_culture_fragmentation (1, 0.000); wellbeing_theater (1, 0.000) |
| P3-cautious | stunted_growth | Y | invisible_burnout (2, 0.540); the_overloaded_manager (6, 0.292); the_undefined_role (4, 0.263); built_to_fail (6, 0.242); the_unformed_leader (6, 0.225); the_dormant_talent (5, 0.190); leadership_continuity_risk (5, 0.154) |
| P3-strong | stunted_growth | Y | invisible_burnout (2, 0.540); the_overloaded_manager (4, 0.388); the_undefined_role (4, 0.263); built_to_fail (6, 0.242); the_unformed_leader (4, 0.163); leadership_continuity_risk (5, 0.154); the_dormant_talent (3, 0.083) |
| P4-cautious | leadership_bottleneck | Y | the_founders_grip (3, 0.403); decision_paralysis (4, 0.371); invisible_influence_architecture (1, 0.275); planning_authority_gap (1, 0.275); the_fracture (3, 0.275); the_broken_compass (5, 0.220); leadership_continuity_risk (5, 0.154); hr_capture (2, 0.138) |
| P4-strong | leadership_bottleneck | Y | decision_paralysis (6, 0.477); the_founders_grip (4, 0.440); invisible_influence_architecture (1, 0.275); planning_authority_gap (1, 0.275); the_fracture (3, 0.275); the_broken_compass (5, 0.220); leadership_continuity_risk (5, 0.154); hr_capture (2, 0.138) |
| P5-cautious | stunted_growth | N | invisible_burnout (2, 0.540); leadership_continuity_risk (4, 0.316); the_overloaded_manager (6, 0.133); the_undefined_role (4, 0.125); the_unformed_leader (6, 0.092); built_to_fail (6, 0.083); the_dormant_talent (5, 0.060) |
| P5-strong | stunted_growth | N | invisible_burnout (2, 0.540); leadership_continuity_risk (5, 0.363); the_overloaded_manager (6, 0.158); the_undefined_role (4, 0.125); the_unformed_leader (6, 0.117); built_to_fail (6, 0.083); the_dormant_talent (5, 0.060) |
| P6-cautious | culture_erosion | Y | identity_erosion (1, 0.500); the_culture_that_wasnt (1, 0.500); wellbeing_theater (1, 0.500); culture_drift (2, 0.375); cultural_overtime (1, 0.250); narrative_lock (4, 0.188); the_burned_credibility (4, 0.188); the_inside_track (3, 0.167); motivational_architecture_failure (2, 0.125); the_basement_standard (2, 0.125); the_wrong_reward (2, 0.125); distributed_culture_fragmentation (1, 0.000); human_displacement_anxiety (1, 0.000); the_inner_circle (2, 0.000) |
| P6-strong | culture_erosion | Y | wellbeing_theater (1, 0.500); identity_erosion (3, 0.450); the_culture_that_wasnt (3, 0.450); culture_drift (4, 0.400); the_inside_track (3, 0.333); cultural_overtime (1, 0.250); narrative_lock (4, 0.188); the_burned_credibility (4, 0.188); motivational_architecture_failure (2, 0.125); the_basement_standard (2, 0.125); the_wrong_reward (2, 0.125); distributed_culture_fragmentation (1, 0.000); human_displacement_anxiety (1, 0.000); the_inner_circle (2, 0.000) |
