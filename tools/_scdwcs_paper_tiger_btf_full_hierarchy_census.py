"""
Untracked scratch diagnostic -- NOT committed until Pete signs off on a
direction. Matches the tracker's tools/_scdwcs_*.py convention.

Purpose: re-run the built_to_fail aptitude_liability/aptitude_asset
salience-suppression candidate (magnitudes 1.0/0.5/0.25/0.1, same
values already screened via the narrower 175-profile pass/fail delta
in tools/_scdwcs_paper_tiger_btf_salience_search.py) through the
tracker's own full-hierarchy false-rank-1 census methodology -- the
standard used throughout Phase 8/9 (build_confusion_matrix()'s
matrix[target_state][rank1_state], counting every profile across the
full 175 where built_to_fail wins rank-1 despite NOT being that
profile's real target), not just this candidate's own 3 dedicated
profiles or the narrower pass/fail total.

This is the rigor check before Pete decides whether to reopen the
2026-08-28 park on built_to_fail's Track 2 disposition. Does NOT write
to disk. Monkey-patches SALIENCE_PROFILES in memory per magnitude,
restores the original afterward.

Usage:
    python tools/_scdwcs_paper_tiger_btf_full_hierarchy_census.py
"""
import sys
import pathlib
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from engine.data.salience import SALIENCE_PROFILES
import tools.calibration_runner as cr

CANDIDATES = [2.5, 1.0, 0.5, 0.25, 0.1]  # 2.5 = current/live baseline
BTF_OWN_PROFILES = ["APT-BF-01", "APT-BF-02", "APT-BF-03"]


def run_and_census():
    profiles = list(cr.ALL_PROFILES)
    run_results = []
    for tc in profiles:
        output, _sev = cr._run_profile_core(tc)
        run_results.append((tc, output))
    matrix = cr.build_confusion_matrix(run_results)
    return run_results, matrix


def false_rank1_breakdown(matrix, state_id):
    """Every profile whose TRUE target is NOT state_id, but whose rank-1 IS state_id."""
    victims = Counter()
    total = 0
    for target, preds in matrix.items():
        if target == state_id:
            continue
        cnt = preds.get(state_id, 0)
        if cnt:
            victims[target] = cnt
            total += cnt
    return total, victims


def own_profile_capture(run_results, state_id, own_profile_ids):
    wins = 0
    for tc, output in run_results:
        if tc.test_id not in own_profile_ids:
            continue
        dist = output.get("state_distribution", [])
        rank1 = next((e["state_id"] for e in dist if e.get("rank") == 1), None)
        if rank1 == state_id:
            wins += 1
    return wins


def main():
    original = dict(SALIENCE_PROFILES["built_to_fail"])
    print("=" * 88)
    print("built_to_fail -- full-hierarchy false-rank-1 census, salience-suppression candidate")
    print("Methodology: build_confusion_matrix()'s matrix[target][rank1], same standard as")
    print("Phase 8/9 of prompts/scd-wcs-remediation-tracker.md")
    print("=" * 88)

    try:
        for magnitude in CANDIDATES:
            SALIENCE_PROFILES["built_to_fail"] = {
                "aptitude_liability": magnitude, "aptitude_asset": magnitude,
                "authority_liability": 0.4, "authority_asset": 0.4,
                "alliance_liability": 0.4, "alliance_asset": 0.4,
                "attitude_liability": 0.4, "attitude_asset": 0.4,
            }
            run_results, matrix = run_and_census()
            total, victims = false_rank1_breakdown(matrix, "built_to_fail")
            own_wins = own_profile_capture(run_results, "built_to_fail", BTF_OWN_PROFILES)

            label = "LIVE/BASELINE" if magnitude == 2.5 else f"magnitude={magnitude}"
            print(f"\n--- built_to_fail aptitude salience = {magnitude} ({label}) ---")
            print(f"  False-rank-1 total: {total}/175 ({total/175*100:.1f}%)")
            print(f"  Own-profile capture (APT-BF-01/02/03): {own_wins}/3")
            if victims:
                print("  Victim breakdown (true_target: profiles stolen):")
                for tgt, cnt in sorted(victims.items(), key=lambda kv: -kv[1]):
                    print(f"    {tgt:40s} {cnt}")
            else:
                print("  Victim breakdown: none")
    finally:
        SALIENCE_PROFILES["built_to_fail"] = original
        print("\n(restored built_to_fail's live salience to original)")


if __name__ == "__main__":
    main()
