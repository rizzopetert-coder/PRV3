"""
PRV3 Scoring Engine — Output Layer
Output Synthesis

Generates five synthesis fields from a diagnosed organizational state.
Single LLM call. Returns SynthesisResult. On timeout or parse failure,
returns full SynthesisResult from fallback_synthesis.py static dict.
No partial LLM survival — coherence over completeness (Gemini Q2, S42).

Context object: state_name, severity_tier, resolution_family (commercial name),
asset_score, liability_score, narrative_response, intake, signal_map_context.

Spec reference: PRV3_Output_Synthesis_Prompts_v1.0.docx — Session 42.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from engine.data.fallback_synthesis import get_fallback_synthesis


# ── System prompt ──────────────────────────────────────────────────────────────

OUTPUT_SYNTHESIS_SYSTEM_PROMPT: str = """\
You are generating output copy for a professional organizational diagnostic instrument.
The person reading this is an internal leader with budget authority who has just received
a verdict about their organization. They are not a consulting industry insider. They did
not come here to be impressed. They came here because something is wrong and they want
to understand it clearly.

Voice standard:
Write the way a trusted advisor would speak. Someone who has been in rooms like this
before, who knows what they are looking at, and who respects the reader enough to say
it plainly. Direct and warm. Serious without being clinical. No consulting vocabulary.
No jargon. No passive constructions. No hedging.

Banned words and phrases: alignment, bandwidth, stakeholder, ecosystem, synergy,
leverage (as a verb), utilize, robust, scalable, actionable, going forward, at the end
of the day, best practices, move the needle, circle back, deep dive.

Format rules:
No em dashes. No bullet points unless the field specification requires a list.
No semicolons. Limit all text fields to 2-3 concise sentences. Output strict JSON.
Short sentences preferred over long ones. Plain words preferred over elevated ones.

The diagnostic has already named the condition and the severity. Do not restate
them unless the field specification requires it. Do not soften the verdict.
Do not add encouragement that was not earned. Do not add caveats that
undermine the finding.

Clinical boundary: no service names appear in any generated field other than the
resolution_family name provided. The diagnostic instrument does not prescribe
specific engagements.

Use all fields in the context object. Copy that could have been written without
the principal's specific responses is not good enough.

FIELDS

liability_condition_text (private — principal only):
What is happening in this organization. Clinical and direct. 2-4 sentences.
Draw from narrative_response and intake. Name what they described. Do not
restate the state name. Describe what it is doing inside their organization right now.
Severity calibration:
  Emerging: describe what is visible and what is coming if not addressed.
  Entrenched: describe what has become normal and what that normalization is costing.
  Endemic: describe what the organization has organized itself around.

asset_resolution_anchor_text (private — principal only):
What strength exists to build from. 1-3 sentences. Draw from asset_score and intake.
Not reassurance. An honest account of what is working. If asset_score is low, say so
plainly. Do not manufacture strength the diagnostic did not find.

framing_text (shareable — professional audience):
Professional framing for a board member or senior leader. 2-3 sentences.
Non-confrontational. No liability language. Behavioral and operational, not accusatory.
Creates conditions for a conversation, not a verdict.

observable_indicators (shareable — JSON array of strings):
3-5 behavioral and operational signals from signal_map_context. Things visible and
verifiable by someone outside the principal's team. Specific enough to be
recognizable, general enough for a shared document. No accusatory framing.
Return as JSON array of strings.

resolution_framing_text (shareable — professional audience):
2-3 sentences describing the resolution pathway in organizational benefit language.
No liability framing. Reference the resolution_family name naturally. Forward-facing.
Do not name specific service inclusions or make guarantees.

REQUIRED OUTPUT FORMAT

Return only this JSON structure. No preamble. No explanation. No markdown.

