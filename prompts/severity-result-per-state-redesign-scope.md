# SeverityResult Per-State Redesign — Scoping Document

Status: **SCOPING COMPLETE — architecture (Sections 1-3, including the confirmed
split-by-option prerequisite, Section 2a), content mapping (19/32 locked, Sections 8-9),
and recalibration-scope estimate (Section 5) all done. Not built, not submitted to
Gemini yet.** Ready for Gemini architecture review pending one open item, not resolved
in this document: Pete's bundle-vs-separate recalibration sequencing call (Section 6) —
see Section 10 for the full readiness call. No engine code touched across any session
that produced this document. No commits to engine files.

Origin: Section 13a Decision Register, "Severity follow-on state scoping" row
(reframed 2026-08-18, commit 362aaaf). Three candidate input-filtering gate designs
(any-qualifying-state, top-1-only, static-intended-state-membership) were assessed and
found to operate one layer above the real defect. This document scopes the actual fix.

---

## 1. The confirmed architecture problem

`SeverityResult` (`engine/severity.py`) is one tier for the entire scoring session, with
zero per-state dimension anywhere in its structure. It gets broadcast identically to
every state that already qualified for output via `rank_states()` + the signal-floor
gate — a completely separate pipeline that runs, and finishes, before `SeverityResult`
is even computed.

