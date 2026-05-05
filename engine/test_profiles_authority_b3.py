"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Authority Dimension — Batch 3: 12 profiles across 4 states.

Source: PRV3_Phase1_Profiles_Authority_B3 (Google Drive, Session 8)
States: The Unexamined Algorithm · Paper Shield · Invisible Influence Architecture
        The Lost Map

Batch 3 design constraint: all weak profiles use pass_criterion = "top_3".
Low-signal-weight confirmatory states — weak signal cannot justify rank_1.

answers: empty at this stage — to be populated when engine is exercised end-to-end.
intake: representative values derived from profile descriptions.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Authority: The Unexamined Algorithm --------------------------------------

AUT_UA_01 = TestCase(
    test_id="AUT-UA-01",
    description=(
        "280-person financial services firm. AI-based resume screening tool deployed "
        "18 months ago for all external hiring — approximately 400 applications per "
        "year. No bias audit conducted; vendor does not provide audit capability. HR "
        "did not review implementation before deployment. No governance owner assigned. "
        "Counsel flagged AI-in-hiring compliance risk at the last quarterly review. "
        "Principal was not aware the tool existed until counsel raised it. Company has "
        "New York offices — NYC Local Law 144 requires a bias audit."
    ),
    profile_type="high_confidence",
    target_state="the_unexamined_algorithm",
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
        identified_states=["the_unexamined_algorithm"],
        severity_tier="Entrenched",
    ),
)

AUT_UA_02 = TestCase(
    test_id="AUT-UA-02",
    description=(
        "130-person technology company. Recruiting team uses an AI tool to rank "
        "candidates for engineering roles — selected by the recruiting manager, in use "
        "for 8 months. HR is aware. Bias audit not conducted; principal isn\'t sure "
        "if one is required. Company does not have New York offices but hires in "
        "California, which has proposed but not finalized AI hiring regulations. "
        "No governance owner assigned."
    ),
    profile_type="moderate",
    target_state="the_unexamined_algorithm",
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
        identified_states=["the_unexamined_algorithm", "the_policy_lag"],
        severity_tier="Emerging",
    ),
)

AUT_UA_03 = TestCase(
    test_id="AUT-UA-03",
    description=(
        "75-person professional services firm. Principal mentions they might be using "
        "some AI tools in recruiting — not sure which ones or how. No bias audit. "
        "No governance owner. Not hiring in jurisdictions with current AI hiring "
        "regulations."
    ),
    profile_type="weak",
    target_state="the_unexamined_algorithm",
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
        identified_states=["the_unexamined_algorithm", "the_policy_lag"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority: Paper Shield --------------------------------------------------

AUT_PS_01 = TestCase(
    test_id="AUT-PS-01",
    description=(
        "210-person manufacturing company. Business continuity plan, succession plan "
        "for the top five roles, and IT disaster recovery plan — all produced three "
        "years ago for an insurance audit. Since then: COO named as successor left "
        "18 months ago, IT systems referenced in the DR plan substantially replaced, "
        "and a vendor relationship referenced in the BCP was terminated. No plan "
        "reviewed or updated since. A significant weather event last year required "
        "an improvised response — the BCP was not consulted. Principal describes "
        "continuity planning as \'solid.\'"
    ),
    profile_type="high_confidence",
    target_state="paper_shield",
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
        identified_states=["paper_shield"],
        severity_tier="Entrenched",
    ),
)

AUT_PS_02 = TestCase(
    test_id="AUT-PS-02",
    description=(
        "115-person healthcare services company. Succession plan for senior roles "
        "produced two years ago. Plan not tested or reviewed since. One role named "
        "in the plan has changed occupants — the new person is not in the plan. "
        "Principal isn\'t sure if the plan is current but assumes it\'s "
        "\'probably fine.\'"
    ),
    profile_type="moderate",
    target_state="paper_shield",
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
        output_type="multi_state",
        identified_states=["paper_shield", "leadership_continuity_risk"],
        severity_tier="Emerging",
    ),
)

