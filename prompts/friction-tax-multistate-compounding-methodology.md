# Friction Tax — Multi-State Compounding Methodology (Implemented)

**Status:** Implemented and verified. Gemini-reviewed and cleared, then implemented in compute_friction_tax() -- commit 8de807a (2026-08-03), MOB v4.80. tools/test_friction_tax.py rewritten 37->45 checks, 45/45 passing at the time of that commit. (Documentation correction made in a later session -- this status line previously read as pending/not-yet-reviewed, describing a step that had already happened and passed.)

## Problem being solved

compute_friction_tax()'s current multi-state combination is a plain arithmetic mean of STATE_MULTIPLIERS across identified state_ids. This is actuarially wrong: it treats multiple identified friction states as competing estimates of the same loss (averaged toward a midpoint) rather than separate, additive sources of loss. An org carrying a severe state alongside a mild one gets diluted below what the severe state alone would produce. Reframing per an actuarial review this session: risk exposures should aggregate more like a collective risk model (sum of expected loss per exposure), not average like uncertain estimates of one true value.

This design resolves three previously-parked factors together (Decision Register: "Multi-state compounding mechanism for Friction Tax" and its Factor A / Factor B addendum):
- State-count compounding (the base problem)
- Factor A: within-criterion stacking
- Factor B: breadth-across-criteria stacking

## Design: anchor-plus-diminishing-layers, built at the criterion level

Critical structural choice: aggregate from the three underlying criterion scores across all identified states directly, NOT by blending already-computed per-state multipliers. Blending pre-blended numbers loses the channel-level information Factor A needs.

### Step 1 — Per-criterion aggregation across identified states (implements Factor A)

For each of the 3 criteria (turnover, productivity, decision_quality — Legal/Compliance is fully split out to its own separate design, see below, and is not part of this loop), sort identified states by their score on that criterion, descending. Apply anchor-plus-diminishing-layers:

combined_criterion_score[k] = c[1,k] + SUM(i=2 to n) of w_i * c[i,k]

Where c[1,k] is the highest score on criterion k across identified states (primary layer, full weight). Each additional state's score on that criterion contributes at decaying weight w_i.

Proposed decay: w_i = 0.5^(i-1) (geometric decay, each additional state contributes half the marginal weight of the prior one). This is structurally motivated, not arbitrary: it guarantees the aggregate stays bounded as state count grows (converges to a fixed ceiling), analogous to a capped aggregate/stop-loss structure. This bounds the output even for orgs with many identified states.

This is where within-criterion stacking happens: if multiple identified states all score high on the same criterion (e.g. several with significant Turnover exposure), that criterion's combined score is genuinely higher than any single state's score, not averaged away.

### Step 2 — Map combined criterion profile to a severity multiplier

Apply the same min-max normalization logic already locked for Calibration Set 3 (prompts/friction-tax-state-multiplier-methodology.md, rescaled this session to a [0.05, 0.25] payroll-fraction target range against a [0, 6] raw-score range), applied to the new combined (not per-state) criterion totals, replacing the current mean_multiplier step entirely.

Continuity requirement: with exactly one identified state, this formula MUST collapse exactly to that state's own existing STATE_MULTIPLIERS entry — zero discontinuity from current single-state behavior. This must be verified explicitly during implementation, not assumed, and must be re-verified against the rescaled [0, 6] / [0.05, 0.25] mapping, not the original [0, 8] / [1.0, 1.4] one.

