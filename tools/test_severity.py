"""
PRV3 Severity Engine — Section V Integration Test

Verifies:
  1. Duration weights: LOCKED values 1.0 / 1.5 / 2.0
  2. compute_raw_severity: multiplicative formula, additive inputs
  3. compute_raw_severity: None duration/population defaults to 1.0
  4. compute_raw_severity: narrative contribution included
  5. normalize_severity: clips to 0-100, uses normalization factor
  6. classify_severity: tier mapping with default thresholds
  7. classify_severity: Endemic is the cap
  8. apply_narrative_severity_ceiling: 25-point cap LOCKED
  9. SeverityEngine: end-to-end with multiple inputs
 10. SeverityEngine: narrative ceiling applied flag
 11. SeverityEngine: zero inputs produces score 0
 12. Severity tier descriptions: all three present and non-empty
 13. Constants: correct LOCKED values
"""

import sys
from math import isclose
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.severity import (
    DURATION_WEIGHTS, POPULATION_WEIGHTS, NARRATIVE_SEVERITY_CEILING_POINTS,
    SEVERITY_TIER_DESCRIPTIONS, SEVERITY_TIERS,
    SeverityInput, SeverityAccumulator, SeverityResult,
    compute_raw_severity, normalize_severity, classify_severity,
    apply_narrative_severity_ceiling, SeverityEngine,
    compute_state_severity, SEVERITY_ID_INTENDED_STATES, SEVERITY_ID_OPTION_STATES,
    _NORMALIZATION_DEFAULT, _EMERGING_MAX_DEFAULT, _ENTRENCHED_MAX_DEFAULT,
)

PASS = []
FAIL = []

def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Severity Engine — Section V Integration Test")
print("=" * 64)


# ── 1. Duration weights ────────────────────────────────────────────────────────
print("\n1. Duration weights (LOCKED)")

check("0_6mo weight = 1.0", isclose(DURATION_WEIGHTS["0_6mo"], 1.0))
check("6_18mo weight = 1.5", isclose(DURATION_WEIGHTS["6_18mo"], 1.5))
check("18mo_plus weight = 2.0", isclose(DURATION_WEIGHTS["18mo_plus"], 2.0))
check("All three duration bands present", len(DURATION_WEIGHTS) == 3)


# ── 2. compute_raw_severity — multiplicative formula ──────────────────────────
print("\n2. compute_raw_severity — multiplicative formula")

# Single input, duration only (population=None → 1.0, additive weights=None → 0.0)
single_short = SeverityAccumulator(inputs=[
    SeverityInput("Q05", "SEVER-01", duration_band="0_6mo")
])
raw_short = compute_raw_severity(single_short)
# duration_w=1.0, population_w=1.0(fallback), base=1.0 → 1.0 * 1.0 * 1.0 = 1.0
check("Single short-duration input: raw = 1.0",
      isclose(raw_short, 1.0),
      f"got {raw_short}")

single_long = SeverityAccumulator(inputs=[
    SeverityInput("Q05", "SEVER-01", duration_band="18mo_plus")
])
raw_long = compute_raw_severity(single_long)
# duration_w=2.0, population_w=1.0, base=1.0 → 2.0
check("Single long-duration input: raw = 2.0",
      isclose(raw_long, 2.0),
      f"got {raw_long}")

single_mid = SeverityAccumulator(inputs=[
    SeverityInput("Q10", "SEVER-03", duration_band="6_18mo")
])
raw_mid = compute_raw_severity(single_mid)
check("Single mid-duration input: raw = 1.5",
      isclose(raw_mid, 1.5),
      f"got {raw_mid}")


# ── 3. compute_raw_severity — None defaults ────────────────────────────────────
print("\n3. compute_raw_severity — None duration/population defaults")

none_input = SeverityAccumulator(inputs=[
    SeverityInput("Q05", "SEVER-01",
                  duration_band=None, population_band=None)
])
raw_none = compute_raw_severity(none_input)
# Both None → 1.0 * 1.0 * 1.0 = 1.0
check("None duration + None population: raw = 1.0",
      isclose(raw_none, 1.0),
      f"got {raw_none}")


# ── 4. compute_raw_severity — additive inputs ──────────────────────────────────
print("\n4. compute_raw_severity — additive inputs (CALIBRATION TARGET = 0.0)")

