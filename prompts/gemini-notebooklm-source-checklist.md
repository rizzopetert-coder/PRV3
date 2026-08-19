# Gemini NotebookLM Source Checklist — PRV3 Architecture Reviews

Status: **Durable, re-runnable checklist.** Not a one-time snapshot — re-derive this
against the real repo (don't carry forward an old version's assumptions) at each
Quarterly Step-Back, or any time a Gemini review cites a file/function that isn't
recognized, the way `output-renderer.ts` vs. `PrivateOutput.tsx` surfaced 2026-08-19.

Purpose: give Pete a direct checklist to verify or refresh the NotebookLM notebook's
actual source list against — not a description of what the notebook currently contains
(that wasn't checked this pass), a description of what it **should** contain, verified
against the real repository as of this session.

Every file below was confirmed to exist at the stated path when this list was built —
this is not carried forward from a prior screenshot or an earlier assumption.

---

## 0. Format constraint — confirmed real, applies to every code file below

**NotebookLM rejects raw source-code files by extension.** Confirmed directly (Pete,
2026-08-19): `.py` files are not accepted as uploads. The same restriction applies to
`.ts`/`.tsx` for the same reason — NotebookLM's accepted source types are Google Docs,
Google Slides, PDF, plain text (`.txt`), Markdown (`.md`), pasted text, and web links.
It does not recognize source-code extensions as a category, regardless of the file's
actual content being plain text underneath.

**Automated as of 2026-08-19 — `tools/export_gemini_sources.py`.** Run it and it
produces a single `gemini_export/` staging folder (repo root, gitignored) containing
every file from Sections 1-6 below, already in an accepted format: code files
(`.py`/`.ts`/`.tsx`) get a `.txt` extension appended with content otherwise byte-
identical to source; `CLAUDE.md` and `tools/_mob.txt` are copied as-is. A
`manifest.txt` lands in the same folder recording the git commit hash and timestamp
the export was taken at, plus every source-path → export-filename mapping. This
replaces the manual per-file conversion described in earlier versions of this doc —
see "How to use this" below for the actual workflow now.

---

## 1. Core engine files (`engine/`)

Confirmed against the real `engine/` directory listing, not assumed from a prior list.

| File | Why it matters for architecture review |
|---|---|
| `engine/severity.py` | Defines `SeverityResult`, `SeverityEngine`, `SeverityInput`, `SeverityAccumulator` — the exact data structures at the center of most architecture questions about severity. |
| `engine/main.py` | Orchestration — `run_engine()` (Path B), `run_accumulated_engine()` (Path 1), `accumulate_one_answer()`/`accumulate_answers()`. Where `severity_result` actually gets computed and threaded through. |
| `engine/output.py` | `OutputEngine`, routing/signal-floor gate (`rank_states()` + `check_signal_gate()`), `build_private_block()`/`build_shareable_block()`. |
| `engine/contract.py` | `assemble_output()` — the single function that builds the real VII.1 JSON contract for both Path 1 and Path B. `_TOP_LEVEL_SCHEMA`, `validate_schema()`, `_assemble_monitoring_metadata()`. |
| `engine/output_synthesis.py` | `_build_synthesis_prompt()`, `synthesize()` — the LLM-facing narrative construction. Confirmed this session to consume `severity_tier` directly; a real architecture-relevant file, not just supporting scaffolding. |
| `engine/friction_tax.py` | `SEVERITY_SCALAR` (the `{Emerging: 0.6, Entrenched: 1.0, Endemic: 1.4}` LOCKED multiplier), `compute_friction_tax()`. |
| `engine/accumulation.py` | `AccumulationEngine`, `rank_states()`, dimensional-vector scoring — the pipeline that runs and finishes *before* severity is ever computed. |
| `engine/checkpoint.py` | Q11/Q19/Q27 checkpoint entropy logic, distinguisher routing. |
| `engine/resolution_families.py` | Resolution-family routing, `apply_causation_override()`. |
| `engine/narrative.py` | Section IV narrative modulation — feeds `SeverityAccumulator.narrative_severity_addition`, currently confirmed dormant (see below), but the file any future wiring would touch. |
| `engine/data/questions.py` | `QUESTION_LIBRARY` — every `severity_trigger`/`severity_follow_on_id` wiring, `state_targets`, all 55 live trigger options across 32 SEVER-## IDs. The ground truth for any question/severity mapping claim. |
| `engine/data/states.py` | `STATE_PROFILES` — the 58-state taxonomy, `descriptive_prose`, dimensional vectors. |
| `engine/data/intake.py` | `IntakeData` — the intake schema every downstream function consumes. |
| `engine/data/salience.py` | `SALIENCE_PROFILES` — per-state weighting consumed by `rank_states()`. |
| `engine/data/fallback_synthesis.py` | Static fallback synthesis content, keyed by `(commercial_name, severity_tier)` — another severity-tier-keyed data source worth Gemini having visibility into. |
| `engine/data/jurisdiction.py` | Jurisdiction lookup table (transparency/retaliation/procedural flags). |
| `engine/data/validate.py` | Referential-integrity checks — useful for understanding which data-contract invariants are actually enforced today. |

**Deliberately not included, noted so the omission is a choice, not an oversight:**
`engine/test_profiles*.py`, `engine/test_suite.py` — these are the 172(+3) calibration
profiles' actual content (test *data*, not architecture) — too voluminous to be useful
as review context, and Gemini doesn't need every profile's answer sequence to review a
data-contract change. If a specific review needs calibration examples, attach the
relevant 2-3 profiles directly to that review's prompt instead of loading all of them
permanently into the notebook.

---

## 2. Calibration harness and API bridge

| File | Why it matters |
|---|---|
| `tools/calibration_runner.py` | `run_profile()`/`generate_answers()` — mirrors production's severity pooling structurally. Any engine-side architecture change needs this harness updated in lockstep, or the 172(+3)-profile suite silently stops reflecting real behavior. |
| `api/engine.py` | The FastAPI bridge — the actual HTTP surface (`/api/accumulate`, `/api/complete`, etc.) between the web layer and the Python engine. This is where wire-contract gaps live (e.g. the confirmed `AccumulatePayload` not carrying `trigger_question_id` today). |

---

## 3. Web-layer types, routing, and state

| File | Why it matters |
|---|---|
| `web/lib/types.ts` | `PrivateOutputPayload`, `ShareableOutputPayload`, `CondensedOutputPayload`, `StateRef`, `SeverityTier` — the web-side contract shapes. |
| `web/lib/engine-client.ts` | `EngineResult`, `AccumulatePayload`, `invokeAccumulate()`/`invokeComplete()` — the TypeScript mirror of the Python API's JSON shapes. |
| `web/lib/session-store.ts` | `DiagnosticSession`, `severity_inputs` storage, splice mechanics (`spliceLabel()`, `severityFollowOnAlreadyAsked()`), `PHASE_1_QUESTION_SEQUENCE`. |
| `web/lib/condensed-session-store.ts` | Category D's parallel, deliberately separate session infrastructure. |
| `web/lib/resolution-family.ts` | Engine-output-to-commercial-name translation, shared across web consumers. |
| `web/lib/book-manifest.ts` | `/book` content registry — where diagnostic output routes to published content; relevant whenever a review touches output routing broadly, not just severity. |
| `web/lib/book-state-index.ts` | Per-state mapping to `/book` pieces and `resolutionFamily` mirror. |
| `web/data/taxonomy.ts` | Web-side 58-state taxonomy mirror (dimension, signature groupings) — must stay in sync with `engine/data/states.py`. |

---

## 4. Live API routes (`web/app/api/`)

Confirmed against the real directory listing — every route currently present.

| File | Why it matters |
|---|---|
| `web/app/api/diagnostic/session/start/route.ts` | Session initialization, Path 1. |
| `web/app/api/diagnostic/session/answer/route.ts` | The real per-answer flow — severity input collection, splice logic, calls `invokeAccumulate()`. |
| `web/app/api/diagnostic/session/resume/route.ts` | Session resume path. |
| `web/app/api/result/route.ts` | Path B — builds `PrivateOutputPayload` from a direct `engineResult`. |
| `web/app/api/share/create/route.ts` | Builds and writes `ShareableOutputPayload` to KV. |
| `web/app/api/share/[id]/route.ts` | Reads a shareable output back from KV. |
| `web/app/api/diagnostic/condensed/start/route.ts` | Category D intake start. |
| `web/app/api/diagnostic/condensed/answer/route.ts` | Category D's answer/completion flow, builds `CondensedOutputPayload`. |
| `web/app/api/interpret/route.ts` | Self-selection Assembly flow (diagnostic entry point independent of the question sequence). |
| `web/app/api/dev/diagnostic-preview/route.ts` | Dev-only preview route — lower priority, but real and occasionally relevant to rendering-layer reviews. |

---

## 5. Live rendering components (`web/components/`)

| File | Why it matters |
|---|---|
| `web/components/PrivateOutput.tsx` | **The real live consumer that renders severity to an actual user.** Reads `payload.severity` directly. Confirmed live this session — was previously missing from architecture-review context while a dead file stood in for it. |
| `web/components/ShareableOutput.tsx` | Same pattern, shareable output — also reads `payload.severity` directly. |
| `web/components/CondensedOutput.tsx` | Category D's output renderer. |
| `web/components/DiagnosticFlow.tsx` | The real question-flow UI — severity follow-on splicing lives here (input side: which follow-on question gets asked next), distinct from the output-rendering role of the two files above. |
| `web/components/CondensedDiagnosticFlow.tsx` | Category D's flow UI. |

---

## 6. Governing and reference docs

| File | Why it matters |
|---|---|
| `CLAUDE.md` | Session protocol, standing rules, locked engine facts (58-state count, etc.), Workflow Governance Four-Tier Model — the rules any architecture review's recommendations need to respect. |
| `tools/_mob.txt` | Current MOB — Decision Register (Section 13a), locked decisions (Section 14), session history. The record of what's already been decided, so a review doesn't re-litigate settled questions or miss a standing constraint. **Always load the current version — this file changes every session.** |
| *(external, not in this repo)* **Current Principal Brief, v1.1** | Governs the whole project (P-01 through P-13 and beyond). **Must be sourced from wherever Pete maintains the current version (Drive / claude.ai project knowledge) — the repo's own copy is confirmed stale, see Section 7 below.** |

---

## 7. Explicitly exclude — remove from the notebook if currently loaded

Confirmed dead, stale, or otherwise wrong to treat as live architecture context. If any
of these are currently sources in the notebook, that's exactly the kind of drift this
checklist exists to catch — remove them, don't just skip re-adding them.

| File | Why it's excluded |
|---|---|
| `web/lib/output-renderer.ts` | **Confirmed dead code this session** — zero imports anywhere in the repo. If this is currently loaded in the notebook, it's actively wrong: a Gemini review reading it would reasonably describe it as the live render layer, exactly the mistake corrected this session. Remove and replace with `PrivateOutput.tsx`/`ShareableOutput.tsx` (Section 5). |
| `documents/PRV3-Principal-Brief.docx` | **Stale** — confirmed "Version 1.0, April 2026" by direct text extraction, superseded by the external v1.1 (Section 6). Still present in this repo (held back from the untracked-pile deletion only because it's cited by name in engine comments, not because it's current) — do not load it as "the Principal Brief" in the notebook. |
| `documents/PRV3_MOB_v1.3.md`, `PRV3_MOB_v1.8.md`, `PRV3_MOB_v2.8.md` | Old MOB version snapshots, deleted from the repo entirely (untracked-pile cleanup, 2026-08-18) — no longer exist at these paths at all. If the notebook has cached copies, remove them; `tools/_mob.txt` is the only current MOB. |
| `.claude/claude_code_brief.md`, `prompts/claude_code_brief.md` | Deleted this session — a pre-project-history engine-build kickoff brief referencing "45 states" and a MOB version format from before the current architecture existed. |
| Any `tools/patch_*.py` or `tools/diag_*.py` scratch script | One-off session patch/investigation artifacts, not architecture — including them adds noise without adding signal. The one narrow exception is `tools/calibration_runner.py` (Section 2), which is a real, load-bearing harness, not a scratch script. |
| `tools/patch_severity_follow_on_state_scoping.py` | Explicitly-flagged non-viable scaffolding — encodes an already-superseded gate design (top-1-only), confirmed this thread to operate at the wrong architectural layer entirely. Do not load as if it represents a real plan. |

---

## How to use this at the next Quarterly Step-Back

**Checking whether a re-export is even needed:** if a `gemini_export/manifest.txt`
from a prior run still exists, compare its `commit:` line against `git rev-parse
HEAD`. Identical means the last export already reflects current `main` — no need to
re-run or re-upload anything.

**Refreshing the notebook (the normal case, once this list itself is still accurate):**
1. Run `python tools/export_gemini_sources.py` from the repo root.
2. Open `gemini_export/` and upload its entire contents to NotebookLM, replacing the
   notebook's existing sources rather than adding alongside them (stale sources
   sitting next to fresh ones is its own drift risk).
