"""
PRV3 Session 27 — Diagnostic: 9 Failing HC Profile Characterization
Read-only. No engine modifications.

Five diagnostic sections:
  1. state_targets coverage — all 47 states
  2. Actual scores and ranks for 9 failing HC states
  3. the_policy_lag — best-option signal map
  4. hr_capture — cross-dimension sink analysis
  5. Coverage vs. gap correlation summary

Outputs to stdout and writes tools/diag_s27_failing_hc_characterization.md
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import QUESTION_LIBRARY
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.salience import SALIENCE_PROFILES
from engine.accumulation import AccumulationEngine, IntakeData, MC_CENTROID_39
from tools.calibration_runner import (
    ALL_PROFILES,
    generate_answers,
    best_option_for_state,
    _neutral_option,
    _passes_cluster_criterion,
    SCD_WCS_CLUSTER_WINDOW,
)

FAILING_HC_STATES = [
    "the_pay_fog",
    "the_tolerated_violation",
    "dueling_narratives",
    "transition_paralysis",
    "the_unexamined_algorithm",
    "hr_capture",
    "leadership_continuity_risk",
    "paper_shield",
    "the_policy_lag",
]


# ── Smoke test ─────────────────────────────────────────────────────────────────

def smoke_test():
    total_q = len(QUESTION_LIBRARY)
    q_with_targets = sum(1 for q in QUESTION_LIBRARY.values() if q.state_targets)
    print(f"SMOKE TEST: {total_q} questions in QUESTION_LIBRARY, "
          f"{q_with_targets} with non-empty state_targets")
    if total_q == 0:
        print("HARD STOP: QUESTION_LIBRARY is empty.")
        sys.exit(1)
    if q_with_targets == 0:
        print("HARD STOP: All state_targets arrays are empty — library population issue.")
        sys.exit(1)
    print("  (Pass)\n")


# ── Section 1: state_targets coverage ─────────────────────────────────────────

def get_state_targets_coverage():
    """
    Build dict: state_id -> list of question_ids that list that state in state_targets.
    Covers all 47 states.
    """
    coverage = {s: [] for s in STATE_PROFILES}
    for q_id, q in QUESTION_LIBRARY.items():
        for state_id in (q.state_targets or []):
            if state_id in coverage:
                coverage[state_id].append(q_id)
    return coverage


# ── Section 2: Actual scores and ranks ────────────────────────────────────────

def _run_hc_profile(tc):
    """
    Run an HC test case through AccumulationEngine exactly as calibration_runner.py
    does in run_profile(). Returns (rankings, accumulated_vector, n_answered).
    """
    intake = IntakeData(**tc.intake)
    acc_engine = AccumulationEngine(intake)
    answers = generate_answers(tc)

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
    return rankings, acc_engine.accumulated_vector, len(answers)


def get_failing_hc_scores(coverage):
    """
    For each of the 9 failing states, find their HC test case from ALL_PROFILES,
    run it, and record scores/ranks.
    """
    # One HC test case per failing state (first encountered in ALL_PROFILES order)
    hc_cases = {}
    for tc in ALL_PROFILES:
        if tc.profile_type in ("high_confidence", "extreme_high_confidence"):
            if tc.target_state in FAILING_HC_STATES and tc.target_state not in hc_cases:
                hc_cases[tc.target_state] = tc

    results = []
    for state_id in FAILING_HC_STATES:
        tc = hc_cases.get(state_id)
        if tc is None:
            results.append({"state_id": state_id, "error": "No HC test case found in ALL_PROFILES"})
            continue

        rankings, acc_vec, n_answered = _run_hc_profile(tc)

        rank1 = rankings[0]
        target_r = next((r for r in rankings if r.state_id == state_id), None)
        if target_r is None:
            results.append({"state_id": state_id, "error": "Target state not found in rankings output"})
            continue

        gap = rank1.score - target_r.score
        results.append({
            "state_id":     state_id,
            "target_score": target_r.score,
            "target_rank":  target_r.rank,
            "rank1_state":  rank1.state_id,
            "rank1_score":  rank1.score,
            "gap":          gap,
            "passes":       _passes_cluster_criterion(rankings, state_id),
            "n_answered":   n_answered,
            "q_count":      len(coverage.get(state_id, [])),
            "acc_vec":      acc_vec,
            "rankings":     rankings,
            "tc":           tc,
        })

    return results


# ── Section 3: policy_lag signal map ──────────────────────────────────────────

def get_policy_lag_signal_map(coverage):
    """
    For the_policy_lag, show which option best_option_for_state() picks per
    state_targets question, the authority_liability contribution from that option,
    and the neutral-option contribution for comparison.
    """
    sid = "the_policy_lag"
    rows = []
    total_best_auth_l = 0.0
    total_neutral_auth_l = 0.0

    for q_id in sorted(coverage.get(sid, [])):
        q = QUESTION_LIBRARY.get(q_id)
        if q is None:
            continue
        best    = best_option_for_state(q, sid)
        neutral = _neutral_option(q)

        b_auth_l = best.dimensional_contributions.get("authority_liability", 0.0)
        n_auth_l = neutral.dimensional_contributions.get("authority_liability", 0.0)
        total_best_auth_l    += b_auth_l
        total_neutral_auth_l += n_auth_l

        rows.append({
            "q_id":          q_id,
            "best_opt_id":   best.option_id,
            "best_auth_l":   b_auth_l,
            "best_full_vec": dict(best.dimensional_contributions),
            "neutral_opt_id": neutral.option_id,
            "neutral_auth_l": n_auth_l,
        })

    return rows, total_best_auth_l, total_neutral_auth_l


# ── Section 4: hr_capture cross-dimension analysis ────────────────────────────

def analyze_hr_capture(hc_results):
    """
    For hr_capture HC profile:
    - Show profile vectors for hr_capture and the_diversity_ceiling
    - Show the accumulated session vector and its centroid-displaced form
    - Show SCD-WCS scores for both states against the hr_capture session
    - Field-by-field: which direction does the displaced vector push each state?
    """
    hr_r = next((r for r in hc_results if r["state_id"] == "hr_capture"), None)
    if not hr_r or "error" in hr_r:
        return None

    hr_profile = STATE_PROFILES.get("hr_capture")
    dc_profile = STATE_PROFILES.get("the_diversity_ceiling")
    rankings   = hr_r["rankings"]
    acc_vec    = hr_r["acc_vec"]
    n          = hr_r["n_answered"]

    # Centroid scaled to session length (mirrors rank_states() internally)
    scale = n / 39.0
    displaced_vec = {
        f: acc_vec.get(f, 0.0) - MC_CENTROID_39.get(f, 0.0) * scale
        for f in DIMENSIONAL_FIELDS
    }

    return {
        "hr_pv":        hr_profile.dimensional_vector.as_dict() if hr_profile else {},
        "dc_pv":        dc_profile.dimensional_vector.as_dict() if dc_profile else {},
        "acc_vec":      acc_vec,
        "displaced_vec": displaced_vec,
        "hr_score":     next((r.score for r in rankings if r.state_id == "hr_capture"), None),
        "dc_score":     next((r.score for r in rankings if r.state_id == "the_diversity_ceiling"), None),
        "hr_rank":      next((r.rank  for r in rankings if r.state_id == "hr_capture"), None),
        "dc_rank":      next((r.rank  for r in rankings if r.state_id == "the_diversity_ceiling"), None),
        "n":            n,
        "scale":        scale,
    }


# ── Report builder ─────────────────────────────────────────────────────────────

def build_report():
    lines = []

    def p(s=""):
        lines.append(s)
        print(s)

    p("=" * 72)
    p("PRV3 Session 27 — 9 Failing HC Profiles Diagnostic")
    p(f"Engine: v23 | Cluster window: Delta={SCD_WCS_CLUSTER_WINDOW}")
    p("=" * 72)

    coverage   = get_state_targets_coverage()
    hc_results = get_failing_hc_scores(coverage)

    # ── SECTION 1 ────────────────────────────────────────────────────────────
    p()
    p("## SECTION 1: state_targets coverage — all 47 HC states")
    p(f"{'State':<44} {'Qs':>4}  {'HC status':>12}  Question IDs")
    p("-" * 90)

    passing_counts, failing_counts = [], []
    for s in sorted(STATE_PROFILES.keys()):
        q_list = sorted(coverage.get(s, []))
        status = "FAILING" if s in FAILING_HC_STATES else "passing"
        q_str  = ", ".join(q_list) or "(none)"
        p(f"{s:<44} {len(q_list):>4}  {status:>12}  {q_str}")
        (failing_counts if s in FAILING_HC_STATES else passing_counts).append(len(q_list))

    p()
    p("Summary (question count):")
    p(f"  Passing HC states ({len(passing_counts)}): "
      f"min={min(passing_counts)}, max={max(passing_counts)}, "
      f"mean={sum(passing_counts)/len(passing_counts):.1f}")
    p(f"  Failing HC states ({len(failing_counts)}):  "
      f"min={min(failing_counts)}, max={max(failing_counts)}, "
      f"mean={sum(failing_counts)/len(failing_counts):.1f}")

    # ── SECTION 2 ────────────────────────────────────────────────────────────
    p()
    p("## SECTION 2: Actual scores and ranks — 9 failing HC states")
    p(f"{'State':<44} {'Tgt score':>10} {'Rank':>5} "
      f"{'Rank-1 sink':<44} {'R1 score':>9} {'Gap':>7} {'Pass':>5}")
    p("-" * 130)

    for r in hc_results:
        if "error" in r:
            p(f"{r['state_id']:<44}  ERROR: {r['error']}")
            continue
        buried = "  <<BURIED" if r["target_rank"] > 10 else ""
        p(f"{r['state_id']:<44} {r['target_score']:>10.4f} {r['target_rank']:>5} "
          f"{r['rank1_state']:<44} {r['rank1_score']:>9.4f} {r['gap']:>7.4f} "
          f"{'Y' if r['passes'] else 'N':>5}{buried}")

    p()
    p("Top-5 rankings for each failing state:")
    for r in hc_results:
        if "error" in r:
            continue
        p(f"\n  {r['state_id']} "
          f"(target rank={r['target_rank']}, score={r['target_score']:.4f}, "
          f"gap={r['gap']:.4f}):")
        for ranking in r["rankings"][:5]:
            marker = "  <<< TARGET" if ranking.state_id == r["state_id"] else ""
            p(f"    rank {ranking.rank:>2}: {ranking.state_id:<44} "
              f"score={ranking.score:.4f}{marker}")

    # ── SECTION 3 ────────────────────────────────────────────────────────────
    p()
    p("## SECTION 3: the_policy_lag — best-option signal map")
    rows, total_best, total_neutral = get_policy_lag_signal_map(coverage)

    if not rows:
        p("  WARNING: No state_targets questions found for the_policy_lag.")
        p("  This is a hard diagnostic signal — the state may have zero targeted questions.")
    else:
        p(f"  {'Q-ID':<10} {'Best':>6} {'auth_l (best)':>14} "
          f"{'Neutral':>9} {'auth_l (neutral)':>17}  "
          f"Best-opt vector (apt / aut / all / att liability)")
        p("  " + "-" * 105)
        for row in rows:
            vec = row["best_full_vec"]
            vec_s = (f"apt={vec.get('aptitude_liability',0):.2f}  "
                     f"aut={vec.get('authority_liability',0):.2f}  "
                     f"all={vec.get('alliance_liability',0):.2f}  "
                     f"att={vec.get('attitude_liability',0):.2f}")
            p(f"  {row['q_id']:<10} {row['best_opt_id']:>6} {row['best_auth_l']:>14.4f} "
              f"{row['neutral_opt_id']:>9} {row['neutral_auth_l']:>17.4f}  {vec_s}")

        p()
        p(f"  Cumulative authority_liability — state_targets questions only:")
        p(f"    Best-option path:       {total_best:.4f}")
        p(f"    Neutral path:           {total_neutral:.4f}")
        p(f"    Delta (best - neutral): {total_best - total_neutral:.4f}")

    pl_r = next((r for r in hc_results if r["state_id"] == "the_policy_lag"), None)
    if pl_r and "acc_vec" in pl_r:
        acc = pl_r["acc_vec"]
        n   = pl_r["n_answered"]
        p()
        p(f"  Full HC session accumulated vector for the_policy_lag (n={n} questions):")
        p(f"  {'Field':<30} {'Accumulated':>12} {'Centroid*scale':>15} {'Displaced':>11}")
        p("  " + "-" * 72)
        for f in DIMENSIONAL_FIELDS:
            centroid_scaled = MC_CENTROID_39.get(f, 0.0) * (n / 39.0)
            displaced       = acc.get(f, 0.0) - centroid_scaled
            p(f"  {f:<30} {acc.get(f,0):>12.4f} {centroid_scaled:>15.4f} {displaced:>11.4f}")

    # ── SECTION 4 ────────────────────────────────────────────────────────────
    p()
    p("## SECTION 4: hr_capture — cross-dimension sink analysis")
    hr_a = analyze_hr_capture(hc_results)

    if hr_a is None:
        p("  ERROR: Could not run hr_capture analysis.")
    else:
        p(f"  SCD-WCS result against hr_capture HC session:")
        p(f"    hr_capture:            rank={hr_a['hr_rank']:>3}  score={hr_a['hr_score']:.4f}")
        p(f"    the_diversity_ceiling:  rank={hr_a['dc_rank']:>3}  score={hr_a['dc_score']:.4f}")
        p(f"    Gap (DC over HR): {hr_a['dc_score'] - hr_a['hr_score']:.4f}")

        p()
        p(f"  Profile vectors (hr_capture vs the_diversity_ceiling):")
        p(f"  {'Field':<30} {'HR profile':>12} {'DC profile':>12}")
        p("  " + "-" * 56)
        for f in DIMENSIONAL_FIELDS:
            hr_v = hr_a["hr_pv"].get(f, 0.0)
            dc_v = hr_a["dc_pv"].get(f, 0.0)
            p(f"  {f:<30} {hr_v:>12.4f} {dc_v:>12.4f}")

        p()
        p(f"  hr_capture HC session: accumulated → displaced "
          f"(n={hr_a['n']}, centroid scale={hr_a['scale']:.3f}x):")
        p(f"  Note: displaced = accumulated − (MC_CENTROID_39 × scale). "
          f"This is what SCD-WCS ranks against.")
        p(f"  {'Field':<30} {'Accumulated':>12} {'Centroid×scale':>15} "
          f"{'Displaced':>10}  {'HR dot':>8}  {'DC dot':>8}  {'Favors'}")
        p("  " + "-" * 100)
        for f in DIMENSIONAL_FIELDS:
            acc_v  = hr_a["acc_vec"].get(f, 0.0)
            disp_v = hr_a["displaced_vec"].get(f, 0.0)
            c_v    = MC_CENTROID_39.get(f, 0.0) * hr_a["scale"]
            hr_v   = hr_a["hr_pv"].get(f, 0.0)
            dc_v   = hr_a["dc_pv"].get(f, 0.0)
            # Raw dot contribution (unweighted — directional guide only, not actual WCS)
            hr_dot = disp_v * hr_v
            dc_dot = disp_v * dc_v
            favors = "DC" if dc_dot > hr_dot else "HR" if hr_dot > dc_dot else "--"
            p(f"  {f:<30} {acc_v:>12.4f} {c_v:>15.4f} {disp_v:>10.4f}  "
              f"{hr_dot:>8.4f}  {dc_dot:>8.4f}  {favors}")

        p()
        p("  Note: 'Favors' reflects raw displaced×profile dot product only.")
        p("  Actual SCD-WCS uses salience-weighted cosine + normalization —")
        p("  the above is directional intuition, not the exact scoring mechanism.")

    # ── SECTION 5 ────────────────────────────────────────────────────────────
    p()
    p("## SECTION 5: coverage vs. gap correlation — 9 failing states")
    p(f"  {'State':<44} {'Gap':>7} {'Q count':>8}  Question IDs")
    p("  " + "-" * 90)

    valid = [r for r in hc_results if "error" not in r]
    for r in sorted(valid, key=lambda x: x["gap"], reverse=True):
        q_ids = sorted(coverage.get(r["state_id"], []))
        p(f"  {r['state_id']:<44} {r['gap']:>7.4f} {r['q_count']:>8}  "
          f"{', '.join(q_ids) or '(none)'}")

    gaps   = [r["gap"] for r in valid]
    counts = [r["q_count"] for r in valid]
    n_pts  = len(gaps)
    if n_pts > 1:
        mean_g = sum(gaps) / n_pts
        mean_c = sum(counts) / n_pts
        cov    = sum((gaps[i] - mean_g) * (counts[i] - mean_c) for i in range(n_pts))
        std_g  = sum((g - mean_g) ** 2 for g in gaps) ** 0.5
        std_c  = sum((c - mean_c) ** 2 for c in counts) ** 0.5
        r_val  = cov / (std_g * std_c) if std_g > 0 and std_c > 0 else 0.0
        p()
        p(f"  Pearson r (gap vs. question count): {r_val:.3f}")
        if abs(r_val) < 0.3:
            p("  Conclusion: weak/no correlation — question count alone does not explain gap size.")
        elif r_val < -0.3:
            p("  Conclusion: negative correlation — more questions associated with smaller gaps.")
        else:
            p("  Conclusion: positive correlation — unusual, requires investigation.")

    p()
    p("=" * 72)
    p("Diagnostic complete — read-only. No engine files modified.")
    p("=" * 72)

    return "\n".join(lines)


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    smoke_test()
    report = build_report()
    out_path = Path(__file__).parent / "diag_s27_failing_hc_characterization.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"\nReport written to: {out_path}")
