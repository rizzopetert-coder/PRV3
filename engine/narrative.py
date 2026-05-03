"""
PRV3 Scoring Engine — Section IV
Narrative Modulation Engine

IV.1  LLM Call Design and System Prompt
IV.2  Confidence-Gated Variable Weight Application
IV.3  Normalization Mechanism and Ceiling Enforcement

The narrative prompt response is processed by an LLM that extracts dimensional
signals and returns confidence scores. Output modulates — confirmation and
elevation only. Cannot introduce new state probability for zero-prior states.

Spec reference: PRV3_Scoring_Architecture_Spec_v1.docx, Section IV
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from engine.data.states import DIMENSIONAL_FIELDS
from engine.accumulation import StateRanking, rank_states


# ── Ceiling and floor constants ────────────────────────────────────────────────

# State probability ceiling: maximum increase per state after narrative modulation.
# Applied after normalization in IV.3. LOCKED.
STATE_PROBABILITY_CEILING: float = 0.12

# Severity ceiling: maximum increase on severity scale from narrative modulation.
# Applied at output stage (Section VI). Defined here as the canonical constant.
# LOCKED.
SEVERITY_CEILING: float = 0.25

# Confidence floor: overall_confidence below this → zero modulation contribution.
# CALIBRATION TARGET — 0.15 is the starting hypothesis.
CONFIDENCE_FLOOR: float = 0.15  # CALIBRATION TARGET


# ── IV.1.1  LLM System Prompt ─────────────────────────────────────────────────

NARRATIVE_SYSTEM_PROMPT: str = """\
You are a signal extraction engine for an organizational diagnostic instrument. \
Your function is to extract dimensional signals from a principal's narrative \
response. You do not interpret intent. You do not generate narrative. \
You return only structured JSON.

SIGNAL VOCABULARY

Four dimensions, each with two axes:

Aptitude - Individual and team capability
  liability: signals of capability deficit, skill gap, developmental failure
  asset: signals of capability strength, talent activation, learning architecture

Authority - Organizational structure and decision-making
  liability: signals of structural dysfunction, governance failure, decision paralysis
  asset: signals of governance clarity, accountability architecture, decision discipline

Alliance - Relationships and coordination
  liability: signals of coordination failure, trust breakdown, cultural fracture
  asset: signals of relational trust, cross-functional alignment, coalition strength

Attitude - Culture, values, and behavioral norms
  liability: signals of cultural dysfunction, value misalignment, behavioral failure
  asset: signals of cultural health, psychological safety, behavioral integrity

CONFIDENCE SCORING

Assign confidence 0.0-1.0 based on signal specificity and observational directness:
- High confidence (0.7-1.0): principal names a specific condition, names a person \
or role, describes a pattern with duration or frequency, or provides concrete examples
- Medium confidence (0.4-0.69): principal describes general concern with some specificity
- Low confidence (0.1-0.39): vague or general description with limited specificity
- Near-zero (0.0-0.09): ambiguous, off-topic, or insufficient for signal extraction

REQUIRED OUTPUT FORMAT

Return only this JSON structure. No preamble. No explanation. No markdown.

{
  "identified_signals": [
    {
      "dimension": "<Aptitude|Authority|Alliance|Attitude>",
      "axis": "<liability|asset>",
      "signal_text": "<brief description of signal extracted, 5-15 words>",
      "confidence": <float 0.0-1.0>
    }
  ],
  "severity_indicators": [
    {
      "indicator_text": "<brief description of severity signal, 5-15 words>",
      "confidence": <float 0.0-1.0>
    }
  ],
  "overall_confidence": <float 0.0-1.0>
}

