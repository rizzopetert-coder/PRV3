# Session Handoff — MOB v4.316

Direct extract/reformatting of this session's Section 16 entries (spanning MOB v4.311 through
v4.316, terminal Claude Code, one continuous session). Section 16 is authoritative; this is a
portable copy for quick reference, not a second independent record.

## What happened, in sequence

**1. Legal/Compliance exposure "25,000-25,000" display bug — root-caused, fixed, shipped.**
Root cause: `_CLUSTER_4B_FLOOR = 25_000.0` (`engine/friction_tax.py:2314`) producing a genuine
TRUE equality between the low and high bounds for Cluster 4b cases, not a rounding artifact.
Fixed with an exact-equality display fallback in `web/components/PrivateOutput.tsx` (lines
~393-409). New Cluster 4b/score=1 fixture added to `tools/test_contract.py` (148 → 150 passed).
MOB v4.312.

**2. `signal_map_context`/Trajectory silent-failure bug — found and fixed.** This session's own
earlier `option_ids` widening had left `engine/main.py`'s `_build_signal_map_context()` and
`_replay_partial_vector()` reading a stale singular `option_id` key instead of the list-shaped
`option_ids`, silently nulling synthesis context and trajectory data for every real Path 1
session since that widening shipped. Fixed both functions to read `entry.get("option_ids")` as a
list; `run_accumulated_engine()`'s final return corrected to pass `answers_log=answers_log`
through to `assemble_output()`. 6 new regression checks added to `tools/test_main.py` (36 → 42
passed), including a Q06 multi-select proof. MOB v4.313.

**3. Friction tax ledger shipped end-to-end, plus the org_type threading fix it surfaced.**
Gemini-gated architecture across two rounds. New `friction_tax_ledger` field: per-condition
risk/dollar/top-contributing-answers, built via `_build_friction_tax_ledger()` in
`engine/contract.py` (an answer-replay technique using a scratch `AccumulationSession`), wired
through `web/lib/types.ts`, `engine-client.ts`, `diagnostic-completion.ts`, the `result`/
`share/create` API routes, and rendered in `PrivateOutput.tsx` as an accordion
(`<details open>`/`<summary>`) using `severityAccentTokens` styling, with Pete's final-approved
footnote copy. Surfaced a real, separate production gap in the same area: Phase 1 never
collected `org_type` at all, silently nulling `friction_tax_estimate` and the new ledger's
`dollar_exposure` for every real session — fixed by threading `org_type` through
`DiagnosticFlow.tsx`'s intake form (new dropdown, `ORG_TYPE_OPTIONS`), `types.ts`, the session-
start validator, and `engine/main.py`'s `_locked_intake_to_engine_intake()`. 6 mechanical
TypeScript fallout sites fixed in the same commits as the type change that caused them. New
ledger fixtures added to `tools/test_contract.py` (150 → 157 passed). Full verification: 11-script
engine suite, `tsc --noEmit`, 175-profile calibration confirmed unchanged at 171/175. MOB v4.314.

**4. Two durable planning docs written.** `prompts/candidate-principle-all-data-is-useful.md` —
a candidate governing principle (Provisional Hold): a silently-null computed value is an active
loss, not a harmless edge case, directly motivated by items 1 and 2 above.
`prompts/asset-integration-into-resolution-scope.md` — a scope-decision doc for integrating
identified assets into recommendations, with an explicit record of a mid-session reconsideration
that reinstated Option 3 rather than silently folding it in. Documentation only, no version bump.

**5. Quarterly Step-Back #4 — dual-sourced, completed and reconciled, no correction needed.**
Independent cold pass: `prompts/prv3-quarterly-step-back-2026-09-19-cc-independent.md`.
Reconciliation: `prompts/prv3-quarterly-step-back-2026-09-19-reconciled.md`. Unlike Step-Back #3
(the Loureiro correction), both assessments agreed on all substantive findings this cycle — no
real divergence to adjudicate. Both independently connected this session's two silent-failure
bugs (items 1 and 2) to the ALL-DATA-IS-USEFUL candidate principle — convergent, not copied. Two
doubly-verified findings: the Dropbox Sign `403` on env-var listing (now confirmed across two
step-backs), and a `fastapi` framework-field oddity. The "Vercel 10GB" notification thread from
earlier the session was fully resolved: **Function Storage**, a cumulative retained-bundle-size
measure across the 11 currently-retained deployments, not a deployment-count problem (that was
already fixed 2026-09-05 and confirmed still holding). Recommendations carried through unchanged
from Step-Back #3 (attorney-review gate as the real critical path, pilot mechanism as the
leading near-term lever). Next step-back due **2026-10-03**. MOB v4.315.

