# SCD-WCS Taxonomy-Wide Vector/Template Re-Authoring — Scoping Document

Date: 2026-08-24. **Scoping only — no building.** This sets up a real future session; nothing here is executed.

## What this project is, precisely

Not a bug fix. The SCD-WCS investigation (this and prior sessions, full record in `prompts/scd-wcs-remediation-tracker.md`) root-caused the taxonomy's ranking-accuracy problem to a **content-authoring gap**, not a math bug: `rank_states()` itself is confirmed correct (no rounding/clamping/quantization anywhere). Of 58 states, only **18 have a unique `dimensional_vector`** — the other 51 (88%) share a vector with at least one other state, across 11 clusters of 2-11 members. Most of those clusters were resolvable with salience-only differentiation (a cheaper, mechanical fix — Ranks 5, 6, 7, 8 all shipped this way this session and prior sessions). What's left is the harder tier: states whose dominance can't be fixed by adjusting salience weights at all, because the problem is the shared/underpowered *vector* itself, not how it's weighted.

## What's actually left in scope — confirmed, not estimated

**4 pre-existing dominant states, confirmed not fixable via salience alone** (whack-a-mole tested directly: suppressing any one or combination's salience caps out at 1 of 19 currently-masked states gaining real payoff, since the pool just promotes its next-most-extreme member):

- `built_to_fail` — 28% false-rank-1 rate at last measurement (49/175), broad attractor (steals across all four dimensions).
- `invisible_performance_management` — the single largest dominance problem in the whole taxonomy at last full measurement (59/175, ~34%), also a broad attractor.
- `the_uninitiated` — re-verified this session at 17/175 (9.7%), but a **structurally different pattern** from the other three: 100% Authority-axis, a cross-cluster asymmetry against its own rank-2/rank-3 clusters, not a broad multi-dimension attractor. Scoping note: this state may need a different remediation approach than the other three (a two-cluster reweighting problem, not a single-vector re-author), not confirmed either way in this pass.
- `the_second_close` — smaller dominance footprint, same general "broad attractor" family as `built_to_fail`/`invisible_performance_management`, less independently characterized than the other three.

**Explicitly out of this scope, confirmed by Phase 2 findings this session:**
- Candidate C (`invisible_performance_management`/`the_unexamined_algorithm` differentiation) is **already shipped and closed** (see `prompts/phase2-item8-candidate-c-status-correction.md`) — it addressed a *different*, narrower same-cluster collision, not this broad-attractor problem. `invisible_performance_management` remains in this list's scope for its *own* dominance issue, unrelated to the Candidate C fix.
- The `decision_paralysis`/`the_lost_map` tie-break question (Item 7) is **not part of this project's scope** — confirmed a cosmetic, insertion-order tie-break artifact carrying no real signal, not a magnitude-dominance problem. Explicitly does not need to be touched by this re-authoring effort.

## Rough scale

Not "up to 51 states" (the total cluster-membership count) — the *confirmed-in-scope* work is **4 states' `dimensional_vector`s**, each requiring genuine clinical/taxonomic re-authoring (real differentiated dimensional content grounded in each state's actual `descriptive_prose`, not a mechanical salience nudge). This is comparable in *nature* to the still-undated `STATE_CAUSATION_OVERRIDES` per-state authoring pass already on the Priority Queue (Pete's own clinical judgment work), and likely larger in *scope* given it's 4 states rather than one field. Each state's re-authoring would need the same rigor this session applied elsewhere: real ripple-audit against the full 175-profile calibration set, concentration sweeps rather than single-value guesses, ripple-attribution to confirm the fix doesn't create new false-rank-1 problems elsewhere (the exact whack-a-mole risk already confirmed real in this taxonomy).

`the_uninitiated`'s structural difference (cross-cluster, not broad-attractor) means it may not fit the same remediation template as the other three — worth a dedicated diagnosis pass before assuming all 4 states can be re-authored via one uniform method.

## What Gemini's gate needs to review before execution starts

Per this project's standing discipline (architectural decisions affecting multiple files/data contracts route through Gemini before execution): a re-authoring pass touching `dimensional_vector` values for 4 states is exactly this kind of structural decision, not a Tier 1 calibration tweak. The review package should cover:

1. **The proposed re-authoring methodology itself** — how a new `dimensional_vector` gets derived from a state's real `descriptive_prose` (the same "real text, not hand-derived extrapolation" discipline already used for the smaller salience-only fixes), and what the acceptance criteria are (full calibration regression, ripple-audit thresholds, confirmed no new false-rank-1 for any other state).
2. **The order/sequencing of the 4 states** — whether they're re-authored one at a time with a full ripple-audit between each (matching the rank-7/8/9 pilot precedent) or batched, given the whack-a-mole risk means fixing one could shift dominance onto another.
3. **`the_uninitiated`'s scoping question specifically** — whether it belongs in this same project or needs its own separate two-cluster reweighting approach, before any vector value is proposed for it.
4. **The uniqueness constraint already locked this session** — no new state may share a `dimensional_vector`/`salience_weights` with an existing state (CLAUDE.md, Engine Rules, locked 2026-08-19) — this re-authoring project is the direct remediation for exactly the taxonomy-expansion pattern that rule was created to prevent going forward; the review should confirm the proposed re-authored vectors for these 4 states also don't collide with any of the *other* 54 states' vectors, not just resolve the original collision.

## Not decided here

Timing, whether to pursue at all, and who authors the actual differentiated content (a real clinical/taxonomic judgment call, not something to delegate to an automated proposal per the standing discipline already established for `STATE_CAUSATION_OVERRIDES`) — all explicitly Pete's call, consistent with every other open item this session left for his decision rather than assumed.