**Real reproduction** (verification session, 2026-08-18, real production path via
`accumulate_one_answer()`/`run_accumulated_engine()`): ATT-UT-01 (target state
`the_untouchable`, rank 58/58 in its own natural session, signal floor not cleared).
Severity credited unconditionally. The_untouchable never appeared in `identified_states`
— confirming severity cannot promote a state into output under any input-filtering
design. But the real output's `identified_states` was `[the_overloaded_manager,
invisible_performance_management, the_undefined_role, the_unformed_leader,
the_dormant_talent, built_to_fail, the_paper_tiger]` — 7 states, none of them
the_untouchable — and **every one of those 7 received the same Endemic tier** that the
severity narrative was substantively about the_untouchable's specific-manager-protected-
by-politics scenario. This is the same shape as the original AUT-PS-01 defect that
started the whole investigation (severity firing with zero per-state awareness, landing
Endemic instead of the locked Entrenched), reproduced at architecture scale.

**New finding this session, narrowing the fix's actual surface area:** `engine/output.py`'s
`build_private_block(qualified_state, severity_result)` and `build_shareable_block(...)`
are *already* called once per qualified state in multi-state mode (`engine/output.py`,
`OutputEngine.build()`, ~line 789-799) — the per-state call shape already exists. But:

1. Every call is fed the *same* session-global `severity_result` object, so every
   resulting block's `severity_tier` is identical regardless of which state it's for.
2. More importantly: **`engine/contract.py`'s `assemble_output()` — the single function
   both Path 1 (`run_accumulated_engine()`) and Path B (`run_engine()`) call to produce
   the final VII.1 JSON contract — never reads `severity_tier`/`severity_anchor_text`
   off these blocks at all.** `assemble_output()` line 449 (`priv =
   session.output_package.private`) only pulls `priv.state_name` and
   `priv.resolution_family`; the top-level `"severity"` object in the final output
   (contract.py line 387-389) is built directly from `session.severity_result.tier`,
   bypassing the per-state blocks entirely. `friction_tax.compute_friction_tax()`
   (line 469-475) and the Decision Blindness flag (line 292-297) both read
   `session.severity_result.tier`/`sev.tier` the same way — three independent
   consumers, all reading the one session-global value directly, none reading the
   per-state blocks' severity fields.

Practical implication: `build_private_block()`/`build_shareable_block()`'s
`severity_tier` output is currently **dead code** from severity's perspective (their
`resolution_family`/`state_name` output is real and used). The per-state *call shape*
partially already exists in the codebase; what's missing is (a) `SeverityResult`
carrying differentiated per-state values at all, and (b) `assemble_output()` actually
reading them instead of `sev.tier` directly.

---

## 2. Proposed data-shape change

`SeverityResult` gains a new field, e.g. `state_severity: dict[state_id, str]` (tier per
state), alongside the existing session-level fields (kept for backward-compat / overall-
session reporting, not removed). `assemble_output()`'s severity block construction and
`build_private_block()`/`build_shareable_block()` look up `state_severity.get(state_id,
"Emerging")` per state instead of `sev.tier` directly — Emerging as the explicit
fallback for any qualified state with no attributed severity input, matching the
existing "zero inputs → Emerging" default behavior.

**Not yet designed, flagged as open questions for the eventual scoping session:**

- **Narrative modulation's severity contribution** (`SeverityAccumulator.narrative_severity_addition`,
  Section IV) is currently a single session-level float, added identically regardless of
  state (`apply_narrative_severity_ceiling()`, `engine/severity.py` line 277-298). It has
  no per-state origin the way SEVER-## trigger inputs do — its signal comes from
  Section IV's LLM narrative call over the whole accumulated vector, not from a specific
  triggering question. Whether it should apply identically to every qualifying state's
  per-state tier (partially preserving today's broadcast for this one input type) or be
  redesigned to be state-aware itself (a materially bigger change touching Section IV) is
  a real open design question, not resolved by "just sum per state."
- Whether `state_severity` should cover every qualifying state or only the profile's
  lead/primary state is itself a scope decision — this document doesn't presume one.
- **Narrative modulation's real current contribution is now confirmed (2026-08-18,
  Section 7 below): zero, always, in production today.** The open design question above
  stands unchanged — it's about what happens if this mechanism is ever wired up as
  spec'd, not about anything it's doing today.

### 2a. Confirmed hard prerequisite: split-by-option attribution (2026-08-18)

**Not optional, not deferrable — part of this redesign's build scope, not a follow-on.**
Elevated from "noted requirement" to confirmed prerequisite once a second locked mapping
needed the same mechanism: **both SEVER-07 and SEVER-03** (Section 8) require
split-by-option severity attribution — different options of the same triggering question
map to different intended states (SEVER-07: C/D/E → three different states; SEVER-03:
C/D → one state, E → a different one). This isn't a one-off for SEVER-07 alone.

`SeverityInput` (`engine/severity.py` line 122-147) carries `trigger_question_id` but no
field recording *which option* of that question was selected — a new field (e.g.
`triggering_option_id: str`) is required, and the mapping's lookup key needs to become
`(severity_follow_on_id, triggering_option_id)` instead of `severity_follow_on_id` alone.
The content-authoring alternative (splitting SEVER-07/SEVER-03 into separate follow-on
IDs per option) was considered and rejected as the default path — it would require
re-authoring live question content and severity_input_mapping wiring for two already-
shipped follow-ons, a larger and riskier change than adding one field.

**Scope check, traced directly (2026-08-19), not inferred — the `trigger_question_id`
wire-contract gap below does NOT affect the 19 locked mappings in Section 9.** Every
lookup, both the scaffolded design and this document's own proposed per-state redesign,
is keyed by `severity_follow_on_id` alone, never `trigger_question_id`:
- `severity_follow_on_id` is set unconditionally and directly from
  `accumulate_one_answer()`'s own `question_id` parameter (`engine/main.py` line 297,
  `"severity_follow_on_id": question_id`) — the follow-on question actually being
  answered, e.g. `"SEVER-19"`. This has zero dependency on `trigger_question_id` and is
  always correct regardless of the wire-contract gap.
- The scaffolded filter design's real lookup (`tools/patch_severity_follow_on_state_scoping.py`
  line 166-168) is `SEVERITY_FOLLOW_ON_INTENDED_STATES.get(severity_input["severity_follow_on_id"])`
  — `trigger_question_id` is never referenced in the lookup at all.
- Section 3's proposed grouping mechanism for the per-state redesign is the same key
  (`severity_follow_on_id`, confirmed there as "already the correct join key").

**What this means concretely:** all 19 locked, single-key mappings (Section 9) are
unaffected — none of them depend on knowing the true originating question, only on
knowing which follow-on fired, which is never in doubt. SEVER-03 and SEVER-07 also don't
need `trigger_question_id` *repaired* to become buildable — `severity_follow_on_id`
already unambiguously identifies the correct parent question (Q21 or Q25) for each; what's
missing is purely the new `triggering_option_id` field distinguishing which option of
that already-known question fired. The `trigger_question_id` wire-contract gap is real,
worth fixing, and listed in the write-site table below since the new option field needs
the same missing plumbing repaired anyway to reach the web layer at all — but it is not
itself a blocker for any of the 19 locked mappings, and not a *separate* blocker for
SEVER-03/07 beyond the option field itself.

**Every current write site that constructs a `SeverityInput`, traced for the eventual
build session:**

| Site | What it does today | What needs to change |
|---|---|---|
| `engine/main.py:293-299`, `accumulate_one_answer()` | Canonical production construction point. Builds the `severity_input` dict from `trigger_question_id` (parameter, defaults to `""`) and `option.severity_input_mapping`. | Needs a new `triggering_option_id` parameter, included in the constructed dict. |
| `engine/main.py:310-354`, `accumulate_answers()` | Multi-select wrapper; threads `trigger_question_id` down to `accumulate_one_answer()` per selected option. | Needs to thread a new `triggering_option_id` parameter the same way. |
| **Real wiring gap, confirmed this session, bigger than the Python-side field alone:** `web/lib/engine-client.ts`'s `AccumulatePayload` (line 182-187) — the wire contract for `/api/accumulate` — has **no `trigger_question_id` field at all today**, let alone an option field. `web/app/api/diagnostic/session/answer/route.ts`'s call to `invokeAccumulate()` (line 132-137) never passes one. Confirmed via `tools/test_main.py` (line 370-377) that `accumulate_one_answer()`'s own default-to-self behavior when `trigger_question_id` is omitted is itself the *tested, documented* behavior — meaning in real production today, every `SeverityInput.trigger_question_id` is already just the follow-on's own ID, not the true originating question. | This is not a smaller version of the Python-side change — it needs new wire-contract plumbing across `AccumulatePayload`, `api/engine.py`'s route (Pydantic model), `route.ts`'s call, and web-side session state to track which option was selected on the *original* triggering question long enough to still know it when the follow-on is answered later in the sequence. |
| `tools/calibration_runner.py:626`, `run_profile()` | Mirrors production construction (already flagged in Section 3 as needing lockstep updates). | Same new field, same lockstep requirement. |
| `tools/test_severity.py` | Direct unit-test construction of `SeverityInput` (positional args, ~15 call sites). | Needs updating if the constructor gains a new field, even an optional one, to keep exercising realistic shapes. |

Not real build touch-points, flagged only so they aren't mistaken for canonical sources:
`tools/diag_severity_bucket2_36profiles.py`, `tools/diag_severity_reachability_85profiles.py`,
`tools/patch_severity_followon_calibration.py`, `tools/patch_severity_follow_on_state_scoping.py`
(already marked non-viable elsewhere), and this session's own
`tools/estimate_severity_redesign_recalibration_scope.py` — all scratch/investigation
scripts, none of them the production or harness path.

---

## 3. Verified consumers and aggregation mechanics (Task 1)

**Every real consumer of `SeverityResult`, repo-wide, engine and web:**

| Layer | File | What it does with the single session-wide tier |
|---|---|---|
| Engine | `engine/severity.py` | Defines `SeverityResult`; `SeverityEngine.score()` (line 355) produces it |
| Engine | `engine/main.py` | Computes `severity_result` via `SeverityEngine`, passes to `output_engine.build()` and into `SessionData` |
| Engine | `engine/output.py` | `build_private_block()`/`build_shareable_block()` (line 658-699) stamp `severity_result.tier` onto each qualified state's block — **output currently unused downstream, see Section 1** |
| Engine | `engine/contract.py` | `SessionData.severity_result` (line 70, required field). `assemble_output()` (line 316+): top-level `severity` object built directly from `sev.tier`/`sev.score_0_100_with_narrative` (line 387-389); `compute_friction_tax(..., severity_tier=sev.tier, ...)` (line 469-475); Decision Blindness flag's `severity_context.current_severity_reading` (line 292-297) |
| Web (types) | `web/lib/types.ts` | `PrivateOutputPayload.severity`, `ShareableOutputPayload.severity`, `CondensedOutputPayload.severity` — all three `SeverityTier` (single flat field, lines 229/322/356) |
| Web (types) | `web/lib/engine-client.ts` | `EngineResult.severity: {tier, score}` — direct mirror of the Python API's JSON response shape (line 101/356) |
| Web (routes) | `web/app/api/result/route.ts`, `web/app/api/share/create/route.ts`, `web/app/api/diagnostic/session/answer/route.ts`, `web/app/api/diagnostic/condensed/answer/route.ts` | Each reads `engineResult.severity.tier` and assigns directly to the outgoing payload's flat `severity` field |
| Web (render) | `web/lib/output-renderer.ts` | Reads `payload.severity` (2 call sites, lines 138-139/196-197) to build the rendered severity block for both Private and Shareable output |
| Web (dev) | `web/lib/dev-diagnostic-preview.ts` | Dev-only fixture type, also a flat `severity: SeverityTier` (line 40) |

Every consumer, both layers, is consistent with a single session-wide tier — none
currently expects or handles a per-state structure. All would need updating in the
redesign, not just `build_private_block()`.

**Aggregation confirmed additive, real code cited:** `engine/severity.py:188-233`,
`compute_raw_severity()`. Line 212: `for inp in accumulator.inputs: ... raw +=
multiplicative + additive` — sums every collected `SeverityInput` into one `raw` float,
regardless of which question/state triggered it. `SeverityAccumulator.inputs` (line 161)
is a flat list with zero grouping.

**Threshold logic confirmed mechanically compatible, no changes needed:**
`normalize_severity(raw_score)` (line 236-250) and `classify_severity(score_0_100)`
(line 253-272) are pure functions — one float/string in, one float/string out, no
session-wide state referenced. Verified directly by using them, unmodified, in this
session's Task 3 estimate to compute per-state tiers on filtered input subsets. The
extension point is upstream: group `SeverityAccumulator.inputs` by intended state
(via each input's existing `severity_follow_on_id` field, `engine/severity.py` line 133
— already the correct join key) before calling these functions, once per state group
instead of once for the pooled list.

**Calibration harness touch points confirmed, will silently drift if not updated in
lockstep:** `tools/calibration_runner.py`'s `run_profile()` (line 591-648) builds one
`SeverityEngine()` per profile, pools every `severity_input_mapping`-carrying answered
option into it via `sev_engine.add_input()` (line 625-631), and passes the single pooled
`sev_result` into `assemble_output()` — structurally identical to production's pooling.
`generate_answers()` (line 438+) already simulates real severity-follow-on answering
(splicing logic at line 540-551, calling `select_severity_follow_on_option()`) — the
harness's answer-*generation* wouldn't need to change. What would: every one of the
172(+3) profiles' `expected.severity_tier` (`engine/test_profiles*.py`, one flat field
per profile) is authored as a single value — under a per-state redesign this needs a
real decision (does it mean "the profile's own `target_state`'s tier," and does the
harness gain a new per-state comparison, replacing the current `actual.severity.tier ==
expected.severity_tier` check)? Not deciding here — flagging that this data model change
is required, not optional, for the harness to keep meaning anything under the redesign.

---

## 4. Coverage-mapping investigation — the 16 previously-unassessed IDs (Task 2)

**Investigation and proposed mapping only — NOT an authored decision.** Content picks
below need Pete's confirmation the same way Q02/Q09/Q14/Q18/Q19/Q33's content did
earlier in this project. Method: live question/option lookup, `state_targets` overlap,
and the triggering option's own text — same method used for the original 14-ID mapping.

| SEVER-ID | Live question / option | Proposed intended state(s) | Confidence | Rationale |
|---|---|---|---|---|
| SEVER-01 | Q16 (live), options B/C/D | `the_diversity_ceiling` | **Clear** | Q16 also targets `the_pay_fog`, but B/C/D's content (advancement/composition-at-senior-levels) is squarely about ceiling dynamics, never mentions pay. Chains unconditionally to SEVER-12. |
| SEVER-03 | Q21 (live), options C/D/E | `decision_paralysis`, `the_lost_map` | **Ambiguous** | C/D (escalation, revisiting) read as decision-paralysis; E ("unclear who has authority") reads as the_lost_map. Three options, plausibly two different intended states depending which fired. |
| SEVER-04 | Q22 (live), options C/D | `the_policy_lag` | **Clear** | Q22 also targets `the_unexamined_algorithm`, but that state's actual content trigger is option E (AI tools), a separate non-triggering option. C/D are squarely about stale/uncovered policy. |
| SEVER-06 | Q24 (live), options B/C/D | `invisible_burnout` | **Clear** | Content ("carrying more than healthy," "seemed fine until they weren't," "running on empty") is burnout language throughout; `human_displacement_anxiety` is a different mechanism (technology/restructuring-driven), not implicated by this option set. |
| SEVER-07 | Q25 (live), options C/D/E | `the_dormant_talent`, `leadership_continuity_risk`, `the_unformed_leader` | **Ambiguous** | General "we don't develop people" framing is genuinely consistent with all three of Q25's targets; no option-level content differentiates which. |
| SEVER-08 | Q26 (live), options C/D | `silosolation`, `distributed_culture_fragmentation` | **Ambiguous** | Structural/procedural silo language ("functions operate independently," "initiatives stall") — excludes `the_fracture` (relational/conflict framing, doesn't fit) but doesn't cleanly separate the other two, which share a similar mechanism. |
| SEVER-09 | Q27A (**parked, not reachable in live production** — calibration-only) | `the_second_close` | **Clear** | Single target, unambiguous content (M&A integration difficulty). Flagging reachability separately from confidence: this ID cannot fire for a real respondent today regardless of mapping. |
| SEVER-11 | Q28 (live, sole target `the_unsolved_problem`) **and** Q31 (parked, targets include `the_unsolved_problem`) | `the_unsolved_problem` | **Clear** | Common state across both parents (one live, one parked) — the live parent's sole target settles it. |
| SEVER-12 | Chained from SEVER-01 (all 5 options, unconditional) — real parent chain is Q16 → SEVER-01 → SEVER-12, not a core question directly | `the_diversity_ceiling` | **Clear** | Inherits SEVER-01's own sole target; SEVER-01's question text ("is this something leadership has named and addressed") continues the same diversity-ceiling narrative. |
| SEVER-14 | Q09 (live), option E | `the_fracture` | **Clear** | "Significant unresolved conflict" is relational/interpersonal framing, matching the_fracture specifically; `silosolation` (Q09's other target) is a structural mechanism this option's text doesn't speak to. |
| SEVER-15 | Q02 (live), option D | `the_exposed`, `hr_capture` | **Ambiguous** | "Absent — no dedicated HR function" plausibly maps to either exposure-without-protection (`the_exposed`) or control-by-unqualified-parties (`hr_capture`); text doesn't disambiguate absence from capture. |
| SEVER-16 | Q18 (live), option C | `the_unreported_hazard` | **Clear** | "Incidents that could have been prevented if people had spoken up earlier" is hazard-reporting-failure language specifically; the other 3 of Q18's targets are broader silence/security mechanisms this option doesn't speak to as directly. |
| SEVER-26 | Q08 (live), option C | `leadership_deafness`, `the_suppression_filter` | **Ambiguous** | "By the time problems reach us they're already crises" is consistent with leadership not hearing signals (deafness) or information being filtered before reaching them (suppression) — Q08's own two targets, genuinely not distinguished by this option's text. |
| SEVER-30 | Q41 (live), option B | `built_to_fail` | **Clear** | Single target, unambiguous. First link of the Structure 1 chain (Q41 → SEVER-30 → SEVER-31). |
| SEVER-31 | Chained from SEVER-30 (option D) | `built_to_fail` | **Clear** | Inherits SEVER-30's sole target; SEVER-31's own text ("what's kept you from raising it") continues the same role/resource-gap narrative. |
| SEVER-32 | Q43 (live), option B | `the_founders_grip` | **Clear** | Single target, unambiguous. |

**Summary: 11 of 16 clear, 5 genuinely ambiguous** (SEVER-03, 07, 08, 15, 26) — flagged
rather than forced. One (SEVER-09) is clear on content but structurally unreachable in
live production today (parked parent question).

---

## 5. Recalibration-scope estimate (Task 3)

Method: ran all 175 profiles (`ALL_PROFILES`) through the real production-equivalent
path (`calibration_runner.py`'s `run_profile()`), tracking which `SEVER-##` IDs actually
fired along each profile's own natural answer path. Combined the existing 14-ID mapping
with Task 2's proposed 16-ID mapping (ambiguous entries included with their *full*
candidate set — deliberately the widest reasonable reading, so this estimate leans
toward *under*-counting the problem, not over-counting it). For each profile, recomputed
its own `target_state`'s severity tier using only the inputs whose mapped state set
includes that target — via the real, unmodified `compute_raw_severity()` /
`normalize_severity()` / `classify_severity()` functions — and compared to the tier the
engine actually broadcasts today.

