# Citation Audit — Seven PRV3 Taxonomy Research Experiments

**Status:** Full verification pass complete (own research + Gemini research pass + taxonomy.ts/engine cross-check, reconciled). One small open item — see Section 1a.
**Scope:** Verify EEOC/DOL/SEC dollar figures, insurance market figures, and named academic citations against current sources; distinguish sourced facts from PRV3's own synthesized estimates.
**Date:** June 2026. Source files: `research/seven-experiments/` (commit `401a7b7`).

---

## 1. Agency dollar figures (E2 — Employment Litigation Taxonomy)

| Claim | Current figure (June 2026) | Verdict | Notes |
|---|---|---|---|
| EEOC total recovery | $660M total FY2025 (third-highest in agency history) — down slightly from ~$700M in FY2024 | Stale & mechanism caveat | Total is down YoY, but pre-litigation component is up — see below. Don't read these as contradictory. |
| EEOC pre-litigation vs. litigation split | $528M pre-litigation (mediation/conciliation/settlement) — highest in 60-year history, +12% YoY; $27M via litigation; $104.6M federal sector | Stale | Pre-litigation is now the dominant recovery channel by a wide margin. Original E2 case-level figure ($125K) isn't checkable against agency totals — note as illustrative, not current-state, if reused. |
| SEC total monetary relief | $17.9B gross headline vs. $2.7B adjusted ($1.4B disgorgement + $1.3B penalties) | Stale & mechanism caveat | **Discrepancy resolved:** the $17.9B figure is inflated by a $14.9B uncollectable 2009 Stanford Ponzi judgment plus $232M "deemed satisfied" by parallel proceedings. $2.7B adjusted is the right comparison figure — represents a 25% YoY decline from FY2024's normalized $3.6B. Original E2 figure ($279M) isn't directly reconcilable to either headline; needs a methodology footnote regardless of which it's compared to. |
| SEC calendar-year vs. fiscal-year split | ~240 of 456 FY2025 actions (>50%) were filed pre-inauguration (before Jan 20, 2025) | Mechanism caveat | Off-channel-communications sweeps alone generated $2.3B under the prior administration vs. $71M in FY2025 (all pre-inauguration) — zero post-inauguration actions on that category. The "FY2025 total" obscures a sharp within-year administrative break. |
| DOL WHD back wages recovered | $259M for ~177,000 workers (avg $1,465/worker), +28% YoY from $202M in FY2024 — highest since 2019 | Stale | Magnitude close to E2's original $274M, but see mechanism caveat below — the number alone is the less important finding here. |
| DOL liquidated damages policy | WHD ceased seeking liquidated damages in pre-litigation administrative settlements (effective June/July 2025); PAID self-audit program relaunched July 2025, allowing voluntary disclosure without penalty or liquidated damages | **Mechanism caveat — most significant finding in this audit** | This is not a number that went stale; it's a structural removal of the deterrent E2's original framing likely relied on. The risk calculus has inverted: self-reporting now carries little cost, while employee-initiated litigation (where liquidated damages still apply) remains the expensive path. Any PRV3 content using DOL settlement figures needs this caveat, not a refreshed number. |
| EBSA annual recovery | $1.4B FY2025 ($714.4M from 878 civil investigations; $468.7M from informal complaint resolutions bypassing internal HR; $117.3M via Abandoned Plan Program) | Stale (straightforward update) | The $468.7M informal-resolution figure is independently interesting for PRV3's employee-voice/HR-capture thesis — employees are routing around internal HR at meaningful scale. |

**Overall verdict for E2:** Confirmed — the fix is not uniform across the three agencies. EEOC needs a re-sourcing or illustrative-use caveat, SEC needs a methodology footnote (and now has a clean adjusted figure to footnote against: $2.7B), DOL needs a mechanism caveat that's more consequential than the number itself.

### 1a. Resolved — taxonomy content check (originally flagged as an escalation, downgraded after checking source files directly)

Initial concern: the EEOC's enforcement pivot (per Section 1, away from disparate-impact toward disparate-treatment claims, with active prosecution of DEI mechanics as reverse discrimination) seemed to imply two taxonomy states — **The Diversity Ceiling** and **Performative Equity** — needed their liability framing reversed.

Checked directly against `taxonomy.ts` and `engine/data/states.py` rather than relying on the research-experiment framing alone. Findings:

