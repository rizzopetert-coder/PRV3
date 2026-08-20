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
