# /book/toc Glossary Intersection — Recurring Phrase Mining

Status: **Investigation only. Internal working doc, Pete + Claude Code audience.
No Gemini gate — not a structural or shipping decision.** No filter UI changes,
no code changes to /book or /book/toc. Raw material for a future plainspoken-
filter-category redesign (replacing filtering by dimension/signature), nothing
more.

Method, tooling: `tools/diag_book_toc_glossary_intersection.py` (read-only,
reusable). Extracts every string from the 8 sources below via source-specific
regex, verified against expected structural counts before trusting anything
downstream (58 states, 5 signatures, etc. — confirmed exact matches). Splits
into sentences, generates word n-grams (3–8 words, never spanning a sentence
boundary) and counts frequency across the whole corpus. Separately flags
near-exact duplicate sentences/clauses via longest-common-subsequence (LCS,
order-preserving, gaps allowed) as a percentage of the shorter sentence's word
count — not a raw-contiguous-match test, which under-credits the "same
template, one clause swapped" pattern this task is specifically looking for
(verified against the flagship example below before trusting the metric).

## Sources mined — live/current versions, confirmed via direct file read

Deliberately went beyond `taxonomy.ts` per the task's instruction — three of
these eight are genuinely separate bodies of copy for the same underlying
states/signatures, not duplicates of each other, and each contributes real,
distinct recurring language:

1. `web/data/taxonomy.ts` — `states[].description` (58)
2. `web/data/taxonomy.ts` — `signatures[].description` (5)
3. `web/data/taxonomy.ts` — `signatures[].coexistenceInterpretation` (5)
4. `engine/resolution_families.py` — `RESOLUTION_FALLBACK_COPY` values (19)
5. `web/lib/book-state-index.ts` — `BOOK_STATE_INDEX[].descriptiveProse` (58) —
   **confirmed distinct from #1**: mirrors `engine/data/states.py`'s
   `descriptive_prose`, a genuinely different body of copy for the same 58
   states, authored separately for the public `/book/toc` surface.
6. `web/lib/book-taxonomy-labels.ts` — `PUBLIC_DIMENSION_LABELS` (8: 4
   dimensions × title + description)
7. `web/app/book/toc/page.tsx` — `SIGNATURE_DEFINITIONS`, the Gestalt Pass
   Terminology Guide copy (5) — **confirmed distinct from #2/#3**: a third,
   shorter body of signature-level copy.
