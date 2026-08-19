"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Aptitude Dimension — 19 profiles across 6 states.

Source: PRV3_Phase1_Profiles_Aptitude.md (Google Drive, Session 7)
Session 7 locked decisions applied:
  - C-Manager cluster moderate/weak: multi_state pre-distinguisher is correct output
  - Cross-dimension multi_state (APT-UR-02): Undefined Role + The Fracture — intentional
  - Paper Tiger four-profile band: APT-PT-00/01/02/03
  - APT-PT-03 pass_criterion = "top_3" (revised from rank_1, Session 7 Flag 3)
  - APT-PT-00 profile_type = "extreme_high_confidence", severity_escalation_flag = True

answers: empty at this stage — to be populated when engine is exercised end-to-end.
intake: representative values derived from profile descriptions.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Aptitude: The Unformed Leader --------------------------------------------

APT_UL_01 = TestCase(
    test_id="APT-UL-01",
    description=(
        "200-person professional services firm. One manager — strong IC promoted "
        "18 months ago — has the lowest team retention in the organization after "
        "two high-performer departures. Development investment delivered, behavior "
        "unchanged. Principal frames it as a management quality problem."
    ),
    profile_type="high_confidence",
    target_state="the_unformed_leader",
    intake={
        "headcount":          152,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_unformed_leader"],
        severity_tier="Entrenched",
    ),
)

APT_UL_02 = TestCase(
    test_id="APT-UL-02",
    description=(
        "75-person tech company. Two recently promoted IC managers producing "
        "inconsistent team outcomes. One team high engagement, the other has turnover "
        "and missed deliverables. Principal unsure if management quality or team "
        "composition. No development attempted."
    ),
    profile_type="moderate",
    target_state="the_unformed_leader",
    intake={
        "headcount":          45,
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_unformed_leader", "the_overloaded_manager"],
        severity_tier="Emerging",
    ),
)

APT_UL_03 = TestCase(
    test_id="APT-UL-03",
    description=(
        "40-person manufacturing firm. Principal mentions some managers could be "
        "better and notes one team had two departures in the past year. No pattern "
        "confirmed, no formal investigation."
    ),
    profile_type="weak",
    target_state="the_unformed_leader",
    intake={
        "headcount":          45,
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_unformed_leader", "the_overloaded_manager", "the_dormant_talent"],
        severity_tier="Emerging",
    ),
)


# -- Aptitude: The Overloaded Manager -----------------------------------------

APT_OM_01 = TestCase(
    test_id="APT-OM-01",
    description=(
        "120-person logistics company that grew 35% in 18 months. Three effective "
        "managers now carry 14-16 direct reports after expansion. Engagement dropped. "
        "Managers have strong track records at prior span. Principal attributes decline "
        "to the growth, not the managers."
    ),
    profile_type="high_confidence",
    target_state="the_overloaded_manager",
    intake={
        "headcount":          152,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["rapid_growth"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_overloaded_manager"],
        severity_tier="Emerging",
    ),
)

APT_OM_02 = TestCase(
    test_id="APT-OM-02",
    description=(
        "90-person healthcare services company post-restructuring. Two departments "
        "consolidated under one manager six months ago. Performing well in some areas, "
        "struggling in others. Principal unsure if capability or scope is the root."
    ),
    profile_type="moderate",
    target_state="the_overloaded_manager",
    intake={
        "headcount":          45,
        "industry":           "Healthcare & Life Sciences",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["restructuring_or_layoff"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_overloaded_manager", "the_unformed_leader"],
        severity_tier="Emerging",
    ),
)

APT_OM_03 = TestCase(
    test_id="APT-OM-03",
    description=(
        "55-person professional services firm. Principal mentions headcount grew "
        "last year and the management layer is stretched. No specific manager "
        "identified, no turnover data cited."
    ),
    profile_type="weak",
    target_state="the_overloaded_manager",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_overloaded_manager", "the_unformed_leader"],
        severity_tier="Emerging",
    ),
)


# -- Aptitude: The Dormant Talent ---------------------------------------------

APT_DT_01 = TestCase(
    test_id="APT-DT-01",
    description=(
        "160-person financial services firm. Senior manager — technically excellent — "
        "passed over for promotion twice in three years. Can articulate team development "
        "needs precisely. Zero development actions initiated in 18 months. Two "
        "high-potential departures citing lack of advancement."
    ),
    profile_type="high_confidence",
    target_state="the_dormant_talent",
    intake={
        "headcount":          152,
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_dormant_talent"],
        severity_tier="Entrenched",
    ),
)

APT_DT_02 = TestCase(
    test_id="APT-DT-02",
    description=(
        "70-person consulting firm. Manager hired for technical depth 18 months ago — "
        "well-liked, technically strong. Team output is good but no promotions or "
        "higher-complexity moves in the past year. Principal unsure if capability gap "
        "or nature of the work."
    ),
    profile_type="moderate",
    target_state="the_dormant_talent",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_dormant_talent", "the_unformed_leader"],
        severity_tier="Emerging",
    ),
)

APT_DT_03 = TestCase(
    test_id="APT-DT-03",
    description=(
        "45-person agency. Principal mentions a senior manager does not seem to be "
        "investing in the team but cannot cite specific departures or performance "
        "gaps. General sense, no data."
    ),
    profile_type="weak",
    target_state="the_dormant_talent",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_dormant_talent", "the_unformed_leader", "the_overloaded_manager"],
        severity_tier="Emerging",
    ),
)


# -- Aptitude: Built to Fail --------------------------------------------------

