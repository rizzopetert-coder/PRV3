"""
PRV3 -- Session 25 Co-Occurrence and Clustering Diagnostic

Read-only. No engine modifications.
Produces 4 markdown output files in tools/.

Usage:
    python tools/diag_s25_cooccurrence.py           # full run, writes 4 files
    python tools/diag_s25_cooccurrence.py --check   # dry-run: first 3 profiles, then exit
"""

import os
import sys
import argparse
import collections

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.calibration_runner import ALL_PROFILES, generate_answers
from engine.accumulation import AccumulationEngine, IntakeData
from engine.data.questions import QUESTION_LIBRARY
from engine.data.states import STATE_PROFILES
from engine.data.salience import SALIENCE_PROFILES
from engine.output import SCD_WCS_ALIGNMENT_THRESHOLD

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
THRESHOLD = SCD_WCS_ALIGNMENT_THRESHOLD  # 0.25
TOP_N = 5   # co-occurrence window
TOP_K = 10  # rankings output depth

NAMED_CLUSTERS = {
    "C-Manager":  ["the_unformed_leader", "the_overloaded_manager", "the_dormant_talent"],
    "C-Culture":  ["culture_drift", "the_culture_that_wasnt", "identity_erosion"],
    "C-Silence":  ["what_nobody_says", "the_unreported_hazard", "the_unlocked_door"],
    "C-InfoFlow": ["leadership_deafness", "the_suppression_filter"],
}

KNOWN_SINKS = ["leadership_deafness", "built_to_fail", "the_fracture"]

ALL_STATE_IDS = sorted(STATE_PROFILES.keys())


# ── Profile runner ────────────────────────────────────────────────────────────

def run_hc_profile(test_case):
    """
    Run one HC profile through AccumulationEngine and return full ranking list.
    Models calibration_runner.run_profile() exactly -- no engine modifications.
    """
    intake = IntakeData(**test_case.intake)
    acc_engine = AccumulationEngine(intake)
    answers = generate_answers(test_case)
    for ans in answers:
        q = QUESTION_LIBRARY.get(ans.question_id)
        if q is None:
            continue
        for opt_id in ans.selected_option_ids:
            opt = next((o for o in q.answer_options if o.option_id == opt_id), None)
            if opt is None:
                continue
            acc_engine.apply_answer(opt, ans.question_id)
    return acc_engine.rank(SALIENCE_PROFILES)


# ── Main data collection ──────────────────────────────────────────────────────

def collect_rankings():
    hc_profiles = [p for p in ALL_PROFILES if p.profile_type == "high_confidence"]
    print(f"Collecting rankings for {len(hc_profiles)} HC profiles...")

    # {target_state: [StateRanking sorted rank-1 first]}
    profile_rankings = {}
    for p in hc_profiles:
        rankings = run_hc_profile(p)
        profile_rankings[p.target_state] = sorted(rankings, key=lambda r: r.rank)

    print(f"  Done. {len(profile_rankings)} profiles collected.")
    return profile_rankings, hc_profiles


# ── Dry-run check ─────────────────────────────────────────────────────────────

def dry_run_check(profile_rankings, hc_profiles):
    sample_targets = [p.target_state for p in hc_profiles[:3]]
    print("\n" + "=" * 72)
    print("DRY-RUN CHECK -- First 3 HC profiles, top-5 states")
    print("=" * 72)
    for target in sample_targets:
        rankings = profile_rankings[target]
        profile = STATE_PROFILES.get(target)
        sname = profile.state_name if profile else target
        print(f"\n  [{target}]  ({sname})")
        print(f"  {'Rank':<5}  {'State ID':<42}  {'Score':>7}  {'Cleared':>8}  {'Note'}")
        print(f"  {'-'*5}  {'-'*42}  {'-'*7}  {'-'*8}  {'-'*10}")
        for r in rankings[:5]:
            cleared = "YES" if r.score > THRESHOLD else "NO"
            marker = "<-- TARGET" if r.state_id == target else ""
            print(f"  {r.rank:<5}  {r.state_id:<42}  {r.score:>7.4f}  {cleared:>8}  {marker}")
        # Show target rank if not in top-5
        target_entry = next((r for r in rankings if r.state_id == target), None)
        if target_entry and target_entry.rank > 5:
            print(f"  [Target at rank {target_entry.rank}, score {target_entry.score:.4f}]")
    print("\n" + "=" * 72)
    print(f"Threshold: {THRESHOLD}  |  Top-N window: {TOP_N}  |  Profile count: {len(profile_rankings)}")
    print("=" * 72 + "\n")


