# /book/toc Gestalt Pass — Build Scope

Status: DRAFT, scoping pass. Extends prompts/book-toc-shared-filter-gestalt-intersections.md
(thread 2 of 3, prioritized first per Pete's confirmation). Not yet Gemini-reviewed. Not started.

## The actual problem, restated precisely

`/book/toc` currently presents 9 filter chips (4 dimensions, 5 signatures) with zero explanation
of what any of them mean or why this taxonomy exists, before asking a visitor to filter by them.
Per Pete's framing, this is the highest-stakes gap on the page — not a polish item, the thing
that determines whether a first-time visitor reads the taxonomy as a credible instrument or as
"gimmicky AI-generated" pattern-matching. The taxonomy itself may be the least important detail;
the *framing around it* is what actually carries trust.

## Real design judgment call — flagging rather than deciding silently

ConstellationField's addendum (just shipped) used a fully on-demand model: nothing visible by
default, a small trigger reveals explanation on hover/tap. That worked there because the shape
itself already communicates *something* even unexplained — a person sees a shape with a glowing
vertex and knows intuitively "something is being measured here," even before understanding what.

`/book/toc`'s filter chips don't have that same baseline legibility. A flat row of "APTITUDE /
AUTHORITY / ALLIANCE / ATTITUDE" and "LEADERSHIP BOTTLENECK / CULTURE EROSION / ..." chips
communicates close to nothing on their own — there's no shape or visual metaphor doing any of
the interpretive work the way ConstellationField's geometry does.

**Recommendation:** don't make the page-level "what is this" framing on-demand at all — make it
default-visible, short, plain-brand-voice text near the top of the page (extending the existing
subhead, which currently just says "Filter by dimension, by signature, or both."). This is the
credibility signal Pete is describing, and hiding it behind a click undersells its importance.
Reserve on-demand disclosure for the *secondary* layer — what each specific dimension or
signature actually means — which is detail, not the primary trust signal.

This is a real call, not an obvious one — flagging for confirmation before it's built rather
than deciding it silently.

## Scope, two layers

**Layer 1 — default-visible page framing (new copy needed).** A short paragraph near the page
top, before or alongside the existing subhead, establishing: what this taxonomy is (not a
personality-quiz-style label generator — a calibrated instrument with real methodology behind
it), and implicitly, why filtering by these terms is a legitimate way to explore it. Needs a
real P-10 brand-voice pass — this is the single most important piece of copy in this entire
scope, worth getting right rather than treating as boilerplate.

**Layer 2 — on-demand per-term explanations.**
- **Dimensions (4):** real, locked content already exists — `PUBLIC_DIMENSION_LABELS`, the same
  source already reused for Category D's industry picker and ConstellationField's own per-axis
  reveals. No new content needed here, just a new place to surface it.
- **Signatures (5):** genuinely new content gap. No existing locked copy defines what "Culture
  Erosion," "Leadership Bottleneck," "Stunted Growth," "Compounding Risks," or "Information
  Blindness" actually mean as groupings — these exist as real `stateIds` lists in `taxonomy.ts`
  but have no authored explanation anywhere. Needs its own P-10 pass, 5 short entries.

## Architecture question for Gemini — one affordance or nine

Two real options, not deciding here:
- **(a) One combined "what do these terms mean" panel** — single trigger, lists all 9 terms with
  short definitions in one place. Lower repetition risk, but requires scrolling/scanning within
  the panel itself.
- **(b) Per-chip on-demand disclosure** — reuses the exact ConstellationField addendum pattern
  literally once per chip (9 total instances). More precise (explanation appears right where the
  term is), but risks the exact "gimmicky/overloaded" feeling this whole pass exists to avoid if
  9 separate hover targets feels like clutter rather than clarity.

**Leaning toward (a)** given the explicit goal of the page reading as credible rather than
busy — but this is exactly the kind of structural choice that should go through the same
narrow, confirm-or-reject Gemini format that's worked reliably for the last several rounds on
this project, not be decided unilaterally here.

## Governing constraints
- Same principle basis as ConstellationField's addendum: P-06 (meets the user where they are),
  now stated more sharply per Pete's own framing — context is not optional polish, it's the
  difference between credibility and gimmickry.
- P-10 brand voice for all new copy (both layers).
- Whichever Layer 2 architecture is chosen should, where possible, reuse the interaction pattern
  already shipped (hover panel desktop / tap-drawer mobile) rather than invent a new one —
  consistency across the site's "explain this" affordances is itself part of feeling considered
  rather than gimmicky.

## Open items before Gemini review
- Layer 1 copy — needs drafting (P-10 pass), not yet written.
- Layer 2 signature definitions — needs drafting (P-10 pass), not yet written.
- (a) vs (b) architecture choice — Gemini gate, narrow format.
- Real check: does the existing gestalt-addendum interaction pattern (from ConstellationField)
  transfer cleanly to a page-level context, or does anything about `/book/toc`'s actual current
  structure make that harder than it sounds? Needs Claude Code's trace before assuming either
  way, same discipline as every prior architecture decision this session.