**Results, real numbers, not extrapolated:**

- **175 total profiles.** 83 (47%) have at least one `severity_trigger` fire along their
  natural path; 92 (53%) never fire severity at all and are entirely unaffected by this
  redesign either way.
- **83 of 175 (47%) have some exposure to the broadcast/misattribution risk** — severity
  fires *and* `identified_states` is multi-state, meaning today's single tier is shared
  across states with no state-specific basis for at least some of them.
- **14 of 175 (8%) would see their own target_state's severity tier actually change** to
  a different classification bucket under corrected per-state attribution — all 14 are
  decreases (the broadcast tier today is inflated relative to what the target state's own
  attributed signal supports), e.g.: `AUT-PF-01` (the_pay_fog) Entrenched → Emerging,
  fired by SEVER-01 (mapped to the_diversity_ceiling, not the_pay_fog); `ALL-SF-01`
  (the_suppression_filter) Endemic → Entrenched, one of its two fired triggers doesn't
  attribute to it. Full list in the estimator script's output
  (`tools/estimate_severity_redesign_recalibration_scope.py`).

This is a real order-of-magnitude answer for the bundle-vs-separate call: a small but
non-trivial slice (8%) of the locked calibration suite's severity assertions would need
re-authoring under a correct redesign, and roughly half the suite (47%) has some exposure
to the underlying issue even where the specific tier happens not to flip.

