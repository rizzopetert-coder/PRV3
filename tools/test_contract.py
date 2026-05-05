"""
PRV3 Engine Output Contract — Section VII Integration Test

Verifies:
  1. assemble_output: produces all 13 top-level fields
  2. validate_schema: clean output passes validation
  3. validate_schema: catches every category of violation
  4. output_type mapping: single_state / multi_state / no_signal
  5. state_distribution: all states present, sorted descending, above_floor correct
  6. identified_states: null distinguishing_language for single, string for multi
  7. severity object: tier enum, anchor_text from V.3, score, inputs
  8. asset_score object: all fields present
  9. narrative_modulation: all fields, correct values when not fired
 10. checkpoint_log: all three checkpoints, all sub-fields
 11. jurisdiction_flags: all fields present
 12. private_output: all fields, friction_tax None
 13. shareable_output: all fields, attribution non-empty
 14. engine_version: string, non-empty
 15. TestCase schema: validate_test_case_schema passes/fails correctly
 16. evaluate_pass_criteria: high_confidence / moderate / weak criteria
 17. run_test_case: passed/failed result assembly
 18. run_suite: summary aggregation
"""

import sys
from math import isclose
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.contract import (
    assemble_output, validate_schema, SessionData, ENGINE_VERSION,
    _OUTPUT_TYPE_VALUES, _SEVERITY_TIER_VALUES,
)
from engine.test_suite import (
    TestCase, TestAnswer, ExpectedOutput, TestResult,
    evaluate_pass_criteria, run_test_case, run_suite,
    validate_test_case_schema, PROFILE_TYPES,
)
from engine.accumulation import IntakeData, AccumulationEngine, StateRanking
from engine.output import OutputEngine
from engine.severity import SeverityEngine, SeverityResult, SEVERITY_TIER_DESCRIPTIONS
from engine.checkpoint import CheckpointResult
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.narrative import NarrativeExtractionResult

PASS = []
FAIL = []

def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


print("=" * 64)
print("PRV3 Engine Output Contract — Section VII Integration Test")
print("=" * 64)

n = len(STATE_PROFILES)
state_ids = list(STATE_PROFILES.keys())
first_sid = state_ids[0]
second_sid = state_ids[1]


# ── Build a synthetic complete session ────────────────────────────────────────

def make_severity(tier="Emerging"):
    from engine.severity import SeverityResult
    return SeverityResult(
        raw_score=1.0,
        score_0_100=20.0,
        score_0_100_with_narrative=20.0,
        tier=tier,
        tier_description=SEVERITY_TIER_DESCRIPTIONS[tier],
        narrative_contribution_0_100=0.0,
        narrative_ceiling_applied=False,
        input_count=0,
    )


def make_rankings(top_score=0.9):
    """One dominant state, rest uniform."""
    remaining = (1.0 - top_score) / (n - 1)
    rankings = []
    for i, sid in enumerate(STATE_PROFILES):
        s = top_score if sid == first_sid else remaining
        rankings.append(StateRanking(rank=i+1, state_id=sid, distance=0.3, score=s))
    rankings.sort(key=lambda r: -r.score)
    for i, r in enumerate(rankings):
        r.rank = i + 1
    return rankings


intake = IntakeData(
    headcount="100-249",
    industry="Technology",
    org_type="PE or VC-backed",
    jurisdictions=["CA"],
    significant_events=["none"],
    principal_role="C-suite",
)

acc_vector = {f: 0.5 for f in DIMENSIONAL_FIELDS}
sev = make_severity("Entrenched")

# Build output package via OutputEngine
from engine.output import OutputEngine
from engine.accumulation import rank_states
from engine.data.states import BASELINE_VALUE
from math import sqrt

# Compute noise baseline
zero_d = sqrt(len(DIMENSIONAL_FIELDS) * BASELINE_VALUE ** 2)
baseline_score = 1.0 / (1.0 + zero_d)
noise_baseline = {sid: baseline_score for sid in STATE_PROFILES}

# Rankings where first_sid is above floor
floor_val = baseline_score * 1.15
above_floor_rankings = make_rankings(top_score=floor_val + 0.05)

