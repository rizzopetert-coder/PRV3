"""
PRV3 -- /book Content Architecture Phase 2, Step 2 closeout
Two edits, both confirmed via Gemini's reviewed ruling (one adopted as
written, one overridden by Pete -- see session record):

1. Issue 1 (adopted as written): primaryDimension is permanently
   optional on BookPiece, not a temporary gap awaiting a future
   required flip. Updates the Step 1 comment to stop describing a
   flip-to-required that is no longer going to happen. No type change
   -- the field was already `primaryDimension?: DimensionKey` from
   Step 1; this corrects the comment only, so it doesn't tell a future
   reader something false.

2. Issue 2 (Gemini's literal recommendation overridden by Pete):
   LIB-014 gets secondaryDimensions: ["aptitude", "authority"] added.
   primaryDimension is deliberately left unset -- LIB-014's two states
   (the_overloaded_manager / aptitude, the_founders_grip / authority)
   are co-equal, and picking one as "primary" would be an unforced,
   unjustified precision per Pete's explicit reasoning. stateIds is
   already set from the earlier batch and is not touched here.

Usage:
  python tools/patch_book_step2_close.py --dry-run
  python tools/patch_book_step2_close.py --write
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "web" / "lib" / "book-manifest.ts"

OLD_COMMENT = "  // Optional until Step 2 population is confirmed and applied -- flips to required per the locked schema once every entry has a value.\n  primaryDimension?: DimensionKey;"
NEW_COMMENT = "  // Permanently optional (Gemini-reviewed, Step 2 closeout) -- not every piece has a state-dimension home, and that's a normal, first-class state, not a gap awaiting population.\n  primaryDimension?: DimensionKey;"

OLD_LIB014_TAIL = '    contentPillar: "Pattern Named",\n    stateIds: ["the_overloaded_manager", "the_founders_grip"],\n  },'
NEW_LIB014_TAIL = '    contentPillar: "Pattern Named",\n    stateIds: ["the_overloaded_manager", "the_founders_grip"],\n    secondaryDimensions: ["aptitude", "authority"],\n  },'


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = TARGET_FILE.read_text(encoding="utf-8")

    if text.count(OLD_COMMENT) != 1:
        print(f"ABORT -- expected interface comment matched {text.count(OLD_COMMENT)} times, need exactly 1", file=sys.stderr)
        sys.exit(1)

    # Anchor the LIB-014 edit to its specific block, not a bare string match,
    # so a coincidentally-identical tail elsewhere can't be touched instead.
    block_pattern = re.compile(r'\{\s*id: "LIB-014".*?\n  \},', re.DOTALL)
    m = block_pattern.search(text)
    if not m:
        print("ABORT -- could not locate LIB-014 block", file=sys.stderr)
        sys.exit(1)
    lib014_block = m.group(0)
    if OLD_LIB014_TAIL not in lib014_block:
        print("ABORT -- LIB-014's expected tail shape not found (has it changed since batch 1?)", file=sys.stderr)
        sys.exit(1)
    if "secondaryDimensions" in lib014_block:
        print("ABORT -- LIB-014 already has secondaryDimensions set", file=sys.stderr)
        sys.exit(1)
    if "primaryDimension" in lib014_block:
        print("ABORT -- LIB-014 unexpectedly already has primaryDimension set", file=sys.stderr)
        sys.exit(1)

    new_lib014_block = lib014_block.replace(OLD_LIB014_TAIL, NEW_LIB014_TAIL)

    print("EDIT 1 -- interface comment (Issue 1, permanently optional)")
    print("BEFORE:")
    print(OLD_COMMENT)
    print("AFTER:")
    print(NEW_COMMENT)
    print("-" * 100)
    print("EDIT 2 -- LIB-014 (Issue 2, secondaryDimensions only)")
    print("BEFORE block:")
    print(lib014_block)
    print("AFTER block:")
    print(new_lib014_block)
    print("-" * 100)
    print("Confirm: primaryDimension absent from AFTER block:", '"primaryDimension"' not in new_lib014_block and "primaryDimension:" not in new_lib014_block)
    print("Confirm: stateIds unchanged:", 'stateIds: ["the_overloaded_manager", "the_founders_grip"]' in new_lib014_block)

    new_text = text.replace(OLD_COMMENT, NEW_COMMENT, 1)
    if new_text.count(lib014_block) != 1:
        print(f"ABORT -- LIB-014 block not uniquely present in text (count={new_text.count(lib014_block)})", file=sys.stderr)
        sys.exit(1)
    new_text = new_text.replace(lib014_block, new_lib014_block, 1)

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TARGET_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
