"""
PRV3 -- apply the Tier 2 no-ai-slop fix for
what-their-resistance-is-actually-telling-you.md (21 -> 8 em-dashes).

The chat-pasted version of this file (attached in-conversation) contained
the recurring mojibake artifact -- stray "â" characters replacing real
em-dashes -- so that copy was not trusted or used. Confirmed instead
against the actual file delivered separately to Downloads
(C:\\Users\\rizzo\\Downloads\\what-their-resistance-is-actually-telling-you.md,
landed 2026-08-17 21:03): zero mojibake, em-dash count exactly 8 as
claimed. Diffed line-by-line against live -- every change is a pure
punctuation conversion (em-dash to comma or colon), no wording or content
changes anywhere. No weasel-attribution claims in this file, nothing to
independently fact-check.

Usage:
  python tools/patch_no_ai_slop_tier2_resistance.py --dry-run
  python tools/patch_no_ai_slop_tier2_resistance.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\what-their-resistance-is-actually-telling-you.md")
LIVE = REPO_ROOT / "web/content/book/methodology/what-their-resistance-is-actually-telling-you.md"


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
