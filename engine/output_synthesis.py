"""
PRV3 Scoring Engine — Output Layer
Output Synthesis

Generates two synthesis outputs from the ranked state cluster:
  private:   LLM-authored synthesis for the principal only
  shareable: LLM-authored synthesis safe for external sharing

Both are Pass 1 (async, LLM-generated). Pass 2 (per-state blocks) and
Pass 3 (resolution direction) are sync and rendered by output-renderer.ts
without LLM involvement.

Failure fallback: on timeout (5s) or API error, returns deterministic
fallback text so the rendering layer never blocks.

Pattern: follows engine/narrative.py — system prompt constant, dataclass
result, parse function, public call function, engine class.

Spec reference: PRV3 Output Layer Brief — Step 4
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional


# ── System prompt ──────────────────────────────────────────────────────────────

OUTPUT_SYNTHESIS_SYSTEM_PROMPT: str = """\
You are a synthesis engine for the PRV3 organizational diagnostic instrument. \
Your function is to generate two output texts from a ranked state cluster. \
You do not make recommendations. You do not name specific services or \
interventions. You return only structured JSON.

PRIVATE OUTPUT
A synthesis for the principal who completed the diagnostic. \
This text acknowledges what they are carrying, names the condition pattern, \
and indicates the resolution direction without naming a specific service. \
Tone: direct, clinical, without softening. Length: 3-5 sentences.

SHAREABLE OUTPUT
A synthesis safe for sharing with a third party (board member, advisor, \
external party). This text describes what the organization is exhibiting \
without identifying the principal or disclosing internal details. \
It frames the pattern from an organizational-observation perspective. \
Tone: objective, professional. Length: 2-3 sentences.

CONSTRAINTS
- Do not name any specific service, program, or intervention.
- Do not use jargon requiring a glossary.
- Do not use semicolons in any output string.
- Do not soften the condition description.
- The private output may be more direct than the shareable output.
- If the state cluster is empty or insufficient, return the fallback structure.

REQUIRED OUTPUT FORMAT

Return only this JSON structure. No preamble. No explanation. No markdown.

{
  "private_synthesis": "<3-5 sentence synthesis for the principal>",
  "shareable_synthesis": "<2-3 sentence synthesis for external sharing>",
  "synthesis_confidence": <float 0.0-1.0>
}

