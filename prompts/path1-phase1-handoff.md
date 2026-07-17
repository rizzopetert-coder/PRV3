# PRV3 Path 1 (Full Diagnostic Instrument) — Phase 1 Build Reference

## Context

Session 71 (Claude.ai) locked Path 1 Phase 1 scope and produced an architecture-reviewed
(Gemini, cleared) build handoff. Session 71 (Claude Code, this session) executed that
handoff across four dry-run-confirmed commits. This doc is the living reference for
Phase 2+ — the schema, endpoint contracts, and rules below are locked as of this build;
extend rather than migrate when Phase 2 lands checkpoints and narrative modulation.

Path 1 is the live sequential-question diagnostic — distinct from Path B (`engine/main.py`
`run_engine()`), the existing self-select path's declared-diagnosis shortcut that bypasses
`AccumulationEngine` entirely. Path 1 is the first time real accumulation math
(`rank_states()`, signal-reliability coefficients, axis modifiers) actually runs in
production rather than only in `tools/calibration_runner.py`'s test harness.

**Phase 1 scope: linear Q01-Q34 core sequence only.** No checkpoints, no narrative
modulation, no Aptitude addenda (Q35-Q39), no severity follow-ons. Those are Phases 2-4.
`checkpoint.py` and `narrative.py` remain exactly as dormant/tested-but-unwired as before
this build — neither is invoked anywhere in the new code path.

## Locked architectural decisions (do not relitigate without a reason)

- **Stateful backend session in Redis/Upstash**, not stateless frontend resubmission.
  Locked on P-03 grounds — the accumulated dimensional vector must never round-trip to
  the client.
- **Session infrastructure built now, in Phase 1**, even though Phase 1 alone has no
  branching logic requiring it — Phase 2 needs per-question round trips regardless, and a
  Phase-1-as-batch-submit design would mean replacing the API contract in Phase 2, not
  extending it.
- **Per-answer vector accumulation runs server-side in the existing Python engine**,
  invoked internally by Next.js route handlers — never reimplemented in TypeScript. The
  browser never talks to Python directly and never receives vector/scoring internals in
  any response payload.

## Redis session schema (`web/lib/session-store.ts`)

```typescript
interface DiagnosticSession {
  session_id: string;              // NanoID, same pattern as ShareableOutput
  intake: IntakeEcho;               // organization_size, industry, role_level,
                                     // tenure_in_role, direct_reports, jurisdiction
  next_question_id: string;         // question ID string, NOT a positional index —
                                     // Phase 2's checkpoint-based dynamic assignment
                                     // will not require a schema change
  accumulated_vector: AccumulatedVector;  // the 8 dimensional liability/asset fields
  answers_log: AnswerLogEntry[];    // append-only {question_id, option_id}. Not read
                                     // back in Phase 1 — required now because Phase 3
                                     // narrative modulation needs the full per-answer
                                     // history; adding it later would be a mid-flight
                                     // schema migration on live session data
  status: "in_progress" | "complete";
}
```

