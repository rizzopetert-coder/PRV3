"""
PRV3 MOB Update — Session 68 (Gemini review resolution for taxonomy expansion)

Updates tools/_mob.txt:
  - Section 14 (Locked Decisions Log): new Session 68 entry appended after Session 67
  - Section 16 (Session Log): new one-line Session 68 entry
  - Version bump v4.38 -> v4.39 (material workstream status change: draft
    classification for 9/10 new states confirmed, 1 state revised, both naming
    collisions resolved)

Updates CLAUDE.md:
  - MOB version cross-reference v4.38 -> v4.39

Usage:
  python tools/patch_mob_s68_gemini_review_resolution.py --dry-run
  python tools/patch_mob_s68_gemini_review_resolution.py --write
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
    "\\\\\\#\\\\\\# MOB v4.38",
    "\\\\\\#\\\\\\# MOB v4.39",
)

S67_ENTRY_TAIL = (
    "warrants a bump per the closeout protocol; no decision in this session is being "
    "recorded as Locked. MOB v4.38. |"
)

S68_ENTRY = (
    "| **July 2026 — Session 68** | Gemini architecture review of the Session 67 draft "
    "classification (prompts/gemini-handoff-taxonomy-expansion-57.md) returned full "
    "verdicts on all 10 new states. **Confirmed as drafted, no changes:** Compression "
    "Crisis, Sequential Decision Blindness, Disparate Impact Architecture, Planning "
    "Authority Gap, Cultural Overtime, Distributed Culture Fragmentation, Invisible "
    "Performance Management (classification fields; naming-collision resolution below is "
    "separate). **Revised from draft:** Wellbeing Theater -- two changes, not one: (1) "
    "removed from CLUSTERS[\"C-Culture\"] in engine/data/states.py (cluster_id and "
    "signal_weight left as drafted -- only the active cluster-routing membership was "
    "rejected, not those fields); (2) resolution_family (engine/resolution_families.py "
    "4-bucket field) changed from \"directional\" to \"structural\". Human Displacement "
    "Anxiety -- resolution_family changed from \"directional\" to \"structural\"; "
    "signatureId (web/data/taxonomy.ts) changed from \"stunted_growth\" to "
    "\"culture_erosion\" (stateIds membership arrays updated on both signatures "
    "accordingly). **Naming collisions resolved:** Motivational Architecture Failure -- "
    "Gemini's review floated a rename (systemic_amotivation or similar) to resolve the "
    "collision with the_wrong_reward's historical inferred-mapping name; Pete rejected "
    "the rename, keeping the existing state_id and external label, resolved via inline "
    "documentation cross-reference only (same pattern as Sequential Decision Blindness vs. "
    "Decision Blindness). Invisible Performance Management -- Gemini's condition for "
    "accepting the retired-identifier reuse (verify no legacy analysis/migration script "
    "string-matches the old identifier against old log files) checked and satisfied: the "
    "only repo hits are this state's own new files plus three inert historical prompt "
    "files describing the original 45-vs-47 resolution as prose, not executable scripts; "
    "the only actual .log file in the repo is an unrelated auto-generated Next.js dev-"
    "server log. Collision treated as closed. **Process note:** the summary instruction "
    "relaying Gemini's review referred once to \"Systemic Amotivation's other fields\" in "
    "the general confirmed-as-drafted list -- that name is the rejected rename proposal "
    "for Motivational Architecture Failure, not a real state; read as a stale carryover "
    "and treated as referring to Motivational Architecture Failure, consistent with the "
    "explicit rejection of that same rename earlier in the same instruction. Flagged in "
    "the handoff doc's resolution section rather than silently resolved. **Draft-marker "
    "comments updated:** the master expansion-block comments in both engine/data/states.py "
    "and web/data/taxonomy.ts, and each of the 10 states' own inline comments, changed from "
    "\"DRAFT -- pending Gemini review\" to \"CONFIRMED -- Gemini review complete (round "
    "two, Session 68)\", noting per-state whether anything changed from the Session 67 "
    "draft. Calibration status (dimensional_vector tuning, separate from classification "
    "review) is called out as still in progress in the updated master comments -- a "
    "CONFIRMED classification does not imply a calibrated vector. **Verification:** "
    "engine/data/validate.py clean at 57 states (7/22/7/21), same 2 pre-existing "
    "stale-check failures as before (unrelated, unchanged). tsc --noEmit: 0 errors. "
    "calibration_runner.py: 152/172, identical to the Session 67 draft run -- none of "
    "this session's changes touch a field the calibration scoring path reads, so no "
    "regression was expected and none occurred. tools/test_resolution_families.py and "
    "tools/test_checkpoint.py: both pass. prompts/gemini-handoff-taxonomy-expansion-57.md "
    "updated with a \"Resolution (Session 68)\" section documenting all verdicts, in "
    "addition to (not replacing) the original review request. CLAUDE.md MOB version "
    "cross-reference updated v4.38->v4.39. MOB version bumped to v4.39 -- material "
    "workstream status change (9 of 10 new states now fully confirmed by Gemini review, "
    "1 revised, both naming collisions resolved) warrants a bump per the closeout "
    "protocol. **OPEN -- next session:** full calibration of the 4 new states still "
    "failing all 3 profiles (Disparate Impact Architecture, Human Displacement Anxiety, "
    "Motivational Architecture Failure, Sequential Decision Blindness) plus partial "
    "calibration for Compression Crisis (2/3) and Cultural Overtime (1/3) -- unchanged "
    "from Session 67, now unblocked since classification is fully confirmed. "
    "Signature-level copy (description/coexistenceInterpretation) still not rewritten for "
    "the composition changes across culture_erosion/leadership_bottleneck/stunted_growth/"
    "compounding_risks -- still flagged as a possible follow-up, not actioned. MOB v4.39. |"
)

edit("tools/_mob.txt", S67_ENTRY_TAIL, S67_ENTRY_TAIL + "\n" + S68_ENTRY)

# --- Section 16 (Session Log): one-line entry, prepended before the Session 67 line ---

S67_LOG_LINE = (
    "| \\\\\\*\\\\\\*July 2026 — Session 67\\\\\\*\\\\\\* | Taxonomy expansion 47->57 implemented end-to-end "
    "(taxonomy.ts, states.py, validate.py, resolution_families.py, salience.py, "
    "checkpoint.py, friction_tax.py, test_suite.py + 30 new test profiles, CLAUDE.md, "
    "book copy) — status DRAFT, per-state classification fields not in Session 65's "
    "Gemini-reviewed scope, routed for review before lock. Two new naming collisions "
    "found and inline-documented (Motivational Architecture Failure, Invisible "
    "Performance Management). Full detail in Section 14. MOB v4.38. |"
)

S68_LOG_LINE = (
    "| \\\\\\*\\\\\\*July 2026 — Session 68\\\\\\*\\\\\\* | Gemini review of the Session 67 draft classification "
    "returned verdicts on all 10 new states — 7 confirmed as drafted, Wellbeing Theater "
    "and Human Displacement Anxiety revised on specific fields, both naming collisions "
    "resolved (one via Pete rejecting a proposed rename, one via a verified-clean legacy-"
    "script check). Full detail in Section 14. MOB v4.39. |"
)

edit("tools/_mob.txt", S67_LOG_LINE, S68_LOG_LINE + "\n" + S67_LOG_LINE)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.38 |",
    "| MOB version | v4.39 |",
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
    print(f"MOB SESSION 68 PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
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
