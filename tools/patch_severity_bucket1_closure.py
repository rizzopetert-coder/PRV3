"""
PRV3 MOB Update -- Severity reachability Bucket 1 closure (Q31 tie-break fix)

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: rewritten to reflect Bucket 1
    closing at zero cleanly-resolved-by-selection-alone, the Q31 fix (commit
    44e85fc), and Bucket 2 growing from 32 to 36.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.113 -> v4.114 (Tier 1 finding closed, real mechanism now
    on permanent record, Bucket 2 scope changed materially).

Updates CLAUDE.md:
  - MOB version cross-reference v4.113 -> v4.114.

Usage:
  python tools/patch_severity_bucket1_closure.py --dry-run
  python tools/patch_severity_bucket1_closure.py --write
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
    "3. Severity-tier expectation/reachability gap, 85 of 172 profiles -- discovered during the severity follow-on calibration reopen. 18 profiles expect Endemic, 66 expect Entrenched, both structurally unreachable because their target_state has zero real severity-trigger wiring reaching that expectation (either not wired to any severity-triggering core-question option, or best_option_for_state() doesn't select the triggering option for that state). 1 additional profile (ATT-DC-01, the_diversity_ceiling) is capped at Entrenched (raw=2.0 max via its two real triggers) but expects Endemic (needs raw>=4.0) -- short by one trigger's worth of wiring. This is a content/wiring gap in engine/data/questions.py's severity-trigger assignments, or a spec gap in the 172-profile expected values themselves (unclear which without further investigation) -- not a calibration-harness mechanism problem, which the 4-profile build above proves works correctly. Full state list and per-profile reachability data captured in this session's investigation, available on request. Needs Pete's direction: (a) wire more severity triggers into questions.py to make more states reachable, (b) revise the 85 profiles' expected values to match real reachability, or (c) some combination -- genuinely undetermined which is correct without Pete's input on what the spec should represent. Scope: likely a full dedicated future session, not an incremental add-on."
)

NEW_ITEM_3 = (
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

edit("tools/_mob.txt", OLD_ITEM_3, NEW_ITEM_3)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.113",
    "\\\\\\#\\\\\\# MOB v4.114",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Severity reachability Bucket 1 closed at zero "
    "selection-only fixes; Q31 tie-break bug found and fixed, commit "
    "44e85fc | Full detail in Section 13b's Priority Queue item 3. Traced "
    "all 4 \"wired, not selected\" profiles individually rather than "
    "assuming a shared root cause -- confirmed 2 have no selection bug "
    "(AUT-PS-01/paper_shield, ATT-BC-02/the_burned_credibility: the trigger "
    "option genuinely scores lower on the state's dimension, a content "
    "question, not code) and 2 share a genuine Q31 tie-break bug "
    "(ALL-DB-01/decision_blindness, EXP-SDB-01/sequential_decision_blindness: "
    "three dimensionally-identical options existed, Python's max() "
    "arbitrarily kept the non-trigger one). Fixed best_option_for_state() "
    "to prefer a severity_trigger=True option on a tie only when fully "
    "dimensionally identical to the otherwise-selected option across every "
    "field -- confirmed via a full QUESTION_LIBRARY sweep before "
    "implementing that a naive \"prefer trigger on any tie\" rule would "
    "have rippled into two other, unrelated ties (Q03A/the_second_close, "
    "Q20/decision_paralysis) that differ on other dimensional fields; the "
    "full-identity requirement deliberately excludes both. Full 172-profile "
    "byte-for-byte regression: 169/172 unchanged, exactly 9 profiles "
    "touched (Q31's 3 wired states x 3 profile types), zero ripple to the "
    "two excluded ties. ALL-DB-01/EXP-SDB-01 added to "
    "_SEVERITY_FOLLOW_ON_TARGETS (SEVER-11) so the harness genuinely "
    "exercises the now-reachable trigger -- confirmed NOT sufficient alone "
    "to reach their locked Entrenched tier, since SEVER-11 has no "
    "duration_band option (ceiling raw=1.0/Emerging). The fix is kept "
    "regardless -- a real, independent correction matching what a real "
    "respondent selecting the trigger option would experience, not "
    "contingent on flipping any profile's pass/fail. Net finding: every "
    "real gap in Bucket 1 traced to content, not code -- the selection-"
    "logic layer is sound. Bucket 1 (4 profiles) closes at zero "
    "selection-only resolutions; all 4 fold into Bucket 2, which grows from "
    "32 to 36. Bucket 3 (49, not wired at all) unchanged. MOB version "
    "bumped v4.113 → v4.114 per standing protocol -- Tier 1 finding closed, "
    "real mechanism on permanent record, Bucket 2 scope changed "
    "materially. | This session (Claude Code) | MOB v4.114 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.113 |",
    "| This session (Claude Code) | MOB v4.113 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.113 |",
    "| MOB version | v4.114 |",
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