3. Done — `manifest.txt` itself is also uploadable if you want the commit hash/
   timestamp visible to Gemini as context, though it's mainly for your own
   staleness-checking, not required reading.

**Re-deriving the list itself (only needed when the file set may have changed —
Quarterly Step-Back, or a Gemini review citing an unrecognized file):**
1. Re-run the directory listings this checklist is built from (`engine/`, `engine/data/`,
   `web/lib/`, `web/app/api/`, `web/components/`, `web/data/`) — don't assume the file
   set hasn't changed since this version was written.
2. For any new file that showed up: is it a real consumer/producer of something an
   architecture review would need to reason about, or a scratch/data file? Categorize
   accordingly (Sections 1-6 vs. the exclude list, Section 7).
3. For any file removed from the repo since this version: confirm it's actually gone
   (not just moved), and if the notebook still has it loaded, remove it.
4. Spot-check a small number of "is this dead code" claims the way `output-renderer.ts`
   was checked this session (repo-wide import search) — dead files silently accumulate
   and this is the cheapest point to catch them.
5. **If the file list changes, update both this doc's Sections 1-6 and
   `EXPORT_FILES` in `tools/export_gemini_sources.py` — they're deliberately not
   auto-synced (the script hardcodes the list rather than parsing this doc, since
   parsing prose-plus-tables reliably is more fragile than keeping two short lists
   aligned by hand). The script prints a warning on run if it finds a path in this
   doc's Sections 1-6 that's missing from `EXPORT_FILES`, but that check is best-
   effort, not a substitute for updating both.**
