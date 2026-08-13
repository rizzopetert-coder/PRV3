# Category D — Free Condensed Diagnostic: Build Scope

Status: DRAFT, scoping pass. Builds on prompts/category-d-condensed-diagnostic.md (concept,
approved 2026-08-11) — read that first, this resolves its open questions and adds the pieces
needed before Gemini review. Not yet approved for build. Not yet Gemini-reviewed.

## What this document resolves vs. what it still leaves open

Resolved here, with recommendation: visible-truncation framing, the financial benchmark
mechanic (sourced and DAF-checked).

Still open, needs Pete's confirmation: whether the recommendations below are accepted as-is,
plus the exact question count/candidates (needs a real data pull only Claude Code can do — see
"Data pull needed" below).

Explicitly still out of scope, unchanged from the concept doc: full-Dx gating mechanism
(paywall/lead-capture/hybrid) — a separate, later decision.

## 1. Visible truncation — recommendation: yes, build it visible

The concept doc flagged this as undecided but already leaned toward visible truncation ("the
limitation itself is part of the pitch"). Recommending that lean gets formally adopted: greyed/
locked additional indicators, an explicit count ("3 more indicators identified"), not silent
omission. Reasoning: silent omission risks reading as a thinner version of the same report,
which undersells the free tier's honest purpose — visible truncation reads as "there is more
here," which is the actual CTA. This is also consistent with P-10's brand-voice standard
(direct, not evasive) — hiding the existence of more findings without saying so would be a soft
form of the "corporate register" the brand voice explicitly avoids.

## 2. Financial benchmark mechanic — recommendation, with full Demographic Applicability
   Filter pass

**Candidate figure:** cost to replace one employee, framed as a percentage-of-salary range, not
a single false-precision number. SHRM and Gallup converge on 50%–200% of annual salary, with
SHRM's own "6–9 months of salary" framing (roughly the 50%–75% low end) as the typical case,
escalating toward 100%–200% for senior/specialized/executive roles.

**Demographic Applicability Filter, run per standing protocol (prompts/demographic-
applicability-filter-protocol.md), before this is treated as usable:**

- *Source's own eligibility boundary:* SHRM and Gallup's figures are general US-employer
  benchmarks, not industry-specific at the headline level — role seniority is the stated
  modifier (frontline lower, specialist/executive higher), not industry or company size.
- *Cross-check against PRV3's actual intake fields:* intake collects headcount, industry,
  respondent's own role level, tenure, direct reports, and jurisdiction — but NOT a per-employee
  salary figure directly, and NOT clearly a total-payroll figure either. This is a real
  open question, not assumed resolved: does the engine already derive an implied payroll from
  headcount + industry elsewhere (Friction Tax's own mechanism suggests payroll figures exist
  somewhere in the system), or does Category D need its own lightweight payroll estimate? Flagged
  below as a data-pull item — do not guess this from memory.
- *Test at the extremes:* the free tier's likely respondent range (per the diagnostic's own
  framing, "an internal leader with budget authority") skews toward SMB/mid-size leadership, not
  enterprise. At the low end (a very small org, low headcount), a 200%-of-salary executive-tier
  figure would badly overclaim; at the high end, using only the 50% low-end figure would
  undersell. Recommendation: use the *midpoint of the general (non-executive) range*, roughly
  50%–75% of one estimated departing employee's salary, explicitly framed as a range rather than
  a single number, and avoid the executive-tier 100%–200% figures entirely for this free,
  intentionally-simple mechanic — reserve any role-tiered precision for the full paid Dx if ever
  built there.
- *Explicit trap avoided:* several sources cite a separate "~$4,700 average cost per hire"
  figure that covers only hard recruiting costs (job postings, recruiter time), not full
  replacement cost including lost productivity and ramp-up. This is NOT the same metric as the
  50%–200%-of-salary figure and must not be conflated with it — using the smaller number would
  badly undersell the benchmark and misrepresent what it measures.

**Mechanic, restated per the concept doc's own constraint:** straight multiplication against
already-collected intake data (headcount, and whatever payroll/salary proxy the data-pull below
confirms is available) — NOT Friction Tax's multi-state compounding model. This stays a single,
simple, honestly-labeled benchmark figure, not a computed-precision number.

## 3. Phase 1 results — CONFIRMED, question candidates locked

Data pull complete, cross-referenced against PHASE_1_QUESTION_SEQUENCE (confirms core, not
spliced/parked) and checked individually against `checkpointIdMap` and per-option severity
triggers before final selection — not assumed safe from state_targets alone.

**Final 9:** Q01, Q05, Q07, Q12, Q14, Q15, Q26, Q47, Q50.