AUT_PS_03 = TestCase(
    test_id="AUT-PS-03",
    description=(
        "65-person professional services firm. Principal mentions they have some "
        "continuity planning but isn\'t sure what it covers or when it was last "
        "updated. No specific gaps identified. No real events that tested the plans."
    ),
    profile_type="weak",
    target_state="paper_shield",
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
        identified_states=["paper_shield", "leadership_continuity_risk"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority: Invisible Influence Architecture ------------------------------

AUT_IA_01 = TestCase(
    test_id="AUT-IA-01",
    description=(
        "165-person technology company. Six months ago the company reorganized — "
        "consolidating four product teams into two. Three months post-reorg, "
        "cross-team coordination has degraded significantly. Two people eliminated "
        "in the restructuring have since been identified as the primary connectors "
        "between the old teams — they ran informal syncs, maintained cross-team "
        "relationships, and were the first call for cross-functional issues. Both "
        "left without knowledge transfer. Current teams cannot identify who to call "
        "for cross-functional decisions. CEO describes the reorg as "
        "\'mostly successful.\'"
    ),
    profile_type="high_confidence",
    target_state="invisible_influence_architecture",
    intake={
        "headcount":          "100-249",
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["restructuring_or_layoff"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["invisible_influence_architecture"],
        severity_tier="Entrenched",
    ),
)

AUT_IA_02 = TestCase(
    test_id="AUT-IA-02",
    description=(
        "90-person professional services firm. Reorganized 10 months ago, "
        "consolidating service lines. Reorganization has gone \'better than expected\' "
        "but two cross-functional projects have stalled in the past three months — "
        "teams can\'t coordinate effectively. Principal attributes it to "
        "\'people still adjusting.\' No specific individuals identified as the "
        "coordination gap."
    ),
    profile_type="moderate",
    target_state="invisible_influence_architecture",
    intake={
        "headcount":          "25-99",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["restructuring_or_layoff"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["invisible_influence_architecture", "the_lost_map"],
        severity_tier="Emerging",
    ),
)

AUT_IA_03 = TestCase(
    test_id="AUT-IA-03",
    description=(
        "70-person agency. Principal mentions they reorganized a while back and things "
        "felt a bit disjointed for a while but seem to have settled. No specific "
        "coordination failures named currently. One team lead left during the "
        "reorg period."
    ),
    profile_type="weak",
    target_state="invisible_influence_architecture",
    intake={
        "headcount":          "25-99",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["restructuring_or_layoff"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["invisible_influence_architecture", "the_lost_map"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority: The Lost Map --------------------------------------------------

AUT_LM_01 = TestCase(
    test_id="AUT-LM-01",
    description=(
        "240-person financial services firm. Leadership communicated three strategic "
        "priorities twice this quarter — in an all-hands and a written memo. A recent "
        "pulse survey asked employees to name the top three priorities: 40% named "
        "priorities not on the current list, 25% could name one of three, and 12% "
        "named all three correctly. Communications team believes the message has "
        "landed because all-hands had 94% attendance. Decision implementation "
        "inconsistent across functions — teams making local decisions that contradict "
        "organizational direction they weren\'t aware had changed."
    ),
    profile_type="high_confidence",
    target_state="the_lost_map",
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
        identified_states=["the_lost_map"],
        severity_tier="Entrenched",
    ),
)

AUT_LM_02 = TestCase(
    test_id="AUT-LM-02",
    description=(
        "110-person technology company. CEO communicates strategic updates in a monthly "
        "newsletter. Several managers have told HR they feel out of the loop — learning "
        "about decisions from their teams rather than from leadership. No pulse survey "
        "data. CEO believes communication is adequate."
    ),
    profile_type="moderate",
    target_state="the_lost_map",
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
        identified_states=["the_lost_map", "leadership_deafness"],
        severity_tier="Emerging",
    ),
)

AUT_LM_03 = TestCase(
    test_id="AUT-LM-03",
    description=(
        "65-person agency. Principal mentions that communication could probably be "
        "better — things sometimes feel siloed. No specific gaps named. "
        "No employee feedback data."
    ),
    profile_type="weak",
    target_state="the_lost_map",
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
        identified_states=["the_lost_map", "silosolation"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority B3 profile collection ------------------------------------------

AUTHORITY_B3_PROFILES: list = [
    AUT_UA_01, AUT_UA_02, AUT_UA_03,
    AUT_PS_01, AUT_PS_02, AUT_PS_03,
    AUT_IA_01, AUT_IA_02, AUT_IA_03,
    AUT_LM_01, AUT_LM_02, AUT_LM_03,
]
