// PRV3 -- static mirror of engine/data/states.py's STATE_PROFILES id,
// state_name, primary_dimension, and descriptive_prose fields, for the
// /book/toc hub page (a purely static content page with no live diagnostic
// session -- cannot read the Python engine directly, same reason
// web/lib/resolution-family.ts mirrors engine/resolution_families.py rather
// than importing it). Content copied verbatim, not re-authored -- if
// engine/data/states.py's descriptive_prose changes, this file needs a
// matching re-sync, same discipline as resolution-family.ts's own header
// note. Generated from a direct read of STATE_PROFILES this session, not
// hand-transcribed.

export type StateDimension = "aptitude" | "authority" | "alliance" | "attitude";

export interface BookStateEntry {
  id: string;
  name: string;
  dimension: StateDimension;
  // Raw engine/data/states.py STATE_PROFILES resolution_family value
  // (e.g. "Executive Counsel + Intervention"), not translated -- added
  // this session for /book/toc's resolution_family badge (Phase 1 data
  // confirmation, prompts/book-toc-fuller-vision.md). Same mirroring
  // pattern as every other field here, same source. Consumers translate
  // via web/lib/resolution-family.ts's translateResolutionFamily() at
  // display time, same as every other real caller -- not a second copy
  // of that logic.
  resolutionFamily: string;
  descriptiveProse: string;
}

