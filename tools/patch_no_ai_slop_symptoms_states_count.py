"""
PRV3 -- apply the "fifty-seven" -> "fifty-eight" institutional-states
correction to symptoms-states-and-why-the-distinction-matters.md.

This supersedes the em-dash fix already live (commit 73c577e). The
chat-pasted version of this file again showed the recurring mojibake
artifact and was not trusted or used. Confirmed instead against the
actual file delivered separately to Downloads
(C:\\Users\\rizzo\\Downloads\\symptoms-states-and-why-the-distinction-matters.md,
landed 2026-08-17 21:38): zero mojibake, em-dash count unchanged at 8.

Diffed against the currently-live file: the only change is the single
"fifty-seven" -> "fifty-eight" swap, confirmed against the live MOB
(tools/_mob.txt, the_inner_circle taxonomy expansion row, locked count
58) in the prior session turn. No other content touched.

Usage:
  python tools/patch_no_ai_slop_symptoms_states_count.py --dry-run
  python tools/patch_no_ai_slop_symptoms_states_count.py --write
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
