# /book/toc Fuller Vision — Build Scope

Status: DRAFT, scoping pass. Builds on prompts/book-toc-fuller-vision.md (concept, approved
2026-08-11) — read that first. This resolves the concept doc's own pre-build data check (now
confirmed, with corrections) and turns the approved direction into an actual phased plan. Not
yet Gemini-reviewed. Not started.

## What the data pull confirmed, corrected from the original concept doc

**1. `primary_dimension` — real, but not where the concept doc assumed.** Not in
`web/data/taxonomy.ts` at all. It's `dimension: StateDimension` in `web/lib/book-state-index.ts`,
already populated for all states and already powering `/book/toc`'s existing hub page. No new
data needed for the dimension filter tag family — just a correction to which file the build
draws from.

**2. `resolution_family` — genuinely not available frontend-side as a static per-state fact.**
This is a real gap, not a formality. `web/lib/resolution-family.ts` is a translator (engine
output → commercial name), not a lookup table — it has no way to answer "what's state X's
default resolution_family" without a live diagnosis session behind it. The badge/link mechanism
the concept doc describes needs a new static frontend source before it's buildable.

Directly relevant precedent: this is the same problem Category D's `resolution_family` bug just
was, and the same fix pattern applies. `run_condensed_engine()` was fixed to source
`resolution_family` from the lead state's own `STATE_PROFILES` entry rather than
`output_package.private` (which structurally excludes multi-state mode) — confirmed same
underlying data, just a different, mode-independent read path. `/book/toc` should use the same
source (`STATE_PROFILES`, not the routing-gated field) to build its static per-state mirror, for
the same reason: it needs to work for every state regardless of any routing mode, since this is
build-time/static content, not a live session output at all.

**3. Signature-grouping data — real and usable, with one number correction and one real
staleness gap.** `web/data/taxonomy.ts`'s `signatures` export is real, 5 signatures, each with a
populated `stateIds`. Correction to the concept doc's own number: `culture_erosion` has 13
states, not "14+."

Real gap: `taxonomy.ts` has exactly 57 states — `the_inner_circle` (the 58th) is entirely absent.
`book-state-index.ts` already includes it correctly, so the two frontend files this feature
draws from are currently out of sync with each other. This needs fixing before the signature-tag
filter can be trusted — a missing state from a filterable tag system isn't a cosmetic gap, it's
a state that would simply never appear no matter what filter combination is selected.

**Open, not yet answered — needs a real check, not a guess:** does `the_inner_circle` belong to
any of the 5 existing signature groupings (`culture_erosion` or otherwise), or does it not
cleanly fit any of them? This needs to be checked against real engine/taxonomy data, not assumed
either way — assigning it to a signature it doesn't actually belong to would be its own new
inaccuracy, not a fix.

## Build plan, phased

**Phase 1 — data layer fixes (Claude Code, no UI yet):**
- Add `the_inner_circle` to `web/data/taxonomy.ts` (the missing 58th state entry), and resolve
  the open signature-membership question above via real source before assigning it to any
  `stateIds` list.
- Build a new static per-state `resolution_family` frontend source, sourced from
  `STATE_PROFILES` (same pattern as Category D's fix), NOT from `output_package.private` or
  `resolution-family.ts`'s translator. Likely lives alongside `book-state-index.ts` as a sibling
  data file, or as an added field on the existing per-state entries there — Claude Code's call
  on the cleaner shape, given real file structure.
- Confirm whether a real, existing service-page URL exists for each commercial resolution_family
  name (`resolution-family.ts`'s translator output) — the badge's link target needs a real
  destination, not a guess at a URL pattern.

**Phase 2 — Gemini architecture review.** This touches `taxonomy.ts`, an existing shared file
with unknown other consumers beyond `/book/toc` — modifying it is a structural change, not a
content-only edit, so it routes through Gemini per standing protocol. The new resolution_family
data source and the filter-combination logic (OR within a tag family, AND across families) are
also structural additions worth review before build, not content changes to an existing surface.

**Phase 3 — build.** Filter UI (dimension tags + signature tags, multi-select per the concept
doc's OR-within/AND-across rule), each state card showing description, tags, linked media
(already buildable via existing `book-state-index.ts` mappings), and the resolution_family badge
linking to its service page.

**Phase 4 — verification.** Standard discipline: `tsc --noEmit`, relevant test suite, live
browser verification of the filter combinations and at least one badge link actually resolving
to a real page, before treating this as shippable.

## Governing constraints, carried forward from the concept doc and locked visual identity
- Rust reserved for Endemic severity only — this feature has no severity dimension at all
  (browsing taxonomy states, not viewing a diagnosis), so rust should not appear anywhere in the
  filter/tag UI. Slate blue (existing general accent) plus distinct-but-non-clashing treatment
  per dimension within that family, per the concept doc's own direction.
- JetBrains Mono for taxonomy data (state IDs, tags) — matches locked type system.
- P-10: no coined terms requiring a glossary — tag labels need to read in plain language.

## Explicitly still deferred, unchanged from the concept doc
- Citations/research linking — blocked on the still-deferred citation-sourcing workstream, link
  in once that catches up, doesn't block the rest of this build.
- A richer interconnection graph/visualization between states — no data foundation supports this
  yet, its own separate future design pass if ever picked up.

## Open items before Gemini review
- The_inner_circle signature-membership question (Phase 1).
- Confirmation of real service-page URLs per resolution_family (Phase 1).
- Exact shape/location of the new resolution_family static data source — Claude Code's
  implementation call, informed by real file structure.

**Status, 2026-08-14: all three closed.** Original scoping content above left unchanged — this
note exists so the doc doesn't silently disagree with the Decision Register (tools/_mob.txt,
Section 13a). The_inner_circle assigned to Culture Erosion (signatureId: "culture_erosion",
added to Culture Erosion's stateIds) — on review of the real member list, it shares its core
mechanism (inconsistent application of standards/accountability based on identity or
relationship) with the_inside_track, the_wrong_reward, the_basement_standard, and
the_burned_credibility. resolutionFamily built as an added field on book-state-index.ts's
existing per-state entries, not a sibling file — same mirroring pattern as the file's other
fields, sourced from STATE_PROFILES, raw values translated at display time via the existing
translateResolutionFamily(). Service-page URLs confirmed real: /about/services has content for
all 4 commercial resolution_family names, and now has per-section id attributes
(#people-tactics-and-strategy, #training-development, #intervention, #executive-advisory) so the
badge can link to the relevant section, not just the flat page. Ready for Phase 2.
