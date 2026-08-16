# /book + /toc: Shared Filtering, Gestalt Context, and Internal Intersection Research

Status: RAW DIRECTION, just captured. Not scoped, not approved for build. Captures a real
strategic redirect from Pete, not just a feature request — the governing principle below should
likely outlive this specific page.

## The governing principle, stated plainly, worth elevating beyond this one page

Pete's own framing: "It cannot be overstated how turned off our clients will be if they explore
this AI-generated site and only see a gimmicky taxonomy without context. The taxonomy may be the
least important detail."

This is a sharper, more specific version of something already flagged this session as a
candidate standing principle but never formally locked: "spoon-feed meaning when not speaking
plainly in brand voice" (surfaced during Category E's ConstellationField work, recorded in
prompts/category-e-direction1-refinement-legibility-motion.md's origin note, still unlocked).
This new framing extends that same instinct from a single component to an entire category of
site content: **complexity/taxonomy without context reads as AI-generated gimmickry, not rigor,
and actively damages trust rather than building it.** The 58-state taxonomy is real, calibrated,
and load-bearing — but a visitor encountering filter chips with no explanation of what they mean
or why they exist has no way to know that, and the default read in that vacuum is skepticism,
not credibility.

**Recommendation, not yet actioned:** this principle is strong and general enough to warrant its
own line in the MOB's governing principles (alongside P-06, P-10, etc.), not just a page-specific
note — worth a real Decision Register entry the next time this gets picked up, separate from any
of the three build threads below.

## Three separable threads

### 1. Shared filter/tag feature between `/book` and `/book/toc`

Currently `/book` (the article index) has no filtering at all — flat list. `/book/toc` (the
taxonomy hub) has the dimension + signature filter UI shipped earlier this session. Pete wants
these unified: the same filter/tag mechanism available on both surfaces, not two different
browsing experiences for content that's already cross-linked via `book-state-index.ts`.

Not yet scoped: whether this means literally the same filter component reused on both pages, a
shared filter *state* that persists across navigation between them, or something else. Real
open question for a future scoping pass.

### 2. `/book/toc` needs its own gestalt pass — explaining the filterable terms themselves

Directly parallel to Category E's just-shipped ConstellationField addendum: that work added a
"how to read this" affordance explaining what the *shape* means, separate from the four per-axis
explanations of what each *dimension* means. `/book/toc` has an analogous gap at the page level —
dimension and signature filter chips currently have zero explanation of what "Aptitude,"
"Culture Erosion," etc. actually mean or why this taxonomy exists at all, before a visitor is
asked to filter by them.

**Likely reusable pattern, not yet confirmed:** the same interaction shape that just shipped
(a distinct, separate "how to read this" trigger, on-demand disclosure, locked short copy) may
transfer directly to `/book/toc` — same principle, same UI language, different content and a
page-level rather than component-level placement. Worth checking against real page structure
before assuming a direct port, not guessing.

This is also where the governing principle above bites hardest: this gestalt pass isn't
optional polish, it's the thing that turns "AI-generated taxonomy" into "credible instrument
with named methodology" in a visitor's actual first impression of the page.

### 3. Internal intersection research — deferred, gated, sequenced deliberately

The original concept doc (prompts/book-toc-fuller-vision.md) already deferred "a richer
interconnection graph/visualization between states" as a later-phase idea with no existing data
foundation. Pete's direction now gives it an actual path, not just a deferral:

1. **Internal research first, not public-facing.** Explore what intersections between states/
   dimensions/signatures are genuinely interesting — a research exercise, not a shipped feature.
2. **Credibility gate before any public surfacing.** Only becomes a real, shippable tool once
   confirmed as methodologically credible and supportive of the actual practice — not shipped
   just because it's visually interesting or technically buildable.

This sequencing itself is consistent with the governing principle above — the whole risk being
guarded against is shipping something that *looks* sophisticated without being *substantively*
grounded, and gating this research behind an internal credibility check before any public
exposure is exactly the discipline that prevents that.

## Explicitly not decided yet
- Whether all three threads move together or get sequenced separately.
- The gestalt pass's exact placement/copy on `/book/toc` (needs its own short content pass,
  same as Category E's addendum needed one).
- What "shared filter feature" between `/book` and `/toc` concretely means in implementation.
- Scope, format, or even internal audience for the intersection research thread.

## Next steps
None yet — captured for continuity. Needs Pete's own further direction on sequencing (all three
at once, one first, or a mix) before this becomes a real scoping conversation.
