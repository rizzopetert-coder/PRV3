"""
PRV3 -- Category C, item C.2: reword output_synthesis.py's
asset_resolution_anchor_text system prompt instruction. Pure prompt
copy change -- the field remains LLM-generated per-session, only the
instruction steering its tone changes. No em-dashes in the replacement
text, confirmed directly against the standing rule that LLM
system-prompt content specs avoid them entirely.

Usage:
  python tools/patch_c2_asset_tone.py --dry-run
  python tools/patch_c2_asset_tone.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


O = "engine/output_synthesis.py"

edit(
    O,
    "asset_resolution_anchor_text (private, principal only):\n"
    "What strength exists to build from. 1-3 sentences. Draw from asset_score and intake.\n"
    "Not reassurance. An honest account of what is working. If asset_score is low, say so\n"
    "plainly. Do not manufacture strength the diagnostic did not find.",
    "asset_resolution_anchor_text (private, principal only):\n"
    "What strength exists to build from. 1-3 sentences. Draw from asset_score and intake.\n"
    "Name what's actually there, including if the picture is thin, but in the same steady,\n"
    "descriptive register as the rest of the report, not as a call-out. This is a reading\n"
    "of current reality, not a verdict.",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 200 chars): {old[:200]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
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
