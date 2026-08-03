# Friction Tax — Legal/Compliance Tail-Risk Methodology (In Progress, Not Locked)

**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. All 30 Legal-scoring states are now classified into 5
mechanism clusters, with 4 of 5 clusters' dollar curves sourced (Addendum, below) -- ready
for Gemini architecture review. NOT yet implemented. Does not supersede the Option A
attritional-criteria rescale (turnover/productivity/decision-quality), which proceeds
independently -- this doc is specifically the deferred Legal/Compliance item that Option A
explicitly excluded.

## Why Legal/Compliance can't share Option A's mapping

Option A rescales the three attritional criteria to a payroll-fraction range (proposed 5%–25%)
because their real-world cost scales roughly with org size — more employees, proportionally
more turnover cost, more disengagement cost. Legal/Compliance doesn't scale that way. A
wrongful termination suit or an ADA claim costs roughly the same in absolute dollars whether
the defendant has 50 employees or 5,000 — severity is set by the legal mechanism and the
claim, not by the defendant's payroll. Forcing it through the same linear payroll-fraction
mapping either badly understates it (individual claims alone can exceed a small org's whole
attritional range) or forces the shared range wide enough to accommodate it, which overstates
every attritional-only state.

## Evidence base — corrected E2 figures only

Following the citation-audit finding this session (research/seven-experiments/citation-audit.md,
fixes committed c8e3c6c), only the corrected figures below should ever inform this design. The
original E2 document's Boeing $38M and Allstate $17.5M figures were fabricated and must never
be reused, including in future sessions that haven't seen this doc.

- **Beck v. Boeing** — $72.5M settlement, class of ~29,000 female employees at Boeing's Seattle
  facilities (2004). Real, verified, class/systemic discrimination case.
- **Tilkey v. Allstate** — $18.6M jury verdict; wrongful-termination component reversed on
  appeal; real final resolved outcome ~$4M (defamation only).
- **EEOC total recovery** — $665M FY2023, ~22,000 victims (real per-victim average across ALL
  case types, individual and class combined: ~$30,000/victim). Note FY2025 figure is $660M,
  FY2024 ~$700M — the number moves year to year; don't treat any single year as a fixed anchor
  without a date.
- **Individual ADA/FMLA claims** — $75K–$450K per claim (headcount-independent).
- **Wrongful termination** — $50K to several million, driven by jurisdiction and protected
  class, not defendant size.
- **SEC whistleblower awards** — $1.9B+ since 2012, largest single award $279M, no statutory
  cap. Driven by the underlying violation's sanction size, not by the reporting org's headcount
  at all.
- **DOL WHD wage-and-hour** — real current figure ~$259M FY2025 recovered nationally. Separately,
  and more importantly: **DOL stopped seeking liquidated damages in pre-litigation
  administrative settlements as of June/July 2025** (citation-audit.md, Section 1 — flagged as
  the single most consequential finding in that audit, not yet written into any PRV3 content).
  This directly affects any wage-and-hour multiplier assumption in this design — the
  traditional 2–4x liquidated-damages multiplier may no longer apply to the administrative
  settlement path, only to employee-initiated litigation, which is a structural change to the
  risk calculus, not a number update.

## Two approaches tried and rejected this session

**Rejected — single log-scale dollar curve, fixed regardless of client size.** Initial proposal:
map the Legal criterion's 0–8 raw score geometrically from a $50K floor to a $72.5M ceiling
(anchored to Beck v. Boeing), same curve applied to every client. Falsified by a plausibility
check: $72.5M against Boeing's own actual payroll (~150K employees, ~$10–11B estimated total
payroll) is under 1% of payroll — not catastrophic for the company it actually happened to.
Using it as a fixed ceiling for a 25-person client produces a meaningless 2,000%+-of-payroll
figure, because a small client could never generate a 29,000-person class in the first place.
This is the same category error as the earlier McKinsey-Fortune-500 mistake (memory-worthy:
caught twice in one session, once by Pete on the decision-quality leg, once here) — an
enterprise-scale absolute figure doesn't transfer to a differently-scaled client just because
it's expressed as a percentage.

