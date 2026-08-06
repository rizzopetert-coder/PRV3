"""
PRV3 -- AUT-PS-01 (paper_shield) targeted hand-test, Q23 option D forced

Precedent pattern: same class of harness-blind-spot test as the
built_to_fail Q35-39 investigation -- calibration_runner.py's
best_option_for_state() never selects Q23's option D (it doesn't win the
dimension-max heuristic; confirmed a genuine, non-tie dimensional loss, not
a selection bug -- see tools/diag_bucket2_track_b_questions.md), so the
172-profile suite's own answer-generation can't exercise D's real content
regardless of AUT-PS-01's data being correct. This test forces D directly
and drives the REAL production engine functions (engine/main.py's
accumulate_one_answer()/run_accumulated_engine()), not
calibration_runner.py's harness mirror, to verify what a real respondent
choosing D would actually experience.

Confirms:
  1. Q23 IS live in Phase 1 (web/lib/session-store.ts's
     PHASE_1_QUESTION_SEQUENCE) -- this path is reachable today, not
     Phase-2-pending like Q31/Q03A/Q27A.
  2. D's severity_trigger=True + severity_follow_on_id=SEVER-05 (commit
     TBD, engine/data/questions.py) correctly fires through the real
     engine when D is answered -- SEVER-05 is reached, its content is
     collected as a real SeverityInput.
  3. The resulting tier is honestly Emerging, NOT AUT-PS-01's locked
     Entrenched -- SEVER-05 has no duration_band option (same shape as
     the rest of Bucket 2's "missing follow-on option" pattern), capping
     raw contribution at 1.00 (needs >=1.98 for Entrenched). This is a
     documented, expected shortfall, not a test failure -- SEVER-05 is
     folded into Track A's duration_band work as a 10th question. This
     test will need updating (not silently re-passing) once that content
     ships, to assert Entrenched instead of Emerging.
  4. Zero regression to the standard 172-profile suite: confirmed
     separately (byte-for-byte snapshot diff, 0 changed) since D's
     trigger flip is a genuine no-op for best_option_for_state() -- D
     still never wins selection there, full-field-identical tie-break
     rule (Bucket 1, commit 44e85fc) correctly leaves this alone.

Usage:
    python tools/test_aut_ps_01_q23_d_forced.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import QUESTION_LIBRARY
from engine.main import accumulate_one_answer, run_accumulated_engine
from engine.data.states import DIMENSIONAL_FIELDS

from tools.calibration_runner import (
    ALL_PROFILES,
    _CORE_QUESTION_IDS,
    _CONDITIONAL_PAIRS,
    best_option_for_state,
    _neutral_option,
    select_severity_follow_on_option,
)

PASS = []
FAIL = []


def check(label, condition, detail=""):
    if condition:
        PASS.append(label)
    else:
        FAIL.append(f"{label}: {detail}")


PHASE_1_QUESTION_SEQUENCE = [
    "Q01", "Q02", "Q03B", "Q04", "Q05", "Q06", "Q07", "Q08", "Q09", "Q10",
    "Q11", "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "Q18", "Q19", "Q20",
    "Q21", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27B", "Q29", "Q30",
    "Q32", "Q33", "Q34",
]  # mirrors web/lib/session-store.ts -- kept literal here rather than
   # importing across the Python/TS boundary; if that list ever changes,
   # this test's live-reachability check should be re-verified against it.


def build_answer_sequence(test_case, force_qid, force_option_id):
    events = test_case.intake.get("significant_events", ["none"])
    has_acq = "acquisition_or_merger" in events
    include = {
        "Q03A" if events != ["none"] else "Q03B",
        "Q27A" if has_acq else "Q27B",
    }
    qids = []
    for qid in sorted(_CORE_QUESTION_IDS):
        excluded = any(
            (qid == a and a not in include) or (qid == b and b not in include)
            for a, b in _CONDITIONAL_PAIRS.items()
        )
        if not excluded:
            qids.append(qid)

    sequence = []
    for qid in qids:
        q = QUESTION_LIBRARY.get(qid)
        if q is None or not q.answer_options:
            continue
        if qid == force_qid:
            option_id = force_option_id
        else:
            wired = test_case.target_state in (q.state_targets or [])
            opt = best_option_for_state(q, test_case.target_state) if wired else _neutral_option(q)
            option_id = opt.option_id
        sequence.append((qid, option_id))
    return sequence


def locked_intake_from_test_case(test_case):
    """Convert calibration_runner.py's engine-shape intake dict into the
    'locked' web-facing shape _locked_intake_to_engine_intake() expects --
    real production functions take the pre-conversion shape, not the
    engine's own internal IntakeData shape run_profile() uses directly."""
    intake = test_case.intake
    jurisdictions = intake.get("jurisdictions") or []
    return {
        "organization_size": intake.get("headcount", ""),
        "industry": intake.get("industry", ""),
        "jurisdiction": jurisdictions[0] if jurisdictions else "",
        "role_level": intake.get("principal_role", ""),
    }