{
  "liability_condition_text": "<2-4 sentences>",
  "asset_resolution_anchor_text": "<1-3 sentences>",
  "framing_text": "<2-3 sentences>",
  "observable_indicators": ["<indicator>", "<indicator>", "<indicator>"],
  "resolution_framing_text": "<2-3 sentences>",
  "synthesis_confidence": <float 0.0-1.0>
}\
"""


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class SynthesisResult:
    """
    Output of one synthesis call. Five content fields plus metadata.
    All string fields are empty string on failure. observable_indicators is
    empty list on failure. is_fallback=True when LLM call failed or response
    was unparseable.
    """
    liability_condition_text:     str
    asset_resolution_anchor_text: str
    framing_text:                 str
    observable_indicators:        list
    resolution_framing_text:      str
    synthesis_confidence:         float
    raw_response:                 str  = ""
    parse_error:                  str  = ""
    is_fallback:                  bool = False


# ── Parse ──────────────────────────────────────────────────────────────────────

_MARKDOWN_FENCE_RE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", re.DOTALL)
_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def _strip_markdown_fence(text: str) -> str:
    """Strip a ```json / ``` code fence wrapping the response, if present.

    Models sometimes wrap their JSON in a markdown code fence despite the
    system prompt explicitly instructing otherwise (confirmed live on
    prv-3 Production, Session 72). Returns text unchanged if no fence
    is found, so the already-working bare-JSON case is untouched.
    """
    match = _MARKDOWN_FENCE_RE.match(text.strip())
    return match.group(1).strip() if match else text


def _parse_synthesis_response(
    response_text: str,
    commercial_name: str = "",
    severity_tier: str | None = None,
) -> SynthesisResult:
    """Parse LLM JSON response. Full fallback from static dict on any failure."""
    cleaned = _strip_markdown_fence(response_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Second layer: the model may have added prose around the JSON
        # rather than a clean fence -- extract the outermost {...} block
        # before giving up. Original error preserved in parse_error either way.
        match = _JSON_OBJECT_RE.search(cleaned)
        try:
            if match is None:
                raise e
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            fb = get_fallback_synthesis(commercial_name, severity_tier)
            return SynthesisResult(
                **fb,
                synthesis_confidence=0.0,
                raw_response=response_text,
                parse_error=str(e),
                is_fallback=True,
            )

    liability  = str(data.get("liability_condition_text", "")).strip()
    asset      = str(data.get("asset_resolution_anchor_text", "")).strip()
    framing    = str(data.get("framing_text", "")).strip()
    indicators = data.get("observable_indicators", [])
    if not isinstance(indicators, list):
        indicators = []
    indicators = [str(i) for i in indicators]
    resolution = str(data.get("resolution_framing_text", "")).strip()
    confidence = float(data.get("synthesis_confidence", 0.0))

    if not liability or not framing or not resolution:
        fb = get_fallback_synthesis(commercial_name, severity_tier)
        return SynthesisResult(
            **fb,
            synthesis_confidence=0.0,
            raw_response=response_text,
            parse_error="missing required fields",
            is_fallback=True,
        )

    return SynthesisResult(
        liability_condition_text=liability,
        asset_resolution_anchor_text=asset,
        framing_text=framing,
        observable_indicators=indicators,
        resolution_framing_text=resolution,
        synthesis_confidence=confidence,
        raw_response=response_text,
    )


# ── LLM call ──────────────────────────────────────────────────────────────────

def _build_synthesis_prompt(
    state_name: str,
    severity_tier: str,
    resolution_family: str,
    asset_score: float,
    liability_score: float,
    narrative_response: str,
    intake: dict,
    signal_map_context: str = "",
) -> str:
    intake_lines = (
        f"  organization_size: {intake.get('organization_size', intake.get('org_size', ''))}\n"
        f"  industry: {intake.get('industry', '')}\n"
        f"  role: {intake.get('role_level', intake.get('principal_role', ''))}"
    )
    parts = [
        f"state_name: {state_name}",
        f"severity_tier: {severity_tier}",
        f"resolution_family: {resolution_family}",
        f"asset_score: {asset_score:.4f}",
        f"liability_score: {liability_score:.4f}",
        f"narrative_response: {narrative_response or '[not provided]'}",
        f"intake:\n{intake_lines}",
    ]
    if signal_map_context:
        parts.append(f"signal_map_context: {signal_map_context}")
    parts.append("\nGenerate all five synthesis fields for this diagnostic result.")
    return "\n".join(parts)


def synthesize(
    state_name: str,
    severity_tier: str,
    resolution_family: str,
    asset_score: float = 0.0,
    liability_score: float = 0.0,
    narrative_response: str = "",
    intake: dict | None = None,
    signal_map_context: str = "",
    model: str = "claude-sonnet-4-6",
    client=None,
    timeout: float = 15.0,
) -> SynthesisResult:
    """
    Call the LLM to generate five synthesis fields for a diagnostic result.

    Parameters:
      state_name:         identified state name, e.g. "The Founder's Grip"
      severity_tier:      "Emerging" | "Entrenched" | "Endemic"
      resolution_family:  commercial name, e.g. "Groundwork"
      asset_score:        float — counterbalancing strength present
      liability_score:    float — how significantly the dimension is compromised
      narrative_response: principal's free-text from narrative prompt
      intake:             org_size, industry, role, significant events
      signal_map_context: observable signals for the identified state
      model:              LLM model identifier
      client:             anthropic.Anthropic client instance
      timeout:            max seconds to wait (15.0s LOCKED, re-set this
                           session -- Gemini-reviewed, Pete-approved,
                           grounded in real Production latency data (6/6
                           samples, 7.4-13.6s, avg ~9.8s). Supersedes the
                           original 5s LOCKED value (Gemini Q4, S42).

    On timeout or any exception: returns full SynthesisResult from static
    fallback dict. No partial LLM survival. max_tokens=800 (Gemini Q5, S42).
    """
    if intake is None:
        intake = {}

    try:
        import anthropic as _anthropic
    except ImportError:
        fb = get_fallback_synthesis(resolution_family, severity_tier)
        return SynthesisResult(
            **fb,
            synthesis_confidence=0.0,
            parse_error="anthropic package not installed",
            is_fallback=True,
        )

    if client is None:
        # max_retries=0: timeout raised to 15.0s LOCKED (this session,
        # Gemini-reviewed, Pete-approved) on real Production latency data
        # (6/6 samples, 7.4-13.6s). Session 72's max_retries=1 traded a
        # longer worst case for resilience against a transient blip -- at
        # 15s that trade no longer holds: one retry means a ~30-40s worst
        # case, unacceptable UX regardless of Vercel's platform ceiling
        # (confirmed 300s, Hobby + Fluid compute -- no collision risk).
        # Fail fast at 15s instead.
        client = _anthropic.Anthropic(max_retries=0)

    prompt = _build_synthesis_prompt(
        state_name=state_name,
        severity_tier=severity_tier,
        resolution_family=resolution_family,
        asset_score=asset_score,
        liability_score=liability_score,
        narrative_response=narrative_response,
        intake=intake,
        signal_map_context=signal_map_context,
    )

    try:
        message = client.messages.create(
            model=model,
            max_tokens=800,
            temperature=0.3,
            system=OUTPUT_SYNTHESIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            timeout=timeout,
        )
        response_text = message.content[0].text
    except Exception as e:
        fb = get_fallback_synthesis(resolution_family, severity_tier)
        return SynthesisResult(
            **fb,
            synthesis_confidence=0.0,
            parse_error=f"API error: {e}",
            is_fallback=True,
        )

    return _parse_synthesis_response(response_text, resolution_family, severity_tier)


# ── Engine class ───────────────────────────────────────────────────────────────

class OutputSynthesisEngine:
    """
    Orchestrates one synthesis pass for a scoring session.
    Stores result for downstream access.
    """

    def __init__(self, model: str = "claude-sonnet-4-6", client=None):
        self.model = model
        self._client = client
        self.result: Optional[SynthesisResult] = None

    def synthesize(
        self,
        state_name: str,
        severity_tier: str,
        resolution_family: str,
        asset_score: float = 0.0,
        liability_score: float = 0.0,
        narrative_response: str = "",
        intake: dict | None = None,
        signal_map_context: str = "",
        timeout: float = 15.0,
    ) -> SynthesisResult:
        """Run synthesis and store result for downstream access."""
        self.result = synthesize(
            state_name=state_name,
            severity_tier=severity_tier,
            resolution_family=resolution_family,
            asset_score=asset_score,
            liability_score=liability_score,
            narrative_response=narrative_response,
            intake=intake,
            signal_map_context=signal_map_context,
            model=self.model,
            client=self._client,
            timeout=timeout,
        )
        return self.result
