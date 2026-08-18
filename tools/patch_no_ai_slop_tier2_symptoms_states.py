"""
PRV3 -- apply the Tier 2 no-ai-slop fix for
symptoms-states-and-why-the-distinction-matters.md (20 -> 8 em-dashes).

The chat-pasted version of this file (attached in-conversation) again
showed the recurring mojibake artifact and was not trusted or used.
Confirmed instead against the actual file delivered separately to
Downloads
(C:\\Users\\rizzo\\Downloads\\symptoms-states-and-why-the-distinction-matters.md,
landed 2026-08-17 21:21): zero mojibake, em-dash count exactly 8 as
claimed. Raw diff against live initially looked like a full rewrite --
the live file is CRLF, the Downloads file is LF -- re-diffed with
--strip-trailing-cr, which confirmed every real content change is a pure
punctuation conversion (em-dash to colon or comma), no wording changes.

NOT fixed here, deliberately: the piece states "Principal Resolution has
identified fifty-seven institutional states." CLAUDE.md's locked engine
state count is 58 (the_inner_circle added as the 58th state). This looks
like a stale pre-addition figure but is explicitly held for Pete's call,
not corrected as part of this em-dash cleanup pass -- confirmed the
Downloads source leaves "fifty-seven" untouched, so this script does not
touch it either.

Usage:
  python tools/patch_no_ai_slop_tier2_symptoms_states.py --dry-run
  python tools/patch_no_ai_slop_tier2_symptoms_states.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\symptoms-states-and-why-the-distinction-matters.md")
LIVE = REPO_ROOT / "web/content/book/methodology/symptoms-states-and-why-the-distinction-matters.md"


def apply(dry_run: bool) -> int:
    if not SRC.exists():
        print(f"ABORT: {SRC} not found")
        return 1
    if not LIVE.exists():
        print(f"ABORT: {LIVE} not found")
        return 1
    new_content = SRC.read_text(encoding="utf-8")
    if "â" in new_content:
        print("ABORT: source still contains mojibake artifact -- not applying")
        return 1
    old_content = LIVE.read_text(encoding="utf-8")
    if dry_run:
        print(f"OK (dry-run): {LIVE} -- {len(old_content)} bytes -> {len(new_content)} bytes")
    else:
        LIVE.write_text(new_content, encoding="utf-8")
        print(f"WRITTEN: {LIVE}")

    if dry_run:
        print("\nDry run complete. Re-run with --write to apply.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
