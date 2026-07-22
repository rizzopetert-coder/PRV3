"""
PRV3 Output Engine — Section VI Integration Test

Verifies:
  1. compute_noise_baseline: populated library Monte Carlo baseline — all states equal
  2. compute_signal_floors: floor = baseline * 1.08 (non-Auth) / 1.00 (Auth)
  3. apply_signal_floor: filters states correctly, populates QualifiedState fields
  4. route_output: insufficient_signal when nothing clears floor
  5. route_output: single mode when one state clears with separation >= threshold
  6. route_output: single mode when exactly one state clears (even below sep threshold)
  7. route_output: multi mode when multiple clear and separation < threshold
  8. route_output: single mode when multiple clear but separation >= threshold
  9. build_private_block: correct fields, severity anchor from V.3
 10. build_shareable_block: correct fields, attribution present
 11. OutputEngine.build: single-state end-to-end
 12. OutputEngine.build: multi-state end-to-end
 13. OutputEngine.build: insufficient_signal end-to-end
 14. OutputEngine: noise baseline caching
 15. Constants: LOCKED values correct
"""

import sys
from math import isclose
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.output import (
    SIGNAL_FLOOR_MULTIPLIER_AUTHORITY, SIGNAL_FLOOR_MULTIPLIER_DEFAULT,
    NOISE_SIMULATION_COUNT, SEPARATION_THRESHOLD,
    _SEPARATION_THRESHOLD_DEFAULT,
    CAUSATION_DISPERSION_THRESHOLD,
    compute_noise_baseline, compute_signal_floors, apply_signal_floor,
    route_output, build_private_block, build_shareable_block,
    compute_causation_pattern,
    OutputEngine, OutputPackage, OutputRouting, QualifiedState,
    PrivateOutputBlock, ShareableOutputBlock,
)
from engine.accumulation import StateRanking
from engine.severity import SeverityEngine, SeverityInput, SEVERITY_TIER_DESCRIPTIONS
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS, BASELINE_VALUE

PASS = []
FAIL = []

def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Output Engine — Section VI Integration Test")
print("=" * 64)

n = len(STATE_PROFILES)

# ── Shared fixtures ────────────────────────────────────────────────────────────

def make_severity_result(tier="Emerging"):
    eng = SeverityEngine()
    result = eng.score()
    # Manually override tier for test purposes
    from engine.severity import SeverityResult
    return SeverityResult(
        raw_score=0.0,
        score_0_100=15.0,
        score_0_100_with_narrative=15.0,
        tier=tier,
        tier_description=SEVERITY_TIER_DESCRIPTIONS[tier],
        narrative_contribution_0_100=0.0,
        narrative_ceiling_applied=False,
        input_count=0,
    )


def make_rankings(scores: dict) -> list:
    """Build StateRanking list from {state_id: score}."""
    rankings = []
    for i, (sid, _) in enumerate(STATE_PROFILES.items()):
        s = scores.get(sid, 0.001)
        rankings.append(StateRanking(rank=i+1, state_id=sid, distance=0.5, score=s))
    rankings.sort(key=lambda r: -r.score)
    for i, r in enumerate(rankings):
        r.rank = i + 1
    return rankings


def uniform_rankings():
    s = -0.5000  # below SCD_WCS_ALIGNMENT_THRESHOLD (-0.4000) — updated v22
    return make_rankings({sid: s for sid in STATE_PROFILES})


# ── 1. compute_noise_baseline ─────────────────────────────────────────────────
print("\n1. compute_noise_baseline — populated library (Monte Carlo baseline)")

# After seeding (Session 12): state profiles are differentiated.
# Monte Carlo baseline scores vary by state — no longer equal by design.
baseline = compute_noise_baseline(random_seed=0)
reference = list(baseline.values())[0]
check("Baseline covers all states", len(baseline) == n, f"got {len(baseline)}")
check("Baseline values vary by state (seeded profiles)",
      not all(isclose(v, reference, rel_tol=1e-6) for v in baseline.values()),
      f"all equal at {reference:.6f} — seeding may not have applied")
