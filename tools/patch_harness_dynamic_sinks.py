"""
PRV3 MC_CENTROID_39 recalibration -- Phase 1, item 4: replace the static
V23_SINKS set with a live sink-count baseline captured at harness
startup, and fix the dependent significant_new_sinks bug.

Pete's direction (tools/_mob.txt precedent, S17-S29 campaign): sink
identification always ran empirically per-round, never as a maintained
static list -- the dominant sink changed on nearly every session of that
campaign (paper_shield -> the_unexamined_algorithm -> the_uninitiated ->
leadership_deafness -> built_to_fail/the_undefined_role). V23_SINKS was a
one-time S27 snapshot, not durable ground truth. Today's finding (3 of 4
dead, invisible_performance_management at 46 captures undetected) is the
same staleness pattern recurring, not new.

Design:
  1. Remove the static V23_SINKS constant.
  2. Add an explicit startup step (after the baseline test-suite check,
     before the round loop) that runs run_calibration_pass() once against
     the freshly-applied initial scalars/window, and captures its
     sink_counts as baseline_sink_counts -- a real empirical snapshot of
     "what's already a sink before any tuning happens," recomputed every
     time the harness runs, never hand-maintained.
  3. significant_new_sinks now compares CURRENT round's sink_counts
     against that captured baseline, not a hardcoded set:
       significant_new_sinks = {s: c for s, c in sink_counts.items()
                                 if c >= 5 and baseline_sink_counts.get(s, 0) < 5}
     A state counts as a genuinely new/escalating sink only if it's
     significant NOW (>=5 captures, unchanged threshold) and was NOT
     already significant at startup (<5 captures at baseline) -- this
     catches sinks the tuning loop itself creates or worsens across
     rounds, without re-flagging chronic sinks (e.g. built_to_fail) that
     were already present before this run started.
  4. This also fixes the dependent bug: the old `s not in hc_passing`
     gate was structurally unreachable once hc_passing reached 57/57 (no
     sink could ever be "new" regardless of severity, since every state
     passes HC). The baseline comparison replaces that gate entirely and
     doesn't depend on hc_passing membership at all -- it will mean
     something again once Phase 2 introduces new signal that can create
     fresh failures.

Costs one extra 172-profile suite run at startup (baseline capture,
separate from round 1's own optimization-loop pass) -- a deliberate,
explicit step, not reused from round 1, so round 1 itself is also
checked against a real baseline rather than being vacuously exempt.

Usage:
  python tools/patch_harness_dynamic_sinks.py --dry-run
  python tools/patch_harness_dynamic_sinks.py --write
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


# 1. Remove the static V23_SINKS constant
edit(
    '# Known v23 sinks — new sinks outside this set trigger escalation\n'
    'V23_SINKS = {"built_to_fail", "leadership_deafness", "the_fracture", "the_diversity_ceiling"}\n'
    '\n'
    '# Test scripts to run after each parameter change (pytest not installed)',
    '# Sink baseline is no longer a static set -- captured dynamically at\n'
    '# harness startup (see baseline_sink_counts in main()). Precedent\n'
    '# (tools/_mob.txt, S17-S29 campaign): the dominant sink changed almost\n'
    '# every session historically; a hand-maintained list goes stale fast\n'
    '# (confirmed this session: 3 of the 4 V23_SINKS entries were no longer\n'
    '# real sinks, while a 46-capture sink existed undetected outside the set).\n'
    '\n'
    '# Test scripts to run after each parameter change (pytest not installed)',
)

# 2. Startup baseline capture, inserted after the baseline test-suite check
edit(
    '    print(f"[HARNESS] Test suite: OK\\n")\n'
    '\n'
    '    # Log initial state\n'
    '    with open(LOG_PATH, "a", encoding="utf-8") as fh:\n'
    '        fh.write(f"Starting scalars (source={scalar_source}):\\n")\n'
    '        for f, v in scalars.items():\n'
    '            fh.write(f"  {f}: {v:.4f}\\n")\n'
    '        fh.write(f"Starting window: {window}\\n\\n")\n',
    '    print(f"[HARNESS] Test suite: OK\\n")\n'
    '\n'
    '    # ── Baseline sink-count capture (dynamic, replaces V23_SINKS) ────────────\n'
    '    # Real empirical snapshot against the freshly-applied initial\n'
    '    # scalars/window, taken fresh every harness run rather than hand-\n'
    '    # maintained -- see module-level comment above for why a static set\n'
    '    # goes stale. Used as the reference point for significant_new_sinks\n'
    '    # in every round of the loop below.\n'
    '    print("\\n[HARNESS] Baseline sink-count capture...")\n'
    '    baseline_cal = run_calibration_pass()\n'
    '    if baseline_cal is None:\n'
    '        print("[HARNESS] ESCALATE: Baseline calibration pass returned no parseable output. Stop.")\n'
    '        return\n'
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
)

# 3+4. significant_new_sinks: baseline-relative, not V23_SINKS/hc_passing-gated
edit(
    '        # Sink emergence check (exclude v23 known sinks and currently-passing states)\n'
    '        significant_new_sinks = {\n'
    '            s: c for s, c in sink_counts.items()\n'
    '            if s not in V23_SINKS and c >= 5 and s not in hc_passing\n'
    '        }\n',
    '        # Sink emergence check -- dynamic baseline (captured at harness\n'
    '        # startup), not a static hardcoded set or hc_passing membership\n'
    '        # (the latter was structurally unreachable once hc_passing hit\n'
    '        # 57/57 -- no sink could ever be "new" regardless of severity).\n'
    '        # A state counts as a genuinely new/escalating sink only if it is\n'
    '        # significant NOW (>=5 captures) and was NOT already significant\n'
    '        # at startup (<5 captures at baseline) -- catches sinks the tuning\n'
    '        # loop itself creates or worsens, without re-flagging chronic\n'
    '        # sinks that predate this run.\n'
    '        significant_new_sinks = {\n'
    '            s: c for s, c in sink_counts.items()\n'
    '            if c >= 5 and baseline_sink_counts.get(s, 0) < 5\n'
    '        }\n',
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