# With additive inputs True but weights = None (fallback 0.0)
with_additive = SeverityAccumulator(inputs=[
    SeverityInput("Q05", "SEVER-01",
                  duration_band="6_18mo",
                  prior_failed_resolution=True,
                  financial_indicators=True,
                  named_condition=True)
])
raw_additive = compute_raw_severity(with_additive)
# duration_w=1.5, pop_w=1.0(fallback), additive=0.0 (calibration targets)
# → 1.5 + 0 = 1.5
check("Additive inputs True but CALIBRATION_TARGET weights = 0.0",
      isclose(raw_additive, 1.5),
      f"got {raw_additive}")

# Multiple inputs accumulate
two_inputs = SeverityAccumulator(inputs=[
    SeverityInput("Q05", "SEVER-01", duration_band="0_6mo"),
    SeverityInput("Q15", "SEVER-05", duration_band="18mo_plus"),
])
raw_two = compute_raw_severity(two_inputs)
# 1.0 + 2.0 = 3.0
check("Two inputs accumulate: 1.0 + 2.0 = 3.0",
      isclose(raw_two, 3.0),
      f"got {raw_two}")


# ── 5. compute_raw_severity — narrative contribution ──────────────────────────
print("\n5. compute_raw_severity — narrative contribution added")

with_narrative = SeverityAccumulator(
    inputs=[SeverityInput("Q05", "SEVER-01", duration_band="0_6mo")],
    narrative_severity_addition=0.5,
)
raw_narr = compute_raw_severity(with_narrative)
# 1.0 (from input) + 0.5 (narrative) = 1.5
check("Narrative contribution added to raw score",
      isclose(raw_narr, 1.5),
      f"got {raw_narr}")

# Zero inputs, only narrative
narrative_only = SeverityAccumulator(
    inputs=[],
    narrative_severity_addition=1.0,
)
raw_narr_only = compute_raw_severity(narrative_only)
check("Narrative-only: raw = narrative_addition",
      isclose(raw_narr_only, 1.0),
      f"got {raw_narr_only}")


# ── 6. normalize_severity ─────────────────────────────────────────────────────
print("\n6. normalize_severity")

# Default normalization: raw / 6.0 * 100
norm_default = normalize_severity(3.0)
expected_norm = (3.0 / _NORMALIZATION_DEFAULT) * 100.0
check("normalize_severity(3.0) uses default normalization",
      isclose(norm_default, expected_norm),
      f"got {norm_default}, expected {expected_norm}")

# Floor: 0.0
check("normalize_severity(0.0) = 0.0",
      isclose(normalize_severity(0.0), 0.0))

# Ceiling: clips to 100.0
check("normalize_severity(very_large) clips to 100.0",
      isclose(normalize_severity(1000.0), 100.0))

# Negative clips to 0.0
check("normalize_severity(-1.0) clips to 0.0",
      isclose(normalize_severity(-1.0), 0.0))

print(f"  normalize_severity(3.0) = {norm_default:.2f} (default norm factor {_NORMALIZATION_DEFAULT})")


# ── 7. classify_severity — tier mapping ───────────────────────────────────────
print("\n7. classify_severity — tier mapping with default thresholds")

emerging_threshold = _EMERGING_MAX_DEFAULT * 100.0     # 33.0
entrenched_threshold = _ENTRENCHED_MAX_DEFAULT * 100.0  # 66.0

check("Score 0.0 -> Emerging", classify_severity(0.0) == "Emerging")
check("Score at emerging threshold - epsilon -> Emerging",
      classify_severity(emerging_threshold - 0.001) == "Emerging")
check("Score at emerging threshold -> Entrenched",
      classify_severity(emerging_threshold) == "Entrenched")
check("Score between thresholds -> Entrenched",
      classify_severity(50.0) == "Entrenched")
check("Score at entrenched threshold -> Endemic",
      classify_severity(entrenched_threshold) == "Endemic")
check("Score 100.0 -> Endemic (cap)",
      classify_severity(100.0) == "Endemic")

print(f"  Emerging: 0.0–{emerging_threshold:.1f} | "
      f"Entrenched: {emerging_threshold:.1f}–{entrenched_threshold:.1f} | "
      f"Endemic: {entrenched_threshold:.1f}–100.0")


# ── 8. classify_severity — Endemic is the cap ─────────────────────────────────
print("\n8. classify_severity — Endemic is the ceiling (no tier beyond Endemic)")

check("Score 99.9 -> Endemic (not beyond)", classify_severity(99.9) == "Endemic")
check("Score 100.0 -> Endemic (hard ceiling)", classify_severity(100.0) == "Endemic")
check("All valid tiers are in SEVERITY_TIERS",
      all(classify_severity(s) in SEVERITY_TIERS for s in [0.0, 33.0, 66.0, 100.0]))