| # | ID | Dimension | Fan-out (targets) | Text |
|---|----|-----------|--------------------|------|
| 1 | Q01 | Authority | 4 — decision_paralysis, the_lost_map, the_founders_grip, sequential_decision_blindness | "When consequential decisions need to be made in your organization — about people, resources, or direction — how does that typically go?" |
| 2 | Q14 | Authority | 3 — pay_exposure, the_pay_fog, compression_crisis | "How would you describe your organization's approach to compensation right now?" |
| 3 | Q12 | Attitude (HIGH, single-seeded — corrected from an earlier, incorrect "Aptitude-leaning" hedge) | 7 — the_unformed_leader, the_overloaded_manager, the_dormant_talent, the_untouchable, leadership_deafness, the_suppression_filter, the_paper_tiger | "How would you describe the quality of management across your organization?" |
| 4 | Q47 | Aptitude (clean) | 1 — the_overloaded_manager | "Think of a manager you'd describe as stretched thin or overloaded. Has anything changed for them...?" |
| 5 | Q26 | Alliance | 3 — silosolation, the_fracture, distributed_culture_fragmentation | "How well do different parts of your organization work together when they need to?" |
| 6 | Q07 | Alliance | 2 — the_fracture, silosolation | "When it comes to losing people you don't want to lose, is there a pattern?" |
| 7 | Q05 | Attitude | 6 — the_basement_standard, the_untouchable, the_inside_track, the_arbitrary_standard, the_wrong_reward, the_paper_tiger | "When someone in your organization stands out because of their underperformance, what happens?" |
| 8 | Q15 | Attitude MED + Authority (dual) | 4 — the_diversity_ceiling, the_inside_track, the_arbitrary_standard, the_dormant_talent | "How would you describe advancement opportunity in your organization?" |
| 9 | Q50 | Attitude | 1 — the_inner_circle | "Every organization has an inner circle or group of people who are especially trusted or protected. When someone in that group makes a costly mistake, what happens to them?" |

**Excluded, with reasons on record:**
- Q34 — explicitly references "everything you've shared," fails standalone by its own wording.
- Q41 — already documented elsewhere in this project as a real content-continuation of Q40, not
  just a labeling question.
- Q46 — dangling reference with no antecedent, never content-fixed.
- **Q11 — dropped after selection, not originally excluded.** Carries a `checkpointIdMap` entry
  and severity trigger SEVER-20 — reusing it risked firing checkpoint/severity machinery
  calibrated for the full 42-question flow inside a 9-question condensed session, violating the
  zero-calibration-risk requirement below. Caught via direct trace of session-store.ts and
  answer/route.ts, not assumed safe from the original state-target-only screening.
- Q49 — considered as Q11's replacement, not selected. Attitude-pure (stronger signal than
  Q15's dual MED classification) but carries `severity_trigger=True` on one option with a `None`
  follow-on ID — verified functionally inert today via direct trace of engine/main.py, but kept
  out on Pete's explicit call to avoid the residual structural risk of an audited-inert flag
  rather than a genuinely clean one.

**Dimension balance, final:** Authority 2 (Q01, Q14), Attitude 3 (Q05, Q12, Q50) + 1 dual
(Q15), Alliance 2 (Q07, Q26), Aptitude 1 (Q47). Attitude's stronger representation reflects its
real share of the taxonomy (22 of 58 states, the largest cluster) — a deliberate proportionality
call, not an oversight. Aptitude's single clean pick (Q47) reflects a genuine property of the
existing core question set — no core question targets a broader pure-Aptitude fan-out.

## 3a. Payroll/salary data — CONFIRMED, no new input needed

Intake does not collect salary or payroll directly (headcount + industry only). Category D
instead reuses `engine/friction_tax.py`'s existing `_INDUSTRY_WAGE_DATA` — real, cited BLS OEWS
May 2023 mean annual wage per employee, keyed to the same 9 industry categories intake already
collects. This is the same data already feeding `PAYROLL_BASELINE_GRID` elsewhere in the system
— already vetted, not a new source introduced for this feature. Only industry is needed for
this specific figure; headcount is not required for the single-employee benchmark.

**Implementation note:** `_INDUSTRY_WAGE_DATA` is currently module-private. A small public
accessor (matching the file's existing precedent, e.g. `resolve_headcount_bucket()`'s shape —
pure, public, returns `Optional[float]`/`None` on a miss rather than raising, consistent with
how every other lookup in this file behaves) is needed to reuse it cleanly. Confirmed as the
right pattern in principle; exact function signature needs Gemini's eyes before being pasted in
as final.

## 4. Build plan, phased

**Phase 1 — data confirmation (Claude Code):** pull real candidate questions per the criteria
above; confirm payroll/salary data availability. No code changes.

**Phase 2 — Gemini architecture review.** Even though the concept doc notes zero new taxonomy
and zero calibration risk, this phase adds a new report shape (truncated output) and a new
financial mechanic (the benchmark multiplication) — both are structural additions to the app,
not content-only changes, so this routes through Gemini per standing protocol before any build.

**Phase 3 — build.** Condensed question subset, truncated result rendering (visible-truncation
per the recommendation above), the benchmark mechanic, CTA. Full diagnostic stays exactly as-is,
untouched, ungated.

**Phase 4 — verification.** Standard discipline: `tsc --noEmit`, relevant test suite runs, live
browser verification of the condensed flow end-to-end before treating this as shippable.

## Open items carried forward, unchanged
- Full-Dx gating mechanism (paywall vs. lead-capture vs. hybrid) — explicitly deferred, separate
  future decision, not blocking this build.
- Rendering path for the truncated output — Gemini's first review proposed routing through
  `web/lib/output-renderer.ts`'s `renderPrivateOutput()`, confirmed dead code (zero real callers,
  same function Category E Direction 3 already found and left untouched). Needs a corrected
  Gemini re-review with a real target, not this function.
- Section 4 financial formula from Gemini's first review ("Headcount × BLS Mean Industry Wage ×
  Attritional Tax% 12%–18%") — confirmed fabricated, does not match what was scoped in Section 2
  above and doesn't exist anywhere in the real codebase. Do not build. The mechanic to build is
  exactly Section 2's percentage-of-one-salary range via `get_industry_wage()`.
