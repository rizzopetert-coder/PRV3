"""
PRV3 -- Revised Decision Register update, replacing the previously
dry-run (never written) combined version with two separate entries per
Pete's explicit split:

Entry A: append the_untouchable cross-state evidence to the EXISTING
"Multi-state compounding mechanism for Friction Tax" row (no new row),
plus update that row's "Last touched" and "Next check-in" columns.
Calibration Set 3's completion status is NOT included in this row
(moved to Entry B per Pete's revision).

Entry B: a genuinely NEW row -- "Calibration Set 3 (STATE_MULTIPLIERS)
-- Scoring Complete" -- mapping Pete's four labeled fields (Item,
Status, Context, Next check-in) onto the Decision Register's real
6-column convention (Item, Tier, Status, Detail, Last touched, Next
check-in). Tier set to 3 (consistent with every other row in this
table). "Last touched" not specified by Pete for this new row --
filled with "This session (Claude Code)" matching standing convention.

Em-dashes in Pete's supplied text converted to "--" to match this
file's own established internal convention (every other row in this
session's writes uses "--", not real em-dashes, even though Pete's own
chat instructions aren't bound by that copy rule).

Documentation-only, no version bump.

Usage:
  python tools/patch_mob_set3_scoring_complete.py --dry-run
  python tools/patch_mob_set3_scoring_complete.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

# ── Entry A: append to the existing row, update Last touched + Next check-in ──

ROW_A_OLD = (
    "this is now three related-but-distinct compounding questions to "
    "resolve together when this item is reopened: (1) how multiple "
    "states combine, (2) within-criterion stacking, (3) breadth-across-"
    "criteria stacking | This session (Claude Code) -- flagged, not "
    "fixed | Pete's call -- hold until Set 3 scoring is fully closed. "
    "Do not start design or Gemini handoff until Pete reopens this "
    "explicitly |\n"
)

ROW_A_NEW = (
    "this is now three related-but-distinct compounding questions to "
    "resolve together when this item is reopened: (1) how multiple "
    "states combine, (2) within-criterion stacking, (3) breadth-across-"
    "criteria stacking. **Additional evidence (from Set 3 scoring):** "
    "the_untouchable's signaling cost -- what employees learn about "
    "organizational values from watching someone go unaccountable -- "
    "doesn't fit cleanly into any of the four per-state scoring "
    "criteria, and was deliberately left out of that state's score "
    "rather than force-fit. Reasoning: this isn't a missing fifth "
    "criterion for this one state, it's a cross-state phenomenon -- an "
    "org carrying the_untouchable is disproportionately likely to also "
    "carry culture_drift, the_basement_standard, or the_wrong_reward, "
    "since the same signaling mechanism that erodes accountability in "
    "one state tends to seed or reinforce the others. This is direct "
    "evidence for why plain multi-state averaging under-weights an org "
    "carrying the_untouchable: the real cost shows up across multiple "
    "states' co-occurrence, not within any single state's row. Relevant "
    "to whichever compounding design gets adopted when this item is "
    "reopened | This session (Claude Code) -- evidence added | Pete's "
    "call -- reopen when ready to design the compounding mechanism "
    "(state-count averaging, within-criterion stacking, breadth-across-"
    "criteria stacking, plus the_untouchable cross-state evidence) |\n"
)

# ── Entry B: brand new row, inserted immediately after Entry A's row ─────────

ROW_B_ANCHOR_TAIL = (
    "call -- reopen when ready to design the compounding mechanism "
    "(state-count averaging, within-criterion stacking, breadth-across-"
    "criteria stacking, plus the_untouchable cross-state evidence) |\n"
)

ROW_B = (
    "| Calibration Set 3 (STATE_MULTIPLIERS) -- Scoring Complete | 3 | "
    "Closed -- all 57 states scored across the 4-criterion rubric "
    "(Turnover/Retention, Productivity/Output, Decision-Quality/"
    "Velocity, Legal/Compliance), all rationales complete, zero open "
    "flags | Methodology per prompts/friction-tax-state-multiplier-"
    "methodology.md. Scoring worksheet and rationale work done in "
    "Claude.ai, values not yet applied to engine/friction_tax.py | This "
    "session (Claude Code) | Ready for Gemini architecture review of "
    "schema/type approach (consistent with OrgTypeScalarEntry pattern "
    "from Set 1) before CC writes STATE_MULTIPLIERS values. Not yet "
    "sent to Gemini |\n"
)


def _apply(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        print(f"ABORT -- anchor not found: {label}", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches): {label}", file=sys.stderr)
        sys.exit(1)
    return text.replace(old, new)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = MOB_FILE.read_text(encoding="utf-8")

    # Entry A: append evidence + update Last touched / Next check-in.
    text = _apply(text, ROW_A_OLD, ROW_A_NEW, "Entry A (existing row update)")
    # Entry B: insert new row immediately after Entry A's row.
    text = _apply(text, ROW_B_ANCHOR_TAIL, ROW_B_ANCHOR_TAIL + ROW_B, "Entry B (new row insertion)")

    print("Entry A -- updated existing row (evidence + Last touched + Next check-in):")
    print("=" * 72)
    print("- " + ROW_A_OLD.rstrip("\n"))
    print()
    print("+ " + ROW_A_NEW.rstrip("\n"))
    print("=" * 72)
    print()
    print("Entry B -- new row inserted immediately after Entry A:")
    print("=" * 72)
    print(ROW_B.rstrip("\n"))
    print("=" * 72)
    print("No version bump -- one existing-item update + one new open item.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    MOB_FILE.write_text(text, encoding="utf-8")
    print(f"\nWROTE {MOB_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
