"""
PRV3 -- apply the Tier 3 no-ai-slop fix for succession-planning.md
(prose em-dash count 11 -> 8; raw, including the exempt
"— Principal Resolution" line: 12 -> 9).

The chat-pasted version of this file (attached in-conversation) again
showed the recurring mojibake artifact, including inside the signature
line, and was not trusted or used. Confirmed instead against the actual
file delivered separately to Downloads
(C:\\Users\\rizzo\\Downloads\\succession-planning.md, landed 2026-08-17
22:00): zero mojibake, raw em-dash count exactly 9 as claimed. Diffed
line-by-line against live (--strip-trailing-cr): exactly 2 changes, one
paired-dash aside converted to commas and one single dash converted to a
colon -- the other 4 paired-dash asides in the file are left intact, no
wording or content changes anywhere. No named claims in this file
requiring citation verification. Signature line untouched.

Usage:
  python tools/patch_no_ai_slop_tier3_succession_planning.py --dry-run
  python tools/patch_no_ai_slop_tier3_succession_planning.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\succession-planning.md")
LIVE = REPO_ROOT / "web/content/book/methodology/succession-planning.md"


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
