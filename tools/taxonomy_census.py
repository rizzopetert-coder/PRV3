"""
SCD-WCS taxonomy census: enumerate every state sharing the over-dominant
pattern identified in Phase 8 Stage C -- standard "primary-only" salience
template (dominant axis 2.5/2.5, else flat 0.4/0.4) paired with a
liability-skewed dimensional_vector on that same dominant axis.

Relocated and tracked this session (was tools/_scdwcs_full_taxonomy_
census.py, untracked scratch) as a standalone, permanent utility --
structural/metadata scan over STATE_PROFILES/SALIENCE_PROFILES, a
genuinely different purpose from tools/scdwcs_validator.py (calibration
measurement) and tools/scdwcs_candidate_search.py (candidate sweep), so
deliberately not folded into either. Content unchanged from the original
script; only this docstring's provenance note is new.

Enumeration only, no fix.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.states import STATE_PROFILES
from engine.data.salience import SALIENCE_PROFILES

AXES = ("aptitude", "authority", "alliance", "attitude")

STANDARD_TEMPLATE_DOMINANT = 2.5
STANDARD_TEMPLATE_FLOOR = 0.4
SKEW_RATIO_THRESHOLD = 2.0  # liability >= 2x asset on the dominant axis


def get_salience(state_id: str):
    # States with no custom entry get uniform 1.0 weight on every field at
    # the real engine level (engine/accumulation.py rank(), not a 0.4/0.4
    # floor) -- they cannot match the primary-only template by definition,
    # so returning None here (rather than inventing a default dict) is
    # correct: matches_standard_template() below returns None for it.
    return SALIENCE_PROFILES.get(state_id)


def vector_axis_values(profile, axis: str):
    return getattr(profile.dimensional_vector, f"{axis}_liability"), getattr(profile.dimensional_vector, f"{axis}_asset")


def matches_standard_template(sal):
    """Return the dominant axis name if sal is EXACTLY one axis at 2.5/2.5
    and the other three at flat 0.4/0.4, else None."""
    if sal is None:
        return None
    dominant_axes = []
    for axis in AXES:
        lia = sal.get(f"{axis}_liability")
        ast = sal.get(f"{axis}_asset")
        if lia == STANDARD_TEMPLATE_DOMINANT and ast == STANDARD_TEMPLATE_DOMINANT:
            dominant_axes.append(axis)
        elif lia == STANDARD_TEMPLATE_FLOOR and ast == STANDARD_TEMPLATE_FLOOR:
            continue
        else:
            return None  # doesn't match the exact pattern
    if len(dominant_axes) == 1:
        return dominant_axes[0]
    return None


def main():
    print(f"Total states in registry: {len(STATE_PROFILES)}")
    print(f"\n{'=' * 100}\nSTEP 1: Template + vector-skew match sweep\n{'=' * 100}")

    candidates = []
    template_matches_no_skew = []

    for state_id, profile in STATE_PROFILES.items():
        sal = get_salience(state_id)
        dominant_axis = matches_standard_template(sal)
        if dominant_axis is None:
            continue

        lia, ast = vector_axis_values(profile, dominant_axis)
        ratio = (lia / ast) if ast > 0 else float("inf")
        skewed = ratio >= SKEW_RATIO_THRESHOLD

        row = {
            "state_id": state_id, "dominant_axis": dominant_axis,
            "vector_liability": lia, "vector_asset": ast, "ratio": ratio, "skewed": skewed,
        }
        if skewed:
            candidates.append(row)
        else:
            template_matches_no_skew.append(row)

    print(f"\nStates matching standard primary-only template AND liability-skewed (ratio>={SKEW_RATIO_THRESHOLD}): {len(candidates)}")
    for r in sorted(candidates, key=lambda x: -x["ratio"]):
        print(f"  {r['state_id']:38s} axis={r['dominant_axis']:10s} vector={r['vector_liability']:.2f}/{r['vector_asset']:.2f}  ratio={r['ratio']:.2f}")

    print(f"\nStates matching template but NOT meaningfully skewed (ratio<{SKEW_RATIO_THRESHOLD}), for completeness: {len(template_matches_no_skew)}")
    for r in sorted(template_matches_no_skew, key=lambda x: -x["ratio"]):
        print(f"  {r['state_id']:38s} axis={r['dominant_axis']:10s} vector={r['vector_liability']:.2f}/{r['vector_asset']:.2f}  ratio={r['ratio']:.2f}")

    # Explicit check for invisible_performance_management (multi-axis, may not match template at all)
    print(f"\n{'=' * 100}\nEXPLICIT CHECK: invisible_performance_management\n{'=' * 100}")
    ipm_sal = get_salience("invisible_performance_management")
    print(f"  salience: {ipm_sal}")
    ipm_profile = STATE_PROFILES["invisible_performance_management"]
    for axis in AXES:
        lia, ast = vector_axis_values(ipm_profile, axis)
        print(f"  {axis:10s} liability={lia:.2f} asset={ast:.2f}")
    print(f"  Standard-template match: {matches_standard_template(ipm_sal)}")

    census_path = Path(__file__).parent / "data" / "scdwcs_census_candidates.txt"
    census_path.parent.mkdir(parents=True, exist_ok=True)
    with open(census_path, "w", encoding="utf-8") as f:
        for r in candidates:
            f.write(f"{r['state_id']}\n")
    print(f"\nWrote {len(candidates)} candidate state_ids to {census_path}")


if __name__ == "__main__":
    main()
