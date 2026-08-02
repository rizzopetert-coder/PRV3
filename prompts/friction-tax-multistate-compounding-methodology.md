# Friction Tax — Multi-State Compounding Methodology (Proposed, Not Yet Implemented)

**Status:** Design proposed and confirmed with Pete this session. NOT yet reviewed by Gemini, NOT yet implemented. Do not build against this until both have happened.

## Problem being solved

compute_friction_tax()'s current multi-state combination is a plain arithmetic mean of STATE_MULTIPLIERS across identified state_ids. This is actuarially wrong: it treats multiple identified friction states as competing estimates of the same loss (averaged toward a midpoint) rather than separate, additive sources of loss. An org carrying a severe state alongside a mild one gets diluted below what the severe state alone would produce. Reframing per an actuarial review this session: risk exposures should aggregate more like a collective risk model (sum of expected loss per exposure), not average like uncertain estimates of one true value.

This design resolves three previously-parked factors together (Decision Register: "Multi-state compounding mechanism for Friction Tax" and its Factor A / Factor B addendum):
- State-count compounding (the base problem)
- Factor A: within-criterion stacking
- Factor B: breadth-across-criteria stacking

## Design: anchor-plus-diminishing-layers, built at the criterion level

Critical structural choice: aggregate from the four underlying criterion scores across all identified states directly, NOT by blending already-computed per-state multipliers. Blending pre-blended numbers loses the channel-level information Factor A needs.

### Step 1 — Per-criterion aggregation across identified states (implements Factor A)

For each of the 4 criteria (turnover, productivity, decision_quality, legal), sort identified states by their score on that criterion, descending. Apply anchor-plus-diminishing-layers:

combined_criterion_score[k] = c[1,k] + SUM(i=2 to n) of w_i * c[i,k]

Where c[1,k] is the highest score on criterion k across identified states (primary layer, full weight). Each additional state's score on that criterion contributes at decaying weight w_i.

Proposed decay: w_i = 0.5^(i-1) (geometric decay, each additional state contributes half the marginal weight of the prior one). This is structurally motivated, not arbitrary: it guarantees the aggregate stays bounded as state count grows (converges to a fixed ceiling), analogous to a capped aggregate/stop-loss structure. This bounds the output even for orgs with many identified states.

This is where within-criterion stacking happens: if multiple identified states all score high on the same criterion (e.g. several with significant Legal exposure), that criterion's combined score is genuinely higher than any single state's score, not averaged away.

### Step 2 — Map combined criterion profile to a severity multiplier

Apply the same min-max normalization logic already locked for Calibration Set 3, applied to the new combined (not per-state) criterion totals, replacing the current mean_multiplier step entirely.

Continuity requirement: with exactly one identified state, this formula MUST collapse exactly to that state's own existing STATE_MULTIPLIERS entry — zero discontinuity from current single-state behavior. This must be verified explicitly during implementation, not assumed.

### Step 3 — Frequency loading (implements Factor B), applied separately and multiplicatively

breadth = count of the 4 criteria where combined_criterion_score[k] > 0
frequency_loading = 1.0 + 0.05 * (breadth - 1)   [yields 1.00 / 1.05 / 1.10 / 1.15 for breadth 1/2/3/4]

Deliberately kept separate from and multiplicative against the severity multiplier from Step 2, not blended into it. Actuarial rationale: breadth-across-criteria represents FREQUENCY (likelihood something in this risk profile materializes at all), not SEVERITY (how bad it is if it does). Conflating frequency and severity into one number is a modeling error per standard actuarial practice (attritional risk is priced via expected value; frequency and severity are typically modeled as separate components even when combined into one final rate).

FLAGGED: the 0.05 increment is a placeholder, not a researched or structurally-derived constant (unlike the geometric decay in Step 1, which is structurally motivated). Requires Pete's judgment or further calibration before implementation, not to be treated as locked.

### Final formula

low = adjusted_baseline * combined_multiplier * frequency_loading * severity_scalar

(severity_scalar remains the existing, locked, unchanged SEVERITY_SCALAR mechanism — this design does not touch it.)

## Explicitly deferred, not part of this design

**Legal/Compliance tail-risk distinction** (separate Decision Register item, explicitly queued behind this one): Turnover, Productivity, and Decision-Quality behave as attritional risk (steady, frequency-driven, well-suited to proportional blending). Legal/Compliance behaves more like a tail/catastrophic peril (rare, severe when realized) and may not be well-modeled by the same proportional blending used here. This design does NOT attempt to resolve that distinction — Legal is scored and aggregated identically to the other three criteria in Steps 1-3 above, pending that separate, queued design conversation.

## Next steps (in order)

1. Gemini architecture review of this design (schema/formula implementation questions) — not yet sent.
2. Resolve the frequency_loading constant (0.05) — placeholder pending Pete's input or calibration.
3. CC implementation: replace compute_friction_tax()'s mean_multiplier step with combined_criterion_score aggregation per Step 1, add frequency_loading per Step 3, verify single-state continuity explicitly, update tests.
4. Only after this design is implemented: reopen the Legal/Compliance tail-risk item.