**Rejected — simple per-capita (rate × client's full headcount).** Refinement: instead of a
fixed ceiling, derive a per-claimant rate from Beck v. Boeing ($72.5M ÷ 29,000 ≈ $2,500/
claimant) and multiply by the client's own headcount. Better, but still wrong on two counts:
(1) Beck's class was a specific affected subgroup (female employees at specific facilities),
not Boeing's whole workforce — using a client's full headcount as the base overstates exposure
for any condition narrower than "affects everyone." (2) One rate cannot honestly cover every
legal mechanism in the taxonomy — see next section.

## Current direction: mechanism-aware treatment, not one curve

The corrected E2 table maps distinct legal mechanisms to different taxonomy states (Title VII
disparate impact, FLSA wage-and-hour, retaliation, ADA/FMLA, wrongful termination,
whistleblower/Dodd-Frank-SOX). These don't share economics and probably need at least three
different calculation shapes:

1. **Individual/isolated claim exposure** — fixed dollar floor, genuinely headcount-independent.
   $50K–$450K range, sourced from ADA/FMLA/individual wrongful-termination figures above. This
   part of the original design holds up and doesn't need to change.

2. **Class/systemic discrimination-type exposure** — per-capita, but scoped to the *plausibly
   affected subgroup* for that specific condition (e.g. a gender-discrimination-shaped state
   scopes to roughly half the workforce; a facility-specific state scopes to that facility's
   headcount), not the client's total headcount. Per-claimant rate: ~$2,500 (Beck v. Boeing) —
   **single data point, needs a second verified class-action rate before this is trustworthy.**
   EEOC's blended $30,000/victim average is much higher but mixes individual and class
   resolutions, so it isn't a clean substitute rate on its own.

3. **Wage-and-hour exposure** — scales by back-wages-owed × a liquidated-damages multiplier,
   which is a different unit (hours/dollars underpaid) than headcount-based per-capita. The
   multiplier itself is now unsettled given DOL's 2025 policy change above — needs its own
   resolution, not just a number.

4. **Whistleblower/regulatory exposure** — explicitly NOT headcount-scaled. Driven by the
   underlying violation's sanction size; a 40-person company with a real SEC-triggering
   violation faces the same order of magnitude as a much larger company. E2 flags this as the
   single most extreme financial-consequence narrative in the taxonomy for exactly this reason
   — headcount offers no protection here. Needs its own uncapped treatment, likely closer to
   "if present, flag at real-world severity" than any scaled formula.

**Expanded to 5 clusters this session** -- a distinct Safety/regulatory cluster (per-incident,
OSHA-penalty-driven) was split out from the 4 buckets above once real states were classified
against them. See the Addendum below for the complete 5-cluster classification and sourced
dollar curves.

## Open questions, unresolved

1. **Does each Legal-criterion taxonomy state need to be classified by mechanism type** (which
   of the four buckets above it belongs to) before this design can be implemented? This is real
   classification work across however many of the 57 states carry a nonzero Legal score — not
   yet scoped, not started. **RESOLVED this session -- see Addendum below: all 30 states
   classified across 5 clusters (the original 4 buckets plus a newly split-out Safety/
   regulatory cluster).**
2. **Does the state's existing Legal sub-score select the mechanism, or set severity within an
   already-implied mechanism?** Raised earlier this session, still open.
3. **Probability-weighted (expected-value) framing vs. deterministic (if-present, here's the
   range)?** Raised earlier, still open. Probability-weighting is more actuarially honest but a
   meaningfully bigger build.
4. **Client-facing prominence** — separate output line with its own visual weight, or clearly
   subordinated relative to the main Friction Tax figure so it doesn't read as "your total
   cost"? Still open; likely a P-10/copy-register question more than a math one once the
   underlying numbers are settled.
5. **A second verified per-claimant or per-mechanism rate** is needed before the $2,500 Beck
   figure is treated as anything more than a single illustrative data point. **Partially
   addressed this session (see Addendum): Clusters 4 and 5 now have sourced floors/ceilings.
   Cluster 2's per-claimant range still rests on exactly two verified data points (Beck v.
   Boeing, Velez v. Novartis) -- a third would strengthen it, per the Addendum's own "Still
   open" list.**

