"""
PRV3 Engine Main — Integration Tests
Verifies the unified synthesis block contract (S42 synthesis wiring).
"""

import sys
import unittest.mock as mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.main import (
    run_engine, run_checkpoint, run_accumulated_engine, accumulate_one_answer,
)
from engine.data.states import DIMENSIONAL_FIELDS

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

# ── 16+  run_checkpoint (Phase 2, Stage 4) ─────────────────────────────────────
print("\n" + "=" * 64)
print("run_checkpoint — contract and answered_question_count wiring")
print("=" * 64)

# Nonzero vector so rank_states() produces a real, non-degenerate ranking
# (an all-zero vector at low answered_question_count can trip the
# magnitude guard and return uniform zero scores for every state).
_CP_VECTOR = {"authority_liability": 5.0}

result_cp = run_checkpoint("Q11", _CP_VECTOR, 11, [])

# 16. run_checkpoint returns exactly the CheckpointResultPayload contract
check(
    "run_checkpoint: returns exactly the wire-contract keys",
    set(result_cp.keys()) == {"entropy", "threshold", "fires", "distinguishers", "top_cluster"},
    f"got keys: {sorted(result_cp.keys())}",
)
check(
    "run_checkpoint: entropy is float",
    isinstance(result_cp["entropy"], float),
    f"got {type(result_cp['entropy'])}",
)
check(
    "run_checkpoint: distinguishers is a list of strings, not QuestionDefinition objects",
    isinstance(result_cp["distinguishers"], list)
    and all(isinstance(d, str) for d in result_cp["distinguishers"]),
    f"got {result_cp['distinguishers']!r}",
)

# 17. answered_question_count is actually wired into rank_states()'s centroid
# displacement, not silently ignored — the bug Stage 4 exists to avoid.
# Same accumulated_vector, two different counts, must NOT produce identical
# entropy (the whole point of threading the real live count through).
result_cp_low = run_checkpoint("Q11", _CP_VECTOR, 11, [])
result_cp_high = run_checkpoint("Q11", _CP_VECTOR, 21, [])
check(
    "run_checkpoint: answered_question_count changes entropy for the same vector "
    "(confirms it reaches rank_states(), not silently dropped)",
    result_cp_low["entropy"] != result_cp_high["entropy"],
    f"count=11 entropy={result_cp_low['entropy']!r}, count=21 entropy={result_cp_high['entropy']!r}",
)

# 18. Invalid checkpoint_position propagates as ValueError (api/engine.py
# maps this to 400 — same contract as evaluate_checkpoint() itself).
try:
    run_checkpoint("Q99", _CP_VECTOR, 11, [])
    check("run_checkpoint: invalid checkpoint_position raises ValueError", False, "no exception raised")
except ValueError:
    check("run_checkpoint: invalid checkpoint_position raises ValueError", True)


# ── 19+  run_accumulated_engine — checkpoint_results threading (Stage 4) ──────
print("\n" + "=" * 64)
print("run_accumulated_engine — checkpoint_results -> SessionData -> checkpoint_log")
print("=" * 64)

_LOCKED_INTAKE = {
    "organization_size": "51-200",
    "industry": "Technology",
    "role_level": "CEO",
    "jurisdiction": "US-CA",
}

_WIRE_Q11 = {
    "entropy": 2.5,
    "threshold": 0.6,
    "fires": True,
    "distinguishers": ["DIST-CM-01", "DIST-CM-02"],
    "top_cluster": "C-Manager",
}
_WIRE_Q19 = {
    "entropy": 1.1,
    "threshold": 0.4,
    "fires": False,
    "distinguishers": [],
    "top_cluster": None,
}
# q27 deliberately omitted from the bundle below — a session can complete
# before reaching a later checkpoint; the None-fallthrough path must still
# work cleanly.

with mock.patch.dict("sys.modules", {"anthropic": None}):
    result_with_checkpoints = run_accumulated_engine(
        _CP_VECTOR,
        _LOCKED_INTAKE,
        27,
        {"q11": _WIRE_Q11, "q19": _WIRE_Q19},
    )

cl = result_with_checkpoints.get("checkpoint_log", {})