If the cluster is empty or synthesis is not possible:
{"private_synthesis": "", "shareable_synthesis": "", "synthesis_confidence": 0.0}\
"""


# ── Fallback text ──────────────────────────────────────────────────────────────
# Returned deterministically on timeout or API failure.
# Rendering layer uses this when Pass 1 does not resolve.

_FALLBACK_PRIVATE: str = (
    "The diagnostic has identified a pattern that warrants closer examination. "
    "A full synthesis will be available once the analysis completes."
)

_FALLBACK_SHAREABLE: str = (
    "An organizational pattern has been identified. "
    "Full analysis is pending."
)


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class SynthesisResult:
    """
    Output of one synthesis call.
    Both fields are empty string on failure — never None.
    """
    private_synthesis:    str
    shareable_synthesis:  str
    synthesis_confidence: float
    raw_response:         str = ""
    parse_error:          str = ""
    is_fallback:          bool = False


# ── Parse ──────────────────────────────────────────────────────────────────────

def _parse_synthesis_response(response_text: str) -> SynthesisResult:
    """Parse LLM JSON response. Returns fallback SynthesisResult on any failure."""
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        return SynthesisResult(
            private_synthesis=_FALLBACK_PRIVATE,
            shareable_synthesis=_FALLBACK_SHAREABLE,
            synthesis_confidence=0.0,
            raw_response=response_text,
            parse_error=str(e),
            is_fallback=True,
        )

    private = str(data.get("private_synthesis", "")).strip()
    shareable = str(data.get("shareable_synthesis", "")).strip()
    confidence = float(data.get("synthesis_confidence", 0.0))

    if not private:
        private = _FALLBACK_PRIVATE
    if not shareable:
        shareable = _FALLBACK_SHAREABLE

    return SynthesisResult(
        private_synthesis=private,
        shareable_synthesis=shareable,
        synthesis_confidence=confidence,
        raw_response=response_text,
    )


# ── LLM call ──────────────────────────────────────────────────────────────────

def _build_synthesis_prompt(
    state_cluster: list[dict],
    severity_tier: str,
    resolution_family_id: str,
) -> str:
    """
    Build the user message for the synthesis LLM call.

    state_cluster: list of {"state_id": str, "state_name": str, "score": float}
    severity_tier: "Emerging" | "Entrenched" | "Endemic"
    resolution_family_id: "structural" | "developmental" | "investigative" | "directional"
    """
    cluster_lines = "\n".join(
        f"  - {s['state_name']} (score: {s['score']:.4f})"
        for s in state_cluster
    )
    return (
        f"State cluster (ranked by score):\n{cluster_lines}\n\n"
        f"Severity tier: {severity_tier}\n"
        f"Resolution family: {resolution_family_id}\n\n"
        "Generate the private_synthesis and shareable_synthesis for this cluster."
    )


def synthesize(
    state_cluster: list[dict],
    severity_tier: str,
    resolution_family_id: str,
    model: str = "claude-sonnet-4-6",
    client=None,
    timeout: float = 5.0,
) -> SynthesisResult:
    """
    Call the LLM to generate private and shareable synthesis for a state cluster.

    Parameters:
      state_cluster:        list of {"state_id", "state_name", "score"} dicts
      severity_tier:        "Emerging" | "Entrenched" | "Endemic"
      resolution_family_id: primary family for the cluster
      model:                LLM model identifier
      client:               anthropic.Anthropic client instance
      timeout:              max seconds to wait for LLM response (5s LOCKED)

    Returns SynthesisResult. On timeout or API error, returns a deterministic
    fallback SynthesisResult (is_fallback=True) so the rendering layer never
    blocks on Pass 1.

    LLM call parameters:
      temperature: 0.3
      max_tokens:  400
    """
    try:
        import anthropic as _anthropic
    except ImportError:
        return SynthesisResult(
            private_synthesis=_FALLBACK_PRIVATE,
            shareable_synthesis=_FALLBACK_SHAREABLE,
            synthesis_confidence=0.0,
            parse_error="anthropic package not installed",
            is_fallback=True,
        )

    if not state_cluster:
        return SynthesisResult(
            private_synthesis=_FALLBACK_PRIVATE,
            shareable_synthesis=_FALLBACK_SHAREABLE,
            synthesis_confidence=0.0,
            parse_error="empty state cluster",
            is_fallback=True,
        )

    if client is None:
        client = _anthropic.Anthropic()

    prompt = _build_synthesis_prompt(state_cluster, severity_tier, resolution_family_id)

    try:
        import httpx as _httpx
        with _httpx.Client(timeout=timeout):
            message = client.messages.create(
                model=model,
                max_tokens=400,
                temperature=0.3,
                system=OUTPUT_SYNTHESIS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                timeout=timeout,
            )
            response_text = message.content[0].text
    except Exception as e:
        return SynthesisResult(
            private_synthesis=_FALLBACK_PRIVATE,
            shareable_synthesis=_FALLBACK_SHAREABLE,
            synthesis_confidence=0.0,
            parse_error=f"API error: {e}",
            is_fallback=True,
        )

    return _parse_synthesis_response(response_text)


# ── Engine class ───────────────────────────────────────────────────────────────

class OutputSynthesisEngine:
    """
    Orchestrates one synthesis pass for a scoring session.

    Usage:
        engine = OutputSynthesisEngine(model="claude-sonnet-4-6")
        result = engine.synthesize(state_cluster, severity_tier, resolution_family_id)
        # result.private_synthesis   → private output text
        # result.shareable_synthesis → shareable output text
        # result.is_fallback         → True if LLM call failed

    Spec reference: PRV3 Output Layer Brief — Step 4
    """

    def __init__(self, model: str = "claude-sonnet-4-6", client=None):
        self.model = model
        self._client = client
        self.result: Optional[SynthesisResult] = None

    def synthesize(
        self,
        state_cluster: list[dict],
        severity_tier: str,
        resolution_family_id: str,
        timeout: float = 5.0,
    ) -> SynthesisResult:
        """Run synthesis and store result for downstream access."""
        self.result = synthesize(
            state_cluster=state_cluster,
            severity_tier=severity_tier,
            resolution_family_id=resolution_family_id,
            model=self.model,
            client=self._client,
            timeout=timeout,
        )
        return self.result