// Ordered Aptitude -> Authority -> Alliance -> Attitude, matching the
// dimension grouping /book/toc renders in. Live count as of this session:
// 7 / 22 / 7 / 22 = 58 (the_inner_circle, the 58th state, is Attitude --
// the older "7/22/7/21" figure some docs cite predates that addition).
export const BOOK_STATE_INDEX: BookStateEntry[] = [
  {
    id: "the_unformed_leader",
    resolutionFamily: "Development",
    name: "The Unformed Leader",
    dimension: "aptitude",
    descriptiveProse: "A manager occupies the role without having been equipped for it. Direction is inconsistent, feedback arrives late or not at all, and the team absorbs the gap by lowering its own expectations. Turnover concentrates among the people who had other options.",
  },
  {
    id: "the_overloaded_manager",
    resolutionFamily: "Development + Roadmap",
    name: "The Overloaded Manager",
    dimension: "aptitude",
    descriptiveProse: "A manager who was competent for the original scope of the role is now carrying more than the role was designed to hold. Development conversations have been replaced by status updates, and decisions queue behind everything else competing for the same attention. The organization redesigned the job without redesigning the resources around it.",
  },
  {
    id: "the_dormant_talent",
    resolutionFamily: "Executive Counsel + Intervention",
    name: "The Dormant Talent",
    dimension: "aptitude",
    descriptiveProse: "The manager can name precisely what each person needs to grow and consistently doesn't act on it. Development stalls while the manager's own visibility and standing continue to rise. The people with the clearest read on the gap are also the ones most able to leave.",
  },
  {
    id: "built_to_fail",
    resolutionFamily: "Roadmap + Intervention",
    name: "Built to Fail",
    dimension: "aptitude",
    descriptiveProse: "The role's scope exceeds what any reasonable allocation of resources could support, and each person who holds it is told to make it work rather than given what making it work would require. The organization treats each departure as an individual hiring failure rather than a structural one. The next person inherits the same impossible math.",
  },
  {
    id: "the_undefined_role",
    resolutionFamily: "Roadmap",
    name: "The Undefined Role",
    dimension: "aptitude",
    descriptiveProse: "The role's actual boundaries were never defined, so what lands on the desk, what gets escalated, and what falls through are all matters of local negotiation rather than design. Work duplicates in some places and goes unclaimed in others. The organization is paying for a function that isn't reliably producing what anyone assumes it produces.",
  },
  {
    id: "the_paper_tiger",
    resolutionFamily: "Development + Roadmap",
    name: "The Paper Tiger",
    dimension: "aptitude",
    descriptiveProse: "A performance problem has been managed verbally for long enough that the written record no longer matches what everyone privately knows. When the organization finally needs to act on documented cause, it discovers it has been managing one employee on paper and a different one in practice. The gap surfaces in front of the people with the least patience for it.",
  },
  {
    id: "invisible_performance_management",
    resolutionFamily: "Development + Roadmap",
    name: "Invisible Performance Management",
    dimension: "aptitude",
    descriptiveProse: "A manager's read on an underperforming employee is accurate but was never written down, so it carries no evidentiary weight when a decision needs defending. This isn't concealment. It's an absence of documentation that turns a sound judgment into an exposed one.",
  },
  {
    id: "the_founders_grip",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "The Founder's Grip",
    dimension: "authority",
    descriptiveProse: "One person's approval gates nearly every consequential decision, and that person is stretched too thin to make those calls on current information. Work either waits in queue or routes around the bottleneck entirely. The senior people who could tolerate neither option have already left.",
  },
  {
    id: "the_exposed",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "The Exposed",
    dimension: "authority",
    descriptiveProse: "There is no function in the organization whose job it actually is to manage employee-related risk. Concerns have nowhere reliable to land, and obligations accumulate without anyone tracking them. The organization isn't between HR leaders. It's accumulating liability on a clock nobody is watching.",
  },
  {
    id: "the_uninitiated",
    resolutionFamily: "Intervention",
    name: "The Uninitiated",
    dimension: "authority",
    descriptiveProse: "A significant organizational event is underway, and the people leading it have never done this before. They are capable in general and unprepared for this specific kind of decision, which means the costliest mistakes are the ones nobody on the team knows to watch for.",
  },
  {
    id: "leadership_continuity_risk",
    resolutionFamily: "Roadmap + Development",
    name: "Leadership Continuity Risk",
    dimension: "authority",
    descriptiveProse: "Authority concentrated in a small number of people has no defined path to anyone else if one of them leaves. The organization can name who is critical but not who would replace them or how. That gap becomes a crisis the moment it stops being theoretical.",
  },
  {
    id: "hr_capture",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "HR Capture",
    dimension: "authority",
    descriptiveProse: "The function responsible for protecting the organization and its people has been repurposed to protect specific leaders instead. Complaints against the powerful get managed differently than complaints against everyone else, and the people making that distinction know exactly what they're doing.",
  },
  {
    id: "decision_paralysis",
    resolutionFamily: "Roadmap + Intervention",
    name: "Decision Paralysis",
    dimension: "authority",
    descriptiveProse: "Decisions that should move at operational speed are instead stalling in a governance structure that was never built to render verdicts quickly. Nobody is refusing to decide. The structure itself doesn't produce clear ownership of the call.",
  },
  {
    id: "the_policy_lag",
    resolutionFamily: "Roadmap",
    name: "The Policy Lag",
    dimension: "authority",
    descriptiveProse: "The organization's written policies describe an operating reality that no longer exists. Practice has moved on without the documentation catching up, so the rules on paper and the rules people actually follow have quietly diverged.",
  },
  {
    id: "the_unexamined_algorithm",
    resolutionFamily: "Roadmap + Executive Counsel",
    name: "The Unexamined Algorithm",
    dimension: "authority",
    descriptiveProse: "An automated or algorithmic system is making or materially influencing consequential decisions with no governance layer reviewing what it's actually doing. Nobody owns auditing its outputs for bias, error, or drift. The organization finds out something was wrong only after it's been wrong for a while.",
  },
  {
    id: "heard_and_ignored",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "Heard & Ignored",
    dimension: "authority",
    descriptiveProse: "Concerns are being raised through the organization's own channels and are reliably not acted on. The reporting mechanism exists and functions as a formality, not a corrective one. People stop using it once they've tested it enough times to know what happens when they do.",
  },
  {
    id: "the_tolerated_violation",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "The Tolerated Violation",
    dimension: "authority",
    descriptiveProse: "A known violation of policy, law, or basic standard has been allowed to continue long enough that it now reads as normal rather than exceptional. Everyone involved can describe the violation accurately. Nobody with the authority to stop it has been willing to be the one who does.",
  },
  {
    id: "dueling_narratives",
    resolutionFamily: "Executive Counsel + Roadmap",
    name: "Dueling Narratives",
    dimension: "authority",
    descriptiveProse: "Different parts of the organization are telling meaningfully different versions of the same set of facts, and nobody has reconciled them into one account. Each version is defensible in isolation. Together they create exposure the moment anyone outside the organization compares notes.",
  },
  {
    id: "the_unsolved_problem",
    resolutionFamily: "Intervention + Roadmap",
    name: "The Unsolved Problem",
    dimension: "aptitude",
    descriptiveProse: "A specific problem has been addressed before, more than once, and keeps returning in close to the same form. Each fix treats the most recent symptom rather than whatever keeps regenerating it. The organization is paying repeatedly for a resolution that has never actually resolved anything.",
  },
  {
    id: "transition_paralysis",
    resolutionFamily: "Intervention + Roadmap",
    name: "Transition Paralysis",
    dimension: "authority",
    descriptiveProse: "An organizational transition has started and then stalled somewhere in the middle, with the old structure partly dismantled and the new one not yet functional. People are operating in the gap, uncertain which authority actually governs their work day to day.",
  },
  {
    id: "paper_shield",
    resolutionFamily: "Roadmap",
    name: "Paper Shield",
    dimension: "aptitude",
    descriptiveProse: "Contingency and continuity plans exist in writing and have never been tested against anything real. The organization believes it is prepared because the documentation says so. The gap between documented readiness and actual readiness surfaces exactly once, at the worst time to discover it.",
  },
  {
    id: "the_lost_map",
    resolutionFamily: "Roadmap + Development",
    name: "The Lost Map",
    dimension: "authority",
    descriptiveProse: "Institutional knowledge lives in individual heads rather than in any system the organization actually maintains. When someone leaves, whatever they knew leaves with them, and the organization relearns it the expensive way.",
  },
  {
    id: "invisible_influence_architecture",
    resolutionFamily: "Roadmap + Executive Counsel",
    name: "Invisible Influence Architecture",
    dimension: "authority",
    descriptiveProse: "Real influence over decisions runs through informal channels that don't match the org chart anyone would draw. The formally accountable people are not always the ones actually deciding outcomes. New arrivals spend real time discovering who actually has to say yes.",
  },
  {
    id: "pay_exposure",
    resolutionFamily: "Roadmap",
    name: "Pay Exposure",
    dimension: "authority",
    descriptiveProse: "Compensation has drifted out of alignment with what the market is currently paying for comparable roles, and the organization is discovering this reactively, through departures, rather than proactively. Each departure it triggers is a preventable one.",
  },
  {
    id: "the_pay_fog",
    resolutionFamily: "Roadmap",
    name: "The Pay Fog",
    dimension: "authority",
    descriptiveProse: "Pay decisions across the organization don't follow a consistent, defensible logic, even though each individual decision might have made sense in the moment it was made. That inconsistency is hard to see from inside any one decision and impossible to miss once someone lines them all up.",
  },
  {
    id: "compression_crisis",
    resolutionFamily: "Roadmap",
    name: "Compression Crisis",
    dimension: "authority",
    descriptiveProse: "Layers of management have been compressed or eliminated faster than the remaining structure can absorb the load, concentrating decision-making into fewer people than the work actually requires. What looks like efficiency on an org chart is strain everywhere it actually gets executed.",
  },
  {
    id: "sequential_decision_blindness",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "Sequential Decision Blindness",
    dimension: "authority",
    descriptiveProse: "A series of individually defensible decisions, made by different people without coordination, adds up to a pattern that looks like retaliation or targeting when viewed together. No single decision-maker intended that outcome. The exposure exists in the aggregate, not in any one decision anyone can point to.",
  },
  {
    id: "disparate_impact_architecture",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "Disparate Impact Architecture",
    dimension: "authority",
    descriptiveProse: "A policy or practice applies the same rule to everyone and produces meaningfully different outcomes across different groups, in a pattern that would be recognizable to anyone who looked at the aggregate data. Neutral intent doesn't change what the data shows.",
  },
  {
    id: "planning_authority_gap",
    resolutionFamily: "Roadmap + Executive Counsel",
    name: "Planning Authority Gap",
    dimension: "authority",
    descriptiveProse: "The people responsible for planning don't hold the authority to make the decisions their plans depend on, and the people who hold that authority aren't the ones doing the planning. Plans get built and then wait for approval from someone who wasn't part of building them.",
  },
  {
    id: "the_fracture",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "The Fracture",
    dimension: "alliance",
    descriptiveProse: "A working relationship between two people, teams, or functions that the organization depends on has broken down past the point of informal repair. Work still moves, but it moves around the fracture rather than through it.",
  },
  {
    id: "the_second_close",
    resolutionFamily: "Development + Intervention",
    name: "The Second Close",
    dimension: "alliance",
    descriptiveProse: "A relationship or agreement was renegotiated once already, and the same underlying issue that forced the first renegotiation is resurfacing. Whatever the first fix addressed, it wasn't the actual cause. The people involved are less willing to extend trust a second time.",
  },
  {
    id: "silosolation",
    resolutionFamily: "Development",
    name: "Silosolation",
    dimension: "alliance",
    descriptiveProse: "Teams that need each other's information to do their jobs well are operating as if they don't, each optimizing for its own metrics without visibility into how that affects anyone else. The isolation isn't hostile. It's structural, and it produces the same friction hostility would.",
  },
  {
    id: "the_suppression_filter",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "The Suppression Filter",
    dimension: "alliance",
    descriptiveProse: "Bad news gets filtered, softened, or dropped entirely as it moves up through the organization's layers, so the people with authority to act on it are consistently the last to hear an accurate version. Each layer believes it's protecting leadership from noise.",
  },
  {
    id: "the_arbitrary_standard",
    resolutionFamily: "Intervention + Roadmap",
    name: "The Arbitrary Standard",
    dimension: "alliance",
    descriptiveProse: "The rules that govern who gets what treatment aren't applied consistently, and the pattern of who benefits isn't accidental even if nobody designed it on purpose. People notice the inconsistency well before anyone in leadership does.",
  },
  {
    id: "decision_blindness",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "Decision Blindness",
    dimension: "alliance",
    descriptiveProse: "A single significant decision was made without input from the people who held the information that would have changed it. The decision-maker wasn't negligent. The information simply never reached them, because nobody's job was making sure it did.",
  },
  {
    id: "distributed_culture_fragmentation",
    resolutionFamily: "Development + Intervention",
    name: "Distributed Culture Fragmentation",
    dimension: "alliance",
    descriptiveProse: "Teams operating in different locations, functions, or time zones have developed genuinely different norms for how work gets done, and nobody has reconciled them into one coherent culture. The friction shows up exactly at the seams where the teams have to work together.",
  },
  {
    id: "the_untouchable",
    resolutionFamily: "Executive Counsel + Intervention",
    name: "The Untouchable",
    dimension: "attitude",
    descriptiveProse: "One person's results or position have made them functionally exempt from the standards everyone else is held to. Everyone around them can name the exemption specifically. The cost isn't just what that person does. It's what everyone watching learns about what the organization actually values.",
  },
  {
    id: "what_nobody_says",
    resolutionFamily: "Intervention",
    name: "What Nobody Says",
    dimension: "attitude",
    descriptiveProse: "There is a specific, known problem that people in the organization can describe accurately in private and will not raise anywhere it might reach someone with the authority to fix it. The silence isn't accidental. It's a rational response to what happened, or is believed to happen, to the last person who spoke up.",
  },
  {
    id: "leadership_deafness",
    resolutionFamily: "Executive Counsel",
    name: "Leadership Deafness",
    dimension: "attitude",
    descriptiveProse: "Leadership is operating on a version of organizational reality that the people below them stopped believing months or years ago. The gap isn't intentional deception so much as an accumulated pattern of information getting softened on its way up.",
  },
  {
    id: "the_diversity_ceiling",
    resolutionFamily: "Intervention",
    name: "The Diversity Ceiling",
    dimension: "attitude",
    descriptiveProse: "The organization's stated commitment to diversity and inclusion is visible in messaging and invisible in outcomes. Representation doesn't advance past a specific point in the hierarchy no matter how the numbers look at entry level. People below that ceiling can see exactly where it sits.",
  },
  {
    id: "culture_drift",
    resolutionFamily: "Intervention",
    name: "Culture Drift",
    dimension: "attitude",
    descriptiveProse: "The organization's stated values and its actual day-to-day behavior have drifted apart gradually enough that no single moment marks the change. Nobody decided to abandon the values. They just stopped being what got rewarded.",
  },
  {
    id: "identity_erosion",
    resolutionFamily: "Intervention",
    name: "Identity Erosion",
    dimension: "attitude",
    descriptiveProse: "The organization has lost a clear, shared answer to what it actually is and what makes it different from anywhere else someone could work. That uncertainty shows up first in retention and recruiting, before it shows up anywhere leadership is looking.",
  },
  {
    id: "the_culture_that_wasnt",
    resolutionFamily: "Intervention",
    name: "The Culture That Wasn't",
    dimension: "attitude",
    descriptiveProse: "What was described during hiring and what actually exists inside the organization are two different cultures, and new hires discover the gap almost immediately. The mismatch is sharpest and most damaging in the first few months, before anyone has built enough tenure to rationalize it.",
  },
  {
    id: "the_burned_credibility",
    resolutionFamily: "Intervention",
    name: "The Burned Credibility",
    dimension: "attitude",
    descriptiveProse: "Leadership has announced significant changes before and either didn't follow through or followed through badly enough that people stopped believing the announcements. The next initiative, however well designed, inherits the skepticism earned by the last one.",
  },
  {
    id: "invisible_burnout",
    resolutionFamily: "Development + Intervention",
    name: "Invisible Burnout",
    dimension: "attitude",
    descriptiveProse: "People are burning out while their output looks fine, which means the organization's usual signals for catching the problem aren't catching it. The cost surfaces later, all at once, as a resignation or a mistake that looks sudden but wasn't.",
  },
  {
    id: "the_basement_standard",
    resolutionFamily: "Intervention + Roadmap",
    name: "The Basement Standard",
    dimension: "attitude",
    descriptiveProse: "A standard of performance well below what the organization would say it expects has become the accepted baseline, because nobody has been willing to enforce the standard that's actually on paper. The best performers notice the gap first, and leave.",
  },
  {
    id: "the_inside_track",
    resolutionFamily: "Intervention + Roadmap",
    name: "The Inside Track",
    dimension: "attitude",
    descriptiveProse: "Advancement and opportunity flow disproportionately to a specific, identifiable group through channels that aren't the organization's stated process. Everyone outside that group can name it, usually specifically.",
  },
  {
    id: "narrative_lock",
    resolutionFamily: "Executive Counsel + Intervention",
    name: "Narrative Lock",
    dimension: "attitude",
    descriptiveProse: "The organization keeps telling itself and its people a story about who it is that stopped being accurate some time ago, and it can't update that story even when the facts on the ground contradict it. Anyone who challenges the story is treated as the problem rather than the messenger.",
  },
  {
    id: "groundhog_day",
    resolutionFamily: "Roadmap + Executive Counsel",
    name: "Groundhog Day",
    dimension: "attitude",
    descriptiveProse: "The same class of mistake recurs across projects, teams, or cycles, and the organization has no mechanism for capturing what it learned the last time so it doesn't happen again. Each recurrence gets treated as a new problem rather than a repeat of an old one.",
  },
  {
    id: "the_wrong_reward",
    resolutionFamily: "Intervention + Roadmap",
    name: "The Wrong Reward",
    dimension: "attitude",
    descriptiveProse: "The organization is getting exactly the behavior its incentive structure actually rewards, and that behavior is not the one leadership says it wants. People are responding rationally to the real incentives, not the stated ones.",
  },
  {
    id: "the_unreported_hazard",
    resolutionFamily: "Intervention",
    name: "The Unreported Hazard",
    dimension: "attitude",
    descriptiveProse: "Real safety concerns exist and are not reliably making it into the organization's reporting system, for reasons that have more to do with culture than process. People have learned that reporting doesn't change much and might cost them something personally.",
  },
  {
    id: "the_unlocked_door",
    resolutionFamily: "Development + Intervention",
    name: "The Unlocked Door",
    dimension: "attitude",
    descriptiveProse: "Security or safety practices that were adequate for an earlier version of the organization haven't kept pace with how the organization actually operates now. Nobody decided to leave the door open. It's simply never been revisited.",
  },
  {
    id: "the_broken_compass",
    resolutionFamily: "Executive Counsel",
    name: "The Broken Compass",
    dimension: "attitude",
    descriptiveProse: "The organization can articulate the right strategic direction clearly and consistently fails to actually move in it when the moment requires a hard call. The gap isn't a knowledge problem. It's a courage problem, and it shows up at exactly the moments that matter most.",
  },
  {
    id: "wellbeing_theater",
    resolutionFamily: "Intervention",
    name: "Wellbeing Theater",
    dimension: "attitude",
    descriptiveProse: "The organization has visible wellbeing programming that isn't changing the underlying conditions actually driving people's stress and dissatisfaction. The initiatives address the symptom the organization is comfortable addressing rather than the cause it would rather not name.",
  },
  {
    id: "human_displacement_anxiety",
    resolutionFamily: "Development + Intervention",
    name: "Human Displacement Anxiety",
    dimension: "attitude",
    descriptiveProse: "People across the organization are anxious about being displaced by automation or AI, and that anxiety is affecting engagement and decision-making whether or not the organization has any actual plans in that direction. Silence from leadership doesn't read as reassurance. It reads as confirmation.",
  },
  {
    id: "motivational_architecture_failure",
    resolutionFamily: "Intervention + Roadmap",
    name: "Motivational Architecture Failure",
    dimension: "attitude",
    descriptiveProse: "The organization's reward system has stopped functioning as a source of motivation at all, for enough of the workforce that engagement has flattened across the board rather than in any one identifiable group. People haven't misread the incentives. They've stopped believing the incentives connect to anything real.",
  },
  {
    id: "cultural_overtime",
    resolutionFamily: "Intervention + Roadmap",
    name: "Cultural Overtime",
    dimension: "attitude",
    descriptiveProse: "Extended hours have become an unstated cultural expectation rather than an occasional operational necessity, and the organization is carrying real legal and financial exposure from that norm without having decided, on paper, that it wants to run this way.",
  },
  {
    id: "the_inner_circle",
    resolutionFamily: "Intervention + Executive Counsel",
    name: "The Inner Circle",
    dimension: "attitude",
    descriptiveProse: "There's a group at the top of this organization who look out for each other first. Decisions get made in rooms you're not in, by people who protect each other's mistakes as readily as their own. It isn't about one person getting away with something — it's a whole layer that answers to itself instead of any standard. The people outside the circle have figured out exactly what that means for them.",
  },
];
