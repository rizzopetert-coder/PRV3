"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Authority Dimension — Batch 2: 24 profiles across 8 states.

Source: PRV3_Phase1_Profiles_Authority_B2 (Google Drive, Session 8)
States: The Uninitiated · Leadership Continuity Risk · Decision Paralysis · The Policy Lag
        Transition Paralysis · Dueling Narratives · Pay Exposure · The Pay Fog

Session locked design decisions:
  - AUT-UN-01: severity = Emerging at high_confidence (acute event, locked by taxonomy)
  - AUT-PE moderate/weak and AUT-PF moderate/weak: same pair [pay_exposure, the_pay_fog]
  - Cross-dimension co-signals: AUT-DN-02 + leadership_deafness, AUT-DN-03 + culture_drift
  - AUT-DP-03, AUT-DN-03, AUT-PE-03, AUT-PF-03: pass_criterion = "top_3"

answers: empty at this stage — to be populated when engine is exercised end-to-end.
intake: representative values derived from profile descriptions.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Authority: The Uninitiated -----------------------------------------------

AUT_UN_01 = TestCase(
    test_id="AUT-UN-01",
    description=(
        "90-person professional services firm. Completed first acquisition — a "
        "30-person boutique — 6 months ago. No prior M&A experience on either side "
        "of the leadership table. Integration managed by COO with no prior M&A "
        "experience. Acquired team\'s two most senior people have resigned. Client "
        "retention from acquired book at 60%, below 85% deal-model target. No "
        "integration plan was produced before close; one is being written now."
    ),
    profile_type="high_confidence",
    target_state="the_uninitiated",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["acquisition_or_merger"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_uninitiated"],
        severity_tier="Emerging",
    ),
)

AUT_UN_02 = TestCase(
    test_id="AUT-UN-02",
    description=(
        "60-person technology company navigating its first significant regulatory "
        "inquiry — a state AG investigation into data practices. CEO engaged outside "
        "counsel. Legal team experienced but the internal leadership team has never "
        "navigated a regulatory event. CEO asking \'how concerned should I be?\' "
        "No prior regulatory experience in the leadership team."
    ),
    profile_type="moderate",
    target_state="the_uninitiated",
    intake={
        "headcount":          45,
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["the_uninitiated", "the_exposed"],
        severity_tier="Emerging",
    ),
)

AUT_UN_03 = TestCase(
    test_id="AUT-UN-03",
    description=(
        "45-person professional services firm. Founder considering a private equity "
        "raise — their first. No prior PE experience in the leadership team. No process "
        "has started; founder is in early conversations only. No advisors engaged yet."
    ),
    profile_type="weak",
    target_state="the_uninitiated",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Founder-led",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_uninitiated"],
        severity_tier="Emerging",
    ),
)


# -- Authority: Leadership Continuity Risk ------------------------------------

AUT_LC_01 = TestCase(
    test_id="AUT-LC-01",
    description=(
        "160-person financial services firm. CFO — in role for 11 years, sole owner "
        "of all banking relationships and financial systems knowledge — announced her "
        "resignation last month. No named successor. Organization has never conducted "
        "a succession planning exercise. CEO describes the situation as \'we\'re going "
        "to have to figure this out.\' Three board members have asked about the "
        "transition plan."
    ),
    profile_type="high_confidence",
    target_state="leadership_continuity_risk",
    intake={
        "headcount":          152,
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["leadership_departure"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["leadership_continuity_risk"],
        severity_tier="Entrenched",
    ),
)

AUT_LC_02 = TestCase(
    test_id="AUT-LC-02",
    description=(
        "100-person healthcare services organization. Long-tenured Medical Director "
        "approaching retirement — likely in 12 to 18 months. Principal is aware and "
        "thinking about it. No formal succession plan. One internal candidate "
        "informally considered a possible successor but not developed or assessed. "
        "No outside search initiated."
    ),
    profile_type="moderate",
    target_state="leadership_continuity_risk",
    intake={
        "headcount":          152,
        "industry":           "Healthcare & Life Sciences",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["leadership_continuity_risk", "paper_shield"],
        severity_tier="Emerging",
    ),
)

AUT_LC_03 = TestCase(
    test_id="AUT-LC-03",
    description=(
        "70-person professional services firm. Principal mentions two of their three "
        "senior partners are getting to the age where succession needs to be considered. "
        "No departures imminent. No timeline named. No formal succession process. "
        "The topic has come up in conversation but has not been actioned."
    ),
    profile_type="weak",
    target_state="leadership_continuity_risk",
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
        identified_states=["leadership_continuity_risk"],
        severity_tier="Emerging",
    ),
)


