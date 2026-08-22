# SCD-WCS Remediation Program v1

**PROGRAM STATUS, 2026-08-21: ALL 8 PHASES RUN TO COMPLETION.** This
document is now a historical sequencing record, not a live plan --
see `prompts/scd-wcs-remediation-tracker.md` for the current,
authoritative per-state disposition (this doc's own stated design,
unchanged). One-line status markers added under each phase header
below; full detail lives in the tracker, not duplicated here.

Phased program for the remaining SCD-WCS / primary-state ranking
remediation scope. Full technical background lives in
`prompts/scd-wcs-cluster-map-findings.md` (the verification record) and
`prompts/scd-wcs-remediation-tracker.md` (the plain-language working
tracker, updated as each phase progresses — that file, not this one, is
the live source of truth for status). This file is the sequencing plan;
re-check the tracker before resuming any phase, since its content moves
faster than this document will.

Shipped so far, not part of remaining scope: rank-7 (`the_unformed_leader`/
`the_dormant_talent`), rank-8's narrow tie-break (`built_to_fail`/
`the_paper_tiger`), rank-9 (declined, accurately authored), rank-10
(pre-existing, validated), rank-5 (`invisible_influence_architecture`/
`planning_authority_gap` differentiated, `paper_shield` re-clustered
Authority→Aptitude), rank-6's partial fix (`silosolation` tie-break-only).
11 of 58 states carry a real, if sometimes partial, fix. `the_arbitrary_standard`
(rank-6) is the one already-diagnosed leftover, carried into this program
as Phase 7.

---

## Standing discipline — every phase, no exceptions

This is unchanged from the work already done this session and is not
relaxed for scale. Re-read before starting each phase:

- **Diagnose before proposing any fix.** Real `descriptive_prose`, real
  `dimensional_vector`/`SALIENCE_PROFILES` pulled fresh from disk, real
  pipeline verification via `run_profile()` — never hand-derived,
  never assumed from a prior session's notes without re-checking.
- **Text-groundedness checked BEFORE any axis or vector value is
  proposed, not after.** If a candidate is only numerically convenient,
  say so and don't recommend it. This is the standard that caught
  `silosolation`'s withdrawn Attitude proposal and
  `the_arbitrary_standard`'s counterproductive weight this session — it
  does not get relaxed because a later phase is bigger or slower.
- **Any fix must hold the full 175-profile regression baseline
  (171/175, the same 4 known pre-existing failures — `identity_erosion`,
  `invisible_burnout`, `leadership_deafness`, `the_untouchable`) with
  zero NEW failures**, or the tradeoff must be explicitly surfaced and
  NOT written without approval.
- **Vector-shape changes (not just salience) require the same search
  discipline as `paper_shield`'s 12-candidate search** — report the
  search across a real candidate spread, not a single hand-pick.
- **Dry-run every patch. Never write without an explicit go-ahead.**
- **Update the tracker honestly.** Partial fixes stay partial in the
  writeup. Residuals get stated plainly, not implied-closed. A phase
  that finds nothing safe to ship is a valid, complete outcome — report
  it as such, don't force a fix to have something to show.
- **STOP AND REPORT after each numbered phase below.** Do not proceed
  to the next phase without an explicit go-ahead, even if a phase's
  findings look clean-cut. This is a hard checkpoint, not a suggestion.

---

## Phase 1 — Rank-4 confirmation

**STATUS: COMPLETE.** All 5 states confirmed SAME-CLUSTER DIFF, 5-way tie still fully live. `identity_erosion`'s pre-existing calibration failure root-caused to Track 2 domination, not a rank-4-intrinsic problem. `narrative_lock`/`the_dormant_talent` razor-thin-margin fragility found and logged. Real fixes deferred to Phase 8 given low practical stakes (shared `resolution_family` across most members). Commit `e8b25a9`.

**Scope:** `identity_erosion`, `the_culture_that_wasnt`, `narrative_lock`,
`the_unreported_hazard`, `the_unlocked_door` — a 5-way uniform tie
(`what_nobody_says`, the 6th member of this vector family, is already
correctly split out with its own validated salience entry, not part of
this phase). Shared vector `(.15,.15,.15,.15,.25,.15,.35,.15)` — Attitude-
dominant, Alliance secondary.

**Why first:** flagged in the cluster-map findings as "partially resolved
already" — `what_nobody_says`'s split is a validated precedent, and the
remaining 5-way tie has real partial stakes (3 of 5 share `resolution_family`
"Intervention"; `narrative_lock` and `the_unlocked_door` differ) and real
narrative distinction if prioritized. Diagnostic-only, low-risk, quick —
confirm what "partially resolved" actually covers before deciding whether
this needs its own pilot or can stay parked.

