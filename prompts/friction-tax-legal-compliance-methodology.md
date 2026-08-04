# Friction Tax — Legal/Compliance Tail-Risk Methodology (In Progress, Not Locked)

**Status:** Design in progress. Direction has shifted several times this session as real data
falsified earlier approaches. All 30 Legal-scoring states are classified into 5 mechanism
clusters -- `the_untouchable` reclassified Cluster 2 -> Cluster 1 (Addendum 4, resolving
Gemini's review flag). Cluster 3's interpolation is locked: scope-modulated, not
path-modulated (Addendum 4). Cluster 4 fully resolved into three org_type-gated sub-tracks
(Addendum 5). All 5 clusters now have sourced dollar curves, and the cross-state aggregation
design (Addendum 3) is UNBLOCKED and ready for Gemini review. Systematic jurisdictions pass
complete for California across all 5 clusters (Addendum 6). **Cluster 5 design decision
LOCKED (Addendum 8): models both statutory maximum (worst-case ceiling) and actual average
assessed penalty (realistic expected value) as a low/high pair**, consistent with how every
other part of this design already presents a range rather than a single point estimate --
the two numbers can diverge enormously within the same state (Oregon: $16,131 statutory vs.
$604 actual average, a ~27x gap). OSHA State Plan research now 11 of 22 states touched
(Addendum 7 + Addendum 8) -- but locking the both-numbers design expanded scope rather than
closing it: only Oregon currently has both figures confirmed; the other 10 touched states
need actual-average data backfilled, on top of the ~11 states still fully unresearched.
Explicitly scoped, not assumed complete: the other 49 states outside Cluster 5's OSHA
research, the ~11 remaining fully-unresearched OSHA State Plan states, and the actual-average
backfill for the 10 already-touched states, have NOT been completed -- flagged in the design
as known-incomplete jurisdictional treatment, not silently treated as accurate everywhere
outside what's actually been researched. NOT yet implemented. Does not supersede the Option A
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

## Addendum 2 — Cluster 2 Two-Tier Restructure, Cluster 3 Sourced Formula, DOL Multiplier Correction

**Status:** Closes the two remaining gaps flagged in Addendum 1. All five clusters now have
sourced dollar curves. Also documents a correction needed to already-committed content
(experiment-2-employment-litigation-taxonomy.html's DOL multiplier). Ready for Gemini review.

### Correction required to already-committed content

The DOL wage-and-hour mechanism-caveat fix committed earlier this session (4 spots in
experiment-2-employment-litigation-taxonomy.html) states liquidated damages as "2-4x back
wages" for the litigation path. This was not independently verified when written and is
incorrect. Confirmed via multiple independent legal sources this session: **the federal FLSA
liquidated-damages standard is a flat 2x — back wages plus an equal amount ("double
damages")**. There is no federal 3x or 4x tier. A small number of states (Massachusetts
confirmed) separately permit treble (3x) damages under state wage law — a distinct legal
avenue, not an extension of the federal multiplier. All 4 spots need "2-4x" corrected to "2x
(federal); some states separately permit treble damages under state law."

### Cluster 2 — restructured as two tiers, not one range

A third verified data point (Jock v. Sterling Jewelers: $175M total, $125M to the class,
~68,000 class members, well-corroborated across plaintiff counsel's own release, Signet's SEC
filings, and independent trade press) changed the shape of the evidence, not just its
precision. Per-claimant: $125M / 68,000 ≈ $1,838. That lands close to Beck v. Boeing's
~$2,500/claimant — and far from Velez v. Novartis's ~$28,000-31,000/claimant. Two convergent
points plus one outlier is evidence of two distinct populations, not one wide range:

- **Tier 2a — Compensatory-only:** ~$1,800-2,500/claimant (Beck v. Boeing, Jock v. Sterling
  Jewelers — both real, verified, no punitive component)
- **Tier 2b — Punitive-inclusive:** ~$25,000-31,000/claimant (Velez v. Novartis — real,
  verified, includes a punitive damages component)

**Tier selection:** proposed to follow the state's existing 0-2 Legal rubric score — score=1
states in cluster 2 default to Tier 2a, score=2 states default to Tier 2b. This isn't
independently evidenced (no data connects rubric score to punitive-vs-compensatory outcome
directly) but is a reasonable design choice: score=2 states in this cluster (e.g.
`disparate_impact_architecture`, `the_arbitrary_standard`) already carry language describing
clearer, more provable patterns — closer to what actually draws punitive exposure in real
cases — while score=1 states (e.g. `pay_exposure`, `the_inside_track`) are explicitly framed
as contingent/secondary. Flagging this mapping as a design choice, not a sourced finding, so
it's not mistaken for verified evidence later.

Per-capita base (either tier) still applies to the plausibly affected subgroup for that
condition, not full headcount, per Addendum 1.

### Cluster 3 — now fully sourced

Using the corrected FLSA multiplier above and the DOL WHD average already sourced earlier this
session (citation-audit.md: $259M recovered / ~177,000 workers FY2025 = ~$1,465/worker average
back wages):

- **Administrative path (1x, no liquidated damages per DOL's June 2025 policy change):**
  affected_workers x $1,465
- **Litigation path (2x, federal liquidated damages):** affected_workers x $2,930

Scoped to the affected subgroup (hourly/non-exempt staff specifically), same per-capita logic
as cluster 2. Both paths should probably be presented as a low/high pair (administrative floor,
litigation ceiling) rather than picking one, since a client doesn't know in advance which path
a real dispute would take — consistent with how the rest of the instrument already presents
low/high rather than a single point estimate.

### Status: all five clusters sourced

1. Individual/isolated claim — $50K-$450K (parent doc)
2. Class/systemic discrimination — two-tier, $1,800-2,500 (compensatory) / $25,000-31,000
   (punitive), per-capita on affected subgroup
3. Wage-and-hour — $1,465/worker (administrative) to $2,930/worker (litigation), per-capita
   on affected subgroup
4. Whistleblower/regulatory — $25,000 floor (EEOC mediation average) to uncapped (SEC
   whistleblower awards, $1.9B+ since 2012)
5. Safety/regulatory — $16,550 (serious violation) to $165,514 (willful) to $500K+
   (aggregate multi-violation), per-incident

### Still open

- Cluster 2 tier-selection logic (rubric score — tier) is a design choice, not evidenced —
  worth Gemini's and/or Pete's explicit sign-off as a judgment call, not treated as settled
  by data.
- How each cluster's dollar curve responds to the state's 0-2 rubric score within a tier
  (linear vs. log-scale, matching the attritional design's precedent) — not yet decided for
  any cluster.
- Cluster 3's "affected subgroup" definition (hourly/non-exempt staff) needs to be confirmed
  as computable from data PRV3 actually collects, not just conceptually correct.

## Addendum 3 — Cross-State Legal/Compliance Aggregation

**Status:** Proposed design. Addresses a gap Gemini's architecture review surfaced that no
prior document in this series addressed: dollar curves were designed per individual state,
but nothing specified how multiple simultaneously-identified Legal-scoring states combine.
Depends on the within-cluster score-to-dollar interpolation formulas (see Addendum 2's
"still open" list and Gemini's review) being finalized, especially Cluster 3's unresolved
disagreement (path-uncertainty pair vs. rubric-score mapping) — this doc specifies the
aggregation shape, not final numbers, and cannot fully lock until that resolves. NOT yet
reviewed by Gemini. NOT implemented.

### The problem

A real client profile can identify multiple Legal-scoring states at once — plausibly, states
spanning different clusters (e.g. `hr_capture` in Cluster 4 alongside `the_unreported_hazard`
in Cluster 5). Nothing in the parent doc or either addendum specifies whether the output sums
every identified state's dollar range independently, which risks the same category of error
already caught and fixed once this session on the attritional side (unbounded compounding
producing an implausible aggregate).

### Core distinction: within-cluster and across-cluster need different treatment

This isn't an arbitrary design choice — it follows from what the clusters actually represent
legally.

**Within a cluster**, multiple identified states usually reflect the same underlying legal
theory, with multiple states serving as multiple pieces of evidence for one broader claim. Two
Cluster 2 states (e.g. `disparate_impact_architecture` and `the_pay_fog`) aren't two separate
discrimination lawsuits — in practice, multiple discriminatory patterns strengthen one
pattern-or-practice case. The org faces a more provable, probably more severe version of ONE
exposure, not two independent ones.

**Across clusters**, this reasoning doesn't hold. A Cluster 2 discrimination exposure and a
Cluster 5 OSHA safety exposure are different bodies of law, different enforcing agencies,
different plaintiffs, different courts. There's no legal-theory basis for these to merge —
real organizations face both as genuinely separate, cumulative liabilities.

### Proposed structure

**Within-cluster: geometric decay, reusing the attritional design's Step 1 math exactly.**
Primary (highest-dollar) state in a cluster contributes at full weight; each additional
same-cluster state contributes at decaying weight, w_i = 0.5^(i-1). No new math — this is the
same shape already locked and implemented for Factor A on the attritional side, applied to a
different input (per-cluster dollar position instead of per-criterion raw score).

**Across-cluster: simple addition. No breadth premium, deliberately, unlike the attritional
design's Factor B.** This is a real departure from the attritional precedent and needs to be
justified explicitly rather than assumed to carry over:

The attritional side's multi_channel_severity_loading (K=0.05) exists because breadth across
criteria measures something beyond any individual criterion's depth — systemic organizational
coupling, fragility from multiple systems failing simultaneously. Legal/Compliance clusters
don't have an equivalent "extra" story: if an org faces a discrimination claim AND a safety
violation, the real-world cost genuinely is close to the sum of both, because they are
literally separate cases with separate remedies, not one entangled condition.

A weaker counter-argument exists — facing many different kinds of legal exposure could signal
broader compliance dysfunction and raise the probability that any single exposure actually
gets litigated — but that's a probability-of-litigation argument, and this entire Legal/
Compliance design has stayed deterministic (if-present, here's the exposure range) rather than
probability-weighted, consistent with open question #3 in the parent doc never having been
resolved toward probability-weighting. Simple addition across clusters is the version
consistent with everything else already built. If the design ever moves toward probability-
weighting, this decision should be revisited alongside that larger change, not patched in
isolation.

**Continuity requirement, same shape as the attritional N=1 guard:** if exactly one Legal-
scoring state is identified across the entire profile, output must collapse exactly to that
state's own individual dollar range from its cluster's curve — no aggregation logic engaged,
regardless of how many clusters a single state's own description might touch.

### Why this can't fully lock yet

Within-cluster decay requires each identified state to have an actual dollar *position* within
its cluster to decay-weight against other same-cluster states. That position depends on the
score-to-dollar interpolation formula for that cluster, which is not yet finalized — Gemini's
review proposed logarithmic interpolation for Clusters 1, 4, and 5, linear-within-tier for
Cluster 2, and a binary step function for Cluster 3 that conflicts with Addendum 2's
path-uncertainty design for that cluster. Cluster 3's resolution specifically changes what
there even is to decay-weight for states in that cluster (a fixed point per score, vs. a
low/high pair regardless of score) — this aggregation design should not be treated as final
until that's resolved.

### Open questions

1. Does simple across-cluster addition hold once real worked-dollar examples are run against
   it (the same plausibility-check standard applied to every other part of this design), or
   does summing a Cluster 2 range and a Cluster 5 range produce something that needs its own
   sanity check the way the original attritional ceiling did?
2. Should the within-cluster decay weight (0.5^(i-1)) be reused as-is from the attritional
   design, or does Legal/Compliance's evidence-strengthening logic (more states = more
   provable, not just more severe) argue for a different decay rate specific to this context?
3. Once Cluster 3's interpolation resolves, revisit whether its within-cluster aggregation
   needs different treatment than the other four clusters, given its output shape may differ
   fundamentally (a range vs. a point) depending on how that disagreement resolves.

## Addendum 4 — Cluster 3 Synthesis Locked, the_untouchable Reclassified, Addendum 3 Unblocked

**Status:** Resolves both open items from Gemini's review. Cluster 3 and the classification
are now final. Addendum 3's cross-state aggregation design is unblocked and ready for its own
Gemini review, alongside a fresh review of the two resolutions below.

### Cluster 3 — locked: scope-modulated, not path-modulated

Resolves the disagreement between Addendum 2 (administrative/litigation presented as a fixed
low/high pair) and Gemini's review (binary step keyed to rubric score). Neither wins outright
— the rubric score doesn't belong on the path-uncertainty axis at all, because path
(administrative vs. litigation) and severity are independent real-world variables: a minor
violation can still end up in litigation, a severe one can still resolve administratively. The
taxonomy data doesn't support predicting legal strategy from severity.

**Locked design:** the administrative ($1,465/worker) to litigation ($2,930/worker) multiplier
range stays fixed, presented together regardless of score — the genuine uncertainty Addendum 2
originally captured is preserved unchanged. The rubric score instead modulates the affected-
worker-count / scope, using the same per-capita-on-plausibly-affected-subgroup logic Cluster 2
already uses. A score=1 state implies a narrower, more contained exposure (fewer roles, one
team); a score=2 state implies broader exposure across more of the hourly/non-exempt
workforce.

**Structural consequence:** Cluster 3 no longer needs a bespoke interpolation rule. It inherits
Cluster 2's existing per-capita mechanism, just with Cluster 3's own dollar rate substituted
in. One fewer special case in the overall design, not one more.

### the_untouchable — reclassified from Cluster 2 to Cluster 1

Gemini's catch stands: the state's own modal case is explicitly non-legal (cultural
exemption), and its edge case — harassment, safety, or fraud committed by one exempted
individual — is shaped like an individual claim (one perpetrator, one or a small number of
victims at a time), not a certified class action. Cluster 2's per-capita/class mechanism
doesn't fit; Cluster 1's individual-claim floor ($50K–$450K) does. Moved.

### Addendum 3 status: unblocked

With Cluster 3's interpolation resolved and now reusing Cluster 2's existing per-capita
mechanism (not a novel step function), Addendum 3's within-cluster geometric-decay design
applies uniformly across all five clusters without a carved-out exception for Cluster 3. The
cross-state aggregation proposal is ready for its own Gemini review as originally scoped.

### Updated full classification (supersedes Addendum 1's table for this one state)

**Cluster 1 — Individual/isolated claim (4 states, was 3):**
`invisible_performance_management`, `the_paper_tiger`, `built_to_fail`, `the_untouchable`

**Cluster 2 — Class/systemic discrimination (11 states, was 12):**
`disparate_impact_architecture`, `the_arbitrary_standard`, `the_pay_fog`, `pay_exposure`,
`the_diversity_ceiling`, `the_inside_track`, `the_unexamined_algorithm`,
`sequential_decision_blindness`, `the_tolerated_violation`, `the_wrong_reward`,
`distributed_culture_fragmentation`

All other cluster memberships (3, 4, 5) unchanged from Addendum 1.

## Addendum 5 — Cluster 4 Resolved: Three Sub-Tracks Replace the Single Uncapped Curve

**Status:** Closes Cluster 4. This is a genuine reframe, not a patch — the original "uncapped,
sanction-driven" design only ever accurately described one org_type's reality (publicly
traded companies subject to SEC jurisdiction). Applying the Demographic Applicability Filter
(prompts/demographic-applicability-filter-protocol.md) surfaced that most of PRV3's actual
clients need a fundamentally different, capped, statute-grounded curve instead. Ready for
Gemini review alongside the rest of the Legal/Compliance package.

### Why the original single curve was wrong, restated precisely

Cluster 4's ceiling was anchored to SEC whistleblower award data (up to $279M single award,
$1.9B+ since 2012). That data is real and correctly sourced — but the SEC only has
jurisdiction over public companies, investment advisers, and broker-dealers. For the org_type
values that cover most of PRV3's actual client base (`Founder-led`, `PE or VC-backed` in most
cases, `Privately held professional leadership`, `Nonprofit`), this mechanism doesn't exist at
all — not a magnitude error, an applicability error. A nonprofit or founder-led company was
never going to face SEC-scale exposure regardless of how severe its Cluster 4 states scored,
and the original design had no way to reflect that.

### The three sub-tracks, gated on `org_type` (engine/accumulation.py's IntakeData field)

### 4a — SEC/Dodd-Frank (org_type = "Publicly traded")

Unchanged from the original design, correctly scoped now to the org_type it actually
describes:
- Floor: ~$25,000 (EEOC National Mediation Program average, sourced Addendum 1)
- Ceiling: uncapped, sanction-driven — average award ~$4.95M (computed directly from SEC's own
  FY2024 data: $2.2B / 444 whistleblowers since 2011), average total organizational sanction
  ~$16.5M-$49.5M (award represents only 10-30% of total sanctions collected, per SEC's own
  stated award-percentage rule), historic outlier ceiling $279M (largest single award, 2023).

**Edge case, not fully resolved:** `org_type = "PE or VC-backed"` may belong here if the
company itself (or its ownership structure) is a registered investment adviser or
broker-dealer — not determinable from `org_type` alone, would need cross-referencing
`industry = "Financial Services"`. Flagged, not built, pending further scoping.

### 4b — General private-sector retaliation (org_type = "Founder-led", "Privately held
professional leadership", "Nonprofit", and "PE or VC-backed" outside the 4a edge case)

Replaces the SEC anchor entirely with a real federal statute: 42 U.S.C. Sec 1981a(b)(3), the
Title VII/ADA compensatory-and-punitive damages cap, verified identically across seven
independent legal sources with zero discrepancy. Maps directly onto PRV3's existing headcount
buckets:

| PRV3 headcount bucket | Statutory cap |
|---|---|
| Under 25 | $50,000 (see coverage-threshold caveat below) |
| 25-99 | $50,000 |
| 100-249 | $50,000-$100,000 (bucket straddles the 100-employee statutory line) |
| 250-499 | $200,000 |
| 500-999 | $300,000 |
| 1000+ | $300,000 |

Floor: $25,000 (EEOC mediation average, same as 4a — the pre-litigation resolution path is
the same regardless of org_type).

**Two caveats built into this track, not glossed over:**
- The statutory cap covers compensatory and punitive damages only — excludes back pay, front
  pay, and attorneys' fees, which stack on top and can be substantial (attorneys' fees alone
  can exceed $100,000 in a contested case, per sourced legal commentary).
- **California's FEHA imposes no statutory cap at all.** A client with CA in `jurisdictions`
  faces genuinely uncapped exposure at the state level regardless of the federal Title VII
  figure. This is the first concrete instance of `jurisdictions` overriding a headcount-based
  cap — worth treating as a live example when the systematic filter pass runs across the
  other four clusters, since state-law overrides may exist elsewhere and haven't been checked.

**Coverage-threshold caveat:** Title VII/ADA apply at 15+ employees (ADA) and generally 15+
(Title VII). The "Under 25" bucket may include employers below this threshold who aren't
covered by this track at all — mirrors the same threshold issue flagged for Clusters 1 and 2,
not yet resolved, part of the systematic pass.

### 4c — Government (org_type = "Government")

**No dollar figure — genuinely thin data, not a research shortfall.** The federal Whistleblower
Protection Act runs through the MSPB, and a specialized legal source states directly: "there
is no published average MSPB settlement amount." The underlying data explains why: only 6 of
118 whistleblower-reprisal cases were found to have merit in FY2025 (~5%), and only 14-20% of
appeals even reach settlement. This mechanism doesn't produce the kind of data the other four
tracks do. Handled the same way the earlier "genuinely unclassifiable" states were handled
before Pete's manual sort resolved them: flagged qualitatively (mechanism named, statute
cited, no dollar range implied), rather than forcing a number onto data that doesn't support
one.

