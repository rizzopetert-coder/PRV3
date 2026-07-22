"""
PRV3 -- Severity Tier Validation (standalone, additive, isolated from v23)

Does NOT modify calibration_runner.py's _build_suite_v23() dispatch or the
tracked 169/172 baseline in any way. This is a separate, additive check.

Reuses evaluate_pass_criteria()'s existing tier-comparison logic (Emerging/
Entrenched +/-1 tolerance, Endemic exact-match only) WITHOUT its rank_1/
top_3/output_type checks. Scope: only the subset of the 172 profiles that
already pass under the CURRENT v23 criteria (_passes_cluster_criterion for
high_confidence/extreme_high_confidence, _passes_prominence_criterion for
moderate/weak -- exactly mirroring _build_suite_v23()'s own dispatch, not
reimplemented differently). Profiles that fail v23 on rank/output grounds
are excluded -- their severity tier isn't meaningfully testable while the
underlying state identification is already known-wrong.

Reports its own distinct number ("X of Y v23-passing profiles also match
expected severity tier") -- never to be merged into or reported alongside
169/172.

Usage:
  python tools/severity_tier_validation.py
"""
from __future__ import annotations

import sys
import types
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.path.insert(0, str(Path(__file__).parent))

from tools.calibration_runner import (
    run_profile, _passes_cluster_criterion, _passes_prominence_criterion,
)
from engine.test_profiles import APTITUDE_PROFILES
from engine.test_profiles_authority_b1 import AUTHORITY_B1_PROFILES
from engine.test_profiles_authority_b2 import AUTHORITY_B2_PROFILES
from engine.test_profiles_authority_b3 import AUTHORITY_B3_PROFILES
from engine.test_profiles_alliance import ALLIANCE_PROFILES
from engine.test_profiles_attitude_b1 import ATTITUDE_B1_PROFILES
from engine.test_profiles_attitude_b2 import ATTITUDE_B2_PROFILES
from engine.test_profiles_attitude_b3 import ATTITUDE_B3_PROFILES
from engine.test_profiles_expansion import EXPANSION_PROFILES

ALL_PROFILES = (
    APTITUDE_PROFILES + AUTHORITY_B1_PROFILES + AUTHORITY_B2_PROFILES +
    AUTHORITY_B3_PROFILES + ALLIANCE_PROFILES + ATTITUDE_B1_PROFILES +
    ATTITUDE_B2_PROFILES + ATTITUDE_B3_PROFILES + EXPANSION_PROFILES
)

# Severity tier ordering for the boundary tolerance check -- identical to
# engine/test_suite.py's evaluate_pass_criteria()._TIER_ORDER.
_TIER_ORDER = {"Emerging": 0, "Entrenched": 1, "Endemic": 2}


def _v23_passes(test_case, output: dict) -> bool:
    """Mirrors _build_suite_v23()'s per-profile-type dispatch exactly."""
    dist = sorted(output.get("state_distribution", []), key=lambda e: e.get("rank", 99))

    if test_case.profile_type in ("high_confidence", "extreme_high_confidence"):
        rankings = [
            types.SimpleNamespace(state_id=e.get("state_id", ""), score=e.get("score", 0.0))
            for e in dist
        ]
        return _passes_cluster_criterion(rankings, test_case.target_state)

    target = next((e for e in dist if e.get("state_id") == test_case.target_state), None)
    rank_1 = dist[0] if dist else None
    prominence_data = {
        "target_score": target.get("score", -999.0) if target else -999.0,
        "rank_1_score": rank_1.get("score", -999.0) if rank_1 else -999.0,
    }
    return _passes_prominence_criterion(prominence_data, test_case.profile_type)


def _tier_matches(expected_tier, actual_tier) -> bool:
    """Identical tolerance rule to engine/test_suite.py's evaluate_pass_criteria()."""
    if expected_tier is None:
        return True
    if actual_tier == expected_tier:
        return True
    exp_ord = _TIER_ORDER.get(expected_tier, -1)
    act_ord = _TIER_ORDER.get(actual_tier, -1)
    return abs(exp_ord - act_ord) == 1 and {exp_ord, act_ord} <= {0, 1}


def main() -> None:
    v23_pass_count = 0
    tier_match_count = 0
    mismatches: list[tuple[str, str, str, str]] = []
    tiers_seen: set[str] = set()

    for tc in ALL_PROFILES:
        output = run_profile(tc)
        tiers_seen.add(output["severity"]["tier"])

        if not _v23_passes(tc, output):
            continue
        v23_pass_count += 1

        actual_tier = output["severity"]["tier"]
        if _tier_matches(tc.expected.severity_tier, actual_tier):
            tier_match_count += 1
        else:
            mismatches.append((tc.test_id, tc.expected.severity_tier, actual_tier, tc.profile_type))

    print("=" * 72)
    print("PRV3 Severity Tier Validation (standalone -- not part of v23 baseline)")
    print("=" * 72)
    print(f"Total profiles: {len(ALL_PROFILES)}")
    print(f"Distinct actual severity tiers observed: {sorted(tiers_seen)}")
    print(f"v23-passing profiles (in-scope subset): {v23_pass_count}/{len(ALL_PROFILES)}")
    print(f"\nRESULT: {tier_match_count} of {v23_pass_count} v23-passing profiles "
          f"also match expected severity tier")

    if mismatches:
        by_expected = Counter(m[1] for m in mismatches)
        print(f"\nMismatches ({len(mismatches)} total), by expected tier: {dict(by_expected)}")
        for test_id, expected, actual, profile_type in mismatches:
            print(f"  [{test_id}] {profile_type}: expected {expected!r}, got {actual!r}")

    if tiers_seen == {"Emerging"}:
        print(
            "\nNOTE: every profile's actual tier is 'Emerging' -- generate_answers() "
            "(the calibration test harness) never simulates answering a SEVER-## "
            "follow-on question, so severity_inputs is empty for all 172 profiles "
            "regardless of the Path 1 engine wiring. This check cannot yet exercise "
            "duration_band's weight values at all -- see the script's module docstring."
        )

    print("=" * 72)


if __name__ == "__main__":
    main()
