# Severity Follow-On State Scoping — Investigation Findings, Open Design Question

Status: **UNRESOLVED. The defect is real, confirmed, and still live in production.
Nothing has been fixed. Two gate designs were tried and both failed on real
engine data. This document is a record of the investigation, not a build
plan.**

---

## The defect

`tools/test_aut_ps_01_q23_d_forced.py` — a regression test that drives
`engine/main.py`'s real production functions directly, not the calibration
harness — caught it: AUT-PS-01 (`paper_shield`, locked
`expected.severity_tier = Entrenched`) lands at `Endemic` in the real engine
instead, because `severity_trigger` firing (`engine/main.py:301`) is purely a
property of the answered option, with zero awareness of which state the
respondent is heading toward. `tools/calibration_runner.py`'s
`_SEVERITY_FOLLOW_ON_TARGETS` — the mechanism used throughout the Bucket 2/3
severity-wiring work to describe "this fix applies to state X" — is
state-scoped, but that scoping exists only in the calibration harness. It has
no production equivalent.

A full scan of every `severity_trigger` option against its question's real
`state_targets`, cross-referenced against which states each fix's harness
extension actually named, found the identical shape in 13 more cases beyond
the original SEVER-19/Q33 finding — 14 follow-on IDs total, spanning nearly
the entirety of this session's Bucket 2/3 severity-wiring effort:
SEVER-02, 10, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29.

