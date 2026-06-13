// PRV3 Self-Selection Interface — Content Data
// web/data/taxonomy.ts
//
// Authoritative source for all self-selection surface content.
// DO NOT import from engine/ — this file has no dependencies outside web/.
// Clinical boundary is enforced here: no dimensional weights, no scoring
// parameters, no severity tiers reach this surface.
//
// Content locked Session 34. Architecture locked Session 35.
// MOB v4.1 governs.

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface State {
  id: string;
  name: string;
  signatureId: string;
  secondarySignatureIds?: string[];
  description: string;
}

export interface Signature {
  id: string;
  name: string;
  stateIds: string[];
  description: string;
  coexistenceInterpretation: string;
}

export interface UICopy {
  phase1Instruction: string;
  transitionTrigger: string;
  seeWhatThisMeans: string;
  singleStateEdgeCase: string;
  phase4Copy: string;
  diagnosticCTA: string;
  conversationCTA: string;
  assemblyTitle: string;
  assemblyEmpty: string;
  collapsedCountSuffix: string;
  phase3CTALabel: string;
}

// ---------------------------------------------------------------------------
// States — 47 total
// ---------------------------------------------------------------------------
// Register: individual lived experience first, organizational cost at close.
// signatureId = primary signature.
// secondarySignatureIds = additional signatures this state appears in.

