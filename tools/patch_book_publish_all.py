#!/usr/bin/env python
"""
PRV3 -- patch_book_publish_all.py
/book go-live: flips all 87 status:"draft" entries in web/lib/book-manifest.ts
to status:"published". LIB-037 ("Organizational Assessment: Engagement SOP")
stays status:"parked", untouched -- not part of this change.

Pete's explicit authorization this session. Rendering fix (commit 4402c24),
citation-free compliance sweep, and shadow-model sweep already confirmed
clean earlier this session; nav confirmed live.

Match pattern is the literal string status: "draft", (WITH the trailing
comma) -- this deliberately excludes the BookPiece interface's own type
declaration (line ~15: status: "draft" | "published" | "parked";), which
contains the substring status: "draft" but with no trailing comma there,
followed by the union's other members instead. Verified before writing
this script: grep -c 'status: "draft"' (no comma) returns 88 -- 87 real
entries + the 1 interface line; grep -c 'status: "draft",' (with comma)
returns exactly 87 -- confirms the comma-inclusive pattern isolates only
real entries.

Global replace_all is used (not a single first-match replace) since this
is a genuine bulk change touching every one of the 87 entries identically
-- unlike this project's usual single-anchor patch convention.

Usage:
  python tools/patch_book_publish_all.py --dry-run
  python tools/patch_book_publish_all.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "web" / "lib" / "book-manifest.ts"

OLD = 'status: "draft",'
NEW = 'status: "published",'

# Sanity-check constants, verified against the file before writing this
# script -- dry-run re-verifies these live against the actual file too.
EXPECTED_DRAFT_COUNT = 87
EXPECTED_PARKED_COUNT = 1
EXPECTED_TOTAL_ENTRIES = 88


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    if not TARGET.exists():
        print(f"ERROR: target not found: {TARGET}")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8")

    draft_count = text.count(OLD)
    parked_count = text.count('status: "parked",')
    published_count = text.count('status: "published",')
    total_entries = text.count('id: "')  # interface's own id field is `id: string;` (no quote), doesn't match

    print(f"Current state of {TARGET.name}:")
    print(f"  status: \"draft\",     count = {draft_count}  (expected {EXPECTED_DRAFT_COUNT})")
    print(f"  status: \"parked\",    count = {parked_count}  (expected {EXPECTED_PARKED_COUNT})")
    print(f"  status: \"published\", count = {published_count}  (expected 0 before write)")
    print(f"  total entries         = {total_entries}  (expected {EXPECTED_TOTAL_ENTRIES})")

    checks_ok = (
        draft_count == EXPECTED_DRAFT_COUNT
        and parked_count == EXPECTED_PARKED_COUNT
        and total_entries == EXPECTED_TOTAL_ENTRIES
    )

    if not checks_ok:
        print("\n  ERROR: counts do not match expected values -- aborting, do not proceed blind.")
        sys.exit(1)

    if args.dry_run:
        print(f"\nDRY RUN -- would replace {draft_count} occurrences of:")
        print(f'    {OLD!r}')
        print(f"  with:")
        print(f'    {NEW!r}')
        print(f"\n  status: \"parked\", (LIB-037) -- left untouched, {parked_count} occurrence, not matched by this pattern")
        print(f"\n  Result after write: {draft_count} published + {parked_count} parked = {draft_count + parked_count} total (expect {EXPECTED_TOTAL_ENTRIES})")
        print("\n  All checks passed. Ready for --write.")
        return

    new_text = text.replace(OLD, NEW)
    new_draft_count = new_text.count(OLD)
    new_published_count = new_text.count('status: "published",')
    new_parked_count = new_text.count('status: "parked",')

    if new_draft_count != 0:
        print(f"ERROR: {new_draft_count} draft entries remain after replace -- aborting write.")
        sys.exit(1)
    if new_published_count != EXPECTED_DRAFT_COUNT:
        print(f"ERROR: published count after replace is {new_published_count}, expected {EXPECTED_DRAFT_COUNT} -- aborting write.")
        sys.exit(1)
    if new_parked_count != EXPECTED_PARKED_COUNT:
        print(f"ERROR: parked count changed to {new_parked_count}, expected unchanged {EXPECTED_PARKED_COUNT} -- aborting write.")
        sys.exit(1)

    TARGET.write_text(new_text, encoding="utf-8")
    print(f"WRITTEN: {TARGET}")
    print(f"  {draft_count} entries flipped draft -> published")
    print(f"  {new_parked_count} entry left parked (LIB-037)")
    print(f"  {new_published_count + new_parked_count} total accounted for")


if __name__ == "__main__":
    main()
