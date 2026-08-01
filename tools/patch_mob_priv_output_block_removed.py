"""
PRV3 -- Decision Register update: PrivateOutputBlock.friction_tax_
estimate field removed (was flagged vestigial, now actually cleaned up).

Documentation-only status update, no version bump -- same reasoning as
the liability_block row precedent: this row already existed, this only
updates its status text to reflect the field's actual removal, not a
new locked decision or workstream status change in itself. The real
code change (the field removal) is tracked via its own commit, not a
MOB version bump.

Usage:
  python tools/patch_mob_priv_output_block_removed.py --dry-run
  python tools/patch_mob_priv_output_block_removed.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

OLD_ROW = (
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
    "dead in a different way than before (was wrong-type placeholder, "
    "now right-type placeholder). Not removed this session, per explicit "
    "instruction -- flagged as a minor cleanup candidate only | This "
    "session (Claude Code) -- surfaced, not fixed | Whenever "
    "engine/output.py's PrivateOutputBlock is next touched for an "
    "unrelated reason, at which point removing the field is a cheap, "
    "low-risk cleanup -- not a forced check-in |\n"
)

NEW_ROW = (
    "| PrivateOutputBlock.friction_tax_estimate -- REMOVED (engine/"
    "output.py) | 3 | Resolved -- field removed | Previously flagged as "
    "vestigial: correctly typed (Optional[dict], {low, high, currency}) "
    "but confirmed permanently unassigned (build_private_block() lacks "
    "the intake context compute_friction_tax() needs) and unread "
    "(engine/contract.py's assemble_output() computes the real value "
    "fresh instead). Deferred at the time to keep that task's footprint "
    "matched to what was scoped. This pass confirmed the field was still "
    "genuinely dead (direct grep, not assumed) before removing it "
    "outright -- also removed the one live test assertion that directly "
    "accessed it (tools/test_output.py), which would otherwise have "
    "raised AttributeError. tools/test_contract.py's separate "
    "friction_tax_estimate check (the assembled output dict's key, a "
    "different thing entirely -- contract.py's own computed value, not "
    "this dataclass field) was confirmed unaffected and left untouched. "
    "Full suite + calibration confirmed zero regressions | This session "
    "(Claude Code) -- field removed | Closed -- no further check-in. If "
    "a comparable vestigial field surfaces again, treat it as a new "
    "item, not a reopening of this row |\n"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = MOB_FILE.read_text(encoding="utf-8")
    count = text.count(OLD_ROW)
    if count == 0:
        print("ABORT -- old row not found", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- old row not unique ({count} matches)", file=sys.stderr)
        sys.exit(1)

    print("Decision Register row update (Section 13a):")
    print("=" * 72)
    print("- " + OLD_ROW.rstrip("\n"))
    print()
    print("+ " + NEW_ROW.rstrip("\n"))
    print("=" * 72)
    print("No version bump -- documentation-only status update, same")
    print("reasoning as the liability_block row precedent.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    new_text = text.replace(OLD_ROW, NEW_ROW)
    MOB_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {MOB_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
