"""
engine/main.py

Path B orchestrator. Accepts the web layer self-selection payload and
sequences the downstream pipeline: IntakeData -> StateRanking construction
-> SeverityEngine -> OutputEngine -> SessionData -> assemble_output.

AccumulationEngine and rank_states are bypassed. selectedStateIds are
the declared diagnosis. Synthetic score 1.0 satisfies StateRanking type
constraints and clears all alignment thresholds unconditionally.

Exceptions propagate. Error handling is the caller's responsibility (api/engine.py).
"""

from engine.accumulation import (
    IntakeData,
    StateRanking,
    AccumulationSession,
    accumulate_answer,
    rank_states,
)
from engine.severity import SeverityEngine
from engine.output import OutputEngine
from engine.contract import SessionData, assemble_output
from engine.data.states import STATE_PROFILES
from engine.data.questions import QUESTION_LIBRARY
from engine.data.salience import SALIENCE_PROFILES
from engine.output_synthesis import OutputSynthesisEngine
from engine.resolution_families import translate_resolution_family


def run_engine(
    payload: dict,
    narrative_response: str = "",
    signal_map_context: str = "",
) -> dict:
    """
    Accept web layer payload, return engine output contract dict.

    payload shape:
    {
        "selectedStateIds": ["state_id_1", "state_id_2", ...],
        "intake": {
            "headcount": str,
            "industry": str,
            "orgType": str,
            "jurisdictions": list[str],
            "significantEvents": list[str],
            "principalRole": str
        },
        "narrative_response":  str (optional),
        "signal_map_context":  str (optional)
    }
    """
    intake_dict = payload.get("intake", {})
    selected_ids = payload.get("selectedStateIds", [])

    # Web layer uses camelCase; IntakeData constructor uses snake_case
    intake_data = IntakeData(
        headcount=intake_dict["headcount"],
        industry=intake_dict["industry"],
        org_type=intake_dict["orgType"],
        jurisdictions=intake_dict["jurisdictions"],
        significant_events=intake_dict["significantEvents"],
        principal_role=intake_dict["principalRole"],
    )

    # Path B: selectedStateIds are the declared diagnosis.
    # Synthetic score 1.0 clears all alignment thresholds unconditionally.
    final_rankings = [
        StateRanking(rank=i + 1, state_id=state_id, distance=0.0, score=1.0)
        for i, state_id in enumerate(selected_ids)
    ]

    # Path B bypasses severity Q&A — no inputs produce Emerging tier at score 0
    severity_engine = SeverityEngine()
    severity_result = severity_engine.score()

    output_engine = OutputEngine()
    output_package = output_engine.build(final_rankings, severity_result)

    # Synthesis — anchored on first ranked state
    synthesis_result = None
    if final_rankings:
        lead_id = final_rankings[0].state_id
        lead_name = (
            STATE_PROFILES[lead_id].state_name
            if lead_id in STATE_PROFILES
            else lead_id
        )
        commercial_family = translate_resolution_family(
            output_package.private.resolution_family
            if output_package.private else ""
        )
        synthesis_result = OutputSynthesisEngine().synthesize(
            state_name=lead_name,
            severity_tier=severity_result.tier,
            resolution_family=commercial_family,
            asset_score=0.0,
            liability_score=0.0,
            narrative_response=narrative_response,
            intake=intake_dict,
            signal_map_context=signal_map_context,
        )

    session_data = SessionData(
        session_id=SessionData.new_session_id(),
        intake=intake_data,
        final_rankings=final_rankings,
        accumulated_vector={},
        output_package=output_package,
        severity_result=severity_result,
    )

    return assemble_output(session_data, synthesis_result=synthesis_result)


# ─────────────────────────────────────────────────────────────────────────────
# Path 1 — live sequential-question diagnostic (Session 71, Phase 1)
#
# Distinct from Path B above. Path 1 runs the real AccumulationEngine
# machinery against a session's actual answers, instead of Path B's
# synthetic score=1.0 declared-diagnosis shortcut. Phase 1 scope: linear
# Q01-Q34 core sequence only -- no checkpoints, no narrative modulation, no
# severity follow-ons. Full rationale: prompts/path1-phase1-handoff.md.
# ─────────────────────────────────────────────────────────────────────────────

def _locked_intake_to_engine_intake(intake: dict) -> IntakeData:
    """
    Adapts the locked canonical intake schema (Section 5 of the MOB:
    organization_size, industry, role_level, tenure_in_role, direct_reports,
    jurisdiction -- also web/lib/types.ts IntakeEcho) to the engine's
    IntakeData contract (headcount, industry, org_type, jurisdictions,
    significant_events, principal_role).

    Phase 1's intake form does not collect org_type or significant_events --
    neither has a locked-spec equivalent. Both default to values confirmed
    inert for Phase 1 (Session 71 architecture decision, confirmed with Pete
    before this build):
      - org_type defaults to "" -- the org_type_founder_led axis modifier
        (engine/accumulation.py _apply_axis_modifiers) only fires on the
        literal value "Founder-led", so any other string is a safe no-op.
      - significant_events defaults to ["none"] -- no PRIOR_ADJUSTER_INDEX
        entry matches "none" (a no-op for prior initialization, which is
        itself never consumed downstream by rank_states/severity/output --
        see AccumulationEngine.priors), and it means Q03A/Q27A conditional
        routing never fires in Phase 1 -- always the Q03B/Q27B "no
        significant event" branch (see web/lib/session-store.ts
        PHASE_1_QUESTION_SEQUENCE, which hardcodes this same assumption).

    tenure_in_role and direct_reports have no IntakeData equivalent at all --
    stored in the session for calibration/analytics purposes only (Task 1),
    never consumed by engine math.

    Revisit if a richer Phase 2+ intake form ever collects org_type or
    significant_events directly.
    """
    jurisdiction = intake.get("jurisdiction", "")
    return IntakeData(
        headcount=intake.get("organization_size", ""),
        industry=intake.get("industry", ""),
        org_type="",
        jurisdictions=[jurisdiction] if jurisdiction else [],
        significant_events=["none"],
        principal_role=intake.get("role_level", ""),
    )