# 19. checkpoint_log.q11 genuinely populated — THE original bug this whole
# stage sequence exists to fix (previously unconditionally null).
check(
    "checkpoint_log.q11: entropy/threshold/threshold_exceeded/distinguisher_fired "
    "genuinely populated, not null",
    cl.get("q11") == {
        "entropy": 2.5,
        "threshold": 0.6,
        "threshold_exceeded": True,
        "distinguisher_fired": True,
    },
    f"got {cl.get('q11')!r}",
)
check(
    "checkpoint_log.q19: populated, fires=False -> distinguisher_fired=False",
    cl.get("q19") == {
        "entropy": 1.1,
        "threshold": 0.4,
        "threshold_exceeded": False,
        "distinguisher_fired": False,
    },
    f"got {cl.get('q19')!r}",
)
# 20. q27 was never in the bundle — must fall through to the all-null shape,
# not raise or silently default to something else.
check(
    "checkpoint_log.q27: never reached this session -> all-null, no crash",
    cl.get("q27") == {
        "entropy": None,
        "threshold": None,
        "threshold_exceeded": None,
        "distinguisher_fired": None,
    },
    f"got {cl.get('q27')!r}",
)

# 21. checkpoint_results omitted entirely (e.g. an older caller, or Path B's
# equivalent) must still produce a clean all-null checkpoint_log — the
# pre-Stage-4 default behavior, now via an explicit default rather than an
# accident of SessionData's dataclass defaults.
with mock.patch.dict("sys.modules", {"anthropic": None}):
    result_no_checkpoints = run_accumulated_engine(_CP_VECTOR, _LOCKED_INTAKE, 27)

cl_none = result_no_checkpoints.get("checkpoint_log", {})
check(
    "checkpoint_log: all three null when checkpoint_results omitted entirely",
    all(
        cl_none.get(k) == {
            "entropy": None,
            "threshold": None,
            "threshold_exceeded": None,
            "distinguisher_fired": None,
        }
        for k in ("q11", "q19", "q27")
    ),
    f"got {cl_none!r}",
)

# ── 22+  accumulate_one_answer / run_accumulated_engine — severity follow-on
#         wiring (Path 1 only). First time severity.tier can vary from the
#         "Emerging" constant in this project's history. ────────────────────
print("\n" + "=" * 64)
print("Severity follow-on wiring — accumulate_one_answer + run_accumulated_engine")
print("=" * 64)

_SEV_INTAKE = {
    "organization_size": "100-249",
    "industry": "Technology",
    "role_level": "CEO",
    "jurisdiction": "US-CA",
}


def _zero_vector():
    return {f: 0.0 for f in DIMENSIONAL_FIELDS}


# 22. Core question answer, non-triggering option: return shape has all
# three keys, severity_input and severity_follow_on_id both None.
r_core = accumulate_one_answer(_zero_vector(), "Q01", "A", _SEV_INTAKE)
check(
    "accumulate_one_answer: core question (non-triggering) returns all three keys, "
    "severity_input=None, severity_follow_on_id=None",
    set(r_core.keys()) == {"accumulated_vector", "severity_input", "severity_follow_on_id"}
    and r_core["severity_input"] is None
    and r_core["severity_follow_on_id"] is None,
    f"got keys={set(r_core.keys())!r}, severity_input={r_core.get('severity_input')!r}, "
    f"severity_follow_on_id={r_core.get('severity_follow_on_id')!r}",
)

# 22b. Core question Q22 option D: severity_trigger=True in the question
# data -- severity_follow_on_id surfaces "SEVER-04" so the caller knows to
# splice it in next. severity_input stays None (Q22's own option carries
# no severity_input_mapping -- only SEVER-04's own options do).
r_trigger = accumulate_one_answer(_zero_vector(), "Q22", "D", _SEV_INTAKE)
check(
    "accumulate_one_answer: Q22 option D surfaces severity_follow_on_id=SEVER-04, "
    "severity_input stays None",
    r_trigger["severity_follow_on_id"] == "SEVER-04"
    and r_trigger["severity_input"] is None,
    f"got severity_follow_on_id={r_trigger['severity_follow_on_id']!r}, "
    f"severity_input={r_trigger['severity_input']!r}",
)

# 23. SEVER-04 option D (18mo_plus): severity_input populated with the
# real duration_band tag, trigger_question_id threaded from the caller.
# severity_follow_on_id is None here -- SEVER-## answers never trigger a
# further follow-on themselves.
r_sever = accumulate_one_answer(
    r_core["accumulated_vector"], "SEVER-04", "D", _SEV_INTAKE,
    trigger_question_id="Q22",
)
check(
    "accumulate_one_answer: SEVER-04 option D produces real SeverityInput dict",
    r_sever["severity_input"] == {
        "trigger_question_id": "Q22",
        "severity_follow_on_id": "SEVER-04",
        "duration_band": "18mo_plus",
    },
    f"got {r_sever['severity_input']!r}",
)
check(
    "accumulate_one_answer: SEVER-04 answer itself has severity_follow_on_id=None "
    "(follow-ons never chain into a further follow-on)",
    r_sever["severity_follow_on_id"] is None,
    f"got {r_sever['severity_follow_on_id']!r}",
)

