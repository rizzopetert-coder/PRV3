"""
Untracked scratch diagnostic -- NOT committed until Pete signs off on a
direction. Matches the tracker's tools/_scdwcs_*.py convention.

Purpose: empirically re-test whether lowering built_to_fail's own
aptitude salience (the exact lever prompts/scd-wcs-remediation-
tracker.md's Phase 8 already tested and found unfixable via
salience-alone, "whack-a-mole... ceiling stuck at 1 of 19 masked
states gaining anything") specifically recovers the_paper_tiger's own
3 dedicated profiles (APT-PT-00/01/02), and whether it costs any
currently-passing profile elsewhere in the full 175-profile suite.

This does NOT write to disk. It monkey-patches SALIENCE_PROFILES in
memory for the duration of the run, restores the original afterward,
and only prints results -- a margin search / candidate-scoping pass,
per the diagnosis-only brief.

Usage:
    python tools/_scdwcs_paper_tiger_btf_salience_search.py
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from engine.data.salience import SALIENCE_PROFILES
import tools.calibration_runner as cr

CANDIDATES = [2.5, 1.0, 0.5, 0.25, 0.1]  # 2.5 = current/live, baseline for comparison


def run_full_suite():
    profiles = list(cr.ALL_PROFILES)
    engine_outputs = {}
    state_severity_map = {}
    for tc in profiles:
        output, sev_result = cr._run_profile_core(tc)
        engine_outputs[tc.test_id] = output
        state_severity_map[tc.test_id] = sev_result.state_severity
    suite = cr._build_suite_v23(profiles, engine_outputs, state_severity_map)
    return suite, engine_outputs


def passing_set(suite):
    return {r.test_id for r in suite["results"] if r.passed}


def main():
    original = dict(SALIENCE_PROFILES["built_to_fail"])
    print("=" * 80)
    print("built_to_fail aptitude-salience margin search -- effect on the_paper_tiger")
    print("=" * 80)
    print(f"Original built_to_fail salience: {original}")

    baseline_suite, _ = run_full_suite()
    baseline_pass = passing_set(baseline_suite)
    baseline_total_pass = len(baseline_pass)
    print(f"\nBaseline (live, unmodified): {baseline_total_pass}/175 passing")
    for tid in ("APT-PT-00", "APT-PT-01", "APT-PT-02"):
        print(f"  {tid}: {'PASS' if tid in baseline_pass else 'FAIL'}")

    try:
        for magnitude in CANDIDATES:
            SALIENCE_PROFILES["built_to_fail"] = {
                "aptitude_liability": magnitude, "aptitude_asset": magnitude,
                "authority_liability": 0.4, "authority_asset": 0.4,
                "alliance_liability": 0.4, "alliance_asset": 0.4,
                "attitude_liability": 0.4, "attitude_asset": 0.4,
            }
            suite, _ = run_full_suite()
            cur_pass = passing_set(suite)
            total = len(cur_pass)
            gained = cur_pass - baseline_pass
            lost = baseline_pass - cur_pass
            print(f"\n--- built_to_fail aptitude salience = {magnitude} ---")
            print(f"  Total: {total}/175 (delta {total - baseline_total_pass:+d})")
            for tid in ("APT-PT-00", "APT-PT-01", "APT-PT-02"):
                print(f"  {tid}: {'PASS' if tid in cur_pass else 'FAIL'}")
            print(f"  Newly passing ({len(gained)}): {sorted(gained)}")
            print(f"  Newly failing / regressed ({len(lost)}): {sorted(lost)}")
    finally:
        SALIENCE_PROFILES["built_to_fail"] = original
        print("\n(restored built_to_fail's live salience to original)")


if __name__ == "__main__":
    main()
