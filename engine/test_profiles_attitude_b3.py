"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Attitude Dimension — Batch 3: 9 profiles across 3 C-Culture cluster states.

Source: PRV3_Phase1_Profiles_Attitude_B3 (Google Drive, Session 7)
  Doc ID: 1IaFtOab94CQyGYn6Ys2BAZRyEP_YPHqNO50JVFNPRII
States: Culture Drift · Identity Erosion · The Culture That Wasn't

Fixed-severity note: the_culture_that_wasnt is Emerging only (locked).
ATT-TCWW-01 is high_confidence but outputs Emerging — severity correctness
for this state is severity_tier == "Emerging" regardless of signal strength.

answers: empty at this stage — to be populated when engine is exercised end-to-end.
intake: representative values derived from profile descriptions.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Attitude: Culture Drift --------------------------------------------------

ATT_CD_01 = TestCase(
    test_id="ATT-CD-01",
    description=(
        "280-person technology company that grew from 80 to 280 people over three "
        "years. The founding value set — explicit, behavioral, referenced in weekly "
        "all-hands — included \'radical transparency\' and \'disagree and commit.\' "
        "Three years later: a culture audit (conducted post-distinguisher) found that "
        "74% of employees believe leadership does not operate by these values, while "
        "91% believe the values are still officially in force. Three VP-level leaders "
        "hired in the growth phase model meeting consensus rather than productive "
        "disagreement. The CEO has not named the gap publicly. Glassdoor reviews "
        "cluster around \'the culture changed after the funding round.\' The "
        "C-Culture distinguisher has confirmed: the drift is ongoing, not a recruiting "
        "misrepresentation, and the departures are not concentrated among foundational "
        "employees."
    ),
    profile_type="high_confidence",
    target_state="culture_drift",
    intake={
        "headcount":          328,
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["rapid_growth"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["culture_drift"],
        severity_tier="Entrenched",
    ),
)

ATT_CD_02 = TestCase(
    test_id="ATT-CD-02",
    description=(
        "140-person professional services firm. The principal describes the culture "
        "as \'not what it used to be\' — the firm has grown and the closeness of "
        "the early days is gone. Some tenured employees have left in the past year "
        "citing culture. Some newer employees have also left early citing culture. "
        "The principal isn\'t sure if this is a drift problem or a recruiting "
        "problem. The C-Culture distinguisher has not fired."
    ),
    profile_type="moderate",
    target_state="culture_drift",
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
        output_type="multi_state",
        identified_states=["culture_drift", "identity_erosion", "the_culture_that_wasnt"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)

ATT_CD_03 = TestCase(
    test_id="ATT-CD-03",
    description=(
        "75-person agency. The principal mentions the culture has \'evolved\' as "
        "the firm has grown — says it with some ambivalence but no specific concern "
        "named, no departures cited."
    ),
    profile_type="weak",
    target_state="culture_drift",
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
        identified_states=["culture_drift", "identity_erosion"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Attitude: Identity Erosion -----------------------------------------------

ATT_IE_01 = TestCase(
    test_id="ATT-IE-01",
    description=(
        "220-person technology company that shifted strategic direction 18 months "
        "ago — moving from a mission-driven open-source model to a commercial "
        "enterprise model. The strategic shift was deliberate and financially sound. "
        "In the 18 months since: 14 tenured employees (average tenure 4.2 years) "
        "have resigned. Exit interviews reveal consistent identity-based language: "
        "\'this isn\'t the company I joined,\' \'the mission changed and I\'m "
        "not the right fit anymore,\' \'I joined because of what we stood for.\' "
        "Newer employees (under 18 months) are not leaving at elevated rates. "
        "Glassdoor reviews from departing tenured employees reference the strategic "
        "shift specifically. The C-Culture distinguisher has confirmed: departures "
        "are concentrated among tenured employees; the change is strategically "
        "intentional."
    ),
    profile_type="high_confidence",
    target_state="identity_erosion",
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
        identified_states=["identity_erosion"],
        severity_tier="Entrenched",
    ),
)

ATT_IE_02 = TestCase(
    test_id="ATT-IE-02",
    description=(
        "110-person professional services firm. The firm was acquired 2 years ago "
        "and has been integrating into the parent company. Several long-tenured "
        "employees have left citing culture — they describe feeling like \'the old "
        "firm is gone.\' Newer employees and employees from the acquiring company "
        "are generally satisfied. The principal isn\'t sure if this is a normal "
        "integration consequence or a problem that needs to be addressed."
    ),
    profile_type="moderate",
    target_state="identity_erosion",
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
        output_type="multi_state",
        identified_states=["identity_erosion", "the_second_close"],
        severity_tier="Emerging",
    ),
)

ATT_IE_03 = TestCase(
    test_id="ATT-IE-03",
    description=(
        "70-person agency. A few longtime employees have left in the past year. "
        "The principal mentions the firm has grown and \'things are different.\' "
        "No identity language cited explicitly. No clear pattern."
    ),
    profile_type="weak",
    target_state="identity_erosion",
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
        identified_states=["identity_erosion", "culture_drift"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Attitude: The Culture That Wasn't ----------------------------------------

ATT_TCWW_01 = TestCase(
    test_id="ATT-TCWW-01",
    description=(
        "185-person technology company. First-year voluntary departure rate is 34% "
        "against an industry benchmark of 14%. Exit interviews from 12 first-year "
        "departures in the past 18 months reveal a consistent pattern: departing "
        "employees describe the recruiting process as having emphasized a "
        "collaborative, transparent, and mission-driven culture. Onboarding "
        "experience was described as \'transactional,\' \'politically charged,\' "
        "and \'nothing like what I was told.\' Three Glassdoor reviews posted by "
        "departing employees in the past 6 months specifically reference the gap "
        "between recruiting narrative and reality. The C-Culture distinguisher has "
        "confirmed: departures are concentrated in the first year; tenured employees "
        "are not leaving at elevated rates; the issue is recruiting misrepresentation, "
        "not culture change."
    ),
    profile_type="high_confidence",
    target_state="the_culture_that_wasnt",
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
        identified_states=["the_culture_that_wasnt"],
        severity_tier="Emerging",
    ),
)

ATT_TCWW_02 = TestCase(
    test_id="ATT-TCWW-02",
    description=(
        "100-person professional services firm. Several employees who joined in "
        "the past year have left citing \'not what I expected.\' The principal "
        "describes their recruiting pitch as emphasizing flexibility, autonomy, "
        "and work-life balance. The current reality is demanding and structured. "
        "The principal wasn\'t aware of the gap until two recent exit interviews "
        "surfaced it. The C-Culture distinguisher has not fired."
    ),
    profile_type="moderate",
    target_state="the_culture_that_wasnt",
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
        output_type="multi_state",
        identified_states=["the_culture_that_wasnt", "culture_drift"],
        severity_tier="Emerging",
    ),
)

ATT_TCWW_03 = TestCase(
    test_id="ATT-TCWW-03",
    description=(
        "60-person agency. The principal mentions one recent hire left after three "
        "months saying it \'wasn\'t the right fit.\' The principal isn\'t sure "
        "if this is a recruiting issue or just a bad hire."
    ),
    profile_type="weak",
    target_state="the_culture_that_wasnt",
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
        identified_states=["the_culture_that_wasnt", "culture_drift"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Attitude B3 profile collection -------------------------------------------

ATTITUDE_B3_PROFILES: list = [
    ATT_CD_01,   ATT_CD_02,   ATT_CD_03,
    ATT_IE_01,   ATT_IE_02,   ATT_IE_03,
    ATT_TCWW_01, ATT_TCWW_02, ATT_TCWW_03,
]