# ── 9. apply_narrative_severity_ceiling ───────────────────────────────────────
print("\n9. apply_narrative_severity_ceiling (25-point cap, LOCKED)")

# Below ceiling
result_below = apply_narrative_severity_ceiling(
    pre_narrative_score=40.0,
    narrative_addition=10.0,
)
check("Narrative addition below 25: not capped",
      isclose(result_below, 50.0),
      f"got {result_below}")

# Exactly at ceiling
result_at = apply_narrative_severity_ceiling(50.0, 25.0)
check("Narrative addition = 25 (at ceiling): not capped",
      isclose(result_at, 75.0),
      f"got {result_at}")

# Above ceiling: capped at 25
result_capped = apply_narrative_severity_ceiling(50.0, 40.0)
check("Narrative addition 40 > 25: capped to 25",
      isclose(result_capped, 75.0),
      f"got {result_capped}")

# Would push past 100.0: clipped
result_clipped = apply_narrative_severity_ceiling(85.0, 30.0)
check("Result clipped to 100.0 even with ceiling applied",
      isclose(result_clipped, 100.0),
      f"got {result_clipped}")

check("NARRATIVE_SEVERITY_CEILING_POINTS = 25.0",
      isclose(NARRATIVE_SEVERITY_CEILING_POINTS, 25.0))


# ── 10. SeverityEngine — end-to-end ────────────────────────────────────────────
print("\n10. SeverityEngine — end-to-end")

eng = SeverityEngine()
check("Fresh engine: zero inputs", len(eng.accumulator.inputs) == 0)

eng.add_input(SeverityInput("Q05", "SEVER-01", duration_band="18mo_plus"))
eng.add_input(SeverityInput("Q15", "SEVER-05", duration_band="6_18mo"))
result = eng.score()

check("SeverityResult has all fields",
      hasattr(result, "raw_score") and
      hasattr(result, "score_0_100") and
      hasattr(result, "score_0_100_with_narrative") and
      hasattr(result, "tier") and
      hasattr(result, "tier_description") and
      hasattr(result, "narrative_contribution_0_100") and
      hasattr(result, "narrative_ceiling_applied") and
      hasattr(result, "input_count"))

check("input_count = 2", result.input_count == 2, f"got {result.input_count}")
check("raw_score = 3.5 (2.0 + 1.5)",
      isclose(result.raw_score, 3.5),
      f"got {result.raw_score}")
check("tier is a valid tier", result.tier in SEVERITY_TIERS,
      f"got {result.tier!r}")
check("tier_description non-empty", len(result.tier_description) > 0)
check("narrative_contribution_0_100 = 0.0 (no narrative set)",
      isclose(result.narrative_contribution_0_100, 0.0),
      f"got {result.narrative_contribution_0_100}")
check("narrative_ceiling_applied = False (no narrative)",
      result.narrative_ceiling_applied is False)
check("score_0_100 = score_0_100_with_narrative (no narrative)",
      isclose(result.score_0_100, result.score_0_100_with_narrative),
      f"{result.score_0_100} vs {result.score_0_100_with_narrative}")

print(f"  Two inputs (18mo+ and 6-18mo): raw={result.raw_score}, "
      f"score={result.score_0_100:.1f}/100, tier={result.tier}")


# ── 11. SeverityEngine — narrative ceiling applied ────────────────────────────
print("\n11. SeverityEngine — narrative ceiling applied flag")

eng_narr = SeverityEngine()
eng_narr.add_input(SeverityInput("Q05", "SEVER-01", duration_band="0_6mo"))
eng_narr.set_narrative_contribution(100.0)  # raw addition; normalizes >> 25 pts
result_narr = eng_narr.score()

check("Large narrative contribution: ceiling_applied = True",
      result_narr.narrative_ceiling_applied is True,
      f"narrative_0_100={result_narr.narrative_contribution_0_100:.1f}")
# Ceiling caps narrative addition at 25 pts; final = pre_score + 25
expected_narr_final = result_narr.score_0_100 + NARRATIVE_SEVERITY_CEILING_POINTS
check("Final score = pre_score + 25 (ceiling applied, narrative capped at 25pt)",
      isclose(result_narr.score_0_100_with_narrative, min(expected_narr_final, 100.0)),
      f"got {result_narr.score_0_100_with_narrative}, expected {expected_narr_final}")

