# Architecture Review — Severity Follow-On Wiring + a Separate Dormant Calibration Risk

## Context

Severity has been structurally unwired since Phase 1 — `SeverityEngine.score()`
always runs with zero inputs, so `severity.tier` is constant `"Emerging"` for
every session today. This blocks three of the five candidate dimensions from
the last review (Trajectory fully, Reversibility/Momentum fully, Urgency
Window partially). Claude Code has now scoped the actual cost of wiring it —
these are real findings, not a request to estimate blind.

## What's confirmed

- The 13 SEVER-## questions are fully authored (real text, real forced-choice
  options, real `dimensional_contributions`) — not stubs. The actual gap is a
  missing translation layer: no answer option is tagged with
  `duration_band`/`population_band`/etc. vocabulary, so there's no mapping
  from "principal chose option B" to a real `SeverityInput` field today.
- `SeverityInput`'s shape and math are proven in isolation (11 test sections)
  — untested against any real constructed input.
- Path 1 (Redis, sequential) has a near-ready hook point: the per-answer
  `AnswerOption` lookup already carries the unused `severity_trigger`/
  `severity_follow_on_id` flags. Wiring here is an incremental extension of
  infrastructure that already works this way for the Phase 2 checkpoint
  system (reusing the splice/wire-threading pattern, not the entropy trigger
  logic, which doesn't transfer).
- Path B (self-select) has no analogous flow at all — no sequential Q&A
  exists to hook a trigger into. Wiring here means designing new UX from
  scratch, not extending anything.

## Questions for you

1. Given Path 1's low relative cost vs. Path B's from-scratch cost, does it
   make sense to scope severity wiring for Path 1 only initially, leaving
   Path B's tier permanently constant (documented limitation) rather than
   building both?
2. The missing `duration_band`/`population_band` tagging on SEVER-## answer
   options — is this content-authoring work (assign tags to existing
   options) or does it require new engine logic? Need your read on scope
   before this goes to content work.
3. Priority call: is unblocking Trajectory/Reversibility/Urgency Window worth
   prioritizing now, or should this sit behind other open work (Category B
   is otherwise closed, `/diagnostic` reskin Stage 3 done and awaiting a
   separate decision)?

## Separate finding — needs its own answer regardless of the above

`engine/test_suite.py` contains a dead `evaluate_pass_criteria()` function
that gates on severity tier (Emerging/Entrenched ±1 tolerance, Endemic
exact-match only) and is unreachable from the active `calibration_runner.py`
suite logic — confirmed via direct execution that it would fail 89 of 172
profiles (all Entrenched/Endemic-expected) on tier mismatch if ever
reactivated. This is a live landmine sitting in the codebase independent of
whether severity gets wired: should this function be removed as
confirmed-dead code, or is it meant to be reactivated once severity works (in
which case it's not dead, it's blocked, and needs to be tracked as a
companion piece to the severity-wiring decision itself)?