## Addendum — Mechanism Classification & Cluster Dollar Curves

**Status:** Completes the "open questions" left in the original methodology doc. All 30
Legal-scoring states are now classified into five mechanism clusters, and four of five
clusters have sourced dollar curves. Ready for Gemini architecture review. Not yet
implemented.

### The classification standard

Applied to every state with ambiguous or absent mechanism language:

1. **Modal first.** If a state's rationale names a specific legal mechanism as its typical
   case, that mechanism governs.
2. **If the modal case is silent on mechanism** (generic language like "secondary,
   contingent," "depending on"), the edge case named in the rationale sets the cluster.
3. **If the modal case explicitly names itself as non-legal** (cultural, reputational,
   procedural) rather than merely being silent, that is a stronger signal than simple
   silence — but the edge case still sets the cluster if one is named, since a state that
   affirmatively describes its typical case as non-legal but names a real legal edge case
   (e.g. `the_untouchable`: modal is cultural exemption, edge case is harassment/safety/
   fraud) is still carrying real, if infrequent, legal exposure that the design needs to
   price.
4. Where neither modal nor edge case names a mechanism, and no closer structural analogy to
   an already-classified state exists, the state's specific facts (known to Pete, not always
   recoverable from the taxonomy text alone) resolve it.

Two categories of "unclear" turned out to need different handling: states whose text was
simply silent on mechanism resolved via rule 2 or Pete's direct judgment; no state in this
pass needed the original "no dollar figure" fallback — every one of the 30 resolved to a
cluster once the standard was applied rigorously.

### Complete classification — all 30 states

**Cluster 1 — Individual/isolated claim** (headcount-independent, $50K–$450K, sourced from
ADA/FMLA/individual wrongful-termination figures in the parent methodology doc):
`invisible_performance_management`, `the_paper_tiger`, `built_to_fail`

**Cluster 2 — Class/systemic discrimination** (per-capita, scoped to the plausibly affected
subgroup — not full headcount — using a $2,500–$31,000/claimant range; wide range reflects
two real, verified anchors an order of magnitude apart — Beck v. Boeing ~$2,500/claimant,
compensatory-only, vs. Velez v. Novartis ~$28,000–$31,000/claimant, includes a punitive
component — with the state's own severity score determining where in that range a given
case lands, not a flat constant):
`disparate_impact_architecture`, `the_arbitrary_standard`, `the_pay_fog`, `pay_exposure`,
`the_diversity_ceiling`, `the_inside_track`, `the_unexamined_algorithm`,
`sequential_decision_blindness`, `the_tolerated_violation`, `the_untouchable`,
`the_wrong_reward`, `distributed_culture_fragmentation`