# ── Output 1: Full top-10 rankings ───────────────────────────────────────────

def write_rankings(profile_rankings, hc_profiles, path):
    lines = []
    lines.append("# PRV3 -- Session 25: Full Top-10 Rankings by HC Profile")
    lines.append(f"\nSCD-WCS metric. Floor threshold: {THRESHOLD}. 47 HC profiles.\n")
    lines.append("---\n")

    for p in hc_profiles:
        target = p.target_state
        rankings = profile_rankings[target]
        profile = STATE_PROFILES.get(target)
        sname = profile.state_name if profile else target

        lines.append(f"## {target}")
        lines.append(f"**Target state name:** {sname}")
        lines.append("")

        target_rank = next((r.rank for r in rankings if r.state_id == target), None)
        if target_rank is not None and target_rank <= TOP_K:
            lines.append(f"**Target in top-{TOP_K}:** YES (rank {target_rank})")
        elif target_rank is not None:
            lines.append(f"**Target in top-{TOP_K}:** NO -- actual rank {target_rank}")
        else:
            lines.append(f"**Target in top-{TOP_K}:** NOT FOUND in rankings")

        lines.append("")
        lines.append(f"| Rank | State ID | State Name | Score | Floor cleared |")
        lines.append(f"|------|----------|------------|-------|----------------|")

        for r in rankings[:TOP_K]:
            sp = STATE_PROFILES.get(r.state_id)
            rname = sp.state_name if sp else r.state_id
            cleared = "YES" if r.score > THRESHOLD else "NO"
            note = " **<-- TARGET**" if r.state_id == target else ""
            lines.append(
                f"| {r.rank} | {r.state_id} | {rname}{note} | {r.score:.4f} | {cleared} |"
            )

        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Written: {os.path.basename(path)}")


# ── Output 2: Co-occurrence matrix ───────────────────────────────────────────

