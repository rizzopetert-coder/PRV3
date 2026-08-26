# Narrative Modulation (Phase 3) — Gemini Architecture Review Request

Durable request file. Continuing the narrative modulation workstream — the last genuinely unstarted piece of Path 1, per this session's own closed-out status (`tools/_mob.txt` Section 13a, Path 1 Phases 2-4 row). This is a new LLM call in the live flow, a new session field, a new route, and new UI — the same class of multi-file, data-contract-touching decision the transaction-path work routed through Gemini earlier this session. **No code has been written.** This document is the only artifact produced so far.

---

## Context

**What's fully built, confirmed by direct read this session:** `engine/narrative.py` is complete — `extract_signals()` (a real, working Claude call with a locked system prompt extracting dimensional signals + severity indicators from free text), `build_modulation_vector()` (confidence-gated, confirmation-and-elevation-only weighting — a signal can only strengthen a field the accumulated vector already has *some* signal in, never introduce a new one), and `enforce_state_probability_ceiling()` (the LOCKED 12-percentage-point cap, with proportional redistribution). `NarrativeModulationEngine` wraps all three cleanly. `STATE_PROBABILITY_CEILING=0.12`, `CONFIDENCE_FLOOR=0.15`, and `SEVERITY_CEILING=0.25` are all declared LOCKED/CALIBRATION-TARGET constants. This is genuinely done and tested, not a stub — same standard as everything else in this engine.

**The trigger rule is also built:** `engine/checkpoint.py::narrative_should_fire()` — fires early at Q27 if entropy exceeds `THRESHOLD_Q27`, otherwise always fires "after Q34," never twice (an `already_fired` guard).

**The wire-shape gap, confirmed by direct read of both sides:** `evaluate_checkpoint()` computes `narrative_trigger` internally, but `run_checkpoint()` (`engine/main.py`) drops it from the response dict — only `{entropy, threshold, fires, distinguishers, top_cluster}` cross the boundary. `CheckpointResultPayload` (`web/lib/engine-client.ts`) has no `narrative_trigger` field at all. **The signal that would tell the frontend "ask the narrative question now" has never once reached the web layer.**

**What has zero code anywhere, confirmed by repo-wide search, not assumed from the "NOT STARTED" label:** the actual principal-facing prompt. P-04 (locked governing principle) requires it be "dynamically generated. Not static." `build_narrative_prompt_context()` assembles the raw ingredients (top 1-3 states by rank/score/distance, current entropy) but nothing turns that into words a principal reads — and the spec is explicit that the prompt must never name states directly ("observational framing only"). No route, no session field, no UI exists to collect the response either.

**A real, deeper gap found during this scoping pass, not previously flagged anywhere:** `SeverityIndicator` (narrative.py's extracted severity signals — `indicator_text` + `confidence`) has **no defined path into `SeverityEngine`**. `SeverityEngine.add_input()` consumes `SeverityInput` objects, whose real fields (`trigger_question_id`, `severity_follow_on_id`, `duration_band`, `population_band`, `prior_failed_resolution`, `financial_indicators`, `named_condition`) have no overlap with `SeverityIndicator`'s shape at all. `SEVERITY_CEILING` (0.25) is declared but referenced nowhere in `narrative.py`'s own logic — `apply_narrative_modulation()` only ever applies `STATE_PROBABILITY_CEILING`. This isn't a wiring gap like the others; it's an unresolved design question the spec constants imply an answer to but no code anywhere provides.

**The downstream consumer is already ready, which narrows the real gap:** `engine/output_synthesis.py::synthesize()` already accepts `narrative_response: str = ""` as a parameter and threads it into the synthesis prompt. Nothing currently passes anything but the hardcoded `""` (`engine/main.py`, both call sites), but the acceptance point already exists — this is a smaller gap than the extraction/generation side.

**Established precedent for this exact kind of call, confirmed by direct read:** `output_synthesis.py::synthesize()` is the closest analog — a dynamic, principal-facing LLM-generated text, called from Python directly (`import anthropic`, `_anthropic.Anthropic(max_retries=0)`), not proxied through Next.js. Its `timeout=15.0` is LOCKED, Gemini-reviewed, Pete-approved, grounded in real Production latency data (6/6 samples, 7.4-13.6s) — a hard-won number from a real prior incident (`tools/_mob.txt` Section 13a, "Synthesis pipeline failing on Production" row), not a guess. On any exception, it returns a static fallback rather than ever blocking the live flow. `extract_signals()` (narrative.py itself) follows the same `import anthropic` / graceful-fallback shape already. Any new narrative-prompt-generation call should mirror this pattern exactly, not invent a new one.

**A real sequencing ambiguity, worth flagging rather than assuming either way:** the spec's "always fires after Q34" was written when Q34 was the literal last core question. It no longer is — `PHASE_1_QUESTION_SEQUENCE` now runs through Q51 (42 core positions before checkpoint/severity splices, per this session's own live-verification work). Does "after Q34" mean the literal question labeled Q34 (now mid-sequence), or "the last core question" (now Q51)? Nothing decides this either way in code or spec comments.

**A related flow-control question this raises:** if narrative fires at completion, the current `isLastQuestion` branch (`session/answer/route.ts`) goes straight from the final answer to `invokeComplete()`. Introducing "narrative might need to fire before completion can proceed" means that branch can no longer assume the last answered question always completes the session — a real change to completion sequencing, not just an additive field.

---

## Existing conventions to follow