def get_question_copy(question_id: str) -> dict:
    """
    Public-safe question copy for Path 1's frontend. Returns ONLY
    question_text and option_id/option_text pairs -- explicitly excludes
    dimensional_contributions, axis_targets, severity_trigger, and
    severity_follow_on_id. This is the runtime enforcement of the P-03
    boundary (scoring weight is invisible) for content actually rendered in
    the browser, not just an absence-by-construction of a duplicated
    dataset -- QUESTION_LIBRARY remains the single source of truth, nothing
    about question copy is ever hand-duplicated in TypeScript.

    Added beyond the Session 71 handoff's explicit task list -- necessary
    to implement Task 3's "session/start returns Q1's copy" and "session/
    answer returns next question" without duplicating question content in
    TypeScript (drift risk). Flagged in the Stage 3 dry-run.

    Raises KeyError on an unknown question_id -- the caller (api/engine.py)
    maps this to a 400.
    """
    question = QUESTION_LIBRARY.get(question_id)
    if question is None:
        raise KeyError(f"Unknown question_id: {question_id!r}")

    return {
        "question_id": question.question_id,
        "question_text": question.question_text,
        "options": [
            {"option_id": opt.option_id, "option_text": opt.option_text}
            for opt in question.answer_options
        ],
    }


def accumulate_one_answer(
    accumulated_vector: dict,
    question_id: str,
    option_id: str,
    intake: dict,
) -> dict:
    """
    Stateless per-answer accumulation step. Pure vector math -- no ranking,
    no severity, no checkpoint, no narrative modulation. The caller (Next.js
    route handler) supplies only question_id/option_id, never
    dimensional_contributions -- this function looks up the real
    AnswerOption server-side from QUESTION_LIBRARY. P-03 boundary: scoring
    weight is invisible, the browser never sees or sends it.

    Raises KeyError on an unknown question_id or option_id -- the caller
    (api/engine.py) maps this to a 400.
    """
    question = QUESTION_LIBRARY.get(question_id)
    if question is None:
        raise KeyError(f"Unknown question_id: {question_id!r}")

    option = next(
        (o for o in question.answer_options if o.option_id == option_id),
        None,
    )
    if option is None:
        raise KeyError(f"Unknown option_id {option_id!r} for question {question_id!r}")

    intake_data = _locked_intake_to_engine_intake(intake)
    session = AccumulationSession(accumulated_vector=dict(accumulated_vector))
    accumulate_answer(session, option, intake_data, question_id)
    return session.accumulated_vector


def run_accumulated_engine(
    accumulated_vector: dict,
    intake: dict,
    answered_question_count: int,
) -> dict:
    """
    Path 1 completion orchestrator ("Path A" -- real accumulation-based
    ranking, as opposed to Path B's declared-diagnosis shortcut above).
    Mirrors run_engine()'s downstream steps exactly (SeverityEngine ->
    OutputEngine -> assemble_output -> OutputSynthesisEngine) but ranks via
    the real rank_states() against the session's actual accumulated vector,
    instead of Path B's synthetic score=1.0 declared rankings. Same
    reference pattern as tools/calibration_runner.py's run_profile().

    Phase 1 has no narrative modulation and no severity follow-ons --
    narrative_response is always "" and SeverityEngine.score() is called
    with no accumulated severity inputs, exactly matching Path B's pattern
    for the same reason (no severity-triggering questions answered in
    Phase 1 scope).
    """
    intake_data = _locked_intake_to_engine_intake(intake)

    final_rankings = rank_states(accumulated_vector, answered_question_count, SALIENCE_PROFILES)

    severity_engine = SeverityEngine()
    severity_result = severity_engine.score()

    output_engine = OutputEngine()
    output_engine.set_noise_baseline()
    output_package = output_engine.build(final_rankings, severity_result)

    synthesis_result = None
    if final_rankings:
        lead_id = final_rankings[0].state_id
        lead_name = (
            STATE_PROFILES[lead_id].state_name
            if lead_id in STATE_PROFILES
            else lead_id
        )
        commercial_family = translate_resolution_family(
            output_package.private.resolution_family
            if output_package.private else ""
        )
        synthesis_result = OutputSynthesisEngine().synthesize(
            state_name=lead_name,
            severity_tier=severity_result.tier,
            resolution_family=commercial_family,
            asset_score=0.0,
            liability_score=0.0,
            narrative_response="",
            intake=intake,
            signal_map_context="",
        )

    session_data = SessionData(
        session_id=SessionData.new_session_id(),
        intake=intake_data,
        final_rankings=final_rankings,
        accumulated_vector=accumulated_vector,
        output_package=output_package,
        severity_result=severity_result,
    )

    return assemble_output(session_data, synthesis_result=synthesis_result)
