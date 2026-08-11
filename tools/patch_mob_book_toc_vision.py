"""
PRV3 -- MOB update: /book/toc fuller vision concept, approved by Pete,
written to prompts/book-toc-fuller-vision.md. Planning artifact only --
no code changes.

Version bump v4.142 -> v4.143: new durable planning doc + Decision
Register row tracking an approved-but-unscoped concept, not a
session-log-only change.

Usage:
  python tools/patch_mob_book_toc_vision.py --dry-run
  python tools/patch_mob_book_toc_vision.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MOB = "tools/_mob.txt"

ANCHOR = (
    "| Q46 topical mismatch -- CLOSED, no action needed | 3 | **Closed -- resolved by decision, not deferred** | N/A | Originally flagged during Structure 3's Gemini review: Q46 (the_arbitrary_standard) shares no topical continuity with Q44/Q45 (the_tolerated_violation), so chaining it under Q45 was explicitly declined -- Q46 left standalone, untouched, in the A5 + Structure 3 combined recalibration (Section 13a above). That row's own close-out carried the mismatch forward as a separate open item (\"remains a separate, real, unresolved content item... flagged for whenever Pete schedules that work\"). Pete's call this session: the flag only ever mattered in the context of whether to chain Q46 under Q45 -- since that chaining was already declined, not left pending, there is no remaining code or content issue to schedule. Q46 stays a standalone core question permanently, confirmed as the intended design, not a gap. | This session (Claude Code) | Closed -- no further check-in |"
)

NEW_ROW = (
    '\n'
    '| /book/toc fuller vision -- concept approved, not yet scoped for build | 3 | **Approved concept -- awaiting build scoping pass** | primary_dimension frontend-availability check (web/data/taxonomy.ts vs. engine-only) not yet done; actual build scoping (phased plan, file list, Gemini gate determination) not started | prompts/book-toc-fuller-vision.md written -- a durable planning artifact, no code changes. Direction, approved by Pete: /book/toc (currently a minimal flat-list hub, Category C this session) moves to a filterable grid. Two color-coded tag families for filtering, both existing data fields -- primary_dimension (the 4 A\'s) and signature groupings (e.g. culture_erosion\'s 14+ states) -- multi-select OR within a family, AND across families, extending the locked visual identity palette (rust stays reserved for Endemic severity only, not reused for dimension tags). Media links reuse web/lib/book-state-index.ts (built this session, Category C) unchanged -- /book piece links buildable now, citation links explicitly blocked on the still-deferred citation-sourcing workstream without blocking the rest of the build. resolution_family (existing field, already indicates the resolving service track) approved as the connective mechanism between taxonomy browsing and services -- each state card gets a resolution_family badge linking to the relevant service page. Explicitly deferred, not part of this build: a richer state-interconnection graph/visualization -- no existing data foundation supports it the way tags and resolution_family already do, would need its own separate design and scoping pass. | This session (Claude Code) | Pete\'s call -- reopen for the build scoping pass whenever ready, starting with the primary_dimension frontend-availability check |\n'
)


def apply(dry_run: bool) -> int:
    changed = 0
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count != 1:
        print(f"ERROR: {MOB} -- expected 1 match for anchor, found {count}")
        return 1
    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROW, 1)
    if dry_run:
        print(f"OK (dry-run): {MOB} -- anchor found, would insert 1 new row")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"WRITTEN: {MOB} -- 1 new row inserted")
    changed += 1

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.142", "\\\\\\#\\\\\\# MOB v4.143"),
        ("CLAUDE.md", "| MOB version | v4.142 |", "| MOB version | v4.143 |"),
    ]
    for rel_path, old, new in version_edits:
        p = REPO_ROOT / rel_path
        t = p.read_text(encoding="utf-8")
        c = t.count(old)
        if c != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {c}")
            return 1
        nt = t.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            p.write_text(nt, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1

    print(f"\n{changed}/3 edits {'validated' if dry_run else 'applied'}.")
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
