# Benchmark 01: blind-persona validation set (pre-registration)

Authored by Claude.ai from on-screen question text only (`prv3-experiment-01-instrument.md`). Claude.ai has seen state names and their published descriptions, never dimensional weights, state targets or severity flags. The personas are deliberately textbook cases: each has one dominant problem described plainly. If the engine cannot find a textbook case, that is stronger evidence than failing on an ambiguous one.

Date: from the git commit timestamp of this file.

## Purpose

Calibration (171/175) builds answers from each state's own weights, so it measures internal consistency, not validity. This set measures validity: whether a respondent-authored answer path puts the respondent's real problem near the top. It is also the yardstick against which any ranking fix is judged.

## Design

- 6 personas x 2 framings = 12 production runs, each tagged `x-prv3-test-run: 1`.
- **Cautious** framing: the answers a careful executive gives about real facts.
- **Strong** framing: the same facts, answered with the more candid adjacent option where one exists. Nothing new is invented in the strong framing.
- Narrative step: **skipped** in every run (the on-screen "Skip this" path), so the result reflects the questions alone. P1 can then be compared with Experiment 01, which had a narrative.

## Answer rules

1. Any core question not listed for a persona takes the DEFAULT answer.
2. Where a persona lists `X/Y`, X is cautious and Y is strong. A single letter applies to both.
3. Duration-type follow-ups (SEVER-06, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29) take the persona's duration letter.
4. Other follow-ups (Q28, Q45, SEVER-01, 02, 03, 05, 07, 08, 10, 11, 12, 13, 30, 31, 32) take the persona's listed answer. The DEFAULT answer for SEVER-05 is C.
5. Distinguishers (DIST-*) take the persona's listed answer.
6. Any served question or option not covered by these rules: HALT and report. Do not guess.

## DEFAULT core answers

Q01 A, Q02 A, Q04 A, Q05 A, Q06 [E], Q07 A, Q08 A, Q09 A, Q10 B, Q11 A, Q12 A, Q13 E, Q14 A, Q15 A, Q16 E, Q17 A, Q18 A, Q19 A, Q20 B, Q21 A, Q22 B, Q23 A, Q24 A, Q25 A, Q26 A, Q27B A, Q30 A, Q32 A, Q33 B, Q35 A, Q36 A, Q37 A, Q38 A, Q39 A, Q40 A, Q41 A, Q42 A, Q43 A, Q44 A, Q46 A, Q47 A, Q48 A, Q49 A, Q50 A, Q51 A.
Q03B and Q34 are always set per persona.

---

## P1: Granite Ridge Components (Experiment 01 persona, rerun)

- **Target:** the_unformed_leader. **Also report:** the_unreported_hazard.
- **Intake:** as Experiment 01.
- **Cautious:** the Experiment 01 answer map exactly, including its follow-up and distinguisher answers.
- **Strong overrides:** Q04 D, Q12 D, Q18 C, Q45 D.
- **Duration letter:** B.

## P2: Halvorsen & Pike LLP (professional services)

- **Facts:** 120 employees. A rainmaker partner (about 35% of revenue) berates associates, ignores timekeeping and policy, and is exempt from the standards everyone else is held to. Two associates left citing him. The issue is over three years old, and leadership will not act.
- **Target:** the_untouchable. **Lenient:** the_arbitrary_standard.
- **Intake:** 120 | Professional Services | Privately held professional leadership | C-suite | 3-5 years | 6-15 | NY | "A known performance or conduct issue involving a specific individual remains unresolved."
- **Core:** Q02 B, Q03B A, Q04 B/D, Q05 B/C, Q07 B, Q09 C, Q11 B/D, Q12 B/D, Q23 B/D, Q24 B, Q34 A, Q35 D, Q36 B/D, Q44 D, Q46 C/D, Q50 B/C, Q51 A/B.
- **Follow-ups:** Q45 C/D. SEVER-05 C.
- **Distinguishers:** CM-01 B, CM-02 B, CC-01 C, CC-02 C.
- **Duration letter:** B.

## P3: Brightwater Family Health (clinic network)

