# Intake Redesign — Expand Industry Taxonomy to Cover Construction and Logistics

**Status:** COMPLETE. Originated from the Demographic Applicability Filter's Cluster 5
work, which found `is_high_hazard` could only ever fire for 2 of PRV3's 9 industry values
(Manufacturing & Industrial, Healthcare & Life Sciences) -- while BLS consistently ranks
construction and transportation/warehousing among the highest injury/fatality-rate industries
nationally, and neither had its own value in the taxonomy. Both fell into `"Other"`,
indistinguishable from any other industry that didn't fit the existing 8 categories.
`INTAKE_FIELDS["industry"]` and `HIGH_HAZARD_INDUSTRIES` both updated, `PAYROLL_BASELINE_GRID`
picked up both new industries via its existing Cartesian-product mechanism (see corrected
scoping note below), full test suite (friction_tax, calibration, contract) verified clean.
One real, unanticipated dependency surfaced during implementation and is now also resolved:
INDUSTRY_NON_EXEMPT_RATIO (Legal/Compliance Cluster 3, a separate table this proposal never
anticipated touching) required its own two new ratios -- resolved cleanly for Construction
(0.554, closely corroborating the existing Manufacturing figure), and for Transportation &
Warehousing (0.422) with a documented denominator limitation (BLS's CPS table does not break
Transportation & Warehousing out from Utilities, understating the true ratio -- flagged
explicitly in engine/friction_tax.py, not silently approximated). Not sent to Gemini for
review -- the correction was a math-mechanism finding (see below) and independently-verified
BLS sourcing, not a new architectural decision.

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

**`PAYROLL_BASELINE_GRID` expansion -- CORRECTED SCOPING (this section was wrong).** This
proposal originally claimed the grid's 6 x 9 = 54 cells expanding to 6 x 11 = 66 would need
"12 new cells" of independently-sourced payroll data, "comparable in scope to the original
54-cell population work." Confirmed false once the actual mechanism was read directly: every
cell is `_INDUSTRY_WAGE_DATA[industry][0] (wage) x HEADCOUNT_MIDPOINTS[headcount].employees_per_firm`
-- and `HEADCOUNT_MIDPOINTS` is industry-agnostic (one set of 6 Census SUSB firm-size figures,
reused identically across every industry column, sourced from SUSB's national All-Industries
Total row). The 54 (now 66) cells rest on only 9 (now 11) independent wage inputs plus 6
industry-agnostic headcount inputs -- adding 2 industries needed exactly 2 new wage figures
(one BLS OEWS lookup each), not 12 independently-sourced cells. Done: Construction ($67,430)
and Transportation & Warehousing ($59,320), both BLS OEWS May 2023 mean annual wage, Sector 23
and Sectors 48-49 respectively. "Other" was also rebuilt in the same pass -- its prior single
SOC 00-0000 national-all-occupations figure structurally overlapped with Construction and
Transportation & Warehousing wage data once those became their own columns (a national total
is not a genuine post-exclusion residual) -- replaced with a verified nine-component
employment-weighted composite ($63,446) that genuinely excludes every industry now claimed
elsewhere in the grid.

## Why this matters beyond Cluster 5

Once these two industries exist as real intake values, they don't just fix `is_high_hazard` --
they also make `org_type = "PE or VC-backed"` cross-referenced with `industry` (the edge case
flagged in Addendum 5 for Cluster 4's SEC-jurisdiction gating) more useful, and any future
industry-specific work (e.g. Cluster 3's wage-and-hour scoping, which already varies
meaningfully by whether a workforce is largely hourly -- construction and logistics skew
heavily non-exempt) gets a real category to hook into instead of being buried in "Other."

## Open questions -- all resolved

1. RESOLVED: "Other" was rebuilt as its own genuine nine-component residual (see above),
   not discarded -- it retains a populated baseline separate from Construction and
   Transportation & Warehousing, now genuinely excluding both rather than structurally
   overlapping with them.
2. RESOLVED: implemented directly, not sent to Gemini -- the actual required work (2 wage
   figures, corrected scoping, 2 non-exempt ratios) was independently-verified BLS sourcing
   and a math-mechanism correction, not a new architectural decision needing review.
3. RESOLVED, and the original premise was wrong -- see the corrected `PAYROLL_BASELINE_GRID`
   scoping note above. Only 2 wage figures were needed, not 12 independently-sourced cells.
   Separately, and NOT anticipated by this proposal at all: INDUSTRY_NON_EXEMPT_RATIO
   (Legal/Compliance Cluster 3) needed its own 2 new ratios -- resolved, see
   engine/friction_tax.py's header comment and the MOB's documentation-reliability finding
   entry (Section 13) for the full account, including a real citation-accuracy gap found and
   corrected in the 9 pre-existing ratios along the way.
