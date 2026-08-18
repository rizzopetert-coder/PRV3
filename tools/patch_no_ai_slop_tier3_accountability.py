"""
PRV3 -- apply the Tier 3 no-ai-slop fix for accountability.md
(prose em-dash count 12 -> 8; raw, including the exempt
"— Principal Resolution" line: 13 -> 9).

This is the sixth and final over-cap file in the Tier 3 signature-closer
group (the prior fix for no-margin-for-error.md incorrectly claimed the
group was complete at 5 files -- this one closes it out for real).

The chat-pasted version of this file (attached in-conversation) again
showed the recurring mojibake artifact, including inside the signature
line, and was not trusted or used. Confirmed instead against the actual
file delivered separately to Downloads
(C:\\Users\\rizzo\\Downloads\\accountability.md, landed 2026-08-17
22:09): zero mojibake, raw em-dash count exactly 9 as claimed. Diffed
line-by-line against live (--strip-trailing-cr): exactly 4 changes, all
pure punctuation conversions (em-dash to colon or comma), no wording or
content changes anywhere. No named claims in this file requiring
citation verification. Signature line untouched.

Usage:
  python tools/patch_no_ai_slop_tier3_accountability.py --dry-run
  python tools/patch_no_ai_slop_tier3_accountability.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\accountability.md")
LIVE = REPO_ROOT / "web/content/book/methodology/accountability.md"


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
