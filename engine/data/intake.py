"""
PRV3 Scoring Engine — Section I.3
Intake Lookup Tables

Two mechanisms convert intake field answers into scoring adjustments before Q1:

  Mechanism 1 — Prior Probability Adjusters (Section I.3.1)
    Intake field 5 (significant events) elevates selected states' starting priors.
    Exact multiplier values are CALIBRATION TARGETS. The state-selection hypotheses
    are the starting model. Phase 1 test suite data validates and differentiates.

  Mechanism 2 — Axis Weight Modifiers (Section I.3.2)
    Industry, headcount, organization type, and jurisdiction scale how heavily
    the engine interprets specific dimensional axis signals during accumulation.
    They do not change which states are possible — they change signal weighting.

Spec reference: Sections I.3.1 and I.3.2

CALIBRATION TARGET convention: multiplier fields set to None indicate the
value is a calibration target. Engine must treat None as 1.0 (no adjustment)
until Phase 1 data populates the real value.
"""

from dataclasses import dataclass, field
from typing import Optional


CALIBRATION_TARGET = None  # Sentinel — treat as 1.0 until Phase 1 data populates value


# ── Prior Probability Adjusters — Section I.3.1 ────────────────────────────────

@dataclass
class PriorAdjuster:
    """
    For a significant event type, lists the states whose prior probability
    is elevated before Q1. Multiplier is a CALIBRATION TARGET — set to None
    until Phase 1 event-conditioned test profiles establish the real value.

    Application: for each selected event, multiply the listed states' priors
    by the multiplier, then normalize the full distribution to sum 1.0.

    Spec reference: Section I.3.1 and II.1
    """
    event_id:        str         # matches intake field 5 option
    event_label:     str
    elevated_states: list        # list of state_ids
    multiplier:      Optional[float]  # CALIBRATION_TARGET until Phase 1


PRIOR_ADJUSTERS: list[PriorAdjuster] = [
    PriorAdjuster(
        event_id="acquisition_or_merger",
        event_label="Acquisition or merger",
        elevated_states=[
            "the_second_close",
            "identity_erosion",
            "transition_paralysis",
        ],
        multiplier=CALIBRATION_TARGET,
    ),
    PriorAdjuster(
        event_id="external_legal_claim",
        event_label="External legal claim or regulatory inquiry",
        elevated_states=[
            "the_unsolved_problem",
        ],
        multiplier=CALIBRATION_TARGET,
    ),
    PriorAdjuster(
        event_id="restructuring_or_layoff",
        event_label="Restructuring or layoff",
        elevated_states=[
            "transition_paralysis",
            "the_fracture",
            "identity_erosion",
        ],
        multiplier=CALIBRATION_TARGET,
    ),
    PriorAdjuster(
        event_id="rapid_growth",
        event_label="Rapid growth 25%+",
        elevated_states=[
            "built_to_fail",
            "the_founders_grip",
            "silosolation",
        ],
        multiplier=CALIBRATION_TARGET,
    ),
    PriorAdjuster(
        event_id="leadership_departure",
        event_label="Leadership departure or transition",
        elevated_states=[
            "leadership_continuity_risk",
            "the_uninitiated",
        ],
        multiplier=CALIBRATION_TARGET,
    ),
    PriorAdjuster(
        event_id="none",
        event_label="None",
        elevated_states=[],
        multiplier=1.0,  # LOCKED — no adjustment for no-event selection
    ),
]

# Index for O(1) lookup by event_id
PRIOR_ADJUSTER_INDEX: dict[str, PriorAdjuster] = {
    a.event_id: a for a in PRIOR_ADJUSTERS
}


# ── Axis Weight Modifiers — Section I.3.2 ─────────────────────────────────────

