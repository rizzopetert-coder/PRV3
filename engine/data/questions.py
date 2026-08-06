"""
PRV3 Scoring Engine — Section I.2
Question Library Schema and Registry

Populated Session 9 from PRV3_Question_Library_Draft (Google Drive).
Source: Session 2 conversation history, confirmed and locked.

Core sequence: Q01-Q34. Q03 and Q27 have conditional A/B versions.
Q28 is a live conditional splice off Q06 (fires when A or B is selected),
  not a fixed position -- see web/lib/session-store.ts's
  PHASE_1_QUESTION_SEQUENCE. Q31 is PARKED (excluded from the live
  sequence entirely) -- its authored guard is unreachable under Q28's
  single-condition gate; see Q31's own inline comment below.
Severity follow-ons: SEVER-01 through SEVER-13.
  Note: spec originally specified 12 follow-ons; Q32a adds a 13th distinct follow-on.
  Q28a and Q31a share SEVER-11 (same content, different adaptive parent
  question) -- with Q31 parked, SEVER-11 can in practice only fire from
  Q28 today.

dimensional_contributions: seeded from Signal Map tier assignments (Session 11).
HIGH->0.60, MEDIUM->0.40, LOW/Cluster->0.25 baseline. Asset fields at 0.25.
Phase 1 calibration will refine these values against test suite results.

Spec reference: Section I.2
"""

from dataclasses import dataclass, field
from typing import Optional


# -- Answer option -------------------------------------------------------------

@dataclass
class AnswerOption:
    """
    One selectable option within a question.

    dimensional_contributions: seeded per Signal Map tier (Session 11).
    HIGH->0.60, MEDIUM->0.40, LOW/Cluster->0.25. Asset fields at 0.25.

    Spec reference: Section I.2 answer_vectors
    """
    option_id:   str
    option_text: str

    dimensional_contributions: dict = field(default_factory=lambda: {
        "aptitude_liability":   0.0,
        "aptitude_asset":       0.0,
        "authority_liability":  0.0,
        "authority_asset":      0.0,
        "alliance_liability":   0.0,
        "alliance_asset":       0.0,
        "attitude_liability":   0.0,
        "attitude_asset":       0.0,
    })

    axis_targets:          list          = field(default_factory=list)
    severity_trigger:      bool          = False
    severity_follow_on_id: Optional[str] = None

    # Populated only on SEVER-01..13 follow-on options (never on core Q01-Q34
    # options, whose own severity_trigger only signals that a follow-on
    # should be presented next -- the SeverityInput values themselves come
    # from the follow-on's own answer). Single-key dict mapping one of the
    # 5 real SeverityInput fields (duration_band, population_band,
    # prior_failed_resolution, financial_indicators, named_condition) to
    # this option's value for that field. See _severity_input_tags below.
    severity_input_mapping: Optional[dict] = None

    # Short third-person observational statement describing what choosing
    # this option indicates about the organization (e.g. "Respondent
    # described authority and responsibility boundaries as a recurring
    # source of friction inside the organization."). Feeds
    # output_synthesis.py's signal_map_context -- never shown to the
    # respondent, never the option_text verbatim. None until authored;
    # see _observation_text_tags below. Content-authoring pass is a
    # separate, later phase -- this field defaults to None for all options
    # as of this build.
    observation_text: Optional[str] = None


# -- Question definition -------------------------------------------------------

@dataclass
class QuestionDefinition:
    """
    Complete definition of one diagnostic question.

    question_id formats:
      Q01-Q34          Core sequence
      Q03A / Q03B      Conditional versions of Q03 (Field 5 event vs. none)
      Q03A-D-FOLLOW    Inline follow-on for Q03A answer D
      Q27A / Q27B      Conditional versions of Q27 (acquisition vs. no acquisition)
      SEVER-01 to -13  Conditional severity follow-ons
      DIST-CM-##       C-Manager distinguisher questions (future)
      DIST-CC-##       C-Culture distinguisher questions (future)
      DIST-CS-##       C-Silence distinguisher questions (future)
      DIST-CI-##       C-InfoFlow distinguisher questions (future)

    Spec reference: Section I.2
    """
    question_id:        str
    question_text:      str
    format:             str
    sequence_position:  Optional[int]
    checkpoint_segment: str

    answer_options:  list = field(default_factory=list)
    state_targets:   list = field(default_factory=list)
    severity_trigger: bool = False


# -- Question data -------------------------------------------------------------
# Each entry:
#   (question_id, question_text, format, sequence_position, checkpoint_segment,
#    [(option_id, option_text, severity_trigger, follow_on_id), ...],
#    [state_targets],
#    question_level_severity_trigger)

