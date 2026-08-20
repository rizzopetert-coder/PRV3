# SCD-WCS / Primary-State Ranking Investigation — Findings

Status: **OPEN, fully scoped, not yet remediated.** Investigation only —
no engine code touched, no vectors or salience weights changed. This
document is the durable record consolidating the original findings
(`prompts/primary-state-target-match-finding.md`,
`prompts/severity-follow-on-gate-investigation-findings.md` lines
178-241) with this session's reproduction pass and full cluster map.

Confirmed distinct from and unaffected by the SeverityResult per-state
redesign (closed prior session) — this investigation concerns
`rank_states()`/SCD-WCS, the primary-state ranking mechanism, not
severity attribution. See Section 13a's "SCD-WCS / primary-state
ranking investigation" row (pre-consolidation) for that confirmation.

---

## Task 1 — Primary-state/target match rate: reproduced, zero drift

Ran all 58 current `high_confidence` profiles through the real
production path (`tools.calibration_runner.run_profile()`). Real
current match rate: **1/58**, byte-identical to the original finding
recorded in `prompts/primary-state-target-match-finding.md`. The sole
match is `APT-BF-01` (`built_to_fail`), scoring 0.98876 at rank 1 — the
same profile family the original finding's own context named as the
historical exception (Session 69: "only `built_to_fail` was found to
reliably achieve rank-1 anywhere in the 57/58-state taxonomy"). All 57
other profiles land their own target between rank 2 and rank 58, target
score consistently behind whatever state actually took rank 1.

No drift. This finding holds exactly as recorded, despite everything
that has changed in the codebase since — taxonomy expansion (47→58
states), multiple recalibration passes, the SeverityResult per-state
redesign, and the no-AI-slop remediation project.

## Task 2 — Exact-tie hypothesis: reproduced, with explained drift

Ran the 6 original sample profiles through current production code and
inspected each one's full ranking for exact score matches:

| Profile | Target | Current tie-group size | vs. original |
|---|---|---|---|
| APT-BF-01 | built_to_fail | 2 (built_to_fail, the_paper_tiger) | unchanged |
| ATT-NL-01 | narrative_lock | 5 | shrank from 6 — `the_suppression_filter` dropped out |
| AUT-HI-01 | heard_and_ignored | 8 | grew from 7 — gained `disparate_impact_architecture` |
| ATT-BS-01 | the_basement_standard | 11 | same underlying cluster as EXP-CO-01 below |
| EXP-CO-01 | cultural_overtime | 11 (same 11 states) | confirmed one cluster, not two separate ones |
| ATT-UT-01 | the_untouchable | 1 (no tie) | unchanged |

**Drift investigated (Task 4), not assumed:**

- **`the_suppression_filter` dropping out of the narrative_lock tie:**
  its `dimensional_vector` was last changed 2026-05-17 (commit
  `253b345`, "Session 17: global tier standardization"), three months
  *before* the original Aug 16 2026 finding was recorded. It has been
  genuinely different from the cluster's vector the entire time since.
  Open discrepancy, not fully resolved: either the original 6-profile
  sample caught a coincidental cosine alignment specific to that one
  session (mathematically possible with different vectors, though
  notable) later disrupted by unrelated recalibration work between
  sessions, or there's imprecision in how that detail was carried
  forward across this project's own session history. Does not affect
  the core finding either way.
- **`disparate_impact_architecture` joining the heard_and_ignored tie:**
  added 2026-07-13 in the 47→57 state taxonomy expansion (commit
  `361f269`), already assigned the cluster's exact template vector
  `(0.1, 0.1, 0.6, 0.1, 0.1, 0.1, 0.1, 0.1)` before the Aug 16 finding.
  Most likely already tied at investigation time and simply fell
  outside whatever rank window the original 6-profile sample reported,
  not a real change since.
- **the_basement_standard/cultural_overtime "merging":** not a merge.
  Direct vector inspection (see cluster map below) confirms these were
  always one 11-state cluster sharing one vector. The original
  investigation sampled two different profiles that each independently
  hit part of the same underlying cluster, without the per-profile
  sampling methodology being able to see they were the same cluster.

## Task 3 — SCD-WCS traced: `engine/accumulation.py:rank_states()`

**What it computes:** weighted cosine similarity between a
centroid-displaced session vector (`accumulated_vector - mu_N`, where
`mu_N` scales `MC_CENTROID_39` by question count) and each state's own
native `dimensional_vector`, across 8 fixed fields (aptitude/
authority/alliance/attitude × liability/asset). No rounding, clamping,
or quantization anywhere in the function — scores are raw floats,
sorted by distance.

**The real mechanism, confirmed by direct data inspection, not
hypothesis:** exact ties happen when two states share both an identical
`dimensional_vector` *and* identical (or equally-absent)
`salience_weights`. Verified concretely:
- `the_untouchable`/`the_inner_circle` share an identical raw vector but
  don't tie, because `the_untouchable` has a custom salience entry and
  `the_inner_circle` has none (defaults to uniform 1.0).
- `built_to_fail`/`the_paper_tiger` share both an identical vector *and*
  identical salience weights, and do tie.

**SCD-WCS itself has no bug.** The math is correct and does exactly
what its own docstring describes. The defect is upstream of the
computation, in how the 58 states were authored.

## Full cluster map — 58 states, 18 unique dimensional_vector values

**51 of 58 states (88%) sit in a shared-vector cluster.** 9 of 11
clusters are fully salience-uniform (guaranteed exact tie across every
member); 2 have internal salience differentiation that breaks part or
all of the tie.

| Rank | Vector | States | Size | Salience pattern | Full exact-tie? | Sampled in the original 6-profile investigation? |
|---|---|---|---|---|---|---|
| 1 | (.15,.15,.15,.15,.15,.15,.45,.15) | the_diversity_ceiling, the_burned_credibility, invisible_burnout, the_basement_standard, the_inside_track, groundhog_day, the_wrong_reward, the_broken_compass, human_displacement_anxiety, motivational_architecture_failure, cultural_overtime | 11 | Uniform (identical custom) | Yes | Yes |
| 2 | (.15,.15,.45,.15,.15,.15,.15,.15) | the_uninitiated, leadership_continuity_risk, decision_paralysis, the_policy_lag, dueling_narratives, transition_paralysis, the_lost_map, pay_exposure, the_pay_fog, compression_crisis | 10 | Uniform (identical custom) | Yes | No — newly surfaced |
| 3 | (.1,.1,.6,.1,.1,.1,.1,.1) | the_founders_grip, the_exposed, hr_capture, heard_and_ignored, the_tolerated_violation, the_unsolved_problem, sequential_decision_blindness, disparate_impact_architecture | 8 | Uniform (identical custom) | Yes | Yes |
| 4 | (.15,.15,.15,.15,.25,.15,.35,.15) | what_nobody_says, identity_erosion, the_culture_that_wasnt, narrative_lock, the_unreported_hazard, the_unlocked_door | 6 | **Differentiated** — 5 states share one weight set `(0.4,0.4,0.4,0.4,1.0,1.0,2.5,2.5)`, `what_nobody_says` alone carries `(0.4,0.4,0.4,0.4,2.5,2.5,1.0,1.0)` | No — 5-of-6 tie, `what_nobody_says` excluded | Yes |
| 5 | (.15,.15,.35,.15,.25,.15,.15,.15) | paper_shield, invisible_influence_architecture, planning_authority_gap | 3 | Uniform (identical custom) | Yes | No — newly surfaced |
| 6 | (.15,.15,.15,.15,.45,.15,.15,.15) | the_second_close, silosolation, the_arbitrary_standard | 3 | Uniform (identical custom) | Yes | No — newly surfaced |
| 7 | (.35,.15,.15,.15,.15,.15,.25,.15) | the_unformed_leader, the_dormant_talent | 2 | Uniform (identical custom) | Yes | No — newly surfaced |
| 8 | (.6,.1,.1,.1,.1,.1,.1,.1) | built_to_fail, the_paper_tiger | 2 | Uniform (identical custom) | Yes | Yes |
| 9 | (.1,.1,.1,.1,.6,.1,.1,.1) | the_fracture, decision_blindness | 2 | Uniform (identical custom) | Yes | No — newly surfaced |
| 10 | (.1,.1,.1,.1,.1,.1,.6,.1) | the_untouchable, the_inner_circle | 2 | **Differentiated** — `the_untouchable` has a custom weight set, `the_inner_circle` has none | No | Yes (confirmed as the non-tie case) |
| 11 | (.15,.15,.25,.15,.15,.15,.35,.15) | culture_drift, wellbeing_theater | 2 | Uniform (identical custom) | Yes | No — newly surfaced |

**6 clusters (22 states) were newly surfaced by this full map** —
ranks 2, 5, 6, 7, 9, 11 above — none appeared in the original 6-profile
sample, which only happened to touch 5 of the 11 clusters.

## The 7 states with genuinely unique vectors

| State | Vector |
|---|---|
| `the_overloaded_manager` | (.35,.15,.25,.15,.15,.15,.15,.15) |
| `the_undefined_role` | (.35,.15,.35,.15,.1,.15,.1,.15) |
| `invisible_performance_management` | (.45,.15,.25,.15,.15,.15,.1,.15) |
| `the_unexamined_algorithm` | (.35,.1,.5,.1,.1,.1,.1,.1) |
| `the_suppression_filter` | (.15,.15,.25,.15,.35,.15,.15,.15) |
| `distributed_culture_fragmentation` | (.15,.15,.15,.15,.45,.15,.25,.15) |
| `leadership_deafness` | (.1,.1,.1,.1,.1,.1,.5,.1) |

These serve as the taxonomy's own reference point for what individually
differentiated authoring looks like — presumably calibrated one at a
time rather than assigned from a shared template. Several of them
(`invisible_performance_management`, `the_unexamined_algorithm`,
`leadership_deafness`) repeatedly appear as the *actual* rank-1 winner
across the 58-profile mismatch list from Task 1 — consistent with the
confirmed mechanism: cosine similarity structurally favors
individually-differentiated states over template-shared ones,
independent of whether the differentiated state is the
respondent's actual correct match.

## What this means, practically

This is not primarily a tie-breaking problem. It's that most states
(51 of 58, 88%) were never given the individual dimensional signature
needed for accurate ranking at all — they were authored from one of 18
shared templates. The primary-state/target match rate (1/58) is the
direct, expected consequence: a taxonomy where most states are
dimensionally indistinguishable from several others cannot reliably
rank the correct one at position 1, regardless of how good the
similarity math is.

**Scale for eventual remediation:** two-layer authoring project, not a
quick fix.
- **Salience-weight differentiation** is the cheaper, more mechanical
  layer — could resolve several smaller clusters (e.g. rank 7, 9, 11
  above, each 2-state) without touching any dimensional_vector at all,
  the same kind of fix that already differentiates `the_untouchable`
  from `the_inner_circle`.
- **Full dimensional-vector re-authoring**, for up to 51 states, is
  real clinical/taxonomic judgment — comparable in nature (though
  likely larger in scope) to the still-undated
  `STATE_CAUSATION_OVERRIDES` item (13b item 8). Not something to rush
  or delegate to an automated proposal.

No remediation approach is being recommended here. Pete's call on
sequencing — salience-first, full vector re-authoring, or staged by
cluster size — whenever this gets picked up.

## Cross-references

- `prompts/primary-state-target-match-finding.md` — original 1/58
  finding, Category E Direction 3 pre-scoping.
- `prompts/severity-follow-on-gate-investigation-findings.md`, lines
  178-241 — original 6-profile exact-tie sample.
- `engine/accumulation.py`'s `rank_states()` — the traced mechanism.
- `engine/data/states.py` — `dimensional_vector` authoring, per-state.
- `engine/data/salience.py` — `SALIENCE_PROFILES`, per-state weighting.
- Section 13a Decision Register — consolidated investigation row.
