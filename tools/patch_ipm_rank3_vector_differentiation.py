"""
PRV3 -- Differentiate invisible_performance_management's (IPM) dimensional_vector
from the_founders_grip's, closing Priority Queue item 5.

Pete's explicit call this session: skip the Gemini architecture gate, go
straight to Claude Code, confirm the content decision directly. Investigated
and confirmed before writing this patch (not proposed on assumption):
  - IPM and the_founders_grip carry byte-identical dimensional_vector AND
    salience_weights. salience_weights sharing is normal/by-design across
    dozens of same-tier Authority-primary states (confirmed via
    engine/data/salience.py -- HIGH and MEDIUM tier sections use identical
    magnitudes); the meaningful collision is dimensional_vector only.
  - f88a7c2 (2026-08-25) is the exact commit that put IPM here. Its axis
    flip (Aptitude -> Authority) was correct -- IPM's own text ("a
    manager's read... is accurate... a sound judgment... an absence of
    documentation") is genuinely an evidentiary-weight/Authority problem,
    not an Aptitude one. But it copied the_founders_grip's HIGH-tier
    magnitude (0.60/0.10) verbatim rather than IPM's own declared
    signal_weight="medium" magnitude (0.45/0.15) -- an unintended side
    effect, not a deliberate decision, confirmed by reading f88a7c2's own
    diff and commit message.
  - This byte-identical vector put IPM in the already-diagnosed 8-state
    "rank-3 cluster" (prompts/scd-wcs-remediation-tracker.md, Stage 3-5):
    the_founders_grip, disparate_impact_architecture, heard_and_ignored,
    hr_capture, sequential_decision_blindness, the_exposed,
    the_tolerated_violation, plus IPM. That cluster's broader architecture
    question stays explicitly OUT OF SCOPE this session, per Pete's
    instruction -- only IPM moves.
  - Full 175-profile ripple check run before this patch
    (tools/_ipm_rank3_differentiation_ripple_check.py, scratch, not
    committed): ZERO profiles anywhere in the suite change predicted
    rank-1 with this vector swapped in. Confirmed specifically for
    the_unexamined_algorithm's own 3 profiles (false-rank-1 3/3 before and
    after, IPM's share 0 -> 0) and all 10 MEDIUM-tier flat-Authority-
    template states (the_uninitiated, leadership_continuity_risk,
    decision_paralysis, the_policy_lag, dueling_narratives,
    transition_paralysis, the_lost_map, pay_exposure, the_pay_fog,
    compression_crisis) -- all identical before/after. Rank-3 cluster's
    other 7 members (including the_founders_grip) confirmed byte-identical
    before/after via direct confusion-matrix comparison, not just
    assumed from non-mutation.

New vector, text-grounded (Pete-confirmed as proposed):
    aptitude_liability=0.10 (unchanged), aptitude_asset=0.20 (was 0.10) --
    "a manager's read... is accurate... a sound judgment" is a real
    asset-side Aptitude signal the old flat vector ignored entirely.
    authority_liability=0.45 (was 0.60), authority_asset=0.15 (was 0.10) --
    corrects the magnitude to IPM's own declared signal_weight="medium"
    tier, no longer borrowing the_founders_grip's HIGH-tier numbers.
    alliance/attitude held flat at 0.15/0.15 -- no textual grounding for
    either axis, confirmed by re-reading the descriptive_prose fresh.

Confirmed unique against every other vector currently in this file,
including the_founders_grip and the 10-state MEDIUM-tier template (IPM is
not simply being relocated into that group -- the aptitude_asset=0.20
elevation, held against the flat template's 0.15, is what keeps it out).

the_founders_grip and the cluster's other 6 members: confirmed untouched --
this script's only EDITS entry targets the
STATE_PROFILES["invisible_performance_management"] assignment block; no
other state_id appears anywhere in this file.

Usage:
  python tools/patch_ipm_rank3_vector_differentiation.py --dry-run
  python tools/patch_ipm_rank3_vector_differentiation.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


S = "engine/data/states.py"

edit(
    S,
    'STATE_PROFILES["invisible_performance_management"].dimensional_vector = DimensionalVector(\n'
    "    # SCD-WCS full re-authoring, Phase 2 Batch 1 (2026-08-24), staged\n"
    "    # Phase 5 (2026-08-25) -- prompts/scd-wcs-full-reauthoring-\n"
    "    # program.md. Full axis flip, supersedes Candidate C: real text\n"
    '    # ("a manager\'s read... is accurate... a sound judgment") directly\n'
    "    # disclaims Aptitude as the liability -- the entire deficiency\n"
    "    # described is evidentiary/documentation weight (Authority).\n"
    "    # Dry-run confirmed clean (Phase 4c): false-rank-1 43 -> 0/175,\n"
    "    # zero new collision against the_founders_grip.\n"
    "    aptitude_liability=0.10,\n"
    "    aptitude_asset=0.10,\n"
    "    authority_liability=0.60,\n"
    "    authority_asset=0.10,\n"
    "    alliance_liability=0.10,\n"
    "    alliance_asset=0.10,\n"
    "    attitude_liability=0.10,\n"
    "    attitude_asset=0.10,\n"
    ")\n",
    'STATE_PROFILES["invisible_performance_management"].dimensional_vector = DimensionalVector(\n'
    "    # Rank-3 cluster differentiation (2026-09-14), Priority Queue item 5.\n"
    "    # f88a7c2 (2026-08-25)'s axis flip to Authority was correct -- real\n"
    "    # text is an evidentiary-weight problem, not an Aptitude one -- but\n"
    "    # it copied the_founders_grip's own HIGH-tier magnitude (0.60/0.10)\n"
    "    # verbatim, producing a byte-identical vector and landing this state\n"
    "    # in the already-diagnosed 8-state rank-3 cluster\n"
    "    # (prompts/scd-wcs-remediation-tracker.md, Stage 3-5) as an\n"
    "    # unintended side effect, not a deliberate decision. Magnitude\n"
    "    # corrected here to 0.45/0.15, matching this state's own\n"
    '    # signal_weight="medium" -- it was never actually a HIGH-tier state,\n'
    "    # the vector just carried HIGH-tier numbers. aptitude_asset raised\n"
    "    # 0.10 -> 0.20 (aptitude_liability held at 0.10, not raised to the\n"
    "    # flat 0.15 template value) on real textual grounding this state's\n"
    '    # own descriptive_prose already carries: "a manager\'s read... is\n'
    '    # accurate... a sound judgment" is an explicit asset-side Aptitude\n'
    "    # signal the flat template ignores. Confirmed unique against every\n"
    "    # other vector in this file, including the_founders_grip and the\n"
    "    # 10-state flat MEDIUM-tier Authority template (the_uninitiated,\n"
    "    # leadership_continuity_risk, decision_paralysis, the_policy_lag,\n"
    "    # dueling_narratives, transition_paralysis, the_lost_map,\n"
    "    # pay_exposure, the_pay_fog, compression_crisis) this state is not\n"
    "    # being folded back into. Full 175-profile ripple check confirmed\n"
    "    # zero flips anywhere in the suite before this shipped (scratch\n"
    "    # script, not committed). the_founders_grip and the cluster's other\n"
    "    # 6 members are explicitly untouched -- that broader architectural\n"
    "    # question stays out of scope, per Pete's explicit instruction.\n"
    "    aptitude_liability=0.10,\n"
    "    aptitude_asset=0.20,\n"
    "    authority_liability=0.45,\n"
    "    authority_asset=0.15,\n"
    "    alliance_liability=0.15,\n"
    "    alliance_asset=0.15,\n"
    "    attitude_liability=0.15,\n"
    "    attitude_asset=0.15,\n"
    ")\n",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 200 chars): {old[:200]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
