# book-manifest.ts em-dash scan (compile only, no rewrites)

Scope: every `teaser` field in web/lib/book-manifest.ts containing an em-dash.
Confirmed via git history (previous turn) that the Aug 30, 2026 corpus-wide
em-dash pass (batches 1-7, closed at commit bb2e26a with the corpus-wide
count 372 -> 12) only ever touched /book piece .md BODY files. It never
touched this manifest, so every teaser field here still carries its
original em-dash phrasing, untouched since it was written.

59 teaser lines contain at least one em-dash. 4 are already being rewritten
under a separate patch this session (tools/patch_book_manifest_teaser_rewrites.py,
held for review) and are marked below. The remaining 55 are new findings,
not previously flagged anywhere -- review only, nothing reworded.

---

Line 48 | LIB-021 | symptoms-states-and-why-the-distinction-matters | "Symptoms, States, and Why the Distinction Matters for Practice" | 2 em-dash(es)
  teaser: "Organizations present with symptoms. The instrument diagnoses states. Understanding why those are different things — and why treating one without identifying the other produces recurrence — is foundational to how Principal Resolution works.",

Line 75 | LIB-026 | the-problem-they-brought-you-is-not-always-the-problem | "The Problem They Brought You Is Not Always the Problem" | 2 em-dash(es)
  teaser: "Clients arrive with a theory. The diagnostic arrives with a finding. Understanding why those two things diverge — and how to navigate the gap without losing the client — is one of the hardest skills in the work.",

Line 89 | LIB-027 | how-to-tell-if-the-organization-will-actually-change | "How to Tell If the Organization Will Actually Change" | 2 em-dash(es)
  teaser: "Every organization that hires a practitioner believes it is ready to change. Learning to distinguish genuine readiness from its performance — before the engagement is half over — is one of the most valuable skills in the work.",

Line 115 | LIB-030 | earned-effectiveness-conversation-framework | "The Earned Effectiveness Conversation Framework: Sequence, Accuracy, and What the Practice Debrief Reads" | 1 em-dash(es)
  teaser: "Effectiveness in a hard conversation is never assumed and never forced — it is earned through a disciplined sequence. This piece explains the framework and what the four practice debrief dimensions are actually measuring.",

Line 128 | LIB-034 | earned-effectiveness | "Earned Effectiveness" | 1 em-dash(es)
  teaser: "Most practitioners know how to be direct. Fewer know how to be direct in a way that produces change rather than defense. The gap between those two outcomes is not a matter of courage or clarity — it is a matter of sequence.",

Line 141 | FTA-17 | anchor | "Anchor" | 1 em-dash(es)
  teaser: "The Anchor is the rarest finding in the diagnostic system — not because healthy organizations are rare, but because they don't usually go looking. What you built is real, it's valuable, and it's more fragile than it looks.",

Line 154 | LIB-014 | anchor-problem | "The Anchor Problem" | 1 em-dash(es)
  teaser: "Anchor is the state that names what happens when a role, a person, or a structure that once worked has not been updated to match what the organization has become. The drag compounds quietly — and adaptation is not resolution.",

Line 169 | LIB-013 | exit-calculation | "The Exit Calculation" | 1 em-dash(es)
  teaser: "The people who left were not wrong. They were just the first to finish the math. The ones still here are running the same calculation — and they are watching to see what you do next.",

Line 184 | LIB-015 | feedback-nobody-wants-to-say | "The Thing About Feedback Nobody Wants to Say" | 1 em-dash(es)
  teaser: "The corporate feedback apparatus has become extraordinarily sophisticated at creating the appearance of feedback without producing the substance of it. The problem is not the tools — we confused delivery infrastructure with candor.",

Line 198 | LIB-016 | psychological-safety-walked-into-a-meeting | "Psychological Safety Walked Into a Meeting" | 1 em-dash(es)
  teaser: "This is not an argument against psychological safety. It is an argument against what most organizations have done with a genuinely useful idea — deploy it in exactly the environments where it cannot survive.",

