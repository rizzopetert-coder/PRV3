"""
PRV3 Scoring Engine — Section VI
Output Engine

VI.1  Signal Floor Application
VI.2  Single-State Output Format
VI.3  Multi-State Output Format
VI.4  Private Output Structure
VI.5  Shareable Output Structure

Takes the final state distribution (post-narrative modulation), severity result,
and asset score; applies the signal floor; routes to single or multi-state output.

Spec reference: PRV3_Scoring_Architecture_Spec_v1.docx, Section VI
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from math import sqrt
from typing import Optional

from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS, BASELINE_VALUE, StateProfile
from engine.data.questions import QUESTION_LIBRARY
from engine.accumulation import StateRanking, rank_states, compute_liability_dispersion
from engine.severity import SeverityResult, SEVERITY_TIER_DESCRIPTIONS


# ── VI.1  Signal Floor Constants ───────────────────────────────────────────────

# Tiered signal floor multipliers — RETIRED v21 (absolute threshold replaces multiplicative floor)
# Kept for backward compatibility with compute_signal_floors() and legacy tests.
SIGNAL_FLOOR_MULTIPLIER_AUTHORITY: float = 1.00   # RETIRED v21
SIGNAL_FLOOR_MULTIPLIER_DEFAULT:   float = 1.08   # RETIRED v21
SIGNAL_FLOOR_CEILING:              float = 0.9650 # RETIRED v21

# SCD-WCS floor gate constants — v22
# Hybrid gate: absolute floor + relative margin constraint.
# Both are CALIBRATION TARGETS — set via Session 25 calibration analysis.
SCD_WCS_ALIGNMENT_THRESHOLD: float = -0.4000   # CALIBRATION TARGET — Session 25
SCD_WCS_MARGIN_GATE: float = 0.0500            # CALIBRATION TARGET — Session 25

# Number of randomized simulations for noise baseline calculation. LOCKED.
NOISE_SIMULATION_COUNT: int = 1000  # LOCKED

# Separation threshold: score gap rank-1 minus rank-2 required for single-state
# output. CALIBRATION TARGET — set via Phase 1 ROC analysis.
SEPARATION_THRESHOLD: Optional[float] = None  # CALIBRATION TARGET

# Default separation threshold (used when CALIBRATION_TARGET is None).
# Conservative starting hypothesis; Phase 1 ROC analysis replaces this.
_SEPARATION_THRESHOLD_DEFAULT: float = 0.05  # CALIBRATION TARGET default

# Precomputed noise baseline — RETIRED v21 (SCD-WCS absolute threshold replaces multiplicative floor).
# Kept for score_lift_pct computation in apply_signal_floor(). Do not use for floor gating.
# v24: SCD-WCS, CENTROID_FIELD_SCALARS focus-damped, SALIENCE_PROFILES, full 47-state path. Session 27.
_PRECOMPUTED_NOISE_BASELINE: dict = {
    "built_to_fail":                         0.8512,
    "culture_drift":                         0.8840,
    "decision_blindness":                    0.7700,
    "decision_paralysis":                    0.9199,
    "dueling_narratives":                    0.9199,
    "groundhog_day":                         0.8597,
    "heard_and_ignored":                     0.8911,
    "hr_capture":                            0.8911,
    "identity_erosion":                      0.8717,
    "invisible_burnout":                     0.8597,
    "invisible_influence_architecture":      0.9153,
    "leadership_continuity_risk":            0.9199,
    "leadership_deafness":                   0.7851,
    "narrative_lock":                        0.8717,
    "paper_shield":                          0.9153,
    "pay_exposure":                          0.9199,
    "silosolation":                          0.8059,
    "the_arbitrary_standard":                0.8059,
    "the_basement_standard":                 0.8597,
    "the_broken_compass":                    0.8597,
    "the_burned_credibility":                0.8597,
    "the_culture_that_wasnt":                0.8717,
    "the_diversity_ceiling":                 0.8597,
    "the_dormant_talent":                    0.8898,
    "the_exposed":                           0.8911,
    "the_founders_grip":                     0.8911,
    "the_fracture":                          0.7700,
    "the_inside_track":                      0.8597,
    "the_lost_map":                          0.9199,
    "the_overloaded_manager":                0.8942,
    "the_paper_tiger":                       0.8512,
    "the_pay_fog":                           0.9199,
    "the_policy_lag":                        0.9199,
    "the_second_close":                      0.8059,
    "the_suppression_filter":                0.8381,
    "the_tolerated_violation":               0.8911,
    "the_undefined_role":                    0.8783,
    "the_unexamined_algorithm":              0.9271,
    "the_unformed_leader":                   0.8898,
    "the_uninitiated":                       0.9199,
    "the_unlocked_door":                     0.8717,
    "the_unreported_hazard":                 0.8717,
    "the_unsolved_problem":                  0.8911,
    "the_untouchable":                       0.8201,
    "the_wrong_reward":                      0.8597,
    "transition_paralysis":                  0.9199,
    "what_nobody_says":                      0.8412,
}


# ── VI.1  Noise Baseline Simulation ───────────────────────────────────────────

def compute_noise_baseline(
    n_simulations: int = NOISE_SIMULATION_COUNT,
    random_seed: Optional[int] = None,
) -> dict:
    """
    Compute the noise baseline score for each state by simulating n_simulations
    randomized answer sets through the accumulation and ranking pipeline.

    For each simulation: randomly select one option per core question (Q01–Q39),
    accumulate the contributions with neutral role ("Other"), run rank_states.
    Noise baseline per state = mean similarity score across all simulations.

    When the question library is empty (current build stage): all questions
    contribute zero to the accumulated vector, so all simulations produce the
    same score — the zero-signal baseline. Returns this theoretical baseline
    for each state.

    Signal floor per state = noise_baseline[state_id] × tiered multiplier
    (1.00 for Authority states, 1.15 for all others — see compute_signal_floors).

    Spec reference: Section VI.1 — LOCKED
    """
    if not QUESTION_LIBRARY:
        # No questions: accumulated vector stays at zero for all simulations.
        # Theoretical score: distance from (0,...,0) to (0.25,...,0.25) across
        # all 8 fields = sqrt(8 * 0.25^2) = sqrt(0.5) ≈ 0.7071
        zero_distance = sqrt(len(DIMENSIONAL_FIELDS) * BASELINE_VALUE ** 2)
        baseline_score = 1.0 / (1.0 + zero_distance)
        return {sid: baseline_score for sid in STATE_PROFILES}

    if random_seed is not None:
        random.seed(random_seed)

    # Accumulate score totals across simulations
    score_totals = {sid: 0.0 for sid in STATE_PROFILES}

    from engine.data.questions import CORE_SEQUENCE_IDS

    for _ in range(n_simulations):
        accumulated = {f: 0.0 for f in DIMENSIONAL_FIELDS}

        for qid in CORE_SEQUENCE_IDS:
            q = QUESTION_LIBRARY.get(qid)
            if q is None or not q.answer_options:
                continue
            option = random.choice(q.answer_options)
            for f in DIMENSIONAL_FIELDS:
                accumulated[f] += option.dimensional_contributions.get(f, 0.0)

        rankings = rank_states(accumulated, len(CORE_SEQUENCE_IDS))
        for r in rankings:
            score_totals[r.state_id] += r.score

    return {sid: score_totals[sid] / n_simulations for sid in STATE_PROFILES}


def compute_signal_floors(noise_baseline: dict) -> dict:
    """
    Compute per-state signal floor using tiered multipliers.
    Authority states: floor = baseline × 1.00 (cosine geometry; floor = noise mean)
    All other states: floor = baseline × 1.08 (standard separation threshold)
    Session 16: tiered multiplier locked. SIGNAL_FLOOR_MULTIPLIER_AUTHORITY and
    SIGNAL_FLOOR_MULTIPLIER_DEFAULT replace the prior single constant.
    Session 23 v18: floor capped at SIGNAL_FLOOR_CEILING (0.9650) so no state
    is permanently ungatable (e.g. culture_drift at 1.0063 before this fix).
    Spec reference: Section VI.1 — LOCKED
    """
    from engine.data.states import STATE_PROFILES
    floors = {}
    for state_id, baseline_score in noise_baseline.items():
        profile = STATE_PROFILES.get(state_id)
        if profile and profile.primary_dimension == "Authority":
            raw = baseline_score * SIGNAL_FLOOR_MULTIPLIER_AUTHORITY
        else:
            raw = baseline_score * SIGNAL_FLOOR_MULTIPLIER_DEFAULT
        floors[state_id] = min(raw, SIGNAL_FLOOR_CEILING)
    return floors


def check_signal_gate(
    score: float,
    rank_1_score: Optional[float] = None,
) -> bool:
    """
    Hybrid floor gate for SCD-WCS space.

    Constraint 1 -- Absolute floor: score must meet or exceed
    SCD_WCS_ALIGNMENT_THRESHOLD (-0.4000). States below this carry
    insufficient signal regardless of session context.

    Constraint 2 -- Relative margin gate: if rank_1_score is provided,
    score must be within SCD_WCS_MARGIN_GATE (0.0500) cosine units of
    rank_1_score to qualify for multi-state output. Applied only when
    rank_1_score is supplied; if None, only Constraint 1 applies.

    Both constraints are CALIBRATION TARGETS (Session 25).
    """
    if score < SCD_WCS_ALIGNMENT_THRESHOLD:
        return False
    if rank_1_score is not None:
        if score < rank_1_score - SCD_WCS_MARGIN_GATE:
            return False
    return True


# ── Output data structures ─────────────────────────────────────────────────────

@dataclass
class QualifiedState:
    """
    A state evaluated against the signal floor.

    cleared_floor: True if score > signal_floor (state qualifies for output).
    score_lift_pct: percentage above noise baseline — (score/baseline - 1) * 100.

    Spec reference: Section VI.1
    """
    rank:              int
    state_id:          str
    state_name:        str
    score:             float
    noise_baseline:    float
    signal_floor:      float
    cleared_floor:     bool
    score_lift_pct:    float   # percentage above noise baseline
    resolution_family: str


@dataclass
class OutputRouting:
    """
    Output routing decision for one scoring session.

    mode:
      "single"             — one state cleared floor with sufficient separation
      "multi"              — two or more states cleared floor (or separation below threshold)
      "insufficient_signal"— no state cleared the signal floor

    Spec reference: Section VI.1, VI.2, VI.3
    """
    mode:                      str     # "single" | "multi" | "insufficient_signal"
    qualified_states:          list    # list[QualifiedState] that cleared signal floor
    all_evaluated:             list    # list[QualifiedState] for all ranked states
    lead_state:                Optional[QualifiedState]
    separation:                float   # score gap rank-1 minus rank-2 (0.0 if < 2 states)
    separation_threshold:      float
    single_state_threshold_met: bool


@dataclass
class PrivateOutputBlock:
    """
    Structured data for private output generation.

    Components per spec VI.4:
      1. state_name — named directly, no softening. LOCKED.
      2. severity_anchor_text — LOCKED copy from V.3.
      3. liability_condition_text — LLM-generated at application layer.
      4. asset_resolution_anchor_text — LLM-generated at application layer.
      5. resolution_family — one of the five service offerings. LOCKED.

    LLM-generated fields are empty strings until populated by the application layer.

    Spec reference: Section VI.2 and VI.4
    """
    state_name:                 str
    severity_tier:              str
    severity_anchor_text:       str         # LOCKED copy from V.3
    resolution_family:          str
    liability_condition_text:   str  = ""   # LLM-generated at application layer
    asset_resolution_anchor_text: str = ""  # LLM-generated at application layer


@dataclass
class ShareableOutputBlock:
    """
    Structured data for shareable output generation.

    Components per spec VI.5:
      1. state_name + severity_tier. LOCKED.
      2. framing_text — professional, non-confrontational. LLM-generated.
      3. observable_indicators — from signal map for identified state. LLM-generated.
      4. resolution_framing_text — organizational benefit language. LLM-generated.
      5. attribution — references PRV3 instrument. LOCKED.

    LLM-generated fields are empty until populated by the application layer.

    Spec reference: Section VI.2 and VI.5
    """
    state_name:                str
    severity_tier:             str
    resolution_family:         str
    attribution:               str  = "Identified using the PRV3 diagnostic instrument."
    framing_text:              str  = ""   # LLM-generated at application layer
    observable_indicators:     list = field(default_factory=list)  # LLM-generated
    resolution_framing_text:   str  = ""   # LLM-generated at application layer


@dataclass
class OutputPackage:
    """
    Complete output from one scoring session.

    For single-state mode: private and shareable are populated; multi_* are empty.
    For multi-state mode: multi_private and multi_shareable are populated.
    For insufficient_signal: all output blocks are None/empty.

    severity_result: always present regardless of output mode.
    insufficient_signal_message: human-readable message for the edge case.

    Spec reference: Section VI
    """
    routing:                       OutputRouting
    severity_result:               SeverityResult
    insufficient_signal:           bool
    insufficient_signal_message:   str  = ""

    # Single-state output
    private:                       Optional[PrivateOutputBlock]  = None
    shareable:                     Optional[ShareableOutputBlock] = None

    # Multi-state output
    multi_state_private:           list = field(default_factory=list)
    multi_state_shareable:         list = field(default_factory=list)


# ── VI.1  Signal Floor Application ────────────────────────────────────────────

def apply_signal_floor(
    rankings: list,
    noise_baseline: Optional[dict] = None,
) -> list:
    """
    Evaluate all ranked states against the SCD-WCS absolute alignment threshold.

    State clears floor if score > SCD_WCS_ALIGNMENT_THRESHOLD (0.25).
    noise_baseline: optional dict used only for score_lift_pct computation.
      If None, uses _PRECOMPUTED_NOISE_BASELINE.

    Returns list[QualifiedState] for ALL ranked states (cleared_floor flag
    distinguishes qualifying states). Ordered by rank (ascending).

    Spec reference: Section VI.1 — v21 absolute threshold
    """
    baseline_map = noise_baseline if noise_baseline is not None else _PRECOMPUTED_NOISE_BASELINE
    rank_1_score = next((r.score for r in rankings if r.rank == 1), None)
    result = []
    for r in rankings:
        sid = r.state_id
        profile = STATE_PROFILES.get(sid)
        baseline = baseline_map.get(sid, 0.0)
        cleared = check_signal_gate(r.score, rank_1_score=rank_1_score)
        lift = ((r.score / baseline) - 1.0) * 100.0 if baseline > 0.0 else 0.0
        result.append(QualifiedState(
            rank=r.rank,
            state_id=sid,
            state_name=profile.state_name if profile else sid,
            score=r.score,
            noise_baseline=baseline,
            signal_floor=SCD_WCS_ALIGNMENT_THRESHOLD,
            cleared_floor=cleared,
            score_lift_pct=lift,
            resolution_family=profile.resolution_family if profile else "",
        ))
    return result


# ── VI.2/VI.3  Output Routing ──────────────────────────────────────────────────

def route_output(evaluated_states: list) -> OutputRouting:
    """
    Determine single-state, multi-state, or insufficient-signal output mode.

    Rules (spec VI.2 and VI.3):
      - No states clear floor → "insufficient_signal"
      - One state clears floor AND separation >= threshold → "single"
      - One state clears floor but separation < threshold → "single" with lower
        confidence language (VI.2: "single state below threshold handled by
        single-state output with lower confidence language, not multi-state format")
      - Two or more states clear floor → "multi" if separation < threshold;
        "single" if rank-1 has meaningful separation from rank-2

    Separation = score(rank-1) - score(rank-2) across all cleared-floor states.

    Spec reference: Section VI.2 and VI.3
    """
    threshold = SEPARATION_THRESHOLD if SEPARATION_THRESHOLD is not None \
        else _SEPARATION_THRESHOLD_DEFAULT

    qualified = [qs for qs in evaluated_states if qs.cleared_floor]
    qualified_sorted = sorted(qualified, key=lambda qs: -qs.score)

    if not qualified:
        return OutputRouting(
            mode="insufficient_signal",
            qualified_states=[],
            all_evaluated=evaluated_states,
            lead_state=None,
            separation=0.0,
            separation_threshold=threshold,
            single_state_threshold_met=False,
        )

    lead = qualified_sorted[0]

    if len(qualified_sorted) >= 2:
        separation = lead.score - qualified_sorted[1].score
    else:
        # Only one state cleared floor; separation measured against
        # the next-ranked state (which did NOT clear floor)
        all_sorted = sorted(evaluated_states, key=lambda qs: -qs.score)
        idx = next((i for i, qs in enumerate(all_sorted) if qs.state_id == lead.state_id), 0)
        next_state = all_sorted[idx + 1] if idx + 1 < len(all_sorted) else None
        separation = (lead.score - next_state.score) if next_state else lead.score

    threshold_met = separation >= threshold

    if len(qualified_sorted) == 1:
        # Always single — VI.2: "single state below threshold is single-state output
        # with lower confidence language"
        mode = "single"
    elif threshold_met:
        mode = "single"
    else:
        mode = "multi"

    return OutputRouting(
        mode=mode,
        qualified_states=qualified_sorted,
        all_evaluated=evaluated_states,
        lead_state=lead,
        separation=separation,
        separation_threshold=threshold,
        single_state_threshold_met=threshold_met,
    )


# ── Category B: SPOF vs. Diffuse Causation ────────────────────────────────────

# Dispersion threshold for the single-qualified-state tiebreak below.
# CALIBRATION TARGET -- starting hypothesis (midpoint of dispersion's
# [0, 1] range), same convention as compute_cascade_risk's combination
# logic in engine/accumulation.py.
CAUSATION_DISPERSION_THRESHOLD: float = 0.5  # CALIBRATION TARGET


def compute_causation_pattern(
    accumulated_vector: dict,
    routing: OutputRouting,
) -> dict:
    """
    SPOF vs. Diffuse Causation -- Category B, Gemini-reviewed. Derived
    output only: zero new signal collection, zero modification to
    route_output() or the 8-field accumulation model. A framing input,
    not a new scored dimension and not currently threaded into the
    engine output contract -- mirrors Category A's compute_cascade_risk
    (a pure helper, not wired into assemble_output()).

    Reads two already-real, already-populated signals. No new math:

    qualified_state_count -- len(routing.qualified_states), the number
    of states that cleared the signal floor this session (this module's
    existing route_output() decision, Section VI.1-VI.3). 0 states = no
    attribution possible; 2+ states = causation is diffuse across
    multiple distinct conditions -- a direct real signal on both Path A
    and Path B, since every session runs OutputEngine.build().

    dispersion -- compute_liability_dispersion() from engine.accumulation,
    the identical Shannon-entropy term Cascade Risk already uses, reused
    rather than reinvented. Used only as a tiebreak when exactly one
    state qualifies: distinguishes a clean single-point-of-failure
    signature (liability concentrated in one axis) from a state that
    surfaced alone but whose underlying liability is already spread
    across multiple axes (diffuse at the axis level even though only
    one state cleared the floor).

    Classification:
      0 states                          -> "insufficient_signal"
      1 state,  dispersion <  threshold -> "single_point"
      1 state,  dispersion >= threshold -> "diffuse"
      2+ states                         -> "diffuse"

    accumulated_vector={} on Path B (self-select, declared diagnosis)
    makes dispersion structurally 0.0 for every Path B session -- the
    same known limitation Cascade Risk already carries there.
    accumulated_vector is never computed for Path B's declared-diagnosis
    shortcut by design (engine/main.py run_engine() passes {} because
    there is no real Q&A sequence to derive it from), not an oversight.
    Path B's pattern value is therefore driven entirely by
    qualified_state_count -- i.e. by how many states the principal
    self-selected, not by a computed axis-level signal. Path A (the live
    sequential diagnostic) populates a real, session-varying vector, so
    dispersion is a genuine computed signal there.

    CALIBRATION TARGET: CAUSATION_DISPERSION_THRESHOLD (0.5) is a
    starting hypothesis, not a locked value.

    Spec reference: Category B architecture review (Gemini-cleared) --
    SPOF vs. Diffuse Causation.
    """
    qualified_count = len(routing.qualified_states)
    dispersion = compute_liability_dispersion(accumulated_vector)

    if qualified_count == 0:
        pattern = "insufficient_signal"
    elif qualified_count >= 2:
        pattern = "diffuse"
    elif dispersion >= CAUSATION_DISPERSION_THRESHOLD:
        pattern = "diffuse"
    else:
        pattern = "single_point"

    return {
        "pattern": pattern,
        "dispersion": round(dispersion, 4),
        "qualified_state_count": qualified_count,
    }


def derive_time_to_consequence(profile: StateProfile) -> str:
    """
    Urgency Window, Component 1 -- Diagnostic Dimension Expansion,
    Candidate 5, Gemini-reviewed, CC-verified. Derived from a state's
    already-real, already-populated static metadata -- zero new intake,
    zero manual 57-state authoring. Reads liability_axes and
    primary_dimension only, both confirmed real fields on StateProfile
    (engine/data/states.py) with a confirmed real vocabulary
    (LIABILITY_CATEGORIES, 9 values including "Legal & Compliance" and
    "Financial & Economic" verbatim).

    Classification:
      "Legal & Compliance" or "Financial & Economic" in liability_axes
        -> "Acute" (a formal claim, filing, or financial event can
        crystallize the exposure at any moment -- not a slow-building risk)
      primary_dimension in ("Authority", "Aptitude")
        -> "Medium-Term" (structural/decision-quality conditions that
        compound over a normal business cycle, not overnight)
      otherwise -> "Attritional" (Alliance/Attitude-primary conditions --
        cultural and relational erosion, felt cumulatively over time)

    Spec reference: Diagnostic Dimension Expansion decision record
    (prompts/diagnostic-dimension-expansion.md), Candidate 5.
    """
    axes = profile.liability_axes
    if "Legal & Compliance" in axes or "Financial & Economic" in axes:
        return "Acute"
    if profile.primary_dimension in ("Authority", "Aptitude"):
        return "Medium-Term"
    return "Attritional"


# Noise filter for synthesize_response_window()'s delta/dispersion_delta
# sign checks -- Pete-requested revision, this session. Deliberately NOT
# TRAJECTORY_STABILITY_THRESHOLD (0.20, engine/accumulation.py) -- that
# constant buckets compute_trajectory()'s 3-way direction classification
# and is already flagged unreliable/unvalidated for that purpose; this is
# a separate, smaller constant scoped only to filtering near-zero noise
# here before it swings the tier index, not a full direction threshold.
# CALIBRATION TARGET -- starting hypothesis, not yet data-validated.
RESPONSE_WINDOW_EPSILON: float = 0.05  # CALIBRATION TARGET


def synthesize_response_window(
    trajectory_result: Optional[dict],
    severity_tier: str,
) -> Optional[str]:
    """
    Urgency Window, Component 2 -- Diagnostic Dimension Expansion,
    Candidate 5, Gemini-reviewed, CC-verified. Synthesized from
    trajectory_result's RAW delta/dispersion_delta/duration_band plus
    severity_tier -- deliberately never reads trajectory_result
    ["direction"]. That field's bucketing threshold
    (TRAJECTORY_STABILITY_THRESHOLD = 0.20, engine/accumulation.py) is
    confirmed unvalidated ("CALIBRATION TARGET... Not yet data-validated"
    per its own comment) with a known false-negative risk -- this function
    reasons from the raw signals directly rather than inheriting that risk.

    None on Path B (trajectory_result itself is None -- engine/main.py's
    run_engine() never computes or passes one, confirmed by direct read).
    Real for Path 1, including the insufficient-answers case
    (_compute_trajectory_context() returns delta=0.0, dispersion_delta=0.0
    rather than None there) -- both values then fail every sign check
    below, so the result falls back to the severity-only base tier with no
    special-casing needed.

    CALIBRATION TARGET, starting hypothesis, not yet data-validated --
    same convention as TRAJECTORY_STABILITY_THRESHOLD/
    MODERATE_PROMINENCE_DELTA elsewhere in this codebase. Sign-based,
    epsilon-filtered (RESPONSE_WINDOW_EPSILON, above) -- no bare sign
    check on raw floats: a delta or dispersion_delta of 0.0001 must not
    swing the tier index as easily as a delta of 5.0 would:

      Base tier, anchored on severity (the one already-established signal):
        Emerging -> "Extended", Entrenched -> "Near-Term", Endemic -> "Immediate"

      delta > RESPONSE_WINDOW_EPSILON (liability denser in the session's
      second half -- genuinely worsening within-session, past the noise
      floor) tightens one step; delta < -RESPONSE_WINDOW_EPSILON loosens
      one step.

      dispersion_delta > RESPONSE_WINDOW_EPSILON (liability spreading
      across more axes -- broadening, past the noise floor) tightens one
      further step, independent of delta's effect since it measures
      spread, not magnitude; dispersion_delta < -RESPONSE_WINDOW_EPSILON
      loosens one step.

      duration_band == "18mo_plus" combined with delta > 
      RESPONSE_WINDOW_EPSILON tightens one additional step -- a condition
      that has already persisted 18+ months AND is still trending worse
      is a distinct compounding-over-time concern, not redundant with
      severity_tier's own point-in-time duration_band contribution.

      Result clamped to the 3 defined tiers -- cannot escalate or de-
      escalate past "Immediate"/"Extended".

    Spec reference: Diagnostic Dimension Expansion decision record
    (prompts/diagnostic-dimension-expansion.md), Candidate 5.
    """
    if trajectory_result is None:
        return None

    delta = trajectory_result.get("delta", 0.0)
    dispersion_delta = trajectory_result.get("dispersion_delta", 0.0)
    duration_band = trajectory_result.get("duration_band")

    tiers = ["Extended", "Near-Term", "Immediate"]
    idx = {"Emerging": 0, "Entrenched": 1, "Endemic": 2}.get(severity_tier, 1)

    if delta > RESPONSE_WINDOW_EPSILON:
        idx += 1
    elif delta < -RESPONSE_WINDOW_EPSILON:
        idx -= 1

    if dispersion_delta > RESPONSE_WINDOW_EPSILON:
        idx += 1
    elif dispersion_delta < -RESPONSE_WINDOW_EPSILON:
        idx -= 1

    if duration_band == "18mo_plus" and delta > RESPONSE_WINDOW_EPSILON:
        idx += 1

    idx = max(0, min(len(tiers) - 1, idx))
    return tiers[idx]


# ── VI.4  Private Output Assembly ─────────────────────────────────────────────

def build_private_block(
    qualified_state: QualifiedState,
    severity_result: SeverityResult,
) -> PrivateOutputBlock:
    """
    Assemble the private output block for one state.

    severity_anchor_text is the LOCKED copy from V.3.
    LLM-generated fields (liability_condition_text, asset_resolution_anchor_text)
    are left empty — populated by the application layer using this block as context.

    Spec reference: Section VI.2 and VI.4
    """
    anchor = SEVERITY_TIER_DESCRIPTIONS.get(severity_result.tier, "")
    return PrivateOutputBlock(
        state_name=qualified_state.state_name,
        severity_tier=severity_result.tier,
        severity_anchor_text=anchor,
        resolution_family=qualified_state.resolution_family,
    )


# ── VI.5  Shareable Output Assembly ───────────────────────────────────────────

def build_shareable_block(
    qualified_state: QualifiedState,
    severity_result: SeverityResult,
) -> ShareableOutputBlock:
    """
    Assemble the shareable output block for one state.

    LLM-generated fields (framing_text, observable_indicators,
    resolution_framing_text) are left empty — populated by the application
    layer using this block as context.

    Spec reference: Section VI.2 and VI.5
    """
    return ShareableOutputBlock(
        state_name=qualified_state.state_name,
        severity_tier=severity_result.tier,
        resolution_family=qualified_state.resolution_family,
    )


# ── OutputEngine ───────────────────────────────────────────────────────────────

class OutputEngine:
    """
    Orchestrates signal floor application, output routing, and output assembly
    for one scoring session.

    Usage:
        engine = OutputEngine()
        engine.set_noise_baseline()          # or set_noise_baseline(custom_dict)
        package = engine.build(rankings, severity_result)

    The noise baseline should be computed once per question library state and
    cached. Call set_noise_baseline() again only if the question library changes.

    LLM-generated output fields (liability_condition_text, framing_text, etc.)
    are empty in the returned OutputPackage. The application layer populates
    them using the package's routing and block structures as LLM context.

    Spec reference: Section VI (all subsections)
    """

    # Class-level cache: pre-filled with the Session 16 precomputed baseline.
    # Recompute by calling compute_noise_baseline() and passing the result to
    # set_noise_baseline(baseline=...) only if the question library changes.
    _cached_baseline: Optional[dict] = _PRECOMPUTED_NOISE_BASELINE

    def __init__(self):
        self._baseline: Optional[dict] = None

    def set_noise_baseline(
        self,
        baseline: Optional[dict] = None,
        n_simulations: int = NOISE_SIMULATION_COUNT,
        random_seed: Optional[int] = None,
    ) -> dict:
        """
        Set the noise baseline used for signal floor computation.

        If baseline is provided, uses it directly (for testing or pre-computed
        baselines). Otherwise runs the simulation.

        Returns the baseline dict for inspection.
        """
        if baseline is not None:
            self._baseline = baseline
        elif OutputEngine._cached_baseline is not None:
            self._baseline = OutputEngine._cached_baseline
        else:
            self._baseline = compute_noise_baseline(n_simulations, random_seed)
            OutputEngine._cached_baseline = self._baseline
        return self._baseline

    def build(
        self,
        rankings: list,
        severity_result: SeverityResult,
    ) -> OutputPackage:
        """
        Build the complete output package from final rankings and severity result.

        Steps:
          1. Ensure noise baseline is set (compute if not already done).
          2. apply_signal_floor on all ranked states.
          3. route_output to determine mode.
          4. Build private and shareable blocks per mode.

        Returns OutputPackage with all structural data populated.
        LLM-generated text fields are empty — application layer fills them.

        Spec reference: Section VI.1–VI.5
        """
        if self._baseline is None:
            self.set_noise_baseline()

        evaluated = apply_signal_floor(rankings, self._baseline)
        routing = route_output(evaluated)

        insufficient = routing.mode == "insufficient_signal"
        insuff_msg = (
            "The diagnostic requires additional context before a condition "
            "can be identified. No state cleared the signal floor."
            if insufficient else ""
        )

        private = None
        shareable = None
        multi_private = []
        multi_shareable = []

        if routing.mode == "single" and routing.lead_state:
            private = build_private_block(routing.lead_state, severity_result)
            shareable = build_shareable_block(routing.lead_state, severity_result)

        elif routing.mode == "multi":
            for qs in routing.qualified_states:
                multi_private.append(build_private_block(qs, severity_result))
                multi_shareable.append(build_shareable_block(qs, severity_result))

        return OutputPackage(
            routing=routing,
            severity_result=severity_result,
            insufficient_signal=insufficient,
            insufficient_signal_message=insuff_msg,
            private=private,
            shareable=shareable,
            multi_state_private=multi_private,
            multi_state_shareable=multi_shareable,
        )