8. `web/components/ConstellationField.tsx` — `GESTALT_INFO` (title + 3 points,
   the gestalt-interpretability addendum's "How to read this" panel)

---

## Recurring phrases — the strongest by raw frequency

**838 total phrases (3–8 words) recur across ≥2 distinct entries.** Most of
that volume is grammatical connective tissue, exactly as the task warned
single-word recurrence would be — "the people who," "the organization is,"
"in this organization," "the organization has," each appearing 10–13 times,
are real counts but not usable filter-category material on their own. Not
discarded (full list is in the tool's raw output, reproducible on demand),
just deprioritized here in favor of the phrases below, which are long enough
(4–8 words) at a real frequency (≥3 distinct entries) to carry actual thematic
content rather than sentence glue:

| phrase | count | appears in | thematic read |
|---|---|---|---|
| "the organization is paying" | 4 | the_undefined_role (×2 sources), the_unsolved_problem, the_unformed_leader | organizational cost is already visible, not projected |
| "the people with the [authority/options]" | 4 | the_dormant_talent, the_paper_tiger, leadership_bottleneck (signature), the_broken_compass | the people positioned to fix it are also the people most able to leave |
| "with the authority to [act/move things]" | 3 | the_tolerated_violation, what_nobody_says, leadership_bottleneck (signature) | authority and the ability to act have separated |
| "the senior people who [couldn't live with it]" | 3 | the_founders_grip (×2 sources), leadership_bottleneck (signature) | the people who'd normally push back have already gone |
| "on a version of [reality]" | 3 | leadership_deafness, information_blindness (signature), the_suppression_filter | leadership is acting on a picture that's already wrong |
| "at the top of this organization" | 3 | the_inner_circle (×2 sources) | concentrated at the top, self-protecting |
| "people tactics and strategy [addresses]" | 7 | RESOLUTION_FALLBACK_COPY (multiple tier/family entries) | resolution-copy template reuse, not a taxonomy concept — see note below |

The last row is a different kind of finding, flagged so it isn't mistaken for
the others: `RESOLUTION_FALLBACK_COPY`'s repetition is a service-name literal
recurring across severity-tier variants of the same resolution family — real,
but mechanical/templated rather than conceptual, and not raw material for a
*taxonomy* filter category the way the first six rows are.

---

## Near-exact duplicate sentences/clauses — the class Pete flagged, surfaced systematically

**39 pairs found at ≥65% LCS overlap.** Sorted strongest first. The flagship
example is confirmed and present:

**100% exact duplicates (9 pairs) — same sentence, word for word, in two
different shipped sources:**

| sentence | appears in |
|---|---|
| "The organization isn't between HR leaders." | the_exposed — taxonomy.ts *and* book-state-index.ts |
| "There's a group at the top of this organization who look out for each other first." | the_inner_circle — taxonomy.ts *and* book-state-index.ts |
| "Decisions get made in rooms you're not in, by people who protect each other's mistakes as readily as their own." | the_inner_circle — taxonomy.ts *and* book-state-index.ts |
| "It isn't about one person getting away with something — it's a whole layer that answers to itself instead of any standard." | the_inner_circle — taxonomy.ts *and* book-state-index.ts |
| "The people outside the circle have figured out exactly what that means for them." | the_inner_circle — taxonomy.ts *and* book-state-index.ts |
| "Leadership here [genuinely] believes they have an accurate picture of what's happening in this organization." | leadership_deafness (state) *and* information_blindness (signature) |
| "The values are [still] on the wall." | the_culture_that_wasnt (state) *and* culture_erosion (signature) |
| "People Tactics and Strategy addresses that level directly..." / "...addresses the architecture." | two different RESOLUTION_FALLBACK_COPY entries |

**The specific example Pete spot-checked, confirmed at 91% LCS (10/11
words):**

> the_founders_grip (state): *"The senior people who couldn't live with either
> option have already left."*
> leadership_bottleneck (signature): *"The senior people who couldn't live
> with that have already left."*

A third variant of the same sentence exists in `book-state-index.ts`'s own
`the_founders_grip` entry (73% LCS): *"The senior people who could tolerate
neither option have already left."* — three independently-worded versions of
the same underlying line across three sources.

**Other strong (70–90%) matches, ranked:**

| match % | sentence pair | where |
|---|---|---|
| 88% | "People who've been here long enough feel it." / "...know what changed" | culture_drift / culture_erosion |
| 86% | "...addresses the architecture." / "...addresses the structural conditions that keep recreating it." | RESOLUTION_FALLBACK_COPY (internal) |
| 80% | "New hires figure this out within their first ninety days." / "New hires figure out the gap in their first ninety days." | the_culture_that_wasnt / culture_erosion |
| 79% | "...discovers it has been managing one employee on paper and a completely different one in practice." | the_paper_tiger — taxonomy.ts *and* book-state-index.ts |
| 78% | "You've learned to work around the bottleneck..." | the_founders_grip / leadership_bottleneck |
| 75% | "The people who most defined what this organization stood for are leaving." / "The ones who cared most about what this place stood for are the ones leaving first." | identity_erosion / culture_erosion |
| 73% | "The organization redesigned the role/job without redesigning the resources..." | the_overloaded_manager — taxonomy.ts *and* book-state-index.ts |

**Below 70% (weaker, tail-end matches, included for completeness, not
recommended as filter-category evidence):** several short generic templates
("Nobody decided to abandon the values" / "Nobody decided to leave the door
open"; "The values are on the wall" coincidentally sharing 4 words with
several unrelated sentences) — full list in the tool's raw output.

---

## Candidate plainspoken filter labels

Per the task's framing — surfacing the strongest *objective* candidates by
frequency, not curating which ones are "good":

| evidence | candidate label |
|---|---|
| "the people with the authority/options," "with the authority to act," the leadership_bottleneck/the_broken_compass/the_inner_circle cluster | **"Who actually has the power to decide"** |
| "leadership...believes/operating on a version of reality," leadership_deafness/information_blindness/the_suppression_filter | **"Leadership doesn't see what's really happening"** |
| "the senior people who couldn't live with it have already left," three independent phrasings across three sources | **"The people who could leave, already have"** |
| "the organization is paying," the_undefined_role/the_unsolved_problem/the_unformed_leader | **"What it's already costing you"** |
| "at the top of this organization," the_inner_circle's 4 fully-duplicated sentences | **"A small group protects itself"** |
| "New hires figure [this/the gap] out within their first ninety days," the_culture_that_wasnt/culture_erosion | **"What a new hire notices fast"** |

---

## Side finding, flagged not fixed — same-state exact duplication across two live sources

`the_inner_circle` has **4 full sentences** word-for-word identical between
`taxonomy.ts`'s `description` and `book-state-index.ts`'s `descriptiveProse`
— not a near-match, the entire description is close to a verbatim copy across
both fields for this one state. Every other state pair checked shows the two
fields as genuinely independently-authored (different wording, same
condition, per `book-state-index.ts`'s own header comment describing
`descriptiveProse` as mirroring `engine/data/states.py`, a separate authoring
source from `taxonomy.ts`). Whether `the_inner_circle`'s two copies were
deliberately written identically (its content was authored more recently,
this session, per MOB) or whether one was copy-pasted from the other instead
of independently authored is not established here — flagged as a real,
narrow content-maintenance observation, out of scope for this task to
resolve.

---

## Explicitly not done here

No filter UI changes. No code changes to `/book` or `/book/toc`. No decision
on which candidate label (if any) gets built. This is raw material for a
future scoping conversation, not a recommendation to act on now.
