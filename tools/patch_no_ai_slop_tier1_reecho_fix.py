"""
PRV3 -- apply the re-revision fixing the "spend it [gerund]-ing" cross-piece
echo caught by the mechanical scan re-run after the first Tier 1 cluster
fix. 3 files re-revised (what-ready-didnt-include.md,
the-first-one-out-the-door.md, the-resignation-that-ended-a-department.md);
what-the-organization-decided-he-was-worth.md's "hoping" ending kept as-is
deliberately, for variety, not touched by this pass.

Delivered via Downloads (not chat-paste), confirmed clean before this
script was written: zero mojibake in any of the 3, em-dash counts
unchanged at 7 each (only the closing line changed -- confirmed via direct
diff, every other line identical to the version already live).

Usage:
  python tools/patch_no_ai_slop_tier1_reecho_fix.py --dry-run
  python tools/patch_no_ai_slop_tier1_reecho_fix.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = Path(r"C:\Users\rizzo\Downloads")

FILE_PAIRS = [
    ("the-resignation-that-ended-a-department.md", "web/content/book/case_pattern/the-resignation-that-ended-a-department.md"),
    ("the-first-one-out-the-door.md", "web/content/book/case_pattern/the-first-one-out-the-door.md"),
    ("what-ready-didnt-include.md", "web/content/book/case_pattern/what-ready-didnt-include.md"),
]


def apply(dry_run: bool) -> int:
    for dl_name, live_rel in FILE_PAIRS:
        dl_path = DOWNLOADS / dl_name
        live_path = REPO_ROOT / live_rel
        if not dl_path.exists():
            print(f"ABORT: {dl_path} not found")
            return 1
        if not live_path.exists():
            print(f"ABORT: {live_path} not found")
            return 1
        new_content = dl_path.read_text(encoding="utf-8")
        if "â" in new_content:
            print(f"ABORT: {dl_name} still contains mojibake artifact -- not applying")
            return 1
        old_content = live_path.read_text(encoding="utf-8")
        if dry_run:
            print(f"OK (dry-run): {live_rel} -- {len(old_content)} bytes -> {len(new_content)} bytes")
        else:
            live_path.write_text(new_content, encoding="utf-8")
            print(f"WRITTEN: {live_rel}")

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
