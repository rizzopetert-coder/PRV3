"""
PRV3 Scoring Engine — Section II
Accumulation Engine

II.1  Prior Probability Initialization
II.2  Vector Accumulation
II.3  Signal Reliability Coefficient Application
II.4  Euclidean Distance Calculation and State Ranking

Spec reference: PRV3_Scoring_Architecture_Spec_v1.docx, Section II
"""

import math
from dataclasses import dataclass, field
from typing import Optional

from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.intake import (
    PRIOR_ADJUSTER_INDEX,
    ROLE_COEFFICIENTS,
    AXIS_MODIFIER_INDEX,
    HIGH_HAZARD_INDUSTRIES,
)


def _coeff(v: Optional[float]) -> float:
    """Return 1.0 for CALIBRATION_TARGET (None), else the value."""
    return 1.0 if v is None else v


# ── Intake data container ──────────────────────────────────────────────────────

@dataclass
class IntakeData:
    """
    Complete intake form result. All six intake fields.
    Spec reference: Section I.3
    """
    headcount:          str   # from INTAKE_FIELDS["headcount"]
    industry:           str   # from INTAKE_FIELDS["industry"]
    org_type:           str   # from INTAKE_FIELDS["org_type"]
    jurisdictions:      list  # list of state abbreviations, e.g. ["CA", "TX"]
    significant_events: list  # list of event_ids
    principal_role:     str   # from INTAKE_FIELDS["principal_role"]

    @property
    def is_high_hazard(self) -> bool:
        """True when industry triggers the Safety & Wellbeing high-hazard multiplier."""
        return self.industry in HIGH_HAZARD_INDUSTRIES


# ── II.1  Prior Probability Initialization ─────────────────────────────────────

def initialize_priors(intake_data: IntakeData) -> dict:
    """
    Build the initial state probability distribution from intake data.
    Returns {state_id: prior_probability} normalized to sum 1.0.

    Steps:
      1. Equal baseline prior: 1/n across all states.
      2. Significant event multipliers applied to elevated state lists.
      3. Headcount < 25 elevates the_founders_grip (CALIBRATION TARGET value).
      4. Proportional normalization.

    Spec reference: Section II.1
    """
    n = len(STATE_PROFILES)
    priors = {sid: 1.0 / n for sid in STATE_PROFILES}

    # Significant event adjustments (Section I.3.1)
    for event_id in intake_data.significant_events:
        adjuster = PRIOR_ADJUSTER_INDEX.get(event_id)
        if adjuster is None:
            continue
        m = _coeff(adjuster.multiplier)
        for sid in adjuster.elevated_states:
            if sid in priors:
                priors[sid] *= m

    # Headcount < 25: elevate the_founders_grip prior
    if intake_data.headcount == "Under 25" and "the_founders_grip" in priors:
        modifier = AXIS_MODIFIER_INDEX.get("headcount_small_founders_grip")
        if modifier is not None:
            priors["the_founders_grip"] *= _coeff(modifier.multiplier)

    # Proportional normalization — full distribution must sum to 1.0
    total = sum(priors.values())
    if total > 0:
        priors = {sid: v / total for sid, v in priors.items()}

    return priors


# ── II.3  Signal Reliability Coefficient Application ──────────────────────────

def _apply_signal_reliability(contributions: dict, role: str) -> dict:
    """
    Scale one answer's dimensional_contributions by the principal role's
    signal reliability coefficients before accumulation.

    CALIBRATION_TARGET values (None) treated as 1.0 until Phase 1 data
    populates real values.

    Spec reference: Section II.3, coefficient table II.3.1
    """
    coefficients = ROLE_COEFFICIENTS.get(role, ROLE_COEFFICIENTS["Other"])
    return {
        f: contributions.get(f, 0.0) * _coeff(coefficients.get(f))
        for f in DIMENSIONAL_FIELDS
    }


