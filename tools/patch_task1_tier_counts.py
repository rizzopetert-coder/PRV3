"""
MC_CENTROID_39 recalibration -- Task 1: add tier_counts to
tools/calibration_runner.py's --output-json serialization, aggregating
from suite["by_profile_type"] (confirmed real key, _build_suite_v23
line 754). Existing hc_passing/hc_failing/overall_passing/overall_total/
sink_counts keys unchanged -- tier_counts is additive, feeds Rule A/B in
the harness (Task 2).

Usage:
  python tools/patch_task1_tier_counts.py --dry-run
  python tools/patch_task1_tier_counts.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNER_PATH = REPO_ROOT / "tools" / "calibration_runner.py"

OLD = (
    '        sink_j: dict = {}\n'
    '        for tgt, preds in matrix.items():\n'
    '            for pred, cnt in preds.items():\n'
    '                if pred != tgt:\n'
    '                    sink_j[pred] = sink_j.get(pred, 0) + cnt\n'
    '        print(json.dumps({\n'
    '            "hc_passing":      hc_passing_j,\n'
    '            "hc_failing":      hc_failing_j,\n'
    '            "overall_passing": suite["passed"],\n'
    '            "overall_total":   suite["total"],\n'
    '            "sink_counts":     sink_j,\n'
    '        }))\n'
    '        sys.exit(0)\n'
)

NEW = (
    '        sink_j: dict = {}\n'
    '        for tgt, preds in matrix.items():\n'
    '            for pred, cnt in preds.items():\n'
    '                if pred != tgt:\n'
    '                    sink_j[pred] = sink_j.get(pred, 0) + cnt\n'
    '        # tier_counts -- Rule A/B input (harness_s27_autonomous_calibration.py).\n'
    '        # hc combines high_confidence + extreme_high_confidence, matching how\n'
    '        # RESOLUTION_TARGET/hc_passing already treat the two as one tier.\n'
    '        by_pt = suite["by_profile_type"]\n'
    '        tier_counts = {\n'
    '            "hc": {\n'
    '                "passed": by_pt["high_confidence"]["passed"] + by_pt["extreme_high_confidence"]["passed"],\n'
    '                "total":  by_pt["high_confidence"]["total"] + by_pt["extreme_high_confidence"]["total"],\n'
    '            },\n'
    '            "moderate": {\n'
    '                "passed": by_pt["moderate"]["passed"],\n'
    '                "total":  by_pt["moderate"]["total"],\n'
    '            },\n'
    '            "weak": {\n'
    '                "passed": by_pt["weak"]["passed"],\n'
    '                "total":  by_pt["weak"]["total"],\n'
    '            },\n'
    '        }\n'
    '        print(json.dumps({\n'
    '            "hc_passing":      hc_passing_j,\n'
    '            "hc_failing":      hc_failing_j,\n'
    '            "overall_passing": suite["passed"],\n'
    '            "overall_total":   suite["total"],\n'
    '            "sink_counts":     sink_j,\n'
    '            "tier_counts":     tier_counts,\n'
    '        }))\n'
    '        sys.exit(0)\n'
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = RUNNER_PATH.read_text(encoding="utf-8")
    count = content.count(OLD)
    if count != 1:
        print(f"ABORT: expected exactly 1 match for anchor, found {count}")
        sys.exit(1)
    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print("=== tools/calibration_runner.py: 1 edit would apply cleanly ===")
    else:
        RUNNER_PATH.write_text(new_content, encoding="utf-8")
        print("=== tools/calibration_runner.py: 1 edit written ===")


if __name__ == "__main__":
    main()
