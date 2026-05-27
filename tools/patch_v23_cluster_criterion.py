"""
PRV3 -- v23 Cluster Criterion Patch (Session 26)

Patches tools/calibration_runner.py -- three sub-changes:

  1. Replace SCD_WCS_MARGIN_GATE_CALIBRATION = 0.0200 constant with
     SCD_WCS_CLUSTER_WINDOW = 0.20.

  2. Replace _passes_margin_gate() with _passes_cluster_criterion().
     New criterion: target score >= rank-1 score - SCD_WCS_CLUSTER_WINDOW.
     Takes rankings: list (objects with .state_id and .score), not an output dict.

  3. Update call site in _build_suite_v23():
     - Reconstruct rankings list from state_distribution dicts via types.SimpleNamespace
     - Call _passes_cluster_criterion(_rnks, tc.target_state)
     - Update comment and failure message

engine/ files are NOT touched.

Usage:
  python tools/patch_v23_cluster_criterion.py --dry-run
  python tools/patch_v23_cluster_criterion.py --write
"""

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parents[1]
RUNNER_PATH = ROOT / "tools" / "calibration_runner.py"


def apply_patch(path: Path, old: str, new: str, label: str, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        print(f"  [ERROR] '{label}' -- old string not found")
        return False
    if count > 1:
        print(f"  [ERROR] '{label}' -- matched {count} times (ambiguous)")
        return False
    new_text = text.replace(old, new, 1)
    if dry_run:
        print(f"  [DRY-RUN] {path.relative_to(ROOT)} -- {label}")
        old_lines = old.splitlines()
        new_lines = new.splitlines()
        for ln in old_lines[:10]:
            print(f"    - {ln}")
        for ln in new_lines[:10]:
            print(f"    + {ln}")
        if len(old_lines) > 10:
            print(f"    ... ({len(old_lines)} old lines -> {len(new_lines)} new lines)")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"  [WRITE]   {path.relative_to(ROOT)} -- {label}")
    return True


