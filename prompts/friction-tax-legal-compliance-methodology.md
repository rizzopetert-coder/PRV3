# Friction Tax — Legal/Compliance Tail-Risk Methodology (In Progress, Not Locked)

**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. NOT yet reviewed by Gemini, NOT yet implemented. Does not
supersede the Option A attritional-criteria rescale (turnover/productivity/decision-quality),
which proceeds independently — this doc is specifically the deferred Legal/Compliance item
that Option A explicitly excluded.

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

## Open questions, unresolved

1. **Does each Legal-criterion taxonomy state need to be classified by mechanism type** (which
   of the four buckets above it belongs to) before this design can be implemented? This is real
   classification work across however many of the 57 states carry a nonzero Legal score — not
   yet scoped, not started.
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
   figure is treated as anything more than a single illustrative data point.

## Structural implications (bigger than Option A)

This is a larger build than the attritional rescale: it likely means `compute_friction_tax()`
returns a separate Legal/Compliance exposure line rather than one blended low/high figure,
touching `contract.py` and `web/lib/types.ts`. Not a small addendum to the existing formula.

## Next steps, in order

1. Classify which of the 57 states carry a Legal/Compliance score, and which mechanism bucket
   (individual / class-discrimination / wage-hour / whistleblower) each represents — real
   research and taxonomy work, not yet started.
2. Find a second verified class-action per-claimant rate to test the $2,500 figure against.
3. Resolve the wage-and-hour multiplier question in light of DOL's 2025 liquidated-damages
   policy change.
4. Resolve the four open questions above (mechanism-selection logic, probability-weighting,
   client-facing prominence, and rate verification).
5. Gemini architecture review — not yet sent, and shouldn't be until the above is further
   resolved, since the mechanism-aware structure is still actively changing.
6. Only after this design locks: revisit whether Option A's attritional range (5%–25%) needs
   any adjustment now that Legal/Compliance has its own separate treatment rather than being
   blended into the same rubric score.
