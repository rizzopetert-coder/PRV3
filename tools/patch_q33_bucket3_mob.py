"""
PRV3 MOB Update -- Q33/SEVER-19 fix closure (commit 5bd5ea3)

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    "16 category (b) states remain" tail with the Q33 fix summary,
    running total 41/85, and the corrected 15-state remaining count.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.121 -> v4.122.

Updates CLAUDE.md:
  - MOB version cross-reference v4.121 -> v4.122.

Usage:
  python tools/patch_q33_bucket3_mob.py --dry-run
  python tools/patch_q33_bucket3_mob.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================================
# tools/_mob.txt -- Section 13b, Priority Queue item 3
# ============================================================================

OLD_TAIL = (
    "OPEN: re-verified directly (not assumed) "
    "that 16 category (b) states now remain zero-trigger -- "
    "dueling_narratives moved out of the pool, fully closed this round. "
    "Each of the 16 needs its own collateral-blast-radius review before "
    "implementation -- proceeding one state at a time, same discipline "
    "as the last four fixes, not batched. 2 category (a) states remain "
    "untouched pending a dedicated Gemini scoping pass."
)

NEW_TAIL = (
    "Fifth Bucket 3 fix CLOSED and committed (commit 5bd5ea3): Q33 "
    "options C/D confirmed as a full-field-identical tie, but unlike "
    "Q14/Q18/Q19, D -- the unselected option -- is the honest severity "
    "pick: D (\"We don't have this infrastructure in place\") describes "
    "total absence, more severe than C's \"Thin -- documentation exists "
    "but isn't actively maintained.\" Flipping D relies on the "
    "already-shipped Bucket 1 tie-break rule (commit 44e85fc) to "
    "reroute all three states wired to Q33 (invisible_influence_"
    "architecture, paper_shield, leadership_continuity_risk) from C to "
    "D -- same mechanism as the Q02 fix, not the simpler no-op pattern "
    "used for Q14/Q18/Q19. Confirmed C/D dimensional_contributions are "
    "provably identical, so the reroute changes zero dimensional/"
    "ranking output for the two externals. New SEVER-19 follow-on built "
    "to the established duration-band style, state_targets scoped to "
    "only invisible_influence_architecture. Closes AUT-IA-01 outright, "
    "reaching its locked Entrenched tier. paper_shield (AUT-PS-01/02/03) "
    "and leadership_continuity_risk (AUT-LC-01/02/03) deliberately "
    "excluded from _SEVERITY_FOLLOW_ON_TARGETS -- both are separate, "
    "already-known/already-tracked items with their own levers "
    "(paper_shield already Bucket-1-closed via Q23/SEVER-05; "
    "leadership_continuity_risk already WIRED_INSUFFICIENT via Q25/"
    "SEVER-07, already in the follow-on table for that), unrelated to "
    "this fix, just sharing Q33. Confirmed all 6 external profile "
    "variants (not just the -01 primaries) are byte-for-byte unchanged "
    "before vs. after, not just absent from the changed-profile diff. "
    "Running Bucket 2/3 total: 41 of the original 85 Entrenched/"
    "Endemic-expected profiles now closed (28 Track A + 2 ALL-FR-01/"
    "ALL-SI-01 + 3 Q02/SEVER-15 + 4 Q18/SEVER-16 + 2 Q14/SEVER-17 + 1 "
    "Q19/SEVER-18 + 1 Q33/SEVER-19). OPEN: re-verified directly (not "
    "assumed) that 15 category (b) states now remain zero-trigger -- "
    "invisible_influence_architecture moved out of the pool, fully "
    "closed this round. Each of the 15 needs its own collateral-"
    "blast-radius review before implementation -- proceeding one state "
    "at a time, same discipline as the last five fixes, not batched. 2 "
    "category (a) states remain untouched pending a dedicated Gemini "
    "scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.121",
    "\\\\\\#\\\\\\# MOB v4.122",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Fifth Bucket 3 fix (Q33/SEVER-19) closed and "
    "committed, commit 5bd5ea3 | Full detail in Section 13b's Priority "
    "Queue item 3. Scanned the 16 remaining category (b) states for "
    "smallest/cleanest blast radius (dueling_narratives now closed, its "
    "prior tie partner stood alone this round): invisible_influence_"
    "architecture won outright at total=2, external=2 via Q33, no tie "
    "this time. Both externals (paper_shield, leadership_continuity_"
    "risk) already well-understood from before. Full workup confirmed "
    "the mechanism concern flagged last round was real: Q33's tied pair "
    "(C/D) has C already winning, but D -- the unselected option -- is "
    "the honest severity pick (\"We don't have this infrastructure in "
    "place\" reads as more severe than C's \"Thin, exists but not "
    "maintained\"), meaning this fix needed the Q02/Q09-style tie-break "
    "reroute rather than a true no-op flip. Verified directly rather "
    "than assumed safe: confirmed C and D's dimensional_contributions "
    "are provably identical (Python equality check), so rerouting "
    "paper_shield and leadership_continuity_risk from C to D changes "
    "zero dimensional/ranking output for either -- only the internal "
    "trigger flag and answer label change, and since neither is added "
    "to _SEVERITY_FOLLOW_ON_TARGETS for SEVER-19, neither gets any "
    "severity contribution from it either. Implemented: flipped D's "
    "severity_trigger to True, added new SEVER-19 (\"How long has this "
    "infrastructure been missing?\", duration_band up to 18mo_plus, "
    "state_targets scoped to only [invisible_influence_architecture]), "
    "extended _SEVERITY_FOLLOW_ON_TARGETS for AUT-IA-01 only. Full "
    "172-profile byte-for-byte regression: exactly 1 profile changed "
    "(AUT-IA-01), nothing else moved -- explicitly confirmed all 6 "
    "external profile variants (AUT-PS-01/02/03, AUT-LC-01/02/03, not "
    "just the -01 primaries) are byte-for-byte identical before vs. "
    "after, 169/172 baseline confirmed unchanged, same 3 pre-existing "
    "gaps. AUT-IA-01 (Entrenched-expected) reaches its locked tier via "
    "normalized severity score 33.33 (single trigger's raw 2.00). All 5 "
    "Python test suites re-run clean (severity 56/56, output 112/112, "
    "accumulation 47/47, output_synthesis 53/53, main 36/36). "
    "Re-verified the remaining category (b) pool directly post-fix: 15 "
    "states now remain genuinely zero-trigger, down from 16. Committed "
    "as engine/data/questions.py, tools/calibration_runner.py, "
    "tools/patch_q33_sever19.py, tools/patch_q33_severity_targets.py "
    "(commit 5bd5ea3). Running Bucket 2/3 total: 41 of the original 85 "
    "Entrenched/Endemic-expected profiles now closed. MOB version "
    "bumped v4.121 → v4.122 per standing protocol -- fifth Bucket 3 fix "
    "shipped, remaining pool re-verified precisely at 15 states. | This "
    "session (Claude Code) | MOB v4.122 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.121 |",
    "| This session (Claude Code) | MOB v4.121 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.121 |",
    "| MOB version | v4.122 |",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    by_file: dict[str, list[tuple[str, str]]] = {}
    for path, old, new in EDITS:
        by_file.setdefault(path, []).append((old, new))

    for rel_path, pairs in by_file.items():
        full_path = REPO_ROOT / rel_path
        content = full_path.read_text(encoding="utf-8")
        for old, new in pairs:
            count = content.count(old)
            if count != 1:
                print(f"ABORT: {rel_path}: expected exactly 1 match for anchor, found {count}")
                print(f"  anchor (first 120 chars): {old[:120]!r}")
                sys.exit(1)
            content = content.replace(old, new, 1)

        if args.dry_run:
            print(f"=== {rel_path}: {len(pairs)} edit(s) would apply cleanly ===")
        else:
            full_path.write_text(content, encoding="utf-8")
            print(f"=== {rel_path}: {len(pairs)} edit(s) written ===")

    if args.dry_run:
        print("\nDry run complete. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
