# "Visualize your data" — per-state severity comparison section

Status: RAW CONCEPT. Not scoped, not approved for build, no urgency assigned.
Logged for continuity so a future session has the design reasoning without
reconstructing it from Claude.ai chat history — same convention as
`prompts/service-expectations-page-concept.md`.

Design reasoning developed in a Claude.ai conversation, 2026-08-19, in the
session immediately following the SeverityResult per-state redesign's
Checkpoint 6 close (Checkpoint 6 was confirmed complete as an audit — the
existing feature set only ever needed the single lead-state-anchored
`severity.tier` scalar, which Checkpoint 3 already fixed). This is new,
separate scope, not something that redesign was ever meant to cover.

## The feature

A new report section showing every qualifying state's own severity (tier +
relative magnitude) side by side, with no state visually privileged over
another. Explicitly **not** a lead-state-anchored view — a deliberate
departure from the pattern Checkpoint 3 locked in for the existing
single-scalar VII.1 fields (top-level `severity`, `urgency_window`, the
Friction Tax `severity_tier` param). Those fields need one scalar because
they're single values in a fixed JSON contract; this feature exists
specifically because a single scalar can't represent what happens across
several qualifying states at once.

Audience: both client-facing and internal.

## Design direction settled this session

- **Row-based layout**, one row per state already present in
  `identified_states` — not all 58 taxonomy states, not some filtered
  subset. The same set already shown elsewhere in the report (state blocks,
  Decision Blindness flag, etc.) — no new state-selection logic needed.
- **Each row**: state name, a color-coded tier badge, and a continuous bar
  reflecting the state's own `score_0_100` magnitude within its tier — so
  two states sharing a tier (e.g. both Entrenched) are still visually
  distinguishable by relative severity, not flattened into three buckets.
- **No sorting/ranking implied by row position** — deliberate, to avoid
  smuggling a lead-state hierarchy back into a section whose entire point is
  that no state is privileged over another.
- **Emerging-as-floor framing**: confirmed with Pete that Emerging is the
  real floor of the severity scale — a state with zero attributed severity
  input still classifies as Emerging via the real math (`compute_state_severity()`
  scoring a state with no `SeverityInput`s), not a placeholder or fallback
  default value. Worth a brief explanatory note in the eventual UI so a
  short bar reads as "a real finding, least severe of three tiers," not as
  "borderline" or "not enough data."

## Underlying data need

`engine/severity.py`'s `SeverityResult.state_severity`
(`dict[state_id, StateSeverity]`, tier + `score_0_100`) has been computed
since Checkpoint 1 of the per-state redesign but has never crossed the
VII.1 wire contract to the web layer. Confirmed via a full trace this
session (Checkpoint 6's audit): `web/lib/types.ts`, `web/lib/engine-client.ts`,
all 4 route files, and every component that reads `payload.severity` only
ever see the single top-level scalar — there is no `state_severity` field
anywhere on the TypeScript side, and a repo-wide grep for `state_severity`
under `web/` returns zero matches. This feature is the first thing that
would actually need that data to cross the wire.

## Rough build shape (NOT yet scoped in detail)

1. **VII.1 schema addition** exposing per-state severity across the wire —
   a locked-contract change, needs its own Gemini architecture review, same
   treatment as Checkpoint 3 (this is new schema surface, not a fix to
   existing surface).
2. **Wire-contract plumbing** — `engine-client.ts`, `types.ts`, the relevant
   routes. Mechanical, similar shape to Checkpoint 2's plumbing work.
3. **The actual UI component** in `PrivateOutput.tsx`, plus an open
   decision on whether it also appears in `ShareableOutput.tsx` given the
   stated dual (client-facing + internal) audience — shareable output
   travels without the principal present, to a board/CFO audience, so this
   needs its own look before assuming parity with the private view.

## Open questions, not resolved here

- Exact placement of the new section within `PrivateOutput.tsx`'s existing
  block structure.
- Whether `ShareableOutputPayload` gets this data at all, and if so, in
  full or filtered (mirrors the existing `secondary_states` weight-based
  filtering precedent — Include only weight >= 0.20, max 2 secondary
  states — or something new).
- Visual system specifics (bar component, color tokens, whether it reuses
  `severityAccentTokens()` from `ConstellationField.tsx` or needs its own).
- Whether this ships as part of a larger Report Depth Initiative pass or as
  its own standalone build.

None of these are decided. This document exists so the next session that
picks this up starts from the real design reasoning, not a cold restart.
