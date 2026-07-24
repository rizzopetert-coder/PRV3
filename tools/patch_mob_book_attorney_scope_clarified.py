#!/usr/bin/env python
"""
PRV3 -- patch_mob_book_attorney_scope_clarified.py
Section 13a: /book publish-decision row -- Pete has explicitly confirmed
/book content was never in scope for attorney review. That gate covers only
the LinkedIn campaign and the coaching engagement template (see the
separate "Attorney review (LinkedIn + coaching template gate)" row). Adds
this clarification to the /book row so it isn't rediscovered as an open
scope question later.

Version bump v4.63 -> v4.64 -- Decision Register scope clarification is a
material status change, not a session-log-only edit, per the closeout
protocol's version-increment rule.

Usage:
  python tools/patch_mob_book_attorney_scope_clarified.py --dry-run
  python tools/patch_mob_book_attorney_scope_clarified.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "tools" / "_mob.txt"

CHANGES = []


def edit(label, old, new):
    CHANGES.append((label, old, new))


edit(
    "MOB version v4.63 -> v4.64",
    "\\\\\\#\\\\\\# MOB v4.63",
    "\\\\\\#\\\\\\# MOB v4.64",
)

OLD_ROW = "| /book publish decision (88 drafted pieces, corrected from earlier 50/71 progression-snapshot figures) | 3 | Deferred | No decision made -- not blocked externally. This session's readiness sweep (Claude Code): nav link confirmed live on every route (mounted once in root layout, single non-responsive markup shared by desktop/mobile); manifest/content cross-reference clean (88 manifest entries, 88 content files, zero missing, zero orphans); citation-free compliance re-verified by direct read of all 36 FTA-18-FTA-53 pieces (Session 57 finding holds, zero external claims without citation, the-unexamined-algorithm's real citations confirmed still attached); shadow-model sweep clean (zero hits for Pete's name or OneDigital across all 88 files). Two gaps found that block real discoverability regardless of this decision: (1) all 88 entries are `status: draft` or `parked`, zero `published` -- both the index page and the `[type]/[slug]` page gate strictly on `published`, so `/book` currently renders 'Coming soon.' live, confirmed by fetching it; (2) the `[type]/[slug]` page never renders the markdown body, only title+teaser -- a code comment describes this as deferred to a 'content migration pass' that appears not to have happened. Neither gap is a defect introduced this session -- both pre-exist, newly surfaced by this sweep | This session (Claude Code) | Session 72 -- and whenever Pete is ready to decide, the two gaps above need scoping alongside the publish decision itself, not discovered again after |"

NEW_ROW = "| /book publish decision (88 drafted pieces, corrected from earlier 50/71 progression-snapshot figures) | 3 | Deferred | No decision made -- not blocked externally. Attorney-review scope CONFIRMED and CLOSED as a question (Pete, direct): /book content was never in scope for attorney review -- that gate covers only the LinkedIn campaign and the coaching engagement template (see the separate \"Attorney review (LinkedIn + coaching template gate)\" row below), not /book publication. Prior session's readiness sweep (Claude Code) still holds: nav link confirmed live on every route (mounted once in root layout, single non-responsive markup shared by desktop/mobile); manifest/content cross-reference clean (88 manifest entries, 88 content files, zero missing, zero orphans); citation-free compliance re-verified by direct read of all 36 FTA-18-FTA-53 pieces (Session 57 finding holds, zero external claims without citation, the-unexamined-algorithm's real citations confirmed still attached); shadow-model sweep clean (zero hits for Pete's name or OneDigital across all 88 files). Two gaps found that block real discoverability regardless of this decision: (1) all 88 entries are `status: draft` or `parked`, zero `published` -- both the index page and the `[type]/[slug]` page gate strictly on `published`, so `/book` currently renders 'Coming soon.' live, confirmed by fetching it; (2) the `[type]/[slug]` page never renders the markdown body, only title+teaser -- a code comment describes this as deferred to a 'content migration pass' that appears not to have happened. Neither gap is a defect from any one session -- both pre-exist, surfaced by the readiness sweep | This session (Claude Code) | Whenever Pete is ready to decide -- no attorney-review dependency anymore. The two content-rendering/publish-status gaps above need scoping alongside the publish decision itself, not discovered again after |"

edit("Section 13a: /book row -- attorney-review scope confirmed not applicable", OLD_ROW, NEW_ROW)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    if not TARGET.exists():
        print(f"ERROR: target not found: {TARGET}")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8")

    if args.dry_run:
        print(f"DRY RUN -- target: {TARGET}")
        print(f"  {len(CHANGES)} change(s) to apply:")
        all_ok = True
        for label, old, new in CHANGES:
            count = text.count(old)
            status = f"OK ({count}x)" if count == 1 else ("MISS" if count == 0 else f"AMBIGUOUS ({count}x)")
            if count != 1:
                all_ok = False
            print(f"  [{status}] {label}")
        if not all_ok:
            print("\n  ERROR: one or more OLD strings not found exactly once in target.")
            sys.exit(1)
        print("\n  All anchors matched exactly once. Ready for --write.")
        return

    for label, old, new in CHANGES:
        count = text.count(old)
        if count != 1:
            print(f"ERROR: OLD string for '{label}' matched {count} times (expected 1) -- aborting.")
            sys.exit(1)

    new_text = text
    for label, old, new in CHANGES:
        new_text = new_text.replace(old, new, 1)

    if new_text == text:
        print("ERROR: no changes produced.")
        sys.exit(1)

    TARGET.write_text(new_text, encoding="utf-8")
    print(f"WRITTEN: {TARGET}")
    print(f"  {len(CHANGES)} change(s) applied")


if __name__ == "__main__":
    main()