# -- Authority: Decision Paralysis --------------------------------------------

AUT_DP_01 = TestCase(
    test_id="AUT-DP-01",
    description=(
        "200-person professional services firm post-merger. Merged entity has two "
        "COOs — one from each legacy organization — with no defined decision authority "
        "between them. Consequential decisions escalated to CEO by default because "
        "neither COO can commit without the other\'s buy-in. CEO consumed by decisions "
        "that should not require CEO involvement. Three decisions in the past six months "
        "reversed after announcement because the other COO objected."
    ),
    profile_type="high_confidence",
    target_state="decision_paralysis",
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
        identified_states=["decision_paralysis"],
        severity_tier="Entrenched",
    ),
)

AUT_DP_02 = TestCase(
    test_id="AUT-DP-02",
    description=(
        "110-person technology company. Decisions about product roadmap made in "
        "leadership meetings, then relitigated via Slack, then re-decided in follow-up "
        "meetings. CTO and CPO frequently disagree; principal characterizes it as "
        "\'healthy debate.\' No decision formally reversed but implementation "
        "consistently lags decision date by 2 to 4 weeks while team waits for "
        "\'final confirmation.\'"
    ),
    profile_type="moderate",
    target_state="decision_paralysis",
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
        identified_states=["decision_paralysis", "the_fracture"],
        severity_tier="Emerging",
    ),
)

AUT_DP_03 = TestCase(
    test_id="AUT-DP-03",
    description=(
        "65-person agency. Principal mentions they \'sometimes struggle to make "
        "decisions stick.\' No specific examples cited. No pattern across decision "
        "types. Principal describes it as an occasional frustration."
    ),
    profile_type="weak",
    target_state="decision_paralysis",
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
        identified_states=["decision_paralysis", "the_fracture"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority: The Policy Lag ------------------------------------------------

AUT_PL_01 = TestCase(
    test_id="AUT-PL-01",
    description=(
        "150-person technology company operating in California, Colorado, and New York. "
        "Employee handbook last updated in 2022. Pay transparency laws in all three "
        "states have taken effect since then — company has not updated job posting "
        "practices or compensation disclosure processes. A candidate asked about pay "
        "range last week; recruiter didn\'t know how to respond. Outside counsel "
        "flagged the issue in a quarterly review two months ago."
    ),
    profile_type="high_confidence",
    target_state="the_policy_lag",
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
        output_type="single_state",
        identified_states=["the_policy_lag"],
        severity_tier="Entrenched",
    ),
)

AUT_PL_02 = TestCase(
    test_id="AUT-PL-02",
    description=(
        "85-person professional services firm. Principal mentions employee handbook "
        "\'probably needs updating\' — not sure when it was last reviewed. A manager "
        "recently asked HR about remote work policy and HR didn\'t have a clear answer. "
        "No counsel review has occurred. No specific compliance situation has arisen. "
        "Principal is aware but hasn\'t prioritized it."
    ),
    profile_type="moderate",
    target_state="the_policy_lag",
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
        identified_states=["the_policy_lag", "the_tolerated_violation"],
        severity_tier="Emerging",
    ),
)

