"""
PRV3 -- apply the em-dash-cap fix for three files, worst-first continuation
of the open queue:

  the-overloaded-manager.md  13 -> 8
  the-paper-tiger.md         13 -> 8
  velocity-of-truth.md       12 -> 8

None use the "— Principal Resolution" signature closer, so no exemption
math applies -- raw counts are genuine prose counts.

The chat-pasted versions of all three files (attached in-conversation)
showed the recurring mojibake artifact and were not trusted or used.
Confirmed instead against the actual files delivered separately to
Downloads as a zip (C:\\Users\\rizzo\\Downloads\\files111\\, extracted
2026-08-17 22:40): zero mojibake in any of the three, em-dash count
exactly 8 in each, as claimed.

Diffed line-by-line against live for all three (--strip-trailing-cr):
the-overloaded-manager.md (5 changes), the-paper-tiger.md (5 changes),
and velocity-of-truth.md (4 changes) are each pure punctuation
conversions (em-dash to colon or comma), no wording or content changes
anywhere. No named claims in any of the three requiring citation
verification.

Usage:
  python tools/patch_no_ai_slop_batch_overloaded_papertiger_velocity.py --dry-run
  python tools/patch_no_ai_slop_batch_overloaded_papertiger_velocity.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(r"C:\Users\rizzo\Downloads\files111")

FILES = [
    ("the-overloaded-manager.md", REPO_ROOT / "web/content/book/methodology/the-overloaded-manager.md"),
    ("the-paper-tiger.md", REPO_ROOT / "web/content/book/methodology/the-paper-tiger.md"),
    ("velocity-of-truth.md", REPO_ROOT / "web/content/book/memo/velocity-of-truth.md"),
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
