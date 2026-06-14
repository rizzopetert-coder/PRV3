"""
PRV3 Scoring Engine — Data Layer
Fallback Synthesis

Static fallback synthesis fields for output_synthesis.py.
Used when LLM call times out or returns an unparseable response.
No partial LLM survival — coherence over completeness (Gemini Q2, S42).

Keyed by (commercial_name, severity_tier).
Single-service keys use severity_tier ("Emerging" | "Entrenched" | "Endemic").
Compound keys use severity_tier=None (tier-agnostic copy).

Source: PRV3_Resolution_Families_Copy_v3.0.docx via RESOLUTION_FALLBACK_COPY.
"""

from __future__ import annotations

from engine.resolution_families import RESOLUTION_FALLBACK_COPY, _FALLBACK_GENERIC


def _make_entry(copy_text: str) -> dict:
    """Build a 5-field synthesis entry from a single copy string."""
    return {
        "liability_condition_text":     copy_text,
        "asset_resolution_anchor_text": "",
        "framing_text":                 copy_text,
        "observable_indicators":        [],
        "resolution_framing_text":      copy_text,
    }


FALLBACK_SYNTHESIS: dict[tuple[str, str | None], dict] = {
    key: _make_entry(copy_text)
    for key, copy_text in RESOLUTION_FALLBACK_COPY.items()
}

_FALLBACK_GENERIC_ENTRY: dict = _make_entry(_FALLBACK_GENERIC)


def get_fallback_synthesis(
    commercial_name: str,
    severity_tier: str | None = None,
) -> dict:
    """
    Return fallback synthesis fields for a commercial name and severity tier.

    Returned dict has exactly 5 keys matching SynthesisResult fields:
        liability_condition_text, asset_resolution_anchor_text, framing_text,
        observable_indicators, resolution_framing_text.

    Single-service names: pass severity_tier ("Emerging", "Entrenched", "Endemic").
    Compound names (contain ' + '): severity_tier is ignored, None key is used.
    Returns generic fallback entry if key is not found.
    """
    if " + " in commercial_name:
        return FALLBACK_SYNTHESIS.get((commercial_name, None), _FALLBACK_GENERIC_ENTRY)
    return FALLBACK_SYNTHESIS.get((commercial_name, severity_tier), _FALLBACK_GENERIC_ENTRY)
