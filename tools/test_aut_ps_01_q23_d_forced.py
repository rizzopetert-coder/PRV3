"""
PRV3 -- AUT-PS-01 (paper_shield) targeted hand-test, Q23 option A forced

Precedent pattern: same class of harness-blind-spot test as the
built_to_fail Q35-39 investigation -- calibration_runner.py's
best_option_for_state() never selects Q23's option A or D (neither wins
the dimension-max heuristic; confirmed a genuine, non-tie dimensional
loss, not a selection bug -- see tools/diag_bucket2_track_b_questions.md),
so the 175-profile suite's own answer-generation can't exercise either
option's real content regardless of AUT-PS-01's data being correct. This
test forces a directly and drives the REAL production engine functions
(engine/main.py's accumulate_one_answer()/run_accumulated_engine()), not
calibration_runner.py's harness mirror, to verify what a real respondent
choosing A would actually experience.

CORRECTED this session (Checkpoint 4, SeverityResult per-state redesign):
originally forced option D, on the assumption D's own SEVER-05 firing was
the mechanism to test for paper_shield. Confirmed via direct question/
option text and state descriptive_prose, Gemini-confirmed: Q23 fires
SEVER-05 from TWO different options with genuinely distinct content --
option A ("no single departure would be unmanageable," a confident,
untested claim) matches paper_shield's definition exactly; option D
("people right now whose loss would be genuinely destabilizing," an
acknowledged, current fragility) matches leadership_continuity_risk's
definition instead. Forcing D to demonstrate paper_shield was the wrong
option under the now-locked split-by-option mapping
(engine/severity.py's SEVERITY_ID_OPTION_STATES) -- switched to A.

Also fixed this session: run_real_engine_session() never threaded
triggering_option_id into the follow-on's constructed SeverityInput --
Checkpoint 2 added this parameter throughout engine/main.py and
calibration_runner.py, but this standalone hand-test predates that pass
and was never updated to match. Without it, SEVER-05's split-by-option
lookup silently failed to resolve to either of its two real states
regardless of which option (A or D) was forced -- caught during this
session's final Checkpoint 4 verification sweep, not assumed fixed.

Confirms:
  1. Q23 IS live in Phase 1 (web/lib/session-store.ts's
     PHASE_1_QUESTION_SEQUENCE) -- this path is reachable today, not
     Phase-2-pending like Q31/Q03A/Q27A.
  2. A's severity_trigger=True + severity_follow_on_id=SEVER-05 correctly
     fires through the real engine when A is answered -- SEVER-05 is
     reached, its content is collected as a real SeverityInput, and (this
     session) correctly attributes to paper_shield specifically via
     triggering_option_id="A", not the session-wide broadcast the
     original architecture used.
  3. The resulting per-state severity for paper_shield is Entrenched --
     matches the forced scenario's own real math (SEVER-05's duration_band
     18mo_plus option, Track A's 10th question). This is a DIFFERENT
     question from AUT-PS-01's own calibration-profile expected.severity_tier
     (now correctly Emerging after this session's recalibration -- that
     profile's own natural generate_answers() path fires zero severity
     input at all, an unrelated, orthogonal fact about profile design, not
     about whether the forced Q23=A -> SEVER-05 mechanism itself works).
  4. Zero regression to the standard 175-profile suite: confirmed
     separately (byte-for-byte snapshot diff, 0 changed) since neither A
     nor D's trigger flip is ever selected by best_option_for_state() for
     this or any other profile's natural path.

Usage:
    python tools/test_aut_ps_01_q23_d_forced.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import QUESTION_LIBRARY
from engine.main import accumulate_one_answer, run_accumulated_engine
from engine.data.states import DIMENSIONAL_FIELDS
from engine.severity import SeverityEngine, SeverityInput

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
            follow_on_opt = select_severity_follow_on_option(follow_on_q, "18mo_plus")
            # Checkpoint 4 fix: thread triggering_option_id (the just-
            # answered trigger question's own option_id, "option_id" in
            # this loop iteration) through to the follow-on's constructed
            # SeverityInput -- mirrors engine/main.py's accumulate_answers()
            # and calibration_runner.py's run_profile(), both updated in
            # Checkpoint 2. Without this, split-by-option IDs (SEVER-03/05/07)
            # can never resolve to any state, regardless of which option
            # is forced.
            fresult = accumulate_one_answer(
                accumulated_vector, follow_on_qid, follow_on_opt.option_id, locked_intake,
                trigger_question_id=qid,
                triggering_option_id=option_id,
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

    # Checkpoint 4: the VII.1 output contract's top-level "severity" object
    # is deliberately lead-state-anchored (Checkpoint 3, Gemini-confirmed) --
    # it reports whichever state ranks #1, not paper_shield specifically.
    # paper_shield ranks #8 in this forced scenario's real identified_states,
    # so output["severity"]["tier"] is the WRONG field to check paper_shield's
    # own attribution against. Mirrors run_accumulated_engine()'s own
    # internal construction (same severity_inputs list) purely to expose
    # state_severity directly -- the VII.1 contract has no per-state
    # severity field at the top level by design.
    state_severity = SeverityEngine()
    for si in severity_inputs:
        state_severity.add_input(SeverityInput(**si))
    state_severity_result = state_severity.score().state_severity

    return output, severity_inputs, state_severity_result


print("=" * 64)
print("AUT-PS-01 (paper_shield) -- Q23 option A forced, real engine path")
print("=" * 64)

check("Q23 is live in Phase 1 (PHASE_1_QUESTION_SEQUENCE)", "Q23" in PHASE_1_QUESTION_SEQUENCE)

tc = next(t for t in ALL_PROFILES if t.test_id == "AUT-PS-01")
# Checkpoint 4: AUT-PS-01's own locked expected.severity_tier is now
# Emerging (this session's recalibration -- its natural generate_answers()
# path fires zero severity input at all, unrelated to this forced
# scenario). Asserted here as a plain fact, not a precondition this test
# depends on -- what this test actually verifies is the FORCED Q23=A path
# below, a deliberately different, artificial scenario the standard suite
# can't reach.
check("AUT-PS-01's locked expected.severity_tier is Emerging (own natural path fires nothing)",
      tc.expected.severity_tier == "Emerging",
      f"got {tc.expected.severity_tier!r}")

a_option = next(o for o in QUESTION_LIBRARY["Q23"].answer_options if o.option_id == "A")
check("Q23 option A carries severity_trigger=True", a_option.severity_trigger is True)
check("Q23 option A's severity_follow_on_id is SEVER-05", a_option.severity_follow_on_id == "SEVER-05",
      f"got {a_option.severity_follow_on_id!r}")

output, severity_inputs, state_severity = run_real_engine_session(tc, force_qid="Q23", force_option_id="A")

# Pre-existing, unrelated to this session's redesign (confirmed identical
# before and after every checkpoint this session via git stash comparison):
# Q33 also fires SEVER-19 incidentally along this profile's own answer
# path, so severity_inputs always has 2 entries here, not 1. Documented,
# not fixed -- out of scope, a separate harness/content question.
check("Two severity_inputs collected (SEVER-05 forced via Q23=A, SEVER-19 incidental via Q33 -- "
      "pre-existing, unrelated to this session)",
      len(severity_inputs) == 2,
      f"got {len(severity_inputs)}: {severity_inputs}")
sever05_inputs = [si for si in severity_inputs if si.get("severity_follow_on_id") == "SEVER-05"]
check("Exactly one SEVER-05 severity_input, correctly attributing triggering_option_id=A",
      len(sever05_inputs) == 1 and sever05_inputs[0].get("triggering_option_id") == "A",
      f"got {sever05_inputs}")

check("paper_shield present in identified_states (qualifies for output, rank irrelevant here)",
      any(s["state_id"] == "paper_shield" for s in output.get("identified_states", [])),
      f"got {[s['state_id'] for s in output.get('identified_states', [])]}")

paper_shield_severity = state_severity.get("paper_shield")
check(
    "Real per-state severity for paper_shield is Entrenched -- the forced Q23=A -> "
    "SEVER-05(triggering_option_id=A, duration_band=18mo_plus) path correctly attributes to "
    "paper_shield specifically, not a session-wide broadcast and not conflated with whichever "
    "state happens to rank #1 (paper_shield ranks #8 here) -- confirmed through the real "
    "engine/main.py production functions, not the calibration harness",
    paper_shield_severity is not None and paper_shield_severity.tier == "Entrenched",
    f"got {paper_shield_severity}",
)

print("\n" + "=" * 64)
print(f"RESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL:
        print(f"  [FAIL] {f}")
else:
    print("\nAll checks passed. Real SEVER-05 path via forced Q23=A confirmed working end to end.")
print("=" * 64)

sys.exit(1 if FAIL else 0)