- **Route shape**: `web/app/api/diagnostic/session/{start,answer,resume}/route.ts` — `NextRequest`/`NextResponse`, manual validation (no schema library), `{ error: string }` on failure.
- **Session mutation**: `getSession()` → mutate → `saveSession()`, sliding 6-hour TTL, same pattern this session's own completion-branch fix (`saveSession()` before `invokeComplete()`) just reinforced.
- **Engine call boundary**: Python owns all real LLM calls directly; Next.js never talks to Anthropic itself for anything touching the accumulation engine (`/api/interpret`'s `buildInterpretationPrompt` is Path B's self-select interpretation feature, unrelated to Path 1's accumulation engine — not a counter-example).
- **P-03 boundary**: no scoring internals (`dimensional_contributions`, raw vector values, state_ids as principal-facing labels) ever reach the client — `get_question_copy()`/`invokeQuestionCopy()` is the existing enforcement precedent to mirror for anything narrative-prompt-related that reaches the browser.

---

## Proposed architecture (for review, not yet built)

1. **Wire-shape fix**: add `narrative_trigger: bool` to `run_checkpoint()`'s return dict (`engine/main.py`) and `CheckpointResultPayload` (`engine-client.ts`). Small, additive, no behavior change until something reads it.
2. **New generation function**, `engine/narrative.py` (or a new small module, open question below): `generate_narrative_prompt(context: dict, model=..., client=None, timeout=15.0) -> NarrativePromptResult`, mirroring `output_synthesis.py::synthesize()`'s exact pattern — direct `anthropic.Anthropic(max_retries=0)`, the same 15.0s LOCKED timeout (no reason to re-derive a new number when a real-data-grounded one already exists for the same latency class of call), static fallback text on any failure, never blocks the live flow. Input: `build_narrative_prompt_context()`'s existing output. New system prompt needed (real content-authoring work, not just wiring) enforcing the "observational framing only, never name states" constraint — a genuinely new locked artifact, worth Gemini's specific review of the actual prompt text, not just the plumbing around it.
3. **Static fallback prompt**: a single well-written, state-agnostic open question, used verbatim whenever the LLM call fails — must not depend on the LLM at all, matching `get_fallback_synthesis()`'s role for the synthesis call.
4. **Session schema**: `DiagnosticSession` gains `narrative_fired: boolean` (default `false`) and `narrative_response: string` (default `""`, mirrors `answers_log`'s append-once-then-read-at-completion shape) — the latter needed since `synthesize()` already has a parameter waiting for it.
5. **New route**, `POST /api/diagnostic/session/narrative`: `{session_id, narrative_text}` → runs `extract_signals()` + `apply_narrative_modulation()` server-side, updates `session.accumulated_vector`, sets `narrative_fired=true` and `narrative_response`, returns the next question exactly like `session/answer` does. **Severity indicators are explicitly NOT threaded anywhere in this proposal** — see the open question below; building a plausible-looking but invented mapping would be worse than leaving it out and flagging it.
6. **Completion-branch change**: at the point `session/answer` would otherwise complete, check `narrative_fired` — if the trigger condition is met and it hasn't fired yet, return a narrative-prompt response instead of completing; only proceed to `invokeComplete()` once `narrative_fired` is true (or the session never met the trigger condition at all).
7. **Frontend**: `DiagnosticFlow.tsx` gains a `narrative` phase (free-text textarea, submit → the new route → continue), gated on the wire-shape fix in item 1 actually surfacing `narrative_trigger`.
8. **`engine/main.py`**: `run_accumulated_engine()` gains `narrative_response: str = ""`, threaded straight into the already-waiting `synthesize()` call — the one genuinely small, low-risk part of this whole proposal.

---

## Open questions for Gemini

1. **The severity_indicators → SeverityEngine gap.** `SeverityIndicator` and `SeverityInput` have no shape overlap. Is there a real, intended mapping (e.g., a severity indicator's `confidence` maps to some synthetic `duration_band`/`named_condition` proxy, bounded by `SEVERITY_CEILING`), or was this always meant to feed severity a different way entirely (e.g., a direct tier-nudge at output stage, never through `SeverityEngine.add_input()` at all)? State a recommendation grounded in the spec's actual IV.1/V wording, not an invented mapping.
2. **"After Q34" — literal question or "last core question"?** Given the sequence has grown past Q34 since the spec was written, which does the trigger rule actually mean, and does `narrative_should_fire()`'s `checkpoint_position: "Q27" | "Q34"` parameter need to become position-based rather than a hardcoded string?
3. **Where does `generate_narrative_prompt()` belong** — a new function in `narrative.py` itself (co-located with extraction, same file already does both directions for `output_synthesis.py`'s pattern... actually `output_synthesis.py` only generates, doesn't extract — `narrative.py` would be the first file in this engine doing both directions of an LLM exchange) or a new dedicated module? Recommend, don't just note the option.
4. **Completion-branch sequencing risk.** Given this session's own recent completion-path bug (a downstream failure leaving a session stuck with no saved progress), does deferring completion behind a possible narrative phase introduce a similar new stuck-state risk, and if so what's the safe shape (mirroring the `saveSession()`-before-engine-call fix already just shipped)?

---

## Verification requirement

Same standard as every prior architecture review this project runs. Any claim about this codebase's existing patterns must cite the specific file/line it's grounded in; any claim about the Anthropic API must be checked against current documentation, not recalled from training data — this project's history includes multiple caught instances of confident-but-wrong technical claims slipping through review (`tools/_mob.txt` Section 13a).

---

## Not asked here

No code written, no route created, no session field added, no prompt text authored. Scoping and a recommended approach only — Pete reviews Gemini's response, confirms explicitly, and only then does any build begin.
