"""
MC_CENTROID_39 recalibration -- scoped, one-time sink-escalation override.

Adds --acknowledge-sink=STATE_ID (repeatable), a CLI flag that lets
main() proceed past a SPECIFIC, already-diagnosed sink's ESCALATING stop
for THIS RUN ONLY. Every other stop condition (a different new sink,
Rule A, Rule B, IMPASSE) remains fully active and unmodified. Does not
raise or disable the significant_new_sinks >=5 capture threshold, does
not persist across runs, does not add anything to a permanent allowlist
-- if the same state crosses the threshold again in a future invocation
run without this flag, it is caught and reviewed fresh, exactly as
before.

Authorized this session, scoped specifically to the_unformed_leader,
based on a clean diagnostic: baseline=3 captures, round1=3, round2=7
(crossed threshold), zero test regressions across all 5 affected source
states (narrative_lock, groundhog_day, the_basement_standard,
motivational_architecture_failure, the_burned_credibility -- all
Attitude-primary, all misclassifying into the_unformed_leader as
attitude_liability's displacement scalar is reduced), Rule A/B healthy
throughout both rounds checked.

When an acknowledged sink is what's suppressing an escalation that would
otherwise have fired, this is logged explicitly (stdout + KPI log) at
the round it applies to -- what was acknowledged, the capture count, and
why, referencing this session's diagnostic. If a DIFFERENT, non-
acknowledged sink also crosses threshold in the same round, escalation
still fires normally (the acknowledgment only removes the one named
state from consideration, not the whole check).

Usage:
  python tools/patch_acknowledge_sink_override.py --dry-run
  python tools/patch_acknowledge_sink_override.py --write
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


# 1. Add argparse import
edit(
    "import sys\n"
    "import os\n"
    "import re\n",
    "import sys\n"
    "import os\n"
    "import re\n"
    "import argparse\n",
)

# 2. Parse --acknowledge-sink at the top of main()
edit(
    'def main():\n'
    '    print("\\n[HARNESS] PRV3 Session 27 — Autonomous Calibration Harness")\n'
    '    print(f"[HARNESS] Target: {RESOLUTION_TARGET}/{RESOLUTION_TARGET} HC | "\n'
    '          f"Impasse limit: {IMPASSE_ROUNDS} flat rounds | "\n'
    '          f"Scalar step: {SCALAR_STEP} | Window step: {WINDOW_STEP}")\n'
    '    print()\n',
    'def main():\n'
    '    parser = argparse.ArgumentParser(\n'
    '        description="PRV3 S27 Autonomous Calibration Harness"\n'
    '    )\n'
    '    parser.add_argument(\n'
    '        "--acknowledge-sink",\n'
    '        action="append",\n'
    '        default=[],\n'
    '        metavar="STATE_ID",\n'
    '        help=(\n'
    '            "Acknowledge a specific state as a diagnosed, non-blocking sink "\n'
    '            "for THIS RUN ONLY -- excludes it from the significant_new_sinks "\n'
    '            "escalation check; every other stop condition (a different new "\n'
    '            "sink, Rule A, Rule B, IMPASSE) stays fully active. Does not "\n'
    '            "raise or disable the >=5 capture threshold, does not persist "\n'
    '            "across runs or add to any allowlist. Repeatable."\n'
    '        ),\n'
    '    )\n'
    '    args = parser.parse_args()\n'
    '    acknowledged_sinks = set(args.acknowledge_sink)\n'
    '\n'
    '    print("\\n[HARNESS] PRV3 Session 27 — Autonomous Calibration Harness")\n'
    '    print(f"[HARNESS] Target: {RESOLUTION_TARGET}/{RESOLUTION_TARGET} HC | "\n'
    '          f"Impasse limit: {IMPASSE_ROUNDS} flat rounds | "\n'
    '          f"Scalar step: {SCALAR_STEP} | Window step: {WINDOW_STEP}")\n'
    '    if acknowledged_sinks:\n'
    '        print(f"[HARNESS] Acknowledged sinks (this run only): {sorted(acknowledged_sinks)}")\n'
    '    print()\n',
)

# 3. significant_new_sinks: compute raw (unfiltered) + filtered, log the override
edit(
    '        significant_new_sinks = {\n'
    '            s: c for s, c in sink_counts.items()\n'
    '            if c >= 5 and baseline_sink_counts.get(s, 0) < 5\n'
    '        }\n',
    '        raw_significant_new_sinks = {\n'
    '            s: c for s, c in sink_counts.items()\n'
    '            if c >= 5 and baseline_sink_counts.get(s, 0) < 5\n'
    '        }\n'
    '        significant_new_sinks = {\n'
    '            s: c for s, c in raw_significant_new_sinks.items()\n'
    '            if s not in acknowledged_sinks\n'
    '        }\n'
    '        overridden_sinks = {\n'
    '            s: c for s, c in raw_significant_new_sinks.items()\n'
    '            if s in acknowledged_sinks\n'
    '        }\n'
    '        if overridden_sinks:\n'
    '            override_msg = (\n'
    '                f"[HARNESS] OVERRIDE: acknowledged sink(s) {overridden_sinks} "\n'
    '                f"excluded from escalation this round -- diagnosed clean this "\n'
    '                f"session, scoped to this run only via --acknowledge-sink, not "\n'
    '                f"a threshold change, not a permanent allowlist."\n'
    '            )\n'
    '            print(override_msg)\n'
    '            with open(LOG_PATH, "a", encoding="utf-8") as fh:\n'
    '                fh.write(f"\\n{override_msg}\\n")\n',
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
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        content = content.replace(old, new, 1)

    if args.dry_run:
        print(f"=== tools/harness_s27_autonomous_calibration.py: {len(EDITS)} edit(s) would apply cleanly ===")
    else:
        HARNESS_PATH.write_text(content, encoding="utf-8")
        print(f"=== tools/harness_s27_autonomous_calibration.py: {len(EDITS)} edit(s) written ===")


if __name__ == "__main__":
    main()