### What this means for cross-state aggregation (Addendum 3)

Addendum 3's within-cluster decay logic needs a per-state dollar position to decay-weight.
Cluster 4 states now need to know which sub-track applies (via the client's own org_type)
before that position exists — this wasn't a consideration when Addendum 3 was written, since
Cluster 4 was still a single curve at that point. Addendum 3 doesn't need structural changes,
but implementation needs to resolve org_type-gating before within-cluster decay can run for
any Cluster 4 state.

### Immediate next step

The Demographic Applicability Filter is being run systematically across the remaining four
clusters next, starting from two live leads already surfaced: a headcount coverage-threshold
issue likely affecting Clusters 1 and 2 (ADA at 15+, FMLA at 50+ employees), and the
`is_high_hazard` property already live in `engine/accumulation.py` (checking `industry`
against `HIGH_HAZARD_INDUSTRIES`) that Cluster 5 should probably hook into rather than
remaining industry-blind.

## Addendum 6 — Systematic Jurisdictions Pass: California Confirmed as a Cross-Cluster Outlier

**Status:** Applies the Demographic Applicability Filter's `jurisdictions` field systematically
across all five clusters, following the pattern first found in Cluster 4 (FEHA's uncapped
damages) and confirmed a second time in Cluster 3 (PAGA). California is now confirmed as a
material outlier in all five clusters, not two. NOT yet reviewed by Gemini. NOT implemented.
Deliberately scoped to California only -- see "Explicitly out of scope" below.

### Why California specifically, and why this matters beyond one state

`jurisdictions` (a list of state abbreviations) is collected at intake but nothing built this
session has used it to modify any cluster's dollar curve. California is the first jurisdiction
checked because it kept surfacing unprompted across unrelated research (FEHA in Cluster 4's
work, then independently again investigating Cluster 3). That's a real signal, not
coincidence -- California consistently legislates stronger worker protections than federal
baseline across nearly every area of employment law. Whether this generalizes to a smaller
number of other high-protection states (NY, MA, IL, WA are common candidates in employment law
commentary) is unverified this session -- flagged as scope, not assumed.

### Findings by cluster, all sourced this session

**Cluster 1 (Individual/isolated claim):** FEHA lowers the coverage threshold from federal
Title VII/ADA's 15 employees to 5 -- and to ANY size for harassment specifically. This closes
part of the coverage-threshold gap flagged in the earlier Clusters 1/2 pass: a California
client in the "Under 25" bucket that federal law might not cover at all is very likely covered
under FEHA regardless of exact headcount. FEHA also applies no damages cap, relevant to
wrongful-termination-type claims within this cluster.

**Cluster 2 (Class/systemic discrimination):** FEHA's uncapped damages already indirectly
reflected in this cluster's real-settlement-based per-claimant rates (Boeing, Sterling,
Novartis all likely include state-law claims stacked into their real outcomes) -- flagged as
already-captured, not a new gap requiring a fix, unlike the other four clusters below.

