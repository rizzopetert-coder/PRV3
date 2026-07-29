# Friction Tax: Band Architecture Decision

Approved 2026-07-29. Architecture proposed by Gemini, verified
against real code by Claude Code (multi-state averaging logic confirmed
accurate: friction_tax.py:185-206, arithmetic mean across state_ids),
approved by Pete. Follows prompts/friction-tax-unit-decision.md
(payroll-based) and prompts/friction-tax-band-segmentation.md
(headcount x industry primary axis, org_type as secondary modifier).

## Decision

Replace the flat 5-key _ORG_SIZE_BANDS dict with a composite tuple-keyed
registry: Dict[Tuple[str, str], PayrollBaselineEntry], keyed by
(headcount_bucket, industry), 54 cells total (6 real headcount buckets
from IntakeData.headcount x 9 industries from IntakeData.industry).

Headcount buckets (retiring the legacy "1_to_25" style keys, adopting
IntakeData.headcount's real values): "Under 25", "25-99", "100-249",
"250-499", "500-999", "1000+".

Industries (from IntakeData.industry, unchanged, already correct):
Professional Services, Healthcare & Life Sciences, Financial Services,
Technology, Manufacturing & Industrial, Retail & Hospitality, Nonprofit
& Education, Government & Public Sector, Other.

Each PayrollBaselineEntry carries: payroll_floor_annual (Optional[float],
CALIBRATION TARGET until populated), a source-attribution field, and a
citation-id field (exact field names/types at Claude Code's discretion
during implementation, structure only decided here).

org_type is NOT a third grid axis (270 cells not researchable). It is a
standalone multiplicative scalar table, ORG_TYPE_SCALARS: Dict[str,
Optional[float]], 6 entries (Founder-led, PE or VC-backed, Privately
held professional leadership, Nonprofit, Publicly traded, Government),
applied to the grid lookup result: adjusted_baseline = band_low(headcount,
industry) * ORG_TYPE_SCALARS[org_type].

compute_friction_tax() signature gains industry and org_type parameters.
Internal sequence: (1) look up (org_size, industry) in the new grid, flag
calibration_complete = False if None; (2) apply org_type scalar; (3)
compute mean_multiplier via the existing, verified, unchanged averaging
logic across state_ids; (4) apply severity_scalar (unchanged, LOCKED);
(5) low = adjusted_baseline * mean_multiplier * severity_scalar, high =
low * 1.4 (unchanged).

## Rationale
See prompts/friction-tax-band-segmentation.md for why headcount x
industry over org_type as primary axis, and why org_type is a modifier
not a third grid dimension. Composite tuple keys over nested dicts: flat
iteration for citation/audit tooling, avoids KeyError depth traps,
easier static type checking -- Gemini's reasoning, unchallenged as sound
architecture.

## Known gap to address during implementation
The multi-state averaging logic (mean across state_ids) has zero test
coverage for multi-element state_ids lists today -- all 4 existing
test_friction_tax.py calls use single-state lists. Build proper
multi-state test coverage as part of this work, not just signature
updates to the existing 4 tests.

## Status
Architecture approved, not yet built. All PayrollBaselineEntry and
ORG_TYPE_SCALARS values remain None/CALIBRATION TARGET. Actual value
research (the 54-cell grid + 6 org_type scalars) is a separate,
subsequent effort -- likely a Gemini research pass, independently
verified per standing discipline, same as every other figure this
session.