out_engine = OutputEngine()
out_engine.set_noise_baseline(baseline=noise_baseline)
output_pkg = out_engine.build(above_floor_rankings, sev)

# Synthetic checkpoint results
cp11 = CheckpointResult(
    checkpoint="Q11", entropy=4.2, threshold=0.6, fires=True,
    top_cluster="C-Manager", distinguishers=[], narrative_trigger=False,
)
cp19 = CheckpointResult(
    checkpoint="Q19", entropy=1.8, threshold=0.4, fires=True,
    top_cluster="C-Manager", distinguishers=[], narrative_trigger=False,
)
cp27 = CheckpointResult(
    checkpoint="Q27", entropy=0.3, threshold=0.2, fires=True,
    top_cluster=None, distinguishers=[], narrative_trigger=True,
)

session = SessionData(
    session_id=SessionData.new_session_id(),
    intake=intake,
    final_rankings=above_floor_rankings,
    accumulated_vector=acc_vector,
    output_package=output_pkg,
    severity_result=sev,
    checkpoint_q11=cp11,
    checkpoint_q19=cp19,
    checkpoint_q27=cp27,
)

output = assemble_output(session)


# ── 1. assemble_output: 13 top-level fields ───────────────────────────────────
print("\n1. assemble_output — 13 top-level fields present")

expected_fields = [
    "session_id", "intake", "state_distribution", "output_type",
    "identified_states", "severity", "asset_score", "narrative_modulation",
    "checkpoint_log", "jurisdiction_flags", "private_output",
    "shareable_output", "engine_version", "monitoring_metadata",
]
for f in expected_fields:
    check(f"Field {f!r} present", f in output, f"missing from output")
check("Exactly 14 top-level fields", len(output) == 14, f"got {len(output)}")


# ── 2. validate_schema: clean output passes ───────────────────────────────────
print("\n2. validate_schema — clean output passes")

violations = validate_schema(output)
check("Clean output: no schema violations",
      violations == [],
      f"violations: {violations}")


# ── 3. validate_schema: catches violations ────────────────────────────────────
print("\n3. validate_schema — catches violations")

import copy

# Missing top-level field
bad_missing = copy.deepcopy(output)
del bad_missing["session_id"]
v_missing = validate_schema(bad_missing)
check("Missing top-level field detected",
      any("MISSING top-level field" in v and "session_id" in v for v in v_missing),
      f"got: {v_missing}")

# Wrong type
bad_type = copy.deepcopy(output)
bad_type["session_id"] = 12345
v_type = validate_schema(bad_type)
check("Wrong type detected",
      any("WRONG TYPE" in v and "session_id" in v for v in v_type),
      f"got: {v_type}")

# Invalid output_type enum
bad_enum = copy.deepcopy(output)
bad_enum["output_type"] = "invalid_type"
v_enum = validate_schema(bad_enum)
check("Invalid output_type enum detected",
      any("INVALID output_type" in v for v in v_enum),
      f"got: {v_enum}")

# Invalid severity tier
bad_tier = copy.deepcopy(output)
bad_tier["severity"]["tier"] = "Catastrophic"
v_tier = validate_schema(bad_tier)
check("Invalid severity tier detected",
      any("INVALID severity.tier" in v for v in v_tier),
      f"got: {v_tier}")

# Missing state_distribution entry field
bad_dist = copy.deepcopy(output)
if bad_dist["state_distribution"]:
    del bad_dist["state_distribution"][0]["above_floor"]
v_dist = validate_schema(bad_dist)
check("Missing state_distribution entry field detected",
      any("MISSING field" in v and "above_floor" in v for v in v_dist),
      f"got: {v_dist}")

# Missing identified_states field
bad_ids = copy.deepcopy(output)
if bad_ids["identified_states"]:
    del bad_ids["identified_states"][0]["distinguishing_language"]
v_ids = validate_schema(bad_ids)
check("Missing identified_states.distinguishing_language detected",
      any("distinguishing_language" in v for v in v_ids),
      f"got: {v_ids}")