_QDATA = [
    (
        "Q01",
        "When consequential decisions need to be made in your organization"
        " — about people, resources, or direction — how does that typically go?",
        "forced_choice", 1, "early",
        [
            ("A", "Clearly. The right people make decisions and they stick.", False, None),
            ("B", "There's usually clarity on smaller decisions but bigger ones tend to get complicated.", False, None),
            ("C", "Decisions get made but they're often revisited — it can be hard to know what's actually final.", False, None),
            ("D", "It's slow and effortful. Getting to a decision takes more than it should.", False, None),
            ("E", "It's unclear who has authority for what. Decisions happen but the accountability is hard to pin down.", False, None),
        ],
        ["decision_paralysis", "the_lost_map", "the_founders_grip", "sequential_decision_blindness"],
        False,
    ),
    (
        "Q02",
        "How would you describe your HR function right now?",
        "forced_choice", 2, "early",
        [
            ("A", "Strong and independent — we have dedicated HR leadership that operates with real authority.", False, None),
            ("B", "Adequate — HR handles what it needs to but it's not a strategic function.", False, None),
            ("C", "Thin — HR is a part-time role or shared responsibility.", False, None),
            ("D", "Absent — we don't have a dedicated HR function right now.", True, "SEVER-15"),
            ("E", "We have HR but I sometimes wonder whether it's truly independent.", False, None),
        ],
        ["the_exposed", "hr_capture", "planning_authority_gap"],
        False,
    ),
    (
        "Q03A",
        "You mentioned some significant changes in the past 18 months."
        " Which of these best describes where things stand now?",
        "forced_choice", 3, "early",
        [
            ("A", "Most of it is behind us — things have largely stabilized.", False, None),
            ("B", "We're still working through it — the effects are ongoing.", False, None),
            ("C", "We're in the middle of it — we haven't reached the other side yet.", False, None),
            ("D", "It depends on which one you mean — some are behind us, some aren't.", True, "Q03A-D-FOLLOW"),
        ],
        ["the_unsolved_problem", "the_burned_credibility", "transition_paralysis",
         "the_second_close", "the_uninitiated", "built_to_fail"],
        True,
    ),
    (
        "Q03A-D-FOLLOW",
        "Which of these is having the biggest impact on your organization right now?",
        "forced_choice", None, "conditional",
        [
            ("A", "Acquisition or merger", False, None),
            ("B", "Restructuring or layoff", False, None),
            ("C", "Rapid growth", False, None),
            ("D", "Leadership transition", False, None),
            ("E", "External legal matter", False, None),
            ("F", "Something else", False, None),
        ],
        ["the_second_close", "identity_erosion", "transition_paralysis", "the_fracture",
         "built_to_fail", "the_founders_grip", "silosolation",
         "leadership_continuity_risk", "the_uninitiated", "the_unsolved_problem"],
        False,
    ),
    (
        "Q03B",
        "What's the primary thing on your mind about your organization right now?",
        "forced_choice", 3, "early",
        [
            ("A", "Something specific is happening that I need to understand better.", False, None),
            ("B", "There's a pattern I've noticed that I want to diagnose.", False, None),
            ("C", "I want to get ahead of something before it becomes a problem.", False, None),
            ("D", "I'm not sure — I have a general sense that something isn't right.", False, None),
        ],
        [],
        False,
    ),
    (
        "Q04",
        "When people in your organization have concerns — about how they're being treated,"
        " about something they've witnessed — what happens?",
        "forced_choice", 4, "early",
        [
            ("A", "They raise them. We have a process and people use it.", False, None),
            ("B", "Some people raise concerns, others don't. It depends on the person and the situation.", False, None),
            ("C", "Honestly, I'm not sure. I don't have great visibility into how concerns are handled.", False, None),
            ("D", "Not much happens. People have learned that raising concerns doesn't produce results.", False, None),
        ],
        ["hr_capture", "heard_and_ignored", "what_nobody_says",
         "the_suppression_filter", "leadership_deafness"],
        False,
    ),
    (
        "Q05",
        "When someone in your organization isn't performing — really isn't performing"
        " — what happens?",
        "forced_choice", 5, "early",
        [
            ("A", "It gets addressed. There's a process and managers use it.", False, None),
            ("B", "It gets addressed eventually, but it takes longer than it should.", False, None),
            ("C", "It depends on who the person is. Some people are held accountable and some aren't.", False, None),
            ("D", "Not much. Underperformance tends to get tolerated.", False, None),
        ],
        ["the_basement_standard", "the_untouchable", "the_inside_track",
         "the_arbitrary_standard", "the_wrong_reward", "the_paper_tiger"],
        False,
    ),
    (
        "Q06",
        "Has your organization dealt with any of the following in the past three years?"
        " Select all that apply.",
        "weighted_multi_select", 6, "early",
        [
            ("A", "An external legal claim, EEOC charge, or regulatory inquiry.", False, None),
            ("B", "A monetary settlement involving an employment matter.", False, None),
            ("C", "A situation your legal counsel flagged as a liability before it became a claim.", False, None),
            ("D", "A known practice that you're aware isn't fully compliant but hasn't been addressed.", False, None),
            ("E", "None of the above.", False, None),
        ],
        ["heard_and_ignored", "the_unsolved_problem", "decision_blindness",
         "the_tolerated_violation", "the_policy_lag", "the_paper_tiger",
         "disparate_impact_architecture"],
        False,
    ),
    (
        "Q07",
        "When you lose people you didn't want to lose, what's the pattern?",
        "forced_choice", 7, "early",
        [
            ("A", "It's spread across the organization — no clear concentration by team, manager, or role.", False, None),
            ("B", "It's concentrated under specific managers or in specific teams.", False, None),
            ("C", "It's concentrated in specific roles — the same positions keep turning over.", False, None),
            ("D", "It's concentrated at a specific level — we keep losing people at a certain point in their career here.", False, None),
        ],
        ["the_fracture", "silosolation"],
        False,
    ),
    (
        "Q08",
        "How does important information travel in your organization"
        " — things leadership needs to know?",
        "forced_choice", 8, "early",
        [
            ("A", "It reaches us reliably. We feel like we have an accurate picture of what's happening.", False, None),
            ("B", "We get information but I sometimes wonder if we're getting the full picture.", False, None),
            ("C", "By the time problems reach us they're already crises — we're frequently surprised.", False, None),
            ("D", "I think there's a gap. What I hear informally is different from what comes through formal channels.", False, None),
        ],
        ["leadership_deafness", "the_suppression_filter"],
        False,
    ),
    (
        "Q09",
        "How would you describe the working relationship among your senior leaders right now?",
        "forced_choice", 9, "early",
        [
            ("A", "Strong. We disagree but it's productive and we move forward together.", False, None),
            ("B", "Functional but not cohesive — people do their jobs but don't really operate as a team.", False, None),
            ("C", "There's tension that's mostly contained at the senior level.", False, None),
            ("D", "There's a dynamic that's broken the surface — the organization below us is aware of it.", False, None),
            ("E", "There's a significant unresolved conflict I'm not sure how to address.", True, "SEVER-14"),
        ],
        ["the_fracture", "silosolation"],
        False,
    ),
    (
        "Q10",
        "How well do your organization's formal processes reflect how things actually work?",
        "forced_choice", 10, "early",
        [
            ("A", "Pretty well — our processes are current and people actually use them.", False, None),
            ("B", "They're mostly there but some are out of date or inconsistently followed.", False, None),
            ("C", "There's a gap — we have processes on paper that don't reflect how we actually operate.", False, None),
            ("D", "We're light on formal process — managers run on judgment more than documented systems.", False, None),
        ],
        ["the_paper_tiger", "the_policy_lag", "paper_shield"],
        False,
    ),
    (
        "Q11",
        "How well do your organization's actions reflect what it says it values"
        " — in who gets ahead, what gets tolerated, and how decisions get made?",
        "forced_choice", 11, "early",
        [
            ("A", "Consistently. What we say we value shows up in how we actually operate.", False, None),
            ("B", "Mostly — but there are visible exceptions that people have noticed.", False, None),
            ("C", "There's a gap. Relationships and visibility drive outcomes more than stated values do.", False, None),
            ("D", "What gets rewarded and what we say we value are two different things — and people know it.", False, None),
            ("E", "Our values are stated but they don't really govern anything.", False, None),
        ],
        ["culture_drift", "the_wrong_reward", "the_inside_track",
         "the_arbitrary_standard", "the_basement_standard", "the_broken_compass",
         "cultural_overtime", "motivational_architecture_failure"],
        False,
    ),
    (
        "Q12",
        "How would you describe the quality of management across your organization?",
        "forced_choice", 12, "mid",
        [
            ("A", "Strong — most managers develop their people and produce results.", False, None),
            ("B", "Uneven — we have some strong managers and some who are struggling.", False, None),
            ("C", "Thin — managers are capable individually but stretched beyond what they can handle.", False, None),
            ("D", "There are specific managers who are a real problem — not the whole layer, but concentrated issues.", False, None),
            ("E", "I don't have great visibility into how managers are actually performing.", False, None),
        ],
        ["the_unformed_leader", "the_overloaded_manager", "the_dormant_talent",
         "the_untouchable", "leadership_deafness", "the_suppression_filter",
         "the_paper_tiger"],
        False,
    ),
    (
        "Q13",
        "How well does your organization understand where it's going"
        " — and believe it will get there?",
        "forced_choice", 13, "mid",
        [
            ("A", "Leadership knows where we're going but I'm not sure the organization does.", False, None),
            ("B", "We've been here before. People have heard the plan and are waiting to see if this time is different.", False, None),
            ("C", "The direction isn't as clear as it should be — people are operating on different assumptions.", False, None),
            ("D", "The direction is clear but there's skepticism about whether we'll follow through.", False, None),
            ("E", "People know the direction and trust that leadership will execute on it.", False, None),
        ],
        ["the_lost_map", "the_burned_credibility", "decision_paralysis", "the_broken_compass"],
        False,
    ),
    (
        "Q14",
        "How would you describe your organization's relationship with compensation right now?",
        "forced_choice", 14, "mid",
        [
            ("A", "We're confident we're competitive and internally consistent.", False, None),
            ("B", "We're competitive externally but I'm not sure we're consistent internally.", False, None),
            ("C", "We're consistent internally but I'm not sure we're competitive externally.", False, None),
            ("D", "We have concerns about both — consistency and competitiveness are issues.", False, None),
            ("E", "Honestly, we haven't looked closely enough to know.", False, None),
        ],
        ["pay_exposure", "the_pay_fog", "compression_crisis"],
        False,
    ),
    (
        "Q15",
        "How would you describe advancement opportunity in your organization?",
        "forced_choice", 15, "mid",
        [
            ("A", "Clear and merit-based — people know what it takes to advance and it happens.", False, None),
            ("B", "Present but inconsistent — advancement happens but the criteria aren't always transparent.", False, None),
            ("C", "Concentrated — advancement tends to favor certain people or certain teams.", False, None),
            ("D", "Limited — the organization doesn't have much advancement to offer.", False, None),
            ("E", "We lose people who are looking to grow before we can develop them.", False, None),
        ],
        ["the_diversity_ceiling", "the_inside_track", "the_arbitrary_standard", "the_dormant_talent"],
        False,
    ),
    (
        "Q16",
        "How would you describe the relationship between diversity and advancement"
        " in your organization?",
        "forced_choice", 16, "mid",
        [
            ("A", "Consistent — diverse talent advances at the same rate as everyone else.", False, None),
            ("B", "We're diverse at entry levels but the composition changes as you move up.", True, "SEVER-01"),
            ("C", "We've invested in diversity but I'm not sure it's translating into advancement.", True, "SEVER-01"),
            ("D", "We're losing diverse talent before they reach senior levels and I'm not sure why.", True, "SEVER-01"),
            ("E", "This isn't something we've looked at closely enough to answer with confidence.", False, None),
        ],
        ["the_diversity_ceiling", "the_pay_fog"],
        True,
    ),
    (
        "Q17",
        "When your organization tries to change something — a new initiative, a cultural shift,"
        " a structural change — what typically happens?",
        "forced_choice", 17, "mid",
        [
            ("A", "We execute well. Changes stick and people invest in them.", False, None),
            ("B", "We start strong but struggle to sustain — initiatives fade before they take hold.", False, None),
            ("C", "People participate but don't really invest — there's a wait-and-see quality to how change lands.", False, None),
            ("D", "We keep addressing the same problems with different approaches and getting the same result.", False, None),
            ("E", "We know what needs to change and we talk about it — but we don't actually move.", False, None),
        ],
        ["the_burned_credibility", "groundhog_day", "the_broken_compass", "narrative_lock"],
        False,
    ),
    (
        "Q18",
        "When it comes to workplace safety and security, which of the following"
        " best describes your organization?",
        "forced_choice", 18, "mid",
        [
            ("A", "Both are taken seriously — people report concerns and the organization responds visibly.", False, None),
            ("B", "The policies are there but I'm not confident people actually follow them or report when something is wrong.", False, None),
            ("C", "We've had incidents that I think could have been prevented if people had spoken up earlier.", False, None),
            ("D", "Security is a known gap — people work around protocols rather than following them.", False, None),
            ("E", "Safety and security aren't significant concerns for our type of work.", False, None),
        ],
        ["the_unreported_hazard", "the_unlocked_door", "what_nobody_says", "the_suppression_filter"],
        False,
    ),
    (
        "Q19",
        "How consistent is what your organization says publicly — about its culture, values,"
        " and commitments — with what's actually happening internally?",
        "forced_choice", 19, "mid",
        [
            ("A", "Consistent. What we say publicly is what we live internally.", False, None),
            ("B", "Mostly consistent but there are some gaps we're aware of.", False, None),
            ("C", "There's a meaningful gap — our external narrative is ahead of our internal reality.", False, None),
            ("D", "I don't think we've really looked at whether they align.", False, None),
        ],
        ["dueling_narratives", "the_pay_fog", "the_policy_lag"],
        False,
    ),
    (
        "Q20",
        "How clear are people in your organization about what they're responsible for"
        " and who has authority over what?",
        "forced_choice", 20, "late",
        [
            ("A", "Clear. People know their mandates and decisions get made at the right level.", False, None),
            ("B", "Mostly clear but there are some areas of overlap or ambiguity.", False, None),
            ("C", "There are meaningful gaps — certain functions or roles don't have clear mandates.", True, "SEVER-02"),
            ("D", "It's a recurring source of friction — people regularly bump into authority or responsibility questions.", True, "SEVER-02"),
        ],
        ["built_to_fail", "the_undefined_role", "decision_paralysis"],
        True,
    ),
    (
        "Q21",
        "When consequential decisions need to move through your organization, what typically happens?",
        "forced_choice", 21, "late",
        [
            ("A", "They move. The right people engage and decisions complete.", False, None),
            ("B", "There's friction — decisions require more back-and-forth than they should.", False, None),
            ("C", "Things escalate more than they should — decisions that shouldn't need senior involvement end up there.", True, "SEVER-03"),
            ("D", "Things get revisited — decisions get made and then reopened without much new information.", True, "SEVER-03"),
            ("E", "It's unclear who has the authority to decide — decisions happen but nobody can say with confidence who was supposed to make them.", True, "SEVER-03"),
        ],
        ["decision_paralysis", "the_lost_map"],
        True,
    ),
    (
        "Q22",
        "How current and complete are your organization's people policies"
        " — employee handbook, HR documentation, compliance obligations?",
        "forced_choice", 22, "late",
        [
            ("A", "Current — we review them regularly and they reflect how we actually operate.", False, None),
            ("B", "Mostly there but some haven't been looked at in a while.", False, None),
            ("C", "We haven't reviewed them recently — I'm not confident they reflect current law or practice.", True, "SEVER-04"),
            ("D", "We had a situation arise that our policies didn't cover or didn't cover correctly.", True, "SEVER-04"),
            ("E", "We use AI tools in hiring, performance, or people decisions and I'm not sure we've assessed the implications.", False, None),
        ],
        ["the_policy_lag", "the_unexamined_algorithm"],
        True,
    ),
    (
        "Q23",
        "How dependent is your organization on specific individuals"
        " — people whose departure would create a crisis?",
        "forced_choice", 23, "late",
        [
            ("A", "We've built real depth — no single departure would be unmanageable.", True, "SEVER-05"),
            ("B", "We're more dependent than we should be but we haven't felt it yet.", False, None),
            ("C", "We've felt it — a departure exposed how thin we were and recovery was harder than expected.", False, None),
            ("D", "We have people right now whose loss would be genuinely destabilizing.", True, "SEVER-05"),
        ],
        ["leadership_continuity_risk", "paper_shield"],
        True,
    ),
    (
        "Q24",
        "How would you describe the state of your highest performers right now?",
        "forced_choice", 24, "late",
        [
            ("A", "They're engaged and sustainable — I'm not worried about them.", False, None),
            ("B", "They're performing but I think some are carrying more than is healthy long term.", True, "SEVER-06"),
            ("C", "We've lost high performers recently in ways that surprised us — people who seemed fine until they weren't.", True, "SEVER-06"),
            ("D", "I know there are people who are running on empty and I'm not sure how to address it.", True, "SEVER-06"),
        ],
        ["invisible_burnout", "human_displacement_anxiety"],
        True,
    ),
    (
        "Q25",
        "How would you describe your organization's track record on developing people?",
        "forced_choice", 25, "late",
        [
            ("A", "Strong — we develop people intentionally and it shows in who we promote.", False, None),
            ("B", "We promote from within when we can but development is inconsistent.", False, None),
            ("C", "We tend to hire externally for senior roles — we haven't built the pipeline.", True, "SEVER-07"),
            ("D", "We've tried to develop people but the investment hasn't produced what we expected.", True, "SEVER-07"),
            ("E", "Honestly, developing people isn't something we've prioritized.", True, "SEVER-07"),
        ],
        ["the_dormant_talent", "leadership_continuity_risk", "the_unformed_leader"],
        True,
    ),
    (
        "Q26",
        "How well do different parts of your organization work together when they need to?",
        "forced_choice", 26, "late",
        [
            ("A", "Well — cross-functional work happens naturally and produces results.", False, None),
            ("B", "It works but requires more effort than it should — there's friction at the seams.", False, None),
            ("C", "It's a consistent problem — cross-functional initiatives stall predictably at the same points.", True, "SEVER-08"),
            ("D", "Functions operate independently — collaboration is the exception rather than the rule.", True, "SEVER-08"),
        ],
        ["silosolation", "the_fracture", "distributed_culture_fragmentation"],
        True,
    ),
    (
        "Q27A",
        "How would you describe where the integration stands right now?",
        "forced_choice", 27, "late",
        [
            ("A", "On track — the two organizations are coming together as planned.", False, None),
            ("B", "The systems and processes are integrating but the people and culture haven't caught up.", True, "SEVER-09"),
            ("C", "We're losing people from the acquired organization and it's affecting what we were trying to gain.", True, "SEVER-09"),
            ("D", "The integration is harder than we expected and I'm not sure we have the right plan to finish it.", True, "SEVER-09"),
        ],
        ["the_second_close"],
        True,
    ),
    (
        "Q27B",
        "How would you describe the current state of the organization's culture?",
        "forced_choice", 27, "late",
        [
            ("A", "Healthy — the stated culture and the lived culture are the same thing.", False, None),
            ("B", "Drifting — things are changing in ways that feel different from what we've been.", True, "SEVER-10"),
            ("C", "Split — different parts of the organization seem to have different cultures.", True, "SEVER-10"),
            ("D", "Unclear — I'm not sure what our culture actually is right now.", True, "SEVER-10"),
            ("E", "The culture people experience doesn't match what we describe in recruiting.", False, None),
        ],
        ["culture_drift", "identity_erosion", "the_culture_that_wasnt", "wellbeing_theater"],
        True,
    ),
    (
        "Q28",
        "You mentioned an earlier legal, compliance, or HR matter."
        " What changed as a result?",
        "forced_choice", 28, "late",
        [
            ("A", "A great deal changed — we made real structural or policy changes and I'm confident we addressed the root cause.", False, None),
            ("B", "Some things changed — process updates, policy revisions — but I'm not sure we got to the root of it.", False, None),
            ("C", "Not much changed. We resolved it and moved on.", True, "SEVER-11"),
            ("D", "The condition that produced it is still present.", True, "SEVER-11"),
        ],
        ["the_unsolved_problem"],
        True,
    ),
    (
        "Q29",
        "How would you describe the relationship between diversity and advancement"
        " in your organization?",
        "forced_choice", 29, "late",
        [
            ("A", "Consistent — diverse talent advances at the same rate as everyone else.", False, None),
            ("B", "We're diverse at entry levels but the composition changes as you move up.", True, "SEVER-12"),
            ("C", "We've invested in diversity but I'm not sure it's translating into advancement.", True, "SEVER-12"),
            ("D", "We're losing diverse talent before they reach senior levels and I'm not sure why.", True, "SEVER-12"),
            ("E", "This isn't something we've looked at closely enough to answer with confidence.", False, None),
        ],
        ["the_diversity_ceiling"],
        True,
    ),
    (
        "Q30",
        "How well do people in your organization know what's happening — decisions that have"
        " been made, where things are headed, what leadership is thinking?",
        "forced_choice", 30, "late",
        [
            ("A", "Well — we communicate deliberately and people are generally informed.", False, None),
            ("B", "There are gaps — some things reach people and some don't.", False, None),
            ("C", "It's inconsistent — communication varies a lot by team or manager.", False, None),
            ("D", "There's a real information gap — people often find out about things through informal channels first.", False, None),
        ],
        ["the_suppression_filter", "the_lost_map"],
        False,
    ),
    # PARKED (live-session investigation, this session): Q31 was authored
    # with a "fires only if Q06 A/B selected AND Q28 not yet asked"
    # condition, but that guard is mathematically unreachable under Q28's
    # own single-condition gate (Q28 fires deterministically whenever the
    # same Q06 answer is true, so "Q28 not yet asked" can never hold).
    # Excluded from web/lib/session-store.ts's PHASE_1_QUESTION_SEQUENCE
    # entirely -- not deleted, not spliced, not guarded, no firing logic
    # of any kind. Do not build firing logic for this question until a
    # real distinguishing condition is found or authored (not the current
    # self-contradicting one). See tools/_mob.txt Section 14 for the full
    # investigation.
    (
        "Q31",
        "Thinking back to the matter you mentioned earlier — what came out of the process?",
        "forced_choice", 31, "late",
        [
            ("A", "Isolated incidents — each situation was distinct and unrelated to the others.", False, None),
            ("B", "There's a theme — similar circumstances or similar people keep appearing.", False, None),
            ("C", "We resolved the situation but I'm not confident we addressed what caused it.", True, "SEVER-11"),
            ("D", "The condition that produced the matter is still present — we closed the claim, not the problem.", True, "SEVER-11"),
        ],
        ["the_unsolved_problem", "decision_blindness", "sequential_decision_blindness"],
        True,
    ),
    (
        "Q32",
        "As an organization, how well do you learn from experience"
        " — your own mistakes, prior initiatives, external feedback?",
        "forced_choice", 32, "late",
        [
            ("A", "Well — we examine what happened, draw conclusions, and actually change as a result.", False, None),
            ("B", "We reflect but don't always follow through — the learning doesn't always produce change.", False, None),
            ("C", "We've received consistent feedback — from surveys, consultants, or data — that we've struggled to act on.", True, "SEVER-13"),
            ("D", "We tend to move on from difficult experiences without examining them closely.", False, None),
        ],
        ["narrative_lock", "groundhog_day", "the_broken_compass"],
        True,
    ),
    (
        "Q33",
        "How current and well-maintained is your operational infrastructure"
        " — continuity plans, technology governance, organizational network documentation?",
        "forced_choice", 33, "late",
        [
            ("A", "Current — we have plans, we test them, and they reflect how we actually operate.", False, None),
            ("B", "Plans exist but I'm not sure they're current or would hold up under pressure.", False, None),
            ("C", "Thin — we have some documentation but it's not something we maintain actively.", False, None),
            ("D", "We don't have this infrastructure in place.", False, None),
        ],
        ["paper_shield", "invisible_influence_architecture", "leadership_continuity_risk"],
        False,
    ),
    (
        "Q34",
        "Looking at everything you've shared — if you had to name what kind of problem this is,"
        " what would you say?",
        "forced_choice", 34, "late",
        [
            ("A", "It's a people issue — specific individuals or relationships are at the center of it.", False, None),
            ("B", "It's a structural issue — the way the organization is set up is producing the problem.", False, None),
            ("C", "It's a cultural issue — it's about how people behave and what the organization accepts.", False, None),
            ("D", "A leadership issue — the will or capability to act on what we know isn't there.", False, None),
            ("E", "I'm not sure — the problem is real but I can't cleanly categorize it.", False, None),
        ],
        ["the_broken_compass", "narrative_lock", "the_burned_credibility"],
        False,
    ),
    # -- Severity follow-ons ---------------------------------------------------
    (
        "SEVER-01",
        "Is this something leadership has named and addressed, or is it more of a recognized"
        " pattern that hasn't been tackled directly?",
        "forced_choice", None, "conditional",
        [
            ("A", "Named and actively addressed — we have a specific plan and owners.", False, None),
            ("B", "Named but not yet addressed — we know it's there but haven't moved on it.", False, None),
            ("C", "Recognized informally but not officially named.", False, None),
            ("D", "I'm not sure leadership has seen it the same way I'm describing it.", False, None),
            ("E", "It's been recognized in some form for years without real traction.", False, None),
        ],
        ["the_diversity_ceiling"],
        False,
    ),
    (
        "SEVER-02",
        "Is this concentrated in specific roles or functions, or is it more broadly felt?",
        "forced_choice", None, "conditional",
        [
            ("A", "Concentrated — it's one or two specific roles or areas.", False, None),
            ("B", "It's a particular function or team.", False, None),
            ("C", "It's broader — multiple functions or levels are affected.", False, None),
            ("D", "It's pervasive — this is how the organization operates generally.", False, None),
            ("E", "It's been this way for as long as I can remember — not a recent shift.", False, None),
        ],
        ["built_to_fail", "the_undefined_role", "decision_paralysis"],
        False,
    ),
    (
        "SEVER-03",
        "How broadly is this felt in the organization?",
        "forced_choice", None, "conditional",
        [
            ("A", "It's isolated — specific decisions or specific functions.", False, None),
            ("B", "It's noticeable — people have named it as a frustration.", False, None),
            ("C", "It's pervasive — it affects how work gets done across the organization.", False, None),
            ("D", "It's become normal — people have built workarounds rather than expecting it to change.", False, None),
            ("E", "It's been this way for as long as I can remember.", False, None),
        ],
        ["decision_paralysis"],
        False,
    ),
    (
        "SEVER-04",
        "When did your policies last get a meaningful review?",
        "forced_choice", None, "conditional",
        [
            ("A", "Within the past twelve months.", False, None),
            ("B", "One to three years ago.", False, None),
            ("C", "More than three years ago.", False, None),
            ("D", "I'm not sure — I don't think there's been a formal review.", False, None),
        ],
        ["the_policy_lag"],
        False,
    ),
    (
        "SEVER-05",
        "How do you know?",
        "forced_choice", None, "conditional",
        [
            ("A", "We've tested it — a departure happened and we navigated it well.", False, None),
            ("B", "We have documented succession plans that we review and update regularly.", False, None),
            ("C", "We've thought about it and we're reasonably confident but haven't really tested it.", False, None),
            ("D", "Honestly, we assume it but I'm not sure we've verified it.", False, None),
            ("E", "We've been operating on assumption for a long time — this hasn't really been tested or reviewed in years.", False, None),
        ],
        ["paper_shield", "leadership_continuity_risk"],
        False,
    ),
    (
        "SEVER-06",
        "How long has this been the case?",
        "forced_choice", None, "conditional",
        [
            ("A", "It's recent — something changed in the past six months.", False, None),
            ("B", "It's been building for a year or more.", False, None),
            ("C", "It's been the operating mode for as long as I can remember.", False, None),
            ("D", "I'm not sure — I may not have been paying attention to it until now.", False, None),
        ],
        ["invisible_burnout"],
        False,
    ),
    (
        "SEVER-07",
        "What happens to strong performers who want to grow here?",
        "forced_choice", None, "conditional",
        [
            ("A", "We find ways to advance them — growth opportunities exist and people know it.", False, None),
            ("B", "We try but we don't always have the right opportunities at the right time.", False, None),
            ("C", "Some leave because they don't see a path — we lose people to growth opportunities elsewhere.", False, None),
            ("D", "We lose our best people regularly to organizations that offer what we can't.", False, None),
            ("E", "This has been true for years — we've been losing people to this same gap for a long time.", False, None),
        ],
        ["the_dormant_talent", "leadership_continuity_risk"],
        False,
    ),
    (
        "SEVER-08",
        "Is this a structural problem or a people problem?",
        "forced_choice", None, "conditional",
        [
            ("A", "Structural — different functions have competing priorities and incentives.", False, None),
            ("B", "People — specific individuals or teams make cross-functional work harder than it needs to be.", False, None),
            ("C", "Both.", False, None),
            ("D", "I'm not sure.", False, None),
            ("E", "It's been this way for as long as anyone can remember — nobody experiences it as new.", False, None),
        ],
        ["silosolation", "the_fracture"],
        False,
    ),
    (
        "SEVER-09",
        "When the deal was being planned, how much attention did the people and culture"
        " integration get relative to the systems and financial integration?",
        "forced_choice", None, "conditional",
        [
            ("A", "Equal attention — people and culture had a dedicated plan alongside everything else.", False, None),
            ("B", "Less — people and culture were acknowledged but not the primary focus.", False, None),
            ("C", "Minimal — the deal was primarily about financials and operations.", False, None),
            ("D", "None — we didn't really plan for the people side.", False, None),
        ],
        ["the_second_close"],
        False,
    ),
    (
        "SEVER-10",
        "Who is most aware of this?",
        "forced_choice", None, "conditional",
        [
            ("A", "Leadership has named it and is actively working on it.", False, None),
            ("B", "Leadership is aware but hasn't addressed it directly.", False, None),
            ("C", "The organization knows before leadership does — it's more visible below than above.", False, None),
            ("D", "It's visible at every level and nobody is sure how to change it.", False, None),
            ("E", "It's been this way long enough that it feels like just how we operate.", False, None),
        ],
        ["culture_drift", "identity_erosion", "the_culture_that_wasnt"],
        False,
    ),
    (
        "SEVER-11",
        "Does the organization know what produced it?",
        "forced_choice", None, "conditional",
        [
            ("A", "Yes — we identified the root cause and addressed it.", False, None),
            ("B", "We think we know but haven't formally confirmed it or verified the fix held.", False, None),
            ("C", "We have a general sense but haven't done a formal analysis.", False, None),
            ("D", "Not really — we settled and moved on without examining what caused it.", False, None),
            ("E", "It's been an open question for as long as I can remember — we've never really pinned it down.", False, None),
        ],
        ["the_unsolved_problem"],
        False,
    ),
    (
        "SEVER-12",
        "What's the most likely explanation?",
        "forced_choice", None, "conditional",
        [
            ("A", "We haven't created enough advancement opportunity internally.", False, None),
            ("B", "Our selection processes may not be as equitable as we think.", False, None),
            ("C", "Diverse talent is leaving before they have a chance to advance.", False, None),
            ("D", "I genuinely don't know — we haven't examined it closely enough.", False, None),
            ("E", "This has been the pattern for years, not something new.", False, None),
        ],
        ["the_diversity_ceiling"],
        False,
    ),
    (
        "SEVER-13",
        "When that feedback hasn't been acted on — what's the typical explanation?",
        "forced_choice", None, "conditional",
        [
            ("A", "The timing wasn't right — we acknowledged it but had other priorities.", False, None),
            ("B", "There was disagreement about whether the findings were accurate.", False, None),
            ("C", "Leadership understood the findings but the will to act on them wasn't there.", False, None),
            ("D", "The findings were addressed in how we talked about them but not in what we did.", False, None),
            ("E", "It's simply how things work here — this has been the pattern for years, not a one-time lapse.", False, None),
        ],
        ["narrative_lock", "the_broken_compass"],
        False,
    ),
    (
        "SEVER-14",
        "How long has this conflict been present?",
        "forced_choice", None, "conditional",
        [
            ("A", "It's recent — it surfaced in the past six months.", False, None),
            ("B", "It's been building for a year or more.", False, None),
            ("C", "It's been unresolved for as long as I can remember.", False, None),
            ("D", "I'm not sure — it may have been there longer than I've recognized.", False, None),
        ],
        ["the_fracture", "silosolation"],
        False,
    ),
    (
        "SEVER-15",
        "How long has your organization been without a dedicated HR function?",
        "forced_choice", None, "conditional",
        [
            ("A", "It's recent — this changed in the past six months.", False, None),
            ("B", "It's been this way for a year or more.", False, None),
            ("C", "It's been this way for as long as I can remember.", False, None),
            ("D", "I'm not sure — it may have been this way longer than I've recognized.", False, None),
        ],
        ["the_exposed", "hr_capture", "planning_authority_gap"],
        False,
    ),
    (
        "Q35",
        "When someone in a key role isn't performing,"
        " what does the conversation usually sound like?",
        "forced_choice", 35, "mid",
        [
            ("A", "We talk about what the person needs to do differently.", False, None),
            ("B", "We talk about whether the role itself is set up to let them succeed.", False, None),
            ("C", "We talk about whether this is the right role for this person.", False, None),
            ("D", "We don't usually have that conversation until something forces it.", False, None),
        ],
        ["built_to_fail", "the_undefined_role", "the_overloaded_manager", "invisible_performance_management"],
        False,
    ),
    (
        "Q36",
        "When someone is underperforming, how does it usually come to a resolution?",
        "forced_choice", 36, "mid",
        [
            ("A", "A direct conversation happens early. Most situations resolve from there.", False, None),
            ("B", "There are conversations, but they tend to drag."
             " The situation usually outlasts the patience for it.", False, None),
            ("C", "The person eventually leaves — resignation, transfer, or mutual agreement"
             " — without a formal process.", False, None),
            ("D", "It depends on who the person is. Some situations get addressed. Others don't.", False, None),
            ("E", "The manager flags it but isn't sure what they're authorized to do about it.", False, None),
        ],
        ["the_paper_tiger", "built_to_fail", "the_undefined_role"],
        False,
    ),
    (
        "Q37",
        "When a policy, process, or tool is no longer working the way it should,"
        " how does that typically surface?",
        "forced_choice", 37, "mid",
        [
            ("A", "Someone with ownership over it flags it and brings a recommendation.", False, None),
            ("B", "People working around it start talking about it"
             " and it eventually reaches leadership.", False, None),
            ("C", "Something breaks — a complaint, a miss, an incident"
             " — and that's when it gets attention.", False, None),
            ("D", "It doesn't always surface. Some things just quietly stop being followed.", False, None),
        ],
        ["the_unexamined_algorithm", "the_policy_lag", "the_undefined_role"],
        False,
    ),
    (
        "Q38",
        "If a senior leader — someone who runs a function or a team — left unexpectedly,"
        " what would happen to what they were carrying?",
        "forced_choice", 38, "mid",
        [
            ("A", "We have someone ready. Coverage would be managed.", False, None),
            ("B", "We'd cover it, but there would be a real gap"
             " while we figured out the transition.", False, None),
            ("C", "A significant amount of what they know and who they know"
             " leaves with them.", False, None),
            ("D", "We'd be in a difficult position."
             " That role holds more than most people realize.", False, None),
        ],
        ["leadership_continuity_risk", "the_unformed_leader", "the_overloaded_manager"],
        False,
    ),
    (
        "Q39",
        "How does your organization typically handle a situation"
        " where someone is clearly not right for a role?",
        "forced_choice", 39, "mid",
        [
            ("A", "We address it directly. The conversation happens and the decision follows.", False, None),
            ("B", "We try to move them into a better fit somewhere else"
             " before making a harder call.", False, None),
            ("C", "We give it more time. Most situations work themselves out.", False, None),
            ("D", "It usually becomes clear the role wasn't set up correctly,"
             " not that the person was wrong for it.", False, None),
        ],
        ["the_paper_tiger", "the_unformed_leader", "built_to_fail"],
        False,
    ),
    # -- Verification probes (Session 14) ----------------------------------------
    (
        "VERIFY-Q16",
        "What's that assessment based on?",
        "forced_choice", None, "conditional",
        [
            ("A", "We've looked at the data. Advancement rates by demographic group"
             " are tracked and reviewed.", False, None),
            ("B", "We don't have formal data on this"
             " — it's my read of how things are going.", False, None),
            ("C", "We've had the conversation but haven't pulled the numbers.", False, None),
            ("D", "We're a small enough organization that I can see it directly.",
             False, None),
        ],
        ["the_diversity_ceiling"],
        True,
    ),
    (
        "VERIFY-Q20",
        "When there's a disagreement about who owns a decision,"
        " how does it get resolved?",
        "forced_choice", None, "conditional",
        [
            ("A", "There's a clear escalation path."
             " It gets to the right person and resolves.", False, None),
            ("B", "It usually works out but the path isn't always obvious.", False, None),
            ("C", "It depends on the people involved — some figure it out,"
             " others escalate unnecessarily.", False, None),
            ("D", "That doesn't come up — ownership is clear enough"
             " that it doesn't create conflict.", False, None),
        ],
        ["built_to_fail", "the_undefined_role", "decision_paralysis"],
        True,
    ),
    (
        "VERIFY-Q21",
        "Think of a significant decision made in the last six months."
        " How long did it take from the moment it needed to be made"
        " to the moment it was made?",
        "forced_choice", None, "conditional",
        [
            ("A", "About as long as it should have."
             " The timeline matched the complexity.", False, None),
            ("B", "Longer than it needed to be, but the outcome was right.", False, None),
            ("C", "Longer than it needed to be, and the delay created real costs.",
             False, None),
            ("D", "I'm not sure I can think of a clear example"
             " — decisions tend to happen gradually.", False, None),
        ],
        ["decision_paralysis", "the_lost_map"],
        True,
    ),
    (
        "VERIFY-Q22",
        "When did your policies last get a meaningful review,"
        " and what changed as a result?",
        "forced_choice", None, "conditional",
        [
            ("A", "Within the past year. Specific updates were made,"
             " reviewed by counsel or HR leadership.", False, None),
            ("B", "Within the past year, but mostly incremental"
             " — format updates more than substantive changes.", False, None),
            ("C", "A few years ago. I can't point to a specific recent review.",
             False, None),
            ("D", "I'm not sure — I'd have to check who's responsible for that.",
             False, None),
        ],
        ["the_policy_lag", "the_unexamined_algorithm"],
        True,
    ),
    (
        "VERIFY-Q24",
        "How do you know?",
        "forced_choice", None, "conditional",
        [
            ("A", "We measure it. Engagement data, pulse surveys, or direct feedback"
             " with real follow-through.", False, None),
            ("B", "My read of the people I interact with most directly.", False, None),
            ("C", "They're performing, so I assume they're okay.", False, None),
            ("D", "I check in regularly and people tell me things are fine.", False, None),
        ],
        ["invisible_burnout"],
        True,
    ),
    (
        "VERIFY-Q25",
        # COPY REVIEW: two-part question — "who" + "what did the path look like"
        # Options address path quality only. Review in voice pass before deployment.
        "Who was the last person you promoted into a leadership role from within,"
        " and what did the development path look like?",
        "forced_choice", None, "conditional",
        [
            ("A", "I can name them. There was a deliberate path"
             " — coaching, expanded scope, clear criteria.", False, None),
            ("B", "I can name them but the path was more organic than structured.",
             False, None),
            ("C", "It's been a while since we've promoted from within"
             " into a leadership role.", False, None),
            ("D", "We promoted someone but it hasn't gone as well as we hoped.",
             False, None),
        ],
        ["leadership_continuity_risk", "the_dormant_talent", "the_unformed_leader"],
        True,
    ),
    (
        "VERIFY-Q26",
        "What was the last significant cross-functional initiative,"
        " and what made it work?",
        "forced_choice", None, "conditional",
        [
            ("A", "I can name it. Clear ownership, right people, produced the outcome.",
             False, None),
            ("B", "I can name it but it worked because specific people made it work"
             " — not because of the system.", False, None),
            ("C", "Cross-functional work tends to happen within clusters"
             " — some functions collaborate well, others don't.", False, None),
            ("D", "It's hard to name a specific example"
             " — most work stays within functions.", False, None),
        ],
        ["silosolation", "the_fracture"],
        True,
    ),
    (
        "VERIFY-Q27A",
        "What specifically has been done to integrate the people and culture side"
        " — not the systems and processes?",
        "forced_choice", None, "conditional",
        [
            ("A", "A specific plan with owners, milestones,"
             " and progress we're tracking.", False, None),
            ("B", "Some deliberate effort but it's been more reactive than planned.",
             False, None),
            ("C", "We've focused on the structural side"
             " — people and culture integration hasn't had the same attention.",
             False, None),
            ("D", "We haven't treated people and culture as a separate workstream.",
             False, None),
        ],
        ["the_second_close"],
        True,
    ),
    (
        "VERIFY-Q27B",
        "If you asked a new hire six months in what surprised them about the culture,"
        " what would they say?",
        "forced_choice", None, "conditional",
        [
            ("A", "Nothing significant"
             " — what they experienced matched what they were told.", False, None),
            ("B", "Mostly matched, but some things were different than they expected.",
             False, None),
            ("C", "I'm not sure"
             " — we don't have good visibility into the new hire experience.",
             False, None),
            ("D", "There are things people mention that suggest a gap"
             " between what we say and what they find.", False, None),
        ],
        ["culture_drift", "identity_erosion", "the_culture_that_wasnt"],
        True,
    ),
    (
        "VERIFY-Q28",
        "What specifically changed,"
        " and how do you know it addressed the root cause?",
        "forced_choice", None, "conditional",
        [
            ("A", "I can describe it. Named changes, traceable to the condition,"
             " confirmed by follow-up.", False, None),
            ("B", "We made changes but I couldn't say with confidence"
             " we got to the root.", False, None),
            ("C", "Process updates and policy changes"
             " — more procedural than structural.", False, None),
            ("D", "Honestly, the situation resolved and we moved forward."
             " I'm not sure what specifically changed.", False, None),
        ],
        ["the_unsolved_problem"],
        True,
    ),
    (
        "VERIFY-Q31",
        "What makes you confident they're unrelated?",
        "forced_choice", None, "conditional",
        [
            ("A", "We looked at them together."
             " No common thread in circumstances, people, or outcomes.", False, None),
            ("B", "They happened at different times,"
             " in different parts of the organization.", False, None),
            ("C", "I haven't looked at them together"
             " — that's my read but I haven't verified it.", False, None),
            ("D", "I'm not sure anyone has looked at them as a set.", False, None),
        ],
        ["the_unsolved_problem", "decision_blindness"],
        True,
    ),
    (
        "VERIFY-Q32",
        "What's an example of something your organization examined,"
        " concluded needed to change, and actually changed?",
        "forced_choice", None, "conditional",
        [
            ("A", "I can name it. Specific situation, clear conclusion,"
             " observable change that held.", False, None),
            ("B", "I can name it but the change was partial"
             " — we moved in the right direction but didn't complete it.", False, None),
            ("C", "It's hard to name a specific example"
             " where the full cycle completed.", False, None),
            ("D", "We're good at the examining and concluding part."
             " The changing part is harder.", False, None),
        ],
        ["narrative_lock", "groundhog_day", "the_broken_compass"],
        True,
    ),
    # -- Distinguisher questions (Session 30) -----------------------------------
    (
        "DIST-CM-01",
        "When you think about the manager whose development of their team concerns you,"
        " which of the following best describes what changed in the last 18 months?",
        "forced_choice", None, "conditional",
        [
            ("A", "The role or team grew significantly — more people, more scope,"
             " or a restructuring added responsibility without removing anything.", False, None),
            ("B", "The role hasn't changed materially."
             " This manager has had roughly the same span and scope for a while.", False, None),
            ("C", "The manager is newer to the role"
             " — promoted or hired into it within the past year.", False, None),
            ("D", "I'm not certain there's been a change"
             " — the concern has been building gradually.", False, None),
        ],
        ["the_overloaded_manager", "the_unformed_leader", "the_dormant_talent"],
        False,
    ),
    (
        "DIST-CM-02",
        "When this manager is asked directly about what their team members need to grow,"
        " what typically happens?",
        "forced_choice", None, "conditional",
        [
            ("A", "They can describe what each person needs with real specificity"
             " — they just haven't acted on it.", False, None),
            ("B", "Their answers are vague or general"
             " — it's hard to tell if they've thought about it.", False, None),
            ("C", "They point to workload or time as the reason development hasn't happened.",
             False, None),
            ("D", "Their answers vary — they can speak to some team members but not others,"
             " with no consistent pattern.", False, None),
        ],
        ["the_dormant_talent", "the_unformed_leader", "the_overloaded_manager"],
        False,
    ),
    (
        "DIST-CC-01",
        "When you think about the employees who have left — or who you're most concerned"
        " about losing — how would you describe their tenure with the organization?",
        "forced_choice", None, "conditional",
        [
            ("A", "Mostly newer employees — people who've been here less than a year,"
             " often within their first few months.", False, None),
            ("B", "Mostly longer-tenured employees — people who've been here for several years"
             " and who built something here.", False, None),
            ("C", "It's mixed — departures are spread across tenure levels without a clear pattern.",
             False, None),
            ("D", "Departures haven't been concentrated in any particular group"
             " — the concern is more about engagement or direction than actual turnover.",
             False, None),
        ],
        ["the_culture_that_wasnt", "identity_erosion", "culture_drift"],
        False,
    ),
    (
        "DIST-CC-02",
        "When departing employees or disengaged employees describe what's wrong,"
        " which framing comes up most?",
        "forced_choice", None, "conditional",
        [
            ("A", "“This isn't what I was told it would be” or"
             " “what they described in the interview isn't what I found here.”",
             False, None),
            ("B", "“This isn't who we used to be” or"
             " “something important got lost when we grew.”",
             False, None),
            ("C", "“Leadership says one thing and does another” or"
             " “the values on the wall don't match how decisions get made.”",
             False, None),
            ("D", "People aren't saying much — the concern is more visible in"
             " engagement scores or quiet behavior than in explicit feedback.",
             False, None),
        ],
        ["the_culture_that_wasnt", "identity_erosion", "culture_drift"],
        False,
    ),
]