export const states: State[] = [
  // APTITUDE — 6 states
  {
    id: "the_unformed_leader",
    name: "The Unformed Leader",
    signatureId: "stunted_growth",
    description:
      "Your manager means well. That much is clear. But nobody on the team knows what's expected of them, feedback is either absent or arrives as a surprise, and the people who were here before you keep leaving. You've stopped waiting for direction. You've started working around it. The organization is paying to replace people it didn't have to lose, and the ones who stay have quietly lowered what they expect from this place.",
  },
  {
    id: "the_overloaded_manager",
    name: "The Overloaded Manager",
    signatureId: "stunted_growth",
    description:
      "Your manager was good at this job before the team doubled and the scope expanded. Now your one-on-ones are status updates, development conversations don't happen, and when you need a decision you wait. They're not checked out — they're drowning. The organization redesigned the role without redesigning the resources, and the team is absorbing the cost of that mistake.",
  },
  {
    id: "the_dormant_talent",
    name: "The Dormant Talent",
    signatureId: "stunted_growth",
    description:
      "Your manager can tell you exactly what you need to grow. They just don't do anything about it. The team's development has stalled while the manager's visibility keeps climbing. People have noticed the pattern. The ones with options are starting to act on it.",
  },
  {
    id: "built_to_fail",
    name: "Built to Fail",
    signatureId: "stunted_growth",
    description:
      "You took this job because it looked like the right next step. Six months in you understand why the last person left. The scope is impossible, the resources aren't there, and when you raise it you're told to figure it out. The person before you was told the same thing. The organization keeps hiring strong people into a broken structure and writing each departure off as a hiring mistake.",
  },
  {
    id: "the_undefined_role",
    name: "The Undefined Role",
    signatureId: "stunted_growth",
    description:
      "You and your manager don't agree on what your job actually is. Not in a conversation you've had — in the daily reality of what lands on your desk, what gets escalated, what falls through. Work is duplicated in some places and orphaned in others. The organization is paying for a role that isn't doing what anyone thinks it's doing because nobody has said clearly what that is.",
  },
  {
    id: "the_paper_tiger",
    name: "The Paper Tiger",
    signatureId: "compounding_risks",
    description:
      "Everyone knows this person shouldn't still be here. The conversations have happened — in one-on-ones, in hallways, in performance reviews that somehow came out fine. The file tells a different story than the one the manager has been telling. When the moment comes to act, the organization discovers it has been managing one employee on paper and a completely different one in practice.",
  },

  // AUTHORITY — 18 states
  {
    id: "the_founders_grip",
    name: "The Founder's Grip",
    signatureId: "leadership_bottleneck",
    description:
      "Nothing significant moves here without one person's approval. That person is overextended, hard to reach, and making decisions on information that's weeks old by the time it gets to them. You've learned to work around the bottleneck or wait. The senior people who couldn't live with either option have already left.",
  },
  {
    id: "the_exposed",
    name: "The Exposed",
    signatureId: "compounding_risks",
    description:
      "There is no functioning HR in this organization. There are employees, obligations, and risk — and nobody whose actual job it is to manage any of it. People with concerns have nowhere to bring them. The organization isn't between HR leaders. It's accumulating liability on a timeline it doesn't know is running.",
  },
  {
    id: "the_uninitiated",
    name: "The Uninitiated",
    signatureId: "compounding_risks",
    description:
      "Something consequential is coming — a merger, a regulatory event, a restructuring — and the organization has never done this before. The people leading it are capable and underprepared. They don't know what they don't know, and the cost of that gap tends to arrive all at once.",
  },
  {
    id: "leadership_continuity_risk",
    name: "Leadership Continuity Risk",
    signatureId: "leadership_bottleneck",
    secondarySignatureIds: ["stunted_growth"],
    description:
      "Two or three people in this organization carry the relationships, the knowledge, and the institutional memory that keep everything functional. There is no plan for what happens when any of them leave. Everyone knows this is a problem. It hasn't become a priority because those people haven't left yet.",
  },
  {
    id: "hr_capture",
    name: "HR Capture",
    signatureId: "leadership_bottleneck",
    description:
      "HR reports to the person it's supposed to provide independent oversight of. If you have a concern about that person, you already know HR isn't where you bring it. The function exists. It cannot do its job from where it sits, and the people who most need it have figured that out.",
  },
  {
    id: "decision_paralysis",
    name: "Decision Paralysis",
    signatureId: "leadership_bottleneck",
    description:
      "Things get decided in meetings and relitigated in the hallway. You've stopped counting on a decision holding until it actually happens. The cost isn't in any single reversal — it's in everything the organization isn't doing while it cycles through the same conversations without landing.",
  },
  {
    id: "the_policy_lag",
    name: "The Policy Lag",
    signatureId: "compounding_risks",
    description:
      "The handbook hasn't been touched in years. The law has. People are operating under policies that were compliant when written and aren't anymore. Nobody has noticed because nothing has gone wrong yet. The organization's exposure is real and invisible until it suddenly isn't.",
  },
  {
    id: "the_unexamined_algorithm",
    name: "The Unexamined Algorithm",
    signatureId: "compounding_risks",
    description:
      "AI tools are making or influencing employment decisions here — hiring, performance, compensation. Nobody has looked carefully at the criteria they're applying or whether those criteria hold up legally. The efficiency is real. The audit hasn't happened. The two facts are going to meet eventually.",
  },
  {
    id: "heard_and_ignored",
    name: "Heard & Ignored",
    signatureId: "compounding_risks",
    description:
      "You reported something. You did it the right way, through the right channel, because you believed it would matter. It didn't. The problem is still present. You're still in the room with it. Everyone who watched what happened to your report has drawn the obvious conclusion about whether the channel is worth using.",
  },
  {
    id: "the_tolerated_violation",
    name: "The Tolerated Violation",
    signatureId: "compounding_risks",
    description:
      "There is a practice in this organization that people know is wrong. It has been known for a while. It continues because the person at the center of it is protected, because addressing it is uncomfortable, or because someone made a quiet calculation that the risk was manageable. Each day it continues that calculation gets harder to defend.",
  },
  {
    id: "dueling_narratives",
    name: "Dueling Narratives",
    signatureId: "compounding_risks",
    description:
      "Two versions of what happened are circulating and both have organizational authority behind them. People have heard both. They've done the math on which one to believe. The inconsistency is a liability in any proceeding that involves discovery — and a daily tax on the credibility of everyone defending the official version.",
  },
  {
    id: "the_unsolved_problem",
    name: "The Unsolved Problem",
    signatureId: "compounding_risks",
    description:
      "There was a complaint. It was resolved — settled, closed, documented. The behavior that produced it was never addressed. The person affected moved on. The condition didn't. The organization's prior resolution will be exhibit A when the next one surfaces.",
  },
  {
    id: "transition_paralysis",
    name: "Transition Paralysis",
    signatureId: "leadership_bottleneck",
    description:
      "A leadership change is underway and the organization has stalled around it. People are waiting to see who lands where before they commit to anything. Decisions are being deferred. Initiatives are on hold. The work is accumulating behind the uncertainty while everyone manages the transition instead of doing their job.",
  },
  {
    id: "paper_shield",
    name: "Paper Shield",
    signatureId: "compounding_risks",
    description:
      "The policies are current. The training is documented. The acknowledgment forms are signed. None of it reflects what actually happens here. The compliance infrastructure is real on paper and largely decorative in practice. When something goes wrong the paper trail will describe an organization that doesn't exist.",
  },
  {
    id: "the_lost_map",
    name: "The Lost Map",
    signatureId: "information_blindness",
    description:
      "The information you need to do your job exists somewhere in this organization. It lives in someone's inbox, someone's memory, a system that hasn't been updated, a folder nobody can find. You make decisions without it because finding it takes longer than making the call. The organization is operating on incomplete pictures because nobody has built the architecture to make the right information findable.",
  },
  {
    id: "invisible_influence_architecture",
    name: "Invisible Influence Architecture",
    signatureId: "leadership_bottleneck",
    description:
      "The org chart shows who has authority. It doesn't show who actually shapes decisions. There are people in this organization whose influence far exceeds their title and others whose title suggests authority they don't have. The real decision-making structure and the official one have separated. Outcomes that nobody can officially explain keep happening anyway.",
  },
  {
    id: "pay_exposure",
    name: "Pay Exposure",
    signatureId: "compounding_risks",
    description:
      "You know you're underpaid. Your manager probably knows too. The organization has looked at the market data and deferred the conversation because fixing it is expensive. The departures it's producing are being explained as career moves, culture fit, better opportunities. The real reason isn't in any exit interview.",
  },
  {
    id: "the_pay_fog",
    name: "The Pay Fog",
    signatureId: "compounding_risks",
    description:
      "You've compared notes. The numbers don't make sense. Similar roles, different pay, no framework anyone can explain or defend. It wasn't a problem when the numbers were private. Pay transparency requirements are making the incoherence visible in ways the organization isn't prepared for.",
  },

  // ALLIANCE — 6 states
  {
    id: "the_fracture",
    name: "The Fracture",
    signatureId: "leadership_bottleneck",
    description:
      "Two leaders at the top of this organization are in open conflict and everyone knows it. You navigate meetings differently depending on who's in the room. Decisions require political calculation rather than judgment. People have chosen sides because the leaders already have. The work that requires both of them to function is the work that isn't getting done.",
  },
  {
    id: "the_second_close",
    name: "The Second Close",
    signatureId: "stunted_growth",
    description:
      "The acquisition closed. The integration didn't. You're working inside two organizations that operate under the same name but run on different systems, different assumptions, and different ideas about who's actually in charge. The deal thesis assumed the hard part was the transaction. The people living inside it know otherwise.",
  },
  {
    id: "silosolation",
    name: "Silosolation",
    signatureId: "information_blindness",
    description:
      "Your team is hitting its targets. The work that requires another team to hit theirs isn't happening. The problem gets explained as a communication issue, a personality conflict, a specific person who's difficult to work with. It's structural. The same failures keep appearing regardless of who's involved because nobody has addressed what's actually producing them.",
  },
  {
    id: "the_suppression_filter",
    name: "The Suppression Filter",
    signatureId: "information_blindness",
    description:
      "You've stopped telling your manager the full picture. Not because you're hiding anything — because you've watched what happens to bad news in this organization. It gets softened on the way up. By the time it reaches someone who could act on it, it doesn't look like bad news anymore. So you edit. Everyone does. Leadership is making decisions on a version of reality that nobody below them actually recognizes.",
  },
  {
    id: "the_arbitrary_standard",
    name: "The Arbitrary Standard",
    signatureId: "compounding_risks",
    description:
      "The rules don't apply the same way to everyone and people have noticed. Someone got away with something that someone else was disciplined for. The inconsistency has a pattern. People have decoded it. The organization's ability to hold anyone accountable depends on a fairness that the workforce no longer believes exists.",
  },
  {
    id: "decision_blindness",
    name: "Decision Blindness",
    signatureId: "compounding_risks",
    description:
      "A consequential decision was made without the people who should have been in the room. Legal found out after. HR heard it secondhand. The coordination failure was invisible until something went wrong — and now everyone is looking at who knew what and when, and the answer is uncomfortable.",
  },

  // ATTITUDE — 17 states
  {
    id: "the_untouchable",
    name: "The Untouchable",
    signatureId: "information_blindness",
    description:
      "There is a specific person in this organization who operates by different rules than everyone else. Complaints have been made. Nothing has changed. The rest of the organization has drawn the obvious conclusion and adjusted accordingly — not just about this person, but about whether the rules mean anything here at all.",
  },
  {
    id: "what_nobody_says",
    name: "What Nobody Says",
    signatureId: "information_blindness",
    description:
      "Everyone knows. Nobody says it. The real conversation happens in the parking lot, in the group chat, in the five minutes after the meeting ends. In the meeting everyone says something different. The gap between those two conversations is where this organization actually lives — and where its worst decisions get made, because the people making them don't have the real information.",
  },
  {
    id: "leadership_deafness",
    name: "Leadership Deafness",
    signatureId: "information_blindness",
    description:
      "Leadership here genuinely believes they have an accurate picture of what's happening in this organization. They don't. Every layer between them and the work has learned to translate bad news into something easier to deliver. The filtered version is consistent enough that leadership has stopped questioning it. They are managing a picture of the organization, not the organization itself.",
  },
  {
    id: "the_diversity_ceiling",
    name: "The Diversity Ceiling",
    signatureId: "information_blindness",
    description:
      "The organization talks about inclusion. The promotion and retention patterns tell a different story. The people who have been passed over know why. The explanations offered don't hold up against the data. The gap between what the organization says it values and what it actually rewards is visible to everyone it affects — and it's shaping decisions about who stays.",
  },
  {
    id: "culture_drift",
    name: "Culture Drift",
    signatureId: "culture_erosion",
    description:
      "Something has changed here and nobody made a decision to change it. The organization that exists today isn't the one people joined. The things that made it distinctive — the candor, the pace, the sense that the work meant something — have eroded without anyone being able to point to when it started. People who've been here long enough feel it. They don't always say it.",
  },
  {
    id: "identity_erosion",
    name: "Identity Erosion",
    signatureId: "culture_erosion",
    description:
      "The people who most defined what this organization stood for are leaving. Not all at once — one at a time, with individual explanations that each make sense on their own. The cumulative pattern is something different. The culture isn't drifting. It's being evacuated by the people who carried it, and the organization hasn't named what's happening yet.",
  },
  {
    id: "the_culture_that_wasnt",
    name: "The Culture That Wasn't",
    signatureId: "culture_erosion",
    description:
      "The values are on the wall. The culture described in the all-hands is not the culture experienced in the building. New hires figure this out within their first ninety days. Tenured employees stopped expecting alignment a long time ago. Maintaining the official story now requires active effort, and the people being asked to maintain it are running out of reasons to bother.",
  },
  {
    id: "the_burned_credibility",
    name: "The Burned Credibility",
    signatureId: "culture_erosion",
    description:
      "Leadership made commitments it didn't keep. The first time it was explained. The second time it was rationalized. By now the workforce has stopped listening to announcements about what's going to be different. The credibility required to lead change has been spent. Initiatives that need people to believe in them are launching into an organization that has already decided not to.",
  },
  {
    id: "invisible_burnout",
    name: "Invisible Burnout",
    signatureId: "stunted_growth",
    description:
      "The people doing the most critical work are running out of capacity and not saying so. They're not saying so because this organization has taught them that flagging it looks like weakness. They will leave before they complain. The warning signs are there for anyone looking. Most people aren't looking until the resignation letter arrives.",
  },
  {
    id: "the_basement_standard",
    name: "The Basement Standard",
    signatureId: "culture_erosion",
    description:
      "Underperformance isn't addressed here. Not one person's — the organization's tolerance for it as a pattern. The people who perform know exactly what they could get away with if they stopped. Some of them are starting to do the math. The ones who care most about standards are the ones most likely to leave rather than lower them.",
  },
  {
    id: "the_inside_track",
    name: "The Inside Track",
    signatureId: "culture_erosion",
    description:
      "Performance isn't the primary criterion for advancement here and people know it. The people who get ahead share characteristics that aren't in any job posting. The people who don't have those characteristics have figured out the real criteria and made their own calculations about whether to keep trying or start looking.",
  },
  {
    id: "narrative_lock",
    name: "Narrative Lock",
    signatureId: "culture_erosion",
    secondarySignatureIds: ["information_blindness"],
    description:
      "The organization has an official account of itself and defends it against evidence. People who contradict the official story — even with data — get managed rather than heard. The people holding the narrative have more organizational power than the people who know it's wrong. The cost is in every decision made to protect the story instead of address the reality.",
  },
  {
    id: "groundhog_day",
    name: "Groundhog Day",
    signatureId: "information_blindness",
    description:
      "This problem has been solved before. The task force ran. The initiative launched. Things improved and then returned to exactly where they were. You've stopped getting excited about the next intervention because you've seen how it ends. The organization keeps treating what's visible and leaving intact what's generating it. Each failed solution makes the next one harder to believe in.",
  },
  {
    id: "the_wrong_reward",
    name: "The Wrong Reward",
    signatureId: "culture_erosion",
    description:
      "The behaviors that get rewarded here and the behaviors leadership says it values are not the same. People have run the experiment. They know which set actually matters for advancement, for recognition, for survival. They're optimizing for the real reward system — not the stated one — and the organization is getting exactly the behavior it's paying for.",
  },
  {
    id: "the_unreported_hazard",
    name: "The Unreported Hazard",
    signatureId: "compounding_risks",
    description:
      "There is a safety concern in this organization — physical, psychological, or operational — that hasn't been formally reported. People know about it. The reason it hasn't been reported is itself a finding about what this organization has taught people to expect when they raise concerns.",
  },
  {
    id: "the_unlocked_door",
    name: "The Unlocked Door",
    signatureId: "compounding_risks",
    description:
      "A known vulnerability exists and hasn't been closed. Not because nobody has seen it — because the mechanism for addressing it hasn't been used. The organization is aware. It hasn't acted. When something goes wrong, the awareness will matter more than the inaction was ever worth.",
  },
  {
    id: "the_broken_compass",
    name: "The Broken Compass",
    signatureId: "leadership_bottleneck",
    description:
      "You've been in the meeting where it was diagnosed. You've read the report. You've heard the leadership team agree that something needs to change. That was eighteen months ago. The people with the most options — the ones the organization can least afford to lose — have stopped waiting for the next conversation to be different.",
  },
];