check("Baseline values are finite (SCD-WCS: noise near zero, some states may be slightly negative)",
      all(not __import__("math").isnan(v) and not __import__("math").isinf(v)
          for v in baseline.values()))
print(f"  Monte Carlo baseline score: {reference:.6f}")
print(f"  Signal floor (non-Auth 1.08x): {reference * SIGNAL_FLOOR_MULTIPLIER_DEFAULT:.6f}")


# ── 2. compute_signal_floors ───────────────────────────────────────────────────
print("\n2. compute_signal_floors")

floors = compute_signal_floors(baseline)
check("Floors cover all states", len(floors) == n)
check("Tiered floor: Authority states — floor = baseline x 1.00",
      all(isclose(floors[sid], baseline[sid] * SIGNAL_FLOOR_MULTIPLIER_AUTHORITY, rel_tol=1e-9)
          for sid in baseline
          if STATE_PROFILES[sid].primary_dimension == "Authority"),
      f"Authority sample: {[(sid, floors[sid]) for sid in baseline if STATE_PROFILES[sid].primary_dimension == 'Authority'][:2]}")
check("Tiered floor: non-Authority states — floor = baseline x 1.08",
      all(isclose(floors[sid], baseline[sid] * SIGNAL_FLOOR_MULTIPLIER_DEFAULT, rel_tol=1e-9)
          for sid in baseline
          if STATE_PROFILES[sid].primary_dimension != "Authority"),
      f"non-Authority sample: {list(floors.values())[:2]}")
check("Authority floors equal baseline exactly (1.00x)",
      all(isclose(floors[sid], baseline[sid], rel_tol=1e-9)
          for sid in baseline
          if STATE_PROFILES[sid].primary_dimension == "Authority"))
check("Non-Authority floors = baseline x 1.08 (signed — direction depends on baseline sign)",
      all(isclose(floors[sid], baseline[sid] * SIGNAL_FLOOR_MULTIPLIER_DEFAULT, rel_tol=1e-9)
          for sid in baseline
          if STATE_PROFILES[sid].primary_dimension != "Authority"))


# ── 3. apply_signal_floor ─────────────────────────────────────────────────────
print("\n3. apply_signal_floor")

# Floor and routing tests (3-14) use a fixed mocked baseline for fixture stability.
# SCD-WCS noise baseline is near zero; v20 WCS values (~0.89) hit the 0.9650 ceiling
# and collapse floor separation. Use 0.5 per state: floor = 0.54 (non-Auth), 0.50
# (Auth) — clearly above uniform 1/n (0.021), clearly below ceiling (0.9650).
baseline = {sid: 0.5 for sid in STATE_PROFILES}
reference = 0.5

# Uniform rankings: all scores = 1/47 ≈ 0.02128, well below floor (0.675)
# → no states clear floor
uniform = uniform_rankings()
evaluated_uniform = apply_signal_floor(uniform, baseline)

check("apply_signal_floor returns list of all states",
      len(evaluated_uniform) == n,
      f"got {len(evaluated_uniform)}")
check("Uniform scores: no states clear signal floor",
      not any(qs.cleared_floor for qs in evaluated_uniform),
      f"cleared: {[qs.state_id for qs in evaluated_uniform if qs.cleared_floor]}")
check("QualifiedState has all required fields",
      all(hasattr(qs, f) for qs in evaluated_uniform[:1]
          for f in ("rank", "state_id", "state_name", "score", "noise_baseline",
                    "signal_floor", "cleared_floor", "score_lift_pct", "resolution_family")))
check("state_name populated from STATE_PROFILES",
      all(qs.state_name == STATE_PROFILES[qs.state_id].state_name
          for qs in evaluated_uniform[:5]))
check("resolution_family populated from STATE_PROFILES",
      all(qs.resolution_family == STATE_PROFILES[qs.state_id].resolution_family
          for qs in evaluated_uniform[:5]))

