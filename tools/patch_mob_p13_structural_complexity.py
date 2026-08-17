"""
PRV3 -- MOB update: new locked governing principle, P-13, Section 2.

Pete's direct instruction, not a draft: taxonomy or structural
complexity presented without context reads as AI-generated gimmickry to
a visitor, not rigor, and damages trust rather than building it. Any
complex/structured content (filter chips, taxonomy displays, dimension
labels, etc.) needs a "how to read this" affordance or framing copy
before or alongside it, not after.

Source, Pete's own words this session: "It cannot be overstated how
turned off our clients will be if they explore this AI-generated site
and only see a gimmicky taxonomy without context. The taxonomy may be
the least important detail."

Cross-referenced as the first two applications, both already shipped
before this principle was formally locked: the ConstellationField
gestalt-interpretability addendum (Category E) and the /book/toc
Gestalt Pass's Terminology Guide -- both independently built the same
"what do these terms mean" affordance shape.

Two edits: (1) terse P-13 row added to the main Section 2 table,
matching the P-01..P-12 house style; (2) a fuller explanatory paragraph
with the source quote and cross-references, placed after the existing
"Provisional Hold vs. Lock (Session 56)" note, matching that note's own
established format for principle elaboration beyond the terse table row.

Version bump v4.180 -> v4.181: a new locked governing principle is a
material change, not a session-log-only update.

Usage:
  python tools/patch_mob_p13_structural_complexity.py --dry-run
  python tools/patch_mob_p13_structural_complexity.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB = "tools/_mob.txt"
CLAUDE = "CLAUDE.md"

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================================
# 1. New P-13 row in the main Section 2 table
# ============================================================================

edit(
    MOB,
    "| \\\\\\*\\\\\\*P-12\\\\\\*\\\\\\* | Scope discipline. Every addition answers: who does this serve and how? |\n",
    "| \\\\\\*\\\\\\*P-12\\\\\\*\\\\\\* | Scope discipline. Every addition answers: who does this serve and how? |\n"
    "\n"
    "  \n"
    "\n"
    "| \\\\\\*\\\\\\*P-13\\\\\\*\\\\\\* | Structural complexity needs a \"how to read this\" affordance before or alongside it, not after -- unexplained taxonomy reads as gimmick, not rigor. |\n",
)


# ============================================================================
# 2. Explanatory paragraph -- source quote and first two applications
# ============================================================================

edit(
    MOB,
    "**Provisional Hold vs. Lock (Session 56):** Before a decision is recorded as Locked in the MOB, confirm whether any open async research threads could invalidate this constraint. If yes, the decision is a Provisional Hold until that thread closes. Provisional Holds are documented in the session log but not listed as Locked Decisions. When the thread closes, the hold converts to a Lock or the decision is revised. Example: displacement-pattern essay count was not locked during the research-refresh automation build because the de Waal verification thread was still open.\n",
    "**Provisional Hold vs. Lock (Session 56):** Before a decision is recorded as Locked in the MOB, confirm whether any open async research threads could invalidate this constraint. If yes, the decision is a Provisional Hold until that thread closes. Provisional Holds are documented in the session log but not listed as Locked Decisions. When the thread closes, the hold converts to a Lock or the decision is revised. Example: displacement-pattern essay count was not locked during the research-refresh automation build because the de Waal verification thread was still open.\n"
    "\n"
    "  \n"
    "\n"
    "**P-13, source and first applications (confirmed 2026-08-16):** Pete's own framing this session: \"It cannot be overstated how turned off our clients will be if they explore this AI-generated site and only see a gimmicky taxonomy without context. The taxonomy may be the least important detail.\" First two applications, both shipped before this principle was formally locked, retroactively named as the pattern's own precedent: the ConstellationField gestalt-interpretability addendum (Category E) and the /book/toc Gestalt Pass's Terminology Guide -- both independently built the same shape, a \"what do these terms mean\" affordance placed before or alongside the complex structural element itself, not after.\n",
)


# ============================================================================
# 3. Version bump
# ============================================================================

edit(MOB, "\\\\\\#\\\\\\# MOB v4.180", "\\\\\\#\\\\\\# MOB v4.181")
edit(CLAUDE, "| MOB version | v4.180 |", "| MOB version | v4.181 |")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    contents: dict[str, str] = {}
    for path, _, _ in EDITS:
        if path not in contents:
            contents[path] = (REPO_ROOT / path).read_text(encoding="utf-8")

    for i, (path, old, new) in enumerate(EDITS, 1):
        count = contents[path].count(old)
        if count != 1:
            print(f"ABORT: edit #{i} ({path}): expected exactly 1 match, found {count}")
            print(f"  anchor (first 150 chars): {old[:150]!r}")
            sys.exit(1)
        contents[path] = contents[path].replace(old, new, 1)

    if args.dry_run:
        print(f"=== {len(EDITS)} edit(s) across {len(contents)} file(s) would apply cleanly ===")
        print("\nDry run complete. Re-run with --write to apply.")
    else:
        for path, content in contents.items():
            (REPO_ROOT / path).write_text(content, encoding="utf-8")
        print(f"=== {len(EDITS)} edit(s) written across {len(contents)} file(s) ===")


if __name__ == "__main__":
    main()
