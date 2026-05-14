"""
PRV3 Patch — Authority HIGH Vector Sharpen (Session 16 Task 1)

Replaces the 6 Authority HIGH state vectors with a single-axis sharpened form:
  authority_liability = 0.60
  all 7 other fields  = 0.15

All 15 pairwise cosine similarities = 1.000000 (accepted — Gemini concession).
Cosine to neutral centroid: ~0.811 (down from ~0.931 for v4 and ~0.930 for v5b).

usage:
  python tools/patch_auth_sharpen.py --dry-run
  python tools/patch_auth_sharpen.py --write
"""

import sys
import math
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "states.py"

FIELD_ORDER = [
    "aptitude_liability",  "aptitude_asset",
    "authority_liability", "authority_asset",
    "alliance_liability",  "alliance_asset",
    "attitude_liability",  "attitude_asset",
]

# All 6 Authority HIGH states receive the same sharpened single-axis vector
AUTH_HIGH_IDS = [
    "the_founders_grip",
    "the_exposed",
    "hr_capture",
    "heard_and_ignored",
    "the_tolerated_violation",
    "the_unsolved_problem",
]

SHARPEN_VECTOR = {
    "aptitude_liability":  0.15,
    "aptitude_asset":      0.15,
    "authority_liability": 0.60,
    "authority_asset":     0.15,
    "alliance_liability":  0.15,
    "alliance_asset":      0.15,
    "attitude_liability":  0.15,
    "attitude_asset":      0.15,
}


def make_override_block(state_id: str, vec: dict) -> str:
    field_lines = "\n".join(
        f"    {f}={vec[f]:.2f},"
        for f in FIELD_ORDER
    )
    return (
        f'STATE_PROFILES["{state_id}"].dimensional_vector = DimensionalVector(\n'
        f"{field_lines}\n"
        f")"
    )


def cosine_sim(a: dict, b: dict) -> float:
    dot   = sum(a[f] * b[f] for f in FIELD_ORDER)
    mag_a = math.sqrt(sum(a[f] ** 2 for f in FIELD_ORDER))
    mag_b = math.sqrt(sum(b[f] ** 2 for f in FIELD_ORDER))
    if mag_a < 1e-10 or mag_b < 1e-10:
        return 0.0
    return dot / (mag_a * mag_b)


def dry_run_verification() -> None:
    neutral = {f: 0.25 for f in FIELD_ORDER}

    sim_to_neutral = cosine_sim(SHARPEN_VECTOR, neutral)
    print(f"\n  New vector cosine to neutral centroid: {sim_to_neutral:.6f}")

    if sim_to_neutral > 0.95:
        print(f"  FLAG: cosine {sim_to_neutral:.4f} > 0.95 — stop and report to Pete")
        sys.exit(1)
    else:
        print(f"  Gate: PASS — below 0.95")

    pairwise = cosine_sim(SHARPEN_VECTOR, SHARPEN_VECTOR)
    print(f"\n  Pairwise cosine between any two Authority HIGH states: {pairwise:.6f}")
    print(f"  (All 15 pairs identical — accepted per spec)")


def find_existing_override(content: str, state_id: str) -> tuple[int, int] | None:
    marker = f'STATE_PROFILES["{state_id}"].dimensional_vector = DimensionalVector('
    start = content.find(marker)
    if start == -1:
        return None
    end = content.find(")\n", start)
    if end == -1:
        return None
    return start, end + 2  # include the closing ")\n"


def apply_patches(content: str, dry_run: bool) -> tuple[str, list[str]]:
    results = []
    new_content = content

    for state_id in AUTH_HIGH_IDS:
        new_block = make_override_block(state_id, SHARPEN_VECTOR)
        span = find_existing_override(new_content, state_id)

        if span is None:
            results.append(f"  ERROR {state_id}: no existing override found — cannot update")
            continue

        old_text = new_content[span[0]:span[1]]

        if dry_run:
            results.append(f"  PLAN  {state_id}:")
            results.append(f"    BEFORE: {old_text[:80].replace(chr(10), ' | ')!r}")
            new_preview = "\n      ".join(new_block.split("\n"))
            results.append(f"    AFTER:  {new_preview[:120]!r}")
        else:
            new_content = new_content[:span[0]] + new_block + "\n" + new_content[span[1]:]
            results.append(f"  WRITE {state_id}: override updated")

    return new_content, results


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    if mode not in ("--dry-run", "--write"):
        print("usage: python patch_auth_sharpen.py [--dry-run | --write]")
        sys.exit(1)

    dry_run = (mode == "--dry-run")
    print(f"patch_auth_sharpen.py  mode={'DRY-RUN' if dry_run else 'WRITE'}")
    print(f"target: {TARGET}")

    print("\n=== DRY-RUN VERIFICATION ===")
    dry_run_verification()

    content = TARGET.read_text(encoding="utf-8")
    new_content, results = apply_patches(content, dry_run)

    print(f"\n=== {'DRY-RUN' if dry_run else 'WRITE'} RESULTS ===\n")
    for r in results:
        print(r)

    if not dry_run:
        TARGET.write_text(new_content, encoding="utf-8")
        print(f"\nWrote {TARGET}")

    errors = [r for r in results if "ERROR" in r]
    if errors:
        print(f"\n{len(errors)} error(s) — review before proceeding.")
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
