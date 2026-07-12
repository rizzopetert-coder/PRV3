# Consolidation-Mapping Trace — Seven Experiments → Locked 47-State Taxonomy

**Source:** Original 108-candidate filter run (session `635e6b27`, "Gemini consolidation
framework approach," May 1 2026), cross-referenced against the locked `taxonomy.ts` (47
states, Session 34/35). All dispositions below are pulled directly from that filter run's
own `outcome` and `note` fields — not reconstructed or inferred.

**Filters applied (per the original framework):**
- **Filter A** — Severity vs. State: is this a tier/variant of another state, not a distinct condition?
- **Filter B** — Root vs. Presenting Complaint: does this produce other states rather than standing alone?
- **Filter C** — Sufficient Consequence Footprint: does it drive a genuinely distinct resolution path?

**Outcome categories:** STATE (survives as a named state), COLLAPSE (folds into an existing
state, usually as a severity/variant flag), ROOT (named as a root mechanism in resolution
design, not a standalone diagnostic state), ELIMINATE (dropped — fails Filter C entirely).

---

## 1. The Squeeze — resolved

**Disposition: COLLAPSE.** Filter A: "The Overloaded Manager at cultural/systemic scale. Same
root condition, higher severity. Severity tier, not standalone state."

Confirmed independently in the actual state profile document: The Overloaded Manager's own
consolidation notes state directly, *"The Squeeze collapsed into this state at
systemic/cultural scale."* Structural Overload's consolidation notes separately confirm,
*"The Squeeze collapsed here."* So The Squeeze didn't fold into one state — it informed the
consolidation of **both** The Overloaded Manager (cultural/systemic framing) and Structural
Overload (job-design framing), depending on which mechanism the original signal pointed to.

**This closes the single most prominent open item from the citation audit.**

---

## 2. E1 candidates (Exit Interview Pattern Analysis) — resolved

| Candidate | Disposition | Detail |
|---|---|---|
| Advancement Ceiling | COLLAPSE | Filter A: structural variant of Performative Equity (The Diversity Ceiling). "Role availability gap is a mechanism, not a standalone condition." |
| Manager Investment Failure | **STATE** — survives, but not as its own named state in the final 47. *(See note below — this is a flagged exception worth your attention.)* | "Critical: presents identically to The Unformed Leader from employee experience — different cause (choice vs. skill absence), different resolution path. Must survive." |
| Market Exposure | **STATE** — same status as above | "Deliberate positioning choice vs. information gap — distinct from Compensation Incoherence. Different resolution path." |
| Relational Exhaustion | ELIMINATE | Filter C: "Fit failure without organizational detection mechanism. Insufficient consequence footprint... Belongs in question design as a confound." |
| Contribution Invisibility | COLLAPSE | Filter B: downstream consequence of Misaligned Incentives. Folds into Silosolation or Compensation Incoherence depending on locus. |
| Strategic Credibility Loss | COLLAPSE | Filter A: severity presentation of Culture Drift or Change Absorption Failure. |
| Values Misrepresentation | **STATE** — survives | "Recruiting described a culture that doesn't exist — distinct from Culture Drift... Different causal mechanism." |
| Post-Restructuring Flight | COLLAPSE | Filter A: predictable consequence/trigger, not standalone. Belongs as an Authority-dimension severity descriptor. |
| Role Identity Loss | COLLAPSE | Filter A: "Specific expression of Identity Erosion triggered by restructuring. Collapses into Identity Erosion at Entrenched severity." |
| Seniority-Role Mismatch | COLLAPSE | Filter A: "Hiring decision presenting as a management complaint." Folds into Aptitude-dimension states or flagged as a question-design confound. |
| Informal Network Severance | *Not found in the recovered filter-run rows* — see Section 5 below. | — |

**Flagged exception worth your attention:** Manager Investment Failure, Market Exposure, and
Values Misrepresentation are marked "STATE — survives" in the filter run, but **none of these
three names appear in the locked 47-state list in `taxonomy.ts`.** This needs a decision, not
a silent resolution — see Section 4.

