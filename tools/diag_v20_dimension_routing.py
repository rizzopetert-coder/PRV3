"""
Diagnostic: v20 dimension routing check — Alliance + Aptitude HC profiles.

For each Alliance and Aptitude HC profile, runs generate_answers() then
accumulate_answer() and reports identify_dominant_dimension() result.

Confirms whether the router correctly routes each HC profile to its target
state's primary_dimension before the full Phase 2 calibration is run.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.accumulation import (
    AccumulationEngine, IntakeData, identify_dominant_dimension,
)
from engine.data.questions import QUESTION_LIBRARY
from engine.data.states import STATE_PROFILES

from tools.calibration_runner import (
    ALL_PROFILES, generate_answers,
)

TARGET_DIMS = {"Alliance", "Aptitude"}

profiles_to_check = [
    p for p in ALL_PROFILES
    if p.profile_type == "high_confidence"
    and STATE_PROFILES.get(p.target_state) is not None
    and STATE_PROFILES[p.target_state].primary_dimension in TARGET_DIMS
]

print(f"\nv20 Dimension Routing Diagnostic — Alliance + Aptitude HC profiles")
print(f"=" * 72)
print(f"Profiles checked: {len(profiles_to_check)}\n")

print(f"  {'test_id':<14} {'target_state':<34} {'target_dim':<12} {'router_dim':<12} {'match'}")
print(f"  {'-'*14} {'-'*34} {'-'*12} {'-'*12} {'-'*5}")

correct = 0
wrong = 0

for tc in sorted(profiles_to_check, key=lambda p: (STATE_PROFILES[p.target_state].primary_dimension, p.target_state)):
    intake = IntakeData(**tc.intake)
    acc_engine = AccumulationEngine(intake)

    answers = generate_answers(tc)
    for ans in answers:
        q = QUESTION_LIBRARY.get(ans.question_id)
        if q is None:
            continue
        for opt_id in ans.selected_option_ids:
            opt = next((o for o in q.answer_options if o.option_id == opt_id), None)
            if opt is None:
                continue
            acc_engine.apply_answer(opt, ans.question_id)

    dominant_dim, magnitudes = identify_dominant_dimension(acc_engine.accumulated_vector)
    target_dim = STATE_PROFILES[tc.target_state].primary_dimension
    match = "OK" if dominant_dim == target_dim else "FAIL"

    if dominant_dim == target_dim:
        correct += 1
    else:
        wrong += 1

    print(f"  {tc.test_id:<14} {tc.target_state:<34} {target_dim:<12} {dominant_dim:<12} {match}")

    # On mismatch: show all 4 dimension magnitudes for diagnosis
    if dominant_dim != target_dim:
        for dim in ["Authority", "Aptitude", "Alliance", "Attitude"]:
            marker = " <-- dominant" if dim == dominant_dim else (" <-- target" if dim == target_dim else "")
            print(f"    {dim:<12}: {magnitudes[dim]:.4f}{marker}")

print(f"\nResult: {correct}/{len(profiles_to_check)} correct routing  "
      f"({wrong} mismatch{'es' if wrong != 1 else ''})")

if wrong == 0:
    print("All Alliance and Aptitude HC profiles route to correct dimension. Safe to proceed.")
else:
    print(f"[WARN] {wrong} profile(s) route to wrong dimension — router will fail for these.")
