"""
MC_CENTROID_39 recalibration -- Task 2: replace derive_scalars() with the
Gemini-final warm-start design, and add Rule A (overall suite floor) /
Rule B (secondary tier cap) to main()'s per-round evaluation.

derive_scalars() now warm-starts unconditionally from
engine.accumulation.CENTROID_FIELD_SCALARS when populated -- no Delta-
Share adjustment, Rule A/B supersede that mechanism. Cold-start fallback
(CENTROID_FIELD_SCALARS empty) computes fresh counts via the new
compute_primary_target_counts(), reading _QDATA directly at index 6
(state_targets) -- confirmed against _build_library()'s own unpacking
order (qid, text, fmt, pos, seg, opts, targets, sev) before use; index 3
is sequence_position, not state_targets, a bug caught in Gemini's first
draft and corrected before this implementation. Denominator N =
len(_CORE_QUESTION_IDS) preserved unchanged (the already-locked fixed
per-question count, not sum-of-dimension-tallies, which double-counts
any question touching multiple dimensions -- confirmed a ~2.5x
discrepancy on live data before this round).

Rule A/B read from Task 1's new tier_counts (tools/calibration_runner.py
--output-json), compared against the Round-0 baseline calibration pass
that already existed in main() (baseline_cal, captured before the round
loop begins) -- extended to also capture baseline_overall_pass/
baseline_overall_total/baseline_tier_counts alongside the existing
baseline_sink_counts. Both rules are checked before RESOLVED in the
status-determination order, so a floor/cap breach halts the loop even if
RESOLUTION_TARGET is hit the same round -- a "resolution" built on a
collapsed overall suite isn't a real resolution, which is exactly the
failure mode this session's MC_CENTROID_39 finding documented (16 rounds
of HC gains bought by 51 silent, unrelated regressions, mostly moderate-
tier, mostly Authority-dimension).

Usage:
  python tools/patch_task2_warmstart_and_rules_ab.py --dry-run
  python tools/patch_task2_warmstart_and_rules_ab.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_PATH = REPO_ROOT / "tools" / "harness_s27_autonomous_calibration.py"

EDITS: list[tuple[str, str]] = []


def edit(old: str, new: str):
    EDITS.append((old, new))


# ============================================================================
# 1. New config constants (Rule A / Rule B thresholds)
# ============================================================================

edit(
    'RESOLUTION_TARGET       = len(STATE_PROFILES)  # HC states that must pass to declare resolution\n'
    'IMPASSE_ROUNDS          = 5       # consecutive flat rounds before impasse\n'
    'REGRESSION_LIMIT        = 3       # HC regressions in one round → escalate immediately\n',
    'RESOLUTION_TARGET       = len(STATE_PROFILES)  # HC states that must pass to declare resolution\n'
    'IMPASSE_ROUNDS          = 5       # consecutive flat rounds before impasse\n'
    'REGRESSION_LIMIT        = 3       # HC regressions in one round → escalate immediately\n'
    '# Rule A/B -- added this session after the MC_CENTROID_39 finding: HC-\n'
    '# pass-count-only stop conditions let 16 rounds run while 51 pre-existing,\n'
    '# unrelated test cases silently regressed (mostly moderate-tier, mostly\n'
    '# Authority-dimension). Both compare against the Round-0 baseline\n'
    '# calibration pass, not round-to-round, so gradual drift across many\n'
    '# rounds is caught the same as a single sharp drop.\n'
    'RULE_A_FLOOR_PCT        = 0.05    # halt if overall_passed drops >5% below Round-0 baseline\n'
    'RULE_B_TIER_CAP         = 3       # halt if moderate or weak tier loses >3 passing profiles vs Round-0\n',
)

# ============================================================================
# 2. derive_scalars() rewrite + new compute_primary_target_counts()
# ============================================================================

OLD_DERIVE_BLOCK = '''def derive_scalars():
    """
    Count questions that target each primary dimension (via state_targets).
    Scalar = count / N, where N is the live core-question count.
    Falls back to Gemini hardcoded values if library is empty.
    Returns (scalars_dict, source_label).

    N source, confirmed this session: len(QUESTION_LIBRARY) is NOT usable
    directly -- it includes SEVER-##, DIST-##, VERIFY-Q##, and FOLLOW
    variants, not just core questions (87 vs. 41 core, confirmed by direct
    count). Uses tools.calibration_runner._CORE_QUESTION_IDS instead --
    the closest existing "core question" concept in this codebase, and the
    one this harness's own calibration loop actually iterates over via
    generate_answers(). Note this is NOT identical to the live product's
    respondent-facing PHASE_1_QUESTION_SEQUENCE (32, defined in
    web/lib/session-store.ts, not importable from Python, and already on
    record as diverging from _CORE_QUESTION_IDS by excluding the Q35-39
    Aptitude addenda) -- this value is internally consistent with what the
    calibration harness itself simulates, which is what this scalar seed is
    for.
    """
    from engine.data.questions import QUESTION_LIBRARY
    from engine.data.states import STATE_PROFILES
    from tools.calibration_runner import _CORE_QUESTION_IDS

    dim_map = {sid: p.primary_dimension for sid, p in STATE_PROFILES.items()}
    dim_counts = {"Aptitude": 0, "Authority": 0, "Alliance": 0, "Attitude": 0}
    q_with_targets = 0

    for q in QUESTION_LIBRARY.values():
        if not q.state_targets:
            continue
        q_with_targets += 1
        touched_dims = set()
        for sid in q.state_targets:
            d = dim_map.get(sid)
            if d in dim_counts:
                touched_dims.add(d)
        for d in touched_dims:
            dim_counts[d] += 1

    if q_with_targets == 0:
        print("[HARNESS] WARNING: QUESTION_LIBRARY empty — using Gemini hardcoded scalars")
        return {
            "aptitude_liability":  0.2564,
            "aptitude_asset":      0.4000,
            "authority_liability": 0.3590,
            "authority_asset":     0.4000,
            "alliance_liability":  0.2051,
            "alliance_asset":      0.4000,
            "attitude_liability":  0.3846,
            "attitude_asset":      0.4000,
        }, "fallback"

    N = len(_CORE_QUESTION_IDS)
    scalars = {
        "aptitude_liability":  round(dim_counts["Aptitude"]  / N, 4),
        "aptitude_asset":      0.4000,
        "authority_liability": round(dim_counts["Authority"] / N, 4),
        "authority_asset":     0.4000,
        "alliance_liability":  round(dim_counts["Alliance"]  / N, 4),
        "alliance_asset":      0.4000,
        "attitude_liability":  round(dim_counts["Attitude"]  / N, 4),
        "attitude_asset":      0.4000,
    }

    print(f"[HARNESS] Derived scalars from library (questions with state_targets: {q_with_targets}):")
    print(f"  dim_counts: {dim_counts}")
    for f, v in scalars.items():
        print(f"  {f:<30} {v:.4f}")
    return scalars, "derived"'''

NEW_DERIVE_BLOCK = '''def compute_primary_target_counts():
    """
    Cold-start only (called from derive_scalars() when
    engine.accumulation.CENTROID_FIELD_SCALARS is empty). Counts questions
    targeting each primary dimension directly from engine/data/questions.py's
    _QDATA -- index 6 is state_targets, confirmed this session against
    _build_library()'s own unpacking order:
        for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:
    Index 3 is sequence_position (int or None), not state_targets -- a bug
    in an earlier draft of this function, caught before implementation.

    Denominator N = len(_CORE_QUESTION_IDS), the already-locked fixed
    per-question count. NOT sum(dim_counts.values()) -- that double-counts
    any question whose state_targets span multiple primary dimensions
    (confirmed ~2.5x discrepancy on live data: 134 vs. 53).

    Returns a scalars dict (not a tuple) -- derive_scalars() attaches the
    "cold_start" source label.
    """
    from engine.data.questions import _QDATA
    from engine.data.states import STATE_PROFILES
    from tools.calibration_runner import _CORE_QUESTION_IDS

    dim_map = {sid: p.primary_dimension for sid, p in STATE_PROFILES.items()}
    dim_counts = {"Aptitude": 0, "Authority": 0, "Alliance": 0, "Attitude": 0}
    q_with_targets = 0

    for entry in _QDATA:
        state_targets = entry[6]
        if not state_targets:
            continue
        q_with_targets += 1
        touched_dims = set()
        for sid in state_targets:
            d = dim_map.get(sid)
            if d in dim_counts:
                touched_dims.add(d)
        for d in touched_dims:
            dim_counts[d] += 1

    if q_with_targets == 0:
        print("[HARNESS] WARNING: _QDATA empty — using Gemini hardcoded scalars")
        return {
            "aptitude_liability":  0.2564,
            "aptitude_asset":      0.4000,
            "authority_liability": 0.3590,
            "authority_asset":     0.4000,
            "alliance_liability":  0.2051,
            "alliance_asset":      0.4000,
            "attitude_liability":  0.3846,
            "attitude_asset":      0.4000,
        }

    N = len(_CORE_QUESTION_IDS)
    scalars = {
        "aptitude_liability":  round(dim_counts["Aptitude"]  / N, 4),
        "aptitude_asset":      0.4000,
        "authority_liability": round(dim_counts["Authority"] / N, 4),
        "authority_asset":     0.4000,
        "alliance_liability":  round(dim_counts["Alliance"]  / N, 4),
        "alliance_asset":      0.4000,
        "attitude_liability":  round(dim_counts["Attitude"]  / N, 4),
        "attitude_asset":      0.4000,
    }
    print(f"[HARNESS] Cold-start dim_counts (questions with state_targets: {q_with_targets}, N={N}): {dim_counts}")
    for f, v in scalars.items():
        print(f"  {f:<30} {v:.4f}")
    return scalars


def derive_scalars():
    """
    Warm-start unconditionally from engine.accumulation.CENTROID_FIELD_SCALARS
    when populated -- returned as-is, no Delta-Share adjustment (Rule A/B
    in main() supersede that mechanism). Preserves whatever configuration
    last converged/was committed, avoiding the discontinuous from-scratch
    re-derivation that caused an 84-test-case regression jump when this
    harness last ran (documented in tools/_mob.txt's MC_CENTROID_39 finding
    and the Round-16 ESCALATING replay analysis, same session).

    Cold-start fallback (CENTROID_FIELD_SCALARS empty): see
    compute_primary_target_counts().

    Returns (scalars_dict, source_label). Zero-arg signature, tuple
    return -- unchanged, no call-site changes needed.
    """
    from engine.accumulation import CENTROID_FIELD_SCALARS

    if CENTROID_FIELD_SCALARS:
        print("[HARNESS] Warm-start from engine.accumulation.CENTROID_FIELD_SCALARS:")
        for f, v in CENTROID_FIELD_SCALARS.items():
            print(f"  {f:<30} {v:.4f}")
        return dict(CENTROID_FIELD_SCALARS), "warm_start"

    print("[HARNESS] CENTROID_FIELD_SCALARS empty — cold-start from _QDATA")
    scalars = compute_primary_target_counts()
    return scalars, "cold_start"'''

edit(OLD_DERIVE_BLOCK, NEW_DERIVE_BLOCK)

# ============================================================================
# 3. Extend baseline capture to also capture overall/tier baseline
# ============================================================================

edit(
    '    baseline_sink_counts = baseline_cal["sink_counts"]\n'
    '    print(f"[HARNESS] Baseline sinks (>=5 captures): "\n'
    '          f"{ {s: c for s, c in baseline_sink_counts.items() if c >= 5} }")\n'
    '\n'
    '    # Log initial state\n'
    '    with open(LOG_PATH, "a", encoding="utf-8") as fh:\n'
    '        fh.write(f"Starting scalars (source={scalar_source}):\\n")\n'
    '        for f, v in scalars.items():\n'
    '            fh.write(f"  {f}: {v:.4f}\\n")\n'
    '        fh.write(f"Starting window: {window}\\n")\n'
    '        fh.write(f"Baseline sinks (>=5 captures): "\n'
    '                 f"{ {s: c for s, c in baseline_sink_counts.items() if c >= 5} }\\n\\n")\n',
    '    baseline_sink_counts = baseline_cal["sink_counts"]\n'
    '    baseline_overall_pass = baseline_cal["overall_passing"]\n'
    '    baseline_overall_total = baseline_cal["overall_total"]\n'
    '    baseline_tier_counts = baseline_cal.get("tier_counts", {})\n'
    '    print(f"[HARNESS] Baseline sinks (>=5 captures): "\n'
    '          f"{ {s: c for s, c in baseline_sink_counts.items() if c >= 5} }")\n'
    '    print(f"[HARNESS] Baseline overall: {baseline_overall_pass}/{baseline_overall_total}")\n'
    '    print(f"[HARNESS] Baseline tier_counts: {baseline_tier_counts}")\n'
    '\n'
    '    # Log initial state\n'
    '    with open(LOG_PATH, "a", encoding="utf-8") as fh:\n'
    '        fh.write(f"Starting scalars (source={scalar_source}):\\n")\n'
    '        for f, v in scalars.items():\n'
    '            fh.write(f"  {f}: {v:.4f}\\n")\n'
    '        fh.write(f"Starting window: {window}\\n")\n'
    '        fh.write(f"Baseline sinks (>=5 captures): "\n'
    '                 f"{ {s: c for s, c in baseline_sink_counts.items() if c >= 5} }\\n")\n'
    '        fh.write(f"Baseline overall: {baseline_overall_pass}/{baseline_overall_total}\\n")\n'
    '        fh.write(f"Baseline tier_counts: {baseline_tier_counts}\\n\\n")\n',
)

# ============================================================================
# 4. Extract tier_counts in the round loop + add Rule A/B, wired into status
# ============================================================================

edit(
    '        overall_total = cal["overall_total"]\n'
    '        sink_counts   = cal.get("sink_counts", {})\n',
    '        overall_total = cal["overall_total"]\n'
    '        sink_counts   = cal.get("sink_counts", {})\n'
    '        tier_counts   = cal.get("tier_counts", {})\n',
)

edit(
    '        # Status determination\n'
    '        if hc_count >= RESOLUTION_TARGET:\n'
    '            status = "RESOLVED"\n'
    '        elif consecutive_flat >= IMPASSE_ROUNDS:\n'
    '            status = "IMPASSE"\n'
    '        elif len(regressions_list) >= REGRESSION_LIMIT:\n'
    '            status = f"ESCALATING — regression cascade: {regressions_list}"\n'
    '        elif significant_new_sinks:\n'
    '            status = f"ESCALATING — new sink emerged: {list(significant_new_sinks.keys())}"\n'
    '        else:\n'
    '            status = "CONTINUING"\n',
    '        # Rule A -- overall suite floor: halt if overall_passed drops more\n'
    '        # than RULE_A_FLOOR_PCT below the Round-0 baseline. Rule B --\n'
    '        # secondary tier cap: halt if moderate or weak tier loses more than\n'
    '        # RULE_B_TIER_CAP passing profiles vs Round-0 baseline. Both checked\n'
    '        # before RESOLVED -- a "resolution" built on a collapsed overall\n'
    '        # suite is exactly the failure mode this session\'s MC_CENTROID_39\n'
    '        # finding documented (HC gains bought by silent, unrelated\n'
    '        # regressions), so a floor/cap breach halts even if RESOLUTION_\n'
    '        # TARGET is hit the same round.\n'
    '        rule_a_breach = (\n'
    '            baseline_overall_pass > 0\n'
    '            and overall_pass < baseline_overall_pass * (1 - RULE_A_FLOOR_PCT)\n'
    '        )\n'
    '        rule_b_breach = []\n'
    '        for tier in ("moderate", "weak"):\n'
    '            base_tier_passed = baseline_tier_counts.get(tier, {}).get("passed", 0)\n'
    '            cur_tier_passed = tier_counts.get(tier, {}).get("passed", 0)\n'
    '            if base_tier_passed - cur_tier_passed > RULE_B_TIER_CAP:\n'
    '                rule_b_breach.append(\n'
    '                    f"{tier} {base_tier_passed}\\u2192{cur_tier_passed} "\n'
    '                    f"(-{base_tier_passed - cur_tier_passed})"\n'
    '                )\n'
    '\n'
    '        # Status determination\n'
    '        if rule_a_breach:\n'
    '            drop_pct = (baseline_overall_pass - overall_pass) / baseline_overall_pass\n'
    '            status = (\n'
    '                f"ESCALATING — Rule A overall suite floor breached: "\n'
    '                f"{overall_pass}/{overall_total} vs baseline "\n'
    '                f"{baseline_overall_pass}/{baseline_overall_total} ({drop_pct:.1%} drop)"\n'
    '            )\n'
    '        elif rule_b_breach:\n'
    '            status = f"ESCALATING — Rule B secondary tier cap breached: {rule_b_breach}"\n'
    '        elif hc_count >= RESOLUTION_TARGET:\n'
    '            status = "RESOLVED"\n'
    '        elif consecutive_flat >= IMPASSE_ROUNDS:\n'
    '            status = "IMPASSE"\n'
    '        elif len(regressions_list) >= REGRESSION_LIMIT:\n'
    '            status = f"ESCALATING — regression cascade: {regressions_list}"\n'
    '        elif significant_new_sinks:\n'
    '            status = f"ESCALATING — new sink emerged: {list(significant_new_sinks.keys())}"\n'
    '        else:\n'
    '            status = "CONTINUING"\n',
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = HARNESS_PATH.read_text(encoding="utf-8")
    for i, (old, new) in enumerate(EDITS, 1):
        count = content.count(old)
        if count != 1:
            print(f"ABORT: edit {i}: expected exactly 1 match for anchor, found {count}")
            print(f"  anchor (first 200 chars): {old[:200]!r}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print(f"=== tools/harness_s27_autonomous_calibration.py: {len(EDITS)} edit(s) would apply cleanly ===")
    else:
        HARNESS_PATH.write_text(content, encoding="utf-8")
        print(f"=== tools/harness_s27_autonomous_calibration.py: {len(EDITS)} edit(s) written ===")


if __name__ == "__main__":
    main()