**Cluster 3 (Wage-and-hour):** California's PAGA adds $100-200 per aggrieved employee, PER PAY
PERIOD -- a fundamentally different shape of exposure than the federal FLSA's flat 2x
multiplier. Stacks on top of back wages and federal liquidated damages, compounds with time.
Worked example: 50 employees, 26 pay periods/year, base tier = $130,000/year in PAGA penalties
alone, before back wages. Confirmed via statute and multiple consistent legal sources.

**Cluster 4 (Whistleblower/regulatory):** Already resolved in Addendum 5's 4b caveat -- FEHA's
uncapped damages apply to CA clients in the general private-sector retaliation track regardless
of the federal statutory cap table.

**Cluster 5 (Safety/regulatory):** Cal/OSHA's serious-violation cap is $25,000 vs. federal
OSHA's $16,550 -- about 51% higher. Willful/repeat is close to parity ($162,851 vs. $165,514).
Confirmed directly from California's Department of Industrial Relations press releases.

### The bigger finding: this isn't just a California problem

**22 states operate their own OSHA-approved State Plans**, required by federal law to be "at
least as effective" as federal OSHA -- meaning equal or higher penalties, never lower.
Cluster 5's flat federal figures are confirmed as a floor across roughly 22 states' worth of
clients, not an accurate number nationally. This is a materially bigger gap than the
California-specific findings above, and it's currently completely unaddressed in the design.

