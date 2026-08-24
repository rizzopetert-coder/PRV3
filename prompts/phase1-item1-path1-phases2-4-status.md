# Path 1, Phases 2-4 — Status Confirmation

Date: 2026-08-24. Verified directly against current `web/app/api/diagnostic/session/answer/route.ts`, `web/lib/session-store.ts`, `web/components/DiagnosticFlow.tsx`, `engine/main.py`, and a real `vitest run` — not inferred from `prompts/path1-phase1-handoff.md` alone, which is confirmed **stale** on this exact question.

## Verdict: mixed, not a single answer — the MOB's "NOT CONFIRMED" framing undersells what's actually there, and the handoff doc is out of date

The handoff doc states plainly: *"Phase 1 scope: linear Q01-Q34 core sequence only... checkpoint.py and narrative.py remain exactly as dormant/tested-but-unwired as before this build — neither is invoked anywhere in the new code path."* **This was true when the doc was committed but is no longer true.** Two commits landed after it: `bc72daf` ("Wire checkpoint evaluation into session/answer, stand up vitest") and `c82c67a` ("web+api: wire severity follow-ons live for Path 1 (code-level complete)").

Confirmed directly, piece by piece:

| Piece | Status | Evidence |
|---|---|---|
| **Checkpoints (Q11/Q19/Q27 distinguisher evaluation)** | **BUILT, with real confirmed test failures** | Real code in `session/answer/route.ts`: `checkpointIdMap`, `checkpointSlot()`/`setCheckpointSlot()`, a real `invokeCheckpoint()` call gated on "evaluated once, never re-evaluated," real distinguisher-splicing logic. Not a stub. |
| **Severity follow-ons** | **BUILT, with real confirmed test failures** | Real code in the same route: `severity_follow_on_origins`, `severity_follow_on_ids`, splice logic reusing the checkpoint-distinguisher path per its own comment. Not a stub. |
| **Narrative modulation** | **NOT STARTED** | Confirmed via current live code comments, not the stale doc: `session-store.ts` line 11-12 states plainly *"No narrative modulation, no Aptitude addenda (Q35-Q39)"*; `engine/main.py` hardcodes `narrative_response=""` in multiple places (lines 621, 706) with an explicit comment *"Phase 1 has no narrative modulation."* `narrative.py` has zero callers anywhere in `web/app`. |
| **Aptitude addenda (Q35-Q39)** | **NOT STARTED** | Same `session-store.ts`/`DiagnosticFlow.tsx` comments confirm this explicitly, no code found anywhere referencing Q35-Q39. |

## The real, confirmed test failures — precisely characterized, not overstated

`npm run test` (`vitest run`, real execution, not cited from memory): **39/45 tests pass, 6 fail — all 6 in `session-store.test.ts`**, all clustering around the same apparent root cause, not 6 independent bugs:

1. `spliceDistinguishers` basic insertion (checkpoint splice)
2. Severity follow-on splice basic insertion
3. Severity follow-on + checkpoint splice compounding together
4. `TOTAL_CORE_QUESTIONS reflects the 32-entry sequence, not a stale hardcoded 34` — test expects **32**, fails
5. `coreQuestionPosition` returning "the 1-indexed static position for a core question" — fails
6. The 3-way compounding checkpoint splice regression test (`Q11+2, Q19+1, Q27B+3`) — expects a length-38 result, gets a length-44 result

**Important nuance, not fully resolved in this pass:** `TOTAL_CORE_QUESTIONS = PHASE_1_QUESTION_SEQUENCE.length` is **computed dynamically** from the real, live `QUESTION_LIBRARY` (per the handoff doc's own description — "verified programmatically at build time, can't silently drift"), not hardcoded. The failing test's own name ("not a stale hardcoded 34") suggests the test author expected 32 to be the new-correct value after some question-library change (plausibly related to a test section literally named "Q28/Q31 parked (live-session investigation)" — implying 2 questions were removed from the core sequence at some point). Whether the 6 failures represent (a) a real production bug in the splice-compounding logic, or (b) a stale test file that wasn't updated after a legitimate 34→32 question-library change, was **not fully disambiguated in this pass** — both are plausible, and distinguishing them precisely would require tracing exactly when/why the core sequence changed, which goes beyond a status-confirmation check. Reported as an open question, not resolved either way, rather than guessed at.

## Also relevant, surfaced by the handoff doc itself: Phase 1's own unresolved verification gap

Separate from the Phases 2-4 question, but directly relevant to "is Path 1 genuinely done": the handoff doc's own "Known open verification gap" section states **no live HTTP round trip has ever been exercised against real Redis/network infrastructure**, anywhere in this build — verification so far is direct Python function calls and type-checking only. Not independently re-verified in this pass (out of this item's scope), but flagged since it bears on how much weight "Path 1 is built" should carry either way.

## Correction to the MOB

The current MOB framing ("Path 1, Phases 2-4... status NOT CONFIRMED... worth a direct verification pass before assuming complete or incomplete") undersells what's actually there. The accurate status is: **checkpoints and severity follow-ons are built and mostly working (39/45 tests passing) but have 6 real, confirmed test failures needing investigation; narrative modulation and Aptitude addenda are confirmed not started.** Not "unconfirmed" — confirmed, with a specific, mixed, evidence-based answer.
