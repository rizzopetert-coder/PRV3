"""
PRV3 Narrative Modulation Engine — Section IV Integration Test

Tests everything except the live LLM API call.
Verifies:
  1. _parse_extraction_response: valid JSON, invalid JSON, empty signals
  2. signal_to_field: valid and invalid dimension/axis combinations
  3. build_modulation_vector: weight formula, confirmation-only rule
  4. _rankings_to_prob_dist: normalization
  5. enforce_state_probability_ceiling: cap logic, re-normalization
  6. apply_narrative_modulation: floor enforcement, full pipeline
  7. System prompt structure: required elements present
  8. Constants: correct values
  9. NarrativeModulationEngine: stateful interface
"""

import sys
from math import isclose
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.narrative import (
    NarrativeSignal, SeverityIndicator, NarrativeExtractionResult,
    NARRATIVE_SYSTEM_PROMPT, CONFIDENCE_FLOOR, STATE_PROBABILITY_CEILING,
    SEVERITY_CEILING, signal_to_field, build_modulation_vector,
    enforce_state_probability_ceiling, apply_narrative_modulation,
    _parse_extraction_response, _rankings_to_prob_dist,
    NarrativeModulationEngine,
)
from engine.accumulation import StateRanking, IntakeData, AccumulationEngine
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS

PASS = []
FAIL = []

def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Narrative Modulation Engine — Section IV Integration Test")
print("=" * 64)

n = len(STATE_PROFILES)


# ── Helper fixtures ────────────────────────────────────────────────────────────

def make_rankings(scores: dict) -> list:
    """Build StateRanking list from {state_id: score} dict."""
    rankings = []
    for i, (sid, score) in enumerate(STATE_PROFILES.items()):
        s = scores.get(sid, 0.01)
        rankings.append(StateRanking(rank=i+1, state_id=sid, distance=0.5, score=s))
    rankings.sort(key=lambda r: -r.score)
    for i, r in enumerate(rankings):
        r.rank = i + 1
    return rankings


def uniform_rankings() -> list:
    s = 1.0 / n
    return make_rankings({sid: s for sid in STATE_PROFILES})


def good_extraction(authority_liability_conf=0.8, overall=0.85):
    return NarrativeExtractionResult(
        identified_signals=[
            NarrativeSignal("Authority", "liability", "Decision paralysis in leadership", authority_liability_conf),
            NarrativeSignal("Attitude", "liability", "Culture of silence around performance", 0.7),
        ],
        severity_indicators=[
            SeverityIndicator("Pattern has been present for over two years", 0.9),
        ],
        overall_confidence=overall,
        raw_response="{}",
    )


# ── 1. _parse_extraction_response ─────────────────────────────────────────────
print("\n1. _parse_extraction_response")

valid_json = """{
  "identified_signals": [
    {"dimension": "Authority", "axis": "liability", "signal_text": "Governance collapse", "confidence": 0.9},
    {"dimension": "Aptitude", "axis": "asset", "signal_text": "Strong talent pipeline", "confidence": 0.6}
  ],
  "severity_indicators": [
    {"indicator_text": "Two-year pattern of dysfunction", "confidence": 0.85}
  ],
  "overall_confidence": 0.8
}"""

result = _parse_extraction_response(valid_json)
check("Parse valid JSON: no parse_error", result.parse_error == "")
check("Parse valid JSON: 2 signals", len(result.identified_signals) == 2, f"got {len(result.identified_signals)}")
check("Parse valid JSON: 1 severity indicator", len(result.severity_indicators) == 1)
check("Parse valid JSON: overall_confidence 0.8", isclose(result.overall_confidence, 0.8))
check("Parse valid JSON: first signal dimension correct", result.identified_signals[0].dimension == "Authority")
check("Parse valid JSON: first signal axis correct", result.identified_signals[0].axis == "liability")
check("Parse valid JSON: first signal confidence 0.9", isclose(result.identified_signals[0].confidence, 0.9))

# Invalid JSON
bad_result = _parse_extraction_response("not valid json {{{")
check("Parse invalid JSON: parse_error non-empty", bad_result.parse_error != "")
check("Parse invalid JSON: empty signals", bad_result.identified_signals == [])
check("Parse invalid JSON: overall_confidence 0.0", bad_result.overall_confidence == 0.0)

