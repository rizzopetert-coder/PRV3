# Ohio Compensatory-Damages Pricing Plan (plan only, not built, not Gemini-reviewed)

Priority Queue item 9 scope, decided 2026-09-14. This is a durable
multi-session plan doc, capturing what was decided and what remains
open — not a build, and not yet submitted to the Gemini architecture
gate.

## Goal

Wire `_oh_is_small_employer()` (`engine/friction_tax.py:3222`) into a
real R.C. 2315.21 compensatory-damages pricing path for Ohio —
currently both of that statute's branches resolve to
`QUALITATIVE_ONLY` because no compensatory-damages base figure exists
anywhere in the codebase for any jurisdiction (confirmed by
investigation this session).

## Decided

- **Salary-range basis:** reuse the existing `_INDUSTRY_WAGE_DATA`
  table (real BLS OEWS May 2023 mean annual wages by industry, already
  wired into `compute_friction_tax()`) as the compensatory-damages
  salary basis, rather than sourcing a new dataset.
- **No individual/case-specific salary collection** — Pete explicitly
  ruled this out. The output will always be an industry-average-
  derived estimate, never anchored to the actual terminated employee's
  real wages. This is permanent, not a fallback for when case data is
  missing.
- **Consequence, flagged and accepted:** because `_INDUSTRY_WAGE_DATA`
  is a MEAN, not a distribution, any known citation-accuracy
  imprecision already living in that table (e.g. the Technology
  sector's "Sector 51 Information" being broader than a clean
  Technology label, documented in the table's own source notes) now
  carries legal-accuracy weight it didn't carry when it only fed a
  friction-cost estimate. This needs explicit review, not silent
  inheritance, when this plan reaches the Gemini gate.
- **State+industry multipliers on top of the salary base:** still
  undefined. Represents litigation-outcome/settlement-variance by
  jurisdiction (not yet confirmed whether that's the right framing vs.
  something else) — scoped as a research task, not yet started.

## Not decided / open

- What the state+industry multiplier is actually supposed to model,
  precisely (litigation outcome variance? settlement variance?
  something else?) — flagged as still fuzzy even after being called a
  "research task."
- Output framing: given no case-specific data is ever collected, the
  UI-facing presentation needs to read as a rough, heavily-caveated
  range, not anything resembling a real case estimate — exact
  language/framing not yet drafted.
- Whether this needs a new field on `LegalPricingResult`/
  `LegalCurveLookup` or reuses an existing shape.
- The broader gap this plan sits inside: no compensatory-damages base
  exists for ANY jurisdiction today, not just OH — this plan only
  solves it for OH. Whether that's the right scope boundary (OH-only)
  or whether the multiplier/base-salary mechanism should be built
  jurisdiction-agnostic from the start is an open architecture
  question for the Gemini gate, not decided here.

## Process

- This entire methodology (new pricing capability, new legal-content
  claim) requires the Gemini architecture gate before any code is
  written — not yet submitted.
- Research on state+industry multipliers to happen next, likely via
  Claude.ai web search given Gemini's documented pattern of citation
  fabrication in this exact codebase (real source, invented precision
  — Financial Services and Technology sector wage corrections this
  same file already required). Every claim independently verified
  against primary source before use, per standing verification
  discipline.
