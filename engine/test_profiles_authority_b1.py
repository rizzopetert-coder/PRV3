"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Authority Dimension — Batch 1: 18 profiles across 6 states.

Source: PRV3_Phase1_Profiles_Authority_B1 (Google Drive, Session 8)
States: The Founders Grip · The Exposed · HR Capture · The Unsolved Problem
        The Tolerated Violation · Heard & Ignored

Session locked design decisions:
  - AUT-HC-01: principal_role = "HR leader" (HR is the presenting principal)
  - AUT-HI-03: cross-dimension co-signal (heard_and_ignored + the_paper_tiger) — intentional
  - AUT-UP-03: single_state at Entrenched at weak signal — prior claim specificity (no override)
  - AUT-HC-03, AUT-TV-03, AUT-HI-03: pass_criterion = "top_3" (doc specifies top-2)

answers: empty at this stage — to be populated when engine is exercised end-to-end.
intake: representative values derived from profile descriptions.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Authority: The Founders Grip ---------------------------------------------

AUT_FG_01 = TestCase(
    test_id="AUT-FG-01",
    description=(
        "95-person SaaS company, founder-led, 11 years old. Founder holds CEO title "
        "and approves all strategic hires, vendor contracts over $10k, and customer "
        "contracts over $50k. Two VPs with strong track records at larger companies "
        "left in the past three years citing inability to operate. Current leadership "
        "team escalates decisions nominally within their authority. Founder describes "
        "the situation as \'I just need to stay involved.\'"
    ),
    profile_type="high_confidence",
    target_state="the_founders_grip",
    intake={
        "headcount":          45,
        "industry":           "Technology",
        "org_type":           "Founder-led",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_founders_grip"],
        severity_tier="Entrenched",
    ),
)

AUT_FG_02 = TestCase(
    test_id="AUT-FG-02",
    description=(
        "55-person professional services firm, founder-led, 7 years old. Founder "
        "beginning to delegate — some client relationships and team decisions now "
        "made without founder involvement. New COO joined 8 months ago, finding their "
        "footing. Principal notes the founder \'still wants to know everything\' but "
        "is trying to step back. One senior hire left in the past year; reason unclear."
    ),
    profile_type="moderate",
    target_state="the_founders_grip",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Founder-led",
        "jurisdictions":      [],
        "significant_events": ["leadership_departure"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_founders_grip"],
        severity_tier="Entrenched",
    ),
)

AUT_FG_03 = TestCase(
    test_id="AUT-FG-03",
    description=(
        "35-person technology company, founder-led, 4 years old. Principal describes "
        "the founder as \'very hands-on\' — team checks in with them frequently. No "
        "senior leader departures. No specific delegation failures named. Company is "
        "growing and the principal describes the dynamic positively."
    ),
    profile_type="weak",
    target_state="the_founders_grip",
    intake={
        "headcount":          45,
        "industry":           "Technology",
        "org_type":           "Founder-led",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_founders_grip"],
        severity_tier="Emerging",
    ),
)


# -- Authority: The Exposed ---------------------------------------------------

AUT_EX_01 = TestCase(
    test_id="AUT-EX-01",
    description=(
        "110-person distribution company. HR Director of 6 years resigned 3 months "
        "ago — no replacement hired; CEO handling HR questions directly. Past 8 weeks: "
        "one FMLA leave approved informally with no paperwork, a manager asking about "
        "terminating a team member, and a workplace injury — all without qualified HR "
        "guidance. No outside counsel or fractional HR engaged. CEO says \'we\'re "
        "managing fine.\'"
    ),
    profile_type="high_confidence",
    target_state="the_exposed",
    intake={
        "headcount":          152,
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["leadership_departure"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_exposed"],
        severity_tier="Entrenched",
    ),
)

AUT_EX_02 = TestCase(
    test_id="AUT-EX-02",
    description=(
        "70-person professional services firm. Part-time HR coordinator left 6 weeks "
        "ago. Firm engaged a fractional HR consultant for 8 hours per week — new and "
        "untested. No active compliance situations have arisen yet. Principal is aware "
        "of the gap and actively searching for a replacement."
    ),
    profile_type="moderate",
    target_state="the_exposed",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["leadership_departure"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_exposed"],
        severity_tier="Emerging",
    ),
)

AUT_EX_03 = TestCase(
    test_id="AUT-EX-03",
    description=(
        "40-person agency. Principal mentions their HR person \'wears a lot of hats\' "
        "and HR is not a dedicated function. No recent incidents. No compliance "
        "situations named. The arrangement has been in place for two years and nothing "
        "has gone wrong."
    ),
    profile_type="weak",
    target_state="the_exposed",
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
        identified_states=["the_exposed"],
        severity_tier="Emerging",
    ),
)