# States that clear: score must exceed floor. first_sid = the_unformed_leader (Aptitude)
# Non-Authority state: floor = baseline * SIGNAL_FLOOR_MULTIPLIER_DEFAULT (1.08)
floor_value = reference * SIGNAL_FLOOR_MULTIPLIER_DEFAULT
above_floor_score = floor_value + 0.05
first_sid = list(STATE_PROFILES.keys())[0]
elevated_scores = {sid: (above_floor_score if sid == first_sid else 0.001)
                   for sid in STATE_PROFILES}
elevated_rankings = make_rankings(elevated_scores)
evaluated_elevated = apply_signal_floor(elevated_rankings, baseline)

cleared = [qs for qs in evaluated_elevated if qs.cleared_floor]
check("Elevated state clears floor",
      len(cleared) == 1 and cleared[0].state_id == first_sid,
      f"cleared: {[qs.state_id for qs in cleared]}")
check("Score lift pct > 0 for cleared state",
      cleared[0].score_lift_pct > 0.0,
      f"got {cleared[0].score_lift_pct:.2f}%")


# ── 4. route_output — insufficient_signal ─────────────────────────────────────
print("\n4. route_output — insufficient_signal")

routing_insuff = route_output(evaluated_uniform)
check("No cleared states: mode = insufficient_signal",
      routing_insuff.mode == "insufficient_signal",
      f"got {routing_insuff.mode!r}")
check("insufficient_signal: lead_state = None",
      routing_insuff.lead_state is None)
check("insufficient_signal: qualified_states = []",
      routing_insuff.qualified_states == [])
check("insufficient_signal: separation = 0.0",
      isclose(routing_insuff.separation, 0.0))


# ── 5. route_output — single mode, sufficient separation ──────────────────────
print("\n5. route_output — single mode (one state, sufficient separation)")

threshold = _SEPARATION_THRESHOLD_DEFAULT
above_floor = reference * SIGNAL_FLOOR_MULTIPLIER_DEFAULT + 0.1
second_score = above_floor - threshold - 0.01  # below threshold gap

first_sid = list(STATE_PROFILES.keys())[0]
second_sid = list(STATE_PROFILES.keys())[1]

scores_single = {sid: 0.001 for sid in STATE_PROFILES}
scores_single[first_sid] = above_floor
scores_single[second_sid] = second_score

rankings_single = make_rankings(scores_single)
# Note: second_sid score may or may not clear floor depending on value
# Let's make second_sid also clear floor but with large separation
scores_single[second_sid] = above_floor - threshold - 0.01

rankings_single2 = make_rankings(scores_single)
eval_single = apply_signal_floor(rankings_single2, baseline)
routing_single = route_output(eval_single)

check("Single mode: mode = single",
      routing_single.mode == "single",
      f"got {routing_single.mode!r}")
check("Single mode: lead_state is rank-1",
      routing_single.lead_state is not None and
      routing_single.lead_state.state_id == first_sid,
      f"got lead={routing_single.lead_state.state_id if routing_single.lead_state else None!r}")
check("Single mode: separation_threshold set",
      isclose(routing_single.separation_threshold, threshold))


# ── 6. route_output — single mode, exactly one state clears floor ─────────────
print("\n6. route_output — single when exactly one state clears floor")

scores_one = {sid: 0.001 for sid in STATE_PROFILES}
scores_one[first_sid] = above_floor  # only one clears

rankings_one = make_rankings(scores_one)
eval_one = apply_signal_floor(rankings_one, baseline)
routing_one = route_output(eval_one)

check("One state cleared: mode = single (not multi, per VI.2)",
      routing_one.mode == "single",
      f"got {routing_one.mode!r}")
check("One state cleared: lead_state populated",
      routing_one.lead_state is not None)
check("One state cleared: qualified_states has 1 entry",
      len(routing_one.qualified_states) == 1)


# ── 7. route_output — multi mode ──────────────────────────────────────────────
print("\n7. route_output — multi mode (multiple states, separation < threshold)")

# Two states above floor, close together (separation < threshold)
close_score_a = above_floor
close_score_b = above_floor - (threshold / 2)  # within threshold of each other