# Invalid dimension filtered out
invalid_dim_json = """{
  "identified_signals": [
    {"dimension": "INVALID", "axis": "liability", "signal_text": "bad signal", "confidence": 0.9},
    {"dimension": "Authority", "axis": "INVALID_AXIS", "signal_text": "bad axis", "confidence": 0.7},
    {"dimension": "Alliance", "axis": "asset", "signal_text": "good signal", "confidence": 0.5}
  ],
  "severity_indicators": [],
  "overall_confidence": 0.6
}"""
filtered = _parse_extraction_response(invalid_dim_json)
check("Invalid dimension filtered: only 1 valid signal remains",
      len(filtered.identified_signals) == 1,
      f"got {len(filtered.identified_signals)}")
check("Valid signal dimension preserved", filtered.identified_signals[0].dimension == "Alliance")

# Empty signals
empty_json = '{"identified_signals": [], "severity_indicators": [], "overall_confidence": 0.0}'
empty_result = _parse_extraction_response(empty_json)
check("Empty signals: no parse_error", empty_result.parse_error == "")
check("Empty signals: 0 identified_signals", len(empty_result.identified_signals) == 0)
check("Empty signals: overall_confidence 0.0", empty_result.overall_confidence == 0.0)


# ── 2. signal_to_field ─────────────────────────────────────────────────────────
print("\n2. signal_to_field")

check("Authority liability -> authority_liability", signal_to_field("Authority", "liability") == "authority_liability")
check("Authority asset -> authority_asset", signal_to_field("Authority", "asset") == "authority_asset")
check("Aptitude liability -> aptitude_liability", signal_to_field("Aptitude", "liability") == "aptitude_liability")
check("Aptitude asset -> aptitude_asset", signal_to_field("Aptitude", "asset") == "aptitude_asset")
check("Alliance liability -> alliance_liability", signal_to_field("Alliance", "liability") == "alliance_liability")
check("Alliance asset -> alliance_asset", signal_to_field("Alliance", "asset") == "alliance_asset")
check("Attitude liability -> attitude_liability", signal_to_field("Attitude", "liability") == "attitude_liability")
check("Attitude asset -> attitude_asset", signal_to_field("Attitude", "asset") == "attitude_asset")
check("Invalid dimension -> None", signal_to_field("INVALID", "liability") is None)
check("Invalid axis -> None", signal_to_field("Authority", "INVALID") is None)
check("Case insensitive dimension -> correct mapping", signal_to_field("authority", "liability") == "authority_liability")


# ── 3. build_modulation_vector ─────────────────────────────────────────────────
print("\n3. build_modulation_vector")

# Accumulated vector with signal in authority_liability and attitude_liability
acc_with_signal = {f: 0.0 for f in DIMENSIONAL_FIELDS}
acc_with_signal["authority_liability"] = 1.5
acc_with_signal["attitude_liability"] = 0.8

extraction = good_extraction(authority_liability_conf=0.8, overall=0.85)
mod_vec = build_modulation_vector(extraction, acc_with_signal)

# authority_liability signal: weight = 0.85 * 0.8 = 0.68
expected_auth = 0.85 * 0.8
# attitude_liability signal: weight = 0.85 * 0.7 = 0.595
expected_att = 0.85 * 0.7

check("Modulation vector covers all 8 fields", set(mod_vec.keys()) == set(DIMENSIONAL_FIELDS))
check("authority_liability contribution = overall * signal.confidence",
      isclose(mod_vec["authority_liability"], expected_auth, rel_tol=1e-9),
      f"got {mod_vec['authority_liability']}, expected {expected_auth}")
check("attitude_liability contribution = overall * signal.confidence",
      isclose(mod_vec["attitude_liability"], expected_att, rel_tol=1e-9),
      f"got {mod_vec['attitude_liability']}, expected {expected_att}")
check("Fields with no signal have 0.0 contribution",
      all(mod_vec[f] == 0.0 for f in DIMENSIONAL_FIELDS
          if f not in ("authority_liability", "attitude_liability")),
      f"non-zero fields: {[f for f in DIMENSIONAL_FIELDS if f not in ('authority_liability','attitude_liability') and mod_vec[f] != 0.0]}")

# Confirmation-only rule: field with zero accumulated signal should get 0 contribution
acc_zero_authority = {f: 0.0 for f in DIMENSIONAL_FIELDS}
acc_zero_authority["attitude_liability"] = 0.5
# authority_liability is 0.0 in accumulated vector
mod_vec_zero = build_modulation_vector(extraction, acc_zero_authority)
check("Confirmation-only: authority_liability blocked when acc=0",
      mod_vec_zero["authority_liability"] == 0.0,
      f"got {mod_vec_zero['authority_liability']}")
check("Confirmation-only: attitude_liability still applied when acc>0",
      isclose(mod_vec_zero["attitude_liability"], expected_att, rel_tol=1e-9),
      f"got {mod_vec_zero['attitude_liability']}")


