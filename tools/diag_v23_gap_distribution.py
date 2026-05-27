"""
PRV3 -- v23 Gap Distribution Diagnostic (Session 26)

Read-only. No writes to engine/ or engine/data/.

For all 47 HC profiles under v23 engine state, reports:
  - Per-profile: target rank, target score, rank-1 state, rank-1 score, gap
  - Delta window pass rates (how many profiles have target within Delta of rank-1)
  - Score range summary
  - Rank-1 captures by state (sink analysis)

Usage:
  python tools/diag_v23_gap_distribution.py

Output:
  tools/diag_v23_gap_distribution.md
"""

import sys
import os
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

# calibration_runner is in the same tools/ directory; tools/ is in sys.path
# when this script is run with `python tools/diag_v23_gap_distribution.py`.
import calibration_runner as cr

from engine.accumulation import IntakeData, AccumulationEngine
from engine.data.salience import SALIENCE_PROFILES
from engine.data.questions import QUESTION_LIBRARY


# ── Filter HC profiles ─────────────────────────────────────────────────────────

HC_PROFILES = [
    tc for tc in cr.ALL_PROFILES
    if tc.profile_type in ("high_confidence", "extreme_high_confidence")
]

print(f"HC profiles loaded: {len(HC_PROFILES)}")


# ── Run each HC profile through accumulation and ranking ──────────────────────

rows = []

for tc in HC_PROFILES:
    intake = IntakeData(**tc.intake)
    acc_engine = AccumulationEngine(intake)

    answers = cr.generate_answers(tc)
    for ans in answers:
        q = QUESTION_LIBRARY.get(ans.question_id)
        if q is None:
            continue
        for opt_id in ans.selected_option_ids:
            opt = next((o for o in q.answer_options if o.option_id == opt_id), None)
            if opt is None:
                continue
            acc_engine.apply_answer(opt, ans.question_id)

    rankings = acc_engine.rank(SALIENCE_PROFILES)

    rank_1 = next((r for r in rankings if r.rank == 1), None)
    target_r = next((r for r in rankings if r.state_id == tc.target_state), None)

    if rank_1 is None or target_r is None:
        print(f"[HARD STOP] Malformed ranking for {tc.test_id} (target: {tc.target_state})")
        print(f"  rank_1={rank_1}  target_r={target_r}")
        sys.exit(1)

    gap = rank_1.score - target_r.score

    rows.append({
        "test_id":       tc.test_id,
        "profile_type":  tc.profile_type,
        "target_state":  tc.target_state,
        "target_rank":   target_r.rank,
        "target_score":  target_r.score,
        "rank_1_state":  rank_1.state_id,
        "rank_1_score":  rank_1.score,
        "gap":           gap,
    })


# ── Dry-run check ──────────────────────────────────────────────────────────────

print("\nFirst 5 profiles (structural check):")
for row in rows[:5]:
    print(
        f"  {row['target_state']:<44}"
        f"  rank={row['target_rank']:>2}"
        f"  target={row['target_score']:.4f}"
        f"  r1={row['rank_1_score']:.4f}"
        f"  gap={row['gap']:.4f}"
        f"  r1_state={row['rank_1_state']}"
    )

for row in rows:
    if row["target_score"] is None or row["rank_1_score"] is None:
        print(f"[HARD STOP] None score for {row['target_state']}")
        sys.exit(1)
    if row["gap"] < -1e-9:
        print(f"[HARD STOP] Negative gap for {row['target_state']}: gap={row['gap']:.6f}")
        sys.exit(1)
    if not (1 <= row["target_rank"] <= 47):
        print(f"[HARD STOP] target_rank out of range for {row['target_state']}: {row['target_rank']}")
        sys.exit(1)

print(f"\nAll {len(rows)} profiles structurally valid. Writing output file.")


# ── Analysis ──────────────────────────────────────────────────────────────────

rows_sorted = sorted(rows, key=lambda r: r["gap"])