- **There is only one state, not two.** `engine/data/states.py` carries an explicit code comment on `the_diversity_ceiling`: `# Inferred from profiles doc: Performative Equity`. "Performative Equity" was an earlier working name for the same state during consolidation — not a separate, still-live state that also needs attention.
- **The live description is already direction-agnostic.** The Diversity Ceiling is framed entirely around the gap between what an organization says it values (inclusion) and what its actual promotion/retention data shows — without naming which group is disadvantaged or asserting a specific discrimination mechanism. The engine's liability axes (`Legal & Compliance`, `Talent & Retention`, `Reputational & Brand`) and resolution family (`Intervention`) carry no directional assumption either. **No content rewrite needed.**
- **No Hammer Index citation currently appears wired to this state.** A search of `hammer-citations.json` found no entry mapped to `the_diversity_ceiling` (or any equivalent ID) — the existing citation index uses an older state-naming generation (`LAST_LEG`, `SACRED_COW`, `CRACKED_MIRROR`, etc.) that hasn't been extended to this state yet. This means there's no existing citation carrying hidden directional bias to fix — but it also means this state's financial-consequence backing is currently thin. Separate, smaller gap, not urgent, not part of this audit's scope.
- **Forward-looking note only:** whenever book-citations.ts citations do get sourced for this state, they should be selected and framed with the current enforcement direction in mind (EEOC risk currently points toward exclusionary/preferential DEI mechanics, not failure-to-promote) — but that's guidance for future citation-building work, not a fix to anything currently in place.

**Net effect: downgraded from "escalation requiring a decision" to "verified clean, no action needed now."** Worth remembering the lesson here independent of the outcome — the research-experiment language ("Performative Equity" as if a separate candidate) doesn't always match what actually shipped into the live taxonomy, and is worth checking against `taxonomy.ts`/`engine/data/states.py` directly before treating a research-stage name as a current decision point.

---

## 2. Insurance market figures (E5 — Insurance Claims & Risk Data)

| Claim | Original E5 figure | Current figure (June 2026) | Verdict |
|---|---|---|---|
| EPLI U.S. annual premium | $4B+ (2023, up from $1.5B in 2010) | $4.68B (2023 baseline confirmed independently), projected $4.94B by 2031 (5.37% CAGR). Entering 2026: premiums flat to +5%, stabilizing after the 2020–2022 hard market. | Stale, directionally still correct | Underwriting has gotten *more* hostile even as pricing stabilizes — wage/hour claims increasingly excluded from standard policies (right when DOL enforcement is most active there), and pay-transparency/DEI-scrutiny documentation now required pre-bind. |
| D&O global annual premium | ~$20B (2023) | $22.4B (2025), projected $38.9B by 2034 (6.8% CAGR). North America = 45.2% of global premium ($10.1B). | Stale | Three-year soft market (double-digit premium decreases) is ending — rising insolvencies (+11% in 2024, +6% projected 2025) and 17 US "mega-bankruptcies" in H1 2025 alone are pushing the market toward a hard floor. SCA median settlements surged to $15.48M (2025). |
| Workers' Comp annual premium | ~$50B annual | $45.6B total / $41.6B private carrier net written (2025), down a negligible 0.2% | Stale, magnitude close | Sector remains highly profitable (91% combined ratio, 12th consecutive year of underwriting gains). Frequency down 2%, but medical/indemnity severity both up 4% — the real story is a frequency/severity decoupling, not a premium-volume story. |
| Cyber annual premium | $15B+ (2023, up from $2B in 2015) | $15.3B global (2024); US specifically saw a first-ever **decline** to $9.14B (2024, -7%), then rebounded +11% in 2025 driven by 34% growth in active policies (not price) | Stale & mechanism caveat | The "steady growth" framing in the original E5 document is wrong for the US market specifically — it had a down year. Projected to reach $30B+ globally by 2030. |
| EBSA FY2023 recovery | $1.4B | $1.4B FY2025 (see Section 1 for breakdown) | Confirmed stable, update source year | Same total, but now sourced to FY2025 rather than FY2023 — figure itself didn't move, just needs a year update. |
| AI liability exposure (new — not in original E5) | N/A — not addressed in original document | "Silent AI" exposure now actively named by actuaries (Gallagher Re, Allianz Commercial 2026): algorithmic bias, model malfunction, automated-decision liability, and IP infringement are **neither covered nor excluded** under standard cyber policies — a real coverage gap, not a hypothetical one. EU Product Liability Directive (transposition deadline Dec 2026) extends strict liability to AI software. *Mobley v. Workday* established US precedent for liability reaching both AI vendors and employers. | New finding — high relevance | Directly actionable for the taxonomy: **The Unexamined Algorithm** state should be reframed from an IT/cybersecurity oversight issue to an enterprise-level EPLI/D&O exposure that standard insurance actively will not defend. This is squarely in scope (insurance market data) and doesn't carry the same content-reframing caution as the EEOC/DEI item in 1a, since it's additive rather than reversing an existing liability direction. |

