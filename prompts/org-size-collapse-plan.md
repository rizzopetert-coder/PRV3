# organization_size string|number Collapse — Build Plan

Status: ready to execute. Step 1 (Redis verification) is complete and clear —
see the record below. This document covers Step 2 only.

## Step 1 record (for the MOB entry, not re-derived here)

- `share:*` keys: 0 live keys. Nothing to check, nothing to wait for.
- `diagnostic-aggregate` list (unbounded, no TTL — confirmed no `expire` call
  anywhere touching it): 15 entries found, 4 carried the legacy string
  `"100-249"` — all dated 2026-08-26/27, *after* the 2026-08-05 redesign,
  proving this wasn't decaying pre-redesign data but an active, ongoing
  source. Source confirmed: `tools/diagnostic_fast_forward.py`'s
  `DEFAULT_INTAKE["organization_size"] = "100-249"` (industry field matches
  exactly: `"Technology"` in both). List confirmed write-only — grepped the
  whole repo, nothing reads `diagnostic-aggregate`/`AGGREGATE_KEY` back — so
  the 4 stale entries carried zero live crash risk, but proved the "wait for
  the TTL" plan didn't apply to this half of the item at all.
- **Pete's decision, 2026-08-29: purge the 4 bad entries now, fix the tool.**
  Both done: the 4 entries removed via index-targeted `LSET`/`LREM` (verified
  after — `LLEN` 15 → 11, `LRANGE` re-checked, all 11 remaining entries
  numeric). `tools/diagnostic_fast_forward.py`'s default changed to `175`
  (numeric midpoint of the old bucket) — done, uncommitted, folded into this
  pass's commits below.

Redis is confirmed clear on both structures. Safe to remove string-branch
handling.

## Step 2 — exact changes

### 1. Type declarations
- `web/lib/types.ts:100-105` — `ShareableIntakeEcho.organization_size:
  string | number` → `number`. Remove the "TEMPORARY" comment block above it.
- `web/lib/session-store.ts:253-260` — `AnonymizedCompletion.organization_size:
  string | number` → `number`. Remove its matching comment.
- `PrivateIntakeEcho extends ShareableIntakeEcho` inherits the field —
  no separate edit needed there.

### 2. TypeScript consumers
- `web/components/ShareableOutput.tsx` — remove the `typeof` branch;
  `orgSizeDisplay` becomes unconditional `` `~${organization_size} employees` ``.
- `web/components/DiagnosticFixturePicker.tsx` — `organization_size: ""` →
  `0` (matches this fixture's existing all-placeholder-fields convention;
  every other field here is also an empty/unset sentinel for a synthetic
  dev-preview payload).
- `web/app/api/diagnostic/session/start/route.ts` (`validateIntake`) —
  `validOrgSize` collapses to the number-only branch; remove the
  string-length branch and the "soft transition" comment.
- `web/app/api/result/route.ts` (`parseOrgSize`) — simplified, kept as a
  small named function (not inlined — the exact same coercion is now needed
  in `share/create/route.ts` too, see below): pass through a real finite
  number, otherwise attempt `Number(value)`, otherwise `0`. No more
  string-passthrough branch.
- `web/app/api/diagnostic/condensed/answer/route.ts`
  (`toPrivateIntakeEchoShape`) — `organization_size: ""` → `0`, same
  "not collected, numeric sentinel" reasoning as the fixture picker.
