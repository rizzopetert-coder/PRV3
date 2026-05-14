"""
PRV3 Patch — Vector Update v5
Session 16: 16-state dimensional vector override batch.

Category 1 (6 states): Authority HIGH — differentiated secondaries per Gemini spec.
Category 2 (10 states): Cluster centroid traps — primary field raised to 0.45.

usage:
  python tools/patch_vectors_v5.py --dry-run
  python tools/patch_vectors_v5.py --write
"""

import sys
import math
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "states.py"

# Field order matches DimensionalVector dataclass declaration order
FIELD_ORDER = [
    "aptitude_liability",  "aptitude_asset",
    "authority_liability", "authority_asset",
    "alliance_liability",  "alliance_asset",
    "attitude_liability",  "attitude_asset",
]

# Vectors specified exactly as per Gemini spec, Pete confirmed.
# Category 1 — Authority HIGH (6 states)
# Category 2 — Cluster states (10 states)
VECTORS = {
    # ── Category 1 — Authority HIGH ─────────────────────────────────────────
    "the_founders_grip": {
        "aptitude_liability":  0.40, "aptitude_asset":  0.20,
        "authority_liability": 0.60, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.30, "attitude_asset":  0.20,
    },
    "the_exposed": {
        "aptitude_liability":  0.40, "aptitude_asset":  0.20,
        "authority_liability": 0.60, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.20, "attitude_asset":  0.20,
    },
    "hr_capture": {
        "aptitude_liability":  0.30, "aptitude_asset":  0.20,
        "authority_liability": 0.60, "authority_asset": 0.20,
        "alliance_liability":  0.40, "alliance_asset":  0.20,
        "attitude_liability":  0.20, "attitude_asset":  0.20,
    },
    "heard_and_ignored": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.60, "authority_asset": 0.20,
        "alliance_liability":  0.40, "alliance_asset":  0.20,
        "attitude_liability":  0.20, "attitude_asset":  0.20,
    },
    "the_tolerated_violation": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.60, "authority_asset": 0.20,
        "alliance_liability":  0.30, "alliance_asset":  0.20,
        "attitude_liability":  0.40, "attitude_asset":  0.20,
    },
    "the_unsolved_problem": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.60, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.40, "attitude_asset":  0.20,
    },
    # ── Category 2 — Cluster states ─────────────────────────────────────────
    "the_overloaded_manager": {
        "aptitude_liability":  0.45, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.20, "attitude_asset":  0.20,
    },
    "the_dormant_talent": {
        "aptitude_liability":  0.45, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.20, "attitude_asset":  0.20,
    },
    "culture_drift": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.45, "attitude_asset":  0.20,
    },
    "identity_erosion": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.45, "attitude_asset":  0.20,
    },
    "leadership_deafness": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.45, "attitude_asset":  0.20,
    },
    "the_culture_that_wasnt": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.45, "attitude_asset":  0.20,
    },
    "the_unlocked_door": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.20, "alliance_asset":  0.20,
        "attitude_liability":  0.45, "attitude_asset":  0.20,
    },
    "the_unreported_hazard": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.45, "alliance_asset":  0.20,
        "attitude_liability":  0.20, "attitude_asset":  0.20,
    },
    "the_suppression_filter": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.45, "alliance_asset":  0.20,
        "attitude_liability":  0.20, "attitude_asset":  0.20,
    },
    "what_nobody_says": {
        "aptitude_liability":  0.20, "aptitude_asset":  0.20,
        "authority_liability": 0.20, "authority_asset": 0.20,
        "alliance_liability":  0.45, "alliance_asset":  0.20,
        "attitude_liability":  0.20, "attitude_asset":  0.20,
    },
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
    print("\n=== DRY-RUN VERIFICATION ===\n")

    # Pairwise cosine among 6 Authority HIGH states
    auth_high_ids = [
        "the_founders_grip", "the_exposed", "hr_capture",
        "heard_and_ignored", "the_tolerated_violation", "the_unsolved_problem",
    ]
    print("Authority HIGH pairwise cosine similarities (new vectors):")
    print(f"  {'Pair':<45} {'Cosine':>10}  {'Flag'}")
    print(f"  {'-'*45} {'-'*10}  {'-'*8}")
    flags_found = []
    for i in range(len(auth_high_ids)):
        for j in range(i + 1, len(auth_high_ids)):
            a, b = auth_high_ids[i], auth_high_ids[j]
            sim = cosine_sim(VECTORS[a], VECTORS[b])
            flag = ""
            if sim > 0.999:
                flag = "** GATE FAIL **"
                flags_found.append((a, b, sim))
            elif sim > 0.95:
                flag = "BUNCHED"
            print(f"  {a} / {b:<22} {sim:>10.6f}  {flag}")

    if flags_found:
        print("\n  GATE TRIGGERED: pairs above 0.999 — write blocked.")
        for a, b, s in flags_found:
            print(f"    {a} / {b}: {s:.6f}")
        sys.exit(1)
    else:
        print("\n  Gate: PASS — no pair above 0.999\n")

    # Centroid distances for cluster states
    neutral = {f: 0.25 for f in FIELD_ORDER}
    cluster_ids = [sid for sid in VECTORS if sid not in auth_high_ids]
    print("Cluster state cosine similarity to neutral centroid (0.25 each field):")
    for sid in cluster_ids:
        sim = cosine_sim(VECTORS[sid], neutral)
        flag = "TRAP" if abs(sim - 1.0) < 1e-6 else ""
        print(f"  {sid:<35} {sim:.6f}  {flag}")
    print()


def apply_patches(content: str, dry_run: bool) -> tuple[str, list[str]]:
    results = []
    new_content = content

    for state_id, vec in VECTORS.items():
        override_marker = f'STATE_PROFILES["{state_id}"].dimensional_vector'
        if override_marker in new_content:
            results.append(f"  SKIP  {state_id}: override already present")
            continue

        state_marker = f'    state_id="{state_id}",'
        idx = new_content.find(state_marker)
        if idx == -1:
            results.append(f"  ERROR {state_id}: state_id marker not found in file")
            continue

        close_idx = new_content.find("))\n", idx)
        if close_idx == -1:
            results.append(f"  ERROR {state_id}: closing )) not found after state_id marker")
            continue

        insertion_point = close_idx + 3  # after "))\n"
        override_block = make_override_block(state_id, vec)

        if dry_run:
            lines_preview = "\n      ".join(override_block.split("\n"))
            results.append(f"  PLAN  {state_id}: insert override after ))")
            results.append(f"      {lines_preview}")
        else:
            insert_text = override_block + "\n"
            new_content = new_content[:insertion_point] + insert_text + new_content[insertion_point:]
            results.append(f"  WRITE {state_id}: override inserted")

    return new_content, results


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"

    if mode not in ("--dry-run", "--write"):
        print("usage: python patch_vectors_v5.py [--dry-run | --write]")
        sys.exit(1)

    dry_run = (mode == "--dry-run")
    print(f"patch_vectors_v5.py  mode={'DRY-RUN' if dry_run else 'WRITE'}")
    print(f"target: {TARGET}")

    dry_run_verification()

    content = TARGET.read_text(encoding="utf-8")
    new_content, results = apply_patches(content, dry_run)

    print(f"\n=== {'DRY-RUN' if dry_run else 'WRITE'} RESULTS ===\n")
    for r in results:
        print(r)

    if not dry_run:
        TARGET.write_text(new_content, encoding="utf-8")
        print(f"\nWrote {TARGET}")

    errors = [r for r in results if r.strip().startswith("ERROR")]
    if errors:
        print(f"\n{len(errors)} error(s) — review before proceeding.")
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
