"""
PRV3 Session 27 — Autonomous Calibration Harness

Iterates on CENTROID_FIELD_SCALARS (Path B) and SCD_WCS_CLUSTER_WINDOW (Path C)
until every HC-tier state passes (RESOLUTION_TARGET, derived from the live
state registry), 5 consecutive flat rounds (impasse), or an escalation trigger.

Files modified in-loop:
  engine/accumulation.py       — CENTROID_FIELD_SCALARS dict
  tools/calibration_runner.py  — SCD_WCS_CLUSTER_WINDOW constant

Never modifies: engine/data/states.py, engine/data/questions.py,
                engine/data/salience.py, or any test profile file.

Round KPI reports written to: tools/harness_log_s27.md

Pete is pinged (loop stops) on:
  RESOLVED   — RESOLUTION_TARGET/RESOLUTION_TARGET HC
  IMPASSE    — 5 consecutive flat rounds
  ESCALATING — regression cascade, new sink, or test suite failure
"""

import sys
import os
import re
import argparse
import copy
import json
import datetime
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = str(Path(__file__).parents[1])
sys.path.insert(0, PROJECT_ROOT)

from engine.data.states import STATE_PROFILES

# ── Configuration ───────────────────────────────────────────────────────────────

# Derived dynamically from the live state registry (was hardcoded 47, the
# pre-taxonomy-expansion state count) -- confirmed this resolves to 57 today,
# and confirmed all 57 states have at least one high_confidence-tier profile
# in the suite, so the target is achievable, not aspirational.
RESOLUTION_TARGET       = len(STATE_PROFILES)  # HC states that must pass to declare resolution
IMPASSE_ROUNDS          = 5       # consecutive flat rounds before impasse
REGRESSION_LIMIT        = 3       # HC regressions in one round → escalate immediately
# Rule A/B -- added this session after the MC_CENTROID_39 finding: HC-
# pass-count-only stop conditions let 16 rounds run while 51 pre-existing,
# unrelated test cases silently regressed (mostly moderate-tier, mostly
# Authority-dimension). Both compare against the Round-0 baseline
# calibration pass, not round-to-round, so gradual drift across many
# rounds is caught the same as a single sharp drop.
RULE_A_FLOOR_PCT        = 0.05    # halt if overall_passed drops >5% below Round-0 baseline
RULE_B_TIER_CAP         = 3       # halt if moderate or weak tier loses >3 passing profiles vs Round-0
# Chronic-sink hybrid threshold -- Gemini-approved this session, added
# because invisible_performance_management (33 captures at Round-0
# baseline, peaked at 55) was structurally invisible to the new-sink
# check: it was already >=5 at that one fixed snapshot, so it could
# never cross into "new" no matter how much worse it got. Requires
# BOTH a relative and an absolute growth threshold so a small sink
# doubling (e.g. 2->4) doesn't trip it, but a large sink growing
# substantially in both senses does.
CHRONIC_SINK_GROWTH_PCT = 0.25    # halt if a baseline sink grows >=25% vs Round-0 baseline
CHRONIC_SINK_GROWTH_DELTA = 8     # AND grows by >=8 captures vs Round-0 baseline
SCALAR_FLOOR            = 0.10    # minimum displacement scalar
SCALAR_CEILING          = 1.00    # maximum displacement scalar (undamped = 1.0)
SCALAR_STEP             = 0.02    # liability scalar reduction per round
ASSET_SCALAR_STEP       = 0.05    # asset scalar adjustment (reserved — not used in Tier 1)
WINDOW_FLOOR            = 0.20    # never narrow cluster window below this
WINDOW_CEILING          = 0.35    # beyond this the criterion is too loose
WINDOW_STEP             = 0.01    # window widening per round
WINDOW_TIER1_MIN_ROUNDS = 3       # wait this many rounds before widening window

LOG_PATH         = os.path.join(PROJECT_ROOT, "tools", "harness_log_s27.md")
ACCUMULATION_PATH = os.path.join(PROJECT_ROOT, "engine", "accumulation.py")
RUNNER_PATH      = os.path.join(PROJECT_ROOT, "tools", "calibration_runner.py")