Line 227 | LIB-035 | organizational-assessment | "Organizational Assessment" | 1 em-dash(es)
  teaser: "An organizational assessment sends someone in with no position in the organization, no relationships to protect, and no stake in what the findings turn out to be. What it produces is a diagnosis — not a set of recommendations designed to be palatable.",

Line 240 | LIB-036 | organizational-assessment-methodology | "Organizational Assessment: Methodology" | 1 em-dash(es)
  teaser: "Most consulting engagements begin with a hypothesis — and the investigation confirms it. Three principles that correct for this: look without an agenda, report what you actually found, and deliver something specific enough to act on.",

Line 253 | LIB-037 | organizational-assessment-sop | "Organizational Assessment: Engagement SOP" | 2 em-dash(es)
  teaser: "The full engagement sequence for an organizational assessment — five phases, none compressible — with guidance for the circumstances where something in the engagement doesn't fit the expected pattern.",

Line 263 | FTA-03 | succession-planning | "Succession Planning" | 1 em-dash(es)
  teaser: "The difference between a succession plan and a succession wish — and what organizational continuity actually requires you to be able to answer.",

Line 277 | FTA-06 | business-case | "Business Case" | 1 em-dash(es)
  teaser: "Business cases aren't predictions. They're arguments optimized for approval — and the system that rewards the confident version over the accurate one keeps producing the same outcomes.",

Line 291 | FTA-10 | accountability | "Accountability" | 1 em-dash(es)
  teaser: "Accountability doesn't collapse all at once. It erodes through exceptions — each one defensible in isolation, accumulating into a permission structure that everyone can see and no one has addressed.",

Line 305 | FTA-11 | matrix-organization | "Matrix Organization" | 2 em-dash(es)
  teaser: "The matrix doesn't eliminate reporting conflict. It relocates it downward — to the person with the least power to resolve it — and calls that structure.",

Line 319 | FTA-12 | toxic-culture | "Toxic Culture" | 2 em-dash(es)
  teaser: "Toxic cultures don't announce themselves. They teach you the rules the old-fashioned way — by making examples — and become stable long before anyone decides to address them.",

Line 333 | FTA-01 | the-untouchable | "The Untouchable" | 1 em-dash(es)
  teaser: "You know exactly who it is. You've done the math on what it's costing. Leadership has done the math too — and decided the answer is to keep waiting. That calculation is almost always wrong.",

Line 365 | FTA-04 | no-margin-for-error | "No Margin for Error" | 1 em-dash(es)
  teaser: "You already know it's bad. The buffer is gone. The people who could help you fix this are the ones who have already left. The window is real — and it is not going to stay open while you think about it.",

Line 412 | FTA-08 | silosolation | "Silosolation" | 1 em-dash(es)
  teaser: "The organization has fractured into self-contained units that have learned to function without each other. Each team is doing fine on their own. The whole is producing less than the sum of its parts — and the gap between the two is where your best people are slowly burning out.",

Line 428 | FTA-09 | the-broken-compass | "The Broken Compass" | 1 em-dash(es)
  teaser: "The offsite was great. Everyone left feeling aligned. That was three months ago. Since then, the same agreed strategy has been interpreted six different ways — and nobody has acknowledged the contradiction because acknowledging it would require having the conversation that nobody wants to have.",

Line 444 | FTA-13 | decision-paralysis | "Decision Paralysis" | 1 em-dash(es)
  teaser: "The meeting moves. The agenda advances. Everyone nods. You walk out and realize nothing was actually decided. Again. This is not professionalism — it is the language of thoughtfulness deployed in the service of permanent deferral.",

Line 492 | FTA-16 | the-lost-map | "The Lost Map" | 1 em-dash(es)
  teaser: "You are not sure what is wrong. You are sure something is. The signals are present but have not formed a pattern yet. That ambiguity is frustrating — and it is also the most valuable moment to be paying attention.",

