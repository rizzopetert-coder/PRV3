"""
PRV3 -- apply the Tier 2 no-ai-slop fix for
earned-effectiveness-conversation-framework.md (19 -> 8 em-dashes).

The chat-pasted version of this file (attached in-conversation) again
showed the recurring mojibake artifact and was not trusted or used.
Confirmed instead against the actual file delivered separately to
Downloads
(C:\\Users\\rizzo\\Downloads\\earned-effectiveness-conversation-framework.md,
landed 2026-08-17 21:28): zero mojibake, em-dash count exactly 8 as
claimed.

Diffed line-by-line against live (--strip-trailing-cr, live is CRLF,
source is LF): almost every change is a pure punctuation conversion
(em-dash to colon or comma). One change is NOT pure punctuation and was
caught before applying, not silently accepted: the section heading
"Why the sequence gets shortcut -- and what it costs" (sentence case,
matching the file's other three headings) became "Why the Sequence Gets
Shortcut: What It Costs" (title case) -- flagged to Pete, who confirmed
apply-as-delivered.

Usage:
  python tools/patch_no_ai_slop_tier2_earned_conv_framework.py --dry-run
  python tools/patch_no_ai_slop_tier2_earned_conv_framework.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\earned-effectiveness-conversation-framework.md")
LIVE = REPO_ROOT / "web/content/book/methodology/earned-effectiveness-conversation-framework.md"


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
