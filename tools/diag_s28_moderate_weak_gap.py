"""
PRV3 S28 Diagnostic — Moderate/Weak Profile Gap Analysis

Read-only. No engine changes. No engine file modifications.

Captures per-profile score data for all failing moderate and weak profiles
to establish the empirical gap distribution before criterion redesign.

Usage:
    python tools/diag_s28_moderate_weak_gap.py --dry-run
    python tools/diag_s28_moderate_weak_gap.py

Output:
    tools/diag_s28_moderate_weak_gap.md
"""

import sys
import argparse
import math
from collections import Counter
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).parents[1]))

from tools.calibration_runner import ALL_PROFILES, run_profile
from engine.test_suite import run_test_case
from engine.output import SCD_WCS_ALIGNMENT_THRESHOLD

FLOOR    = SCD_WCS_ALIGNMENT_THRESHOLD  # -0.4000
OUT_PATH = Path(__file__).parent / "diag_s28_moderate_weak_gap.md"


# ── Engine run ────────────────────────────────────────────────────────────────

def run_diagnostic(profiles: list, dry_run: bool = False) -> list:
    """
    Run all moderate/weak profiles through the engine.
    Returns list of result dicts with the 10 diagnostic fields + passed flag.
    Prints progress per profile.
    """
    results = []
    for i, tc in enumerate(profiles, 1):
        if dry_run:
            print(f"  [{i:3d}] {tc.test_id:<20} {tc.profile_type:<10} "
                  f"target={tc.target_state}")
            continue

        output = run_profile(tc)
        dist   = output.get("state_distribution", [])

        target_entry = next((e for e in dist if e.get("state_id") == tc.target_state), None)
        rank1_entry  = next((e for e in dist if e.get("rank") == 1), None)

        target_score = target_entry.get("score") if target_entry else None
        rank1_state  = rank1_entry.get("state_id") if rank1_entry else None
        rank1_score  = rank1_entry.get("score") if rank1_entry else None

        target_above_floor = (target_score is not None and target_score >= FLOOR)

        prominence_gap = (
            (target_score - rank1_score)
            if target_score is not None and rank1_score is not None
            else None
        )

        output_type = output.get("output_type", "unknown")

        above_floor_entries     = [e for e in dist if e.get("score", -999.0) >= FLOOR]
        states_above_floor      = len(above_floor_entries)
        states_above_floor_list = [e.get("state_id") for e in above_floor_entries]

        test_result = run_test_case(tc, output)
        passed = test_result.passed

        gap_str = f"{prominence_gap:+.4f}" if prominence_gap is not None else "   N/A"
        status  = "PASS" if passed else "FAIL"
        print(f"  [{i:3d}] {tc.test_id:<20} {tc.profile_type:<10} "
              f"gap={gap_str}  af={str(target_above_floor):<5}  {status}")

        results.append({
            "profile_id":             tc.test_id,
            "target_state":           tc.target_state,
            "profile_type":           tc.profile_type,
            "target_score":           target_score,
            "target_above_floor":     target_above_floor,
            "rank_1_state":           rank1_state,
            "rank_1_score":           rank1_score,
            "prominence_gap":         prominence_gap,
            "output_type":            output_type,
            "states_above_floor":     states_above_floor,
            "states_above_floor_list": states_above_floor_list,
            "passed":                 passed,
        })

    return results


# ── Gap bucket helper ─────────────────────────────────────────────────────────

def gap_bucket(gap: float) -> str:
    """Return 0.05-wide bucket label for a prominence_gap value."""
    lower = math.floor(gap / 0.05) * 0.05
    upper = lower + 0.05
    return f"{lower:+.2f} to {upper:+.2f}"


# ── Markdown report builder ───────────────────────────────────────────────────

