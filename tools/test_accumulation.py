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
from math import sqrt, isclose
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.accumulation import (
    IntakeData, AccumulationEngine, AccumulationSession,
    initialize_priors, rank_states, accumulate_answer, _apply_signal_reliability,
    StateRanking,
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
    headcount="100-249",
    industry="Technology",
    org_type="Privately held professional leadership",
    jurisdictions=["TX"],
    significant_events=["none"],
    principal_role="Other",
)

INTAKE_EVENT = IntakeData(
    headcount="25-99",
    industry="Technology",
    org_type="PE or VC-backed",
    jurisdictions=["CA"],
    significant_events=["acquisition_or_merger"],
    principal_role="C-suite",
)

INTAKE_HEADCOUNT_SMALL = IntakeData(
    headcount="Under 25",
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
rankings = rank_states(zero_vector)

# After seeding (Session 12): 32 states have differentiated primary liability fields.
# Cluster/low states (15) remain at all-0.25 — distance from zero = sqrt(8 * 0.25^2)
# HIGH states (11) have one liability field at 0.60 — distance from zero > sqrt(0.5)
# Distances are no longer equal by design.
cluster_dist    = sqrt(8 * BASELINE_VALUE ** 2)
cluster_ranking = next(r for r in rankings if r.state_id == "the_unformed_leader")
high_ranking    = next(r for r in rankings if r.state_id == "the_founders_grip")

check("Rankings cover all states", len(rankings) == n, f"got {len(rankings)}")
check("Cluster state at uniform baseline distance",
      isclose(cluster_ranking.distance, cluster_dist, rel_tol=1e-9),
      f"expected={cluster_dist:.6f}, got={cluster_ranking.distance:.6f}")
check("HIGH state further from zero than cluster state (seeded profiles)",
      high_ranking.distance > cluster_ranking.distance,
      f"high={high_ranking.distance:.6f}, cluster={cluster_ranking.distance:.6f}")
check("Ranks are 1..n",
      [r.rank for r in rankings] == list(range(1, n + 1)),
      f"ranks: {[r.rank for r in rankings[:5]]}")

print(f"  Cluster state baseline distance: {cluster_dist:.6f}")
print(f"  HIGH state (founders_grip) distance: {high_ranking.distance:.6f}")


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

# After seeding: states have differentiated profiles — distances are no longer equal.
# Cluster state (the_unformed_leader, all 0.25):
#   d = sqrt((0.3-0.25)^2 + 7*(0.0-0.25)^2) = sqrt(0.44)
# Authority HIGH state (the_founders_grip, authority_liability=0.60):
#   d = sqrt((0.3-0.60)^2 + 7*(0.0-0.25)^2) > sqrt(0.44) — acc=0.3 undershoots profile=0.60
cluster_d_after = sqrt((0.3 - BASELINE_VALUE)**2 + 7 * (0.0 - BASELINE_VALUE)**2)
cluster_r_after = next(r for r in rankings_after if r.state_id == "the_unformed_leader")
high_r_after    = next(r for r in rankings_after if r.state_id == "the_founders_grip")

check("Cluster state has expected distance after authority signal",
      isclose(cluster_r_after.distance, cluster_d_after, rel_tol=1e-9),
      f"expected={cluster_d_after:.6f}, got={cluster_r_after.distance:.6f}")
check("Authority HIGH state further from acc vector than cluster (acc=0.3 < profile=0.60)",
      high_r_after.distance > cluster_r_after.distance,
      f"high={high_r_after.distance:.6f}, cluster={cluster_r_after.distance:.6f}")

print(f"  Distance after authority_liability=0.3: {cluster_d_after:.6f}")


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
    headcount="100-249",
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
    headcount="100-249",
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