# Small narrative contribution (below 25 points on 0-100 scale)
eng_small = SeverityEngine()
eng_small.add_input(SeverityInput("Q05", "SEVER-01", duration_band="0_6mo"))
# To produce < 25 points on 0-100 scale: raw_narr < 25/100 * normalization
# With default norm=6.0: raw < 1.5 → use 0.5
eng_small.set_narrative_contribution(0.5)
result_small = eng_small.score()

check("Small narrative contribution: ceiling_applied = False",
      result_small.narrative_ceiling_applied is False,
      f"narrative_0_100={result_small.narrative_contribution_0_100:.1f}")


# ── 12. SeverityEngine — zero inputs ──────────────────────────────────────────
print("\n12. SeverityEngine — zero inputs")

eng_zero = SeverityEngine()
result_zero = eng_zero.score()

check("Zero inputs: raw_score = 0.0",
      isclose(result_zero.raw_score, 0.0),
      f"got {result_zero.raw_score}")
check("Zero inputs: score_0_100 = 0.0",
      isclose(result_zero.score_0_100, 0.0),
      f"got {result_zero.score_0_100}")
check("Zero inputs: tier = Emerging",
      result_zero.tier == "Emerging",
      f"got {result_zero.tier!r}")
check("Zero inputs: input_count = 0",
      result_zero.input_count == 0)


# ── 13. Severity tier descriptions ────────────────────────────────────────────
print("\n13. Severity tier behavioral anchors (LOCKED copy)")

check("Emerging description present", len(SEVERITY_TIER_DESCRIPTIONS.get("Emerging", "")) > 0)
check("Entrenched description present", len(SEVERITY_TIER_DESCRIPTIONS.get("Entrenched", "")) > 0)
check("Endemic description present", len(SEVERITY_TIER_DESCRIPTIONS.get("Endemic", "")) > 0)
check("Emerging contains 'easiest moment'", "easiest moment" in SEVERITY_TIER_DESCRIPTIONS["Emerging"])
check("Entrenched contains 'Workarounds'", "Workarounds" in SEVERITY_TIER_DESCRIPTIONS["Entrenched"])
check("Endemic contains 'operating environment'", "operating environment" in SEVERITY_TIER_DESCRIPTIONS["Endemic"])
check("All three tiers in SEVERITY_TIERS", set(SEVERITY_TIERS) == {"Emerging", "Entrenched", "Endemic"})


# ── 14. Constants ──────────────────────────────────────────────────────────────
print("\n14. Constants")

check("NARRATIVE_SEVERITY_CEILING_POINTS = 25.0 (LOCKED)",
      isclose(NARRATIVE_SEVERITY_CEILING_POINTS, 25.0))
check("Population weights all CALIBRATION_TARGET (None)",
      all(v is None for v in POPULATION_WEIGHTS.values()))
check("Duration weights dict has exactly 3 entries", len(DURATION_WEIGHTS) == 3)


# ── 15. compute_state_severity — per-state attribution (Checkpoint 1) ────────
# Updated this session (Checkpoint 1 follow-on): state_severity's values are
# now StateSeverity objects (tier + score_0_100), not bare tier strings --
# every check below reads .tier explicitly and new checks verify score_0_100
# is present, a real float, and matches the real normalize_severity(raw) math.
print("\n15. compute_state_severity — per-state attribution")

check("Locked flat mapping covers exactly 17 SEVER-IDs",
      len(SEVERITY_ID_INTENDED_STATES) == 17,
      f"got {len(SEVERITY_ID_INTENDED_STATES)}")
check("Split-by-option mapping covers exactly 2 IDs x 3 options = 6 entries",
      len(SEVERITY_ID_OPTION_STATES) == 6,
      f"got {len(SEVERITY_ID_OPTION_STATES)}")
check("Combined locked SEVER-ID count = 19 (17 flat + 2 split), matches Section 9",
      len(SEVERITY_ID_INTENDED_STATES) + 2 == 19)

# Single input, single-state mapping (SEVER-15 -> the_exposed only)
single_state_acc = SeverityAccumulator(inputs=[
    SeverityInput("Q02", "SEVER-15", duration_band="0_6mo")
])
single_state_result = compute_state_severity(single_state_acc)
check("Single-state mapping: state_severity has exactly the_exposed",
      set(single_state_result.keys()) == {"the_exposed"},
      f"got {single_state_result}")
check("Single-state mapping: value is a StateSeverity with a real tier and score",
      single_state_result["the_exposed"].tier in SEVERITY_TIERS
      and isinstance(single_state_result["the_exposed"].score_0_100, float),
      f"got {single_state_result['the_exposed']}")
