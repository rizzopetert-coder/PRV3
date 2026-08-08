"""
MC_CENTROID_39 follow-up, Task 2: chronic-sink detection, per Gemini's
approved Q1-Q4 design (hybrid threshold: baseline>=5 AND growth>=25%
AND delta>=8 captures; ESCALATING halt, same severity as new-sink
detection; fixed Round-0 baseline comparison; --acknowledge-sink applies
identically, no new flag).

Deliberately does NOT rename significant_new_sinks -- confirmed via
direct read of the real code that it has exactly one downstream
consumer (the status-determination elif), and Gemini's proposed rename
to new_sinks would require touching that line for zero functional
benefit. chronic_sinks is added as a parallel, independent path,
mirroring significant_new_sinks's own structure (raw -> filtered by
acknowledged_sinks -> overridden), reusing the same acknowledged_sinks
set, not a new flag.

chronic sinks carry baseline/current/delta/pct, not just a capture
count, so they get their own OVERRIDE (chronic): log line -- the
existing OVERRIDE: format (plain {state: count} dict) can't represent
that data, kept visually distinct rather than overloading the same
format.

Three edits, all in tools/harness_s27_autonomous_calibration.py:
  1. Two new constants (CHRONIC_SINK_GROWTH_PCT, CHRONIC_SINK_GROWTH_DELTA)
     alongside RULE_A_FLOOR_PCT/RULE_B_TIER_CAP.
  2. chronic_sinks computation + its own OVERRIDE (chronic): block,
     inserted right after the existing new-sink OVERRIDE block.
  3. Combined new-sink + chronic-sink status check, replacing the
     trailing "elif significant_new_sinks: / else:" pair -- confirmed
     via direct read of the live file that this pair is the LAST branch
     in the chain (after rule_a_breach, rule_b_breach, RESOLVED,
     IMPASSE, regression cascade), not positioned "before RESOLVED/
     IMPASSE" as an earlier paraphrase assumed. Both checks now report
     together (joined by " | ") if both fire the same round, instead of
     new-sink short-circuiting chronic-sink via elif. Verified this is
     a pure addition for the new-sink-only case: when chronic_sinks is
     empty, reasons contains exactly the old single string and
     "ESCALATING — " + reasons[0] reproduces the old f-string byte for
     byte.

Usage:
  python tools/patch_chronic_sink_detection.py --dry-run
  python tools/patch_chronic_sink_detection.py --write
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


# 1. Two new constants, alongside RULE_A_FLOOR_PCT/RULE_B_TIER_CAP.
edit(
    'RULE_A_FLOOR_PCT        = 0.05    # halt if overall_passed drops >5% below Round-0 baseline\n'
    'RULE_B_TIER_CAP         = 3       # halt if moderate or weak tier loses >3 passing profiles vs Round-0\n'
    'SCALAR_FLOOR            = 0.10    # minimum displacement scalar\n',
    'RULE_A_FLOOR_PCT        = 0.05    # halt if overall_passed drops >5% below Round-0 baseline\n'
    'RULE_B_TIER_CAP         = 3       # halt if moderate or weak tier loses >3 passing profiles vs Round-0\n'
    '# Chronic-sink hybrid threshold -- Gemini-approved this session, added\n'
    '# because invisible_performance_management (33 captures at Round-0\n'
    '# baseline, peaked at 55) was structurally invisible to the new-sink\n'
    '# check: it was already >=5 at that one fixed snapshot, so it could\n'
    '# never cross into "new" no matter how much worse it got. Requires\n'
    '# BOTH a relative and an absolute growth threshold so a small sink\n'
    '# doubling (e.g. 2->4) doesn\'t trip it, but a large sink growing\n'
    '# substantially in both senses does.\n'
    'CHRONIC_SINK_GROWTH_PCT = 0.25    # halt if a baseline sink grows >=25% vs Round-0 baseline\n'
    'CHRONIC_SINK_GROWTH_DELTA = 8     # AND grows by >=8 captures vs Round-0 baseline\n'
    'SCALAR_FLOOR            = 0.10    # minimum displacement scalar\n',
)

# 2. chronic_sinks computation + its own OVERRIDE block, after the
#    existing new-sink override block.
edit(
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
    '        if overridden_sinks:\n'
    '            override_msg = (\n'
    '                f"[HARNESS] OVERRIDE: acknowledged sink(s) {overridden_sinks} "\n'
    '                f"excluded from escalation this round -- diagnosed clean this "\n'
    '                f"session, scoped to this run only via --acknowledge-sink, not "\n'
    '                f"a threshold change, not a permanent allowlist."\n'
    '            )\n'
    '            print(override_msg)\n'
    '            with open(LOG_PATH, "a", encoding="utf-8") as fh:\n'
    '                fh.write(f"\\n{override_msg}\\n")\n'
    '\n'
    '        # Chronic-sink check -- Gemini-approved hybrid threshold (this\n'
    '        # session): a state already significant at the fixed Round-0\n'
    '        # baseline (>=5 captures, the complement of the new-sink check\'s\n'
    '        # <5 condition) that has since grown by BOTH >=25% relative AND\n'
    '        # >=8 absolute captures. Added because invisible_performance_\n'
    '        # management (33 at baseline, peaked at 55 during reconvergence)\n'
    '        # was structurally invisible to significant_new_sinks -- already\n'
    '        # >=5 at that one fixed snapshot, so it could never cross into\n'
    '        # "new" no matter how much worse it got. Same fixed-baseline\n'
    '        # comparison as the new-sink check (not a rolling window), same\n'
    '        # ESCALATING severity, same acknowledged_sinks set --\n'
    '        # --acknowledge-sink applies to both checks identically.\n'
    '        raw_chronic_sinks = {}\n'
    '        for s, c in sink_counts.items():\n'
    '            base_c = baseline_sink_counts.get(s, 0)\n'
    '            if base_c < 5:\n'
    '                continue\n'
    '            growth = c - base_c\n'
    '            growth_pct = growth / base_c if base_c > 0 else 0.0\n'
    '            if growth_pct >= CHRONIC_SINK_GROWTH_PCT and growth >= CHRONIC_SINK_GROWTH_DELTA:\n'
    '                raw_chronic_sinks[s] = {\n'
    '                    "baseline": base_c, "current": c,\n'
    '                    "delta": growth, "pct": round(growth_pct, 4),\n'
    '                }\n'
    '        chronic_sinks = {\n'
    '            s: d for s, d in raw_chronic_sinks.items()\n'
    '            if s not in acknowledged_sinks\n'
    '        }\n'
    '        overridden_chronic_sinks = {\n'
    '            s: d for s, d in raw_chronic_sinks.items()\n'
    '            if s in acknowledged_sinks\n'
    '        }\n'
    '        if overridden_chronic_sinks:\n'
    '            override_chronic_msg = (\n'
    '                f"[HARNESS] OVERRIDE (chronic): acknowledged sink(s) "\n'
    '                f"{overridden_chronic_sinks} excluded from chronic-growth "\n'
    '                f"escalation this round -- diagnosed clean this session, "\n'
    '                f"scoped to this run only via --acknowledge-sink, not a "\n'
    '                f"threshold change, not a permanent allowlist."\n'
    '            )\n'
    '            print(override_chronic_msg)\n'
    '            with open(LOG_PATH, "a", encoding="utf-8") as fh:\n'
    '                fh.write(f"\\n{override_chronic_msg}\\n")\n',
)

# 3. Combined new-sink + chronic-sink status check. Confirmed via direct
#    read of the live file that this elif/else pair is the LAST branch
#    in the chain -- after rule_a_breach, rule_b_breach, RESOLVED,
#    IMPASSE, and regression cascade, immediately before the final
#    else. Kept in that real position rather than the "before RESOLVED/
#    IMPASSE" placement an earlier paraphrase assumed. Replaces the
#    elif/else with an if/else that collects both reasons instead of
#    letting one short-circuit the other -- pure addition for the
#    new-sink-only case: when chronic_sinks is empty, reasons contains
#    exactly the old single string, and "ESCALATING — " + reasons[0]
#    reproduces the old f-string byte for byte.
edit(
    '        elif significant_new_sinks:\n'
    '            status = f"ESCALATING — new sink emerged: {list(significant_new_sinks.keys())}"\n'
    '        else:\n'
    '            status = "CONTINUING"\n',
    '        else:\n'
    '            reasons = []\n'
    '            if significant_new_sinks:\n'
    '                reasons.append(f"new sink emerged: {list(significant_new_sinks.keys())}")\n'
    '            if chronic_sinks:\n'
    '                reasons.append(f"chronic sink worsening: {chronic_sinks}")\n'
    '            if reasons:\n'
    '                status = "ESCALATING — " + " | ".join(reasons)\n'
    '            else:\n'
    '                status = "CONTINUING"\n',
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
