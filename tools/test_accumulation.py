"""
PRV3 Accumulation Engine — Section II Integration Test

Verifies:
  1. Module imports cleanly
  2. Prior initialization produces normalized distribution
  3. Significant event multipliers (CALIBRATION TARGET / 1.0) produce uniform dist
  4. Baseline rank_states on zero accumulated vector: all states equidistant
  5. Synthetic answer contribution: single field increment, correct distance delta
  6. AccumulationEngine end-to-end with no answers: baseline distances
  7. Signal reliability coefficient: 1.2 role scales contribution correctly
"""

import sys
import math
from math import isclose
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.accumulation import (
    IntakeData, AccumulationEngine, AccumulationSession,
    initialize_priors, rank_states, accumulate_answer, _apply_signal_reliability,
    StateRanking, compute_cascade_risk, compute_liability_dispersion, MC_CENTROID_39,
)
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS, BASELINE_VALUE
from engine.data.questions import AnswerOption, QUESTION_LIBRARY

PASS = []
FAIL = []

def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Accumulation Engine — Section II Integration Test")
print("=" * 64)


# ── Shared test intake fixtures ────────────────────────────────────────────────

INTAKE_BASIC = IntakeData(
    headcount=152,
    industry="Technology",
    org_type="Privately held professional leadership",
    jurisdictions=["TX"],
    significant_events=["none"],
    principal_role="Other",
)

INTAKE_EVENT = IntakeData(
    headcount=45,
    industry="Technology",
    org_type="PE or VC-backed",
    jurisdictions=["CA"],
    significant_events=["acquisition_or_merger"],
    principal_role="C-suite",
)

INTAKE_HEADCOUNT_SMALL = IntakeData(
    headcount=4,
    industry="Professional Services",
    org_type="Founder-led",
    jurisdictions=["TX"],
    significant_events=["none"],
    principal_role="Owner or founder",
)


# ── 1. Baseline prior — equal probability ─────────────────────────────────────
print("\n1. Prior initialization — baseline (no events)")

priors_basic = initialize_priors(INTAKE_BASIC)
n = len(STATE_PROFILES)
expected = 1.0 / n

