# Friction Tax Unit Decision

Decided 2026-07-27. Full research trail: this session's conversation
log (web searches on SHRM/Gallup/McKinsey turnover, disengagement, and
organizational-dysfunction cost benchmarks).

## Decision
STATE_MULTIPLIERS represents a percentage of estimated organizational
payroll (not revenue). band_low in _ORG_SIZE_BANDS represents estimated
total payroll for that headcount tier (not a revenue proxy). No change
to field types, table shapes, or compute_friction_tax()'s math
(low = band_low * mean_multiplier * severity_scalar) -- only the
semantic interpretation and the real values to be populated change.

## Why
- SHRM: replacing an employee costs 50-200% of their annual salary
  (converges across many independent citations of SHRM's own published
  figures).
- Gallup: disengaged employees cost roughly 18% of annual salary
  (converges similarly, Gallup's own State of the Global Workplace
  report).
- McKinsey's contribution to this space is a flat dollar range scoped to
  one company-size cohort (median S&P company), not a transferable
  percentage of anything -- doesn't support either unit directly, but
  doesn't contradict payroll-based framing either.
- Revenue-percentage figures found (e.g. "20-30% of revenue") came only
  from low-quality sources with vague "studies show" attribution and
  citations to McKinsey/HBR reports that don't correspond to verifiable
  real publications -- rejected as unreliable by the same standard
  applied to this session's Gemini fabrication findings, not merely
  deprioritized for being less common.

## What needs updating (Task 2, this same session)
- engine/friction_tax.py module docstring: "revenue proxy" language ->
  "payroll proxy" language, wherever band_low is described.
- Inline comment on STATE_MULTIPLIERS describing it as a "per-state
  friction multiplier applied to org size band_low" should clarify
  payroll basis once this doc exists.
- No change to _ORG_SIZE_BANDS or STATE_MULTIPLIERS structure/keys --
  values remain None (CALIBRATION TARGET) until the actual research pass
  populates them.

## Not yet done
Actual population of STATE_MULTIPLIERS (57 states) and band_low (5
bands) with real researched values. That's the next step -- a Gemini
research pass, reconciled and independently verified before any value is
written to the engine, per standing Gemini-verification discipline.