# -- Authority: HR Capture ----------------------------------------------------

AUT_HC_01 = TestCase(
    test_id="AUT-HC-01",
    description=(
        "200-person manufacturing company. HR reports directly to the COO, who is the "
        "subject of all three most recent employee complaints — two harassment-related, "
        "one retaliation. HR investigations found all three unsubstantiated; no "
        "disciplinary action taken. Two of three complainants have since left. The "
        "third filed an EEOC charge last month. HR described by the principal as "
        "\'a real business partner.\'"
    ),
    profile_type="high_confidence",
    target_state="hr_capture",
    intake={
        "headcount":          152,
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["hr_capture"],
        severity_tier="Entrenched",
    ),
)

AUT_HC_02 = TestCase(
    test_id="AUT-HC-02",
    description=(
        "120-person healthcare services organization. HR reports to the CFO. One "
        "compensation fairness grievance filed against the CFO in the past 18 months — "
        "HR investigated and found no violation. Employee still employed and has not "
        "escalated externally. Principal expresses mild concern about whether HR is "
        "\'truly independent\' but has not acted on it."
    ),
    profile_type="moderate",
    target_state="hr_capture",
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
        identified_states=["hr_capture", "the_exposed"],
        severity_tier="Emerging",
    ),
)

AUT_HC_03 = TestCase(
    test_id="AUT-HC-03",
    description=(
        "80-person professional services firm. HR reports to the CEO. CEO has not been "
        "the subject of any complaints. Principal mentions it is sometimes hard to know "
        "if HR is \'giving independent advice or just telling us what we want to hear.\' "
        "No specific complaint history cited."
    ),
    profile_type="weak",
    target_state="hr_capture",
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
        identified_states=["hr_capture", "the_exposed"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority: The Unsolved Problem ------------------------------------------

AUT_UP_01 = TestCase(
    test_id="AUT-UP-01",
    description=(
        "175-person financial services firm. Three years ago a harassment claim was "
        "filed against a senior manager, investigated, and settled confidentially — "
        "manager retained without root cause analysis. Eighteen months later a second "
        "claim was filed by a different employee against the same manager. Organization "
        "is now managing the second claim. Principal attributes the situation to "
        "\'bad luck — two bad actors on the same team.\'"
    ),
    profile_type="high_confidence",
    target_state="the_unsolved_problem",
    intake={
        "headcount":          152,
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_unsolved_problem"],
        severity_tier="Entrenched",
    ),
)

AUT_UP_02 = TestCase(
    test_id="AUT-UP-02",
    description=(
        "90-person technology company. Wage and hour complaint settled two years ago — "
        "settlement required a pay practices audit that was never conducted. Principal "
        "says they \'took care of it\' and is surprised to be asked. A class action "
        "inquiry letter from a plaintiffs\' firm arrived last month."
    ),
    profile_type="moderate",
    target_state="the_unsolved_problem",
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
        output_type="single_state",
        identified_states=["the_unsolved_problem"],
        severity_tier="Entrenched",
    ),
)

AUT_UP_03 = TestCase(
    test_id="AUT-UP-03",
    description=(
        "60-person professional services firm. A discrimination complaint was filed "
        "and settled 18 months ago. Principal believes the issue was resolved. No "
        "second claim, no named recurrence. Principal mentions it somewhat reluctantly "
        "when asked about prior employment situations."
    ),
    profile_type="weak",
    target_state="the_unsolved_problem",
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
        identified_states=["the_unsolved_problem"],
        severity_tier="Entrenched",
    ),
)


# -- Authority: The Tolerated Violation ---------------------------------------