def write_cooccurrence_matrix(profile_rankings, hc_profiles, path):
    n_profiles = len(profile_rankings)

    # Build top-5 sets per profile
    top5_sets = {}
    for target, rankings in profile_rankings.items():
        top5_sets[target] = {r.state_id for r in rankings[:TOP_N]}

    # Count co-occurrences
    cooccur = collections.defaultdict(int)
    for target, top5 in top5_sets.items():
        top5_list = sorted(top5)
        for i, a in enumerate(top5_list):
            for b in top5_list[i+1:]:
                cooccur[(a, b)] += 1

    # Sort by count descending
    sorted_pairs = sorted(cooccur.items(), key=lambda x: -x[1])

    # Cluster co-occurrence analysis
    # For each cluster, compute:
    #   internal_rate = avg co-occur count among intra-cluster pairs / n_profiles
    #   cross_rate = avg co-occur count for all cluster-member vs non-member pairs / n_profiles
    cluster_stats = {}
    all_cluster_members = set(sid for members in NAMED_CLUSTERS.values() for sid in members)

    for cluster_name, members in NAMED_CLUSTERS.items():
        members = [m for m in members if m in STATE_PROFILES]
        # Internal pairs
        internal_pairs = []
        for i, a in enumerate(members):
            for b in members[i+1:]:
                pair = tuple(sorted([a, b]))
                internal_pairs.append(cooccur[pair])
        internal_avg = sum(internal_pairs) / len(internal_pairs) if internal_pairs else 0.0
        internal_rate = internal_avg / n_profiles

        # Cross-cluster pairs (member vs non-member, non-member not in ANY cluster)
        cross_pairs = []
        non_members = [s for s in ALL_STATE_IDS if s not in all_cluster_members]
        for m in members:
            for nm in non_members:
                pair = tuple(sorted([m, nm]))
                cross_pairs.append(cooccur[pair])
        cross_avg = sum(cross_pairs) / len(cross_pairs) if cross_pairs else 0.0
        cross_rate = cross_avg / n_profiles

        cluster_stats[cluster_name] = {
            "members": members,
            "internal_rate": internal_rate,
            "cross_rate": cross_rate,
            "internal_avg_count": internal_avg,
            "cross_avg_count": cross_avg,
        }

    # Write output
    lines = []
    lines.append("# PRV3 -- Session 25: Co-Occurrence Matrix")
    lines.append(f"\nDefinition: two states co-occur if both appear in top-{TOP_N} across an HC profile.")
    lines.append(f"47 HC profiles. Co-occurrence counts are raw (out of 47 max).\n")
    lines.append("---\n")

    lines.append("## Top 20 Most Frequent Co-Occurrence Pairs\n")
    lines.append("| Rank | State A | State B | Count (of 47) | Rate |")
    lines.append("|------|---------|---------|--------------|------|")
    for i, ((a, b), cnt) in enumerate(sorted_pairs[:20], start=1):
        rate = cnt / n_profiles
        lines.append(f"| {i} | {a} | {b} | {cnt} | {rate:.2%} |")
    lines.append("")

    lines.append("## Named Cluster Co-Occurrence Analysis\n")
    lines.append(
        "Internal rate = avg co-occurrences among cluster-member pairs / 47 profiles.  \n"
        "Cross rate = avg co-occurrences of cluster members vs non-cluster states / 47 profiles.\n"
    )
    lines.append("| Cluster | Members | Internal rate | Cross rate | Internal > Cross? |")
    lines.append("|---------|---------|--------------|------------|-------------------|")
    for cname, stats in cluster_stats.items():
        ir = stats["internal_rate"]
        cr = stats["cross_rate"]
        stronger = "YES" if ir > cr else "NO"
        mlist = ", ".join(stats["members"])
        lines.append(f"| {cname} | {mlist} | {ir:.3f} | {cr:.3f} | {stronger} |")
    lines.append("")

    lines.append("## Cluster Detail\n")
    for cname, stats in cluster_stats.items():
        lines.append(f"### {cname}")
        lines.append(f"Members: {', '.join(stats['members'])}")
        lines.append(
            f"Internal avg co-occurrence count: {stats['internal_avg_count']:.2f} / 47"
        )
        lines.append(
            f"Cross avg co-occurrence count: {stats['cross_avg_count']:.2f} / 47"
        )
        # List internal pair counts
        members = stats["members"]
        if len(members) >= 2:
            lines.append("\nInternal pair counts:")
            for i, a in enumerate(members):
                for b in members[i+1:]:
                    pair = tuple(sorted([a, b]))
                    cnt = cooccur[pair]
                    lines.append(f"- {a} x {b}: {cnt}/47 ({cnt/n_profiles:.2%})")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Written: {os.path.basename(path)}")

    return cooccur, top5_sets


# ── Output 3: Score distribution + threshold candidates ───────────────────────

