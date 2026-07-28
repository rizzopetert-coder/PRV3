"""
PRV3 Scoring Engine — Output Layer
Friction Tax Computation

Computes an estimated financial consequence range for the identified
organizational state cluster. All multiplier values are flagged
CALIBRATION TARGET until Pete populates from source research.

Output: {"low": float, "high": float, "currency": "USD"}
  high = low * 1.4  (range spread, LOCKED)

Severity scalars (LOCKED):
  EMERGING:    0.6
  ENTRENCHED:  1.0
  ENDEMIC:     1.4

Source research flagged:
  McKinsey & Company — leadership dysfunction cost benchmarks
  SHRM — HR failure / turnover cost studies
  Gallup — engagement / productivity loss quantification
  Peer-reviewed literature — organizational dysfunction financial impact

Spec reference: PRV3 Output Layer Brief — Step 2
"""

from __future__ import annotations

from typing import Optional


# ── Severity scalars (LOCKED) ──────────────────────────────────────────────────

SEVERITY_SCALAR: dict[str, float] = {
    "Emerging":    0.6,
    "Entrenched":  1.0,
    "Endemic":     1.4,
}

_DEFAULT_SEVERITY_SCALAR: float = 1.0


# ── Org size bands ─────────────────────────────────────────────────────────────
# Maps headcount intake strings to annual payroll proxy bands used in
# friction tax computation. Payroll basis, not revenue -- see
# prompts/friction-tax-unit-decision.md.
# CALIBRATION TARGET — all band_low values require population from source research.

_ORG_SIZE_BANDS: dict[str, dict] = {
    "1_to_25": {
        "label": "Micro (1–25)",
        "band_low": None,   # CALIBRATION TARGET
    },
    "26_to_100": {
        "label": "Small (26–100)",
        "band_low": None,   # CALIBRATION TARGET
    },
    "101_to_500": {
        "label": "Mid-size (101–500)",
        "band_low": None,   # CALIBRATION TARGET
    },
    "501_to_2500": {
        "label": "Large (501–2,500)",
        "band_low": None,   # CALIBRATION TARGET
    },
    "2501_plus": {
        "label": "Enterprise (2,501+)",
        "band_low": None,   # CALIBRATION TARGET
    },
}

_FALLBACK_BAND: dict = {"label": "Unknown", "band_low": None}


# ── State multiplier table ─────────────────────────────────────────────────────
# Per-state friction multiplier applied to the org size band_low (payroll
# basis, not revenue -- see prompts/friction-tax-unit-decision.md).
# All values CALIBRATION TARGET — populated from source research.
# Keys: state_id strings matching engine/data/states.py registry (47 states).

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

    # ── Taxonomy expansion (Session 67) ──────────────────────────────────────
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


# ── Band resolution ────────────────────────────────────────────────────────────

def _resolve_band(org_size: str) -> dict:
    """Return the org size band dict for a headcount/org_size string."""
    return _ORG_SIZE_BANDS.get(org_size, _FALLBACK_BAND)


# ── Core computation ───────────────────────────────────────────────────────────

def compute_friction_tax(
    state_ids: list[str],
    severity_tier: str,
    org_size: str,
) -> dict:
    """
    Compute a friction tax estimate for a state cluster.

    Parameters:
      state_ids:     list of identified state IDs (from identified_states)
      severity_tier: "Emerging" | "Entrenched" | "Endemic"
      org_size:      headcount band string from intake (e.g. "101_to_500")

    Returns:
      {
        "low": float | None,
        "high": float | None,     # low * 1.4 when calibrated
        "currency": "USD",
        "org_size_label": str,
        "severity_scalar": float,
        "calibration_complete": bool,
      }

    Returns low=None, high=None, calibration_complete=False when any required
    value is a CALIBRATION TARGET. Downstream renderer treats this as
    "estimate pending calibration."
    """
    band = _resolve_band(org_size)
    band_low = band["band_low"]
    severity_scalar = SEVERITY_SCALAR.get(severity_tier, _DEFAULT_SEVERITY_SCALAR)

    state_multiplier_values = [
        STATE_MULTIPLIERS.get(sid, _DEFAULT_MULTIPLIER)
        for sid in state_ids
    ]

    calibration_complete = (
        band_low is not None
        and bool(state_ids)
        and all(v is not None for v in state_multiplier_values)
    )

    if not calibration_complete:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "org_size_label": band["label"],
            "severity_scalar": severity_scalar,
            "calibration_complete": False,
        }

    mean_multiplier = sum(state_multiplier_values) / len(state_multiplier_values)  # type: ignore[arg-type]

    low = round(band_low * mean_multiplier * severity_scalar, 2)
    high = round(low * 1.4, 2)

    return {
        "low": low,
        "high": high,
        "currency": "USD",
        "org_size_label": band["label"],
        "severity_scalar": severity_scalar,
        "calibration_complete": True,
    }