- **`web/app/api/share/create/route.ts`** (Pete's explicit instruction) —
  replace the raw `(engineIntake.org_size as string) ?? ""` cast with the
  same real coercion logic `parseOrgSize` now uses, not just a type-only
  change. Duplicated as a small local function (matching this project's own
  precedent — `STATE_RESOLUTION_FAMILY`'s existing triplication, and the
  "three similar lines beats premature abstraction" standing preference)
  rather than a new shared module for a 4-line helper.

### 3. Python engine
- `engine/main.py` (`_locked_intake_to_engine_intake` adapter) —
  `intake.get("organization_size", "")` → `intake.get("organization_size", 0)`.
  A missing key is a real anomaly now (both the numeric stepper and the
  tightened `validateIntake` guarantee a number), so the fallback becomes an
  explicit numeric sentinel instead of a value that itself violates the new
  contract.
- `engine/friction_tax.py` `resolve_headcount_bucket()` — remove the
  `isinstance(headcount, str)` block and its docstring paragraph describing
  the legacy-string tolerance; add the now-genuine `headcount: int` type
  hint.
- `engine/friction_tax.py` `compute_friction_tax()` — no change needed.
  Confirmed: its first line already calls `resolve_headcount_bucket(org_size)`
  before anything else, so it inherits the simplification automatically; its
  own `org_size: int` signature was already correct.
- `engine/accumulation.py:92` — `IntakeData.headcount: int` already correct,
  no change.
- `engine/contract.py:542,557` — pure passthrough (`org_size=session.intake.headcount`),
  no change needed.
- `engine/output_synthesis.py` — f-string interpolation, type-insensitive,
  no change needed.
- `engine/main.py` `run_condensed_engine()` docstring — the "crashes on the
  empty-string default" claim is corrected, not just deleted: replaced with
  the real, still-true reason Category D bypasses `assemble_output()` —
  its intake is a synthetic placeholder with no real headcount collected,
  so a friction-tax number computed against it would be meaningless, not a
  crash-avoidance measure specifically.

### 4. Test/fixture files
- `tools/test_main.py` — already `152`, no change.
- `web/lib/engine-client.test.ts` — `BASE_INTAKE.organization_size: "51-200"`
  → `150`. This fixture was never testing string-tolerance (the file's own
  header says `tsc --noEmit` is the real enforcement mechanism here, for the
  `CompletePayload` shape) — it just needs to keep type-checking under the
  new contract. Converting, not deleting.
- `tools/test_output_synthesis.py` — 4 occurrences of
  `"organization_size": "medium"` inside `_build_synthesis_prompt()` calls →
  `150`. None of these tests assert anything about headcount content in the
  generated prompt (they check `state_name`/`severity_tier`/
  `resolution_family`/`narrative_response`/`significant_events` inclusion) —
  `"medium"` was incidental filler, not coverage of the string-tolerance
  path (that path lived in `resolve_headcount_bucket()`, which
  `_build_synthesis_prompt()` never calls). Converting for contract
  consistency, not because anything here would break.
- `tools/diagnostic_fast_forward.py` — already fixed (`175`), see Step 1.
  Does not resolve this tool's separate rework-or-retire open status.

### 5. Verification
- `tsc --noEmit`, full `vitest` run, full Python engine suite (11 scripts)
  plus `calibration_runner.py`.
- This touches API route validation logic (`session/start`, `share/create`)
  — qualifies for the standing live-production-round-trip rule (locked
  2026-08-27). Real HTTP round trip against Production after deploy, not
  local-clean only.

### 6. Commits
Grouped, not one giant commit:
1. Type declarations (`types.ts`, `session-store.ts`)
2. TS consumers (`ShareableOutput.tsx`, `DiagnosticFixturePicker.tsx`,
   `session/start/route.ts`, `result/route.ts`, `condensed/answer/route.ts`,
   `share/create/route.ts`)
3. Python engine (`main.py`, `friction_tax.py`)
4. Test/fixture files (`engine-client.test.ts`, `test_output_synthesis.py`,
   `diagnostic_fast_forward.py`)
5. MOB update, own commit, after live verification passes

### 7. MOB update
Close the Decision Register item and Priority Queue's top item. Record: the
Redis verification result (including the mid-stream discovery that the
aggregate list had no TTL and an active legacy-format source, and Pete's
purge-and-fix decision), what shipped, commit hashes, live-verification
result, version bump.
