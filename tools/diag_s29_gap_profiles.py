"""
S29 Diagnostic: 9 Structural Failure Gap Profiles
Read-only. No writes. No engine modifications.

For every state that fails one or more profile types (HC / moderate / weak)
under the v25 calibration criteria, report:
  - State name
  - Profile types failing
  - Target score, rank-1 state name, rank-1 score, prominence gap

Stops immediately if HC drops below 47/47.
"""

import sys
import types as _types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from tools.calibration_runner import (
    ALL_PROFILES,
    run_profile,
    _passes_cluster_criterion,
    _passes_prominence_criterion,
    SCD_WCS_CLUSTER_WINDOW,
    MODERATE_PROMINENCE_DELTA,
    WEAK_PROMINENCE_DELTA,
)
from engine.output import SCD_WCS_ALIGNMENT_THRESHOLD


def main():
    print("S29 Diagnostic — v25 gap profiles for failing states")
    print("=" * 72)

    # Run all profiles
    engine_outputs = {}
    for tc in ALL_PROFILES:
        engine_outputs[tc.test_id] = run_profile(tc)

    # ── HC check ────────────────────────────────────────────────────────────────
    hc_pass = 0
    hc_total = 0
    hc_seen = set()
    for tc in ALL_PROFILES:
        if tc.profile_type not in ("high_confidence", "extreme_high_confidence"):
            continue
        if tc.target_state in hc_seen:
            continue
        hc_seen.add(tc.target_state)
        hc_total += 1
        out = engine_outputs.get(tc.test_id, {})
        _dist = sorted(out.get("state_distribution", []), key=lambda e: e.get("rank", 99))
        _rnks = [_types.SimpleNamespace(state_id=e.get("state_id", ""), score=e.get("score", 0.0))
                 for e in _dist]
        if _passes_cluster_criterion(_rnks, tc.target_state):
            hc_pass += 1

    print(f"\nHC check: {hc_pass}/{hc_total}")
    if hc_pass < hc_total:
        print(f"HARD STOP — HC regression detected: {hc_pass}/{hc_total}. Aborting.")
        sys.exit(1)
    print("HC 47/47 confirmed. Proceeding.\n")

    # ── Moderate / Weak gap extraction ──────────────────────────────────────────
    # Collect per-failing-profile detail, keyed by (target_state, profile_type)
    # Each value: list of gap dicts (one per profile instance — most states have 3 per type)

    failing: dict = {}  # state_id -> {profile_type -> list of gap dicts}

    for tc in ALL_PROFILES:
        if tc.profile_type not in ("moderate", "weak"):
            continue
        out = engine_outputs.get(tc.test_id, {})
        if not out:
            continue

        _dist = sorted(out.get("state_distribution", []), key=lambda e: e.get("rank", 99))
        _target = next((e for e in _dist if e.get("state_id") == tc.target_state), None)
        _rank1 = _dist[0] if _dist else None

        target_score = _target.get("score", -999.0) if _target else -999.0
        rank1_score = _rank1.get("score", -999.0) if _rank1 else -999.0
        rank1_state = _rank1.get("state_id", "?") if _rank1 else "?"

        pdata = {"target_score": target_score, "rank_1_score": rank1_score}
        passed = _passes_prominence_criterion(pdata, tc.profile_type)

        if not passed:
            sid = tc.target_state
            pt = tc.profile_type
            if sid not in failing:
                failing[sid] = {}
            if pt not in failing[sid]:
                failing[sid][pt] = []
            failing[sid][pt].append({
                "target_score": target_score,
                "rank1_state":  rank1_state,
                "rank1_score":  rank1_score,
                "gap":          target_score - rank1_score,
            })

    # ── Consolidate: one row per (state, profile_type) — use worst gap instance ──
    rows = []
    for sid in sorted(failing):
        for pt in ("moderate", "weak"):
            if pt not in failing[sid]:
                continue
            entries = failing[sid][pt]
            # Worst gap = most negative
            worst = min(entries, key=lambda e: e["gap"])
            rows.append({
                "state":         sid,
                "profile_type":  pt,
                "target_score":  worst["target_score"],
                "rank1_state":   worst["rank1_state"],
                "rank1_score":   worst["rank1_score"],
                "gap":           worst["gap"],
                "n_instances":   len(entries),
                "n_failing":     len(entries),
            })

    # ── Hard stop if HC regression already caught above; also flag unexpected state count ──
    unique_failing_states = sorted(failing.keys())
    n_states = len(unique_failing_states)

    if n_states != 9:
        print(f"FLAG: Expected 9 failing states, found {n_states}.")
    else:
        print(f"Failing state count: {n_states} (expected 9 — OK)")

    print(f"Failing states: {', '.join(unique_failing_states)}\n")

    # ── Table ──────────────────────────────────────────────────────────────────
    col_state   = 36
    col_type    = 10
    col_tscore  = 12
    col_r1state = 36
    col_r1score = 12
    col_gap     = 10

    header = (
        f"{'State':<{col_state}} {'Type':<{col_type}} "
        f"{'Target':>{col_tscore}} {'Rank-1 State':<{col_r1state}} "
        f"{'R1 Score':>{col_r1score}} {'Gap':>{col_gap}}"
    )
    sep = "-" * len(header)

    print(header)
    print(sep)

    prev_state = None
    for row in rows:
        state_label = row["state"] if row["state"] != prev_state else ""
        prev_state = row["state"]
        print(
            f"{state_label:<{col_state}} "
            f"{row['profile_type']:<{col_type}} "
            f"{row['target_score']:>{col_tscore}.4f} "
            f"{row['rank1_state']:<{col_r1state}} "
            f"{row['rank1_score']:>{col_r1score}.4f} "
            f"{row['gap']:>{col_gap}.4f}"
        )

    print(sep)
    print(f"\nTotal failing (state × profile_type) rows: {len(rows)}")
    print(f"MODERATE_PROMINENCE_DELTA = {MODERATE_PROMINENCE_DELTA}")
    print(f"WEAK_PROMINENCE_DELTA     = {WEAK_PROMINENCE_DELTA}")
    print(f"SCD_WCS_ALIGNMENT_THRESHOLD = {SCD_WCS_ALIGNMENT_THRESHOLD}")
    print("\nDone.")


if __name__ == "__main__":
    main()
