"""
PRV3 -- /book Content Architecture Phase 2, Step 1
Schema extension: adds DimensionKey type and primaryDimension /
secondaryDimensions / stateIds fields to the BookPiece interface in
web/lib/book-manifest.ts.

Deviation from the handoff's literal schema, confirmed with Pete before
writing: primaryDimension is landed as OPTIONAL here, not required.
Step 2 (population) is explicitly gated on Pete's review of a
match/no-match report and cannot be written in the same pass -- making
primaryDimension required now would break tsc on all 88 existing
entries for the duration of that gap. Flip to required in a follow-up
edit once Step 2's population write is confirmed and applied.

Usage:
  python tools/patch_book_schema_step1.py --dry-run
  python tools/patch_book_schema_step1.py --write
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "web" / "lib" / "book-manifest.ts"

OLD = '''export type BookContentType = "memo" | "methodology" | "case_pattern";
export type BookVoice = "standard" | "from_the_author";

export interface BookPiece {
  id: string;
  slug: string;
  contentType: BookContentType;
  voice: BookVoice;
  title: string;
  teaser: string;
  signatureId?: string;
  citationIds?: string[];
  relatedSlug?: string;
  author: "Principal Resolution";
  status: "draft" | "published" | "parked";
  scheduledWeek?: number;
  scheduledDay?: "Tue" | "Thu" | "Fri";
  contentPillar?: "Reframe" | "Pattern Named" | "Case Composited" | "Underneath" | "Foundation";
}'''

NEW = '''export type BookContentType = "memo" | "methodology" | "case_pattern";
export type BookVoice = "standard" | "from_the_author";
export type DimensionKey = "aptitude" | "authority" | "alliance" | "attitude";

export interface BookPiece {
  id: string;
  slug: string;
  contentType: BookContentType;
  voice: BookVoice;
  title: string;
  teaser: string;
  signatureId?: string;
  citationIds?: string[];
  relatedSlug?: string;
  author: "Principal Resolution";
  status: "draft" | "published" | "parked";
  scheduledWeek?: number;
  scheduledDay?: "Tue" | "Thu" | "Fri";
  contentPillar?: "Reframe" | "Pattern Named" | "Case Composited" | "Underneath" | "Foundation";
  // Optional until Step 2 population is confirmed and applied -- flips to required per the locked schema once every entry has a value.
  primaryDimension?: DimensionKey;
  secondaryDimensions?: DimensionKey[];
  stateIds?: string[];
}'''


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = TARGET_FILE.read_text(encoding="utf-8")
    if OLD not in text:
        raise SystemExit("ERROR: expected interface block not found -- file may have changed.")
    if text.count(OLD) != 1:
        raise SystemExit("ERROR: expected interface block matched more than once.")

    print(f"Target file: {TARGET_FILE.relative_to(REPO_ROOT)}")
    print("=" * 72)
    print("BEFORE:")
    print(OLD)
    print("-" * 72)
    print("AFTER:")
    print(NEW)
    print("=" * 72)

    if args.dry_run:
        print("DRY RUN -- no file written.")
        return

    new_text = text.replace(OLD, NEW, 1)
    TARGET_FILE.write_text(new_text, encoding="utf-8")
    print(f"WROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
