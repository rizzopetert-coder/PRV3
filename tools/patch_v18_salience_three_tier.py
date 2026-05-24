"""
Patch: engine/data/salience.py — v18 Three-Tier Salience Architecture

Reduces LOW/CLUSTER secondary axis weights from 2.5 to 1.0.
HIGH/MEDIUM states: unchanged (primary 2.5, others 0.4).
LOW/CLUSTER states: primary 2.5, secondary 1.0, others 0.4.

15 states modified. the_inside_track excluded (MEDIUM). narrative_lock included (LOW).
leadership_deafness: secondary changed from Alliance to Authority (Gemini-specified).
what_nobody_says: primary=Alliance (2.5), secondary=Attitude (1.0) (Gemini-specified).

Pete confirmed 2026-05-23 Session 23.

Usage:
  python tools/patch_v18_salience_three_tier.py --dry-run
  python tools/patch_v18_salience_three_tier.py --write
"""

import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "salience.py"

CHANGES = [
    # ── Module docstring update ────────────────────────────────────────────────
    {
        "description": "Module docstring: update seeding rule to three-tier (v18)",
        "old": (
            'Seeding rule (Gemini-specified, Session 21):\n'
            '  Target fields (primary dimension + secondary dimension, both axes): 2.5\n'
            '  Off-axis fields (all other dimensions, both axes): 0.4'
        ),
        "new": (
            'Seeding rule — three-tier architecture (v18, Session 23):\n'
            '  HIGH/MEDIUM states: primary fields 2.5; all others 0.4\n'
            '  LOW/CLUSTER states: primary fields 2.5; secondary fields 1.0; all others 0.4\n'
            '  (Session 21 original: binary seeding — primary 2.5, secondary 2.5, others 0.4)'
        ),
    },
    # ── APTITUDE LOW/CLUSTER ───────────────────────────────────────────────────
    {
        "description": "the_unformed_leader: attitude_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "the_unformed_leader": {\n'
            '        "aptitude_liability": 2.5, "aptitude_asset": 2.5,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "the_unformed_leader": {  # Tier 2 v18: attitude secondary 2.5->1.0\n'
            '        "aptitude_liability": 2.5, "aptitude_asset": 2.5,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 1.0, "attitude_asset": 1.0,\n'
            '    },'
        ),
    },
    {
        "description": "the_dormant_talent: attitude_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "the_dormant_talent": {\n'
            '        "aptitude_liability": 2.5, "aptitude_asset": 2.5,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "the_dormant_talent": {  # Tier 2 v18: attitude secondary 2.5->1.0\n'
            '        "aptitude_liability": 2.5, "aptitude_asset": 2.5,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 1.0, "attitude_asset": 1.0,\n'
            '    },'
        ),
    },
    {
        "description": "the_overloaded_manager: authority_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "the_overloaded_manager": {\n'
            '        "aptitude_liability": 2.5, "aptitude_asset": 2.5,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
        "new": (
            '    "the_overloaded_manager": {  # Tier 2 v18: authority secondary 2.5->1.0\n'
            '        "aptitude_liability": 2.5, "aptitude_asset": 2.5,\n'
            '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
    },
    # ── AUTHORITY LOW/CLUSTER ──────────────────────────────────────────────────
    {
        "description": "the_unexamined_algorithm: aptitude_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "the_unexamined_algorithm": {\n'
            '        "aptitude_liability": 2.5, "aptitude_asset": 2.5,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
        "new": (
            '    "the_unexamined_algorithm": {  # Tier 2 v18: aptitude secondary 2.5->1.0\n'
            '        "aptitude_liability": 1.0, "aptitude_asset": 1.0,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
    },
    {
        "description": "paper_shield: alliance_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "paper_shield": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
        "new": (
            '    "paper_shield": {  # Tier 2 v18: alliance secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 1.0, "alliance_asset": 1.0,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
    },
    {
        "description": "invisible_influence_architecture: alliance_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "invisible_influence_architecture": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
        "new": (
            '    "invisible_influence_architecture": {  # Tier 2 v18: alliance secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 1.0, "alliance_asset": 1.0,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
    },
    # ── ALLIANCE LOW/CLUSTER ───────────────────────────────────────────────────
    {
        "description": "the_suppression_filter: authority_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "the_suppression_filter": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
        "new": (
            '    "the_suppression_filter": {  # Tier 2 v18: authority secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 0.4, "attitude_asset": 0.4,\n'
            '    },'
        ),
    },
    # ── ATTITUDE LOW/CLUSTER — Alliance secondary ──────────────────────────────
    {
        "description": "narrative_lock: alliance_liability/asset 2.5 -> 1.0 (secondary reduced; primary=Attitude)",
        "old": (
            '    "narrative_lock": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "narrative_lock": {  # Tier 2 v18: alliance secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 1.0, "alliance_asset": 1.0,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
    },
    {
        "description": "what_nobody_says: attitude 2.5->1.0 (secondary); alliance 2.5 stays (primary per Gemini)",
        "old": (
            '    "what_nobody_says": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "what_nobody_says": {  # Tier 2 v18: primary=Alliance(2.5), attitude secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 1.0, "attitude_asset": 1.0,\n'
            '    },'
        ),
    },
    {
        "description": "leadership_deafness: alliance 2.5->0.4 + authority 0.4->1.0 (secondary changed Alliance->Authority per Gemini)",
        "old": (
            '    "leadership_deafness": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "leadership_deafness": {  # Tier 2 v18: secondary changed Alliance->Authority(1.0)\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
    },
    {
        "description": "identity_erosion: alliance_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "identity_erosion": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "identity_erosion": {  # Tier 2 v18: alliance secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 1.0, "alliance_asset": 1.0,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
    },
    {
        "description": "the_culture_that_wasnt: alliance_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "the_culture_that_wasnt": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "the_culture_that_wasnt": {  # Tier 2 v18: alliance secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 1.0, "alliance_asset": 1.0,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
    },
    {
        "description": "the_unreported_hazard: alliance_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "the_unreported_hazard": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "the_unreported_hazard": {  # Tier 2 v18: alliance secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 1.0, "alliance_asset": 1.0,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
    },
    {
        "description": "the_unlocked_door: alliance_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "the_unlocked_door": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 2.5, "alliance_asset": 2.5,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "the_unlocked_door": {  # Tier 2 v18: alliance secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 0.4, "authority_asset": 0.4,\n'
            '        "alliance_liability": 1.0, "alliance_asset": 1.0,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
    },
    # ── ATTITUDE LOW/CLUSTER — Authority secondary ─────────────────────────────
    {
        "description": "culture_drift: authority_liability/asset 2.5 -> 1.0 (secondary reduced)",
        "old": (
            '    "culture_drift": {\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 2.5, "authority_asset": 2.5,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
        "new": (
            '    "culture_drift": {  # Tier 2 v18: authority secondary 2.5->1.0\n'
            '        "aptitude_liability": 0.4, "aptitude_asset": 0.4,\n'
            '        "authority_liability": 1.0, "authority_asset": 1.0,\n'
            '        "alliance_liability": 0.4, "alliance_asset": 0.4,\n'
            '        "attitude_liability": 2.5, "attitude_asset": 2.5,\n'
            '    },'
        ),
    },
]


def run(dry_run: bool):
    text = TARGET.read_text(encoding="utf-8")
    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"{'=' * 72}")
    print(f"patch_v18_salience_three_tier.py — {mode}")
    print(f"Target: {TARGET}")
    print(f"{'=' * 72}\n")

    errors = []
    applied = []

    for change in CHANGES:
        desc = change["description"]
        old = change["old"]
        new = change["new"]

        count = text.count(old)
        if count == 0:
            errors.append(f"[NOT FOUND] {desc}")
        elif count > 1:
            errors.append(f"[NOT UNIQUE — {count} occurrences] {desc}")
        else:
            applied.append((desc, old, new))
            if dry_run:
                print(f"  [DRY-RUN] Would apply: {desc}")
            else:
                text = text.replace(old, new, 1)
                print(f"  [APPLIED] {desc}")

    if errors:
        print()
        for e in errors:
            print(f"  {e}")
        print(f"\n[ABORT] {len(errors)} error(s). No file written.")
        sys.exit(1)

    if dry_run:
        print(f"\n[DRY-RUN COMPLETE] {len(applied)} change(s) validated. No file written.")
    else:
        TARGET.write_text(text, encoding="utf-8")
        print(f"\n[DONE] {TARGET} written. {len(applied)} change(s) applied.")


if __name__ == "__main__":
    dry_run = "--write" not in sys.argv
    run(dry_run)