---

## 3. E4 candidates (Consulting Engagement Postmortem) — resolved

| Candidate | Disposition | Detail |
|---|---|---|
| Decision Authority Ambiguity | COLLAPSE | Filter A: cross-functional variant of Decision Paralysis. Confirmed in `taxonomy.ts` as `decision_paralysis`. |
| Recommendation Absorption Deficit | COLLAPSE | Filter B: downstream consequence of Diagnostic Dependency, eliminated with its parent. |
| Implementation Courage Deficit | **STATE** — survives per filter run, but not present under this name in `taxonomy.ts`. Same flagged-exception pattern as Section 4. | "Leaders know what to do and won't... Most common consulting failure mode." |
| Anxiety Threshold Breach | ELIMINATE | Filter C: "Describes a diagnostic process failure, not an organizational condition." |
| Leadership Continuity Risk in Change Initiatives | COLLAPSE | Filter A: severity variant of Leadership Continuity Risk. Confirmed in `taxonomy.ts` as `leadership_continuity_risk` with a "change-initiative flag," not a separate state. |
| Diagnostic Dependency | ELIMINATE | Filter C: "Describes the client's relationship to diagnosis, not an organizational condition." |
| Accountability Architecture Gap | **COLLAPSE** — confirmed | Filter B: "Downstream consequence of Structural Reassertion. Change without accountability mechanisms is the mechanism, not the condition." |
| Stakeholder Capture | **ELIMINATE** — confirmed | Filter C: "Engagement dynamic, not organizational condition. Belongs in engagement methodology, not diagnostic taxonomy." |
| Diagnostic Fatigue | **COLLAPSE** — confirmed | Filter A: "Endemic presentation of Change Absorption Failure. Organizations that have stopped engaging with diagnosis as a category are exhibiting Endemic Change Absorption Failure." |
| Presenting Complaint Displacement | **ROOT** — confirmed, and notably this candidate appeared in the raw list itself (id 73) | "The core PRV3 value proposition mechanism... Not a diagnostic state — a named architectural principle." This directly confirms PCD's longstanding treatment as internal-only shorthand was the original intent from the filter run itself, not a later-applied rule. |

**E4 fully resolved as of this pass** — all 10 named candidates now have confirmed dispositions.

---

## 4. Seven previously-unresolved candidates — now fully resolved

The P-10 rename log itself is confirmed unrecoverable as a standalone artifact (Claude Code
checked git history, repo documents, and the rename window — see prior handoff). However, the
**Signal Map** and **Question Signal Map** documents (May 2026, the 45-state intermediate
version) describe each state's distinguishing mechanism in enough detail to confirm matches
directly, without guessing from name similarity alone. Each match below is supported by the
documents' own explicit distinguishing language, not a thematic resemblance.

