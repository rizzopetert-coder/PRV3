"""
PRV3 Scoring Engine — Section VII.2
Phase 1 Test Suite Interface Contract

Defines the test case schema, pass criteria, and validation scaffolding for
the Phase 1 test suite. Test profiles are a separate deliverable — this module
defines the schema they must conform to and the evaluation functions.

Phase 1 minimum: 3 profiles per state × 57 states = 171 test profiles.
(Spec references 45 states × 3 = 135; confirmed count is 57 as of Session 67
taxonomy expansion, up from 47 locked Session 5.)

Profile types per state:
  high_confidence:        clear single-state signal → output_type = single_state
  extreme_high_confidence: high_confidence + severity_escalation_flag required in output
  moderate:               signal with noise → correct state in top 3, correct output_type
  weak:                   signal near floor → correct state above floor, or correct no_signal

pass_criterion on ExpectedOutput (optional override):
  rank_1                     — target must be rank 1 (default for high_confidence)
  top_3                      — target must appear in top 3 (default for moderate)
  top_3_with_escalation_flag — top 3 AND severity.escalation_flag must be True
  None                       — profile-implied default applies

Spec reference: PRV3_Scoring_Architecture_Spec_v1.docx, Section VII.2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from engine.contract import validate_schema


# ── VII.2  Test case data structures ──────────────────────────────────────────

@dataclass
class TestAnswer:
    """
    One question answer in a test profile.

    selected_option_ids: list of option_id strings (single-element for
    forced_choice questions; one or more for weighted_multi_select).

    Spec reference: Section VII.2 — answers array schema
    """
    question_id:       str
    selected_option_ids: list  # list[str]


@dataclass
class ExpectedOutput:
    """
    Expected output values for a test profile.

    output_type:              "single_state" | "multi_state" | "no_signal"
    identified_states:        list of state_ids expected to appear in identified_states
    severity_tier:            expected severity tier (or None if not specified)
    asset_domain:             expected primary_asset_domain (or None if not specified)
    pass_criterion:           override pass criterion (or None for profile-implied default)
                              Values: "rank_1" | "top_3" | "top_3_with_escalation_flag"
    severity_escalation_flag: True if the engine output must carry severity.escalation_flag

    Spec reference: Section VII.2 — expected_output schema
    """
    output_type:              str
    identified_states:        list   # list of state_ids
    severity_tier:            Optional[str]  = None
    asset_domain:             Optional[str]  = None
    pass_criterion:           Optional[str]  = None
    severity_escalation_flag: bool           = False


@dataclass
class TestCase:
    """
    One Phase 1 test profile.

    profile_type: "high_confidence" | "extreme_high_confidence" | "moderate" | "weak"
    target_state: the state this profile is designed to elicit
    intake:        intake field values (dict matching IntakeData fields)
    answers:       simulated question answers
    expected:      expected output values for pass/fail evaluation

    Spec reference: Section VII.2 — test_id, description, intake, answers,
    expected_output schema. LOCKED.
    """
    test_id:       str
    description:   str
    profile_type:  str    # "high_confidence" | "extreme_high_confidence" | "moderate" | "weak"
    target_state:  str    # state_id this profile targets
    intake:        dict   # six intake fields
    answers:       list   # list[TestAnswer]
    expected:      ExpectedOutput


# ── VII.2  Pass criteria ───────────────────────────────────────────────────────

PROFILE_TYPES = ("high_confidence", "extreme_high_confidence", "moderate", "weak")

# Severity tier ordering for boundary tolerance checks
_TIER_ORDER = {"Emerging": 0, "Entrenched": 1, "Endemic": 2}


@dataclass
class TestResult:
    """
    Result of running one test case against the engine output.

    passed:            True if all applicable pass criteria were met.
    violations:        schema violations (from validate_schema).
    criteria_failures: list of human-readable pass-criteria failures.
    output:            the engine output dict that was evaluated.

    Spec reference: Section VII.2 — pass criteria definitions. LOCKED.
    """
    test_id:            str
    passed:             bool
    violations:         list   # schema violations
    criteria_failures:  list   # pass-criteria failures
    output:             dict   # engine output evaluated


def evaluate_pass_criteria(
    test_case: TestCase,
    engine_output: dict,
) -> list:
    """
    Evaluate pass criteria for one test case against the engine output.
    Returns a list of failure strings. Empty = all criteria met.

    Pass criteria by profile_type (Section VII.2, LOCKED):

    high_confidence / extreme_high_confidence:
      - Correct state is rank 1 in state_distribution (default)
      - output_type == single_state
      - expected.pass_criterion overrides rank check if set

    moderate:
      - Correct state appears in top 3 of state_distribution (default)
      - output_type matches expected
      - expected.pass_criterion overrides rank check if set

    weak:
      - Correct state is above_floor == True in state_distribution, OR
      - output_type == no_signal and expected is no_signal
      - expected.pass_criterion overrides to top_3 or top_3_with_escalation_flag if set

    severity_escalation_flag (all profile_types):
      - When expected.severity_escalation_flag is True:
        engine output severity.escalation_flag must be True

    Severity (all profile_types):
      - tier matches expected (if expected.severity_tier is specified)
      - Boundary tolerance: Emerging/Entrenched boundary allows ±1 tier

    Asset domain (all profile_types):
      - primary_asset_domain matches expected (if expected.asset_domain specified)

    Spec reference: Section VII.2
    """
    failures = []
    expected = test_case.expected
    profile = test_case.profile_type
    target = test_case.target_state

    # Resolve effective pass criterion
    if expected.pass_criterion is not None:
        criterion = expected.pass_criterion
    elif profile in ("high_confidence", "extreme_high_confidence"):
        criterion = "rank_1"
    elif profile == "moderate":
        criterion = "top_3"
    else:
        criterion = None  # weak: uses its own logic

    dist = engine_output.get("state_distribution", [])
    output_type = engine_output.get("output_type", "")

    # Find target state in distribution
    target_entry = next((e for e in dist if e.get("state_id") == target), None)
    target_rank = target_entry["rank"] if target_entry else None
    target_above_floor = target_entry.get("above_floor", False) if target_entry else False

    if profile in ("high_confidence", "extreme_high_confidence"):
        if criterion in ("top_3", "top_3_with_escalation_flag"):
            if target_rank is None or target_rank > 3:
                failures.append(
                    f"{profile}: {target!r} is rank {target_rank}, expected top 3"
                )
        else:  # rank_1 (default)
            if target_rank != 1:
                failures.append(
                    f"{profile}: {target!r} is rank {target_rank}, expected rank 1"
                )
        if output_type != "single_state":
            failures.append(
                f"{profile}: output_type={output_type!r}, expected 'single_state'"
            )

    elif profile == "moderate":
        if criterion == "rank_1":
            if target_rank != 1:
                failures.append(
                    f"moderate: {target!r} is rank {target_rank}, expected rank 1"
                )
        else:  # top_3 or top_3_with_escalation_flag (default for moderate)
            if target_rank is None or target_rank > 3:
                failures.append(
                    f"moderate: {target!r} is rank {target_rank}, expected top 3"
                )
        if output_type != expected.output_type:
            failures.append(
                f"moderate: output_type={output_type!r}, expected {expected.output_type!r}"
            )

    elif profile == "weak":
        if criterion in ("top_3", "top_3_with_escalation_flag"):
            if target_rank is None or target_rank > 3:
                failures.append(
                    f"weak: {target!r} is rank {target_rank}, expected top 3"
                )
        elif expected.output_type == "no_signal":
            if output_type != "no_signal":
                failures.append(
                    f"weak: output_type={output_type!r}, expected 'no_signal'"
                )
        else:
            if not target_above_floor:
                failures.append(
                    f"weak: {target!r} is not above signal floor "
                    f"(above_floor={target_above_floor})"
                )

    else:
        failures.append(f"Unknown profile_type: {profile!r}")

    # Severity escalation flag check
    if expected.severity_escalation_flag:
        actual_flag = engine_output.get("severity", {}).get("escalation_flag", False)
        if not actual_flag:
            failures.append(
                "severity_escalation_flag: expected True in output, got False"
            )

    # Severity tier check
    if expected.severity_tier is not None:
        actual_tier = engine_output.get("severity", {}).get("tier")
        if actual_tier != expected.severity_tier:
            # Apply boundary tolerance: ±1 tier at Emerging/Entrenched boundary
            exp_ord = _TIER_ORDER.get(expected.severity_tier, -1)
            act_ord = _TIER_ORDER.get(actual_tier, -1)
            boundary_case = (
                abs(exp_ord - act_ord) == 1
                and {exp_ord, act_ord} <= {0, 1}  # Emerging/Entrenched boundary
            )
            if not boundary_case:
                failures.append(
                    f"severity: tier={actual_tier!r}, expected {expected.severity_tier!r}"
                )

    # Asset domain check
    if expected.asset_domain is not None:
        actual_domain = engine_output.get("asset_score", {}).get("primary_asset_domain")
        if actual_domain != expected.asset_domain:
            failures.append(
                f"asset_score: primary_asset_domain={actual_domain!r}, "
                f"expected {expected.asset_domain!r}"
            )

    return failures


def run_test_case(
    test_case: TestCase,
    engine_output: dict,
) -> TestResult:
    """
    Validate schema and evaluate pass criteria for one test case.

    engine_output is the dict returned by assemble_output(). This function
    does not run the engine — the caller is responsible for producing the
    output from test_case.intake and test_case.answers.

    Returns TestResult with passed flag, any schema violations, and any
    criteria failures.

    Spec reference: Section VII.2
    """
    violations = validate_schema(engine_output)
    criteria_failures = evaluate_pass_criteria(test_case, engine_output)
    passed = len(violations) == 0 and len(criteria_failures) == 0
    return TestResult(
        test_id=test_case.test_id,
        passed=passed,
        violations=violations,
        criteria_failures=criteria_failures,
        output=engine_output,
    )


# ── Test suite collection helpers ──────────────────────────────────────────────

def validate_test_case_schema(tc: dict) -> list:
    """
    Validate a test case dict against the VII.2 test case schema.
    Returns list of violation strings. Empty = schema-compliant.

    Required fields: test_id, description, profile_type, target_state,
    intake, answers, expected (with output_type and identified_states).

    Spec reference: Section VII.2 — test case schema. LOCKED.
    """
    violations = []
    required = {
        "test_id": str, "description": str, "profile_type": str,
        "target_state": str, "intake": dict, "answers": list,
        "expected": dict,
    }
    for fname, ftype in required.items():
        if fname not in tc:
            violations.append(f"MISSING field: {fname!r}")
        elif not isinstance(tc[fname], ftype):
            violations.append(
                f"WRONG TYPE for {fname!r}: "
                f"expected {ftype.__name__}, got {type(tc[fname]).__name__}"
            )

    if "profile_type" in tc and tc["profile_type"] not in PROFILE_TYPES:
        violations.append(
            f"INVALID profile_type: {tc['profile_type']!r}. "
            f"Must be one of {PROFILE_TYPES}"
        )

    expected = tc.get("expected", {})
    if isinstance(expected, dict):
        for f in ("output_type", "identified_states"):
            if f not in expected:
                violations.append(f"expected MISSING field {f!r}")

    answers = tc.get("answers", [])
    if isinstance(answers, list):
        for i, ans in enumerate(answers):
            if not isinstance(ans, dict):
                violations.append(f"answers[{i}] is not a dict")
                continue
            for f in ("question_id", "selected_option_ids"):
                if f not in ans:
                    violations.append(f"answers[{i}] MISSING field {f!r}")

    return violations


def run_suite(
    test_cases: list,
    engine_outputs: dict,
) -> dict:
    """
    Run the full test suite.

    Parameters:
      test_cases:     list[TestCase]
      engine_outputs: {test_id: engine_output_dict} — pre-computed outputs

    Returns a summary dict:
      {
        "total": int,
        "passed": int,
        "failed": int,
        "results": list[TestResult],
        "by_profile_type": {"high_confidence": ..., "extreme_high_confidence": ...,
                            "moderate": ..., "weak": ...},
        "by_state": {state_id: {"total": int, "passed": int}},
      }
    """
    results = []
    by_type = {pt: {"total": 0, "passed": 0} for pt in PROFILE_TYPES}
    by_state: dict = {}

    for tc in test_cases:
        output = engine_outputs.get(tc.test_id, {})
        if not output:
            result = TestResult(
                test_id=tc.test_id,
                passed=False,
                violations=[],
                criteria_failures=[f"No engine output found for test_id {tc.test_id!r}"],
                output={},
            )
        else:
            result = run_test_case(tc, output)

        results.append(result)

        pt = tc.profile_type
        if pt in by_type:
            by_type[pt]["total"] += 1
            if result.passed:
                by_type[pt]["passed"] += 1

        sid = tc.target_state
        if sid not in by_state:
            by_state[sid] = {"total": 0, "passed": 0}
        by_state[sid]["total"] += 1
        if result.passed:
            by_state[sid]["passed"] += 1

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    return {
        "total":           total,
        "passed":          passed,
        "failed":          total - passed,
        "results":         results,
        "by_profile_type": by_type,
        "by_state":        by_state,
    }
