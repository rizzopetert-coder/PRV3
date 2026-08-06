"""
PRV3 MOB Update -- Track A (10 duration_band additions) CLOSED

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: trimmed to a concise
    pointer-style summary now that Track A is closed, keeping only what's
    still genuinely open front and center (5-profile gap, SEVER-09
    Phase-2-pending, ATT-BC-02 parked, Bucket 3 untouched). Full narrative
    detail moved to the new Section 16 entry, matching the established
    pattern for closed work.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.115 -> v4.116.

Updates CLAUDE.md:
  - MOB version cross-reference v4.115 -> v4.116.

Usage:
  python tools/patch_track_a_closure.py --dry-run
  python tools/patch_track_a_closure.py --write
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
    "Phase 2 intake form exists. Bucket 1 (\"wired, not selected,\" originally "
    "4 profiles) -- CLOSED at zero cleanly-resolved-by-selection-alone (full "
    "detail: commit 44e85fc, prior session-log entry). Reclassified by "
    "live-reachability this session: AUT-PS-01/paper_shield (Q23, LIVE) -- "
    "FIXED AND COMMITTED, commit a6a7828: option D's severity_trigger "
    "flipped to True, reuses A's existing SEVER-05 follow-on (real "
    "severity_input_mapping content, no new follow-on question needed), zero "
    "dimensional_contributions changes (D's -0.15 attitude_liability -- a "
    "real, live signal in the production accumulation engine, independent of "
    "severity -- preserved exactly). Confirmed a genuine no-op for the "
    "calibration harness (172-profile byte-for-byte regression, 0 changed -- "
    "D never wins best_option_for_state()'s dimension-max selection, a real "
    "non-tie loss, not a bug). Verified via a new real regression test, "
    "tools/test_aut_ps_01_q23_d_forced.py (committed, not scratch -- same "
    "harness-blind-spot precedent as the built_to_fail Q35-39 case) -- "
    "drives engine/main.py's real production functions directly "
    "(accumulate_one_answer/run_accumulated_engine), not the calibration "
    "harness, forcing D to bypass best_option_for_state() entirely. Confirms "
    "SEVER-05 genuinely fires through the real live path. Result is honestly "
    "Emerging (raw=1.00/score=16.67), NOT AUT-PS-01's locked Entrenched -- "
    "SEVER-05 has no duration_band option, same shape as the rest of Bucket "
    "2. SEVER-05 folded into Track A's duration_band list as a 10th "
    "question. leadership_continuity_risk confirmed NOT needing the same "
    "treatment -- its severity path was always Q25, Q23's trigger placement "
    "is a no-op for it either way. ATT-BC-02/the_burned_credibility (Q03A, "
    "INERT/PHASE-2-PENDING) -- PARKED, Pete's explicit instruction, not to "
    "be proactively re-raised. Rationale on record: Q03A is inert in live "
    "Phase 1 today; designing content against it now risks targeting a "
    "branch that may shift once Phase 2 actually un-parks it. Investigated "
    "first (this session): no question is uniquely wired to "
    "the_burned_credibility (Q03A shares with 5 states, Q13 with 3, Q17 with "
    "3, Q34 with 2 -- least shared, and unlike Q03A/Q13/Q17, ALL confirmed "
    "LIVE in Phase 1, and Q34 specifically has zero overlap with "
    "the_unsolved_problem/the_uninitiated/built_to_fail, the states driving "
    "the original overshoot concern -- though it does share with "
    "the_broken_compass/narrative_lock, both already in Track A's SEVER-13 "
    "group, so the same magnitude-capping discipline would apply there "
    "instead if ever revisited). Q03A's shared blast radius is structural to "
    "the question (state_targets is question-level, not option-level) -- "
    "switching Q03A's selected option would not reduce sharing. Revisit "
    "together with the rest of the PHASE-2-PENDING work once Phase 2 is "
    "live, not before. ALL-DB-01/decision_blindness, "
    "EXP-SDB-01/sequential_decision_blindness (Q31, INERT/PHASE-2-PENDING) "
    "-- selection-logic fix already committed (44e85fc) and correct, but "
    "Q31 itself never fires for a real respondent today -- reclassified "
    "PHASE-2-PENDING, not urgent, no further action needed until Phase 2. "
    "Bucket 2 (\"wired, insufficient magnitude\") -- Track A (duration_band "
    "additions), full live-reachability pass this session, not assumed: "
    "SEVER-13(Q32)/SEVER-08(Q26)/SEVER-11(Q28)/SEVER-07(Q25)/SEVER-02(Q20)/"
    "SEVER-10(Q27B)/SEVER-03(Q21)/SEVER-01(Q16)/SEVER-12(Q29)/SEVER-05(Q23) "
    "-- all 10 confirmed LIVE. SEVER-09(Q27A) -- confirmed INERT, "
    "reclassified PHASE-2-PENDING (not part of the live Track A count). "
    "Full question content, options, and blast-radius tables for all 10 "
    "live questions at tools/diag_bucket2_track_a_questions.md (untracked "
    "working reference, Claude.ai content-authoring handoff). Track B "
    "(AUT-PS-01/Q23 -- resolved above; ATT-BC-02/Q03A -- parked above), "
    "full detail at tools/diag_bucket2_track_b_questions.md. Severity "
    "aggregation confirmed additive in real production code (engine/main.py's "
    "run_accumulated_engine() -> SeverityEngine.add_input() per fired "
    "trigger, engine/severity.py's compute_raw_severity() sums all inputs) "
    "-- real compounding-overshoot risk exists if a new follow-on's content "
    "also reaches full duration_band=18mo_plus magnitude while sharing a "
    "question with an already-fired trigger; safe if capped at the typical "
    "raw<=1.00 shape. Bucket 3 (\"not wired at all,\" 49 profiles) -- "
    "unchanged, not yet investigated for live-reachability -- apply the same "
    "LIVE-REACHABLE/PHASE-2-PENDING split when this is taken up, explicitly "
    "flagged as its own dedicated future session given its size."
)

NEW_ITEM_3 = (
    "3. Severity-tier expectation/reachability gap -- Track A (10 "
    "duration_band additions across all confirmed LIVE-REACHABLE follow-on "
    "questions: SEVER-13/08/11/07/02/10/03/01/12/05) CLOSED this session, "
    "commit 55f0bbe -- full detail in Section 16's session log. 28 of 33 "
    "targeted profiles now reach their locked expected.severity_tier via "
    "real content; 169/172 baseline unchanged (same 3 pre-existing gaps, "
    "verified per-state). ATT-DC-01 confirmed reaching Endemic via "
    "SEVER-01+SEVER-12 firing together. AUT-PS-01 (Action 1 + SEVER-05) "
    "confirmed reaching Entrenched via the real production engine path "
    "(tools/test_aut_ps_01_q23_d_forced.py) -- correctly absent from the "
    "standard harness's changed list since best_option_for_state() still "
    "can't select Q23's option D, unrelated to SEVER-05's fix, expected not "
    "a gap. Real bug caught and fixed along the way: generate_answers() was "
    "double-splicing SEVER-11 for states wired to both Q28 and Q31 "
    "(AUT-UP-01/02/03), producing incorrect raw=4.00/Endemic instead of "
    "correct raw=2.00/Entrenched -- fixed with a dedup guard matching the "
    "live app's severityFollowOnAlreadyAsked(), which the harness lacked. "
    "STANDING NOTE: second confirmed instance of the calibration harness "
    "and the live app silently diverging on shared logic (first: the "
    "write_log.jsonl scope gap surfaced during the MemPalace investigation) "
    "-- worth a deliberate spot-check against live-app guards whenever "
    "touching shared severity-splice logic again, not assumed automatic "
    "going forward. OPEN, new and smaller: 5 profiles (ALL-FR-01, "
    "ALL-SI-01, APT-BF-01, ATT-GD-01, ATT-NL-01) confirmed genuinely short "
    "-- all Endemic-expected, capped at Entrenched (raw 2.00) with only one "
    "fireable trigger each, structurally the same two-trigger-needed "
    "pattern ATT-DC-01 already resolved -- needs either a second "
    "independent trigger identified for each, or a tier-expectation "
    "reconsideration; Pete's call, not resolved here. OPEN, "
    "PHASE-2-PENDING: SEVER-09 (the_second_close, routes via inert Q27A) is "
    "the one Track A item still not live -- parked with the rest of that "
    "category. OPEN, PARKED: ATT-BC-02/Q03A (prior session, Pete's "
    "explicit instruction, rationale on record there). OPEN, UNTOUCHED: "
    "Bucket 3 (49 profiles, not wired at all) -- not yet investigated for "
    "live-reachability, apply the same LIVE-REACHABLE/PHASE-2-PENDING "
    "split whenever taken up, explicitly flagged as its own dedicated "
    "future session given its size."
)

edit("tools/_mob.txt", OLD_ITEM_3, NEW_ITEM_3)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.115",
    "\\\\\\#\\\\\\# MOB v4.116",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Track A (10 duration_band additions) CLOSED, real "
    "harness double-splice bug caught and fixed, commit 55f0bbe | Content "
    "for all 10 confirmed LIVE-REACHABLE severity follow-on questions "
    "(SEVER-13/08/11/07/02/10/03/01/12/05) drafted on Claude.ai (style "
    "precedent SEVER-06), added to engine/data/questions.py. SEVER-05 "
    "required a third edit beyond the other 9 -- a per-option _opt_contrib "
    "override unique to it, which would have KeyError'd at import time "
    "without an explicit new-option entry; matched to its existing "
    "\"Weak/untested\" category (same as its C/D options). Confirmed "
    "empirically, not assumed, that content alone changes nothing (0/172 "
    "profiles moved) -- generate_answers()'s severity splice is gated "
    "entirely by _SEVERITY_FOLLOW_ON_TARGETS; expanded it with 33 "
    "new/updated entries (all targeting the new \"18mo_plus\" option, "
    "including updating ALL-DB-01/EXP-SDB-01's existing entries from their "
    "old True/named_condition target). That surfaced a real, previously-"
    "latent bug: AUT-UP-01/02/03 (the_unsolved_problem) are wired to both "
    "Q28 and Q31, and since the Bucket 1 Q31 tie-break fix (44e85fc) both "
    "now select a severity_trigger=True option routing to the same "
    "follow-on, SEVER-11 -- generate_answers() spliced it in twice, "
    "confirmed directly in the answer list, double-counting raw "
    "contribution to 4.00/Endemic instead of the correct single-count "
    "2.00/Entrenched. The real live app already guards against exactly "
    "this (severityFollowOnAlreadyAsked(), web/lib/session-store.ts, the "
    "\"dual-parent\" case its own header comment documents) -- the "
    "calibration harness simply lacked the equivalent. Fixed with a "
    "matching dedup guard (a local already-spliced-follow-ons set, checked "
    "before each splice). Re-verified: same 33 profiles changed, no new "
    "ripple, AUT-UP-01/02/03 now correctly land on Entrenched. Full "
    "172-profile byte-for-byte regression: 33 profiles changed, all "
    "intended, zero elsewhere; 28/33 now reach locked expected tier; 5 "
    "(ALL-FR-01, ALL-SI-01, APT-BF-01, ATT-GD-01, ATT-NL-01) confirmed "
    "genuinely short -- Endemic-expected, only one fireable trigger each, "
    "capped at Entrenched -- logged as a new, smaller open item, "
    "structurally the same two-trigger pattern ATT-DC-01 needed and got "
    "(SEVER-01+SEVER-12, confirmed reaching Endemic). AUT-PS-01 "
    "re-verified via tools/test_aut_ps_01_q23_d_forced.py, updated to "
    "target the new option -- confirmed reaching Entrenched via the real "
    "engine/main.py production path; correctly does not appear in the "
    "standard harness's changed list since best_option_for_state() still "
    "cannot select Q23's option D (a separate, already-settled mechanism "
    "from Bucket 1's \"path c\" decision -- SEVER-05's new content doesn't "
    "change Q23's own selection game). 169/172 baseline unchanged, same 3 "
    "pre-existing gaps (identity_erosion, the_untouchable, "
    "transition_paralysis, each 2/3) verified per-state, not just "
    "aggregate. All other Python test suites (severity, output, "
    "accumulation, output_synthesis, main) re-run clean. STANDING NOTE for "
    "future severity-splice work: this is the second confirmed instance of "
    "the calibration harness and the live app silently diverging on shared "
    "logic -- first was write_log.jsonl's scope gap (only ever logged "
    "diary_write, never mine operations) surfaced during the MemPalace "
    "investigation. Worth a deliberate spot-check against live-app guards "
    "whenever touching shared severity-splice logic again, not assumed "
    "automatic. MOB version bumped v4.115 → v4.116 per standing protocol "
    "-- a real Bucket 2 batch closed with a genuine bug fix, standing "
    "cross-check note added, two new smaller open items logged precisely. "
    "| This session (Claude Code) | MOB v4.116 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.115 |",
    "| This session (Claude Code) | MOB v4.115 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.115 |",
    "| MOB version | v4.116 |",
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