Line 508 | LIB-018 | everyone-is-defensive-and-no-one-knows-why | "Everyone Is Defensive and No One Knows Why" | 1 em-dash(es)
  teaser: "You have started preparing for conversations that should take five minutes. Feedback stopped being a tool and became a risk — not because anyone decided that, but through small, accumulated signals that added up to something legible: raising difficult things here costs more than staying quiet.",

Line 522 | LIB-019 | the-room-that-never-pushes-back | "The Room That Never Pushes Back" | 1 em-dash(es)
  teaser: "Your meetings go smoothly. Proposals land well. Nobody raises objections you haven't already thought of. A room that never pushes back is not a room full of people who agree with you — it is a room full of people who have decided that disagreeing with you costs more than it returns.",

Line 536 | LIB-022 | what-the-organization-decided-he-was-worth | "What the Organization Decided He Was Worth" | 1 em-dash(es)
  teaser: "A director. A CEO friendship. An HR function without standing. Two women who followed the process exactly as designed — and found out what the process was built to protect. The complaint worked. That was the problem.",

Line 550 | LIB-023 | the-first-one-out-the-door | "The First One Out the Door" | 2 em-dash(es)
  teaser: "She had been there six years. When she resigned, the executive director said it was a loss but that he understood. What he did not do — what nobody did — was ask her what she had been watching for the last eighteen months.",

Line 564 | LIB-024 | why-your-team-stopped-disagreeing-with-you | "Why Your Team Stopped Disagreeing with You" | 2 em-dash(es)
  teaser: "You put a real question to your senior team — one where you genuinely expected the table to split — and instead you got unanimous agreement. You are left wondering whether you just got consensus or whether you got a performance of it. Those are not the same thing.",

Line 578 | LIB-029 | the-resignation-that-ended-a-department | "The Resignation That Ended a Department" | 1 em-dash(es)
  teaser: "She had been there eleven years — long enough to become the person who keeps an organization functioning in ways nobody thought to measure. The restructuring disrupted something invisible. She raised it in March. She resigned in April. What the transition checklist could not capture left with her.",

Line 592 | LIB-031 | what-ready-didnt-include | "What Ready Didn't Include" | 1 em-dash(es)
  teaser: "She was not excluded. She was simply not included at the moment when inclusion would have changed something. That distinction matters — because the first version of the problem is about intent, and the second is about structure. Intent is easy to defend. Structure is what actually determines what information reaches a decision.",

Line 606 | LIB-032 | one-exception-at-a-time | "One Exception at a Time" | 1 em-dash(es)
  teaser: "The strategy was real. The exceptions were reasonable. By the fourth exception, no one was calling them exceptions anymore. Drift is not a single decision — it is the product of many reasonable decisions that no one ever accounted for together.",

Line 634 | LIB-043 | anatomy-of-resentment | "The Anatomy of Resentment" | 1 em-dash(es)
  teaser: "It starts with a disagreement about the work. The most dangerous shift is when that disagreement becomes a judgment about the person — and the organization learns to route around what it will not name.",

Line 683 | LIB-046 | risk-of-family-friction | "The Risk of Family Friction" | 1 em-dash(es)
  teaser: "The org chart says Vice President. The actual governance document says something different. Any organization running on authority structures built for a different version of itself is paying a lag cost — and the informal structures are always the last thing anyone is willing to name.",

Line 715 | LIB-048 | politeness-tax | "The Politeness Tax" | 1 em-dash(es)
  teaser: "Every person in the organization who holds an opinion that would require uncomfortable delivery is running a calculation. In a high-politeness culture, the cost of uncomfortable delivery is systematically higher — and the role ambiguity it leaves in place compounds with every cycle of growth.",

