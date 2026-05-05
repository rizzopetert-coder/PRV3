#!/usr/bin/env python
"""
PRV3 — patch_attitude_b1_profiles.py
Creates engine/test_profiles_attitude_b1.py with 30 Attitude Phase 1 test profiles.

Source: PRV3_Phase1_Profiles_Attitude_B1 (Google Drive, Session 7)
States: The Untouchable · The Diversity Ceiling · The Burned Credibility
        Invisible Burnout · The Basement Standard · The Inside Track
        Narrative Lock · Groundhog Day · The Wrong Reward · The Broken Compass

Severity floor/cap notes:
  - sev_min=Entrenched: the_basement_standard, the_inside_track, narrative_lock,
                         groundhog_day, the_untouchable
  - sev_max=Entrenched: invisible_burnout
  - Entrenched only (locked): the_broken_compass

Pass-criterion overrides (weak profiles with co-signals):
  ATT-UT-03, ATT-BS-03, ATT-IT-03, ATT-NL-03, ATT-GD-03,
  ATT-WR-03, ATT-BCP-03 → pass_criterion="top_3"

Cross-dimension co-signals in this batch:
  - ATT-BC-02: the_burned_credibility + dueling_narratives (Attitude + Authority)
  - ATT-IB-02: invisible_burnout + the_overloaded_manager (Attitude + Aptitude)
  - ATT-IT-02/03: the_inside_track + the_arbitrary_standard (Attitude + Alliance)
  - ATT-GD-03: groundhog_day + the_lost_map (Attitude + Authority)
  - ATT-WR-03: the_wrong_reward + invisible_burnout (Attitude + Attitude)

Usage:
  python tools/patch_attitude_b1_profiles.py --dry-run
  python tools/patch_attitude_b1_profiles.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "test_profiles_attitude_b1.py"

CONTENT = '''\
"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Attitude Dimension — Batch 1: 30 profiles across 10 states.

Source: PRV3_Phase1_Profiles_Attitude_B1 (Google Drive, Session 7)
States: The Untouchable · The Diversity Ceiling · The Burned Credibility
        Invisible Burnout · The Basement Standard · The Inside Track
        Narrative Lock · Groundhog Day · The Wrong Reward · The Broken Compass

answers: empty at this stage — to be populated when engine is exercised end-to-end.
intake: representative values derived from profile descriptions.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Attitude: The Untouchable ------------------------------------------------

ATT_UT_01 = TestCase(
    test_id="ATT-UT-01",
    description=(
        "210-person financial services firm. A senior VP — one of the top revenue "
        "producers — has been the subject of four formal HR complaints in three years: "
        "two harassment, one retaliation, one hostile work environment. All four were "
        "investigated and closed without disciplinary action. The VP\\'s team has 40% "
        "annual turnover against a company average of 12%. Three members of the "
        "leadership team have privately told the CEO the VP is \\'untouchable.\\' The "
        "CEO describes the situation as \\'complicated because of his book of business.\\'"
    ),
    profile_type="high_confidence",
    target_state="the_untouchable",
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
        identified_states=["the_untouchable"],
        severity_tier="Endemic",
    ),
)

ATT_UT_02 = TestCase(
    test_id="ATT-UT-02",
    description=(
        "130-person technology company. A senior engineering manager has received "
        "negative feedback from two direct reports in annual surveys for two years "
        "running — described as \\'dismissive\\' and \\'plays favorites.\\' One direct "
        "report transferred internally citing \\'working environment.\\' No formal "
        "complaint has been filed. The principal is aware and describes the manager "
        "as \\'difficult but brilliant.\\'"
    ),
    profile_type="moderate",
    target_state="the_untouchable",
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
        identified_states=["the_untouchable"],
        severity_tier="Entrenched",
    ),
)

ATT_UT_03 = TestCase(
    test_id="ATT-UT-03",
    description=(
        "70-person professional services firm. The principal mentions one senior "
        "leader who \\'rubs people the wrong way\\' — no complaints filed, no "
        "departures cited, no feedback data. General perception."
    ),
    profile_type="weak",
    target_state="the_untouchable",
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
        identified_states=["the_untouchable", "the_basement_standard"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Attitude: The Diversity Ceiling ------------------------------------------

ATT_DC_01 = TestCase(
    test_id="ATT-DC-01",
    description=(
        "240-person financial services firm. Entry-level hiring is 48% women and "
        "32% people of color. Director-level and above: 18% women, 9% people of "
        "color. Mid-level diverse talent departure rate is 2.4x the majority "
        "departure rate. The organization has run three DEI initiatives in four "
        "years. No structured sponsorship program exists. An external audit "
        "commissioned last year found no documented advancement criteria for "
        "Director-level roles."
    ),
    profile_type="high_confidence",
    target_state="the_diversity_ceiling",
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
        identified_states=["the_diversity_ceiling"],
        severity_tier="Endemic",
    ),
)

ATT_DC_02 = TestCase(
    test_id="ATT-DC-02",
    description=(
        "120-person technology company. The principal notes their leadership team "
        "is \\'not very diverse\\' and they\\'ve been trying to hire more diversely "
        "at the senior level. No internal advancement data reviewed. Mid-level "
        "diverse talent departure rate not tracked. One DEI initiative (unconscious "
        "bias training) conducted last year."
    ),
    profile_type="moderate",
    target_state="the_diversity_ceiling",
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
        identified_states=["the_diversity_ceiling"],
        severity_tier="Emerging",
    ),
)

ATT_DC_03 = TestCase(
    test_id="ATT-DC-03",
    description=(
        "75-person professional services firm. The principal mentions they "
        "\\'could be more diverse\\' at the leadership level. No data. No "
        "initiatives. No specific departures cited."
    ),
    profile_type="weak",
    target_state="the_diversity_ceiling",
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
        output_type="single_state",
        identified_states=["the_diversity_ceiling"],
        severity_tier="Emerging",
    ),
)


# -- Attitude: The Burned Credibility -----------------------------------------

ATT_BC_01 = TestCase(
    test_id="ATT-BC-01",
    description=(
        "190-person manufacturing company. In four years: a lean manufacturing "
        "initiative failed at implementation, a culture survey produced a report "
        "that was never shared with employees, a new performance management system "
        "was launched and quietly abandoned after six months, and an engagement "
        "initiative was announced with fanfare and defunded after three months. "
        "The workforce uses the phrase \\'flavor of the month\\' to describe "
        "leadership initiatives. A new operational improvement initiative is being "
        "planned. When leadership mentioned it in a team meeting, three managers "
        "responded with visible skepticism. No one asked questions."
    ),
    profile_type="high_confidence",
    target_state="the_burned_credibility",
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
        identified_states=["the_burned_credibility"],
        severity_tier="Endemic",
    ),
)

ATT_BC_02 = TestCase(
    test_id="ATT-BC-02",
    description=(
        "110-person technology company. A major reorganization 18 months ago was "
        "poorly communicated — employees learned about it informally before the "
        "announcement. A DEI commitment made publicly last year has not been "
        "followed up on. Two managers have told HR that \\'people are skeptical "
        "of anything leadership says.\\' No new major initiative announced."
    ),
    profile_type="moderate",
    target_state="the_burned_credibility",
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
        output_type="multi_state",
        identified_states=["the_burned_credibility", "dueling_narratives"],
        severity_tier="Entrenched",
    ),
)

ATT_BC_03 = TestCase(
    test_id="ATT-BC-03",
    description=(
        "65-person agency. The principal mentions a strategic planning process "
        "last year that \\'didn\\'t really go anywhere.\\' Employees know about "
        "it. No pattern of multiple failures. No named workforce response."
    ),
    profile_type="weak",
    target_state="the_burned_credibility",
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
        output_type="single_state",
        identified_states=["the_burned_credibility"],
        severity_tier="Emerging",
    ),
)


# -- Attitude: Invisible Burnout -----------------------------------------------

ATT_IB_01 = TestCase(
    test_id="ATT-IB-01",
    description=(
        "160-person professional services firm. Over 18 months: three high "
        "performers have resigned with no job lined up, citing \\'needing a break.\\' "
        "Two others have taken extended medical leave. Engagement scores have "
        "declined from 72% to 58%. The leadership team works routinely past 9pm "
        "and models this behavior visibly. No workload analysis has been conducted. "
        "The principal describes the culture as \\'high-performance, "
        "high-expectation\\' and expresses pride in it."
    ),
    profile_type="high_confidence",
    target_state="invisible_burnout",
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
        output_type="single_state",
        identified_states=["invisible_burnout"],
        severity_tier="Entrenched",
    ),
)

ATT_IB_02 = TestCase(
    test_id="ATT-IB-02",
    description=(
        "95-person technology company. One high performer resigned last quarter "
        "citing \\'burnout.\\' Two others have mentioned feeling overwhelmed in "
        "1:1s. The principal is aware and is \\'keeping an eye on it.\\' No formal "
        "workload analysis. Leadership team is also stretched — two VPs are "
        "carrying roles that have been unfilled for four months."
    ),
    profile_type="moderate",
    target_state="invisible_burnout",
    intake={
        "headcount":          "25-99",
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["invisible_burnout", "the_overloaded_manager"],
        severity_tier="Emerging",
    ),
)

ATT_IB_03 = TestCase(
    test_id="ATT-IB-03",
    description=(
        "60-person agency. The principal mentions the team has been \\'running "
        "hot\\' for the past few months — a big project push. No departures. "
        "No formal feedback. Expects it to normalize."
    ),
    profile_type="weak",
    target_state="invisible_burnout",
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
        output_type="single_state",
        identified_states=["invisible_burnout"],
        severity_tier="Emerging",
    ),
)


# -- Attitude: The Basement Standard ------------------------------------------

ATT_BS_01 = TestCase(
    test_id="ATT-BS-01",
    description=(
        "220-person manufacturing company. Three managers — all with documented "
        "performance issues in their files — have been in their roles for more "
        "than three years without remediation or separation. Peers and direct "
        "reports describe them as \\'passengers.\\' High performers on those "
        "managers\\' teams report frustration and are leaving at 2x the company "
        "average. HR describes the situation as \\'difficult to move on without "
        "airtight documentation.\\' The principal describes it as \\'a legacy issue.\\'"
    ),
    profile_type="high_confidence",
    target_state="the_basement_standard",
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
        identified_states=["the_basement_standard"],
        severity_tier="Endemic",
    ),
)

ATT_BS_02 = TestCase(
    test_id="ATT-BS-02",
    description=(
        "115-person technology company. One manager has been underperforming for "
        "18 months — peers know it, the manager\\'s skip-level knows it. A PIP "
        "was started six months ago and quietly dropped when the manager pushed "
        "back. Two direct reports of this manager have transferred internally. "
        "The principal is \\'trying to figure out the right approach.\\'"
    ),
    profile_type="moderate",
    target_state="the_basement_standard",
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
        identified_states=["the_basement_standard", "the_untouchable"],
        severity_tier="Entrenched",
    ),
)

ATT_BS_03 = TestCase(
    test_id="ATT-BS-03",
    description=(
        "70-person professional services firm. The principal mentions that "
        "\\'performance management isn\\'t our strong suit\\' — no specific "
        "underperformers named, no departures cited, no PIP history."
    ),
    profile_type="weak",
    target_state="the_basement_standard",
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
        identified_states=["the_basement_standard", "the_untouchable"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Attitude: The Inside Track -----------------------------------------------

ATT_IT_01 = TestCase(
    test_id="ATT-IT-01",
    description=(
        "185-person financial services firm. Over three years, seven of the eight "
        "Director-level promotions went to individuals with prior working "
        "relationships with the CEO — three former colleagues from a prior firm, "
        "two who attended the same MBA program, two who are socially connected to "
        "the CEO outside of work. Promotion criteria are not documented. An "
        "employee survey found 68% of respondents believe advancement is based on "
        "\\'who you know.\\' Two high performers without CEO proximity have resigned "
        "in the past year, both citing advancement as the reason."
    ),
    profile_type="high_confidence",
    target_state="the_inside_track",
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
        identified_states=["the_inside_track"],
        severity_tier="Endemic",
    ),
)

ATT_IT_02 = TestCase(
    test_id="ATT-IT-02",
    description=(
        "110-person technology company. Two recent promotions went to candidates "
        "who are socially connected to the VP of Engineering outside of work. Two "
        "other candidates who were passed over had stronger performance records. "
        "The VP says \\'cultural fit\\' was the deciding factor. No promotion "
        "criteria documented."
    ),
    profile_type="moderate",
    target_state="the_inside_track",
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
        identified_states=["the_inside_track", "the_arbitrary_standard"],
        severity_tier="Entrenched",
    ),
)

ATT_IT_03 = TestCase(
    test_id="ATT-IT-03",
    description=(
        "65-person agency. The principal mentions that \\'some people seem to "
        "have an easier path to advancement than others\\' — no specific network "
        "identified, no data."
    ),
    profile_type="weak",
    target_state="the_inside_track",
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
        identified_states=["the_inside_track", "the_arbitrary_standard"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Attitude: Narrative Lock --------------------------------------------------

ATT_NL_01 = TestCase(
    test_id="ATT-NL-01",
    description=(
        "200-person financial services firm. Three external diagnostic engagements "
        "in five years have produced consistent findings: siloed decision-making, "
        "inadequate cross-functional communication, and advancement criteria that "
        "lack transparency. Each time, leadership reviewed the findings and "
        "concluded the methodology was flawed, the consultant \\'didn\\'t understand "
        "the business,\\' or the data reflected an unrepresentative sample. No "
        "finding has been incorporated into any operational change. A fourth "
        "engagement is being planned."
    ),
    profile_type="high_confidence",
    target_state="narrative_lock",
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
        identified_states=["narrative_lock"],
        severity_tier="Endemic",
    ),
)

ATT_NL_02 = TestCase(
    test_id="ATT-NL-02",
    description=(
        "120-person technology company. An engagement survey 18 months ago "
        "produced low scores on trust in leadership and communication "
        "transparency. Leadership reviewed the results and concluded the questions "
        "were \\'poorly worded\\' and the results were \\'not representative of how "
        "people really feel.\\' No follow-up survey. One of the survey "
        "administrators has since left. A new survey is being discussed."
    ),
    profile_type="moderate",
    target_state="narrative_lock",
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
        identified_states=["narrative_lock", "the_burned_credibility"],
        severity_tier="Entrenched",
    ),
)

ATT_NL_03 = TestCase(
    test_id="ATT-NL-03",
    description=(
        "70-person professional services firm. The principal mentions they did a "
        "culture survey two years ago and \\'weren\\'t sure what to make of the "
        "results.\\' No action taken. No dismissal articulated — just uncertainty."
    ),
    profile_type="weak",
    target_state="narrative_lock",
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
        identified_states=["narrative_lock", "the_burned_credibility"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Attitude: Groundhog Day --------------------------------------------------

ATT_GD_01 = TestCase(
    test_id="ATT-GD-01",
    description=(
        "230-person manufacturing company. The same category of problem — "
        "cross-functional communication failure — has been addressed four times "
        "in six years with different interventions: a new project management tool, "
        "a weekly cross-functional sync, a reorganization, and a shared OKR "
        "system. Each produced improvement for two to three months, then reverted. "
        "The current leadership team is planning a fifth intervention. When asked "
        "whether previous interventions were analyzed, the COO says they \\'look "
        "at things differently now.\\'"
    ),
    profile_type="high_confidence",
    target_state="groundhog_day",
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
        identified_states=["groundhog_day"],
        severity_tier="Endemic",
    ),
)

ATT_GD_02 = TestCase(
    test_id="ATT-GD-02",
    description=(
        "115-person technology company. Turnover in the engineering team has been "
        "addressed twice — once with a compensation adjustment, once with a culture "
        "initiative. Turnover improved briefly both times and returned to prior "
        "levels. The VP of Engineering is now considering a third approach — better "
        "career pathing. No analysis of why the first two interventions did not hold."
    ),
    profile_type="moderate",
    target_state="groundhog_day",
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
        identified_states=["groundhog_day", "the_burned_credibility"],
        severity_tier="Entrenched",
    ),
)

ATT_GD_03 = TestCase(
    test_id="ATT-GD-03",
    description=(
        "70-person agency. The principal mentions that \\'we keep trying to fix "
        "communication\\' and it \\'never really sticks.\\' No specific intervention "
        "history cited, no recurrence count."
    ),
    profile_type="weak",
    target_state="groundhog_day",
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
        identified_states=["groundhog_day", "the_lost_map"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Attitude: The Wrong Reward ------------------------------------------------

ATT_WR_01 = TestCase(
    test_id="ATT-WR-01",
    description=(
        "200-person financial services firm. The incentive structure rewards "
        "individual deal volume; the company strategy requires cross-functional "
        "deal teaming to serve enterprise clients. Sales representatives have "
        "learned that teaming on deals reduces individual credit without "
        "proportional benefit. As a result, the three largest enterprise "
        "opportunities in the past year have been managed as individual deals, "
        "leading to two client losses and one significant service failure. Sales "
        "leadership can articulate the gap between incentive structure and "
        "strategy clearly. No change to the incentive structure has been initiated."
    ),
    profile_type="high_confidence",
    target_state="the_wrong_reward",
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
        identified_states=["the_wrong_reward"],
        severity_tier="Entrenched",
    ),
)

ATT_WR_02 = TestCase(
    test_id="ATT-WR-02",
    description=(
        "110-person technology company. The engineering team is rewarded for "
        "shipping features. Product quality metrics — bugs in production, technical "
        "debt accumulation — are not in any engineer\\'s performance evaluation. "
        "Engineers produce features at a high rate; technical debt has accumulated "
        "significantly over two years. The CTO acknowledges the problem and says "
        "\\'we need to fix how we measure success.\\'"
    ),
    profile_type="moderate",
    target_state="the_wrong_reward",
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
        identified_states=["the_wrong_reward"],
        severity_tier="Emerging",
    ),
)

ATT_WR_03 = TestCase(
    test_id="ATT-WR-03",
    description=(
        "65-person agency. The principal says the team is \\'incentivized to say "
        "yes to everything\\' and it\\'s creating capacity problems. No formal "
        "incentive structure analysis. No specific financial consequence named."
    ),
    profile_type="weak",
    target_state="the_wrong_reward",
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
        identified_states=["the_wrong_reward", "invisible_burnout"],
        severity_tier="Emerging",
        pass_criterion="top_3",
    ),
)


# -- Attitude: The Broken Compass ---------------------------------------------

ATT_BCP_01 = TestCase(
    test_id="ATT-BCP-01",
    description=(
        "175-person professional services firm. An external consulting engagement "
        "14 months ago produced a 47-page organizational diagnosis — specific "
        "findings on role clarity, accountability architecture, and cross-functional "
        "coordination. The principal has read the report. The leadership team has "
        "discussed it in three meetings. A summary was shared with the board. "
        "Eleven months later: none of the report\\'s recommendations have been "
        "implemented. When asked why, the principal says \\'we know what needs to "
        "be done, we just haven\\'t been able to prioritize it.\\'"
    ),
    profile_type="high_confidence",
    target_state="the_broken_compass",
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
        output_type="single_state",
        identified_states=["the_broken_compass"],
        severity_tier="Entrenched",
    ),
)

ATT_BCP_02 = TestCase(
    test_id="ATT-BCP-02",
    description=(
        "100-person technology company. A culture survey 8 months ago identified "
        "psychological safety concerns in two teams. The principal reviewed the "
        "results and agrees with the findings. A proposed intervention plan was "
        "presented by HR. The plan has been on the agenda for three leadership "
        "team meetings and has not been approved. The principal says \\'we want "
        "to get this right.\\'"
    ),
    profile_type="moderate",
    target_state="the_broken_compass",
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
        identified_states=["the_broken_compass"],
        severity_tier="Entrenched",
    ),
)

ATT_BCP_03 = TestCase(
    test_id="ATT-BCP-03",
    description=(
        "60-person agency. The principal has a clear sense of what\\'s wrong — "
        "\\'communication and accountability, honestly\\' — and says they \\'need "
        "to do something about it.\\' No diagnostic engagement. No plan. No timeline."
    ),
    profile_type="weak",
    target_state="the_broken_compass",
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
        identified_states=["the_broken_compass", "groundhog_day"],
        severity_tier="Entrenched",
        pass_criterion="top_3",
    ),
)


# -- Attitude B1 profile collection -------------------------------------------

ATTITUDE_B1_PROFILES: list = [
    ATT_UT_01,  ATT_UT_02,  ATT_UT_03,
    ATT_DC_01,  ATT_DC_02,  ATT_DC_03,
    ATT_BC_01,  ATT_BC_02,  ATT_BC_03,
    ATT_IB_01,  ATT_IB_02,  ATT_IB_03,
    ATT_BS_01,  ATT_BS_02,  ATT_BS_03,
    ATT_IT_01,  ATT_IT_02,  ATT_IT_03,
    ATT_NL_01,  ATT_NL_02,  ATT_NL_03,
    ATT_GD_01,  ATT_GD_02,  ATT_GD_03,
    ATT_WR_01,  ATT_WR_02,  ATT_WR_03,
    ATT_BCP_01, ATT_BCP_02, ATT_BCP_03,
]
'''


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create engine/test_profiles_attitude_b1.py"
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