# Missing checkpoint sub-field
bad_cp = copy.deepcopy(output)
del bad_cp["checkpoint_log"]["q11"]["entropy"]
v_cp = validate_schema(bad_cp)
check("Missing checkpoint_log.q11.entropy detected",
      any("q11" in v and "entropy" in v for v in v_cp),
      f"got: {v_cp}")

# Missing monitoring_metadata sub-field
bad_mm = copy.deepcopy(output)
del bad_mm["monitoring_metadata"]["flag_count"]
v_mm = validate_schema(bad_mm)
check("Missing monitoring_metadata.flag_count detected",
      any("monitoring_metadata" in v and "flag_count" in v for v in v_mm),
      f"got: {v_mm}")


# ── 4. output_type mapping ────────────────────────────────────────────────────
print("\n4. output_type mapping")

check("output_type is a valid enum value",
      output["output_type"] in _OUTPUT_TYPE_VALUES,
      f"got {output['output_type']!r}")

# Verify mapping logic: single vs multi vs no_signal
routing_mode = output_pkg.routing.mode
mode_map = {"single": "single_state", "multi": "multi_state",
            "insufficient_signal": "no_signal"}
expected_ot = mode_map.get(routing_mode, "no_signal")
check("output_type matches routing mode",
      output["output_type"] == expected_ot,
      f"routing={routing_mode!r}, output_type={output['output_type']!r}")


# ── 5. state_distribution ─────────────────────────────────────────────────────
print("\n5. state_distribution")

dist = output["state_distribution"]
check("state_distribution has all states",
      len(dist) == n,
      f"got {len(dist)}")
check("state_distribution sorted descending by score",
      all(dist[i]["score"] >= dist[i+1]["score"] for i in range(len(dist)-1)))
check("state_distribution ranks are 1..n",
      sorted(e["rank"] for e in dist) == list(range(1, n+1)))
check("first_sid appears in distribution",
      any(e["state_id"] == first_sid for e in dist))

# above_floor correct: first_sid should be above floor (we built it that way)
first_entry = next(e for e in dist if e["state_id"] == first_sid)
check("first_sid above_floor=True (above signal floor)",
      first_entry["above_floor"] is True,
      f"above_floor={first_entry['above_floor']}")


# ── 6. identified_states ──────────────────────────────────────────────────────
print("\n6. identified_states")

ids = output["identified_states"]
check("identified_states is a list", isinstance(ids, list))
if output["output_type"] == "single_state":
    check("single_state: exactly 1 identified state",
          len(ids) == 1, f"got {len(ids)}")
    check("single_state: distinguishing_language is None",
          ids[0]["distinguishing_language"] is None,
          f"got {ids[0]['distinguishing_language']!r}")
elif output["output_type"] == "multi_state":
    check("multi_state: >= 2 identified states",
          len(ids) >= 2, f"got {len(ids)}")
    check("multi_state: distinguishing_language is string",
          all(isinstance(s["distinguishing_language"], str) for s in ids))
else:
    check("no_signal: identified_states empty",
          ids == [], f"got {ids}")


# ── 7. severity object ────────────────────────────────────────────────────────
print("\n7. severity object")

sev_obj = output["severity"]
check("severity.tier is valid enum",
      sev_obj["tier"] in _SEVERITY_TIER_VALUES,
      f"got {sev_obj['tier']!r}")
check("severity.anchor_text = LOCKED V.3 copy",
      sev_obj["anchor_text"] == SEVERITY_TIER_DESCRIPTIONS[sev_obj["tier"]],
      f"mismatch")
check("severity.score is float",
      isinstance(sev_obj["score"], float),
      f"type={type(sev_obj['score']).__name__}")
check("severity.inputs has all required keys",
      all(k in sev_obj["inputs"] for k in (
          "duration_band", "population_band", "prior_attempts",
          "financial_indicators_present", "named_condition"
      )))


# ── 8. asset_score ────────────────────────────────────────────────────────────
print("\n8. asset_score")

asset = output["asset_score"]
check("asset_score.score is float",
      isinstance(asset["score"], float))
check("asset_score.score in [0, 1]",
      0.0 <= asset["score"] <= 1.0,
      f"got {asset['score']}")
