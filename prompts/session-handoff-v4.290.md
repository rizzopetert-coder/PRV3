# Session Handoff — MOB v4.290

Direct extract/reformat of `tools/_mob.txt` Section 16's closeout entry for this session ("SESSION CLOSEOUT (2026-09-08, continuation session)..."). Section 16 is authoritative if these ever diverge.

---

## Files to attach next session

- `tools/_mob.txt` — always.
- `CLAUDE.md` — always.
- If picking up the **new z-index item** (Priority Queue item 1): `web/app/diagnostic/page.tsx` (the phase-transition bars), and `web/components/AssemblyPanel.tsx` (the mobile bottom-sheet trigger).
- If revisiting **PARTIAL coverage-threshold state verification** (Priority Queue item 2): `prompts/state-coverage-threshold-design.md`.
- If picking up the **`extreme_high_confidence` investigation** (Priority Queue item 3): the calibration runner and `prompts/scd-wcs-remediation-tracker.md`.
- If picking up the **v2 token migration question** (Priority Queue item 4): `web/app/globals.css`, `web/app/page.tsx`, `web/components/home/WayfindingGrid.tsx`.

## What happened this session, in one line

Self-select flow's "Take the diagnostic" gap closed: it never collected headcount/industry/org_type/jurisdictions, so `friction_tax_estimate` and `legal_tail_risk_exposure` could never price for this path. Added a pre-submit intake modal; found and fixed a real type-level blocker along the way (`headcount: string` would have silently defeated the modal's own purpose); live-verified end-to-end on production for the first time.

## Shipped and closed this session

1. **`SelfSelectIntakeModal.tsx` — new component.** Four fields (headcount, industry, jurisdictions, org_type), confirmed as the exact and complete set both consuming engine functions need by tracing every real consumer in `friction_tax.py` — not assumed. `org_type` is not a minor addition: it's a direct multiplier on `compute_friction_tax()`'s payroll baseline (`ORG_TYPE_SCALARS`) and gates Cluster 4's org_type-specific legal tracks, so its absence would have left `friction_tax_estimate` unable to complete at all, not just made legal pricing less precise.
   - Reused `DiagnosticFlow.tsx`'s `HeadcountStepper`, `INDUSTRY_OPTIONS`, and `JURISDICTION_OPTIONS` (the latter two now exported) rather than hand-maintaining a second field-option set.
   - `ORG_TYPE_OPTIONS` is a new constant, exact-matching `ORG_TYPE_SCALARS`' six keys, commented as mirroring that table as source of truth.
   - Jurisdictions: multi-select (matches what the engine's own multi-state compounding logic already supports).
   - Strict completeness gating: submission blocked until all four fields are filled — the engine's clean-degrade behavior from last round exists as a safety net, not an invitation to allow partial submission through the one flow built specifically to close that gap.
   - Explicitly did NOT reuse `DiagnosticFlow`'s `IntakeForm` or its `session/start` Q&A machinery — traced end to end and confirmed that path discovers states through sequential questions with no mechanism to accept pre-selected states; self-select already knows its states, so routing through `DiagnosticFlow` would have discarded that and forced redundant re-discovery. Standalone modal was the deliberate choice, not an oversight.

2. **Real blocker found and fixed before the component was built, not after.** `EnginePayload["intake"].headcount` and `ResultRequest.headcount` both declared `string`, but this session's earlier headcount-guard fix uses `isinstance(headcount, (int, float))` with no string coercion by design (garbage vs. a real number arriving as a string are indistinguishable to that guard). Had the modal built its submission as `headcount: String(65)` — the only way to satisfy the old type — every submission would have returned a clean 200 with silently null pricing, the exact same failure mode as the bug fixed earlier tonight, just quieter and now unfixable by inspection alone. Fixed by widening `headcount` to `number | string` in both `EnginePayload["intake"]` and `ResultRequest`; confirmed every existing blank-intake call site stays valid unchanged. `HeadcountStepper`'s submission path explicitly re-narrows `number | ""` to a definite number inline before it enters the intake object — confirmed by direct inspection of the real outgoing request body (via a fetch intercept, not by trusting the UI), which showed `headcount: 65` as a genuine unquoted JSON number.

3. **Gemini fabrication caught and dropped, same review as always.** Gemini justified reusing `HeadcountStepper` by claiming its increment schedule "aligns precisely with statutory boundaries like ADA, FMLA, and OSHA." Checked against `friction_tax.py`: only the `<50` boundary ties to a real coded threshold (FMLA's 50-employee federal threshold); OSHA has no coded employee-count threshold anywhere in this file, and the 250/500 boundaries aren't tied to any statute either. The underlying recommendation (reuse the component) was correct and shipped; the overstated justification was not carried into any code comment or copy.

4. **File-location correction, from Claude Code's own check, not assumed:** `EnginePayload` lives in `web/lib/engine-client.ts`, not `web/lib/types.ts` as the build spec referenced — confirmed and worked from the correct location rather than silently guessing.

## Live verification (production, real HTTP round-trips)

- **Real end-to-end submission, first time through this path**: `compression_crisis` + `disparate_impact_architecture`, headcount=65, industry="Professional Services", orgType="Founder-led", jurisdictions=["AL"] — `friction_tax_estimate` low/high=713084.22/998317.91, `legal_tail_risk_exposure` low/high=28749.56/38499.12, band="Minor", coverage_basis="federal_baseline", has_partial_jurisdictions=true. Both modules genuinely non-null through this flow for the first time.
- **Blank-intake regression, re-confirmed on deployed infrastructure**: `built_to_fail` + headcount="" — HTTP 200, both fields null, no 500. Last round's fix holds live, not just in-process.
- Prior to production checks: actual browser click-through in local dev, real fetch-intercept capturing the true outgoing request body (not inference), then that exact captured payload run through `run_engine()` in-process, before final production confirmation.

## Test suite / type check

`tsc --noEmit` clean. Full 11-script suite: 838/838, unchanged (no Python touched this round — TS/frontend only).

## Named exceptions — not gaps to rediscover later

- Local dev cannot run the Python engine (Vercel-routing-only constraint) — same limitation as last round. Verified in two parts (real browser capture locally, real HTTP round-trip on production after deploy) rather than treating either alone as sufficient.

## New item surfaced, not investigated — flagging, not fixing

- **Possible pre-existing mobile z-index collision.** At a narrow viewport, `AssemblyPanel`'s mobile bottom-sheet trigger and `SelfSelectionInterface`'s phase-transition bars are both `fixed bottom-0 left-0 right-0`, and coordinate-based clicks on the phase-transition CTA didn't register during this session's browser testing — worked around with direct JS clicks, not diagnosed further. Not confirmed to reproduce on a real device. Not something introduced this session.

## On the horizon — updated Priority Queue

1. **New: possible mobile z-index collision**, `AssemblyPanel` vs. phase-transition bars at narrow viewports — needs a real-device check, not confirmed as a real bug yet.
2. PARTIAL coverage-threshold state verification (~30 of 44 states) — unchanged.
3. `extreme_high_confidence` calibration tier at 0/1 — unchanged.
4. v2 token migration for the homepage — unchanged, architectural only.

(Last session's item — why `handleTakeDiagnostic()` hardcoded `headcount: ""` — is now fully closed by this session's work, not carried forward.)
