"""
Report 2: culture_drift capture breakdown — v17 (Session 23)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

# Import calibration infrastructure from runner
from tools.calibration_runner import (
    ALL_PROFILES, generate_answers, run_profile,
    _get_noise_baseline, best_option_for_state, _neutral_option,
    QUESTION_LIBRARY,
)
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.salience import SALIENCE_PROFILES
from engine.output import _PRECOMPUTED_NOISE_BASELINE
from engine.accumulation import AccumulationEngine, rank_states
from engine.severity import SeverityEngine
from engine.contract import SessionData, assemble_output
from engine.output import OutputEngine

# States that passed in v16
V16_PASSES = {
    "built_to_fail", "culture_drift", "decision_paralysis",
    "leadership_continuity_risk", "the_dormant_talent", "the_exposed",
    "the_founders_grip", "the_overloaded_manager", "the_policy_lag",
    "the_undefined_role", "the_unformed_leader", "the_uninitiated",
    "the_unsolved_problem", "transition_paralysis",
}

def run():
    baseline = _get_noise_baseline()

    cd_captures = {"HC": [], "extreme_HC": [], "moderate": [], "weak": []}
    ui_captures = {"HC": [], "extreme_HC": [], "moderate": [], "weak": []}
    other_captures = {}  # sink -> count

    state_cd_routes = {}  # state_id -> [profile_types that went to cd]

    # Run all profiles
    for tc in ALL_PROFILES:
        output = run_profile(tc)
        dist = output.get("state_distribution", [])
        rank1 = next((e["state_id"] for e in dist if e.get("rank") == 1), "insufficient_signal")
        target = tc.target_state
        ptype = tc.profile_type

        # Map profile_type to short label
        label_map = {
            "high_confidence": "HC",
            "extreme_high_confidence": "extreme_HC",
            "moderate": "moderate",
            "weak": "weak",
        }
        label = label_map.get(ptype, ptype)

        if rank1 != target:
            if rank1 == "culture_drift":
                cd_captures[label].append(target)
                if target not in state_cd_routes:
                    state_cd_routes[target] = []
                state_cd_routes[target].append(label)
            elif rank1 == "the_uninitiated":
                ui_captures[label].append(target)
            else:
                other_captures[rank1] = other_captures.get(rank1, 0) + 1

    all_cd = [s for lst in cd_captures.values() for s in lst]
    all_ui = [s for lst in ui_captures.values() for s in lst]
    cd_state_set = set(all_cd)

    # Regressions: v16 passes that now route to culture_drift
    regressions = [sid for sid in V16_PASSES if sid in state_cd_routes]

    # culture_drift salience profile and state vector
    cd_sal = SALIENCE_PROFILES.get("culture_drift", {})
    cd_profile = STATE_PROFILES.get("culture_drift")
    cd_vec = cd_profile.dimensional_vector if cd_profile else None
    cd_baseline = _PRECOMPUTED_NOISE_BASELINE.get("culture_drift", 0.0)
    ui_baseline = _PRECOMPUTED_NOISE_BASELINE.get("the_uninitiated", 0.0)

    FIELDS = [
        "aptitude_liability", "aptitude_asset",
        "authority_liability", "authority_asset",
        "alliance_liability", "alliance_asset",
        "attitude_liability", "attitude_asset",
    ]

    print("=" * 72)
    print("REPORT 2 — culture_drift Capture Breakdown — v17 (Session 23)")
    print("=" * 72)

    print(f"\n1. CULTURE_DRIFT SALIENCE PROFILE (weights in weighted cosine)")
    for f in FIELDS:
        print(f"   {f:<28}  {cd_sal.get(f, 0.0)}")

    print(f"\n2. CULTURE_DRIFT STATE VECTOR (dimensional_vector)")
    for f in FIELDS:
        val = getattr(cd_vec, f, 0.0) if cd_vec else 0.0
        print(f"   {f:<28}  {val}")

    print(f"\n3. NOISE BASELINE (v17)")
    print(f"   culture_drift:    {cd_baseline:.4f}  (floor at 1.08x = {cd_baseline*1.08:.4f})")
    print(f"   the_uninitiated:  {ui_baseline:.4f}  (floor at 1.00x = {ui_baseline*1.00:.4f})")

    print(f"\n4. RANK-1 CAPTURE TOTALS")
    print(f"   culture_drift:    {len(all_cd):3d} profiles")
    print(f"     HC:             {len(cd_captures['HC']):3d}")
    print(f"     extreme HC:     {len(cd_captures['extreme_HC']):3d}")
    print(f"     moderate:       {len(cd_captures['moderate']):3d}")
    print(f"     weak:           {len(cd_captures['weak']):3d}")
    print(f"   the_uninitiated:  {len(all_ui):3d} profiles")
    print(f"     HC:             {len(ui_captures['HC']):3d}")
    print(f"     extreme HC:     {len(ui_captures['extreme_HC']):3d}")
    print(f"     moderate:       {len(ui_captures['moderate']):3d}")
    print(f"     weak:           {len(ui_captures['weak']):3d}")

    print(f"\n5. STATES ROUTING TO CULTURE_DRIFT ({len(cd_state_set)} states)")
    for sid in sorted(cd_state_set):
        dim = STATE_PROFILES[sid].primary_dimension if sid in STATE_PROFILES else "?"
        types = state_cd_routes.get(sid, [])
        print(f"   {sid:<45}  {dim:<12}  [{', '.join(types)}]")

    print(f"\n6. REGRESSIONS — v16 passes now with culture_drift capture ({len(regressions)})")
    for sid in sorted(regressions):
        types = state_cd_routes.get(sid, [])
        print(f"   {sid:<45}  profiles captured: {types}")

    print()
    print("=" * 72)

if __name__ == "__main__":
    run()
