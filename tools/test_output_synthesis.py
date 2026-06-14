"""
PRV3 Output Layer — Output Synthesis Unit Tests

Verifies the 5-field contract migration (S42):
  1.  SynthesisResult: 5 content fields + confidence + is_fallback + metadata
  2.  SynthesisResult: is_fallback defaults to False
  3.  SynthesisResult: observable_indicators accepts list
  4.  _parse_synthesis_response: valid 5-field JSON → correct SynthesisResult
  5.  _parse_synthesis_response: synthesis_confidence correct
  6.  _parse_synthesis_response: invalid JSON → full fallback, is_fallback=True
  7.  _parse_synthesis_response: parse error populates parse_error field
  8.  _parse_synthesis_response: missing required field → full fallback, not partial
  9.  _parse_synthesis_response: observable_indicators not a list → coerced to []
  10. get_fallback_synthesis: returns dict with 5 correct keys
  11. get_fallback_synthesis: fallback text is non-empty for known key
  12. synthesize: missing anthropic package → is_fallback=True with coherent fallback
  13. synthesize: coherent fallback has all 5 fields populated (no empty required strings)
  14. synthesize: coherent fallback has is_fallback=True
  15. synthesize: fallback observable_indicators is a list
  16. OUTPUT_SYNTHESIS_SYSTEM_PROMPT: no old service names
  17. OUTPUT_SYNTHESIS_SYSTEM_PROMPT: 5-field JSON output format required
  18. OUTPUT_SYNTHESIS_SYSTEM_PROMPT: no semicolons constraint present
  19. OUTPUT_SYNTHESIS_SYSTEM_PROMPT: brevity constraint present
  20. _build_synthesis_prompt: includes state_name
  21. _build_synthesis_prompt: includes severity_tier
  22. _build_synthesis_prompt: includes resolution_family
  23. _build_synthesis_prompt: includes narrative_response context
  24. OutputSynthesisEngine: result is None before first call
  25. OutputSynthesisEngine: result stored after synthesize() call
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import unittest.mock as mock

from engine.output_synthesis import (
    SynthesisResult,
    OUTPUT_SYNTHESIS_SYSTEM_PROMPT,
    _parse_synthesis_response,
    _build_synthesis_prompt,
    synthesize,
    OutputSynthesisEngine,
)
from engine.data.fallback_synthesis import (
    FALLBACK_SYNTHESIS,
    get_fallback_synthesis,
)

PASS = []
FAIL = []

OLD_SERVICE_NAMES = {"formation", "practicum", "counsel", "navigation"}


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Output Synthesis — Unit Tests (5-field contract, S42)")
print("=" * 64)


# ── 1–3. SynthesisResult dataclass ───────────────────────────────────────────

result = SynthesisResult(
    liability_condition_text="test liability",
    asset_resolution_anchor_text="test asset",
    framing_text="test framing",
    observable_indicators=["one", "two"],
    resolution_framing_text="test resolution",
    synthesis_confidence=0.75,
)

check(
    "SynthesisResult: has liability_condition_text",
    result.liability_condition_text == "test liability",
    f"got {result.liability_condition_text!r}",
)
check(
    "SynthesisResult: is_fallback defaults to False",
    result.is_fallback is False,
    f"got {result.is_fallback}",
)
check(
    "SynthesisResult: observable_indicators is list",
    isinstance(result.observable_indicators, list),
    f"got {type(result.observable_indicators)}",
)


# ── 4–5. _parse_synthesis_response: valid JSON ────────────────────────────────

valid_json = json.dumps({
    "liability_condition_text":     "The decision-making pattern is structural.",
    "asset_resolution_anchor_text": "Governance discipline is intact.",
    "framing_text":                 "An organizational pattern is affecting decision-making.",
    "observable_indicators":        ["Decisions escalate to senior leadership.", "Projects stall."],
    "resolution_framing_text":      "Groundwork at this stage produces a clear structural account.",
    "synthesis_confidence":         0.82,
})
parsed = _parse_synthesis_response(valid_json, "Groundwork", "Entrenched")

check(
    "Valid JSON: liability_condition_text populated",
    parsed.liability_condition_text == "The decision-making pattern is structural.",
    f"got {parsed.liability_condition_text!r}",
)
check(
    "Valid JSON: framing_text populated",
    parsed.framing_text == "An organizational pattern is affecting decision-making.",
    f"got {parsed.framing_text!r}",
)
check(
    "Valid JSON: resolution_framing_text populated",
    parsed.resolution_framing_text == "Groundwork at this stage produces a clear structural account.",
    f"got {parsed.resolution_framing_text!r}",
)
check(
    "Valid JSON: observable_indicators is list of 2",
    parsed.observable_indicators == ["Decisions escalate to senior leadership.", "Projects stall."],
    f"got {parsed.observable_indicators!r}",
)
check(
    "Valid JSON: synthesis_confidence correct",
    abs(parsed.synthesis_confidence - 0.82) < 0.001,
    f"got {parsed.synthesis_confidence}",
)
check(
    "Valid JSON: is_fallback False",
    parsed.is_fallback is False,
    f"got {parsed.is_fallback}",
)


# ── 6–7. _parse_synthesis_response: invalid JSON → full fallback ──────────────

bad = _parse_synthesis_response("not json {{{{", "Groundwork", "Entrenched")

check(
    "Invalid JSON: is_fallback True",
    bad.is_fallback is True,
    f"got {bad.is_fallback}",
)
check(
    "Invalid JSON: parse_error populated",
    len(bad.parse_error) > 0,
    "parse_error empty",
)
check(
    "Invalid JSON: liability_condition_text from static fallback (not empty)",
    len(bad.liability_condition_text) > 0,
    "fallback text is empty",
)
check(
    "Invalid JSON: framing_text from static fallback (not empty)",
    len(bad.framing_text) > 0,
    "fallback framing is empty",
)


# ── 8. _parse_synthesis_response: missing required field → full fallback ──────

missing_liability_json = json.dumps({
    "liability_condition_text":     "",  # empty — required field missing
    "asset_resolution_anchor_text": "some asset text",
    "framing_text":                 "some framing text",
    "observable_indicators":        ["indicator"],
    "resolution_framing_text":      "some resolution",
    "synthesis_confidence":         0.5,
})
missing_result = _parse_synthesis_response(missing_liability_json, "Groundwork", "Entrenched")

check(
    "Missing required field: is_fallback True",
    missing_result.is_fallback is True,
    f"got {missing_result.is_fallback}",
)
check(
    "Missing required field: full fallback not partial (liability from static dict)",
    len(missing_result.liability_condition_text) > 0,
    "fallback liability is empty",
)
check(
    "Missing required field: parse_error populated",
    "missing required fields" in missing_result.parse_error,
    f"got {missing_result.parse_error!r}",
)


# ── 9. _parse_synthesis_response: observable_indicators not a list ────────────

not_list_json = json.dumps({
    "liability_condition_text":     "Some liability text.",
    "asset_resolution_anchor_text": "",
    "framing_text":                 "Some framing text.",
    "observable_indicators":        "should be a list not a string",
    "resolution_framing_text":      "Some resolution text.",
    "synthesis_confidence":         0.6,
})
not_list_result = _parse_synthesis_response(not_list_json, "Groundwork", "Entrenched")

check(
    "observable_indicators not list: coerced to []",
    not_list_result.observable_indicators == [],
    f"got {not_list_result.observable_indicators!r}",
)
check(
    "observable_indicators not list: is_fallback stays False",
    not_list_result.is_fallback is False,
    f"got {not_list_result.is_fallback}",
)


# ── 10–11. get_fallback_synthesis: structure and content ──────────────────────

REQUIRED_KEYS = {
    "liability_condition_text",
    "asset_resolution_anchor_text",
    "framing_text",
    "observable_indicators",
    "resolution_framing_text",
}

fb_entry = get_fallback_synthesis("Groundwork", "Entrenched")

check(
    "get_fallback_synthesis: returns dict with 5 correct keys",
    set(fb_entry.keys()) == REQUIRED_KEYS,
    f"got keys: {set(fb_entry.keys())}",
)
check(
    "get_fallback_synthesis: liability_condition_text non-empty for known key",
    len(fb_entry["liability_condition_text"]) > 0,
    "empty liability_condition_text",
)
check(
    "get_fallback_synthesis: asset_resolution_anchor_text is empty string",
    fb_entry["asset_resolution_anchor_text"] == "",
    f"got {fb_entry['asset_resolution_anchor_text']!r}",
)
check(
    "get_fallback_synthesis: observable_indicators is empty list",
    fb_entry["observable_indicators"] == [],
    f"got {fb_entry['observable_indicators']!r}",
)
check(
    "get_fallback_synthesis: unknown key returns generic entry",
    len(get_fallback_synthesis("Unknown", "Entrenched")["liability_condition_text"]) > 0,
    "generic fallback is empty",
)


# ── 12–15. synthesize: missing anthropic → coherent full fallback ─────────────

with mock.patch.dict("sys.modules", {"anthropic": None}):
    fallback_result = synthesize(
        state_name="Decision Paralysis",
        severity_tier="Entrenched",
        resolution_family="Groundwork",
    )

check(
    "Missing anthropic: is_fallback True",
    fallback_result.is_fallback is True,
    f"got {fallback_result.is_fallback}",
)
check(
    "Missing anthropic: liability_condition_text non-empty (coherent fallback)",
    len(fallback_result.liability_condition_text) > 0,
    "fallback liability is empty — partial LLM survival detected",
)
check(
    "Missing anthropic: framing_text non-empty (coherent fallback)",
    len(fallback_result.framing_text) > 0,
    "fallback framing is empty",
)
check(
    "Missing anthropic: resolution_framing_text non-empty (coherent fallback)",
    len(fallback_result.resolution_framing_text) > 0,
    "fallback resolution is empty",
)
check(
    "Missing anthropic: observable_indicators is a list",
    isinstance(fallback_result.observable_indicators, list),
    f"got {type(fallback_result.observable_indicators)}",
)


# ── 16–19. OUTPUT_SYNTHESIS_SYSTEM_PROMPT quality ────────────────────────────

prompt_lower = OUTPUT_SYNTHESIS_SYSTEM_PROMPT.lower()

for sn in OLD_SERVICE_NAMES:
    check(
        f"System prompt: no old service name '{sn}'",
        sn not in prompt_lower,
        f"found '{sn}' in system prompt",
    )

check(
    "System prompt: 5-field JSON output format — liability_condition_text",
    "liability_condition_text" in OUTPUT_SYNTHESIS_SYSTEM_PROMPT,
    "field not found in prompt",
)
check(
    "System prompt: 5-field JSON output format — synthesis_confidence",
    "synthesis_confidence" in OUTPUT_SYNTHESIS_SYSTEM_PROMPT,
    "field not found in prompt",
)
check(
    "System prompt: no semicolons constraint present",
    "semicolons" in prompt_lower,
    "semicolons constraint not found",
)
check(
    "System prompt: brevity constraint present",
    "limit all text fields" in prompt_lower,
    "brevity constraint not found",
)


# ── 20–23. _build_synthesis_prompt ───────────────────────────────────────────

prompt_text = _build_synthesis_prompt(
    state_name="Decision Paralysis",
    severity_tier="Entrenched",
    resolution_family="Groundwork",
    asset_score=0.15,
    liability_score=0.60,
    narrative_response="Leadership keeps deferring the hard calls.",
    intake={"organization_size": "medium", "industry": "healthcare", "role_level": "director"},
)

check(
    "_build_synthesis_prompt: includes state_name",
    "Decision Paralysis" in prompt_text,
    "state_name not found",
)
check(
    "_build_synthesis_prompt: includes severity_tier",
    "Entrenched" in prompt_text,
    "severity_tier not found",
)
check(
    "_build_synthesis_prompt: includes resolution_family",
    "Groundwork" in prompt_text,
    "resolution_family not found",
)
check(
    "_build_synthesis_prompt: includes narrative_response",
    "Leadership keeps deferring the hard calls." in prompt_text,
    "narrative_response not found",
)


# ── 24–25. OutputSynthesisEngine stateful interface ──────────────────────────

engine = OutputSynthesisEngine(model="claude-sonnet-4-6")

check(
    "OutputSynthesisEngine: result is None before first call",
    engine.result is None,
    f"got result={engine.result}",
)

with mock.patch.dict("sys.modules", {"anthropic": None}):
    stored = engine.synthesize(
        state_name="Decision Paralysis",
        severity_tier="Entrenched",
        resolution_family="Groundwork",
    )

check(
    "OutputSynthesisEngine: result stored after synthesize() call",
    engine.result is not None,
    "engine.result is still None",
)
check(
    "OutputSynthesisEngine: synthesize() returns same object as engine.result",
    stored is engine.result,
    "returned object differs from engine.result",
)


# ── Results ───────────────────────────────────────────────────────────────────

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  {f}")
else:
    print("All tests passed.")

sys.exit(0 if not FAIL else 1)
