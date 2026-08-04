# Intake Redesign — Precise Headcount via "About How Many" Stepper

**Status:** Proposed design. Originates from the Demographic Applicability Filter's systematic
pass across Legal/Compliance clusters, which found that PRV3's six-bucket headcount field
creates real coverage-threshold uncertainty (ADA/Title VII at 15, FMLA at 50) that a precise
number would eliminate. Reach extends well beyond Legal/Compliance -- affects Cluster 4's
Title VII damage-cap tiers (100/200/500) and Cluster 5's OSHA penalty-reduction tiers
(25/100/250), both of which currently approximate against bucket edges that don't align
exactly with the real statutory boundaries. NOT yet reviewed by Gemini. NOT implemented.
Schema-level change -- larger scope than any other proposal from this session.

## Why buckets no longer serve their original purpose for this specific field

Buckets were chosen deliberately, for intake completion speed, not to accommodate genuine
uncertainty about headcount. That reasoning holds less than it might for other fields:
PRV3's `principal_role` values (Owner/founder, C-suite, VP/senior director, HR leader, Board
member) describe people running a diagnostic on their own organization -- they almost
certainly know their real headcount or something very close to it. The completion-speed
benefit buckets provide doesn't require sacrificing precision if the UI pattern itself stays
fast.

## Proposed UX: "About how many employees?" stepper

Replaces the six-value dropdown with a number input styled to feel like an estimate, not a
data-entry task -- framing ("about how many") plus +/- stepper controls rather than a bare
numeric field, softening the precision-seeking feel while capturing a real number underneath.
Tapping the displayed number should also allow direct typing, standard pattern, for anyone who
wants to skip stepping entirely.

**Variable increment size, not uniform across the range** -- deliberately matched to where the
real legal thresholds this session found are dense, not evenly spread:
- 1-50: steps of 1 (this is exactly the range containing the ADA/Title VII (15) and FMLA (50)
  thresholds -- precision matters most here)
- 50-250: steps of 5 (covers the OSHA reduction tiers at 25/100/250 and the low end of Title
  VII's damage-cap tiers)
- 250-500: steps of 25 (covers Title VII's remaining tier boundary at 500)
- 500+: steps of 100, capped at a final "1000+" open-ended option

**Precision above ~500 has genuinely diminishing value** -- nothing in any cluster's currently
built threshold logic (Clusters 1, 2, 4, 5) changes behavior above 500 employees; OSHA's
reduction schedule resolves to 0% at 251+, Title VII's damage cap tops out at 500+. The
stepper doesn't need to work hard for precision the underlying legal thresholds don't reward.

## Schema changes

`engine/data/intake.py`'s `INTAKE_FIELDS["headcount"]` changes from a fixed 6-value list to a
numeric field specification (min/max bounds, increment schedule per the ranges above).
`engine/accumulation.py`'s `IntakeData.headcount` changes type from `str` (bucket label) to
`int` (actual or best-estimate headcount).

## What happens to HEADCOUNT_MIDPOINTS and the SUSB-based payroll baseline

This does NOT go away -- it changes role. `friction_tax.py`'s `HEADCOUNT_MIDPOINTS` maps
PRV3's buckets to real Census SUSB employees-per-firm figures, which is a mechanism for
estimating payroll baseline, not a duplicate of the headcount field itself. Real payroll data
is only available at Census bucket resolution, not per-exact-headcount, so this lookup still
needs a bucket. Proposed resolution: keep precise headcount as the source of truth everywhere
threshold logic needs it (Clusters 1, 2, 4, 5's tiers now check the real number directly,
resolving the boundary-uncertainty problem this proposal originated from), and derive a bucket
internally via simple range logic wherever Census-bucket-resolution data is the only available
source (the SUSB-based payroll baseline specifically). One field, two uses -- precise for
threshold checks, bucketed-on-the-fly for payroll-baseline lookup.

## What this simplifies once implemented

- Clusters 1 and 2: the ADA/Title VII (15) and FMLA (50) coverage-threshold uncertainty found
  in this session's applicability pass resolves completely -- a precise number is either above
  or below each threshold, no ambiguity.
- Cluster 4: Title VII's headcount-tiered damage caps (50K/100K/200K/300K) apply exactly
  instead of approximating against bucket edges that don't align with the real 100/200/500
  boundaries.
- Cluster 5: OSHA's size-based penalty-reduction schedule (70%/40%/20%/0% at
  25/100/250) applies exactly instead of approximating.

## Open questions

1. Does `web/lib/types.ts`'s `IntakeEcho` (client-facing output type) need updating to echo a
   precise number instead of a bucket label -- and if so, is showing an exact headcount back
   to the client desirable, or should client-facing copy still describe it in bucket-like
   language even though the underlying calculation is now precise?
2. Migration: does this apply only to new intakes going forward, or does existing stored
   bucket-based intake data need any backfill/handling?
3. Does the PAYROLL_BASELINE_GRID (54-cell headcount x industry composite-key grid, per the
   Tier 3 friction tax work) need its own bucket-derivation logic built, or does it already
   have one to adapt from `HEADCOUNT_MIDPOINTS`?