@dataclass
class AxisModifier:
    """
    For a given intake field condition, scales how heavily the engine
    interprets a specific dimensional axis during answer accumulation.

    The modifier is applied as a scalar multiplier to the relevant
    dimensional_contributions fields of each answer vector as it is
    accumulated — not as a change to the state profile.

    Spec reference: Section I.3.2
    """
    modifier_id:     str
    intake_field:    str   # "industry" | "headcount" | "org_type" | "jurisdiction"
    condition:       str   # human-readable condition description
    axis_modified:   str   # dimensional field name(s) affected — see note
    multiplier:      Optional[float]  # CALIBRATION_TARGET where None
    notes:           str  = ""


AXIS_MODIFIERS: list[AxisModifier] = [
    AxisModifier(
        modifier_id="industry_high_hazard",
        intake_field="industry",
        condition="Construction or Manufacturing selected",
        axis_modified="Safety & Wellbeing liability signals",
        multiplier=1.2,  # LOCKED per spec Section I.3.2
        notes=(
            "Applies a 1.2x multiplier to answer vector contributions "
            "that target Safety & Wellbeing liability axes. "
            "Status: LOCKED."
        ),
    ),
    AxisModifier(
        modifier_id="headcount_small_founders_grip",
        intake_field="headcount",
        condition="Under 25 selected",
        axis_modified="Prior probability: The Founder's Grip elevated",
        multiplier=CALIBRATION_TARGET,
        notes=(
            "Elevates the_founders_grip prior probability when headcount < 25. "
            "Mechanism: prior adjuster (not axis multiplier — stored here for "
            "documentation completeness). Exact value: CALIBRATION TARGET."
        ),
    ),
    AxisModifier(
        modifier_id="org_type_founder_led",
        intake_field="org_type",
        condition="Founder-led selected",
        axis_modified="authority_liability",
        multiplier=CALIBRATION_TARGET,
        notes=(
            "Elevated Authority-Liability axis signals for founder-led organizations. "
            "Hypothesis: weight is elevated. Exact value: CALIBRATION TARGET. "
            "Phase 1 founder-led organization profiles establish the real value."
        ),
    ),
    AxisModifier(
        modifier_id="jurisdiction_transparency",
        intake_field="jurisdiction",
        condition="Jurisdiction transparency = True (see jurisdiction_table.py)",
        axis_modified="authority_liability (compensation-related signals only)",
        multiplier=1.3,  # Soft hypothesis — CALIBRATION TARGET, see note
        notes=(
            "Adds 1.3x weight to Liability-Authority signals involving compensation "
            "(pay_exposure, the_pay_fog, heard_and_ignored in compensation context). "
            "This is a softer hypothesis than other multipliers — NY pay transparency "
            "law is relatively new and the liability exposure curve is not fully "
            "established. Flag for early revision in calibration. "
            "Status: CALIBRATION TARGET (soft hypothesis)."
        ),
    ),
]

# Index for lookup by modifier_id
AXIS_MODIFIER_INDEX: dict[str, AxisModifier] = {
    m.modifier_id: m for m in AXIS_MODIFIERS
}


# ── Intake field option definitions ───────────────────────────────────────────
# These define the valid values for each intake field.
# Used for validation and routing logic.

INTAKE_FIELDS = {
    "headcount": [
        "Under 25",
        "25-99",
        "100-249",
        "250-499",
        "500-999",
        "1000+",
    ],
    "industry": [
        "Professional Services",
        "Healthcare & Life Sciences",
        "Financial Services",
        "Technology",
        "Manufacturing & Industrial",
        "Retail & Hospitality",
        "Nonprofit & Education",
        "Government & Public Sector",
        "Other",
    ],
    "org_type": [
        "Founder-led",
        "PE or VC-backed",
        "Privately held professional leadership",
        "Nonprofit",
        "Publicly traded",
        "Government",
    ],
    "significant_events": [
        "acquisition_or_merger",
        "restructuring_or_layoff",
        "rapid_growth",
        "leadership_departure",
        "external_legal_claim",
        "none",
    ],
    "principal_role": [
        "Owner or founder",
        "C-suite",
        "VP or senior director",
        "HR leader",
        "Board member",
        "Other",
    ],
}

