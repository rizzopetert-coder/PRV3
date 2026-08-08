"""
PRV3 Scoring Engine — Section II
Accumulation Engine

II.1  Prior Probability Initialization
II.2  Vector Accumulation
II.3  Signal Reliability Coefficient Application
II.4  Cosine Similarity and State Ranking

Spec reference: PRV3_Scoring_Architecture_Spec_v1.docx, Section II
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Optional

from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.intake import (
    PRIOR_ADJUSTER_INDEX,
    ROLE_COEFFICIENTS,
    AXIS_MODIFIER_INDEX,
    HIGH_HAZARD_INDUSTRIES,
)

# Empirical noise centroid — per-field mean of accumulated vector across N=1000
# random simulations, seed=42, across the 44 live PHASE_1_QUESTION_SEQUENCE
# questions (web/lib/session-store.ts, read live at generation time) --
# regenerated this session after Q40-Q51 were added (32 -> 44 live questions).
# Original values (37 real questions -- Q03/Q27 were silently unreachable
# under the old range-based generation, not 39 despite the name; see
# tools/_mob.txt Decision Register for the full MC_CENTROID_39/core-
# question-count coupling finding): aptitude_liability 3.9565, aptitude_
# asset 0.6800, authority_liability 5.3601, authority_asset 1.6503,
# alliance_liability 2.9859, alliance_asset 0.1924, attitude_liability
# 4.8137, attitude_asset 0.9795.
# Name intentionally NOT changed to reflect 44 -- separate rename decision
# (Gemini suggested MC_CENTROID_LIVE), not yet signed off by Pete.
# Derived from tools/diag_v21_accumulated_centroid.py. LOCKED.
MC_CENTROID_39: dict = {
    "aptitude_liability":  3.5307,
    "aptitude_asset":      0.5296,
    "authority_liability": 6.2624,
    "authority_asset":     1.3872,
    "alliance_liability":  3.0468,
    "alliance_asset":      0.4396,
    "attitude_liability":  6.3701,
    "attitude_asset":      1.3307,
}

# Field-specific centroid displacement scalars — Path B, Session 27.
# Scales MC_CENTROID_39 per field: mu_focused[f] = MC_CENTROID_39[f] * scalar[f] * (N/44).
# Derived from state_targets coverage per dimension / 44 live questions
# (updated this session -- was /39, see MC_CENTROID_39 comment above).
# Values below are stale pending Step 4 (harness reconvergence) -- not
# updated by this step, per Pete's explicit Step 3 scope.
# Managed by tools/harness_s27_autonomous_calibration.py — do not hand-edit.
# All 1.0 = undamped (current SCD-WCS behavior). Harness writes derived values at round 0.
CENTROID_FIELD_SCALARS = {
    "aptitude_liability": 0.2415,
    "aptitude_asset": 0.4000,
    "authority_liability": 0.2318,
    "authority_asset": 0.4000,
    "alliance_liability": 0.2185,
    "alliance_asset": 0.4000,
    "attitude_liability": 0.3067,
    "attitude_asset": 0.4000,
}


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
    headcount:          int   # precise headcount (engine/data/intake.py's HEADCOUNT_FIELD_SPEC)
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
    if intake_data.headcount < 25 and "the_founders_grip" in priors:
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


def _weighted_cosine_similarity(
    accumulated: dict,
    profile_vector: dict,
    weights: dict,
    fields: list,
) -> float:
    """
    Weighted cosine similarity between accumulated session vector and a state
    profile vector, using per-field salience weights.

    WCS(A, B, W) = sum(W_i * A_i * B_i) / (sqrt(sum(W_i * A_i^2)) * sqrt(sum(W_i * B_i^2)))

    Returns 0.0 if either weighted magnitude is zero (undefined direction).
    """
    weighted_dot   = sum(weights.get(f, 1.0) * accumulated.get(f, 0.0) * profile_vector.get(f, 0.0) for f in fields)
    weighted_mag_a = math.sqrt(sum(weights.get(f, 1.0) * accumulated.get(f, 0.0) ** 2 for f in fields))
    weighted_mag_b = math.sqrt(sum(weights.get(f, 1.0) * profile_vector.get(f, 0.0) ** 2 for f in fields))

    if weighted_mag_a == 0.0 or weighted_mag_b == 0.0:
        return 0.0

    return weighted_dot / (weighted_mag_a * weighted_mag_b)


def compute_session_magnitude(accumulated: dict, fields: list) -> float:
    """L2 norm of the accumulated session vector. Interpretable as session intensity."""
    return math.sqrt(sum(accumulated.get(f, 0.0) ** 2 for f in fields))


def compute_liability_dispersion(accumulated_vector: dict) -> float:
    """
    Normalized Shannon entropy of the four liability fields' relative
    shares -- how evenly liability signal is spread across axes
    (aptitude/authority/alliance/attitude) rather than concentrated in
    one. The same entropy technique engine/checkpoint.py already uses
    for checkpoint routing, reused rather than reinvented. 0.0 =
    liability fully concentrated in one axis (contained); 1.0 =
    perfectly even across all four (maximally dispersed). Negative
    per-field values (individual answer contributions can be signed,
    e.g. authority_liability: -0.15 in engine/data/questions.py) are
    clamped to 0.0 before forming the probability distribution --
    entropy is undefined over negative "probabilities", and a
    net-negative accumulated field means that axis contributed no
    liability signal to disperse, not negative dispersion.

    Returns 0.0 if all four liability fields are non-positive (no
    signal to disperse).

    Extracted from compute_cascade_risk() (Category A) so Category B's
    SPOF vs. Diffuse Causation candidate (engine/output.py) can reuse
    the identical dispersion term without duplicating the entropy math.

    Spec reference: Category A architecture review (Gemini-cleared) --
    Cross-Dimensional Cascade Risk.
    """
    liability_fields = [f for f in DIMENSIONAL_FIELDS if f.endswith("_liability")]
    liability_values = [max(accumulated_vector.get(f, 0.0), 0.0) for f in liability_fields]
    total_liability = sum(liability_values)

    if total_liability <= 0.0:
        return 0.0

    probabilities = [v / total_liability for v in liability_values if v > 0.0]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    max_entropy = math.log2(len(liability_fields))  # log2(4) = 2.0
    dispersion = entropy / max_entropy if max_entropy > 0.0 else 0.0

    # max(0.0, ...) is a floor, not just a sign-cleanup: entropy's
    # -sum(p * log2(p)) produces a signed -0.0 when exactly one axis holds
    # all the signal (log2(1.0) == 0.0), which would otherwise surface as
    # -0.0 in the returned/serialized value.
    return max(0.0, dispersion)


def compute_cascade_risk(accumulated_vector: dict) -> float:
    """
    Cross-Dimensional Cascade Risk (CR) -- Category A, Gemini-reviewed.
    Derived output only: zero new signal collection, zero modification to
    the 8-field accumulation model or rank_states(). A framing input for
    output_synthesis, not a new scored dimension and not threaded into
    accumulated_vector or the ranking pipeline.

    CR = dispersion * intensity, both terms in [0.0, 1.0]:

    dispersion -- compute_liability_dispersion() above. High off-axis
    liability accumulation across MULTIPLE axes indicates the condition
    has already spilled over structurally, not remained contained to a
    single dimension.

    intensity -- session magnitude (compute_session_magnitude(), the same
    L2 norm used elsewhere), normalized against the L2 norm of
    MC_CENTROID_39 -- an already-locked empirical reference (N=1000
    simulations), not an invented threshold -- and saturated at 1.0
    rather than left unbounded.

    A session with wide off-axis spread but low overall signal, or high
    signal concentrated in one axis, both score low; only high signal AND
    high spread scores high.

    Returns 0.0 if all four liability fields are non-positive (no signal
    to disperse) -- dispersion is 0.0 in that case, which forces the
    product to 0.0 regardless of intensity.

    CALIBRATION TARGET: the multiplicative combination and the centroid-
    based intensity normalization are starting hypotheses, not locked
    values -- consistent with this engine's existing convention for
    not-yet-data-validated constants (see MODERATE_PROMINENCE_DELTA,
    SEVERITY_SCORE_NORMALIZATION, etc. elsewhere in this codebase).

    Spec reference: Category A architecture review (Gemini-cleared,
    this session) -- Cross-Dimensional Cascade Risk.
    """
    dispersion = compute_liability_dispersion(accumulated_vector)

    magnitude = compute_session_magnitude(accumulated_vector, list(DIMENSIONAL_FIELDS))
    reference_magnitude = math.sqrt(sum(v ** 2 for v in MC_CENTROID_39.values()))
    intensity = min(magnitude / reference_magnitude, 1.0) if reference_magnitude > 0.0 else 0.0

    # max(0.0, ...) is a floor against the same -0.0 propagation described
    # in compute_liability_dispersion() above.
    return max(0.0, round(dispersion * intensity, 4))


# Bucketing threshold for compute_trajectory()'s direction classification.
# CALIBRATION TARGET -- starting hypothesis, same order of magnitude as
# WEAK_DAMPED_THRESHOLD / MODERATE_PROMINENCE_DELTA elsewhere in this
# codebase. Not yet data-validated.
TRAJECTORY_STABILITY_THRESHOLD: float = 0.20  # CALIBRATION TARGET


def compute_trajectory(
    early_vector: dict,
    late_vector: dict,
    duration_band: Optional[str] = None,
) -> dict:
    """
    Trajectory / Directionality -- Diagnostic Dimension Expansion Step 3.
    Derived output only: zero new signal collection, zero modification to
    the 8-field accumulation model or rank_states(). A framing input for
    output_synthesis, not a new scored dimension -- same convention as
    Cascade Risk and SPOF/Diffuse Causation.

    early_vector / late_vector: independently-accumulated vectors from the
    first half and second half of a session's answered-question sequence
    (position-based split -- answers_log carries no timestamp field, so
    "early/late" means early/late in answer order, not wall-clock time).
    Each is its own scratch accumulation, not cumulative-through-midpoint
    vs. final -- this measures whether the session's SECOND HALF alone
    carried more or less liability signal than its FIRST HALF, not
    whether a running total grew (which contributions being signed would
    make a non-monotonic, misleading read anyway).

    delta -- sum(late 4 liability fields) - sum(early 4 liability fields),
    RAW values, not clamped to 0.0 the way compute_liability_dispersion()
    clamps (that clamp exists because entropy is undefined over negative
    "probabilities" -- a requirement specific to entropy math, not a
    general policy here). Positive: liability signal denser in the
    session's second half than its first. Negative: denser in the first
    half. Same DIMENSIONAL_FIELDS liability-only filtering Cascade Risk
    and compute_liability_dispersion() already use.

    dispersion_delta -- compute_liability_dispersion(late_vector) -
    compute_liability_dispersion(early_vector), the identical Shannon-
    entropy term Cascade Risk and SPOF/Diffuse Causation already use,
    reused rather than reinvented. Positive: liability spread across more
    axes in the second half than the first (broadening). Negative:
    concentrated into fewer axes in the second half (narrowing).

    direction -- delta bucketed against TRAJECTORY_STABILITY_THRESHOLD:
      delta >=  threshold -> "escalating"
      delta <= -threshold -> "decelerating"
      otherwise            -> "stable"

    duration_band -- passthrough only, not blended into delta/direction by
    any formula. Real value ("0_6mo" | "6_18mo" | "18mo_plus") only when a
    severity follow-on collecting it fired this session; None otherwise.
    Reported alongside the intra-session read, not fused with it.

    Spec reference: Diagnostic Dimension Expansion decision record
    (prompts/diagnostic-dimension-expansion.md), Candidate 1.
    """
    liability_fields = [f for f in DIMENSIONAL_FIELDS if f.endswith("_liability")]
    early_sum = sum(early_vector.get(f, 0.0) for f in liability_fields)
    late_sum = sum(late_vector.get(f, 0.0) for f in liability_fields)
    delta = round(late_sum - early_sum, 4)

    dispersion_delta = round(
        compute_liability_dispersion(late_vector) - compute_liability_dispersion(early_vector),
        4,
    )

    if delta >= TRAJECTORY_STABILITY_THRESHOLD:
        direction = "escalating"
    elif delta <= -TRAJECTORY_STABILITY_THRESHOLD:
        direction = "decelerating"
    else:
        direction = "stable"

    return {
        "delta": delta,
        "dispersion_delta": dispersion_delta,
        "direction": direction,
        "duration_band": duration_band,
    }


def rank_states(
    accumulated_vector: dict,
    answered_question_count: int,
    salience_weights: Optional[dict] = None,
) -> list:
    """
    Compute SCD-WCS similarity from accumulated_vector to each state profile vector.
    Return list of StateRanking sorted ascending by distance (rank 1 = best match).

    SCD-WCS — Session-Centroid-Displaced Weighted Cosine Similarity (v21):
      Only the session vector is displaced by the empirical noise centroid
      (scaled to the current question count). Profile vectors remain in their
      native space. This measures the session's deviation from expected noise
      in the direction of each state profile.

      mu_N    = MC_CENTROID_39 * (answered_question_count / 44.0)
      A_d     = accumulated - mu_N     (session: centroid-displaced)
      B       = profile                 (profile: undisplaced, native space)
      sim = WCS(A_d, B, W) if salience_weights else cosine(A_d, B)

    Magnitude guard: if displaced session vector magnitude < 1e-5 (zero-signal
    or exactly-at-centroid session), all states return score 0.0.

    salience_weights: optional dict mapping state_id -> {field: weight_value}.
      When provided, uses weighted cosine similarity per state. When None,
      falls back to standard unweighted cosine similarity.

    Spec reference: Section II.4 (SCD-WCS update, v21)
    """
    fields = list(DIMENSIONAL_FIELDS)
    N = float(answered_question_count)
    scale = N / 44.0

    mu_N = np.array([MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS.get(f, 1.0) * scale for f in fields])
    vec_A = np.array([accumulated_vector.get(f, 0.0) for f in fields])
    vec_A_displaced = vec_A - mu_N

    # Zero-signal or exactly-at-centroid session: no directional information
    if np.linalg.norm(vec_A_displaced) < 1e-5:
        zero_results = [
            StateRanking(rank=0, state_id=sid, distance=1.0, score=0.0)
            for sid in STATE_PROFILES
        ]
        for i, r in enumerate(zero_results):
            r.rank = i + 1
        return zero_results

    results = []
    for sid, profile in STATE_PROFILES.items():
        profile_dict = profile.dimensional_vector.as_dict()
        vec_B = np.array([profile_dict.get(f, 0.0) for f in fields])

        if salience_weights is not None:
            sw = salience_weights.get(sid, {f: 1.0 for f in fields})
            w = np.array([sw.get(f, 1.0) for f in fields])
        else:
            w = np.ones(len(fields))

        num = np.sum(w * vec_A_displaced * vec_B)
        den = (np.sqrt(np.sum(w * vec_A_displaced ** 2)) *
               np.sqrt(np.sum(w * vec_B ** 2)))

        sim = float(num / den) if den > 1e-5 else 0.0
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
        Return full state ranking sorted ascending by distance (1 - similarity).
        Call after all answers have been applied.
        salience_weights: pass SALIENCE_PROFILES from engine.data.salience to
          activate weighted cosine mode. None = unweighted (default).
        """
        return rank_states(self.session.accumulated_vector, len(self.session.answers_applied), salience_weights)

    @property
    def accumulated_vector(self) -> dict:
        return dict(self.session.accumulated_vector)

    @property
    def priors(self) -> dict:
        return dict(self.session.priors)