**Diagnostic tasks:**
- Pull real `descriptive_prose` for all 5 remaining-tied states directly
  from `engine/data/states.py`.
- Run the direct decomposition method (mirroring
  `tools/_scdwcs_decomposition_rank6.py`) against the real pipeline —
  confirm the 5-way tie is still live post this session's rank-5/rank-6/
  paper_shield changes (none of which touched rank-4, but re-verify
  rather than assume).
- Check for tie-artifact vs. genuine cross-cluster signal, same method
  as every other cluster this session.
- Report findings; no fix proposed in this phase unless the diagnosis is
  unusually clean and Pete explicitly asks to continue same-session.

**Checkpoint:** stop and report after this phase.

---

## Phase 2 — Cross-cluster asymmetry mechanism investigation

**STATUS: COMPLETE.** Working theory found and validated: three distinct lever shapes (uniform floor raise, targeted secondary-axis raise, dual-primary-axis), not one universal fix. Refined once in Phase 6 for dimension-crowding (a comparably-shaped rival isn't enough if the broader dimension family is too large). See the tracker's Open Investigative Questions table for the full writeup. Commit `511dd7b`.

**Scope:** the shared open question underlying `the_uninitiated`,
`the_unexamined_algorithm`, and `culture_drift` — all three show some
version of "steals from a whole other group" rather than a clean same-
cluster tie or a broad Track-2-style attractor. Logged in the tracker's
Open Investigative Questions table, status OPEN.

**The question:** when two whole clusters (or a unique-vector state and a
cluster) compete on the same dominant dimension, what actually decides
which one wins? The naive theory — "the sharper/more concentrated vector
wins" — is confirmed **backwards** in the one case checked directly:
`the_uninitiated` (rank-2, authority_liability=0.45, the *less*
concentrated vector) systematically beats 7 of rank-3's 8 states
(authority_liability=0.6, the *sharper* vector) across real score gaps of
0.023–0.065, not ties. No replacement theory exists yet.

**Why second, before ranks 1/2/3/11:** this mechanism directly blocks any
confident fix decision for `culture_drift` (Phase 3), the rank-3 cluster
`the_uninitiated` steals from (Phase 4), rank-2 which contains
`the_uninitiated` itself (Phase 5), and by extension informs how rank-1
(Phase 6) should be approached if similar cross-cluster signal shows up
there too. Diagnostic-only — this phase does not fix any state, it tries
to explain the shared mechanism so Phases 3–6 aren't each re-deriving it
independently or guessing at a fix that ignores the real cause.

**Diagnostic tasks:**
- Pull the real `dimensional_vector`/`SALIENCE_PROFILES` for `the_uninitiated`,
  rank-3's 8 states, `the_unexamined_algorithm`, `culture_drift`, and
  culture_drift's rank-1/rank-10 targets.
- Look for a property that actually correlates with which side wins —
  candidates to check directly against real data, not assumed: salience
  magnitude ratio (not just presence), the accumulated session vector's
  own alignment/angle to each competing vector, liability vs. asset
  balance, secondary-axis contribution size, cluster size itself.
- Test any candidate theory against all three known cases
  (`the_uninitiated`/rank-3, `the_unexamined_algorithm`'s 3-cluster
  spread, `culture_drift`'s rank-1/rank-10 split) before treating it as
  confirmed — three independent test cases, not one.
- Report the mechanism if found, or report clearly that it remains
  unexplained if the search comes up empty. Either is a valid, complete
  outcome for this phase.

**Checkpoint:** stop and report after this phase.

---

## Phase 3 — Rank 11 (2 states)

**STATUS: COMPLETE.** `culture_drift`/`wellbeing_theater` confirmed genuinely Attitude-dominant and distinct; real fix deferred to Phase 8 given low practical stakes (shared `resolution_family`). A differentiation candidate was searched and confirmed clean but not shipped (available for a future session). `paper_shield`'s ripple effect on rank-11's own profiles surfaced and logged. Commit `511dd7b`.

**Scope:** `culture_drift`, `wellbeing_theater` — smallest remaining
cluster, vector `(.15,.15,.25,.15,.15,.15,.35,.15)`, Attitude-dominant
with Authority secondary. `culture_drift` already has a real dominance
signal on record (5/175, 2.9%) and a partially-decomposed cross-cluster
footprint (1 of 5 stolen profiles is the tie-artifact against
`wellbeing_theater`; the remaining 4 genuine wins split 75%/25% between
rank-1 and rank-10).

**Why third:** smallest scale (2 states, like ranks 7/8/9/10 already
resolved), and directly depends on Phase 2's mechanism finding — the
75%/25% cross-cluster split needs the same-shape explanation Phase 2 is
trying to establish before proposing any differentiation with confidence.

**Diagnostic tasks:** real text comparison between `culture_drift` and
`wellbeing_theater` (do they read as genuinely distinct in real life, or
is this another `the_fracture`/`decision_blindness`-style accurately-
authored tie with low practical stakes — both currently route to the
same `resolution_family`, "Intervention", per the tracker); apply Phase
2's mechanism finding to the rank-1/rank-10 cross-cluster piece before
proposing any fix there.

**Checkpoint:** stop and report after this phase.

---

## Phase 4 — Rank 3 (8 states)

**STATUS: COMPLETE.** All 8 states diagnosed: 5 confirmed SAME-CLUSTER DIFF (deferred to Phase 8), `sequential_decision_blindness` scoped and declined (genuine three-way axis mismatch, no fix recommended), `disparate_impact_architecture` genuinely unresolved (data favors Authority, text still pulls toward Alliance, not settled either way). `the_unsolved_problem` moved out of this cluster entirely via a separate re-clustering (Authority -> Aptitude, commit `2deb461`). Confirms Phase 2's theory comprehensively -- 100% own-profile loss rate across the cluster. Commit `00944a6`.

**Scope:** `the_founders_grip`, `the_exposed`, `hr_capture`,
`heard_and_ignored`, `the_tolerated_violation`, `the_unsolved_problem`,
`sequential_decision_blindness`, `disparate_impact_architecture` — full
8-way uniform tie, vector `(.1,.1,.6,.1,.1,.1,.1,.1)`, the sharpest
Authority-dominant vector in the taxonomy. This is `the_uninitiated`'s
real cross-cluster target (14 of 16 genuine wins land here, concentrated
on 7 of these 8 states — `the_founders_grip` alone absorbs 3 of them).

**Why fourth:** real stakes are mixed, not uniform — 7 of 8 states share
`resolution_family` "Intervention + Executive Counsel" exactly (mostly
low differentiation value on its own), but `the_unsolved_problem` is a
genuine outlier ("Intervention + Roadmap"). The real reason to prioritize
this cluster is its relationship to `the_uninitiated`, not its own
internal tie-stakes — cannot be fixed sensibly without Phase 2's finding,
since any internal rank-3 differentiation could interact with why
`the_uninitiated` currently wins against it.

**Diagnostic tasks:** real text pass across all 8 states (the cluster-map
findings already note a partial narrative grouping — 4 states sharing "the
correction mechanism doesn't act" as a theme, `the_founders_grip` reading
as a bottleneck, `sequential_decision_blindness`/`disparate_impact_architecture`
reading as aggregate/statistical rather than a bad-actor story — confirm
or correct this against full `descriptive_prose`, not the summary); apply
Phase 2's cross-cluster finding to scope whether/how `the_uninitiated`'s
relationship to this cluster factors into any internal differentiation.

**Checkpoint:** stop and report after this phase.

---

## Phase 5 — Rank 2 (10 states)

**STATUS: COMPLETE.** All 10 states diagnosed: `decision_paralysis`/`the_lost_map` confirmed genuine internal-tie winners (a distinct pattern from rank-3's complete-victim shape); 3 states (`leadership_continuity_risk`, `transition_paralysis`, `compression_crisis`) confirmed SAME-CLUSTER DIFF with real consequential stakes, deferred to Phase 8; `the_policy_lag`/`the_pay_fog` mis-clustering hypotheses mechanically tested and empirically rejected; `dueling_narratives`/`pay_exposure` flagged genuinely open, not tested. Logged the standing Attitude-dominant `dimension_summary` confound across 9 states, 3 phases (Direction 1) -- later confirmed bidirectional in Phase 6. Commit `eab8003`.

**Scope:** `the_uninitiated`, `leadership_continuity_risk`,
`decision_paralysis`, `the_policy_lag`, `dueling_narratives`,
`transition_paralysis`, `the_lost_map`, `pay_exposure`, `the_pay_fog`,
`compression_crisis` — full 10-way uniform tie, vector
`(.15,.15,.45,.15,.15,.15,.15,.15)`, Authority-dominant.
`the_uninitiated` is the cluster's own dominance-signal carrier (22/175,
12.6% — the session's second-largest raw dominance figure after
`built_to_fail`), and its internal tie is the "6 of 22 are just rank-2's
own known cluster tie" component already decomposed.

**Why fifth, after rank-3:** rank-3 is `the_uninitiated`'s real external
target; understanding that relationship first (Phase 4) informs whether
`the_uninitiated` itself needs a vector-level fix (it's currently WINNING
against a sharper rival, contradicting the "sharper wins" assumption —
Phase 2's mechanism, once understood, should clarify whether that's
something to correct or something to leave alone) before touching rank-2's
internal 10-way tie, which includes `the_uninitiated` as a full member.

**Diagnostic tasks:** real text pass across all 10 states; apply Phase
2's mechanism directly to `the_uninitiated`'s specific case (does the
mechanism finding suggest `the_uninitiated`'s dominance against rank-3 is
something to fix, or an accurate reflection of real narrative strength
that happens to contradict the sharper-vector intuition); scope whether
`the_uninitiated`'s own differentiation from its 9 rank-2 cluster-mates
is even sensible before its external relationship to rank-3 is settled.

**Checkpoint:** stop and report after this phase.

---

## Phase 6 — Rank 1 (11 states)

**STATUS: COMPLETE.** All 11 states diagnosed via Stage A + 3 Stage B batches: `the_diversity_ceiling` carries the rank-1-wide shared finding (zero outbound wins, 100% own-profile loss, Phase 2's theory refined for dimension-crowding); 6 states confirmed same-cluster-diff and deferred to Phase 8; `invisible_burnout`/`groundhog_day` mis-clustering candidates mechanically rejected; `the_inside_track` surfaced a genuinely new "weak positive, impractical magnitude" outcome category; `the_broken_compass` re-confirmed unchanged from Phase 2/3. Confirmed the bidirectional `dimension_summary` confound across all 11 states (Direction 2), bringing the confirmed footprint to 20 states across 4 phases. Full ripple audit run afterward, 32 newly-surfaced winner instances, zero new counted regressions. Commit `973079a`.

**Scope:** `the_diversity_ceiling`, `the_burned_credibility`,
`invisible_burnout`, `the_basement_standard`, `the_inside_track`,
`groundhog_day`, `the_wrong_reward`, `the_broken_compass`,
`human_displacement_anxiety`, `motivational_architecture_failure`,
`cultural_overtime` — the largest remaining cluster, full 11-way uniform
tie, vector `(.15,.15,.15,.15,.15,.15,.45,.15)`, Attitude-dominant. Real
stakes are high — 5 distinct `resolution_family` combinations across the
11 states, and each reads as a genuinely distinct real mechanism (diversity
ceiling, broken promises, hidden burnout, low-performance norm, favoritism,
no institutional learning, misaligned incentives, execution-courage gap,
AI/automation anxiety, reward-system collapse, unstated-overtime/legal
exposure — per the cluster-map findings' own characterization pass).
`culture_drift`'s largest genuine cross-cluster win (`the_broken_compass`,
3 of `culture_drift`'s 4 genuine wins) targets a member of this cluster.

**Why last of the four remaining clusters:** explicitly flagged in the
findings doc as closer in scale to a dedicated project than a quick pilot
— an 11-way differentiation is a materially different undertaking than
anything shipped so far this session, all of which were 2-3-state pairs
or trios. Sequenced last so Phases 2–5's method and mechanism findings
are as mature as possible before the largest, highest-stakes cluster is
attempted. Real possibility this phase itself needs to be broken into
its own sub-phases once scoped — don't assume it fits the same shape as
the smaller clusters.

**Diagnostic tasks:** real text pass across all 11 states, mapped against
the 5 `resolution_family` combinations; apply Phase 2's cross-cluster
finding to the `the_broken_compass`/`culture_drift` relationship
specifically; scope realistically whether this is one phase or several
before proposing any search.

**Checkpoint:** stop and report after this phase.

---

## Phase 7 — `the_arbitrary_standard`'s axis question

**STATUS: SHIPPED.** Attitude was re-confirmed as the wrong axis (unchanged from rank-6). Authority found on fresh re-examination -- real, previously-untested rule-application/documentation language in the text. Margin-searched (5 candidates), landed on 0.4 -> 2.0, closes rank-6 entirely. Commit `e9a2750`.

**Scope:** the one leftover from this session's rank-6 work. Confirmed
SAME-CLUSTER DIFF (genuinely Alliance-correct — "inconsistent, non-
transparent rule application producing differential treatment," a
fairness/equity-in-treatment story), but no text-grounded, mechanically-
sound secondary axis has been found. Attitude was tested and rejected on
both grounds this session (not text-grounded — the text explicitly
disclaims a willful/mindset framing the same way `silosolation`'s does;
and mechanically counterproductive — raising the weight monotonically
*decreased* its own score, traced to a liability:asset shape mismatch in
the real session signal).

**Why here, not folded into rank-6 cleanup earlier:** genuinely needs its
own fresh investigation, not a retry of the same axis — Authority and
Aptitude are the two untested candidates; neither has an obvious textual
hook yet (re-read the full `descriptive_prose` fresh, don't assume the
prior session's negative result on Attitude means one of the other two is
automatically right). Also carries a separate, already-confirmed caveat:
its own 3 dedicated profiles are lost outright to Track 2 broad attractors
regardless of what secondary axis eventually gets chosen — any fix found
here won't close that separately-flagged problem, and the writeup must
say so plainly, same as `paper_shield`'s and `silosolation`'s.

**Diagnostic tasks:** re-read the full `descriptive_prose` fresh (don't
carry forward the prior session's framing uncritically); test Authority
and Aptitude as candidate secondaries against both the text-groundedness
standard and the real pipeline (mirroring the rank-6 search method) before
proposing either; if no candidate passes both bars, report that plainly —
"no viable axis found" is itself a valid, complete outcome, as it was
this session.

**Checkpoint:** stop and report after this phase.

---

## Phase 8 — Track 2 investigation (`built_to_fail`, `invisible_performance_management`)

**STATUS: RUN TO COMPLETION, PARTIALLY RESOLVED.** Scope expanded well beyond the original 2 states once measured directly: a full 58-state taxonomy census found 37 states share the standard template+skew shape, of which 6 are actively dominant -- the original 2 plus `the_uninitiated`, `the_second_close`, and 2 states this session's own re-clustering work had manufactured (`paper_shield`, `the_unsolved_problem`, confirmed via `git show` reconstruction to have measured 0/175 pre-session). The 2 manufactured ones are SHIPPED/mitigated (commit `4c1a5de`). The original 2 plus `the_uninitiated`/`the_second_close` remain OPEN -- confirmed NOT fixable via any single-state or combined salience lever (whack-a-mole, caps real payoff at 1 of 19 masked states), needing a future taxonomy-wide vector/template re-authoring project, a distinct and much larger undertaking not completed within this program. This is the one phase left with a real, explicitly-flagged residual -- not force-closed as "done."

**Scope:** the two confirmed "broad cross-dimensional attractor" states.
`built_to_fail` steals 49/175 profiles (28%) spanning all four
dimensions; `invisible_performance_management` steals 59/175 (33.7%,
the single largest dominance problem in the entire taxonomy) and has
never once been the genuinely correct rank-1 answer across all 175
profiles. Both have no cluster-mate to differentiate against and no tie
to break — this is pure vector-strength dominance, structurally different
from every same-cluster or cross-cluster-asymmetry problem addressed in
Phases 1–7.

**Confirmed NOT fixable via salience alone**, direct evidence from
rank-8's own pilot: searching 4 magnitudes spanning a wide range never
moved `built_to_fail`'s false-rank-1 rate. This needs real
`dimensional_vector`-level attention — likely reducing peak concentration
or reshaping the vector itself — comparable in kind and difficulty to the
still-undated `STATE_CAUSATION_OVERRIDES` item, not a same-cluster pilot.

**Why last:** explicitly the harder of the two tracks per this session's
own sequencing analysis, and every phase above (1–7) surfaces `built_to_fail`
and/or `invisible_performance_management` as the winner stealing some
OTHER state's profiles — Phase 8 benefits from having the full picture of
how many different states' calibration profiles these two states are
already touching before any redesign is attempted, since a vector-level
change here has the widest possible blast radius of anything in this
program.

**Diagnostic tasks (scoping at minimum — do not assume a pilot ships this
phase):** pull real `descriptive_prose`/`dimensional_vector`/`SALIENCE_PROFILES`
for both states fresh; catalog every profile stolen from Phases 1–7's
work plus the two states' own already-known theft footprint, to build
one complete picture rather than the piecemeal view accumulated so far;
investigate whether a *reduced-magnitude* version of the same vector
shape (rather than a differently-shaped one) has been genuinely ruled
out, or only specific magnitudes were tested in rank-8's original search;
if a real fix direction emerges, it needs the same 12+-candidate search
discipline as `paper_shield`, scoped as its own multi-step effort, not a
single-session pilot.

**Checkpoint:** stop and report after this phase — end of program.
