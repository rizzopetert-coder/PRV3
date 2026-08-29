"""
PRV3 Scoring Engine — Section IV
Narrative Modulation Engine

IV.1  LLM Call Design and System Prompt
IV.2  Confidence-Gated Variable Weight Application
IV.3  Normalization Mechanism and Ceiling Enforcement

The narrative prompt response is processed by an LLM that extracts dimensional
signals and returns confidence scores. Output modulates — confirmation and
elevation only. Cannot introduce new state probability for zero-prior states.

Spec reference: documents/PRV3_Scoring_Architecture_Spec_v1.docx, Section IV
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from engine.data.states import DIMENSIONAL_FIELDS, STATE_PROFILES
from engine.data.salience import SALIENCE_PROFILES
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
    answered_question_count: int,
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

    # Re-rank on updated vector -- SALIENCE_PROFILES-weighted, matching
    # pre_rankings above and every rank_states() call in engine/main.py
    # (fixed this session -- was silently falling back to unweighted
    # cosine similarity, inert until Bug 1's fix made this value flow
    # through to real completion).
    post_rankings = rank_states(updated_vector, answered_question_count, SALIENCE_PROFILES)

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
        answered_question_count: int,
    ) -> tuple:
        """
        Apply modulation and return (updated_vector, ceiling_enforced_rankings).
        """
        return apply_narrative_modulation(
            accumulated_vector, extraction_result, pre_rankings, answered_question_count
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


# ── Section V integration: severity_indicators -> SeverityEngine ──────────────
#
# Found during this session's Gemini architecture review (prompts/
# narrative-modulation-phase3-gemini-request.md): SeverityIndicator has no
# schema overlap with SeverityInput/add_input(), but a SEPARATE, already-
# built, already-ceiling-enforced path exists -- SeverityEngine.
# set_narrative_contribution(raw_addition: float) (engine/severity.py),
# feeding NARRATIVE_SEVERITY_CEILING_POINTS (25.0, real and referenced in
# live scoring logic there). This module's own SEVERITY_CEILING=0.25
# constant above is a separate, never-referenced-elsewhere declaration --
# not the real ceiling in effect, which is severity.py's. Kept as-is here
# rather than removed, to avoid an unrelated edit in this same pass; worth
# reconciling or removing in a future cleanup, flagged not fixed.

def compute_narrative_severity_addition(
    extraction_result: NarrativeExtractionResult,
) -> float:
    """
    Converts extracted severity_indicators into the single raw_addition
    value SeverityEngine.set_narrative_contribution() expects -- the real
    path for narrative's severity contribution (Section V.1/V.2), not
    SeverityInput/add_input(), which this data's shape can't satisfy.
    raw_addition must sit on compute_raw_severity()'s own raw scale (per
    set_narrative_contribution()'s own docstring) -- real SEVER-##
    triggers contribute roughly 1.0-3.0 raw points each
    (duration_weight * population_weight), so this formula's per-
    indicator ceiling of 1.0 (confidence times confidence, both in
    [0,1]) mirrors that rough magnitude rather than an unrelated scale.

    Confirmation-and-elevation spirit carried over from
    build_modulation_vector() (IV.2): weighted by
    overall_confidence * indicator.confidence, summed across every
    extracted severity_indicators entry. Below CONFIDENCE_FLOOR,
    contributes nothing -- mirrors apply_narrative_modulation()'s own
    floor check exactly, so a low-confidence narrative response never
    touches severity even where dimensional modulation is also skipped.

    CALIBRATION TARGET: this weighting formula is a reasonable starting
    construction for this build, not derived from real data -- same
    status as every other CALIBRATION TARGET constant in this engine,
    flagged as such rather than presented as precisely derived.
    """
    if extraction_result.overall_confidence < CONFIDENCE_FLOOR:
        return 0.0
    oc = extraction_result.overall_confidence
    return sum(oc * ind.confidence for ind in extraction_result.severity_indicators)


# ── III.3 generation: the principal-facing narrative prompt itself ────────────
#
# Zero code existed anywhere for this direction before this build --
# extract_signals() (above) only ever extracts FROM a narrative response.
# P-04 (locked): "Narrative prompt used surgically. Dynamically
# generated. Not static." New system prompt below is real content-
# authoring for this build, not a verbatim spec transcription --
# flagged as such for review.

NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT: str = """\
You write ONE open-ended question for a principal completing an \
organizational diagnostic. Your question invites them to describe, in \
their own words, something happening in their organization that the \
structured questions so far may not have fully captured.

