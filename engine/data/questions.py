"""
PRV3 Scoring Engine — Section I.2
Question Library Schema and Registry

Populated Session 9 from PRV3_Question_Library_Draft (Google Drive).
Source: Session 2 conversation history, confirmed and locked.

Core sequence: Q01-Q34. Q03 and Q27 have conditional A/B versions.
Severity follow-ons: SEVER-01 through SEVER-13.
  Note: spec originally specified 12 follow-ons; Q32a adds a 13th distinct follow-on.
  Q28a and Q31a share SEVER-11 (same content, different adaptive parent question).

All dimensional_contributions: 0.25 baseline across all 8 fields.
Calibration target - weights differentiated after Phase 1 calibration.
Do not set speculative weights.

Spec reference: Section I.2
"""

from dataclasses import dataclass, field
from typing import Optional


# -- Answer option -------------------------------------------------------------

@dataclass
class AnswerOption:
    """
    One selectable option within a question.

    dimensional_contributions: all 8 fields initialized at 0.25 (baseline).
    Calibration target - do not set speculative weights.

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
        ["decision_paralysis", "the_lost_map", "the_founders_grip"],
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
            ("D", "Absent — we don't have a dedicated HR function right now.", False, None),
            ("E", "We have HR but I sometimes wonder whether it's truly independent.", False, None),
        ],
        ["the_exposed", "hr_capture"],
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
         "the_arbitrary_standard", "the_wrong_reward"],
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
         "the_tolerated_violation", "the_policy_lag"],
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
        ["the_fracture", "silosolation", "built_to_fail", "the_untouchable",
         "the_diversity_ceiling", "the_inside_track", "invisible_burnout",
         "the_unformed_leader", "the_overloaded_manager", "the_dormant_talent"],
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
            ("E", "There's a significant unresolved conflict I'm not sure how to address.", False, None),
        ],
        ["the_fracture", "silosolation", "decision_paralysis"],
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
        ["the_policy_lag", "paper_shield", "the_paper_tiger"],
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
         "the_arbitrary_standard", "the_basement_standard", "the_broken_compass"],
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
         "the_untouchable", "leadership_deafness", "the_suppression_filter"],
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
        ["pay_exposure", "the_pay_fog"],
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
            ("D", "We have people right now whose loss would be genuinely destabilizing.", False, None),
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
        ["invisible_burnout"],
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
        ["leadership_continuity_risk", "the_dormant_talent", "the_unformed_leader"],
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
        ["silosolation", "the_fracture"],
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
        ["culture_drift", "identity_erosion", "the_culture_that_wasnt"],
        True,
    ),
    (
        "Q28",
        "You mentioned [earlier legal/compliance/HR matter]. What changed as a result?"
        " (Adaptive — fires only if Q06 A or B selected.)",
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
        ["the_lost_map", "the_suppression_filter"],
        False,
    ),
    (
        "Q31",
        "Thinking back to the matter you mentioned earlier — what came out of the process?"
        " (Adaptive — fires only if Q06 A or B selected and Q28 not yet asked.)",
        "forced_choice", 31, "late",
        [
            ("A", "Isolated incidents — each situation was distinct and unrelated to the others.", False, None),
            ("B", "There's a theme — similar circumstances or similar people keep appearing.", False, None),
            ("C", "We resolved the situation but I'm not confident we addressed what caused it.", True, "SEVER-11"),
            ("D", "The condition that produced the matter is still present — we closed the claim, not the problem.", True, "SEVER-11"),
        ],
        ["the_unsolved_problem", "decision_blindness"],
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
        ],
        ["narrative_lock", "the_broken_compass"],
        False,
    ),
]


# -- Builder -------------------------------------------------------------------

def _build_library():
    lib = {}
    _base = {
        "aptitude_liability": 0.25, "aptitude_asset": 0.25,
        "authority_liability": 0.25, "authority_asset": 0.25,
        "alliance_liability": 0.25, "alliance_asset": 0.25,
        "attitude_liability": 0.25, "attitude_asset": 0.25,
    }
    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:
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
                    dimensional_contributions=dict(_base),
                    severity_trigger=o[2],
                    severity_follow_on_id=o[3],
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

CORE_SEQUENCE_IDS = [f"Q{i:02d}" for i in range(1, 35)]   # Q01-Q34
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