### Explicitly out of scope for this pass

Pulling all 22 OSHA State Plan states' actual penalty schedules, and checking whether other
high-protection states (NY, MA, IL, WA, etc.) have FEHA/PAGA-equivalent statutes in the other
four clusters, is real, substantial research this session did not do. California was checked
because it kept surfacing organically, not because it's confirmed as the only or the most
extreme outlier. Treating California as "the" jurisdictional exception rather than "a"
jurisdictional exception risks the same category error already caught twice this session
(McKinsey's F500 data, Beck v. Boeing's ceiling) -- a real, verified finding that doesn't
generalize as far as it might look like it does.

### Proposed treatment given this scope limit

Build California as a confirmed, sourced exception across all applicable clusters now (real
findings, ready to implement), while explicitly flagging in the design that this is a known-
incomplete jurisdictional treatment -- not "California and defaults everywhere else are
accurate," but "California is verified, everywhere else uses federal baseline and has NOT been
checked for its own state-level exceptions." Recommend this distinction be visible in the
architecture itself (e.g. a documented TODO or explicit confidence flag), not just in this doc,
so a future session doesn't mistake "we checked California" for "we checked all 50 states."

### Open questions

1. Should the design proactively flag other likely-high-protection states (NY, MA, IL, WA) as
   priority candidates for the same research pass, or wait until a specific client's
   jurisdiction surfaces a gap organically the way California did?
