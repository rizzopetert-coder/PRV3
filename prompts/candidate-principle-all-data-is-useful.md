# Candidate Governing Principle: "ALL DATA IS USEFUL"

**Status: Provisional Hold, not Locked.** Same treatment P-13/P-14 received before they were formally worded and locked (see `tools/_mob.txt`, "P-13, source and first applications" / "P-14, source and first application"). Not added to CLAUDE.md's Governing Principles list or the Principal Brief until Pete explicitly locks it. Recorded here so the reasoning and precedent trail exist outside conversational context, per standing rule.

## Exact wording

**"ALL DATA IS USEFUL."**

This is Pete's own phrasing, stated directly this session. A weaker framing — "data must be useful" — was floated during the same discussion and explicitly rejected. The difference between the two is not stylistic; it is the entire point of the principle.

## The distinction, precisely

**"Data must be useful"** puts the burden on the data to justify its existence. A computed value that isn't visibly consumed somewhere becomes suspect by default — the implicit next question is "why are we computing this?", and the implicit next move is to prune it. The data has to earn its keep before it's trusted.

**"ALL DATA IS USEFUL"** reverses that burden. Every computed value is presumed valuable from the moment it exists. If something isn't being consumed yet, that is a gap in the system to close — a missing consumer, not evidence that the data was wrong to compute in the first place. The data doesn't have to earn its keep; the system has to earn the data's value by eventually using it.

This is not a small reframing. It changes what counts as a finding versus what counts as a non-issue.

## Two-sided in practice

1. **An ongoing obligation to keep building real consumers for values already computed.** A thinly-used computed value is not a settled state — it's an open item. The presumption of value doesn't discharge itself; it has to be made good on.
2. **A stricter intolerance for any computed value going silently null, degenerate, or guessed.** Under "data must be useful," a value quietly returning `null` or a degenerate default is a harmless edge case — the data wasn't being used anyway. Under "ALL DATA IS USEFUL," that same silent failure is actively destroying something presumed valuable. The severity of a silent-degradation bug is categorically higher under this principle than under the weaker framing.

## Precedent cases (this session)

Following the same retroactive-precedent pattern P-13 used — cases that already fit the principle's shape before it was named, cited as evidence the principle describes something real rather than something invented after the fact:

1. **`asset_score` / `dimension_summary`** — real, computed values, thinly consumed: one ratio, one visualization feed via `ConstellationField`, one conditionally-empty synthesis text block. Not proof they're wrong to compute; evidence more consumers are owed.
2. **`jurisdiction_flags.applied_multipliers`** — empty per `engine/contract.py`'s own docstring, "until axis modifier logging is wired end-to-end." A schema field representing nothing yet, not a mistake to remove.
3. **`causation_pattern`** — documented as a pure helper not threaded into the output contract in some call paths. Computed, real, under-consumed.
4. **The org_type gap (this session).** `compute_friction_tax()`'s `calibration_complete: False` sat silently on every real Path 1 session because `org_type` was never collected — invisible until the friction tax ledger build made the gap consequential enough to surface and fix. Exactly the "silent degradation is not a harmless edge case" half of the principle, caught only because someone built a new consumer that exposed the missing input.
5. **The `signal_map_context` / Trajectory bug (this session).** Same shape: computed, silently degenerate (`""` / `0.0` delta), invisible for an unknown span of time until directly investigated. Two real features (synthesis context, trajectory direction) were quietly producing nothing, for real sessions, with no error raised anywhere.

## What's still open

Per the Provisional Hold vs. Lock convention (Session 56): a Provisional Hold exists because an open thread could still change the shape of the final decision. Here, the open thread is not the naming — Pete's wording is exact and final as stated — it's **whether Pete wants a permanent verification/observability discipline attached to this principle**, not just the naming of it. That is, does "ALL DATA IS USEFUL" stay a descriptive/cultural principle (a lens for evaluating findings like the five above), or does it become a locked, checkable rule (e.g., a standing session-close check for newly-silent-null fields)? That decision is Pete's, not made here.
