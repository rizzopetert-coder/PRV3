# Friction Tax — STATE_MULTIPLIERS Methodology (Calibration Set 3)

**Status:** Scoring complete, all 57 states populated (Calibration Set 3, commit 469b148). Combination function rescaled (Option A, below) -- Gemini-reviewed and cleared (structural check + worked dollar-figure plausibility check across mild/typical/severe scenarios, all landing in a defensible 3%-49% of payroll range), then implemented in compute_friction_tax() -- commit 8de807a (2026-08-03), MOB v4.80. (Documentation correction made in a later session -- this status line previously read "Not yet implemented," describing a step that had already happened and passed.)

## Purpose

STATE_MULTIPLIERS[state] represents a given friction state's inherent cost profile — independent of how severe the condition currently is for a specific org. Severity is handled entirely separately by the existing, locked SEVERITY_SCALAR dict (Emerging 0.6 / Entrenched 1.0 / Endemic 1.4), which multiplies the final friction tax figure downstream of this table. These two factors are deliberately kept separate and must never be combined or allowed to double-count each other:

- STATE_MULTIPLIERS[state] = "how costly is this kind of condition, inherently"
- SEVERITY_SCALAR[tier] = "how deep has this condition taken root for this org"

Confirmed via direct read of compute_friction_tax() (engine/friction_tax.py:464-546): the two scalars are applied as independent, sequential multiplications against the same adjusted_baseline, with no branching or interaction between them. This methodology preserves that separation deliberately — severity must never be folded into a state's score.

## Scoring criteria (applied per state, by Pete)

Each of the 57 states was originally scored 0-2 on each of four criteria (Calibration Set 3, closed). These are business-recognizable cost channels, chosen so a skeptical outside reader (HR leader, CFO, attorney) can evaluate the framework without needing PRV3 taxonomy vocabulary:

1. **Turnover/retention cost** — does this condition drive people out the door?
2. **Productivity/output loss** — does it degrade the work itself, even if people stay?
3. **Decision-quality/velocity cost** — does it cause bad or slow decisions?
4. **Legal/compliance exposure** — **REMOVED from this rubric's raw score (this session).** Legal/Compliance is now fully split out to its own mechanism-aware design (prompts/friction-tax-legal-compliance-methodology.md, in progress, not yet Gemini-reviewed, not yet implemented) — its economics don't scale with headcount the way the other three do, and forcing it through the same linear payroll-fraction mapping either understated it or overstated the other three. Each state's original Legal/Compliance sub-score (from the closed Calibration Set 3 pass) still exists in the underlying scoring worksheet but is no longer summed into this rubric's raw_total.

Scale per criterion: 0 = negligible, 1 = moderate, 2 = significant.

**Total raw score range: 0-6 per state (3 criteria x 0-2), not the original 0-8.** Whoever implements this must recompute each state's raw_total using only the three remaining criteria (turnover, productivity, decision_quality), dropping the original Legal/Compliance sub-score, before applying the rescaled interpolation formula below — this is a real recomputation against the existing 57-state scoring worksheet, not just a formula swap.

A one-line rationale is required per criterion score, per state, for audit-trail defensibility — not just the numeric total. (Already satisfied for all 57 states from the original Set 3 pass; no new rationale-writing needed, only the resulting raw_total recompute.)

## Resolving intra-state variance

Some states' cost profile varies by context — e.g., role level, team size, or which sub-case of the condition is present. When a criterion's score would differ depending on context, score for the TYPICAL / MODAL instance of the condition, not the worst-case or an averaged range. Edge cases are deliberately ignored in scoring, though a rationale may still note them for context.

This rule was surfaced during scoring of built_to_fail's Legal/Compliance criterion, where the initial rationale reasoned about role-level variance (leadership vs. mid-level incumbents) rather than committing to a single typical case.

## Combination function (rescaled this session — Option A)

Supersedes the original [1.0, 1.4] bare-multiplier design and its empirical observed-min/max approach. The rescale uses a **fixed theoretical raw-score range**, not an empirically observed one — this keeps the single-state formula compatible with the multi-state compounding design's frozen-range requirement (prompts/friction-tax-multistate-compounding-methodology.md, Step 2), which needs bounds fixed at design time regardless of which states happen to be identified in a given session.