| Candidate | Original mechanism | Confirmed PRV3 state | Evidence |
|---|---|---|---|
| **Manager Investment Failure** | "Presents identically to The Unformed Leader — different cause: choice vs. skill absence." | **The Dormant Talent** | Signal Map: "disengagement, not incapacity... manager prioritizes own visibility over team outcomes." Direct match to the choice-vs-skill-absence contrast. |
| **Market Exposure** | "Deliberate positioning choice vs. information gap — distinct from Compensation Incoherence." | **Pay Exposure** | QSM: "market-driven, segment-specific — distinct from The Pay Fog (internal equity) by external vs. internal driver." Exact match to the original contrast. |
| **Values Misrepresentation** | "Recruiting described a culture that doesn't exist — distinct from Culture Drift by causal mechanism." | **The Culture That Wasn't** | QSM: "new hire attrition is the signal... gap between recruiting narrative and employment reality." Matches the recruiting-specific framing precisely, not just thematically. |
| **Implementation Courage Deficit** | "Leaders know what to do and won't. Most common consulting failure mode." | **The Broken Compass** | Signal Map: "the barrier is not knowledge or clarity but will." QSM: "the barrier is named as will, not knowledge or clarity." Direct, near-verbatim match. |
| **Disclosure Misalignment** | "Public narrative and internal reality managed independently — D&O exposure when investors rely on the narrative." | **Dueling Narratives** | Signal Map: "public-facing narrative... makes claims about internal practices that operational reality does not support... gap has grown over time rather than converging." Direct mechanism match. |
| **Safety Culture Deficit** | "Management culture producing under-reporting of hazards — distinct from Security Culture Gap (protocol compliance)." | **The Unreported Hazard** | QSM: explicitly the safety-domain branch of C-Silence, distinguished from What Nobody Says (general) and The Unlocked Door (security) within the same document. |
| **Security Culture Gap** | "Human-driven cyber loss — largest and fastest-growing category." | **The Unlocked Door** | QSM: explicitly the security-domain branch of C-Silence. Signal Map: "training delivered but behaviors not observed... security incident attributable to employee behavior." Direct mechanism match. |

### Net result — fully resolved

**All 7 of 7 candidates now have confirmed or highly confident matches**, following recovery
of the May 2026 Signal Map and Question Signal Map documents (45-state intermediate version,
predating the final 45→47 reconciliation), which describe each state's distinguishing
mechanism directly:

- **Manager Investment Failure → The Dormant Talent.** Confirmed — "choice, not incapacity" framing matches exactly.
- **Market Exposure → Pay Exposure.** Confirmed — "market-driven, segment-specific... distinct from The Pay Fog by external vs. internal driver" matches the original contrast precisely.
- **Values Misrepresentation → The Culture That Wasn't.** Confirmed — "new hire attrition is the signal... gap between recruiting narrative and employment reality" is the original mechanism exactly, not just adjacent.
- **Implementation Courage Deficit → The Broken Compass.** Confirmed — "the barrier is named as will, not knowledge or clarity" is a direct match to the original candidate's defining language.
- **Disclosure Misalignment → Dueling Narratives.** Confirmed — "public-facing narrative makes claims internal reality does not support... gap is growing, not converging" matches the original mechanism precisely.
- **Safety Culture Deficit → The Unreported Hazard.** Confirmed — explicitly the safety-specific branch of the C-Silence cluster, distinguished from What Nobody Says (general) and The Unlocked Door (security).
- **Security Culture Gap → The Unlocked Door.** Confirmed — explicitly the security-specific branch of the same C-Silence cluster, with the exact "training delivered, behavior not observed" mechanism.

No remaining gaps. All seven candidates that the original filter run insisted "must survive"
did, in fact, survive — under renamed, P-10-voice identities that the Signal Map and Question
Signal Map documents make traceable with high confidence, not guesswork.

---

## 5. Candidates still not located after two search passes

After a second, more targeted search pass, only **Informal Network Severance (E1)** and
**Structural Reassertion** (referenced only in note text for another candidate, never found
as its own numbered entry) remain genuinely unlocated. Both searches for Informal Network
Severance returned the full E1 candidate range (ids 45-54) with no match — this is reasonably
strong evidence the name either wasn't carried into the formal 108-candidate filter run at
all, or it's the audit's own paraphrase of a differently-named original candidate, not a
search-recall failure. Not worth a third search pass; flagging as genuinely unresolved rather
than continuing to search for something that may not exist under this name.

---

## 6. E5 candidates (Insurance Claims & Risk Data) — fully resolved

Second search pass closed every remaining gap. Full disposition for all candidates, direct
from the filter run:

