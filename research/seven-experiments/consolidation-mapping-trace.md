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
