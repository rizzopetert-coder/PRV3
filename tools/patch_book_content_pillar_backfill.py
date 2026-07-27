"""
PRV3 -- /book Content Architecture Phase 2, Step 0
contentPillar backfill: FTA-18 through FTA-53 (36 entries) get
contentPillar: "Reframe" inserted after their status field.

Scope confirmed with Pete before writing this script (two discrepancies
found against the original handoff and resolved):
  - LIB-052 already carries contentPillar: "Pattern Named" (not absent as
    the handoff assumed) -- left untouched, NOT changed to "Underneath".
  - LIB-037 (parked, "Organizational Assessment: Engagement SOP") has no
    contentPillar and is not one of the FTA-18-53 entries -- left
    untagged. Target after this step is 87/88, not 88/88.

Usage:
  python tools/patch_book_content_pillar_backfill.py --dry-run
  python tools/patch_book_content_pillar_backfill.py --write
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "web" / "lib" / "book-manifest.ts"

TARGET_IDS = [f"FTA-{i:02d}" for i in range(18, 54)]  # FTA-18 .. FTA-53, 36 entries

OLD_TAIL_TEMPLATE = '    author: "Principal Resolution",\n    status: "published",\n  }},'
NEW_TAIL_TEMPLATE = (
    '    author: "Principal Resolution",\n'
    '    status: "published",\n'
    '    contentPillar: "Reframe",\n'
    "  },"
)


def build_edits(text: str) -> list[tuple[str, str, str]]:
    edits: list[tuple[str, str, str]] = []
    for entry_id in TARGET_IDS:
        # Anchor on the specific entry block so we don't touch any other
        # entry that happens to share the same tail shape.
        block_pattern = re.compile(
            r'(\{\s*id: "' + re.escape(entry_id) + r'".*?)(\n\s*\},)',
            re.DOTALL,
        )
        m = block_pattern.search(text)
        if not m:
            print(f"ERROR: could not locate entry block for {entry_id}", file=sys.stderr)
            sys.exit(1)
        block = m.group(0)
        old_tail = '    author: "Principal Resolution",\n    status: "published",\n  },'
        new_tail = (
            '    author: "Principal Resolution",\n'
            '    status: "published",\n'
            '    contentPillar: "Reframe",\n'
            "  },"
        )
        if old_tail not in block:
            print(f"ERROR: expected tail shape not found in {entry_id} block", file=sys.stderr)
            sys.exit(1)
        old_full = block
        new_full = block.replace(old_tail, new_tail)
        edits.append((entry_id, old_full, new_full))
    return edits


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = TARGET_FILE.read_text(encoding="utf-8")
    edits = build_edits(text)

    print(f"Target file: {TARGET_FILE.relative_to(REPO_ROOT)}")
    print(f"Entries to modify: {len(edits)} ({TARGET_IDS[0]} .. {TARGET_IDS[-1]})")
    print("=" * 72)

    new_text = text
    for entry_id, old_full, new_full in edits:
        print(f"\n--- {entry_id} ---")
        print("BEFORE (tail):")
        for line in old_full.strip().splitlines()[-2:]:
            print("  " + line)
        print("AFTER (tail):")
        for line in new_full.strip().splitlines()[-3:]:
            print("  " + line)
        if old_full not in new_text:
            print(f"ERROR: block for {entry_id} not found in working text (already edited?)", file=sys.stderr)
            sys.exit(1)
        new_text = new_text.replace(old_full, new_full, 1)

    print("\n" + "=" * 72)

    if args.dry_run:
        # Verification counts against the dry-run result, without writing.
        pillar_count = new_text.count("contentPillar:")
        print(f"DRY RUN -- no file written.")
        print(f"Projected contentPillar count after write: {pillar_count} (expect 87)")
        print("LIB-052 unchanged check:", '"Pattern Named"' in new_text and 'id: "LIB-052"' in new_text)
        print("LIB-037 remains untagged (expected, out of scope this step).")
        return

    TARGET_FILE.write_text(new_text, encoding="utf-8")
    pillar_count = new_text.count("contentPillar:")
    print(f"WROTE {TARGET_FILE.relative_to(REPO_ROOT)}")
    print(f"contentPillar count after write: {pillar_count} (expect 87)")


if __name__ == "__main__":
    main()
