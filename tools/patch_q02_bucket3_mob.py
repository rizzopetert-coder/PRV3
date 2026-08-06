"""
PRV3 MOB Update -- Bucket 3 scoping pass + Q02/SEVER-15 fix (commit b0f0a2b)

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    "OPEN, UNTOUCHED: Bucket 3" tail with the completed scoping-pass
    summary + the first Bucket 3 fix closed, running total 33/85.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.117 -> v4.118.

Updates CLAUDE.md:
  - MOB version cross-reference v4.117 -> v4.118.

Usage:
  python tools/patch_q02_bucket3_mob.py --dry-run
  python tools/patch_q02_bucket3_mob.py --write
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
    "OPEN, UNTOUCHED: Bucket 3 (49 profiles "
    "not wired at all, plus APT-BF-01/ATT-GD-01/ATT-NL-01 added this "
    "session -- 52 total) -- not yet investigated for live-reachability, "
    "apply the same LIVE-REACHABLE/PHASE-2-PENDING split whenever taken "
    "up, explicitly flagged as its own dedicated future session given its "
    "size."
)

NEW_TAIL = (
    "RESOLVED, Bucket 3 scoping: data-gathering pass complete "
    "(tools/diag_bucket3_52profiles.md) -- 52 profiles collapse to 31 "
    "distinct states: 2 category (a) (zero live questions wired at all, "
    "needs new question design, Gemini architecture-review gate, not "
    "drafted), 26 category (b) (live question(s) wired but untriggered, "
    "cheaper fix -- new trigger + SEVER-## follow-on), 3 category (c) "
    "(the APT-BF-01/ATT-GD-01/ATT-NL-01 folded-in profiles, already "
    "understood from the two-trigger-gap investigation, not a new "
    "anomaly). First Bucket 3 fix CLOSED and committed (commit b0f0a2b): "
    "Q02 options C/D confirmed as a full-field-identical tie (same "
    "mechanism as Q09/ALL-FR-01/ALL-SI-01) -- flipped D's "
    "severity_trigger, new SEVER-15 follow-on grounded in D's existing "
    "\"Absent -- no dedicated HR function\" framing. Closes AUT-EX-01 "
    "(the_exposed), EXP-PAG-01 (planning_authority_gap), and AUT-HC-02 "
    "(hr_capture) outright, all reaching their locked Entrenched tier. "
    "AUT-HC-01 (hr_capture, Endemic-expected) correctly lands short at "
    "Entrenched (raw 2.00, confirmed via normalized score, no "
    "double-count) -- its second trigger, candidate Q04, is separate "
    "future work, not part of this fix. Running Bucket 2/3 total: 33 of "
    "the original 85 Entrenched/Endemic-expected profiles now closed (28 "
    "Track A + 2 ALL-FR-01/ALL-SI-01 + 3 this fix). OPEN: 25 category (b) "
    "states remain, each needing its own collateral-blast-radius review "
    "before implementation -- proceeding one state at a time, same "
    "discipline as tonight, not batched. 2 category (a) states remain "
    "untouched pending a dedicated Gemini scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.117",
    "\\\\\\#\\\\\\# MOB v4.118",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Bucket 3 scoping pass complete, first Bucket 3 fix "
    "(Q02/SEVER-15) closed and committed, commit b0f0a2b | Full detail in "
    "Section 13b's Priority Queue item 3. Bucket 3 data-gathering "
    "(tools/diag_bucket3_52profiles.py/.md, read-only, same discipline as "
    "Buckets 1/2): 52 profiles collapse to 31 distinct states -- 2 "
    "category (a) (invisible_performance_management, transition_paralysis "
    "-- zero live questions wired at all), 26 category (b) (live but "
    "untriggered), 3 category (c) (built_to_fail/groundhog_day/"
    "narrative_lock, the folded-in two-trigger-gap profiles -- confirmed "
    "each already has exactly the one known live trigger on record, not "
    "a new finding). Leverage-ranked the 26 category (b) states by "
    "profile count; found every high-count state (the_paper_tiger, "
    "leadership_deafness, motivational_architecture_failure, etc.) routes "
    "through heavily-shared hub questions (Q04/Q05/Q06/Q11/Q12/Q18) with "
    "wide collateral exposure -- no easy batch win at the top of that "
    "list. Pete redirected to one-state-at-a-time review instead of "
    "batching. Scanned all 26 for smallest/cleanest blast radius "
    "(candidate-question sharing count, not profile-count leverage): "
    "the_exposed and planning_authority_gap tied cleanest at 2 other "
    "states each, and uniquely at zero EXTERNAL exposure -- both states' "
    "only live question is Q02, whose full state_targets is exactly "
    "[the_exposed, hr_capture, planning_authority_gap], all three already "
    "inside this investigation. Full workup confirmed: Q02 options C/D "
    "are a full-field-identical tie (aptitude_liability 0.3, "
    "authority_liability 0.6, verified via best_option_for_state() "
    "directly both before and after the fix), all three states already "
    "select C by list-order; D's existing text (\"Absent -- we don't have "
    "a dedicated HR function right now\") already reads as more severe "
    "than C (\"Thin -- part-time or shared\"), same shape as Q09's E/C, "
    "no new option needed. Implemented: flipped D's severity_trigger to "
    "True, added new SEVER-15 (\"How long has your organization been "
    "without a dedicated HR function?\", duration_band up to 18mo_plus), "
    "extended _SEVERITY_FOLLOW_ON_TARGETS for AUT-EX-01, EXP-PAG-01, "
    "AUT-HC-01, AUT-HC-02. Verified directly (not assumed) that the "
    "already-shipped Bucket 1 tie-break rule (44e85fc) reroutes all "
    "three states from C to D automatically post-fix. Full 172-profile "
    "byte-for-byte regression: exactly 4 profiles changed (AUT-EX-01, "
    "EXP-PAG-01, AUT-HC-01, AUT-HC-02), nothing else moved -- 169/172 "
    "baseline confirmed unchanged, same 3 pre-existing gaps. AUT-EX-01, "
    "EXP-PAG-01, AUT-HC-02 (all Entrenched-expected) now correctly reach "
    "Entrenched. AUT-HC-01 (Endemic-expected) reaches Entrenched only -- "
    "confirmed via normalized severity score (33.33, identical to the "
    "other three, i.e. a single trigger's raw 2.00, not a double-count) "
    "that it's landing correctly short rather than silently passing or "
    "overshooting; its second trigger (candidate Q04, own wider blast "
    "radius) is out of scope, logged as separate future work. All 5 "
    "Python test suites re-run clean (severity 56/56, output 112/112, "
    "accumulation 47/47, output_synthesis 53/53, main 36/36). One "
    "process note: the calibration_runner.py edit was initially made "
    "directly instead of through a dry-run patch script -- caught before "
    "any further action, reverted, and redone properly through "
    "tools/patch_q02_severity_targets.py; both patch scripts dry-ran "
    "clean before writing. Committed as engine/data/questions.py, "
    "tools/calibration_runner.py, tools/patch_q02_sever15.py, "
    "tools/patch_q02_severity_targets.py (commit b0f0a2b). Running "
    "Bucket 2/3 total: 33 of the original 85 Entrenched/Endemic-expected "
    "profiles now closed. MOB version bumped v4.117 → v4.118 per "
    "standing protocol -- Bucket 3 scoping closed, first Bucket 3 fix "
    "shipped with the same one-state-at-a-time discipline established "
    "this session, 25 category (b) states remain for future review. | "
    "This session (Claude Code) | MOB v4.118 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.117 |",
    "| This session (Claude Code) | MOB v4.117 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.117 |",
    "| MOB version | v4.118 |",
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