def write_score_distribution(profile_rankings, hc_profiles, path):
    lines = []
    lines.append("# PRV3 -- Session 25: Score Distribution and Threshold Candidates")
    lines.append(f"\nSCD-WCS metric. Floor threshold: {THRESHOLD}. 47 HC profiles.\n")
    lines.append("---\n")

    # Per-profile table
    lines.append("## Per-Profile Score Table\n")
    lines.append("| Target State | R1 | R3 | R5 | R10 | Gap R1-R3 | States > T=0.25 |")
    lines.append("|---|---|---|---|---|---|---|")

    per_profile_data = []
    all_top5_scores = []

    for p in hc_profiles:
        target = p.target_state
        rankings = profile_rankings[target]

        def score_at(rank, _rankings=rankings):
            r = next((x for x in _rankings if x.rank == rank), None)
            return r.score if r else None

        scores_by_rank = {rk: score_at(rk) for rk in range(1, 11)}
        r1 = scores_by_rank[1]
        r3 = scores_by_rank[3]
        r5 = scores_by_rank[5]
        r10 = scores_by_rank[10]
        gap = (r1 - r3) if (r1 is not None and r3 is not None) else None
        n_cleared = sum(1 for r in rankings if r.score > THRESHOLD)

        def fmt(v):
            return f"{v:.4f}" if v is not None else "—"

        lines.append(
            f"| {target} | {fmt(r1)} | {fmt(r3)} | {fmt(r5)} | {fmt(r10)} "
            f"| {fmt(gap)} | {n_cleared} |"
        )

        row = {"target": target, "gap": gap, "n_cleared": n_cleared}
        row.update({f"r{rk}": scores_by_rank[rk] for rk in range(1, 11)})
        per_profile_data.append(row)

        for r in rankings[:TOP_N]:
            all_top5_scores.append(r.score)

    lines.append("")

    # Aggregate stats
    lines.append("## Aggregate Statistics\n")

    def rank_scores(rank):
        vals = [d[f"r{rank}"] for d in per_profile_data if d[f"r{rank}"] is not None]
        return vals

    def stats_row(label, vals):
        if not vals:
            return f"| {label} | — | — | — |"
        return (
            f"| {label} | {sum(vals)/len(vals):.4f} "
            f"| {min(vals):.4f} | {max(vals):.4f} |"
        )

    lines.append("| Rank position | Mean | Min | Max |")
    lines.append("|---|---|---|---|")
    for rk in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        vals = rank_scores(rk)
        lines.append(stats_row(f"Rank {rk}", vals))
    lines.append("")

    # Gap analysis
    gaps = [d["gap"] for d in per_profile_data if d["gap"] is not None]
    cleared_counts = [d["n_cleared"] for d in per_profile_data]
    lines.append("## Gap Analysis (Rank-1 minus Rank-3)\n")
    lines.append(f"- Mean gap: {sum(gaps)/len(gaps):.4f}")
    lines.append(f"- Min gap: {min(gaps):.4f}")
    lines.append(f"- Max gap: {max(gaps):.4f}")
    lines.append(f"- Profiles with gap > 0.10: {sum(1 for g in gaps if g > 0.10)}")
    lines.append(f"- Profiles with gap > 0.20: {sum(1 for g in gaps if g > 0.20)}")
    lines.append("")

    # States clearing threshold
    lines.append("## States Clearing T=0.25 Per Profile\n")
    lines.append(f"- Mean: {sum(cleared_counts)/len(cleared_counts):.1f}")
    lines.append(f"- Min: {min(cleared_counts)}")
    lines.append(f"- Max: {max(cleared_counts)}")
    lines.append(f"- Distribution:")

    count_dist = collections.Counter(cleared_counts)
    for k in sorted(count_dist):
        lines.append(f"  - {k} states cleared: {count_dist[k]} profiles")
    lines.append("")

    # Natural break / histogram
    lines.append("## Score Histogram -- Rank-1 through Rank-5 (bucket width 0.05)\n")
    lines.append("All 235 scores (47 profiles x 5 ranks) bucketed.\n")

    buckets = collections.defaultdict(int)
    for s in all_top5_scores:
        bucket = int(s / 0.05) * 0.05
        buckets[round(bucket, 2)] += 1

    all_bucket_keys = sorted(buckets.keys())
    if all_bucket_keys:
        b_min = min(all_bucket_keys)
        b_max = max(all_bucket_keys)
        cur = b_min
        while cur <= b_max + 0.001:
            cur_r = round(cur, 2)
            cnt = buckets.get(cur_r, 0)
            bar = "#" * cnt
            lines.append(f"  [{cur_r:.2f}–{cur_r+0.05:.2f})  {cnt:3d}  {bar}")
            cur = round(cur + 0.05, 2)

    lines.append("")

    # Natural break candidates
    lines.append("## Natural Break Candidates\n")
    lines.append("Identifying buckets with count significantly lower than adjacent buckets.\n")
    bucket_list = [(round(b_min + i*0.05, 2), buckets.get(round(b_min + i*0.05, 2), 0))
                   for i in range(int((b_max - b_min) / 0.05) + 2)]
    candidates = []
    for i in range(1, len(bucket_list) - 1):
        lo_b, lo_c = bucket_list[i-1]
        cur_b, cur_c = bucket_list[i]
        hi_b, hi_c = bucket_list[i+1]
        if lo_c > 0 and hi_c > 0 and cur_c == 0:
            candidates.append((cur_b, cur_b + 0.05, "empty bucket"))
        elif lo_c > 0 and hi_c > 0 and cur_c < 0.33 * ((lo_c + hi_c) / 2):
            candidates.append((cur_b, cur_b + 0.05, f"sparse ({cur_c} vs neighbors {lo_c}/{hi_c})"))

    if candidates:
        for lo, hi, note in candidates:
            lines.append(f"- [{lo:.2f}–{hi:.2f}): {note}")
    else:
        lines.append("No clear natural breaks detected in top-5 score distribution.")

    lines.append("")
    lines.append(f"*Note: T=0.25 is the current SCD_WCS_ALIGNMENT_THRESHOLD.*")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Written: {os.path.basename(path)}")

    return per_profile_data


