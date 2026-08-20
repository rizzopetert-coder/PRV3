# SCD-WCS / Primary-State Ranking Investigation — Findings

Status: **OPEN, fully scoped, PILOT COMPLETE (1 of 11 clusters).**
First remediation result landed 2026-08-20 (commit 043b8ad) — see
"Pilot result" below. Remaining 10 clusters not attempted; general
remediation sequencing still undecided, Pete's call. This
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
  from `the_inner_circle`. Rank 7 now piloted (see "Pilot result"
  below) — mechanically validated, but narrative-correct
  differentiation was not achievable within calibration-safe bounds
  for that cluster. One data point, not a confirmed pattern for 9/11
  or the remaining clusters.
- **Full dimensional-vector re-authoring**, for up to 51 states, is
  real clinical/taxonomic judgment — comparable in nature (though
  likely larger in scope) to the still-undated
  `STATE_CAUSATION_OVERRIDES` item (13b item 8). Not something to rush
  or delegate to an automated proposal.

No remediation approach is being recommended here. Pete's call on
sequencing — salience-first, full vector re-authoring, or staged by
cluster size — whenever this gets picked up.

## Pilot result — rank-7 cluster (`the_unformed_leader` / `the_dormant_talent`)

First-ever remediation result for this investigation. Commit `043b8ad`,
2026-08-20. Salience-only differentiation — `dimensional_vector`
deliberately untouched, by design, to test whether salience alone can
move ranking outcomes before committing to the larger 51-state
remediation project.

**Two passes.** First (`the_dormant_talent` aptitude 2.5→1.5, attitude
1.0→2.0 — making attitude fully dominant, per the real
`descriptive_prose`) broke the tie but regressed calibration profile
`APT-DT-02` below its moderate-tier prominence threshold — caught by a
full-suite regression, not assumed clean. Second pass searched smaller
deltas against the real calibration pipeline (not hand-derived
extrapolation — the underlying formula is weighted cosine, nonlinear).
Landed on `the_dormant_talent` aptitude=2.0/attitude=1.3
(`the_unformed_leader`'s originally proposed attitude=0.6 unchanged,
its own 3 profiles held 3/3 throughout both passes).

**Mechanically validated:**
- Tie fully broken: 175/175 calibration profiles tied before this
  change → 0/175 tied after, score gap range 0.000633–0.139833.
- Zero cross-contamination: full 58-state × 175-profile comparison
  (10,150 pairs), not spot-checked — every other state's score
  byte-identical before/after in every single profile. Traced to the
  formula itself (`rank_states()`, `engine/accumulation.py:572-588`):
  each state's score depends only on the session vector and that
  state's own profile vector and salience weights, no cross-state term.
- Full regression exactly at the 171/175 baseline — same 4
  pre-existing failures (`identity_erosion`, `invisible_burnout`,
  `leadership_deafness`, `the_untouchable`), nothing new.
- `APT-DT-02` passes with real margin: +0.064 above its threshold,
  not a bare clear.

**Real, load-bearing tension found, not routed around.** Every
candidate tested that preserved attitude as the dominant dimension for
`the_dormant_talent` (matching the actual `descriptive_prose` —
retained capability plus a willingness failure) failed `APT-DT-02`,
whose underlying session vector carries strong aptitude signal. Every
candidate that kept aptitude dominant passed with real margin. The
landed value keeps aptitude dominant on both states — **this is not a
finished clinical differentiation**, only the largest safe tie-break
found by search.

**Open question this raises, Pete's call, not resolved here:** when
salience-only can't achieve narrative-correct differentiation within
calibration-safe bounds, does that cluster get left as a
mechanical-only fix, get combined with a targeted vector nudge, or get
deferred to the larger vector re-authoring pass? No general answer
yet — this is one confirmed data point, not assumed to generalize to
the other 8 salience-uniform clusters. Needs testing against a few
more before any pattern can be claimed. This pilot's scope was
deliberately one cluster — its result is the signal to bring back for
a sequencing conversation, not a green light to mechanically repeat
the search across the rest.

## Cluster check — rank-9 (`the_fracture` / `decision_blindness`)