Line 747 | LIB-050 | crisis-as-catalyst-for-clarity | "Crisis as a Catalyst for Clarity" | 1 em-dash(es)
  teaser: "The organizations that call at this stage have usually been building toward it for longer than they know. What the work looks like when an organization is already in structural collapse — and why the instinct to tighten control is exactly wrong.",

Line 760 | LIB-051 | why-blaming-the-person-almost-never-fixes-the-problem | "Why Blaming the Person Almost Never Fixes the Problem" | 1 em-dash(es)
  teaser: "The impulse to look for a person before looking for a structure is not a leadership failing. It is a well-documented cognitive default — and acting on it without checking first produces a specific kind of waste that organizations pay for, on a delay, in the next hire.",

Line 774 | FTA-18 | the-overloaded-manager | "The Overloaded Manager" | 1 em-dash(es)
  teaser: "Three years ago she managed six people and ran the best team in the building. The org chart absorbed the growth. Nobody decided this on purpose — and now you're looking at her numbers wondering what changed about her, when nothing did.",

Line 787 | FTA-19 | the-unformed-leader | "The Unformed Leader" | 1 em-dash(es)
  teaser: "He was the best individual contributor on the team, so you made him the manager of it. The instincts that made him excellent at the job don't transfer to leading it — and the development you already tried wasn't built for what he actually needed.",

Line 800 | FTA-20 | the-dormant-talent | "The Dormant Talent" | 1 em-dash(es)
  teaser: "Ask him what each person on his team needs to grow and he'll tell you, specifically. He's also done nothing about it in eighteen months. Knowing isn't the same as doing — and a manager who can name the gap and doesn't close it is a more complete failure than one who simply doesn't know.",

Line 813 | FTA-21 | decision-blindness | "Decision Blindness" | 1 em-dash(es)
  teaser: "A complaint came in four months ago. Since then, four individually defensible decisions happened to the person who raised it. Nobody has examined them together — and the correction window that's still open right now is closing on a schedule the organization doesn't control.",

Line 826 | FTA-22 | what-nobody-says | "What Nobody Says" | 1 em-dash(es)
  teaser: "The meeting ends and everyone agreed. Twenty minutes later, in the parking lot, your people are having the real conversation — the one that would have changed the plan if it had happened in the room. Smooth meetings aren't evidence of health. They're often evidence the friction moved somewhere you're not.",

Line 839 | FTA-23 | heard-and-ignored | "Heard & Ignored" | 1 em-dash(es)
  teaser: "She did it the right way — used the actual channel, exactly as the handbook described. Nothing happened. Everyone who watched what happened to her report has drawn the same conclusion: the channel doesn't actually do anything.",

Line 852 | FTA-24 | the-suppression-filter | "The Suppression Filter" | 1 em-dash(es)
  teaser: "You stopped telling your manager the full picture a while ago — not because you're hiding anything, but because you watched what happens to bad news once it enters this organization. By the time it reaches someone who could act, it doesn't look like the thing you actually reported.",

Line 865 | FTA-25 | culture-drift | "Culture Drift" | 1 em-dash(es)
  teaser: "Nobody decided this. No policy changed. The words on the wall are the same words that were there three years ago — but a recent survey found ninety-one percent still believe the values are officially in force while seventy-four percent believe leadership doesn't actually operate by them.",

Line 878 | FTA-26 | the-burned-credibility | "The Burned Credibility" | 1 em-dash(es)
  teaser: "The first broken commitment got an explanation. The second got a more skeptical one. By now, the next announcement about what's going to be different will land in a room that has already decided not to believe it — and credibility doesn't come back through a better pitch.",

Line 891 | FTA-27 | pay-exposure | "Pay Exposure" | 1 em-dash(es)
  teaser: "She knows she's underpaid. Her manager probably does too. The organization has the market data and has deferred the conversation because fixing it is expensive — and when she leaves, the exit interview will say something true and substantively incomplete.",