check("asset_score.primary_asset_domain is string",
      isinstance(asset["primary_asset_domain"], str))
check("asset_score.resolution_anchor_text is string",
      isinstance(asset["resolution_anchor_text"], str))


# ── 9. narrative_modulation ───────────────────────────────────────────────────
print("\n9. narrative_modulation")

narr = output["narrative_modulation"]
check("narrative_modulation.fired is bool",
      isinstance(narr["fired"], bool))
check("narrative_modulation.overall_confidence is float",
      isinstance(narr["overall_confidence"], float))
check("narrative_modulation.signals_extracted is int",
      isinstance(narr["signals_extracted"], int))
check("narrative_modulation.state_delta is float",
      isinstance(narr["state_delta"], float))
check("narrative_modulation.severity_delta is float",
      isinstance(narr["severity_delta"], float))
check("narrative_modulation.trigger_point is None (no narrative this session)",
      narr["trigger_point"] is None,
      f"got {narr['trigger_point']!r}")
check("narrative_modulation.fired = False (no narrative this session)",
      narr["fired"] is False)


# ── 10. checkpoint_log ────────────────────────────────────────────────────────
print("\n10. checkpoint_log")

cl = output["checkpoint_log"]
check("checkpoint_log has q11, q19, q27",
      all(k in cl for k in ("q11", "q19", "q27")))
for ck in ("q11", "q19", "q27"):
    entry = cl[ck]
    check(f"{ck} has all 4 sub-fields",
          all(f in entry for f in ("entropy", "threshold", "threshold_exceeded", "distinguisher_fired")))
check("q11.entropy matches CheckpointResult",
      isclose(cl["q11"]["entropy"], cp11.entropy, rel_tol=1e-4))
check("q27.threshold_exceeded = True (entropy 0.3 > threshold 0.2)",
      cl["q27"]["threshold_exceeded"] is True)
check("q11.distinguisher_fired = False (empty distinguishers list)",
      cl["q11"]["distinguisher_fired"] is False)


# ── 11. jurisdiction_flags ────────────────────────────────────────────────────
print("\n11. jurisdiction_flags")

jf = output["jurisdiction_flags"]
check("jurisdiction_flags.transparency is bool",
      isinstance(jf["transparency"], bool))
check("CA jurisdiction: transparency = True",
      jf["transparency"] is True,
      f"got {jf['transparency']}")
check("jurisdiction_flags.applied_multipliers is list",
      isinstance(jf["applied_multipliers"], list))


# ── 12. private_output ────────────────────────────────────────────────────────
print("\n12. private_output")

priv = output["private_output"]
check("private_output.opening_text is string",
      isinstance(priv["opening_text"], str))
check("private_output.liability_block is string",
      isinstance(priv["liability_block"], str))
check("private_output.asset_anchor_text is string",
      isinstance(priv["asset_anchor_text"], str))
check("private_output.resolution_routing is string",
      isinstance(priv["resolution_routing"], str))
check("private_output.friction_tax_estimate is None (CALIBRATION TARGET)",
      priv["friction_tax_estimate"] is None)
if output["output_type"] == "single_state":
    check("single_state: opening_text = state name",
          len(priv["opening_text"]) > 0,
          f"got empty string")


# ── 13. shareable_output ──────────────────────────────────────────────────────
print("\n13. shareable_output")

sha = output["shareable_output"]
check("shareable_output.framing_text is string",
      isinstance(sha["framing_text"], str))
check("shareable_output.observable_indicators is list",
      isinstance(sha["observable_indicators"], list))
check("shareable_output.resolution_framing is string",
      isinstance(sha["resolution_framing"], str))
check("shareable_output.attribution_text non-empty and contains PRV3",
      isinstance(sha["attribution_text"], str) and "PRV3" in sha["attribution_text"],
      f"got {sha['attribution_text']!r}")


# ── 14. engine_version ────────────────────────────────────────────────────────
print("\n14. engine_version")

check("engine_version is string", isinstance(output["engine_version"], str))
check("engine_version non-empty", len(output["engine_version"]) > 0)
check("engine_version matches ENGINE_VERSION constant",
      output["engine_version"] == ENGINE_VERSION)