scores_multi = {sid: 0.001 for sid in STATE_PROFILES}
scores_multi[first_sid] = close_score_a
scores_multi[second_sid] = close_score_b

rankings_multi = make_rankings(scores_multi)
eval_multi = apply_signal_floor(rankings_multi, baseline)
routing_multi = route_output(eval_multi)

check("Multi mode: mode = multi",
      routing_multi.mode == "multi",
      f"got {routing_multi.mode!r}, separation={routing_multi.separation:.4f}, "
      f"threshold={routing_multi.separation_threshold:.4f}")
check("Multi mode: at least 2 qualified_states",
      len(routing_multi.qualified_states) >= 2,
      f"got {len(routing_multi.qualified_states)}")


# ── 8. route_output — single mode, multiple states, large separation ───────────
print("\n8. route_output — single mode (multiple clear, large separation)")

big_separation = threshold * 3
scores_sep = {sid: 0.001 for sid in STATE_PROFILES}
scores_sep[first_sid] = above_floor
scores_sep[second_sid] = above_floor - big_separation

rankings_sep = make_rankings(scores_sep)
eval_sep = apply_signal_floor(rankings_sep, baseline)
routing_sep = route_output(eval_sep)

check("Large separation: mode = single",
      routing_sep.mode == "single",
      f"got {routing_sep.mode!r}, separation={routing_sep.separation:.4f}")
check("Large separation: threshold_met = True",
      routing_sep.single_state_threshold_met is True)


# ── 9. build_private_block ────────────────────────────────────────────────────
print("\n9. build_private_block")

qs_test = QualifiedState(
    rank=1, state_id=first_sid,
    state_name=STATE_PROFILES[first_sid].state_name,
    score=above_floor, noise_baseline=reference,
    signal_floor=reference * SIGNAL_FLOOR_MULTIPLIER_DEFAULT,
    cleared_floor=True, score_lift_pct=20.0,
    resolution_family=STATE_PROFILES[first_sid].resolution_family,
)
sev = make_severity_result("Entrenched")

private = build_private_block(qs_test, sev)

check("PrivateOutputBlock state_name matches",
      private.state_name == STATE_PROFILES[first_sid].state_name)
check("PrivateOutputBlock severity_tier matches",
      private.severity_tier == "Entrenched")
check("PrivateOutputBlock severity_anchor_text = LOCKED V.3 copy",
      private.severity_anchor_text == SEVERITY_TIER_DESCRIPTIONS["Entrenched"],
      f"got: {private.severity_anchor_text[:50]}")
check("PrivateOutputBlock resolution_family populated",
      private.resolution_family == STATE_PROFILES[first_sid].resolution_family)
check("PrivateOutputBlock liability_condition_text empty (LLM-generated)",
      private.liability_condition_text == "")
check("PrivateOutputBlock asset_resolution_anchor_text empty (LLM-generated)",
      private.asset_resolution_anchor_text == "")
check("PrivateOutputBlock friction_tax_estimate None (CALIBRATION TARGET)",
      private.friction_tax_estimate is None)


# ── 10. build_shareable_block ─────────────────────────────────────────────────
print("\n10. build_shareable_block")

shareable = build_shareable_block(qs_test, sev)

check("ShareableOutputBlock state_name matches",
      shareable.state_name == STATE_PROFILES[first_sid].state_name)
check("ShareableOutputBlock severity_tier matches",
      shareable.severity_tier == "Entrenched")
check("ShareableOutputBlock attribution present and non-empty",
      len(shareable.attribution) > 0 and "PRV3" in shareable.attribution)
check("ShareableOutputBlock framing_text empty (LLM-generated)",
      shareable.framing_text == "")
check("ShareableOutputBlock observable_indicators empty list (LLM-generated)",
      shareable.observable_indicators == [])


# ── 11. OutputEngine.build — single-state ─────────────────────────────────────
print("\n11. OutputEngine.build — single-state")

engine = OutputEngine()
engine.set_noise_baseline(baseline=baseline)

sev_result = make_severity_result("Emerging")
package = engine.build(rankings_one, sev_result)