def _apply_axis_modifiers(
    contributions: dict,
    axis_targets: list,
    intake_data: IntakeData,
    original_contributions: Optional[dict] = None,
) -> dict:
    """
    Apply intake-conditioned axis weight modifiers to one answer's
    dimensional_contributions before accumulation.

    Modifiers fire when both the intake condition is met and the answer carries
    the matching axis_target tag. CALIBRATION_TARGET multipliers treated as 1.0.

    Axis targets are set on AnswerOption.axis_targets when questions are written.
    Tags used:
      "Safety & Wellbeing"    — triggers industry_high_hazard (1.2x LOCKED)
      "authority_liability"   — triggers org_type_founder_led (CALIBRATION TARGET)
      "compensation_authority"— triggers jurisdiction_transparency (CALIBRATION TARGET)

    Tags with "_DE" suffix trigger delta overlay before multiplier checks:
      Conditional vector resolved from original_contributions["_conditional"]
      using intake_data, then the tag is normalized (suffix stripped) so
      downstream multipliers stack normally.

    Spec reference: Section I.3.2, applied during Section II.2 accumulation
    """
    result = dict(contributions)

    # _DE delta overlay — resolve conditional vectors before multiplier checks
    de_tags = [t for t in axis_targets if t.endswith("_DE")]
    if de_tags and original_contributions is not None:
        cond = original_contributions.get("_conditional")
        if cond is not None:
            gate = cond.get("logic_gate")
            condition_value = getattr(intake_data, gate, None)
            resolved = cond.get("condition_map", {}).get(condition_value, {})
            result.update(resolved)
        axis_targets = [t[:-3] if t.endswith("_DE") else t for t in axis_targets]

    # industry_high_hazard — 1.2x LOCKED on Safety & Wellbeing liability signals
    if intake_data.industry in HIGH_HAZARD_INDUSTRIES and "Safety & Wellbeing" in axis_targets:
        modifier = AXIS_MODIFIER_INDEX.get("industry_high_hazard")
        m = _coeff(modifier.multiplier) if modifier else 1.0
        for f in DIMENSIONAL_FIELDS:
            if f.endswith("_liability"):
                result[f] = result.get(f, 0.0) * m

    # org_type_founder_led — CALIBRATION TARGET (authority_liability axis)
    if intake_data.org_type == "Founder-led" and "authority_liability" in axis_targets:
        modifier = AXIS_MODIFIER_INDEX.get("org_type_founder_led")
        m = _coeff(modifier.multiplier) if modifier else 1.0
        result["authority_liability"] = result.get("authority_liability", 0.0) * m

    # jurisdiction_transparency — CALIBRATION TARGET (compensation + authority)
    if "compensation_authority" in axis_targets:
        from engine.data.jurisdiction import resolve_jurisdiction_flags
        flags = resolve_jurisdiction_flags(intake_data.jurisdictions)
        if flags.get("transparency"):
            modifier = AXIS_MODIFIER_INDEX.get("jurisdiction_transparency")
            m = _coeff(modifier.multiplier) if modifier else 1.0
            result["authority_liability"] = result.get("authority_liability", 0.0) * m

    return result


# ── II.2  Vector Accumulation ─────────────────────────────────────────────────

@dataclass
class AccumulationSession:
    """
    Mutable state for one scoring run.

    accumulated_vector: element-wise sum of all applied answer contributions.
    priors: initial state probability distribution from II.1 (static after init).
    answers_applied: ordered list of question_ids accumulated this session.

    Spec reference: Section II.2
    """
    accumulated_vector: dict = field(default_factory=lambda: {
        f: 0.0 for f in DIMENSIONAL_FIELDS
    })
    priors:            dict = field(default_factory=dict)
    answers_applied:   list = field(default_factory=list)


def accumulate_answer(
    session: AccumulationSession,
    answer_option,
    intake_data: IntakeData,
    question_id: str = "",
) -> None:
    """
    Apply one AnswerOption's dimensional_contributions to the session's
    accumulated_vector. Signal reliability coefficients and axis modifiers
    applied before addition. Mutates session in place.

    For multi-select questions, call once per selected option.

    Spec reference: Section II.2 and II.3
    """
    contributions = dict(answer_option.dimensional_contributions)
    axis_targets = getattr(answer_option, "axis_targets", [])

    # II.3 — signal reliability coefficient (role-based observational proximity)
    contributions = _apply_signal_reliability(contributions, intake_data.principal_role)

    # I.3.2 — axis modifiers (intake-conditioned signal scaling)
    contributions = _apply_axis_modifiers(
        contributions, axis_targets, intake_data,
        original_contributions=answer_option.dimensional_contributions,
    )

    # II.2 — element-wise addition to accumulated vector
    for f in DIMENSIONAL_FIELDS:
        session.accumulated_vector[f] += contributions.get(f, 0.0)

    if question_id:
        session.answers_applied.append(question_id)


