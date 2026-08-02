"""
PRV3 -- Decision Register addition: Legal/Compliance channel -- actuarial
tail-risk distinction. New row only, inserted immediately after the
"Calibration Set 3 (STATE_MULTIPLIERS) -- Scoring Complete" row
(tools/_mob.txt Section 13a). Does not modify that row or either of the
"Multi-state compounding mechanism for Friction Tax" rows.

Pete's four supplied fields (Item, Status, Context, Sequencing, Next
check-in) mapped onto the Decision Register's real 6-column convention
(Item, Tier, Status, Detail, Last touched, Next check-in): Context and
Sequencing folded into one Detail cell (matching how every other row in
this table combines multiple sub-points into a single narrative Detail
column), Tier set to 3 (consistent with every other row), Last touched
filled with "This session (Claude Code)" per standing convention. Plain
hyphen dash-separators in Pete's supplied text converted to "--" to
match this file's own established internal convention (every other row
in this session's writes uses "--", not em-dashes or single hyphens, as
a clause separator).

Documentation-only, no version bump -- new open item, not a locked
decision, no rule change, no material workstream status change.

Usage:
  python tools/patch_mob_legal_tail_risk_register.py --dry-run
  python tools/patch_mob_legal_tail_risk_register.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

ANCHOR = (
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

NEW_ROW = (
    "| Legal/Compliance channel -- actuarial tail-risk distinction | 3 | "
    "Open -- flagged, not scoped, queued behind the multi-state "
    "compounding redesign | Raised during an actuarial-framing review "
    "of the Friction Tax scoring methodology. Turnover, Productivity, "
    "and Decision-Quality behave as attritional risk -- steady, "
    "expected, frequency-driven costs, well-suited to proportional "
    "blending on a shared 0-2 scale. Legal/Compliance behaves more like "
    "a tail/catastrophic peril -- rare, but severe when realized -- and "
    "is not well-modeled by the same proportional blending used for the "
    "other three channels. Standard actuarial practice prices these two "
    "risk types with different methods (expected-value pricing for "
    "attritional, separate large-loss loading for tail risk) rather "
    "than folding both into one blended severity score. Current Set 3 "
    "rubric scores Legal on the same 0-2 scale as the other three and "
    "sums it into the same raw total -- this may understate the "
    "\"beyond question\" credibility bar for that specific channel. "
    "Sequencing: explicitly queued behind the multi-state compounding "
    "mechanism (state-count/Factor A/Factor B) -- do not start design "
    "work on this until that item is resolved and reopened by Pete | "
    "This session (Claude Code) | Pete's call -- reopen after "
    "multi-state compounding design is finalized |\n"
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

    print("New Decision Register row (Section 13a), inserted immediately")
    print("after the 'Calibration Set 3 (STATE_MULTIPLIERS) -- Scoring")
    print("Complete' row. No existing row modified:")
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