If no signals are found: \
{"identified_signals": [], "severity_indicators": [], "overall_confidence": 0.0}\
"""


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class NarrativeSignal:
    """
    One dimensional signal extracted from the narrative response.
    Spec reference: Section IV.1 — identified_signals schema
    """
    dimension:   str    # Aptitude | Authority | Alliance | Attitude
    axis:        str    # liability | asset
    signal_text: str
    confidence:  float  # 0.0–1.0


@dataclass
class SeverityIndicator:
    """
    One severity signal extracted from the narrative response.
    Spec reference: Section IV.1 — severity_indicators schema
    """
    indicator_text: str
    confidence:     float  # 0.0–1.0


@dataclass
class NarrativeExtractionResult:
    """
    Full LLM output from one narrative extraction call.
    Spec reference: Section IV.1 — required LLM output fields
    """
    identified_signals:  list  # list[NarrativeSignal]
    severity_indicators: list  # list[SeverityIndicator]
    overall_confidence:  float  # 0.0–1.0
    raw_response:        str   = ""  # LLM response text before parsing
    parse_error:         str   = ""  # non-empty if JSON parsing failed


# ── IV.1  LLM Call ─────────────────────────────────────────────────────────────

_VALID_DIMENSIONS = {"Aptitude", "Authority", "Alliance", "Attitude"}
_VALID_AXES = {"liability", "asset"}


def _parse_extraction_response(response_text: str) -> NarrativeExtractionResult:
    """
    Parse the LLM's JSON response into a NarrativeExtractionResult.
    Returns a zero-confidence result on any parse failure.
    """
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        return NarrativeExtractionResult(
            identified_signals=[],
            severity_indicators=[],
            overall_confidence=0.0,
            raw_response=response_text,
            parse_error=str(e),
        )

    signals = []
    for s in data.get("identified_signals", []):
        dim = s.get("dimension", "")
        ax = s.get("axis", "")
        if dim in _VALID_DIMENSIONS and ax in _VALID_AXES:
            signals.append(NarrativeSignal(
                dimension=dim,
                axis=ax,
                signal_text=str(s.get("signal_text", "")),
                confidence=float(s.get("confidence", 0.0)),
            ))

    severity = []
    for sv in data.get("severity_indicators", []):
        severity.append(SeverityIndicator(
            indicator_text=str(sv.get("indicator_text", "")),
            confidence=float(sv.get("confidence", 0.0)),
        ))

    return NarrativeExtractionResult(
        identified_signals=signals,
        severity_indicators=severity,
        overall_confidence=float(data.get("overall_confidence", 0.0)),
        raw_response=response_text,
    )


def extract_signals(
    narrative_text: str,
    model: str = "claude-sonnet-4-6",
    client=None,
) -> NarrativeExtractionResult:
    """
    Call the LLM to extract dimensional signals from the principal's narrative.

    Parameters:
      narrative_text: the principal's free-text narrative response
      model:          LLM model identifier (configurable per spec IV.1)
      client:         anthropic.Anthropic client instance; creates one if None

    LLM call parameters (LOCKED per spec IV.1):
      temperature: 0.2
      max_tokens:  500

    Returns NarrativeExtractionResult. On API or parse failure, returns a
    zero-confidence result so the engine continues without modulation.

    Spec reference: Section IV.1
    """
    try:
        import anthropic as _anthropic
    except ImportError:
        return NarrativeExtractionResult(
            identified_signals=[],
            severity_indicators=[],
            overall_confidence=0.0,
            parse_error="anthropic package not installed",
        )

    if client is None:
        client = _anthropic.Anthropic()

    try:
        message = client.messages.create(
            model=model,
            max_tokens=500,
            temperature=0.2,
            system=NARRATIVE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": narrative_text}],
        )
        response_text = message.content[0].text
    except Exception as e:
        return NarrativeExtractionResult(
            identified_signals=[],
            severity_indicators=[],
            overall_confidence=0.0,
            parse_error=f"API error: {e}",
        )

    return _parse_extraction_response(response_text)


# ── IV.2  Variable Weight Application ─────────────────────────────────────────

def signal_to_field(dimension: str, axis: str) -> Optional[str]:
    """
    Map a NarrativeSignal (dimension, axis) to a DIMENSIONAL_FIELD name.
    Returns None if the combination is not a valid field.
    """
    candidate = f"{dimension.lower()}_{axis.lower()}"
    return candidate if candidate in DIMENSIONAL_FIELDS else None


def build_modulation_vector(
    extraction_result: NarrativeExtractionResult,
    accumulated_vector: dict,
) -> dict:
    """
    Convert LLM-extracted signals to a dimensional modulation vector.

    Confirmation and elevation only (LOCKED):
      A signal only contributes to a field where accumulated_vector[field] > 0.
      If the accumulated vector has no prior signal in a field, the narrative
      cannot introduce new signal there.

    Weight formula (LOCKED):
      modulation_weight = overall_confidence * signal.confidence
      field_contribution += 1.0 * modulation_weight

    The unit contribution (1.0) represents one signal-equivalent. Magnitude
    is a calibration target — the 12% ceiling in IV.3 bounds the downstream
    impact regardless of raw modulation magnitude.

    Returns {field: contribution} for all 8 dimensional fields. Fields with
    no signal contribution or blocked by zero-prior rule are 0.0.

    Spec reference: Section IV.2
    """
    modulation = {f: 0.0 for f in DIMENSIONAL_FIELDS}
    oc = extraction_result.overall_confidence

    for sig in extraction_result.identified_signals:
        f = signal_to_field(sig.dimension, sig.axis)
        if f is None:
            continue
        # Confirmation and elevation only: skip if field has no prior accumulation
        if accumulated_vector.get(f, 0.0) <= 0.0:
            continue
        weight = oc * sig.confidence
        modulation[f] += weight

    return modulation


# ── IV.3  Normalization Mechanism and Ceiling Enforcement ─────────────────────

def _rankings_to_prob_dist(rankings: list) -> dict:
    """Normalize ranking scores to a probability distribution."""
    total = sum(r.score for r in rankings)
    if total == 0.0:
        n = len(rankings)
        return {r.state_id: 1.0 / n for r in rankings}
    return {r.state_id: r.score / total for r in rankings}


def enforce_state_probability_ceiling(
    pre_rankings: list,
    post_rankings: list,
    ceiling: float = STATE_PROBABILITY_CEILING,
) -> list:
    """
    Cap any state's probability increase from narrative modulation at `ceiling`
    percentage points (default 12 pp). Re-normalize after capping.

    Algorithm:
      1. Convert pre and post rankings to probability distributions.
      2. Identify states whose share increased by more than `ceiling`.
      3. For each capped state: fix final share at pre_prob[s] + ceiling.
      4. Redistribute remaining probability among uncapped states proportionally
         to their post-modulation shares. This preserves the ceiling strictly
         in the final distribution — not just in the pre-normalization space.
      5. Return updated StateRanking list with adjusted scores, re-ranked.

    Spec reference: Section IV.2 (ceiling definition) and IV.3 (enforcement)
    LOCKED.
    """
    pre_prob = _rankings_to_prob_dist(pre_rankings)
    post_prob = _rankings_to_prob_dist(post_rankings)

    capped_states = {}   # state_id → final capped share
    uncapped_states = []  # state_ids not requiring a cap

    for sid in post_prob:
        increase = post_prob[sid] - pre_prob.get(sid, 0.0)
        if increase > ceiling:
            capped_states[sid] = pre_prob.get(sid, 0.0) + ceiling
        else:
            uncapped_states.append(sid)

    if not capped_states:
        return post_rankings

    # Probability budget remaining for uncapped states
    remaining = 1.0 - sum(capped_states.values())

    # Redistribute remaining to uncapped states proportionally to post_prob
    uncapped_post_total = sum(post_prob[sid] for sid in uncapped_states)
    final_shares = dict(capped_states)

    if uncapped_post_total > 0.0 and remaining > 0.0:
        for sid in uncapped_states:
            final_shares[sid] = post_prob[sid] / uncapped_post_total * remaining
    else:
        n_uncapped = len(uncapped_states)
        share_each = max(remaining / n_uncapped, 0.0) if n_uncapped > 0 else 0.0
        for sid in uncapped_states:
            final_shares[sid] = share_each

    dist_by_id = {r.state_id: r.distance for r in post_rankings}
    adjusted = [
        StateRanking(
            rank=0,
            state_id=sid,
            distance=dist_by_id.get(sid, 0.0),
            score=final_shares.get(sid, 0.0),
        )
        for sid in final_shares
    ]
    adjusted.sort(key=lambda r: -r.score)
    for i, r in enumerate(adjusted):
        r.rank = i + 1
    return adjusted


def apply_narrative_modulation(
    accumulated_vector: dict,
    extraction_result: NarrativeExtractionResult,
    pre_rankings: list,
) -> tuple:
    """
    Apply narrative modulation to the accumulated vector and return the
    updated vector and ceiling-enforced rankings.

    Steps (Section IV.2 and IV.3):
      1. Confidence floor check: if overall_confidence < CONFIDENCE_FLOOR,
         return unchanged (no modulation).
      2. Build modulation vector (confirmation-and-elevation-only, weighted).
      3. Add modulation vector to accumulated_vector (element-wise).
      4. Re-run rank_states on the updated accumulated vector.
      5. Enforce 12% state probability ceiling.

    Returns (updated_accumulated_vector, ceiling_enforced_rankings).
    If no modulation (floor not met), returns (original_vector, pre_rankings).

    Spec reference: Section IV.2 and IV.3
    """
    if extraction_result.overall_confidence < CONFIDENCE_FLOOR:
        return dict(accumulated_vector), pre_rankings

    modulation = build_modulation_vector(extraction_result, accumulated_vector)

    # Element-wise addition — modulation adds to accumulated vector
    updated_vector = {
        f: accumulated_vector.get(f, 0.0) + modulation.get(f, 0.0)
        for f in DIMENSIONAL_FIELDS
    }

    # Re-rank on updated vector
    post_rankings = rank_states(updated_vector)

    # Enforce state probability ceiling (IV.3)
    final_rankings = enforce_state_probability_ceiling(pre_rankings, post_rankings)

    return updated_vector, final_rankings


# ── NarrativeModulationEngine ──────────────────────────────────────────────────

class NarrativeModulationEngine:
    """
    Orchestrates one narrative modulation pass for a scoring session.

    Usage:
        engine = NarrativeModulationEngine(model="claude-sonnet-4-6")

        # After narrative prompt response received:
        result = engine.extract(narrative_text)

        # Apply modulation to accumulated vector and pre-narrative rankings:
        updated_vector, final_rankings = engine.modulate(
            accumulated_vector, result, pre_narrative_rankings
        )

        # Severity indicators for Section V:
        severity_signals = engine.severity_signals

    Spec reference: Section IV (all subsections)
    """

    def __init__(self, model: str = "claude-sonnet-4-6", client=None):
        self.model = model
        self._client = client
        self.extraction_result: Optional[NarrativeExtractionResult] = None

    def extract(self, narrative_text: str) -> NarrativeExtractionResult:
        """
        Call the LLM to extract signals. Stores result for downstream access.
        """
        self.extraction_result = extract_signals(
            narrative_text, model=self.model, client=self._client
        )
        return self.extraction_result

    def modulate(
        self,
        accumulated_vector: dict,
        extraction_result: NarrativeExtractionResult,
        pre_rankings: list,
    ) -> tuple:
        """
        Apply modulation and return (updated_vector, ceiling_enforced_rankings).
        """
        return apply_narrative_modulation(
            accumulated_vector, extraction_result, pre_rankings
        )

    @property
    def severity_signals(self) -> list:
        """
        Severity indicators from the last extraction, for use in Section V.
        Returns empty list if no extraction has been run.
        """
        if self.extraction_result is None:
            return []
        return list(self.extraction_result.severity_indicators)
