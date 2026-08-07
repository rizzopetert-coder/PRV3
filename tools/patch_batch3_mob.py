"""
PRV3 MOB Update -- Q11+Q06+Q04+SEVER-20-reuse batch closure (commit 37ba6eb)

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    "15 category (b) states remain" tail with the full 22-profile
    breakdown, running total, and a corrected remaining-pool count
    (the naive "has_any_trigger" heuristic undercounts -- the_tolerated_
    violation and disparate_impact_architecture look removed from the
    pool because Q06 now carries A trigger via D, but they route through
    the still-untriggered A/B tie, confirmed still genuinely Emerging via
    direct run_profile check, not assumed).
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.122 -> v4.123.

Updates CLAUDE.md:
  - MOB version cross-reference v4.122 -> v4.123.

Usage:
  python tools/patch_batch3_mob.py --dry-run
  python tools/patch_batch3_mob.py --write
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
    "that 15 category (b) states now remain zero-trigger -- "
    "invisible_influence_architecture moved out of the pool, fully "
    "closed this round. Each of the 15 needs its own "
    "collateral-blast-radius review before implementation -- proceeding "
    "one state at a time, same discipline as the last five fixes, not "
    "batched. 2 category (a) states remain untouched pending a dedicated "
    "Gemini scoping pass."
)

NEW_TAIL = (
    "Batched review adopted per Pete's explicit direction (reduce "
    "round-trips, keep the human checkpoint on content/judgment calls): "
    "full workup across all remaining zero-trigger states in one pass "
    "(tools/diag_bucket3_remaining_batch.md), surfacing mechanism "
    "dead-ends, true-clean fixes, and content-judgment items explicitly "
    "rather than resolving them unilaterally. Two new DEAD-ENDs "
    "confirmed: the_overloaded_manager (Q12 carries zero real signal for "
    "its Aptitude field, all options 0.0) and the_arbitrary_standard "
    "(all 3 candidates -- Q05/Q11/Q15 -- carry zero/negative Alliance "
    "signal); new-design pile now 7 states. Sixth Bucket 3 fix CLOSED "
    "and committed (commit 37ba6eb, bundling the previously-implemented "
    "but not-yet-committed Q11 fix together with 3 newly-approved CLEAN "
    "groups built on top of it -- flagged plainly as a commit-gap "
    "catch, same pattern as the earlier Q19 gap, not silently absorbed): "
    "Q11/D (motivational_architecture_failure/cultural_overtime, "
    "SEVER-20) + Q06/D (the_paper_tiger, new SEVER-21, zero blast radius "
    "-- D unique to this state on Q06, no other state even reaches it) "
    "+ Q04/D (hr_capture/heard_and_ignored/what_nobody_says/leadership_"
    "deafness, new SEVER-22, true no-op for all four) + SEVER-20 reuse "
    "(the_basement_standard/the_inside_track/the_wrong_reward, pure "
    "table addition, no new content). Full 172-profile byte-for-byte "
    "regression: exactly 22 profiles changed -- APT-PT-00/01/02/03, "
    "ATT-BS-01/02/03, ATT-IT-01/02/03, ATT-LD-01/02/03, ATT-WNS-01, "
    "ATT-WR-01, AUT-HC-01, AUT-HI-01/02, EXP-CO-01, EXP-MAF-01/02/03 -- "
    "nothing else moved. 17 CLOSE outright (APT-PT-00/01/02/03, "
    "ATT-BS-02/03, ATT-IT-02/03, ATT-LD-02/03, ATT-WNS-01, ATT-WR-01, "
    "AUT-HC-01, AUT-HI-02, EXP-CO-01, EXP-MAF-02/03); AUT-HC-01 and "
    "ATT-WNS-01 notably jump straight to Endemic (score 66.67, raw 4.00 "
    "-- their long-standing second-trigger gaps, closed via Q04/D as a "
    "genuine second trigger). 5 land correctly SHORT at Entrenched "
    "(score 33.33, raw 2.00, confirmed no overshoot): ATT-BS-01, "
    "ATT-IT-01, ATT-LD-01, AUT-HI-01, EXP-MAF-01, all pending a second "
    "trigger not yet identified. Running Bucket 2/3 total: 58 of the "
    "original 85 Entrenched/Endemic-expected profiles now closed (28 "
    "Track A + 2 ALL-FR-01/ALL-SI-01 + 3 Q02/SEVER-15 + 4 Q18/SEVER-16 + "
    "2 Q14/SEVER-17 + 1 Q19/SEVER-18 + 1 Q33/SEVER-19 + 17 this batch). "
    "All 5 Python test suites re-run clean. OPEN: remaining-pool count "
    "corrected rather than taken from the naive per-question trigger "
    "heuristic -- the_tolerated_violation (AUT-TV-01/02) and "
    "disparate_impact_architecture (EXP-DIA-01/02/03) both LOOK removed "
    "from the zero-trigger pool because Q06 now carries a trigger via D "
    "(the_paper_tiger's), but both route through the still-untriggered "
    "A/B tie on Q06 and are confirmed still genuinely Emerging via direct "
    "run_profile check, not assumed -- same classification artifact "
    "already caught once this session for the_arbitrary_standard. "
    "Genuinely remaining: the_untouchable (Q05/Q12, NEEDS-PETE-CALL), "
    "the_founders_grip (Q01, NEEDS-PETE-CALL, Pete confirming thematic "
    "intent), the_burned_credibility (Q17/Q34, under active "
    "investigation this round), the_tolerated_violation and "
    "disparate_impact_architecture (Q06 A vs B, mechanism question "
    "pending on multi-select trigger semantics), plus the 2 new "
    "DEAD-ENDs. 2 category (a) states remain untouched pending a "
    "dedicated Gemini scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.122",
    "\\\\\\#\\\\\\# MOB v4.123",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Batched Bucket 3 review adopted; sixth fix "
    "(Q11+Q06+Q04+SEVER-20-reuse) closed and committed, commit 37ba6eb; "
    "2 new dead-ends confirmed | Full detail in Section 13b's Priority "
    "Queue item 3 and tools/diag_bucket3_remaining_batch.md. Pete "
    "directed a switch from one-state-at-a-time to a single consolidated "
    "batch review across all remaining zero-trigger states, to reduce "
    "round-trips while keeping the human checkpoint on content/judgment "
    "calls. Mechanism-viability-first discipline (established the prior "
    "round via the_overloaded_manager) applied to every remaining "
    "candidate before trusting any blast-radius ranking -- surfaced a "
    "second dead-end (the_arbitrary_standard, zero/negative Alliance "
    "signal on all 3 of its candidates) alongside the_overloaded_manager, "
    "new-design pile now 7 states total. Three CLEAN groups identified "
    "with zero content ambiguity: the_paper_tiger via Q06/D (D is the "
    "unique max, not shared with any other Q06-wired state at all -- the "
    "cleanest blast radius found all session, not just zero external "
    "exposure but zero exposure of any kind); Q04/D reaching hr_capture/"
    "heard_and_ignored/what_nobody_says/leadership_deafness "
    "simultaneously (unique max, true no-op for all four, unambiguous "
    "content); and reuse of the already-drafted SEVER-20 for "
    "the_basement_standard/the_inside_track/the_wrong_reward (pure table "
    "addition, zero new content decisions). Implemented and regression-"
    "tested together with the previously-uncommitted Q11 fix (motivational_"
    "architecture_failure/cultural_overtime) -- caught and flagged a "
    "commit-status gap before committing (Q11 was never separately "
    "approved for commit, same pattern as the earlier Q19 gap), then "
    "committed all four as one unit per Pete's evident intent. Full "
    "172-profile byte-for-byte regression (baseline taken at the prior "
    "commit, so this run covers all four fixes together): exactly 22 "
    "profiles changed, matching the precise expected union, nothing else "
    "moved. AUT-HC-01 and ATT-WNS-01 -- both long-standing second-trigger "
    "gaps from earlier Bucket 3 fixes -- close to Endemic via Q04/D as "
    "their genuine second trigger, confirmed via normalized score 66.67 "
    "(raw 4.00), not just tier label. 5 profiles (ATT-BS-01, ATT-IT-01, "
    "ATT-LD-01, AUT-HI-01, EXP-MAF-01) land correctly short at raw 2.00, "
    "confirmed no overshoot. All 5 Python test suites re-run clean. "
    "Running Bucket 2/3 total: 58 of the original 85 profiles now "
    "closed. Also caught and corrected a remaining-pool counting "
    "artifact: the naive per-question 'any trigger exists' heuristic now "
    "undercounts, since Q06 carries a trigger via D even though "
    "the_tolerated_violation/disparate_impact_architecture route through "
    "the separate, still-untriggered A/B tie -- both confirmed still "
    "genuinely Emerging via direct run_profile check before reporting "
    "the corrected remaining scope, not assumed from the heuristic. "
    "Separately, empirically resolved the Q17/Q34/the_broken_compass "
    "collision question flagged last round: in-memory, non-destructive "
    "test (flip Q17/B's or Q34/C's trigger to a real-but-unrelated "
    "follow-on, confirm the_broken_compass's 3 profile variants stay "
    "byte-for-byte identical when not opted into _SEVERITY_FOLLOW_ON_"
    "TARGETS, then a positive control -- temporarily opting one in -- to "
    "confirm the mechanism does respond when actually opted in, "
    "validating the test itself) confirmed the earlier ATT-GD-01/"
    "ATT-NL-01 collision finding conflated selection-reroute with "
    "severity-firing; Q17/Q34 are structurally safe by the same "
    "per-profile-ID gate protecting every other external state this "
    "session. Implementation of that unlock (Q17/Q34, reopening "
    "ATT-GD-01/ATT-NL-01, un-parking ATT-BC-02) is a separate action, "
    "not part of this commit. MOB version bumped v4.122 → v4.123 per "
    "standing protocol -- sixth Bucket 3 fix shipped, 2 new dead-ends on "
    "record, remaining-pool count corrected precisely rather than taken "
    "from a heuristic. | This session (Claude Code) | MOB v4.123 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.122 |",
    "| This session (Claude Code) | MOB v4.122 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.122 |",
    "| MOB version | v4.123 |",
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
