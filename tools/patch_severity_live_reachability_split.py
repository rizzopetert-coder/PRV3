"""
PRV3 MOB Update -- Severity reachability: live-reachability split, AUT-PS-01
fix committed, ATT-BC-02 parked

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: rewritten to record the
    major finding (PHASE_1_QUESTION_SEQUENCE structurally hardcodes off
    Q03A/Q27A/Q31), Action 1's completion (commit a6a7828), the new
    LIVE-REACHABLE vs PHASE-2-PENDING split, and ATT-BC-02's explicit park.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.114 -> v4.115.

Updates CLAUDE.md:
  - MOB version cross-reference v4.114 -> v4.115.

Usage:
  python tools/patch_severity_live_reachability_split.py --dry-run
  python tools/patch_severity_live_reachability_split.py --write
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

OLD_ITEM_3 = (
    "3. Severity-tier expectation/reachability gap -- Bucket 1 (\"wired, not "
    "selected\") CLOSED this session at zero cleanly-resolved-by-selection-alone. "
    "Buckets 2 and 3 remain open: Bucket 2 now 36 profiles (was 32), Bucket 3 "
    "unchanged at 49. Full per-profile reachability data regenerated fresh "
    "against live code (the original investigation's raw output was never "
    "saved durably) at tools/diag_severity_reachability_85profiles.py/.md, "
    "cross-verified against the one available ground-truth case (ATT-DC-01: "
    "raw=2.0 via two real triggers) before being trusted -- an early pass "
    "over-counted by including a question's neutral-fallback option when it "
    "coincidentally carried severity_trigger=True (Q23's does), inflating 36 "
    "of the 85 to falsely look reachable; caught and fixed before this data "
    "was used for anything. Bucket 1 breakdown (originally 4 profiles, "
    "\"wired but best_option_for_state() doesn't select the trigger option\"): "
    "traced all 4 individually rather than assuming one root cause applied "
    "to all. The engine's SELECTION logic itself is sound in every case "
    "investigated. Two (AUT-PS-01/paper_shield via Q23, "
    "ATT-BC-02/the_burned_credibility via Q03A) have no selection bug at all "
    "-- the trigger-bearing option genuinely scores lower on the state's "
    "primary liability field than a non-trigger option (not a tie); reaching "
    "them needs a content decision on which real answer should carry "
    "severity_trigger, not a code fix. The other two "
    "(ALL-DB-01/decision_blindness, EXP-SDB-01/sequential_decision_blindness) "
    "shared a genuine tie-break bug on Q31, where three dimensionally-"
    "identical options (B/C/D) existed and Python's max() arbitrarily kept "
    "the non-trigger option (B) on the tie -- FIXED, commit 44e85fc: "
    "best_option_for_state() (tools/calibration_runner.py) now prefers a "
    "severity_trigger=True option on a tie only when it is fully "
    "dimensionally identical to the otherwise-selected option across every "
    "field, not just the maximized one. Confirmed via a full "
    "QUESTION_LIBRARY sweep before implementing, not assumed safe: two OTHER "
    "trigger-involved ties exist (Q03A/the_second_close, "
    "Q20/decision_paralysis) but differ on other dimensional fields and were "
    "deliberately excluded by the full-identity requirement -- a naive "
    "\"prefer trigger on any tie\" rule would have silently rippled into "
    "those profiles' accumulated vectors. The fix is kept as a real, "
    "independent correction regardless of pass/fail outcome -- it makes the "
    "calibration harness match what a real respondent selecting C or D "
    "would actually experience, which it could not do at all before. Full "
    "172-profile regression, byte-for-byte: 169/172 unchanged (same 3 "
    "pre-existing failures), exactly 9 profiles touched (Q31's 3 wired "
    "states x 3 profile types each), zero ripple to the two "
    "deliberately-excluded ties, zero change to any other profile's output. "
    "ALL-DB-01/EXP-SDB-01 also added to _SEVERITY_FOLLOW_ON_TARGETS "
    "(SEVER-11, prior_failed_resolution=True) so the harness genuinely "
    "exercises the now-reachable trigger rather than leaving it silently "
    "untested -- confirmed empirically (a non-destructive test before "
    "committing to the change) NOT sufficient alone to reach either "
    "profile's locked Entrenched tier: SEVER-11 has no duration_band "
    "option, capping the real ceiling at raw=1.0/score=16.67/Emerging. That "
    "remaining gap is content (SEVER-11's own option set), not selection "
    "logic. NET FINDING, worth stating plainly: every real gap traced in "
    "Bucket 1 resolved to content, not code -- the engine's selection-logic "
    "layer is sound throughout. This sharpens what Buckets 2 and 3 actually "
    "are: a content/spec problem end to end, not a mix of bugs and content "
    "gaps. Bucket 2 (\"wired, insufficient magnitude\") now 36 profiles: the "
    "original 32 plus all four Bucket 1 members (AUT-PS-01, ATT-BC-02, "
    "ALL-DB-01, EXP-SDB-01), which share the identical underlying character "
    "-- real triggers exist or now genuinely fire, but current content "
    "(which option carries severity_trigger, or a follow-on's available "
    "option set) caps below the locked expected tier. Bucket 3 (\"not wired "
    "at all\") unchanged at 49 -- states with zero relationship to any "
    "severity-triggering question. Needs Pete's direction on Buckets 2 (36) "
    "and 3 (49): (a) author richer follow-on content / reassign trigger "
    "placement to close the gaps, (b) revise expected values to match real "
    "reachability, or (c) some combination -- genuinely undetermined which "
    "is correct without Pete's input on what the spec should represent. "
    "Scope: Bucket 2 is a content-authoring pass across the affected "
    "follow-on questions and option-to-trigger assignments; Bucket 3 is new "
    "question/trigger design from scratch, explicitly flagged as its own "
    "dedicated future session given its size, not an incremental add-on."
)

NEW_ITEM_3 = (
    "3. Severity-tier expectation/reachability gap -- MAJOR FINDING this "
    "session, standing distinction established going forward: LIVE-REACHABLE "
    "vs PHASE-2-PENDING. web/lib/session-store.ts's PHASE_1_QUESTION_SEQUENCE "
    "(the actual live question list) structurally hardcodes off three "
    "branches -- Q03A (Q03B is the only live branch, significant_events "
    "always defaults to [\"none\"] per engine/main.py's "
    "_locked_intake_to_engine_intake()), Q27A (Q27B only, same mechanism), "
    "and Q31 (code comment, verbatim: \"parked... never spliced\" -- "
    "\"SEVER-11 can in practice only ever fire from Q28 today\"). Confirmed "
    "directly in the real splice code (web/app/api/diagnostic/session/answer/"
    "route.ts), not just comments: Q28 genuinely fires via a real conditional "
    "splice whenever Q06 is answered A or B -- live, unlike Q31. This means a "
    "real fraction of this project's severity-reachability work targets code "
    "paths no live respondent can currently reach -- the project's own "
    "standing \"don't build correct-but-inert code\" principle applies "
    "directly. Not a reason to abandon the underlying calibration-suite "
    "correctness (still matters whenever Phase 2 collects significant_events "
    "and un-parks Q31), but reprioritizes urgency: LIVE-REACHABLE work is "
    "immediately real, PHASE-2-PENDING work is correct-but-dormant until a "
    "Phase 2 intake form exists.\n\n"
    "Bucket 1 (\"wired, not selected,\" originally 4 profiles) -- CLOSED at "
    "zero cleanly-resolved-by-selection-alone (full detail: commit 44e85fc, "
    "prior session-log entry). Reclassified by live-reachability this "
    "session: AUT-PS-01/paper_shield (Q23, LIVE) -- FIXED AND COMMITTED, "
    "commit a6a7828: option D's severity_trigger flipped to True, reuses A's "
    "existing SEVER-05 follow-on (real severity_input_mapping content, no "
    "new follow-on question needed), zero dimensional_contributions changes "
    "(D's -0.15 attitude_liability -- a real, live signal in the production "
    "accumulation engine, independent of severity -- preserved exactly). "
    "Confirmed a genuine no-op for the calibration harness (172-profile "
    "byte-for-byte regression, 0 changed -- D never wins best_option_for_state()'s "
    "dimension-max selection, a real non-tie loss, not a bug). Verified via "
    "a new real regression test, tools/test_aut_ps_01_q23_d_forced.py "
    "(committed, not scratch -- same harness-blind-spot precedent as the "
    "built_to_fail Q35-39 case) -- drives engine/main.py's real production "
    "functions directly (accumulate_one_answer/run_accumulated_engine), not "
    "the calibration harness, forcing D to bypass best_option_for_state() "
    "entirely. Confirms SEVER-05 genuinely fires through the real live path. "
    "Result is honestly Emerging (raw=1.00/score=16.67), NOT AUT-PS-01's "
    "locked Entrenched -- SEVER-05 has no duration_band option, same shape "
    "as the rest of Bucket 2. SEVER-05 folded into Track A's duration_band "
    "list as a 10th question. leadership_continuity_risk confirmed NOT "
    "needing the same treatment -- its severity path was always Q25, Q23's "
    "trigger placement is a no-op for it either way. ATT-BC-02/"
    "the_burned_credibility (Q03A, INERT/PHASE-2-PENDING) -- PARKED, Pete's "
    "explicit instruction, not to be proactively re-raised. Rationale on "
    "record: Q03A is inert in live Phase 1 today; designing content against "
    "it now risks targeting a branch that may shift once Phase 2 actually "
    "un-parks it. Investigated first (this session): no question is uniquely "
    "wired to the_burned_credibility (Q03A shares with 5 states, Q13 with 3, "
    "Q17 with 3, Q34 with 2 -- least shared, and unlike Q03A/Q13/Q17, ALL "
    "confirmed LIVE in Phase 1, and Q34 specifically has zero overlap with "
    "the_unsolved_problem/the_uninitiated/built_to_fail, the states driving "
    "the original overshoot concern -- though it does share with "
    "the_broken_compass/narrative_lock, both already in Track A's SEVER-13 "
    "group, so the same magnitude-capping discipline would apply there "
    "instead if ever revisited). Q03A's shared blast radius is structural "
    "to the question (state_targets is question-level, not option-level) -- "
    "switching Q03A's selected option would not reduce sharing. Revisit "
    "together with the rest of the PHASE-2-PENDING work once Phase 2 is "
    "live, not before. ALL-DB-01/decision_blindness, "
    "EXP-SDB-01/sequential_decision_blindness (Q31, INERT/PHASE-2-PENDING) "
    "-- selection-logic fix already committed (44e85fc) and correct, but "
    "Q31 itself never fires for a real respondent today -- reclassified "
    "PHASE-2-PENDING, not urgent, no further action needed until Phase 2.\n\n"
    "Bucket 2 (\"wired, insufficient magnitude\") -- Track A (duration_band "
    "additions), full live-reachability pass this session, not assumed: "
    "SEVER-13(Q32)/SEVER-08(Q26)/SEVER-11(Q28)/SEVER-07(Q25)/SEVER-02(Q20)/"
    "SEVER-10(Q27B)/SEVER-03(Q21)/SEVER-01(Q16)/SEVER-12(Q29)/SEVER-05(Q23) "
    "-- all 10 confirmed LIVE. SEVER-09(Q27A) -- confirmed INERT, "
    "reclassified PHASE-2-PENDING (not part of the live Track A count). Full "
    "question content, options, and blast-radius tables for all 10 live "
    "questions at tools/diag_bucket2_track_a_questions.md (untracked "
    "working reference, Claude.ai content-authoring handoff). Track B ("
    "AUT-PS-01/Q23 -- resolved above; ATT-BC-02/Q03A -- parked above), full "
    "detail at tools/diag_bucket2_track_b_questions.md. Severity aggregation "
    "confirmed additive in real production code (engine/main.py's "
    "run_accumulated_engine() -> SeverityEngine.add_input() per fired "
    "trigger, engine/severity.py's compute_raw_severity() sums all inputs) "
    "-- real compounding-overshoot risk exists if a new follow-on's content "
    "also reaches full duration_band=18mo_plus magnitude while sharing a "
    "question with an already-fired trigger; safe if capped at the typical "
    "raw<=1.00 shape. Bucket 3 (\"not wired at all,\" 49 profiles) -- "
    "unchanged, not yet investigated for live-reachability -- apply the "
    "same LIVE-REACHABLE/PHASE-2-PENDING split when this is taken up, "
    "explicitly flagged as its own dedicated future session given its size."
)

edit("tools/_mob.txt", OLD_ITEM_3, NEW_ITEM_3)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.114",
    "\\\\\\#\\\\\\# MOB v4.115",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Severity reachability: PHASE_1_QUESTION_SEQUENCE "
    "live-reachability finding, AUT-PS-01/Q23 fixed and committed (a6a7828), "
    "ATT-BC-02 parked | Full detail in Section 13b's Priority Queue item 3. "
    "Major finding: web/lib/session-store.ts's PHASE_1_QUESTION_SEQUENCE "
    "structurally hardcodes off Q03A, Q27A, and Q31 -- confirmed via the "
    "real splice code (not just comments) that Q28 IS genuinely live "
    "(conditional splice off Q06 A/B) while Q31 is not. This means the "
    "Bucket 1 Q31 fix (44e85fc, ALL-DB-01/EXP-SDB-01), Track A's SEVER-09 "
    "(Q27A), and ATT-BC-02's whole Q03A path are currently inert in live "
    "production -- reclassified PHASE-2-PENDING rather than urgent, per the "
    "project's own \"don't build correct-but-inert code\" standing "
    "principle. New standing distinction (LIVE-REACHABLE vs "
    "PHASE-2-PENDING) to apply to all future reachability work including "
    "Bucket 3. AUT-PS-01/paper_shield (Q23, confirmed LIVE) fixed and "
    "committed: option D's severity_trigger flipped True, reuses A's real "
    "SEVER-05 follow-on, zero dimensional_contributions changes. Confirmed "
    "a genuine no-op for the calibration harness (172-profile byte-for-byte "
    "regression, 0 changed). New real regression test committed, "
    "tools/test_aut_ps_01_q23_d_forced.py (matching the built_to_fail "
    "Q35-39 harness-blind-spot precedent) -- drives engine/main.py's real "
    "production functions directly, confirms SEVER-05 genuinely fires via "
    "the live path, result honestly Emerging (SEVER-05 lacks duration_band, "
    "same shape as the rest of Bucket 2) -- SEVER-05 folded into Track A as "
    "a 10th question. Full live-reachability pass across Track A's 10 "
    "routing questions: all 10 confirmed LIVE (Q32/Q26/Q28/Q25/Q20/Q27B/"
    "Q21/Q16/Q29/Q23). ATT-BC-02/the_burned_credibility (Q03A) investigated "
    "for a less-shared alternative path -- no question is uniquely wired to "
    "it; Q34 is meaningfully better than Q03A (live, avoids the specific "
    "states driving the original overshoot concern) but relocates rather "
    "than removes the compounding-magnitude tradeoff (shares with "
    "the_broken_compass/narrative_lock instead). PARKED per Pete's explicit "
    "instruction, not proactively re-raised -- Q03A is inert today, "
    "designing content against it now risks targeting a branch that may "
    "shift once Phase 2 un-parks it. Severity aggregation confirmed "
    "additive in real production code (engine/main.py's "
    "run_accumulated_engine(), not just the calibration harness). MOB "
    "version bumped v4.114 → v4.115 per standing protocol -- major "
    "reachability finding on permanent record, a real Bucket-2 fix shipped, "
    "Bucket 2/3 scope reframed by live-reachability going forward. | This "
    "session (Claude Code) | MOB v4.115 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.114 |",
    "| This session (Claude Code) | MOB v4.114 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.114 |",
    "| MOB version | v4.115 |",
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
