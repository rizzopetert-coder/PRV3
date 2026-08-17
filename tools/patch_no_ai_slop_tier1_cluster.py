"""
PRV3 -- apply the Tier 1 no-ai-slop fix: the 4-file case_pattern closing-
duplicate cluster (what-the-organization-decided-he-was-worth.md,
the-resignation-that-ended-a-department.md, what-ready-didnt-include.md,
the-first-one-out-the-door.md).

Delivered via a zip in Downloads (files0.zip -> files0/), not chat-paste,
per the mojibake lesson from the prior 8-file batch -- confirmed clean
before this script was written: zero "â" artifacts, em-dash counts
7/7/7/7 exactly matching what was claimed, all 4 diffed line-by-line
against live counterparts (each diff is the closing-kicker rewrite only,
nothing else changed).

Closing lines confirmed distinct from each other and from the two
already-live fixes in this same cluster (built-for-comfort.md,
one-exception-at-a-time.md):
  the-first-one-out-the-door.md: "...Most organizations spend it writing
    a job posting." (dropped the shared "Every organization has that
    window" clause entirely)
  the-resignation-that-ended-a-department.md: "...Most organizations
    spend it assuming eleven years of knowledge will fit on a
    fifteen-item checklist." (also dropped the shared clause)
  what-the-organization-decided-he-was-worth.md: "...Most organizations
    spend it hoping the test never comes." (also dropped the shared
    clause)
  what-ready-didnt-include.md: "Every organization has that window. Most
    spend it redefining ready after the launch instead of before it." --
    KEPT the "Every organization has that window" opening clause. This
    is the same clause built-for-comfort.md and one-exception-at-a-time.md
    also still open with -- a real, smaller residual duplication, not
    eliminated by this fix. Flagged in the commit message and to Pete
    directly; not silently treated as fully resolved.

Usage:
  python tools/patch_no_ai_slop_tier1_cluster.py --dry-run
  python tools/patch_no_ai_slop_tier1_cluster.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(r"C:\Users\rizzo\Downloads\files0")

FILE_PAIRS = [
    ("what-the-organization-decided-he-was-worth.md", "web/content/book/case_pattern/what-the-organization-decided-he-was-worth.md"),
    ("the-resignation-that-ended-a-department.md", "web/content/book/case_pattern/the-resignation-that-ended-a-department.md"),
    ("what-ready-didnt-include.md", "web/content/book/case_pattern/what-ready-didnt-include.md"),
    ("the-first-one-out-the-door.md", "web/content/book/case_pattern/the-first-one-out-the-door.md"),
]


def apply(dry_run: bool) -> int:
    for src_name, live_rel in FILE_PAIRS:
        src_path = SOURCE / src_name
        live_path = REPO_ROOT / live_rel
        if not src_path.exists():
            print(f"ABORT: {src_path} not found")
            return 1
        if not live_path.exists():
            print(f"ABORT: {live_path} not found")
            return 1
        new_content = src_path.read_text(encoding="utf-8")
        if "â" in new_content:
            print(f"ABORT: {src_name} still contains mojibake artifact -- not applying")
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
