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

from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS, BASELINE_VALUE
from engine.data.questions import QUESTION_LIBRARY
from engine.accumulation import StateRanking, rank_states
from engine.severity import SeverityResult, SEVERITY_TIER_DESCRIPTIONS


# ── VI.1  Signal Floor Constants ───────────────────────────────────────────────

# Signal floor multiplier: state must score SIGNAL_FLOOR_MULTIPLIER above noise
# baseline to qualify for output. LOCKED.
SIGNAL_FLOOR_MULTIPLIER: float = 1.15  # LOCKED — 15% above noise baseline

# Number of randomized simulations for noise baseline calculation. LOCKED.
NOISE_SIMULATION_COUNT: int = 1000  # LOCKED

# Separation threshold: score gap rank-1 minus rank-2 required for single-state
# output. CALIBRATION TARGET — set via Phase 1 ROC analysis.
SEPARATION_THRESHOLD: Optional[float] = None  # CALIBRATION TARGET

# Default separation threshold (used when CALIBRATION_TARGET is None).
# Conservative starting hypothesis; Phase 1 ROC analysis replaces this.
_SEPARATION_THRESHOLD_DEFAULT: float = 0.05  # CALIBRATION TARGET default


# ── VI.1  Noise Baseline Simulation ───────────────────────────────────────────

def compute_noise_baseline(
    n_simulations: int = NOISE_SIMULATION_COUNT,
    random_seed: Optional[int] = None,
) -> dict:
    """
    Compute the noise baseline score for each state by simulating n_simulations
    randomized answer sets through the accumulation and ranking pipeline.

    For each simulation: randomly select one option per core question (Q01–Q34),
    accumulate the contributions with neutral role ("Other"), run rank_states.
    Noise baseline per state = mean similarity score across all simulations.

    When the question library is empty (current build stage): all questions
    contribute zero to the accumulated vector, so all simulations produce the
    same score — the zero-signal baseline. Returns this theoretical baseline
    for each state.

    Signal floor per state = noise_baseline[state_id] * SIGNAL_FLOOR_MULTIPLIER.

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

        rankings = rank_states(accumulated)
        for r in rankings:
            score_totals[r.state_id] += r.score

    return {sid: score_totals[sid] / n_simulations for sid in STATE_PROFILES}


def compute_signal_floors(noise_baseline: dict) -> dict:
    """
    Compute the signal floor for each state.
    floor[state_id] = noise_baseline[state_id] * SIGNAL_FLOOR_MULTIPLIER

    Spec reference: Section VI.1 — LOCKED
    """
    return {sid: score * SIGNAL_FLOOR_MULTIPLIER for sid, score in noise_baseline.items()}


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
      6. friction_tax_estimate — CALIBRATION TARGET (separate spec task).

    LLM-generated fields are empty strings until populated by the application layer.

    Spec reference: Section VI.2 and VI.4
    """
    state_name:                 str
    severity_tier:              str
    severity_anchor_text:       str         # LOCKED copy from V.3
    resolution_family:          str
    liability_condition_text:   str  = ""   # LLM-generated at application layer
    asset_resolution_anchor_text: str = ""  # LLM-generated at application layer
    friction_tax_estimate:      Optional[float] = None  # CALIBRATION TARGET


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
    noise_baseline: dict,
) -> list:
    """
    Evaluate all ranked states against the signal floor.

    For each state: floor = noise_baseline[state_id] * SIGNAL_FLOOR_MULTIPLIER.
    State clears floor if score > floor.

    Returns list[QualifiedState] for ALL ranked states (cleared_floor flag
    distinguishes qualifying states). Ordered by rank (ascending).

    Spec reference: Section VI.1 — LOCKED
    """
    floors = compute_signal_floors(noise_baseline)
    result = []
    for r in rankings:
        sid = r.state_id
        profile = STATE_PROFILES.get(sid)
        baseline = noise_baseline.get(sid, 0.0)
        floor = floors.get(sid, 0.0)
        cleared = r.score > floor
        lift = ((r.score / baseline) - 1.0) * 100.0 if baseline > 0.0 else 0.0
        result.append(QualifiedState(
            rank=r.rank,
            state_id=sid,
            state_name=profile.state_name if profile else sid,
            score=r.score,
            noise_baseline=baseline,
            signal_floor=floor,
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

    # Class-level cache: noise baseline is expensive to compute and stable until
    # the question library changes.
    _cached_baseline: Optional[dict] = None

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
