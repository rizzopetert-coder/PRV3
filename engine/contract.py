"""
PRV3 Scoring Engine — Section VII
Engine Output Contract

VII.1  Engine Output Data Structure (immutable JSON schema)
VII.2  Phase 1 Test Suite Interface Contract

Key names, data types, and field presence are immutable per spec VII.1.
This module is the interface boundary between the scoring engine and all
downstream systems (renderer, test suite, future integrations).

Spec reference: documents/PRV3_Scoring_Architecture_Spec_v1.docx, Section VII
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.jurisdiction import resolve_jurisdiction_flags
from engine.data.questions import QUESTION_LIBRARY, PROBLEM_CONTEXT_VALENCES
from engine.data.salience import SALIENCE_PROFILES
from engine.accumulation import (
    IntakeData, StateRanking, compute_cascade_risk,
    AccumulationSession, accumulate_answer,
)
from engine.checkpoint import CheckpointResult
from engine.narrative import NarrativeExtractionResult
from engine.severity import SeverityResult, SEVERITY_TIER_DESCRIPTIONS
from engine.friction_tax import (
    compute_friction_tax, compute_legal_compliance_exposure,
    compute_legal_per_state_breakdown, STATE_MULTIPLIERS,
)
from engine.resolution_families import (
    apply_causation_override, translate_resolution_family, HR_DIAGNOSTIC_FAMILY_NAME,
)

# Addendum 11 -- caveat text for legal_tail_risk_exposure (private_output only).
LEGAL_TAIL_RISK_CAVEAT_TEXT = (
    "This estimate reflects contingent exposure -- a range of what could be at "
    "stake if this pattern were ever formally challenged, not a prediction that "
    "it will be. Most organizations carrying a similar pattern never face an "
    "actual claim. This figure combines identified conditions across legal and "
    "regulatory categories, using publicly available case outcomes, agency "
    "enforcement data, and statutory penalty schedules as reference points -- "
    "not a legal opinion, and not specific to your organization's actual risk "
    "of being challenged. If any of these conditions concern you, this is worth "
    "a conversation with employment counsel, not just this number."
)

# is_floor scoping follow-up, this session -- 7 verified per-state
# caveats for the flat_cap component-vs-total mismatch (FL/ID/KS/VA)
# and the state_specific_tiers unmodeled-carve-out cases (AR/MD/TN).
# Keyed by the jurisdiction id LegalPricingResult/LegalCurveLookup's
# specific_caveat_jurisdiction reports -- friction_tax.py carries only
# that identifier, never prose; this dict is the single source of
# truth for which jurisdictions have a specific caveat written at all
# (a jurisdiction id not present here, e.g. any other state_specific_
# flat/tiers state, resolves to None via .get() below, no separate
# allow-list needed in friction_tax.py). Texts verbatim, Pete-confirmed,
# do not alter.
_SPECIFIC_CAVEAT_TEXT: dict[str, str] = {
    "FL": (
        "This figure reflects only punitive damages, capped at $100,000 "
        "under Fla. Stat. Sec 760.11(5). Compensatory damages are legally "
        "available in addition and aren't capped by this provision -- the "
        "real total could be materially higher than what's reflected here."
    ),
    "ID": (
        "This figure reflects only punitive damages, capped at $1,000 per "
        "violation under Idaho Code Sec 67-5908(3)(e). Actual and economic "
        "damages, including back pay, are legally available in addition "
        "and aren't capped by this provision -- the real total could be "
        "materially higher than what's reflected here."
    ),
    "KS": (
        "This figure reflects only pain-and-suffering damages, capped at "
        "$2,000 under K.S.A. Sec 44-1005(k). Back pay and other economic "
        "damages are legally available in addition and aren't capped by "
        "this provision -- the real total could be materially higher than "
        "what's reflected here."
    ),
    "VA": (
        "This figure reflects only punitive damages, capped at $350,000 "
        "under Va. Code Sec 8.01-38.1. Compensatory damages are legally "
        "available in addition and aren't capped under Virginia law -- "
        "the real total could be materially higher than what's reflected "
        "here."
    ),
    "AR": (
        "Arkansas law doesn't cap damages for retaliation claims "
        "specifically -- if this involves retaliation, the actual limit "
        "could be materially higher than what's reflected here."
    ),
    "MD": (
        "In Howard, Montgomery, and Prince George's counties, Maryland "
        "law offers an uncapped alternative to this limit -- if this "
        "claim would qualify, the actual limit could be materially "
        "higher than what's reflected here."
    ),
    "TN": (
        "Tennessee law doesn't cap damages for race-discrimination "
        "claims brought under 42 U.S.C. Sec 1981 -- if this involves "
        "such a claim, the actual limit could be materially higher than "
        "what's reflected here."
    ),
}
from engine.output import (
    OutputPackage, OutputRouting, compute_causation_pattern,
    derive_time_to_consequence, synthesize_response_window,
)


# ── Engine version ─────────────────────────────────────────────────────────────

ENGINE_VERSION: str = "0.2.1"  # Incremented at each build milestone


# ── VII.1  Session data container ──────────────────────────────────────────────

@dataclass
class SessionData:
    """
    Complete state from one scoring session. Passed to assemble_output().

    All fields required for VII.1 contract assembly. Narrative and checkpoint
    fields are Optional because they may not fire in every session.

    Spec reference: Section VII.1 (input side of the output assembler)
    """
    session_id:          str
    intake:              IntakeData
    final_rankings:      list              # list[StateRanking], post-modulation
    accumulated_vector:  dict              # final accumulated vector
    output_package:      OutputPackage
    severity_result:     SeverityResult

    narrative_result:    Optional[NarrativeExtractionResult] = None
    narrative_trigger:   Optional[str]     = None   # "Q27" | "Q34" | None
    pre_narrative_rankings: Optional[list] = None   # for state_delta calculation

    checkpoint_q11:      Optional[CheckpointResult] = None
    checkpoint_q19:      Optional[CheckpointResult] = None
    checkpoint_q27:      Optional[CheckpointResult] = None

    q_signal_decision_blindness: bool = False

    @staticmethod
    def new_session_id() -> str:
        return str(uuid.uuid4())


# ── Asset score derivation ─────────────────────────────────────────────────────

def _compute_asset_score(
    accumulated_vector: dict,
    lead_state_id: Optional[str],
) -> dict:
    """
    Derive asset score from the accumulated vector and the leading state's profile.

    score: ratio of asset-axis signal to total signal in the accumulated vector.
      Range 0.0–1.0. CALIBRATION TARGET methodology — this proxy will be
      refined once question-library asset contributions are established.

    primary_asset_domain: first asset_axes entry from the leading state's profile.
    resolution_anchor_text: LLM-generated at application layer (empty here).

    Spec reference: Section VII.1 — asset_score field
    """
    asset_fields = [f for f in DIMENSIONAL_FIELDS if f.endswith("_asset")]
    total_all = sum(accumulated_vector.get(f, 0.0) for f in DIMENSIONAL_FIELDS)
    total_asset = sum(accumulated_vector.get(f, 0.0) for f in asset_fields)

    score = round(min(total_asset / total_all, 1.0), 4) if total_all > 0.0 else 0.0

    primary_domain = ""
    if lead_state_id and lead_state_id in STATE_PROFILES:
        axes = STATE_PROFILES[lead_state_id].asset_axes
        primary_domain = axes[0] if axes else ""

    return {
        "score": score,
        "primary_asset_domain": primary_domain,
        "resolution_anchor_text": "",  # LLM-generated at application layer
    }


# ── Liability score derivation ──────────────────────────────────────────────

def _compute_liability_score(
    accumulated_vector: dict,
    lead_state_id: Optional[str],
) -> dict:
    """
    Derive liability score from the accumulated vector and the leading
    state's profile. Mirrors _compute_asset_score() exactly, substituting
    the liability-side fields and the leading state's liability_axes.

    Not part of the VII.1 output contract -- no liability_score field
    exists there (asset_score does). This exists solely to give
    OutputSynthesisEngine.synthesize() a real liability_score instead of
    the hardcoded 0.0 both call sites passed before this fix.

    score: ratio of liability-axis signal to total signal in the
      accumulated vector. Range 0.0-1.0. Same CALIBRATION TARGET
      methodology caveat as _compute_asset_score().
    """
    liability_fields = [f for f in DIMENSIONAL_FIELDS if f.endswith("_liability")]
    total_all = sum(accumulated_vector.get(f, 0.0) for f in DIMENSIONAL_FIELDS)
    total_liability = sum(accumulated_vector.get(f, 0.0) for f in liability_fields)

    score = round(min(total_liability / total_all, 1.0), 4) if total_all > 0.0 else 0.0

    primary_domain = ""
    if lead_state_id and lead_state_id in STATE_PROFILES:
        axes = STATE_PROFILES[lead_state_id].liability_axes
        primary_domain = axes[0] if axes else ""

    return {
        "score": score,
        "primary_liability_domain": primary_domain,
        "condition_text": "",  # LLM-generated at application layer
    }


def _compute_dimension_summary(accumulated_vector: dict) -> dict:
    """
    Per-axis asset ratio: asset_d / (asset_d + liability_d), computed
    independently for each of the four dimensions (aptitude/authority/
    alliance/attitude). Range 0.0-1.0 per axis. A zero-signal axis
    (asset_d + liability_d == 0.0) returns 0.0 -- same convention as
    _compute_asset_score().

    Mirrors _compute_asset_score()'s existing aggregation pattern (a
    derived ratio, not the raw vector) rather than a fresh min-max
    normalization -- consistent with how the engine already aggregates
    dimensional signal without exposing the raw liability/asset split to
    the client (P-03). Gemini architecture review cleared this shape
    (single normalized [0,1] scalar per axis) before implementation.

    Spec reference: Section VII.1 — dimension_summary field
    """
    axes = ("aptitude", "authority", "alliance", "attitude")
    summary: dict = {}
    for axis in axes:
        liability = accumulated_vector.get(f"{axis}_liability", 0.0)
        asset = accumulated_vector.get(f"{axis}_asset", 0.0)
        total = liability + asset
        summary[axis] = round(asset / total, 4) if total > 0.0 else 0.0
    return summary


# ── Jurisdiction flags assembly ────────────────────────────────────────────────

def _assemble_jurisdiction_flags(intake: IntakeData) -> dict:
    """
    Assemble the jurisdiction_flags output object from intake data.

    applied_multipliers: axis modifiers that fired based on intake conditions.
    Currently empty until axis modifier logging is wired end-to-end.

    Spec reference: Section VII.1 — jurisdiction_flags field
    """
    flags = resolve_jurisdiction_flags(intake.jurisdictions)
    return {
        "transparency": flags.get("transparency", False),
        "retaliation": flags.get("retaliation"),
        "procedural": flags.get("procedural"),
        "applied_multipliers": [],  # populated when axis modifier logging added
    }


# ── Checkpoint log assembly ────────────────────────────────────────────────────

def _checkpoint_entry(result: Optional[CheckpointResult]) -> dict:
    """Single checkpoint entry for checkpoint_log."""
    if result is None:
        return {
            "entropy": None,
            "threshold": None,
            "threshold_exceeded": None,
            "distinguisher_fired": None,
        }
    return {
        "entropy": round(result.entropy, 6),
        "threshold": result.threshold,
        "threshold_exceeded": result.fires,
        "distinguisher_fired": len(result.distinguishers) > 0,
    }


# ── VII.1  Output Assembly ─────────────────────────────────────────────────────

# ── monitoring_metadata constants ─────────────────────────────────────────────

_PROTECTED_ACTIVITY_INTAKE_EVENTS = frozenset(["external_legal_matter"])

_DB_FLAG_ID = "decision_blindness_protected_activity"
_DB_SEVERITY_FLOOR = "entrenched"
_DB_RECOMMENDED_ROUTES = ["executive_counsel", "intervention"]
_DB_INTERNAL_NOTE = (
    "Decision Blindness signal present with confirmed protected activity context. "
    "Prioritize engagement review before diagnostic output is shared."
)


def _assemble_monitoring_metadata(session: SessionData) -> dict:
    """
    Assemble monitoring_metadata for one scoring session.

    Always present in engine output. Excluded from shareable output package.

    Decision Blindness protected-activity flag (decision_blindness_protected_activity)
    fires when both conditions are met:
      (1) decision_blindness score >= noise_baseline for that state
      (2) protected activity confirmed from at least one source:
            intake_significant_events: significant_events contains a protected
                                       activity event (e.g. external_legal_matter)
            q_signal:                  session.q_signal_decision_blindness is True
                                       (set by session orchestrator from Q06 answers)

    Flag is always present in the flags list. triggered=True only when both
    conditions are met. priority is always "high" for this flag type.
    any_high_priority reflects whether any triggered flag carries high priority.

    Spec reference: Section VII.1 -- monitoring_metadata
    """
    db_entry = next(
        (qs for qs in session.output_package.routing.all_evaluated
         if qs.state_id == "decision_blindness"),
        None,
    )
    db_score = db_entry.score if db_entry else 0.0
    db_noise = db_entry.noise_baseline if db_entry else 0.0
    db_above_baseline = db_score >= db_noise

    pa_sources = []
    if any(e in _PROTECTED_ACTIVITY_INTAKE_EVENTS
           for e in session.intake.significant_events):
        pa_sources.append("intake_significant_events")
    if session.q_signal_decision_blindness:
        pa_sources.append("q_signal")

    protected_activity_confirmed = len(pa_sources) > 0
    flag_triggered = db_above_baseline and protected_activity_confirmed

    # Checkpoint 3: decision_blindness's OWN attributed StateSeverity, not
    # the session-wide/lead-state value -- this flag is specifically about
    # the decision_blindness state (hardcoded state_id just above),
    # unambiguous, no lead-state reasoning needed here. Explicit
    # get-then-unwrap, not a bare .get(id, "Emerging") -- state_severity's
    # values are StateSeverity objects now (Checkpoint 1 follow-on), so a
    # bare .get() with a string default would return a StateSeverity on
    # hit and a plain string on miss.
    _db_severity_entry = session.severity_result.state_severity.get("decision_blindness")
    db_severity_tier = (
        _db_severity_entry.tier if _db_severity_entry is not None else "Emerging"
    )

    db_flag = {
        "flag_id":   _DB_FLAG_ID,
        "triggered": flag_triggered,
        "trigger_conditions": {
            "state_id":                    "decision_blindness",
            "score_at_trigger":            round(db_score, 6),
            "score_threshold":             "noise_baseline",
            "protected_activity_confirmed": protected_activity_confirmed,
            "protected_activity_sources":   pa_sources,
        },
        "severity_context": {
            "decision_blindness_severity_floor": _DB_SEVERITY_FLOOR,
            "current_severity_reading": db_severity_tier.lower(),
        },
        "recommended_routes":           list(_DB_RECOMMENDED_ROUTES),
        "priority":                     "high",
        "internal_note":                _DB_INTERNAL_NOTE,
        "visible_to_principal":         False,
        "visible_to_resolution_specialist": True,
    }

    flags = [db_flag]
    return {
        "flags":            flags,
        "flag_count":       len(flags),
        "any_high_priority": any(
            f["triggered"] and f["priority"] == "high" for f in flags
        ),
    }


# ── Friction Tax Ledger (per-condition risk/dollar/top-contributing-answers,
# Gemini-cleared across two rounds) ─────────────────────────────────────────

# Build-time default, not a locked spec figure -- flagged for Pete alongside
# the row-count/UI-shape decision (Gemini's Q5 finding). Caps each ledger
# row's own answer list independently of how many state rows the ledger
# carries.
_LEDGER_TOP_ANSWERS_MAX = 3


def _build_friction_tax_ledger(
    identified_states: list,
    by_state: list,
    answers_log: list,
    intake_data: IntakeData,
) -> list:
    """
    Per-condition/state friction tax ledger row: risk label, dollar
    exposure, and a ranked top-contributing-answers list -- one row per
    entry in identified_states, in that same order.

    risk_label reuses each state's own severity tier from `by_state`
    (already computed by assemble_output() above) rather than a new
    risk-classification mechanism -- least-disruptive-contract, per
    Gemini's cleared architecture.

    dollar_exposure reuses compute_friction_tax() called with a single-
    element state_ids list, using THIS state's own tier (not the lead
    state's, unlike the aggregate friction_tax_estimate above) -- with
    exactly one identified state, compute_friction_tax()'s own combined-
    criterion aggregation collapses to that state's untouched criterion
    scores (confirmed by that function's own docstring and
    tools/test_friction_tax.py's continuity assertions), so this is a
    real per-state standalone estimate, not an approximation. None when
    that single-state call isn't calibration_complete (same null
    contract as friction_tax_estimate itself).

    top_contributing_answers reuses _build_signal_map_context()'s own
    replay technique (engine/main.py) -- a fresh scratch
    AccumulationSession per candidate option, salience-weighted dot
    product against SALIENCE_PROFILES[state_id] -- duplicated here
    rather than imported, since engine/main.py imports FROM this module
    and importing back would be circular; same "duplicate the technique,
    don't extract a cross-module helper" precedent
    _replay_partial_vector() already established alongside
    _build_signal_map_context() itself. answers_log entries carry
    option_ids (a list, widened from a singular option_id this session's
    A.2 Q06 weighted_multi_select work) -- every id in every entry is
    scored as its own independent candidate, matching
    _build_signal_map_context()'s per-option ranking unit exactly, not a
    per-entry combined score. Skip-and-backfill: an option with no
    authored observation_text is skipped outright, never padded with raw
    option_text -- same convention as _build_signal_map_context(). []
    when answers_log is empty (Path B/self-select has no real per-
    question answer history) or the state has no SALIENCE_PROFILES
    entry.

    [] when identified_states is empty (no_signal output_type) -- same
    "nothing to show" convention as friction_tax_estimate=None and
    severity.by_state=[].
    """
    if not identified_states:
        return []

    tier_by_state = {s["state_id"]: s["tier"] for s in by_state}

    ledger: list = []
    for s in identified_states:
        state_id = s["state_id"]
        risk_label = tier_by_state.get(state_id, "Emerging")

        friction_result = compute_friction_tax(
            state_ids=[state_id],
            severity_tier=risk_label,
            org_size=intake_data.headcount,
            industry=intake_data.industry,
            org_type=intake_data.org_type,
        )
        dollar_exposure = (
            {
                "low":      friction_result["low"],
                "high":     friction_result["high"],
                "currency": friction_result["currency"],
            }
            if friction_result["calibration_complete"]
            else None
        )

        salience = SALIENCE_PROFILES.get(state_id)
        scored: list = []
        if salience and answers_log:
            for entry in answers_log:
                question_id = entry.get("question_id") if isinstance(entry, dict) else None
                option_ids = entry.get("option_ids") if isinstance(entry, dict) else None
                if not isinstance(option_ids, list):
                    continue
                question = QUESTION_LIBRARY.get(question_id)
                if question is None:
                    continue
                for option_id in option_ids:
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

        top_contributing_answers: list = []
        for _, option in scored:
            if option.observation_text and option.observation_valence in PROBLEM_CONTEXT_VALENCES:
                top_contributing_answers.append(option.observation_text)
            if len(top_contributing_answers) == _LEDGER_TOP_ANSWERS_MAX:
                break

        ledger.append({
            "state_id":                 state_id,
            "state_name":               s["state_name"],
            "risk_label":               risk_label,
            "dollar_exposure":          dollar_exposure,
            "top_contributing_answers": top_contributing_answers,
        })

    return ledger


def lead_resolution_family(routing, private_block) -> str:
    """
    The result's resolution family in both routing modes. private.resolution_family
    is only populated in single-state mode, so multi-state results (most real
    results) fall back to the lead QualifiedState's family, the same source
    run_condensed_engine() uses. "" only when nothing qualified.
    """
    if private_block is not None and private_block.resolution_family:
        return private_block.resolution_family
    if routing is not None and routing.lead_state is not None:
        return routing.lead_state.resolution_family
    if routing is not None and routing.qualified_states:
        return routing.qualified_states[0].resolution_family
    return ""


def effective_resolution_family(routing, private_block, accumulated_vector) -> str:
    """
    The result's resolution family exactly as the report displays it: the
    lead state's family (lead_resolution_family) with the state's causation
    override applied (apply_causation_override, keyed by the causation
    pattern of accumulated_vector). The single source of truth for the
    displayed pathway AND the synthesis family (Call 1, the backup copy, the
    hr fallback key), so pathway and narrative always name the same service.
    """
    lead_id = (
        routing.lead_state.state_id if routing is not None and routing.lead_state
        else (routing.qualified_states[0].state_id
              if routing is not None and routing.qualified_states else None)
    )
    pattern_obj = compute_causation_pattern(accumulated_vector or {}, routing)
    pattern_type = pattern_obj.get("pattern") if isinstance(pattern_obj, dict) else None
    return apply_causation_override(
        state_id=lead_id,
        default_family=lead_resolution_family(routing, private_block),
        causation_pattern=pattern_type,
    )


# ── Phase 1 show-your-work: evidence receipts ──────────────────────────────
#
# EvidenceReceipt: {"category": str, "rationale": str, "triggering_answer"?: str}.
# triggering_answer is included ONLY when an authored observation_text
# exists for the condition. It is never padded with raw option_text.

_LEGAL_CLUSTER_LABELS = {
    1: "Individual employment claims",
    2: "Class or systemic discrimination",
    3: "Wage and hour",
    4: "Whistleblower and retaliation",
    5: "Workplace safety and regulatory",
}

_FRICTION_CHANNEL_LABELS = {
    "turnover":         "turnover",
    "productivity":     "lost productivity",
    "decision_quality": "weaker decisions",
}


def _usd(value: float) -> str:
    return f"${value:,.0f}"


def _join_words(items: list) -> str:
    if len(items) <= 1:
        return "".join(items)
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _top_observation_texts(
    state_id: str, answers_log: list, intake_data, limit: Optional[int] = 1,
) -> list:
    """
    The respondent's own answers most relevant to state_id, as authored
    observation_text only. Same replay-and-rank technique as
    _build_friction_tax_ledger() (a scratch AccumulationSession per
    selected option, salience-weighted against SALIENCE_PROFILES), kept
    separate rather than refactoring the ledger. Unauthored options are
    skipped, never replaced with raw option_text. Only problem-context
    valences (PROBLEM_CONTEXT_VALENCES) are cited. limit=None returns the
    full ranking.
    """
    salience = SALIENCE_PROFILES.get(state_id)
    if not salience or not answers_log:
        return []
    scored: list = []
    for entry in answers_log:
        if not isinstance(entry, dict):
            continue
        question = QUESTION_LIBRARY.get(entry.get("question_id"))
        option_ids = entry.get("option_ids")
        if question is None or not isinstance(option_ids, list):
            continue
        for option_id in option_ids:
            option = next((o for o in question.answer_options if o.option_id == option_id), None)
            if (
                option is None or not option.observation_text
                or option.observation_valence not in PROBLEM_CONTEXT_VALENCES
            ):
                continue
            scratch = AccumulationSession()
            accumulate_answer(scratch, option, intake_data, entry.get("question_id"))
            weight = sum(
                scratch.accumulated_vector.get(f, 0.0) * salience.get(f, 0.0)
                for f in DIMENSIONAL_FIELDS
            )
            if weight > 0:
                scored.append((weight, option.observation_text))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    texts: list = []
    for _, text in scored:
        if text not in texts:
            texts.append(text)
        if limit is not None and len(texts) == limit:
            break
    return texts


def _pick_distinct(ranked: list, used: set) -> Optional[str]:
    """The highest-ranked text not already cited by an earlier condition in
    the same receipt list. Falls back to the top one when every candidate
    is already used (reused rather than dropped). Records the pick."""
    if not ranked:
        return None
    pick = next((t for t in ranked if t not in used), ranked[0])
    used.add(pick)
    return pick


def _receipt(category: str, rationale: str, triggering_answer: Optional[str] = None) -> dict:
    receipt = {"category": category, "rationale": rationale}
    if triggering_answer:
        receipt["triggering_answer"] = triggering_answer
    return receipt


def _friction_driving_factors(
    friction_result: dict, identified_states: list, severity_tier: str,
    intake_data, answers_log: list,
) -> list:
    """The friction tax math, step by step, from compute_friction_tax()'s
    own intermediate figures. [] when uncalibrated."""
    c = friction_result.get("components")
    if not friction_result.get("calibration_complete") or not c:
        return []
    if c["org_type_scalar"] == 1.0:
        org_type_text = f"No adjustment for {intake_data.org_type} organizations."
    else:
        org_type_text = (
            f"Adjusted by a factor of {c['org_type_scalar']:.2f} for {intake_data.org_type} "
            f"organizations, giving a baseline of {_usd(c['adjusted_baseline'])}."
        )
    receipts = [
        _receipt(
            "Payroll baseline",
            f"Estimated annual payroll for a {friction_result['org_size_label']} person "
            f"{intake_data.industry} organization: {_usd(c['payroll_floor'])}.",
        ),
        _receipt("Organization type", org_type_text),
    ]
    used_answers: set = set()
    for s in identified_states:
        entry = STATE_MULTIPLIERS.get(s["state_id"])
        if entry is None:
            continue
        channels = [
            label for key, label in _FRICTION_CHANNEL_LABELS.items()
            if entry.criteria[key].score > 0
        ]
        if not channels:
            continue
        receipts.append(_receipt(
            "Condition",
            f"{s['state_name']} adds cost through {_join_words(channels)}.",
            _pick_distinct(
                _top_observation_texts(s["state_id"], answers_log, intake_data, limit=None),
                used_answers,
            ),
        ))
    share = (
        f"Together these conditions put {c['combined_multiplier']:.1%} of that baseline at risk"
    )
    if c["multi_channel_severity_loading"] > 1.0:
        share += (
            f", raised by a factor of {c['multi_channel_severity_loading']:.2f} because "
            f"the cost spreads across {c['breadth']} channels"
        )
    receipts.append(_receipt("Share of payroll at risk", share + "."))
    receipts.append(_receipt(
        "Severity",
        f"Multiplied by {c['severity_scalar']:.2f} for {severity_tier} severity.",
    ))
    receipts.append(_receipt(
        "Estimate",
        f"Low estimate {_usd(friction_result['low'])}. The high estimate is 1.4 times "
        f"the low, {_usd(friction_result['high'])}.",
    ))
    return receipts


def _legal_driving_factors(
    breakdown: list, identified_states: list, intake_data, answers_log: list,
) -> list:
    """One receipt per priced condition from
    compute_legal_per_state_breakdown(), plus how they combine. [] when
    nothing was priced."""
    if not breakdown:
        return []
    names = {s["state_id"]: s["state_name"] for s in identified_states}
    receipts = []
    used_answers: set = set()
    for b in breakdown:
        name = names.get(b["state_id"], b["state_id"])
        amount = (
            _usd(b["low"]) if b["low"] == b["high"]
            else f"{_usd(b['low'])} to {_usd(b['high'])}"
        )
        rationale = f"{name}: {amount}"
        if b["weight"] < 1.0:
            rationale += (
                f", counted at {b['weight']:.0%} because a larger exposure in the "
                "same category is already included"
            )
        receipts.append(_receipt(
            _LEGAL_CLUSTER_LABELS.get(b["cluster"], "Legal exposure"),
            rationale + ".",
            _pick_distinct(
                _top_observation_texts(b["state_id"], answers_log, intake_data, limit=None),
                used_answers,
            ),
        ))
    if len(breakdown) > 1:
        receipts.append(_receipt(
            "Total",
            "Within a category, overlapping exposures count at decreasing weight "
            "(full, half, then a quarter). Categories are then added together.",
        ))
    return receipts


# ── Phase 1 asset evidence ──────────────────────────────────────────────────

_ASSET_FIELDS = ("aptitude_asset", "authority_asset", "alliance_asset", "attitude_asset")
# Most quoted strength lines asset_evidence carries (Pete, 2026-09-28).
_ASSET_EVIDENCE_MAX = 5


def _derive_asset_baseline_question_ids() -> frozenset:
    """Questions whose options all carry the same nonzero asset values, so
    answering them adds asset signal whatever the answer (the question
    library's placeholder seeding). Derived, not hardcoded."""
    ids = set()
    for qid, q in QUESTION_LIBRARY.items():
        vectors = {
            tuple(round(o.dimensional_contributions.get(f, 0.0), 6) for f in _ASSET_FIELDS)
            for o in q.answer_options
        }
        if len(vectors) == 1 and any(next(iter(vectors))):
            ids.add(qid)
    return frozenset(ids)


_ASSET_BASELINE_QUESTION_IDS = _derive_asset_baseline_question_ids()


def _answer_dependent(question, field: str) -> bool:
    """True when the question's options actually differ on this field."""
    return len({round(o.dimensional_contributions.get(field, 0.0), 6) for o in question.answer_options}) > 1


def _selected_options(entry):
    if not isinstance(entry, dict):
        return None, []
    question = QUESTION_LIBRARY.get(entry.get("question_id"))
    option_ids = entry.get("option_ids")
    if question is None or not isinstance(option_ids, list):
        return None, []
    return question, [o for o in question.answer_options if o.option_id in option_ids]


def _build_asset_evidence(accumulated_vector: dict, answers_log: list, intake_data) -> Optional[dict]:
    """
    Where this respondent's own answers show strength. None (key omitted)
    when every net asset score is 0.0. See tools/patch_phase1_asset_evidence.py
    for the full rule set.
    """
    baseline = AccumulationSession()
    for entry in answers_log or []:
        if not isinstance(entry, dict) or entry.get("question_id") not in _ASSET_BASELINE_QUESTION_IDS:
            continue
        _, options = _selected_options(entry)
        for option in options:
            accumulate_answer(baseline, option, intake_data, entry.get("question_id"))

    net = {
        f: max(0.0, accumulated_vector.get(f, 0.0) - baseline.accumulated_vector.get(f, 0.0))
        for f in _ASSET_FIELDS
    }
    top = max(net.values())
    if top <= 1e-9:
        return None
    leading = [f for f in _ASSET_FIELDS if abs(net[f] - top) <= 1e-9]

    scored: list = []
    for entry in answers_log or []:
        question_id = entry.get("question_id") if isinstance(entry, dict) else None
        if not question_id or question_id.startswith("TC-") or question_id in _ASSET_BASELINE_QUESTION_IDS:
            continue
        question, options = _selected_options(entry)
        for option in options:
            # Strength evidence cites asset-valence text only: problem-phrased
            # text on an answer that happens to add asset signal is never a
            # strength.
            if not option.observation_text or option.observation_valence != "asset":
                continue
            scratch = AccumulationSession()
            accumulate_answer(scratch, option, intake_data, question_id)
            for f in leading:
                amount = scratch.accumulated_vector.get(f, 0.0)
                if amount > 0 and _answer_dependent(question, f):
                    scored.append((amount, f, option.observation_text))

    # Highest contribution to a leading axis first. The sort is stable and
    # answers_log is in question order, so ties keep question order.
    scored.sort(key=lambda item: item[0], reverse=True)
    signals: list = []
    seen: set = set()
    for _, f, text in scored:
        if text in seen:
            continue
        seen.add(text)
        signals.append({"axis": f.replace("_asset", ""), "observation_text": text})
        if len(signals) == _ASSET_EVIDENCE_MAX:
            break

    return {
        "strongest_axes": [f.replace("_asset", "") for f in leading],
        "contributing_signals": signals,
        "net_scores": {f.replace("_asset", ""): round(net[f], 4) for f in _ASSET_FIELDS},
    }


def assemble_output(
    session: SessionData, synthesis_result=None, trajectory_result=None, answers_log=None,
    brand: str = "principal_resolution", tactical_findings=None,
) -> dict:
    """
    Assemble the complete VII.1 engine output object from session data.

    Returns a dict that serializes directly to the contract-compliant JSON.
    Key names, data types, and field presence are immutable per spec VII.1.

    answers_log (Path 1 only, friction tax ledger build): optional list of
    {"question_id": str, "option_ids": list[str]} dicts, the same
    AnswerLogEntry shape run_accumulated_engine() (engine/main.py) threads
    through to _build_signal_map_context(). None or [] (the default)
    preserves every pre-existing caller's behavior exactly -- the ledger's
    risk_label/dollar_exposure per row are still computed (they don't
    depend on answers_log), only top_contributing_answers falls back to
    [] per row.

    LLM-generated text fields (private_output.liability_block, etc.) are
    empty strings in the assembled output. The application layer populates
    them before final delivery.

    Spec reference: Section VII.1
    """
    routing = session.output_package.routing
    sev = session.severity_result

    # Checkpoint 3 (SeverityResult per-state redesign): the top-level
    # "severity" object, urgency_window.response_window, and
    # compute_friction_tax()'s severity_tier param are all single
    # session-scoped scalars in the VII.1 schema (immutable field shape,
    # not per-state) -- resolved here as the LEAD/primary state's own
    # attributed StateSeverity rather than the old pooled session-wide
    # value. Real design decision, not dictated by the scoping doc: for
    # multi-state output, "the lead state's severity" is the most
    # defensible single answer a scalar field can give, matching how
    # asset_score/urgency_window's time_to_consequence already anchor on
    # lead_id elsewhere in this function.
    #
    # Fallback when the lead state has no attributed StateSeverity
    # (insufficient_signal mode, or a lead state with zero severity
    # inputs of its own): tier="Emerging", score_0_100=0.0 -- not two
    # independently invented defaults. classify_severity(normalize_severity
    # (0.0)) == "Emerging" exactly, so this is the same floor pair a
    # genuinely zero-input state would produce if run through the real
    # pipeline, confirmed by the pure functions themselves, not assumed.
    lead_severity_state_id = routing.lead_state.state_id if routing.lead_state else (
        routing.qualified_states[0].state_id if routing.qualified_states else None
    )
    _lead_severity_entry = sev.state_severity.get(lead_severity_state_id)
    lead_severity_tier = (
        _lead_severity_entry.tier if _lead_severity_entry is not None else "Emerging"
    )
    lead_severity_score_0_100 = (
        _lead_severity_entry.score_0_100 if _lead_severity_entry is not None else 0.0
    )

    # ── state_distribution — all states, sorted by score descending ──
    state_distribution = [
        {
            "state_id":   r.state_id,
            "state_name": STATE_PROFILES[r.state_id].state_name
                          if r.state_id in STATE_PROFILES else r.state_id,
            "score":      round(r.score, 6),
            "rank":       r.rank,
            "above_floor": any(
                qs.state_id == r.state_id and qs.cleared_floor
                for qs in routing.all_evaluated
            ),
            "descriptive_prose": STATE_PROFILES[r.state_id].descriptive_prose
                          if r.state_id in STATE_PROFILES else "",
        }
        for r in sorted(session.final_rankings, key=lambda r: -r.score)
    ]

    # ── output_type ──
    output_type_map = {
        "single":             "single_state",
        "multi":              "multi_state",
        "insufficient_signal": "no_signal",
    }
    output_type = output_type_map.get(routing.mode, "no_signal")

    # ── identified_states ──
    identified_states = []
    if routing.mode == "single" and routing.lead_state:
        identified_states = [{
            "state_id":              routing.lead_state.state_id,
            "state_name":            routing.lead_state.state_name,
            "score":                 round(routing.lead_state.score, 6),
            "descriptive_prose":     STATE_PROFILES[routing.lead_state.state_id].descriptive_prose
                                     if routing.lead_state.state_id in STATE_PROFILES else "",
            "distinguishing_language": None,  # null for single-state per spec
        }]
    elif routing.mode == "multi":
        identified_states = [
            {
                "state_id":              qs.state_id,
                "state_name":            qs.state_name,
                "score":                 round(qs.score, 6),
                "descriptive_prose":     STATE_PROFILES[qs.state_id].descriptive_prose
                                         if qs.state_id in STATE_PROFILES else "",
                "distinguishing_language": "",  # LLM-generated at application layer
            }
            for qs in routing.qualified_states
        ]

    # ── severity ──
    sev_inputs: dict = {}
    if sev.input_count > 0 and session.output_package.severity_result:
        # Input details are in the SeverityEngine — pulled from first input if present
        pass  # populated when full session pipeline wires SeverityAccumulator
    # Checkpoint 3 (Checkpoint 1 follow-on landed first, this session):
    # tier, score, AND anchor_text are now all resolved from the SAME
    # per-state StateSeverity entry -- the score/tier inconsistency the
    # original Checkpoint 3 dry-run flagged and left open (score staying
    # session-wide/pooled while tier/anchor_text became per-state) is
    # closed. sev.score_0_100_with_narrative (the old session-wide,
    # post-narrative-ceiling value) is no longer read here at all.
    # by_state (Visualize Your Data, Layer 1 -- VII.1 additive field,
    # commit pending): pure exposure of sev.state_severity filtered to
    # identified_states, no new computation. Mirrors the
    # lead_severity_tier/score fallback pattern above (get() -> is not
    # None check -> "Emerging"/0.0 default) rather than a new idiom.
    by_state = []
    for s in identified_states:
        _state_entry = sev.state_severity.get(s["state_id"])
        by_state.append({
            "state_id":    s["state_id"],
            "tier":        _state_entry.tier if _state_entry is not None else "Emerging",
            "score_0_100": _state_entry.score_0_100 if _state_entry is not None else 0.0,
        })

    severity_obj = {
        "tier":        lead_severity_tier,
        "score":       round(lead_severity_score_0_100, 2),
        "anchor_text": SEVERITY_TIER_DESCRIPTIONS.get(lead_severity_tier, ""),
        "inputs": {
            "duration_band":               None,  # from SeverityInput
            "population_band":             None,  # from SeverityInput
            "prior_attempts":              None,  # from SeverityInput
            "financial_indicators_present": None,  # from SeverityInput
            "named_condition":             None,  # from SeverityInput
        },
        "by_state": by_state,
    }

    # ── asset_score ──
    lead_id = routing.lead_state.state_id if routing.lead_state else (
        routing.qualified_states[0].state_id if routing.qualified_states else None
    )
    asset_obj = _compute_asset_score(session.accumulated_vector, lead_id)

    # ── dimension_summary ──
    dimension_obj = _compute_dimension_summary(session.accumulated_vector)

    # ── urgency_window ── (Diagnostic Dimension Expansion, Candidate 5)
    lead_profile = STATE_PROFILES.get(lead_id) if lead_id else None
    urgency_window_obj = {
        "time_to_consequence": derive_time_to_consequence(lead_profile) if lead_profile else None,
        # Checkpoint 3: lead_severity_tier, not sev.tier -- a 4th real
        # consumer found via exhaustive trace, not among the 3 sites
        # originally named for this checkpoint.
        "response_window":     synthesize_response_window(trajectory_result, lead_severity_tier),
    }

    # ── narrative_modulation ──
    narr = session.narrative_result
    pre_rankings = session.pre_narrative_rankings or session.final_rankings
    state_delta = 0.0
    if narr and routing.lead_state and pre_rankings:
        pre_score = next(
            (r.score for r in pre_rankings if r.state_id == routing.lead_state.state_id),
            0.0,
        )
        state_delta = round(
            routing.lead_state.score - pre_score, 6
        )

    narrative_obj = {
        "fired":             narr is not None,
        "trigger_point":     session.narrative_trigger,
        "overall_confidence": round(narr.overall_confidence, 4) if narr else 0.0,
        "signals_extracted": len(narr.identified_signals) if narr else 0,
        "state_delta":       state_delta,
        "severity_delta":    round(sev.narrative_contribution_0_100, 4),
    }

    # ── checkpoint_log ──
    checkpoint_log = {
        "q11": _checkpoint_entry(session.checkpoint_q11),
        "q19": _checkpoint_entry(session.checkpoint_q19),
        "q27": _checkpoint_entry(session.checkpoint_q27),
    }

    # ── jurisdiction_flags ──
    jurisdiction_flags = _assemble_jurisdiction_flags(session.intake)

    # ── private_output ──
    priv = session.output_package.private

    # causation_pattern routing override (Priority Queue item 2, Diagnostic
    # Dimension Expansion follow-on) -- reuses the routing/lead_id already
    # computed above (lines ~328/~400), not redeclared. causation_pattern is
    # computed once here and reused below for the private_output dict, rather
    # than calling compute_causation_pattern() a second time.
    causation_pattern_obj = compute_causation_pattern(session.accumulated_vector, routing)
    pattern_type = (
        causation_pattern_obj.get("pattern")
        if isinstance(causation_pattern_obj, dict)
        else None
    )
    # One definition shared with the synthesis call sites (engine/main.py),
    # so the displayed pathway and the narrative name the same service.
    effective_resolution_routing = effective_resolution_family(
        routing, priv, session.accumulated_vector,
    )

    friction_tax_result = compute_friction_tax(
        state_ids=[s["state_id"] for s in identified_states],
        # Checkpoint 3: lead_severity_tier, not sev.tier. compute_friction_tax()
        # itself is unchanged (out of scope, not one of this checkpoint's
        # named files) -- it takes one severity_tier scalar applied across
        # the full state_ids list, so the lead state's own tier is the only
        # per-state value this single-scalar call site can meaningfully use.
        severity_tier=lead_severity_tier,
        org_size=session.intake.headcount,
        industry=session.intake.industry,
        org_type=session.intake.org_type,
    )
    friction_tax_estimate = (
        {
            "low":      friction_tax_result["low"],
            "high":     friction_tax_result["high"],
            "currency": friction_tax_result["currency"],
            "driving_factors": _friction_driving_factors(
                friction_tax_result, identified_states, lead_severity_tier,
                session.intake, answers_log or [],
            ),
        }
        if friction_tax_result["calibration_complete"]
        else None
    )
    legal_result = compute_legal_compliance_exposure(
        state_ids=[s["state_id"] for s in identified_states],
        org_size=session.intake.headcount,
        industry=session.intake.industry,
        org_type=session.intake.org_type,
        jurisdictions=session.intake.jurisdictions,
    )
    legal_tail_risk_exposure = (
        {
            "low":                       legal_result["low"],
            "high":                      legal_result["high"],
            "currency":                  legal_result["currency"],
            "band":                      legal_result["band"],
            "caveat":                    LEGAL_TAIL_RISK_CAVEAT_TEXT,
            "has_unpriced_conditions":   legal_result["has_unpriced_conditions"],
            "unpriced_state_ids":        legal_result["unpriced_state_ids"],
            "coverage_basis":            legal_result["coverage_basis"],
            "has_partial_jurisdictions": legal_result["has_partial_jurisdictions"],
            "has_uncollected_net_worth_caveat": legal_result["has_uncollected_net_worth_caveat"],
            "specific_caveat": _SPECIFIC_CAVEAT_TEXT.get(legal_result["specific_caveat_jurisdiction"]),
            "driving_factors": _legal_driving_factors(
                compute_legal_per_state_breakdown(
                    state_ids=[s["state_id"] for s in identified_states],
                    org_size=session.intake.headcount,
                    industry=session.intake.industry,
                    org_type=session.intake.org_type,
                    jurisdictions=session.intake.jurisdictions,
                ),
                identified_states, session.intake, answers_log or [],
            ),
        }
        if legal_result["low"] is not None or legal_result["has_unpriced_conditions"]
        else None
    )
    friction_tax_ledger = _build_friction_tax_ledger(
        identified_states, by_state, answers_log or [], session.intake,
    )
    asset_evidence = _build_asset_evidence(
        session.accumulated_vector, answers_log or [], session.intake,
    )
    # service_cost_comparison (Phase 1, Pete: ship with nulls). Inaction
    # cost counts friction tax and legal exposure only where each is priced.
    _cost_parts = [
        (friction_tax_estimate["low"], friction_tax_estimate["high"])
        if friction_tax_estimate else None,
        (legal_tail_risk_exposure["low"], legal_tail_risk_exposure["high"])
        if legal_tail_risk_exposure and legal_tail_risk_exposure["low"] is not None else None,
    ]
    _cost_parts = [p for p in _cost_parts if p is not None]
    if brand == "hr_diagnostic":
        _target_service = HR_DIAGNOSTIC_FAMILY_NAME if effective_resolution_routing else ""
    else:
        _target_service = translate_resolution_family(effective_resolution_routing)
    service_cost_comparison = (
        {
            "target_service_name":   _target_service,
            "inaction_cost_low":     round(sum(p[0] for p in _cost_parts), 2) if _cost_parts else None,
            "inaction_cost_high":    round(sum(p[1] for p in _cost_parts), 2) if _cost_parts else None,
            "service_estimate_low":  None,
            "service_estimate_high": None,
            "pricing_model_note":    "",
        }
        if identified_states else None
    )
    private_output = {
        "opening_text":            priv.state_name if priv else "",
        "resolution_routing":      effective_resolution_routing,
        "friction_tax_estimate":   friction_tax_estimate,
        "friction_tax_ledger":     friction_tax_ledger,
        "legal_tail_risk_exposure": legal_tail_risk_exposure,
        "cascade_risk":            compute_cascade_risk(session.accumulated_vector),
        "causation_pattern":       causation_pattern_obj,
        "trajectory":            trajectory_result,
        "urgency_window":        urgency_window_obj,
    }
    # Omitted entirely, not an empty object, when there is no net
    # asset signal (Phase 1 spec).
    if asset_evidence is not None:
        private_output["asset_evidence"] = asset_evidence
    if service_cost_comparison is not None:
        private_output["service_cost_comparison"] = service_cost_comparison
    # Phase 1 Call 2 output: always a list, [] when the session has no
    # TC-* answers or the tactical call failed.
    private_output["tactical_findings"] = list(tactical_findings or [])
    # Every above-floor state, score-descending, in single AND multi mode
    # (identified_states keeps only the lead in single mode, and every
    # dollar figure is computed from identified_states, so this is a
    # separate silent field -- Pete, Phase 1). In private_output, not the
    # top level, which is pinned at 16 fields.
    private_output["all_qualified_states"] = [
        {
            "state_id":          qs.state_id,
            "state_name":        qs.state_name,
            "score":             round(qs.score, 6),
            "descriptive_prose": STATE_PROFILES[qs.state_id].descriptive_prose
                                 if qs.state_id in STATE_PROFILES else "",
        }
        for qs in routing.qualified_states
    ]

    # ── shareable_output ──
    sha = session.output_package.shareable
    shareable_output = {
        "attribution_text": sha.attribution if sha else
                            "Identified using the PRV3 diagnostic instrument.",
    }

    # ── synthesis ──
    synthesis_dict = (
        {
            "liability_condition_text":     synthesis_result.liability_condition_text,
            "asset_resolution_anchor_text": synthesis_result.asset_resolution_anchor_text,
            "framing_text":                 synthesis_result.framing_text,
            "observable_indicators":        synthesis_result.observable_indicators,
            "resolution_framing_text":      synthesis_result.resolution_framing_text,
            "headline":                     synthesis_result.headline,
            "synthesis_confidence":         synthesis_result.synthesis_confidence,
            "is_fallback":                  synthesis_result.is_fallback,
            # Why a fallback happened (API error, parse failure); None on
            # success. Additive -- consumers map named fields only. Read
            # by web/lib/diagnostic-completion.ts's [DIAG] log, never
            # forwarded to the client payload.
            "parse_error":                  synthesis_result.parse_error,
            # Phase 1 Call 3, "" when skipped or failed.
            "executive_summary":            getattr(synthesis_result, "executive_summary", ""),
        }
        if synthesis_result is not None
        else None
    )

    # ── intake echo ──
    intake_obj = {
        "headcount":          session.intake.headcount,
        "org_size":           session.intake.headcount,   # org_size band — resolved by friction_tax
        "industry":           session.intake.industry,
        "org_type":           session.intake.org_type,
        "jurisdictions":      list(session.intake.jurisdictions),
        "significant_events": list(session.intake.significant_events),
        "principal_role":     session.intake.principal_role,
        "significant_event_elaboration": session.intake.significant_event_elaboration,
    }

    return {
        "session_id":           session.session_id,
        "intake":               intake_obj,
        "state_distribution":   state_distribution,
        "output_type":          output_type,
        "identified_states":    identified_states,
        "severity":             severity_obj,
        "asset_score":          asset_obj,
        "dimension_summary":    dimension_obj,
        "narrative_modulation": narrative_obj,
        "checkpoint_log":       checkpoint_log,
        "jurisdiction_flags":   jurisdiction_flags,
        "private_output":       private_output,
        "shareable_output":     shareable_output,
        "synthesis":            synthesis_dict,
        "engine_version":       ENGINE_VERSION,
        "monitoring_metadata":  _assemble_monitoring_metadata(session),
    }


# ── VII.1  Schema Validation ───────────────────────────────────────────────────

# Required top-level fields and their expected Python types
_TOP_LEVEL_SCHEMA: dict[str, type] = {
    "session_id":          str,
    "intake":              dict,
    "state_distribution":  list,
    "output_type":         str,
    "identified_states":   list,
    "severity":            dict,
    "asset_score":         dict,
    "dimension_summary":   dict,
    "narrative_modulation": dict,
    "checkpoint_log":      dict,
    "jurisdiction_flags":  dict,
    "private_output":      dict,
    "shareable_output":    dict,
    "engine_version":      str,
    "monitoring_metadata": dict,
}

_OUTPUT_TYPE_VALUES = {"single_state", "multi_state", "no_signal"}

_SEVERITY_TIER_VALUES = {"Emerging", "Entrenched", "Endemic"}

_STATE_DISTRIBUTION_ENTRY_FIELDS = {
    "state_id": str, "state_name": str, "score": float,
    "rank": int, "above_floor": bool, "descriptive_prose": str,
}

_IDENTIFIED_STATE_FIELDS = {
    "state_id": str, "state_name": str, "score": float,
    "descriptive_prose": str,
    # distinguishing_language: str or None — validated separately
}

_SEVERITY_FIELDS = {"tier", "score", "anchor_text", "inputs"}
_ASSET_SCORE_FIELDS = {"score", "primary_asset_domain", "resolution_anchor_text"}
_DIMENSION_SUMMARY_FIELDS = {"aptitude", "authority", "alliance", "attitude"}
_NARRATIVE_FIELDS = {
    "fired", "trigger_point", "overall_confidence",
    "signals_extracted", "state_delta", "severity_delta",
}
_CHECKPOINT_LOG_KEYS = {"q11", "q19", "q27"}
_CHECKPOINT_ENTRY_FIELDS = {
    "entropy", "threshold", "threshold_exceeded", "distinguisher_fired",
}
_JURISDICTION_FLAGS_FIELDS = {
    "transparency", "retaliation", "procedural", "applied_multipliers",
}
_PRIVATE_OUTPUT_FIELDS = {
    "opening_text", "resolution_routing", "friction_tax_estimate",
    "friction_tax_ledger", "legal_tail_risk_exposure", "cascade_risk",
    "causation_pattern", "trajectory", "urgency_window",
}
_SHAREABLE_OUTPUT_FIELDS = {
    "attribution_text",
}
_SYNTHESIS_FIELDS = {
    "liability_condition_text", "asset_resolution_anchor_text",
    "framing_text", "observable_indicators", "resolution_framing_text",
    "headline", "synthesis_confidence", "is_fallback",
}
_INTAKE_FIELDS = {
    "headcount", "org_size", "industry", "org_type",
    "jurisdictions", "significant_events", "principal_role",
    "significant_event_elaboration",
}

_MONITORING_METADATA_FIELDS = {"flags", "flag_count", "any_high_priority"}

_FLAG_REQUIRED_FIELDS = {
    "flag_id", "triggered", "trigger_conditions", "severity_context",
    "recommended_routes", "priority", "internal_note",
    "visible_to_principal", "visible_to_resolution_specialist",
}


def validate_schema(output: dict) -> list:
    """
    Validate an engine output dict against the VII.1 contract.

    Returns a list of violation strings. Empty list = fully contract-compliant.

    Checks:
      - All 15 top-level fields present with correct types
      - output_type value in allowed enum
      - state_distribution entries have required fields and types
      - identified_states entries have required fields
      - severity tier value in allowed enum; required sub-fields present
      - asset_score, dimension_summary, narrative_modulation,
        checkpoint_log sub-fields present
      - jurisdiction_flags, private_output, shareable_output sub-fields present
      - intake echo has all six fields

    Spec reference: Section VII.1 — "key names, data types, field presence
    are immutable"
    """
    violations = []

    # Top-level fields
    for fname, ftype in _TOP_LEVEL_SCHEMA.items():
        if fname not in output:
            violations.append(f"MISSING top-level field: {fname!r}")
        elif not isinstance(output[fname], ftype):
            violations.append(
                f"WRONG TYPE for {fname!r}: "
                f"expected {ftype.__name__}, got {type(output[fname]).__name__}"
            )

    if violations:
        return violations  # can't safely check sub-fields if top-level broken

    # output_type enum
    if output["output_type"] not in _OUTPUT_TYPE_VALUES:
        violations.append(
            f"INVALID output_type: {output['output_type']!r}. "
            f"Must be one of {_OUTPUT_TYPE_VALUES}"
        )

    # state_distribution entries
    for i, entry in enumerate(output["state_distribution"]):
        for fname, ftype in _STATE_DISTRIBUTION_ENTRY_FIELDS.items():
            if fname not in entry:
                violations.append(
                    f"state_distribution[{i}] MISSING field {fname!r}"
                )
            elif not isinstance(entry[fname], ftype):
                violations.append(
                    f"state_distribution[{i}].{fname}: "
                    f"expected {ftype.__name__}, got {type(entry[fname]).__name__}"
                )

    # identified_states entries
    for i, entry in enumerate(output["identified_states"]):
        for fname, ftype in _IDENTIFIED_STATE_FIELDS.items():
            if fname not in entry:
                violations.append(
                    f"identified_states[{i}] MISSING field {fname!r}"
                )
            elif not isinstance(entry[fname], ftype):
                violations.append(
                    f"identified_states[{i}].{fname}: "
                    f"expected {ftype.__name__}, got {type(entry[fname]).__name__}"
                )
        if "distinguishing_language" not in entry:
            violations.append(
                f"identified_states[{i}] MISSING field 'distinguishing_language'"
            )

    # severity sub-fields
    sev = output["severity"]
    for f in _SEVERITY_FIELDS:
        if f not in sev:
            violations.append(f"severity MISSING field {f!r}")
    if "tier" in sev and sev["tier"] not in _SEVERITY_TIER_VALUES:
        violations.append(
            f"INVALID severity.tier: {sev['tier']!r}. "
            f"Must be one of {_SEVERITY_TIER_VALUES}"
        )

    # asset_score sub-fields
    for f in _ASSET_SCORE_FIELDS:
        if f not in output["asset_score"]:
            violations.append(f"asset_score MISSING field {f!r}")

    # dimension_summary sub-fields
    for f in _DIMENSION_SUMMARY_FIELDS:
        if f not in output["dimension_summary"]:
            violations.append(f"dimension_summary MISSING field {f!r}")

    # narrative_modulation sub-fields
    for f in _NARRATIVE_FIELDS:
        if f not in output["narrative_modulation"]:
            violations.append(f"narrative_modulation MISSING field {f!r}")

    # checkpoint_log structure
    cl = output["checkpoint_log"]
    for ck in _CHECKPOINT_LOG_KEYS:
        if ck not in cl:
            violations.append(f"checkpoint_log MISSING key {ck!r}")
        else:
            for f in _CHECKPOINT_ENTRY_FIELDS:
                if f not in cl[ck]:
                    violations.append(f"checkpoint_log.{ck} MISSING field {f!r}")

    # jurisdiction_flags sub-fields
    for f in _JURISDICTION_FLAGS_FIELDS:
        if f not in output["jurisdiction_flags"]:
            violations.append(f"jurisdiction_flags MISSING field {f!r}")

    # private_output sub-fields
    for f in _PRIVATE_OUTPUT_FIELDS:
        if f not in output["private_output"]:
            violations.append(f"private_output MISSING field {f!r}")

    # shareable_output sub-fields
    for f in _SHAREABLE_OUTPUT_FIELDS:
        if f not in output["shareable_output"]:
            violations.append(f"shareable_output MISSING field {f!r}")

    # intake echo fields
    for f in _INTAKE_FIELDS:
        if f not in output["intake"]:
            violations.append(f"intake MISSING field {f!r}")

    # synthesis — None or dict with 7 required fields
    if "synthesis" not in output:
        violations.append("MISSING top-level field: 'synthesis'")
    elif output["synthesis"] is not None:
        for f in _SYNTHESIS_FIELDS:
            if f not in output["synthesis"]:
                violations.append(f"synthesis MISSING field {f!r}")

    # monitoring_metadata
    mm = output["monitoring_metadata"]
    for f in _MONITORING_METADATA_FIELDS:
        if f not in mm:
            violations.append(f"monitoring_metadata MISSING field {f!r}")
    for i, flag in enumerate(mm.get("flags", [])):
        for f in _FLAG_REQUIRED_FIELDS:
            if f not in flag:
                violations.append(
                    f"monitoring_metadata.flags[{i}] MISSING field {f!r}"
                )

    return violations
