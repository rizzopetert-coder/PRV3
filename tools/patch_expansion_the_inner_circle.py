"""
MC_CENTROID_39 follow-up, Task 1 of 2: add EXP-IC-01/02/03
(the_inner_circle) to engine/test_profiles_expansion.py, closing the
zero-HC-tier-coverage gap that made RESOLUTION_TARGET=58 mathematically
unreachable during tonight's MC_CENTROID_39 reconvergence (terminal
state was 57/58, confirmed genuine impasse).

Naming convention verified against real source before writing: every
one of the 30 existing profiles in this file uses the EXP- prefix
regardless of primary_dimension (EXP-MAF is Attitude, EXP-DIA/EXP-CC/
EXP-PAG/EXP-SDB are Authority, EXP-DCF is Alliance, EXP-IPM is Aptitude,
EXP-CO/EXP-WT/EXP-HDA are also Attitude) -- the prefix marks "taxonomy-
expansion state," not dimension. Uses EXP-IC-01/02/03, not the
dimension-prefixed ATT-IC originally proposed, per Pete's confirmation
after this discrepancy was flagged.

Content basis: the_inner_circle's approved spec (Decision Register,
tools/_mob.txt Section 13a -- culture_erosion signature, Attitude-
primary, Emerging->Endemic severity range) and its live question wiring
(Q50/Q51, commit 8f36282). Structure matches the EXP_DIA_01/02/03
pattern exactly (single_state output_type, 3-tier profile_type/
severity_tier spread, standard 6-field intake dict).

expected.severity_tier values are targets to verify empirically via the
real suite, same discipline as every profile this session -- not
asserted on faith.

Usage:
  python tools/patch_expansion_the_inner_circle.py --dry-run
  python tools/patch_expansion_the_inner_circle.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PROFILES_PATH = REPO_ROOT / "engine" / "test_profiles_expansion.py"

ANCHOR = '''EXPANSION_PROFILES = [
    EXP_CC_01, EXP_CC_02, EXP_CC_03,
    EXP_SDB_01, EXP_SDB_02, EXP_SDB_03,
    EXP_DIA_01, EXP_DIA_02, EXP_DIA_03,
    EXP_PAG_01, EXP_PAG_02, EXP_PAG_03,
    EXP_WT_01, EXP_WT_02, EXP_WT_03,
    EXP_HDA_01, EXP_HDA_02, EXP_HDA_03,
    EXP_MAF_01, EXP_MAF_02, EXP_MAF_03,
    EXP_CO_01, EXP_CO_02, EXP_CO_03,
    EXP_IPM_01, EXP_IPM_02, EXP_IPM_03,
    EXP_DCF_01, EXP_DCF_02, EXP_DCF_03,
]'''

NEW_CONTENT = '''# -- Attitude: The Inner Circle (MC_CENTROID_39 follow-up, this session) --------

EXP_IC_01 = TestCase(
    test_id="EXP-IC-01",
    description=(
        "400-person financial services firm. A small group of senior leaders "
        "has covered for each other's costly mistakes for years -- one "
        "director's failed initiative was quietly absorbed, another's "
        "compliance shortcut was never escalated. Decisions on budget and "
        "promotion are made among this same small group regardless of who "
        "is closest to the issue. Staff outside the group have stopped "
        "expecting to be included."
    ),
    profile_type="high_confidence",
    target_state="the_inner_circle",
    intake={
        "headcount":          412,
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_inner_circle"],
        severity_tier="Endemic",
    ),
)

EXP_IC_02 = TestCase(
    test_id="EXP-IC-02",
    description=(
        "180-person healthcare organization. A senior leadership group has "
        "started to notice their own mistakes get less scrutiny than "
        "others', and there's some sense that decisions cluster among a "
        "familiar few. Not yet a fixed pattern across every major call."
    ),
    profile_type="moderate",
    target_state="the_inner_circle",
    intake={
        "headcount":          184,
        "industry":           "Healthcare",
        "org_type":           "Nonprofit",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_inner_circle"],
        severity_tier="Entrenched",
    ),
)

EXP_IC_03 = TestCase(
    test_id="EXP-IC-03",
    description=(
        "55-person professional services firm. One senior leader mentioned "
        "offhand that a peer's error was handled quietly. No pattern "
        "confirmed, no sense that decisions are concentrated among a "
        "specific group."
    ),
    profile_type="weak",
    target_state="the_inner_circle",
    intake={
        "headcount":          55,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_inner_circle"],
        severity_tier="Emerging",
    ),
)


EXPANSION_PROFILES = [
    EXP_CC_01, EXP_CC_02, EXP_CC_03,
    EXP_SDB_01, EXP_SDB_02, EXP_SDB_03,
    EXP_DIA_01, EXP_DIA_02, EXP_DIA_03,
    EXP_PAG_01, EXP_PAG_02, EXP_PAG_03,
    EXP_WT_01, EXP_WT_02, EXP_WT_03,
    EXP_HDA_01, EXP_HDA_02, EXP_HDA_03,
    EXP_MAF_01, EXP_MAF_02, EXP_MAF_03,
    EXP_CO_01, EXP_CO_02, EXP_CO_03,
    EXP_IPM_01, EXP_IPM_02, EXP_IPM_03,
    EXP_DCF_01, EXP_DCF_02, EXP_DCF_03,
    EXP_IC_01, EXP_IC_02, EXP_IC_03,
]'''


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = TEST_PROFILES_PATH.read_text(encoding="utf-8")
    count = content.count(ANCHOR)
    if count != 1:
        print(f"ABORT: expected exactly 1 match for anchor, found {count}")
        sys.exit(1)
    new_content = content.replace(ANCHOR, NEW_CONTENT, 1)

    if args.dry_run:
        print("=== engine/test_profiles_expansion.py: EXP-IC-01/02/03 would be added ===")
    else:
        TEST_PROFILES_PATH.write_text(new_content, encoding="utf-8")
        print("=== engine/test_profiles_expansion.py: EXP-IC-01/02/03 written ===")


if __name__ == "__main__":
    main()