// ---------------------------------------------------------------------------
// Signatures — 5 total
// ---------------------------------------------------------------------------
// stateIds lists every state that appears in this signature.
// description = the opening paragraph (visitor recognition).
// coexistenceInterpretation = what the co-occurrence means together.

export const signatures: Signature[] = [
  {
    id: "leadership_bottleneck",
    name: "Leadership Bottleneck",
    stateIds: [
      "the_founders_grip",
      "decision_paralysis",
      "leadership_continuity_risk",
      "transition_paralysis",
      "the_broken_compass",
      "invisible_influence_architecture",
      "hr_capture",
      "the_fracture",
    ],
    description:
      "You know what needs to happen. Getting there requires navigating a set of approvals, relationships, and informal power structures that aren't on any org chart. Decisions that should take days take weeks. The people with the authority to move things forward are either unreachable, uncommitted, or operating without the independence their role requires. You've learned to work around the bottleneck because working through it stopped being viable. The senior people who couldn't live with that have already left. The organization isn't frozen — it's moving, just not in the direction anyone chose.",
    coexistenceInterpretation:
      "What makes this pattern distinct is not any single failure of leadership — it's what happens when several of them are present at once. Concentrated authority produces a bottleneck. Paralysis keeps decisions from moving through it. Compromised oversight means nobody is positioned to name what's happening. Invisible influence means the official structure and the real one have separated far enough that fixing the official one won't solve anything. These conditions don't just coexist — they protect each other. The organization can address any one of them and find the others still in place, still producing the same results. That's the signature. That's what has to be read whole.",
  },
  {
    id: "culture_erosion",
    name: "Culture Erosion",
    stateIds: [
      "culture_drift",
      "identity_erosion",
      "the_culture_that_wasnt",
      "the_burned_credibility",
      "the_wrong_reward",
      "the_basement_standard",
      "the_inside_track",
      "narrative_lock",
    ],
    description:
      "You remember when this place felt different. The people who've been here long enough know what changed — not the moment it changed, but the accumulation of small decisions that added up to something large. The values are still on the wall. The all-hands still describes an organization that doesn't quite match the one people experience every day. New hires figure out the gap in their first ninety days. Tenured employees stopped expecting it to close. The ones who cared most about what this place stood for are the ones leaving first.",
    coexistenceInterpretation:
      "What makes this pattern dangerous is the sequence it follows. The culture drifts first — gradually, without a single decision anyone can point to. Then the reward system starts reflecting the new reality instead of the stated values, and the people paying attention adjust their behavior accordingly. Then the official story stops matching the lived experience, and maintaining it requires active effort from the people least inclined to provide it. Then credibility burns — not in one moment but across the accumulated weight of commitments that didn't hold. By the time the organization recognizes what's happened, the people most capable of reversing it have already made their decision. Culture erosion at this stage isn't a morale problem. It's a structural condition, and it has a direction.",
  },
  {
    id: "stunted_growth",
    name: "Stunted Growth",
    stateIds: [
      "the_unformed_leader",
      "the_overloaded_manager",
      "the_dormant_talent",
      "built_to_fail",
      "the_undefined_role",
      "leadership_continuity_risk",
      "invisible_burnout",
      "the_second_close",
    ],
    description:
      "You're not being developed here. You're not sure your manager could tell you what your next step looks like, or whether they've thought about it. The people above you are either too stretched to invest in anyone else's growth, too disengaged to bother, or operating inside roles that were never designed to be survivable. You're doing good work in a structure that isn't built to recognize or advance it. The people who figured that out before you did have already moved on.",
    coexistenceInterpretation:
      "What makes this signature distinct from a general talent problem is where the failure is actually located. It isn't in the people — it's distributed across the conditions surrounding them. The manager who isn't developing anyone may be genuinely incapable, structurally prevented, or simply disengaged — and those three conditions look identical from where the team sits but require completely different responses. When they appear together, the organization is losing on every front at once: the pipeline isn't being built, the people currently in leadership are operating below capacity, the roles designed to carry growth aren't structured to do it, and the people absorbing all of it are burning out quietly rather than saying so. The organization reads this as a talent problem and goes looking for better people. The conditions that produced it are still in place when they arrive.",
  },
  {
    id: "compounding_risks",
    name: "Compounding Risks",
    stateIds: [
      "the_exposed",
      "the_uninitiated",
      "the_paper_tiger",
      "the_tolerated_violation",
      "heard_and_ignored",
      "the_unsolved_problem",
      "the_unexamined_algorithm",
      "pay_exposure",
      "the_pay_fog",
      "the_policy_lag",
      "dueling_narratives",
      "the_unreported_hazard",
      "the_unlocked_door",
      "decision_blindness",
      "the_arbitrary_standard",
      "paper_shield",
    ],
    description:
      "You've raised concerns before. Some of them went somewhere. Others landed in a process that looked responsive and produced nothing. The organization has policies, documentation, training records, acknowledgment forms — the infrastructure of compliance. What it doesn't always have is the practice that infrastructure is supposed to reflect. Meanwhile the gaps are accumulating: the report that wasn't acted on, the practice everyone knows is wrong, the policy that hasn't been updated, the algorithm nobody has audited. Each one is manageable in isolation. Together they represent an exposure the organization hasn't fully mapped.",
    coexistenceInterpretation:
      "What changes when these conditions appear together is not the size of any individual risk — it's the story they tell in combination. A single compliance failure is an incident. A pattern of them across multiple domains, over time, with documentation that contradicts the witness accounts, is evidence of a culture of non-compliance — and that is what plaintiffs' attorneys, regulators, and journalists are trained to find. The organization isn't being evaluated on whether it made mistakes. It's being evaluated on whether it knew, whether it acted, and whether the gap between those two things was a choice. When this signature is present, that gap exists in multiple places simultaneously. The question isn't whether exposure will surface. It's which one surfaces first and what it pulls behind it.",
  },
  {
    id: "information_blindness",
    name: "Information Blindness",
    stateIds: [
      "leadership_deafness",
      "the_suppression_filter",
      "what_nobody_says",
      "narrative_lock",
      "the_lost_map",
      "groundhog_day",
      "the_diversity_ceiling",
      "the_untouchable",
      "silosolation",
    ],
    description:
      "Leadership here believes they have an accurate picture of what's happening in this organization. The people doing the work know they don't. The real information — about what's broken, who's struggling, what the unofficial rules actually are — travels laterally, in private, through channels leadership doesn't have access to. What reaches the top has been edited for safety at every level it passed through. The decisions being made at the top are being made on a version of reality that the people closest to the work don't recognize.",
    coexistenceInterpretation:
      "What makes this signature so costly is that it's self-concealing. The same conditions that prevent accurate information from reaching leadership also prevent leadership from knowing that's what's happening. The suppression filter edits the signal. The official narrative explains away what gets through. The untouchable person at the center of half the real conversations is never in the ones leadership hears. The problems that recur do so because the diagnosis required to stop them never forms — not because the organization lacks smart people, but because the information those people would need is trapped below the level where decisions get made. The organization keeps solving the wrong problem with full confidence, because the right problem has never been safely speakable. That's not a communication failure. That's a closed system — and closed systems don't correct themselves from the inside.",
  },
];