# Sink baseline is no longer a static set -- captured dynamically at
# harness startup (see baseline_sink_counts in main()). Precedent
# (tools/_mob.txt, S17-S29 campaign): the dominant sink changed almost
# every session historically; a hand-maintained list goes stale fast
# (confirmed this session: 3 of the 4 V23_SINKS entries were no longer
# real sinks, while a 46-capture sink existed undetected outside the set).

# Test scripts to run after each parameter change (pytest not installed)
TEST_SCRIPTS = [
    os.path.join(PROJECT_ROOT, "tools", "test_accumulation.py"),
    os.path.join(PROJECT_ROOT, "tools", "test_contract.py"),
    os.path.join(PROJECT_ROOT, "tools", "test_checkpoint.py"),
    os.path.join(PROJECT_ROOT, "tools", "test_output.py"),
    os.path.join(PROJECT_ROOT, "tools", "test_severity.py"),
]

# Subprocess environment: ensures PYTHONPATH is set for all child processes
_ENV = dict(os.environ)
_ENV["PYTHONPATH"] = PROJECT_ROOT


# ── Step 1: Derive starting scalars from live QUESTION_LIBRARY ─────────────────

def compute_primary_target_counts():
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
    return scalars, "cold_start"


def derive_starting_window() -> tuple[float, str]:
    """
    Dynamically read the committed SCD_WCS_CLUSTER_WINDOW from tools/calibration_runner.py.

    Returns:
        tuple[float, str]: (window_value, source_description)
    """
    try:
        from tools.calibration_runner import SCD_WCS_CLUSTER_WINDOW
        if SCD_WCS_CLUSTER_WINDOW is not None and isinstance(SCD_WCS_CLUSTER_WINDOW, (int, float)):
            return float(SCD_WCS_CLUSTER_WINDOW), "tools.calibration_runner (warm-start)"
    except (ImportError, AttributeError):
        pass

    return 0.20, "hardcoded_default (cold-start fallback)"


# ── Step 2: Write CENTROID_FIELD_SCALARS to accumulation.py ───────────────────

def apply_scalars(scalars: dict, dry_run: bool = True) -> bool:
    """
    Overwrite the CENTROID_FIELD_SCALARS block in engine/accumulation.py.
    Dry-run: verify the target pattern exists and print the change.
    Wet-run: write via pathlib.Path.write_text.
    """
    scalar_block = "CENTROID_FIELD_SCALARS = {\n"
    for f, v in scalars.items():
        scalar_block += f'    "{f}": {v:.4f},\n'
    scalar_block += "}"

    content = Path(ACCUMULATION_PATH).read_text(encoding="utf-8")
    pattern = r"CENTROID_FIELD_SCALARS\s*=\s*\{[^}]*\}"

    if not re.search(pattern, content):
        print(f"[HARNESS] ERROR: CENTROID_FIELD_SCALARS block not found in engine/accumulation.py")
        return False

    new_content = re.sub(pattern, scalar_block, content)

    if dry_run:
        print("[DRY RUN] Would update CENTROID_FIELD_SCALARS in engine/accumulation.py:")
        for f, v in scalars.items():
            print(f"  {f:<30} {v:.4f}")
        return True

    Path(ACCUMULATION_PATH).write_text(new_content, encoding="utf-8")
    print("[HARNESS] Written CENTROID_FIELD_SCALARS to engine/accumulation.py")
    return True


# ── Step 3: Write SCD_WCS_CLUSTER_WINDOW to calibration_runner.py ─────────────

def apply_window(window: float, dry_run: bool = True) -> bool:
    """
    Overwrite SCD_WCS_CLUSTER_WINDOW in tools/calibration_runner.py.
    Matches the ': float =' annotation format used in that file.
    """
    content = Path(RUNNER_PATH).read_text(encoding="utf-8")
    # \\s* tolerates calibration_runner.py's column-aligned spacing
    # ("SCD_WCS_CLUSTER_WINDOW:      float = 0.3500") -- a literal
    # single-space pattern here escalated at the Round 0 smoke test
    # this session before any tuning began, confirmed via a live run.
    pattern = r"SCD_WCS_CLUSTER_WINDOW:\s*float\s*=\s*[\d\.]+"

    if not re.search(pattern, content):
        print("[HARNESS] ERROR: SCD_WCS_CLUSTER_WINDOW pattern not found in calibration_runner.py")
        return False

    new_content = re.sub(pattern, f"SCD_WCS_CLUSTER_WINDOW: float = {window:.4f}", content)

    if dry_run:
        print(f"[DRY RUN] Would set SCD_WCS_CLUSTER_WINDOW: float = {window:.4f}")
        return True

    Path(RUNNER_PATH).write_text(new_content, encoding="utf-8")
    print(f"[HARNESS] Set SCD_WCS_CLUSTER_WINDOW: float = {window:.4f}")
    return True