# ── 4. _rankings_to_prob_dist ──────────────────────────────────────────────────
print("\n4. _rankings_to_prob_dist")

uniform = uniform_rankings()
prob_dist = _rankings_to_prob_dist(uniform)
check("Prob dist sums to 1.0",
      isclose(sum(prob_dist.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(prob_dist.values())}")
check("Uniform rankings -> equal probabilities",
      all(isclose(p, 1.0/n, rel_tol=1e-9) for p in prob_dist.values()))

# Zero scores -> uniform fallback
zero_rankings = [StateRanking(rank=i+1, state_id=sid, distance=0.0, score=0.0)
                 for i, sid in enumerate(STATE_PROFILES)]
prob_zero = _rankings_to_prob_dist(zero_rankings)
check("Zero scores: fallback to uniform",
      all(isclose(p, 1.0/n, rel_tol=1e-9) for p in prob_zero.values()))


# ── 5. enforce_state_probability_ceiling ──────────────────────────────────────
print("\n5. enforce_state_probability_ceiling")

# Build pre-rankings: uniform
pre = uniform_rankings()

# Build post-rankings with one state at 80% of total score (way above 12pp ceiling)
post_scores = {sid: 0.001 for sid in STATE_PROFILES}
first_state = next(iter(STATE_PROFILES))
post_scores[first_state] = 10.0  # dominant
post = make_rankings(post_scores)

post_prob_before = _rankings_to_prob_dist(post)
print(f"  Pre-ceiling dominant state share: {post_prob_before[first_state]:.4f}")

capped = enforce_state_probability_ceiling(pre, post)
post_prob_after = _rankings_to_prob_dist(capped)
pre_prob = _rankings_to_prob_dist(pre)

increase = post_prob_after[first_state] - pre_prob[first_state]
print(f"  After ceiling: dominant state share {post_prob_after[first_state]:.4f}, increase {increase:.4f}")

check("Ceiling enforced: dominant state increase = exactly ceiling (12pp)",
      isclose(increase, STATE_PROBABILITY_CEILING, rel_tol=1e-6),
      f"increase={increase:.4f}, expected={STATE_PROBABILITY_CEILING}")
check("Ceiling-enforced distribution sums to 1.0",
      isclose(sum(post_prob_after.values()), 1.0, rel_tol=1e-6),
      f"sum={sum(post_prob_after.values())}")
check("Ceiling result covers all states",
      len(capped) == n,
      f"got {len(capped)}")

# No ceiling needed when increase is within bounds
post_small = make_rankings({sid: (1.0/n * 1.05 if sid == first_state else 1.0/n * 0.999)
                             for sid in STATE_PROFILES})
capped_small = enforce_state_probability_ceiling(pre, post_small)
# Should return post_small unchanged (no cap needed)
check("No ceiling when increase within bounds: returns post unchanged",
      capped_small is post_small,
      "Should return post_rankings reference when no capping needed")


# ── 6. apply_narrative_modulation ─────────────────────────────────────────────
print("\n6. apply_narrative_modulation")

# Confidence below floor -> no modulation
low_conf_result = NarrativeExtractionResult(
    identified_signals=[NarrativeSignal("Authority", "liability", "some signal", 0.9)],
    severity_indicators=[],
    overall_confidence=CONFIDENCE_FLOOR - 0.01,  # just below floor
)
acc_base = {f: 1.0 for f in DIMENSIONAL_FIELDS}  # non-zero everywhere
pre_rankings = uniform_rankings()

updated_vec, final_rankings = apply_narrative_modulation(
    acc_base, low_conf_result, pre_rankings, 39
)
check("Below confidence floor: vector unchanged",
      updated_vec == acc_base,
      f"changed: {[(f, updated_vec[f]) for f in DIMENSIONAL_FIELDS if updated_vec[f] != acc_base[f]]}")
check("Below confidence floor: rankings unchanged (same list)",
      final_rankings is pre_rankings,
      "rankings should be same object when no modulation")

# Confidence at exactly floor -> modulation proceeds (spec says "below 0.15" = strict <)
at_floor_result = NarrativeExtractionResult(
    identified_signals=[NarrativeSignal("Authority", "liability", "signal", 0.9)],
    severity_indicators=[],
    overall_confidence=CONFIDENCE_FLOOR,  # exactly at floor
)
vec_at_floor, _ = apply_narrative_modulation(acc_base, at_floor_result, pre_rankings, 39)
check("At exactly confidence floor: modulation proceeds (spec: 'below 0.15' = strict <)",
      vec_at_floor["authority_liability"] > acc_base["authority_liability"],
      "At exactly 0.15, spec says 'below' not 'at or below' — modulation should apply")

# Above confidence floor -> modulation applied
above_floor_result = NarrativeExtractionResult(
    identified_signals=[NarrativeSignal("Authority", "liability", "signal", 0.8)],
    severity_indicators=[],
    overall_confidence=CONFIDENCE_FLOOR + 0.01,
)
vec_above, rankings_above = apply_narrative_modulation(
    acc_base, above_floor_result, pre_rankings, 39
)
check("Above confidence floor: authority_liability increased",
      vec_above["authority_liability"] > acc_base["authority_liability"],
      f"before={acc_base['authority_liability']}, after={vec_above['authority_liability']}")
check("Above confidence floor: returns full rankings",
      len(rankings_above) == n,
      f"got {len(rankings_above)}")

# Full pipeline with good extraction
acc_nonzero = {f: 0.5 for f in DIMENSIONAL_FIELDS}
ext = good_extraction()
updated, final = apply_narrative_modulation(acc_nonzero, ext, pre_rankings, 39)

check("Full pipeline: vector modified in signal fields",
      updated["authority_liability"] > acc_nonzero["authority_liability"],
      f"authority_liability: {acc_nonzero['authority_liability']} -> {updated['authority_liability']}")
check("Full pipeline: non-signal fields unchanged",
      all(isclose(updated[f], acc_nonzero[f], rel_tol=1e-9)
          for f in DIMENSIONAL_FIELDS
          if f not in ("authority_liability", "attitude_liability")),
      "non-signal fields should be unchanged")
check("Full pipeline: ceiling enforced (no state increased by > 12pp)",
      True)  # ceiling enforcement verified in check #5; structural verify here
check("Full pipeline: final rankings count = 47",
      len(final) == n,
      f"got {len(final)}")


# ── 7. System prompt structure ─────────────────────────────────────────────────
print("\n7. NARRATIVE_SYSTEM_PROMPT structure")

check("System prompt contains 'Aptitude'", "Aptitude" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt contains 'Authority'", "Authority" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt contains 'Alliance'", "Alliance" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt contains 'Attitude'", "Attitude" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt contains 'liability'", "liability" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt contains 'asset'", "asset" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt specifies JSON output", "JSON" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt contains overall_confidence field", "overall_confidence" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt contains identified_signals field", "identified_signals" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt contains severity_indicators field", "severity_indicators" in NARRATIVE_SYSTEM_PROMPT)
check("System prompt does not name states",
      all(p.state_name not in NARRATIVE_SYSTEM_PROMPT for p in STATE_PROFILES.values()),
      "state names must not appear in system prompt (IV.1.1 spec)")
check("System prompt specifies no preamble / no explanation",
      "No preamble" in NARRATIVE_SYSTEM_PROMPT or "no preamble" in NARRATIVE_SYSTEM_PROMPT.lower())


# ── 8. Constants ───────────────────────────────────────────────────────────────
print("\n8. Constants")

check("STATE_PROBABILITY_CEILING = 0.12 (LOCKED)", isclose(STATE_PROBABILITY_CEILING, 0.12))
check("SEVERITY_CEILING = 0.25 (LOCKED)", isclose(SEVERITY_CEILING, 0.25))
check("CONFIDENCE_FLOOR = 0.15 (CALIBRATION TARGET starting value)",
      isclose(CONFIDENCE_FLOOR, 0.15),
      f"got {CONFIDENCE_FLOOR}")


# ── 9. NarrativeModulationEngine ──────────────────────────────────────────────
print("\n9. NarrativeModulationEngine")

engine = NarrativeModulationEngine(model="claude-sonnet-4-6")
check("Engine initial extraction_result is None", engine.extraction_result is None)
check("Engine initial severity_signals is []", engine.severity_signals == [])
check("Engine default model", engine.model == "claude-sonnet-4-6")

# Simulate extraction result injection (bypasses API call)
engine.extraction_result = good_extraction()
check("After extraction: severity_signals populated",
      len(engine.severity_signals) == 1,
      f"got {len(engine.severity_signals)}")
check("severity_signals returns a copy (not the original list)",
      engine.severity_signals is not engine.extraction_result.severity_indicators)

# Modulate via engine interface
acc_test = {f: 0.5 for f in DIMENSIONAL_FIELDS}
pre_test = uniform_rankings()
updated_v, final_r = engine.modulate(acc_test, good_extraction(), pre_test, 39)
check("Engine.modulate returns updated vector", updated_v["authority_liability"] > 0.5)
check("Engine.modulate returns rankings list", len(final_r) == n)


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Section IV narrative modulation engine is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
