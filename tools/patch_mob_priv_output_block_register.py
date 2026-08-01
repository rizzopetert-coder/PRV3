"""
PRV3 -- Decision Register addition: PrivateOutputBlock.friction_tax_
estimate is now vestigial (correctly typed, never assigned, never read)
after this session's friction-tax private-output wiring.

Usage:
  python tools/patch_mob_priv_output_block_register.py --dry-run
  python tools/patch_mob_priv_output_block_register.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

ANCHOR = (
    '| Whenever Pete opens a dedicated task for the Section 13 rewrite -- '
    'not a forced check-in |\n'
)

NEW_ROW = (
    "| PrivateOutputBlock.friction_tax_estimate is now vestigial "
    "(engine/output.py) | 3 | Open, informational -- no urgency, minor "
    "cleanup | Fixed this session from the wrong Optional[float] type to "
    "the correct Optional[dict] ({low, high, currency}) shape, but "
    "confirmed build_private_block() (engine/output.py:534-553) cannot "
    "actually assign it -- it only receives one QualifiedState and a "
    "SeverityResult, not the intake data (org_size/industry/org_type) or "
    "the full multi-state state_ids list compute_friction_tax() requires. "
    "The real value is now computed fresh in engine/contract.py's "
    "assemble_output(), which has that context, and that function no "
    "longer reads priv.friction_tax_estimate at all. Net effect: the "
    "field is correctly typed but permanently unassigned and unread -- "
    "dead in a different way than before (was wrong-type placeholder, now "
    "right-type placeholder). Not removed this session, per explicit "
    "instruction -- flagged as a minor cleanup candidate only | This "
    "session (Claude Code) -- surfaced, not fixed | Whenever "
    "engine/output.py's PrivateOutputBlock is next touched for an "
    "unrelated reason, at which point removing the field is a cheap, "
    "low-risk cleanup -- not a forced check-in |\n"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = MOB_FILE.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count == 0:
        print("ABORT -- anchor not found", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches)", file=sys.stderr)
        sys.exit(1)

    print("New Decision Register row (Section 13a), inserted after the")
    print('Section 13 staleness row:')
    print("=" * 72)
    print(NEW_ROW.rstrip("\n"))
    print("=" * 72)
    print("No version bump -- informational addition only.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROW)
    MOB_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {MOB_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
