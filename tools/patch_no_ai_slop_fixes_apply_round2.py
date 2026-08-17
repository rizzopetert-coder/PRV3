"""
PRV3 -- apply the final 4 of 8 no-ai-slop content fixes (toxic-culture.md,
silosolation.md, anchor.md, why-blaming-the-person-almost-never-fixes-the-
problem.md). The other 4 (everyone-is-defensive-and-no-one-knows-why.md,
the-room-that-never-pushes-back.md, built-for-comfort.md,
one-exception-at-a-time.md) plus the 3 new book-citations.ts entries
(HC-MITCHELLWOOD-1980, HC-HEINRICH-1931, HC-BLUME-2010) were already
applied in a prior commit (tools/patch_no_ai_slop_fixes_apply.py).

These 4 were withheld across two earlier delivery attempts -- both times
the chat-paste channel introduced a real "â" mojibake artifact in place
of every em-dash, confirmed absent from the live repo entirely (zero
occurrences anywhere), so not a pre-existing quirk. This round's content
arrived via the Downloads file channel instead (same mechanism that
delivered the first 4 clean) and is confirmed byte-clean:
  anchor.md: no mojibake, em-dash count 8
  silosolation.md: no mojibake, em-dash count 8
  toxic-culture.md: no mojibake, em-dash count 8
  why-blaming-the-person-almost-never-fixes-the-problem.md: no mojibake,
    em-dash count 8, all 5 named citations (Mitchell & Wood 1980,
    Swift/Moore/Sharek/Gino 2013, Heinrich 1931,
    Blume/Ford/Baldwin/Huang 2010, Senge 1990) confirmed present

All 4 diffed line-by-line against live counterparts before this script
was written -- each diff is a further em-dash trim (comma/period/colon
substitution) plus, for anchor.md, the previously-verified
throat-clearing/header/rhetorical-setup fixes, all consistent with the
described fix and nothing else changed.

Usage:
  python tools/patch_no_ai_slop_fixes_apply_round2.py --dry-run
  python tools/patch_no_ai_slop_fixes_apply_round2.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = Path(r"C:\Users\rizzo\Downloads")

FILE_PAIRS = [
    ("toxic-culture.md", "web/content/book/methodology/toxic-culture.md"),
    ("silosolation.md", "web/content/book/methodology/silosolation.md"),
    ("why-blaming-the-person-almost-never-fixes-the-problem.md", "web/content/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem.md"),
    ("anchor.md", "web/content/book/methodology/anchor.md"),
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
