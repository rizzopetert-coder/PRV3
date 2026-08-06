"""
PRV3 MOB Fix -- clean up garbled MemPalace Decision Register row

The prior patch (patch_mempalace_root_cause_closure.py) replaced only the
first three columns (Item/Tier/Status) of the MemPalace mine row, using a
substring match. That left the ORIGINAL row's remaining columns (Named
blocker/Last touched/Next check-in -- the old "confirmed three times, root
cause unknown" text) still trailing after the new content on the same
physical line, producing a garbled, duplicated row.

Fix: find the exact end of the new content (a unique anchor phrase) and
delete everything between it and the line's terminating newline.

Usage:
  python tools/patch_mempalace_row_cleanup.py --dry-run
  python tools/patch_mempalace_row_cleanup.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET = REPO_ROOT / "tools" / "_mob.txt"

# End of the NEW content this row should have -- everything after this point
# on the same line, up to the newline, is stale leftover from the old row.
END_ANCHOR = (
    "not merely worked around |"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TARGET.read_text(encoding="utf-8")

    count = content.count(END_ANCHOR)
    if count != 1:
        print(f"ABORT: expected exactly 1 occurrence of end anchor, found {count}")
        sys.exit(1)

    anchor_start = content.index(END_ANCHOR)
    anchor_end = anchor_start + len(END_ANCHOR)
    newline_pos = content.index("\n", anchor_end)

    stale_span = content[anchor_end:newline_pos]
    print(f"Stale trailing text to remove ({len(stale_span)} chars):")
    print(stale_span[:300] + (" ...[truncated]..." if len(stale_span) > 300 else ""))
    print("...")
    print(stale_span[-300:] if len(stale_span) > 300 else "")

    if not stale_span.strip():
        print("\nNothing stale found -- row already clean. No change needed.")
        return

    new_content = content[:anchor_end] + content[newline_pos:]

    if args.dry_run:
        print(f"\nDry run: would remove {len(stale_span)} stale characters after the anchor.")
        print("Re-run with --write to apply.")
    else:
        TARGET.write_text(new_content, encoding="utf-8")
        print(f"\nWrote fix: removed {len(stale_span)} stale characters.")


if __name__ == "__main__":
    main()