2. For Cluster 5 specifically: is a full 22-state OSHA State Plan research pass worth doing
   before implementation, given it's confirmed as a real, non-trivial national accuracy gap --
   or does California's confirmed example plus an honest "federal baseline, not state-verified"
   flag suffice for a first implementation?

## Addendum 7 — OSHA State Plan Research, 7 of 22 States (In Progress)

**Status:** Durable record of state-by-state jurisdictional research into Cluster 5's OSHA
State Plan variation, continuing from Addendum 6's California findings. 7 of 22
full private-sector State Plans researched with primary-source rigor. NOT complete -- 15
states remain. NOT yet reviewed by Gemini. Written now per the standing durable-write
protocol given the volume and structural significance of findings so far.

### The full 22-state list (confirmed, primary-sourced: osha.gov)

Alaska, Arizona, California, Hawaii, Indiana, Iowa, Kentucky, Maryland, Michigan, Minnesota,
Nevada, New Mexico, North Carolina, Oregon, Puerto Rico, South Carolina, Tennessee, Utah,
Vermont, Virginia, Washington, Wyoming.

**Researched (7):** California, Washington, Oregon, Alaska, Hawaii, Arizona, Indiana.
**Remaining (15):** Iowa, Kentucky, Maryland, Michigan, Minnesota, Nevada, New Mexico, North
Carolina, Puerto Rico, South Carolina, Tennessee, Utah, Vermont, Virginia, Wyoming.