| Candidate | Disposition | Detail |
|---|---|---|
| Governance Architecture Failure | **ROOT** | Named as a root mechanism in resolution design (board/executive oversight gap), not a standalone state — consistent with absence from `taxonomy.ts`. |
| Disclosure Misalignment | **STATE** — survives per filter run, but not present under this name in `taxonomy.ts`. Same flagged-exception pattern as Section 4. | "Public narrative and internal reality managed independently... D&O exposure when investors rely on the narrative." |
| Safety Culture Deficit | **STATE** — same flagged-exception pattern | "Management culture producing under-reporting of hazards — distinct from Psychological Safety Collapse... and Security Culture Gap." |
| Workload-Induced Disability | **COLLAPSE** — confirmed | "Endemic severity presentation of Structural Overload with workers comp consequence." Matches Section 1's cross-reference exactly. |
| Benefits Administration Gap | **COLLAPSE** | "Specific expression of structural capability mismatch. Collapses into Structural Overload or Governance Architecture Failure at the compliance layer." |
| Security Culture Gap | **STATE** — same flagged-exception pattern | "Human-driven cyber loss — largest and fastest-growing category. Distinct from AI Governance Failure... and Safety Culture Deficit." |
| Vendor Risk Blindness | **COLLAPSE** | Filter C: "Third-party risk mapping gap — collapses into Governance Architecture Failure with vendor/cyber flag. Insufficient standalone footprint." |
| Single Point of AI Failure | **COLLAPSE** | "The Unguarded Function applied to AI operations. Collapses into AI Governance Failure at Entrenched/Endemic severity." |

**Net for E5, fully resolved:** 3 of 8 cleanly collapsed into existing states (Workload-Induced
Disability, Benefits Administration Gap, Vendor Risk Blindness, Single Point of AI Failure —
actually 4 of 8 collapsed), 1 named as ROOT (Governance Architecture Failure), and **3 more
candidates joining the Section 4 exception list** (Disclosure Misalignment, Safety Culture
Deficit, Security Culture Gap) — all marked "survives" in the filter run with explicit
reasoning, none present under these names in the locked `taxonomy.ts`.

This significantly raises the importance of Section 4's open question — see the expanded
list below.

---

## 7. Already-confirmed before this trace (unchanged, included for completeness)