- **Facts:** 280 employees. The network grew about 40% in two years through new sites. Practice managers' spans doubled with no added administrative support. They raised it twice and nothing changed. Development conversations have become status updates. The managers themselves are competent.
- **Target:** the_overloaded_manager. **Lenient:** compression_crisis.
- **Intake:** 280 | Healthcare & Life Sciences | Privately held professional leadership | HR leader | 3-5 years | 1-5 | CT | "Rapid growth 25%+".
- **Core:** Q03B B, Q05 B, Q07 A/B, Q12 C, Q20 B, Q21 B/C, Q24 B/D, Q25 B, Q26 B, Q27B A/B, Q30 C, Q34 B, Q35 B, Q39 D, Q42 B/C, Q44 B/D, Q47 B/D.
- **Follow-ups:** Q45 B. SEVER-03 B. SEVER-10 B.
- **Distinguishers:** CM-01 A, CM-02 C, CC-01 D, CC-02 D.
- **Duration letter:** B.

## P4: Lakeshore Learning Alliance (education nonprofit)

- **Facts:** 210 employees. A consensus culture spans the leadership team and board committees. Decisions get revisited and sit for months. Nobody refuses to decide, but nothing produces a final call. The direction blurs while choices wait.
- **Target:** decision_paralysis. **Lenient:** planning_authority_gap.
- **Intake:** 210 | Nonprofit & Education | Nonprofit | C-suite | 1-3 years | 6-15 | IL | "None".
- **Core:** Q01 C/D, Q02 B, Q03B B, Q09 B, Q13 C, Q17 C/E, Q20 B/D, Q21 B/D, Q26 B, Q32 B, Q34 B, Q42 C/D, Q44 B/D, Q51 B.
- **Follow-ups:** Q45 C. SEVER-02 C. SEVER-03 D.
- **Distinguishers:** CM-01 D, CM-02 D, CC-01 D, CC-02 D.
- **Duration letter:** B.

## P5: Northloop Analytics (venture-backed software)

- **Facts:** 90 employees. Compensation bands were set three years ago and the market has moved past them. Pay is internally consistent but behind the market. The company keeps losing engineers to better offers, and exit interviews say pay.
- **Target:** pay_exposure. **Lenient:** none.
- **Intake:** 90 | Technology | PE or VC-backed | HR leader | 1-3 years | 1-5 | CA | "None".
- **Core:** Q02 B, Q03B A, Q07 C, Q14 C, Q23 B/D, Q24 B/C, Q34 B, Q38 B/C, Q44 B/D, Q49 C/D.
- **Follow-ups:** Q45 B. SEVER-05 D.
- **Distinguishers:** CM-01 D, CM-02 D, CC-01 C, CC-02 D.
- **Duration letter:** B.

## P6: Coastline Hospitality Group (restaurants and hotels)

- **Facts:** 450 employees. Recruiting sells "family, growth, flexibility." New hires find rigid scheduling and little room to advance. Most departures happen within 90 days, and exit interviews say "not what I was told."
- **Target:** the_culture_that_wasnt. **Lenient:** dueling_narratives.
- **Intake:** 450 | Retail & Hospitality | Founder-led | C-suite | 1-3 years | 6-15 | FL | "Rapid growth 25%+".
- **Core:** Q03B B, Q07 D, Q11 B, Q15 B/D, Q19 B/C, Q27B E, Q34 C, Q44 B/C.
- **Follow-ups:** Q45 B.
- **Distinguishers:** CM-01 D, CM-02 D, CC-01 A, CC-02 A.
- **Duration letter:** B.

---

## Measures (per run, computed by script from the saved result JSON)

- target rank and target score
- top-3 hit and top-5 hit
- lenient top-3 hit (target or lenient state)
- qualifying count
- spread from rank 1 to the last qualifying rank, as % of the top score
- distinct score values
- margin from rank 1 to rank 2
- rank-1 tie (yes/no)
- lead condition tier, and the highest tier in the top 5
- legal total
- executive summary text, verbatim, plus a label NAMES / DOES NOT NAME for the persona's dominant problem (Claude Code labels, Claude.ai checks)

## Hypotheses (pre-registered)