AUT_PL_03 = TestCase(
    test_id="AUT-PL-03",
    description=(
        "55-person agency. Principal isn\'t sure when their employment policies were "
        "last reviewed — \'a while ago.\' No specific situation has arisen. No questions "
        "from employees or managers about policy gaps. No counsel review."
    ),
    profile_type="weak",
    target_state="the_policy_lag",
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
        identified_states=["the_policy_lag"],
        severity_tier="Emerging",
    ),
)


# -- Authority: Transition Paralysis ------------------------------------------

AUT_TP_01 = TestCase(
    test_id="AUT-TP-01",
    description=(
        "180-person manufacturing company. ERP system transition began 8 months ago. "
        "Legacy system partially decommissioned at month four; new system was to go "
        "live at month six. Now at month eight — new system not live, legacy partially "
        "dismantled, operational decisions made on spreadsheets and workarounds. "
        "Finance cannot produce reliable reports. Implementation vendor says go-live "
        "is \'still a few weeks away.\'"
    ),
    profile_type="high_confidence",
    target_state="transition_paralysis",
    intake={
        "headcount":          152,
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["transition_paralysis"],
        severity_tier="Emerging",
    ),
)

AUT_TP_02 = TestCase(
    test_id="AUT-TP-02",
    description=(
        "95-person professional services firm. Moved to a new project management "
        "platform 3 months ago. Old platform still accessible but team is supposed to "
        "use the new one. Half the team on the new platform, half still on the old one. "
        "Project status visibility fragmented. No hard cutoff date set for the "
        "legacy platform."
    ),
    profile_type="moderate",
    target_state="transition_paralysis",
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
        identified_states=["transition_paralysis", "decision_paralysis"],
        severity_tier="Emerging",
    ),
)

AUT_TP_03 = TestCase(
    test_id="AUT-TP-03",
    description=(
        "60-person agency. Currently in the middle of moving to a new HR platform. "
        "Principal doesn\'t know the timeline. Old system still running. "
        "No issues named yet."
    ),
    profile_type="weak",
    target_state="transition_paralysis",
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
        identified_states=["transition_paralysis"],
        severity_tier="Emerging",
    ),
)


# -- Authority: Dueling Narratives --------------------------------------------

AUT_DN_01 = TestCase(
    test_id="AUT-DN-01",
    description=(
        "220-person financial services firm. Public DEI commitments — in annual report "
        "and on careers page — include specific representation targets and pay equity "
        "commitments. Internally: two DEI initiatives quietly defunded 6 months ago, "
        "pay equity analysis committed to in the report not conducted, and "
        "representation data in the report drawn from a pre-departure snapshot that "
        "no longer reflects current numbers. IR and people teams operate independently "
        "with no coordinating review process."
    ),
    profile_type="high_confidence",
    target_state="dueling_narratives",
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
        identified_states=["dueling_narratives"],
        severity_tier="Entrenched",
    ),
)

AUT_DN_02 = TestCase(
    test_id="AUT-DN-02",
    description=(
        "120-person technology company. CEO regularly describes company culture in "
        "external interviews as flat, transparent, and collaborative. Internally, two "
        "senior leaders have flagged to HR that decisions are made in small groups "
        "without broad input. Concern has not escalated externally. CEO is not aware "
        "of the internal feedback."
    ),
    profile_type="moderate",
    target_state="dueling_narratives",
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
        identified_states=["dueling_narratives", "leadership_deafness"],
        severity_tier="Emerging",
    ),
)