**Confirmed audit distinction (unchanged from original pass):** E5's premium-impact percentage ranges (5–15% productivity drag, 25–100%+ per prior claim, MOD 1.5x = 50% premium increase, 15–30% for security culture gaps) remain correctly identified as PRV3's own synthesized estimates with no named external source. Gemini's research pass independently confirmed this and correctly did not attempt to source them.

---

## 3. Academic citations (E7 — Organizational Psychology Literature Review)

Full list, with N-sizes, cross-linked to live `hammer-citations.json` entries:

- Kahn (1964)
- Gilboa et al. (2008, n=169) — **see refinement below**
- Edmondson (1999) — lineage to HC-068/HC-108; confirmed "immaculate, universally cited" with no challenge
- Google Project Aristotle (2016, n=180) — lineage to HC-007
- Cohen-Charash & Spector (2001, n=190) — confirmed robust, unchallenged
- Hobfoll (1989)
- Deci & Ryan (1985) — confirmed core tenets "unassailable"
- Van den Broeck et al. (2016, n=99)
- Tajfel & Turner (1979)
- Bandura (1999)
- Rousseau (1989) — **see refinement below**
- Zhao et al. (2007, n=51) — **see refinement below**
- Argyris & Schön (1978) — lineage to HC-102; confirmed robust
- Weick & Sutcliffe (2001) — confirmed robust

**Verdict: no retractions or replication failures across all 14 foundational citations as of June 2026.** Confirmed by independent research pass. These don't go stale the way agency figures do — but two specific findings have evolved and warrant a nuance note (not a correction):

- **Gilboa et al. (2008):** the original finding (role overload has a non-significant relationship with job performance) has been meaningfully refined by 2023–2026 "challenge-hindrance" stress-appraisal research — role overload only harms performance when appraised as a hindrance (threat, no growth potential); appraised as a challenge, it can enhance motivation and performance. **This actually strengthens PRV3's existing dual-axis (Liability/Asset) architecture** — it validates that a liability stressor alone is diagnostically insufficient without assessing the counterbalancing organizational assets that shape appraisal.
- **Rousseau (1989) / Zhao et al. (2007):** psychological contract breach research has moved from contemporaneous (one-time, static) models toward longitudinal "post-violation" models — breach isn't a single static penalty but a dynamic process of disruption, renegotiation, and repair over time. Any PRV3 state relying on contract-breach framing should reflect that severity depends partly on subsequent organizational repair effort, not just the initial breach.

**Document-drift flag (unchanged, still unresolved):** E7's own validation section states "72+ candidates → 35-40 distinct conditions," contradicting the locked 108→47 numbers. Still needs explicit note in any audit write-up; not resolved by this pass.

