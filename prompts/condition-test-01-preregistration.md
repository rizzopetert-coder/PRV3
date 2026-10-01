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
