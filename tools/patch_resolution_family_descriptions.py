"""
PRV3 -- Patch: engine/resolution_families.py COPY PENDING placeholders

Replaces the four "description" field values in
RESOLUTION_FAMILY_DESCRIPTIONS with Pete-supplied final copy. No schema
change, no key changes, no other fields touched -- the inline
"# COPY PENDING -- ..." comments and the module docstring's "COPY
PENDING" note are deliberately left as-is, out of this task's stated
scope (flagged separately, not fixed here).

Usage:
  python tools/patch_resolution_family_descriptions.py --dry-run
  python tools/patch_resolution_family_descriptions.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "engine" / "resolution_families.py"

EDITS = [
    (
        '        "description": "COPY PENDING",  # COPY PENDING — structural design resolution copy\n',
        '        "description": "Something in how decisions get made, who holds authority, or how the organization is built is producing this condition. Not a person carrying it. The structure itself. It will keep producing the same outcome until that structure changes. Fixing it means no longer managing around it.",  # COPY PENDING — structural design resolution copy\n',
    ),
    (
        '        "description": "COPY PENDING",  # COPY PENDING — capability development resolution copy\n',
        '        "description": "Somebody in this organization needs to be able to do something they can\'t do yet, and no amount of good intention closes that gap on its own. This is capability work. It\'s specific, it\'s learnable, and it requires deliberate practice aimed at exactly what the diagnostic found, not a general program hoping to cover it.",  # COPY PENDING — capability development resolution copy\n',
    ),
    (
        '        "description": "COPY PENDING",  # COPY PENDING — investigative / compliance resolution copy\n',
        '        "description": "Something here needs a direct, unbiased look from someone with no stake in what they find. Not coaching. Not a communication fix. A fact-finding problem, and the resolution starts with an honest, unflinching read on what\'s actually happening before anyone decides what to do about it.",  # COPY PENDING — investigative / compliance resolution copy\n',
    ),
    (
        '        "description": "COPY PENDING",  # COPY PENDING — strategic direction / culture resolution copy\n',
        '        "description": "The organization is drifting, and drift doesn\'t correct itself. This is about realigning what the organization says it values with what it actually rewards and tolerates day to day. Resolution here means naming the gap plainly and doing the harder work of closing it, not writing a new mission statement.",  # COPY PENDING — strategic direction / culture resolution copy\n',
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = TARGET_FILE.read_text(encoding="utf-8")

    for old, new in EDITS:
        count = text.count(old)
        if count == 0:
            print(f"ABORT -- anchor not found:\n{old!r}", file=sys.stderr)
            sys.exit(1)
        if count > 1:
            print(f"ABORT -- anchor not unique ({count} matches):\n{old!r}", file=sys.stderr)
            sys.exit(1)

    print(f"Target: {TARGET_FILE.relative_to(REPO_ROOT)}")
    print("=" * 72)
    for old, new in EDITS:
        print("- " + old.rstrip("\n"))
        print("+ " + new.rstrip("\n"))
        print()
    print("=" * 72)

    if args.dry_run:
        print("DRY RUN -- no file written.")
        return

    for old, new in EDITS:
        text = text.replace(old, new)
    TARGET_FILE.write_text(text, encoding="utf-8")
    print(f"WROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
