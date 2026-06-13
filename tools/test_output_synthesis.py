"""
PRV3 Output Layer — Output Synthesis Unit Tests

Tests everything except the live LLM API call.
Verifies:
  1. _parse_synthesis_response: valid JSON returns correct SynthesisResult
  2. _parse_synthesis_response: invalid JSON returns fallback
  3. _parse_synthesis_response: empty private_synthesis falls back to _FALLBACK_PRIVATE
  4. _parse_synthesis_response: empty shareable_synthesis falls back to _FALLBACK_SHAREABLE
  5. synthesize: empty state_cluster returns is_fallback=True
  6. synthesize: missing anthropic package returns is_fallback=True
  7. SynthesisResult: is_fallback=False by default
  8. OUTPUT_SYNTHESIS_SYSTEM_PROMPT: no service names, required constraints present
  9. _build_synthesis_prompt: includes state names, severity tier, family
  10. OutputSynthesisEngine: stateful interface stores result
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import json

from engine.output_synthesis import (
    SynthesisResult,
    OUTPUT_SYNTHESIS_SYSTEM_PROMPT,
    _FALLBACK_PRIVATE,
    _FALLBACK_SHAREABLE,
    _parse_synthesis_response,
    _build_synthesis_prompt,
    synthesize,
    OutputSynthesisEngine,
)

PASS = []
FAIL = []

SERVICE_NAMES = {"formation", "practicum", "counsel", "navigation"}


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Output Synthesis — Unit Tests")
print("=" * 64)


# ── 1. Valid JSON parse ────────────────────────────────────────────────────────

valid_json = json.dumps({
    "private_synthesis": "The organization has a structural problem.",
    "shareable_synthesis": "An organizational pattern has been identified.",
    "synthesis_confidence": 0.85,
})
result = _parse_synthesis_response(valid_json)

check(
    "Valid JSON: private_synthesis populated",
    result.private_synthesis == "The organization has a structural problem.",
    f"got {result.private_synthesis!r}",
)
check(
    "Valid JSON: shareable_synthesis populated",
    result.shareable_synthesis == "An organizational pattern has been identified.",
    f"got {result.shareable_synthesis!r}",
)
check(
    "Valid JSON: synthesis_confidence correct",
    abs(result.synthesis_confidence - 0.85) < 0.001,
    f"got {result.synthesis_confidence}",
)
check(
    "Valid JSON: is_fallback False",
    result.is_fallback is False,
    f"got is_fallback={result.is_fallback}",
)
check(
    "Valid JSON: no parse_error",
    result.parse_error == "",
    f"got parse_error={result.parse_error!r}",
)


# ── 2. Invalid JSON returns fallback ──────────────────────────────────────────

bad_result = _parse_synthesis_response("not json at all {{{")
check(
    "Invalid JSON: is_fallback True",
    bad_result.is_fallback is True,
    f"got is_fallback={bad_result.is_fallback}",
)
check(
    "Invalid JSON: parse_error populated",
    len(bad_result.parse_error) > 0,
    f"parse_error empty",
)
check(
    "Invalid JSON: private_synthesis is fallback text",
    bad_result.private_synthesis == _FALLBACK_PRIVATE,
    f"got {bad_result.private_synthesis!r}",
)


# ── 3. Empty private_synthesis falls back ─────────────────────────────────────

empty_private_json = json.dumps({
    "private_synthesis": "",
    "shareable_synthesis": "Some shareable text.",
    "synthesis_confidence": 0.5,
})
result_ep = _parse_synthesis_response(empty_private_json)
check(
    "Empty private_synthesis: falls back to _FALLBACK_PRIVATE",
    result_ep.private_synthesis == _FALLBACK_PRIVATE,
    f"got {result_ep.private_synthesis!r}",
)


# ── 4. Empty shareable_synthesis falls back ───────────────────────────────────

empty_share_json = json.dumps({
    "private_synthesis": "Some private text.",
    "shareable_synthesis": "",
    "synthesis_confidence": 0.5,
})
result_es = _parse_synthesis_response(empty_share_json)
check(
    "Empty shareable_synthesis: falls back to _FALLBACK_SHAREABLE",
    result_es.shareable_synthesis == _FALLBACK_SHAREABLE,
    f"got {result_es.shareable_synthesis!r}",
)


# ── 5. Empty state_cluster returns fallback ───────────────────────────────────

# Mock out anthropic import to isolate
import unittest.mock as mock
with mock.patch.dict("sys.modules", {"anthropic": mock.MagicMock()}):
    result_empty = synthesize(
        state_cluster=[],
        severity_tier="Entrenched",
        resolution_family_id="structural",
    )
check(
    "Empty state_cluster: is_fallback True",
    result_empty.is_fallback is True,
    f"got is_fallback={result_empty.is_fallback}",
)


# ── 6. Missing anthropic returns fallback ─────────────────────────────────────

with mock.patch.dict("sys.modules", {"anthropic": None}):
    result_no_pkg = synthesize(
        state_cluster=[{"state_id": "decision_paralysis", "state_name": "Decision Paralysis", "score": 0.8}],
        severity_tier="Entrenched",
        resolution_family_id="structural",
    )
check(
    "Missing anthropic package: is_fallback True",
    result_no_pkg.is_fallback is True,
    f"got is_fallback={result_no_pkg.is_fallback}",
)


# ── 7. SynthesisResult default is_fallback ────────────────────────────────────

default_result = SynthesisResult(
    private_synthesis="test",
    shareable_synthesis="test",
    synthesis_confidence=0.0,
)
check(
    "SynthesisResult: is_fallback defaults to False",
    default_result.is_fallback is False,
    f"got {default_result.is_fallback}",
)


# ── 8. System prompt constraints ──────────────────────────────────────────────

prompt_lower = OUTPUT_SYNTHESIS_SYSTEM_PROMPT.lower()

for sn in SERVICE_NAMES:
    check(
        f"System prompt: no service name '{sn}'",
        sn not in prompt_lower,
        f"found '{sn}' in system prompt",
    )

check(
    "System prompt: JSON output format required",
    "private_synthesis" in OUTPUT_SYNTHESIS_SYSTEM_PROMPT,
    "missing private_synthesis field",
)
check(
    "System prompt: no semicolons constraint present",
    "semicolons" in prompt_lower,
    "semicolons constraint not found",
)


# ── 9. _build_synthesis_prompt content ────────────────────────────────────────

cluster = [
    {"state_id": "decision_paralysis", "state_name": "Decision Paralysis", "score": 0.65},
    {"state_id": "the_fracture", "state_name": "The Fracture", "score": 0.45},
]
prompt_text = _build_synthesis_prompt(cluster, "Entrenched", "structural")

check(
    "_build_synthesis_prompt: includes state name",
    "Decision Paralysis" in prompt_text,
    "state name not found",
)
check(
    "_build_synthesis_prompt: includes severity tier",
    "Entrenched" in prompt_text,
    "severity tier not found",
)
check(
    "_build_synthesis_prompt: includes resolution family",
    "structural" in prompt_text,
    "resolution family not found",
)


# ── 10. OutputSynthesisEngine stateful interface ──────────────────────────────

engine = OutputSynthesisEngine(model="claude-sonnet-4-6")
check(
    "OutputSynthesisEngine: result is None before first call",
    engine.result is None,
    f"got result={engine.result}",
)

# Call with empty cluster to exercise fallback path without API
with mock.patch.dict("sys.modules", {"anthropic": mock.MagicMock()}):
    stored = engine.synthesize(
        state_cluster=[],
        severity_tier="Entrenched",
        resolution_family_id="structural",
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