Frozen-range requirement: the min-max normalization bounds applied to combined_criterion_score must be fixed, pre-defined constants set at design time, not derived dynamically from whichever states happen to be identified in a given session or from empirically observed data. combined_criterion_score's range is not the same as a single state's raw_score range ([0, 6] under the rescaled Calibration Set 3, not the original [0, 8] — Legal/Compliance is no longer part of this rubric's raw score) once geometric-decay aggregation across multiple states is applied, so the theoretical min/max used for interpolation here must be independently defined and locked before implementation, analogous to how Set 3's own [0, 6] to [0.05, 0.25] mapping was frozen at design time rather than computed from observed data.

Extrapolation beyond R_max: combined_criterion_score can exceed a single state's own raw-score ceiling (6) once geometric-decay aggregation stacks multiple identified states' scores on the same criterion (Step 1). When this happens, the linear formula continues to extrapolate above the 0.25 target ceiling rather than clamping at it — per the original design, this is intentional: multiple states genuinely carrying high scores on the same criterion should be able to push the resulting fraction past a single state's own maximum, not be capped at it.

### Step 3 — Multi-Channel Severity Loading (implements Factor B), applied separately and multiplicatively

breadth = count of the 3 criteria where combined_criterion_score[k] > 0
multi_channel_severity_loading = 1.0 + 0.05 * (breadth - 1)   [yields 1.00 / 1.05 / 1.10 for breadth 1/2/3]

Deliberately kept separate from and multiplicative against the severity multiplier from Step 2, not blended into it. Rationale (revised from an earlier frequency/severity framing that overstated an actuarial analogy this instrument doesn't fully earn): breadth-across-criteria measures how many distinct damage channels a diagnosed condition spans simultaneously — a dimension of systemic coupling and diversification, not the depth of harm within any single channel (which Step 2 already captures), and not classical actuarial frequency (how often a loss event recurs over time). An organization whose identified states hit all three channels at once is structurally more exposed than one with the same combined severity concentrated in a single channel, independent of either being more 'frequent' in any insurance sense. This is additive information to Step 2's depth measure, not a restatement of it: Step 2 asks how bad each affected channel is, Step 3 asks how many channels are affected at once.

Continuity requirement (N=1): when exactly one state is identified, multi_channel_severity_loading MUST equal 1.0 regardless of how many criteria that single state's own scores span. The breadth-based formula above applies only when two or more states are identified (N >= 2). Without this guard, a single identified state whose own criterion scores happen to span multiple channels (e.g. a state scoring above zero on all three criteria) would incorrectly trigger loading, breaking the exact single-state parity that Step 2's own continuity requirement establishes. This must be verified explicitly during implementation, not assumed.

CLOSED (Pete's final decision): the 0.05 increment is locked, not a placeholder. Rationale: treats the multi-area premium as a tiebreaker, not a primary cost driver — the strongest alternative considered (0.15) tops out at a 30% max swing at full breadth (recalculated this session against the corrected 3-criterion breadth range; was calculated as 45% under the original 4-criterion range before Legal/Compliance was split out), proportionate to the depth lever's 40% max swing and well under severity's ~133% max swing. K=0.05's own max swing at full breadth is correspondingly 10% (would have been 15% under the original, now-corrected 4-criterion range, though never spelled out explicitly before this correction) — even more conservative relative to the depth lever's 40% max than originally calculated, not less. **DOCUMENTATION CORRECTION ONLY (this session):** the breadth-range correction does not reopen K=0.05 itself — it remains locked, and this paragraph only corrects the arithmetic to match the corrected breadth range. Not to be reopened absent new information.

### Final formula

low = adjusted_baseline * combined_multiplier * multi_channel_severity_loading * severity_scalar

(severity_scalar remains the existing, locked, unchanged SEVERITY_SCALAR mechanism — this design does not touch it.)

## Legal/Compliance — split out, no longer part of this design

Originally, this design (Steps 1-3 above) treated Legal/Compliance as a 4th criterion, identical in treatment to the other three, with the actuarial mismatch flagged but deferred pending a future conversation. This session split Legal/Compliance out entirely into its own mechanism-aware design (prompts/friction-tax-legal-compliance-methodology.md, in progress, not yet Gemini-reviewed, not yet implemented) — it is no longer scored, aggregated, or combined within Steps 1-3 of this document at all, and the "4 criteria" language throughout this doc has been corrected to "3 criteria" to reflect that. Turnover, Productivity, and Decision-Quality (the 3 remaining criteria here) share the property of scaling roughly with org size, which is what makes the proportional payroll-fraction blending in this design appropriate for them; Legal/Compliance does not scale that way and needs mechanism-specific treatment instead (individual claim vs. class/systemic vs. wage-hour vs. whistleblower), detailed in the separate doc.

## Next steps (in order)

1. Gemini architecture review of this design (schema/formula implementation questions) — not yet sent.
2. multi_channel_severity_loading (K) = 0.05 CLOSED — Pete's final decision, not to be reopened absent new information. Breadth range corrected to 1-3 this session (was 1-4, before Legal/Compliance was split out) — see Step 3; documentation correction only, K itself not reopened.
3. CC implementation: replace compute_friction_tax()'s mean_multiplier step with combined_criterion_score aggregation per Step 1 (3 criteria: turnover, productivity, decision_quality), add multi_channel_severity_loading per Step 3 (breadth 1-3), verify single-state continuity explicitly against the rescaled [0, 6] / [0.05, 0.25] mapping (prompts/friction-tax-state-multiplier-methodology.md), update tests.
4. Legal/Compliance tail-risk methodology is its own separate, actively in-progress design (prompts/friction-tax-legal-compliance-methodology.md) — no longer gated on this design's implementation.