---

## 6. Open sequencing question for Pete

Two paths, not decided here:

**A — Bundle:** scope and build the `SeverityResult` per-state redesign and the
recalibration (re-authoring the ~14+ affected profiles' `expected.severity_tier`, plus
deciding the harness's new per-state comparison mechanism) as one piece of work. Single
Gemini review covering both the architecture change and its calibration-data
consequences together.

**B — Separate:** ship the redesign first (engine + web consumers + harness mechanism
change), verify it against the *existing* locked tiers where they still apply, then run
recalibration as its own dedicated follow-on once the new mechanism is live and stable.

Neither is recommended here — this document reports what's now known (verified
consumers, mechanical compatibility, the 16-ID mapping proposal, and the real 8%/47%
scope numbers) so the sequencing call can be made with that information rather than a
guess. Both paths route through a Gemini architecture review before any code, per Tier 3
— `SeverityResult` is a core engine data contract consumed by every downstream output
path (Section 3 above).

---

## 7. Narrative Modulation — Origin and Scope

Information-gathering only. Not a design decision — added 2026-08-18 to inform the open
question flagged in Section 2.

**Plain answer: narrative modulation currently contributes nothing to severity, ever, in
real practice.** Traced every caller of `SeverityEngine.set_narrative_contribution()`
(`engine/severity.py` line 348-353, the only method that can move
`narrative_severity_addition` off its default of `0.0`) across the entire repository.
It is called from exactly one place: `tools/test_severity.py`, a unit test that exercises
the method directly, in isolation. **It is never called anywhere in `engine/main.py`**
(confirmed by direct grep across all three of `main.py`'s `SeverityEngine` construction
sites — `run_engine()` line 86-87, `run_accumulated_engine()` line 612-615, the condensed
engine line 715 — each one constructs `SeverityEngine()`, calls `.add_input()` per
collected trigger, then `.score()` directly, with no narrative step anywhere in between)
and never in `tools/calibration_runner.py`'s `run_profile()` either. Confirmed by direct
execution, not just by reading the code: ran a real profile (AUT-PS-01) through
`run_profile()` and inspected the actual severity object — no narrative field is even
exposed in the final output contract, consistent with the mechanism being fully dormant.