**TTL: 6 hours, SLIDING — not fixed-from-creation.** Refreshed on every write
(`session/start` and every `session/answer` alike), via the same
`redis.set(key, val, { ex })` pattern already used for `ShareableOutput`. This was an
implementation detail filled in during Stage 1 that reads differently from how "6 hours"
was originally approved — flagged explicitly per Pete's request so it is never silently
assumed to be a fixed 6-hour window in a later session. Practical consequence: an
abandoned-then-resumed session can theoretically outlive 6 hours measured from creation,
as long as answers keep trickling in slowly enough to keep refreshing the TTL. Accepted
as the right UX tradeoff (an active but slow user shouldn't get cut off mid-session), not
revisited — but real behavior, not a fixed 21600-second hard cap.

**Transition Rule** (`completeSession()`): the moment `status` becomes `"complete"`,
extracts ONLY `industry`, `organization_size`, and final state rankings into a single
shared Redis list (`diagnostic-aggregate`) — not a per-completion key, so no correlatable
identifier survives at all, not even an anonymized one (stronger than the original spec's
"anonymized aggregate table/key" framing, which implied a per-completion record) — then
hard-deletes the session key and its full `answers_log` in the same call. Implements the
already-locked Session 34 Option D data-retention decision; this build did not make a new
retention decision, it executed an existing one.

**`PHASE_1_QUESTION_SEQUENCE`** (34 entries) is derived by querying the live
`QUESTION_LIBRARY`'s `sequence_position` field, not hand-transcribed — verified
programmatically at build time, can't silently drift from the real question library.
Positions 3 and 27 resolve to `Q03B`/`Q27B` (not `Q03A`/`Q27A`) because of the intake
adapter's `significant_events=["none"]` default (see below) — Phase 1 never asks the
conditional-on-significant-event variants.

## Intake field mismatch and the adapter

The locked canonical intake spec (MOB Section 5: `organization_size, industry,
role_level, tenure_in_role, direct_reports, jurisdiction` — also `web/lib/types.ts`'s
`IntakeEcho`) does not match the engine's actual `IntakeData` dataclass
(`headcount, industry, org_type, jurisdictions (list), significant_events (list),
principal_role`). This mismatch predates this build and was never load-bearing before it
— Path B bypasses `AccumulationEngine` entirely, so `IntakeData`'s field values barely
affected Path B's output. Path 1 is the first time this gap actually matters.

Confirmed with Pete before any code was written (not silently resolved): Redis stores
exactly the 6 locked fields, no more. `engine/main.py::_locked_intake_to_engine_intake()`
adapts them for engine calls:

| Locked field | Engine field | Mapping |
|---|---|---|
| `organization_size` | `headcount` | direct |
| `industry` | `industry` | direct |
| `role_level` | `principal_role` | direct (falls back to `"Other"` coefficients if unrecognized — existing engine behavior, not new) |
| `jurisdiction` | `jurisdictions` | wrapped as a 1-item list, or `[]` if empty |
| *(none)* | `org_type` | defaults to `""` — the `org_type_founder_led` axis modifier only fires on the literal `"Founder-led"`, so any other value is a safe no-op |
| *(none)* | `significant_events` | defaults to `["none"]` — no `PRIOR_ADJUSTER_INDEX` entry matches `"none"` (no-op), and it means the Q03A/Q27A conditional branches never fire in Phase 1 |
| `tenure_in_role`, `direct_reports` | *(none)* | stored in the session for calibration/analytics only, never consumed by engine math |

Revisit if a richer Phase 2+ intake form ever collects `org_type` or
`significant_events` directly — the adapter and `PHASE_1_QUESTION_SEQUENCE`'s
Q03B/Q27B hardcoding both assume this default and would need to change together.

## Python endpoints (`engine/main.py` + `api/engine.py`, same FastAPI app)

All three share the existing `x-engine-secret` header check (`_check_secret()`), and all
three are routed in `vercel.json` to the same `api/engine.py` build — no new Python
serverless function.

**`POST /api/accumulate`** — `accumulate_one_answer(accumulated_vector, question_id,
option_id, intake)`. Stateless, pure vector math. Looks up the real `AnswerOption`
server-side from `QUESTION_LIBRARY` — the caller only ever sends `question_id`/
`option_id`, never `dimensional_contributions` (the P-03 boundary enforced at the actual
network edge, not just by convention). Does not invoke `checkpoint.py` or `narrative.py`.
Returns the updated vector only.

**`POST /api/complete`** — `run_accumulated_engine(accumulated_vector, intake,
answered_question_count)`. The real "Path A" completion orchestrator: calls the actual
`rank_states()` (weighted by `SALIENCE_PROFILES`, same reference pattern as
`tools/calibration_runner.py`'s `run_profile()`) instead of Path B's synthetic score=1.0
declared rankings, then reuses `SeverityEngine` → `OutputEngine` → `assemble_output()` →
`OutputSynthesisEngine` completely unchanged from Path B. Same output shape as
`run_engine()`.

**`POST /api/question-copy`** — `get_question_copy(question_id)`. Added beyond the
original task list, flagged and approved during Stage 3: returns ONLY `question_text`
and `option_id`/`option_text` pairs, explicitly excluding `dimensional_contributions`,
`axis_targets`, and severity fields. Exists so `QUESTION_LIBRARY` stays the single source
of truth for question content — without it, the frontend would need a hand-maintained
TypeScript transcription of question copy, a drift risk. This is the runtime enforcement
of the P-03 boundary for rendered content, not just an absence-by-construction of a
duplicated dataset.

## Next.js routes (`web/app/api/diagnostic/session/{start,answer}/route.ts`)

**`session/start`** — accepts the 6 intake fields, creates the Redis session, calls
`/api/question-copy` for Q1, returns `{ session_id, question }`.

**`session/answer`** — accepts `{ session_id, question_id, option_id }`.

- **Index-invariant guardrail**: rejects with **400** (not silent-ignore) any request
  where `question_id` doesn't match the session's `next_question_id`. This is the actual
  security boundary given NanoID-only session ownership (Gemini-approved as consistent
  with the existing `ShareableOutput` trust model) — explicit rejection chosen over
  silent-ignore because the only caller is our own frontend, so an explicit error is more
  debuggable and costs nothing.
- Calls `/api/accumulate`, advances via `PHASE_1_QUESTION_SEQUENCE` (simple list
  increment in Phase 1 — Phase 2 replaces this with checkpoint-driven dynamic
  assignment, which is exactly why `next_question_id` is a string, not an index).
  Returns `{ status: "in_progress", question }` for Q01-Q33.
- On Q34: calls `/api/complete`, builds a `PrivateOutputPayload` with **real normalized
  weights** (`score_i / sum(all_scores)` — Path A, per the doc comment already on
  `StateRef` in `web/lib/types.ts`), NOT Path B's equal-weight scheme. Runs the
  Transition Rule (`completeSession()`). Returns `{ status: "complete", result }`.
  ShareableOutput generation is explicitly NOT part of Phase 1 — matches the existing
  `/api/result` vs. `/api/share/create` separation; deferred to a later phase.

`STATE_RESOLUTION_FAMILY` is duplicated a third time in `session/answer/route.ts`,
matching the existing (already 2x-duplicated) pattern in `/api/result` and
`/api/share/create` — per the standing rule against refactoring adjacent files mid-build,
not extracted into a shared module this session. Verified not a transcription error: all
47 entries programmatically diffed against the original, identical. A genuine future
cleanup opportunity, not urgent.

## Frontend (`web/components/DiagnosticFlow.tsx`)

Replaces `FullInstrumentPlaceholder` (deleted — confirmed single caller) at
`path === "diagnostic"` in `web/app/diagnostic/page.tsx`. State machine: `intake` →
`question` (×34) → `complete` / `error`. Deliberately linear and plain — no
checkpoint-triggered branching UI, no narrative textbox, no addenda, no severity
follow-on prompts.

Intake form dropdown values are sourced from `engine/data/intake.py`'s `INTAKE_FIELDS`
wherever an engine equivalent exists (`organization_size`, `industry`, `role_level`), so
real form values match what `is_high_hazard`/`ROLE_COEFFICIENTS` actually key on — free
text that type-checks but doesn't match the engine's lookup strings would silently fall
back to neutral defaults with no error anywhere in the chain. `tenure_in_role`,
`direct_reports`, and the jurisdiction dropdown (51 entries, all 50 states + DC, matching
`JURISDICTION_TABLE`) are new Phase-1-only value sets with no prior engine equivalent.

`PrivateOutput.tsx` gained an optional `enableSharing` prop (default `true`, self-select
path unaffected) — Path 1's completion view passes `enableSharing={false}` because
`ShareButton` re-invokes `/api/share/create` with Path B's declared-diagnosis logic
(equal weight), which would silently recompute and corrupt Path 1's real weights if
reused as-is. Real Path-1-aware sharing is explicitly out of scope this phase.

## Known open verification gap

**No live HTTP round trip has been exercised anywhere in this build.**

**Correction, same session, before this doc's first commit:** the original framing above
attributed this to credentials not being provisioned in Vercel at all, mirroring a MOB
note that turned out to be stale — Pete confirmed all 5 vars (`ENGINE_URL`,
`ENGINE_SECRET`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`,
`ANTHROPIC_API_KEY`) were provisioned in Vercel Production/Preview on 2026-06-14,
Sensitive-flagged. That MOB note (Section 13, Workstream 2 narrative) had been carried
forward inaccurately for roughly a month of session history and is now corrected there.

The real gap is narrower: those credentials exist in Vercel but are not present in the
Claude Code coding sandbox this build was done in. `vercel env pull web/.env.local`
would resolve this directly, but requires an authenticated Vercel CLI session — this
sandbox has network access to Vercel's API (confirmed: `vercel whoami` returned a real
401 "token not valid" response, not a connection failure) but no valid token, and
completing `vercel login` requires an interactive step (browser or email verification)
this non-interactive environment can't perform. Resolving this is Pete's call: pull
`.env.local` locally and transfer it into the coding environment some other way, or
authenticate the CLI in-session some other way.

What WAS verified, rigorously:
- Direct Python function calls — `accumulate_one_answer()` and `run_accumulated_engine()`
  smoke-tested end-to-end with a synthetic 34-answer sequence, producing real varied
  cosine-similarity rankings, correct severity tier, expected synthesis fallback (no
  `ANTHROPIC_API_KEY` in this dev environment).
- `get_question_copy()` smoke-tested directly — confirmed no scoring fields leak, `KeyError`
  raised correctly on bad IDs.
- Full TypeScript type-checking (`tsc --noEmit`) across the complete call chain, all four
  stages, 0 errors.
- `eslint` clean on all new/changed frontend files.
- Full calibration suite (169/172, unchanged) and the full unit test suite re-run after
  every stage — zero regression to `accumulation.py`, `checkpoint.py`, `narrative.py`, or
  Path B.
- `STATE_RESOLUTION_FAMILY`'s third duplication programmatically diffed against the
  original — identical, not a transcription error.

What was NOT verified — because it requires real infrastructure this sandbox doesn't
have: an actual `session/start` → 34× `session/answer` → completion round trip against
real Redis, exercising the real Upstash client's serialization, real network conditions,
and real TTL behavior. Direct function calls and type-checking are real verification, but
they don't catch anything that only surfaces under real network/serialization conditions.

**This is one open item, not two** — Stage 3 and Stage 4's caveats are the same
underlying gap (no live exercise has happened anywhere in this build), tracked once in
the Decision Register (`tools/_mob.txt` Section 13a) rather than duplicated. **Before
Path 1 Phase 1 is treated as genuinely done — not just committed — this round trip needs
to happen once the credential-access path into the coding sandbox is resolved** (the
credentials themselves already exist in Vercel; access from wherever this round trip
gets run is the actual remaining blocker).

## Commits, this build

1. `1939d96` — Stage 1: Redis session schema + helper (`web/lib/session-store.ts`)
2. `294f3c4` — Stage 2: Python accumulation + completion endpoints
3. `2cda77b` — Stage 3: Python question-copy endpoint + Next.js session routes
4. `37ab8a7` — Stage 4: frontend linear question-flow component
