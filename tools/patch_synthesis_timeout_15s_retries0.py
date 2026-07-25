#!/usr/bin/env python
"""
PRV3 -- patch_synthesis_timeout_15s_retries0.py
Re-sets the synthesis timeout LOCKED value: 5.0s -> 15.0s, max_retries: 1 -> 0.

Lineage, for the record:
  Session 42  -- 5s timeout LOCKED (Gemini Q4).
  Session 72  -- max_retries=1 fix (commit 72a97b9): the 5s timeout was a
                 per-attempt budget, not total -- SDK default (2 retries)
                 silently made it ~17s. Fixed to max_retries=1, ~10.5s
                 worst case, keeping one retry for blip-resilience.
  This session -- Production investigation found the 5s value itself was
                 the deeper problem: 6/6 real successful Production calls
                 measured 7.4-13.6s (avg ~9.8s) -- every one would have
                 been killed by either the old 5s value or Session 72's
                 max_retries=1 fix on top of it. Gemini reviewed reopening
                 the Session 42 lock; confirmed the evidence justified it,
                 though Gemini's supporting Vercel-platform-limits argument
                 used outdated figures. Independently verified: this
                 project is Hobby + Fluid compute, 300s function-duration
                 ceiling (default and max) -- no platform collision risk
                 at any reasonable value. vercel.json carries no
                 maxDuration override (confirmed via direct repo read).

Pete's final numbers: timeout=15.0s (comfortable margin above the observed
13.6s max), max_retries=0 (deliberately superseding Session 72's
max_retries=1 -- at a 15s timeout, one retry means a ~30-40s worst-case
wait, unacceptable UX regardless of the platform ceiling being moot).

This SUPERSEDES commit 72a97b9, not a revert of that work -- that fix
was correct given the 5s value it operated against; this session changes
the value itself, which changes which retry trade-off makes sense.

Changes, engine/output_synthesis.py:
  - synthesize(): timeout default 5.0 -> 15.0
  - synthesize(): docstring timeout line updated (new LOCKED value + why)
  - synthesize(): client instantiation comment + max_retries 1 -> 0
  - OutputSynthesisEngine.synthesize(): timeout default 5.0 -> 15.0

Usage:
  python tools/patch_synthesis_timeout_15s_retries0.py --dry-run
  python tools/patch_synthesis_timeout_15s_retries0.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "output_synthesis.py"

CHANGES = []


def edit(label, old, new):
    CHANGES.append((label, old, new))


# ── 1. module-level synthesize(): timeout default ──────────────────────────────
edit(
    "synthesize(): timeout default 5.0 -> 15.0",
    '''    model: str = "claude-sonnet-4-6",
    client=None,
    timeout: float = 5.0,
) -> SynthesisResult:''',
    '''    model: str = "claude-sonnet-4-6",
    client=None,
    timeout: float = 15.0,
) -> SynthesisResult:''',
)

# ── 2. docstring: timeout line ──────────────────────────────────────────────────
edit(
    "synthesize(): docstring timeout line updated",
    '''      timeout:            max seconds to wait (5s LOCKED, Gemini Q4, S42)''',
    '''      timeout:            max seconds to wait (15.0s LOCKED, re-set this
                           session -- Gemini-reviewed, Pete-approved,
                           grounded in real Production latency data (6/6
                           samples, 7.4-13.6s, avg ~9.8s). Supersedes the
                           original 5s LOCKED value (Gemini Q4, S42).''',
)

# ── 3. client instantiation: max_retries 1 -> 0, comment rewritten ─────────────
edit(
    "client instantiation: max_retries=0, comment rewritten",
    '''    if client is None:
        # max_retries=1: the 5s timeout (LOCKED, Session 42) is a per-attempt
        # budget in the SDK's request loop, not a total budget -- left at the
        # SDK default (2 retries) it silently becomes a ~15s+ giveaway. One
        # retry is kept deliberately (not 0) for resilience against a single
        # transient blip; worst case is now ~10.5s, not ~17s.
        client = _anthropic.Anthropic(max_retries=1)''',
    '''    if client is None:
        # max_retries=0: timeout raised to 15.0s LOCKED (this session,
        # Gemini-reviewed, Pete-approved) on real Production latency data
        # (6/6 samples, 7.4-13.6s). Session 72's max_retries=1 traded a
        # longer worst case for resilience against a transient blip -- at
        # 15s that trade no longer holds: one retry means a ~30-40s worst
        # case, unacceptable UX regardless of Vercel's platform ceiling
        # (confirmed 300s, Hobby + Fluid compute -- no collision risk).
        # Fail fast at 15s instead.
        client = _anthropic.Anthropic(max_retries=0)''',
)

# ── 4. OutputSynthesisEngine.synthesize(): timeout default ─────────────────────
edit(
    "OutputSynthesisEngine.synthesize(): timeout default 5.0 -> 15.0",
    '''        signal_map_context: str = "",
        timeout: float = 5.0,
    ) -> SynthesisResult:
        """Run synthesis and store result for downstream access."""''',
    '''        signal_map_context: str = "",
        timeout: float = 15.0,
    ) -> SynthesisResult:
        """Run synthesis and store result for downstream access."""''',
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    if not TARGET.exists():
        print(f"ERROR: target not found: {TARGET}")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8")

    if args.dry_run:
        print(f"DRY RUN -- target: {TARGET}")
        print(f"  {len(CHANGES)} change(s) to apply:")
        all_ok = True
        for label, old, new in CHANGES:
            count = text.count(old)
            status = f"OK ({count}x)" if count == 1 else ("MISS" if count == 0 else f"AMBIGUOUS ({count}x)")
            if count != 1:
                all_ok = False
            print(f"  [{status}] {label}")
        if not all_ok:
            print("\n  ERROR: one or more OLD strings not found exactly once in target.")
            sys.exit(1)
        print("\n  All anchors matched exactly once. Ready for --write.")
        return

    for label, old, new in CHANGES:
        count = text.count(old)
        if count != 1:
            print(f"ERROR: OLD string for '{label}' matched {count} times (expected 1) -- aborting.")
            sys.exit(1)

    new_text = text
    for label, old, new in CHANGES:
        new_text = new_text.replace(old, new, 1)

    if new_text == text:
        print("ERROR: no changes produced.")
        sys.exit(1)

    TARGET.write_text(new_text, encoding="utf-8")
    print(f"WRITTEN: {TARGET}")
    print(f"  {len(CHANGES)} change(s) applied")


if __name__ == "__main__":
    main()
