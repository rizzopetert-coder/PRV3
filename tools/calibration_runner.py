"""
PRV3 Phase 1 Calibration Runner

Runs all 142 test profiles through the full engine pipeline and generates
a Confusion Matrix. Designed to be re-run as answer population progresses.

With answers=[], every profile produces intake-only output (prior priors only).
This is the baseline Confusion Matrix before answer population.

Modes:
  Default (--signal):   generate_answers() — signal-driven per profile type.
                        high_confidence → best_option_for_state() on state_targets questions, neutral elsewhere
                        moderate        → best_option_for_state() on state_targets questions,
                                         neutral elsewhere
                        weak            → neutral throughout
                        Neutral = option with smallest absolute sum of all dimensional fields.
  Synthetic (--synthetic): Option A — inject dimensional vector directly before
                            rank_states(), bypassing question routing layer.
                            high_confidence → primary_liability = 0.60
                            moderate        → primary_liability = 0.40
                            weak            → primary_liability = 0.25

Usage:
    python tools/calibration_runner.py
    python tools/calibration_runner.py --signal
    python tools/calibration_runner.py --synthetic
    python tools/calibration_runner.py --verbose
    python tools/calibration_runner.py --state the_founders_grip
    python tools/calibration_runner.py --dim
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.accumulation import IntakeData, AccumulationEngine, rank_states
from engine.severity import SeverityEngine, SeverityInput
from engine.output import OutputEngine, compute_noise_baseline, SCD_WCS_ALIGNMENT_THRESHOLD
from engine.contract import SessionData, assemble_output
from engine.test_suite import run_test_case, run_suite, PROFILE_TYPES
from engine.data.questions import QUESTION_LIBRARY
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.salience import SALIENCE_PROFILES

from engine.test_profiles import APTITUDE_PROFILES
from engine.test_profiles_authority_b1 import AUTHORITY_B1_PROFILES
from engine.test_profiles_authority_b2 import AUTHORITY_B2_PROFILES
from engine.test_profiles_authority_b3 import AUTHORITY_B3_PROFILES
from engine.test_profiles_alliance import ALLIANCE_PROFILES
from engine.test_profiles_attitude_b1 import ATTITUDE_B1_PROFILES
from engine.test_profiles_attitude_b2 import ATTITUDE_B2_PROFILES
from engine.test_profiles_attitude_b3 import ATTITUDE_B3_PROFILES
from engine.test_profiles_expansion import EXPANSION_PROFILES


ALL_PROFILES = (
    APTITUDE_PROFILES
    + AUTHORITY_B1_PROFILES
    + AUTHORITY_B2_PROFILES
    + AUTHORITY_B3_PROFILES
    + ALLIANCE_PROFILES
    + ATTITUDE_B1_PROFILES
    + ATTITUDE_B2_PROFILES
    + ATTITUDE_B3_PROFILES
    + EXPANSION_PROFILES
)

# Noise baseline computed once and shared across the full run
_NOISE_BASELINE: dict = {}

# v23 calibration cluster window -- HC/extreme pass criterion: target within SCD_WCS_CLUSTER_WINDOW of rank-1
SCD_WCS_CLUSTER_WINDOW:      float = 0.3500  # CALIBRATION TARGET -- Session 26
MODERATE_PROMINENCE_DELTA:   float = 0.26   # CALIBRATION TARGET -- Session 29 (was 0.20, S28)
WEAK_PROMINENCE_DELTA:       float = 0.50   # CALIBRATION TARGET -- Session 28


def _get_noise_baseline() -> dict:
    global _NOISE_BASELINE
    if not _NOISE_BASELINE:
        _NOISE_BASELINE = compute_noise_baseline(random_seed=42)
    return _NOISE_BASELINE


# ── Synthetic Injection (Option A) ────────────────────────────────────────────

_DIM_TO_LIABILITY_FIELD = {
    "Aptitude":  "aptitude_liability",
    "Authority": "authority_liability",
    "Alliance":  "alliance_liability",
    "Attitude":  "attitude_liability",
}

_PROFILE_TYPE_TO_SIGNAL = {
    "high_confidence":         0.60,
    "extreme_high_confidence": 0.60,
    "moderate":                0.40,
    "weak":                    0.25,
}


def _build_synthetic_vector(target_state: str, profile_type: str) -> dict:
    """
    Build a synthetic accumulated vector for Option A injection.
    Sets the target state's primary liability field to the profile-type signal
    strength. All other fields remain at 0.0.
    """
    vec = {f: 0.0 for f in DIMENSIONAL_FIELDS}
    profile = STATE_PROFILES.get(target_state)
    if profile is None:
        return vec
    field = _DIM_TO_LIABILITY_FIELD.get(profile.primary_dimension, "")
    strength = _PROFILE_TYPE_TO_SIGNAL.get(profile_type, 0.25)
    if field:
        vec[field] = strength
    return vec


# ── Phase 2 Answer Generation ─────────────────────────────────────────────────

def best_option_for_state(question, target_state_id: str):
    """Return option with highest contribution on target state's primary liability field.

    On an exact tie for the max value, prefer an option carrying
    severity_trigger=True IF it is dimensionally identical to the
    otherwise-first-picked option across every field, not just the
    maximized one -- an arbitrary list-order pick was silently discarding
    real severity signal at zero dimensional cost. Deliberately narrow:
    confirmed via a full QUESTION_LIBRARY sweep to affect only Q31's 3
    wired states (the_unsolved_problem, decision_blindness,
    sequential_decision_blindness). Two other trigger-involved ties exist
    (Q03A/the_second_close, Q20/decision_paralysis) but differ on other
    fields and are deliberately excluded by the full-identity check.
    """
    profile = STATE_PROFILES.get(target_state_id)
    if not profile:
        return question.answer_options[0]
    field = _DIM_TO_LIABILITY_FIELD.get(profile.primary_dimension, "")
    best = max(
        question.answer_options,
        key=lambda opt: opt.dimensional_contributions.get(field, 0.0),
    )
    if not best.severity_trigger:
        for opt in question.answer_options:
            if (
                opt is not best
                and opt.severity_trigger
                and opt.dimensional_contributions == best.dimensional_contributions
            ):
                return opt
    return best


def _neutral_option(question):
    """Return option with minimum absolute sum of all dimensional contributions."""
    def _abs_sum(opt):
        return sum(
            abs(v) for v in opt.dimensional_contributions.values()
            if isinstance(v, (int, float))
        )
    return min(question.answer_options, key=_abs_sum)


# CALIBRATION TARGET -- Session 70. Weak-branch damped primary-dimension routing.
WEAK_DAMPED_THRESHOLD: float = 0.25

# CALIBRATION TARGET -- this session's weighted-damping redesign (replaces the
# reverted hard-gate attempt). Applied only to UNWIRED questions in the weak
# branch -- scales WEAK_DAMPED_THRESHOLD down further so unwired-question
# signal is real but weaker than wired-question signal, rather than zeroed.
# NOTE: the current 172-profile suite is insensitive to this exact value --
# every value tested from 0.0 to 1.0 produced a byte-for-byte identical
# by-state result. 0.4 is chosen to honor the qualitative design intent
# (real, non-zero, meaningfully damped unwired signal), not because this
# suite can currently discriminate it from other values in range.
WEAK_UNWIRED_DAMPING_FACTOR: float = 0.4


def _damped_weak_option(question, target_state_id: str, threshold: float = WEAK_DAMPED_THRESHOLD):
    """
    Weak-branch damped primary-dimension routing -- Session 70, weighted-
    damping redesign this session (threshold parameter, defaults to the
    original Session 70 value for wired-question callers).

    Prefer the option with the largest positive contribution (<= threshold)
    on target_state's primary_dimension liability field. Falls back to the real,
    unmodified _neutral_option(question) when no qualifying option exists for this
    question.

    Confirmed via Session 70 dry-run against 4 states (decision_paralysis,
    the_arbitrary_standard, the_untouchable, sequential_decision_blindness):
    2 fail-to-pass flips, 0 pass-to-fail regressions at threshold 0.25.

    Known limitation, accepted as-is: operates at dimension granularity, not state
    granularity. Any two states sharing a primary_dimension receive byte-for-byte
    identical weak-branch answer vectors under this rule (for wired questions;
    unwired questions now diverge further via the tighter down-weighted threshold)
    -- downstream cosine similarity against each state's own distinct profile
    vector still differentiates them.
    """
    profile = STATE_PROFILES.get(target_state_id)
    field = _DIM_TO_LIABILITY_FIELD.get(profile.primary_dimension, "") if profile else ""
    candidates = [
        opt for opt in question.answer_options
        if 0.0 < opt.dimensional_contributions.get(field, 0.0) <= threshold
    ]
    if not candidates:
        return _neutral_option(question)
    return max(candidates, key=lambda opt: opt.dimensional_contributions.get(field, 0.0))


_CORE_QUESTION_IDS = [
    qid for qid in QUESTION_LIBRARY
    if qid.startswith("Q") and "SEVER" not in qid
    and "DIST" not in qid and "FOLLOW" not in qid
]

_CONDITIONAL_PAIRS = {"Q03A": "Q03B", "Q27A": "Q27B"}


# ── Severity Follow-On Calibration (reopened, scoped to 4 profiles) ───────────
# Re-investigation finding: every one of the 172 profiles already carries a
# LOCKED expected.severity_tier (Section VII.2). Cross-referencing all 172
# against real severity-trigger reachability found only 4 genuinely achievable
# as spec'd -- the other 168 either already match trivially (Emerging, zero
# signal) or are structurally unreachable given today's SEVER-## question
# wiring (a separate, much larger finding, logged as its own Priority Queue
# item, not addressed here). This table is deliberately sparse and test_id-
# scoped -- a profile absent from it never gets a follow-on spliced in,
# preserving pre-build behavior exactly for all 168 untouched profiles.
#
# ALL-DB-01 / EXP-SDB-01 added following the Q31 tie-break fix to
# best_option_for_state() (below) -- that fix makes Q31's real trigger
# option (C, severity_trigger=True -> SEVER-11) genuinely selectable for
# decision_blindness/sequential_decision_blindness for the first time.
# Opting them in here exercises that real path rather than leaving it
# silently untested. Confirmed NOT sufficient to reach either profile's
# locked expected Entrenched tier on its own -- SEVER-11 has no
# duration_band option (every option maps prior_failed_resolution only),
# capping the achievable raw contribution at 1.0 (score 16.67, Emerging).
# Target value True chosen as the semantically-correct "worst case" signal
# (prior_failed_resolution=True); raw score is identical regardless of
# True/False today since PRIOR_FAILED_RESOLUTION_WEIGHT is still a
# CALIBRATION TARGET (None -> 0.0 fallback). Closing the remaining gap to
# Entrenched needs either a duration_band option added to SEVER-11 or
# another independent trigger wired to these states -- content work,
# folded into the Bucket 2 ("wired, insufficient magnitude") discussion,
# not resolved by this table entry alone.
_SEVERITY_FOLLOW_ON_TARGETS: dict[str, dict[str, object]] = {
    "AUT-PL-01":  {"SEVER-04": "18mo_plus"},
    "AUT-UA-01":  {"SEVER-04": "18mo_plus"},
    "ATT-IB-01":  {"SEVER-06": "18mo_plus"},
    "EXP-HDA-01": {"SEVER-06": "18mo_plus"},
    # Track A duration_band additions (10 questions, all confirmed
    # LIVE-REACHABLE except SEVER-11's Q31 path -- see below). ALL-DB-01/
    # EXP-SDB-01 updated from True to "18mo_plus" now that SEVER-11 offers
    # a real duration_band option; still Phase-2-pending (Q31 inert), kept
    # for calibration-suite internal consistency, not live urgency.
    "ALL-DB-01":  {"SEVER-11": "18mo_plus"},
    "EXP-SDB-01": {"SEVER-11": "18mo_plus"},
    "AUT-UP-01":  {"SEVER-11": "18mo_plus"},
    "AUT-UP-02":  {"SEVER-11": "18mo_plus"},
    "AUT-UP-03":  {"SEVER-11": "18mo_plus"},
    "ATT-BCP-01": {"SEVER-13": "18mo_plus"},
    "ATT-BCP-02": {"SEVER-13": "18mo_plus"},
    "ATT-BCP-03": {"SEVER-13": "18mo_plus"},
    "ATT-GD-01":  {"SEVER-13": "18mo_plus"},
    "ATT-GD-02":  {"SEVER-13": "18mo_plus"},
    "ATT-GD-03":  {"SEVER-13": "18mo_plus"},
    "ATT-NL-01":  {"SEVER-13": "18mo_plus"},
    "ATT-NL-02":  {"SEVER-13": "18mo_plus"},
    "ATT-NL-03":  {"SEVER-13": "18mo_plus"},
    "ALL-FR-01":  {"SEVER-08": "18mo_plus", "SEVER-14": "18mo_plus"},
    "ALL-FR-02":  {"SEVER-08": "18mo_plus"},
    "ALL-SI-01":  {"SEVER-08": "18mo_plus", "SEVER-14": "18mo_plus"},
    "ALL-SI-02":  {"SEVER-08": "18mo_plus"},
    "ALL-SI-03":  {"SEVER-08": "18mo_plus"},
    "EXP-DCF-01": {"SEVER-08": "18mo_plus"},
    # Q02/D second trigger (the_exposed / planning_authority_gap /
    # hr_capture) -- AUT-EX-01, EXP-PAG-01, AUT-HC-02 are single-trigger
    # Entrenched-expected, closed by this alone. AUT-HC-01 is
    # Endemic-expected and genuinely needs a second trigger (candidate:
    # Q04, separate future review, not part of this fix) -- correctly
    # lands short at Entrenched (raw 2.00), not a bug.
    "AUT-EX-01":  {"SEVER-15": "18mo_plus"},
    "EXP-PAG-01": {"SEVER-15": "18mo_plus"},
    "AUT-HC-01":  {"SEVER-15": "18mo_plus"},
    "AUT-HC-02":  {"SEVER-15": "18mo_plus"},
    # Q18/C second trigger (the_unreported_hazard / the_unlocked_door /
    # what_nobody_says / the_suppression_filter) -- ATT-UD-01, ATT-UH-01,
    # ALL-SF-02, ALL-SF-03 are single-trigger Entrenched-expected, closed
    # by this alone. ATT-WNS-01 and ALL-SF-01 are Endemic-expected and
    # genuinely need a second trigger (candidates: Q04 for
    # what_nobody_says; Q04/Q08/Q12/Q30 for the_suppression_filter --
    # separate future review, not part of this fix) -- correctly land
    # short at Entrenched (raw 2.00), not a bug.
    "ATT-UD-01":  {"SEVER-16": "18mo_plus"},
    "ATT-UH-01":  {"SEVER-16": "18mo_plus"},
    "ATT-WNS-01": {"SEVER-16": "18mo_plus"},
    "ALL-SF-01":  {"SEVER-16": "18mo_plus"},
    "ALL-SF-02":  {"SEVER-16": "18mo_plus"},
    "ALL-SF-03":  {"SEVER-16": "18mo_plus"},
    "APT-UL-01":  {"SEVER-07": "18mo_plus"},
    "APT-DT-01":  {"SEVER-07": "18mo_plus"},
    "AUT-LC-01":  {"SEVER-07": "18mo_plus"},
    "APT-BF-01":  {"SEVER-02": "18mo_plus"},
    "APT-BF-02":  {"SEVER-02": "18mo_plus"},
    "APT-UR-01":  {"SEVER-02": "18mo_plus"},
    "ATT-CD-01":  {"SEVER-10": "18mo_plus"},
    "ATT-IE-01":  {"SEVER-10": "18mo_plus"},
    "EXP-WT-01":  {"SEVER-10": "18mo_plus"},
    "AUT-DP-01":  {"SEVER-03": "18mo_plus"},
    "AUT-LM-01":  {"SEVER-03": "18mo_plus"},
    "AUT-PF-01":  {"SEVER-01": "18mo_plus"},
    # ATT-DC-01 needs BOTH to reach its locked Endemic (raw>=4.00) -- either
    # alone caps at Entrenched (raw=2.00).
    "ATT-DC-01":  {"SEVER-01": "18mo_plus", "SEVER-12": "18mo_plus"},
}


def select_severity_follow_on_option(question, target_value):
    """
    Select the SEVER-## follow-on option whose severity_input_mapping
    contains target_value. Selects on the actual severity_input_mapping
    value, not liability-vector contribution -- confirmed during
    investigation that best_option_for_state() doesn't meaningfully
    differentiate SEVER-## options (only SEVER-05 has real per-option
    dimensional_contributions variation; every other SEVER-## question
    ties all its options at the same seeded per-question uniform value).

    Fail-loud: raises ValueError if no option matches, rather than
    silently falling back to the first option -- a profile-table mistake
    (e.g. assigning a duration_band value to a question that only maps to
    named_condition) should surface immediately, not mask as a neutral pick.
    """
    for opt in question.answer_options:
        if opt.severity_input_mapping and target_value in opt.severity_input_mapping.values():
            return opt
    raise ValueError(
        f"{question.question_id}: no option maps to target_value={target_value!r} "
        f"-- check the profile table against this question's real severity_input_mapping"
    )


def generate_answers(test_case):
    """
    Generate TestAnswer list from test_case.profile_type and target_state.

    high_confidence/extreme: best_option_for_state() where target in state_targets, neutral elsewhere.
    moderate: best_option_for_state() where target in state_targets, neutral elsewhere.
    weak: weighted-damping redesign, this session -- best_option_for_state() (real,
          full-strength signal) where target in state_targets; damped primary-
          dimension routing (Session 70) at a further down-weighted threshold
          (WEAK_DAMPED_THRESHOLD * WEAK_UNWIRED_DAMPING_FACTOR) where not, neutral
          fallback only if no qualifying option exists even at that tighter threshold.

    Handles Q03A/Q03B and Q27A/Q27B conditional pairs from intake.
    """
    from engine.test_suite import TestAnswer
    events = test_case.intake.get("significant_events", ["none"])
    has_acq = "acquisition_or_merger" in events
    include = {
        "Q03A" if events != ["none"] else "Q03B",
        "Q27A" if has_acq else "Q27B",
    }

    answers = []
    # Dedup guard, mirroring the real live app's severityFollowOnAlreadyAsked()
    # (web/lib/session-store.ts) -- a follow-on with multiple real parent
    # questions (SEVER-11 via Q28 and Q31, the "dual-parent" case that
    # module's own header comment already documents) must only ever be
    # spliced in once per session. Without this, a later core question
    # that also fires an already-spliced follow-on would double-count its
    # raw contribution -- confirmed as a real, latent bug via the Track A
    # regression check (AUT-UP-01/02/03 overshot to Endemic instead of
    # their locked Entrenched, SEVER-11 fired twice, raw summed to 4.00
    # instead of the correct single-count 2.00).
    already_spliced_followons = set()
    for qid in sorted(_CORE_QUESTION_IDS):
        excluded = any(
            (qid == a and a not in include) or (qid == b and b not in include)
            for a, b in _CONDITIONAL_PAIRS.items()
        )
        if excluded:
            continue
        q = QUESTION_LIBRARY.get(qid)
        if q is None or not q.answer_options:
            continue
        strategy = test_case.profile_type
        if strategy in ("high_confidence", "extreme_high_confidence"):
            opt = (best_option_for_state(q, test_case.target_state)
                   if test_case.target_state in (q.state_targets or [])
                   else _neutral_option(q))
        elif strategy == "moderate":
            opt = (best_option_for_state(q, test_case.target_state)
                   if test_case.target_state in (q.state_targets or [])
                   else _neutral_option(q))
        else:
            # "weak" -- weighted-damping redesign, this session. Wired
            # questions get real full-strength signal (same as moderate/
            # high_confidence); unwired questions keep the Session 70 damped
            # dimension-level signal but at a further down-weighted threshold,
            # rather than the reverted hard-gate attempt's zeroed _neutral_option().
            if test_case.target_state in (q.state_targets or []):
                opt = best_option_for_state(q, test_case.target_state)
            else:
                opt = _damped_weak_option(
                    q, test_case.target_state,
                    threshold=WEAK_DAMPED_THRESHOLD * WEAK_UNWIRED_DAMPING_FACTOR,
                )
        answers.append(TestAnswer(question_id=qid, selected_option_ids=[opt.option_id]))

        # Severity follow-on simulation -- opt-in only, via
        # _SEVERITY_FOLLOW_ON_TARGETS. A test_id absent from that table
        # (168 of 172 profiles) produces byte-for-byte identical answers to
        # before this build -- no follow-on ever gets spliced in for them.
        if (
            opt.severity_trigger
            and opt.severity_follow_on_id
            and opt.severity_follow_on_id not in already_spliced_followons
        ):
            target_value = _SEVERITY_FOLLOW_ON_TARGETS.get(test_case.test_id, {}).get(
                opt.severity_follow_on_id
            )
            if target_value is not None:
                follow_on_q = QUESTION_LIBRARY[opt.severity_follow_on_id]
                follow_on_opt = select_severity_follow_on_option(follow_on_q, target_value)
                answers.append(TestAnswer(
                    question_id=opt.severity_follow_on_id,
                    selected_option_ids=[follow_on_opt.option_id],
                ))
                already_spliced_followons.add(opt.severity_follow_on_id)
    return answers


def run_profile_synthetic(test_case) -> dict:
    """
    Run one test profile using synthetic dimensional injection (Option A).
    Bypasses the question routing layer — directly injects a vector before
    rank_states(). Used for Phase 1 calibration before answer population.

    Returns the assemble_output() dict.
    """
    intake = IntakeData(**test_case.intake)
    synthetic_vector = _build_synthetic_vector(test_case.target_state, test_case.profile_type)

    rankings  = rank_states(synthetic_vector, 39, SALIENCE_PROFILES)
    sev_engine = SeverityEngine()
    sev_result = sev_engine.score()

    out_engine = OutputEngine()
    out_engine.set_noise_baseline(baseline=_get_noise_baseline())
    out_pkg = out_engine.build(rankings, sev_result)

    session = SessionData(
        session_id=SessionData.new_session_id(),
        intake=intake,
        final_rankings=rankings,
        accumulated_vector=synthetic_vector,
        output_package=out_pkg,
        severity_result=sev_result,
    )
    return assemble_output(session)


def run_profile(test_case) -> dict:
    """
    Run one test profile through the full engine pipeline.
    Returns the assemble_output() dict.

    With test_case.answers=[], generates answers via generate_answers() based
    on profile_type and target_state (Phase 2 mode).
    """
    intake = IntakeData(**test_case.intake)

    # Accumulation
    acc_engine = AccumulationEngine(intake)
    sev_engine = SeverityEngine()

    answers_to_use = test_case.answers or generate_answers(test_case)
    for ans in answers_to_use:
        q = QUESTION_LIBRARY.get(ans.question_id)
        if q is None:
            continue
        for opt_id in ans.selected_option_ids:
            opt = next(
                (o for o in q.answer_options if o.option_id == opt_id),
                None,
            )
            if opt is None:
                continue
            acc_engine.apply_answer(opt, ans.question_id)

            # Severity follow-on collection -- mirrors engine/main.py's
            # accumulate_one_answer() exactly, including its own documented
            # trigger_question_id simplification (defaults to the follow-on's
            # own question_id when true provenance isn't threaded through --
            # the same convention already used in the real, live-verified
            # Path 1 code, not a new one invented for calibration).
            if opt.severity_input_mapping:
                severity_input = SeverityInput(
                    trigger_question_id=ans.question_id,
                    severity_follow_on_id=ans.question_id,
                    **opt.severity_input_mapping,
                )
                sev_engine.add_input(severity_input)

    rankings = acc_engine.rank(SALIENCE_PROFILES)
    sev_result = sev_engine.score()

    out_engine = OutputEngine()
    out_engine.set_noise_baseline(baseline=_get_noise_baseline())
    out_pkg = out_engine.build(rankings, sev_result)

    session = SessionData(
        session_id=SessionData.new_session_id(),
        intake=intake,
        final_rankings=rankings,
        accumulated_vector=acc_engine.accumulated_vector,
        output_package=out_pkg,
        severity_result=sev_result,
    )
    return assemble_output(session)


# -- v23 Calibration Suite Builder -------------------------------------------

def _passes_cluster_criterion(rankings: list, target_state_id: str) -> bool:
    # Top-cluster presence criterion -- v23 revised calibration pass criterion.
    # Pass condition: target state score >= rank-1 score minus SCD_WCS_CLUSTER_WINDOW.
    # rankings: list of objects with .state_id and .score (descending by score).
    if not rankings:
        return False
    rank_1_score = rankings[0].score
    target = next((r for r in rankings if r.state_id == target_state_id), None)
    if target is None:
        return False
    return target.score >= rank_1_score - SCD_WCS_CLUSTER_WINDOW


def _passes_prominence_criterion(result: dict, profile_type: str) -> bool:
    """
    Prominence-based pass criterion for moderate and weak profiles.
    Replaces strict single_state output_type requirement.

    Pass conditions (both required):
      1. Target state score >= SCD_WCS_ALIGNMENT_THRESHOLD (floor gate)
      2. Target state score >= rank_1_score - delta
         where delta = MODERATE_PROMINENCE_DELTA for moderate profiles
                       WEAK_PROMINENCE_DELTA for weak profiles

    Calibration targets -- subject to revision with real-world signal data.
    Session 28.
    """
    target_score = result['target_score']
    rank_1_score = result['rank_1_score']

    if target_score < SCD_WCS_ALIGNMENT_THRESHOLD:
        return False

    if profile_type == 'moderate':
        delta = MODERATE_PROMINENCE_DELTA
    elif profile_type == 'weak':
        delta = WEAK_PROMINENCE_DELTA
    else:
        raise ValueError(
            f'_passes_prominence_criterion called with unexpected profile_type: {profile_type!r}'
        )

    return target_score >= (rank_1_score - delta)


def _build_suite_v23(
    test_cases: list,
    engine_outputs: dict,
) -> dict:
    # HC/extreme: pass iff _passes_cluster_criterion().
    # Moderate/weak: pass iff _passes_prominence_criterion() -- Session 28.
    import types as _types
    from engine.test_suite import TestResult
    results = []
    by_type = {pt: {'total': 0, 'passed': 0} for pt in PROFILE_TYPES}
    by_state: dict = {}

    for tc in test_cases:
        output = engine_outputs.get(tc.test_id, {})
        if tc.profile_type in ('high_confidence', 'extreme_high_confidence'):
            if output:
                _dist = sorted(output.get('state_distribution', []), key=lambda e: e.get('rank', 99))
                _rnks = [_types.SimpleNamespace(state_id=e.get('state_id', ''), score=e.get('score', 0.0)) for e in _dist]
                passed = _passes_cluster_criterion(_rnks, tc.target_state)
            else:
                passed = False
            result = TestResult(
                test_id=tc.test_id,
                passed=passed,
                violations=[],
                criteria_failures=[] if passed else [
                    f'{tc.profile_type}: cluster criterion failed for {tc.target_state!r}'
                ],
                output=output,
            )
        elif tc.profile_type in ('moderate', 'weak'):
            if output:
                _dist   = sorted(output.get('state_distribution', []),
                                 key=lambda e: e.get('rank', 99))
                _target = next(
                    (e for e in _dist if e.get('state_id') == tc.target_state), None
                )
                _rank1  = _dist[0] if _dist else None
                _pdata  = {
                    'target_score': _target.get('score', -999.0) if _target else -999.0,
                    'rank_1_score': _rank1.get('score',  -999.0) if _rank1  else -999.0,
                }
                passed = _passes_prominence_criterion(_pdata, tc.profile_type)
            else:
                passed = False
            result = TestResult(
                test_id=tc.test_id,
                passed=passed,
                violations=[],
                criteria_failures=[] if passed else [
                    f'{tc.profile_type}: prominence criterion failed for {tc.target_state!r}'
                ],
                output=output,
            )
        else:
            if output:
                result = run_test_case(tc, output)
            else:
                result = TestResult(
                    test_id=tc.test_id,
                    passed=False,
                    violations=[],
                    criteria_failures=[f'No engine output for {tc.test_id!r}'],
                    output={},
                )

        results.append(result)

        pt = tc.profile_type
        if pt in by_type:
            by_type[pt]['total'] += 1
            if result.passed:
                by_type[pt]['passed'] += 1

        sid = tc.target_state
        if sid not in by_state:
            by_state[sid] = {'total': 0, 'passed': 0}
        by_state[sid]['total'] += 1
        if result.passed:
            by_state[sid]['passed'] += 1

    total = len(results)
    passed_count = sum(1 for r in results if r.passed)
    return {
        'total':           total,
        'passed':          passed_count,
        'failed':          total - passed_count,
        'results':         results,
        'by_profile_type': by_type,
        'by_state':        by_state,
    }


# ── Confusion Matrix ───────────────────────────────────────────────────────────

def build_confusion_matrix(run_results: list) -> dict:
    """
    Build a Confusion Matrix from calibration run results.

    run_results: list of (TestCase, engine_output_dict)

    Returns matrix[target_state][rank1_state] = count.
    Diagonal entries are correct classifications.
    Off-diagonal entries are misclassifications.
    """
    matrix: dict = {}
    for tc, output in run_results:
        target = tc.target_state
        dist = output.get("state_distribution", [])
        rank1 = next(
            (e["state_id"] for e in dist if e.get("rank") == 1),
            "insufficient_signal",
        )
        if target not in matrix:
            matrix[target] = {}
        matrix[target][rank1] = matrix[target].get(rank1, 0) + 1
    return matrix


def _target_rank(output: dict, target_state: str) -> int:
    """Return the rank of target_state in state_distribution, or 48 if absent."""
    dist = output.get("state_distribution", [])
    entry = next((e for e in dist if e.get("state_id") == target_state), None)
    return entry["rank"] if entry else 48


def build_dimensional_error_table(run_results: list) -> list:
    """
    For each misclassified profile, return the leading dimensional mismatch.

    Compares the accumulated vector's dominant dimension against the predicted
    rank-1 state's dominant profile dimension, flagging where they diverge from
    the target state.

    Returns list of dicts with keys:
        test_id, target, predicted_rank1, target_rank,
        dominant_acc_dim, target_dominant_dim, predicted_dominant_dim
    """
    rows = []
    for tc, output in run_results:
        dist = output.get("state_distribution", [])
        rank1 = next(
            (e["state_id"] for e in dist if e.get("rank") == 1),
            None,
        )
        if rank1 == tc.target_state:
            continue  # correct

        t_rank = _target_rank(output, tc.target_state)

        # Dominant dimension in the accumulated vector (highest absolute value)
        acc_vec = output.get("state_distribution", [])
        # The accumulated vector isn't in the output dict directly; pull from first entry
        # We use state_distribution scores as proxy
        target_profile = STATE_PROFILES.get(tc.target_state)
        predicted_profile = STATE_PROFILES.get(rank1)

        def dominant_dim(profile):
            if profile is None:
                return "?"
            vec = profile.dimensional_vector.as_dict()
            return max(vec, key=lambda f: vec[f])

        rows.append({
            "test_id":              tc.test_id,
            "profile_type":         tc.profile_type,
            "target":               tc.target_state,
            "predicted_rank1":      rank1 or "insufficient_signal",
            "target_rank":          t_rank,
            "target_dominant_dim":  dominant_dim(target_profile),
            "predicted_dominant_dim": dominant_dim(predicted_profile),
        })
    return rows


# ── Reporting ─────────────────────────────────────────────────────────────────

def _rank_label(rank: int) -> str:
    if rank == 1:
        return "rank-1"
    if rank <= 3:
        return f"rank-{rank}"
    return f"rank-{rank} (miss)"


def print_report(
    suite: dict,
    matrix: dict,
    dim_table: list,
    profiles: list,
    verbose: bool = False,
    show_dim: bool = False,
    synthetic: bool = False,
) -> None:
    answered = sum(1 for p in profiles if p.answers)
    total = len(profiles)
    mode = "synthetic injection (Option A)" if synthetic else "signal-driven (generate_answers)"

    print("=" * 72)
    print("PRV3 Phase 1 Calibration Run")
    print(f"  Profiles:          {total}")
    print(f"  Mode:              {mode}")
    if not synthetic:
        print(f"  Pre-populated answers: {answered}/{total}")
    print("=" * 72)

    print(f"\nRESULT: {suite['passed']}/{suite['total']} passed "
          f"({suite['failed']} failed)")

    print("\nBy profile type:")
    for pt in PROFILE_TYPES:
        data = suite["by_profile_type"].get(pt, {})
        t = data.get("total", 0)
        p = data.get("passed", 0)
        bar = "OK" if p == t else f"{p}/{t}"
        print(f"  {pt:<32} {bar}")

    # Per-state summary
    print("\nBy state:")
    for sid, data in sorted(suite["by_state"].items()):
        p = data["passed"]
        t = data["total"]
        flag = "" if p == t else " <--"
        print(f"  {sid:<44} {p}/{t}{flag}")

    # Confusion Matrix — misclassifications only
    print("\nConfusion Matrix (misclassifications only):")
    any_miss = False
    for target in sorted(matrix):
        preds = matrix[target]
        for pred, cnt in sorted(preds.items(), key=lambda x: -x[1]):
            if pred != target:
                any_miss = True
                correct = preds.get(target, 0)
                total_t = sum(preds.values())
                print(f"  {target:<44} -> {pred:<44} x{cnt}  "
                      f"(correct {correct}/{total_t})")
    if not any_miss:
        print("  All profiles classified correctly at rank-1.")

    # Dimensional error analysis
    if show_dim and dim_table:
        print("\nDimensional error analysis (misclassified profiles):")
        print(f"  {'test_id':<14} {'profile_type':<22} {'target_rank':<12} "
              f"{'target_dominant':<28} {'predicted_dominant'}")
        print(f"  {'-'*14} {'-'*22} {'-'*12} {'-'*28} {'-'*28}")
        for row in sorted(dim_table, key=lambda r: r["target_rank"]):
            print(f"  {row['test_id']:<14} {row['profile_type']:<22} "
                  f"{_rank_label(row['target_rank']):<12} "
                  f"{row['target_dominant_dim']:<28} "
                  f"{row['predicted_dominant_dim']}")

    # Verbose: per-profile detail on failures
    if verbose:
        print("\nFailed profiles:")
        for r in suite["results"]:
            if not r.passed:
                for f in r.criteria_failures:
                    print(f"  [{r.test_id}] {f}")

    print("=" * 72)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PRV3 Phase 1 Calibration Runner"
    )
    parser.add_argument("--verbose", action="store_true",
                        help="Print per-profile failure details")
    parser.add_argument("--state",
                        help="Filter run to one target_state")
    parser.add_argument("--dim", action="store_true",
                        help="Show dimensional error analysis for misclassified profiles")
    parser.add_argument("--signal", action="store_true",
                        help="Explicit signal-driven mode (default — generate_answers() per profile type)")
    parser.add_argument("--synthetic", action="store_true",
                        help="Option A: inject synthetic dimensional vectors (bypasses question layer)")
    parser.add_argument("--output-json", action="store_true",
                        help="Output structured JSON (hc_passing, hc_failing, sink_counts) for harness use")
    args = parser.parse_args()

    profiles = list(ALL_PROFILES)
    if args.state:
        profiles = [p for p in profiles if p.target_state == args.state]
        if not profiles:
            print(f"No profiles found for state: {args.state!r}")
            sys.exit(1)

    runner = run_profile_synthetic if args.synthetic else run_profile

    # Run all profiles
    run_results = []
    engine_outputs = {}

    for tc in profiles:
        output = runner(tc)
        run_results.append((tc, output))
        engine_outputs[tc.test_id] = output

    suite = _build_suite_v23(profiles, engine_outputs)
    matrix = build_confusion_matrix(run_results)
    dim_table = build_dimensional_error_table(run_results)

    if args.output_json:
        import json
        import types as _types_j
        hc_passing_j, hc_failing_j, hc_seen = [], [], set()
        for tc in profiles:
            if tc.profile_type in ("high_confidence", "extreme_high_confidence"):
                out_j = engine_outputs.get(tc.test_id, {})
                if out_j:
                    _d = sorted(out_j.get("state_distribution", []), key=lambda e: e.get("rank", 99))
                    _r = [_types_j.SimpleNamespace(
                        state_id=e.get("state_id", ""),
                        score=e.get("score", 0.0),
                    ) for e in _d]
                    ok = _passes_cluster_criterion(_r, tc.target_state)
                else:
                    ok = False
                if tc.target_state not in hc_seen:
                    hc_seen.add(tc.target_state)
                    (hc_passing_j if ok else hc_failing_j).append(tc.target_state)
        sink_j: dict = {}
        for tgt, preds in matrix.items():
            for pred, cnt in preds.items():
                if pred != tgt:
                    sink_j[pred] = sink_j.get(pred, 0) + cnt
        print(json.dumps({
            "hc_passing":      hc_passing_j,
            "hc_failing":      hc_failing_j,
            "overall_passing": suite["passed"],
            "overall_total":   suite["total"],
            "sink_counts":     sink_j,
        }))
        sys.exit(0)

    print_report(
        suite, matrix, dim_table, profiles,
        verbose=args.verbose,
        show_dim=args.dim,
        synthetic=args.synthetic,
    )

    sys.exit(0 if suite["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