# Industries that trigger the high-hazard Safety & Wellbeing multiplier
HIGH_HAZARD_INDUSTRIES = {"Manufacturing & Industrial", "Healthcare & Life Sciences"}
# Construction and Logistics are not in the current intake industry list.
# Pending intake list expansion if those industries are added.


# ── Signal reliability coefficient table — Section II.3.1 ─────────────────────
# Located here (intake layer) because principal_role is an intake field.
# Applied during accumulation, not at intake initialization.
# All values are CALIBRATION TARGETS — starting hypotheses from spec II.3.1.

ROLE_COEFFICIENTS: dict[str, dict[str, float]] = {
    "Owner or founder": {
        "aptitude_liability":   1.0,   # CALIBRATION TARGET
        "aptitude_asset":       1.0,   # CALIBRATION TARGET
        "authority_liability":  1.2,   # CALIBRATION TARGET — direct causal proximity
        "authority_asset":      1.2,   # CALIBRATION TARGET
        "alliance_liability":   0.9,   # CALIBRATION TARGET — filtered, above org
        "alliance_asset":       0.9,   # CALIBRATION TARGET
        "attitude_liability":   0.9,   # CALIBRATION TARGET — filtered
        "attitude_asset":       0.9,   # CALIBRATION TARGET
    },
    "C-suite": {
        "aptitude_liability":   1.0,   # CALIBRATION TARGET
        "aptitude_asset":       1.0,   # CALIBRATION TARGET
        "authority_liability":  1.1,   # CALIBRATION TARGET
        "authority_asset":      1.1,   # CALIBRATION TARGET
        "alliance_liability":   1.1,   # CALIBRATION TARGET — broad visibility
        "alliance_asset":       1.1,   # CALIBRATION TARGET
        "attitude_liability":   1.0,   # CALIBRATION TARGET
        "attitude_asset":       1.0,   # CALIBRATION TARGET
    },
    "VP or senior director": {
        "aptitude_liability":   1.1,   # CALIBRATION TARGET — close to team performance
        "aptitude_asset":       1.1,   # CALIBRATION TARGET
        "authority_liability":  1.0,   # CALIBRATION TARGET
        "authority_asset":      1.0,   # CALIBRATION TARGET
        "alliance_liability":   1.0,   # CALIBRATION TARGET
        "alliance_asset":       1.0,   # CALIBRATION TARGET
        "attitude_liability":   1.0,   # CALIBRATION TARGET
        "attitude_asset":       1.0,   # CALIBRATION TARGET
    },
    "HR leader": {
        "aptitude_liability":   1.0,   # CALIBRATION TARGET
        "aptitude_asset":       1.0,   # CALIBRATION TARGET
        "authority_liability":  1.1,   # CALIBRATION TARGET — professional pattern recognition
        "authority_asset":      1.1,   # CALIBRATION TARGET
        "alliance_liability":   1.0,   # CALIBRATION TARGET
        "alliance_asset":       1.0,   # CALIBRATION TARGET
        "attitude_liability":   1.2,   # CALIBRATION TARGET — professional pattern recognition
        "attitude_asset":       1.2,   # CALIBRATION TARGET
    },
    "Board member": {
        "aptitude_liability":   0.8,   # CALIBRATION TARGET — distant from operations
        "aptitude_asset":       0.8,   # CALIBRATION TARGET
        "authority_liability":  1.1,   # CALIBRATION TARGET — governance proximity
        "authority_asset":      1.1,   # CALIBRATION TARGET
        "alliance_liability":   0.9,   # CALIBRATION TARGET
        "alliance_asset":       0.9,   # CALIBRATION TARGET
        "attitude_liability":   0.8,   # CALIBRATION TARGET — distant from culture
        "attitude_asset":       0.8,   # CALIBRATION TARGET
    },
    "Other": {
        "aptitude_liability":   1.0,   # LOCKED — neutral baseline
        "aptitude_asset":       1.0,
        "authority_liability":  1.0,
        "authority_asset":      1.0,
        "alliance_liability":   1.0,
        "alliance_asset":       1.0,
        "attitude_liability":   1.0,
        "attitude_asset":       1.0,
    },
}
