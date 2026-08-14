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

## 1. Visible truncation — RESOLVED, indicators ship fully locked (not 2-3 shown)

The concept doc flagged this as undecided but already leaned toward visible truncation ("the
limitation itself is part of the pitch"). That lean is adopted: locked, not silently omitted.
Reasoning: silent omission risks reading as a thinner version of the same report, which
undersells the free tier's honest purpose — visible locking reads as "there is more here," which
is the actual CTA. This is also consistent with P-10's brand-voice standard (direct, not
evasive) — hiding the existence of more findings without saying so would be a soft form of the
"corporate register" the brand voice explicitly avoids.

**Result shape, resolved — this table corrects the concept doc's original version, which assumed
a live synthesis call that was never actually decided on:**

| Full Report | Condensed Report |
|---|---|
| Top state + secondary ("Also Present") states | Top state only |
| Full indicator list (LLM-synthesized, live) | **Fully locked, zero shown** — not "2-3 shown, rest locked." Copy reads along the lines of "All indicators locked — unlock the full diagnostic to see what's driving this result," not a partial reveal. |
| Two-paragraph synthesis (LLM-synthesized, live) | One paragraph — `get_fallback_synthesis()`'s static copy, keyed on `resolution_family` + `severity_tier`. **No live `synthesize()` call.** |
| Full Friction Tax estimate | Simple benchmark-based figure (`get_industry_wage()` x 0.50–0.75, Section 3 below) |
| — | "Partial read" framing + CTA to the full diagnostic |

**Verdict/indicator sourcing decision, resolved this session (Pete's call, product/cost
decision, not an architecture question — no further Gemini round needed):**

- **Verdict paragraph:** `engine/data/fallback_synthesis.py`'s `get_fallback_synthesis()` —
  the same static fallback mechanism already live in the full diagnostic's own timeout/failure
  path, real and already-approved copy, zero marginal cost. **Not** a live call to
  `engine/output_synthesis.py`'s `synthesize()`.
- **Why no live synthesis:** a free, anonymous, ungated tool invoking a paid, timeout-exposed
  LLM endpoint on every submission is a real cost and abuse-surface risk this feature shouldn't
  carry, and it breaks the "zero new content" framing that has governed every other decision on
  this feature.
- **Why indicators ship fully locked rather than partially shown:** `get_fallback_synthesis()`'s
  `observable_indicators` field is hardcoded to an empty list by design (confirmed by direct
  read — the fallback path deliberately gives up on indicators rather than inventing generic
  ones, "coherence over completeness"). There is no real per-respondent indicator content to
  partially show without a live synthesis call, which was just ruled out. Locking the section
  entirely, with explicit unlock-framing copy, is honest about what's actually available —
  matches the feature's own "the limitation is part of the pitch" design rather than fabricating
  a partial reveal from content that doesn't exist yet.
- **Option D rejected (state's static `descriptive_prose` as the verdict text):** that content
  was authored for `/book`'s general state descriptions, not as a response to a specific
  respondent's answers. Reusing it here repurposes content for a job it wasn't designed for.

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

**Phase 3 — SHIPPED, commit 5573bd4.** Condensed question subset, engine completion path
(`run_condensed_engine()`, no live LLM call), the benchmark mechanic (`get_industry_wage()`,
null-path handled — omits the range with an explicit unavailable note, never a broken figure),
`CondensedOutput.tsx` with indicators fully locked, CTA. Full diagnostic stays exactly as-is,
untouched, ungated. Two real bugs found and fixed during verification (not assumed away, see
tools/_mob.txt Decision Register for full detail): `run_condensed_engine()` originally reused
`assemble_output()` and crashed on Category D's industry-only intake (Friction Tax's own
`compute_friction_tax()` requires a numeric headcount) — rewritten to bypass `assemble_output()`
entirely; and `resolution_family` was found to come back empty in multi-state mode, confirmed
pre-existing (`OutputPackage.private` only populated in single-state routing,
`engine/output.py`) and confirmed to match `PrivateOutput.tsx`'s own identical, already-shipped
gap byte-for-byte, not a new regression.

**Phase 4 — verification, DONE except live HTTP.** `tsc --noEmit` clean, `tools/test_main.py`
36/36, full 172(+3)-profile calibration regression 171/175 (exact baseline, zero movement),
vitest unchanged. Real end-to-end Python run (not mocked) confirmed the full 9-question
accumulate → complete pipeline works. **Not yet done:** live HTTP/browser verification of the
deployed condensed flow — not verifiable from the coding environment (no Preview deployment,
`next dev` doesn't serve the Python engine locally, same pre-existing infrastructure gap already
on record). Needs Pete's own live check post-deploy, same as Category E Directions 1 and 3.

## Gemini gate — CLEARED (round 3, prompts/category-d-gemini-review-round3-constrained.md)

Both open architecture questions confirmed sound after a deliberately constrained round 3
(rounds 1-2 each produced fabricated proposals — see tools/_mob.txt Decision Register,
"Gemini fails to incorporate explicit, verbatim correction across review rounds"):
- **Rendering target:** `web/components/CondensedOutput.tsx`, a new, separate component — not
  `web/lib/output-renderer.ts`'s `renderPrivateOutput()` (confirmed dead code, zero callers).
- **Financial mechanic:** `low = get_industry_wage(industry) x 0.50`, `high =
  get_industry_wage(industry) x 0.75` — per-departing-employee, headcount not involved.

Category D is ready to move toward Phase 3 build on both fronts.

## Open items carried forward

- Full-Dx gating mechanism (paywall vs. lead-capture vs. hybrid) — explicitly deferred, separate
  future decision, not blocking this build.
- **RESOLVED, Phase 3:** `get_industry_wage()` returning `None` (unrecognized industry) now has
  real consuming-side handling — `CondensedOutput.tsx` omits the financial range entirely with
  an explicit "benchmark figure isn't available" note, never a broken or missing figure.
- **RESOLVED via Pete's own live check, two real bugs found and fixed:** (1) no page anywhere
  mounted the condensed flow (`/diagnostic/condensed` 404'd) — fixed, commit `106105c`
  (`web/components/CondensedDiagnosticFlow.tsx` + `web/app/diagnostic/condensed/page.tsx`).
  (2) the completion step (Q50, the 9th question) failed with an empty-body 500/503 in
  production, reproduced twice — traced via Vercel's real runtime error logs (not code
  inspection): the actual error was a 404 on `/api/condensed-complete` itself, because
  `vercel.json`'s explicit routes allowlist never got the entry for that route when it was
  built. `run_condensed_engine()` never ran. Fixed, commit `b7ec5ac`. Logged as its own
  standing-practice Decision Register row — this is a generalizable gap (any new `api/engine.py`
  route needs its own `vercel.json` entry), not a one-off. Still open: one live end-to-end
  click-through (industry select → all 9 questions → `CondensedOutput` render) as final
  confirmation, though the specific bug that would have broken it is now fixed and verified via
  real production error logs, not assumed fixed.
- **New, carried forward, informational (not blocking, shared-engine scope):** `resolution_family`
  renders empty in multi-state mode — confirmed pre-existing across both the full diagnostic and
  Category D, not something either build introduced. A real fix (if ever wanted) is
  shared-engine-level work spanning `engine/output.py`/`engine/contract.py`, out of scope for
  both features as currently built.
