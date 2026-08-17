"""
PRV3 -- MOB update: clarify the /book em-dash cap (Section 14, "/book
editorial standard -- em-dash cap") to exempt the fixed "-- [Author
Name]" attribution/signature line from the <=8 prose-density count.

Pete's decision, this session: the cap targets prose clustering (dashes
overused as rhetorical interruption to the point of reading mechanical).
A signature-line dash is a fixed typographic convention -- one
occurrence, identical every time, functionally equivalent to an em dash
before a quote attribution -- not an instance of the pattern the cap
exists to catch. Counting it penalizes the byline for existing rather
than catching anything real.

Practical effect confirmed this session: toxic-culture.md and
silosolation.md (both use the "-- Principal Resolution" closer) need no
further em-dash changes under either reading -- both already clean on
prose alone. 14 total published files share this closer
(prompts/no-ai-slop-mechanical-scan.md's raw counts for all 14 need
re-reading as prose-only going forward, not the raw grep count that
included the signature line).

Version bump v4.182 -> v4.183: new locked-decision clarification, not a
session-log-only change.

Usage:
  python tools/patch_mob_emdash_signature_exemption.py --dry-run
  python tools/patch_mob_emdash_signature_exemption.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB = "tools/_mob.txt"
CLAUDE = "CLAUDE.md"

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


edit(
    MOB,
    "| /book editorial standard — em-dash cap | Em-dash density hard-capped at ≤8 per piece, enforced by grep, not judgment call. |\n",
    "| /book editorial standard — em-dash cap | Em-dash density hard-capped at ≤8 per piece, enforced by grep, not judgment call. **Clarified this session:** the cap applies to prose content only. The closing \"— [Author Name]\" attribution/signature line (e.g. \"— Principal Resolution\", used as a fixed closer across 14 published methodology pieces) is exempted from the count — it is a fixed typographic convention, one occurrence, identical every time, not an instance of the rhetorical-interruption pattern the cap exists to catch. Grep-based counts for any file using this closer must subtract the signature line's own dash before comparing against ≤8. |\n",
)
edit(MOB, "\\\\\\#\\\\\\# MOB v4.182", "\\\\\\#\\\\\\# MOB v4.183")
edit(CLAUDE, "| MOB version | v4.182 |", "| MOB version | v4.183 |")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    contents: dict[str, str] = {}
    for path, _, _ in EDITS:
        if path not in contents:
            contents[path] = (REPO_ROOT / path).read_text(encoding="utf-8")

    for i, (path, old, new) in enumerate(EDITS, 1):
        count = contents[path].count(old)
        if count != 1:
            print(f"ABORT: edit #{i} ({path}): expected exactly 1 match, found {count}")
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        contents[path] = contents[path].replace(old, new, 1)

    if args.dry_run:
        print(f"=== {len(EDITS)} edit(s) across {len(contents)} file(s) would apply cleanly ===")
        print("\nDry run complete. Re-run with --write to apply.")
    else:
        for path, content in contents.items():
            (REPO_ROOT / path).write_text(content, encoding="utf-8")
        print(f"=== {len(EDITS)} edit(s) written across {len(contents)} file(s) ===")


if __name__ == "__main__":
    main()