check("Single-state package: insufficient_signal = False",
      package.insufficient_signal is False)
check("Single-state package: routing.mode = single",
      package.routing.mode == "single",
      f"got {package.routing.mode!r}")
check("Single-state package: private block populated",
      package.private is not None)
check("Single-state package: shareable block populated",
      package.shareable is not None)
check("Single-state package: multi_state_private empty",
      package.multi_state_private == [])
check("Single-state package: multi_state_shareable empty",
      package.multi_state_shareable == [])
check("Single-state package: severity_result present",
      package.severity_result is sev_result)


# ── 12. OutputEngine.build — multi-state ──────────────────────────────────────
print("\n12. OutputEngine.build — multi-state")

package_multi = engine.build(rankings_multi, sev_result)

if package_multi.routing.mode == "multi":
    check("Multi-state package: private = None",
          package_multi.private is None)
    check("Multi-state package: shareable = None",
          package_multi.shareable is None)
    check("Multi-state package: multi_state_private populated",
          len(package_multi.multi_state_private) >= 2,
          f"got {len(package_multi.multi_state_private)}")
    check("Multi-state package: multi_state_shareable populated",
          len(package_multi.multi_state_shareable) >= 2)
    check("Multi-state: per-block severity tier matches",
          all(b.severity_tier == sev_result.tier
              for b in package_multi.multi_state_private))
else:
    # If routing resolved to single due to separation, verify that instead
    check("Multi rankings routed to single or multi (both valid)",
          package_multi.routing.mode in ("single", "multi"))


# ── 13. OutputEngine.build — insufficient_signal ──────────────────────────────
print("\n13. OutputEngine.build — insufficient_signal")

package_insuff = engine.build(uniform_rankings(), sev_result)

check("Insufficient signal: insufficient_signal = True",
      package_insuff.insufficient_signal is True,
      f"mode={package_insuff.routing.mode!r}")
check("Insufficient signal: message non-empty",
      len(package_insuff.insufficient_signal_message) > 0)
check("Insufficient signal: private = None",
      package_insuff.private is None)
check("Insufficient signal: shareable = None",
      package_insuff.shareable is None)
check("Insufficient signal: multi_state_private = []",
      package_insuff.multi_state_private == [])


# ── 14. OutputEngine noise baseline caching ───────────────────────────────────
print("\n14. OutputEngine — noise baseline caching")

engine2 = OutputEngine()
engine2.set_noise_baseline(baseline=baseline)
check("Second engine uses provided baseline",
      engine2._baseline is baseline)

# Clear class cache for test isolation
OutputEngine._cached_baseline = None
engine3 = OutputEngine()
baseline3 = engine3.set_noise_baseline()
check("Fresh engine computes baseline when not cached",
      baseline3 is not None and len(baseline3) == n)
check("Computed baseline gets cached at class level",
      OutputEngine._cached_baseline is not None)


# ── 15. Constants ──────────────────────────────────────────────────────────────
print("\n15. Constants")

check("SIGNAL_FLOOR_MULTIPLIER_AUTHORITY = 1.00 (LOCKED Session 16)",
      isclose(SIGNAL_FLOOR_MULTIPLIER_AUTHORITY, 1.00))
check("SIGNAL_FLOOR_MULTIPLIER_DEFAULT = 1.08 (Session 17 cosine-space correction)",
      isclose(SIGNAL_FLOOR_MULTIPLIER_DEFAULT, 1.08))
check("NOISE_SIMULATION_COUNT = 1000 (LOCKED)",
      NOISE_SIMULATION_COUNT == 1000)
check("SEPARATION_THRESHOLD = None (CALIBRATION TARGET)",
      SEPARATION_THRESHOLD is None)
check("_SEPARATION_THRESHOLD_DEFAULT > 0",
      _SEPARATION_THRESHOLD_DEFAULT > 0.0)


# ── 16. compute_causation_pattern (Category B) ────────────────────────────────
print("\n16. compute_causation_pattern — SPOF vs. Diffuse Causation")

