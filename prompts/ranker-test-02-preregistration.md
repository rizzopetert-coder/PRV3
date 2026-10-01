# Ranker test 02: coarse-level test under R0 (pre-registration)

Date: from the git commit timestamp of this file, per the standing date rule.

## Disclosure, recorded before any M1, M2 or M3 value exists

- At the time of this commit no M1, M2 or M3 value has been computed for any path or profile, and no script for this test exists.
- Claude Code has seen the lead states and target ranks of the 13 paths (Ranker Test 01 results, commit `dad5b25`). It has not tabulated the primary dimension or resolution family of any state for these paths. Claude.ai's own disclosure is inside the specification below.
- The calibration rank distribution requested in the same task (item 1) and the item coverage audit (item 2) are descriptive and are computed after this commit. They do not compute M1, M2 or M3.

## Specification (verbatim from the task, not edited)

--- SPECIFICATION ---
Question: does R0 get the right AREA even when it gets the wrong state? If coarse identification works, the redesign can be coarse-then-distinguish. If it fails too, the item bank is the binding constraint at every level.
Data: the 13 paths from Ranker Test 01 (Experiment 01 + 12 Benchmark 01), plus all 175 calibration profiles.
Measures under R0:
M1 dimension hit: rank-1 state's primary dimension equals the target's.
M2 family hit: rank-1 state's resolution family shares at least one family with the target's.
M3 dimension top-3 hit: any of the top 3 shares the target's primary dimension.
Disclosure: Claude.ai saw the 13 paths' lead states and target ranks before writing this, but not the states' primary dimensions or families, apart from the_unformed_leader (Aptitude) and the_arbitrary_standard (Authority, per the diagnostic).
Hypotheses (Claude.ai's predictions):
C1: M1 on the 13 paths is 5 to 8 of 13. It is not 10 or more.
C2: M2 on the 13 paths is 7 or more of 13. Families are coarser than dimensions.
C3: on the 175 calibration profiles, M1 is 140 or more. Engine-chosen answers keep the dimension right.
--- END ---

## Implementation definitions (frozen at this commit)

- **R0 ranking.** `engine.accumulation.rank_states(vector, N, SALIENCE_PROFILES)` over all 58 states, stable sort, ties in `STATE_PROFILES` insertion order, as in Ranker Test 01. "Rank-1 state" and "top 3" are the first one and three states in that order, whether or not they qualify under the 0.05 margin gate.
- **Primary dimension of a state.** `STATE_PROFILES[state].primary_dimension` (one of Aptitude, Authority, Alliance, Attitude).
- **Family of a state.** `STATE_PROFILES[state].resolution_family`, a string of one or more families joined by " + " (for example "Intervention + Roadmap"). It is split on " + " into a set of component families. M2 is a hit when the rank-1 state's set and the target's set share at least one component.
- **The 13 paths.** The same 13 replayed paths, targets and replay-validity rule as Ranker Test 01 (`prompts/ranker-test-01-preregistration.md`). A path whose R0 replay does not reproduce the live ranking (state order, scores within 5e-7) is excluded and reported, and the denominator is the valid count.
- **The 175 calibration profiles.** `tools.calibration_runner.ALL_PROFILES`. Each profile is answered exactly as `_run_profile_core` does (`test_case.answers`, or `generate_answers(test_case)` when empty), accumulated with `AccumulationEngine` using `IntakeData(**test_case.intake)`, and ranked with `acc_engine.rank(SALIENCE_PROFILES)`. The target is `test_case.target_state`. Profiles are counted per profile, not per target state, and per-profile-type counts are also reported.
- **Hypothesis arithmetic.** C1 holds when M1 on the valid 13 paths is from 5 to 8 inclusive, and fails otherwise (9 is reported as outside both the stated range and the "10 or more" exclusion). C2 holds when M2 on the valid 13 paths is 7 or more. C3 holds when M1 on the 175 profiles is 140 or more. Each is scored HOLDS or FAILS. M3 is reported with no hypothesis.
- **Results.** The script is committed as `tools/ranker_test_02.py`. Its output is appended as a RESULTS section to this file, and the text above that section is not edited.
