"""
PRV3 MOB Update -- Category A: Cascade Risk shipped, Trajectory blocked

Updates tools/_mob.txt:
  - Section 14 (Locked Decisions Log): new entry appended after the
    dimension_summary entry (ascending order, this section's newest tail)
  - Section 16 (Session Log): new one-line entry prepended before the
    Visual identity v2 entry (descending order, this section's newest head)
  - Version bump v4.54 -> v4.55 (material workstream status change --
    Cascade Risk shipped, Trajectory formally logged as blocked with a
    named prerequisite)

Updates CLAUDE.md:
  - MOB version cross-reference v4.54 -> v4.55

Documentation-only change -- no product code touched by this script.
(Product code change already committed separately: 787a4e1.)

Usage:
  python tools/patch_mob_category_a_cascade_risk.py --dry-run
  python tools/patch_mob_category_a_cascade_risk.py --write
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
    "\\\\\\#\\\\\\# MOB v4.54",
    "\\\\\\#\\\\\\# MOB v4.55",
)

# --- Section 14 (Locked Decisions Log, ascending -- append after newest tail) ---

DIMSUM_ENTRY_TAIL = (
    "| **July 2026 — dimension_summary shipped** | New field added to the engine "
    "output contract, commit 9c52e7d, pushed to origin/main. Closes the gate "
    "flagged in the visual identity v2 entry — Gemini-cleared (per-axis normalized "
    "[0,1] score, not the raw liability/asset split, respects P-03). "
    "**Implementation:** asset_d/(asset_d+liability_d) ratio computed independently "
    "per axis in a new _compute_dimension_summary(), mirroring "
    "_compute_asset_score()'s existing pattern — not the unreconciled min-max "
    "formula Gemini's response initially offered. Landed as a top-level field, "
    "sibling to asset_score, not nested inside private_output — confirmed correct "
    "placement by checking _PRIVATE_OUTPUT_FIELDS's actual contents before "
    "assuming. Threaded through PrivateOutputPayload and EngineResult on the "
    "TypeScript side, both construction sites (/api/result, session/answer's Q34 "
    "completion) updated to match. **Two incidental stale-count bugs fixed as a "
    "byproduct:** contract.py's docstring and tools/test_contract.py's own "
    "field-count assertion both said 14 top-level fields when the real count was "
    "already 15 before this change (synthesis was never counted) — both now "
    "correctly say 16. Zero regressions across every existing test suite. "
    "ConstellationField's live mode remains unwired to this real field — that's "
    "the next, separate step. MOB v4.54. |"
)

CATA_ENTRY = (
    "| **July 2026 — Category A implementation (Cascade Risk shipped, Trajectory "
    "blocked)** | Gemini-cleared Category A derived-outputs pass -- Trajectory + "
    "Cross-Dimensional Cascade Risk, zero modification to the 8-field accumulation "
    "model, zero new questions, zero change to accumulated_vector or rank_states(), "
    "preserving the 172-profile suite's calibration state. "
    "**Cascade Risk (CR) shipped:** new compute_cascade_risk() in "
    "engine/accumulation.py, commit 787a4e1. CR = dispersion x intensity, both in "
    "[0, 1]. Dispersion is normalized Shannon entropy of the four liability "
    "fields' relative shares, reusing the same entropy technique "
    "engine/checkpoint.py already applies for checkpoint routing rather than "
    "inventing a new one -- negative per-field values (confirmed real, e.g. "
    "authority_liability: -0.15 in engine/data/questions.py) clamped to 0 before "
    "forming the probability distribution. Intensity is L2-norm session magnitude "
    "(compute_session_magnitude()) normalized against the already-locked "
    "MC_CENTROID_39 empirical reference (N=1000 simulations), saturated at 1.0. A "
    "-0.0 sign artifact on the single-axis-concentration case was caught and fixed "
    "via a max(0.0, ...) floor. Marked CALIBRATION TARGET per this engine's "
    "existing convention for not-yet-data-validated combination logic. 9 new "
    "dedicated checks added to tools/test_accumulation.py (39/0, up from 30/0). "
    "**Full 172-profile calibration suite unchanged at 169/172** (same 3 "
    "pre-existing moderate-tier failures, zero regression); test_main.py (27/0), "
    "test_checkpoint.py (58/0), test_resolution_families.py (101/0) also zero "
    "regressions. No value inconsistent with a known state profile found across "
    "8 hand-verified edge cases. "
    "**Trajectory (Accelerating/Stable/Decelerating) BLOCKED -- not built in any "
    "form,** per Pete's explicit instruction that correct-but-inert code is worse "
    "than no code here. Confirmed via direct trace of engine/main.py that neither "
    "run_engine() nor run_accumulated_engine() ever calls "
    "SeverityEngine.add_input() -- severity_result.tier is a hardcoded "
    "'Emerging' constant in current practice and duration_band is never "
    "populated anywhere in the pipeline, verified empirically by executing "
    "SeverityEngine() directly with zero inputs. Also confirmed Path 1's Redis "
    "session state (DiagnosticSession, AnswerLogEntry in web/lib/session-store.ts) "
    "carries no usable duration/progression signal either -- no created_at or "
    "started_at field anywhere in session state, the only timestamp in the "
    "system is AnonymizedCompletion.completed_at, written post-completion to a "
    "separate aggregate list, disconnected from assemble_output()'s already-"
    "completed call. **Prerequisite identified, not actioned:** wiring severity "
    "follow-on collection into an orchestrator (real add_input() calls "
    "populating duration_band) is its own separate, unscoped piece of work. Do "
    "not revisit Trajectory until that prerequisite is scoped and built on its "
    "own. Category B (reversibility/momentum, SPOF routing, urgency window/"
    "Friction Tax) remains queued as a separate follow-on handoff, held pending "
    "Pete's sequencing confirmation. MOB v4.55. |"
)

edit("tools/_mob.txt", DIMSUM_ENTRY_TAIL, DIMSUM_ENTRY_TAIL + "\n" + CATA_ENTRY)

# --- Section 16 (Session Log, descending -- prepend before newest head) ---

VIS_ID_V2_LOG_HEAD = (
    "| **July 2026 — Visual identity v2 shipped (homepage proof point)** | OD-07 "
    "hybrid Constellation-Topology model built and shipped to the homepage as a "
    "single-page proof point, four staged commits (2d063f7, 374d42d, c9e63d9, "
    "f5c36ac), pushed to origin/main. **Scope:** three-theme token system "
    "(Warm/Dark/Neutral) added as an additive layer alongside the still-live "
    "Session 58 palette — no existing route repainted except the homepage, "
    "verified via direct diff of rendered DOM output across every other route "
    "(not a visual skim), confirmed byte-identical. ThemeSwitcher built, mounted "
    "homepage-only via a usePathname() guard on the shared NavBar component — "
    "NavBar being singular, shared infrastructure across every route was a real "
    "constraint surfaced during the build, not anticipated in the original "
    "scoping. Ambient ConstellationField (four-axis weighted quadrilateral plus "
    "severity-ring motif, continuous non-eased animation) mounted in the "
    "homepage hero. Live-mode ConstellationField also built and tested "
    "(severity-tier-conditional --urgency/--oxide branching, verified "
    "byte-identical against the approved mockup) but NOT wired into the results "
    "page or any real route yet. **Explicitly gated, not yet closed:** live "
    "mode's real-data wiring depends on a new dimension_summary engine output "
    "field, which does not exist yet and is held pending separate Gemini "
    "architecture review (P-03 clinical-boundary implications) — sent for "
    "review, response not yet received as of this entry. Do not wire live mode "
    "to production data until that clears. MOB v4.53. |"
)

CATA_LOG_LINE = (
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

edit("tools/_mob.txt", VIS_ID_V2_LOG_HEAD, CATA_LOG_LINE + "\n" + VIS_ID_V2_LOG_HEAD)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.54 |",
    "| MOB version | v4.55 |",
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
    print(f"MOB CATEGORY A PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
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
