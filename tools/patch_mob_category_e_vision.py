"""
PRV3 -- MOB update: Category E (visual identity refresh) concept sketch,
approved direction and sequencing by Pete, written to
prompts/category-e-visual-identity-refresh.md. Planning artifact only --
no code changes. Gemini architecture review required before Direction 1
build starts (structural/rendering-system decision touching OD-07's
shipped token infrastructure), not done yet.

Version bump v4.143 -> v4.144: new durable planning doc + Decision
Register row tracking an approved-but-unreviewed concept, not a
session-log-only change.

Usage:
  python tools/patch_mob_category_e_vision.py --dry-run
  python tools/patch_mob_category_e_vision.py --write
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
    "| /book/toc fuller vision -- concept approved, not yet scoped for build | 3 | **Approved concept -- awaiting build scoping pass** | primary_dimension frontend-availability check (web/data/taxonomy.ts vs. engine-only) not yet done; actual build scoping (phased plan, file list, Gemini gate determination) not started | prompts/book-toc-fuller-vision.md written -- a durable planning artifact, no code changes. Direction, approved by Pete: /book/toc (currently a minimal flat-list hub, Category C this session) moves to a filterable grid. Two color-coded tag families for filtering, both existing data fields -- primary_dimension (the 4 A's) and signature groupings (e.g. culture_erosion's 14+ states) -- multi-select OR within a family, AND across families, extending the locked visual identity palette (rust stays reserved for Endemic severity only, not reused for dimension tags). Media links reuse web/lib/book-state-index.ts (built this session, Category C) unchanged -- /book piece links buildable now, citation links explicitly blocked on the still-deferred citation-sourcing workstream without blocking the rest of the build. resolution_family (existing field, already indicates the resolving service track) approved as the connective mechanism between taxonomy browsing and services -- each state card gets a resolution_family badge linking to the relevant service page. Explicitly deferred, not part of this build: a richer state-interconnection graph/visualization -- no existing data foundation supports it the way tags and resolution_family already do, would need its own separate design and scoping pass. | This session (Claude Code) | Pete's call -- reopen for the build scoping pass whenever ready, starting with the primary_dimension frontend-availability check |"
)

NEW_ROW = (
    '\n'
    '| Category E (visual identity refresh) -- concept + sequencing approved, Gemini review required before build | 3 | **Approved direction -- Gemini architecture review required before Direction 1 build starts, not done yet** | Gemini architecture review of Direction 1 (structural/rendering-system decision touching OD-07\'s shipped token infrastructure -- globals.css tokens, ThemeSwitcher.tsx) has not happened. No code changes until it clears | prompts/category-e-visual-identity-refresh.md written -- a durable planning artifact, no code changes. Context: session opened on Pete\'s critique that the site "looks sterile," specifically the existing 4-axis quadrilateral (OD-07\'s ConstellationField) reading as "cheap and rudimentary." Governing constraint, explicit: the fix is craft-execution quality within the existing locked 3-color discipline (Principal Brief\'s Saint-Exupery restraint principle + the "magnanimous but unflinching" Core Reframe), not new decoration on top of it -- rust stays reserved for Endemic severity only, unchanged. Sequencing approved by Pete: Direction 1 (rendering-quality upgrade -- soft radial gradients, severity-scaled vertex glow, layering/depth, plus upgraded recede/resolve motion to spring physics/layered timing, reactivating OD-07\'s dormant infrastructure rather than building from zero) starts first as the lowest-risk test of whether "cheap-looking" is a craft problem (most likely) or a concept problem. Directions 2 (four-dial instrument-panel reframe, one gauge per Aptitude/Authority/Alliance/Attitude) and 3 (editorial/typographic hero, de-emphasizing the geometric shape entirely in favor of bold typography per the Output Precision principle) stay concept-level, explored only after Direction 1\'s result is seen -- Pete\'s own sequencing call, not a technical dependency. No visual mockups exist yet for any direction. | This session (Claude Code) | Pete\'s call -- reopen once ready to send Direction 1 to Gemini for architecture review; no code changes before that clears |\n'
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
        (MOB, "\\\\\\#\\\\\\# MOB v4.143", "\\\\\\#\\\\\\# MOB v4.144"),
        ("CLAUDE.md", "| MOB version | v4.143 |", "| MOB version | v4.144 |"),
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