# 24. trigger_question_id defaults to the follow-on's own question_id when
# not supplied by the caller (documented simplification).
r_sever_default = accumulate_one_answer(
    r_core["accumulated_vector"], "SEVER-04", "D", _SEV_INTAKE,
)
check(
    "accumulate_one_answer: trigger_question_id defaults to question_id when omitted",
    r_sever_default["severity_input"]["trigger_question_id"] == "SEVER-04",
    f"got {r_sever_default['severity_input']!r}",
)

with mock.patch.dict("sys.modules", {"anthropic": None}):
    # 25. Zero severity_inputs (default None/[]) preserves the original
    # constant-Emerging behavior exactly — backward compatible, and this is
    # Path B's permanent behavior by design (Path B never calls this at all).
    out_zero = run_accumulated_engine(_CP_VECTOR, _LOCKED_INTAKE, 27)
    check(
        "run_accumulated_engine: severity_inputs omitted -> tier stays Emerging (unchanged)",
        out_zero["severity"]["tier"] == "Emerging",
        f"got {out_zero['severity']['tier']!r}",
    )

    # 26. One 18mo_plus duration_band input -> raw=2.0 -> score=33.33 ->
    # Entrenched. First non-"Emerging" tier ever produced in this project.
    out_entrenched = run_accumulated_engine(
        _CP_VECTOR, _LOCKED_INTAKE, 27,
        severity_inputs=[{
            "trigger_question_id": "Q22",
            "severity_follow_on_id": "SEVER-04",
            "duration_band": "18mo_plus",
        }],
    )
    check(
        "run_accumulated_engine: 1x 18mo_plus duration_band -> tier=Entrenched, score=33.33",
        out_entrenched["severity"]["tier"] == "Entrenched"
        and abs(out_entrenched["severity"]["score"] - 33.33) < 0.01,
        f"got tier={out_entrenched['severity']['tier']!r}, score={out_entrenched['severity']['score']!r}",
    )

    # 27. Two 18mo_plus duration_band inputs -> raw=4.0 -> score=66.67 ->
    # Endemic.
    out_endemic = run_accumulated_engine(
        _CP_VECTOR, _LOCKED_INTAKE, 27,
        severity_inputs=[
            {"trigger_question_id": "Q22", "severity_follow_on_id": "SEVER-04",
             "duration_band": "18mo_plus"},
            {"trigger_question_id": "Q24", "severity_follow_on_id": "SEVER-06",
             "duration_band": "18mo_plus"},
        ],
    )
    check(
        "run_accumulated_engine: 2x 18mo_plus duration_band -> tier=Endemic, score=66.67",
        out_endemic["severity"]["tier"] == "Endemic"
        and abs(out_endemic["severity"]["score"] - 66.67) < 0.01,
        f"got tier={out_endemic['severity']['tier']!r}, score={out_endemic['severity']['score']!r}",
    )

    # 28. CALIBRATION TARGET exposure, confirmed not assumed: named_condition/
    # financial_indicators/population_band alone (no duration_band) produce
    # the SAME score regardless of value, since POPULATION_WEIGHTS and the
    # three additive weights are still None (CALIBRATION TARGET) in
    # engine/severity.py -- pre-existing, out of this task's scope to
    # populate. Documents the gap rather than silently passing over it.
    out_named_true = run_accumulated_engine(
        _CP_VECTOR, _LOCKED_INTAKE, 27,
        severity_inputs=[{"trigger_question_id": "Q30", "severity_follow_on_id": "SEVER-01",
                           "named_condition": True}],
    )
    out_named_false = run_accumulated_engine(
        _CP_VECTOR, _LOCKED_INTAKE, 27,
        severity_inputs=[{"trigger_question_id": "Q30", "severity_follow_on_id": "SEVER-01",
                           "named_condition": False}],
    )
    check(
        "CALIBRATION TARGET exposure: named_condition True vs False produce identical "
        "score today (NAMED_CONDITION_WEIGHT still None) -- confirmed, not assumed",
        out_named_true["severity"]["score"] == out_named_false["severity"]["score"],
        f"got True->{out_named_true['severity']['score']!r}, "
        f"False->{out_named_false['severity']['score']!r}",
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