check("Prior dict covers all states", len(priors_basic) == n, f"got {len(priors_basic)}")
check("Prior sums to 1.0",
      isclose(sum(priors_basic.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(priors_basic.values())}")
check("None-event: uniform prior (all states equal)",
      all(isclose(v, expected, rel_tol=1e-9) for v in priors_basic.values()),
      f"non-uniform: sample={list(priors_basic.values())[:3]}")


# ── 2. Significant event — elevated states then normalized ─────────────────────
print("\n2. Prior initialization — significant event (acquisition_or_merger)")

priors_event = initialize_priors(INTAKE_EVENT)
# acquisition_or_merger elevates: the_second_close, identity_erosion, transition_paralysis
# multiplier is CALIBRATION_TARGET (None) → treated as 1.0 → distribution stays uniform
elevated_ids = ["the_second_close", "identity_erosion", "transition_paralysis"]

check("Event prior sums to 1.0",
      isclose(sum(priors_event.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(priors_event.values())}")

# With CALIBRATION_TARGET multiplier (1.0), distribution is still uniform
check("CALIBRATION_TARGET multiplier = 1.0 → uniform prior preserved",
      all(isclose(priors_event[sid], expected, rel_tol=1e-9)
          for sid in elevated_ids),
      f"non-uniform: {[(s, priors_event[s]) for s in elevated_ids]}")


# ── 3. Headcount < 25 — founders_grip elevated (CALIBRATION_TARGET = 1.0) ─────
print("\n3. Prior initialization — headcount Under 25")

priors_small = initialize_priors(INTAKE_HEADCOUNT_SMALL)
check("Headcount prior sums to 1.0",
      isclose(sum(priors_small.values()), 1.0, rel_tol=1e-9),
      f"sum={sum(priors_small.values())}")
check("Headcount CALIBRATION_TARGET (1.0) → founders_grip at baseline",
      isclose(priors_small["the_founders_grip"], expected, rel_tol=1e-9),
      f"founders_grip={priors_small['the_founders_grip']}, expected={expected}")


# ── 4. Baseline rank_states — zero accumulated vector ─────────────────────────
print("\n4. rank_states — zero accumulated vector (baseline)")

zero_vector = {f: 0.0 for f in DIMENSIONAL_FIELDS}
rankings = rank_states(zero_vector, 39)

# Under CDWCS, a zero session vector is displaced to -mu_N (negative centroid).
# Cosine similarity is defined and non-zero — scores reflect similarity between
# -mu_N and each displaced state profile vector.

check("Rankings cover all states", len(rankings) == n, f"got {len(rankings)}")
check("CDWCS: zero session vector produces finite scores for all states",
      all(not __import__("math").isnan(r.score) and not __import__("math").isinf(r.score)
          for r in rankings),
      f"NaN or Inf scores detected")
check("Ranks are 1..n",
      [r.rank for r in rankings] == list(range(1, n + 1)),
      f"ranks: {[r.rank for r in rankings[:5]]}")


# ── 5. Signal reliability coefficient — Owner 1.2x on authority_liability ──────
print("\n5. Signal reliability coefficient")

test_contributions = {f: 0.1 for f in DIMENSIONAL_FIELDS}
scaled = _apply_signal_reliability(test_contributions, "Owner or founder")

# Owner or founder: authority_liability = 1.2, alliance_liability/asset = 0.9,
# attitude_liability/asset = 0.9, aptitude = 1.0
check("Owner authority_liability scaled 1.2",
      isclose(scaled["authority_liability"], 0.1 * 1.2, rel_tol=1e-9),
      f"got {scaled['authority_liability']}")
check("Owner authority_asset scaled 1.2",
      isclose(scaled["authority_asset"], 0.1 * 1.2, rel_tol=1e-9),
      f"got {scaled['authority_asset']}")
check("Owner alliance_liability scaled 0.9",
      isclose(scaled["alliance_liability"], 0.1 * 0.9, rel_tol=1e-9),
      f"got {scaled['alliance_liability']}")
check("Owner aptitude_liability scaled 1.0",
      isclose(scaled["aptitude_liability"], 0.1 * 1.0, rel_tol=1e-9),
      f"got {scaled['aptitude_liability']}")

# Other role — neutral baseline, all 1.0
scaled_other = _apply_signal_reliability(test_contributions, "Other")
check("Other role: all contributions unchanged",
      all(isclose(scaled_other[f], 0.1, rel_tol=1e-9) for f in DIMENSIONAL_FIELDS),
      f"non-1.0 scaling: {[(f, scaled_other[f]) for f in DIMENSIONAL_FIELDS if not isclose(scaled_other[f], 0.1)]}")

# Unknown role → falls back to Other (neutral)
scaled_unknown = _apply_signal_reliability(test_contributions, "Unknown Role")
check("Unknown role falls back to Other (1.0 scaling)",
      all(isclose(scaled_unknown[f], 0.1, rel_tol=1e-9) for f in DIMENSIONAL_FIELDS),
      f"got: {scaled_unknown}")


# ── 6. accumulate_answer — single answer, Other role (no coefficient scaling) ──
print("\n6. accumulate_answer — synthetic answer")

engine = AccumulationEngine(INTAKE_BASIC)

# Confirm initial accumulated vector is all zeros
check("Initial accumulated_vector all zeros",
      all(engine.accumulated_vector[f] == 0.0 for f in DIMENSIONAL_FIELDS),
      f"non-zero: {[(f, engine.accumulated_vector[f]) for f in DIMENSIONAL_FIELDS if engine.accumulated_vector[f] != 0.0]}")

# Apply a synthetic answer with 0.3 on authority_liability only
synthetic = AnswerOption(
    option_id="TEST_A",
    option_text="Test option",
    dimensional_contributions={
        "aptitude_liability": 0.0,
        "aptitude_asset": 0.0,
        "authority_liability": 0.3,
        "authority_asset": 0.0,
        "alliance_liability": 0.0,
        "alliance_asset": 0.0,
        "attitude_liability": 0.0,
        "attitude_asset": 0.0,
    },
)

engine.apply_answer(synthetic, "Q01")

# Other role coefficient on authority_liability = 1.0 → no scaling
check("authority_liability accumulated to 0.3 (Other role, coefficient 1.0)",
      isclose(engine.accumulated_vector["authority_liability"], 0.3, rel_tol=1e-9),
      f"got {engine.accumulated_vector['authority_liability']}")
check("Other fields remain 0.0",
      all(engine.accumulated_vector[f] == 0.0
          for f in DIMENSIONAL_FIELDS if f != "authority_liability"),
      f"non-zero other fields: {[(f, engine.accumulated_vector[f]) for f in DIMENSIONAL_FIELDS if f != 'authority_liability' and engine.accumulated_vector[f] != 0.0]}")
check("Q01 recorded in answers_applied",
      "Q01" in engine.session.answers_applied,
      f"answers_applied: {engine.session.answers_applied}")


# ── 7. rank_states after single answer — distance delta for authority signal ───
print("\n7. rank_states after single answer")

rankings_after = engine.rank()
check("Rankings still cover all states", len(rankings_after) == n, f"got {len(rankings_after)}")

# CDWCS distances after authority_liability=0.3 (acc vector: auth=0.3, all others=0.0), N=1.
# Centroid is scaled to N=1: mu_N[f] = MC_CENTROID_39[f] * (1/39).
# Both session vector and profile vector are displaced by mu_N before cosine computation.
# NOTE: Absolute distance value is CENTROID_FIELD_SCALARS-dependent (harness-managed).
#       Only structural invariants are checked here:
#         (a) distance is finite and in valid cosine range [0, 2]
#         (b) relative ordering: authority signal ranks authority HIGH state closer than cluster state
# Authority HIGH state (the_founders_grip): SCD-WCS; original all-1.0 scalar reference = 0.638033.
cluster_r_after = next(r for r in rankings_after if r.state_id == "the_unformed_leader")
high_r_after    = next(r for r in rankings_after if r.state_id == "the_founders_grip")

check("SCD-WCS: cluster state distance is finite and within cosine range [0, 2]",
      (not __import__("math").isnan(cluster_r_after.distance)
       and not __import__("math").isinf(cluster_r_after.distance)
       and 0.0 <= cluster_r_after.distance <= 2.0),
      f"got={cluster_r_after.distance:.6f}")
check("Cosine sees directional alignment — authority signal in accumulated vector is closer to Authority HIGH state than to cluster state",
      high_r_after.distance < cluster_r_after.distance,
      f"high={high_r_after.distance:.6f}, cluster={cluster_r_after.distance:.6f}")

print(f"  Cosine distance to cluster state after authority signal: {cluster_r_after.distance:.6f}")
print(f"  Cosine distance to Authority HIGH state: {high_r_after.distance:.6f}")


# ── 8. AccumulationEngine with C-suite role — coefficient scaling confirmed ────
print("\n8. AccumulationEngine — C-suite role coefficient scaling")

engine_csuite = AccumulationEngine(INTAKE_EVENT)
engine_csuite.apply_answer(synthetic, "Q01")

# C-suite: authority_liability coefficient = 1.1
# So accumulated authority_liability should be 0.3 * 1.1 = 0.33
check("C-suite authority_liability scaled by 1.1",
      isclose(engine_csuite.accumulated_vector["authority_liability"], 0.3 * 1.1, rel_tol=1e-9),
      f"got {engine_csuite.accumulated_vector['authority_liability']}, expected {0.3 * 1.1}")


# ── 9. Q18-E conditional — non-hazard industry ────────────────────────────────
print("\n9. Q18-E conditional — non-hazard industry (Technology)")

INTAKE_Q18_LOW = IntakeData(
    headcount=152,
    industry="Technology",
    org_type="Privately held professional leadership",
    jurisdictions=["TX"],
    significant_events=["none"],
    principal_role="Other",
)

q18_opt_e = next(o for o in QUESTION_LIBRARY["Q18"].answer_options if o.option_id == "E")

engine_q18_low = AccumulationEngine(INTAKE_Q18_LOW)
engine_q18_low.apply_answer(q18_opt_e, "Q18")

# Non-hazard: condition_map[False] → attitude_asset 0.30, no 1.2x multiplier
check("Q18-E non-hazard: attitude_asset = 0.30",
      isclose(engine_q18_low.accumulated_vector["attitude_asset"], 0.30, rel_tol=1e-9),
      f"got {engine_q18_low.accumulated_vector['attitude_asset']}")
check("Q18-E non-hazard: attitude_liability = 0.00",
      engine_q18_low.accumulated_vector["attitude_liability"] == 0.0,
      f"got {engine_q18_low.accumulated_vector['attitude_liability']}")
check("Q18-E non-hazard: all other fields 0.00",
      all(engine_q18_low.accumulated_vector[f] == 0.0
          for f in DIMENSIONAL_FIELDS if f != "attitude_asset"),
      f"non-zero: {[(f, engine_q18_low.accumulated_vector[f]) for f in DIMENSIONAL_FIELDS if f != 'attitude_asset' and engine_q18_low.accumulated_vector[f] != 0.0]}")


# ── 10. Q18-E conditional — high-hazard industry ──────────────────────────────
print("\n10. Q18-E conditional — high-hazard industry (Manufacturing & Industrial)")

INTAKE_Q18_HIGH = IntakeData(
    headcount=152,
    industry="Manufacturing & Industrial",
    org_type="Privately held professional leadership",
    jurisdictions=["TX"],
    significant_events=["none"],
    principal_role="Other",
)

engine_q18_high = AccumulationEngine(INTAKE_Q18_HIGH)
engine_q18_high.apply_answer(q18_opt_e, "Q18")

# High-hazard: condition_map[True] → attitude_liability 0.60, then 1.2x → 0.72
check("Q18-E high-hazard: attitude_liability = 0.72 (0.60 × 1.2)",
      isclose(engine_q18_high.accumulated_vector["attitude_liability"], 0.72, rel_tol=1e-9),
      f"got {engine_q18_high.accumulated_vector['attitude_liability']}")
check("Q18-E high-hazard: attitude_asset = 0.00",
      engine_q18_high.accumulated_vector["attitude_asset"] == 0.0,
      f"got {engine_q18_high.accumulated_vector['attitude_asset']}")
check("Q18-E high-hazard: all other fields 0.00",
      all(engine_q18_high.accumulated_vector[f] == 0.0
          for f in DIMENSIONAL_FIELDS if f != "attitude_liability"),
      f"non-zero: {[(f, engine_q18_high.accumulated_vector[f]) for f in DIMENSIONAL_FIELDS if f != 'attitude_liability' and engine_q18_high.accumulated_vector[f] != 0.0]}")


# ── 11. compute_cascade_risk (Category A) ─────────────────────────────────────
print("\n11. compute_cascade_risk")

_ref_mag = math.sqrt(sum(v ** 2 for v in MC_CENTROID_39.values()))

check("all-zero vector: CR = 0.0 (no signal to disperse)",
      compute_cascade_risk({}) == 0.0,
      f"got {compute_cascade_risk({})}")

_v_concentrated = {"aptitude_liability": _ref_mag}
check("fully concentrated in one axis at reference magnitude: CR = 0.0",
      compute_cascade_risk(_v_concentrated) == 0.0,
      f"got {compute_cascade_risk(_v_concentrated)}")

_per_axis = _ref_mag / math.sqrt(4)
_v_even = {
    "aptitude_liability": _per_axis, "authority_liability": _per_axis,
    "alliance_liability": _per_axis, "attitude_liability": _per_axis,
}
check("evenly spread across all 4 axes at reference magnitude: CR = 1.0",
      isclose(compute_cascade_risk(_v_even), 1.0, rel_tol=1e-6),
      f"got {compute_cascade_risk(_v_even)}")

_v_even_low = {k: v / 10 for k, v in _v_even.items()}
check("evenly spread but low magnitude: CR = 0.1 (max dispersion, low intensity)",
      isclose(compute_cascade_risk(_v_even_low), 0.1, rel_tol=1e-6),
      f"got {compute_cascade_risk(_v_even_low)}")

_v_two_axes = {
    "aptitude_liability": _ref_mag / math.sqrt(2),
    "authority_liability": _ref_mag / math.sqrt(2),
}
check("spread across 2 of 4 axes at reference magnitude: CR = 0.5 (log2(2)/log2(4))",
      isclose(compute_cascade_risk(_v_two_axes), 0.5, rel_tol=1e-6),
      f"got {compute_cascade_risk(_v_two_axes)}")

_v_huge = {k: v * 10 for k, v in _v_even.items()}
check("intensity saturates at 1.0, never exceeds, even at 10x reference magnitude",
      compute_cascade_risk(_v_huge) == 1.0,
      f"got {compute_cascade_risk(_v_huge)}")

_v_negative = {"aptitude_liability": -5.0, "authority_liability": 3.0}
check("negative field clamped to 0 signal (not negative dispersion), no crash",
      compute_cascade_risk(_v_negative) == 0.0,
      f"got {compute_cascade_risk(_v_negative)}")

check("return value is never negative (no -0.0 sign artifact)",
      all(compute_cascade_risk(v) >= 0.0 for v in
          (_v_concentrated, _v_negative, {}, _v_even, _v_two_axes)),
      "found a negative CR value")

check("CR always in [0.0, 1.0]",
      all(0.0 <= compute_cascade_risk(v) <= 1.0 for v in
          (_v_concentrated, _v_even, _v_even_low, _v_two_axes, _v_huge, _v_negative, {})),
      "found a CR value outside [0, 1]")


# ── 12. compute_liability_dispersion (extracted for Category B reuse) ─────────
print("\n12. compute_liability_dispersion")

check("empty vector: dispersion = 0.0 (no signal to disperse)",
      compute_liability_dispersion({}) == 0.0,
      f"got {compute_liability_dispersion({})}")

check("fully concentrated in one axis: dispersion = 0.0, regardless of magnitude",
      compute_liability_dispersion(_v_concentrated) == 0.0,
      f"got {compute_liability_dispersion(_v_concentrated)}")

check("evenly spread across all 4 axes: dispersion = 1.0, regardless of magnitude",
      isclose(compute_liability_dispersion(_v_even), 1.0, rel_tol=1e-6),
      f"got {compute_liability_dispersion(_v_even)}")

check("evenly spread, low magnitude: dispersion still 1.0 (dispersion is magnitude-independent)",
      isclose(compute_liability_dispersion(_v_even_low), 1.0, rel_tol=1e-6),
      f"got {compute_liability_dispersion(_v_even_low)}")

check("spread across 2 of 4 axes: dispersion = 0.5 (log2(2)/log2(4))",
      isclose(compute_liability_dispersion(_v_two_axes), 0.5, rel_tol=1e-6),
      f"got {compute_liability_dispersion(_v_two_axes)}")

check("negative field clamped to 0 signal, no crash",
      compute_liability_dispersion(_v_negative) == 0.0,
      f"got {compute_liability_dispersion(_v_negative)}")

check("dispersion never negative (no -0.0 sign artifact)",
      all(compute_liability_dispersion(v) >= 0.0 for v in
          (_v_concentrated, _v_negative, {}, _v_even, _v_two_axes)),
      "found a negative dispersion value")

check("compute_cascade_risk(v) == round(compute_liability_dispersion(v) * intensity(v), 4) "
      "for all tested vectors -- refactor is behavior-preserving",
      all(
          isclose(
              compute_cascade_risk(v),
              max(0.0, round(
                  compute_liability_dispersion(v) *
                  min(
                      math.sqrt(sum(v.get(f, 0.0) ** 2 for f in DIMENSIONAL_FIELDS)) / _ref_mag,
                      1.0,
                  ),
                  4,
              )),
              abs_tol=1e-9,
          )
          for v in (_v_concentrated, _v_even, _v_even_low, _v_two_axes, _v_huge, _v_negative, {})
      ),
      "cascade_risk no longer matches dispersion * intensity for some tested vector")


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Section II accumulation engine is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
