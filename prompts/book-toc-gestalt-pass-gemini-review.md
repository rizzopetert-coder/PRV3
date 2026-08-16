# /book/toc Gestalt Pass — Gemini Review: Constrained Confirmation Only

Status: ready to send. Not an open architecture review. Full context:
`prompts/book-toc-gestalt-pass-build-scope.md` (build scope) and
`prompts/book-toc-shared-filter-gestalt-intersections.md` (parent thread). Real component
traced: `web/app/book/toc/page.tsx` as currently shipped (unchanged since `/book/toc` Phase 3,
commit `93dce90`).

Same discipline that's cleared cleanly on the last several rounds (Category D's rounds 3–4,
`/book/toc` Phase 2, Category E's gestalt-interpretability addendum): state what's already
confirmed against real source plainly, ask for confirm-or-reject only, no room for reinventing a
third option.

## Locked, not open for reinvention

- **Trigger placement: option (A).** Inline text trigger placed in normal document flow
  immediately after the existing intro paragraph (`<p className="font-ui text-base text-gray-600
  mb-10">The full set of organizational conditions...</p>`), before the filter-bar `<div
  className="mb-10 space-y-4">`. No new wrapper `<div>`, no absolute positioning — DOM order
  alone gives it tab-first placement ahead of the filter chips. Rejected: (B) corner-anchored
  inside the filter-bar div (would need a `relative` wrapper added for no real structural reason
  here — unlike ConstellationField's SVG, this page has no fixed coordinate space, so a corner
  position isn't grounded in anything); (C) its own default-visible section (too heavy for
  Layer 2's on-demand/secondary role per the build scope doc's own framing). Do not propose an
  alternative placement.
- **Panel shape: two labeled sub-groups, not one flat list.** The combined panel holds
  "Dimensions" (4 items) and "Signatures" (5 items) as two internally-labeled groups, not 9 items
  in one undifferentiated list. Do not propose flattening this or splitting it into two separate
  panels/triggers (that's option (b), already rejected in favor of (a) — the single combined
  panel — per Pete's own confirmation).
- **One combined trigger, not per-term.** Confirmed already: option (a) over (b) (9 separate
  per-chip triggers). Not reopened here.

## What's actually being asked — two confirm-or-reject items

**1. State/Drawer mechanics — sound against `page.tsx`'s real current state, or not?**

`page.tsx` is already `"use client"`, already holds two `useState` pairs
(`dimensionFilters`/`setDimensionFilters`, `signatureFilters`/`setSignatureFilters`) plus a
`useMemo`-derived `filtered` list. Confirmed via direct read, not assumed: no `Drawer` import
from `vaul` currently exists in this file (only in `ConstellationField.tsx`/`StateDrawer.tsx`),
and `PUBLIC_DIMENSION_LABELS` is not currently imported here either (removed as unused during
Phase 3's build, since that build didn't need it).

The proposed addition, mirroring the same `hoveredX`/`tappedX` boolean-pair pattern Gemini
already confirmed for Category E's addendum (option (a) there, same reasoning applies): a new
boolean pair (e.g. `termsHovered`/`termsTapped`) driving one desktop panel and one `Drawer.Root`
instance, a new `import { Drawer } from "vaul"`, and a re-added `import {
PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels"`. `preventDefault()` on Enter/Space
suppresses the native button's keyboard-triggered click, same as the addendum's shipped pattern,
so keyboard focus alone never opens the Drawer's body-scroll-lock.

> Confirm this state/Drawer approach is sound against `page.tsx`'s real current imports and state
> (listed above), with no hidden conflict — naming collision, hook-ordering issue, or otherwise —
> or state a specific objection. Do not propose a different state-management approach (e.g. a
> context provider, a separate component extraction, or a shared-with-the-filter-state design) —
> the ask is whether this specific, already-proven pattern ports cleanly, not whether a different
> pattern would also work.

**2. Two-group panel content and accessibility — anything Category E's addendum didn't have to
handle?**

Category E's addendum panel held one content type only: a title plus a flat list of 3 short
points, under one `Drawer.Title` (sr-only, set to that single title). This panel is structurally
different: two labeled groups (Dimensions, Signatures) inside one panel, one shared trigger, one
shared `Drawer.Root`.

> Confirm whether combining two labeled groups inside one panel/Drawer — as opposed to the
> addendum's single flat list — introduces any real accessibility concern (e.g. how the two
> groups should be marked up for screen-reader users to distinguish them, what `Drawer.Title`
> should represent when the content covers two groups rather than one) that the shipped addendum
> pattern didn't have to solve, and if so, what the specific fix is. Do not propose reverting to
> per-chip triggers (option (b), already rejected) as the fix — the ask is what changes inside
> the single combined panel's own markup, not a structural rollback to a rejected option.

## Still open, explicitly not blocking this review

- **Layer 1 copy** (default-visible page framing, near the existing subhead) — not yet drafted,
  needs a P-10 pass.
- **The 5 signature definitions** (Culture Erosion, Leadership Bottleneck, Stunted Growth,
  Compounding Risks, Information Blindness) — genuinely new content, no existing locked source
  (unlike the 4 dimensions, which reuse `PUBLIC_DIMENSION_LABELS` verbatim). Needs its own P-10
  pass.

Same sequencing as Category E's addendum, where copy and architecture were coupled but the
review proceeded on the confirmed shape of the copy (title + N short points) without the final
wording being locked yet. Evaluate the two items above with placeholder-shaped awareness — a
short paragraph for Layer 1, five short entries for signatures — not against any specific
wording, since none exists yet.

## What counts as a well-formed response

- **(1) and (2), each confirmed as sound**, optionally with a specific, narrow objection.
- **Not well-formed:** a different placement, a different panel shape, a different trigger
  model (per-chip or otherwise), a proposal to draft the missing copy, or a claim about
  `page.tsx`/`ConstellationField.tsx`/`book-taxonomy-labels.ts` not checked against the real,
  current files.

Standard discipline applies on the way back in: whatever Gemini returns gets independently
verified against real source before anything is treated as final, same as every round before
this one.