### Key finding: variation from federal baseline is genuinely bidirectional, not just upward

The original hypothesis (a few states exceed federal, most match) undersold the real
complexity found once actually checked. Five distinct patterns confirmed across 7 states
(originally reported as six in this addendum's first pass -- Washington's finding was
corrected this session and folded into the existing clean-parity pattern below, not left as
its own separate category; see the CORRECTION note under Washington):

**Exceeds federal, flat higher cap:**
- **California (Cal/OSHA):** Serious violation cap $25,000 vs. federal $16,550 (~51% higher).
  Willful/repeat close to parity ($162,851 vs. $165,514).

**Exceeds federal, but only conditionally (outcome-triggered, not a blanket cap):**
- **Oregon:** Ordinary serious violations sit at near-parity ($16,131 vs. federal $16,550).
  Senate Bill 592 (effective May 2023) creates a separate, much higher tier triggered
  specifically by a workplace fatality: serious-with-fatality $20,000-$50,000, willful/repeat-
  with-fatality $50,000-$250,000 (vs. federal's flat $165,514 max regardless of outcome).

**Clean parity, statutorily required:**
- **Alaska:** Alaska Dept. of Labor policy directive states explicitly: "Alaska's maximum
  penalties must be the same as those for federal OSHA." Confirmed via current posting
  ($16,131, matching federal's cycle with minor timing lag).
- **Hawaii (HIOSH):** Statutorily required (Act 396, HRS) to mirror federal exactly. Confirmed
  current: $16,550 serious, $165,514 willful/repeat -- identical to federal 2025 levels.
- **Washington (WISHA):** **CORRECTION (this session) -- the original version of this addendum
  placed Washington in the "exceeds federal" category. That was incorrect, not a refinement.**
  WAC 296-900-14010 governs serious violations (maximum penalty: the maximum civil penalty
  established by federal OSHA, or $7,000, whichever is more). WAC 296-900-14020 separately
  governs willful/repeat violations (federal max, or $70,000, whichever is more) -- these are
  two different violation categories with two different statutory floors, not two competing
  figures for the same category as originally implied. Both floors currently sit BELOW
  federal's own current maximums ($16,550 serious, $165,514 willful/repeat), so Washington's
  EFFECTIVE current penalties equal federal's exactly -- Washington is at parity right now,
  not exceeding federal. The floor mechanism only matters if a future federal reduction ever
  drops federal's own maximums below $7,000/$70,000, which is not the current state of the
  world.

**Statutory parity, but documented under-enforcement (a new category, not anticipated at the
start of this research):**
- **Arizona (ADOSH):** Statutory maximums track federal via legislated requirement. However,
  Arizona's Industrial Commission is "the only state or federal OSHA program in the country"
  with an independent body that reviews and frequently reduces proposed penalties after the
  fact -- one documented case cut $18,500 to $4,750 (~74% reduction). Federal OSHA has formally
  investigated this practice as undermining deterrence and potentially exceeding the
  commission's legal authority. Effective real-world exposure likely runs below the statutory
  maximum, the opposite direction from California/Oregon. This practice is under active
  federal scrutiny as of research date -- may not be a stable long-term feature.

**Genuinely, confirmedly lower than federal (the first and only state found in this direction
so far):**
- **Indiana (IOSHA):** Current official Indiana Dept. of Labor page (in.gov/dol) confirms
  active maximums of $7,000 for serious violations -- less than half of federal's $16,550.
  Deliberate, controversial, longstanding: Indiana has resisted adopting federal's post-2016
  inflation-adjusted structure, retaining pre-2016 levels ($7,000/$70,000). Federal OSHA
  formally found Indiana out of compliance with the "at least as effective" requirement
  (Finding FY 2021-05); Indiana's response states it cannot unilaterally change penalties
  without state legislative action, which has not occurred. Note: multiple third-party
  compliance-training sites incorrectly claim Indiana "mirrors federal" at higher figures --
  contradicted directly by Indiana's own current official government source. State primary
  source resolved this conflict, consistent with citation-verification practice used
  throughout this session.

### Implication for Cluster 5's design

A single "does this state exceed federal" binary is insufficient. At minimum, three axes are
now confirmed as real and independent: (1) does the state's *statutory* maximum exceed,
match, or fall below federal, (2) is any escalation *conditional* on a specific outcome
(Oregon's fatality trigger) rather than blanket, and (3) does *effective* enforcement diverge
from the *statutory* figure (Arizona's under-enforcement pattern). A design that only checks
"jurisdiction = CA, apply a flat multiplier" would miss Oregon's conditional structure,
Arizona's enforcement gap, and Indiana's genuine downward deviation entirely. Washington's
corrected finding adds a fourth, related caution: a state's statutory mechanism (a floor tied
to federal's own maximum) can look like it should exceed federal on paper while resolving to
exact parity in practice, given federal's own current figures -- read the actual effective
number, not just the formula's structure, before classifying a state.

### Next steps

Continue state-by-state research through the remaining 15 states at the same rigor. Given the
real complexity found in 7 of 7 states checked so far (every single state researched has
produced a genuine, non-trivial, distinct finding -- none has been a simple confirmed match
requiring no further note), there is no indication the remaining 15 will be faster or simpler.

## Addendum 8 — Cluster 5 Models Both Statutory Max and Actual Average, Scope Expanded

**Status:** Locks a design decision and documents its consequence for research scope. NOT
yet reviewed by Gemini. NOT implemented. Continues the OSHA State Plan research from
Addendum 7, now 11 of 22 states touched (10 fully researched plus one bonus data point),
with a corrected Washington finding and a newly identified data gap.

### Design decision: Cluster 5 models both statutory maximum and actual average

Confirmed this session: rather than picking one, Cluster 5's low/high range should represent
statutory maximum (worst-case ceiling) and actual average assessed penalty (realistic
expected value), consistent with how every other part of this design already presents a
low/high pair rather than a single point estimate.

### Why this matters more than it might look like

These two numbers can diverge enormously within the same state. Oregon's statutory serious-
violation maximum is $16,131 (near federal parity) -- but its actual average assessed penalty
is $604, per a 2023 union petition citing OSHA's own audit findings. That's a ~27x gap between
the two figures for the identical state and violation category. Treating either number alone
as "Oregon's penalty" would be materially misleading in one direction or the other.

### Consequence: most states researched so far only have one of the two numbers

| State | Statutory max | Actual average |
|---|---|---|
| California | Confirmed: $25,000 serious (Cal/OSHA) | Not researched |
| Washington | Confirmed: parity with federal (corrected from Addendum 7's original error -- see that addendum's correction note) | Not researched |
| Oregon | Confirmed: $16,131 serious / $20K-50K and $50K-250K fatality tiers | Confirmed: $604 average |
| Alaska | Confirmed: parity, statutorily required | Not researched |
| Hawaii | Confirmed: parity, statutorily required | Not researched |
| Arizona | Confirmed: parity (statutory) | Partial -- specific case examples only (e.g. $18,500 reduced to $4,750), not a clean average figure |
| Indiana | Confirmed: $7,000 serious (materially below federal) | Not researched |
| Iowa | Confirmed: parity by legislative design (auto-tracks federal) | Not researched |
| Kentucky | Confirmed: $7,000 serious (materially below federal), HB 398 (2025) makes penalties discretionary going forward | Not researched |
| Maryland | Partial -- confirmed "not raised since 2016" but exact current statutory figure not captured | Confirmed: $862-892 average (OSHA's own FY2020 FAME report plus 2023 corroboration) |
| South Carolina | Partial -- exact current statutory figure not captured; governor unsuccessfully sued OSHA over the 2022 requirement to raise penalties | Confirmed: $2,019 average |
| Minnesota (bonus, not yet formally researched) | Confirmed near-parity as of July 2023 effective date ($15,625/$156,259, matching that year's federal levels) | Not researched |

**Only Oregon has both numbers.** Completing the "both, as a range" design means going back to
fill the average-penalty gap in the 10 other states already touched, not just continuing
forward through the remaining ~11 unresearched states (Nevada, New Mexico, North Carolina,
Puerto Rico, Tennessee, Utah, Vermont, Virginia, Wyoming, plus formally confirming Minnesota
and Michigan -- Michigan specifically needs its actual-average figure since its statutory
picture is already confirmed materially low).

### Useful primary source found this round, worth reusing

OSHA's own official adoption-tracking table (osha.gov/stateplans/adoption/standards/2016-07-01,
last updated 1/30/2023) records each state's stated intent to adopt the 2016 federal penalty
increase. Important caveat, confirmed by direct contradiction: Michigan's entry shows
"Yes/Adopt Identical: Yes" in this table, but Michigan's actual current penalties (confirmed
via Michigan's own current-year sources) remain at pre-2016 levels -- Michigan stated intent
and never followed through, and the table doesn't distinguish stated intent from verified
completion (blank "Effective Date" is the tell for entries that didn't actually complete,
versus states like Arizona with a specific completion date). This table is useful for
prioritizing which states to check first (explicit "No" or "Pending" entries are strong
signals for materially-lower states, already confirmed accurate for Indiana, Kentucky, and
Maryland) but cannot be trusted as a standalone source of current truth for any single state.

### Also worth carrying forward: an aggregate figure with real value

The same union petition source states "current state plan penalties for a serious violation
average $2,372 for all state plans put together" against a "national average of $3,259" --
a real, if secondary-sourced, aggregate comparison suggesting state-plan actual averages run
meaningfully below the broader national average as a general pattern, not just in the specific
low states already found. Worth citing as context, not as a substitute for individual state
figures.

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
