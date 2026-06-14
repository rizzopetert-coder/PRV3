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

from engine.accumulation import IntakeData, StateRanking
from engine.severity import SeverityEngine
from engine.output import OutputEngine
from engine.contract import SessionData, assemble_output
from engine.data.states import STATE_PROFILES
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