**New supplementary literature worth adding to the canon (2023–2026):**
- Gallup's 2026 *State of the Global Workplace*: global engagement fell to 20% in 2025 (lowest since 2020), costing an estimated $10T in lost productivity globally; manager engagement specifically dropped 5 points to 22% — the steepest single-group decline.
- A 2024 systematic review (217 studies) validating psychological-safety measurement instruments (Cronbach's alpha .77–.81) — direct empirical backing for survey-based diagnostics like PRV3.
- A 2023/2024 meta-analysis (136 samples, 22,000+ individuals, 5,000+ groups) confirming psychological safety predicts performance and citizenship behavior independent of basic leader relations and general engagement — i.e., it's not just a subset of engagement, it's an independent driver.

---

## 4. Remaining four experiments — audit profile summary

| Experiment | Citation density | Audit burden | Status |
|---|---|---|---|
| E1 (Exit Interview Pattern Analysis) | Low — qualitative pattern analysis | Light fact-check; consolidation-mapping check needed (see Section 5) | **Confirmed via independent research pass: no external data sourced, no verification needed.** |
| E3 (Glassdoor/Indeed Review Clustering) | Low — composite/illustrative review language, not verbatim attributed quotes | No fact-check needed | **Confirmed: internal synthesis only.** HR Capture's origin documented here, confirmed surviving into 47-state taxonomy. |
| E4 (Consulting Engagement Postmortem) | Low — PRV3's own synthesis, no external citations | Register-sensitivity work (two-question test) only | **Confirmed: entirely internal synthesis.** Origin point for Presenting Complaint Displacement (Pattern 5, Candidate 10). |
| E6 (HR Conference Theme Analysis) | Lowest — conference-circuit trend observation | "2024-2025" framing now confirmed stale | **Resolved — see below.** |

**E6 resolution:** original framing characterized 2024–2025 conference themes as dominated by basic psychological safety, generalized empathy, and expansive equity programming. As of mid-2026 (SHRM26, HR Tech, Unleash, Transform agendas), the dominant themes have shifted to: (1) AI governance and bias-auditing frameworks moving from conceptual to operational deployment, (2) global pay-transparency compliance driven by the EU directive and US state-law patchwork, (3) **defensive** DEI and skills-based talent architecture — DEI conversation has shifted from expansionary cultural programming to legal-defensibility guidance for navigating the current EEOC enforcement posture (directly connects to the Section 1a escalation). This is a clean, confirmed update — the "current state" framing in E6 needs revision before any public use.

Purpose Deficit confirmed eliminated during consolidation; The Squeeze's fate remains unconfirmed (still needs the fold-into-Overloaded-Manager check).

---

## 5. Consolidation-mapping leads (unchanged from original pass — not addressed by this verification round)

**Confirmed surviving into current 47-state taxonomy:** HR Capture, Identity Erosion, Narrative Lock (as state #42), **Performative Equity (confirmed via Section 1a check — survived as The Diversity Ceiling; not a separate candidate)**.

**Confirmed dropped/folded:** Purpose Deficit (eliminated); Workforce Planning Myopia (collapsed into Reactive Talent Management).

**Unresolved — needs explicit consolidation check:**
- The Squeeze (E6) — possible fold into The Overloaded Manager
- Advancement Ceiling, Manager Investment Failure, Relational Exhaustion, Market Exposure, Contribution Invisibility, Seniority-Role Mismatch, Role Identity Loss, Informal Network Severance (E1)
- Structural Reassertion, Implementation Courage Deficit, Anxiety Threshold Breach, Diagnostic Dependency, Stakeholder Capture, Decision Authority Ambiguity, Recommendation Absorption Deficit, Diagnostic Fatigue, Accountability Architecture Gap, Leadership Continuity Risk in Change Initiatives (E4)
- Governance Architecture Failure, Disclosure Misalignment, Safety Culture Gap, Workload-Induced Disability, Benefits Administration Gap, Vendor Risk Blindness, Single Point of AI Failure (E5)

**Quad/triple-confirmed across multiple experiments:** AI Governance Failure, Performative Equity (→ The Diversity Ceiling), The Inclusion Gap, Organizational Deafness, Psychological Safety Collapse.

---

## 6. Status and recommended next steps

**Done as of this pass:**
- ✅ All agency dollar figures (EEOC, SEC, DOL, EBSA) verified — Section 1
- ✅ All insurance market figures (EPLI, D&O, Workers' Comp, Cyber) verified — Section 2
- ✅ AI liability exposure researched as new addition — Section 2
- ✅ Academic citation challenge/retraction check complete — Section 3
- ✅ Supplementary 2023–2026 literature identified — Section 3
- ✅ E1/E3/E4 confirmed as needing no external verification — Section 4
- ✅ E6 HR conference theme currency resolved — Section 4
- ✅ Diversity Ceiling / Performative Equity content check resolved — Section 1a (no rewrite needed; confirmed single state, direction-agnostic as written)

**Still open:**
1. Write the methodology/mechanism footnotes into actual PRV3 content. **DOL portion RESOLVED (2026-08-03):** the mechanism caveat (WHD ceased seeking liquidated damages in pre-litigation administrative settlements as of mid-2025, PAID self-audit relaunched) is now written directly into research/seven-experiments/experiment-2-employment-litigation-taxonomy.html (4 spots: DOL Recovery data label, financial-text prose, candidate summary, closing findings), with the figure updated $274M FY2023 → $259M FY2025 throughout. **Still open:** Section 1's SEC methodology footnote (the $2.7B-adjusted-vs-$17.9B-gross distinction) and Section 2's Unexamined Algorithm reframe (EPLI/D&O insurance-coverage-gap framing — Silent AI, Mobley v. Workday, the EU Product Liability Directive) — confirmed via direct repo search this session that neither has been written into any live content: web/content/book/methodology/the-unexamined-algorithm.md's live /book piece frames the state purely as employment-discrimination exposure, not the insurance-coverage-gap finding this item refers to.
2. Run the formal two-question test pass on all seven experiments (Foundation doc Section 5 standard, adapted: "PRV2 vocabulary" → "internal research jargon") — unaddressed by this citation-focused pass.
3. Complete the consolidation-mapping trace for unresolved candidates in Section 5.
4. Resolve the E7 document-drift flag (72+/35-40 vs. 108/47) — still just flagged, not corrected anywhere.
5. Source book-citations.ts citations for The Diversity Ceiling, which currently appears to have none — minor, separate gap noted in Section 1a, not urgent.
6. Hold the public methodology series framing decision until 2 and 3 are done.

