"""
PRV3 -- MOB v4.129 -> v4.130: close out both validate.py failures flagged
in the 2026-08-08 session-log catch-up entry.

Item 1 (baseline-vector check): FIXED, commit 5f66e07. Independently
re-verified before the fix (grep-confirmed all 58 states carry an
explicit dimensional_vector override; runtime-confirmed 0/58 fully
baseline) -- not taken on faith from the investigation that proposed it.

Item 2 (cluster_id gap): explained-and-logged, not fixed -- new Section
13a Decision Register row. Independently re-verified beyond the
investigation's originally-scoped 5 files: grepped the full engine/,
web/, and tools/ trees, confirming StateProfile.cluster_id and
.signal_weight have zero live scoring consumers anywhere. Also found
and logged a distinction the original investigation's scope missed:
the separate module-level CLUSTERS dict (only C-Manager/C-Culture
populated) IS live, consumed by engine/checkpoint.py's Q11
distinguisher-question selection -- a different mechanism from the
per-state cluster_id field this finding is about, noted in the new row
so the two aren't conflated later.

Three edits:
  1. tools/_mob.txt Section 13a -- new Decision Register row.
  2. tools/_mob.txt Section 16 -- update the dangling "left open,
     flagged for a future dedicated session" line to reflect
     resolution (Pete's explicit instruction: not left dangling).
  3. tools/_mob.txt + CLAUDE.md -- version bump v4.129 -> v4.130
     (new Decision Register row + a corrected stale check both
     warrant one per standing protocol).

Usage:
  python tools/patch_mob_validate_checks_closeout.py --dry-run
  python tools/patch_mob_validate_checks_closeout.py --write
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
CLAUDE = "CLAUDE.md"

# ---------------------------------------------------------------------
# 1. New Decision Register row (Section 13a), appended after the
#    Mechanism 1 row (the last row in the table).
# ---------------------------------------------------------------------

NEW_ROW = (
    "| cluster_id gap -- explained and logged, not fixed | 3 | Informational, no forced check-in | "
    "5 states (the_suppression_filter, what_nobody_says, leadership_deafness, the_unreported_hazard, "
    "the_unlocked_door) carry signal_weight='cluster' with cluster_id=None; CLUSTER_IDS declares "
    "C-Silence and C-InfoFlow but CLUSTERS has no entries for either. Confirmed inert -- cluster_id "
    "and signal_weight (the per-state StateProfile fields) have zero downstream scoring consumers "
    "anywhere in the repo, grep-verified across the full engine/, web/, and tools/ trees (not just "
    "the originally-scoped 5 files from the investigation that surfaced this) -- the only other hit "
    "for either term outside states.py/validate.py is a comment in engine/data/salience.py and a "
    "docstring in engine/test_profiles_expansion.py, neither live code. signal_weight's only live use "
    "is as a one-time construction-time seed hint in states.py's own _profile() helper, overwritten "
    "by every state's real calibrated vector (confirmed directly in _profile()'s own code). "
    "Distinct from this: the separate module-level CLUSTERS dict (only C-Manager/C-Culture populated) "
    "is genuinely live, consumed by engine/checkpoint.py's dominant_cluster() and "
    "select_distinguisher_questions() for Q11 distinguisher-question selection -- not the same "
    "mechanism as the per-state cluster_id field this row is about, noted here so the two aren't "
    "conflated later. Cluster assignment (C-Silence vs. C-InfoFlow vs. new grouping) is Pete's "
    "content/taxonomy call, not scheduled. Closes former validate.py failure #2 as explained, not "
    "fixed. | This session (Claude Code) | No forced check-in -- informational, revisit only if Pete "
    "schedules the cluster-assignment content work |\n"
)

edit(
    MOB,
    "| Mechanism 1 (Prior Probability Adjusters) — deprecated, RESOLVED across 3 phases | 3 | **RESOLVED**",
    NEW_ROW.rstrip("\n") + "\n"
    "| Mechanism 1 (Prior Probability Adjusters) — deprecated, RESOLVED across 3 phases | 3 | **RESOLVED**",
)

# ---------------------------------------------------------------------
# 2. Section 16 -- update the dangling "left open" line to reflect
#    resolution, per Pete's explicit instruction not to leave it as
#    dangling historical text.
# ---------------------------------------------------------------------

edit(
    MOB,
    "Two unrelated validate.py failures (baseline-vector check, 5-state cluster_id gap) left open, "
    "flagged for a future dedicated session.",
    "Two unrelated validate.py failures (baseline-vector check, 5-state cluster_id gap) left open, "
    "flagged for a future dedicated session. **RESOLVED, same-day follow-up (commit 5f66e07, MOB "
    "v4.130):** both independently re-verified before any change, not taken on faith. Baseline-vector "
    "check FIXED -- flipped from asserting all 58 states remain fully at BASELINE_VALUE (a "
    "pre-calibration invariant that can never pass again; grep-confirmed all 58 carry an explicit "
    "dimensional_vector override, runtime-confirmed 0/58 fully baseline) to asserting none do, "
    "catching a future state added without a real calibration override. cluster_id gap "
    "explained-and-logged, not fixed -- new Section 13a Decision Register row, confirming zero live "
    "scoring consumers for the per-state cluster_id/signal_weight fields across the full repo (wider "
    "than the investigation's original 5-file scope), and distinguishing this dead field from the "
    "separate, genuinely-live CLUSTERS dict consumed by engine/checkpoint.py's Q11 distinguisher "
    "selection. validate.py now 40/41 (up from 39/41; the one remaining failure is the cluster_id row "
    "itself, expected -- log-only, not a code fix). Full 172(+3)-profile regression reconfirmed at "
    "170/175, 58/58 HC, zero movement.",
)

# ---------------------------------------------------------------------
# 3. Version bump, both files.
# ---------------------------------------------------------------------

edit(MOB, "\\\\\\#\\\\\\# MOB v4.129", "\\\\\\#\\\\\\# MOB v4.130")
edit(CLAUDE, "| MOB version | v4.129 |", "| MOB version | v4.130 |")


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
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
