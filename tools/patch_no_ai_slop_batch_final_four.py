"""
PRV3 -- apply the em-dash-cap fix for the final four files in the open
queue:

  dueling-narratives.md              10 -> 8
  narrative-lock.md                  10 -> 8
  crisis-as-catalyst-for-clarity.md   9 -> 8
  the-unformed-leader.md              9 -> 8

None use the "— Principal Resolution" signature closer, so no exemption
math applies -- raw counts are genuine prose counts.

The chat-pasted versions of all four files (attached in-conversation)
showed the recurring mojibake artifact and were not trusted or used.
Confirmed instead against the actual files delivered separately to
Downloads as a zip (C:\\Users\\rizzo\\Downloads\\files113\\, extracted
2026-08-17 22:55): zero mojibake in any of the four, em-dash count
exactly 8 in each, as claimed.

Diffed line-by-line against live for all four (--strip-trailing-cr):
crisis-as-catalyst-for-clarity.md (1 change), dueling-narratives.md
(2 changes), narrative-lock.md (2 changes), and the-unformed-leader.md
(1 change) are each pure punctuation conversions (em-dash to colon or
comma), no wording or content changes anywhere. No named claims in any
of the four requiring citation verification.

This closes out the entire em-dash-over-cap queue -- Tier 1 through
Tier 4 plus this worst-first continuation -- with zero files remaining
above the locked ≤8 standard.

Usage:
  python tools/patch_no_ai_slop_batch_final_four.py --dry-run
  python tools/patch_no_ai_slop_batch_final_four.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(r"C:\Users\rizzo\Downloads\files113")

FILES = [
    ("crisis-as-catalyst-for-clarity.md", REPO_ROOT / "web/content/book/methodology/crisis-as-catalyst-for-clarity.md"),
    ("dueling-narratives.md", REPO_ROOT / "web/content/book/methodology/dueling-narratives.md"),
    ("narrative-lock.md", REPO_ROOT / "web/content/book/methodology/narrative-lock.md"),
    ("the-unformed-leader.md", REPO_ROOT / "web/content/book/methodology/the-unformed-leader.md"),
]


def apply(dry_run: bool) -> int:
    contents = {}
    for name, live_path in FILES:
        src_path = SRC_DIR / name
        if not src_path.exists():
            print(f"ABORT: {src_path} not found")
            return 1
        if not live_path.exists():
            print(f"ABORT: {live_path} not found")
            return 1
        new_content = src_path.read_text(encoding="utf-8")
        if "â" in new_content:
            print(f"ABORT: {src_path} still contains mojibake artifact -- not applying")
            return 1
        contents[name] = (live_path, new_content)

    for name, (live_path, new_content) in contents.items():
        old_content = live_path.read_text(encoding="utf-8")
        if dry_run:
            print(f"OK (dry-run): {live_path} -- {len(old_content)} bytes -> {len(new_content)} bytes")
        else:
            live_path.write_text(new_content, encoding="utf-8")
            print(f"WRITTEN: {live_path}")

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
