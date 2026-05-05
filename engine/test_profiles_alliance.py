"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Alliance Dimension — 18 profiles across 6 states.

Source: PRV3_Phase1_Profiles_Alliance.md (Google Drive, Session 8)
States: The Fracture · The Second Close · Silosolation · The Suppression Filter
        The Arbitrary Standard · Decision Blindness

Session locked design decisions:
  - Silosolation and Suppression Filter: sev_min=Entrenched; even weak profiles are Entrenched
  - The Second Close: single_state at all signal levels (M&A event self-identifies)
  - ALL-FR-03, ALL-SI-03, ALL-SF-03, ALL-AS-03, ALL-DB-03: pass_criterion = "top_3"

answers: empty at this stage — to be populated when engine is exercised end-to-end.
intake: representative values derived from profile descriptions.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Alliance: The Fracture ---------------------------------------------------

ALL_FR_01 = TestCase(
    test_id="ALL-FR-01",
    description=(
        "195-person financial services firm. The CEO and CFO — co-founders — have "
        "been in open conflict for eight months. Conflict surfaced publicly when the "
        "CFO countermanded a staffing decision the CEO announced in an all-hands. Both "
        "have direct reports routing work and information through their respective "
        "principal. Two senior leaders resigned in the past three months citing "
        "leadership instability. Board is aware and has not intervened. The workforce "
        "uses the phrase \'which side are you on\' informally."
    ),
    profile_type="high_confidence",
    target_state="the_fracture",
    intake={
        "headcount":          "100-249",
        "industry":           "Financial Services",
        "org_type":           "Founder-led",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_fracture"],
        severity_tier="Endemic",
    ),
)

ALL_FR_02 = TestCase(
    test_id="ALL-FR-02",
    description=(
        "120-person technology company. The CTO and VP of Product have been in "
        "persistent disagreement about roadmap priorities for six months. Conflict is "
        "known to their direct reports but has not broken the organizational surface — "
        "no public countermanding, no workforce factionalism. One product manager "
        "transferred teams citing \'working environment.\' CEO is aware and "
        "\'managing it.\'"
    ),
    profile_type="moderate",
    target_state="the_fracture",
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
        output_type="single_state",
        identified_states=["the_fracture"],
        severity_tier="Entrenched",
    ),
)