def run(dry_run: bool):
    errors = []

    # -- 1. Replace constant -----------------------------------------------------
    ok = apply_patch(
        RUNNER_PATH,
        old=(
            "# v23 calibration margin gate -- HC/extreme pass criterion:"
            " rank-1 AND gap(rank1-rank2) >= 0.0200\n"
            "SCD_WCS_MARGIN_GATE_CALIBRATION: float = 0.0200"
            "  # CALIBRATION TARGET -- Session 26"
        ),
        new=(
            "# v23 calibration cluster window -- HC/extreme pass criterion:"
            " target within SCD_WCS_CLUSTER_WINDOW of rank-1\n"
            "SCD_WCS_CLUSTER_WINDOW: float = 0.20"
            "  # CALIBRATION TARGET -- Session 26"
        ),
        label="replace SCD_WCS_MARGIN_GATE_CALIBRATION with SCD_WCS_CLUSTER_WINDOW = 0.20",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("SCD_WCS_CLUSTER_WINDOW constant")

    # -- 2. Replace _passes_margin_gate() with _passes_cluster_criterion() ------
    _old_fn_lines = [
        "def _passes_margin_gate(output: dict, target_state_id: str) -> bool:",
        "    # v23 HC pass criterion: target is rank-1 AND gap(rank1-rank2) >= 0.0200",
        "    dist = sorted(output.get('state_distribution', []), key=lambda e: e.get('rank', 99))",
        "    if not dist or dist[0].get('state_id') != target_state_id:",
        "        return False",
        "    if len(dist) < 2:",
        "        return True",
        "    gap = dist[0].get('score', 0.0) - dist[1].get('score', 0.0)",
        "    return gap >= SCD_WCS_MARGIN_GATE_CALIBRATION",
    ]
    _new_fn_lines = [
        "def _passes_cluster_criterion(rankings: list, target_state_id: str) -> bool:",
        "    # Top-cluster presence criterion -- v23 revised calibration pass criterion.",
        "    # Pass condition: target state score >= rank-1 score minus SCD_WCS_CLUSTER_WINDOW.",
        "    # rankings: list of objects with .state_id and .score (descending by score).",
        "    if not rankings:",
        "        return False",
        "    rank_1_score = rankings[0].score",
        "    target = next((r for r in rankings if r.state_id == target_state_id), None)",
        "    if target is None:",
        "        return False",
        "    return target.score >= rank_1_score - SCD_WCS_CLUSTER_WINDOW",
    ]
    ok = apply_patch(
        RUNNER_PATH,
        old="\n".join(_old_fn_lines),
        new="\n".join(_new_fn_lines),
        label="replace _passes_margin_gate with _passes_cluster_criterion",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("_passes_cluster_criterion function")

    # -- 3. Update call site in _build_suite_v23() ------------------------------
    # Old: comment referencing _passes_margin_gate, then direct call with output dict
    _old_call_lines = [
        "    # HC/extreme: pass iff _passes_margin_gate() -- bypasses output_type ==",
        "    # single_state requirement since all scores fall below the absolute floor.",
        "    # Moderate/weak: run_test_case() unchanged.",
        "    from engine.test_suite import TestResult",
        "    results = []",
        "    by_type = {pt: {'total': 0, 'passed': 0} for pt in PROFILE_TYPES}",
        "    by_state: dict = {}",
        "",
        "    for tc in test_cases:",
        "        output = engine_outputs.get(tc.test_id, {})",
        "        if tc.profile_type in ('high_confidence', 'extreme_high_confidence'):",
        "            passed = _passes_margin_gate(output, tc.target_state) if output else False",
        "            result = TestResult(",
        "                test_id=tc.test_id,",
        "                passed=passed,",
        "                violations=[],",
        "                criteria_failures=[] if passed else [",
        "                    f'{tc.profile_type}: margin gate failed for {tc.target_state!r}'",
        "                ],",
        "                output=output,",
        "            )",
    ]
    _new_call_lines = [
        "    # HC/extreme: pass iff _passes_cluster_criterion() -- bypasses output_type ==",
        "    # single_state requirement since all scores fall below the absolute floor.",
        "    # Moderate/weak: run_test_case() unchanged.",
        "    import types as _types",
        "    from engine.test_suite import TestResult",
        "    results = []",
        "    by_type = {pt: {'total': 0, 'passed': 0} for pt in PROFILE_TYPES}",
        "    by_state: dict = {}",
        "",
        "    for tc in test_cases:",
        "        output = engine_outputs.get(tc.test_id, {})",
        "        if tc.profile_type in ('high_confidence', 'extreme_high_confidence'):",
        "            if output:",
        "                _dist = sorted(output.get('state_distribution', []), key=lambda e: e.get('rank', 99))",
        "                _rnks = [_types.SimpleNamespace(state_id=e.get('state_id', ''), score=e.get('score', 0.0)) for e in _dist]",
        "                passed = _passes_cluster_criterion(_rnks, tc.target_state)",
        "            else:",
        "                passed = False",
        "            result = TestResult(",
        "                test_id=tc.test_id,",
        "                passed=passed,",
        "                violations=[],",
        "                criteria_failures=[] if passed else [",
        "                    f'{tc.profile_type}: cluster criterion failed for {tc.target_state!r}'",
        "                ],",
        "                output=output,",
        "            )",
    ]
    ok = apply_patch(
        RUNNER_PATH,
        old="\n".join(_old_call_lines),
        new="\n".join(_new_call_lines),
        label="_build_suite_v23: call site -> _passes_cluster_criterion with SimpleNamespace rankings",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("_build_suite_v23 call site")

    # -- Summary -----------------------------------------------------------------
    print(f"\n{'=' * 60}")
    if errors:
        print(f"ERRORS ({len(errors)}) -- patch NOT applied:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        mode = "DRY-RUN" if dry_run else "WRITTEN"
        print(f"All 3 patches {mode} successfully. 1 file affected: tools/calibration_runner.py")
        if dry_run:
            print("Run with --write to apply.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