def build_markdown(results: list) -> str:
    failing = [r for r in results if not r["passed"]]

    mod_total  = sum(1 for r in results if r["profile_type"] == "moderate")
    mod_pass   = sum(1 for r in results if r["profile_type"] == "moderate" and r["passed"])
    mod_fail   = mod_total - mod_pass
    weak_total = sum(1 for r in results if r["profile_type"] == "weak")
    weak_pass  = sum(1 for r in results if r["profile_type"] == "weak" and r["passed"])
    weak_fail  = weak_total - weak_pass

    failing_gaps = [r["prominence_gap"] for r in failing if r["prominence_gap"] is not None]
    floor_gated  = [r for r in failing if not r["target_above_floor"]]
    comp_blocked = [r for r in failing if r["target_above_floor"]]

    lines = []
    lines.append("# PRV3 S28 Diagnostic — Moderate/Weak Profile Gap Analysis")
    lines.append("")
    lines.append(f"Generated: Session 28 — 2026-05-27  ")
    lines.append(f"Engine: v24 (CENTROID_FIELD_SCALARS locked, SCD_WCS_CLUSTER_WINDOW=0.35)  ")
    lines.append(f"Floor threshold: SCD_WCS_ALIGNMENT_THRESHOLD = {FLOOR}")
    lines.append("")

    # ── Section 1 ────────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Section 1 — Summary")
    lines.append("")
    lines.append("| Profile type | Total | Passing | Failing |")
    lines.append("|---|---|---|---|")
    lines.append(f"| moderate | {mod_total} | {mod_pass} | {mod_fail} |")
    lines.append(f"| weak | {weak_total} | {weak_pass} | {weak_fail} |")
    lines.append(f"| **Total** | **{mod_total+weak_total}** | **{mod_pass+weak_pass}** | **{mod_fail+weak_fail}** |")
    lines.append("")
    lines.append("**Failure classification (failing profiles only):**")
    lines.append("")
    lines.append("| Category | Count | Description |")
    lines.append("|---|---|---|")
    lines.append(
        f"| Floor-gated | {len(floor_gated)} | "
        f"target_score < {FLOOR} — absolute threshold not met |"
    )
    lines.append(
        f"| Competition-blocked | {len(comp_blocked)} | "
        f"target_score >= {FLOOR} but outscored or output_type mismatch |"
    )
    lines.append("")
    if floor_gated:
        lines.append(
            "Floor-gated profile IDs: "
            + ", ".join(r["profile_id"] for r in floor_gated)
        )
        lines.append("")
    if comp_blocked:
        lines.append(
            "Competition-blocked profile IDs: "
            + ", ".join(r["profile_id"] for r in comp_blocked)
        )
        lines.append("")

    # ── Section 2 ────────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Section 2 — Prominence Gap Distribution (failing profiles only)")
    lines.append("")
    if not failing_gaps:
        lines.append("No failing profiles with computable gaps.")
    else:
        lines.append(f"Mean gap:   {mean(failing_gaps):+.4f}  ")
        lines.append(f"Median gap: {median(failing_gaps):+.4f}  ")
        lines.append(f"Min gap:    {min(failing_gaps):+.4f}  ")
        lines.append(f"Max gap:    {max(failing_gaps):+.4f}  ")
        lines.append("")

        bucket_counts: Counter = Counter(gap_bucket(g) for g in failing_gaps)

        def bucket_sort_key(label: str) -> float:
            try:
                return float(label.split(" to ")[0])
            except ValueError:
                return 0.0

        sorted_buckets = sorted(bucket_counts.keys(), key=bucket_sort_key)
        total_failing  = len(failing_gaps)

        lines.append("| Gap bucket (target minus rank-1) | Count | % of failing |")
        lines.append("|---|---|---|")
        for b in sorted_buckets:
            cnt = bucket_counts[b]
            pct = 100.0 * cnt / total_failing
            lines.append(f"| {b} | {cnt} | {pct:.1f}% |")
        lines.append("")
        lines.append(f"Total failing profiles with gap data: {total_failing}")
        lines.append("")
        lines.append(
            "**Interpretation note:** gap = 0.00 means target is rank-1 but profile "
            "fails for another reason (output_type mismatch or weak above_floor criterion). "
            "Negative gap means target is outscored by the rank-1 state."
        )
    lines.append("")

    # ── Section 3 ────────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Section 3 — Rank-1 Sink Analysis (failing profiles only)")
    lines.append("")
    if not failing:
        lines.append("No failing profiles.")
    else:
        sink_counts: Counter = Counter()
        for r in failing:
            if r["rank_1_state"] is None:
                sink_counts["[no rank-1]"] += 1
            elif r["rank_1_state"] == r["target_state"]:
                sink_counts["[target is rank-1 — other failure reason]"] += 1
            else:
                sink_counts[r["rank_1_state"]] += 1

        lines.append("| Rank-1 state (when target fails) | Count |")
        lines.append("|---|---|")
        for state, cnt in sorted(sink_counts.items(), key=lambda x: -x[1]):
            lines.append(f"| {state} | {cnt} |")
        lines.append("")

    # ── Section 4 ────────────────────────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## Section 4 — Per-Profile Detail (failing profiles only)")
    lines.append("")
    lines.append(
        "Sorted by profile_type, then prominence_gap ascending (worst gaps first)."
    )
    lines.append("")

    def sort_key(r: dict) -> tuple:
        pt_order = {"moderate": 0, "weak": 1}
        gap = r["prominence_gap"] if r["prominence_gap"] is not None else -999.0
        return (pt_order.get(r["profile_type"], 9), gap)

    failing_sorted = sorted(failing, key=sort_key)

    lines.append(
        "| profile_id | target_state | type | target_score | above_floor | "
        "rank_1_state | rank_1_score | gap | output_type | states_above_floor |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for r in failing_sorted:
        ts  = f"{r['target_score']:+.4f}"   if r["target_score"]   is not None else "N/A"
        r1s = f"{r['rank_1_score']:+.4f}"   if r["rank_1_score"]   is not None else "N/A"
        gap = f"{r['prominence_gap']:+.4f}" if r["prominence_gap"] is not None else "N/A"
        af  = str(r["target_above_floor"])
        lines.append(
            f"| {r['profile_id']} | {r['target_state']} | {r['profile_type']} "
            f"| {ts} | {af} | {r['rank_1_state'] or 'N/A'} "
            f"| {r1s} | {gap} | {r['output_type']} | {r['states_above_floor']} |"
        )
    lines.append("")

    lines.append("### States above floor detail (per failing profile)")
    lines.append("")
    for r in failing_sorted:
        saf = ", ".join(r["states_above_floor_list"]) if r["states_above_floor_list"] else "none"
        lines.append(f"**{r['profile_id']}** ({r['target_state']}): {saf}")
        lines.append("")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PRV3 S28 Moderate/Weak Gap Diagnostic"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what the script will do without calling the engine",
    )
    args = parser.parse_args()

    profiles   = [p for p in ALL_PROFILES if p.profile_type in ("moderate", "weak")]
    mod_count  = sum(1 for p in profiles if p.profile_type == "moderate")
    weak_count = sum(1 for p in profiles if p.profile_type == "weak")

    print("=" * 72)
    print("PRV3 S28 — Moderate/Weak Profile Gap Diagnostic")
    print(f"  Total profiles: {len(profiles)}"
          f"  ({mod_count} moderate, {weak_count} weak)")
    print(f"  Floor threshold: SCD_WCS_ALIGNMENT_THRESHOLD = {FLOOR}")
    mode_label = "DRY-RUN (engine will NOT be called)" if args.dry_run else "FULL RUN"
    print(f"  Mode: {mode_label}")
    print("=" * 72)

    if args.dry_run:
        print(f"\nProfiles that would be processed ({len(profiles)}):")
        run_diagnostic(profiles, dry_run=True)
        print("\nDry-run complete. Re-run without --dry-run to execute.")
        sys.exit(0)

    print("\nRunning profiles...")
    results = run_diagnostic(profiles, dry_run=False)

    # ── Sanity checks ─────────────────────────────────────────────────────────
    failing = [r for r in results if not r["passed"]]
    passing = [r for r in results if r["passed"]]
    print(f"\nSanity check:")
    print(f"  Total processed:     {len(results)}")
    print(f"  Passing:             {len(passing)}")
    print(f"  Failing:             {len(failing)}")

    if len(results) == 0:
        print("\nHARD STOP: zero results — check import errors.")
        sys.exit(1)

    if len(failing) == 0:
        print(
            "\nHARD STOP: zero failing profiles. Unexpected given v24 moderate/weak "
            "pass rates (4/47 moderate, 5/47 weak). Verify ALL_PROFILES contains "
            "moderate/weak profiles and calibration_runner is importing correctly."
        )
        sys.exit(1)

    floor_gated  = [r for r in failing if not r["target_above_floor"]]
    comp_blocked = [r for r in failing if r["target_above_floor"]]
    print(f"  Floor-gated:         {len(floor_gated)}")
    print(f"  Competition-blocked: {len(comp_blocked)}")

    if len(floor_gated) == len(failing) and len(failing) > 0:
        print(
            "\nWARNING: All failing profiles are floor-gated (target below -0.4000). "
            "Zero competition-blocked. This is unexpected — stopping before markdown. "
            "Report this to Pete before proceeding."
        )
        sys.exit(1)

    # ── Write markdown ────────────────────────────────────────────────────────
    print("\nGenerating markdown...")
    md = build_markdown(results)
    OUT_PATH.write_text(md, encoding="utf-8")
    print(f"Written: {OUT_PATH}")
    print("\nDone.")


if __name__ == "__main__":
    main()
