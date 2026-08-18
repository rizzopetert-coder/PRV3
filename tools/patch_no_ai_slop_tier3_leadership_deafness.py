"""
PRV3 -- apply the Tier 3 no-ai-slop fix for leadership-deafness.md
(prose em-dash count 13 -> 8; raw, including the exempt
"— Principal Resolution" line: 14 -> 9).

The chat-pasted version of this file (attached in-conversation) again
showed the recurring mojibake artifact, including inside the signature
line, and was not trusted or used. Confirmed instead against the actual
file delivered separately to Downloads
(C:\\Users\\rizzo\\Downloads\\leadership-deafness.md, landed 2026-08-17
21:52): zero mojibake, raw em-dash count exactly 9 as claimed.

Citation fix independently verified before applying, not just taken on
claim: the live text's "The research on this is brutal ... it literally
changes your brain" overclaimed Keltner's actual research, which is
behavioral (facial-expression matching, empathy/perspective-taking
tasks), not a neural claim -- confirmed via WebSearch against Keltner's
The Power Paradox findings. The neural/TMS mirroring evidence belongs to
a separate study (Obhi, McMaster University), also confirmed real via
WebSearch, and was never Keltner's own work. Same overclaim pattern
already corrected elsewhere in the corpus as HC-103 (confirmed present in
book-citations.ts). Fixed to "The research on this is consistent ... it
makes you worse at reading other people," with "spent decades" corrected
to "spent over two decades," matching Keltner's actual ~20+ year
research span. Keltner remains correctly named; no new citation entry
needed since HC-103 already covers this claim.

Diffed line-by-line against live (--strip-trailing-cr): every other
change is a pure punctuation conversion (em-dash to comma), no other
wording changes. Signature line untouched.

Usage:
  python tools/patch_no_ai_slop_tier3_leadership_deafness.py --dry-run
  python tools/patch_no_ai_slop_tier3_leadership_deafness.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"C:\Users\rizzo\Downloads\leadership-deafness.md")
LIVE = REPO_ROOT / "web/content/book/methodology/leadership-deafness.md"


def apply(dry_run: bool) -> int:
    if not SRC.exists():
        print(f"ABORT: {SRC} not found")
        return 1
    if not LIVE.exists():
        print(f"ABORT: {LIVE} not found")
        return 1
    new_content = SRC.read_text(encoding="utf-8")
    if "â" in new_content:
        print("ABORT: source still contains mojibake artifact -- not applying")
        return 1
    old_content = LIVE.read_text(encoding="utf-8")
    if dry_run:
        print(f"OK (dry-run): {LIVE} -- {len(old_content)} bytes -> {len(new_content)} bytes")
    else:
        LIVE.write_text(new_content, encoding="utf-8")
        print(f"WRITTEN: {LIVE}")

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
