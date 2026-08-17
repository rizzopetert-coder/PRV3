"""
PRV3 -- apply the Tier 2 no-ai-slop fix for
psychological-safety-walked-into-a-meeting.md (24 -> 8 em-dashes, plus
the file's one weasel-attribution hit resolved).

Delivered via Downloads, confirmed clean before this script was written:
zero mojibake, em-dash count exactly 8 as claimed.

Weasel-attribution fix independently verified before applying: the live
text's "The research on this is fairly consistent: psychological safety
is built through demonstrated response, not declared intent" is replaced
with an attribution to Edmondson's own follow-up work (The Fearless
Organization, 2019) naming the three specific leader behaviors --
setting the stage, inviting participation, responding productively.
Confirmed via WebSearch: Edmondson's book does name exactly these three
behaviors, and Edmondson is already the piece's established named
authority (cited correctly earlier in the same file for the original
psychological-safety definition) -- this is a correct-attribution fix,
not a new, unverified source.

All other diff lines are pure em-dash-to-comma/colon punctuation
conversions -- confirmed via direct diff, no other wording changed.

Usage:
  python tools/patch_no_ai_slop_tier2_psych_safety.py --dry-run
  python tools/patch_no_ai_slop_tier2_psych_safety.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\psychological-safety-walked-into-a-meeting.md")
LIVE = REPO_ROOT / "web/content/book/memo/psychological-safety-walked-into-a-meeting.md"


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
