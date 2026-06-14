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


def run_engine(payload: dict) -> dict:
    """
    Accept web layer payload, return 14-field JSON contract dict.

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
        }
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

    session_data = SessionData(
        session_id=SessionData.new_session_id(),
        intake=intake_data,
        final_rankings=final_rankings,
        accumulated_vector={},
        output_package=output_package,
        severity_result=severity_result,
    )

    return assemble_output(session_data)