# ── 15. TestCase schema validation ────────────────────────────────────────────
print("\n15. validate_test_case_schema")

valid_tc = {
    "test_id": "TC-001",
    "description": "High-confidence Unformed Leader profile",
    "profile_type": "high_confidence",
    "target_state": "the_unformed_leader",
    "intake": {"headcount": "25-99"},
    "answers": [{"question_id": "Q01", "selected_option_ids": ["A"]}],
    "expected": {"output_type": "single_state", "identified_states": ["the_unformed_leader"]},
}
v_tc = validate_test_case_schema(valid_tc)
check("Valid test case: no violations", v_tc == [], f"got: {v_tc}")

# Missing required field
bad_tc = {k: v for k, v in valid_tc.items() if k != "test_id"}
v_bad = validate_test_case_schema(bad_tc)
check("Missing test_id detected", any("test_id" in v for v in v_bad), f"got: {v_bad}")

# Invalid profile_type
bad_type_tc = {**valid_tc, "profile_type": "invalid"}
v_bad_type = validate_test_case_schema(bad_type_tc)
check("Invalid profile_type detected",
      any("INVALID profile_type" in v for v in v_bad_type),
      f"got: {v_bad_type}")

# Missing expected.output_type
bad_exp = {**valid_tc, "expected": {"identified_states": []}}
v_bad_exp = validate_test_case_schema(bad_exp)
check("Missing expected.output_type detected",
      any("output_type" in v for v in v_bad_exp),
      f"got: {v_bad_exp}")

# Missing answer field
bad_ans = {**valid_tc, "answers": [{"question_id": "Q01"}]}
v_bad_ans = validate_test_case_schema(bad_ans)
check("Missing answer selected_option_ids detected",
      any("selected_option_ids" in v for v in v_bad_ans),
      f"got: {v_bad_ans}")


# ── 16. evaluate_pass_criteria ────────────────────────────────────────────────
print("\n16. evaluate_pass_criteria")

# Build a synthetic engine output for pass criteria testing
def make_output(rank1_state, output_type, severity_tier, above_floor_states=None):
    above_floor_states = above_floor_states or [rank1_state]
    d = copy.deepcopy(output)
    d["output_type"] = output_type
    d["severity"]["tier"] = severity_tier
    d["severity"]["anchor_text"] = SEVERITY_TIER_DESCRIPTIONS[severity_tier]
    d["identified_states"] = [{"state_id": rank1_state, "state_name": "X",
                                "score": 0.9, "distinguishing_language": None}]
    # Rebuild distribution with correct ranks and above_floor
    for i, entry in enumerate(d["state_distribution"]):
        if entry["state_id"] == rank1_state:
            entry["rank"] = 1
            entry["above_floor"] = rank1_state in above_floor_states
            entry["score"] = 0.9
        else:
            # Ensure rank is > 1 for all others
            entry["above_floor"] = entry["state_id"] in above_floor_states
    # Re-sort and re-rank
    d["state_distribution"].sort(key=lambda e: -e["score"])
    for i, e in enumerate(d["state_distribution"]):
        e["rank"] = i + 1
    return d

target = "the_unformed_leader"

# high_confidence: rank 1 + single_state → PASS
tc_hc = TestCase("T1", "desc", "high_confidence", target,
                 {}, [], ExpectedOutput("single_state", [target]))
out_hc = make_output(target, "single_state", "Emerging", [target])
failures_hc = evaluate_pass_criteria(tc_hc, out_hc)
check("high_confidence PASS: rank 1 + single_state",
      failures_hc == [], f"failures: {failures_hc}")

# high_confidence: rank 2 → FAIL
out_hc_bad = copy.deepcopy(out_hc)
for e in out_hc_bad["state_distribution"]:
    if e["state_id"] == target:
        e["rank"] = 2
failures_hc_bad = evaluate_pass_criteria(tc_hc, out_hc_bad)
check("high_confidence FAIL: rank 2",
      any("rank" in f for f in failures_hc_bad),
      f"failures: {failures_hc_bad}")

# moderate: in top 3 + correct output_type → PASS
tc_mod = TestCase("T2", "desc", "moderate", target,
                  {}, [], ExpectedOutput("single_state", [target]))
