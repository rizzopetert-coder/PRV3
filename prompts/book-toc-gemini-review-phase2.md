# /book/toc Fuller Vision — Gemini Review, Phase 2: Constrained Confirmation Only

Status: ready to send. Not an open architecture review — every item below reflects a decision
already made and, in three of four cases, already built and shipped. This follows the same
discipline that Category D's later review rounds settled into after two rounds of fabricated
proposals there (`prompts/category-d-gemini-review-round3-constrained.md` and `-round4-*`):
state what's already confirmed against real source plainly, ask for confirm-or-reject only, no
room for reinvention on settled questions.

Full context: `prompts/book-toc-fuller-vision.md` (concept, approved 2026-08-11) and
`prompts/book-toc-build-scope.md` (phased build plan, Phase 1 now closed). Decision Register:
`tools/_mob.txt`, the `/book/toc fuller vision` row.

---

## What to confirm or reject — four items, no substitutions

**1. `taxonomy.ts` modification — the_inner_circle added as the 58th state, assigned to
Culture Erosion.**

> `web/data/taxonomy.ts` was missing its 58th state (`the_inner_circle`) entirely — confirmed by
> direct count, not assumed. It has been added as a new `states` entry and assigned
> `signatureId: "culture_erosion"`, and added to Culture Erosion's `stateIds` array. Real fit,
> not forced: it shares its core mechanism (inconsistent application of standards/accountability
> based on identity or relationship) with four existing Culture Erosion members
> (`the_inside_track`, `the_wrong_reward`, `the_basement_standard`, `the_burned_credibility`).
>
> Real consumers of `taxonomy.ts` confirmed by grep, not assumed: `web/app/book/state/
> [stateSlug]/page.tsx`, `web/app/diagnostic/page.tsx`, `web/components/AssemblyPanel.tsx`,
> `web/components/SignatureCard.tsx`, `web/components/StateDrawer.tsx`, `web/lib/prompts.ts`.
> Traced the two highest-risk paths directly: `getDominantSignature()` and
> `handleSeeWhatThisMeans()` in `diagnostic/page.tsx` both read `signatureId` straight off
> `states` for whatever a respondent selects, feeding `web/lib/prompts.ts`'s
> `buildInterpretationPrompt()` via `POST /api/interpret`. Before this change, selecting
> `the_inner_circle` sent `signatureId: ""` into that live path — miscounted into an
> empty-string signature bucket in `getDominantSignature()`, and capable of producing an
> unlabeled group in the live LLM interpretation prompt. This is a genuine production bug fix,
> not only a `/book/toc` data-availability fix. Confirm this consumer-impact analysis is sound
> and complete, or state a specific objection with a specific consumer this missed. Do not
> propose a different signature assignment or a different set of consumers to check — the
> assignment and the consumer list are both final, verified against real source.
>
> Already built, verified, committed: commit `7efd812`. `tsc --noEmit` clean. `vitest` at
> baseline (same 4 files / 6 pre-existing failures, none touching `taxonomy.ts` or its
> consumers).

**2. `resolutionFamily` field added to `book-state-index.ts`'s `BookStateEntry`.**

> A new `resolutionFamily: string` field was added directly on `BookStateEntry` (not a sibling
> data file), populated for all 58 states from `engine/data/states.py`'s `STATE_PROFILES`, raw
> engine values, not translated at write time. Consumers translate via the existing
> `web/lib/resolution-family.ts`'s `translateResolutionFamily()` at display time — same as every
> other real caller of that function, not a second copy of the translation logic.
>
> Real consumers of `book-state-index.ts` confirmed by grep: `web/app/book/toc/page.tsx`,
> `web/components/DiagnosticFixturePicker.tsx`. Adding a required field to an existing exported
> interface is a breaking type change in principle — confirmed non-breaking in practice, since
> neither consumer constructs a `BookStateEntry` (both only read the pre-populated
> `BOOK_STATE_INDEX` export), and `tsc --noEmit` ran clean after the change. Confirm this shape
> (added field vs. a sibling file) is the right call given these two real consumers, or state a
> specific objection. Do not propose a different data source or file structure — `STATE_PROFILES`
> as the source and the mirroring pattern itself are both final, matching every other field
> already on this interface.
>
> Already built, verified, committed: commit `7efd812`.

**3. `/about/services/page.tsx` anchor IDs — additive, no behavior change.**

> Four `id` attributes were added to `/about/services/page.tsx`'s four existing `<section>`
> elements (`people-tactics-and-strategy`, `training-development`, `intervention`,
> `executive-advisory`), so a future `resolution_family` badge on `/book/toc` can link to the
> relevant section rather than the flat page. This is a shared file outside `/book/toc`'s own
> directory, folded into this same review pass per Pete's explicit instruction rather than
> treated as exempt. Confirm four additive `id` attributes on existing elements, with no other
> markup or content change, carries no structural risk, or state a specific objection. Do not
> propose a shared slugify utility or a different anchor scheme — four fixed, hand-matched values
> is the final decision, documented inline in the file itself.
>
> Already built, verified, committed: commit `7efd812`.

**4. Phase 3 filter-combination logic — not yet built, this is the one genuinely open item.**

> Per the approved concept doc, `/book/toc`'s filter UI uses two tag families — dimension
> (`primary_dimension`, 4 values, sourced from `book-state-index.ts`) and signature (5 values,
> sourced from `taxonomy.ts`'s `signatures` export) — with OR-within-a-family, AND-across-families
> combination logic (e.g. selecting two dimension tags shows states matching either; adding a
> signature tag narrows that result to states also matching the signature). Confirm this
> combination logic is implementable cleanly against the two real data sources named above with
> no additional data layer needed beyond what Phase 1 already built, or state a specific
> objection. Do not propose a different filter model (e.g. AND-within-family, a third tag
> family, or a scoring/ranking model instead of a boolean filter) — the OR/AND rule itself is
> final, carried from the approved concept doc, not open for redesign here.

---

## What counts as a well-formed response

A well-formed answer to each item is **one of exactly two things**:

- **(a) Confirmed as sound.**
- **(b) A specific, narrow objection** to what's actually described above — not a replacement for
  it.

**Any response that proposes a different signature assignment, a different data file shape, a
different anchor scheme, or a different filter-combination model is non-responsive to what was
asked.** Do not evaluate such a response on its own merits or treat it as a usable proposal —
flag it plainly, the same as Category D's early rounds, not extract something buildable from it.

---

Standard discipline applies on the way back in: whatever Gemini returns gets independently
verified against real source before anything is treated as final, same as every round before
this one. Items 1–3 are already shipped — a rejection on any of those means a follow-up fix, not
a blocked build. Item 4 is the actual gate before Phase 3 build starts.
