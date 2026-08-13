# Category E, Direction 2 — Instrument-Panel Reframe: Four-Dial Concept Spec

Status: DRAFT, concept-level. Written after Directions 1 and 3 shipped (MOB v4.148/v4.149) —
this spec inherits their locked constraints rather than starting fresh. Not yet through Gemini
review. Not started.

## Origin, and what's changed since the original three-direction brief

The original Category E brief (category-e-visual-identity-refresh.md) scoped Direction 2 as an
alternative to Direction 1: four radial gauges/dials, one per dimension, instead of one combined
quadrilateral. At the time it was written, none of the three directions had shipped, so Direction
2 was framed as competing with Direction 1 for the same job — fixing "looks cheap and
rudimentary."

That job is done. Direction 1 shipped (centroid-tracking radial gradient, per-axis vertex glow,
depth stacking, CSS-only motion) and was live-verified against an Endemic-tier result. Direction
3 also shipped (editorial/typographic hero, variable-length cluster display) and took over as the
results experience's primary visual moment. Direction 2 was never built.

This means Direction 2 is no longer answering "does the shape look cheap" — that's resolved. It's
now an open question of **what job Direction 2 would even be doing today**, addressed below.

## Constraints carried forward from shipped work (binding, not re-litigated)

- Rust reserved for Endemic severity only, never decorative — same rule Direction 1 honored.
- No Framer Motion. CSS-only motion, tuned cubic-bezier curves — confirmed absent from
  package.json, your explicit call on Direction 1.
- The real `data-emphasis` enum is `"primary"|"secondary"|"receded"` — not `"dimmed"`, which was
  Gemini's fabricated value on Direction 1. Any Direction 2 spec sent to Gemini should have this
  stated explicitly up front rather than left for Gemini to infer.
- P-11 (dual-axis dimensional scoring): each dimension carries a liability axis and an asset
  axis. ConstellationField's shipped model reads both. A four-dial reframe needs an explicit
  answer for whether each dial shows one axis or both — a single-needle dial that only shows
  liability would be a real regression from what's already live, not a lateral redesign.

## The open question that isn't mine to resolve

Direction 1's ConstellationField is shipped, live, and already reads all four dimensions in one
combined instrument. Direction 2 replacing it with four separate dials is a real product
decision with three genuinely different shapes, not a design nuance:

1. **Replace** — four dials become the new primary visualization, ConstellationField retired.
2. **Supplement** — four dials ship as a secondary/expanded view (e.g., below Direction 3's hero,
   or behind a "see the full read" expansion), ConstellationField stays as the primary glance.
3. **Shelve** — Direction 1 solved "doesn't look professionally made" and Direction 3 became the
   hero; Direction 2 no longer has a clear job and stays concept-level indefinitely.

My read: **(2) is the strongest case if this gets built at all.** ConstellationField's one-shape
gestalt is genuinely good for a fast first read, and ripping it out to replace it with four dials
risks re-litigating a "doesn't look professionally made" problem you already solved. A dial panel
earns its place as a deeper, optional read — closer to how a real diagnostic instrument invites
a second look — not a wholesale swap. But this is a real call about what the results page is for,
not a craft-execution question, so I'm flagging it rather than deciding it.

## If (2) is the direction — open design items, not yet resolved
- Layout: four dials in a row, 2×2 grid, or arranged around/beneath the existing
  ConstellationField.
- Whether "expanded view" is a click-to-reveal, a scroll continuation, or a toggle.
- Whether severity/rust-gating logic (a property of the *identified state*, not any one
  dimension) has a sensible mapping onto four independent dials at all, or whether rust only
  ever belongs on the combined shape.

## Next steps
Needs your call on replace/supplement/shelve before anything else is scoped. If supplement or
replace: needs Gemini architecture review before any code changes, per standing protocol — this
touches ConstellationField's shipped rendering system either way.
