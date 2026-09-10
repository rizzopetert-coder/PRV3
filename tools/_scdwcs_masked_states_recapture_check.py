"""
Untracked scratch diagnostic -- NOT committed until Pete signs off on a
direction. Matches the tracker's tools/_scdwcs_*.py convention.

Purpose: answer the specific question Phase 8's "1 of 19 masked states
gaining anything" finding was measuring, but couldn't be answered from
today's false-rank-1 total alone -- for each state currently losing at
least one of its OWN dedicated profiles to built_to_fail (at the live
baseline), does built_to_fail's salience=0.25 candidate let the state
recapture its own profile at rank-1, or does the profile just go to a
DIFFERENT third-party rival instead of both built_to_fail and the true
target?

NOTE on scope: the literal named list of "Phase 8's original 19 masked
states" could not be recovered -- grepped both
prompts/scd-wcs-remediation-tracker.md and
prompts/scd-wcs-cluster-map-findings.md; the only "19" on record there
is the_unsolved_problem's own false-rank-1 count (one of the six
historically-dominant attacker states' own figures), not a separate
enumerated victim list, and the script that produced Phase 8's
original census (tools/_scdwcs_phase8_track2_diagnostic.py) was
untracked scratch, never committed, no longer present. Rather than
reconstruct a plausible-looking list and risk presenting it as the
real historical one, this uses TODAY's live, verifiable victim
population instead: every state that loses at least one of its own
dedicated profiles to built_to_fail at the current baseline
(salience=2.5). Flagged explicitly, not silently substituted.

Does NOT write to disk. Monkey-patches SALIENCE_PROFILES in memory,
restores the original afterward.

Usage:
    python tools/_scdwcs_masked_states_recapture_check.py
"""
import sys
import pathlib
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from engine.data.salience import SALIENCE_PROFILES
import tools.calibration_runner as cr

CANDIDATE_MAGNITUDE = 0.25


def run_rank1_map():
    """Returns {test_id: (target_state, rank1_state)} for the full 175-profile suite."""
    profiles = list(cr.ALL_PROFILES)
    result = {}
    for tc in profiles:
        output, _sev = cr._run_profile_core(tc)
        dist = output.get("state_distribution", [])
        rank1 = next((e["state_id"] for e in dist if e.get("rank") == 1), "insufficient_signal")
        result[tc.test_id] = (tc.target_state, rank1)
    return result


def own_profiles_by_state(rank1_map):
    """Groups test_ids by their true target_state."""
    grouped = defaultdict(list)
    for test_id, (target, _rank1) in rank1_map.items():
        grouped[target].append(test_id)
    return grouped


def main():
    original = dict(SALIENCE_PROFILES["built_to_fail"])

    print("=" * 92)
    print("Masked-state recapture check -- built_to_fail salience=0.25 candidate")
    print("Question: does each masked state recover its OWN profile, or does it")
    print("go to a different third-party rival instead?")
    print("=" * 92)

    # Baseline (live, unmodified)
    baseline_map = run_rank1_map()
    own_profiles = own_profiles_by_state(baseline_map)

    # Identify today's live victim population: states losing >=1 own profile to built_to_fail
    victims = []
    for state_id, test_ids in own_profiles.items():
        if state_id == "built_to_fail":
            continue
        btf_steals = [tid for tid in test_ids if baseline_map[tid][1] == "built_to_fail"]
        if btf_steals:
            victims.append(state_id)
    victims.sort()

    print(f"\nToday's live baseline victim population (states losing >=1 own profile")
    print(f"to built_to_fail, salience=2.5): {len(victims)} states")
    print(f"(NOT Phase 8's literal '19' -- that list could not be recovered; see docstring)")

    # Candidate run
    SALIENCE_PROFILES["built_to_fail"] = {
        "aptitude_liability": CANDIDATE_MAGNITUDE, "aptitude_asset": CANDIDATE_MAGNITUDE,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    }
    try:
        candidate_map = run_rank1_map()
    finally:
        SALIENCE_PROFILES["built_to_fail"] = original

    print(f"\n{'STATE':38s} {'BEFORE (2.5)':22s} {'AFTER (0.25)':22s} DISPOSITION")
    print("-" * 110)

    recovered = 0
    reassigned_to_third_party = 0
    still_lost_to_btf = 0

    for state_id in victims:
        test_ids = own_profiles[state_id]
        n = len(test_ids)
        before_wins = sum(1 for tid in test_ids if baseline_map[tid][1] == state_id)
        after_wins = sum(1 for tid in test_ids if candidate_map[tid][1] == state_id)
        before_btf = sum(1 for tid in test_ids if baseline_map[tid][1] == "built_to_fail")
        after_btf = sum(1 for tid in test_ids if candidate_map[tid][1] == "built_to_fail")

        # who wins each profile after, if not the true target and not built_to_fail
        after_others = [candidate_map[tid][1] for tid in test_ids
                         if candidate_map[tid][1] not in (state_id, "built_to_fail")]

        before_str = f"{before_wins}/{n} own, {before_btf}/{n} btf"
        after_str = f"{after_wins}/{n} own, {after_btf}/{n} btf"

        if after_wins == n:
            disposition = "FULLY RECOVERED (true target)"
            recovered += 1
        elif after_btf > 0:
            disposition = f"STILL LOST TO built_to_fail ({after_btf}/{n})"
            still_lost_to_btf += 1
        elif after_others:
            disposition = f"REASSIGNED to third party: {sorted(set(after_others))}"
            reassigned_to_third_party += 1
        else:
            disposition = f"PARTIAL recovery ({after_wins}/{n} own)"
            recovered += 1  # partial counts toward "not simply reassigned/still-lost"

        print(f"{state_id:38s} {before_str:22s} {after_str:22s} {disposition}")

    print("\n" + "=" * 92)
    print(f"Summary across {len(victims)} today-live masked states at salience=0.25:")
    print(f"  Fully or partially recovered by TRUE TARGET: {recovered}")
    print(f"  Reassigned to a DIFFERENT third-party rival (not target, not built_to_fail): {reassigned_to_third_party}")
    print(f"  STILL lost to built_to_fail specifically: {still_lost_to_btf}")


if __name__ == "__main__":
    main()
