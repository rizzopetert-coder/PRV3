# Visualize Your Data — Per-State Severity Comparison: Build Scope

Status: SCOPED, not yet Gemini-reviewed, not yet built.
Precedes: SeverityResult per-state redesign (Checkpoints 1-6, CLOSED 2026-08-19) —
this feature's underlying data is now trustworthy (0/175 profile mismatches,
verified by the calibration harness itself).
Concept doc (unchanged): prompts/visualize-your-data-severity-comparison-concept.md

## Problem

engine/severity.py's state_severity dict (tier + score_0_100 per state,
correct since Checkpoint 1, verified correct end-to-end since Checkpoint 4/5)
has never crossed the VII.1 wire contract. Confirmed via Checkpoint 6's full
trace: web/lib/types.ts, engine-client.ts, all 4 routes, and every component
only ever see the single top-level lead-state-anchored severity scalar.
Nothing today lets a Principal (or Pete, internally) see how their own
identified states compare to each other in severity — only the single lead
state's tier/score is visible anywhere in the product.

## Design (already settled, Claude.ai session 2026-08-19 — not open for
## re-litigation in this scope, only implementation)

- Row-based layout, one row per state already in identified_states (NOT all
  58 taxonomy states — matches the report's existing qualifying-state scope).
- Each row: state name, color-coded tier badge, continuous bar reflecting
  that state's own score_0_100 within its tier (so two states sharing a tier
  stay visually distinguishable from each other).
- No sorting/ranking implied by row position.
- Deliberately NOT lead-state-anchored — a departure from Checkpoint 3's
  pattern for the existing single-scalar VII.1 fields, by design.
- Emerging is the real floor of the severity scale (a zero-input state
  classifies Emerging via the real math, not a placeholder default) — the
  eventual UI needs an explanatory note so a short bar reads as a real
  finding, not as "borderline" or "broken."

## Explicit non-dependency (avoid conflating with a different open item)

This feature needs PER-STATE severity, already fully available and correct
today via engine/severity.py's state_severity dict. It does NOT need
triggering_option_id or any split-by-option attribution — that's a separate,
unrelated prerequisite that only matters for the SeverityResult per-state
redesign's own possible follow-on (split-by-option severity), not for this
feature. Do not scope triggering_option_id work into this build.

## Build layers

**Layer 1 — VII.1 schema addition (locked-contract change, needs its own
Gemini architecture review, same treatment as Checkpoint 3):**
- New field exposing a list of {state_id, tier, score_0_100} entries, one
  per state in identified_states — mirrors state_severity's existing shape,
  no new computation, pure exposure.
- Open question for Gemini: Section VII is referred to elsewhere as an
  "immutable contract" (Checkpoint 3 notes) in the context of not mutating
  existing scalar fields — confirm whether a purely ADDITIVE new field is
  permitted under that immutability rule without an ENGINE_VERSION bump
  (currently 0.2.0), or whether this counts as a contract change requiring
  one. Do not assume either answer going in.
- Build target: build_private_block() (output.py) first. Do NOT touch
  build_shareable_block() in this pass — see audience decision below.

**Layer 2 — wire-contract plumbing (mechanical, similar shape to
Checkpoint 2):**
- web/lib/types.ts: new StateSeverityEntry type, extends
  PrivateOutputPayload only (not ShareableOutputPayload — see below).
- engine-client.ts: pass the new field through.
- Routes: do NOT assume Checkpoint 6's route list carries over unchanged —
  re-trace which routes construct PrivateOutputPayload from engine output
  at build time before touching any of them. Category D's condensed flow
  (run_condensed_engine()) should very likely be excluded entirely: it
  deliberately never collects severity_inputs, so its output is always a
  single Emerging tier with nothing to compare — confirm this reasoning
  against the real code before excluding, don't just assert it.

**Layer 3 — UI:**
- PrivateOutput.tsx: new section per the settled design above. In scope now.
- ShareableOutput.tsx: OUT OF SCOPE for this pass — see audience decision.

## Open decision for Pete: audience sequencing

Recommendation: build internal-only first (PrivateOutput.tsx), defer
ShareableOutput.tsx to a second, separately-gated phase. Reasoning, not a
default hedge: the client-facing surface carries real extra cost this
internal-only pass doesn't — P-13 ("structural complexity needs a 'how to
read this' affordance before or alongside it") applies directly to a
multi-state severity comparison shown to a Principal who has no context for
reading it, on top of the Emerging-floor explanatory note already required
by the settled design. Internal audience (Pete) doesn't need either. Shipping
internal-only first also exercises the new schema field and wire plumbing
against a real, lower-stakes surface before deciding how (or whether) to
expose it externally — the schema/wire work doesn't need to be redone for
Phase 2, only the ShareableOutput.tsx component and its P-13 framing.

## Verification plan

- Full 172(+3)-profile calibration regression must stay byte-identical
  (state ranking untouched by a purely additive field).
- New engine test coverage confirming the new field's values match
  state_severity exactly, for a multi-state and a single-state profile.
- tsc clean, vitest extended with a PrivateOutput.tsx component test.
- Live round trip (Preview or production, Pete's call per standing
  credential-access pattern): confirm per-state tiers/scores rendered in
  the UI match engine/severity.py's state_severity dict directly for a real
  multi-state session — not just unit-verified in isolation.

## Sequencing note

No hard dependency on the SCD-WCS remediation or any other open item. Not
time-sensitive. Candidate item for the ~August 23 Quarterly Step-Back's
forward-planning discussion, not a forced pre-Step-Back build.
