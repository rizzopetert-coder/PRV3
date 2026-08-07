"""
PRV3 MOB Update -- Q14/SEVER-17 fix closure (commit f75e512)

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    "19 category (b) states remain" tail with the Q14 fix summary,
    running total 39/85, and the corrected 17-state remaining count.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.119 -> v4.120.

Updates CLAUDE.md:
  - MOB version cross-reference v4.119 -> v4.120.

Usage:
  python tools/patch_q14_bucket3_mob.py --dry-run
  python tools/patch_q14_bucket3_mob.py --write
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
    "that 19 category (b) states now remain zero-trigger -- hr_capture, "
    "the_suppression_filter, and what_nobody_says all now carry a live "
    "trigger via Q02/Q18 respectively and have moved from \"zero-trigger\" "
    "to \"needs a second trigger,\" so they no longer count toward this "
    "pool even though the_suppression_filter/what_nobody_says aren't "
    "fully closed. Each of the 19 needs its own collateral-blast-radius "
    "review before implementation -- proceeding one state at a time, same "
    "discipline as the last two fixes, not batched. 2 category (a) states "
    "remain untouched pending a dedicated Gemini scoping pass."
)

NEW_TAIL = (
    "Third Bucket 3 fix CLOSED and committed (commit f75e512): Q14 "
    "options D/E confirmed as a full-field-identical tie, and like Q18, "
    "D already won outright via plain max() for all three states wired "
    "to Q14 -- no tie-break mechanism needed, a direct flip of the "
    "already-selected option. D (\"We have concerns about both -- "
    "consistency and competitiveness are issues\") is a concrete, "
    "admitted problem, read as more severe than E's unassessed "
    "\"haven't looked closely enough to know\" -- honest pick, not "
    "fabricated. New SEVER-17 follow-on built to the SEVER-14/15/16 "
    "duration-band style, state_targets deliberately scoped to only "
    "[pay_exposure, compression_crisis], excluding the_pay_fog. Closes "
    "EXP-CC-01 (compression_crisis) and AUT-PE-01 (pay_exposure) "
    "outright, both reaching their locked Entrenched tier -- no "
    "short-landing profile this round, unlike the last two fixes. "
    "the_pay_fog's AUT-PF-01 deliberately excluded from "
    "_SEVERITY_FOLLOW_ON_TARGETS -- it remains a separate, "
    "already-known open gap (WIRED_INSUFFICIENT, Entrenched-expected, "
    "still short via its own Q16/SEVER-01 path, raw 1.00/1.98), "
    "unrelated to this fix and unaffected by it, just sharing Q14. "
    "Confirmed word-for-word identical Q14 selection and a byte-for-byte "
    "identical snapshot for AUT-PF-01 before vs. after, not just its "
    "absence from the changed-profile diff. Running Bucket 2/3 total: "
    "39 of the original 85 Entrenched/Endemic-expected profiles now "
    "closed (28 Track A + 2 ALL-FR-01/ALL-SI-01 + 3 Q02/SEVER-15 + 4 "
    "Q18/SEVER-16 + 2 Q14/SEVER-17). OPEN: re-verified directly (not "
    "assumed) that 17 category (b) states now remain zero-trigger -- "
    "compression_crisis and pay_exposure both moved out of the pool, "
    "fully closed this round. Each of the 17 needs its own "
    "collateral-blast-radius review before implementation -- proceeding "
    "one state at a time, same discipline as the last three fixes, not "
    "batched. 2 category (a) states remain untouched pending a dedicated "
    "Gemini scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.119",
    "\\\\\\#\\\\\\# MOB v4.120",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Third Bucket 3 fix (Q14/SEVER-17) closed and "
    "committed, commit f75e512 | Full detail in Section 13b's Priority "
    "Queue item 3. Scanned the 19 remaining category (b) states for "
    "smallest/cleanest blast radius, same external-exposure-first "
    "methodology as the last two rounds -- but this round, unlike the "
    "prior two, no state hit zero external exposure; compression_crisis "
    "and pay_exposure tied cleanest at external=1 (the one external "
    "state, the_pay_fog), both states' only live question is Q14. Full "
    "workup confirmed: Q14 options D/E are a full-field-identical tie "
    "(aptitude_liability 0.25, authority_liability 0.5), with D already "
    "winning outright for all three states wired to Q14, including "
    "the_pay_fog -- same \"already-winning\" shape as Q18, not Q02/Q09's "
    "tie-break-reliant shape. Checked the_pay_fog directly before "
    "touching anything: it's a separate, already-known open gap "
    "(AUT-PF-01, WIRED_INSUFFICIENT, Entrenched-expected, raw 1.00/1.98 "
    "via its own Q16/SEVER-01 path, not in _SEVERITY_FOLLOW_ON_TARGETS) "
    "with two other wired questions (Q16 already-triggered, Q19 "
    "untriggered) -- Q14 isn't its only lever and it's out of scope. "
    "Since D already won for the_pay_fog too, flipping D is a true "
    "no-op on its selection: same answer, word-for-word, only the "
    "option-level trigger flag changes, and with the_pay_fog excluded "
    "from _SEVERITY_FOLLOW_ON_TARGETS it gets zero severity contribution "
    "from it either. Content check: D (\"concerns about both... are "
    "issues\" -- concrete admission) reads as more severe than E "
    "(\"haven't looked closely enough to know\" -- unassessed, not a "
    "confirmed problem), honest pick, no new option needed. Implemented: "
    "flipped D's severity_trigger to True, added new SEVER-17 (\"How "
    "long has this been the case?\", duration_band up to 18mo_plus, "
    "state_targets scoped to only [pay_exposure, compression_crisis] to "
    "keep the_pay_fog out of every touched surface, not just the "
    "follow-on table), extended _SEVERITY_FOLLOW_ON_TARGETS for "
    "EXP-CC-01 and AUT-PE-01 only. Verified directly (not assumed) that "
    "D remains selected for all three states post-flip, the_pay_fog's "
    "answer text unchanged word-for-word. Full 172-profile byte-for-byte "
    "regression: exactly 2 profiles changed (EXP-CC-01, AUT-PE-01), "
    "nothing else moved -- explicitly confirmed AUT-PF-01's full "
    "snapshot dict is byte-for-byte identical before vs. after (not just "
    "absent from the diff), 169/172 baseline confirmed unchanged, same 3 "
    "pre-existing gaps. Both EXP-CC-01 and AUT-PE-01 (Entrenched-"
    "expected) reach their locked tier via normalized severity score "
    "33.33 (single trigger's raw 2.00) -- no short-landing profile this "
    "round, first Bucket 3 fix without one. All 5 Python test suites "
    "re-run clean (severity 56/56, output 112/112, accumulation 47/47, "
    "output_synthesis 53/53, main 36/36). Re-verified the remaining "
    "category (b) pool directly post-fix: 17 states now remain "
    "genuinely zero-trigger, down from 19. Committed as "
    "engine/data/questions.py, tools/calibration_runner.py, "
    "tools/patch_q14_sever17.py, tools/patch_q14_severity_targets.py "
    "(commit f75e512). Running Bucket 2/3 total: 39 of the original 85 "
    "Entrenched/Endemic-expected profiles now closed. MOB version bumped "
    "v4.119 → v4.120 per standing protocol -- third Bucket 3 fix "
    "shipped, remaining pool re-verified precisely at 17 states. | This "
    "session (Claude Code) | MOB v4.120 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.119 |",
    "| This session (Claude Code) | MOB v4.119 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.119 |",
    "| MOB version | v4.120 |",
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