# -- Builder -------------------------------------------------------------------

def _build_library():
    lib = {}
    _uniform = {
        "aptitude_liability":  0.25, "aptitude_asset":  0.25,
        "authority_liability": 0.25, "authority_asset": 0.25,
        "alliance_liability":  0.25, "alliance_asset":  0.25,
        "attitude_liability":  0.25, "attitude_asset":  0.25,
    }
    # Signal Map tier seedings (Session 11 pre-calibration pass).
    # Source: PRV3_Signal_Map (Drive 1LMx13dWDvAMWwxYHG7ikd9moZLndphNZw66hbejfLqI)
    # Rule: highest-weight non-cluster state in state_targets; primary dim(s) seeded.
    # HIGH->0.60, MEDIUM->0.40. LOW/Cluster questions absent (remain at 0.25).
    # Asset fields not seeded — liability-only pass.
    _seed = {
        "Q01":           {"authority_liability": 0.60},
        "Q02":           {"authority_liability": 0.60, "aptitude_liability": 0.60},
        "Q03A":          {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q03A-D-FOLLOW": {"authority_liability": 0.60, "alliance_liability": 0.60},
        "Q04":           {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q05":           {"attitude_liability": 0.60},
        "Q06":           {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q07":           {"authority_liability": 0.60, "alliance_liability": 0.60},
        "Q09":           {"authority_liability": 0.60, "alliance_liability": 0.60},
        "Q10":           {"aptitude_liability": 0.60},
        "Q11":           {"authority_liability": 0.40, "attitude_liability": 0.40},
        "Q12":           {"attitude_liability": 0.60},
        "Q13":           {"authority_liability": 0.40, "alliance_liability": 0.40},
        "Q14":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q15":           {"attitude_liability": 0.40, "authority_liability": 0.40},
        "Q16":           {"attitude_liability": 0.40, "authority_liability": 0.40},
        "Q17":           {"attitude_liability": 0.40, "alliance_liability": 0.40},
        "Q19":           {"authority_liability": 0.40, "attitude_liability": 0.40},
        "Q20":           {"authority_liability": 0.60, "aptitude_liability": 0.60},
        "Q21":           {"authority_liability": 0.40, "alliance_liability": 0.40},
        "Q22":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q23":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q24":           {"attitude_liability": 0.40, "alliance_liability": 0.40},
        # Q25: cluster governing (the_dormant_talent) — no seed entry
        "Q26":           {"authority_liability": 0.60, "alliance_liability": 0.60},
        "Q27A":          {"alliance_liability": 0.40},
        "Q28":           {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q29":           {"attitude_liability": 0.40, "authority_liability": 0.40},
        # Q30: cluster governing (the_suppression_filter) — no seed entry
        "Q31":           {"authority_liability": 0.60, "attitude_liability": 0.60},
        "Q32":           {"authority_liability": 0.40, "alliance_liability": 0.40},
        "Q33":           {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "Q34":           {"attitude_liability": 0.40, "alliance_liability": 0.40},
        "SEVER-01":      {"attitude_liability": 0.40, "authority_liability": 0.40},
        "SEVER-02":      {"authority_liability": 0.60, "aptitude_liability": 0.60},
        "SEVER-03":      {"authority_liability": 0.40, "alliance_liability": 0.40},
        "SEVER-04":      {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "SEVER-05":      {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "SEVER-06":      {"attitude_liability": 0.40, "alliance_liability": 0.40},
        "SEVER-07":      {"authority_liability": 0.40, "aptitude_liability": 0.40},
        "SEVER-08":      {"authority_liability": 0.60, "alliance_liability": 0.60},
        "SEVER-09":      {"alliance_liability": 0.40},
        "SEVER-11":      {"authority_liability": 0.60, "attitude_liability": 0.60},
        "SEVER-12":      {"attitude_liability": 0.40, "authority_liability": 0.40},
        "SEVER-13":      {"attitude_liability": 0.40, "alliance_liability": 0.40},
    }
    # Phase 3 Pass 1 (Session 13): per-option aptitude_liability overrides.
    # Authority-overlap questions with documented Aptitude crossover.
    # Problem options: apt = 0.25 (explicit secondary signal, enables discrimination).
    # Neutral/positive options: apt = 0.0 (removes uniform noise).
    # Primary Authority signal unchanged.
    _opt_apt = {
        "Q03A": {"A": 0.0,  "B": 0.25, "C": 0.25, "D": 0.25},
        "Q06":  {"A": 0.25, "B": 0.25, "C": 0.25, "D": 0.25, "E": 0.0},
        "Q19":  {"A": 0.0,  "B": 0.0,  "C": 0.25, "D": 0.25},
    }
    # Session 14: per-option full contribution overrides for Aptitude additive questions.
    # Q35-Q39 bypass _uniform / _seed — each option carries explicit per-field values.
    # "all others: 0.0" means every unspecified field is 0.0.
    _z = {
        "aptitude_liability":  0.0, "aptitude_asset":  0.0,
        "authority_liability": 0.0, "authority_asset": 0.0,
        "alliance_liability":  0.0, "alliance_asset":  0.0,
        "attitude_liability":  0.0, "attitude_asset":  0.0,
    }
    # Contribution vocabulary for _opt_contrib:
    #   0.60 = HIGH           primary liability or asset — maximum signal confidence
    #   0.50 = INTERMEDIATE   between MEDIUM and HIGH; verification probe answers
    #                         that fall between ambiguous and clearly problem-indicating
    #   0.40 = MEDIUM         secondary or partial signal
    #   0.25 = LOW/baseline   minimal or cluster-level signal
    #   0.0  = absent         field not relevant to this option
    _opt_contrib = {
        # -- WS1: bulk valence template, Q01–Q34 (Session 15) ------------------
        # Questions with DE options deferred to WS2: Q02 Q06 Q13 Q18 Q22 Q23 Q27A Q32
        # Q03B and Q03A-D-FOLLOW excluded (routing questions).
        "Q01": {  # Authority HIGH (founders_grip). Single-seeded. Neutral drain B v17.
            "A": {**_z, "authority_asset":    0.40},                    # F
            "B": {**_z, "authority_liability": -0.15},                  # A — neutral drain v17
            "C": {**_z, "authority_liability": 0.60},                   # P
            "D": {**_z, "authority_liability": 0.60},                   # P
            "E": {**_z, "authority_liability": 0.60},                   # P
        },
        "Q02": {  # Authority HIGH + Aptitude (dual).
            "A": {**_z, "authority_asset":     0.40},                              # F
            "B": {**_z, "authority_liability": 0.25, "aptitude_liability": -0.15, "attitude_liability": -0.10},  # A
            "C": {**_z, "authority_liability": 0.60, "aptitude_liability": 0.30},  # P
            "D": {**_z, "authority_liability": 0.60, "aptitude_liability": 0.30},  # P
            "E": {**_z, "authority_liability": 0.30, "authority_asset":    0.20},  # DE
        },
        "Q03A": {  # Authority HIGH + Attitude (dual). _opt_apt crossover folded.
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30,
                        "aptitude_liability":  0.25},                   # P + crossover
            "C": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30,
                        "aptitude_liability":  0.25},                   # P + crossover
            "D": {**_z, "authority_liability": 0.25},                   # A
        },
        "Q04": {  # Authority HIGH + Attitude (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.25},                   # A
            "D": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30, "alliance_liability": -0.15},  # P
        },
        "Q05": {  # Attitude HIGH (the_untouchable). Single-seeded.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.60},                    # P
            "D": {**_z, "attitude_liability": 0.60},                    # P
        },
        "Q06": {  # Authority HIGH + Attitude (dual) + aptitude crossover.
            "A": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30, "aptitude_liability": 0.25},  # P
            "B": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30, "aptitude_liability": 0.25},  # P
            "C": {**_z, "authority_liability": 0.20, "authority_asset":    0.25},                              # DE
            "D": {**_z, "aptitude_liability": 0.60, "attitude_liability": 0.30},  # P — APT-PT fix v15
            "E": {**_z, "authority_asset":     0.40},                                                          # F
        },
        "Q07": {  # Alliance HIGH (the_fracture). Authority drain v15; amplify B v17.
            "A": {**_z, "alliance_liability": 0.25},                    # A
            "B": {**_z, "alliance_liability": 0.80},                    # P — amplify v17
            "C": {**_z, "alliance_liability": 0.60},                    # P
            "D": {**_z, "alliance_liability": 0.60},                    # P
        },
        "Q08": {  # No seed. Attitude MED (leadership_deafness) + Alliance (dual).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
        },
        "Q09": {  # Alliance HIGH (the_fracture). Authority drain v15.
            "A": {**_z, "alliance_asset":     0.40},                    # F
            "B": {**_z, "alliance_liability": 0.25},                    # A
            "C": {**_z, "alliance_liability": 0.60},                    # P
            "D": {**_z, "alliance_liability": 0.60},                    # P
            "E": {**_z, "alliance_liability": 0.60},                    # P
        },
        "Q10": {  # Aptitude HIGH (paper_tiger) + Authority (dual).
            "A": {**_z, "aptitude_asset":     0.40},                    # F
            "B": {**_z, "aptitude_liability": 0.25},                    # A
            "C": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.30, "authority_asset": -0.10},  # P
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.30},  # P
        },
        "Q11": {  # Attitude MED + Authority (dual). Amplify D v17 (C locked S18).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.05},  # P — LOCKED S18
            "D": {**_z, "attitude_liability": 0.75, "authority_liability": 0.25},  # P — amplify v17
            "E": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
        },
        "Q12": {  # Attitude HIGH (the_untouchable). Single-seeded.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.60},                    # P
            "D": {**_z, "attitude_liability": 0.60},                    # P
            "E": {**_z, "attitude_liability": 0.25},                    # A
        },
        "Q13": {  # Authority MED + Alliance (dual). Neutral drain E v17.
            "A": {**_z, "alliance_liability":  0.30, "authority_liability": 0.20, "authority_asset": 0.15},  # DE
            "B": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P
            "C": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P
            "D": {**_z, "authority_liability": 0.50, "alliance_liability":  0.25},                           # P
            "E": {**_z, "authority_asset":     0.40, "authority_liability": -0.15},                          # F — neutral drain v17
        },
        "Q14": {  # Authority MED (pay_exposure, pay_fog) + Aptitude (dual). Contrast B/C v16.
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": -0.05},                  # A — contrast v16
            "C": {**_z, "authority_liability": -0.05},                  # A — contrast v16
            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P
            "E": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P
        },
        "Q15": {  # Attitude MED (diversity_ceiling) + Authority (dual). Amplify D v17 (C locked S18).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25, "alliance_liability": -0.15},  # P — LOCKED S18
            "D": {**_z, "attitude_liability": 0.75, "authority_liability": 0.25},  # P — amplify v17
            "E": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
        },
        "Q16": {  # Attitude MED (diversity_ceiling). Authority partial drain v15; contrast B/C v16.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50, "authority_liability": -0.20},  # P — contrast v16
            "C": {**_z, "attitude_liability": 0.50, "authority_liability": -0.20},  # P — contrast v16
            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P
            "E": {**_z, "attitude_liability": 0.25},                    # A
        },
        "Q17": {  # Attitude MED + Alliance (dual). All targets are Attitude.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "E": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
        },
        "Q18": {  # Attitude MED (C-Silence) + Alliance. Q18-E conditional.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "E": {
                "_conditional": {
                    "logic_gate": "is_high_hazard",
                    "condition_map": {
                        True:  {"attitude_liability": 0.60, "attitude_asset": 0.00},
                        False: {"attitude_liability": 0.00, "attitude_asset": 0.30},
                    }
                }
            },  # DE — conditional on intake.is_high_hazard
        },
        "Q19": {  # Authority MED + Attitude (dual). _opt_apt crossover folded.
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.50, "attitude_liability": 0.25,
                        "aptitude_liability":  0.25},                   # P + crossover
            "D": {**_z, "authority_liability": 0.50, "attitude_liability": 0.25,
                        "aptitude_liability":  0.25},                   # P + crossover
        },
        "Q20": {  # Aptitude HIGH (built_to_fail). Authority drain v15. v19: C/D 0.60->0.80.
            "A": {**_z, "aptitude_asset":     0.40},                    # F
            "B": {**_z, "aptitude_liability": 0.25},                    # A
            "C": {**_z, "aptitude_liability": 0.80},                    # P
            "D": {**_z, "aptitude_liability": 0.80},                    # P
        },
        "Q21": {  # Authority MED + Alliance (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.50, "alliance_liability": 0.25},  # P
            "D": {**_z, "authority_liability": 0.50, "alliance_liability": 0.25},  # P
            "E": {**_z, "authority_liability": 0.50, "alliance_liability": 0.25},  # P
        },
        "Q22": {  # Authority MED + Aptitude (dual). Contrast B v16.
            "A": {**_z, "authority_asset":     0.40},                                                       # F
            "B": {**_z, "authority_liability": -0.10},                                                      # A — contrast v16
            "C": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},                           # P
            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},                           # P
            "E": {**_z, "authority_liability": 0.45, "aptitude_liability": 0.25, "authority_asset": 0.10},  # DE
        },
        "Q23": {  # Authority MED + Aptitude (dual). No F option; A is DE base.
            "A": {**_z, "authority_asset":     0.40, "authority_liability": 0.15},                          # DE base
            "B": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},                           # P
            "C": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.10},                           # P
            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25, "attitude_liability": -0.15},  # P
        },
        "Q24": {  # Attitude MED (invisible_burnout) + Alliance (dual).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
        },
        "Q25": {  # Aptitude MED (dormant_talent, unformed_leader) + Authority (dual).
            "A": {**_z, "aptitude_asset":     0.40},                    # F
            "B": {**_z, "aptitude_liability": 0.25},                    # A
            "C": {**_z, "aptitude_liability": 0.50, "authority_liability": 0.25},  # P
            "D": {**_z, "aptitude_liability": 0.50, "authority_liability": 0.25},  # P
            "E": {**_z, "aptitude_liability": 0.50, "authority_liability": 0.25},  # P
        },
        "Q26": {  # Alliance HIGH (the_fracture). Authority drain v15; contrast C v16; amplify C v17.
            "A": {**_z, "alliance_asset":     0.40},                    # F
            "B": {**_z, "alliance_liability": 0.25},                    # A
            "C": {**_z, "alliance_liability": 0.80, "authority_liability": -0.30},  # P — contrast v16, amplify v17
            "D": {**_z, "alliance_liability": 0.60},                    # P
        },
        "Q27A": {  # Alliance MED. Single-seeded.
            "A": {**_z, "alliance_asset":     0.40},                                                     # F
            "B": {**_z, "alliance_liability":  0.45, "authority_asset":   0.20, "alliance_asset": 0.10}, # DE
            "C": {**_z, "alliance_liability":  0.50},                                                    # P
            "D": {**_z, "alliance_liability":  0.50},                                                    # P
        },
        "Q27B": {  # No seed. Attitude MED (C-Culture cluster). Single-dim.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50},                    # P
            "C": {**_z, "attitude_liability": 0.50},                    # P
            "D": {**_z, "attitude_liability": 0.50},                    # P
            "E": {**_z, "attitude_liability": 0.50},                    # P
        },
        "Q28": {  # Authority HIGH (unsolved_problem) + Attitude (dual). Neutral drain B v17.
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": -0.15},                  # A — neutral drain v17
            "C": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P
            "D": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P
        },
        "Q29": {  # Attitude MED (diversity_ceiling). Authority partial drain v15.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P
            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P
            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.10},  # P
            "E": {**_z, "attitude_liability": 0.25},                    # A
        },
        "Q30": {  # Authority MED + Alliance (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.25},                   # A
            "D": {**_z, "authority_liability": 0.50, "alliance_liability": 0.25},  # P
        },
        "Q31": {  # Authority HIGH (unsolved_problem) + Alliance (dual).
            # Seed had attitude but targets include decision_blindness (Alliance HIGH).
            # Corrected to authority+alliance to match actual targets.
            "A": {**_z, "authority_liability": 0.25},                   # A
            "B": {**_z, "authority_liability": 0.60, "alliance_liability": 0.30},  # P
            "C": {**_z, "authority_liability": 0.60, "alliance_liability": 0.30},  # P
            "D": {**_z, "authority_liability": 0.60, "alliance_liability": 0.30},  # P
        },
        "Q32": {  # Attitude MED. Single-seeded.
            "A": {**_z, "attitude_asset":     0.40},                                # F
            "B": {**_z, "attitude_liability":  0.35, "attitude_asset":    0.15},    # DE
            "C": {**_z, "attitude_liability":  0.50},                               # P
            "D": {**_z, "attitude_liability":  0.50},                               # P
        },
        "Q33": {  # Authority MED + Aptitude (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P
            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P
        },
        "Q34": {  # Attitude MED + Alliance (dual). All targets are Attitude.
            "A": {**_z, "attitude_liability": 0.25},                    # A
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "E": {**_z, "attitude_liability": 0.25},                    # A
        },
        # -- End WS1 entries ----------------------------------------------------
        "Q35": {  # Contrast B v16; amplify B v17.
            "A": {**_z, "aptitude_liability": 0.25},
            "B": {**_z, "aptitude_liability": 0.80, "authority_liability": -0.35},  # contrast v16, amplify v17
            "C": {**_z, "aptitude_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.40},
        },
        "Q36": {  # Contrast E v16 (APT-PT-00 decoupling); amplify E v17.
            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},
            "B": {**_z, "aptitude_liability": 0.40},
            "C": {**_z, "aptitude_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.40, "attitude_liability": 0.40},
            "E": {**_z, "aptitude_liability": 0.80, "authority_liability": -0.40},  # contrast v16, amplify v17
        },
        "Q37": {
            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},
            "B": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.25},
            "C": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40},
        },
        "Q38": {
            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},
            "B": {**_z, "aptitude_liability": 0.25, "authority_liability": 0.40},
            "C": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.60},
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.60},
        },
        "Q39": {
            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.25},
            "B": {**_z, "aptitude_liability": 0.25, "alliance_liability": 0.25},
            "C": {**_z, "aptitude_liability": 0.60, "alliance_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.40, "alliance_liability": 0.60},
        },
        # -- Verification probes (Session 14) ----------------------------------------
        "VERIFY-Q16": {
            "A": {**_z, "attitude_asset":     0.40, "authority_asset":     0.40},
            "B": {**_z, "attitude_liability":  0.40, "authority_liability":  0.25},
            "C": {**_z, "attitude_liability":  0.40, "authority_liability":  0.25},
            "D": {**_z, "attitude_liability":  0.25},
        },
        "VERIFY-Q20": {
            "A": {**_z, "aptitude_asset":     0.40, "authority_asset":     0.40},
            "B": {**_z, "aptitude_liability":  0.25, "authority_liability":  0.25},
            "C": {**_z, "aptitude_liability":  0.40, "authority_liability":  0.40},
            "D": {**_z, "aptitude_asset":     0.25, "authority_asset":     0.40},
        },
        "VERIFY-Q21": {
            "A": {**_z, "authority_asset":     0.40},
            "B": {**_z, "authority_liability":  0.25},
            "C": {**_z, "authority_liability":  0.50},
            "D": {**_z, "authority_liability":  0.40, "aptitude_liability":  0.25},
        },
        "VERIFY-Q22": {
            "A": {**_z, "aptitude_asset":     0.40, "authority_asset":     0.40},
            "B": {**_z, "aptitude_liability":  0.25, "authority_liability":  0.25},
            "C": {**_z, "aptitude_liability":  0.50, "authority_liability":  0.40},
            "D": {**_z, "aptitude_liability":  0.60, "authority_liability":  0.60},
        },
        "VERIFY-Q24": {
            "A": {**_z, "attitude_asset":     0.40},
            "B": {**_z, "attitude_liability":  0.40},
            "C": {**_z, "attitude_liability":  0.60},
            "D": {**_z, "attitude_liability":  0.40},
        },
        "VERIFY-Q25": {
            "A": {**_z, "aptitude_asset":     0.40, "authority_asset":     0.40},
            "B": {**_z, "aptitude_liability":  0.25, "authority_liability":  0.25},
            "C": {**_z, "aptitude_liability":  0.50, "authority_liability":  0.40},
            "D": {**_z, "aptitude_liability":  0.60, "authority_liability":  0.40},
        },
        "VERIFY-Q26": {
            "A": {**_z, "alliance_asset":     0.40},
            "B": {**_z, "alliance_liability":  0.40},
            "C": {**_z, "alliance_liability":  0.50},
            "D": {**_z, "alliance_liability":  0.60},
        },
        "VERIFY-Q27A": {
            "A": {**_z, "alliance_asset":     0.40, "attitude_asset":     0.40},
            "B": {**_z, "alliance_liability":  0.25, "attitude_liability":  0.25},
            "C": {**_z, "alliance_liability":  0.50, "attitude_liability":  0.50},
            "D": {**_z, "alliance_liability":  0.60, "attitude_liability":  0.60},
        },
        "VERIFY-Q27B": {
            "A": {**_z, "attitude_asset":     0.40},
            "B": {**_z, "attitude_liability":  0.25},
            "C": {**_z, "attitude_liability":  0.50, "alliance_liability":  0.25},
            "D": {**_z, "attitude_liability":  0.60, "alliance_liability":  0.25},
        },
        "VERIFY-Q28": {
            "A": {**_z, "authority_asset":    0.40, "aptitude_asset":     0.40},
            "B": {**_z, "authority_liability": 0.40, "aptitude_liability":  0.25},
            "C": {**_z, "authority_liability": 0.50, "aptitude_liability":  0.40},
            "D": {**_z, "authority_liability": 0.60, "aptitude_liability":  0.60},
        },
        "VERIFY-Q31": {
            "A": {**_z, "authority_asset":    0.40},
            "B": {**_z, "authority_liability": 0.25},
            "C": {**_z, "authority_liability": 0.60, "alliance_liability":  0.40},
            "D": {**_z, "authority_liability": 0.60, "alliance_liability":  0.50},
        },
        "VERIFY-Q32": {
            "A": {**_z, "attitude_asset":     0.40, "authority_asset":     0.25},
            "B": {**_z, "attitude_liability":  0.25, "authority_liability":  0.25},
            "C": {**_z, "attitude_liability":  0.50, "authority_liability":  0.40},
            "D": {**_z, "attitude_liability":  0.60, "authority_liability":  0.40},
        },
        "SEVER-05": {  # Q23-A probe. Weak response = retroactive base downgrade.
            "A": {**_z},                                                           # Strong — tested; Q23-A base stands
            "B": {**_z},                                                           # Strong — documented; Q23-A base stands
            "C": {**_z, "authority_asset": -0.30, "authority_liability": 0.30},    # Weak — retroactive downgrade
            "D": {**_z, "authority_asset": -0.30, "authority_liability": 0.30},    # Weak — retroactive downgrade
            "E": {**_z, "authority_asset": -0.30, "authority_liability": 0.30},    # Weak — untested for years, same category as C/D
        },
        # -- Distinguisher questions (Session 30) ----------------------------------
        "DIST-CM-01": {
            "A": {**_z, "aptitude_liability": 0.35, "aptitude_asset": 0.25, "authority_liability": 0.25},
            "B": {**_z, "aptitude_liability": 0.25},
            "C": {**_z, "aptitude_liability": 0.45},
            "D": {**_z, "aptitude_liability": 0.15},
        },
        "DIST-CM-02": {
            "A": {**_z, "aptitude_asset": 0.40, "attitude_liability": 0.45},
            "B": {**_z, "aptitude_liability": 0.45},
            "C": {**_z, "aptitude_liability": 0.35, "aptitude_asset": 0.20, "authority_liability": 0.25},
            "D": {**_z, "aptitude_liability": 0.15},
        },
        "DIST-CC-01": {
            "A": {**_z, "alliance_liability": 0.25, "attitude_liability": 0.40},
            "B": {**_z, "alliance_liability": 0.35, "attitude_liability": 0.40},
            "C": {**_z, "authority_liability": 0.30, "attitude_liability": 0.40},
            "D": {**_z, "attitude_liability": 0.15},
        },
        "DIST-CC-02": {
            "A": {**_z, "aptitude_liability": 0.30, "attitude_liability": 0.45},
            "B": {**_z, "alliance_liability": 0.40, "attitude_liability": 0.40},
            "C": {**_z, "authority_liability": 0.40, "attitude_liability": 0.40},
            "D": {**_z, "attitude_liability": 0.15},
        },
    }

    # Axis tags wired to AnswerOption.axis_targets at build time.
    # "_DE" suffix: delta overlay resolved at accumulation time via _apply_axis_modifiers().
    _axis_tags = {
        "Q18": {"E": ["Safety & Wellbeing_DE"]},
    }

    # Sparse per-option observation_text, wired to AnswerOption.observation_text
    # at build time -- same pattern as _axis_tags above. Any option not
    # listed here defaults to None via .get(qid, {}).get(o[0]). Q03B
    # intentionally excluded -- all four options share an identical flat
    # 0.25 baseline across every field, no salience-differentiating signal
    # to author against. The single strength/baseline option per other
    # question (the asset/healthy case) is deliberately left unauthored
    # throughout, except where a question has no such option (Q07, Q34).
    _observation_text_tags: dict = {
        "Q01": {
            "B": "Bigger decisions get complicated here even when smaller ones don't.",
            "C": "Decisions get made, then get reopened. People aren't always sure what's actually final.",
            "D": "Getting to a decision here takes more effort than it should.",
            "E": "Decisions happen, but nobody's quite sure who was accountable for making them.",
        },
        "Q02": {
            "B": "HR handles what it needs to, but it isn't operating as a strategic function here.",
            "C": "HR is thin -- a part-time role or something people share on top of other work.",
            "D": "There's no dedicated HR function in this organization right now.",
            "E": "There's an HR function, but its independence is genuinely in question.",
        },
        "Q04": {
            "B": "Whether a concern gets addressed here depends more on the person than the process.",
            "C": "There's real uncertainty about what actually happens once a concern gets raised.",
            "D": "People have learned that raising a concern here doesn't produce results.",
        },
        "Q05": {
            "B": "Underperformance gets addressed eventually, but it takes longer than it should.",
            "C": "Whether someone's held accountable here seems to depend on who they are.",
            "D": "Underperformance tends to get tolerated rather than addressed.",
        },
        "Q06": {
            "A": "There's been an external legal claim, EEOC charge, or regulatory inquiry.",
            "B": "There's been a monetary settlement tied to an employment matter.",
            "C": "Legal counsel has already flagged something here as a liability.",
            "D": "There's a known practice here that isn't fully compliant, and it hasn't been addressed.",
        },
        "Q07": {
            "A": "Turnover here doesn't concentrate anywhere obvious -- it's spread across the organization.",
            "B": "Turnover concentrates under specific managers or in specific teams.",
            "C": "The same roles keep turning over here.",
            "D": "People tend to leave at a specific point in their career with this organization.",
        },
        "Q08": {
            "B": "Leadership sometimes wonders whether they're getting the full picture.",
            "C": "Problems tend to reach leadership only once they're already crises.",
            "D": "What people hear informally here doesn't match what comes through formal channels.",
        },
        "Q09": {
            "B": "People here do their jobs, but they don't really operate as a team.",
            "C": "There's tension at the senior level that's mostly stayed contained there.",
            "D": "There's a senior-level dynamic that's broken the surface -- the rest of the organization has noticed.",
            "E": "There's a real unresolved conflict at the senior level.",
        },
        "Q10": {
            "B": "Some processes here are out of date or inconsistently followed.",
            "C": "There's a real gap between what's written down and how this organization actually operates.",
            "D": "This organization runs more on managers' judgment than on documented process.",
        },
        "Q11": {
            "B": "There are visible exceptions here to what this organization says it values.",
            "C": "Relationships and visibility tend to drive outcomes here more than the stated values do.",
            "D": "What gets rewarded here and what this organization says it values are two different things, and people know it.",
            "E": "This organization's values are written down, but they don't really govern anything.",
        },
        "Q12": {
            "B": "Manager quality is uneven here, some strong, some struggling.",
            "C": "The managers here are capable individually, but they're stretched beyond what they can handle.",
            "D": "There are specific managers here who are a real problem, not the whole layer.",
            "E": "Leadership doesn't have great visibility into how managers are actually performing.",
        },
        "Q13": {
            "A": "Leadership knows where this organization is going, but it's not clear the rest of the organization does.",
            "B": "This organization has been here before. People are waiting to see if this time is actually different.",
            "C": "The direction here isn't as clear as it should be, and people are operating on different assumptions.",
            "D": "The direction is clear, but there's real skepticism about whether it'll be followed through on.",
        },
        "Q14": {
            "B": "This organization may be externally competitive, but internal consistency is a real question.",
            "C": "This organization may be internally consistent, but external competitiveness is a real question.",
            "D": "There are real concerns here about both compensation consistency and competitiveness.",
            "E": "This organization hasn't looked closely enough at compensation to know where it stands.",
        },
        "Q15": {
            "B": "Advancement happens here, but the criteria aren't always transparent.",
            "C": "Advancement here tends to favor certain people or certain teams.",
            "D": "This organization doesn't have much room for advancement to offer.",
            "E": "People looking to grow tend to leave before this organization can develop them.",
        },
        "Q16": {
            "B": "This organization is diverse at entry levels, but that changes as people move up.",
            "C": "This organization has invested in diversity, but it's not clear that's translating into advancement.",
            "D": "This organization is losing diverse talent before it reaches senior levels, and the reason isn't clear.",
            "E": "This isn't something this organization has looked at closely enough to answer with confidence.",
        },
        "Q17": {
            "B": "Initiatives here tend to start strong and fade before they take hold.",
            "C": "People here participate in change, but they don't really invest in it.",
            "D": "This organization keeps addressing the same problems with different approaches and getting the same result.",
            "E": "This organization knows what needs to change and talks about it, but doesn't actually move.",
        },
        "Q18": {
            "B": "The policies exist here, but there's real doubt about whether people follow them or report when something's wrong.",
            "C": "This organization has had incidents that, in hindsight, could have been prevented if people had spoken up earlier.",
            "D": "Security here is a known gap, people work around protocols rather than follow them.",
            "E": "Safety and security concerns here have gone unaddressed longer than they should have.",
        },
        "Q19": {
            "B": "There are gaps between what this organization says internally and externally, and people are aware of them.",
            "C": "There's a real gap here, the external narrative is ahead of the internal reality.",
            "D": "This organization hasn't really looked at whether its internal and external stories align.",
        },
        "Q20": {
            "B": "There are some areas of overlap or ambiguity in who owns what here.",
            "C": "There are meaningful gaps here, certain functions or roles don't have clear mandates.",
            "D": "Authority and responsibility questions are a recurring source of friction here.",
        },
        "Q21": {
            "B": "Decisions here require more back-and-forth than they should.",
            "C": "Decisions that shouldn't need senior involvement tend to escalate there anyway.",
            "D": "Decisions get made here and then get reopened without much new information.",
            "E": "Decisions happen here, but it's unclear who actually has the authority to make them.",
        },
        "Q22": {
            "B": "Some policies here haven't been looked at in a while.",
            "C": "This organization hasn't reviewed its policies recently, and there's real doubt they reflect current law or practice.",
            "D": "This organization has run into a situation its policies didn't cover, or didn't cover correctly.",
            "E": "This organization uses AI tools in people decisions without a clear sense of the implications.",
        },
        "Q23": {
            "B": "This organization is more dependent on certain people than it should be, even if it hasn't been tested yet.",
            "C": "A past departure exposed how thin this organization was in a role, and recovery was harder than expected.",
            "D": "There are people here right now whose departure would be genuinely destabilizing.",
        },
        "Q24": {
            "B": "Some high performers here are carrying more than is healthy long term.",
            "C": "This organization has lost high performers recently in ways that came as a real surprise.",
            "D": "There are people here running on empty, and it's not clear how to address it.",
        },
        "Q25": {
            "B": "Internal development here is inconsistent, promotion from within happens when it can.",
            "C": "This organization tends to hire externally for senior roles rather than build the pipeline.",
            "D": "This organization has invested in developing people, but it hasn't produced what was expected.",
            "E": "Developing people hasn't really been a priority here.",
        },
        "Q26": {
            "B": "Cross-functional work here happens, but there's more friction at the seams than there should be.",
            "C": "Cross-functional initiatives here stall predictably at the same points.",
            "D": "Functions here operate independently, collaboration is the exception rather than the rule.",
        },
        "Q27B": {
            "B": "This organization's culture is drifting, things feel different from what it's been.",
            "C": "Different parts of this organization seem to have genuinely different cultures.",
            "D": "There's real uncertainty here about what the culture actually is right now.",
            "E": "The culture people experience here doesn't match what gets described in recruiting.",
        },
        "Q29": {
            "B": "This organization is diverse at entry levels, but that changes as people move up.",
            "C": "This organization has invested in diversity, but it's not clear that's translating into advancement.",
            "D": "This organization is losing diverse talent before it reaches senior levels, and the reason isn't clear.",
            "E": "This isn't something this organization has looked at closely enough to answer with confidence.",
        },
        "Q30": {
            "B": "There are gaps in what reaches people here, some things land and some don't.",
            "C": "Communication here is inconsistent, it varies a lot by team or manager.",
            "D": "There's a real information gap here, people often hear about things informally before it's official.",
        },
        "Q32": {
            "B": "This organization reflects on what happens, but doesn't always follow through on the learning.",
            "C": "This organization has received consistent feedback, through surveys, consultants, or data, that it's struggled to act on.",
            "D": "This organization tends to move on from difficult experiences without really examining them.",
        },
        "Q33": {
            "B": "Continuity plans exist here, but there's real doubt they're current or would hold up under pressure.",
            "C": "This organization has some continuity documentation, but it isn't something actively maintained.",
            "D": "This organization doesn't have continuity infrastructure in place.",
        },
        "Q34": {
            "A": "This reads as a people issue, specific individuals or relationships are at the center of it.",
            "B": "This reads as a structural issue, the way this organization is set up is producing the problem.",
            "C": "This reads as a cultural issue, about how people behave and what this organization accepts.",
            "D": "This reads as a leadership issue, the will or capability to act on what's known isn't there.",
            "E": "The problem here is real, but it doesn't cleanly categorize into one clear cause.",
        },
    }

    # Severity follow-on input tags wired to AnswerOption.severity_input_mapping
    # at build time. Maps each SEVER-01..13 answer option to one of the 5 real
    # SeverityInput fields -- content-authoring pass, Gemini-approved handoff.
    # Confidence noted per question (fit strength against the question's
    # actual authored content, flagged rather than smoothed over):
    #
    #   STRONG   -- direct fit: SEVER-01, 02, 03, 04, 06, 07, 11
    #   MODERATE -- fits under a reasonable reinterpretation of the field's
    #               literal definition: SEVER-05, 09, 10
    #   WEAK     -- stretch fit, noted inline: SEVER-08, SEVER-12
    #   SEVER-13 -- all 4 options map to the same value; the question only
    #               fires on already-unactioned feedback, so the fact that
    #               it fired (not which option is chosen) carries the
    #               prior_failed_resolution=True signal. No per-option
    #               discrimination is possible from this question's content.
    _severity_input_tags = {
        "SEVER-01": {  # STRONG -- awareness/naming (the_diversity_ceiling)
            "A": {"named_condition": True},
            "B": {"named_condition": True},
            "C": {"named_condition": False},
            "D": {"named_condition": False},
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-02": {  # STRONG -- breadth (built_to_fail / the_undefined_role / decision_paralysis)
            "A": {"population_band": "under_10pct"},
            "B": {"population_band": "under_10pct"},
            "C": {"population_band": "10_30pct"},
            "D": {"population_band": "30pct_plus"},
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-03": {  # STRONG -- breadth (decision_paralysis)
            "A": {"population_band": "under_10pct"},
            "B": {"population_band": "10_30pct"},
            "C": {"population_band": "30pct_plus"},
            "D": {"population_band": "30pct_plus"},
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-04": {  # STRONG -- policy review recency as inverse-duration proxy (the_policy_lag)
            "A": {"duration_band": "0_6mo"},
            "B": {"duration_band": "6_18mo"},
            "C": {"duration_band": "18mo_plus"},
            "D": {"duration_band": "18mo_plus"},
        },
        "SEVER-05": {  # MODERATE -- verification confidence, reinterpreted as named_condition
            "A": {"named_condition": True},          # tested and confirmed
            "B": {"named_condition": True},           # documented and reviewed
            "C": {"named_condition": False},          # unconfirmed
            "D": {"named_condition": False},          # assumed, unverified
            "E": {"duration_band": "18mo_plus"},      # untested/unverified for years -- Weak category
        },
        "SEVER-06": {  # STRONG -- duration (invisible_burnout)
            "A": {"duration_band": "0_6mo"},
            "B": {"duration_band": "6_18mo"},
            "C": {"duration_band": "18mo_plus"},
            "D": {"duration_band": "18mo_plus"},
        },
        "SEVER-07": {  # STRONG -- realized turnover as financial indicator (the_dormant_talent / leadership_continuity_risk)
            "A": {"financial_indicators": False},
            "B": {"financial_indicators": False},
            "C": {"financial_indicators": True},      # real departures already occurred
            "D": {"financial_indicators": True},
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-08": {  # WEAK -- root-cause diagnosis, reinterpreted as named_condition (silosolation / the_fracture)
            "A": {"named_condition": True},
            "B": {"named_condition": True},
            "C": {"named_condition": True},
            "D": {"named_condition": False},          # "I'm not sure" -- no diagnosis given
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-09": {  # MODERATE -- upfront preparation adequacy, reinterpreted as prior_failed_resolution (the_second_close)
            "A": {"prior_failed_resolution": False},
            "B": {"prior_failed_resolution": False},
            "C": {"prior_failed_resolution": True},
            "D": {"prior_failed_resolution": True},
        },
        "SEVER-10": {  # MODERATE -- awareness breadth, reinterpreted as population_band (culture_drift / identity_erosion / the_culture_that_wasnt)
            "A": {"population_band": "under_10pct"},
            "B": {"population_band": "under_10pct"},
            "C": {"population_band": "10_30pct"},
            "D": {"population_band": "30pct_plus"},
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-11": {  # STRONG -- root-cause resolution outcome (the_unsolved_problem)
            "A": {"prior_failed_resolution": False},  # identified and addressed
            "B": {"prior_failed_resolution": True},
            "C": {"prior_failed_resolution": True},
            "D": {"prior_failed_resolution": True},
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-12": {  # WEAK -- only 1 of 4 options discriminates (the_diversity_ceiling)
            "A": {"financial_indicators": False},
            "B": {"financial_indicators": False},
            "C": {"financial_indicators": True},      # realized attrition
            "D": {"financial_indicators": False},
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-13": {  # non-discriminating -- see note above (narrative_lock / the_broken_compass)
            "A": {"prior_failed_resolution": True},
            "B": {"prior_failed_resolution": True},
            "C": {"prior_failed_resolution": True},
            "D": {"prior_failed_resolution": True},
            "E": {"duration_band": "18mo_plus"},
        },
        "SEVER-14": {  # STRONG -- duration (the_fracture / silosolation, Q09-E second trigger)
            "A": {"duration_band": "0_6mo"},
            "B": {"duration_band": "6_18mo"},
            "C": {"duration_band": "18mo_plus"},
            "D": {"duration_band": "18mo_plus"},
        },
        "SEVER-15": {  # STRONG -- duration (the_exposed / planning_authority_gap / hr_capture, Q02-D trigger)
            "A": {"duration_band": "0_6mo"},
            "B": {"duration_band": "6_18mo"},
            "C": {"duration_band": "18mo_plus"},
            "D": {"duration_band": "18mo_plus"},
        },
    }

    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:
        base = dict(_uniform)
        base.update(_seed.get(qid, {}))
        lib[qid] = QuestionDefinition(
            question_id=qid,
            question_text=text,
            format=fmt,
            sequence_position=pos,
            checkpoint_segment=seg,
            answer_options=[
                AnswerOption(
                    option_id=o[0],
                    option_text=o[1],
                    dimensional_contributions=(
                        dict(_opt_contrib[qid][o[0]])
                        if qid in _opt_contrib
                        else {
                            **base,
                            "aptitude_liability": _opt_apt.get(qid, {}).get(
                                o[0], base["aptitude_liability"]
                            ),
                        }
                    ),
                    severity_trigger=o[2],
                    severity_follow_on_id=o[3],
                    axis_targets=_axis_tags.get(qid, {}).get(o[0], []),
                    severity_input_mapping=_severity_input_tags.get(qid, {}).get(o[0]),
                    observation_text=_observation_text_tags.get(qid, {}).get(o[0]),
                )
                for o in opts
            ],
            state_targets=list(targets),
            severity_trigger=sev,
        )
    return lib


# -- Question registry ---------------------------------------------------------

QUESTION_LIBRARY: "dict[str, QuestionDefinition]" = _build_library()


# -- Expected question ID patterns (for validation) ----------------------------

CORE_SEQUENCE_IDS = [f"Q{i:02d}" for i in range(1, 40)]   # Q01-Q39
SEVERITY_FOLLOW_ON_IDS = [f"SEVER-{i:02d}" for i in range(1, 14)]  # SEVER-01 to SEVER-13

DISTINGUISHER_CLUSTER_PREFIXES = {
    "C-Manager":  "DIST-CM",
    "C-Culture":  "DIST-CC",
    "C-Silence":  "DIST-CS",
    "C-InfoFlow": "DIST-CI",
}

CHECKPOINT_SEGMENTS = {
    "early":       range(1, 12),   # Q01-Q11
    "mid":         range(12, 20),  # Q12-Q19
    "late":        range(20, 35),  # Q20-Q34
    "conditional": None,           # severity follow-ons and distinguisher questions
}
