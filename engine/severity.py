"""
PRV3 Scoring Engine — Section V
Severity Engine

V.1  Severity Accumulation Inputs
V.2  Multiplicative Interaction Rule and Endemic Cap
V.3  Severity Tier Behavioral Anchors

Severity accumulation is independent and orthogonal from dimensional vector
accumulation. It operates on conditional severity follow-on question answers
(SEVER-01 through SEVER-12) and produces a severity tier classification.

Spec reference: PRV3_Scoring_Architecture_Spec_v1.docx, Section V
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ── Duration band weights — LOCKED ─────────────────────────────────────────────
# Spec reference: Section V.1

DURATION_WEIGHTS: dict[str, float] = {
    "0_6mo":     1.0,  # LOCKED
    "6_18mo":    1.5,  # LOCKED
    "18mo_plus": 2.0,  # LOCKED
}

DURATION_BAND_LABELS: dict[str, str] = {
    "0_6mo":     "0–6 months",
    "6_18mo":    "6–18 months",
    "18mo_plus": "18+ months",
}

# ── Population band weights — CALIBRATION TARGET ───────────────────────────────
# Spec reference: Section V.1

POPULATION_WEIGHTS: dict[str, Optional[float]] = {
    "under_10pct": None,  # CALIBRATION TARGET
    "10_30pct":    None,  # CALIBRATION TARGET
    "30pct_plus":  None,  # CALIBRATION TARGET
}

POPULATION_BAND_LABELS: dict[str, str] = {
    "under_10pct": "<10% of headcount",
    "10_30pct":    "10–30% of headcount",
    "30pct_plus":  "30%+ of headcount",
}

# ── Additive input weights — CALIBRATION TARGET ────────────────────────────────
# Spec reference: Section V.1
# "Prior failed resolution attempts carries highest weight of all inputs."

PRIOR_FAILED_RESOLUTION_WEIGHT: Optional[float] = None   # CALIBRATION TARGET — highest weight
FINANCIAL_INDICATOR_WEIGHT:      Optional[float] = None   # CALIBRATION TARGET
NAMED_CONDITION_WEIGHT:          Optional[float] = None   # CALIBRATION TARGET

# ── Band thresholds — CALIBRATION TARGET ───────────────────────────────────────
# Spec reference: Section V.2
# Score 0.0–EMERGING_MAX  → Emerging
# Score EMERGING_MAX–ENDEMIC_MIN → Entrenched
# Score ENDEMIC_MIN–1.0   → Endemic

EMERGING_MAX:  Optional[float] = None  # CALIBRATION TARGET (called X in spec)
ENTRENCHED_MAX: Optional[float] = None  # CALIBRATION TARGET (called Y in spec)

# Fallback thresholds used when calibration targets are None.
# Set conservatively — Phase 1 data will replace these.
_EMERGING_MAX_DEFAULT:   float = 0.33
_ENTRENCHED_MAX_DEFAULT: float = 0.66

# ── Narrative severity ceiling — LOCKED ────────────────────────────────────────
# Spec reference: Section V.2 and Section IV.2
# "Narrative modulation can increase severity by a maximum of 25 severity points
#  (on a normalized 0–100 scale). Applied at output stage after severity calculation."

NARRATIVE_SEVERITY_CEILING_POINTS: float = 25.0  # LOCKED — on 0–100 scale

# ── Severity score normalization — CALIBRATION TARGET ──────────────────────────
# The raw severity score (sum of multiplicative + additive contributions) is
# divided by this factor and multiplied by 100 to produce the 0–100 output score.
# Phase 1 reverse-calibration (from clearly-Entrenched and clearly-Endemic test
# profiles) sets the real value.

SEVERITY_SCORE_NORMALIZATION: Optional[float] = None  # CALIBRATION TARGET

# Fallback normalization: based on theoretical max of locked inputs only.
# With duration max 2.0, population fallback 1.0, one trigger: raw max = 2.0.
# At 12 triggers max: raw max = 24.0. Use 6.0 as a moderate default (calibration target).
_NORMALIZATION_DEFAULT: float = 6.0  # CALIBRATION TARGET — replace with Phase 1 data


# ── V.3  Severity Tier Behavioral Anchors — LOCKED copy ───────────────────────

SEVERITY_TIER_DESCRIPTIONS: dict[str, str] = {
    "Emerging": (
        "Something is wrong and you can see it. It hasn't settled into the "
        "organization yet. The consequences are coming but haven't fully arrived. "
        "This is the easiest moment to move."
    ),
    "Entrenched": (
        "The condition has been here long enough that people have stopped treating "
        "it as a problem to solve. Workarounds exist. Expectations have adjusted. "
        "The organization has absorbed it without resolving it."
    ),
    "Endemic": (
        "This is how the organization works now. The condition isn't something that "
        "happens inside the organization anymore. It is part of the operating "
        "environment itself. People make decisions inside it without questioning it. "
        "Resolution means changing the environment, not just addressing the condition."
    ),
}

SEVERITY_TIERS = ("Emerging", "Entrenched", "Endemic")


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class SeverityInput:
    """
    Severity follow-on answers for one triggered severity assessment.

    Collected from SEVER-## questions fired after a severity_trigger answer.
    All fields are Optional because individual follow-on questions may cover
    only a subset of the five input types.

    Spec reference: Section V.1
    """
    trigger_question_id:     str            # core question that fired the trigger
    severity_follow_on_id:   str            # SEVER-## question that collected this
    triggering_option_id:    Optional[str]  = None
    # which option (e.g. "C") of the SEVER-## follow-on was selected --
    # required only for follow-ons whose intended state depends on which
    # option fired (SEVER-03, SEVER-07 today); unused/None otherwise.

    duration_band:           Optional[str]  = None
    # "0_6mo" | "6_18mo" | "18mo_plus"

    population_band:         Optional[str]  = None
    # "under_10pct" | "10_30pct" | "30pct_plus"

    prior_failed_resolution: Optional[bool] = None
    # True = condition has been identified and addressed before without resolution

    financial_indicators:    Optional[bool] = None
    # True = financial consequences already present (turnover cost, legal exposure, etc.)

    named_condition:         Optional[bool] = None
    # True = condition has been identified and named internally (leadership awareness)


@dataclass
class SeverityAccumulator:
    """
    Collects all severity inputs across the full question sequence.

    narrative_severity_addition: raw severity contribution from narrative
    modulation (Section IV). Applied before normalization and ceiling check.

    Spec reference: Section V.1 and Section IV.2
    """
    inputs: list = field(default_factory=list)  # list[SeverityInput]
    narrative_severity_addition: float = 0.0    # raw contribution from Section IV


# ── Internal helpers ───────────────────────────────────────────────────────────

def _coeff(v: Optional[float], fallback: float = 1.0) -> float:
    """Return fallback for CALIBRATION_TARGET (None), else the value."""
    return fallback if v is None else v


def _duration_weight(band: Optional[str]) -> float:
    """Return the LOCKED duration weight for a duration band. Defaults to 1.0."""
    if band is None:
        return 1.0
    return DURATION_WEIGHTS.get(band, 1.0)


def _population_weight(band: Optional[str]) -> float:
    """Return population weight for band. CALIBRATION_TARGET → 1.0 placeholder."""
    if band is None:
        return 1.0
    return _coeff(POPULATION_WEIGHTS.get(band))


# ── V.1 + V.2  Severity Scoring ────────────────────────────────────────────────

def compute_raw_severity(accumulator: SeverityAccumulator) -> float:
    """
    Compute the raw (un-normalized) severity score from all collected inputs.

    Formula per trigger (Section V.2):
      multiplicative_component = duration_weight * population_weight * 1.0
      (base_score = 1.0 per trigger — calibrated via normalization factor)

    Additive contributions (CALIBRATION TARGET weights default to 0.0 until
    Phase 1 establishes values):
      + PRIOR_FAILED_RESOLUTION_WEIGHT  if prior_failed_resolution is True
      + FINANCIAL_INDICATOR_WEIGHT      if financial_indicators is True
      + NAMED_CONDITION_WEIGHT          if named_condition is True

    Total = sum of all trigger contributions + narrative_severity_addition.

    Spec reference: Section V.2
    """
    raw = 0.0

    prior_w    = _coeff(PRIOR_FAILED_RESOLUTION_WEIGHT, fallback=0.0)
    financial_w = _coeff(FINANCIAL_INDICATOR_WEIGHT, fallback=0.0)
    named_w    = _coeff(NAMED_CONDITION_WEIGHT, fallback=0.0)

    for inp in accumulator.inputs:
        dur_w = _duration_weight(inp.duration_band)
        pop_w = _population_weight(inp.population_band)

        # Multiplicative kernel (LOCKED formula)
        multiplicative = dur_w * pop_w * 1.0

        # Additive contributions (CALIBRATION TARGET — weights default 0.0)
        additive = 0.0
        if inp.prior_failed_resolution is True:
            additive += prior_w
        if inp.financial_indicators is True:
            additive += financial_w
        if inp.named_condition is True:
            additive += named_w

        raw += multiplicative + additive

    # Narrative contribution added before normalization
    raw += accumulator.narrative_severity_addition

    return raw


def normalize_severity(raw_score: float) -> float:
    """
    Normalize raw severity score to 0–100 scale.

    Divides by SEVERITY_SCORE_NORMALIZATION (CALIBRATION TARGET; uses
    _NORMALIZATION_DEFAULT until Phase 1 data populates the real value),
    then multiplies by 100 and clips to [0.0, 100.0].

    Spec reference: Section V.2 ("normalized 0–100 scale")
    """
    norm = _coeff(SEVERITY_SCORE_NORMALIZATION, fallback=_NORMALIZATION_DEFAULT)
    if norm <= 0.0:
        return 0.0
    score = (raw_score / norm) * 100.0
    return max(0.0, min(score, 100.0))


def classify_severity(score_0_100: float) -> str:
    """
    Map a 0–100 severity score to a severity tier.

    Thresholds (CALIBRATION TARGET; defaults until Phase 1 reverse-calibration):
      Emerging:   0.0  – EMERGING_MAX  (default: 0–33)
      Entrenched: EMERGING_MAX – ENTRENCHED_MAX (default: 33–66)
      Endemic:    ENTRENCHED_MAX – 100.0 (default: 66–100)

    Spec reference: Section V.2 — "Severity cannot exceed Endemic ceiling."
    Endemic is the cap regardless of multiplicative interaction result.
    """
    emerging_max   = _coeff(EMERGING_MAX,   fallback=_EMERGING_MAX_DEFAULT * 100.0)
    entrenched_max = _coeff(ENTRENCHED_MAX, fallback=_ENTRENCHED_MAX_DEFAULT * 100.0)

    if score_0_100 >= entrenched_max:
        return "Endemic"
    if score_0_100 >= emerging_max:
        return "Entrenched"
    return "Emerging"


# ── Per-state severity attribution — locked mapping ────────────────────────────
# Spec reference: prompts/severity-result-per-state-redesign-scope.md, Section 9
# 31 of 32 live SEVER-## IDs locked to their intended state(s), Checkpoint 4
# (this session -- promoted from 19/32, Gemini-confirmed: SEVER-05 added as a
# real split-by-option entry, 11 previously-unmapped flat IDs promoted from
# Section 4's own "Clear" investigation, never formally locked until now).
# Three IDs (SEVER-03, SEVER-05, SEVER-07) require per-option attribution —
# different options of the same follow-on question map to different intended
# states — and are keyed by (severity_follow_on_id, triggering_option_id) in
# SEVERITY_ID_OPTION_STATES instead. Every other locked ID fires into every
# state listed for it (not split/divided across them). SEVER-13 is the sole
# remaining exclusion — "found clean," no state-scoping leak, per the
# original SEVER-19 leak investigation. IDs absent from both tables (SEVER-13
# and any future new SEVER-##) attribute to no state — the qualifying state
# falls back to "Emerging" downstream rather than inheriting an unrelated
# broadcast tier.

SEVERITY_ID_INTENDED_STATES: dict[str, tuple[str, ...]] = {
    "SEVER-01": ("the_diversity_ceiling",),
    "SEVER-02": ("built_to_fail", "the_undefined_role"),
    "SEVER-04": ("the_policy_lag",),
    "SEVER-06": ("invisible_burnout",),
    "SEVER-08": ("silosolation",),
    "SEVER-09": ("the_second_close",),
    "SEVER-10": ("culture_drift", "identity_erosion", "wellbeing_theater"),
    "SEVER-11": ("the_unsolved_problem",),
    "SEVER-12": ("the_diversity_ceiling",),
    "SEVER-14": ("the_fracture",),
    "SEVER-15": ("the_exposed",),
    "SEVER-16": ("the_unreported_hazard",),
    "SEVER-17": ("compression_crisis", "pay_exposure"),
    "SEVER-18": ("dueling_narratives",),
    "SEVER-19": ("invisible_influence_architecture",),
    "SEVER-20": (
        "cultural_overtime", "motivational_architecture_failure",
        "the_basement_standard", "the_inside_track", "the_wrong_reward",
    ),
    "SEVER-21": ("the_paper_tiger",),
    "SEVER-22": ("heard_and_ignored", "hr_capture", "leadership_deafness", "what_nobody_says"),
    "SEVER-23": ("groundhog_day", "the_burned_credibility"),
    "SEVER-24": ("narrative_lock", "the_burned_credibility"),
    "SEVER-25": ("the_basement_standard", "the_inside_track", "the_untouchable"),
    "SEVER-26": ("the_suppression_filter",),
    "SEVER-27": ("disparate_impact_architecture", "heard_and_ignored", "the_tolerated_violation"),
    "SEVER-28": ("the_founders_grip",),
    "SEVER-29": ("the_untouchable",),
    "SEVER-30": ("built_to_fail",),
    "SEVER-31": ("built_to_fail",),
    "SEVER-32": ("the_founders_grip",),
}

# Split-by-option: (severity_follow_on_id, triggering_option_id) -> single state.
SEVERITY_ID_OPTION_STATES: dict[tuple[str, str], str] = {
    ("SEVER-03", "C"): "decision_paralysis",
    ("SEVER-03", "D"): "decision_paralysis",
    ("SEVER-03", "E"): "the_lost_map",
    # SEVER-05 (Checkpoint 4, this session): Q23 fires SEVER-05 from two
    # different options with genuinely distinct content -- option A ("no
    # single departure would be unmanageable") is a confident, untested
    # claim matching paper_shield's exact definition; option D ("people
    # right now whose loss would be genuinely destabilizing") is an
    # acknowledged, current fragility matching leadership_continuity_risk's
    # definition. Verified against real question/option text and state
    # descriptive_prose, Gemini-confirmed.
    ("SEVER-05", "A"): "paper_shield",
    ("SEVER-05", "D"): "leadership_continuity_risk",
    ("SEVER-07", "C"): "leadership_continuity_risk",
    ("SEVER-07", "D"): "the_dormant_talent",
    ("SEVER-07", "E"): "the_unformed_leader",
}


def _intended_states(inp: SeverityInput) -> tuple[str, ...]:
    """
    Return the intended state(s) a single SeverityInput attributes to, per the
    locked mapping. Empty tuple if this input's severity_follow_on_id is not
    yet mapped (unmapped IDs, explicitly-excluded IDs, or an unrecognized ID).
    """
    key = (inp.severity_follow_on_id, inp.triggering_option_id)
    if key in SEVERITY_ID_OPTION_STATES:
        return (SEVERITY_ID_OPTION_STATES[key],)
    return SEVERITY_ID_INTENDED_STATES.get(inp.severity_follow_on_id, ())


@dataclass
class StateSeverity:
    """
    One state's own severity result, computed from only the SeverityInputs
    attributed to it (compute_state_severity()) -- the per-state analog of
    SeverityResult's session-wide tier/score_0_100 pair.

    tier:        Emerging | Entrenched | Endemic -- classify_severity(score_0_100).
    score_0_100: normalize_severity() output for this state's own raw score.
                 NOT the same value as SeverityResult.score_0_100 (the
                 session-wide pooled score) -- this is the per-state figure.

    Checkpoint 1 follow-on (this session, revises already-shipped/Gemini-
    confirmed code): state_severity originally mapped state_id -> a bare
    tier string. Extended to this small object once Checkpoint 3's dry-run
    surfaced a real consistency gap -- the top-level severity.score field
    had no per-state numeric equivalent to resolve against, only tier did.
    Deliberately minimal: no tier_description/raw_score/narrative fields.
    Callers wanting the LOCKED behavioral-anchor copy for a resolved tier
    use SEVERITY_TIER_DESCRIPTIONS[state_severity[id].tier] directly, same
    as SeverityResult.tier_description already does at the session level.

    Spec reference: prompts/severity-result-per-state-redesign-scope.md,
    Section 2 (Checkpoint 1), revised per Checkpoint 3's dry-run finding.
    """
    tier:        str
    score_0_100: float


def compute_state_severity(accumulator: SeverityAccumulator) -> dict[str, StateSeverity]:
    """
    Group accumulator.inputs by intended state (via the locked mapping above)
    and classify each state's own tier AND score independently, using the
    same unmodified normalize_severity()/classify_severity() pipeline as the
    pooled session-wide score. An input mapped to multiple states (e.g.
    SEVER-02 -> built_to_fail, the_undefined_role) contributes to every one
    of them, not divided across them.

    Deliberately excludes narrative_severity_addition — narrative
    modulation's per-state distribution is an open design question (Section
    2 of the redesign scoping doc), not resolved here, and its real
    contribution is confirmed zero in production today regardless.

    States with zero attributed inputs are simply absent from the returned
    dict — callers apply the "Emerging" fallback for any qualifying state
    with no key present, not this function.

    Spec reference: prompts/severity-result-per-state-redesign-scope.md,
    Sections 2/3/9.
    """
    by_state: dict[str, list[SeverityInput]] = {}
    for inp in accumulator.inputs:
        for state_id in _intended_states(inp):
            by_state.setdefault(state_id, []).append(inp)

    state_severity: dict[str, StateSeverity] = {}
    for state_id, state_inputs in by_state.items():
        raw = compute_raw_severity(SeverityAccumulator(inputs=state_inputs))
        score = normalize_severity(raw)
        state_severity[state_id] = StateSeverity(
            tier=classify_severity(score),
            score_0_100=score,
        )

    return state_severity


# ── Narrative severity ceiling enforcement ─────────────────────────────────────

def apply_narrative_severity_ceiling(
    pre_narrative_score: float,
    narrative_addition: float,
    ceiling: float = NARRATIVE_SEVERITY_CEILING_POINTS,
) -> float:
    """
    Enforce the narrative severity ceiling: narrative modulation cannot increase
    the severity score by more than 25 points on the 0–100 scale.

    Parameters:
      pre_narrative_score: severity score (0–100) before narrative contribution
      narrative_addition:  raw score increase from narrative modulation (0–100)
      ceiling:             max allowed increase in points (default 25.0, LOCKED)

    Returns the final severity score after capping, clipped to [0.0, 100.0].

    Spec reference: Section V.2 and Section IV.2 (severity ceiling definition)
    LOCKED.
    """
    capped_addition = min(narrative_addition, ceiling)
    final = pre_narrative_score + capped_addition
    return max(0.0, min(final, 100.0))


# ── SeverityEngine ─────────────────────────────────────────────────────────────

@dataclass
class SeverityResult:
    """
    Complete severity assessment for one scoring session.

    raw_score:                 Un-normalized sum of all severity contributions.
    score_0_100:               Normalized 0–100 scale score (before narrative ceiling).
    score_0_100_with_narrative: Final score after narrative ceiling enforcement.
    tier:                      Emerging | Entrenched | Endemic
    tier_description:          LOCKED behavioral anchor copy from V.3.
    narrative_contribution_0_100: Narrative addition on 0–100 scale.
    narrative_ceiling_applied: True if narrative addition was capped.
    state_severity:            Per-state StateSeverity (tier + score_0_100),
                                keyed by state_id. Only states with at least
                                one attributed input are present; callers
                                apply the "Emerging" tier fallback for any
                                qualifying state with no key present (no
                                score fallback defined -- callers needing a
                                per-state score for an unmapped state have
                                no real value to fall back to). Kept
                                alongside the session-wide fields above, not
                                a replacement for them (backward-compat).

    Spec reference: Section V. Per-state field added per
    prompts/severity-result-per-state-redesign-scope.md, Checkpoint 1;
    widened from dict[str, str] to dict[str, StateSeverity] this session
    (Checkpoint 1 follow-on, revises already-shipped/Gemini-confirmed code).
    """
    raw_score:                    float
    score_0_100:                  float
    score_0_100_with_narrative:   float
    tier:                         str
    tier_description:             str
    narrative_contribution_0_100: float
    narrative_ceiling_applied:    bool
    input_count:                  int
    state_severity:               dict[str, StateSeverity] = field(default_factory=dict)


class SeverityEngine:
    """
    Orchestrates severity accumulation for one scoring session.

    Usage:
        engine = SeverityEngine()
        engine.add_input(SeverityInput(...))   # for each SEVER-## answer
        engine.set_narrative_contribution(raw_addition)  # from Section IV
        result = engine.score()

    Spec reference: Section V (all subsections)
    """

    def __init__(self):
        self.accumulator = SeverityAccumulator()

    def add_input(self, severity_input: SeverityInput) -> None:
        """Record one severity follow-on answer set."""
        self.accumulator.inputs.append(severity_input)

    def set_narrative_contribution(self, raw_addition: float) -> None:
        """
        Set the raw severity contribution from narrative modulation (Section IV).
        raw_addition is on the same raw scale as compute_raw_severity output.
        """
        self.accumulator.narrative_severity_addition = max(0.0, raw_addition)

    def score(self) -> SeverityResult:
        """
        Compute the full severity assessment.

        Steps:
          1. compute_raw_severity from all inputs (without narrative).
          2. normalize_severity to 0–100 (without narrative).
          3. Compute narrative contribution on 0–100 scale.
          4. apply_narrative_severity_ceiling (25-point cap).
          5. classify_severity on final score.

        Spec reference: Section V.2 — narrative ceiling applied at output stage.
        """
        # Score without narrative contribution
        raw_without_narrative = compute_raw_severity(
            SeverityAccumulator(inputs=self.accumulator.inputs, narrative_severity_addition=0.0)
        )
        score_without_narrative = normalize_severity(raw_without_narrative)

        # Narrative contribution on 0-100 scale
        raw_narrative = self.accumulator.narrative_severity_addition
        narrative_0_100 = normalize_severity(raw_narrative)

        # Apply ceiling to narrative contribution
        pre = score_without_narrative
        capped = min(narrative_0_100, NARRATIVE_SEVERITY_CEILING_POINTS)
        final_score = max(0.0, min(pre + capped, 100.0))
        narrative_ceiling_applied = narrative_0_100 > NARRATIVE_SEVERITY_CEILING_POINTS

        tier = classify_severity(final_score)
        state_severity = compute_state_severity(self.accumulator)

        return SeverityResult(
            raw_score=raw_without_narrative + raw_narrative,
            score_0_100=score_without_narrative,
            score_0_100_with_narrative=final_score,
            tier=tier,
            tier_description=SEVERITY_TIER_DESCRIPTIONS[tier],
            narrative_contribution_0_100=capped,
            narrative_ceiling_applied=narrative_ceiling_applied,
            input_count=len(self.accumulator.inputs),
            state_severity=state_severity,
        )