You are given internal signal only -- never repeat it back, never name \
it, never let the principal infer it from your phrasing. Use it only to \
make your question observationally relevant, not diagnostic or leading.

RULES
- Up to 3 concise sentences: an observational opener, then the \
open-ended question itself. No explanation after the question.
- Never name a condition, pattern, or diagnosis. Never use clinical or \
assessment language ("we've identified," "this suggests," "your \
organization shows signs of").
- Never presuppose an answer or imply a problem exists. The principal \
may have nothing further to add, and the question must not penalize \
that.
- Ground the question in the general theme of the internal signal (e.g. \
authority/decision-making, capability/skill, relationships/\
coordination, culture/behavior) without naming the specific condition \
or citing the signal directly.
- Plain, direct language. No jargon. Second person ("you," "your \
organization").
- Output ONLY the question text. No markdown, no quotation marks, no \
JSON, no surrounding punctuation beyond the question itself.
"""

_NARRATIVE_PROMPT_FALLBACK: str = (
    "Is there anything about what's happening in your organization right "
    "now that you'd want to describe in your own words, even if it "
    "hasn't come up in the questions so far?"
)


@dataclass
class NarrativePromptResult:
    """
    Result of one generate_narrative_prompt() call.
    """
    prompt:      str
    is_fallback: bool
    parse_error: str = ""


def _build_prompt_generation_input(context: dict) -> str:
    """
    Builds the user-message content for generate_narrative_prompt() from
    build_narrative_prompt_context()'s output. Internal-only signal --
    state_id/descriptive_prose never reach the principal, only inform
    what the LLM writes (same P-03 discipline get_question_copy()
    already applies elsewhere in this engine, applied here to prompt
    INPUT rather than output). Falls back to a generic framing if no
    top state is available (e.g. a fully flat/zero-signal session).
    """
    top_states = context.get("top_states", [])
    if not top_states:
        return (
            "No strong signal yet in any particular direction. Write a "
            "general, open-ended question inviting the principal to add "
            "anything relevant in their own words."
        )
    lines = ["Internal signal (never reveal these details to the principal):"]
    for entry in top_states[:3]:
        profile = STATE_PROFILES.get(entry.get("state_id", ""))
        if profile is None:
            continue
        prose = profile.descriptive_prose or ""
        lines.append(f"- {profile.primary_dimension} axis, rank {entry.get('rank')}: {prose}")
    lines.append(
        f"\nCurrent entropy: {context.get('entropy')}/{context.get('max_entropy')} "
        "(higher = less certainty in the current picture)."
    )
    return "\n".join(lines)


def generate_narrative_prompt(
    context: dict,
    model: str = "claude-sonnet-4-6",
    client=None,
    timeout: float = 15.0,
) -> NarrativePromptResult:
    """
    Generate the principal-facing narrative question -- P-04 locked
    ("dynamically generated, not static"). Mirrors
    engine/output_synthesis.py::synthesize()'s pattern exactly: direct
    Anthropic call, max_retries=0, the same 15.0s LOCKED timeout real
    Production latency data justified for this class of call
    (tools/_mob.txt Section 13a, "Synthesis pipeline failing on
    Production"). On any failure, returns the static fallback rather
    than ever blocking the live flow -- narrative modulation is
    confirmation-and-elevation only, never load-bearing for completion.

    context: build_narrative_prompt_context()'s output (top_states,
    entropy, max_entropy) -- internal signal only, used to inform theme
    relevance. Never exposes state_id, dimension names, or scores to
    the principal -- enforced by the system prompt's own instruction,
    not by omission from context alone.
    """
    try:
        import anthropic as _anthropic
    except ImportError:
        return NarrativePromptResult(
            prompt=_NARRATIVE_PROMPT_FALLBACK, is_fallback=True,
            parse_error="anthropic package not installed",
        )

    if client is None:
        client = _anthropic.Anthropic(max_retries=0)

    user_content = _build_prompt_generation_input(context)

    try:
        message = client.messages.create(
            model=model,
            max_tokens=150,
            temperature=0.6,
            system=NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
            timeout=timeout,
        )
        text = message.content[0].text.strip()
    except Exception as e:
        return NarrativePromptResult(
            prompt=_NARRATIVE_PROMPT_FALLBACK, is_fallback=True,
            parse_error=f"API error: {e}",
        )

    if not text:
        return NarrativePromptResult(
            prompt=_NARRATIVE_PROMPT_FALLBACK, is_fallback=True,
            parse_error="empty response",
        )

    return NarrativePromptResult(prompt=text, is_fallback=False)
