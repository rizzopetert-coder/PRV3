"""
PRV3 -- Decision Register addition: multi-state compounding mechanism
for Friction Tax flagged as methodologically wrong, Set 3-independent.

Documentation-only, no version bump -- new open item, not a locked
decision, no rule change, no material workstream status change.

Usage:
  python tools/patch_mob_multistate_compounding_register.py --dry-run
  python tools/patch_mob_multistate_compounding_register.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

ANCHOR = (
    "| PrivateOutputBlock.friction_tax_estimate -- REMOVED (engine/output.py) "
    "| 3 | Resolved -- field removed | Previously flagged as vestigial: "
    "correctly typed (Optional[dict], {low, high, currency}) but confirmed "
    "permanently unassigned (build_private_block() lacks the intake context "
    "compute_friction_tax() needs) and unread (engine/contract.py's "
    "assemble_output() computes the real value fresh instead). Deferred at "
    "the time to keep that task's footprint matched to what was scoped. "
    "This pass confirmed the field was still genuinely dead (direct grep, "
    "not assumed) before removing it outright -- also removed the one live "
    "test assertion that directly accessed it (tools/test_output.py), "
    "which would otherwise have raised AttributeError. "
    "tools/test_contract.py's separate friction_tax_estimate check (the "
    "assembled output dict's key, a different thing entirely -- "
    "contract.py's own computed value, not this dataclass field) was "
    "confirmed unaffected and left untouched. Full suite + calibration "
    "confirmed zero regressions | This session (Claude Code) -- field "
    "removed | Closed -- no further check-in. If a comparable vestigial "
    "field surfaces again, treat it as a new item, not a reopening of "
    "this row |\n"
)

NEW_ROW = (
    "| Multi-state compounding mechanism for Friction Tax | 3 | Open -- "
    "flagged, not scoped, not designed | compute_friction_tax()'s current "
    "multi-state combination (plain arithmetic mean of STATE_MULTIPLIERS "
    "across identified state_ids) was flagged by Pete as methodologically "
    "wrong for the instrument -- averaging can dilute an org's tax below "
    "what its worst single condition alone would produce, and doesn't "
    "reflect that carrying multiple identified conditions should increase "
    "both cost and response urgency, not blend toward a midpoint. Out of "
    "scope for Calibration Set 3 (STATE_MULTIPLIERS per-state values) -- "
    "Set 3's scored values remain valid inputs regardless of which "
    "combination formula is eventually adopted, this only affects how "
    "per-state values combine when more than one state is identified, not "
    "the values themselves. Related open item: connects to the deferred "
    "\"urgency window\" from Diagnostic Dimension Expansion (Report Depth "
    "Initiative) -- if states should compound urgency as well as dollar "
    "cost, that may be the same design conversation, not two separate "
    "ones | This session (Claude Code) -- flagged, not fixed | Pete's "
    "call -- hold until Set 3 scoring is fully closed. Do not start "
    "design or Gemini handoff until Pete reopens this explicitly |\n"
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
    print("friction_tax_estimate -- REMOVED row:")
    print("=" * 72)
    print(NEW_ROW.rstrip("\n"))
    print("=" * 72)
    print("No version bump -- new open item, not a locked decision.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROW)
    MOB_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {MOB_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