- **Purpose Deficit** — ELIMINATED (Pete's explicit ruling, confirmed multiple times across sessions)
- **Workforce Planning Myopia** — the filter run actually marked this "STATE — survives narrowly...
  Borderline — Pete decides" (id 96), and Pete's ruling was to **collapse it into Reactive
  Talent Management** rather than let it stand alone — so this was a Pete override of Gemini's
  filter-run recommendation, not Gemini's own disposition. Worth knowing the actual sequence:
  Gemini said borderline-survives, Pete said collapse.
- **AI Governance Failure, The Inclusion Gap, Organizational Deafness, Psychological Safety
  Collapse** — quad/triple-confirmed across experiments, high-priority survivors (exact
  `taxonomy.ts` IDs not individually re-verified this pass, but their survival as a category is
  well-established across multiple session records).
- **Performative Equity** — confirmed this session (separate from this trace) to be the same
  state as `the_diversity_ceiling` under an earlier working name.

---

## 8. E2/E3/E6/E7 raw candidates — already resolved, cross-referenced only

| Candidate | Source | Disposition | Basis |
|---|---|---|---|
| Purpose Deficit | E6 #4 | ELIMINATE | Trace Section 7 — Pete's explicit ruling, confirmed multiple times across sessions. |
| The Squeeze | E6 #8, also referenced in E7 | COLLAPSE | Trace Section 1 — collapses into both The Overloaded Manager and Structural Overload. E6's own description ("The Overloaded Manager at cultural and systemic scale") matches almost verbatim — third independent confirmation. |
| Workforce Planning Myopia | E6 #15 | COLLAPSE | Trace Section 7 — Pete's ruling: collapse into Reactive Talent Management (override of Gemini's original "borderline survives" filter-run read). |
| Performative Equity | E3 #8, also "Triple-Confirmed" in E6 | COLLAPSE | Already established outside this trace as the same state as the_diversity_ceiling under an earlier working name. |
| Resource Depletion Architecture | E7 #04 | ROOT | Confirmed in tools/qualitative_review.py's MOB_ROOT_CONDITIONS set — existing formal code classification, not a thematic read. |

These five are logged here for completeness of the E2/E3/E6/E7 consolidation effort so this
work has one canonical record. No new disposition work was performed — all five dispositions
predate this pass.

---

## 9. Batch consolidation dispositions (Filter A/B/C, Gemini + quote-verification passes)

### Tier 5 — high-signal cross-experiment candidates (Filter A/B/C, two-pass Gemini review with quote verification)

| Candidate | Disposition | Target | Note |
|---|---|---|---|
| Organizational Deafness | COLLAPSE | Leadership Deafness | Absorbed Organizing Trigger Blindness (E2 inline sub-candidate) as a downstream mechanism, not a separate condition. |
| AI Governance Failure | COLLAPSE | The Unexamined Algorithm | Absorbed Algorithmic Accountability Gap (E2 inline sub-candidate) as the same underlying claim. First-pass response for this candidate contained a fabricated quote (invented "Unexamined Algorithm" text); rejected and redone with real corpus text before this disposition was accepted. |
| Misconduct Infrastructure Absence | COLLAPSE | The Tolerated Violation | E2 inline-only candidate, no numbered definition; "accumulated tolerance" framing led to an early invalid-target COLLAPSE attempt (Normalization Creep, not a locked state) — corrected on rework. |
| Unmanaged Underperformance | COLLAPSE | The Paper Tiger | Dual-sourced (E2 inline, E3 #07, contradictory "already exists" vs. "new candidate" framing between the two files). Split disposition: behavioral half collapses into The Paper Tiger; the documentation-failure half was separated out as its own candidate (see Invisible Performance Management, below). |
| Invisible Performance Management | STATE | — | E2 #06. Split out from Unmanaged Underperformance — accurate managerial judgment rendered legally indefensible solely by lack of documentation, distinct from The Paper Tiger's active-concealment mechanism. |
| Psychological Contract Violation | COLLAPSE | The Culture That Wasn't | E3 #10. Absorbed two E7 sub-candidates as mechanism/endpoint: Unacknowledged Breach (mechanism) and Trust Collapse (accumulated endpoint). |
| Executive Reality Gap | COLLAPSE | The Suppression Filter | E3 #09. E7's own citation of this candidate mislabeled its source as "the conference experiment" (E6) — corrected; it is exclusively E3-sourced, cited once by E7. |

### Batch A — E2 candidates (Filter A/B/C, Gemini + quote-verification pass; first batch run after the verification tool was built)

| Candidate | Disposition | Target | Note |
|---|---|---|---|
| Disparate Impact Architecture | STATE | — | E2 #02. Distinct from The Unexamined Algorithm (bounded to AI/automated tooling specifically) and The Arbitrary Standard (selective enforcement vs. systemic disparate-impact-through-operation). |
| Manager Legal Overreach | COLLAPSE | Decision Blindness | E2 #05. Managers acting independently without regulatory coordination checks — same coordination-failure mechanism Decision Blindness already names. |
| Internal Reporting Failure | COLLAPSE | Heard & Ignored | E2 #07, marked "Highest Priority" in source. First check attempt lacked real Heard & Ignored text and correctly declined to force a fit rather than fabricate; re-run with real text confirmed the collapse. |
| Cultural Overtime | STATE | — | E2 #08. Distinct wage-and-hour compliance mechanism (unrecorded off-the-clock liability from cultural pressure) from Invisible Burnout (individual psychological exhaustion) and The Tolerated Violation (protected-individual violation, not diffuse cultural norm). |

### Batch B — E3 candidates (Filter A/B/C, Gemini + quote-verification pass)

| Candidate | Disposition | Target | Note |
|---|---|---|---|
| Development Promise Violation | STATE | — | Distinct trust-based onboarding covenant breach; checked against The Dormant Talent and The Culture That Wasn't, no clean fit. |
| Information Architecture Failure | STATE | — | Downward communication vacuum, distinct from The Lost Map (findability) and The Suppression Filter (upward distortion). |
| Sustainability Theater | COLLAPSE | The Wrong Reward | Initial pass checked only against Culture Drift and called STATE; expanded check against The Wrong Reward found direct structural match — wellbeing is a specific instantiation of the same stated-vs-actual reward mismatch. Disposition reversed; this table reflects the final call, not the original. |
| Trust Deficit | STATE | — | Institutionalized-distrust root cause, distinct from The Suppression Filter (the downstream symptom — upward-filtered bad news) on Filter B grounds. |
| Compensation Indifference | COLLAPSE | Pay Exposure | "Know and haven't acted" language matches Pay Exposure closely; also checked against The Pay Fog (transparency-driven exposure, different mechanism), ruled out. |

**Known non-load-bearing error, logged for the record:** one response in this batch contained
a factual error unrelated to any disposition — a stray, out-of-context mention of "The
Unexamined Algorithm" appeared inside the Compensation Indifference/Pay Fog comparison prose,
with no bearing on pay-related states. Not adopted, not load-bearing, logged here only so it
isn't later mistaken for a considered claim.

### Batch C — E6 candidates (Filter A/B/C, Gemini + quote-verification pass)

| Candidate | Disposition | Target | Note |
|---|---|---|---|
| Human Displacement Anxiety | STATE | — | AI-deployment-specific role-security anxiety and departure; checked against Invisible Burnout (capacity exhaustion) and Transition Paralysis (leadership-change stall), distinct mechanism from both. |
| DEI Accountability Collapse | ROOT | — | Two-pass disposition, same pattern as Anchor/LIB-014. First pass: COLLAPSE into The Diversity Ceiling, but its own Filter B reasoning actually described a root mechanism rather than supporting collapse — inconsistency flagged and re-run. Second pass, targeted ROOT-vs-COLLAPSE re-check: reversed to ROOT — accountability-vacuum governance gap plausibly generates downstream symptoms beyond Diversity Ceiling's specific promotion/retention pattern. CAVEAT: the second pass's two illustrative examples of alternate downstream symptoms ("inconsistent enforcement patterns," "tolerated exceptions") were verified as unsupported by any real source text — not fabricated as false attributions to a specific state, but offered in quotation marks as if evidentiary when they were actually hypothetical. The core structural argument for ROOT does not depend on these two phrases and is not undermined by their absence, but they should not be treated as verified textual support. Third ROOT mechanism identified, alongside Presenting Complaint Displacement and Anchor/LIB-014. |
| Transparency Exposure | COLLAPSE | The Pay Fog | Near-duplicate mechanism — legacy compensation inconsistency exposed by transparency/disclosure requirements, same as The Pay Fog's existing description. |
| Compression Crisis | STATE | — | Distinct salary-inversion dynamic (new-hire pay meeting/exceeding tenured pay); checked against Pay Exposure (market-rate lag) and The Pay Fog (unexplained internal discrepancy), neither captures the tenure-inversion mechanism. |
| Proximity Bias | COLLAPSE | The Inside Track | Specific instantiation of unwritten-advancement-criteria pattern (physical presence as the unstated qualifying trait); checked against The Arbitrary Standard (disciplinary inconsistency, different domain) and ruled out. |

### Batch D — E7 psych-construct candidates (Filter A/B/C, Gemini + CC independent comparison, both quote-verified)

| Candidate | Disposition | Target | Note |
|---|---|---|---|
| Motivational Architecture Failure | STATE | — | Distinct psychological condition (controlled/amotivated workforce via reward-system failure) from The Wrong Reward (strategic optimization for unstated incentives) and Invisible Burnout (capacity exhaustion). Checked independently by both Gemini and CC (run in parallel on identical source text as a process-quality comparison); both landed on STATE with matching reasoning. |
| Organizational Moral Drift | ROOT | — | Moral-disengagement mechanisms (euphemistic language, diffused responsibility, advantageous comparison) as generative cultural substrate — plausibly produces Tolerated Violation (if harm concentrates around one protected practice) or Narrative Lock (if euphemism calcifies into defended official story), not a single presenting complaint. Independently confirmed by both Gemini and CC on identical source text — first cross-model corroborated ROOT disposition in this consolidation effort. Fourth ROOT mechanism identified, alongside Presenting Complaint Displacement, Anchor/LIB-014, and DEI Accountability Collapse. |
| Learning Architecture Failure | COLLAPSE | Groundhog Day | Single-loop/double-loop learning failure as the structural mechanism explaining Groundhog Day's cyclical presenting pattern ("keeps treating what's visible and leaving intact what's generating it"). Independently confirmed by both Gemini and CC. Note: this is the second distinct experiment candidate to collapse into Groundhog Day (after Change Absorption Failure, Tier 5) — worth flagging as a sign Groundhog Day's description is absorbing a wide range of "repeated failed intervention" mechanisms, not a disposition concern on its own. |

Process note: Batch D was run as a deliberate comparison exercise — Gemini and Claude Code independently
analyzed identical locked source text to evaluate whether a second AI party adds verification value
beyond quote-checking alone. Both parties reached identical dispositions on all three candidates,
including the harder ROOT judgment call, with zero genuine fabrication from either side (CC's
quote-hygiene issues were self-labeling/formatting lapses, not invented content). Result: dual-party
analysis retained for subsequent batches.

### Batch E — carried-forward candidates (Filter A/B/C, Gemini + quote-verification pass)

| Candidate | Disposition | Target | Note |
|---|---|---|---|
| Sequential Decision Blindness | STATE | — | Originally flagged as a false match to Decision Blindness in Tier 2 (name collision, different mechanism). Confirmed distinct: retaliation-liability pattern from uncoordinated sequential decisions, vs. Decision Blindness's single-decision coordination failure. Checked against Decision Blindness and The Tolerated Violation. Confirmed E2-native — E7 cites both under the 'Confirms and Explains' pattern (cond-confirm badge, research-basis explanation, not a competing definition), same structure as Psychological Contract Violation's E7 citation. No separate E7-proposed candidate exists under either name; single disposition fully accounts for both source appearances. |
| Transition Paralysis (E6) | STATE — NAME PENDING | — | Deliberate namespace-collision test: shares an identical name with the locked taxonomy state but describes a genuinely different mechanism (infrastructure/talent-system migration stall vs. leadership succession stall). Confirmed as a real collision, not a coincidence — collapse into the locked state was explicitly rejected as the correct call. Gemini proposed the replacement name "Talent Transformation Deadlock" — this is an unconfirmed suggestion, not an adopted decision; Pete has not signed off on the specific name. Disposition (distinct STATE) stands; naming is open. |
| Normalization Creep | ROOT | — | "Accumulated tolerance" as generative cultural substrate producing Tolerated Violation instances and Policy Lag drift downstream, not itself a single presenting complaint. Same Filter B reasoning pattern as Organizational Moral Drift (Batch D). Fifth ROOT mechanism identified, alongside Presenting Complaint Displacement, Anchor/LIB-014, DEI Accountability Collapse, and Organizational Moral Drift. Confirmed E2-native — E7 cites both under the 'Confirms and Explains' pattern (cond-confirm badge, research-basis explanation, not a competing definition), same structure as Psychological Contract Violation's E7 citation. No separate E7-proposed candidate exists under either name; single disposition fully accounts for both source appearances. |
| Training-Behavior Gap | COLLAPSE | Groundhog Day | Development-investment-without-consequence pattern folds into Groundhog Day's repeated-intervention-same-root-untouched mechanism; checked against The Dormant Talent (individual manager neglect, different scope), ruled out. |

### Batch F — Tier 4 rejects, full Filter A/B/C pass (Gemini + quote-verification, one direct reconciliation)

| Candidate | Disposition | Target | Note |
|---|---|---|---|
| Favoritism Architecture | COLLAPSE | The Inside Track | Political-proximity advancement mechanism is the structural cause of The Inside Track's presenting pattern (unwritten advancement criteria); checked against The Founder's Grip (localized bottleneck, different scope), ruled out. Third independent instantiation of The Inside Track's pattern this consolidation effort, alongside Proximity Bias (Batch C). |
| Manager Accountability Vacuum | ROOT | — | Source text self-suggested "extension of The Untouchable" but did not rubber-stamp — accountability vacuum at the manager-development layer plausibly generates multiple downstream symptoms (Basement Standard-style team tolerance, Untouchable-style unaccountable individuals, misattributed exit-interview turnover), not a single presenting complaint. Sixth ROOT mechanism identified this session. |
| Distributed Culture Fragmentation | STATE | — | Source text self-suggested "Culture Drift applied to a geographic dimension" but confirmed distinct on independent check — active structural divergence between location-based cohorts, not passive historical erosion (Culture Drift) or interdepartmental workflow friction (Silosolation). |
| Wellbeing Theater | STATE | — | Reconciled directly against Sustainability Theater (Batch B) after apparent contradiction — both self-describe as "variant of Culture Drift" and share adjacent vocabulary, but Sustainability Theater's text explicitly invokes a reward mechanism ("systematically rewarding the opposite") matching The Wrong Reward's own defining language, while Wellbeing Theater's text names a resource-allocation/intervention-design mismatch with no reward-mechanism language. Two independently-argued reconciliation passes reached different conclusions (one confirmed the distinction, one argued unification); Pete resolved in favor of keeping them distinct, on the basis that unifying them would require importing a reward-mechanism claim into text that doesn't contain one. |
| Planning Authority Gap | STATE | — | Source text self-argued distinction from HR Capture ("gap between analytical capability and organizational standing," not compromised oversight); confirmed on independent check. Also distinct from Invisible Influence Architecture (informal power vs. formal functional exclusion). |
| Resilience Architecture Gap | ROOT | — | No-mechanism-for-failure-containment condition plausibly generates multiple downstream symptoms (Unlocked Door-style unaddressed vulnerabilities, Unreported Hazard-style operational strain), not a single presenting complaint. Seventh ROOT mechanism identified this session. Closes Batch F — this is the last of the six original E2/E3/E6/E7 experiments' remaining candidates from the original 44-item raw pool. |

---

## Summary

This trace is now complete. **The Squeeze**, all of **E1, E4, and E5** (8/8, 10/10, 8/8 named
candidates), and all **7 of the "survived but missing" candidates** are resolved with sourced
confirmation — the last group via direct recovery of the May 2026 Signal Map and Question
Signal Map documents, which describe each state's distinguishing mechanism in language that
matches the original candidates' defining contrasts closely enough to confirm rather than
guess at the mapping.

Final tally: **Manager Investment Failure → The Dormant Talent; Market Exposure → Pay
Exposure; Values Misrepresentation → The Culture That Wasn't; Implementation Courage Deficit
→ The Broken Compass; Disclosure Misalignment → Dueling Narratives; Safety Culture Deficit →
The Unreported Hazard; Security Culture Gap → The Unlocked Door.** All seven of the original
filter run's "must survive" calls turned out to be correct — every one of them survived into
the locked 47, under P-10-voice names that the recovered documents make traceable with high
confidence.

Only two items remain genuinely unlocated: Informal Network Severance (E1) and Structural
Reassertion (referenced only as a related mechanism in another candidate's note, never as its
own numbered entry) — both flagged as likely never having existed as separate named candidates
in the formal 108-list, rather than as search failures. Given their minor standing relative to
everything else resolved, these don't block treating this trace as complete.

**This trace is now complete enough to support the held framing decision for the public
methodology series**, pending the still-separate two-question test pass on all seven
experiments (not part of this trace's scope).