out_mod = make_output(target, "single_state", "Emerging", [target])
for e in out_mod["state_distribution"]:
    if e["state_id"] == target:
        e["rank"] = 3
failures_mod = evaluate_pass_criteria(tc_mod, out_mod)
check("moderate PASS: rank 3 + single_state",
      failures_mod == [], f"failures: {failures_mod}")

# moderate: rank 4 → FAIL
out_mod_bad = copy.deepcopy(out_mod)
for e in out_mod_bad["state_distribution"]:
    if e["state_id"] == target:
        e["rank"] = 4
failures_mod_bad = evaluate_pass_criteria(tc_mod, out_mod_bad)
check("moderate FAIL: rank 4",
      any("top 3" in f for f in failures_mod_bad),
      f"failures: {failures_mod_bad}")

# weak: above floor → PASS
tc_weak = TestCase("T3", "desc", "weak", target,
                   {}, [], ExpectedOutput("single_state", [target]))
out_weak = make_output(target, "single_state", "Emerging", [target])
failures_weak = evaluate_pass_criteria(tc_weak, out_weak)
check("weak PASS: above_floor=True",
      failures_weak == [], f"failures: {failures_weak}")

# weak: not above floor → FAIL
out_weak_bad = copy.deepcopy(out_weak)
for e in out_weak_bad["state_distribution"]:
    if e["state_id"] == target:
        e["above_floor"] = False
failures_weak_bad = evaluate_pass_criteria(tc_weak, out_weak_bad)
check("weak FAIL: above_floor=False",
      any("floor" in f for f in failures_weak_bad),
      f"failures: {failures_weak_bad}")

# Severity boundary tolerance: Emerging expected, Entrenched actual → PASS
tc_sev = TestCase("T4", "desc", "high_confidence", target,
                  {}, [], ExpectedOutput("single_state", [target], severity_tier="Emerging"))
out_sev = make_output(target, "single_state", "Entrenched", [target])
failures_sev = evaluate_pass_criteria(tc_sev, out_sev)
check("Severity boundary tolerance: Emerging/Entrenched boundary passes",
      failures_sev == [], f"failures: {failures_sev}")

# Severity out of tolerance: Emerging expected, Endemic actual → FAIL
out_sev_bad = make_output(target, "single_state", "Endemic", [target])
failures_sev_bad = evaluate_pass_criteria(tc_sev, out_sev_bad)
check("Severity boundary fail: Emerging expected, Endemic actual",
      any("severity" in f for f in failures_sev_bad),
      f"failures: {failures_sev_bad}")


# ── 17. run_test_case ─────────────────────────────────────────────────────────
print("\n17. run_test_case")

tc_pass = TestCase("T5", "Pass case", "high_confidence", target,
                   {}, [], ExpectedOutput("single_state", [target]))
result_pass = run_test_case(tc_pass, out_hc)
check("run_test_case: passing case passed=True",
      result_pass.passed is True,
      f"violations={result_pass.violations}, criteria={result_pass.criteria_failures}")
check("run_test_case: test_id preserved",
      result_pass.test_id == "T5")

tc_fail = TestCase("T6", "Fail case", "high_confidence", target,
                   {}, [], ExpectedOutput("single_state", [target]))
result_fail = run_test_case(tc_fail, out_hc_bad)
check("run_test_case: failing case passed=False",
      result_fail.passed is False)
check("run_test_case: criteria_failures populated",
      len(result_fail.criteria_failures) > 0)

# Schema violation → passed=False regardless of criteria
tc_schema = TestCase("T7", "Schema fail", "high_confidence", target,
                     {}, [], ExpectedOutput("single_state", [target]))
bad_schema_out = copy.deepcopy(out_hc)
del bad_schema_out["engine_version"]
result_schema = run_test_case(tc_schema, bad_schema_out)
check("run_test_case: schema violation → passed=False",
      result_schema.passed is False)
check("run_test_case: violations populated on schema failure",
      len(result_schema.violations) > 0)


# ── 18. run_suite ─────────────────────────────────────────────────────────────
print("\n18. run_suite")