**Target range: [0.05, 0.25]** (payroll fraction), replacing [1.0, 1.4] (a bare multiplier).
**Raw score range: [0, 6]** (R_min = 0, R_max = 6 — 3 criteria x 0-2 each), replacing the original [0, 8].

Formula:

  attritional_fraction(R) = 0.05 + (0.25 - 0.05) x ((R - R_min) / (R_max - R_min))
  where R_min = 0, R_max = 6

Floor and ceiling sourcing (Pete, this session):
- **Floor = 0.05 (5% of payroll)**, **ceiling = 0.25 (25% of payroll)** — sourced at roughly 5%-25% across the three criteria's evidence: productivity 14-18% (Gallup Q12 — solid), turnover ~13% typical / ~38% elevated (solid), decision-quality ~5-7% (Track B reconstruction — softer, no direct source). 25% is the negotiated ceiling across all three criteria's evidence, not any single criterion's own maximum.

**Decision-quality's softer evidentiary support does not need special-casing.** Equal 0-2 rubric weighting across all three criteria naturally bounds decision-quality's max marginal contribution to ~6.7% of payroll (one-sixth of the full [0.05, 0.25] range), which matches the reconstruction's own independently-estimated 5-7% range closely enough that no separate down-weighting is needed.

**Gemini review (this session):** structural check plus a worked dollar-figure plausibility check across mild/typical/severe scenarios, all landing in a defensible 3%-49% of payroll range. Cleared.

Sequencing note: scoring is already complete (Set 3 closed) — the original design's "defer interpolation until all 57 states are scored" caveat no longer applies. What remains is recomputing each state's raw_total (3-criteria only, per the Scoring criteria section above) and applying this formula in code.

## Explicitly out of scope for this table

- Severity — handled entirely by SEVERITY_SCALAR, never folded into a state's score.
- Multi-state averaging logic — historically a plain arithmetic mean across state_ids in compute_friction_tax(); a redesign is locked (not yet implemented) — see prompts/friction-tax-multistate-compounding-methodology.md.

## Known adjacent issue (not blocking, logged for awareness)

STATE_MULTIPLIERS.get(sid, _DEFAULT_MULTIPLIER) falls back to _DEFAULT_MULTIPLIER = 0.0 for any unrecognized state_id, silently pulling the mean toward zero rather than raising an error. Not a Set 3 scoping concern today (all 57 known states will be populated), but worth a Tier 3 Decision Register entry if the taxonomy ever expands past 57 without a corresponding STATE_MULTIPLIERS update.

## Implementation status

All four steps completed. Independently re-verified this session (2026-08-08), not restated from the header alone: engine/friction_tax.py's STATE_MULTIPLIERS dict carries 58 populated entries (the original 57 states plus the_inner_circle, added in a later session -- see note below), zero placeholder/None values, recomputed against the 3 remaining criteria (turnover, productivity, decision_quality) per item 1. _attritional_fraction() implements the exact rescaled interpolation formula from item 2 (`_FRACTION_MIN + (_FRACTION_MAX - _FRACTION_MIN) * ((raw_total - _R_MIN) / (_R_MAX - _R_MIN))`, with _R_MIN=0.0, _R_MAX=6.0, _FRACTION_MIN=0.05, _FRACTION_MAX=0.25), and its own docstring cites this document by name as the source of the frozen-range design. compute_friction_tax() treats the result as a payroll fraction throughout, per item 3. Coordination with the multi-state compounding doc (item 4) confirmed landed together in the same commit -- single-state continuity holds against the [0, 6] / [0.05, 0.25] mapping (tools/test_friction_tax.py checks 7-8, 93/93 passing). Commits confirmed accurate via git blame: 469b148 (2026-08-02, original scoring) and 8de807a (2026-08-03, rescaled implementation) -- matching this document's own header exactly, no correction needed there.

No genuinely forward-looking items remain in this section.

Note, flagged not fixed (out of this pass's scope -- this fix is scoped to the Next steps section only): this document's own "Status" line above and the "Known adjacent issue" section still say "all 57 states populated." That is stale on a different axis -- STATE_MULTIPLIERS is 58/58 as of a later session, the_inner_circle included -- worth a follow-up pass.