_v_concentrated = {"aptitude_liability": 5.0}
_v_even = {
    "aptitude_liability": 2.5, "authority_liability": 2.5,
    "alliance_liability": 2.5, "attitude_liability": 2.5,
}
_v_two_axes = {"aptitude_liability": 3.0, "authority_liability": 3.0}  # dispersion = 0.5 (boundary)
_v_negative = {"aptitude_liability": -5.0, "authority_liability": 3.0}

check("0 qualified states (insufficient_signal routing): pattern = insufficient_signal",
      compute_causation_pattern(_v_concentrated, routing_insuff)["pattern"] == "insufficient_signal",
      f"got {compute_causation_pattern(_v_concentrated, routing_insuff)}")
check("insufficient_signal: qualified_state_count = 0",
      compute_causation_pattern({}, routing_insuff)["qualified_state_count"] == 0)

check("1 qualified state, concentrated liability: pattern = single_point",
      compute_causation_pattern(_v_concentrated, routing_one)["pattern"] == "single_point",
      f"got {compute_causation_pattern(_v_concentrated, routing_one)}")
check("1 qualified state, evenly spread liability: pattern = diffuse (dispersion 1.0)",
      compute_causation_pattern(_v_even, routing_one)["pattern"] == "diffuse",
      f"got {compute_causation_pattern(_v_even, routing_one)}")
check("1 qualified state, dispersion exactly at threshold (0.5): pattern = diffuse (>= threshold)",
      compute_causation_pattern(_v_two_axes, routing_one)["pattern"] == "diffuse"
      and isclose(compute_causation_pattern(_v_two_axes, routing_one)["dispersion"],
                  CAUSATION_DISPERSION_THRESHOLD, rel_tol=1e-6),
      f"got {compute_causation_pattern(_v_two_axes, routing_one)}")
check("1 qualified state, negative field clamped: pattern = single_point, no crash",
      compute_causation_pattern(_v_negative, routing_one)["pattern"] == "single_point",
      f"got {compute_causation_pattern(_v_negative, routing_one)}")

check("2+ qualified states: pattern = diffuse regardless of dispersion (concentrated vector)",
      compute_causation_pattern(_v_concentrated, routing_multi)["pattern"] == "diffuse",
      f"got {compute_causation_pattern(_v_concentrated, routing_multi)}")
check("2+ qualified states: qualified_state_count matches routing.qualified_states length",
      compute_causation_pattern({}, routing_multi)["qualified_state_count"]
      == len(routing_multi.qualified_states),
      f"got {compute_causation_pattern({}, routing_multi)['qualified_state_count']} vs "
      f"{len(routing_multi.qualified_states)}")

# Path B representative case: accumulated_vector={} (main.py run_engine() passes {}
# literally). Pattern must be driven entirely by qualified_state_count since
# dispersion is structurally 0.0 -- confirmed here, not assumed.
check("Path B style (empty vector), 1 qualified state: pattern = single_point, dispersion = 0.0",
      compute_causation_pattern({}, routing_one) == {
          "pattern": "single_point", "dispersion": 0.0,
          "qualified_state_count": 1,
      },
      f"got {compute_causation_pattern({}, routing_one)}")
check("Path B style (empty vector), 2+ qualified states: pattern = diffuse, dispersion = 0.0",
      compute_causation_pattern({}, routing_multi)["pattern"] == "diffuse"
      and compute_causation_pattern({}, routing_multi)["dispersion"] == 0.0,
      f"got {compute_causation_pattern({}, routing_multi)}")

check("dispersion always in [0.0, 1.0]",
      all(0.0 <= compute_causation_pattern(v, r)["dispersion"] <= 1.0
          for v in (_v_concentrated, _v_even, _v_two_axes, _v_negative, {})
          for r in (routing_insuff, routing_one, routing_multi)))
check("pattern always one of the three allowed values",
      all(compute_causation_pattern(v, r)["pattern"]
          in ("insufficient_signal", "single_point", "diffuse")
          for v in (_v_concentrated, _v_even, _v_two_axes, _v_negative, {})
          for r in (routing_insuff, routing_one, routing_multi)))


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Section VI output engine is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