**Answering the three questions directly:**

- **What does it actually compute, in plain language?** By spec (Section IV.2/V.2), it's
  meant to be a session-wide bonus derived from the narrative-modulation engine's reading
  of the whole accumulated session (an LLM interpretation step, not tied to any one
  question or state), added on top of the trigger-based severity score and capped at 25
  points on the 0–100 scale (`apply_narrative_severity_ceiling()`,
  `engine/severity.py` line 277-298). It does **not** have a hidden per-state origin
  that's just unexposed — by its own design it's explicitly session-wide, the same way
  the rest of narrative modulation (Section IV) operates on the whole accumulated vector,
  not per-state.
- **How much does it typically contribute, relative to question-triggered inputs?**
  **Zero, always, today** — not "small," genuinely zero, because the code path that would
  set it to anything else is never invoked in production or in the calibration harness.
  All of a session's real severity signal today comes entirely from question-triggered
  `SeverityInput`s (the SEVER-## follow-on answers); the narrative addition sits at its
  default in every real session that has ever run.
- **Does it ride on the same broadcast problem, or is it separate?** **Neither, currently
  — it's inert, not broadcasting anything.** It cannot be "part of what's driving the
  incorrect tier broadcasting to unrelated states today" because it contributes nothing
  to any session's score right now. It is, however, a live open question for the
  *redesign*: if this mechanism is ever wired up as currently spec'd (a single
  session-wide LLM-derived value with no state attribution), it would introduce the exact
  same broadcast problem SEVER-## inputs have today, the moment it's turned on — which is
  why Section 2 flags it as needing its own explicit design decision rather than being
  swept along automatically by the per-state redesign for trigger-based inputs.

