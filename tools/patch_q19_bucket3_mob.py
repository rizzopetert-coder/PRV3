"""
PRV3 MOB Update -- Q19/SEVER-18 fix closure (commit 3030de1)

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    "17 category (b) states remain" tail with the Q19 fix summary,
    running total 40/85, and the corrected 16-state remaining count.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.120 -> v4.121.

Updates CLAUDE.md:
  - MOB version cross-reference v4.120 -> v4.121.

Usage:
  python tools/patch_q19_bucket3_mob.py --dry-run
  python tools/patch_q19_bucket3_mob.py --write
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
    "that 17 category (b) states now remain zero-trigger -- "
    "compression_crisis and pay_exposure both moved out of the pool, "
    "fully closed this round. Each of the 17 needs its own "
    "collateral-blast-radius review before implementation -- proceeding "
    "one state at a time, same discipline as the last three fixes, not "
    "batched. 2 category (a) states remain untouched pending a dedicated "
    "Gemini scoping pass."
)

NEW_TAIL = (
    "Fourth Bucket 3 fix CLOSED and committed (commit 3030de1): Q19 "
    "options C/D confirmed as a full-field-identical tie, and like "
    "Q14/Q18, C already won outright via plain max() for all three "
    "states wired to Q19 -- no tie-break mechanism needed, a direct "
    "flip of the already-selected option. C (\"There's a meaningful gap "
    "-- our external narrative is ahead of our internal reality\") is an "
    "acknowledged, admitted problem, read as more severe than D's "
    "unassessed \"I don't think we've really looked at whether they "
    "align\" -- honest pick, not fabricated. New SEVER-18 follow-on "
    "built to the established duration-band style, state_targets scoped "
    "to only dueling_narratives. Closes AUT-DN-01 outright, reaching its "
    "locked Entrenched tier -- no short-landing profile this round, "
    "same clean shape as the Q14 fix. the_pay_fog's AUT-PF-01 and "
    "the_policy_lag's AUT-PL-01 deliberately excluded from "
    "_SEVERITY_FOLLOW_ON_TARGETS -- both are separate, already-known/"
    "already-tracked items with their own levers (the_pay_fog via Q16/"
    "SEVER-01; the_policy_lag's AUT-PL-01 already correctly Entrenched "
    "via a pre-existing SEVER-04 trigger), unrelated to this fix, just "
    "sharing Q19. Confirmed word-for-word identical Q19 selection and "
    "byte-for-byte identical snapshots for both AUT-PF-01 and AUT-PL-01 "
    "before vs. after, not just their absence from the changed-profile "
    "diff. Running Bucket 2/3 total: 40 of the original 85 Entrenched/"
    "Endemic-expected profiles now closed (28 Track A + 2 ALL-FR-01/"
    "ALL-SI-01 + 3 Q02/SEVER-15 + 4 Q18/SEVER-16 + 2 Q14/SEVER-17 + 1 "
    "Q19/SEVER-18). OPEN: re-verified directly (not assumed) that 16 "
    "category (b) states now remain zero-trigger -- dueling_narratives "
    "moved out of the pool, fully closed this round. Each of the 16 "
    "needs its own collateral-blast-radius review before implementation "
    "-- proceeding one state at a time, same discipline as the last four "
    "fixes, not batched. 2 category (a) states remain untouched pending "
    "a dedicated Gemini scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.120",
    "\\\\\\#\\\\\\# MOB v4.121",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Fourth Bucket 3 fix (Q19/SEVER-18) closed and "
    "committed, commit 3030de1 | Full detail in Section 13b's Priority "
    "Queue item 3. Scanned the 17 remaining category (b) states for "
    "smallest/cleanest blast radius, same external-exposure-first "
    "methodology: dueling_narratives and invisible_influence_"
    "architecture tied cleanest at total=2, external=2 (via Q19 and Q33 "
    "respectively). Both externals in each group were already "
    "well-understood -- the_pay_fog (already investigated, WIRED_"
    "INSUFFICIENT via Q16/SEVER-01) and the_policy_lag (newly checked "
    "this round, AUT-PL-01 already correctly Entrenched via a "
    "pre-existing SEVER-04 trigger unrelated to Q19) for Q19; "
    "paper_shield (already Bucket-1-closed via Q23/SEVER-05) and "
    "leadership_continuity_risk (already known, WIRED_INSUFFICIENT via "
    "Q25/SEVER-07) for Q33. Broke the tie on mechanism simplicity: Q19's "
    "tied pair (C/D) has C already winning AND C's content is the "
    "honest severity pick (true no-op flip, same shape as Q14/Q18); "
    "Q33's tied pair also has C winning, but D -- the unselected option "
    "-- reads as more severe there, meaning Q33 needs the Q02/Q09-style "
    "tie-break reroute instead. Picked Q19 as cleaner, deferred Q33 to "
    "the next round (implemented same session, see below). Full workup "
    "confirmed for Q19: options C/D are a full-field-identical tie "
    "(aptitude_liability 0.25, authority_liability 0.5, attitude_"
    "liability 0.25), all three states already select C outright. C "
    "(\"meaningful gap -- external narrative ahead of internal reality\" "
    "-- acknowledged problem) reads as more severe than D (\"haven't "
    "really looked\" -- unassessed), honest pick, no new option needed. "
    "Implemented: flipped C's severity_trigger to True, added new "
    "SEVER-18 (\"How long has this gap been present?\", duration_band up "
    "to 18mo_plus, state_targets scoped to only [dueling_narratives]), "
    "extended _SEVERITY_FOLLOW_ON_TARGETS for AUT-DN-01 only. Verified "
    "directly that C remains selected for all three states post-flip, "
    "word-for-word identical text for both externals. Full 172-profile "
    "byte-for-byte regression: exactly 1 profile changed (AUT-DN-01), "
    "nothing else moved -- explicitly confirmed AUT-PF-01 and AUT-PL-01 "
    "full snapshot dicts are byte-for-byte identical before vs. after "
    "(not just absent from the diff), 169/172 baseline confirmed "
    "unchanged, same 3 pre-existing gaps. AUT-DN-01 (Entrenched-"
    "expected) reaches its locked tier via normalized severity score "
    "33.33 (single trigger's raw 2.00). All 5 Python test suites "
    "re-run clean (severity 56/56, output 112/112, accumulation 47/47, "
    "output_synthesis 53/53, main 36/36). Note: this fix was implemented "
    "in the prior working session but held uncommitted at end of turn "
    "pending explicit go-ahead per standing protocol -- Pete's next "
    "message assumed it had already landed; caught the gap, reported "
    "honestly rather than fabricating a commit hash, and committed once "
    "explicit approval arrived this turn. Re-verified the remaining "
    "category (b) pool directly post-fix: 16 states now remain "
    "genuinely zero-trigger, down from 17. Committed as engine/data/"
    "questions.py, tools/calibration_runner.py, "
    "tools/patch_q19_sever18.py, tools/patch_q19_severity_targets.py "
    "(commit 3030de1). Running Bucket 2/3 total: 40 of the original 85 "
    "Entrenched/Endemic-expected profiles now closed. MOB version "
    "bumped v4.120 → v4.121 per standing protocol -- fourth Bucket 3 fix "
    "shipped, remaining pool re-verified precisely at 16 states. | This "
    "session (Claude Code) | MOB v4.121 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.120 |",
    "| This session (Claude Code) | MOB v4.120 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.120 |",
    "| MOB version | v4.121 |",
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