suite_cases = [
    TestCase("S1", "HC", "high_confidence", target, {}, [], ExpectedOutput("single_state", [target])),
    TestCase("S2", "Mod", "moderate", target, {}, [], ExpectedOutput("single_state", [target])),
    TestCase("S3", "Weak", "weak", target, {}, [], ExpectedOutput("single_state", [target])),
]
# S1: passes (out_hc is rank 1, single_state)
# S2: passes (rank 3 is top 3, single_state)
# S3: passes (above_floor=True)
suite_outputs = {
    "S1": out_hc,
    "S2": out_mod,
    "S3": out_weak,
}
summary = run_suite(suite_cases, suite_outputs)
check("run_suite: total = 3", summary["total"] == 3, f"got {summary['total']}")
check("run_suite: all passed", summary["passed"] == 3,
      f"passed={summary['passed']}, failed={summary['failed']}")
check("run_suite: by_profile_type covers all types",
      all(pt in summary["by_profile_type"] for pt in PROFILE_TYPES))
check("run_suite: by_state has target state",
      target in summary["by_state"],
      f"states: {list(summary['by_state'].keys())[:3]}")
check("run_suite: results list has 3 TestResult objects",
      len(summary["results"]) == 3 and
      all(isinstance(r, TestResult) for r in summary["results"]))

# Missing output → failure
suite_missing = run_suite(suite_cases, {"S1": out_hc})  # S2 and S3 missing
check("run_suite: missing output → failed",
      suite_missing["failed"] >= 2,
      f"failed={suite_missing['failed']}")


# ── 19. monitoring_metadata ────────────────────────────────────────────────────
print("\n19. monitoring_metadata")

mm = output.get("monitoring_metadata", {})

# Structure
check("monitoring_metadata present in output",
      "monitoring_metadata" in output)
check("monitoring_metadata.flags is a list",
      isinstance(mm.get("flags"), list))
check("monitoring_metadata.flag_count is int",
      isinstance(mm.get("flag_count"), int))
check("monitoring_metadata.any_high_priority is bool",
      isinstance(mm.get("any_high_priority"), bool))
check("monitoring_metadata.flag_count equals len(flags)",
      mm.get("flag_count") == len(mm.get("flags", [])))
check("monitoring_metadata has exactly 1 flag (Phase 1)",
      len(mm.get("flags", [])) == 1,
      f"got {len(mm.get('flags', []))}")

# Flag field structure (using existing session with none intake)
flag0 = mm["flags"][0] if mm.get("flags") else {}
check("flag.flag_id correct",
      flag0.get("flag_id") == "decision_blindness_protected_activity")
check("flag.triggered is bool",
      isinstance(flag0.get("triggered"), bool))
check("flag.trigger_conditions is dict",
      isinstance(flag0.get("trigger_conditions"), dict))
check("flag.severity_context is dict",
      isinstance(flag0.get("severity_context"), dict))
check("flag.recommended_routes is list",
      isinstance(flag0.get("recommended_routes"), list))
check("flag.priority is str",
      isinstance(flag0.get("priority"), str))
check("flag.internal_note is str",
      isinstance(flag0.get("internal_note"), str))
check("flag.visible_to_principal is False",
      flag0.get("visible_to_principal") is False)
check("flag.visible_to_resolution_specialist is True",
      flag0.get("visible_to_resolution_specialist") is True)

# trigger_conditions sub-fields
tc0 = flag0.get("trigger_conditions", {})
check("trigger_conditions.state_id is decision_blindness",
      tc0.get("state_id") == "decision_blindness")
check("trigger_conditions.score_threshold is noise_baseline",
      tc0.get("score_threshold") == "noise_baseline")
check("trigger_conditions.protected_activity_sources is list",
      isinstance(tc0.get("protected_activity_sources"), list))

# With none intake + q_signal=False: flag should not be triggered
check("flag not triggered with none intake and no q_signal",
      flag0.get("triggered") is False,
      f"triggered={flag0.get('triggered')}")


# ── Firing condition tests ────────────────────────────────────────────────────

