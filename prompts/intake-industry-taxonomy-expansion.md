# Intake Redesign — Expand Industry Taxonomy to Cover Construction and Logistics

**Status:** Proposed design. Originates from the Demographic Applicability Filter's Cluster 5
work, which found `is_high_hazard` can only ever fire for 2 of PRV3's 9 industry values
(Manufacturing & Industrial, Healthcare & Life Sciences) -- while BLS consistently ranks
construction and transportation/warehousing among the highest injury/fatality-rate industries
nationally, and neither has its own value in the current taxonomy. Both fall into `"Other"`
today, indistinguishable from any other industry that doesn't fit the existing 8 categories.
NOT yet reviewed by Gemini. NOT implemented. Second intake-schema proposal this session,
alongside the headcount-precision redesign -- related but scoped separately per Pete's
direction, not combined into one change.

## Proposed new values

Add two values to `engine/data/intake.py`'s `INTAKE_FIELDS["industry"]`, named to match
standard federal industry classification (NAICS sectors) rather than invented labels, so real
BLS/SUSB data can be sourced against them directly:

- **"Construction"** (NAICS Sector 23)
- **"Transportation & Warehousing"** (NAICS Sectors 48-49)

Resulting taxonomy: 11 industry values instead of 9. `"Other"` remains as a residual category
for whatever doesn't fit any of the 11.

## What this requires beyond the schema edit itself

**`HIGH_HAZARD_INDUSTRIES` update:** straightforward, add both new values to the existing set.

**`PAYROLL_BASELINE_GRID` expansion -- the real lift.** This grid is built as a composite key
over `HEADCOUNT_BUCKETS x INDUSTRIES` (currently 6 x 9 = 54 cells, matching the "54-cell" grid
already referenced elsewhere in the Friction Tax Tier 3 work). Adding 2 industries expands this
to 6 x 11 = 66 cells -- **12 new cells need real payroll-baseline data sourced**, not just a
code change. This is genuine research (SUSB or BLS industry-specific average
payroll/wage-per-employee figures for Construction and Transportation & Warehousing, matched
across all 6 of PRV3's headcount buckets), comparable in scope to the original 54-cell
population work, not a trivial addition.

## Why this matters beyond Cluster 5

Once these two industries exist as real intake values, they don't just fix `is_high_hazard` --
they also make `org_type = "PE or VC-backed"` cross-referenced with `industry` (the edge case
flagged in Addendum 5 for Cluster 4's SEC-jurisdiction gating) more useful, and any future
industry-specific work (e.g. Cluster 3's wage-and-hour scoping, which already varies
meaningfully by whether a workforce is largely hourly -- construction and logistics skew
heavily non-exempt) gets a real category to hook into instead of being buried in "Other."

## Open questions

1. Does the existing 54-cell grid's Construction/Transportation-adjacent data (if any
   currently gets approximated via "Other" or a similar industry) get discarded once real
   figures exist, or does "Other" retain its own populated baseline separately from these two
   new specific categories?
2. Should this proposal go to Gemini together with the headcount-precision redesign (both are
   intake-schema changes surfaced by the same applicability pass, in the same session) or
   separately, given Pete's direction to keep them scoped apart? Recommend checking with Pete
   before bundling anything into one Gemini handoff.
3. Real payroll-baseline sourcing for the 12 new cells is unstarted -- needs the same rigor as
   the original 54-cell population (real SUSB/BLS data, not estimated), which is a nontrivial
   research task on its own before this can be implementation-ready.
