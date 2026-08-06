"""
PRV3 MOB Update -- Q18/SEVER-16 fix closure (commit 14b3f2c)

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    "OPEN: 25 category (b) states remain" tail (already corrected to 23
    last update, now further reduced) with the Q18 fix summary, running
    total 37/85, and the corrected 19-state remaining count.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.118 -> v4.119.

Updates CLAUDE.md:
  - MOB version cross-reference v4.118 -> v4.119.

Usage:
  python tools/patch_q18_bucket3_mob.py --dry-run
  python tools/patch_q18_bucket3_mob.py --write
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
    "OPEN: 25 category (b) states remain, each needing "
    "its own collateral-blast-radius review before implementation -- "
    "proceeding one state at a time, same discipline as tonight, not "
    "batched. 2 category (a) states remain untouched pending a dedicated "
    "Gemini scoping pass."
)

NEW_TAIL = (
    "Second Bucket 3 fix CLOSED and committed (commit 14b3f2c): Q18 "
    "options C/D confirmed as a full-field-identical tie, but unlike "
    "Q02/Q09 C already won outright via plain max() for all four states "
    "wired to Q18 -- no tie-break mechanism needed, a direct flip of the "
    "already-selected option. C (\"We've had incidents that I think could "
    "have been prevented if people had spoken up earlier\") describes "
    "realized harm, read as more severe than D's ongoing-but-unconfirmed "
    "framing -- honest pick, not fabricated. New SEVER-16 follow-on built "
    "to the SEVER-14/SEVER-15 duration-band style. Closes ATT-UD-01 "
    "(the_unlocked_door), ATT-UH-01 (the_unreported_hazard), ALL-SF-02, "
    "and ALL-SF-03 (both the_suppression_filter) outright, all reaching "
    "their locked Entrenched tier. ATT-WNS-01 (what_nobody_says) and "
    "ALL-SF-01 (the_suppression_filter), both Endemic-expected, correctly "
    "land short at Entrenched (raw 2.00, confirmed via normalized score, "
    "no double-count) -- their second triggers are separate future work: "
    "Q04 for what_nobody_says, Q04/Q08/Q12/Q30 for the_suppression_filter "
    "(the_suppression_filter has four other live-untriggered candidate "
    "questions, more headroom than what_nobody_says' single Q04). Running "
    "Bucket 2/3 total: 37 of the original 85 Entrenched/Endemic-expected "
    "profiles now closed (28 Track A + 2 ALL-FR-01/ALL-SI-01 + 3 Q02/"
    "SEVER-15 + 4 Q18/SEVER-16). OPEN: re-verified directly (not assumed) "
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

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.118",
    "\\\\\\#\\\\\\# MOB v4.119",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Second Bucket 3 fix (Q18/SEVER-16) closed and "
    "committed, commit 14b3f2c | Full detail in Section 13b's Priority "
    "Queue item 3. Scanned the (then-)23 remaining category (b) states "
    "for smallest/cleanest blast radius, same external-exposure-first "
    "methodology as the Q02 pick: the_unlocked_door and "
    "the_unreported_hazard tied cleanest with zero external exposure -- "
    "both states' only live question is Q18, whose full state_targets is "
    "exactly [the_unreported_hazard, the_unlocked_door, what_nobody_says, "
    "the_suppression_filter], all four already inside this investigation "
    "(a closed group of 4, one larger than Q02's group of 3, but "
    "strictly cleaner in kind -- every affected state already tracked "
    "with a known expected tier). Full workup confirmed: Q18 options C/D "
    "are a full-field-identical tie (alliance_liability 0.25, "
    "attitude_liability 0.5), but C already wins outright via plain "
    "max() for all four states (Attitude-primary states max on "
    "attitude_liability, Alliance-primary the_suppression_filter maxes "
    "on alliance_liability, C wins both by list order) -- no reliance on "
    "the Bucket 1 tie-break rule at all, a simpler mechanism than Q02/Q09 "
    "(flip the already-winning option directly, not the losing tied "
    "option). Content check: C (\"incidents that could have been "
    "prevented if people had spoken up earlier\" -- realized harm) reads "
    "as more severe than D (\"security is a known gap, people work "
    "around protocols\" -- an ongoing but unconfirmed-harm risk factor), "
    "so C is the honest severity pick, not D -- flagged explicitly since "
    "it inverts the Q02/Q09 pattern of flipping the non-selected option. "
    "Implemented: flipped C's severity_trigger to True, added new "
    "SEVER-16 (\"How long has this been happening?\", duration_band up to "
    "18mo_plus), extended _SEVERITY_FOLLOW_ON_TARGETS for ATT-UD-01, "
    "ATT-UH-01, ATT-WNS-01, ALL-SF-01, ALL-SF-02, ALL-SF-03. Verified "
    "directly (not assumed) that C remains selected for all four states "
    "post-flip -- confirmed a true no-op on selection, as predicted. Full "
    "172-profile byte-for-byte regression: exactly 6 profiles changed "
    "(ATT-UD-01, ATT-UH-01, ATT-WNS-01, ALL-SF-01, ALL-SF-02, ALL-SF-03), "
    "nothing else moved -- 169/172 baseline confirmed unchanged, same 3 "
    "pre-existing gaps. ATT-UD-01, ATT-UH-01, ALL-SF-02, ALL-SF-03 (all "
    "Entrenched-expected) now correctly reach Entrenched. ATT-WNS-01 and "
    "ALL-SF-01 (both Endemic-expected) reach Entrenched only -- confirmed "
    "via normalized severity score (33.33, identical to the other four, "
    "i.e. a single trigger's raw 2.00) landing correctly short rather "
    "than silently passing or overshooting; their second triggers are "
    "out of scope, logged as separate future work. All 5 Python test "
    "suites re-run clean (severity 56/56, output 112/112, accumulation "
    "47/47, output_synthesis 53/53, main 36/36). Re-verified the "
    "remaining category (b) pool directly post-fix rather than assuming "
    "a simple subtraction: hr_capture, the_suppression_filter, and "
    "what_nobody_says all now carry a live trigger (via Q02/Q18) and "
    "have moved out of \"zero-trigger category (b)\" into \"needs a "
    "second trigger,\" even though the latter two aren't fully closed -- "
    "19 states now remain genuinely zero-trigger, not 25 or 23. "
    "Committed as engine/data/questions.py, tools/calibration_runner.py, "
    "tools/patch_q18_sever16.py, tools/patch_q18_severity_targets.py "
    "(commit 14b3f2c). Running Bucket 2/3 total: 37 of the original 85 "
    "Entrenched/Endemic-expected profiles now closed. MOB version bumped "
    "v4.118 → v4.119 per standing protocol -- second Bucket 3 fix "
    "shipped, remaining pool re-verified precisely at 19 states. | This "
    "session (Claude Code) | MOB v4.119 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.118 |",
    "| This session (Claude Code) | MOB v4.118 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.118 |",
    "| MOB version | v4.119 |",
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