---

## 8. SEVER-ID Content Calls — Locked (5 of 5)

Section 4's 5 ambiguous IDs, walked through and confirmed by Pete across two sessions
(2026-08-18). **All 5 locked.** State descriptions are each state's own real
`descriptive_prose` (`engine/data/states.py`, `STATE_PROFILES`), not paraphrase.

### SEVER-03 — Q21 — **LOCKED, split by option**

**Question:** "As a decision works its way through your organization — from idea to
final call — what usually happens along the way?"

| Option | Text | Locked state |
|---|---|---|
| C | "Things escalate more than they should — decisions that shouldn't need senior involvement end up there." | `decision_paralysis` |
| D | "Things get revisited — decisions get made and then reopened without much new information." | `decision_paralysis` |
| E | "It's unclear who has the authority to decide — decisions happen but nobody can say with confidence who was supposed to make them." | `the_lost_map` |

**Real discrepancy found and resolved this thread (Task 1, prior session):** an earlier
direction named "Q31" as SEVER-03's parent and proposed `invisible_influence_architecture`
for option E. Verified directly against `engine/data/questions.py`: Q31 doesn't trigger
SEVER-03 at all (its own options fire `SEVER-11`, a different follow-on) and its real
`state_targets` never included `invisible_influence_architecture` either way. SEVER-03's
actual parent is **Q21** (confirmed, line 470-476), and `invisible_influence_architecture`
belongs to the already-locked, unrelated `SEVER-19`/Q33 pair (Section 9). Reverted to the
original Q21-grounded proposal, both options confirmed by Pete this session.