deltas = [0.05, 0.10, 0.20, 0.30, 0.50, 1.00]
delta_counts = {d: sum(1 for r in rows if r["gap"] <= d) for d in deltas}

r1_scores = [r["rank_1_score"] for r in rows]
t_scores  = [r["target_score"] for r in rows]
gaps      = [r["gap"] for r in rows]

sink_counts: dict = defaultdict(int)
for r in rows:
    sink_counts[r["rank_1_state"]] += 1


# ── Build output ───────────────────────────────────────────────────────────────

n = len(rows)
lines = []

lines.append("# PRV3 v23 Gap Distribution Diagnostic")
lines.append("")
lines.append(f"Session 26 read-only. {n} HC profiles under v23 engine state.")
lines.append("Engine: v23 (salience revert + leadership_deafness vector reshape + cluster cleanup)")
lines.append("")

# Section 1 -- Per-profile table
lines.append("## Per-Profile Gap Analysis (47 HC Profiles)")
lines.append("")
lines.append("Sorted by gap ascending (smallest gap first).")
lines.append("")
lines.append("| Target State | Target Rank | Target Score | Rank-1 State | Rank-1 Score | Gap |")
lines.append("|---|---|---|---|---|---|")
for r in rows_sorted:
    lines.append(
        f"| {r['target_state']} | {r['target_rank']} | {r['target_score']:.4f}"
        f" | {r['rank_1_state']} | {r['rank_1_score']:.4f} | {r['gap']:.4f} |"
    )
lines.append("")

# Section 2 -- Delta window
lines.append("## Top-Cluster Pass Rate by Delta Window")
lines.append("")
lines.append("Target state within Delta of rank-1 score.")
lines.append("")
lines.append("| Delta_margin | Profiles passing | Pass rate |")
lines.append("|---|---|---|")
for d in deltas:
    count = delta_counts[d]
    pct = count / n * 100
    lines.append(f"| {d:.2f} | {count} / {n} | {pct:.0f}% |")
lines.append("")

# Section 3 -- Score range
lines.append("## Score Range Summary")
lines.append("")
lines.append("Rank-1 scores across 47 HC profiles:")
lines.append(
    f"  Min: {min(r1_scores):.4f}  "
    f"Max: {max(r1_scores):.4f}  "
    f"Mean: {sum(r1_scores)/n:.4f}"
)
lines.append("")
lines.append("Target-state scores across 47 HC profiles:")
lines.append(
    f"  Min: {min(t_scores):.4f}  "
    f"Max: {max(t_scores):.4f}  "
    f"Mean: {sum(t_scores)/n:.4f}"
)
lines.append("")
lines.append("Gap distribution:")
lines.append(
    f"  Min gap: {min(gaps):.4f}  "
    f"Max gap: {max(gaps):.4f}  "
    f"Mean gap: {sum(gaps)/n:.4f}"
)
lines.append(f"  Profiles with gap = 0.000 (target is rank-1): {sum(1 for g in gaps if g < 1e-9)} / {n}")
lines.append(f"  Profiles with gap <= 0.050: {sum(1 for g in gaps if g <= 0.050)} / {n}")
lines.append(f"  Profiles with gap <= 0.100: {sum(1 for g in gaps if g <= 0.100)} / {n}")
lines.append(f"  Profiles with gap <= 0.200: {sum(1 for g in gaps if g <= 0.200)} / {n}")
lines.append("")

# Section 4 -- Sink analysis
lines.append("## Rank-1 Captures by State (across 47 HC profiles)")
lines.append("")
lines.append("| State | Rank-1 count |")
lines.append("|---|---|")
for state, count in sorted(sink_counts.items(), key=lambda x: -x[1]):
    lines.append(f"| {state} | {count} |")
lines.append("")

# Write file
OUT_PATH = Path(__file__).parent / "diag_v23_gap_distribution.md"
OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
print(f"Output: {OUT_PATH}")