- **B1-ideal** (a valid instrument): top-3 hits in 10 or more of 12 runs.
- **B1-engine** (Claude.ai's prediction): top-3 hits in 3 or fewer of 12 runs.
- **B2 Framing:** the target's rank differs between cautious and strong in 4 or more of the 6 personas, and at least one persona's top-3 hit status flips between framings (a P-02 violation).
- **B3 Breadth:** 25 or more conditions qualify in 10 or more of 12 runs.
- **B4 Severity:** all 6 cautious runs have an Emerging lead. In 3 or more of the 6 strong runs, at least one top-5 condition is Entrenched or higher.
- **B5 Synthesis:** with no narrative, the executive summary names the persona's dominant problem in 4 or more of the 6 cautious runs.
- **B6 Narrative effect (P1):** without the narrative, the_unformed_leader is still outside the top 10 in P1-cautious.

**Scoring:** each hypothesis is scored HOLDS / FAILS / PARTIAL against its registered wording. Nothing here is revised after any run starts.

## Known confounds, recorded

- One author wrote all 12 answer paths.
- The author knows the published state descriptions, so the personas lean toward textbook cases.
- DEFAULT answers are mostly healthy, which makes each persona's problem as visible as it can be.
- Jurisdiction takes one state only.

## RESULTS

Produced by `tools/benchmark_01_score.py` from the 12 saved runs in `C:\Users\rizzo\Downloads\benchmark-01\<persona>-<framing>.json` (each holds the full request and response log and the completion payload). Target ranks and scores are replayed from the logged answers through the production engine functions (`accumulate_answers`, `rank_states`) and are checked against the live `all_qualified_states` (the `Replay` column). The pre-registration text above this section is unchanged. No figure below is hand-typed.

Runs complete: 12 of 12. Runs not complete: 0.

### Per-run measures

| Run | Target | Target rank (of 58) | Target score | Top-3 | Top-5 | Lenient top-3 | Lead state | Qualifying | Spread % | Distinct scores | Margin r1-r2 | R1 tie | Lead tier | Top-5 highest tier | Legal total (low-high) | Replay |
|---|---|---:|---:|:-:|:-:|:-:|---|---:|---:|---:|---:|:-:|---|---|---|:-:|
| P1-cautious | the_unformed_leader | 49 (not qualified) | 0.894330 | N | N | N | the_arbitrary_standard | 38 | 4.19 | 14 | 0.000125 | N | Emerging | Emerging | $1,709,654-$2,213,397 (Elevated) | ok |
| P1-strong | the_unformed_leader | 48 (not qualified) | 0.903498 | N | N | N | the_arbitrary_standard | 37 | 3.45 | 13 | 0.000322 | N | Emerging | Emerging | $1,709,640-$2,213,377 (Elevated) | ok |
| P2-cautious | the_untouchable | 56 (not qualified) | 0.559004 | N | N | N | distributed_culture_fragmentation | 7 | 4.48 | 7 | 0.004741 | N | Emerging | Emerging | $50,900-$57,250 (Minor) | ok |
| P2-strong | the_untouchable | 40 (not qualified) | 0.824801 | N | N | N | what_nobody_says | 24 | 4.83 | 9 | 0.002717 | N | Emerging | Emerging | $731,864-$776,271 (Elevated) | ok |
| P3-cautious | the_overloaded_manager | 4 | 0.845632 | N | Y | N | the_unformed_leader | 5 | 4.47 | 5 | 0.002839 | N | Emerging | Emerging | $24,825-$24,825 (Minor) | ok |
| P3-strong | the_overloaded_manager | 5 | 0.874887 | N | Y | N | the_unformed_leader | 7 | 5.51 | 7 | 0.008998 | N | Emerging | Emerging | $49,825-$49,825 (Minor) | ok |
| P4-cautious | decision_paralysis | 5 | 0.798249 | N | Y | Y | planning_authority_gap | 14 | 5.74 | 5 | 0.018643 | N | Emerging | Emerging | $582,942-$599,609 (Elevated) | ok |
| P4-strong | decision_paralysis | 5 | 0.919368 | N | Y | Y | planning_authority_gap | 14 | 2.37 | 5 | 0.014018 | N | Emerging | Emerging | $582,942-$599,609 (Elevated) | ok |
| P5-cautious | pay_exposure | 30 (not qualified) | 0.523583 | N | N | N | the_undefined_role | 5 | 7.28 | 5 | 0.011189 | N | Emerging | Emerging | $24,825-$24,825 (Minor) | ok |
| P5-strong | pay_exposure | 14 | 0.709390 | N | N | N | planning_authority_gap | 17 | 6.60 | 8 | 0.015565 | N | Emerging | Emerging | $796,625-$810,425 (Elevated) | ok |
| P6-cautious | the_culture_that_wasnt | 15 (not qualified) | 0.498041 | N | N | N | what_nobody_says | 7 | 7.94 | 7 | 0.009084 | N | Emerging | Emerging | $24,825-$24,825 (Minor) | ok |
| P6-strong | the_culture_that_wasnt | 2 | 0.798260 | Y | Y | Y | identity_erosion | 10 | 5.65 | 5 | 0.000000 | Y | Emerging | Emerging | $173,789-$173,789 (Moderate) | ok |

Also-report (P1): the_unreported_hazard rank per run: cautious: 25; strong: 21. Lenient-state ranks: P2-cautious: the_arbitrary_standard 6; P2-strong: the_arbitrary_standard 10; P3-cautious: compression_crisis 44; P3-strong: compression_crisis 46; P4-cautious: planning_authority_gap 1; P4-strong: planning_authority_gap 1; P6-cautious: dueling_narratives 28; P6-strong: dueling_narratives 41.

### Per persona: cautious versus strong

| Persona | Target | Cautious rank | Strong rank | Rank delta (strong minus cautious) | Cautious score | Strong score | Score delta | Top-3 cautious | Top-3 strong | Top-3 flips | Lead cautious | Lead strong | Qualifying c / s |
|---|---|---:|---:|---:|---:|---:|---:|:-:|:-:|:-:|---|---|---|
| P1 | the_unformed_leader | 49 | 48 | -1 | 0.894330 | 0.903498 | +0.009168 | N | N | - | the_arbitrary_standard | the_arbitrary_standard | 38 / 37 |
| P2 | the_untouchable | 56 | 40 | -16 | 0.559004 | 0.824801 | +0.265796 | N | N | - | distributed_culture_fragmentation | what_nobody_says | 7 / 24 |
| P3 | the_overloaded_manager | 4 | 5 | +1 | 0.845632 | 0.874887 | +0.029255 | N | N | - | the_unformed_leader | the_unformed_leader | 5 / 7 |
| P4 | decision_paralysis | 5 | 5 | +0 | 0.798249 | 0.919368 | +0.121119 | N | N | - | planning_authority_gap | planning_authority_gap | 14 / 14 |
| P5 | pay_exposure | 30 | 14 | -16 | 0.523583 | 0.709390 | +0.185807 | N | N | - | the_undefined_role | planning_authority_gap | 5 / 17 |
| P6 | the_culture_that_wasnt | 15 | 2 | -13 | 0.498041 | 0.798260 | +0.300219 | N | Y | FLIP | what_nobody_says | identity_erosion | 7 / 10 |

### Aggregates

- Target rank over 12 runs: min 2, median 14.5, mean 22.75, max 56.
- Top-3 hits: 1 of 12. Top-5 hits: 5. Lenient top-3 hits: 3. Target qualified at all: 6.
- Qualifying count: min 5, median 12.0, mean 15.4, max 38. Runs with 25 or more: 2 of 12.
- Spread rank 1 to last qualifying, % of top score: min 2.37, median 5.17, max 7.94.
- Margin rank 1 to rank 2: min 0.000000, median 0.006869, max 0.018643. Rank-1 ties: 1 of 12.
- Lead tiers: Emerging 12, Entrenched 0, Endemic 0. Top-5 highest tier: Emerging 12, Entrenched 0, Endemic 0.
- Lead state frequency across runs: planning_authority_gap 3, the_arbitrary_standard 2, what_nobody_says 2, the_unformed_leader 2, distributed_culture_fragmentation 1, the_undefined_role 1, identity_erosion 1.
- Legal total (low end): min $24,825, median $378,366, max $1,709,654.
- Replay matched the live qualified list in 12 of 12 runs. Narrative skipped in 12 of 12 runs.

### Executive summaries, verbatim, with Claude Code's labels (Claude.ai to check)

Label rule: NAMES if the summary states the persona's registered dominant problem in substance. The label and its reasoning are Claude Code's judgment, not computed, and are stored in `tools/benchmark_01_labels.json`.

**P1-cautious** (Granite Ridge Components, target the_unformed_leader, lead the_arbitrary_standard, pathway First Call + People Tactics & Strategy)

> Right now, how decisions get made depends on who's in the room and which manager is involved, and that gap between what you say and what people actually experience is already visible in turnover patterns and a regulatory inquiry. The near-term cost is skepticism and inconsistent follow-through on your own direction. Left as is, these management styles become permanent and much harder to unwind.

Label: **DOES NOT NAME**. Dominant problem is untrained supervisors promoted for technical skill. The summary says decisions depend on who is in the room and mentions turnover patterns and a regulatory inquiry, but never the supervision capability gap.

**P1-strong** (Granite Ridge Components, target the_unformed_leader, lead the_arbitrary_standard, pathway First Call + People Tactics & Strategy)

> Right now, how a decision gets made depends heavily on who's involved, and your people have noticed. That inconsistency has already produced a legal claim, is driving turnover around certain managers, and has taught employees that speaking up changes nothing. Closing the gap between what you say happens and what actually happens needs to start now, before it becomes the accepted way things work here.

Label: **DOES NOT NAME**. Closest in substance is people learning that speaking up changes nothing, plus turnover around certain managers. It still does not name supervisors who were never taught to lead.

**P2-cautious** (Halvorsen & Pike LLP, target the_untouchable, lead distributed_culture_fragmentation, pathway Training & Development + First Call)

> Your people have noticed a problem that hasn't been addressed, and they're watching closely to see what you do about it. The cost is showing up as turnover clustering under certain managers, and a growing sense that someone's experience at work depends more on who they report to than on what the organization claims to stand for. Closing that gap means acting visibly on what you already know, not waiting for it to force your hand.

Label: **DOES NOT NAME**. Says a known problem has not been addressed and experience depends on who you report to. It never says one individual is exempt from the standards others are held to.

**P2-strong** (Halvorsen & Pike LLP, target the_untouchable, lead what_nobody_says, pathway People Tactics & Strategy)

> Your teams are quietly building workarounds for a known problem instead of resolving it, and people are watching accountability bend depending on who is involved. That's costing you through uneven turnover, senior tension that never gets worked through, and good people absorbing extra load until they decide not to anymore. This needs a direct look now, before it finishes shaping who stays.

Label: **NAMES**. Says accountability bends depending on who is involved around a known, unresolved problem. That is the exempt-individual condition in substance, though no individual is identified.

**P3-cautious** (Brightwater Family Health, target the_overloaded_manager, lead the_unformed_leader, pathway People Tactics & Strategy)

> Your managers took on bigger roles during a period of fast growth, but their workload never shrank to make space for it. Their personal effort is quietly filling gaps that real development should be closing, so the strain isn't visible yet. If growth keeps pace, that effort will run out, and you'll learn too late which management strengths were real and which were assumed.

Label: **NAMES**. Managers took on bigger roles during fast growth and their workload never shrank to make space. That is the span-without-support problem in substance.

**P3-strong** (Brightwater Family Health, target the_overloaded_manager, lead the_unformed_leader, pathway People Tactics & Strategy)

> Your organization grew faster than your managers were prepared to lead it. The strain shows up as work falling into the cracks between teams, uneven coaching of your people, and turnover that keeps pointing back to the same managers. Unless you deliberately build their capacity to lead at this scale, these patterns will settle in as just how things work here.

Label: **DOES NOT NAME**. Frames the problem as managers not prepared to lead at this scale. That is a capability framing, not span or workload without support. Mentions strain only generally.

**P4-cautious** (Lakeshore Learning Alliance, target decision_paralysis, lead planning_authority_gap, pathway People Tactics & Strategy + Executive Advisory)

> Right now, decisions in your organization don't actually stick. People build plans on calls that later get reopened, which shows up as extra back-and-forth, contingency plans nobody really trusts, and problems that get identified but never fully closed out. Fixing this means making decisions final when you say they're final, so your teams can move forward without constantly checking if the ground has shifted.

Label: **NAMES**. States that decisions do not stick and get reopened, which is the registered problem.

**P4-strong** (Lakeshore Learning Alliance, target decision_paralysis, lead planning_authority_gap, pathway People Tactics & Strategy + Executive Advisory)

> Right now decisions take too long to make and don't hold once they're made, because people aren't working from the same picture of where you're headed. That shows up as the same debates resurfacing without new information, friction over who actually has the call, and a succession plan nobody trusts would work under pressure. Fixing this means clarifying direction, placing decision authority firmly, and pressure testing continuity before you need it.

Label: **NAMES**. States decisions take too long and do not hold, with the same debates resurfacing.

**P5-cautious** (Northloop Analytics, target pay_exposure, lead the_undefined_role, pathway People Tactics & Strategy)

> Right now your teams are getting work done by leaning on a few capable people to quietly cover gaps that no one has formally assigned, and the same roles keep turning over without anyone asking why. That costs you consistency, slows decisions, and puts your most reliable people at risk of burning out or leaving. You need to step back and look at how work is actually structured, not keep patching it one person at a time.

Label: **DOES NOT NAME**. Never mentions pay, compensation or market position. Describes unassigned work and reliance on a few capable people.

**P5-strong** (Northloop Analytics, target pay_exposure, lead planning_authority_gap, pathway People Tactics & Strategy + Executive Advisory)

> Right now, a small number of people are quietly holding the organization together, and your backup plans for losing them haven't been seriously tested. HR is managing the daily fallout, but nobody is stepping back to ask why the same roles keep reopening. Until someone owns that question, you'll keep losing stability every time one of these people walks out.

Label: **DOES NOT NAME**. Never mentions pay, compensation or market position. Describes a few people holding things together and untested backups.

**P6-cautious** (Coastline Hospitality Group, target the_culture_that_wasnt, lead what_nobody_says, pathway People Tactics & Strategy)

> Your people hit the same wall at the same point in their careers, and it's pushing them out the door. The story you tell candidates during recruiting doesn't hold up once they're inside, and promotions happen without clear enough criteria that people stop noticing the exceptions. Right now that costs you attrition and quiet doubt.

Label: **NAMES**. Says the story told to candidates during recruiting does not hold up once they are inside, with attrition as the cost.

**P6-strong** (Coastline Hospitality Group, target the_culture_that_wasnt, lead identity_erosion, pathway People Tactics & Strategy)

> Your growth has outpaced the reality new hires find once they arrive, and the gap between what recruiting promises and what leadership actually tolerates is showing up as predictable departures at a specific point in tenure. That gap is quietly driving turnover you haven't fully traced yet. Closing it means looking honestly at where leadership's actions contradict its stated values and fixing that before recruiting messaging outruns reality again.

Label: **NAMES**. Says the gap between what recruiting promises and what new hires find drives departures.

### B1 to B6 scored against the registered wording

- **B1-ideal** (top-3 hits in 10 or more of 12): **FAILS**. Top-3 hits = 1 of 12.
- **B1-engine** (top-3 hits in 3 or fewer of 12): **HOLDS**. Top-3 hits = 1 of 12.
- **B2 Framing**: **HOLDS**. Target rank differs between framings in 5 of 6 personas (registered threshold 4 or more: met). Personas whose top-3 status flips: 1 (registered at least one: met).
- **B3 Breadth**: **FAILS**. Runs with 25 or more qualifying conditions: 2 of 12 (registered 10 or more of 12). Counts: [5, 5, 7, 7, 7, 10, 14, 14, 17, 24, 37, 38].
- **B4 Severity**: **PARTIAL**. Cautious runs with an Emerging lead: 6 of 6 (registered all 6: met). Strong runs with an Entrenched-or-higher condition in the top 5: 0 of 6 (registered 3 or more: not met).
- **B5 Synthesis**: **FAILS**. Cautious summaries labelled NAMES: 3 of 6 (registered 4 or more). Labels are Claude Code's judgment, flagged for Claude.ai to check. Cautious labels marked borderline: P2-cautious.
- **B6 Narrative effect (P1)**: **HOLDS**. P1-cautious the_unformed_leader rank 49 of 58 (registered: still outside the top 10).

Registered confounds stand as written above.