# ── II.4  Cosine Similarity and State Ranking ─────────────────────────────────

@dataclass
class StateRanking:
    """
    One state's similarity result against the accumulated answer vector.

    rank:     1 = closest match (ascending by distance = descending by score)
    distance: 1 - cosine_similarity, range 0–2; 0 = identical direction
    score:    cosine similarity, range [-1, 1]; higher = stronger directional match

    Spec reference: Section II.4
    """
    rank:     int
    state_id: str
    distance: float
    score:    float


def _cosine_similarity(accumulated: dict, profile_vector: dict, fields: list) -> float:
    """
    Compute cosine similarity between accumulated session vector and a state
    profile vector across the 8 dimensional fields.

    Returns float in [-1.0, 1.0]. Returns 0.0 if either vector has zero magnitude
    (undefined cosine — treated as no directional signal).

    In practice, state profiles are always non-zero (minimum 0.25 per field).
    Accumulated vectors approach zero only on fully neutral (all-F) sessions.
    SEVER-05 signed delta (authority_asset: -0.30) can produce negative field
    values — cosine similarity handles this correctly; scores may be slightly
    negative for sessions with strong SEVER-05 activation against profile direction.
    """
    dot = sum(accumulated.get(f, 0.0) * profile_vector.get(f, 0.0) for f in fields)
    mag_a = math.sqrt(sum(accumulated.get(f, 0.0) ** 2 for f in fields))
    mag_b = math.sqrt(sum(profile_vector.get(f, 0.0) ** 2 for f in fields))

    if mag_a < 1e-10 or mag_b < 1e-10:
        return 0.0  # undefined — no directional signal

    return dot / (mag_a * mag_b)


def compute_session_magnitude(accumulated: dict, fields: list) -> float:
    """L2 norm of the accumulated session vector. Interpretable as session intensity."""
    return math.sqrt(sum(accumulated.get(f, 0.0) ** 2 for f in fields))


def rank_states(
    accumulated_vector: dict,
    salience_weights: Optional[dict] = None,
) -> list:
    """
    Compute cosine similarity from accumulated_vector to each state profile vector.
    Return list of StateRanking sorted ascending by distance (rank 1 = best match).

    distance = 1 - cosine_similarity, so rank 1 has the smallest distance and
    the highest cosine similarity score.

    salience_weights: reserved for future per-state per-field weighting.
      CALIBRATION TARGET — not applied in cosine mode.

    Spec reference: Section II.4
    """
    fields = list(DIMENSIONAL_FIELDS)
    results = []
    for sid, profile in STATE_PROFILES.items():
        profile_vec = profile.dimensional_vector.as_dict()
        sim = _cosine_similarity(accumulated_vector, profile_vec, fields)
        d = 1.0 - sim
        results.append(StateRanking(rank=0, state_id=sid, distance=d, score=sim))

    results.sort(key=lambda r: r.distance)
    for i, r in enumerate(results):
        r.rank = i + 1

    return results


# ── AccumulationEngine ─────────────────────────────────────────────────────────

class AccumulationEngine:
    """
    Orchestrates a complete Section II accumulation run.

    Usage:
        engine = AccumulationEngine(intake_data)
        engine.apply_answer(answer_option, question_id)  # once per answer
        rankings = engine.rank()

    For multi-select questions, call apply_answer once per selected option.
    For narrative modulation (Section IV), apply_answer with the LLM-weighted
    answer option when confidence threshold is met.

    Spec reference: Section II (all subsections)
    """

    def __init__(self, intake_data: IntakeData):
        self.intake_data = intake_data
        self.session = AccumulationSession(
            priors=initialize_priors(intake_data),
        )

    def apply_answer(self, answer_option, question_id: str = "") -> None:
        """Accumulate one answer option. Call once per selected answer."""
        accumulate_answer(self.session, answer_option, self.intake_data, question_id)

    def rank(self, salience_weights: Optional[dict] = None) -> list:
        """
        Return full state ranking sorted ascending by Euclidean distance.
        Call after all answers have been applied.
        """
        return rank_states(self.session.accumulated_vector, salience_weights)

    @property
    def accumulated_vector(self) -> dict:
        return dict(self.session.accumulated_vector)

    @property
    def priors(self) -> dict:
        return dict(self.session.priors)
