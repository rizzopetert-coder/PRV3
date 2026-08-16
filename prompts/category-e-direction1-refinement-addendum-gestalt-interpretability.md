# Category E, Direction 1 Refinement — Addendum: Part 4, Gestalt Interpretability

Status: DRAFT, concept-level. Not yet through Gemini review. Not started. Addendum to
prompts/category-e-direction1-refinement-legibility-motion.md — read that file first, this
extends it rather than replacing it.

## Origin

Live verification of the shipped Part 3 (per-axis hover reveal, via the new
/dev/diagnostic-fixture route) confirmed the axis-level interpretability fix works correctly —
hovering AUTH correctly surfaces its `PUBLIC_DIMENSION_LABELS` copy, `aria-expanded` toggles per
axis, the active vertex gets a real visual highlight.

But a real gap surfaced during that same check: the four per-axis reveals answer "what does this
axis measure," never "what does the shape as a whole mean." Someone could hover all four vertices,
learn every axis definition, and still have no way to read the composite picture — why one vertex
sitting far out while the others stay near center matters, or what the rust glow/concentric rings
are signaling. Part 3 solved interpretability one axis at a time; it never solved it for the
shape's own gestalt.

## Why this is a distinct problem, not more of Part 3

Part 3's reveals are correctly scoped to a single axis each — that's exactly right for what they
are. Folding gestalt-level explanation into one of them (or into all four, redundantly) would
either misattribute shape-level meaning to a single dimension or repeat the same explanation four
times. This needs its own affordance, answering a different question than the per-axis ones do.

## Governing-principle basis

Same as Part 3: P-06, the instrument meets the user where they are and cannot assume prior
orienting work. This applies at the shape level exactly as it applied at the axis level — a user
who understands what "Authority" means can still fail to understand what a lopsided quadrilateral
with a rust-glowing vertex is telling them about their organization.

## Scope

A separate, single "how to read this" affordance — not a fifth per-axis-style hover target,
something visually distinct from the four (e.g. a small info icon or short text link positioned
near the shape, not competing with the four vertex hit-areas). On activation (hover desktop / tap
mobile, same interaction family as Part 3), reveals a short, plain-brand-voice explanation
covering:

- What distance from center means (how pronounced a liability reads on that dimension).
- What the rust glow/concentric rings signal, and why they only ever appear at Endemic severity.
- A rough read on shape patterns — one dominant vertex vs. a more even spread — without turning
  into a stats tutorial.

Kept short. This is orientation, not a legend — a sentence or two per point, not a paragraph.
Same "spoon-feed on demand, not spoon-feed always-on" standard as Part 3: this affordance stays
inert until activated, doesn't add permanent on-page text, and doesn't compete visually with the
shape itself at rest.

## Real content gap, not yet resolved

Unlike Part 3, there's no existing locked copy source for this — `PUBLIC_DIMENSION_LABELS`
covers the four axes, nothing covers the shape's own reading mechanics. This needs its own short
P-10 brand-voice pass before or alongside the build. Not drafted here.

## Open, unresolved
- Exact placement and visual treatment of the affordance — needs to read as clearly secondary to
  the four axis hit-areas, not a fifth vertex.
- Whether this needs a distinct mobile pattern from Part 3's tap-to-reveal drawer, or can reuse
  it directly — likely reusable, not yet confirmed.
- The actual explanatory copy — not yet drafted, needs P-10 pass.

## Draft copy, P-10 pass (first draft, needs Pete's review before treated as locked)

Confirmed against `severityAccentTokens()`'s real mechanic before writing the rust line: the
rust/slate rule is a hard binary, rust only at `severityTier === "Endemic"`, slate at every other
tier, zero interpolation — the copy below reflects that as a threshold, not a gradient, on
purpose.

**Title:** How to read this

**Body, three short points, not paragraphs — sized for a short list layout per CC's trace
finding that this is more content than a single axis panel:**

- The further a point sits from the center, the more compromised that dimension is.
- Rust means Endemic. It only appears at the most serious tier — nothing gradual leads into it.
- One point pulled far out names a specific condition. Several pulled out together means more
  than one thing is compounding at once.

This is a first draft, not locked — needs Pete's own read before it's treated as final P-10
copy, same as any other brand-voice pass. Point 1 uses "compromised" rather than "carrying" —
Pete's call, swapped after flagging the original word's overlap with the homepage's "what your
organization is carrying" copy. "Compromised" is a deliberate anchor to already-locked language,
not just an avoidance of repetition: P-11 (Principal Brief) defines the liability axis in this
exact term — "the liability axis measures how significantly the dimension is compromised." This
copy now uses the project's own governing vocabulary for the concept rather than a new metaphor.

## Next steps
Touches ConstellationField's rendering surface again, directly adjacent to Part 3's shipped
interactivity. Needs Gemini architecture review before any code changes, per standing protocol —
same file, same gate, no exception for it being an addition rather than a fresh direction.

Given the content/architecture coupling CC flagged, Gemini's review should evaluate the
structural question (option (a), fully separate state and a second Drawer.Root, vs. option (b),
a widened AxisKey | "gestalt" | null type sharing one Drawer.Root) against this copy's actual
shape — three short points, not a two-paragraph panel — rather than against the addendum's
original abstract description. The tab-order question CC raised (this affordance first, before
the four axes, vs. last) still needs Pete's explicit call — not a default, not Gemini's or CC's
decision to make.