# ── Output 4: Cluster alignment ───────────────────────────────────────────────

def write_cluster_alignment(profile_rankings, hc_profiles, cooccur, top5_sets, path):
    n_profiles = len(profile_rankings)
    all_cluster_members = set(sid for members in NAMED_CLUSTERS.values() for sid in members)

    lines = []
    lines.append("# PRV3 -- Session 25: Cluster Alignment Check")
    lines.append(f"\nNamed clusters vs empirical co-occurrence. 47 HC profiles. Top-{TOP_N} window.\n")
    lines.append("---\n")

    # Per-cluster alignment
    lines.append("## Named Cluster Internal vs Cross Co-Occurrence\n")
    lines.append(
        "Internal co-occurrence rate: fraction of profiles where any two cluster members both appear in top-5.  \n"
        "Cross co-occurrence rate: cluster members appearing in top-5 alongside non-cluster states (average).\n"
    )

    for cluster_name, members in NAMED_CLUSTERS.items():
        members = [m for m in members if m in STATE_PROFILES]
        lines.append(f"### {cluster_name} ({', '.join(members)})\n")

        if len(members) < 2:
            lines.append("(Only 1 member -- no internal pair analysis possible.)\n")
            continue

        # Count profiles where at least 2 cluster members co-appear in top-5
        at_least_two = 0
        all_three = 0 if len(members) >= 3 else None
        for target, top5 in top5_sets.items():
            in_top5 = [m for m in members if m in top5]
            if len(in_top5) >= 2:
                at_least_two += 1
            if len(members) >= 3 and len(in_top5) == len(members):
                all_three += 1

        lines.append(f"- Profiles with >= 2 cluster members in top-5: {at_least_two}/{n_profiles} ({at_least_two/n_profiles:.2%})")
        if all_three is not None:
            lines.append(f"- Profiles with all {len(members)} cluster members in top-5: {all_three}/{n_profiles} ({all_three/n_profiles:.2%})")

        # Per-pair internal counts
        lines.append("\nPair-level counts:")
        for i, a in enumerate(members):
            for b in members[i+1:]:
                pair = tuple(sorted([a, b]))
                cnt = cooccur[pair]
                lines.append(f"- {a} x {b}: {cnt}/47 ({cnt/n_profiles:.2%})")

        # Cross-cluster: how often does each member appear in top-5 profiles where
        # the target is NOT a cluster member
        lines.append("\nAppearance in non-member HC profiles (top-5 frequency):")
        non_member_profiles = {t: top5 for t, top5 in top5_sets.items() if t not in all_cluster_members}
        for m in members:
            appear = sum(1 for top5 in non_member_profiles.values() if m in top5)
            total = len(non_member_profiles)
            lines.append(f"- {m}: appears in {appear}/{total} non-cluster profiles ({appear/total:.2%})")
        lines.append("")

    # Sink dominance analysis
    lines.append("## Known Dominant Sink Appearance Rates\n")
    lines.append(
        "For each known dominant sink, how often does it appear in top-5 rankings "
        "across HC profiles where it is NOT the target state?\n"
    )
    lines.append("| Sink State | Non-target profiles | Appears in top-5 | Rate |")
    lines.append("|---|---|---|---|")

    for sink in KNOWN_SINKS:
        non_target_profiles = [(t, top5) for t, top5 in top5_sets.items() if t != sink]
        appear = sum(1 for _, top5 in non_target_profiles if sink in top5)
        total = len(non_target_profiles)
        lines.append(f"| {sink} | {total} | {appear} | {appear/total:.2%} |")
    lines.append("")

    # Detailed sink breakdown: which profiles does each sink dominate?
    lines.append("## Sink Dominance Detail\n")
    for sink in KNOWN_SINKS:
        dominated = []
        for target, rankings in profile_rankings.items():
            if target == sink:
                continue
            entry = next((r for r in rankings if r.state_id == sink), None)
            if entry and entry.rank <= TOP_N:
                dominated.append((target, entry.rank, entry.score))
        dominated.sort(key=lambda x: x[1])
        lines.append(f"### {sink}")
        lines.append(f"Appears in top-{TOP_N} for {len(dominated)}/46 non-target profiles:\n")
        if dominated:
            lines.append(f"| Target profile | Sink rank | Sink score |")
            lines.append(f"|---|---|---|")
            for target, rank, score in dominated:
                lines.append(f"| {target} | {rank} | {score:.4f} |")
        else:
            lines.append("(Does not appear in top-5 for any non-target HC profile.)")
        lines.append("")

    # Summary: which states appear most frequently in top-5 across ALL profiles
    lines.append("## Most Frequent Top-5 Appearances Across All 47 HC Profiles\n")
    lines.append("(Including as the target state itself.)\n")

    appearance_counts = collections.Counter()
    for top5 in top5_sets.values():
        for sid in top5:
            appearance_counts[sid] += 1

    lines.append("| State | Top-5 appearances (of 47) | Rate |")
    lines.append("|---|---|---|")
    for sid, cnt in appearance_counts.most_common(20):
        lines.append(f"| {sid} | {cnt} | {cnt/n_profiles:.2%} |")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Written: {os.path.basename(path)}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Dry-run: print first 3 profiles and exit without writing files.")
    args = parser.parse_args()

    profile_rankings, hc_profiles = collect_rankings()

    dry_run_check(profile_rankings, hc_profiles)

    if args.check:
        print("--check mode: exiting before writing files.")
        return

    print("Writing output files...")

    write_rankings(
        profile_rankings, hc_profiles,
        os.path.join(TOOLS_DIR, "diag_s25_cooccurrence_rankings.md"),
    )

    cooccur, top5_sets = write_cooccurrence_matrix(
        profile_rankings, hc_profiles,
        os.path.join(TOOLS_DIR, "diag_s25_cooccurrence_matrix.md"),
    )

    write_score_distribution(
        profile_rankings, hc_profiles,
        os.path.join(TOOLS_DIR, "diag_s25_score_distribution.md"),
    )

    write_cluster_alignment(
        profile_rankings, hc_profiles, cooccur, top5_sets,
        os.path.join(TOOLS_DIR, "diag_s25_cluster_alignment.md"),
    )

    print("\nDone. 4 files written to tools/.")
    print(f"rank_states() call signature used: acc_engine.rank(SALIENCE_PROFILES)")
    print(f"  (AccumulationEngine.rank delegates to rank_states(accumulated_vector, answered_question_count, salience_weights))")
    print(f"  answered_question_count inferred from AccumulationEngine internal state")


if __name__ == "__main__":
    main()
