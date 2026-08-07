"""
PRV3 MOB Update -- Q01/D + Q06/A closure (commit e6fb160)

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    tail with the Q01/D + Q06/A closure summary and updated running
    total (72/85).
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.124 -> v4.125.

Updates CLAUDE.md:
  - MOB version cross-reference v4.124 -> v4.125.

Usage:
  python tools/patch_q01d_q06a_mob.py --dry-run
  python tools/patch_q01d_q06a_mob.py --write
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
    "OPEN: 13 profiles remain across 9 distinct open items "
    "-- 2 confirmed dead-ends (fold into new-design pile, total 7), 2 "
    "pending explicit content calls (Q01 the_founders_grip thematic "
    "intent; Q06 A-vs-B, now mechanism-cleared), 2 needing new question "
    "design (already in the pile), 2 known PHASE-2-PENDING harness gaps "
    "(no action needed), 1 (ATT-UT-01) needing a second trigger via Q12 "
    "(still undecided), and EXP-MAF-01/APT-BF-01 needing an unidentified "
    "second trigger. 2 category (a) states remain untouched pending a "
    "dedicated Gemini scoping pass."
)

NEW_TAIL = (
    "Eighth Bucket 3 fix CLOSED and committed (commit e6fb160): both "
    "pending content calls resolved. Q01/D (the_founders_grip) -- C/D/E "
    "full-field-identical tie, all 4 Q01 states on C, flipping D relies "
    "on the tie-break rule (44e85fc) to reroute all 4 to D -- same "
    "mechanism as Q02/Q33, verified directly, not assumed. New SEVER-28 "
    "follow-on grounded in D's \"slow and effortful\" framing. "
    "decision_paralysis/the_lost_map/sequential_decision_blindness "
    "confirmed dimensionally identical and not opted in -- byte-for-"
    "byte unchanged. Q06/A (the_tolerated_violation/disparate_impact_"
    "architecture) -- content call confirmed by Pete (A already the "
    "correct severity read, already winning), true no-op flip, new "
    "SEVER-27. Opted in only AUT-TV-01/02 and EXP-DIA-01/02/03, the two "
    "states this call was scoped to unblock -- heard_and_ignored/the_"
    "unsolved_problem/decision_blindness/the_policy_lag also reach A "
    "but deliberately excluded, already closed/tracked via other "
    "levers. Flagged, not actioned: AUT-HI-01 (heard_and_ignored) is "
    "still short a second trigger and could close via this same "
    "SEVER-27 if picked up later -- deliberately left out, out of scope "
    "for this specific call. Full 172-profile byte-for-byte regression: "
    "exactly 7 profiles changed -- AUT-FG-01/02, AUT-TV-01/02, "
    "EXP-DIA-01/02/03 -- nothing else moved. AUT-FG-02, AUT-TV-02, "
    "EXP-DIA-02/03 (Entrenched-expected) close outright; AUT-FG-01, "
    "AUT-TV-01, EXP-DIA-01 (Endemic-expected) land correctly short at "
    "raw 2.00, confirmed via normalized score, no overshoot. All 5 "
    "Python test suites re-run clean. Running total: 72 of 85 closed "
    "(68 prior + 4 newly closed outright this fix -- AUT-FG-02, "
    "AUT-TV-02, EXP-DIA-02, EXP-DIA-03). OPEN: Q12/leadership_deafness "
    "under active investigation -- Pete described a new symptom "
    "(group-wide accountability failure, no leadership standard) none "
    "of Q12's existing options capture; proposed option F "
    "(attitude_liability: 0.75) confirmed via in-memory, non-destructive "
    "test to win outright for leadership_deafness, but the SAME test "
    "surfaced that the_untouchable is Q12's only other Attitude-primary "
    "state and would ALSO reroute to F, whose content doesn't honestly "
    "fit the_untouchable's actual condition (specific protected "
    "individuals, not group-wide accountability failure) -- Pete "
    "rejected F at 0.75 as-is on this basis. Investigating alternatives "
    "(tunable dimensional split, a parallel sixth option G fitting "
    "the_untouchable's own theme, or a confirmed dead-end) before any "
    "Q12 content is touched. 12 profiles remain open across the "
    "remaining items: 2 confirmed dead-ends (the_arbitrary_standard, "
    "the_overloaded_manager), 2 needing new question design "
    "(transition_paralysis, invisible_performance_management), 2 known "
    "PHASE-2-PENDING harness gaps (paper_shield, the_second_close), 1 "
    "(ATT-UT-01) needing a second trigger pending the Q12 investigation, "
    "and EXP-MAF-01/APT-BF-01 needing an unidentified second trigger. 2 "
    "category (a) states remain untouched pending a dedicated Gemini "
    "scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.124",
    "\\\\\\#\\\\\\# MOB v4.125",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Eighth Bucket 3 fix (Q01/D + Q06/A closures) "
    "closed and committed, commit e6fb160; running total 72/85; Q12 "
    "investigation opened, no content touched | Full detail in Section "
    "13b's Priority Queue item 3. Implemented both content calls "
    "confirmed by Pete last round. Q01/D: verified the tie-break "
    "mechanism directly rather than assuming it would transfer from "
    "Q02/Q33 -- confirmed all 4 Q01 states rerouted from C to D "
    "post-flip. Q06/A: confirmed the option had no trigger yet, added "
    "one (SEVER-27) scoped narrowly to the two states this call was "
    "meant to unblock (AUT-TV-01/02, EXP-DIA-01/02/03) rather than "
    "opportunistically sweeping in every other state that also reaches "
    "A -- flagged AUT-HI-01 (heard_and_ignored) as an available but "
    "deliberately-not-taken bonus closure, consistent with keeping each "
    "commit's scope matched to what was actually asked. Full 172-profile "
    "byte-for-byte regression: exactly 7 profiles changed, matching the "
    "precise expected set, nothing else moved; all deliberately-excluded "
    "profiles (AUT-HI-01/02, AUT-UP-01/02/03, ALL-DB-01, AUT-PL-01, "
    "AUT-DP-01, AUT-LM-01, EXP-SDB-01) confirmed byte-for-byte "
    "unchanged. All 5 Python test suites re-run clean. Running Bucket "
    "2/3 total: 72 of the original 85 Entrenched/Endemic-expected "
    "profiles now closed. Opened the Q12/leadership_deafness "
    "investigation for the new group-accountability-failure symptom "
    "Pete described, none of Q12's existing A-E options capture it. "
    "Confirmed leadership_deafness's primary_dimension directly (Attitude "
    "/ attitude_liability, not assumed) and, via an in-memory, "
    "non-destructive simulation (no files touched, confirmed via git "
    "status), that a proposed option F at attitude_liability=0.75 wins "
    "outright for leadership_deafness over the existing C/D tie at 0.6 "
    "-- but the same simulation showed the_untouchable is Q12's only "
    "other Attitude-primary state, also tied at 0.6 on C, and would "
    "ALSO reroute to F. Pete reviewed and rejected F at 0.75 as-is: its "
    "content (group-wide accountability failure, no leadership "
    "standard) doesn't honestly represent the_untouchable's actual "
    "condition (specific protected individuals escaping consequences), "
    "so the_untouchable would end up with a live answer that doesn't "
    "fit it. Now investigating three alternatives per Pete's explicit "
    "direction, read-only, no content touched yet: (a) whether a "
    "secondary dimensional field could distinguish the two states' "
    "selection logic on Q12 without relying purely on attitude_"
    "liability magnitude, (b) whether a parallel sixth option G, "
    "honestly fitting the_untouchable's own theme, could be added at "
    "the same 0.75 tier so both states get a correctly-fitting "
    "escalation instead of one winning by default, or (c) reporting "
    "plainly if neither yields a clean answer. MOB version bumped "
    "v4.124 → v4.125 per standing protocol -- eighth Bucket 3 fix "
    "shipped, Q12 investigation opened and logged before any content "
    "change. | This session (Claude Code) | MOB v4.125 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.124 |",
    "| This session (Claude Code) | MOB v4.124 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.124 |",
    "| MOB version | v4.125 |",
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