Line 904 | FTA-28 | built-to-fail | "Built to Fail" | 1 em-dash(es)
  teaser: "You took the job because it looked like the right next step. Six months in, you understand exactly why the last person left. The scope was never realistic — and the organization keeps restaffing the role rather than redesigning it, because restaffing feels like progress and redesigning feels like admitting a mistake.",

Line 917 | FTA-29 | the-paper-tiger | "The Paper Tiger" | 1 em-dash(es) [ALREADY COVERED BY TASK 2]
  teaser: "Everyone already knows this person shouldn't still be on the team. The conversations have happened more than once — in one-on-ones, in hallway asides, in performance reviews that somehow, every cycle, come out fine. The personnel file describes one employee. The conversations describe a completely different one.",

Line 930 | FTA-30 | the-unsolved-problem | "The Unsolved Problem" | 1 em-dash(es) [ALREADY COVERED BY TASK 2]
  teaser: "There was a complaint, a while back. It went through the right process — investigated, addressed, formally closed. The behavior that caused it didn't move on at all. What got resolved was the paperwork. The condition underneath it was never what anyone addressed.",

Line 943 | FTA-31 | the-tolerated-violation | "The Tolerated Violation" | 1 em-dash(es)
  teaser: "There's a practice that people know is wrong. Not unclear or debatable — known, ubiquitous. It continues because the person at the center of it is protected or privileged, and because somewhere along the way it was calculated that the risk of letting it continue was smaller than the discomfort of confronting it.",

Line 956 | FTA-32 | the-unreported-hazard | "The Unreported Hazard" | 1 em-dash(es) [ALREADY COVERED BY TASK 2]
  teaser: "There's a safety concern in this organization right now — physical, psychological, operational. People know about it. It hasn't been formally reported. The silence is a separate finding from the hazard itself, and it's the one that will produce the next hazard nobody reports either.",

Line 969 | FTA-33 | the-unlocked-door | "The Unlocked Door" | 1 em-dash(es)
  teaser: "A known vulnerability exists in this organization. Not hidden, not undiscovered — known, named, and sitting there unaddressed. Not because nobody's seen it. Because the mechanism for closing it has never been used.",

Line 982 | FTA-34 | dueling-narratives | "Dueling Narratives" | 1 em-dash(es)
  teaser: "Two different accounts of what happened are circulating in this organization right now, and both have real authority behind them. The organization isn't operating from one shared understanding of a significant event. It's operating from two, simultaneously — and everyone navigating it has to decide privately which reality they're acting on.",

Line 995 | FTA-35 | narrative-lock | "Narrative Lock" | 1 em-dash(es)
  teaser: "This organization has an official account of itself, and it defends that account against evidence. People who contradict the official narrative, even with solid information, don't get heard. They get handled — because the people holding the narrative have more power than the people who can see it's wrong.",

Line 1021 | FTA-37 | groundhog-day | "Groundhog Day" | 1 em-dash(es)
  teaser: "This problem has been solved before. There was a task force, an initiative, a few months of real visible energy — and then, without any single dramatic reversal, everything drifted back to almost exactly where it started. The initiatives aren't failing. They're succeeding at the wrong target.",

Line 1047 | FTA-39 | invisible-influence-architecture | "Invisible Influence Architecture" | 1 em-dash(es)
  teaser: "The org chart says who has authority. It doesn't say who actually decides anything — and by now you've stopped checking it.",

Line 1099 | FTA-43 | the-exposed | "The Exposed" | 1 em-dash(es)
  teaser: "There is no functioning HR here. There are employees, obligations, and risk — and nobody whose job it is to manage any of it.",

Line 1243 | LIB-052 | what-not-to-document | "What NOT to Document" | 1 em-dash(es) [ALREADY COVERED BY TASK 2]
  teaser: "Most organizations document defensively and starve the documentation that actually protects people — the performance conversation, the commitment, the disagreement. The paper that creates real risk isn't the paper you're missing. It's the paper you didn't need.",

