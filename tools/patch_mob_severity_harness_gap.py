"""
PRV3 MOB Update -- Severity follow-on wiring (Path 1) shipped + new
test-harness prerequisite logged

Updates tools/_mob.txt:
  - Section 14 (Locked Decisions Log): new entry appended after the
    Category B entry (ascending order, this section's newest tail)
  - Section 16 (Session Log): new one-line entry prepended before the
    Category B log line (descending order, this section's newest head)
  - Version bump v4.56 -> v4.57 (material workstream status change --
    severity follow-ons wired for Path 1 for the first time in this
    project's history, plus a new named prerequisite logged)

Updates CLAUDE.md:
  - MOB version cross-reference v4.56 -> v4.57

Documentation-only change -- no product code touched by this script.
(Product code change already committed separately: 03b40a6.)

Usage:
  python tools/patch_mob_severity_harness_gap.py --dry-run
  python tools/patch_mob_severity_harness_gap.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ═══════════════════════════════════════════════════════════════════════════
# tools/_mob.txt
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.56",
    "\\\\\\#\\\\\\# MOB v4.57",
)

# --- Section 14 (Locked Decisions Log, ascending -- append after newest tail) ---

CATB_ENTRY_TAIL = (
    "**Consolidated finding, logged as a single named prerequisite rather than "
    "three separate footnotes:** the severity-follow-on gap (SeverityEngine.add_input() "
    "never called in either orchestrator, confirmed across Category A and this "
    "session) is now a confirmed blocker across 2.5 of 5 candidate dimensions "
    "surfaced this session -- Trajectory (Category A), Reversibility/Momentum, "
    "and the severity_scalar half of Urgency Window. Worth its own scoping pass "
    "as a single prerequisite (wire real severity follow-on collection into an "
    "orchestrator) rather than being tracked as three independent blockers that "
    "happen to share a root cause. MOB v4.56. |"
)

SEVERITY_WIRING_ENTRY = (
    "| **July 2026 — Severity follow-on wiring shipped (Path 1), new test-"
    "harness prerequisite identified** | Gemini-approved handoff executed in "
    "three parts. **Tagging (engine/data/questions.py):** all 13 SEVER-01..13 "
    "follow-on questions' answer options tagged with severity_input_mapping, "
    "mapping each option to one of the 5 real SeverityInput fields "
    "(duration_band, population_band, prior_failed_resolution, "
    "financial_indicators, named_condition), following the same per-option "
    "lookup pattern already used by _axis_tags -- zero changes to the _QDATA "
    "tuple schema. Fit confidence flagged per question, not smoothed over: "
    "STRONG direct fit for 7 of 13 (SEVER-01/02/03/04/06/07/11), MODERATE "
    "reinterpreted fit for 3 (SEVER-05/09/10), WEAK stretch fit for 2 "
    "(SEVER-08/12), and SEVER-13 non-discriminating (all 4 options map to the "
    "same value -- the question only fires on already-unactioned feedback, so "
    "firing at all carries the signal, not which option is chosen). SEVER-13 "
    "confirmed in scope (questions.py's 13 governs over severity.py's stale "
    "'SEVER-01 through SEVER-12' docstring). **Runtime wiring (engine/main.py):** "
    "accumulate_one_answer() detects severity_input_mapping and constructs a "
    "real SeverityInput-shaped dict (new trigger_question_id param, defaults "
    "to the follow-on's own ID when not supplied); run_accumulated_engine() "
    "accepts a new severity_inputs list and calls SeverityEngine.add_input() "
    "per entry before scoring -- None/[] preserves the original zero-input "
    "behavior exactly. Path B untouched, confirmed permanently 'Emerging' by "
    "design, per engine/main.py's own docstring (AccumulationEngine/rank_states "
    "deliberately bypassed, no real Q&A to derive a vector from). **KNOWN "
    "CALLER IMPACT, flagged not silently patched:** accumulate_one_answer()'s "
    "return shape changed from a bare accumulated_vector dict to "
    "{accumulated_vector, severity_input} -- api/engine.py's /api/accumulate "
    "route and its Next.js caller still expect the old bare-vector shape and "
    "need a companion update (plus web/lib/session-store.ts splice wiring, "
    "mirroring the Phase 2 checkpoint pattern) before Path 1 is live-"
    "functional for severity. Not touched this pass -- scope was engine/main.py "
    "only. **Testing:** 7 new checks in tools/test_main.py (34/0). Zero "
    "regressions across test_accumulation.py, test_output.py, "
    "test_checkpoint.py, test_severity.py, test_resolution_families.py, and "
    "the full 172-profile v23 suite (169/172 unchanged, confirmed empirically "
    "-- this code path never calls the two changed functions so was never at "
    "risk, but verified rather than assumed). test_contract.py's pre-existing "
    "unrelated 'liability_block' KeyError confirmed unchanged. **Hand-verified "
    "two real end-to-end sessions via the actual modified functions, not "
    "reimplemented logic:** 1x SEVER-04 answer (duration_band=18mo_plus) -> "
    "raw=2.0 -> score=33.33 -> tier=Entrenched; SEVER-04 + SEVER-06 both "
    "18mo_plus -> raw=4.0 -> score=66.67 -> tier=Endemic. First non-'Emerging' "
    "severity tier ever produced in this project's history. **CALIBRATION "
    "TARGET exposure, confirmed not assumed:** named_condition/"
    "financial_indicators/population_band tested in isolation (no "
    "duration_band) all produce the identical score regardless of value -- "
    "POPULATION_WEIGHTS and the three additive weights (PRIOR_FAILED_"
    "RESOLUTION_WEIGHT, FINANCIAL_INDICATOR_WEIGHT, NAMED_CONDITION_WEIGHT) "
    "are still None (CALIBRATION TARGET) in severity.py, a pre-existing gap "
    "predating this work and out of scope to populate here -- today, severity "
    "tier variation is driven entirely by duration_band. Commit 03b40a6. "
    "**Severity tier validation built (tools/severity_tier_validation.py), "
    "standalone and additive -- calibration_runner.py's _build_suite_v23() "
    "dispatch and the tracked 169/172 baseline untouched, confirmed via git "
    "status.** Reuses evaluate_pass_criteria()'s tier-comparison logic "
    "(Emerging/Entrenched +/-1 tolerance, Endemic exact-match) restricted to "
    "the subset of profiles that already pass under the current v23 criteria. "
    "**Result: 150 of 169 v23-passing profiles match expected severity tier "
    "-- reported as its own distinct number, never merged with 169/172.** All "
    "19 mismatches are Endemic-expected high_confidence profiles. **Root-cause "
    "finding, the more important result than the count itself:** distinct "
    "actual severity tiers observed across all 172 profiles is {'Emerging'} "
    "only -- confirmed via direct read of generate_answers() "
    "(tools/calibration_runner.py:187-230) that it iterates core questions "
    "only and never answers a triggered SEVER-## follow-on, so "
    "severity_inputs is empty for every profile regardless of the Path 1 "
    "engine wiring now being correct. The uniform mismatch pattern (100% of "
    "Endemic-expected profiles fail, 0% of Emerging/Entrenched fail) is itself "
    "diagnostic -- a real weight-calibration problem would produce a mixed "
    "signature (some Endemic profiles clearing the threshold, others falling "
    "short); this clean split is the signature of zero severity signal being "
    "generated at all, not of weights that are close-but-wrong. duration_band's "
    "weight values (1.0/1.5/2.0) remain genuinely untested by this or any "
    "check against the current harness. **New prerequisite logged, named and "
    "distinct from the now-resolved orchestrator-wiring prerequisite:** "
    "extending generate_answers() to simulate answering triggered severity "
    "follow-ons is required before duration_band or any other severity weight "
    "can be calibrated against real profile data -- a test-harness gap one "
    "level up from the severity-follow-on-orchestrator-wiring prerequisite "
    "this same entry resolves for Path 1. Not actioned, not scoped further "
    "here. MOB v4.57. |"
)

edit("tools/_mob.txt", CATB_ENTRY_TAIL, CATB_ENTRY_TAIL + "\n" + SEVERITY_WIRING_ENTRY)

# --- Section 16 (Session Log, descending -- prepend before newest head) ---

CATB_LOG_HEAD = (
    "| **July 2026 — Category B: SPOF shipped, Reversibility/Urgency Window "
    "held** | compute_causation_pattern() built in engine/output.py, reusing "
    "Cascade Risk's dispersion term (extracted to compute_liability_dispersion() "
    "in accumulation.py), commit bace548. Full 172-profile suite unchanged at "
    "169/172, zero regressions, 20 new tests. Hand-verified on one real Path 1 "
    "and one real Path B case. Reversibility/Momentum held on the same "
    "severity-follow-on prerequisite as Trajectory; Urgency Window held on that "
    "same prerequisite plus a separate friction-tax multiplier/band calibration "
    "gap (STATE_MULTIPLIERS, _ORG_SIZE_BANDS all None today). Severity-follow-on "
    "gap now a confirmed blocker across 2.5 of 5 candidate dimensions -- flagged "
    "as one consolidated prerequisite worth its own scoping pass. Full detail in "
    "Section 14. MOB v4.56. |"
)

SEVERITY_WIRING_LOG_LINE = (
    "| **July 2026 — Severity follow-on wiring shipped (Path 1), new test-"
    "harness prerequisite** | All 13 SEVER-## questions tagged with "
    "severity_input_mapping (engine/data/questions.py); accumulate_one_answer() "
    "and run_accumulated_engine() wired to construct real SeverityInput objects "
    "and call add_input() (engine/main.py), commit 03b40a6. First non-"
    "'Emerging' severity tier ever produced, hand-verified (Entrenched and "
    "Endemic cases). api/engine.py's /api/accumulate route needs a companion "
    "update before Path 1 is live-functional for severity -- flagged, not "
    "fixed this pass. Standalone tools/severity_tier_validation.py (169/172 "
    "v23 baseline untouched) found 150/169 match expected tier, but the real "
    "finding is that generate_answers() never simulates severity follow-on "
    "answers -- a new, named test-harness prerequisite, distinct from and one "
    "level up from the now-resolved orchestrator-wiring prerequisite. Full "
    "detail in Section 14. MOB v4.57. |"
)

edit("tools/_mob.txt", CATB_LOG_HEAD, SEVERITY_WIRING_LOG_LINE + "\n" + CATB_LOG_HEAD)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.56 |",
    "| MOB version | v4.57 |",
)


# ---------------------------------------------------------------------------

def apply(dry_run: bool):
    changed_files: dict[str, str] = {}
    errors = []

    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = changed_files.get(rel_path)
        if text is None:
            if not path.exists():
                errors.append(f"MISSING FILE: {rel_path}")
                continue
            text = path.read_text(encoding="utf-8")

        count = text.count(old)
        if count != 1:
            errors.append(
                f"{rel_path}: expected 1 match, found {count}\n"
                f"  --- anchor (first 160 chars) ---\n  {old[:160]!r}"
            )
            continue

        changed_files[rel_path] = text.replace(old, new, 1)

    print("=" * 72)
    print(f"MOB SEVERITY-HARNESS-GAP PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"Files touched: {len(changed_files)}")
    for rel_path in changed_files:
        print(f"  - {rel_path}")

    if errors:
        print("\nERRORS:" if dry_run else "\nERRORS — nothing written:")
        for e in errors:
            print(f"\n[ERROR] {e}")
        if not dry_run:
            sys.exit(1)
        return

    if dry_run:
        print("\nDry run OK — all anchors matched exactly once. No files written.")
        return

    for rel_path, text in changed_files.items():
        (REPO_ROOT / rel_path).write_text(text, encoding="utf-8")
    print("\nAll files written.")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