// ---------------------------------------------------------------------------
// Static interpretations — keyed by signature id
// ---------------------------------------------------------------------------
// Used when ≥70% of selected states belong to a single signature (clean match).
// Source: signature.coexistenceInterpretation above.
// Provided here as a convenience lookup.

export const staticInterpretations: Record<string, string> = Object.fromEntries(
  signatures.map((s) => [s.id, s.coexistenceInterpretation])
);

// ---------------------------------------------------------------------------
// UI Copy — all static strings
// ---------------------------------------------------------------------------

export const uiCopy: UICopy = {
  phase1Instruction:
    "Start here. Read each one. Select the ones that sound familiar.",
  transitionTrigger: "Let's take a closer look.",
  seeWhatThisMeans: "See what this means.",
  singleStateEdgeCase:
    "You've identified one condition. The diagnostic can tell you more about what's beneath it.",
  phase4Copy:
    "Here's what comes next. The diagnostic goes deeper — it sees what self-report can't. Or, if you've seen enough, start a conversation.",
  diagnosticCTA: "Take the full diagnostic",
  conversationCTA: "Start a conversation",
  assemblyTitle: "What you're carrying",
  assemblyEmpty: "Select conditions above to build your picture.",
  collapsedCountSuffix: "conditions inside",
  phase3CTALabel: "See what this means.",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Returns all states belonging to a given signature (primary or secondary). */
export function getStatesForSignature(signatureId: string): State[] {
  return states.filter(
    (s) =>
      s.signatureId === signatureId ||
      s.secondarySignatureIds?.includes(signatureId)
  );
}

/** Returns the signature for a given state id. */
export function getSignatureForState(stateId: string): Signature | undefined {
  const state = states.find((s) => s.id === stateId);
  if (!state) return undefined;
  return signatures.find((sig) => sig.id === state.signatureId);
}

/**
 * Given a set of selected state ids, returns the dominant signature id
 * and the percentage of states belonging to it.
 * Used to determine static vs. dynamic interpretation path.
 */
export function getDominantSignature(selectedStateIds: string[]): {
  signatureId: string;
  percentage: number;
} | null {
  if (selectedStateIds.length === 0) return null;

  const counts: Record<string, number> = {};
  for (const id of selectedStateIds) {
    const state = states.find((s) => s.id === id);
    if (state) {
      counts[state.signatureId] = (counts[state.signatureId] ?? 0) + 1;
    }
  }

  const dominant = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  return {
    signatureId: dominant[0],
    percentage: dominant[1] / selectedStateIds.length,
  };
}
