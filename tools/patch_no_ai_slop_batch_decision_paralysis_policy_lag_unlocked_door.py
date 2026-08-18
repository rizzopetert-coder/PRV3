"""
PRV3 -- apply the em-dash-cap fix for three files, worst-first from the
open Tier 4+ queue:

  the-policy-lag.md      15 -> 8
  the-unlocked-door.md   15 -> 8
  decision-paralysis.md  14 -> 8

None use the "— Principal Resolution" signature closer, so no exemption
math applies -- raw counts are genuine prose counts.

The chat-pasted versions of all three files (attached in-conversation)
showed the recurring mojibake artifact and were not trusted or used.
Confirmed instead against the actual files delivered separately to
Downloads as a zip (C:\\Users\\rizzo\\Downloads\\files00\\, extracted
2026-08-17 22:23): zero mojibake in any of the three, em-dash count
exactly 8 in each, as claimed.

Diffed line-by-line against live for all three (--strip-trailing-cr):
decision-paralysis.md (6 changes), the-policy-lag.md (7 changes), and
the-unlocked-door.md (7 changes) are each pure punctuation conversions
(em-dash to colon or comma), no wording or content changes anywhere.
Remaining paired-dash asides in each file were left intact where not
needed to hit the cap. No named claims in any of the three requiring
citation verification.

Usage:
  python tools/patch_no_ai_slop_batch_decision_paralysis_policy_lag_unlocked_door.py --dry-run
  python tools/patch_no_ai_slop_batch_decision_paralysis_policy_lag_unlocked_door.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(r"C:\Users\rizzo\Downloads\files00")

FILES = [
    ("decision-paralysis.md", REPO_ROOT / "web/content/book/methodology/decision-paralysis.md"),
    ("the-policy-lag.md", REPO_ROOT / "web/content/book/methodology/the-policy-lag.md"),
    ("the-unlocked-door.md", REPO_ROOT / "web/content/book/methodology/the-unlocked-door.md"),
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