def _make_db_session(intake_events, q_signal=False, db_score_mult=1.1):
    """
    Session where decision_blindness has score = db_score_mult * noise_baseline.
    db_score_mult > 1.0  -> DB above baseline -> condition (1) met.
    db_score_mult < 1.0  -> DB below baseline -> condition (1) not met.
    """
    from engine.accumulation import IntakeData, StateRanking
    from engine.contract import SessionData
    pa_intake = IntakeData(
        headcount="100-249",
        industry="Technology",
        org_type="PE or VC-backed",
        jurisdictions=["CA"],
        significant_events=intake_events,
        principal_role="C-suite",
    )
    db_score = baseline_score * db_score_mult
    other_score = baseline_score * 0.5
    db_rankings = []
    for i, sid in enumerate(STATE_PROFILES):
        s = db_score if sid == "decision_blindness" else other_score
        db_rankings.append(StateRanking(rank=i+1, state_id=sid, distance=0.3, score=s))
    db_rankings.sort(key=lambda r: -r.score)
    for i, r in enumerate(db_rankings):
        r.rank = i + 1
    db_pkg = out_engine.build(db_rankings, sev)
    return SessionData(
        session_id=SessionData.new_session_id(),
        intake=pa_intake,
        final_rankings=db_rankings,
        accumulated_vector=acc_vector,
        output_package=db_pkg,
        severity_result=sev,
        q_signal_decision_blindness=q_signal,
    )


# Scenario A: DB above baseline + external_legal_matter -> triggered
sess_a = _make_db_session(["external_legal_matter"])
out_a = assemble_output(sess_a)
mm_a = out_a.get("monitoring_metadata", {})
flag_a = mm_a["flags"][0] if mm_a.get("flags") else {}
check("Scenario A: flag triggered (DB above baseline + external_legal_matter)",
      flag_a.get("triggered") is True,
      f"triggered={flag_a.get('triggered')}, "
      f"tc={flag_a.get('trigger_conditions')}")
check("Scenario A: intake_significant_events in protected_activity_sources",
      "intake_significant_events" in flag_a.get(
          "trigger_conditions", {}).get("protected_activity_sources", []))
check("Scenario A: any_high_priority is True",
      mm_a.get("any_high_priority") is True)

# Scenario B: DB above baseline + q_signal -> triggered
sess_b = _make_db_session(["none"], q_signal=True)
out_b = assemble_output(sess_b)
mm_b = out_b.get("monitoring_metadata", {})
flag_b = mm_b["flags"][0] if mm_b.get("flags") else {}
check("Scenario B: flag triggered (DB above baseline + q_signal)",
      flag_b.get("triggered") is True,
      f"triggered={flag_b.get('triggered')}")
check("Scenario B: q_signal in protected_activity_sources",
      "q_signal" in flag_b.get(
          "trigger_conditions", {}).get("protected_activity_sources", []))

# Scenario C: DB below baseline -> not triggered even with protected activity
sess_c = _make_db_session(["external_legal_matter"], db_score_mult=0.5)
out_c = assemble_output(sess_c)
mm_c = out_c.get("monitoring_metadata", {})
flag_c = mm_c["flags"][0] if mm_c.get("flags") else {}
check("Scenario C: flag not triggered (DB below baseline)",
      flag_c.get("triggered") is False,
      f"triggered={flag_c.get('triggered')}")
check("Scenario C: any_high_priority is False",
      mm_c.get("any_high_priority") is False)

# Scenario D: DB above baseline but no protected activity -> not triggered
sess_d = _make_db_session(["none"], q_signal=False)
out_d = assemble_output(sess_d)
mm_d = out_d.get("monitoring_metadata", {})
flag_d = mm_d["flags"][0] if mm_d.get("flags") else {}
check("Scenario D: flag not triggered (no protected activity)",
      flag_d.get("triggered") is False,
      f"triggered={flag_d.get('triggered')}, "
      f"tc={flag_d.get('trigger_conditions')}")
check("Scenario D: protected_activity_sources empty",
      flag_d.get("trigger_conditions", {}).get("protected_activity_sources") == [])


# ── Summary ────────────────────────────────────────────────────────────────────
print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Section VII output contract is structurally valid.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