**Flagged explicitly, not resolved by this mapping:** the E → `the_lost_map` pick is the
best-available fit among Q21's only two real `state_targets`, not a confident match.
`the_lost_map`'s own definition (institutional knowledge living in individual heads,
lost when someone leaves) is adjacent to but not the same thing as option E's actual
content (ambiguity about who currently holds decision authority — a live governance-
clarity gap, not specifically a knowledge-loss-on-departure problem). **This is a real
taxonomy gap for a future conversation** — no existing state cleanly captures
"decision-authority ambiguity" as distinct from decision-paralysis (a speed problem) or
the_lost_map (a knowledge-findability problem). Not attempted to fix here, per explicit
scope — recorded so it isn't mistaken for a settled, confident match later.

### SEVER-15 — Q02 — **LOCKED: `the_exposed`**

**Question:** "How would you describe your HR function right now?"
**Triggering option D:** "Absent — we don't have a dedicated HR function right now."

Locked to `the_exposed` — "There is no function in the organization whose job it
actually is to manage employee-related risk. Concerns have nowhere reliable to land..."
`hr_capture` (a function that exists but has been redirected) and
`planning_authority_gap` (planning/authority mismatch, unrelated to HR existing at all)
both considered and not selected.

### SEVER-08 — Q26 — **LOCKED: `silosolation`** (options C and D both)