AUT_TV_01 = TestCase(
    test_id="AUT-TV-01",
    description=(
        "300-person logistics company. Drivers classified as independent contractors. "
        "Outside counsel flagged 14 months ago that the classification likely fails "
        "the ABC test in the primary operating state. Operations leadership reviewed "
        "and decided reclassification cost and disruption outweigh the legal risk. "
        "Practice continues. A class action inquiry has arrived from a plaintiffs\' firm."
    ),
    profile_type="high_confidence",
    target_state="the_tolerated_violation",
    intake={
        "headcount":          328,
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_tolerated_violation"],
        severity_tier="Entrenched",
    ),
)

AUT_TV_02 = TestCase(
    test_id="AUT-TV-02",
    description=(
        "140-person healthcare services company. Salaried employees in certain roles "
        "not receiving overtime pay — a manager raised the question internally 8 months "
        "ago. HR reviewed and concluded the exemption was valid; outside counsel not "
        "consulted. Principal considers the matter resolved. Two employees in the "
        "affected roles have since left without filing complaints."
    ),
    profile_type="moderate",
    target_state="the_tolerated_violation",
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
        identified_states=["the_tolerated_violation", "the_policy_lag"],
        severity_tier="Entrenched",
    ),
)

AUT_TV_03 = TestCase(
    test_id="AUT-TV-03",
    description=(
        "75-person professional services firm. Principal mentions practices that are "
        "\'probably a bit gray\' in terms of employment law — specifically around how "
        "certain roles are classified. Not sure if it is a problem. No counsel review. "
        "No complaints. No external attention."
    ),
    profile_type="weak",
    target_state="the_tolerated_violation",
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
        identified_states=["the_tolerated_violation", "the_policy_lag"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority: Heard & Ignored -----------------------------------------------

AUT_HI_01 = TestCase(
    test_id="AUT-HI-01",
    description=(
        "220-person financial services firm. Employee filed harassment complaint "
        "against a VP 14 months ago. HR acknowledged receipt, conducted a two-week "
        "investigation, communicated that \'appropriate action was taken\' — but the "
        "employee was not told the outcome and the VP remains in role unchanged. "
        "Employee filed an EEOC charge 6 months ago; charge currently under "
        "EEOC investigation."
    ),
    profile_type="high_confidence",
    target_state="heard_and_ignored",
    intake={
        "headcount":          152,
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["heard_and_ignored"],
        severity_tier="Endemic",
    ),
)

AUT_HI_02 = TestCase(
    test_id="AUT-HI-02",
    description=(
        "130-person technology company. Two employees filed informal complaints about "
        "a team lead\'s management style over the past year — described as demeaning "
        "and dismissive. HR spoke with the team lead both times; no formal "
        "investigation opened, no documentation produced. Complainants told "
        "\'we spoke with them.\' Team lead still in role. No external escalation."
    ),
    profile_type="moderate",
    target_state="heard_and_ignored",
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
        identified_states=["heard_and_ignored", "the_tolerated_violation"],
        severity_tier="Entrenched",
    ),
)

AUT_HI_03 = TestCase(
    test_id="AUT-HI-03",
    description=(
        "85-person professional services firm. One employee mentioned to their manager "
        "6 months ago feeling uncomfortable with how a senior leader spoke to them in "
        "meetings. Manager noted it informally and told HR. HR made a note. No formal "
        "complaint filed, no investigation opened, no follow-up occurred. Employee has "
        "not raised it again."
    ),
    profile_type="weak",
    target_state="heard_and_ignored",
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
        identified_states=["heard_and_ignored", "the_paper_tiger"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Authority B1 profile collection ------------------------------------------

AUTHORITY_B1_PROFILES: list = [
    AUT_FG_01, AUT_FG_02, AUT_FG_03,
    AUT_EX_01, AUT_EX_02, AUT_EX_03,
    AUT_HC_01, AUT_HC_02, AUT_HC_03,
    AUT_UP_01, AUT_UP_02, AUT_UP_03,
    AUT_TV_01, AUT_TV_02, AUT_TV_03,
    AUT_HI_01, AUT_HI_02, AUT_HI_03,
]