# ── Step 4: Run test suite (5 scripts; pytest not installed) ───────────────────

def run_test_suite() -> tuple:
    """
    Run all 5 test scripts as subprocesses.
    Returns (all_passed: bool, failing_scripts: list).
    """
    failing = []
    for script in TEST_SCRIPTS:
        r = subprocess.run(
            ["python", script],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=PROJECT_ROOT, env=_ENV,
        )
        if r.returncode != 0:
            name = os.path.basename(script)
            failing.append(name)
            print(f"[HARNESS] TEST FAILURE in {name}:")
            if r.stdout:
                print(r.stdout[-800:])
            if r.stderr:
                print(r.stderr[-400:])
    return len(failing) == 0, failing


# ── Step 5: Run calibration pass → JSON ────────────────────────────────────────

def run_calibration_pass() -> dict:
    """
    Execute calibration_runner.py --output-json as a subprocess.
    Returns parsed JSON dict, or None on failure.
    JSON keys: hc_passing, hc_failing, overall_passing, overall_total, sink_counts.
    """
    r = subprocess.run(
        ["python", "tools/calibration_runner.py", "--output-json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=PROJECT_ROOT, env=_ENV,
    )
    if r.returncode != 0:
        print(f"[HARNESS] Calibration runner exited with code {r.returncode}")
        print(r.stderr[-800:] if r.stderr else "(no stderr)")
        return None
    try:
        return json.loads(r.stdout.strip())
    except json.JSONDecodeError as exc:
        print(f"[HARNESS] JSON parse error: {exc}")
        print(f"  stdout (first 500): {r.stdout[:500]}")
        return None


# ── Step 6: Determine next adjustment ─────────────────────────────────────────

def compute_next_adjustment(
    scalars: dict,
    window: float,
    hc_failing: list,
    tier1_rounds: int,
) -> tuple:
    """
    Determine scalar/window changes for the next round.

    Tier 1: reduce liability scalar for each failing dimension by SCALAR_STEP.
    Tier 2: widen window by WINDOW_STEP if Tier 1 rounds >= WINDOW_TIER1_MIN_ROUNDS
            or all failing dimensions are at floor.

    Returns (new_scalars, new_window, description_string).
    """
    from engine.data.states import STATE_PROFILES
    dim_map = {sid: p.primary_dimension for sid, p in STATE_PROFILES.items()}

    # Collect liability fields for failing states' dimensions
    failing_fields = set()
    for sid in hc_failing:
        d = dim_map.get(sid)
        if d:
            failing_fields.add(f"{d.lower()}_liability")

    new_scalars = copy.deepcopy(scalars)
    adjustments = []
    all_at_floor = True

    for field in sorted(failing_fields):
        current = scalars.get(field, 1.0)
        if current > SCALAR_FLOOR:
            new_val = round(max(SCALAR_FLOOR, current - SCALAR_STEP), 4)
            new_scalars[field] = new_val
            adjustments.append(f"{field} {current:.4f}→{new_val:.4f}")
            all_at_floor = False
        else:
            adjustments.append(f"{field} AT_FLOOR({SCALAR_FLOOR})")

    new_window = window
    if all_at_floor or tier1_rounds >= WINDOW_TIER1_MIN_ROUNDS:
        if window < WINDOW_CEILING:
            new_window = round(window + WINDOW_STEP, 4)
            adjustments.append(f"window {window:.4f}→{new_window:.4f}")

    desc = " | ".join(adjustments) if adjustments else "no adjustment available"
    return new_scalars, new_window, desc


# ── Step 7: Write KPI round report ────────────────────────────────────────────

def write_kpi_report(
    round_num: int,
    version_tag: str,
    hc_passing: list,
    prev_hc_passing: list,
    overall_pass: int,
    overall_total: int,
    sink_counts: dict,
    adj_desc: str,
    consecutive_flat: int,
    status: str,
) -> list:
    """Print and append round KPI to log. Returns regressions list."""
    new_passes  = sorted(set(hc_passing) - set(prev_hc_passing))
    regressions = sorted(set(prev_hc_passing) - set(hc_passing))
    hc_count    = len(hc_passing)
    hc_pct      = round(hc_count / RESOLUTION_TARGET * 100, 1)
    overall_pct = round(overall_pass / overall_total * 100, 1) if overall_total else 0
    top_sink     = max(sink_counts, key=sink_counts.get) if sink_counts else "none"
    top_sink_cnt = sink_counts.get(top_sink, 0) if sink_counts else 0

    lines = [
        f"\n{'─'*44}",
        f"ROUND {round_num} — {version_tag}  [{datetime.datetime.now().strftime('%H:%M:%S')}]",
        f"{'─'*44}",
        f"• HC pass rate:            {hc_count}/{RESOLUTION_TARGET} ({hc_pct}%)",
        f"• Overall pass rate:       {overall_pass}/{overall_total} ({overall_pct}%)",
        f"• New HC passes:           {', '.join(new_passes) or 'none'}",
        f"• HC regressions:          {', '.join(regressions) or 'none'}",
        f"• Dominant sink:           {top_sink} ({top_sink_cnt} captures)",
        f"• Parameter adjusted:      {adj_desc}",
        f"• Consecutive flat rounds: {consecutive_flat}",
        f"• Status:                  {status}",
        f"{'─'*44}",
    ]
    report = "\n".join(lines)
    print(report)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(report + "\n")
    return regressions


# ── Main loop ──────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PRV3 S27 Autonomous Calibration Harness"
    )
    parser.add_argument(
        "--acknowledge-sink",
        action="append",
        default=[],
        metavar="STATE_ID",
        help=(
            "Acknowledge a specific state as a diagnosed, non-blocking sink "
            "for THIS RUN ONLY -- excludes it from the significant_new_sinks "
            "escalation check; every other stop condition (a different new "
            "sink, Rule A, Rule B, IMPASSE) stays fully active. Does not "
            "raise or disable the >=5 capture threshold, does not persist "
            "across runs or add to any allowlist. Repeatable."
        ),
    )
    args = parser.parse_args()
    acknowledged_sinks = set(args.acknowledge_sink)

    print("\n[HARNESS] PRV3 Session 27 — Autonomous Calibration Harness")
    print(f"[HARNESS] Target: {RESOLUTION_TARGET}/{RESOLUTION_TARGET} HC | "
          f"Impasse limit: {IMPASSE_ROUNDS} flat rounds | "
          f"Scalar step: {SCALAR_STEP} | Window step: {WINDOW_STEP}")
    if acknowledged_sinks:
        print(f"[HARNESS] Acknowledged sinks (this run only): {sorted(acknowledged_sinks)}")
    print()

    # Init log file
    with open(LOG_PATH, "w", encoding="utf-8") as fh:
        fh.write("# PRV3 S27 Autonomous Calibration Log\n")
        fh.write(f"# Started: {datetime.datetime.now().isoformat()}\n\n")

    # ── Derive starting scalars ────────────────────────────────────────────────
    scalars, scalar_source = derive_scalars()
    window, window_source = derive_starting_window()
    print(f"[HARNESS] Loaded cluster window from: {window_source}")
    print(f"[HARNESS] Initial window: {window:.4f}")

    # ── Round 0: dry-run smoke test ────────────────────────────────────────────
    print("\n[HARNESS] Round 0: dry-run smoke test")
    if not apply_scalars(scalars, dry_run=True):
        print("[HARNESS] ESCALATE: Scalar pattern not found in accumulation.py. Stop.")
        return
    if not apply_window(window, dry_run=True):
        print("[HARNESS] ESCALATE: Window pattern not found in calibration_runner.py. Stop.")
        return
    print("[HARNESS] Dry-run passed.")

    # ── Apply initial parameters (wet run) ────────────────────────────────────
    print("\n[HARNESS] Applying initial derived scalars (wet run)...")
    if not apply_scalars(scalars, dry_run=False):
        print("[HARNESS] ESCALATE: Wet-run write failed. Stop.")
        return
    if not apply_window(window, dry_run=False):
        print("[HARNESS] ESCALATE: Window wet-run write failed. Stop.")
        return

    # ── Baseline test suite check ──────────────────────────────────────────────
    print("\n[HARNESS] Baseline test suite check (5 scripts)...")
    tests_ok, failing_tests = run_test_suite()
    if not tests_ok:
        print(f"[HARNESS] ESCALATE: Test failures at baseline: {failing_tests}")
        print("[HARNESS] STOP. Ping Pete — test suite failures before round 1.")
        return
    print(f"[HARNESS] Test suite: OK\n")

    # ── Baseline sink-count capture (dynamic, replaces V23_SINKS) ────────────
    # Real empirical snapshot against the freshly-applied initial
    # scalars/window, taken fresh every harness run rather than hand-
    # maintained -- see module-level comment above for why a static set
    # goes stale. Used as the reference point for significant_new_sinks
    # in every round of the loop below.
    print("\n[HARNESS] Baseline sink-count capture...")
    baseline_cal = run_calibration_pass()
    if baseline_cal is None:
        print("[HARNESS] ESCALATE: Baseline calibration pass returned no parseable output. Stop.")
        return
    baseline_sink_counts = baseline_cal["sink_counts"]
    baseline_overall_pass = baseline_cal["overall_passing"]
    baseline_overall_total = baseline_cal["overall_total"]
    baseline_tier_counts = baseline_cal.get("tier_counts", {})
    print(f"[HARNESS] Baseline sinks (>=5 captures): "
          f"{ {s: c for s, c in baseline_sink_counts.items() if c >= 5} }")
    print(f"[HARNESS] Baseline overall: {baseline_overall_pass}/{baseline_overall_total}")
    print(f"[HARNESS] Baseline tier_counts: {baseline_tier_counts}")

    # Log initial state
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"Starting scalars (source={scalar_source}):\n")
        for f, v in scalars.items():
            fh.write(f"  {f}: {v:.4f}\n")
        fh.write(f"Starting window: {window}\n")
        fh.write(f"Baseline sinks (>=5 captures): "
                 f"{ {s: c for s, c in baseline_sink_counts.items() if c >= 5} }\n")
        fh.write(f"Baseline overall: {baseline_overall_pass}/{baseline_overall_total}\n")
        fh.write(f"Baseline tier_counts: {baseline_tier_counts}\n\n")

    # ── Main calibration loop ──────────────────────────────────────────────────
    round_num        = 0
    consecutive_flat = 0
    tier1_rounds     = 0
    prev_hc_passing  = []

    while True:
        round_num += 1
        version_tag = f"v24-r{round_num}"
        print(f"\n[HARNESS] ── Round {round_num} ({version_tag}) ──────────────────────")

        # Run calibration pass
        cal = run_calibration_pass()
        if cal is None:
            print("[HARNESS] ESCALATE: Calibration runner returned no parseable output. Stop.")
            return

        hc_passing    = cal.get("hc_passing", [])
        hc_failing    = cal.get("hc_failing", [])
        overall_pass  = cal.get("overall_passing", 0)
        # Fail loudly rather than silently fall back to a stale hardcoded
        # count -- confirmed this key is unconditionally set by
        # calibration_runner.py's --output-json branch (suite["total"]),
        # never omitted, so a KeyError here means a real schema mismatch
        # worth surfacing immediately, not papering over.
        overall_total = cal["overall_total"]
        sink_counts   = cal.get("sink_counts", {})
        tier_counts   = cal.get("tier_counts", {})

        hc_count  = len(hc_passing)
        prev_count = len(prev_hc_passing)

        # Trajectory tracking
        if hc_count > prev_count:
            consecutive_flat = 0
        else:
            consecutive_flat += 1
        tier1_rounds += 1

        # Regression list
        regressions_list = sorted(set(prev_hc_passing) - set(hc_passing))

        # Sink emergence check -- dynamic baseline (captured at harness
        # startup), not a static hardcoded set or hc_passing membership
        # (the latter was structurally unreachable once hc_passing hit
        # 57/57 -- no sink could ever be "new" regardless of severity).
        # A state counts as a genuinely new/escalating sink only if it is
        # significant NOW (>=5 captures) and was NOT already significant
        # at startup (<5 captures at baseline) -- catches sinks the tuning
        # loop itself creates or worsens, without re-flagging chronic
        # sinks that predate this run.
        raw_significant_new_sinks = {
            s: c for s, c in sink_counts.items()
            if c >= 5 and baseline_sink_counts.get(s, 0) < 5
        }
        significant_new_sinks = {
            s: c for s, c in raw_significant_new_sinks.items()
            if s not in acknowledged_sinks
        }
        overridden_sinks = {
            s: c for s, c in raw_significant_new_sinks.items()
            if s in acknowledged_sinks
        }
        if overridden_sinks:
            override_msg = (
                f"[HARNESS] OVERRIDE: acknowledged sink(s) {overridden_sinks} "
                f"excluded from escalation this round -- diagnosed clean this "
                f"session, scoped to this run only via --acknowledge-sink, not "
                f"a threshold change, not a permanent allowlist."
            )
            print(override_msg)
            with open(LOG_PATH, "a", encoding="utf-8") as fh:
                fh.write(f"\n{override_msg}\n")

        # Chronic-sink check -- Gemini-approved hybrid threshold (this
        # session): a state already significant at the fixed Round-0
        # baseline (>=5 captures, the complement of the new-sink check's
        # <5 condition) that has since grown by BOTH >=25% relative AND
        # >=8 absolute captures. Added because invisible_performance_
        # management (33 at baseline, peaked at 55 during reconvergence)
        # was structurally invisible to significant_new_sinks -- already
        # >=5 at that one fixed snapshot, so it could never cross into
        # "new" no matter how much worse it got. Same fixed-baseline
        # comparison as the new-sink check (not a rolling window), same
        # ESCALATING severity, same acknowledged_sinks set --
        # --acknowledge-sink applies to both checks identically.
        raw_chronic_sinks = {}
        for s, c in sink_counts.items():
            base_c = baseline_sink_counts.get(s, 0)
            if base_c < 5:
                continue
            growth = c - base_c
            growth_pct = growth / base_c if base_c > 0 else 0.0
            if growth_pct >= CHRONIC_SINK_GROWTH_PCT and growth >= CHRONIC_SINK_GROWTH_DELTA:
                raw_chronic_sinks[s] = {
                    "baseline": base_c, "current": c,
                    "delta": growth, "pct": round(growth_pct, 4),
                }
        chronic_sinks = {
            s: d for s, d in raw_chronic_sinks.items()
            if s not in acknowledged_sinks
        }
        overridden_chronic_sinks = {
            s: d for s, d in raw_chronic_sinks.items()
            if s in acknowledged_sinks
        }
        if overridden_chronic_sinks:
            override_chronic_msg = (
                f"[HARNESS] OVERRIDE (chronic): acknowledged sink(s) "
                f"{overridden_chronic_sinks} excluded from chronic-growth "
                f"escalation this round -- diagnosed clean this session, "
                f"scoped to this run only via --acknowledge-sink, not a "
                f"threshold change, not a permanent allowlist."
            )
            print(override_chronic_msg)
            with open(LOG_PATH, "a", encoding="utf-8") as fh:
                fh.write(f"\n{override_chronic_msg}\n")

        # Rule A -- overall suite floor: halt if overall_passed drops more
        # than RULE_A_FLOOR_PCT below the Round-0 baseline. Rule B --
        # secondary tier cap: halt if moderate or weak tier loses more than
        # RULE_B_TIER_CAP passing profiles vs Round-0 baseline. Both checked
        # before RESOLVED -- a "resolution" built on a collapsed overall
        # suite is exactly the failure mode this session's MC_CENTROID_39
        # finding documented (HC gains bought by silent, unrelated
        # regressions), so a floor/cap breach halts even if RESOLUTION_
        # TARGET is hit the same round.
        rule_a_breach = (
            baseline_overall_pass > 0
            and overall_pass < baseline_overall_pass * (1 - RULE_A_FLOOR_PCT)
        )
        rule_b_breach = []
        for tier in ("moderate", "weak"):
            base_tier_passed = baseline_tier_counts.get(tier, {}).get("passed", 0)
            cur_tier_passed = tier_counts.get(tier, {}).get("passed", 0)
            if base_tier_passed - cur_tier_passed > RULE_B_TIER_CAP:
                rule_b_breach.append(
                    f"{tier} {base_tier_passed}\u2192{cur_tier_passed} "
                    f"(-{base_tier_passed - cur_tier_passed})"
                )

        # Status determination
        if rule_a_breach:
            drop_pct = (baseline_overall_pass - overall_pass) / baseline_overall_pass
            status = (
                f"ESCALATING — Rule A overall suite floor breached: "
                f"{overall_pass}/{overall_total} vs baseline "
                f"{baseline_overall_pass}/{baseline_overall_total} ({drop_pct:.1%} drop)"
            )
        elif rule_b_breach:
            status = f"ESCALATING — Rule B secondary tier cap breached: {rule_b_breach}"
        elif hc_count >= RESOLUTION_TARGET:
            status = "RESOLVED"
        elif consecutive_flat >= IMPASSE_ROUNDS:
            status = "IMPASSE"
        elif len(regressions_list) >= REGRESSION_LIMIT:
            status = f"ESCALATING — regression cascade: {regressions_list}"
        else:
            reasons = []
            if significant_new_sinks:
                reasons.append(f"new sink emerged: {list(significant_new_sinks.keys())}")
            if chronic_sinks:
                reasons.append(f"chronic sink worsening: {chronic_sinks}")
            if reasons:
                status = "ESCALATING — " + " | ".join(reasons)
            else:
                status = "CONTINUING"

        # Next adjustment (only if continuing)
        if status == "CONTINUING":
            new_scalars, new_window, adj_desc = compute_next_adjustment(
                scalars, window, hc_failing, tier1_rounds
            )
        else:
            new_scalars, new_window, adj_desc = scalars, window, "none — loop terminating"

        # Write KPI report
        write_kpi_report(
            round_num, version_tag,
            hc_passing, prev_hc_passing,
            overall_pass, overall_total,
            sink_counts, adj_desc,
            consecutive_flat, status,
        )

        # Stop conditions
        if status != "CONTINUING":
            print(f"\n[HARNESS] ═══════════════════════════════════════")
            print(f"[HARNESS] STOP. Status: {status}")
            print(f"[HARNESS] Final HC: {hc_count}/{RESOLUTION_TARGET}")
            print(f"[HARNESS] Failing:  {sorted(hc_failing)}")
            print(f"[HARNESS] Final scalars:")
            for f, v in scalars.items():
                print(f"  {f:<30} {v:.4f}")
            print(f"[HARNESS] Final window: {window:.4f}")
            print(f"[HARNESS] Log: {LOG_PATH}")
            print(f"[HARNESS] ═══════════════════════════════════════")
            if status == "RESOLVED":
                print("[HARNESS] RESOLUTION ACHIEVED. Ping Pete.")
            elif status == "IMPASSE":
                print("[HARNESS] IMPASSE: 5 flat rounds. Ping Pete.")
                print("  Recommendation: Gemini brief — state vector or salience weight intervention.")
            else:
                print("[HARNESS] ESCALATION. Ping Pete for direction.")
            return

        # Apply next round parameters
        scalars = new_scalars
        window  = new_window
        prev_hc_passing = hc_passing

        apply_scalars(scalars, dry_run=False)
        apply_window(window, dry_run=False)

        # Test suite after parameter change — escalate on any failure
        tests_ok, failing_tests = run_test_suite()
        if not tests_ok:
            msg = f"Test suite failures after round {round_num}: {failing_tests}"
            print(f"[HARNESS] ESCALATE: {msg}")
            with open(LOG_PATH, "a", encoding="utf-8") as fh:
                fh.write(f"\nESCALATION: {msg}\n")
            print("[HARNESS] STOP. Ping Pete — do not continue until failures are resolved.")
            return


# ── Entry point ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
