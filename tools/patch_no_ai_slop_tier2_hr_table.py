"""
PRV3 -- apply the Tier 2 no-ai-slop fix for hr-is-the-table.md
(21 -> 8 em-dashes).

Delivered via Downloads, confirmed clean before this script was written:
zero mojibake, em-dash count exactly 8 as claimed.

Load-bearing anchor claim (Tracy Keogh, CHRO at HP, "HR is the table"
quote, referenced on The Talent War Podcast) independently verified via
WebSearch before applying, even though it wasn't flagged by the
mechanical scan's weasel-attribution pattern -- a named person/title/
podcast claim this central to the piece is worth checking regardless of
what the automated pattern catches. Confirmed: Tracy Keogh genuinely was
CHRO at HP, the quote is documented and associated with her, referenced
on The Talent War Podcast (hosted by George Randle and Tom Lokar). Diff
confirms this section received only an em-dash trim, no content change.

All other diff lines confirmed pure em-dash-to-comma/colon punctuation
conversions, no wording changes.

Usage:
  python tools/patch_no_ai_slop_tier2_hr_table.py --dry-run
  python tools/patch_no_ai_slop_tier2_hr_table.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\hr-is-the-table.md")
LIVE = REPO_ROOT / "web/content/book/memo/hr-is-the-table.md"


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