Verification pass only, 2026-08-20 — no code changed. `SALIENCE_PROFILES`
confirmed byte-identical for both (`engine/data/salience.py`, ALLIANCE —
HIGH tier), `dimensional_vector` confirmed identical (`alliance_liability`
dominant at 0.6, matches the cluster map's rank-9 row).

**Not a schema limitation — the real finding is narrower.** An initial
working hypothesis (Alliance-liability for `the_fracture`,
Authority-liability/exclusion-from-decision-rights for
`decision_blindness`) was checked against the live `descriptive_prose`
and against precedent elsewhere in the taxonomy. The mechanism itself is
real: `the_suppression_filter` (also Alliance-primary) already carries an
Authority-secondary weight (`authority_liability/asset = 1.0`, above the
0.4 floor) — an Alliance/Authority split is an authored pattern in this
schema, not an invented one. What doesn't hold up is applying it to this
pair: `decision_blindness`'s own prose explicitly rules out an
authority/exclusion framing — *"The decision-maker wasn't negligent. The
information simply never reached them, because nobody's job was making
sure it did"* — an information-routing gap, not a decision-rights
exclusion. No confident secondary-dimension read was found for either
state in this pair.

**Low downstream impact, independent of the above.** Both states route to
the same `resolution_family` — `"Intervention + Executive Counsel"` —
confirmed via direct read of `engine/data/states.py`. Whichever state wins
an unresolved tie here, a real respondent gets the same resolution
recommendation either way.

**Logged as:** a real tie, accurately authored given the available
textual grounding, low practical/product stakes — not prioritized for
further pursuit. Not a candidate for a salience or vector remediation
pass unless the underlying descriptive_prose for one of these two states
changes.

## Pilot result — rank-8 cluster (`built_to_fail` / `the_paper_tiger`)

Third pilot for this investigation. Commit `58a19a0`, 2026-08-20. Two
explicitly separate parts — the tie-break succeeded mechanically; the
pilot's real significance is a taxonomy-wide finding it surfaced, not
the tie-break itself.

### Part 1 — the tie-break: real, safe, same kind of success as rank-7

`SALIENCE_PROFILES` confirmed byte-identical for both states before this
change (APTITUDE — HIGH tier), `dimensional_vector` confirmed identical —
combined, a guaranteed exact-tie score, 175/175 calibration profiles tied.

`built_to_fail`'s salience is unchanged — approved as-is, clean
aptitude-dominant read. `the_paper_tiger` differentiated on two axes per
its real `descriptive_prose`: aptitude reduced (not a skill/resourcing
story), authority raised (a structural gap — no one held responsible for
keeping documentation current — the same magnitude class as
`the_suppression_filter`'s own Authority secondary, real precedent, not
invented), attitude raised (operational avoidance — *"managed
verbally... discovers the record doesn't match reality"*). alliance
untouched on both — no textual basis to move it. `dimensional_vector`
deliberately untouched — salience-only, by design.

4 candidates searched against the real calibration pipeline (aptitude
1.0–2.0, authority 1.0–1.2, attitude 1.3–1.5), all passed identically
clean. Landed on aptitude=1.0/authority=1.0/attitude=1.5 — best
worst-case gap floor (min 0.0195, also best max 0.254) among candidates
tested, no further search needed given every candidate passed cleanly.

**Mechanically validated, same four checks as rank-7:**
- Tie fully broken: 175/175 tied before → 0/175 after.
- Zero cross-contamination: full 58-state × 175-profile comparison.
  (One methodology note for the record: the first verification pass
  showed 350 apparent contamination hits — a stale-baseline bug on this
  session's own end, comparing against a snapshot predating the
  already-committed rank-7 change. Regenerated a correct current-HEAD
  baseline and re-ran; zero once compared correctly.)
- Full regression exactly at the 171/175 baseline — same 4 pre-existing
  failures, nothing new, confirmed across all 4 candidates tested, not
  just the landed one.
- Real margin: `built_to_fail`'s own 3 profiles stay at a perfect 0.0000
  self-match, entirely unaffected (its salience never changed).
  `the_paper_tiger`'s 4 profiles pass with a 0.077–0.143 gap to rank-1 —
  well inside the pass window, not a bare clear.

### Part 2 — the dominance finding: this pilot's actually significant result

This cluster was chosen because `built_to_fail` wins a false rank-1 in
**49 of 175 calibration profiles (28%)** — quantified directly from the
full-suite snapshot, not estimated. Only 3 of its 52 total rank-1 wins are
genuinely correct.

**That rate does not move, at any tested magnitude.** Confirmed
empirically across all 4 candidates (a wide spread — aptitude 1.0 to 2.0,
more than double) — `btf_false_rank1` sat at exactly 49/175 every single
time. Traced to why, not just observed: `built_to_fail` and
`the_paper_tiger` share an identical `dimensional_vector`, and
`built_to_fail`'s own aptitude weight (its only real vector signal) stays
fixed at 2.5. No `the_paper_tiger`-only salience reweighting can out-score
a fixed, full-weighted identical vector on `the_paper_tiger`'s own
aptitude-flavored calibration profiles (`APT-PT-00/01/02/03`) — confirmed
directly: `built_to_fail` wins those 4 by a consistent gap in every
candidate tested. This is a mechanical ceiling, not a search-tuning
problem.

**Of the 49 false-rank-1 profiles, only 4 belong to `the_paper_tiger`. The
other 45 are unrelated states entirely** — states that share no vector
with `built_to_fail` at all. This pilot's scope (one paired state) never
touches them, by design, same as rank-7 and rank-9's scope discipline.

**What this means for sequencing:** `built_to_fail`'s dominance is not a
tie artifact this or any other salience pilot can resolve. It's the
**first concrete, evidence-backed candidate in the whole SCD-WCS
investigation for the `dimensional_vector` re-authoring layer** —
pointing at a *specific* state as high-value for that work, rather than
treating the remaining 43+ states needing vector re-authoring as an
undifferentiated backlog. Not scoped or actioned here — Pete's call on
if/when the vector re-authoring layer opens, and whether `built_to_fail`
leads it.

## Full cluster characterization — all 11 clusters

**Characterization-only, 2026-08-20. No code touched, no weight numbers
proposed anywhere in this section.** Same verification depth as the
rank-8/rank-9 checks (live `SALIENCE_PROFILES`, live `descriptive_prose`
for every state, `dimensional_vector` confirmation, `resolution_family`
per state), applied to the 8 remaining clusters (ranks 1, 2, 3, 4, 5, 6,
10, 11) and reconciled against the 3 already-piloted/checked clusters
(7, 8, 9) in one table. This is input for a sequencing decision, not a
further pilot commitment.

| Rank | Size | Tie status | Stakes (`resolution_family` match) | Narrative-splittable? | Dominance (false rank-1) |
|---|---|---|---|---|---|
| 1 | 11 | Full uniform tie | **High** — 5 distinct family combos across the 11 states | **Yes** — 11 genuinely distinct mechanisms (diversity ceiling, broken promises, hidden burnout, low-performance norm, favoritism, no institutional learning, misaligned incentives, execution-courage gap, AI/automation anxiety, reward-system collapse, unstated-overtime/legal exposure) | None — 0/175 for all 11 |
| 2 | 10 | Full uniform tie | **High** — Intervention-only vs. Roadmap-only vs. several mixed combos | **Yes** — 10 distinct mechanisms | **`the_uninitiated`: 22/175 (12.6%)** — second-strongest dominance signal found this session |
| 3 | 8 | Full uniform tie | **Mostly low** — 7/8 share "Intervention + Executive Counsel" exactly; `the_unsolved_problem` alone differs ("Intervention + Roadmap") | **Partial** — 4 states (`the_exposed`, `hr_capture`, `heard_and_ignored`, `the_tolerated_violation`) share a real family resemblance ("the correction mechanism doesn't act"); `the_founders_grip` (bottleneck) and `sequential_decision_blindness`/`disparate_impact_architecture` (aggregate/statistical pattern, no bad actor) are genuinely different in kind | None |
| 4 | 6 (1 already split: `what_nobody_says`) | 5-way tie remains among the other 5 | **Partial** — 3/5 share "Intervention"; `narrative_lock` and `the_unlocked_door` differ | **Yes** for the remaining 5 — distinct (self-narrative rigidity vs. safety-reporting culture vs. neglected security practice, etc.) | `identity_erosion`: 1/175 (minimal) |
| 5 | 3 | Full uniform tie | **Partial** — `invisible_influence_architecture` + `planning_authority_gap` share a family; `paper_shield` differs | **Yes** — `paper_shield` (untested plans) is a different failure kind from the other two (informal-power/formal-authority mismatch) | `paper_shield`: 1/175 (minimal) |
| 6 | 3 | Full uniform tie | **High** — all 3 states have *different* `resolution_family`, no two match | **Yes** — 3 distinct mechanisms | **`the_second_close`: 5/175 (2.9%)** — real, smaller-scale dominance |
| 7 *(piloted)* | 2 | Resolved, commit 043b8ad | — | `the_unformed_leader`/`the_dormant_talent`, aptitude/attitude split landed; narrative compromise (aptitude stayed dominant on both, not the attitude-dominant read the text argued for) | Residual: `the_unformed_leader` 8/175, `the_dormant_talent` 6/175 — unrelated to the tie itself |
| 8 *(piloted)* | 2 | Resolved, commit 58a19a0 | Real — differing families (Roadmap+Intervention vs. Development+Roadmap) | `built_to_fail`=structural/resourcing, `the_paper_tiger`=documentation/accountability, real split | **`built_to_fail`: 49/175 (28%)** — largest dominance signal among any tied-cluster state, structurally unresolvable via salience alone (see Pilot result above) |
| 9 *(checked)* | 2 | Confirmed tie, not pursued | Low/cosmetic — same `resolution_family` | **No** — text doesn't support the tested hypothesis; tie reads accurately authored | None |
| 10 | 2 | **Already differentiated** (`the_untouchable` custom salience, `the_inner_circle` uniform default) | **Low in substance** — same two families, reordered strings ("Executive Counsel + Intervention" vs. "Intervention + Executive Counsel") | **Yes** — individual exemption vs. systemic clique; the existing differentiation is well-grounded, self-validating precedent | None — 0/175 for both |
| 11 | 2 | Full uniform tie | **Low** — both "Intervention" | **Yes** — gradual value drift vs. performative wellness programs, real distinction despite low stakes | **`culture_drift`: 5/175 (2.9%)** — real dominance despite low tie-stakes |

### Sequencing read (analysis, not a decision)

- **Rank 1 and rank 2** are large (10-11 states each), high-stakes
  (real `resolution_family` spread), and narratively real (every member
  reads as a genuinely distinct mechanism) — but that scale puts them
  closer to the full `dimensional_vector` re-authoring project than to a
  quick 2-3-state pilot. An 11-way or 10-way differentiation is a
  different kind of undertaking than what ranks 7/8/9 tested.
- **Rank 6 and rank 5** read as the cleanest remaining small-pilot
  candidates if that path continues — rank 6 has the cleanest possible
  stakes signal (all 3 states carry a different `resolution_family`,
  no two match) with a real, if modest, dominance finding
  (`the_second_close`); rank 5 has partial stakes and a clean 1-vs-2
  narrative split.
- **Rank 3, rank 9, and rank 11** read as low-value/cosmetic — same
  category as rank 9's already-logged finding (real ties, accurately
  authored, low practical stakes). Not prioritized.
- **Rank 4 and rank 10** are partially resolved already. Rank 10's
  existing split is confirmed well-grounded (its own real narrative
  distinction backs it up) — a validated precedent, not an open item.
  Rank 4's remaining 5-way tie has real partial stakes and real
  narrative distinction if it's ever prioritized, but `what_nobody_says`
  is already correctly split out.

## Separately flagged — pure vector-strength dominance (not a tie or cluster question)

**A structurally different kind of finding from everything else in this
document.** Surfaced as a side effect of the dominance check applied to
the 11 clusters, but these three states have **no cluster-mate to
characterize against and no tie to break** — they have genuinely unique
`dimensional_vector`s (confirmed in the original cluster map, "The 7
states with genuinely unique vectors" above) and win false rank-1 purely
on raw vector alignment against unrelated profiles, not shared-vector
confusion:

| State | False rank-1 | True rank-1 |
|---|---|---|
| `invisible_performance_management` | **59/175 (33.7%)** | **0** |
| `the_unexamined_algorithm` | 11/175 (6.3%) | 0 |
| `the_overloaded_manager` | 4/175 (2.3%) | 0 |

`invisible_performance_management` is **the single largest dominance
problem in the entire taxonomy** — larger than `built_to_fail`'s 28%,
and it has never once been the genuinely correct rank-1 answer across
all 175 profiles. No salience or tie remediation touches this class of
problem at all — there is no cluster-mate to differentiate against, and
no shared-vector confusion to resolve. This needs its own future
investigation, independent of the cluster/tie remediation track this
whole document has been about. Not scoped or actioned here.

## Dominance-mechanism investigation — cross-cutting, not per-state

**Diagnostic only, 2026-08-20. No code touched, no weight numbers
proposed.** Seven states flagged this session with meaningful
false-rank-1 dominance, spanning both tied clusters and
genuinely-unique vectors, examined together rather than one at a time:
`built_to_fail` (28%), `invisible_performance_management` (33.7%),
`the_uninitiated` (12.6%), `the_unexamined_algorithm` (6.3%),
`the_second_close` (2.9%), `culture_drift` (2.9%),
`the_overloaded_manager` (2.3%). For each: `dimensional_vector`
magnitude/concentration on its dominant field, `SALIENCE_PROFILES`
entry (presence and magnitude), and — pulled directly, not
inferred — every profile ID it steals rank-1 from and that profile's
true target's own dominant vector field.

| State | Dominance | Vector dominant field (magnitude) | Vector concentration (dom/total) | Salience | Theft pattern |
|---|---|---|---|---|---|
| `invisible_performance_management` | **33.7%** | aptitude, 0.45 | 0.290 | Custom, sharp: aptitude=2.5, rest 0.4 | **Broad, cross-dimensional** — steals from Alliance-, Aptitude-, Attitude-, and Authority-dominant targets alike |
| `built_to_fail` | **28.0%** | aptitude, 0.60 (highest raw magnitude of the 7) | 0.462 (sharpest/most peaked) | Custom, sharp: aptitude=2.5, rest 0.4 | **Broad, cross-dimensional** — all 4 target dimensions represented among its 49 stolen profiles |
| `the_uninitiated` | 12.6% | authority, 0.45 | 0.300 | Custom, sharp: authority=2.5, rest 0.4 | **Narrow, same-dimension** — 20 of 22 stolen targets are authority-dominant |
| `the_unexamined_algorithm` | 6.3% | authority, 0.50 | 0.345 | Custom: authority=2.5, aptitude=1.0 secondary, rest 0.4 | **Narrow, same-dimension** — 10 of 11 stolen targets are authority-dominant |
| `the_second_close` | 2.9% | alliance, 0.45 | 0.300 | Custom, sharp: alliance=2.5, rest 0.4 | **Narrow, same-dimension** — all 5 stolen targets are alliance-dominant |
| `culture_drift` | 2.9% | attitude, 0.35 | 0.233 | Custom: attitude=2.5, authority=1.0 secondary, rest 0.4 | **Narrow, same-dimension** — all 5 stolen targets are attitude-dominant |
| `the_overloaded_manager` | 2.3% | aptitude, 0.35 | 0.233 | Custom: aptitude=2.5, authority=1.0 secondary, rest 0.4 | **Anomalous** — all 4 stolen targets are attitude-dominant, not aptitude (its own dimension) or authority (its secondary) |

### Three direct findings

**(a) Salience presence/magnitude does not correlate with dominance —
it's a constant across all 7, not a variable.** Every one of the 7 has a
custom, sharply-weighted salience entry (2.5 on its dominant field),
from the biggest dominator (33.7%) to the smallest (2.3%). This falsifies
the "lacking a custom entry = generalist attractor" hypothesis outright
— nothing in this set lacks an entry.

**(b) Vector magnitude/concentration on the dominant field does not
correlate with dominance magnitude, and not even in a consistent
direction.** `invisible_performance_management` has the *lowest*
concentration (0.290) of the top two dominators yet wins the most
(33.7%); `built_to_fail` has the *highest* concentration of all 7
(0.462, a sharp single-spike vector) and wins second-most.
`the_unexamined_algorithm` has higher raw magnitude (0.50) than
`the_uninitiated` (0.45) but roughly half its dominance (6.3% vs.
12.6%). No single metric here predicts dominance magnitude
monotonically.

**(c) The aptitude-signal-correlation hypothesis specifically checked
against `built_to_fail` does NOT hold — confirmed directly, not
assumed.** `built_to_fail`'s 49 stolen profiles span all four
dimensions in roughly even measure (Alliance, Aptitude, Attitude, and
Authority targets all represented), not concentrated on
aptitude-flavored targets. What the theft data actually shows instead
is a **magnitude-of-dominance split**: the two biggest dominators
(`invisible_performance_management`, `built_to_fail`, both >25%) steal
broadly across all four dimensions; four of the remaining five
(`the_uninitiated`, `the_unexamined_algorithm`, `the_second_close`,
`culture_drift`) steal almost exclusively from targets sharing their
*own* dominant dimension — a narrow same-dimension "neighbor" effect,
structurally different from a broad attractor effect.

### Genuine anomaly, logged as open rather than forced into a pattern

`the_overloaded_manager` fits neither pattern. It's aptitude-dominant
with an authority secondary, but all 4 profiles it steals are
attitude-dominant — a dimension where it has no elevated presence in
either vector or salience. Checked one case directly (`ATT-IT-02`'s
`dimension_summary`: authority 0.44, attitude 0.40, alliance 0.25,
aptitude 0.15 — aptitude is actually the *lowest* of the four, not
elevated); it doesn't explain the win either. Small sample (n=4) —
flagged for more data before any theory is trusted, not resolved here.

## Sequencing synthesis — two-track recommendation (Pete's call, not decided here)

**A proposal for Pete's decision, drawn directly from the theft-pattern
split above — not a decision already made, and nothing here has been
built.** The broad-vs-narrow theft distinction maps onto two
structurally different remediation problems that likely need different
handling.

**Track 1 — narrow neighbor-stealers.** `the_uninitiated`,
`the_unexamined_algorithm`, `the_second_close`, `culture_drift`, and by
extension any other state found later with the same narrow,
same-dimension theft signature. Salience-only differentiation is a
*plausible* fix for this shape of problem — structurally similar to
rank-7's confirmed success (`the_unformed_leader`/`the_dormant_talent`,
also a narrow within-cluster tie, resolved via salience alone without
touching `dimensional_vector`). Candidate for continued pilot-style
remediation, cluster by cluster, same process as rank-7/8/9 — dry-run,
search against the real calibration suite, full verification, Pete
confirms before commit.

**Track 2 — broad cross-dimensional attractors.**
`invisible_performance_management` and `built_to_fail`. Confirmed NOT
fixable via salience alone — direct evidence from rank-8's actual pilot
(searched 4 magnitudes spanning a wide range, `built_to_fail`'s false
rank-1 rate never moved), now reinforced by this session's broader
theft-pattern data showing the dominance isn't concentrated on any one
paired opponent or dimension to reweight against. These need
`dimensional_vector`-level attention — likely reducing peak
concentration or reshaping the vector itself, not just reweighting a
paired opponent, since there often isn't a single clean opponent to
pair against (the theft is spread across many unrelated states). This
is real clinical/taxonomic authoring work, comparable in kind to the
still-undated `STATE_CAUSATION_OVERRIDES` item — the harder of the two
tracks, and should be sequenced with that in mind rather than attempted
piecemeal alongside Track 1's lighter-weight pilots.

**`the_overloaded_manager`** sits outside both tracks — logged as an
open, small-sample anomaly, not assigned to either track until more
data (more theft profiles, or a deeper trace of the actual
centroid-displaced accumulated_vector rather than the derived
`dimension_summary`) clarifies what's actually happening.

Not scoped or actioned here. Both tracks, their relative priority
against each other and against `invisible_performance_management`'s
own unscoped investigation, and whether Track 1 continues at all given
rank-1/rank-2's scale (see "Full cluster characterization" above) are
all Pete's call.

## Cross-references

- `prompts/primary-state-target-match-finding.md` — original 1/58
  finding, Category E Direction 3 pre-scoping.
- `prompts/severity-follow-on-gate-investigation-findings.md`, lines
  178-241 — original 6-profile exact-tie sample.
- `engine/accumulation.py`'s `rank_states()` — the traced mechanism.
- `engine/data/states.py` — `dimensional_vector` authoring, per-state.
- `engine/data/salience.py` — `SALIENCE_PROFILES`, per-state weighting.
- `tools/_salience_pilot_search.py` (untracked, scratch) — the delta
  search used to find the pilot's final magnitude against the real
  calibration pipeline.
- Section 13a Decision Register — consolidated investigation row.
