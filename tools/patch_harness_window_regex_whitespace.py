"""
MC_CENTROID_39 recalibration -- Step 4 blocker fix: apply_window()'s
regex assumed literal single-space formatting ("SCD_WCS_CLUSTER_WINDOW:
float = ") but tools/calibration_runner.py actually uses column-aligned
spacing ("SCD_WCS_CLUSTER_WINDOW:      float = 0.3500"), causing the
harness to escalate at the Round 0 smoke test before any actual tuning
began -- confirmed via a live run this session, nothing was written to
either engine/accumulation.py or tools/calibration_runner.py before the
escalation (git status clean on both).

apply_scalars()'s CENTROID_FIELD_SCALARS pattern was checked for the same
class of bug and confirmed NOT affected -- it already uses \\s* around
"=" (r"CENTROID_FIELD_SCALARS\\s*=\\s*\\{[^}]*\\}"), and its Round 0
dry-run succeeded in the same live run.

Only tools/harness_s27_autonomous_calibration.py is touched here, per
Pete's explicit instruction -- tools/calibration_runner.py's actual
formatting is left exactly as-is.

Usage:
  python tools/patch_harness_window_regex_whitespace.py --dry-run
  python tools/patch_harness_window_regex_whitespace.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_PATH = REPO_ROOT / "tools" / "harness_s27_autonomous_calibration.py"

OLD = (
    '    content = Path(RUNNER_PATH).read_text(encoding="utf-8")\n'
    '    pattern = r"SCD_WCS_CLUSTER_WINDOW: float = [\\d\\.]+"\n'
)

NEW = (
    '    content = Path(RUNNER_PATH).read_text(encoding="utf-8")\n'
    "    # \\\\s* tolerates calibration_runner.py's column-aligned spacing\n"
    '    # ("SCD_WCS_CLUSTER_WINDOW:      float = 0.3500") -- a literal\n'
    "    # single-space pattern here escalated at the Round 0 smoke test\n"
    "    # this session before any tuning began, confirmed via a live run.\n"
    '    pattern = r"SCD_WCS_CLUSTER_WINDOW:\\s*float\\s*=\\s*[\\d\\.]+"\n'
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = HARNESS_PATH.read_text(encoding="utf-8")
    count = content.count(OLD)
    if count != 1:
        print(f"ABORT: expected exactly 1 match for anchor, found {count}")
        print(f"  anchor: {OLD!r}")
        sys.exit(1)
    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print("=== tools/harness_s27_autonomous_calibration.py: 1 edit would apply cleanly ===")
    else:
        HARNESS_PATH.write_text(new_content, encoding="utf-8")
        print("=== tools/harness_s27_autonomous_calibration.py: 1 edit written ===")


if __name__ == "__main__":
    main()
