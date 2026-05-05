#!/usr/bin/env python
"""
PRV3 — patch_attitude_b2_profiles.py
Creates engine/test_profiles_attitude_b2.py with 12 Attitude Phase 1 test profiles.

Source: PRV3_Phase1_Profiles_Attitude_B2 (Google Drive, Session 7)
States: What Nobody Says (C-Silence) · The Unreported Hazard (C-Silence)
        The Unlocked Door (C-Silence) · Leadership Deafness (C-InfoFlow)

Cluster design:
  - C-Silence: high_confidence profiles assume distinguisher resolved.
    Moderate/weak are pre-distinguisher — co-signal with other cluster state(s).
  - C-InfoFlow: high_confidence assumes executive-layer confirmed.
    Moderate/weak pair [leadership_deafness, the_suppression_filter].

Severity caps:
  - the_unreported_hazard: sev_max=Entrenched (no Endemic)
  - the_unlocked_door: sev_max=Entrenched (no Endemic)
  - leadership_deafness: sev_min=Entrenched (no Emerging)

Pass-criterion overrides (weak profiles):
  ATT-WNS-03, ATT-UH-03, ATT-UD-03, ATT-LD-03 → pass_criterion="top_3"

Usage:
  python tools/patch_attitude_b2_profiles.py --dry-run
  python tools/patch_attitude_b2_profiles.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "test_profiles_attitude_b2.py"

CONTENT = '''\
"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Attitude Dimension — Batch 2: 12 profiles across 4 cluster states.

Source: PRV3_Phase1_Profiles_Attitude_B2 (Google Drive, Session 7)
States: What Nobody Says (C-Silence) · The Unreported Hazard (C-Silence)
        The Unlocked Door (C-Silence) · Leadership Deafness (C-InfoFlow)

answers: empty at this stage — to be populated when engine is exercised end-to-end.
intake: representative values derived from profile descriptions.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Attitude: What Nobody Says -----------------------------------------------

ATT_WNS_01 = TestCase(
    test_id="ATT-WNS-01",
    description=(
        "240-person financial services firm. An anonymous pulse survey found that "
        "71% of employees \\'rarely or never\\' share concerns directly with their "
        "manager. Exit interviews over two years reveal a consistent pattern: "
        "departing employees describe having held concerns for months before "
        "leaving, citing prior instances where colleagues who raised concerns were "
        "sidelined or excluded from projects. Three specific incidents — all within "
        "the past 18 months — are referenced repeatedly across exit interviews by "
        "employees who were not part of those incidents. The C-Silence distinguisher "
        "has confirmed: the silence is general organizational candor suppression, "
        "not safety- or security-specific. Leadership has no skip-level mechanism."
    ),
    profile_type="high_confidence",
    target_state="what_nobody_says",
    intake={
        "headcount":          "100-249",
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["what_nobody_says"],
        severity_tier="Endemic",
    ),
)

ATT_WNS_02 = TestCase(
    test_id="ATT-WNS-02",
    description=(
        "130-person technology company. The CEO describes meetings as \\'very "
        "polished — real disagreement doesn\\'t surface until after.\\' Two 1:1 "
        "conversations with direct reports in the past month produced concerns the "
        "CEO hadn\\'t heard before, despite the issues apparently being known for "
        "weeks. The C-Silence distinguisher has not yet fired — the domain of "
        "silence is unclear. No safety or security incidents. No specific prior "
        "consequence named by employees."
    ),
    profile_type="moderate",
    target_state="what_nobody_says",
    intake={
        "headcount":          "100-249",
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["what_nobody_says", "the_suppression_filter"],
        severity_tier="Emerging",
    ),
)

ATT_WNS_03 = TestCase(
    test_id="ATT-WNS-03",
    description=(
        "80-person professional services firm. The principal says they \\'sometimes "
        "feel like people aren\\'t being fully candid.\\' No survey data. No "
        "specific incident. No named prior consequence. General intuition."
    ),
    profile_type="weak",
    target_state="what_nobody_says",
    intake={
        "headcount":          "25-99",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["what_nobody_says", "the_suppression_filter", "leadership_deafness"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Attitude: The Unreported Hazard ------------------------------------------

ATT_UH_01 = TestCase(
    test_id="ATT-UH-01",
    description=(
        "190-person distribution company. OSHA recordable incident rate is "
        "3.2 per 100 workers — 2.1x the industry benchmark. Post-incident "
        "interviews from the past 18 months reveal a consistent pattern: in "
        "7 of 9 recordable incidents, coworkers were aware of the precursor "
        "condition and did not report it. Reasons given include \\'didn\\'t want "
        "to slow down production,\\' \\'didn\\'t think anyone would listen,\\' and "
        "\\'last time someone reported something, they got extra scrutiny.\\' The "
        "C-Silence distinguisher has confirmed: silence is safety-specific. "
        "Near-miss reporting is at near-zero despite industry guidance suggesting "
        "near-misses should outnumber incidents 30:1."
    ),
    profile_type="high_confidence",
    target_state="the_unreported_hazard",
    intake={
        "headcount":          "100-249",
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_unreported_hazard"],
        severity_tier="Entrenched",
    ),
)

ATT_UH_02 = TestCase(
    test_id="ATT-UH-02",
    description=(
        "100-person light manufacturing company. The principal is \\'not sure\\' "
        "the incident reporting culture is healthy — the safety committee meets "
        "monthly but the principal doesn\\'t feel they\\'re hearing about "
        "near-misses. Two incidents in the past year were reported externally by "
        "employees rather than through the internal system. The C-Silence "
        "distinguisher has not fired. General candor concerns have not been raised."
    ),
    profile_type="moderate",
    target_state="the_unreported_hazard",
    intake={
        "headcount":          "100-249",
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_unreported_hazard", "what_nobody_says"],
        severity_tier="Emerging",
    ),
)

ATT_UH_03 = TestCase(
    test_id="ATT-UH-03",
    description=(
        "65-person manufacturing company. The principal mentions they\\'re "
        "\\'probably not hearing about every issue on the floor.\\' No incident "
        "data. No reported near-misses. No specific incidents cited."
    ),
    profile_type="weak",
    target_state="the_unreported_hazard",
    intake={
        "headcount":          "25-99",
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_unreported_hazard", "what_nobody_says"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Attitude: The Unlocked Door ----------------------------------------------

ATT_UD_01 = TestCase(
    test_id="ATT-UD-01",
    description=(
        "165-person healthcare services company (HIPAA-covered entity). Annual "
        "security training is mandatory and completion rate is 98%. Three months "
        "ago, a phishing simulation test produced a 34% click-through rate — well "
        "above the 5% target. Two weeks later, a real phishing attack succeeded "
        "against four employees, resulting in a reportable breach of 2,400 patient "
        "records. Post-breach interviews found employees described their behavior "
        "as \\'I thought I was doing what I was supposed to do\\' — they had "
        "completed the training but had not changed their behavior. The C-Silence "
        "distinguisher has confirmed: silence is security-specific. General candor "
        "is not suppressed."
    ),
    profile_type="high_confidence",
    target_state="the_unlocked_door",
    intake={
        "headcount":          "100-249",
        "industry":           "Healthcare & Life Sciences",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_unlocked_door"],
        severity_tier="Entrenched",
    ),
)

ATT_UD_02 = TestCase(
    test_id="ATT-UD-02",
    description=(
        "95-person financial services company (PCI-DSS obligation). Security "
        "training is completed annually. The IT team has flagged informal password "
        "sharing between colleagues in two departments. No security incident has "
        "occurred. The C-Silence distinguisher has not fired."
    ),
    profile_type="moderate",
    target_state="the_unlocked_door",
    intake={
        "headcount":          "25-99",
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_unlocked_door", "what_nobody_says"],
        severity_tier="Emerging",
    ),
)

ATT_UD_03 = TestCase(
    test_id="ATT-UD-03",
    description=(
        "55-person professional services firm. The principal mentions employees "
        "\\'probably don\\'t follow all the security protocols\\' — no specific "
        "incident, no simulation data, no regulatory obligation named."
    ),
    profile_type="weak",
    target_state="the_unlocked_door",
    intake={
        "headcount":          "25-99",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_unlocked_door", "what_nobody_says"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Attitude: Leadership Deafness --------------------------------------------

ATT_LD_01 = TestCase(
    test_id="ATT-LD-01",
    description=(
        "275-person financial services firm. The CEO received a 360-degree "
        "feedback assessment last year showing a 42-point gap between their "
        "self-assessment and direct report assessment on openness to feedback. "
        "In the past 18 months: two regulatory matters that became material were "
        "known to the direct report layer 6-8 weeks before the CEO was informed. "
        "An acquisition target due diligence finding was raised internally by one "
        "VP and not escalated because it \\'wasn\\'t the kind of thing you brought "
        "to [CEO].\\' The C-InfoFlow distinguisher has confirmed: the breakdown is "
        "at the executive layer — direct reports to the CEO are filtering based on "
        "the CEO\\'s known response to unwelcome information."
    ),
    profile_type="high_confidence",
    target_state="leadership_deafness",
    intake={
        "headcount":          "250-499",
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["leadership_deafness"],
        severity_tier="Endemic",
    ),
)

ATT_LD_02 = TestCase(
    test_id="ATT-LD-02",
    description=(
        "140-person technology company. The CEO feels they are \\'always the last "
        "to know\\' about problems. In two recent cases, product issues were known "
        "at the engineering level for 2-3 weeks before reaching the CEO. The CEO "
        "attributes this to \\'people trying to solve problems before escalating.\\' "
        "No 360 assessment has been conducted. No skip-level mechanism. The "
        "C-InfoFlow distinguisher has not fired — the hierarchy level of filtering "
        "is unconfirmed."
    ),
    profile_type="moderate",
    target_state="leadership_deafness",
    intake={
        "headcount":          "100-249",
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["leadership_deafness", "the_suppression_filter"],
        severity_tier="Entrenched",
    ),
)

ATT_LD_03 = TestCase(
    test_id="ATT-LD-03",
    description=(
        "80-person professional services firm. The principal says they \\'sometimes "
        "feel out of the loop.\\' No specific examples. No data. General sense."
    ),
    profile_type="weak",
    target_state="leadership_deafness",
    intake={
        "headcount":          "25-99",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["leadership_deafness", "the_suppression_filter"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Attitude B2 profile collection -------------------------------------------

ATTITUDE_B2_PROFILES: list = [
    ATT_WNS_01, ATT_WNS_02, ATT_WNS_03,
    ATT_UH_01,  ATT_UH_02,  ATT_UH_03,
    ATT_UD_01,  ATT_UD_02,  ATT_UD_03,
    ATT_LD_01,  ATT_LD_02,  ATT_LD_03,
]
'''


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create engine/test_profiles_attitude_b2.py"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be written without writing",
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Write the file",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    if args.dry_run:
        print(f"DRY RUN — target: {TARGET}")
        print(f"  File exists: {TARGET.exists()}")
        lines = CONTENT.splitlines()
        profile_lines = [l for l in lines if "profile_type=" in l]
        state_lines   = [l for l in lines if "target_state=" in l]
        print(f"  Profiles in CONTENT: {len(profile_lines)}")
        print(f"  Unique target_states: {len(set(state_lines))}")
        print()
        rows = []
        current_id = current_type = current_state = None
        for line in lines:
            line = line.strip()
            if line.startswith('test_id='):
                current_id = line.split('"')[1]
            elif line.startswith('profile_type='):
                current_type = line.split('"')[1]
            elif line.startswith('target_state='):
                current_state = line.split('"')[1]
                if current_id and current_type and current_state:
                    rows.append((current_id, current_state, current_type))
                    current_id = current_type = current_state = None
        print(f"  {'test_id':<14} {'target_state':<42} {'profile_type'}")
        print(f"  {'-'*14} {'-'*42} {'-'*20}")
        for tid, state, ptype in rows:
            print(f"  {tid:<14} {state:<42} {ptype}")
        print(f"\n  Total: {len(rows)} profiles")
        return

    if args.write:
        TARGET.write_text(CONTENT, encoding="utf-8")
        print(f"WRITTEN: {TARGET}")
        lines = CONTENT.splitlines()
        profile_count = sum(1 for l in lines if "profile_type=" in l)
        print(f"  {profile_count} profiles written")


if __name__ == "__main__":
    main()
