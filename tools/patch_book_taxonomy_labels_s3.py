"""
PRV3 -- /book Content Architecture Phase 2, Step 3 (labels file only)
Creates web/lib/book-taxonomy-labels.ts -- DimensionKey type +
PUBLIC_DIMENSION_LABELS, four entries. Titles reused verbatim from the
diagnostic self-selection surface (web/data/taxonomy.ts's UICopy
register); descriptions are new, one line each, for /book visitors who
have no diagnostic-flow setup to lean on.

Pillar-page wiring is explicitly OUT OF SCOPE for this script --
app/book/dimension/[slug]/page.tsx does not exist yet (Step 4 not yet
built). This script only creates the new, standalone label file.

Note: the handoff's description text used literal "--" where the rest
of this codebase's public-facing copy (taxonomy.ts, book-manifest.ts)
consistently uses a real em dash. Rendered as em dash here to match
existing convention -- flagged for Pete's review, not silently assumed
without surfacing it.

Usage:
  python tools/patch_book_taxonomy_labels_s3.py --dry-run
  python tools/patch_book_taxonomy_labels_s3.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "web" / "lib" / "book-taxonomy-labels.ts"

CONTENT = """export type DimensionKey = "aptitude" | "authority" | "alliance" | "attitude";

export const PUBLIC_DIMENSION_LABELS: Record<DimensionKey, { title: string; description: string }> = {
  aptitude: {
    title: "How the work actually gets done",
    description: "Skills, roles, and capacity — whether people can do what the job requires, and whether the structure around them lets them.",
  },
  authority: {
    title: "Who really has the power to decide",
    description: "Where decisions actually get made, versus where the org chart says they get made.",
  },
  alliance: {
    title: "How people work together",
    description: "Trust, coordination, and follow-through across teams — what happens at the handoffs.",
  },
  attitude: {
    title: "How people show up",
    description: "Candor, culture, and the unwritten rules people have learned to live by.",
  },
};
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if TARGET_FILE.exists():
        print(f"ABORT -- {TARGET_FILE.relative_to(REPO_ROOT)} already exists, this script only creates a new file", file=sys.stderr)
        sys.exit(1)

    print(f"New file: {TARGET_FILE.relative_to(REPO_ROOT)}")
    print("=" * 72)
    print(CONTENT)
    print("=" * 72)
    print("No other files touched by this script.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TARGET_FILE.write_text(CONTENT, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
