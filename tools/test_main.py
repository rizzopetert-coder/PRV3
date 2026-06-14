"""
PRV3 Engine Main — Integration Tests
Verifies the unified synthesis block contract (S42 synthesis wiring).
"""

import sys
import unittest.mock as mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.main import run_engine

PASS = []
FAIL = []

VALID_PAYLOAD = {
    "selectedStateIds": ["decision_paralysis"],
    "intake": {
        "headcount": "51-200",
        "industry": "Technology",
        "orgType": "private",
        "jurisdictions": ["US-CA"],
        "significantEvents": [],
        "principalRole": "CEO",
    },
}

EMPTY_STATES_PAYLOAD = {
    "selectedStateIds": [],
    "intake": {
        "headcount": "51-200",
        "industry": "Technology",
        "orgType": "private",
        "jurisdictions": [],
        "significantEvents": [],
        "principalRole": "CEO",
    },
}

_SYNTHESIS_FIELDS = {
    "liability_condition_text", "asset_resolution_anchor_text",
    "framing_text", "observable_indicators", "resolution_framing_text",
    "synthesis_confidence", "is_fallback",
}


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Engine Main — Synthesis Wiring Tests (S42)")
print("=" * 64)

# Run with anthropic mocked absent — synthesis falls back coherently, no LLM call
with mock.patch.dict("sys.modules", {"anthropic": None}):
    result = run_engine(VALID_PAYLOAD)

# 1. synthesis key present at top level
check(
    "synthesis: top-level key present",
    "synthesis" in result,
    f"keys: {list(result.keys())}",
)

# 2. synthesis is not None for non-empty state list
check(
    "synthesis: not None for non-empty states",
    result.get("synthesis") is not None,
    "synthesis is None",
)

# 3–9. synthesis has all 7 required fields
s = result.get("synthesis") or {}
for field in _SYNTHESIS_FIELDS:
    check(
        f"synthesis: has field {field!r}",
        field in s,
        "field missing from synthesis dict",
    )

# 10. observable_indicators is a list
check(
    "synthesis.observable_indicators is list",
    isinstance(s.get("observable_indicators"), list),
    f"got {type(s.get('observable_indicators'))}",
)

# 11. is_fallback is bool
check(
    "synthesis.is_fallback is bool",
    isinstance(s.get("is_fallback"), bool),
    f"got {type(s.get('is_fallback'))}",
)

# 12. synthesis_confidence is float
check(
    "synthesis.synthesis_confidence is float",
    isinstance(s.get("synthesis_confidence"), float),
    f"got {type(s.get('synthesis_confidence'))}",
)

# 13. private_output does NOT contain liability_block or asset_anchor_text
priv = result.get("private_output", {})
check(
    "private_output: no liability_block",
    "liability_block" not in priv,
    "liability_block still in private_output",
)
check(
    "private_output: no asset_anchor_text",
    "asset_anchor_text" not in priv,
    "asset_anchor_text still in private_output",
)

# 14. shareable_output does NOT contain synthesis text fields
shar = result.get("shareable_output", {})
check(
    "shareable_output: no framing_text",
    "framing_text" not in shar,
    "framing_text still in shareable_output",
)
check(
    "shareable_output: no observable_indicators",
    "observable_indicators" not in shar,
    "observable_indicators still in shareable_output",
)
check(
    "shareable_output: no resolution_framing",
    "resolution_framing" not in shar,
    "resolution_framing still in shareable_output",
)

# 15. synthesis is None when no states selected
with mock.patch.dict("sys.modules", {"anthropic": None}):
    result_empty = run_engine(EMPTY_STATES_PAYLOAD)

check(
    "synthesis: None when selectedStateIds is empty",
    result_empty.get("synthesis") is None,
    f"got {result_empty.get('synthesis')}",
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
