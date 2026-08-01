"""
PRV3 Scoring Engine -- Output Layer
Friction Tax Computation

Computes an estimated financial consequence range for the identified
organizational state cluster. All calibration values are flagged
CALIBRATION TARGET until Pete populates from source research.

Output: {"low": float, "high": float, "currency": "USD"}
  high = low * 1.4  (range spread, LOCKED)

Severity scalars (LOCKED):
  EMERGING:    0.6
  ENTRENCHED:  1.0
  ENDEMIC:     1.4

Payroll baseline architecture (approved 2026-07-29, Gemini-proposed,
Pete-approved -- see prompts/friction-tax-architecture-decision.md):
  PAYROLL_BASELINE_GRID is keyed by (headcount, industry), 54 cells (6
  IntakeData.headcount buckets x 9 IntakeData.industry categories,
  confirmed against the live engine/data/intake.py INTAKE_FIELDS).
  ORG_TYPE_SCALARS applies as a standalone multiplicative scalar on top
  of the grid lookup, not a third grid axis (5 x 9 x 6 = 270 cells was
  rejected as not researchable -- see prompts/friction-tax-band-
  segmentation.md). This supersedes the older flat headcount-only
  _ORG_SIZE_BANDS structure and its legacy key format ("1_to_25" etc.,
  which never matched IntakeData.headcount's real values). See also
  prompts/friction-tax-unit-decision.md (payroll basis, not revenue).

Source research flagged:
  McKinsey & Company -- leadership dysfunction cost benchmarks
  SHRM -- HR failure / turnover cost studies
  Gallup -- engagement / productivity loss quantification
  Peer-reviewed literature -- organizational dysfunction financial impact

Spec reference: PRV3 Output Layer Brief -- Step 2
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# -- Severity scalars (LOCKED) --------------------------------------------------

SEVERITY_SCALAR: dict[str, float] = {
    "Emerging":    0.6,
    "Entrenched":  1.0,
    "Endemic":     1.4,
}

_DEFAULT_SEVERITY_SCALAR: float = 1.0


# -- Payroll baseline grid -------------------------------------------------------
# Keyed by (headcount, industry), using IntakeData's real string values
# directly (engine/data/intake.py's INTAKE_FIELDS) -- not a separate
# internal bucket format. 6 headcount buckets x 9 industries = 54 cells.
# CALIBRATION TARGET -- all payroll_floor_annual values require population
# from source research. Payroll basis, not revenue -- see
# prompts/friction-tax-unit-decision.md.

HEADCOUNT_BUCKETS: tuple[str, ...] = (
    "Under 25", "25-99", "100-249", "250-499", "500-999", "1000+",
)

INDUSTRIES: tuple[str, ...] = (
    "Professional Services",
    "Healthcare & Life Sciences",
    "Financial Services",
    "Technology",
    "Manufacturing & Industrial",
    "Retail & Hospitality",
    "Nonprofit & Education",
    "Government & Public Sector",
    "Other",
)


@dataclass(frozen=True)
class PayrollBaselineEntry:
    """One cell of the payroll baseline grid."""
    payroll_floor_annual: Optional[float]  # CALIBRATION TARGET
    source: Optional[str]                  # named benchmark/study, None until populated
    citation_id: Optional[str]             # cross-reference key into a future citations table


PAYROLL_BASELINE_GRID: dict[tuple[str, str], PayrollBaselineEntry] = {
    (headcount, industry): PayrollBaselineEntry(
        payroll_floor_annual=None,
        source=None,
        citation_id=None,
    )
    for headcount in HEADCOUNT_BUCKETS
    for industry in INDUSTRIES
}


# -- Org type scalar --------------------------------------------------------------
# Standalone multiplicative scalar applied to the grid lookup result, not a
# third grid axis. Keys match IntakeData.org_type / engine/data/intake.py's
# INTAKE_FIELDS["org_type"]. CALIBRATION TARGET -- all values require
# population from source research.

ORG_TYPE_SCALARS: dict[str, Optional[float]] = {
    "Founder-led":                            None,  # CALIBRATION TARGET
    "PE or VC-backed":                        None,  # CALIBRATION TARGET
    "Privately held professional leadership": None,  # CALIBRATION TARGET
    "Nonprofit":                               None,  # CALIBRATION TARGET
    "Publicly traded":                        None,  # CALIBRATION TARGET
    "Government":                              None,  # CALIBRATION TARGET
}


# -- State multiplier table -------------------------------------------------------
# Per-state friction multiplier applied to the adjusted payroll baseline
# (payroll basis, not revenue -- see prompts/friction-tax-unit-decision.md).
# All values CALIBRATION TARGET -- populated from source research.
# Keys: state_id strings matching engine/data/states.py registry (57 states).

STATE_MULTIPLIERS: dict[str, Optional[float]] = {
    "the_unformed_leader":              None,  # CALIBRATION TARGET
    "the_overloaded_manager":           None,  # CALIBRATION TARGET
    "the_dormant_talent":               None,  # CALIBRATION TARGET
    "built_to_fail":                    None,  # CALIBRATION TARGET
    "the_undefined_role":               None,  # CALIBRATION TARGET
    "the_paper_tiger":                  None,  # CALIBRATION TARGET
    "the_founders_grip":                None,  # CALIBRATION TARGET
    "the_exposed":                      None,  # CALIBRATION TARGET
    "the_uninitiated":                  None,  # CALIBRATION TARGET
    "leadership_continuity_risk":       None,  # CALIBRATION TARGET
    "hr_capture":                       None,  # CALIBRATION TARGET
    "decision_paralysis":               None,  # CALIBRATION TARGET
    "the_policy_lag":                   None,  # CALIBRATION TARGET
    "the_unexamined_algorithm":         None,  # CALIBRATION TARGET
    "heard_and_ignored":                None,  # CALIBRATION TARGET
    "the_tolerated_violation":          None,  # CALIBRATION TARGET
    "dueling_narratives":               None,  # CALIBRATION TARGET
    "the_unsolved_problem":             None,  # CALIBRATION TARGET
    "transition_paralysis":             None,  # CALIBRATION TARGET
    "paper_shield":                     None,  # CALIBRATION TARGET
    "the_lost_map":                     None,  # CALIBRATION TARGET
    "invisible_influence_architecture": None,  # CALIBRATION TARGET
    "pay_exposure":                     None,  # CALIBRATION TARGET
    "the_pay_fog":                      None,  # CALIBRATION TARGET
    "the_fracture":                     None,  # CALIBRATION TARGET
    "the_second_close":                 None,  # CALIBRATION TARGET
    "silosolation":                     None,  # CALIBRATION TARGET
    "the_suppression_filter":           None,  # CALIBRATION TARGET
    "the_arbitrary_standard":           None,  # CALIBRATION TARGET
    "decision_blindness":               None,  # CALIBRATION TARGET
    "the_untouchable":                  None,  # CALIBRATION TARGET
    "what_nobody_says":                 None,  # CALIBRATION TARGET
    "leadership_deafness":              None,  # CALIBRATION TARGET
    "the_diversity_ceiling":            None,  # CALIBRATION TARGET
    "culture_drift":                    None,  # CALIBRATION TARGET
    "identity_erosion":                 None,  # CALIBRATION TARGET
    "the_culture_that_wasnt":           None,  # CALIBRATION TARGET
    "the_burned_credibility":           None,  # CALIBRATION TARGET
    "invisible_burnout":                None,  # CALIBRATION TARGET
    "the_basement_standard":            None,  # CALIBRATION TARGET
    "the_inside_track":                 None,  # CALIBRATION TARGET
    "narrative_lock":                   None,  # CALIBRATION TARGET
    "groundhog_day":                    None,  # CALIBRATION TARGET
    "the_wrong_reward":                 None,  # CALIBRATION TARGET
    "the_unreported_hazard":            None,  # CALIBRATION TARGET
    "the_unlocked_door":                None,  # CALIBRATION TARGET
    "the_broken_compass":               None,  # CALIBRATION TARGET

    # -- Taxonomy expansion (Session 67) -----------------------------------------
    "invisible_performance_management":  None,  # CALIBRATION TARGET
    "compression_crisis":                None,  # CALIBRATION TARGET
    "sequential_decision_blindness":     None,  # CALIBRATION TARGET
    "disparate_impact_architecture":     None,  # CALIBRATION TARGET
    "planning_authority_gap":            None,  # CALIBRATION TARGET
    "distributed_culture_fragmentation": None,  # CALIBRATION TARGET
    "wellbeing_theater":                 None,  # CALIBRATION TARGET
    "human_displacement_anxiety":        None,  # CALIBRATION TARGET
    "motivational_architecture_failure": None,  # CALIBRATION TARGET
    "cultural_overtime":                 None,  # CALIBRATION TARGET
}

_DEFAULT_MULTIPLIER: float = 0.0


# -- Core computation ---------------------------------------------------------------

def compute_friction_tax(
    state_ids: list[str],
    severity_tier: str,
    org_size: str,
    industry: str,
    org_type: str,
) -> dict:
    """
    Compute a friction tax estimate for a state cluster.

    Parameters:
      state_ids:     list of identified state IDs (from identified_states)
      severity_tier: "Emerging" | "Entrenched" | "Endemic"
      org_size:      IntakeData.headcount value (e.g. "100-249")
      industry:      IntakeData.industry value
      org_type:      IntakeData.org_type value

    Returns:
      {
        "low": float | None,
        "high": float | None,     # low * 1.4 when calibrated
        "currency": "USD",
        "org_size_label": str,
        "severity_scalar": float,
        "calibration_complete": bool,
      }

    Sequence: (1) look up (org_size, industry) in PAYROLL_BASELINE_GRID,
    (2) apply ORG_TYPE_SCALARS[org_type] to the grid result, (3) compute
    mean_multiplier via the existing, unchanged averaging logic across
    state_ids, (4) apply severity_scalar (unchanged, LOCKED), (5)
    low = adjusted_baseline * mean_multiplier * severity_scalar,
    high = low * 1.4 (unchanged, LOCKED).

    Returns low=None, high=None, calibration_complete=False when any
    required value is a CALIBRATION TARGET or the (org_size, industry)
    pair isn't a recognized grid cell. Downstream renderer treats this as
    "estimate pending calibration."
    """
    grid_entry = PAYROLL_BASELINE_GRID.get((org_size, industry))
    payroll_floor = grid_entry.payroll_floor_annual if grid_entry is not None else None
    org_type_scalar = ORG_TYPE_SCALARS.get(org_type)
    severity_scalar = SEVERITY_SCALAR.get(severity_tier, _DEFAULT_SEVERITY_SCALAR)

    state_multiplier_values = [
        STATE_MULTIPLIERS.get(sid, _DEFAULT_MULTIPLIER)
        for sid in state_ids
    ]

    calibration_complete = (
        payroll_floor is not None
        and org_type_scalar is not None
        and bool(state_ids)
        and all(v is not None for v in state_multiplier_values)
    )

    if not calibration_complete:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "org_size_label": org_size,
            "severity_scalar": severity_scalar,
            "calibration_complete": False,
        }

    adjusted_baseline = payroll_floor * org_type_scalar  # type: ignore[operator]
    mean_multiplier = sum(state_multiplier_values) / len(state_multiplier_values)  # type: ignore[arg-type]

    low = round(adjusted_baseline * mean_multiplier * severity_scalar, 2)
    high = round(low * 1.4, 2)

    return {
        "low": low,
        "high": high,
        "currency": "USD",
        "org_size_label": org_size,
        "severity_scalar": severity_scalar,
        "calibration_complete": True,
    }
