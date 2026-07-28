# PRV3 Report Depth Initiative

## Context

Fact-finding this session (see conversation log, Session with commit `ee48861` and the subsequent full-payload inventory) established that the private diagnostic report is thin by design, not by accident: most of the current rendering gap is either data that never reaches the payload, data that reaches the payload but isn't rendered, or content that genuinely doesn't exist anywhere yet. Pete has approved treating this as a full four-tier initiative rather than a single fix. This document is the durable plan — written down now per standing protocol, after the `/diagnostic` reskin lost its Stage 4-5 scope by living only in conversation.

Four tiers, ordered by how much new engineering/content each requires, not by priority. Tier 1 can proceed independently and immediately. Tiers 2 and 4's schema questions must go to Gemini before any Claude Code building starts on either. Tier 3 is fully independent of the others. Tier 4's content-authoring sub-items depend on Tier 4's schema questions being resolved first.

---

## Tier 1 — Render already-computed content (no new engineering, display only)

Data the engine already computes and already sends to the browser inside `PrivateOutputPayload`, but `PrivateOutput.tsx` never reads it.

- `synthesis.framing_text` and `synthesis.observable_indicators[]` — generated every session already (measured at ~125-130 words per session from real test runs), present in the payload, never rendered in `PrivateOutput.tsx`. Currently only surfaced on the separate `ShareableOutput.tsx` card.
- `secondary_states[]` — names + weights for other identified conditions, currently entirely unacknowledged on the report. No prose exists per secondary state today; this is a completeness/acknowledgment fix, not a content-depth fix.
- `asset_score.primary_asset_domain` — a short category label (e.g. "Governance Discipline"), computed server-side via `_compute_asset_score()`, never sent to the client at all (dropped at the `session/answer/route.ts` layer, not just unrendered).

**Status: ready to build, no Gemini gate needed.** Pure rendering and payload pass-through — no new data flow, no new architecture, no new LLM call shape.

**Status update: DONE. Committed 3710f37.** All three sub-items built in one commit: framing_text/observable_indicators rendered in PrivateOutput.tsx, secondary_states rendered as closing acknowledgment, primary_asset_domain threaded through both Path 1 (answer/route.ts) and Path B (result/route.ts) plus PrivateOutput.tsx render. One correction to this doc's original framing: primary_asset_domain was not "dropped at the route.ts layer" as originally described -- it had no field on PrivateOutputPayload at all yet, one layer earlier than stated. One scope addition beyond original plan: Path B was included (not originally scoped as Path-1-only, but the value is Path-independent so both routes now carry it). Follow-on fix required: DevDiagnosticPreviewPayload (web/lib/dev-diagnostic-preview.ts) needed a matching field addition, caught by tsc, not proactive discovery -- worth remembering that grep-based searches for PrivateOutputPayload references will miss deliberately-separate matching-shape types.

---

## Tier 2 — Wire existing, tested, unused engine functions into the output contract

Real functions that already exist, are Gemini-reviewed, and are unit-tested, but are never invoked during a live session.

- `compute_causation_pattern()` (`engine/output.py`) — SPOF vs. Diffuse Causation classification (`insufficient_signal` / `single_point` / `diffuse`). Docstring states directly: "not currently threaded into the engine output contract... not wired into `assemble_output()`."
- `compute_cascade_risk()` (`engine/accumulation.py`) — cross-dimensional cascade risk (dispersion × intensity). Same status — defined, tested, never called from `contract.py`, `main.py`, or `output_synthesis.py`.

**Status: needs a Gemini structural review before building.** The underlying math already exists and is already cleared, but adding either to the output contract is genuine output-contract/architecture surface area (new top-level payload fields, new client-facing meaning) — **not yet sent to Gemini.**

**Status update: DONE, ahead of this initiative's own sequencing.** Both compute_causation_pattern() and compute_cascade_risk() were wired into the output contract under a separately-tracked effort (Diagnostic Dimension Expansion, see prompts/diagnostic-dimension-expansion.md), committed 1b75a1b and f4ee405 respectively, before this doc's own "needs a Gemini structural review before building" gate was invoked. This happened because the two initiatives were scoped and tracked independently and the overlap wasn't caught until Report Depth Initiative's Tier 1 build began. No harm done -- Gemini did review compute_cascade_risk() during Diagnostic Dimension Expansion's own process (see that doc), so the substance of the gate was satisfied, just not procedurally through this doc's own sequencing. Flagging for the record: when two plan docs reference the same underlying engine functions, check for overlap before either one's build phase starts, not after.

---

## Tier 3 — Friction tax calibration

- `engine/friction_tax.py::compute_friction_tax()` exists and is more detailed than the current payload type suggests — it returns `org_size_label`, `severity_scalar`, and `calibration_complete` in addition to `low`/`high`/`currency`. But every value in `STATE_MULTIPLIERS` (57 states) and every `_ORG_SIZE_BANDS[...]["band_low"]` value is `None`. This is real calibration work, not a wiring fix — the function isn't even called anywhere in the live pipeline today, and would return `calibration_complete: False` for every session even if it were.

**Status: separate thread, not blocking Tiers 1/2/4.** Needs its own calibration pass — likely warranting the same rigor as the original 57-state calibration campaign (Sessions 16-29), since populating `STATE_MULTIPLIERS` and org-size revenue bands from real source research (McKinsey, SHRM, Gallup benchmarks already flagged in the module's own docstring) is a comparable scope of work, not a quick patch.

---

## Tier 4 — New content, doesn't exist anywhere yet

- **A hook-worthy headline field** — new LLM-generated content with no equivalent in the current 7-field synthesis schema.
- **Richer per-state descriptive prose** — `states.py`'s `StateProfile` dataclass has no prose field at all today, only short category-label lists (`liability_axes`/`asset_axes`, 2-3 items each). Closing this needs either a new authored-content pass across all 57 states (similar in shape and scale to the 146-option `observation_text` authoring project completed this session) or an expanded LLM synthesis field.
- **Real resolution-family descriptions** — `RESOLUTION_FAMILY_DESCRIPTIONS[...].description` is literally the placeholder string `"COPY PENDING"` for all 4 families today. Real authored content, not LLM-generated — matches how resolution_family names and blurbs are already handled elsewhere in the system (static per-family copy, not per-session generation).
- **Visual/layout treatment for "color and dynamism"** — a frontend-design pass, separate from any of the content decisions above. More text blocks alone doesn't address this; it's a distinct design question.

**Status: needs a Gemini structural review** (new synthesis fields mean a new paid LLM call shape) **and** needs Claude.ai content-authoring passes for the two authored-content sub-items, same pattern as this session's `observation_text` work. **Not yet started in any way.**

---

## Sequencing note

- Tier 1: proceed independently and immediately whenever building resumes.
- Tier 2: Gemini structural review first, then build.
- Tier 3: fully independent — can run in parallel with any other tier, on its own calibration timeline.
- Tier 4: Gemini structural review on the schema question first; the two authored-content sub-items (state prose, resolution-family copy) cannot start until that review resolves what the schema actually needs.

This is a planning document. No tier has been built as part of writing this file.