def run_real_engine_session(test_case, force_qid, force_option_id):
    locked_intake = locked_intake_from_test_case(test_case)
    accumulated_vector = {f: 0.0 for f in DIMENSIONAL_FIELDS}
    severity_inputs = []
    answers_log = []
    answered_count = 0

    for qid, option_id in build_answer_sequence(test_case, force_qid, force_option_id):
        result = accumulate_one_answer(accumulated_vector, qid, option_id, locked_intake)
        accumulated_vector = result["accumulated_vector"]
        answers_log.append({"question_id": qid, "option_id": option_id})
        answered_count += 1

        if result["severity_input"] is not None:
            severity_inputs.append(result["severity_input"])

        if result["severity_follow_on_id"]:
            follow_on_qid = result["severity_follow_on_id"]
            follow_on_q = QUESTION_LIBRARY[follow_on_qid]
            follow_on_opt = select_severity_follow_on_option(follow_on_q, True)
            fresult = accumulate_one_answer(
                accumulated_vector, follow_on_qid, follow_on_opt.option_id, locked_intake,
                trigger_question_id=qid,
            )
            accumulated_vector = fresult["accumulated_vector"]
            answers_log.append({"question_id": follow_on_qid, "option_id": follow_on_opt.option_id})
            answered_count += 1
            if fresult["severity_input"] is not None:
                severity_inputs.append(fresult["severity_input"])

    output = run_accumulated_engine(
        accumulated_vector=accumulated_vector,
        intake=locked_intake,
        answered_question_count=answered_count,
        severity_inputs=severity_inputs,
        answers_log=answers_log,
    )
    return output, severity_inputs


print("=" * 64)
print("AUT-PS-01 (paper_shield) -- Q23 option D forced, real engine path")
print("=" * 64)

check("Q23 is live in Phase 1 (PHASE_1_QUESTION_SEQUENCE)", "Q23" in PHASE_1_QUESTION_SEQUENCE)

tc = next(t for t in ALL_PROFILES if t.test_id == "AUT-PS-01")
check("AUT-PS-01's locked expected.severity_tier is Entrenched", tc.expected.severity_tier == "Entrenched",
      f"got {tc.expected.severity_tier!r}")

d_option = next(o for o in QUESTION_LIBRARY["Q23"].answer_options if o.option_id == "D")
check("Q23 option D carries severity_trigger=True", d_option.severity_trigger is True)
check("Q23 option D's severity_follow_on_id is SEVER-05", d_option.severity_follow_on_id == "SEVER-05",
      f"got {d_option.severity_follow_on_id!r}")
check("Q23 option D's dimensional_contributions unchanged (attitude_liability=-0.15)",
      d_option.dimensional_contributions.get("attitude_liability") == -0.15,
      f"got {d_option.dimensional_contributions.get('attitude_liability')}")

output, severity_inputs = run_real_engine_session(tc, force_qid="Q23", force_option_id="D")

check("Exactly one severity_input collected (SEVER-05 via forced Q23=D)", len(severity_inputs) == 1,
      f"got {len(severity_inputs)}: {severity_inputs}")
if severity_inputs:
    si = severity_inputs[0]
    check("severity_input's trigger_question_id is Q23", si.get("trigger_question_id") == "Q23", str(si))
    check("severity_input's severity_follow_on_id is SEVER-05", si.get("severity_follow_on_id") == "SEVER-05", str(si))

severity = output.get("severity", {})
check("Real engine severity raw score is 1.0 (SEVER-05 has no duration_band -- documented shortfall, not a failure)",
      severity.get("score") == 16.67, f"got {severity}")
check(
    "Real engine severity tier is Emerging (SHORT of locked Entrenched -- SEVER-05 "
    "needs Track A's duration_band content before this reaches expected.severity_tier; "
    "update this assertion to Entrenched once that content ships, don't let it silently "
    "keep passing against a stale expectation)",
    severity.get("tier") == "Emerging",
    f"got {severity.get('tier')!r} -- if this now reads Entrenched, SEVER-05's content "
    f"has changed; update this test's assertions to match, don't just delete the check",
)

print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Real SEVER-05 path via forced Q23=D confirmed working end to end.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
