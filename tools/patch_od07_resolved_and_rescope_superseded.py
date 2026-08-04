"""
PRV3 -- Close out the OD-07 discrepancy flag now that the rollback is
committed (b8860b5), and mark the /diagnostic reskin Stages 4-5 rescope
doc as superseded rather than completed -- the reskin direction
reversed (OD-07 rolled back to v1), so there is nothing left to extend
outward in Stages 4/5 as originally conceived.

Usage:
  python tools/patch_od07_resolved_and_rescope_superseded.py --dry-run
  python tools/patch_od07_resolved_and_rescope_superseded.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.93",
    "\\\\\\#\\\\\\# MOB v4.94",
)

edit(
    "tools/_mob.txt",
    '| OD-07 — Visual concept for the methodology (Topology vs. Constellation) — CLOSED (design decision), but see DISCREPANCY flag below | 3 | Closed (the hybrid-model decision itself) -- but this row\'s own "not yet built into the live site" claim is confirmed stale, flagged not resolved |',
    '| OD-07 — Visual concept for the methodology (Topology vs. Constellation) — CLOSED (design decision), discrepancy RESOLVED | 3 | Closed (the hybrid-model decision itself) -- the "not yet built into the live site" discrepancy is resolved: rolled back to locked v1 identity, commit b8860b5 |',
)

edit(
    "tools/_mob.txt",
    "Reopened for awareness only, not action -- Pete's design review of OD-07 live on the three Stage 3 files will determine whether this row needs correcting or whether the live shipping is confirmed intentional and this flag can close |",
    "Resolved -- rolled back to locked v1 identity, commit b8860b5. OD-07 infrastructure (globals.css tokens, ThemeSwitcher.tsx) left in place, dormant, not deleted, in case worth revisiting deliberately later. Not currently consumed anywhere in the live site. |",
)

edit(
    "prompts/diagnostic-reskin-stages-4-5-rescope.md",
    "# /diagnostic Visual Identity Reskin — Stages 4-5 Rescope\n\n**Status:**",
    "# /diagnostic Visual Identity Reskin — Stages 4-5 Rescope\n\n"
    "**SUPERSEDED (2026-08-03):** The reskin direction reversed after this session's design "
    "review of OD-07 live on the three Stage 3 files. Stages 4/5 as originally conceived below "
    "-- extending v2/OD-07 tokens outward to the rest of the site -- no longer apply: OD-07 was "
    "rolled back to v1 across all four files that had it (commit b8860b5), so there is nothing "
    "left to extend. The files listed below as still needing the v2 rename (NavBar, "
    "AssemblyPanel, SignatureCard, StateDrawer, ShareButton, ShareableOutput, /about, /ask, "
    "/book, /share) were already correct on v1 and do not need touching. This plan is "
    "superseded, not completed -- do not pick Stage 4 back up as the next step.\n\n"
    "**Status:**",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
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