APT_BF_01 = TestCase(
    test_id="APT-BF-01",
    description=(
        "250-person manufacturing company. Regional operations director role has turned "
        "over four times in five years. Each occupant was a strong performer before and "
        "after the role. All four cited scope confusion, resource gaps, and conflicting "
        "reporting lines. Role was never formally scoped."
    ),
    profile_type="high_confidence",
    target_state="built_to_fail",
    intake={
        "headcount":          328,
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["built_to_fail"],
        severity_tier="Entrenched",
    ),
)

APT_BF_02 = TestCase(
    test_id="APT-BF-02",
    description=(
        "100-person tech company. Product lead role turned over twice in two years. "
        "Both prior occupants were strong ICs. First departure attributed to culture "
        "fit, second to compensation. Current occupant nine months in, performing "
        "unevenly. Role covers unusually broad surface."
    ),
    profile_type="moderate",
    target_state="built_to_fail",
    intake={
        "headcount":          152,
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["built_to_fail", "the_unformed_leader"],
        severity_tier="Entrenched",
    ),
)

APT_BF_03 = TestCase(
    test_id="APT-BF-03",
    description=(
        "60-person professional services firm. One senior role turned over once in "
        "18 months. Principal attributes it to a compensation mismatch. Replacement "
        "is new and performing adequately."
    ),
    profile_type="weak",
    target_state="built_to_fail",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["built_to_fail"],
        severity_tier="Emerging",
    ),
)


# -- Aptitude: The Undefined Role ---------------------------------------------

APT_UR_01 = TestCase(
    test_id="APT-UR-01",
    description=(
        "180-person professional services firm post-acquisition. Director of Client "
        "Success role created during integration escalates more decisions than any "
        "other director because the role boundaries are unclear. Manager and VP give "
        "materially different answers on role responsibilities. No formal role charter."
    ),
    profile_type="high_confidence",
    target_state="the_undefined_role",
    intake={
        "headcount":          152,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["acquisition_or_merger"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_undefined_role"],
        severity_tier="Entrenched",
    ),
)

APT_UR_02 = TestCase(
    test_id="APT-UR-02",
    description=(
        "90-person SaaS company reorganized six months ago. New Head of Revenue Ops "
        "duplicating work with Sales Ops. Principal unsure if role design issue or "
        "interpersonal conflict between the two leaders. Cross-dimension: Undefined "
        "Role + The Fracture."
    ),
    profile_type="moderate",
    target_state="the_undefined_role",
    intake={
        "headcount":          45,
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["restructuring_or_layoff"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_undefined_role", "the_fracture"],
        severity_tier="Emerging",
    ),
)

APT_UR_03 = TestCase(
    test_id="APT-UR-03",
    description=(
        "50-person agency. New role created three months ago that has not quite "
        "found its footing yet. No escalation pattern, no documented confusion. "
        "Role occupant is new."
    ),
    profile_type="weak",
    target_state="the_undefined_role",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_undefined_role"],
        severity_tier="Emerging",
    ),
)


# -- Aptitude: The Paper Tiger (four-profile band) ----------------------------

APT_PT_00 = TestCase(
    test_id="APT-PT-00",
    description=(
        "110-person logistics company. Warehouse shift supervisor verbally documented "
        "as chronic underperformer by three successive operations managers over two "
        "years is being terminated today. HR learned of the termination when the "
        "manager called about final pay. Personnel file has no written warnings, no "
        "PIPs, two annual reviews rating meets expectations. Supervisor is a 58-year-old "
        "Black woman. Termination letter already delivered."
    ),
    profile_type="extreme_high_confidence",
    target_state="the_paper_tiger",
    intake={
        "headcount":          152,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_paper_tiger"],
        severity_tier="Entrenched",
        pass_criterion="top_3_with_escalation_flag",
        severity_escalation_flag=True,
    ),
)

APT_PT_01 = TestCase(
    test_id="APT-PT-01",
    description=(
        "140-person distribution company. Warehouse manager verbally documented as "
        "poor performer by operations VP for 14 months, being terminated this week. "
        "HR not involved in the process. Personnel file has satisfactory annual "
        "reviews. Manager is a member of a protected class."
    ),
    profile_type="high_confidence",
    target_state="the_paper_tiger",
    intake={
        "headcount":          152,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_paper_tiger"],
        severity_tier="Entrenched",
    ),
)

APT_PT_02 = TestCase(
    test_id="APT-PT-02",
    description=(
        "85-person professional services firm. Client-facing manager informally "
        "managed out over six months — workload reduced, client assignments pulled, "
        "key meeting invitations stopped. No formal PIP. Manager not told employment "
        "is at risk. HR aware but has not formalized the process. Manager is male, age 52."
    ),
    profile_type="moderate",
    target_state="the_paper_tiger",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_paper_tiger"],
        severity_tier="Entrenched",
    ),
)

APT_PT_03 = TestCase(
    test_id="APT-PT-03",
    description=(
        "60-person healthcare services company. Principal mentions a manager probably "
        "needs to go but no formal process has started. Documentation: stuff in emails. "
        "No HR involvement. No timeline."
    ),
    profile_type="weak",
    target_state="the_paper_tiger",
    intake={
        "headcount":          45,
        "industry":           "Healthcare & Life Sciences",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_paper_tiger", "the_undefined_role", "the_unformed_leader"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Aptitude profile collection ----------------------------------------------

APTITUDE_PROFILES: list = [
    APT_UL_01, APT_UL_02, APT_UL_03,
    APT_OM_01, APT_OM_02, APT_OM_03,
    APT_DT_01, APT_DT_02, APT_DT_03,
    APT_BF_01, APT_BF_02, APT_BF_03,
    APT_UR_01, APT_UR_02, APT_UR_03,
    APT_PT_00, APT_PT_01, APT_PT_02, APT_PT_03,
]
