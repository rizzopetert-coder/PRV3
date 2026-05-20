"""
v14 detailed analysis — the_uninitiated capture breakdown by profile type.
Read-only. No engine writes.

Outputs:
  1. Regressions from v13 (states that were passing, now 0/3)
  2. the_uninitiated rank-1 capture count by profile type
  3. HC profile rank-1 destination for every state
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.accumulation import IntakeData, AccumulationEngine
from engine.data.salience import SALIENCE_PROFILES
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.questions import QUESTION_LIBRARY
from engine.output import OutputEngine
from engine.severity import SeverityEngine
from engine.contract import SessionData, assemble_output
from engine.test_suite import run_test_case, PROFILE_TYPES

from engine.test_profiles import APTITUDE_PROFILES
from engine.test_profiles_authority_b1 import AUTHORITY_B1_PROFILES
from engine.test_profiles_authority_b2 import AUTHORITY_B2_PROFILES
from engine.test_profiles_authority_b3 import AUTHORITY_B3_PROFILES
from engine.test_profiles_alliance import ALLIANCE_PROFILES
from engine.test_profiles_attitude_b1 import ATTITUDE_B1_PROFILES
from engine.test_profiles_attitude_b2 import ATTITUDE_B2_PROFILES
from engine.test_profiles_attitude_b3 import ATTITUDE_B3_PROFILES

ALL_PROFILES = (
    APTITUDE_PROFILES
    + AUTHORITY_B1_PROFILES
    + AUTHORITY_B2_PROFILES
    + AUTHORITY_B3_PROFILES
    + ALLIANCE_PROFILES
    + ATTITUDE_B1_PROFILES
    + ATTITUDE_B2_PROFILES
    + ATTITUDE_B3_PROFILES
)

# Import calibration_runner helpers
sys.path.insert(0, str(Path(__file__).parent))
from calibration_runner import run_profile, generate_answers, _get_noise_baseline


def get_rank1(test_case) -> str:
    """Run one profile, return the rank-1 state_id."""
    result = run_profile(test_case)
    return result["state_distribution"][0]["state_id"]


# ── Single pass: run all 142 profiles ─────────────────────────────────────────

from engine.test_suite import run_test_case

uninitiated_by_type = {"high_confidence": [], "extreme_high_confidence": [], "moderate": [], "weak": []}
hc_rank1 = {}   # state_id -> rank-1 state
state_results = {sid: [] for sid in STATE_PROFILES}

print("Running 142 profiles... (this takes ~30s)")

for tc in ALL_PROFILES:
    engine_out = run_profile(tc)
    r1 = engine_out["state_distribution"][0]["state_id"]
    result = run_test_case(tc, engine_out)
    ptype = tc.profile_type
    sid = tc.target_state
    state_results[sid].append(result.passed)
    if r1 == "the_uninitiated":
        uninitiated_by_type.setdefault(ptype, []).append(sid)
    if ptype in ("high_confidence", "extreme_high_confidence"):
        hc_rank1[sid] = r1

# ── 1. Regressions (0/3 in v14, were passing in v13) ─────────────────────────

V13_PASSING = {
    "built_to_fail", "culture_drift", "decision_paralysis",
    "leadership_continuity_risk", "the_founders_grip", "the_policy_lag",
    "the_unexamined_algorithm", "the_undefined_role", "the_unformed_leader",
    "the_uninitiated", "transition_paralysis",
}

v14_zero = {sid for sid, results in state_results.items() if not any(results)}
regressions = v14_zero & V13_PASSING

print("\n" + "="*64)
print("1. REGRESSIONS — states passing in v13, now 0/3 in v14")
print("="*64)
if regressions:
    for sid in sorted(regressions):
        hc_dest = hc_rank1.get(sid, "n/a")
        print(f"  {sid:<45} HC rank-1 -> {hc_dest}")
else:
    print("  None")

# ── 2. the_uninitiated rank-1 captures by profile type ────────────────────────

print("\n" + "="*64)
print("2. THE_UNINITIATED rank-1 captures by profile type")
print("="*64)
for ptype in ["high_confidence", "extreme_high_confidence", "moderate", "weak"]:
    captures = uninitiated_by_type.get(ptype, [])
    print(f"  {ptype:<30} {len(captures):>3} captures")
    if captures:
        for sid in sorted(captures):
            print(f"    {sid}")

# ── 3. HC rank-1 destination — all 47 states ─────────────────────────────────

print("\n" + "="*64)
print("3. HC rank-1 destination — all 47 HC profiles")
print("="*64)
dest_counts = {}
for sid in sorted(hc_rank1.keys()):
    dest = hc_rank1[sid]
    dest_counts[dest] = dest_counts.get(dest, 0) + 1
    marker = "CORRECT" if dest == sid else f"-> {dest}"
    print(f"  {sid:<45} {marker}")

print(f"\nHC rank-1 destination summary:")
for dest in sorted(dest_counts, key=lambda d: -dest_counts[d]):
    print(f"  {dest:<45} {dest_counts[dest]:>3}x")

print("="*64)