AUT_DN_03 = TestCase(
    test_id="AUT-DN-03",
    description=(
        "70-person professional services firm. Principal mentions their website "
        "describes them as a \'best place to work\' based on an award from three years "
        "ago. Recent internal survey results were mixed. No external commitments "
        "beyond the website language."
    ),
    profile_type="weak",
    target_state="dueling_narratives",
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
        identified_states=["dueling_narratives", "culture_drift"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority: Pay Exposure --------------------------------------------------

AUT_PE_01 = TestCase(
    test_id="AUT-PE-01",
    description=(
        "175-person technology company. Five senior software engineers resigned in the "
        "past 18 months — all citing compensation as the primary reason. Exit interviews "
        "confirm competing offers 20 to 35% above current base. Last compensation "
        "benchmarking exercise was three years ago. Engineering manager says they can "
        "no longer recruit at the level the business needs. Three senior engineering "
        "roles unfilled for more than four months."
    ),
    profile_type="high_confidence",
    target_state="pay_exposure",
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
        output_type="single_state",
        identified_states=["pay_exposure"],
        severity_tier="Entrenched",
    ),
)

AUT_PE_02 = TestCase(
    test_id="AUT-PE-02",
    description=(
        "100-person healthcare services company. Principal aware they probably pay "
        "below market in nursing roles but believes total compensation — benefits, "
        "stability, mission — compensates. Two nurses left in the past year citing pay. "
        "Recruitment in nursing has taken longer than usual. No formal market analysis "
        "conducted."
    ),
    profile_type="moderate",
    target_state="pay_exposure",
    intake={
        "headcount":          152,
        "industry":           "Healthcare & Life Sciences",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["pay_exposure", "the_pay_fog"],
        severity_tier="Emerging",
    ),
)

AUT_PE_03 = TestCase(
    test_id="AUT-PE-03",
    description=(
        "60-person professional services firm. Principal mentions they\'ve heard the "
        "firm might be a little low on pay for some roles — one employee mentioned it "
        "informally. No departures cited. No recruitment difficulty named."
    ),
    profile_type="weak",
    target_state="pay_exposure",
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
        identified_states=["pay_exposure", "the_pay_fog"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority: The Pay Fog ---------------------------------------------------

AUT_PF_01 = TestCase(
    test_id="AUT-PF-01",
    description=(
        "190-person professional services firm operating in California and New York. "
        "Pay ranges have never been formally established — compensation set through "
        "individual negotiation for each hire over 12 years. Internal review found "
        "two employees in the same role with equivalent tenure differ in base salary "
        "by 31%. Company is required to post pay ranges in California and New York for "
        "open roles this year. HR cannot produce the ranges. Three employees have asked "
        "about pay ranges in the past month."
    ),
    profile_type="high_confidence",
    target_state="the_pay_fog",
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
        identified_states=["the_pay_fog"],
        severity_tier="Emerging",
    ),
)

AUT_PF_02 = TestCase(
    test_id="AUT-PF-02",
    description=(
        "105-person technology company. Principal says pay decisions are made "
        "\'case by case\' and they\'ve never really had a framework. Employees compare "
        "salaries and the numbers don\'t always make sense to them. No formal "
        "complaints. Operating in Colorado — pay transparency required. No pay ranges "
        "published on job postings yet."
    ),
    profile_type="moderate",
    target_state="the_pay_fog",
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
        identified_states=["the_pay_fog", "pay_exposure"],
        severity_tier="Emerging",
    ),
)

AUT_PF_03 = TestCase(
    test_id="AUT-PF-03",
    description=(
        "55-person agency. Principal says they don\'t have a formal compensation "
        "structure but feels their pay is generally fair. No employee complaints. "
        "Not operating in a pay transparency jurisdiction. No specific situations cited."
    ),
    profile_type="weak",
    target_state="the_pay_fog",
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
        identified_states=["the_pay_fog", "pay_exposure"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority B2 profile collection ------------------------------------------

AUTHORITY_B2_PROFILES: list = [
    AUT_UN_01, AUT_UN_02, AUT_UN_03,
    AUT_LC_01, AUT_LC_02, AUT_LC_03,
    AUT_DP_01, AUT_DP_02, AUT_DP_03,
    AUT_PL_01, AUT_PL_02, AUT_PL_03,
    AUT_TP_01, AUT_TP_02, AUT_TP_03,
    AUT_DN_01, AUT_DN_02, AUT_DN_03,
    AUT_PE_01, AUT_PE_02, AUT_PE_03,
    AUT_PF_01, AUT_PF_02, AUT_PF_03,
]