`SEVERITY_FOLLOW_ON_INTENDED_STATES` (the state each of the 14 was actually
authored for, sourced from each fix's own MOB session-log record) was
authored and cross-verified — full detail and derivation in
`prompts/severity-follow-on-state-scoping-fix.md`. That data is not in
question. What's in question is how to gate on it.

**Explicitly out of scope, both here and in the fix:** Q23/SEVER-05
(`paper_shield` / `leadership_continuity_risk`) has zero harness opt-in for
*either* wired state — a different defect (never calibration-tested at all,
not a leak from one intended state to another). It surfaces repeatedly below
as background noise in test sessions, and is correctly *not* filtered by
either gate design, on purpose.

---

## Gate design 1 — any qualifying state (Gemini-confirmed, then falsified)

Filter `severity_inputs` against `SEVERITY_FOLLOW_ON_INTENDED_STATES`, keeping
an input only if at least one of its intended states cleared the signal floor
(`apply_signal_floor()`'s `cleared_floor`) — i.e., any state the product would
actually present to the respondent, not just the top-ranked one. Reasoning at
the time: the product already treats multi-state output as real
(`OutputRouting.qualified_states`), so gating severity on "any qualifying
state" matched how the product treats state membership everywhere else.
Gemini reviewed this as a narrow confirm-or-reject and returned a clean
confirm, no objections.

**Dry-run tested against real engine traces, confirmed too permissive:**

- AUT-PS-01's own session had **21 of 58 states** simultaneously clearing the
  signal floor, including both `paper_shield` and `invisible_influence_architecture`
  at once. SEVER-19's intended state genuinely did qualify this session — not
  as the real diagnosis, just as one of 21 co-qualifiers — so the filter
  correctly, uselessly, did not exclude it. Result unchanged: `Endemic`, not
  `Entrenched`.
- `the_broken_compass`'s own natural (unforced) answer path had **42 of 58
  states** qualifying, including `the_burned_credibility` — one of SEVER-23's
  *and* SEVER-24's intended states. The overshoot protection this session
  explicitly built to protect `the_broken_compass` from SEVER-23/24 (see
  `prompts/severity-follow-on-state-scoping-fix.md`'s own citation of that
  protection) does not survive contact with real qualifying-state breadth.

Root cause: the signal floor is loose enough that a large fraction of the
58-state taxonomy co-qualifies in almost any real session. "Any qualifying
state" ends up nearly as permissive as no gate at all.

## Gate design 2 — top-1 only (tested, falsified in the opposite direction)

Same mapping, same filter point, gated instead on the session's single
leading state (`rank_states()`'s rank-1, not `apply_signal_floor()` at all).

**Dry-run tested against real engine traces:**

- AUT-PS-01 — fixed. Lands at `Entrenched/33.33` exactly, as calibrated.
- `the_broken_compass`/SEVER-23/SEVER-24 — the specific protection is
  restored precisely. Isolated the math: SEVER-13 alone (the_broken_compass's
  own genuinely-wired trigger, untouched by this fix since it's outside the
  14-ID scope) produces `Entrenched/33.33`, exactly matching its locked
  target. The residual `Endemic/66.67` in the full session trace is fully and
  precisely attributable to the separate, out-of-scope SEVER-05 issue, not a
  gap in this design.
- **But four more spot-checks, run against each state's own natural,
  unforced answer path (not a forced scenario), surfaced a worse failure
  mode:**

| Profile | State | Own state = top-1? | Own intended trigger(s) alone → | Actual result under top-1 gating |
|---|---|---|---|---|
| AUT-IA-01 | invisible_influence_architecture | No (top-1 = paper_shield) | SEVER-19 alone → Entrenched/33.33 (correct) | Lands at Entrenched/33.33 anyway — but only because SEVER-05 (unrelated, out-of-scope) coincidentally produces the identical score. The real trigger was silently dropped. |
| ATT-UT-01 | the_untouchable | No (top-1 = the_overloaded_manager) | SEVER-25+29 together → **Endemic/66.67** (locked target) | **Lands at Entrenched/33.33 — one tier short.** Both of the_untouchable's own legitimately-intended triggers were stripped. |
| AUT-DN-01 | dueling_narratives | No (top-1 = invisible_performance_management) | SEVER-18 alone → Entrenched/33.33 (correct) | Same coincidental-match pattern as AUT-IA-01. |
| ATT-BS-01 | the_basement_standard | No (top-1 = the_overloaded_manager) | SEVER-25+20 together → **Endemic/66.67** (locked target) | **Lands at Entrenched/33.33 — one tier short**, same failure mode as ATT-UT-01. |

None of these four states ranked themselves top-1 in their own real session —
consistent with the already-logged `primary-state/intended-target match rate
1/58` Decision Register finding (see below). Top-1 gating strips a state's
own legitimately-intended severity contribution almost every time, because a
state being its own rank-1 match is the exception, not the rule.

---

## Diagnostic pass — is there ANY rank/score/margin cutoff that works?

For all 14 follow-on IDs, ran each intended state's own high-confidence
calibration profile through its natural, unforced answer path, and recorded
its real rank, real score, and real `cleared_floor` in that session (31 rows
total — some follow-ons have multiple intended states).

Correction made mid-investigation: `cleared_floor` is not governed by the
loose absolute threshold its own docstring implies. `check_signal_gate()`
(`engine/output.py`) applies two constraints — an almost-meaningless absolute
floor (`SCD_WCS_ALIGNMENT_THRESHOLD = -0.4`) and the real gate, a **relative
margin of `SCD_WCS_MARGIN_GATE = 0.05`** cosine units from the session's own
top-1 score. The table below reports that real margin explicitly.

| follow-on | intended state | profile | rank | score | margin from top-1 | cleared_floor | top-1 state |
|---|---|---|---|---|---|---|---|
| SEVER-02 | built_to_fail | APT-BF-01 | 1 | 0.9906 | 0.0000 | True | built_to_fail |
| SEVER-19 | invisible_influence_architecture | AUT-IA-01 | 2 | 0.9472 | 0.0000 | True | paper_shield |
| SEVER-21 | the_paper_tiger | APT-PT-01 | 2 | 0.9496 | 0.0000 | True | built_to_fail |
| SEVER-27 | the_tolerated_violation | AUT-TV-01 | 6 | 0.9861 | 0.0016 | True | the_unexamined_algorithm |
| SEVER-23 | groundhog_day | ATT-GD-01 | 16 | 0.9621 | 0.0145 | True | identity_erosion |
| SEVER-27 | disparate_impact_architecture | EXP-DIA-01 | 19 | 0.9645 | 0.0166 | True | the_unexamined_algorithm |
| SEVER-24 | narrative_lock | ATT-NL-01 | 8 | 0.9544 | 0.0191 | True | the_unformed_leader |
| SEVER-28 | the_founders_grip | AUT-FG-01 | 12 | 0.9506 | 0.0206 | True | the_uninitiated |
| SEVER-22 | heard_and_ignored | AUT-HI-01 | 19 | 0.9508 | 0.0298 | True | the_uninitiated |
| SEVER-27 | heard_and_ignored | AUT-HI-01 | 19 | 0.9508 | 0.0298 | True | the_uninitiated |
| SEVER-17 | compression_crisis | EXP-CC-01 | 18 | 0.9164 | 0.0349 | True | invisible_performance_management |
| SEVER-17 | pay_exposure | AUT-PE-01 | 16 | 0.9164 | 0.0349 | True | invisible_performance_management |
| SEVER-22 | hr_capture | AUT-HC-01 | 18 | 0.9395 | 0.0349 | True | the_uninitiated |
| SEVER-23 | the_burned_credibility | ATT-BC-01 | 33 | 0.9079 | 0.0529 | False | the_overloaded_manager |
| SEVER-24 | the_burned_credibility | ATT-BC-01 | 33 | 0.9079 | 0.0529 | False | the_overloaded_manager |
| SEVER-02 | the_undefined_role | APT-UR-01 | 5 | 0.9257 | 0.0575 | False | built_to_fail |
| SEVER-20 | the_basement_standard | ATT-BS-01 | 20 | 0.9004 | 0.0589 | False | the_overloaded_manager |
| SEVER-25 | the_basement_standard | ATT-BS-01 | 20 | 0.9004 | 0.0589 | False | the_overloaded_manager |
| SEVER-18 | dueling_narratives | AUT-DN-01 | 15 | 0.8807 | 0.0756 | False | invisible_performance_management |
| SEVER-22 | what_nobody_says | ATT-WNS-01 | 23 | 0.8829 | 0.0834 | False | the_overloaded_manager |
| SEVER-10 | wellbeing_theater | EXP-WT-01 | 12 | 0.8594 | 0.0849 | False | the_overloaded_manager |
| SEVER-10 | culture_drift | ATT-CD-01 | 24 | 0.8833 | 0.0863 | False | paper_shield |
| SEVER-20 | the_inside_track | ATT-IT-01 | 35 | 0.8436 | 0.1120 | False | the_overloaded_manager |
| SEVER-25 | the_inside_track | ATT-IT-01 | 35 | 0.8436 | 0.1120 | False | the_overloaded_manager |
| SEVER-20 | motivational_architecture_failure | EXP-MAF-01 | 38 | 0.8216 | 0.1314 | False | invisible_performance_management |
| SEVER-20 | cultural_overtime | EXP-CO-01 | 49 | 0.7380 | 0.1946 | False | the_overloaded_manager |
| SEVER-10 | identity_erosion | ATT-IE-01 | 30 | 0.7619 | 0.1998 | False | invisible_performance_management |
| SEVER-20 | the_wrong_reward | ATT-WR-01 | 49 | 0.7598 | 0.2022 | False | the_overloaded_manager |
| SEVER-22 | leadership_deafness | ATT-LD-01 | 56 | 0.6689 | 0.2987 | False | the_overloaded_manager |
| SEVER-25 | the_untouchable | ATT-UT-01 | 58 | 0.5867 | 0.3753 | False | the_overloaded_manager |
| SEVER-29 | the_untouchable | ATT-UT-01 | 58 | 0.5867 | 0.3753 | False | the_overloaded_manager |

**No global rank, score, or margin threshold separates these.** These 31 rows
are all *legitimately intended* states, run through their own best-case
calibration profile — and they span rank 1 to rank 58 of 58, margin 0.0000
to 0.3753. `the_untouchable` is dead last in its own session; a loose
threshold that keeps it would admit nearly the whole taxonomy (the same
failure mode as any-qualifying); a tight threshold that meaningfully excludes
noise (roughly where the existing 0.05 signal-floor gate already sits) would
exclude two-thirds of these legitimately-intended rows too (the same failure
mode as top-1). Caveat: this used each state's idealized best-case answer
path, so real-world spread is likely at least this wide, not narrower.

## Follow-up pass — per-state calibrated threshold, also falsified, more decisively

Hypothesis: even if one *global* threshold can't work, could each state's own
genuine/calibrated score (e.g. built_to_fail's own ~0.99 vs. the_untouchable's
own ~0.59) serve as a *per-state* floor? Tested by pulling each sample
state's full session ranking and inspecting the states occupying nearby rank
positions:

```
built_to_fail (rank 1, score 0.9906):
  rank 2  score 0.9906  the_paper_tiger        [tied EXACTLY]
  rank 3  score 0.9457  invisible_performance_management
  rank 4  score 0.8901  the_undefined_role

narrative_lock (rank 8, score 0.9544):
  rank 5-10, SIX different states, ALL tied at exactly 0.9544:
  the_suppression_filter, identity_erosion, the_culture_that_wasnt,
  narrative_lock, the_unreported_hazard, the_unlocked_door

heard_and_ignored (rank 19, score 0.9508):
  rank 16-22, SEVEN different states, ALL tied at exactly 0.9508:
  the_founders_grip, the_exposed, hr_capture, heard_and_ignored,
  the_tolerated_violation, the_unsolved_problem, sequential_decision_blindness

the_basement_standard (rank 20, score 0.9004):
  rank 17-23, SEVEN different states, ALL tied at exactly 0.9004:
  the_diversity_ceiling, the_burned_credibility, invisible_burnout,
  the_basement_standard, the_inside_track, groundhog_day, the_wrong_reward

cultural_overtime (rank 49, score 0.7380):
  rank 46-49, FOUR states tied at exactly 0.7380:
  the_broken_compass, human_displacement_anxiety,
  motivational_architecture_failure, cultural_overtime

the_untouchable (rank 58, score 0.5867):
  rank 55  score 0.7005  decision_blindness
  rank 56  score 0.6193  leadership_deafness
  rank 57  score 0.5980  the_inner_circle
  rank 58  score 0.5867  the_untouchable (distinct values here, no tie)
```

**This falsifies the per-state hypothesis more decisively than the rank/margin
data alone.** In 5 of 6 sampled sessions, the intended state's score is not
merely *close to* unrelated neighbors — it is **bit-for-bit numerically
identical** to 3-6 completely unrelated states simultaneously. No threshold
of any kind, global or per-state, can separate values that are exactly equal.
This points to something structural in how SCD-WCS similarity resolves for
this dimensional space (large numbers of states sharing identical or
near-identical relevant-dimension profiles against a given accumulated
vector), not a tuning problem solvable by picking a better number.

**Distinct, worth-its-own-investigation hypothesis — do not flatten this into
"the scores overlap."** "Close" and "exactly equal" are different findings
with different causes, and the data here is the second one, not the first.
5 of 6 sampled states weren't near-ties resolved to 4 decimal places by
coincidence — they were bit-for-bit identical floating-point values shared
across 3-7 states with no evident taxonomic relationship to each other
(`the_suppression_filter`, `the_culture_that_wasnt`, `the_unreported_hazard`,
and `the_unlocked_door` sharing an exact score with `narrative_lock` is not
an obviously-related cluster). That specific shape — many states landing on
the *same* value, not merely close values — is consistent with a structural
cause in the SCD-WCS computation itself: quantization or rounding somewhere
in the pipeline, a clamping step collapsing a range of inputs to one output,
or degenerate cosine geometry once enough states' profile vectors project
similarly against a given accumulated vector in this dimensional space. It is
not, on its own, evidence that the taxonomy is simply "noisy" or that these
states are conceptually close — that would predict *close* scores, not
*identical* ones. This wasn't investigated further tonight (out of scope for
a gate-design question), but it's a separate, real, mechanism-level question
about the scoring math itself, not a restatement of the rank-spread finding
above, and should be treated as its own line of inquiry rather than folded
into "the primary-state/target-match distribution is wide."

---

## Connection to the existing primary-state/target-match finding

This is not a coincidence and should not be treated as a separate item. The
`primary-state/intended-target match rate (1/58 in real calibration data)`
Decision Register row (Session Priority Queue item 5;
`prompts/primary-state-target-match-finding.md`; originally surfaced during
Category E Direction 3's investigation, same session that also first noted
"the gap between the calibration pass bar (0.35, `SCD_WCS_CLUSTER_WINDOW`)
and the live display's actual margin gate (0.05, `SCD_WCS_MARGIN_GATE`)") is
the same underlying ranking-distribution behavior, now quantified at much
larger scale and directly tied to a real, live scoring-integrity defect
rather than an output-display observation. The calibration harness's own
0.35 pass criterion is far looser than the 0.05 margin gate that actually
governs what a real respondent sees — which is exactly why the calibration
suite stayed byte-for-byte unchanged (171/175) through every gate design
tested here: it cannot detect this class of leak at all, in either direction.

Any future design for this gate should be evaluated jointly with that
existing item, not independently — they are very likely the same root cause
wearing two names.

---

## Current state, explicit

- **Working tree: clean, reverted.** No patch applied to `engine/main.py` or
  `engine/data/questions.py`. `tools/patch_severity_follow_on_state_scoping.py`
  exists on disk, uncommitted, and currently encodes the top-1 design (the
  last one tested) — it does not represent a decision, just leftover
  investigation scaffolding. Not deleted, in case it's a useful starting
  point for a future attempt, but should not be run as-is.
- **The defect is live and unpatched in production**, unchanged from before
  this investigation started: `severity_trigger` firing has no per-state
  gating anywhere in `engine/main.py` today. AUT-PS-01 and any real session
  matching a similar shape across the other 13 follow-on IDs will continue
  to collect severity input from unrelated states.
- No third gate design has been proposed. This is an open design question,
  not a task in flight.
