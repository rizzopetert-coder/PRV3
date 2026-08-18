"""
PRV3 -- apply the Tier 4 no-ai-slop fix for intellectual-bottleneck.md
(10 -> 8 em-dashes).

The chat-pasted version of this file (attached in-conversation) again
showed the recurring mojibake artifact and was not trusted or used.
Confirmed instead against the actual file delivered separately to
Downloads (C:\\Users\\rizzo\\Downloads\\intellectual-bottleneck.md,
landed 2026-08-17 22:14): zero mojibake, em-dash count exactly 8 as
claimed.

Location check done before touching anything: this repo has exactly one
copy of this file, at web/content/book/memo/intellectual-bottleneck.md,
confirmed present and published in book-manifest.ts (LIB-049). A concern
was raised about a possible stale PRV2 path
(src/content/library/memo/...) not migrating into the live corpus -- that
path does not exist anywhere in this repo, so there is no location
ambiguity; this is the correct, only, live file.

Citation check: the Keltner/power-cognition claim already matches the
corrected HC-103 wording ("the brain gets worse at reading social
feedback the longer someone holds power") -- no citation fix needed,
confirmed present in both the live file and the Downloads copy
unchanged.

Diffed line-by-line against live (--strip-trailing-cr): exactly 2
changes, both pure em-dash-to-comma conversions, no wording or content
changes anywhere.

Usage:
  python tools/patch_no_ai_slop_tier4_intellectual_bottleneck.py --dry-run
  python tools/patch_no_ai_slop_tier4_intellectual_bottleneck.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\intellectual-bottleneck.md")
LIVE = REPO_ROOT / "web/content/book/memo/intellectual-bottleneck.md"


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
