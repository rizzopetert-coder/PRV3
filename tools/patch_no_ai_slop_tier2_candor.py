"""
PRV3 -- apply the Tier 2 no-ai-slop fix for
candor-as-an-organizational-variable.md (28 -> 7 em-dashes, plus a real
citation-accuracy correction, not just a missing-name weasel fix).

Delivered via Downloads, confirmed clean before this script was written:
zero mojibake, em-dash count exactly 7 as claimed.

Content verification performed independently before applying, not taken
on the fix description's word:
- Confirmed via WebSearch that the 65,672-employee/14.9%-turnover study,
  the 530-work-unit/12.5%-productivity study, and the 469-business-unit/
  8.9%-profitability study are three genuinely SEPARATE Gallup studies
  with different sample sets -- the live (pre-fix) text incorrectly
  attributed all three to "the same research." Real factual overstatement
  corrected, not just a missing citation name.
- Confirmed "How Fast Feedback Fuels Performance" is a real, named Gallup
  report matching the 3.6x daily-feedback-motivation figure the piece
  cites.
- Project Aristotle's 180-teams/250-variables figures were already
  accurate (matches the existing, already-verified HC-007 book-citations.ts
  entry) -- untouched by this fix beyond an em-dash trim, confirmed via
  diff.

No book-citations.ts changes -- this piece attributes sources in prose
(naming Gallup/Google directly), not via the ID-based citation system
used elsewhere in the corpus; nothing in the fix introduces a new
citation-ID need.

Usage:
  python tools/patch_no_ai_slop_tier2_candor.py --dry-run
  python tools/patch_no_ai_slop_tier2_candor.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\candor-as-an-organizational-variable.md")
LIVE = REPO_ROOT / "web/content/book/methodology/candor-as-an-organizational-variable.md"


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