**Cluster 3 — Wage-and-hour** (back-wages owed × liquidated-damages multiplier; multiplier
applies only to the litigation path, NOT the pre-litigation administrative path, per DOL's
mid-2025 policy change already written into experiment-2's content):
`cultural_overtime`, `compression_crisis`

**Cluster 4 — Whistleblower/regulatory** (uncapped high end, sanction-driven, NOT
headcount-scaled; floor now sourced — see below):
`hr_capture`, `heard_and_ignored`, `the_policy_lag`, `the_basement_standard`,
`dueling_narratives`, `the_suppression_filter`

**Cluster 5 — Safety/regulatory** (per-incident; scope is broader than originally proposed —
covers states whose worst-case realization is a safety incident, not only states with
safety-specific modal language; floor and ceiling now sourced — see below):
`the_unreported_hazard`, `the_unlocked_door`, `invisible_burnout`, `the_undefined_role`,
`the_unsolved_problem`, `groundhog_day`, `the_exposed`

### Sourced dollar curves — Clusters 4 and 5 (new this session)

**Cluster 5 (Safety/regulatory) — real, primary-sourced, OSHA's own current penalty
schedule (osha.gov, current through 2026):**
- Floor: $16,550 (single serious/other-than-serious violation)
- Mid: $165,514 (single willful/repeat violation; statutory minimum for willful is $11,823)
- Ceiling: $500K+ (real aggregate example: a repeat willful lockout/tagout citation across
  multiple pieces of equipment). This track covers regulatory penalty exposure only — it
  does NOT attempt to cover injury or wrongful-death litigation following a safety incident,
  which is a separate, larger, and unaddressed exposure track.

**Cluster 4 (Whistleblower/regulatory) — floor newly sourced, ceiling already established:**
- Floor: ~$25,000, computed directly from EEOC's own published National Mediation Program
  data (eeoc.gov) — total monetary benefits ÷ successful resolutions, consistently
  $25,000–$28,500/resolution across FY2019–FY2024. This is the right floor conceptually,
  not just numerically: EEOC mediation is the actual voluntary, pre-litigation, lowest-
  severity resolution path, so it represents what these institutional-failure states look
  like if they surface as a real charge and get resolved informally, before escalating
  toward the whistleblower/SEC end of the range.
- Ceiling: unchanged, uncapped, sanction-driven (SEC whistleblower awards $1.9B+ since 2012,
  largest single award $279M — already sourced in the parent methodology doc).

### Genuine research gap, explicitly flagged, not resolved

Cluster 4's floor search surfaced a structural limitation worth stating plainly: **minimal-
severity cases in this space are, by definition, the cases where nothing escalated — no
lawsuit, no settlement, no public record.** Vendor/HR-consulting marketing content was the
only thing findable at that resolution, and it doesn't meet this project's evidentiary
standard (already established: industry-marketing content citing unnamed studies is
excluded). The EEOC mediation figure above is a legitimate primary-sourced substitute, but
it's an adjacent proxy (a real government program's actual average), not a direct measurement
of "the floor of institutional-failure-type regulatory risk" — worth remembering if this
figure is ever challenged.

### Still open

- Cluster 2's per-claimant range ($2,500–$31,000) rests on exactly two verified data points.
  A third would meaningfully strengthen it.
- Cluster 3's wage-and-hour multiplier needs its own resolution given the DOL policy change
  (2–4x applies to litigation only) — not yet built into a formula.
- How does a given state's existing 0–2 rubric score position it within its cluster's range
  (linear? log-scale, matching the attritional design's precedent?) — not yet decided per
  cluster.

## Structural implications (bigger than Option A)

This is a larger build than the attritional rescale: it likely means `compute_friction_tax()`
returns a separate Legal/Compliance exposure line rather than one blended low/high figure,
touching `contract.py` and `web/lib/types.ts`. Not a small addendum to the existing formula.

## Next steps, in order

1. ~~Classify which of the 57 states carry a Legal/Compliance score, and which mechanism
   bucket each represents~~ **DONE this session -- see Addendum: all 30 states classified
   across 5 mechanism clusters.**
2. Find a second verified class-action per-claimant rate to test the $2,500 figure against
   (Cluster 2 specifically -- Clusters 4 and 5 now have sourced floors/ceilings per the
   Addendum; still open for Cluster 2).
3. Resolve the wage-and-hour multiplier question in light of DOL's 2025 liquidated-damages
   policy change (Cluster 3, per the Addendum -- not yet built into a formula).
4. Resolve the four open questions above (mechanism-selection logic, probability-weighting,
   client-facing prominence, and rate verification).
5. Gemini architecture review -- classification and cluster structure now ready per the
   Addendum (all 30 states classified, 4/5 clusters' dollar curves sourced). Items 2 and 3
   above (Cluster 2's third data point, Cluster 3's multiplier formula) remain open and can be
   resolved in parallel with or before that review, per Pete's call.
6. Only after this design locks: revisit whether Option A's attritional range (5%–25%) needs
   any adjustment now that Legal/Compliance has its own separate treatment rather than being
   blended into the same rubric score.