**6. Diary-write integrity audit, plus a gated future task logged.** Audited this session's own
Section 16 entries against real tool-call history: 3 entries found falsely claiming a diary write
had happened when none had, corrected in place with dated amendment markers (diary is append-
only, so the correction is additive, not a rewrite of history). Separately, investigated the
Vercel Function Storage driver with real numbers and declined to remove `numpy` from
`engine/accumulation.py` without gates — captured as
`prompts/candidate-future-task-numpy-removal.md`, explicitly gated on (a) a confirmed per-
deployment storage number isolating numpy's actual share, not an assumption, and (b) its own full
calibration re-run when picked up, never bundled into unrelated cleanup. `accumulation.py` itself
was not touched.

**7. `tools/prv3_diary.py` Bug A/B — investigated, self-corrected, fixed, verified.** Found: 50%
of real write attempts (2 of 4) this session were reported as unretrievable on a following read.
**First diagnosis was wrong** — a write-path/`close()`-during-shutdown durability theory, shipped
as a fix using `Memory.get(id)` for verification. Caught the contradiction before it reached git
(verification reported `True` but a fresh independent read still failed), traced the real cause,
and fully rewrote the fix rather than let the wrong diagnosis stand. **Real cause:**
`Memory.get_all()`'s undocumented default `top_k=20`, silently truncating the candidate pool
before `read_recent()`'s own slicing/sorting ever ran. The claude-code agent already had 29 real
entries — 9 already past the silent cap — and both "unretrievable" entries were proven present,
correctly timestamped, sitting just past position 20 the entire time. **No data was ever lost or
non-persisted.** Fixed via a new `_GET_ALL_TOP_K = 5000` constant applied in both `write_entry()`
(read-after-write verification, now checking the same `get_all()` path `read_recent()` actually
uses, not a direct `get(id)` lookup that would bypass the truncation entirely) and `read_recent()`
itself. CLI now prints a distinct `WARNING: ... verification FAILED` message on a genuine
verification failure. Verified end to end via the real CLI: a fresh write, confirmed `verified:
True`, then independently re-confirmed via a separate `read --last-n 30` call showing all 29 real
entries in place. Separately confirmed: the local-Qdrant/no-cloud/`infer=False` architecture is
the intentional, Gemini-reviewed post-MemPalace-retirement design (2026-08-26 record), not a gap.
No calibration re-run needed (diary tool is outside the engine). MOB v4.316.

## Open items carried forward, not acted on this session

- **`gh` CLI still not installed** — a `winget install` attempt this session failed on an
  unattended UAC prompt with nobody present to approve; needs Pete to run it interactively.
- **Local dev Upstash Redis credentials missing** (`UPSTASH_REDIS_REST_URL`/`TOKEN` unset
  locally) — informational only, production already has them, does not affect the org_type fix's
  validation-layer verification (which succeeded before hitting this unrelated failure).
- **Function Storage remediation not executed** — either a dashboard-only `deploymentsToKeep`
  reduction, and/or the gated numpy removal task, neither actioned this session.
- **Dropbox Sign provisioning still unconfirmed** — a `403` on env-var listing, now confirmed
  twice independently across two step-backs; Pete checking the Vercel dashboard directly is the
  fastest remaining close.
- **Attorney-review gate and the pilot-mechanism recommendation** — unchanged from Step-Back #3,
  Pete's call, no forced check-in.
- **Next Quarterly Step-Back** due on or near **2026-10-03** (locked biweekly cadence).

## Files to attach next session, by likely task

- **Always:** `tools/_mob.txt` (current version, v4.316).
- **If picking up the gated numpy-removal task:** `prompts/candidate-future-task-numpy-removal.md`, `engine/accumulation.py`, `requirements.txt`, `vercel.json`.
- **If resuming the attorney-review gate or pilot mechanism:** the Step-Back #4 docs (`prompts/prv3-quarterly-step-back-2026-09-19-cc-independent.md`, `prompts/prv3-quarterly-step-back-2026-09-19-reconciled.md`) as the last-confirmed baseline.
- **If touching the diary tool again:** `tools/prv3_diary.py` (both fixes and their comments are load-bearing documentation of the real root cause — read before changing `_GET_ALL_TOP_K` or the verification path).
- **If continuing the ALL-DATA-IS-USEFUL principle's Provisional Hold:** `prompts/candidate-principle-all-data-is-useful.md`, `prompts/asset-integration-into-resolution-scope.md`.
- **If the next Quarterly Step-Back is due:** both Step-Back #4 docs listed above.

## MOB version confirmation

Header (`tools/_mob.txt`) reads `MOB v4.316`. CLAUDE.md's Key References table cross-reference
was updated in lockstep with every version bump this session (v4.311 through v4.316, each pairing
confirmed individually, not assumed to have held from the prior fix).
