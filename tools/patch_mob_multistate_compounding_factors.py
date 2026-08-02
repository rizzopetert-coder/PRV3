"""
PRV3 -- Append brainstormed compounding factors to the existing
"Multi-state compounding mechanism for Friction Tax" Decision Register
row (tools/_mob.txt Section 13a). Appends within that row's own detail
column -- does NOT create a new row, does not touch any other row.

Documentation-only, no version bump.

Usage:
  python tools/patch_mob_multistate_compounding_factors.py --dry-run
  python tools/patch_mob_multistate_compounding_factors.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

ANCHOR = (
    "if states should compound urgency as well as dollar cost, that may "
    "be the same design conversation, not two separate ones | This "
    "session (Claude Code) -- flagged, not fixed | Pete's call -- hold "
    "until Set 3 scoring is fully closed. Do not start design or Gemini "
    "handoff until Pete reopens this explicitly |\n"
)

REPLACEMENT = (
    "if states should compound urgency as well as dollar cost, that may "
    "be the same design conversation, not two separate ones. "
    "**Brainstormed factors (Pete, not yet designed or decided -- "
    "captured to avoid losing them before this gets scoped):** "
    "Factor A -- within-criterion compounding: if multiple identified "
    "states all score high on the SAME criterion (e.g. several states "
    "each carrying significant Legal/Compliance exposure), that "
    "criterion's contribution to the tax should stack across those "
    "states rather than simply average out against the other, lower-"
    "scoring criteria. Factor B -- breadth-across-criteria compounding: "
    "an org whose identified states collectively \"hit\" more of the 4 "
    "criteria (turnover, productivity, decision-quality, legal) should "
    "see a higher multiplier than one where severity concentrates in "
    "just 1-2 criteria, even at similar raw totals -- proposed shape: a "
    "graduated multiplier keyed to how many of the 4 criteria are met "
    "across the org's identified states (1 criterion met vs. 2 vs. 3 vs. "
    "4), with the possibility that the multiplier also scales with how "
    "high the scores are within those met criteria, not just a binary "
    "met/not-met count. Both factors are additive to, not a replacement "
    "for, the original entry's state-count compounding question -- this "
    "is now three related-but-distinct compounding questions to resolve "
    "together when this item is reopened: (1) how multiple states "
    "combine, (2) within-criterion stacking, (3) breadth-across-criteria "
    "stacking | This session (Claude Code) -- flagged, not fixed | "
    "Pete's call -- hold until Set 3 scoring is fully closed. Do not "
    "start design or Gemini handoff until Pete reopens this explicitly "
    "|\n"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = MOB_FILE.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count == 0:
        print("ABORT -- anchor not found", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches)", file=sys.stderr)
        sys.exit(1)

    print("Appending to the existing 'Multi-state compounding mechanism")
    print("for Friction Tax' row (Section 13a) -- no new row created:")
    print("=" * 72)
    print("- " + ANCHOR.rstrip("\n"))
    print()
    print("+ " + REPLACEMENT.rstrip("\n"))
    print("=" * 72)
    print("No version bump -- appending detail to an existing open item.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    new_text = text.replace(ANCHOR, REPLACEMENT)
    MOB_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {MOB_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
