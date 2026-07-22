"""
PRV3 MOB Update -- Category B: SPOF vs. Diffuse Causation shipped

Updates tools/_mob.txt:
  - Section 14 (Locked Decisions Log): new entry appended after the
    Category A entry (ascending order, this section's newest tail)
  - Section 16 (Session Log): new one-line entry prepended before the
    Category A log line (descending order, this section's newest head)
  - Version bump v4.55 -> v4.56 (material workstream status change --
    SPOF shipped, severity-follow-on gap consolidated into a single
    named prerequisite across three candidate dimensions)

Updates CLAUDE.md:
  - MOB version cross-reference v4.55 -> v4.56

Documentation-only change -- no product code touched by this script.
(Product code change already committed separately: bace548.)

Usage:
  python tools/patch_mob_category_b_spof.py --dry-run
  python tools/patch_mob_category_b_spof.py --write
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
    "\\\\\\#\\\\\\# MOB v4.55",
    "\\\\\\#\\\\\\# MOB v4.56",
)

# --- Section 14 (Locked Decisions Log, ascending -- append after newest tail) ---

CATA_ENTRY_TAIL = (
    "Also confirmed Path 1's Redis session state (DiagnosticSession, AnswerLogEntry "
    "in web/lib/session-store.ts) carries no usable duration/progression signal "
    "either -- no created_at or started_at field anywhere in session state, the "
    "only timestamp in the system is AnonymizedCompletion.completed_at, written "
    "post-completion to a separate aggregate list, disconnected from "
    "assemble_output()'s already-completed call. **Prerequisite identified, not "
    "actioned:** wiring severity follow-on collection into an orchestrator (real "
    "add_input() calls populating duration_band) is its own separate, unscoped "
    "piece of work. Do not revisit Trajectory until that prerequisite is scoped "
    "and built on its own. Category B (reversibility/momentum, SPOF routing, "
    "urgency window/Friction Tax) remains queued as a separate follow-on "
    "handoff, held pending Pete's sequencing confirmation. MOB v4.55. |"
)

CATB_ENTRY = (
    "| **July 2026 — Category B pre-check + SPOF shipped, Reversibility/Urgency "
    "Window held** | Ran the same input-verification pass used for Trajectory "
    "across all three Category B candidates before writing any implementation "
    "code, per Pete's explicit instruction. **Reversibility/Structural Momentum: "
    "BLOCKED, same prerequisite as Trajectory.** Confirmed Gemini's original "
    "scoping depends on severity.tier's qualitative variation (Entrenched "
    "'workarounds' vs. Endemic 'operating environment' language) as the "
    "reweighting justification -- and confirmed (again, this pass) that both "
    "orchestrators score SeverityEngine with zero inputs, so tier is always "
    "'Emerging' on Path 1 as well as Path B, not just Path B as Category A "
    "established. No tier variation exists anywhere to reweight against. Holding, "
    "not rebuilt on accumulated_vector alone -- that would be a different "
    "mechanism than what Gemini actually reviewed, a rescoping question, not a "
    "unilateral substitution. **Urgency Window/Friction Tax: BLOCKED on a "
    "compound, different prerequisite.** engine/friction_tax.py confirmed: every "
    "STATE_MULTIPLIERS entry (57/57) and every _ORG_SIZE_BANDS band_low (5/5) is "
    "None -- compute_friction_tax() returns calibration_complete=False for every "
    "state, every org size, every session, today. A friction-tax multiplier/band "
    "calibration gap (McKinsey/SHRM/Gallup research population, Pete's task per "
    "the file's own docstring), layered on top of the same tier-flatness problem "
    "(severity_scalar is always 0.6 since tier never varies). **SPOF vs. Diffuse "
    "Causation: SHIPPED, real and buildable, commit bace548.** New "
    "compute_causation_pattern() in engine/output.py classifies each session from "
    "two already-real, already-populated signals -- no new math: "
    "routing.qualified_states count (0 -> insufficient_signal, 2+ -> diffuse, "
    "both populated on Path A and Path B since every session runs "
    "OutputEngine.build()) and, only as a tiebreak when exactly one state "
    "qualifies, the identical Shannon-entropy dispersion term Cascade Risk "
    "already uses -- extracted into a shared compute_liability_dispersion() in "
    "engine/accumulation.py so the two functions share one implementation rather "
    "than duplicating the entropy math. Refactor verified behavior-preserving via "
    "a new equivalence test (compute_cascade_risk(v) == dispersion(v) * "
    "intensity(v) across every existing fixture). CAUSATION_DISPERSION_THRESHOLD "
    "(0.5) marked CALIBRATION TARGET. Not wired into assemble_output() -- pure "
    "derived-output helper, same convention as Cascade Risk. 20 new tests (8 in "
    "tools/test_accumulation.py, 12 in tools/test_output.py). Full 172-profile "
    "calibration suite unchanged at 169/172, zero regressions; test_main.py "
    "(27/0), test_checkpoint.py, test_resolution_families.py (101/0), "
    "test_severity.py all clean (test_contract.py's pre-existing 'liability_block' "
    "KeyError confirmed unrelated via git stash, not a regression from this "
    "work). **Hand-verified against one real Path 1 case and one real Path B "
    "case, through the actual pipeline, not synthetic fixtures:** a real "
    "high_confidence/the_unformed_leader profile (routing.mode=multi, 4 "
    "qualified) returned diffuse/dispersion=0.9669/cascade_risk=0.6493, genuine "
    "computed signal; a real Path B run (selectedStateIds=[built_to_fail, "
    "the_paper_tiger], accumulated_vector={} exactly as main.py's run_engine() "
    "passes it) returned diffuse/dispersion=0.0/cascade_risk=0.0, confirming "
    "empirically -- not just by reading the code -- that Path B's pattern value "
    "is driven entirely by how many states the principal self-selected, the "
    "same known limitation Cascade Risk already carries there. "
    "accumulated_vector={} on Path B reconfirmed intentional per engine/main.py's "
    "own docstring (AccumulationEngine and rank_states deliberately bypassed, no "
    "real Q&A sequence to derive a vector from) -- not an overlooked gap. "
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

edit("tools/_mob.txt", CATA_ENTRY_TAIL, CATA_ENTRY_TAIL + "\n" + CATB_ENTRY)

# --- Section 16 (Session Log, descending -- prepend before newest head) ---

CATA_LOG_HEAD = (
    "| **July 2026 — Category A: Cascade Risk shipped, Trajectory blocked** | "
    "compute_cascade_risk() built in engine/accumulation.py (dispersion via "
    "checkpoint.py's entropy technique, intensity normalized against locked "
    "MC_CENTROID_39), commit 787a4e1. Full 172-profile suite unchanged at "
    "169/172, zero regressions, 9 new tests. Trajectory formally logged as "
    "blocked, not built in any form -- confirmed empirically that neither "
    "main.py orchestrator nor Path 1's Redis session state carries any usable "
    "duration/progression signal today. Held pending a separate, unscoped "
    "prerequisite (severity follow-on collection wired into an orchestrator). "
    "Category B held pending Pete's sequencing confirmation. Full detail in "
    "Section 14. MOB v4.55. |"
)

CATB_LOG_LINE = (
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

edit("tools/_mob.txt", CATA_LOG_HEAD, CATB_LOG_LINE + "\n" + CATA_LOG_HEAD)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.55 |",
    "| MOB version | v4.56 |",
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
    print(f"MOB CATEGORY B PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
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
