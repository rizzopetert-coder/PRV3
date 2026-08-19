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

from typing import Optional
from dataclasses import asdict

from engine.accumulation import (
    IntakeData,
    StateRanking,
    AccumulationSession,
    accumulate_answer,
    rank_states,
    compute_trajectory,
)
from engine.severity import SeverityEngine, SeverityInput
from engine.output import OutputEngine
from engine.contract import SessionData, assemble_output, _compute_asset_score, _compute_liability_score
from engine.checkpoint import evaluate_checkpoint, checkpoint_result_from_wire
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.questions import QUESTION_LIBRARY
from engine.data.salience import SALIENCE_PROFILES
from engine.output_synthesis import OutputSynthesisEngine, SynthesisResult
from engine.resolution_families import translate_resolution_family
from engine.data.fallback_synthesis import get_fallback_synthesis


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
        # A1 -- optional, .get() not bracket access: this camelCase
        # payload shape predates the field and Path B's UI doesn't
        # collect it, so no existing caller sends it.
        significant_event_elaboration=intake_dict.get("significantEventElaboration", ""),
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
        # Checkpoint 3: lead_id's own attributed tier, not the pooled
        # session-wide value. Path B never collects real severity inputs
        # ("Path B bypasses severity Q&A" above) -- state_severity is
        # always {} here, so this resolves to "Emerging" unconditionally
        # today, same as before. Changed anyway for consistency with every
        # other severity_tier consumer in this file, not because it fixes
        # a live Path B bug. Explicit get-then-unwrap -- state_severity's
        # values are StateSeverity objects (Checkpoint 1 follow-on), not
        # bare strings.
        _lead_severity_entry = severity_result.state_severity.get(lead_id)
        lead_severity_tier = (
            _lead_severity_entry.tier if _lead_severity_entry is not None else "Emerging"
        )
        synthesis_result = OutputSynthesisEngine().synthesize(
            state_name=lead_name,
            severity_tier=lead_severity_tier,
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
    jurisdiction, significant_events -- also web/lib/types.ts IntakeEcho) to
    the engine's IntakeData contract (headcount, industry, org_type,
    jurisdictions, significant_events, principal_role).

    significant_events is now collected directly by the intake form
    (web/components/DiagnosticFlow.tsx's checkbox multi-select, validated
    server-side against the 9 canonical PRIOR_ADJUSTER_INDEX keys in
    validateIntake()) and passed through here. This session's Mechanism 1
    deprecation (Decision Register) means it no longer drives any scoring
    math -- initialize_priors() (engine/accumulation.py) is now an
    unconditional flat baseline -- but it IS now real, user-submitted
    synthesis-only narrative metadata rather than a hardcoded ["none"]
    default. Falls back to ["none"] only if the field is absent or empty
    (defensive -- the validated web path always sends a non-empty list, but
    this adapter has no way to enforce that on its own callers).

    org_type has no locked-spec intake equivalent -- unrelated to
    significant_events, unchanged: still defaults to "" (Session 71
    architecture decision) -- the org_type_founder_led axis modifier only
    fires on the literal value "Founder-led", so any other string
    (including "") is a safe no-op.

    tenure_in_role and direct_reports have no IntakeData equivalent at all --
    stored in the session for calibration/analytics purposes only (Task 1),
    never consumed by engine math.
    """
    jurisdiction = intake.get("jurisdiction", "")
    return IntakeData(
        headcount=intake.get("organization_size", ""),
        industry=intake.get("industry", ""),
        org_type="",
        jurisdictions=[jurisdiction] if jurisdiction else [],
        significant_events=intake.get("significant_events") or ["none"],
        principal_role=intake.get("role_level", ""),
        # A1 -- free-text elaboration, present only when "other" was
        # selected in the checkbox multi-select (validated server-side
        # in validateIntake(), required non-empty when "other" is
        # selected).
        significant_event_elaboration=intake.get("significant_event_elaboration", ""),
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
        # format ("forced_choice" | "weighted_multi_select") -- A.2, this
        # session. Not scoring-sensitive (a UI rendering hint, not
        # dimensional_contributions/axis_targets/severity_trigger/
        # severity_follow_on_id), safe to include -- P-03 boundary
        # unaffected.
        "format": question.format,
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
    trigger_question_id: str = "",
    triggering_option_id: str = "",
) -> dict:
    """
    Stateless per-answer accumulation step. Pure vector math -- no ranking,
    no checkpoint, no narrative modulation. The caller (Next.js route
    handler) supplies only question_id/option_id, never
    dimensional_contributions -- this function looks up the real
    AnswerOption server-side from QUESTION_LIBRARY. P-03 boundary: scoring
    weight is invisible, the browser never sees or sends it.

    Severity follow-on wiring (Path 1 only): when the answered option
    carries AnswerOption.severity_input_mapping (populated only on
    SEVER-01..13 follow-on options -- see engine/data/questions.py's
    _severity_input_tags), constructs a SeverityInput-shaped dict for the
    caller to accumulate across the session and pass into
    run_accumulated_engine()'s severity_inputs parameter at completion.
    None for every other question, including core Q01-Q34 questions
    themselves -- their own severity_trigger only signals that a follow-on
    should be presented next; the actual SeverityInput values come from the
    follow-on's own answer, not the triggering question's answer.

    trigger_question_id: the core question whose answer caused this
    follow-on to be presented (known only by the caller, which decided to
    splice the follow-on in). Defaults to question_id itself (the
    follow-on's own ID) when not supplied -- a documented simplification,
    not true provenance, when the real trigger context isn't threaded
    through. Ignored entirely when this question has no
    severity_input_mapping.

    triggering_option_id (Checkpoint 2, SeverityResult per-state
    redesign): which option of trigger_question_id was selected --
    required only for follow-ons whose intended state depends on which
    option fired (SEVER-03, SEVER-07 today, per SEVERITY_ID_OPTION_STATES
    in engine/severity.py). Threaded into the constructed severity_input
    dict as "triggering_option_id" (None when not supplied). Same
    "known only by the caller" caveat as trigger_question_id above --
    this function has no way to derive it independently.

    severity_follow_on_id (return value): the OPPOSITE direction from
    severity_input above -- when the just-answered option itself carries
    severity_trigger=True (a core question option, e.g. Q22-D), this
    surfaces its severity_follow_on_id (e.g. "SEVER-04") so the caller
    knows to splice that follow-on question into the live sequence next,
    mirroring how checkpoint distinguisher IDs are already surfaced as
    bare strings (P-03 safe -- a routing ID, not a scoring weight). None
    whenever the answered option doesn't trigger a follow-on, including
    every SEVER-01..13 option itself (those never carry their own
    severity_trigger -- confirmed in engine/data/questions.py's _QDATA).

    KNOWN CALLER IMPACT, applied this pass: this function's return shape
    changed from a bare accumulated_vector dict to {"accumulated_vector":
    dict, "severity_input": dict | None, "severity_follow_on_id": str |
    None}. api/engine.py's /api/accumulate route and the Next.js caller
    have been updated to match (see api/engine.py, web/lib/engine-client.ts,
    web/lib/session-store.ts, web/app/api/diagnostic/session/answer/route.ts).

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

    severity_input = None
    if option.severity_input_mapping:
        severity_input = {
            "trigger_question_id": trigger_question_id or question_id,
            "severity_follow_on_id": question_id,
            **option.severity_input_mapping,
        }
        # Omitted (not set to None) when absent -- preserves the old dict
        # shape byte-for-byte for every non-split-option mapping, matches
        # SeverityInputPayload's optional-field convention on the wire,
        # and SeverityInput(**severity_input) fills its own
        # Optional[str] = None default either way.
        if triggering_option_id:
            severity_input["triggering_option_id"] = triggering_option_id

    severity_follow_on_id = option.severity_follow_on_id if option.severity_trigger else None

    return {
        "accumulated_vector": session.accumulated_vector,
        "severity_input": severity_input,
        "severity_follow_on_id": severity_follow_on_id,
    }


def accumulate_answers(
    accumulated_vector: dict,
    question_id: str,
    option_ids: list,
    intake: dict,
    trigger_question_id: str = "",
    triggering_option_id: str = "",
) -> dict:
    """
    Multi-option wrapper around accumulate_one_answer() -- A.2 (Q06
    multi-select), this session. Loops accumulate_one_answer() once per
    selected option_id, threading accumulated_vector through
    sequentially (each call's output feeds the next call's input) --
    exactly the stateless-per-option contract accumulate_one_answer()
    already guarantees. That function itself is UNCHANGED; this is a
    second caller, not a modification, per its own docstring's "KNOWN
    CALLER IMPACT" convention.

    Every existing single-select caller now sends a 1-element list --
    this function's behavior for len(option_ids) == 1 is byte-for-byte
    identical to calling accumulate_one_answer() directly once, so it
    fully replaces the old single-option call path everywhere (one code
    path, not a dual branch).

    Aggregates severity_input/severity_follow_on_id across every
    selected option into lists (plural) rather than a single optional
    value -- confirmed necessary, not hypothetical: Q06's own A option
    (severity_trigger=True -> SEVER-27) and D option
    (severity_trigger=True -> SEVER-21) mean a real multi-select answer
    selecting both can legitimately fire two severity follow-ons from
    one submission.

    triggering_option_id (Checkpoint 2): threaded uniformly into every
    accumulate_one_answer() call in the loop below, same as
    trigger_question_id already is -- both describe the ORIGIN question/
    option of whichever follow-on is currently being answered, not a
    per-selected-option value, so one value applies to the whole call.

    severity_follow_on_origins (return value, Checkpoint 2): maps each
    entry in severity_follow_on_ids to the option_id (within THIS call's
    option_ids) that produced it. Not strictly required for any
    currently-locked mapping (SEVER-03/07's real parents, Q21/Q25, are
    both format="forced_choice" -- option_ids is always 1 element for
    them), but removes a latent correctness trap for any future
    multi-select trigger question whose fired follow-ons need
    split-by-option attribution -- Q06 already proves multi-select
    triggers exist live (A -> SEVER-27, D -> SEVER-21).

    Raises KeyError (same as accumulate_one_answer(), same caller
    handling in api/engine.py) if option_ids is empty or any entry is
    invalid for question_id.
    """
    if not option_ids:
        raise KeyError(f"option_ids must be non-empty for question {question_id!r}")

    vector = dict(accumulated_vector)
    severity_inputs = []
    severity_follow_on_ids = []
    severity_follow_on_origins = {}
    for option_id in option_ids:
        step = accumulate_one_answer(
            vector, question_id, option_id, intake,
            trigger_question_id, triggering_option_id,
        )
        vector = step["accumulated_vector"]
        if step["severity_input"] is not None:
            severity_inputs.append(step["severity_input"])
        if step["severity_follow_on_id"] is not None:
            severity_follow_on_ids.append(step["severity_follow_on_id"])
            severity_follow_on_origins[step["severity_follow_on_id"]] = option_id

    return {
        "accumulated_vector": vector,
        "severity_inputs": severity_inputs,
        "severity_follow_on_ids": severity_follow_on_ids,
        "severity_follow_on_origins": severity_follow_on_origins,
    }


def run_checkpoint(
    checkpoint_position: str,
    accumulated_vector: dict,
    answered_question_count: int,
    already_asked: list,
) -> dict:
    """
    Path 1 checkpoint evaluation (Phase 2). Ranks the session's current
    accumulated vector via rank_states() -- the same call
    run_accumulated_engine() makes at completion, same
    answered_question_count-scaled centroid displacement -- then evaluates
    the named checkpoint via engine.checkpoint.evaluate_checkpoint(). No
    orchestration logic duplicated here; this is a thin wire-shape adapter
    over both, consistent with accumulate_one_answer() and
    get_question_copy() above.

    answered_question_count MUST be the session's true live answer count
    at the moment this checkpoint fires (session.answers_log.length on the
    caller side), not derived from checkpoint_position -- a session that
    has already had an earlier checkpoint splice distinguisher questions in
    will have answered more than 11/19/27 questions by the time a later
    checkpoint position is reached, and rank_states()'s centroid
    displacement scales directly off this count.

    Returns only the fields CheckpointResultPayload (web/lib/engine-client.ts)
    needs: entropy, threshold, fires, distinguishers (question_id strings,
    not QuestionDefinition objects -- P-03 boundary, same treatment as
    get_question_copy()), top_cluster. narrative_trigger and trigger_path
    are Section III.3 / Phase 3 concerns, out of Phase 2 scope, not
    returned here.

    Raises ValueError on an invalid checkpoint_position -- the caller
    (api/engine.py) maps this to a 400.
    """
    rankings = rank_states(accumulated_vector, answered_question_count, SALIENCE_PROFILES)
    result = evaluate_checkpoint(checkpoint_position, rankings, already_asked)

    return {
        "entropy": result.entropy,
        "threshold": result.threshold,
        "fires": result.fires,
        "distinguishers": [q.question_id for q in result.distinguishers],
        "top_cluster": result.top_cluster,
    }


def _build_signal_map_context(
    answers_log: list,
    intake_data: IntakeData,
    winning_state_id: Optional[str],
) -> str:
    """
    Rank every answered core-question option by its resolved contribution's
    salience-weighted dot product against the winning state's profile
    (SALIENCE_PROFILES[winning_state_id]), then walk down the ranking and
    join the first 5-7 options that carry authored AnswerOption.
    observation_text. Skip-and-backfill: an unauthored option is skipped
    outright, never padded with a fallback (no raw option_text, no
    axis-level canned phrasing) -- Session decision, see MOB.

    Each option's REAL resolved per-answer contribution is obtained by
    replaying accumulate_answer() against a scratch, zero-initialized
    AccumulationSession rather than reading
    AnswerOption.dimensional_contributions directly. This is required for
    correctness, not just consistency: options like Q18-E carry an
    intake-conditioned _conditional contribution
    (is_high_hazard-gated, resolved via _apply_axis_modifiers() inside
    accumulate_answer()) with no single static value to read. Reusing
    accumulate_answer() wholesale means this ranking can never drift from
    what the same answer actually contributed to the live session's
    accumulated_vector.

    Returns "" when answers_log is empty, winning_state_id has no salience
    profile, or zero ranked options carry authored observation_text yet
    (the expected state until the copywriting pass populates entries --
    synthesize() treats "" as "omit signal_map_context from the prompt
    entirely", not an error).
    """
    salience = SALIENCE_PROFILES.get(winning_state_id) if winning_state_id else None
    if not answers_log or not salience:
        return ""

    scored: list = []
    for entry in answers_log:
        question_id = entry.get("question_id") if isinstance(entry, dict) else None
        option_id = entry.get("option_id") if isinstance(entry, dict) else None
        question = QUESTION_LIBRARY.get(question_id)
        if question is None:
            continue
        option = next(
            (o for o in question.answer_options if o.option_id == option_id),
            None,
        )
        if option is None:
            continue

        scratch = AccumulationSession()
        accumulate_answer(scratch, option, intake_data, question_id)
        contribution = scratch.accumulated_vector

        weight = sum(
            contribution.get(f, 0.0) * salience.get(f, 0.0)
            for f in DIMENSIONAL_FIELDS
        )
        scored.append((weight, option))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    observations: list = []
    for _, option in scored:
        if option.observation_text:
            observations.append(option.observation_text)
        if len(observations) == 7:
            break

    return " ".join(observations)


# Need >=2 real answers per half for a split to mean anything --
# structural correctness guard, not an empirical calibration constant.
MIN_ANSWERS_FOR_TRAJECTORY: int = 4


def _replay_partial_vector(answers_log_slice: list, intake_data: IntakeData) -> dict:
    """
    Replay a slice of answers_log through ONE shared scratch
    AccumulationSession to get the real accumulated vector for just that
    slice. Reuses the same accumulate_answer()-against-a-scratch-session
    technique _build_signal_map_context() uses above, applied differently:
    one shared scratch session per slice (cumulative across the whole
    slice), not a fresh scratch per individual answer (which is what
    _build_signal_map_context() needs to isolate each answer's own
    contribution in isolation). Duplicated rather than extracted into a
    shared helper -- same precedent as the STATE_RESOLUTION_FAMILY
    triplication elsewhere in this codebase, per the standing rule
    against refactoring adjacent code mid-build.
    """
    scratch = AccumulationSession()
    for entry in answers_log_slice:
        question_id = entry.get("question_id") if isinstance(entry, dict) else None
        option_id = entry.get("option_id") if isinstance(entry, dict) else None
        question = QUESTION_LIBRARY.get(question_id)
        if question is None:
            continue
        option = next(
            (o for o in question.answer_options if o.option_id == option_id),
            None,
        )
        if option is None:
            continue
        accumulate_answer(scratch, option, intake_data, question_id)
    return scratch.accumulated_vector


def _compute_trajectory_context(
    answers_log: list,
    intake_data: IntakeData,
    duration_band: Optional[str],
) -> dict:
    """
    Split answers_log by position (first half vs. second half of the
    answered sequence) and diff the two halves' independently-replayed
    vectors via compute_trajectory(). Below MIN_ANSWERS_FOR_TRAJECTORY,
    returns the defined "insufficient_data" default rather than a
    degenerate/misleading delta -- same convention as
    compute_causation_pattern()'s "insufficient_signal" and
    compute_cascade_risk()'s 0.0-on-no-signal. duration_band is still
    passed through even in this case -- it is independently real data,
    unrelated to whether the intra-session split was viable.
    """
    if len(answers_log) < MIN_ANSWERS_FOR_TRAJECTORY:
        return {
            "delta": 0.0,
            "dispersion_delta": 0.0,
            "direction": "insufficient_data",
            "duration_band": duration_band,
        }

    midpoint = len(answers_log) // 2
    early_vector = _replay_partial_vector(answers_log[:midpoint], intake_data)
    late_vector = _replay_partial_vector(answers_log[midpoint:], intake_data)

    return compute_trajectory(early_vector, late_vector, duration_band)


def run_accumulated_engine(
    accumulated_vector: dict,
    intake: dict,
    answered_question_count: int,
    checkpoint_results: Optional[dict] = None,
    severity_inputs: Optional[list] = None,
    answers_log: Optional[list] = None,
) -> dict:
    """
    Path 1 completion orchestrator ("Path A" -- real accumulation-based
    ranking, as opposed to Path B's declared-diagnosis shortcut above).
    Mirrors run_engine()'s downstream steps exactly (SeverityEngine ->
    OutputEngine -> assemble_output -> OutputSynthesisEngine) but ranks via
    the real rank_states() against the session's actual accumulated vector,
    instead of Path B's synthetic score=1.0 declared rankings. Same
    reference pattern as tools/calibration_runner.py's run_profile().

    Phase 1 has no narrative modulation -- narrative_response is always "".

    Severity follow-on wiring (Path 1 only): severity_inputs is an optional
    list of dicts, each shaped like accumulate_one_answer()'s
    severity_input return value (trigger_question_id,
    severity_follow_on_id, plus whichever of duration_band/population_band/
    prior_failed_resolution/financial_indicators/named_condition that
    follow-on's answer set). Each is constructed into a real SeverityInput
    and passed to SeverityEngine.add_input() before scoring -- the first
    time severity.tier can vary from the "Emerging" constant in this
    project's history. None or [] (the default) preserves the original
    zero-input behavior exactly, so this remains backward compatible with
    any caller not yet collecting real severity inputs -- including Path B,
    which is untouched and stays permanently "Emerging" by design.

    checkpoint_results (Phase 2): optional dict keyed "q11"/"q19"/"q27",
    each value either None (that checkpoint was never reached this
    session -- completion before Q27 is possible, e.g.) or a wire-shaped
    dict matching run_checkpoint()'s return shape. Threaded into
    SessionData.checkpoint_q11/19/27 via checkpoint_result_from_wire() so
    checkpoint_log in the assembled output reflects what actually happened
    live during the session, instead of the None defaults every session
    fell through to before this parameter existed.

    answers_log (Path 1 only): optional list of {"question_id": str,
    "option_id": str} dicts, mirroring web/lib/session-store.ts's
    AnswerLogEntry -- the session's full answer history. None or [] (the
    default) preserves prior behavior exactly (empty signal_map_context).
    Used only to build signal_map_context via _build_signal_map_context()
    below; not accumulated again here (accumulated_vector already reflects
    every answer by the time this function is called).

    asset_score / liability_score: computed here, before synthesize(), via
    _compute_asset_score()/_compute_liability_score() -- previously
    hardcoded 0.0 at this call site even though accumulated_vector already
    held the real signal needed to compute them (assemble_output() below
    recomputes asset_score independently for the VII.1 contract; this is a
    second, earlier call for synthesis's benefit, not a dependency between
    the two).
    """
    intake_data = _locked_intake_to_engine_intake(intake)

    final_rankings = rank_states(accumulated_vector, answered_question_count, SALIENCE_PROFILES)

    severity_engine = SeverityEngine()
    for severity_input in (severity_inputs or []):
        severity_engine.add_input(SeverityInput(**severity_input))
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
        asset_obj = _compute_asset_score(accumulated_vector, lead_id)
        liability_obj = _compute_liability_score(accumulated_vector, lead_id)
        signal_map_context = _build_signal_map_context(
            answers_log or [], intake_data, lead_id
        )
        # Checkpoint 3: lead_id's own attributed tier -- this is the real,
        # live fix. Path 1's full diagnostic collects real severity
        # inputs, so state_severity can genuinely differ from the old
        # pooled sev.tier here, unlike Path B/Category D. Explicit
        # get-then-unwrap, same reasoning as the Path B site above.
        _lead_severity_entry = severity_result.state_severity.get(lead_id)
        lead_severity_tier = (
            _lead_severity_entry.tier if _lead_severity_entry is not None else "Emerging"
        )
        synthesis_result = OutputSynthesisEngine().synthesize(
            state_name=lead_name,
            severity_tier=lead_severity_tier,
            resolution_family=commercial_family,
            asset_score=asset_obj["score"],
            liability_score=liability_obj["score"],
            narrative_response="",
            intake=intake,
            signal_map_context=signal_map_context,
        )

    duration_band = next(
        (si.get("duration_band") for si in (severity_inputs or []) if si.get("duration_band")),
        None,
    )
    trajectory_result = _compute_trajectory_context(answers_log or [], intake_data, duration_band)

    checkpoint_results = checkpoint_results or {}
    session_data = SessionData(
        session_id=SessionData.new_session_id(),
        intake=intake_data,
        final_rankings=final_rankings,
        accumulated_vector=accumulated_vector,
        output_package=output_package,
        severity_result=severity_result,
        checkpoint_q11=checkpoint_result_from_wire("Q11", checkpoint_results.get("q11")),
        checkpoint_q19=checkpoint_result_from_wire("Q19", checkpoint_results.get("q19")),
        checkpoint_q27=checkpoint_result_from_wire("Q27", checkpoint_results.get("q27")),
    )

    return assemble_output(session_data, synthesis_result=synthesis_result, trajectory_result=trajectory_result)


def run_condensed_engine(
    accumulated_vector: dict,
    answered_question_count: int,
) -> dict:
    """
    Category D (free condensed diagnostic) completion orchestrator, this
    session. Deliberately does NOT call assemble_output() -- that function
    builds the full VII.1 contract, which has a hard dependency Category
    D's industry-only intake can't satisfy: compute_friction_tax() requires
    a numeric session.intake.headcount and crashes on the empty-string
    default (confirmed via a real end-to-end run during this session's own
    verification pass, not assumed safe). assemble_output() also computes
    several other full-diagnostic-only fields (narrative_modulation,
    jurisdiction_flags, causation_pattern, urgency_window, legal exposure)
    Category D has no use for. This returns a smaller, self-contained dict
    with only what CondensedOutputPayload (web/lib/types.ts) actually
    needs.

    identified_states construction mirrors assemble_output()'s own logic
    exactly (engine/contract.py, routing.mode == "single"/"multi" branches)
    so the two stay consistent if that logic ever changes.

    No intake parameter -- unlike run_accumulated_engine(), nothing in
    this function's own logic (rank_states, SeverityEngine, OutputEngine,
    get_fallback_synthesis) consumes it; accumulated_vector already
    reflects every intake-conditioned adjustment made during accumulation
    (signal reliability, axis modifiers). The industry value is used
    separately, by the caller (api/engine.py's /api/condensed-complete
    route), only for get_industry_wage() -- unrelated to this function.

    No checkpoints, no severity follow-ons, no trajectory context --
    Category D's condensed session never collects any of these inputs by
    design (web/lib/condensed-session-store.ts never reads
    severity_follow_on_id/severity_input from /api/accumulate's
    response). severity_result is therefore always "Emerging" --
    SeverityEngine with zero inputs, same behavior as Path B, not a bug
    introduced here.

    asset_score/liability_score/signal_map_context are intentionally not
    computed here -- they exist solely to feed the real synthesis
    prompt, which this function never calls.
    """
    final_rankings = rank_states(accumulated_vector, answered_question_count, SALIENCE_PROFILES)

    severity_result = SeverityEngine().score()

    output_engine = OutputEngine()
    output_engine.set_noise_baseline()
    output_package = output_engine.build(final_rankings, severity_result)
    routing = output_package.routing

    identified_states = []
    if routing.mode == "single" and routing.lead_state:
        identified_states = [{
            "state_id": routing.lead_state.state_id,
            "state_name": routing.lead_state.state_name,
            "score": round(routing.lead_state.score, 6),
            "descriptive_prose": STATE_PROFILES[routing.lead_state.state_id].descriptive_prose
                if routing.lead_state.state_id in STATE_PROFILES else "",
        }]
    elif routing.mode == "multi":
        identified_states = [
            {
                "state_id": qs.state_id,
                "state_name": qs.state_name,
                "score": round(qs.score, 6),
                "descriptive_prose": STATE_PROFILES[qs.state_id].descriptive_prose
                    if qs.state_id in STATE_PROFILES else "",
            }
            for qs in routing.qualified_states
        ]

    # Deliberately NOT output_package.private.resolution_family -- that field
    # is only ever populated in single-state routing mode (engine/output.py's
    # own OutputPackage docstring), which leaves it "" in multi-state mode --
    # the empirically common case (Direction 3's own real-data investigation
    # found ~100% of real high_confidence profiles land multi-state). An
    # empty resolution_family cascades into get_fallback_synthesis() finding
    # no match and returning the fully generic entry -- confirmed via a real
    # production reproduction this session, not assumed. Fixed by reading
    # resolution_family from the lead QualifiedState directly instead --
    # confirmed same provenance as output_package.private.resolution_family
    # would have had (engine/output.py: QualifiedState.resolution_family is
    # populated from STATE_PROFILES[state_id].resolution_family for every
    # ranked state unconditionally, and build_private_block() does nothing
    # but copy qualified_state.resolution_family through verbatim) -- not a
    # separately-maintained field that could drift, the exact same value,
    # just read through a path that also works in multi-state mode.
    if routing.mode == "single" and routing.lead_state:
        resolution_routing = routing.lead_state.resolution_family
    elif routing.mode == "multi" and routing.qualified_states:
        resolution_routing = routing.qualified_states[0].resolution_family
    else:
        resolution_routing = ""

    synthesis_result = None
    if identified_states:
        commercial_family = translate_resolution_family(resolution_routing)
        # Checkpoint 3: resolve per-state, same identified_states[0]
        # state_id already used for resolution_routing above (same
        # single/multi provenance split). Provable no-op today (this
        # function's own docstring: Category D never collects severity
        # inputs, severity_result.state_severity is always {} here, so
        # this already always resolved to "Emerging" either way) --
        # changed for consistency with every other get_fallback_synthesis()/
        # synthesize() call site in this file, and to remove a latent
        # trap if Category D's design ever changes to collect real
        # severity inputs later. Explicit get-then-unwrap, same reasoning
        # as every other site in this file.
        lead_state_id = identified_states[0]["state_id"]
        _lead_severity_entry = severity_result.state_severity.get(lead_state_id)
        lead_severity_tier = (
            _lead_severity_entry.tier if _lead_severity_entry is not None else "Emerging"
        )
        fb = get_fallback_synthesis(commercial_family, lead_severity_tier)
        synthesis_result = SynthesisResult(
            **fb,
            synthesis_confidence=0.0,
            is_fallback=True,
        )

    return {
        "identified_states": identified_states,
        "severity": {"tier": severity_result.tier},
        "resolution_routing": resolution_routing,
        "synthesis": asdict(synthesis_result) if synthesis_result else None,
    }
