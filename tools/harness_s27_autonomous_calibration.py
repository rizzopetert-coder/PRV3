"""
PRV3 Session 27 — Autonomous Calibration Harness

Iterates on CENTROID_FIELD_SCALARS (Path B) and SCD_WCS_CLUSTER_WINDOW (Path C)
until 47/47 HC, 5 consecutive flat rounds (impasse), or an escalation trigger.

Files modified in-loop:
  engine/accumulation.py       — CENTROID_FIELD_SCALARS dict
  tools/calibration_runner.py  — SCD_WCS_CLUSTER_WINDOW constant

Never modifies: engine/data/states.py, engine/data/questions.py,
                engine/data/salience.py, or any test profile file.

Round KPI reports written to: tools/harness_log_s27.md

Pete is pinged (loop stops) on:
  RESOLVED   — 47/47 HC
  IMPASSE    — 5 consecutive flat rounds
  ESCALATING — regression cascade, new sink, or test suite failure
"""

import sys
import os
import re
import copy
import json
import datetime
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = str(Path(__file__).parents[1])
sys.path.insert(0, PROJECT_ROOT)

# ── Configuration ───────────────────────────────────────────────────────────────

RESOLUTION_TARGET       = 47      # HC states that must pass to declare resolution
IMPASSE_ROUNDS          = 5       # consecutive flat rounds before impasse
REGRESSION_LIMIT        = 3       # HC regressions in one round → escalate immediately
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

# Known v23 sinks — new sinks outside this set trigger escalation
V23_SINKS = {"built_to_fail", "leadership_deafness", "the_fracture", "the_diversity_ceiling"}

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

def derive_scalars():
    """
    Count questions that target each primary dimension (via state_targets).
    Scalar = count / 39 (question sequence length).
    Falls back to Gemini hardcoded values if library is empty.
    Returns (scalars_dict, source_label).
    """
    from engine.data.questions import QUESTION_LIBRARY
    from engine.data.states import STATE_PROFILES

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

    N = 39
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
    return scalars, "derived"


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
    pattern = r"SCD_WCS_CLUSTER_WINDOW: float = [\d\.]+"

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
    hc_pct      = round(hc_count / 47 * 100, 1)
    overall_pct = round(overall_pass / overall_total * 100, 1) if overall_total else 0
    top_sink     = max(sink_counts, key=sink_counts.get) if sink_counts else "none"
    top_sink_cnt = sink_counts.get(top_sink, 0) if sink_counts else 0

    lines = [
        f"\n{'─'*44}",
        f"ROUND {round_num} — {version_tag}  [{datetime.datetime.now().strftime('%H:%M:%S')}]",
        f"{'─'*44}",
        f"• HC pass rate:            {hc_count}/47 ({hc_pct}%)",
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
    print("\n[HARNESS] PRV3 Session 27 — Autonomous Calibration Harness")
    print(f"[HARNESS] Target: {RESOLUTION_TARGET}/47 HC | "
          f"Impasse limit: {IMPASSE_ROUNDS} flat rounds | "
          f"Scalar step: {SCALAR_STEP} | Window step: {WINDOW_STEP}")
    print()

    # Init log file
    with open(LOG_PATH, "w", encoding="utf-8") as fh:
        fh.write("# PRV3 S27 Autonomous Calibration Log\n")
        fh.write(f"# Started: {datetime.datetime.now().isoformat()}\n\n")

    # ── Derive starting scalars ────────────────────────────────────────────────
    scalars, scalar_source = derive_scalars()
    window = 0.20  # v23 starting value

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

    # Log initial state
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(f"Starting scalars (source={scalar_source}):\n")
        for f, v in scalars.items():
            fh.write(f"  {f}: {v:.4f}\n")
        fh.write(f"Starting window: {window}\n\n")

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
        overall_total = cal.get("overall_total", 142)
        sink_counts   = cal.get("sink_counts", {})

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

        # Sink emergence check (exclude v23 known sinks and currently-passing states)
        significant_new_sinks = {
            s: c for s, c in sink_counts.items()
            if s not in V23_SINKS and c >= 5 and s not in hc_passing
        }

        # Status determination
        if hc_count >= RESOLUTION_TARGET:
            status = "RESOLVED"
        elif consecutive_flat >= IMPASSE_ROUNDS:
            status = "IMPASSE"
        elif len(regressions_list) >= REGRESSION_LIMIT:
            status = f"ESCALATING — regression cascade: {regressions_list}"
        elif significant_new_sinks:
            status = f"ESCALATING — new sink emerged: {list(significant_new_sinks.keys())}"
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
            print(f"[HARNESS] Final HC: {hc_count}/47")
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