**Question:** "How well do different parts of your organization work together when they
need to?"
**Triggering options:** C ("consistent problem — cross-functional initiatives stall
predictably"), D ("functions operate independently — collaboration is the exception").

Locked to `silosolation` for both triggering options. `distributed_culture_fragmentation`
explicitly excluded — Pete's direct call: its live definition is narrowly geographic
(in-office vs. remote divergence specifically), and option C was confirmed broader than
that, not exclusively about distributed/remote teams, so it doesn't fit either option.
`the_fracture` (Q26's third `state_targets` entry) remains excluded as before — its
definition is relationship/conflict-specific, neither option reads as conflict language.

### SEVER-07 — Q25 — **LOCKED, split by option**

**Question:** "How would you describe your organization's track record on developing
people?"

| Option | Text | Locked state |
|---|---|---|
| C | "We tend to hire externally for senior roles — we haven't built the pipeline." | `leadership_continuity_risk` |
| D | "We've tried to develop people but the investment hasn't produced what we expected." | `the_dormant_talent` |
| E | "Honestly, developing people isn't something we've prioritized." | `the_unformed_leader` |

Locked per-option, not one state for all three. **Implementation note (see Section 2):**
this requires per-triggering-option attribution, which `SeverityInput` cannot currently
distinguish (all three options share `severity_follow_on_id = "SEVER-07"`) — a real,
confirmed data-shape requirement for the redesign, not yet built.

### SEVER-26 — Q08 — **LOCKED: `the_suppression_filter`**

**Question:** "How does important information travel in your organization — things
leadership needs to know?"
**Triggering option C:** "By the time problems reach us they're already crises — we're
frequently surprised."

Locked to `the_suppression_filter`. `leadership_deafness` was considered — both fit the
option text plausibly (receiving end vs. transmission mechanism) — Pete's direct call:
`the_suppression_filter` preferred as the more common real-world pattern.

---

## 9. Combined Mapping — Current State, 32 Live IDs

**19 of 32 locked.** All 5 of Section 4's ambiguous IDs (including SEVER-03, resolved
this session) confirmed by Pete and combined with the original 14-ID mapping from the
SEVER-19 leak investigation.

### Locked (19): original 14 + all 5 from Section 8

| SEVER-ID | Intended state(s) |
|---|---|
| SEVER-02 | `built_to_fail`, `the_undefined_role` |
| SEVER-03 | `decision_paralysis` (opt. C, D), `the_lost_map` (opt. E) — *per-option, needs data-shape change, Section 2a; E's fit flagged as a real taxonomy gap, Section 8* |
| SEVER-07 | `leadership_continuity_risk` (opt. C), `the_dormant_talent` (opt. D), `the_unformed_leader` (opt. E) — *per-option, needs data-shape change, Section 2a* |
| SEVER-08 | `silosolation` |
| SEVER-10 | `culture_drift`, `identity_erosion`, `wellbeing_theater` |
| SEVER-15 | `the_exposed` |
| SEVER-17 | `compression_crisis`, `pay_exposure` |
| SEVER-18 | `dueling_narratives` |
| SEVER-19 | `invisible_influence_architecture` |
| SEVER-20 | `cultural_overtime`, `motivational_architecture_failure`, `the_basement_standard`, `the_inside_track`, `the_wrong_reward` |
| SEVER-21 | `the_paper_tiger` |
| SEVER-22 | `heard_and_ignored`, `hr_capture`, `leadership_deafness`, `what_nobody_says` |
| SEVER-23 | `groundhog_day`, `the_burned_credibility` |
| SEVER-24 | `narrative_lock`, `the_burned_credibility` |
| SEVER-25 | `the_basement_standard`, `the_inside_track`, `the_untouchable` |
| SEVER-26 | `the_suppression_filter` |
| SEVER-27 | `disparate_impact_architecture`, `heard_and_ignored`, `the_tolerated_violation` |
| SEVER-28 | `the_founders_grip` |
| SEVER-29 | `the_untouchable` |

### Assessed and explicitly excluded (2) — not gaps, checked and out of scope

| SEVER-ID | Why excluded |
|---|---|
| SEVER-05 | Different, unrelated defect — never calibration-tested for either wired state at all, not a state-attribution leak. Out of scope for this mapping by design, per the original SEVER-19 leak investigation. |
| SEVER-13 | Explicitly assessed and found clean — no state-scoping leak present. |

### Unmapped (11) — confirmed against the original coverage investigation's own Task 1, not assumed by subtraction

`SEVER-01, 04, 06, 09, 11, 12, 14, 16, 30, 31, 32`

Cross-checked against Section 4's own coverage table: all 11 were marked "Clear" there
(single, unambiguous best-supported state each, from the prior investigation) — but none
have been walked through and confirmed by Pete directly the way the 5 in Section 8 were,
so none count as locked yet. Re-derived by elimination and verified, not assumed: 32
total − 19 locked − 2 excluded = 11. Matches exactly, list unchanged from the prior pass.

---

## 10. Final Status and Gemini-Review Readiness

**Section 2 (data-shape, including the confirmed hard prerequisite in 2a) and Section 3
(consumer verification) are complete.** Split-by-option attribution is now part of this
redesign's confirmed build scope, not a deferred nice-to-have — a new
`triggering_option_id` field on `SeverityInput`, a new lookup key shape, and real
wire-contract plumbing through the web layer (Section 2a's write-site trace) all need to
ship as part of the same build that adds `state_severity` to `SeverityResult`.

**Mapping coverage is 19/32 locked, and full coverage is not required to proceed to a
build.** The proposed fallback behavior (`state_severity.get(state_id, "Emerging")`,
Section 2) means any of the 11 genuinely unmapped IDs, or any future new SEVER-##, simply
contributes nothing to per-state severity until mapped — which is strictly better than
today's broadcast behavior (an unmapped trigger inflating every qualifying state's tier),
not a blocker. Coverage can grow incrementally after the redesign ships. SEVER-05 and
SEVER-13 are excluded by design, not gaps.

**Recommendation: this document is ready for Gemini architecture review, contingent on
one thing, not resolved here:** Pete's confirmation on the bundle-vs-separate
recalibration sequencing call (Section 6). Nothing else is outstanding — the mapping is
locked, the data-shape proposal includes the confirmed per-option prerequisite, and the
consumer/aggregation verification is complete.

No code changes, no commits to engine files across any session that produced this
document.
