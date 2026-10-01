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
