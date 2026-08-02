"""
PRV3 -- New Decision Register row (Section 13a): MemPalace mine --
silent non-persistence, confirmed recurring. Inserted as the new last
row of 13a, immediately before Section 13b's header (after the
Legal/Compliance tail-risk row, currently 13a's last row).

Session 70 reference verified directly against the live file before
writing this row's Detail text, not assumed from memory: Section 13's
general Open Items list (a separate, older 2-column table, not the
Decision Register) carries the exact row "MemPalace mine -- Session 70
run did not persist," with specifics (413 files, prv3 wing, 5 rooms
scanned; 8775 drawers before/after, unchanged; direct search for that
session's new content -- patch_weak_damped_routing_s70 -- returned
nothing). Cited by that exact description in this new row's Detail
field rather than paraphrased.

Documentation-only, no version bump -- new open item, not a locked
decision, no rule change, no material workstream status change.

Usage:
  python tools/patch_mob_mempalace_mine_register.py --dry-run
  python tools/patch_mob_mempalace_mine_register.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

ANCHOR = (
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

NEW_ROW = (
    "| MemPalace mine -- silent non-persistence, confirmed recurring | "
    "3 | Open -- confirmed twice, root cause unknown | mempalace mine "
    "ran without error but did not persist new drawers, verified by "
    "direct search rather than assumed from exit status. First "
    "observed Session 70 (Section 13's general Open Items list, not "
    "this register: \"MemPalace mine -- Session 70 run did not "
    "persist\" -- 413 files scanned, prv3 wing, 5 rooms, but drawer "
    "count unchanged at 8775 before/after, and a direct search for "
    "that session's new content, patch_weak_damped_routing_s70, "
    "returned nothing). Second confirmed instance this session (August "
    "2, 2026), immediately following the Set 3/compounding closeout "
    "Diary Write -- verified by search per standing \"verify, don't "
    "assume\" practice, not just trusted. Elevated from a general "
    "Priority Queue housekeeping line (Section 13b, item 7) to its own "
    "row because two confirmed instances make this a repeatable gap, "
    "not a one-off flake, and it specifically undermines MemPalace's "
    "value as a cross-session searchable record -- the exact retrieval "
    "path that was needed and came up empty earlier this session. "
    "**Impact if unresolved:** this session's full work (Set 3 "
    "closure, compounding design, governance cadence repair) has no "
    "MemPalace-searchable trace despite a successful Diary Write -- "
    "durable record currently exists only in tools/_mob.txt and git "
    "history, not in MemPalace | This session (Claude Code) -- "
    "confirmed, not fixed | Pete's call -- not urgent tonight, but "
    "should not silently persist across many more sessions unexamined "
    "given confirmed recurrence. Related follow-up (not urgent, logged "
    "for future reference): worth a deliberate comparison of "
    "MemPalace's actual feature set and reliability against "
    "open-source alternatives (e.g. mcp-memory-service/doobidoo -- "
    "SQLite-based, no embeddings, positioned for reliability via "
    "simplicity; Cognee -- graph+vector, native Claude Code plugin, "
    "more complete but more moving parts; mem0 self-hosted; "
    "Graphiti/Neo4j-backed options for more complex needs) before "
    "deciding whether to keep, fix, or replace MemPalace. Not a "
    "recommendation to switch -- a note that this comparison hasn't "
    "been done and should happen before any replacement decision, "
    "given the specific failure mode here is silent non-persistence on "
    "writes that report success, which argues for weighing "
    "simplicity/reliability as its own axis, not just feature "
    "completeness |\n"
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

    print("New Decision Register row (Section 13a), inserted as the new")
    print("last row -- immediately before Section 13b's header:")
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
