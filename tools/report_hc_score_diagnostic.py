"""
HC Score Diagnostic — v18 (Session 23)

For every HC profile: reports target-state cosine score, rank-1 sink score,
gap to floor, and accumulated primary-liability value.

Purpose: identify whether HC failure is driven by insufficient target signal,
excessive sink alignment, or both. Provides arithmetic for v19 brief to Gemini.

Usage:
  python tools/report_hc_score_diagnostic.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from tools.calibration_runner import (
    ALL_PROFILES, generate_answers, run_profile,
    _get_noise_baseline, QUESTION_LIBRARY,
)
from engine.accumulation import AccumulationEngine, rank_states
from engine.severity import SeverityEngine
from engine.output import OutputEngine, compute_signal_floors
from engine.contract import SessionData, assemble_output
from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.salience import SALIENCE_PROFILES
from engine.data.questions import _build_library
from engine.test_suite import TestAnswer

_DIM_TO_LIABILITY = {
    "Aptitude":  "aptitude_liability",
    "Authority": "authority_liability",
    "Alliance":  "alliance_liability",
    "Attitude":  "attitude_liability",
}


def run_profile_with_vector(tc):
    """Run profile, return (output_dict, accumulated_vector, rankings)."""
    from engine.data.questions import QUESTION_LIBRARY as QL
    from engine.accumulation import IntakeData
    intake = IntakeData(**tc.intake)
    acc_engine = AccumulationEngine(intake)
    sev_engine = SeverityEngine()

    answers = generate_answers(tc)
    for ans in answers:
        q = QL.get(ans.question_id)
        if q is None:
            continue
        for opt_id in ans.selected_option_ids:
            opt = next((o for o in q.answer_options if o.option_id == opt_id), None)
            if opt is None:
                continue
            acc_engine.apply_answer(opt, ans.question_id)

    rankings = acc_engine.rank(SALIENCE_PROFILES)
    sev_result = sev_engine.score()
    out_engine = OutputEngine()
    out_engine.set_noise_baseline(baseline=_get_noise_baseline())
    out_pkg = out_engine.build(rankings, sev_result)

    return acc_engine.accumulated_vector, rankings


def run():
    baseline = _get_noise_baseline()
    floors = compute_signal_floors(baseline)

    hc_profiles = [tc for tc in ALL_PROFILES
                   if tc.profile_type in ("high_confidence", "extreme_high_confidence")]

    # Aggregate by dimension
    by_dim = {}  # dim -> list of (target_score, floor, gap_to_floor, sink_margin)

    rows = []
    for tc in hc_profiles:
        vec, rankings = run_profile_with_vector(tc)

        target = tc.target_state
        profile = STATE_PROFILES.get(target)
        dim = profile.primary_dimension if profile else "?"
        plib_field = _DIM_TO_LIABILITY.get(dim, "")

        primary_accum = vec.get(plib_field, 0.0) if plib_field else 0.0

        rank_map = {r.state_id: r.score for r in rankings}
        target_score = rank_map.get(target, 0.0)
        floor = floors.get(target, 0.0)
        gap_to_floor = floor - target_score  # positive = below floor (failing)

        rank1 = rankings[0] if rankings else None
        if rank1 and rank1.state_id == target:
            sink_id = rankings[1].state_id if len(rankings) > 1 else "—"
            sink_score = rankings[1].score if len(rankings) > 1 else 0.0
        else:
            sink_id = rank1.state_id if rank1 else "—"
            sink_score = rank1.score if rank1 else 0.0

        sink_margin = sink_score - target_score  # positive = sink beating target

        rows.append((
            target, dim, tc.profile_type,
            primary_accum, target_score, floor, gap_to_floor,
            sink_id, sink_score, sink_margin,
        ))

        if dim not in by_dim:
            by_dim[dim] = []
        by_dim[dim].append((target_score, floor, gap_to_floor, sink_margin))

    # ── Print report ──────────────────────────────────────────────────────────

    print("=" * 100)
    print("HC Score Diagnostic — v18 (Session 23)")
    print("=" * 100)
    print()
    print(f"{'State':<45} {'Dim':<10} {'PrimAccum':>9} {'TargScore':>9} "
          f"{'Floor':>7} {'GapToFloor':>10} {'Sink':<45} {'SinkScore':>9} {'SinkMargin':>10}")
    print("-" * 160)

    for (target, dim, ptype, primary_accum, target_score, floor, gap_to_floor,
         sink_id, sink_score, sink_margin) in sorted(rows, key=lambda r: r[1]):
        flag = " !" if gap_to_floor > 0 else " +"
        print(f"{target:<45} {dim:<10} {primary_accum:>9.4f} {target_score:>9.4f} "
              f"{floor:>7.4f} {gap_to_floor:>+10.4f} {sink_id:<45} {sink_score:>9.4f} {sink_margin:>+10.4f}"
              f"{flag}")

    print()
    print("=" * 100)
    print("SUMMARY BY DIMENSION")
    print("=" * 100)
    print(f"  {'Dim':<12} {'N':>3}  {'AvgTargScore':>12}  {'AvgFloor':>8}  "
          f"{'AvgGapToFloor':>13}  {'AvgSinkMargin':>13}  {'MaxGap':>7}  {'MinGap':>7}")
    print("-" * 100)
    for dim in sorted(by_dim.keys()):
        entries = by_dim[dim]
        n = len(entries)
        avg_ts = sum(e[0] for e in entries) / n
        avg_fl = sum(e[1] for e in entries) / n
        avg_gap = sum(e[2] for e in entries) / n
        avg_margin = sum(e[3] for e in entries) / n
        max_gap = max(e[2] for e in entries)
        min_gap = min(e[2] for e in entries)
        print(f"  {dim:<12} {n:>3}  {avg_ts:>12.4f}  {avg_fl:>8.4f}  "
              f"{avg_gap:>+13.4f}  {avg_margin:>+13.4f}  {max_gap:>+7.4f}  {min_gap:>+7.4f}")

    print()
    print("NOTES")
    print("  GapToFloor  = floor - target_score.  Positive = below floor (failing).")
    print("  SinkMargin  = sink_score - target_score.  Positive = sink beating target.")
    print("  PrimAccum   = accumulated value on target state primary liability field.")
    print("  Floor       = min(baseline × multiplier, 0.9650) per v18 ceiling.")
    print()

    # Sink frequency
    from collections import Counter
    sink_counts = Counter(r[7] for r in rows if r[7] != "—")
    print("RANK-1 SINK FREQUENCY (HC profiles only)")
    for sink, cnt in sink_counts.most_common():
        print(f"  {sink:<45}  {cnt:>3}")
    print()


if __name__ == "__main__":
    run()
