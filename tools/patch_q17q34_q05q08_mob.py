"""
PRV3 MOB Update -- Q17/Q34 unlock + Q05/Q08 content-call closures
(commit f1bd7de), exact 85-profile running total, Q06 mechanism trace.

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    tail with the Q17/Q34 unlock + Q05/Q08 closures, the exact 68/85
    running total (direct run_profile() count, not incremental
    arithmetic), and the Q06 weighted_multi_select mechanism finding.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.123 -> v4.124.

Updates CLAUDE.md:
  - MOB version cross-reference v4.123 -> v4.124.

Usage:
  python tools/patch_q17q34_q05q08_mob.py --dry-run
  python tools/patch_q17q34_q05q08_mob.py --write
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
    "OPEN: remaining-pool count "
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

NEW_TAIL = (
    "Seventh Bucket 3 fix CLOSED and committed (commit f1bd7de): the "
    "Q17/Q34 collision question resolved definitively via empirical "
    "in-memory test with a positive control (prior round) -- confirmed "
    "the earlier ATT-GD-01/ATT-NL-01 collision finding conflated "
    "selection-reroute with severity-firing, not a real mechanism "
    "difference from Q14/Q18/Q19. Q17/B and Q34/C flipped to "
    "severity_trigger=True (new SEVER-23/SEVER-24, both already-winning, "
    "true no-op for every state on each question including "
    "the_broken_compass). Un-parks ATT-BC-02 (the_burned_credibility, "
    "parked since the AUT-PS-01/paper_shield session over Q03A) and "
    "closes it to Entrenched; closes ATT-BC-01 to Endemic (both "
    "triggers, zero to start); reopens and closes ATT-GD-01/ATT-NL-01 "
    "(groundhog_day/narrative_lock) to Endemic via their genuine second "
    "trigger, on top of their existing SEVER-13 first trigger. Same "
    "commit also carries Pete's content calls on Q05/C (\"It depends on "
    "who the person is...\") and Q08/C (\"By the time problems reach us "
    "they're already crises...\") -- both already-winning, true no-op, "
    "new SEVER-25/SEVER-26. Closes ATT-UT-02/03 outright, lands ATT-UT-01 "
    "correctly short (still needs Q12, undecided); gives ATT-BS-01, "
    "ATT-IT-01, ATT-LD-01, and ALL-SF-01 their genuine second trigger, "
    "closing all four to Endemic. Full 172-profile byte-for-byte "
    "regression across both (baseline at prior commit, covering Q17/Q34 "
    "+ Q05/Q08 together): exactly 11 profiles changed -- ALL-SF-01, "
    "ATT-BC-01, ATT-BC-02, ATT-BS-01, ATT-GD-01, ATT-IT-01, ATT-LD-01, "
    "ATT-NL-01, ATT-UT-01/02/03 -- matching the precise expected union, "
    "nothing else moved. Every already-closed sibling profile "
    "(ATT-BS-02/03, ATT-IT-02/03, ATT-WR-01, ATT-LD-02/03, ALL-SF-02/03, "
    "ATT-GD-02/03, ATT-NL-02/03, ATT-BC-03, ATT-BCP-01/02/03) confirmed "
    "byte-for-byte unchanged -- the_broken_compass verified unaffected "
    "in the REAL implementation, not just the prior round's in-memory "
    "test. All 5 Python test suites re-run clean. EXACT running total, "
    "recomputed directly against the full 85-profile list (tools/"
    "diag_severity_reachability_85profiles.md) via run_profile() per "
    "profile, not incremental session-log arithmetic, per Pete's "
    "explicit instruction not to estimate: **68 of 85 CLOSED** (actual "
    "tier == locked expected tier), 4 SHORT (partial progress, "
    "APT-BF-01/ATT-UT-01/AUT-HI-01/EXP-MAF-01, each needing an "
    "unidentified or undecided second trigger), 13 OPEN (still "
    "Emerging: ALL-AS-01/the_arbitrary_standard and "
    "APT-OM-01/the_overloaded_manager, both confirmed dead-ends; "
    "AUT-FG-01/02/the_founders_grip pending Q01's content call; "
    "AUT-TV-01/02 and EXP-DIA-01/02/03, pending Q06's A-vs-B content "
    "call; AUT-TP-01/transition_paralysis and "
    "EXP-IPM-01/invisible_performance_management, both needing new "
    "question design; AUT-PS-01/paper_shield and "
    "ALL-SC-01/the_second_close, both known, already-documented "
    "PHASE-2-PENDING harness gaps unrelated to tonight's work). Q06 "
    "weighted_multi_select severity_trigger mechanism traced directly "
    "through the real code per Pete's request, resolving the last open "
    "question blocking Q06's content call: confirmed per-option-"
    "independent, no combination logic exists or is even possible today "
    "-- web/app/api/diagnostic/session/answer/route.ts's AnswerRequest "
    "takes a single option_id: string (not an array), and "
    "engine/main.py's accumulate_one_answer() takes a single option_id "
    "parameter, checking only that one option's own severity_trigger "
    "flag with zero awareness of any other option. \"weighted_multi_"
    "select\" as a QUESTION_LIBRARY format label does not correspond to "
    "genuine multi-checkbox submission in the current live wire "
    "protocol -- every answer, regardless of question format, submits "
    "exactly one option_id per call. The calibration harness has "
    "matched this all session (generate_answers() always wraps a single "
    "best_option_for_state() pick in a one-element list). Practical "
    "conclusion: Q06's content call (A vs B) carries zero special "
    "multi-select risk -- mechanically identical to every other "
    "true-no-op fix shipped tonight, a pure content judgment now "
    "unblocked. Separately noted, not urgent: route.ts's own comment "
    "(\"Q06 itself carries no severity_trigger of its own\") is now "
    "stale relative to tonight's Q06/D flip (the_paper_tiger fix) -- "
    "harmless, since the splice mechanism it describes is fully generic "
    "and reads the real engine's severity_follow_on_id at runtime, not "
    "the comment, but worth a doc cleanup pass sometime. OPEN: 13 "
    "profiles remain across 9 distinct open items -- 2 confirmed "
    "dead-ends (fold into new-design pile, total 7), 2 pending explicit "
    "content calls (Q01 the_founders_grip thematic intent; Q06 A-vs-B, "
    "now mechanism-cleared), 2 needing new question design (already in "
    "the pile), 2 known PHASE-2-PENDING harness gaps (no action needed), "
    "1 (ATT-UT-01) needing a second trigger via Q12 (still undecided), "
    "and EXP-MAF-01/APT-BF-01 needing an unidentified second trigger. 2 "
    "category (a) states remain untouched pending a dedicated Gemini "
    "scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.123",
    "\\\\\\#\\\\\\# MOB v4.124",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Seventh Bucket 3 fix (Q17/Q34 unlock + Q05/Q08 "
    "content-call closures) closed and committed, commit f1bd7de; exact "
    "85-profile running total recomputed at 68/85; Q06 multi-select "
    "mechanism traced | Full detail in Section 13b's Priority Queue "
    "item 3. Implemented the Q17/Q34 unlock confirmed clean last round: "
    "Q17/B and Q34/C flipped to severity_trigger=True (SEVER-23/24), "
    "both already-winning options, true no-op for every state on each "
    "question. Un-parks ATT-BC-02 (the_burned_credibility, parked since "
    "an earlier session over Q03A) -- closes to Entrenched. Closes "
    "ATT-BC-01 to Endemic (needed both new triggers, had zero). Reopens "
    "ATT-GD-01/ATT-NL-01 (deferred earlier this session on the now-"
    "corrected collision finding) -- closes both to Endemic via their "
    "genuine second trigger stacked on the existing SEVER-13. Same "
    "commit implements Pete's Q05/C and Q08/C content calls (SEVER-25/"
    "26, both already-winning, true no-op) -- closes ATT-UT-02/03 "
    "outright, ATT-UT-01 lands correctly short (Q12 still undecided); "
    "gives ATT-BS-01/ATT-IT-01/ATT-LD-01/ALL-SF-01 their genuine second "
    "trigger, closing all four to Endemic. Full 172-profile byte-for-"
    "byte regression, both fixes together: exactly 11 profiles changed, "
    "matching the precise expected union, nothing else moved. Every "
    "already-closed sibling profile confirmed byte-for-byte unchanged, "
    "including the_broken_compass's 3 variants -- the empirical finding "
    "from the in-memory test held in the real implementation, not just "
    "theory. All 5 Python test suites re-run clean. Computed the exact "
    "running total against the full 85-profile list directly via "
    "run_profile() per Pete's explicit instruction not to estimate, "
    "given several fixes this round touched profiles that may have "
    "partially closed in earlier rounds (confirmed true for ATT-GD-01/"
    "ATT-NL-01, already at Entrenched via SEVER-13 before this round's "
    "Endemic closure) -- landed at 68 CLOSED, 4 SHORT, 13 OPEN, summing "
    "to exactly 85, not assumed from incremental session-log addition. "
    "Traced the Q06 weighted_multi_select severity_trigger mechanism "
    "through the real production code (engine/main.py's "
    "accumulate_one_answer(), web/app/api/diagnostic/session/answer/"
    "route.ts's AnswerRequest schema) per Pete's request: confirmed "
    "per-option-independent firing with no combination logic across "
    "multiple selections, because the live wire protocol only ever "
    "carries a single option_id per answer submission regardless of a "
    "question's declared format -- \"weighted_multi_select\" as a "
    "QUESTION_LIBRARY label does not correspond to genuine multi-"
    "checkbox submission in the app as currently built. This resolves "
    "the last open blocker on Q06's A-vs-B content call -- mechanically "
    "identical to every other true-no-op fix shipped tonight. Also "
    "noted, not urgent: route.ts carries a comment (\"Q06 itself carries "
    "no severity_trigger of its own\") now stale relative to tonight's "
    "earlier Q06/D flip (the_paper_tiger fix) -- harmless since the "
    "splice logic it describes reads the real engine's runtime output, "
    "not the comment itself, but flagged for a future doc pass. MOB "
    "version bumped v4.123 → v4.124 per standing protocol -- seventh "
    "Bucket 3 fix shipped, exact running total computed and verified "
    "directly, Q06 mechanism question resolved. | This session (Claude "
    "Code) | MOB v4.124 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.123 |",
    "| This session (Claude Code) | MOB v4.123 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.123 |",
    "| MOB version | v4.124 |",
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
