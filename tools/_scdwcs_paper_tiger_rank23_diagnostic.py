"""
Untracked scratch diagnostic -- NOT committed until Pete signs off on a
direction. Matches the tracker's tools/_scdwcs_*.py convention.

Purpose: confirm what's actually beating the_paper_tiger at rank 1-22
for APT-PT-00/01/02 (the calibration_runner --dim failures), and check
whether this matches the tracker's already-documented "still
occasionally loses to built_to_fail on built_to_fail's own turf"
disposition (the_paper_tiger's own row, prompts/scd-wcs-remediation-
tracker.md) or represents something bigger (rank-23 is a much larger
gap than a single-position "occasional" loss would suggest).

Reuses the real pipeline directly (tools.calibration_runner.run_profile)
rather than reimplementing engine wiring -- output shape matches
assemble_output()'s real state_distribution exactly, same source the
--dim table itself reads from.

Usage:
    python tools/_scdwcs_paper_tiger_rank23_diagnostic.py
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from engine.test_profiles import APT_PT_00, APT_PT_01, APT_PT_02
from engine.data.states import STATE_PROFILES
from engine.data.salience import SALIENCE_PROFILES
from tools.calibration_runner import run_profile

TEST_CASES = [APT_PT_00, APT_PT_01, APT_PT_02]


def main():
    print("=" * 80)
    print("the_paper_tiger -- rank-1 rival diagnostic (APT-PT-00/01/02)")
    print("=" * 80)

    for tc in TEST_CASES:
        output = run_profile(tc)
        dist = sorted(output.get("state_distribution", []), key=lambda e: e.get("rank", 99))

        print(f"\n[{tc.test_id}] profile_type={tc.profile_type!r} target={tc.target_state!r}")
        print("  Top 5:")
        for e in dist[:5]:
            marker = " <-- TARGET" if e.get("state_id") == tc.target_state else ""
            print(f"    rank {e.get('rank')}: {e.get('state_id', ''):40s} score={e.get('score', 0.0):.4f}{marker}")

        target_entry = next((e for e in dist if e.get("state_id") == tc.target_state), None)
        rank1 = dist[0] if dist else None
        if target_entry and rank1:
            gap = rank1.get("score", 0.0) - target_entry.get("score", 0.0)
            print(f"  Target actual: rank {target_entry.get('rank')}, score={target_entry.get('score'):.4f}, gap-to-rank1={gap:.4f}")
        else:
            print("  Target not found in state_distribution at all.")

    print("\n" + "=" * 80)
    print("the_paper_tiger's own live dimensional_vector:")
    dv = STATE_PROFILES["the_paper_tiger"].dimensional_vector
    print(f"  {dv}")
    print("the_paper_tiger's own live salience:")
    print(f"  {SALIENCE_PROFILES.get('the_paper_tiger')}")
    print()
    print("built_to_fail's own live dimensional_vector:")
    dv2 = STATE_PROFILES["built_to_fail"].dimensional_vector
    print(f"  {dv2}")
    print("built_to_fail's own live salience:")
    print(f"  {SALIENCE_PROFILES.get('built_to_fail')}")


if __name__ == "__main__":
    main()
