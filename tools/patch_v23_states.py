"""
PRV3 -- v23 States Patch (Session 26)

Patches engine/data/states.py -- six sub-changes:

  1. leadership_deafness:
       cluster_id: "C-InfoFlow" -> None
       dimensional_vector: att_l=0.50, all other 7 fields = 0.10

  2. what_nobody_says:
       cluster_id: "C-Silence" -> None

  3. the_unreported_hazard:
       cluster_id: "C-Silence" -> None

  4. the_unlocked_door:
       cluster_id: "C-Silence" -> None

  5. the_suppression_filter:
       cluster_id: "C-InfoFlow" -> None

  6. CLUSTERS dict:
       Remove C-Silence and C-InfoFlow entries (both now empty)

Usage:
  python tools/patch_v23_states.py --dry-run
  python tools/patch_v23_states.py --write
"""

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parents[1]
STATES_PATH = ROOT / "engine" / "data" / "states.py"


def apply_patch(path: Path, old: str, new: str, label: str, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        print(f"  [ERROR] '{label}' -- old string not found")
        return False
    if count > 1:
        print(f"  [ERROR] '{label}' -- matched {count} times (ambiguous)")
        return False
    new_text = text.replace(old, new, 1)
    if dry_run:
        print(f"  [DRY-RUN] {path.relative_to(ROOT)} -- {label}")
        old_lines = old.splitlines()
        new_lines = new.splitlines()
        for ln in old_lines[:10]:
            print(f"    - {ln}")
        for ln in new_lines[:10]:
            print(f"    + {ln}")
        if len(old_lines) > 10:
            print(f"    ... ({len(old_lines)} lines -> {len(new_lines)} lines)")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"  [WRITE]   {path.relative_to(ROOT)} -- {label}")
    return True


def run(dry_run: bool):
    errors = []

    # ── 1. leadership_deafness: cluster_id + dimensional_vector ──────────────
    ok = apply_patch(
        STATES_PATH,
        old="""_reg(_profile(
    state_id="leadership_deafness",
    state_name="Leadership Deafness",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id="C-InfoFlow",
    liability_axes=["Governance & Authority", "Cultural & Behavioral", "Strategic"],
    asset_axes=["Communication Integrity", "Adaptive Capacity"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Organizational Deafness
    resolution_family="Executive Counsel",
))
STATE_PROFILES["leadership_deafness"].dimensional_vector = DimensionalVector(
    aptitude_liability=0.15,
    aptitude_asset=0.15,
    authority_liability=0.15,
    authority_asset=0.15,
    alliance_liability=0.25,
    alliance_asset=0.15,
    attitude_liability=0.35,
    attitude_asset=0.15,
)""",
        new="""_reg(_profile(
    state_id="leadership_deafness",
    state_name="Leadership Deafness",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id=None,
    liability_axes=["Governance & Authority", "Cultural & Behavioral", "Strategic"],
    asset_axes=["Communication Integrity", "Adaptive Capacity"],
    sev_min="Entrenched", sev_max="Endemic",
    # Inferred from profiles doc: Organizational Deafness
    resolution_family="Executive Counsel",
))
STATE_PROFILES["leadership_deafness"].dimensional_vector = DimensionalVector(  # v23: att_l=0.50, all others=0.10
    aptitude_liability=0.10,
    aptitude_asset=0.10,
    authority_liability=0.10,
    authority_asset=0.10,
    alliance_liability=0.10,
    alliance_asset=0.10,
    attitude_liability=0.50,
    attitude_asset=0.10,
)""",
        label="leadership_deafness: cluster_id C-InfoFlow->None, att_l 0.35->0.50, all others 0.15/0.25->0.10",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("leadership_deafness")

    # ── 2. what_nobody_says: cluster_id C-Silence -> None ────────────────────
    ok = apply_patch(
        STATES_PATH,
        old="""    state_id="what_nobody_says",
    state_name="What Nobody Says",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id="C-Silence",""",
        new="""    state_id="what_nobody_says",
    state_name="What Nobody Says",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id=None,""",
        label="what_nobody_says: cluster_id C-Silence->None",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("what_nobody_says")

    # ── 3. the_unreported_hazard: cluster_id C-Silence -> None ───────────────
    ok = apply_patch(
        STATES_PATH,
        old="""    state_id="the_unreported_hazard",
    state_name="The Unreported Hazard",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id="C-Silence",""",
        new="""    state_id="the_unreported_hazard",
    state_name="The Unreported Hazard",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id=None,""",
        label="the_unreported_hazard: cluster_id C-Silence->None",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("the_unreported_hazard")

    # ── 4. the_unlocked_door: cluster_id C-Silence -> None ───────────────────
    ok = apply_patch(
        STATES_PATH,
        old="""    state_id="the_unlocked_door",
    state_name="The Unlocked Door",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id="C-Silence",""",
        new="""    state_id="the_unlocked_door",
    state_name="The Unlocked Door",
    primary_dimension="Attitude",
    signal_weight="cluster",
    cluster_id=None,""",
        label="the_unlocked_door: cluster_id C-Silence->None",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("the_unlocked_door")

    # ── 5. the_suppression_filter: cluster_id C-InfoFlow -> None ─────────────
    ok = apply_patch(
        STATES_PATH,
        old="""    state_id="the_suppression_filter",
    state_name="The Suppression Filter",
    primary_dimension="Alliance",
    signal_weight="cluster",
    cluster_id="C-InfoFlow",""",
        new="""    state_id="the_suppression_filter",
    state_name="The Suppression Filter",
    primary_dimension="Alliance",
    signal_weight="cluster",
    cluster_id=None,""",
        label="the_suppression_filter: cluster_id C-InfoFlow->None",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("the_suppression_filter")

    # ── 6. CLUSTERS dict: remove C-Silence and C-InfoFlow ────────────────────
    ok = apply_patch(
        STATES_PATH,
        old="""CLUSTERS: dict[str, list[str]] = {
    "C-Manager": [
        "the_unformed_leader",
        "the_overloaded_manager",
        "the_dormant_talent",
    ],
    "C-Culture": [
        "culture_drift",
        "identity_erosion",
        "the_culture_that_wasnt",
    ],
    "C-Silence": [
        "what_nobody_says",
        "the_unreported_hazard",
        "the_unlocked_door",
    ],
    "C-InfoFlow": [
        "the_suppression_filter",
        "leadership_deafness",
    ],
}""",
        new="""CLUSTERS: dict[str, list[str]] = {
    "C-Manager": [
        "the_unformed_leader",
        "the_overloaded_manager",
        "the_dormant_talent",
    ],
    "C-Culture": [
        "culture_drift",
        "identity_erosion",
        "the_culture_that_wasnt",
    ],
}""",
        label="CLUSTERS dict: remove C-Silence and C-InfoFlow (both dismantled v23)",
        dry_run=dry_run,
    )
    if not ok:
        errors.append("CLUSTERS dict")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    if errors:
        print(f"ERRORS ({len(errors)}) -- patch NOT applied:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        mode = "DRY-RUN" if dry_run else "WRITTEN"
        print(f"All 6 patches {mode} successfully. 1 file affected: engine/data/states.py")
        if dry_run:
            print("Run with --write to apply.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    run(dry_run=args.dry_run)
