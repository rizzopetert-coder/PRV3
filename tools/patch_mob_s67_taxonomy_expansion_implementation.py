"""
PRV3 MOB Update — Session 67 (taxonomy expansion 47 -> 57 implementation, draft status)

Updates tools/_mob.txt:
  - Section 4 (State Taxonomy): 47 -> 57 confirmed, 10 new names added to dimension rows
  - Section 14 (Locked Decisions Log): new Session 67 entry
  - Section 16 (Session Log): new one-line Session 67 entry
  - Version bump v4.37 -> v4.38 (material workstream status change)

Updates CLAUDE.md:
  - MOB version cross-reference v4.37 -> v4.38

Usage:
  python tools/patch_mob_s67_taxonomy_expansion_implementation.py --dry-run
  python tools/patch_mob_s67_taxonomy_expansion_implementation.py --write
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
    "\\\\\\#\\\\\\# MOB v4.37",
    "\\\\\\#\\\\\\# MOB v4.38",
)

TAXONOMY_LOCK_OLD = "47 confirmed states. Locked. No additions or removals without Pete's decision."
TAXONOMY_LOCK_NEW = (
    "57 confirmed states. Locked. No additions or removals without Pete's decision.\n\n"
    "  \n\n  \n\n"
    "\\\\\\*\\\\\\*Taxonomy expansion (Session 65 decision, Session 67 implementation):\\\\\\*\\\\\\* "
    "10 states added below. Names and dimension assignment are LOCKED (Session 65 Gemini "
    "review). The engine's per-state classification fields for these 10 (signal_weight, "
    "severity_range, resolution_family, liability/asset axes, dimensional_vector, "
    "signatureId) are DRAFT — authored Session 67, not yet Gemini-reviewed. See Session 67 "
    "log entry and prompts/gemini-handoff-taxonomy-expansion-57.md."
)
edit("tools/_mob.txt", TAXONOMY_LOCK_OLD, TAXONOMY_LOCK_NEW)

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*Aptitude\\\\\\*\\\\\\* | The Paper Tiger — The Undefined Role — The Unformed Leader — The Overloaded Manager — The Dormant Talent |",
    "| \\\\\\*\\\\\\*Aptitude\\\\\\*\\\\\\* | The Paper Tiger — The Undefined Role — The Unformed Leader — The Overloaded Manager — The Dormant Talent — Invisible Performance Management |",
)

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*Authority\\\\\\*\\\\\\* | The Founders' Grip — The Exposed — HR Capture — Heard and Ignored — The Tolerated Violation — The Unsolved Problem — The Uninitiated — Leadership Continuity Risk — Decision Paralysis — The Policy Lag — Dueling Narratives — Transition Paralysis — The Lost Map — Pay Exposure — The Pay Fog — The Unexamined Algorithm — Paper Shield — Invisible Influence Architecture — The Overloaded Manager |",
    "| \\\\\\*\\\\\\*Authority\\\\\\*\\\\\\* | The Founders' Grip — The Exposed — HR Capture — Heard and Ignored — The Tolerated Violation — The Unsolved Problem — The Uninitiated — Leadership Continuity Risk — Decision Paralysis — The Policy Lag — Dueling Narratives — Transition Paralysis — The Lost Map — Pay Exposure — The Pay Fog — The Unexamined Algorithm — Paper Shield — Invisible Influence Architecture — The Overloaded Manager — Compression Crisis — Sequential Decision Blindness — Disparate Impact Architecture — Planning Authority Gap |",
)

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*Alliance\\\\\\*\\\\\\* | The Fracture — Decision Blindness — The Second Close — Silosolation — The Arbitrary Standard — The Suppression Filter — Paper Shield — Invisible Influence Architecture |",
    "| \\\\\\*\\\\\\*Alliance\\\\\\*\\\\\\* | The Fracture — Decision Blindness — The Second Close — Silosolation — The Arbitrary Standard — The Suppression Filter — Paper Shield — Invisible Influence Architecture — Distributed Culture Fragmentation |",
)

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*Attitude\\\\\\*\\\\\\* | The Untouchable — The Diversity Ceiling — The Burned Credibility — Invisible Burnout — The Basement Standard — The Inside Track — Groundhog Day — The Wrong Reward — The Broken Compass — Narrative Lock — What Nobody Says — Leadership Deafness — Culture Drift — Identity Erosion — The Culture That Wasn't — The Unreported Hazard — The Unlocked Door — The Unformed Leader — The Dormant Talent |",
    "| \\\\\\*\\\\\\*Attitude\\\\\\*\\\\\\* | The Untouchable — The Diversity Ceiling — The Burned Credibility — Invisible Burnout — The Basement Standard — The Inside Track — Groundhog Day — The Wrong Reward — The Broken Compass — Narrative Lock — What Nobody Says — Leadership Deafness — Culture Drift — Identity Erosion — The Culture That Wasn't — The Unreported Hazard — The Unlocked Door — The Unformed Leader — The Dormant Talent — Wellbeing Theater — Human Displacement Anxiety — Motivational Architecture Failure — Cultural Overtime |",
)

# --- Section 14 (Locked Decisions Log): new Session 67 entry, appended after Session 66 ---

S66_ENTRY = (
    "| **July 2026 — Session 66** | Closeout for the consolidation-mapping/taxonomy-expansion session (Session 65). "
    "Reusable tooling committed after Session 65's MOB entry was already written: tools/verify_gemini_quotes.py, "
    "tools/consolidation_source_corpus.json, tools/generate_filter_prompt.py, tools/batch_config_example.json (commit e082870) — "
    "built this session to catch fabricated/paraphrased quotes and invalid disposition targets in Gemini Filter A/B/C output, "
    "reusable for future consolidation or taxonomy-expansion verification work. tools/gemini_prompts/ and tools/gemini_responses/ "
    "deliberately left untracked — per-batch working artifacts, not lasting infrastructure. Diary written (topic: "
    "prv3-consolidation-taxonomy-expansion). Mine run. No new locked decisions, no rule changes — MOB version not bumped. MOB v4.37. |"
)

S67_ENTRY = (
    "| **July 2026 — Session 67** | Taxonomy expansion 47 -> 57 IMPLEMENTED as one atomic change, status DRAFT "
    "pending Gemini architecture review — not locked. "
    "**What shipped:** web/data/taxonomy.ts (10 state entries, exact-text descriptions pulled from "
    "tools/consolidation_source_corpus.json and verified as literal substrings, signatureId assignments, stateIds membership "
    "updates, count comment 47->57), engine/data/states.py (10 StateProfile registry entries with dimensional vectors, count "
    "comment, CLUSTERS[C-Culture] updated), engine/data/validate.py (count assertions 47->57, dimension counts), "
    "engine/resolution_families.py (assert 47->57, 10 new STATE_RESOLUTION_FAMILY mappings), engine/data/salience.py (10 new "
    "SALIENCE_PROFILES entries — NEW FILE FOUND needing changes, not in original scope, since all 47 existing states had 100% "
    "coverage), engine/checkpoint.py (entropy comment; MAX_ENTROPY computes dynamically off len(STATE_PROFILES) so no code "
    "change needed there), engine/friction_tax.py (10 new None/CALIBRATION TARGET entries in STATE_MULTIPLIERS — verified this "
    "file keys strictly by state_id string via dict.get(), no array-position risk as Pete's brief flagged for checking), "
    "engine/test_suite.py (Phase 1 minimum comment 141->171), engine/test_profiles_expansion.py (NEW FILE, 30 authored test "
    "profiles, 3 per new state, wired into tools/calibration_runner.py's ALL_PROFILES), CLAUDE.md (4 count references), "
    "web/content/book/methodology/symptoms-states-and-why-the-distinction-matters.md (forty-seven -> fifty-seven), "
    "tools/test_checkpoint.py + tools/test_resolution_families.py (2 pre-existing unit tests hardcoded the old count as their "
    "own expected value — fixed to dynamic/57, not part of original file list but found during regression verification). "
    "**Why DRAFT, not locked:** Session 65's Gemini review approved state names, dimension assignment, and disposition only — "
    "it did not assign signal_weight, cluster_id, liability/asset axes, severity_range, resolution_family (both the states.py "
    "legacy field and the live resolution_families.py 4-bucket field), dimensional_vector, salience weights, or taxonomy.ts "
    "signatureId for the 10 new states, and no source document exists for these (confirmed by grep of "
    "consolidation-mapping-trace.md — rich disposition rationale, zero calibration data). Pete's explicit direction this "
    "session (asked via AskUserQuestion): draft the values now grounded in the trace file's own rationale and analogy to the "
    "closest existing state, route through Gemini before locking, do not commit as final. Full rationale documented per-field "
    "in prompts/gemini-handoff-taxonomy-expansion-57.md. "
    "**Naming collisions found beyond Session 65's single flagged case (Sequential Decision Blindness vs. Decision Blindness, "
    "which already had a required mitigation):** (1) Motivational Architecture Failure is the profiles-doc inferred-mapping "
    "source name for the existing locked state the_wrong_reward (states.py's own comment on that entry) — inline "
    "cross-reference added, not independently reviewed. (2) Invisible Performance Management is a literal retired state_id "
    "(states.py header: Rename applied: invisible_performance_management -> the_paper_tiger; resolved years ago per "
    "state_removal_final.md/state_removal_v3.md, no live collision) reused for a mechanistically distinct new state — inline "
    "cross-reference added, not independently reviewed. Both flagged in the Gemini handoff. "
    "**Test suite status:** engine/data/validate.py clean at 57 states/7-22-7-21 dimension split (same 2 pre-existing "
    "stale-check failures as before, unrelated to this session — all-vectors-at-baseline inverted-logic check, and 5 "
    "pre-existing cluster-weight-without-cluster_id states). calibration_runner.py: 152/172 (was 137/142; 5 pre-existing "
    "deferred Phase-3 failures unchanged, 15 of 30 new profiles pass on first draft pass — 3 states clear all 3 profiles "
    "outright, 6 states fail on cluster/prominence criteria consistent with the same calibration gap the original 47 states "
    "took roughly 13 sessions, S16-S29, to close). No attempt made to hand-tune vectors to force a pass against unreviewed "
    "classification — that would waste effort if Gemini's review changes the underlying assignments. All other engine unit "
    "tests (severity/narrative/output/accumulation/checkpoint/friction_tax/output_synthesis/main/resolution_families) pass; "
    "the one remaining failure (test_contract.py liability_block KeyError) is the same pre-existing issue confirmed since "
    "Session 57, unrelated to this session. tsc: 0 errors. Full corpus-substring verification run on all 10 descriptions: "
    "exact match, confirmed programmatically. No hardcoded state-count reference found in any live web/ UI component (Pete's "
    "brief flagged this as unconfirmed; checked this session, clean). "
    "**OPEN — next session:** Gemini architecture review of the draft classification table (full detail in the handoff doc); "
    "full calibration of the 6 under-performing new states once that review lands; signature-level copy "
    "(description/coexistenceInterpretation) not rewritten for the composition changes to "
    "culture_erosion/leadership_bottleneck/stunted_growth/compounding_risks — flagged as a possible follow-up, not actioned. "
    "CLAUDE.md MOB version cross-reference updated v4.37->v4.38. MOB version bumped to v4.38 — material workstream status "
    "change (taxonomy expansion moved from not started to implemented, draft, pending review) warrants a bump per the "
    "closeout protocol; no decision in this session is being recorded as Locked. MOB v4.38. |"
)

edit("tools/_mob.txt", S66_ENTRY, S66_ENTRY + "\n" + S67_ENTRY)

# --- Section 16 (Session Log): one-line entry, prepended before Session 1 ---

SESSION1_LOG = (
    "| \\\\\\*\\\\\\*May 2026 — Session 1\\\\\\*\\\\\\* | Taxonomy consolidation (108 to 47 states), name register audit, Liability "
    "Risk Framework, Leadership Competency Framework, Signal Map. All 47 states profiled. Four cluster identifiers confirmed. "
    "Eight root conditions named. MOB v1.0 created. |"
)

S67_LOG_LINE = (
    "| \\\\\\*\\\\\\*July 2026 — Session 67\\\\\\*\\\\\\* | Taxonomy expansion 47->57 implemented end-to-end (taxonomy.ts, states.py, "
    "validate.py, resolution_families.py, salience.py, checkpoint.py, friction_tax.py, test_suite.py + 30 new test profiles, "
    "CLAUDE.md, book copy) — status DRAFT, per-state classification fields not in Session 65's Gemini-reviewed scope, routed "
    "for review before lock. Two new naming collisions found and inline-documented (Motivational Architecture Failure, "
    "Invisible Performance Management). Full detail in Section 14. MOB v4.38. |"
)

edit("tools/_mob.txt", SESSION1_LOG, S67_LOG_LINE + "\n" + SESSION1_LOG)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.37 |",
    "| MOB version | v4.38 |",
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
    print(f"MOB SESSION 67 PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
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
