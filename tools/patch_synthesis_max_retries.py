#!/usr/bin/env python
"""
PRV3 -- patch_synthesis_max_retries.py
Patches engine/output_synthesis.py -- fixes the synthesis-timeout root cause
confirmed Session 72: the Anthropic client is constructed with no max_retries
override, so the SDK default (DEFAULT_MAX_RETRIES=2, confirmed via direct
source inspection of installed anthropic 0.119.0) applies -- 1 initial
attempt + 2 retries. Each attempt gets its own full 5s timeout (the same
FinalRequestOptions object, carrying the per-call timeout=5.0 override, is
reused across every retry in the SDK's request loop), plus exponential
backoff between attempts (~0.5s, ~1.0s nominal before jitter). 3 x 5s + backoff
matches the observed Preview reproduction (~17.4-17.8s) almost exactly.

Does NOT change the 5s LOCKED timeout value itself (Session 42, Gemini Q4).
Fixes only how that locked value is honored.

REVISED per Pete's decision: max_retries=1 (not 0) -- keeps one retry as
resilience against a single transient blip on the first attempt, trading a
longer worst-case fallback time for that resilience. Worst case with
max_retries=1: 2 attempts (retries_taken=0,1 in the SDK's request loop) x
5.0s each + one backoff interval. Backoff for the sole retry uses
nb_retries=0 in _calculate_retry_timeout() (nb_retries = max_retries -
remaining_retries = 1 - 1 = 0), so sleep_seconds = INITIAL_RETRY_DELAY
(0.5) * 2**0 = 0.5, jittered by 0.75-1.0x -> ~0.375-0.5s. Total: ~10.4-10.5s,
confirmed against SDK source, not just assumed from the max_retries=0 math.

Change:
  engine/output_synthesis.py -- Anthropic client instantiation
  Before: client = _anthropic.Anthropic()
  After:  client = _anthropic.Anthropic(max_retries=1)

Usage:
  python tools/patch_synthesis_max_retries.py --dry-run
  python tools/patch_synthesis_max_retries.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "output_synthesis.py"

OLD = '''    if client is None:
        client = _anthropic.Anthropic()'''

NEW = '''    if client is None:
        # max_retries=1: the 5s timeout (LOCKED, Session 42) is a per-attempt
        # budget in the SDK's request loop, not a total budget -- left at the
        # SDK default (2 retries) it silently becomes a ~15s+ giveaway. One
        # retry is kept deliberately (not 0) for resilience against a single
        # transient blip; worst case is now ~10.5s, not ~17s.
        client = _anthropic.Anthropic(max_retries=1)'''

CHANGES = [("Anthropic client: max_retries=1", OLD, NEW)]


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
            found = old in text
            status = "OK  " if found else "MISS"
            if not found:
                all_ok = False
            print(f"  [{status}] {label}")
        if not all_ok:
            print("\n  ERROR: one or more OLD strings not found in target.")
            sys.exit(1)
        print("\n  Summary of changes:")
        print("    Anthropic client instantiation: max_retries=1 added")
        print("    5s LOCKED timeout value: UNCHANGED")
        print("    No other retry/timeout config touched")
        return

    for label, old, new in CHANGES:
        if old not in text:
            print(f"ERROR: OLD string not found for '{label}' -- aborting.")
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
    print("  Anthropic client: max_retries=1")


if __name__ == "__main__":
    main()