# duration_band="0_6mo" alone -> raw=1.0 (dur_w=1.0, pop_w=1.0 fallback) --
# same math as compute_raw_severity()'s own Section 2 checks above.
expected_single_score = normalize_severity(1.0)
check("Single-state mapping: score_0_100 matches the real normalize_severity(raw) math",
      isclose(single_state_result["the_exposed"].score_0_100, expected_single_score),
      f"got {single_state_result['the_exposed'].score_0_100}, expected {expected_single_score}")

# One input mapped to multiple states (SEVER-02 -> built_to_fail, the_undefined_role)
# -- both should carry the identical tier AND score, since the same input feeds
# both groups (StateSeverity's dataclass equality checks both fields at once).
multi_state_acc = SeverityAccumulator(inputs=[
    SeverityInput("Q05", "SEVER-02", duration_band="18mo_plus")
])
multi_state_result = compute_state_severity(multi_state_acc)
check("Multi-state mapping: both built_to_fail and the_undefined_role present",
      set(multi_state_result.keys()) == {"built_to_fail", "the_undefined_role"},
      f"got {multi_state_result}")
check("Multi-state mapping: both states carry the same tier and score_0_100",
      multi_state_result["built_to_fail"] == multi_state_result["the_undefined_role"],
      f"got {multi_state_result}")
check("Multi-state mapping: score_0_100 is a real float, not a placeholder",
      isinstance(multi_state_result["built_to_fail"].score_0_100, float)
      and multi_state_result["built_to_fail"].score_0_100 > 0.0,
      f"got {multi_state_result['built_to_fail'].score_0_100}")

# Split-by-option: SEVER-03 option C -> decision_paralysis, option E -> the_lost_map
split_acc = SeverityAccumulator(inputs=[
    SeverityInput("Q21", "SEVER-03", triggering_option_id="C", duration_band="0_6mo"),
    SeverityInput("Q21", "SEVER-03", triggering_option_id="E", duration_band="0_6mo"),
])
split_result = compute_state_severity(split_acc)
check("Split-by-option: option C and option E route to different states",
      set(split_result.keys()) == {"decision_paralysis", "the_lost_map"},
      f"got {split_result}")
check("Split-by-option: each state's own StateSeverity carries a real tier",
      split_result["decision_paralysis"].tier in SEVERITY_TIERS
      and split_result["the_lost_map"].tier in SEVERITY_TIERS,
      f"got {split_result}")

# Unmapped ID: still contributes to the pooled score (backward compat) but
# attributes to no state -- absent from state_severity entirely, not defaulted
# to Emerging here (that fallback is a downstream caller's responsibility).
unmapped_acc = SeverityAccumulator(inputs=[
    SeverityInput("Q99", "SEVER-99", duration_band="18mo_plus")
])
check("Unmapped SEVER-ID still contributes to pooled raw score",
      isclose(compute_raw_severity(unmapped_acc), 2.0),
      f"got {compute_raw_severity(unmapped_acc)}")
check("Unmapped SEVER-ID: state_severity is empty (no attribution, no state key)",
      compute_state_severity(unmapped_acc) == {},
      f"got {compute_state_severity(unmapped_acc)}")

# SeverityEngine.score() populates state_severity alongside unchanged session fields
eng_state = SeverityEngine()
eng_state.add_input(SeverityInput("Q02", "SEVER-15", duration_band="18mo_plus"))
result_state = eng_state.score()
check("SeverityResult.state_severity[id].tier matches the session tier "
      "(single input, no divergence possible)",
      result_state.state_severity["the_exposed"].tier == result_state.tier,
      f"got {result_state.state_severity['the_exposed'].tier}, session tier={result_state.tier}")
check("SeverityResult.state_severity[id].score_0_100 matches the session's own "
      "score_0_100 (single input, no divergence possible)",
      isclose(result_state.state_severity["the_exposed"].score_0_100, result_state.score_0_100),
      f"got {result_state.state_severity['the_exposed'].score_0_100}, "
      f"session score_0_100={result_state.score_0_100}")
check("SeverityResult still exposes all session-wide fields unchanged (backward compat)",
      hasattr(result_state, "raw_score") and hasattr(result_state, "tier"),
      "session-wide fields missing")

# Zero inputs: state_severity is empty, session-wide fields unaffected
eng_state_zero = SeverityEngine()
result_state_zero = eng_state_zero.score()
check("Zero inputs: state_severity is empty dict",
      result_state_zero.state_severity == {},
      f"got {result_state_zero.state_severity}")


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Section V severity engine is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