ALL_FR_03 = TestCase(
    test_id="ALL-FR-03",
    description=(
        "70-person professional services firm. The principal mentions two senior "
        "leaders \'don\'t really see eye to eye\' — no specific conflict cited, no "
        "departures, no workforce awareness named. Principal describes it as "
        "\'just a personality thing.\'"
    ),
    profile_type="weak",
    target_state="the_fracture",
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
        identified_states=["the_fracture", "decision_paralysis"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Alliance: The Second Close -----------------------------------------------

ALL_SC_01 = TestCase(
    test_id="ALL-SC-01",
    description=(
        "210-person professional services firm that acquired a 45-person boutique "
        "10 months ago. Three of the five senior people from the acquired firm have "
        "resigned. Client retention from acquired book at 65% against an 85% target. "
        "People integration plan produced post-close but not implemented — integration "
        "managed as a systems and process project. Acquiring firm\'s leadership "
        "describes the situation as \'integration always takes time.\'"
    ),
    profile_type="high_confidence",
    target_state="the_second_close",
    intake={
        "headcount":          "100-249",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["acquisition_or_merger"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_second_close"],
        severity_tier="Entrenched",
    ),
)

ALL_SC_02 = TestCase(
    test_id="ALL-SC-02",
    description=(
        "130-person technology company, 5 months post-acquisition of a 20-person team. "
        "Two acquired engineers have resigned. Integration has been choppy — acquired "
        "team is on different tools and processes. A people integration plan is in "
        "progress. Acquired team engagement scores below company average but declining "
        "slowly. Principal is cautiously optimistic."
    ),
    profile_type="moderate",
    target_state="the_second_close",
    intake={
        "headcount":          "100-249",
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["acquisition_or_merger"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_second_close"],
        severity_tier="Emerging",
    ),
)

ALL_SC_03 = TestCase(
    test_id="ALL-SC-03",
    description=(
        "90-person professional services firm, 2 months post-acquisition of a "
        "15-person team. No departures yet. Integration in early stages. Principal "
        "mentions it has been \'a bit bumpy\' getting people on the same systems. "
        "No people integration plan yet."
    ),
    profile_type="weak",
    target_state="the_second_close",
    intake={
        "headcount":          "25-99",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["acquisition_or_merger"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_second_close"],
        severity_tier="Emerging",
    ),
)


# -- Alliance: Silosolation ---------------------------------------------------

ALL_SI_01 = TestCase(
    test_id="ALL-SI-01",
    description=(
        "250-person manufacturing company. Cross-functional initiatives have "
        "consistently stalled at the dependency point between Operations and Finance "
        "for two years. Three enterprise projects required CEO escalation to proceed. "
        "Both department heads have strong performance records within their functions. "
        "Incentive structure rewards functional metrics exclusively — no cross-functional "
        "performance component exists. CEO describes it as \'two great departments that "
        "just don\'t play well together.\'"
    ),
    profile_type="high_confidence",
    target_state="silosolation",
    intake={
        "headcount":          "250-499",
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["silosolation"],
        severity_tier="Endemic",
    ),
)

ALL_SI_02 = TestCase(
    test_id="ALL-SI-02",
    description=(
        "130-person technology company. Sales and Engineering functions have recurring "
        "friction around feature prioritization. Feature requests from Sales "
        "consistently get deprioritized in Engineering sprints; Sales escalates to CEO "
        "monthly. Both leaders express frustration with each other. No formal "
        "cross-functional prioritization process exists."
    ),
    profile_type="moderate",
    target_state="silosolation",
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
        identified_states=["silosolation", "the_fracture"],
        severity_tier="Entrenched",
    ),
)

ALL_SI_03 = TestCase(
    test_id="ALL-SI-03",
    description=(
        "75-person professional services firm. Principal mentions that different "
        "departments \'don\'t always communicate well\' — no specific initiatives "
        "cited, no pattern data. General impression."
    ),
    profile_type="weak",
    target_state="silosolation",
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
        identified_states=["silosolation", "the_lost_map"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Alliance: The Suppression Filter -----------------------------------------

ALL_SF_01 = TestCase(
    test_id="ALL-SF-01",
    description=(
        "280-person financial services firm. A post-acquisition culture assessment "
        "by an outside firm found that middle managers systematically filter negative "
        "information before it reaches senior leadership. Interviews with 40 middle "
        "managers confirmed a consistent pattern: prior executive reactions to bad news "
        "trained managers not to surface problems. Three managers independently "
        "described using \'managing up\' to mean presenting only what leadership "
        "wanted to hear. Senior leadership was uniformly surprised by the findings. "
        "Pattern in place for at least three years."
    ),
    profile_type="high_confidence",
    target_state="the_suppression_filter",
    intake={
        "headcount":          "250-499",
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["acquisition_or_merger"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_suppression_filter"],
        severity_tier="Endemic",
    ),
)

ALL_SF_02 = TestCase(
    test_id="ALL-SF-02",
    description=(
        "140-person technology company. CEO mentions they often feel \'out of the "
        "loop\' on problems that turn out to have been known internally for weeks. "
        "Two recent product failures had warning signals that didn\'t reach leadership "
        "until they became crises. Direct reports consistently report \'everything is "
        "fine\' in 1:1s. No skip-level mechanism exists. CEO attributes it to "
        "\'people wanting to solve problems before escalating.\'"
    ),
    profile_type="moderate",
    target_state="the_suppression_filter",
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
        identified_states=["the_suppression_filter", "leadership_deafness"],
        severity_tier="Entrenched",
    ),
)

ALL_SF_03 = TestCase(
    test_id="ALL-SF-03",
    description=(
        "85-person professional services firm. The principal says they \'sometimes "
        "feel like I\'m not getting the full picture\' — no specific examples, "
        "no confirmed filtering pattern. General sense."
    ),
    profile_type="weak",
    target_state="the_suppression_filter",
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
        identified_states=["the_suppression_filter", "leadership_deafness"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Alliance: The Arbitrary Standard -----------------------------------------

ALL_AS_01 = TestCase(
    test_id="ALL-AS-01",
    description=(
        "185-person professional services firm. An internal review triggered by an "
        "EEOC inquiry found that promotion decisions over three years were made without "
        "documented criteria. In five specific cases employees with stronger performance "
        "records were passed over in favor of employees with weaker records. Three of "
        "the five passed-over employees are members of protected classes. HR cannot "
        "explain the differential outcomes. Decision-makers cannot produce "
        "documentation. EEOC inquiry is ongoing."
    ),
    profile_type="high_confidence",
    target_state="the_arbitrary_standard",
    intake={
        "headcount":          "100-249",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_arbitrary_standard"],
        severity_tier="Entrenched",
    ),
)

ALL_AS_02 = TestCase(
    test_id="ALL-AS-02",
    description=(
        "110-person technology company. Two employees in the same role raised concerns "
        "about inconsistent treatment — one was placed on a PIP for behavior the other "
        "engaged in without consequence. HR investigated informally and found "
        "\'differences in context.\' No formal documentation of the criteria "
        "differences exists. No external escalation. Both employees are aware of "
        "each other\'s situations."
    ),
    profile_type="moderate",
    target_state="the_arbitrary_standard",
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
        identified_states=["the_arbitrary_standard", "the_inside_track"],
        severity_tier="Emerging",
    ),
)

ALL_AS_03 = TestCase(
    test_id="ALL-AS-03",
    description=(
        "65-person agency. The principal mentions that \'some people feel like the "
        "rules apply differently to different people.\' No specific examples, "
        "no investigation, no departures cited."
    ),
    profile_type="weak",
    target_state="the_arbitrary_standard",
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
        identified_states=["the_arbitrary_standard", "the_inside_track"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Alliance: Decision Blindness ---------------------------------------------

ALL_DB_01 = TestCase(
    test_id="ALL-DB-01",
    description=(
        "230-person technology company. An engineer was terminated six months ago "
        "following a PIP. In the three months after the engineer raised performance "
        "concerns with their manager, four decisions were made independently by "
        "different people: project reassigned, excluded from a key meeting, team access "
        "reduced, remote work accommodation denied. No individual was aware of the "
        "others\' actions. Engineer filed a retaliation charge with the EEOC. Outside "
        "counsel identified the decision sequence as a pattern claim."
    ),
    profile_type="high_confidence",
    target_state="decision_blindness",
    intake={
        "headcount":          "100-249",
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["decision_blindness"],
        severity_tier="Entrenched",
    ),
)

ALL_DB_02 = TestCase(
    test_id="ALL-DB-02",
    description=(
        "125-person professional services firm. An employee raised a wage and hour "
        "concern with HR four months ago. Since then: their schedule was changed, they "
        "were passed over for a project they\'d requested, and their manager gave "
        "them a lower performance rating than the prior quarter. No retaliation claim "
        "filed. HR is not aware the employee connects these decisions. Outside counsel "
        "has not been consulted."
    ),
    profile_type="moderate",
    target_state="decision_blindness",
    intake={
        "headcount":          "100-249",
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["decision_blindness", "heard_and_ignored"],
        severity_tier="Emerging",
    ),
)

ALL_DB_03 = TestCase(
    test_id="ALL-DB-03",
    description=(
        "70-person agency. The principal mentions an employee raised a concern about "
        "pay equity two months ago and \'things have been a little awkward since "
        "then.\' No specific adverse decisions named. No external escalation."
    ),
    profile_type="weak",
    target_state="decision_blindness",
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
        identified_states=["decision_blindness", "heard_and_ignored"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Alliance profile collection ----------------------------------------------

ALLIANCE_PROFILES: list = [
    ALL_FR_01, ALL_FR_02, ALL_FR_03,
    ALL_SC_01, ALL_SC_02, ALL_SC_03,
    ALL_SI_01, ALL_SI_02, ALL_SI_03,
    ALL_SF_01, ALL_SF_02, ALL_SF_03,
    ALL_AS_01, ALL_AS_02, ALL_AS_03,
    ALL_DB_01, ALL_DB_02, ALL_DB_03,
]
