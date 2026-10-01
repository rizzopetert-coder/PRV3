# Session handoff, MOB v4.330 (extract of Section 16)

Source: tools/_mob.txt Section 16, entry `SESSION CLOSEOUT (2026-09-30`. If this file and Section 16 ever differ, Section 16 is authoritative.

## SESSION CLOSEOUT (2026-09-30, terminal Claude Code) -- friction rebuild verified and specified,
## share payload fix -- MOB v4.329 -> v4.330

**Claude.ai ran the full engage protocol: MOB v4.329 header confirmed from the attached tools/_mob.txt, Principal Brief read, status reported.** **Startup Protocol ran partially in the terminal Claude Code session.** The diary read ran and succeeded (the Qdrant shutdown traceback at exit is harmless). The MOB was read where needed (13b, Section 16). The test suites were run mid-session rather than at start: all 13 Python suites passed, `tsc --noEmit` was clean and vitest was 143/143 with the share fix applied (working tree at `8680886`). The research-refresh PR check could not run (`gh` is not installed) and `research/refresh-log/pending-integration.json` was not read. Calibration (171/175 at `2bad54f`) was not re-run: nothing in the engine changed. That figure is carried forward, unverified this session.

**One-line summary:** the friction tax rebuild's three open verification items were closed against primary sources, 18 decisions were recorded, a build spec was written and Gemini-cleared (no engine code), and a share payload exposure was found and fixed in production.

### 1. Shipped

- **Verification doc** `prompts/friction-tax-rebuild-source-verification.md`, six commits: `dfdf8d7`, `a85eb6d`, `578dad6`, `3763f3d`, `edbfafa`, `2a34ca3`. Gallup 18% composition, Gallup Q12 quartile spread, BLS OEWS management share by industry (May 2025, `oesm25in4.zip`, 3-digit NAICS aggregated to the 11 engine industries), the McKinsey 2019 source check, relayed inputs verified (Gallup engagement and best-practice level, Gallup 42% preventable, Work Institute 33.3%), and decisions 1-18.
- **Build spec** `prompts/friction-tax-rebuild-build-spec.md`, four commits: `4445210`, `caa3f25`, `8cb333b`, `87a8ded`. Status: Gemini-cleared 2026-09-30, awaiting Pete's go to build. No engine code was changed.
- **Share payload fix**, code, two commits: `2e56044` (stop storing `friction_tax_estimate` and `legal_tail_risk_band` in the share payload, route test) and `8680886` (strip both fields on read in `getShareRecord`, test). Both tests failed before the fix and pass after. Deploy `dpl_ET1SXFDk8yz2j2W5N84vtHkh565L` READY. Production round trip: self-select share `-H8h7IhaxYXb32YJ5QJIp`, `POST /api/share/create` 200, `GET /api/share/<id>` 200 with no friction or legal fields, `/share/<id>` page 200 with normal content and no friction or legal data in the HTML. The read-time strip was covered by its unit test only, since no pre-existing share id could be found read-only.
- **Production session health check** (tagged `is_test`, `prv-3.vercel.app`): `session/start` 200 in 4.28 s, `session/answer` 200 in 1.42 s, no Upstash or rate-limit text, no runtime errors in 24 hours.

### 2. Decisions

Decisions 1-18 are recorded in `prompts/friction-tax-rebuild-source-verification.md` under "Decisions (Pete, 2026-09-30)". Not restated here.

### 3. CORRECTIONS

- **(a)** The 2026-09-28 option C hide did not cover shares. Self-select share payloads carried friction dollars in the page source and in `GET /api/share/[id]` until `2e56044` and `8680886`. The share page serialized the whole stored payload to the browser, and the API returned it whole.
- **(b)** The 2026-09-29 Gemini outcome's P2 amendment (partial-year discount) is withdrawn by decision 7. It was Claude.ai's reasoning error: the engagement channel prices position-years of payroll, so a leaver's remaining year is filled by the replacement.
- **(c)** The "20% manager share" was a proposal assumption taken from McKinsey's thought-experiment footnote, not a live engine value. It is not in `engine/friction_tax.py` or `prompts/friction-tax-*.md`.
- **(d)** An in-session claim that the share headcount string bug was live was wrong. It is latent: Path 1 sharing is disabled (`web/components/DiagnosticFlow.tsx:930`), so the string headcount is never sent.
- **(e)** Decision 10's original wording ("bucket mean only for legacy string labels") assumed legacy headcount strings still arrive. String tolerance in `resolve_headcount_bucket` was deliberately removed 2026-08-29. Corrected in the verification doc.

### 4. Deploy and infrastructure findings

- 4445210 deploy ERROR: `next build` failed in Turbopack on a next/font/google lookup for Source Serif 4 ('next/font/google queries have exactly one entry', 18 errors), not a GitHub or clone failure (clone succeeded). Docs-only commit, later deploys caa3f25 and 8680886 READY with no font change, so likely transient. Cause not confirmed.
- Upstash (checked by Pete 2026-09-30): `web/.env.local` has no Upstash credentials, deliberately. The root `.env.local` held credentials for a database not on Pete's Upstash account (deleted or foreign), and its PING rate-limit error is unrelated to production. CORRECTS the v4.330 line "present in .env.local but rate-limited", which conflated the two files. The dead entries were removed from the root file (nothing in the repo reads them).
- Source Serif 4 is loaded and preloaded on every page with no consumers, introduced with OD-07 Stage 1 (2d063f7). The OD-07 row (rolled back in b8860b5, infrastructure 'left in place, dormant') covers its --font-serif mapping in globals.css but does not name the font import in layout.tsx. Recommendation: stop loading it. Geist Mono is loaded and preloaded with no consumers. Geist Sans is the live body font. Details in 13b.
- DISCREPANCY: the Session 58 identity lock names Inter as the body font, but the live body font is Geist Sans (web/app/globals.css:199, :478). Either the lock is stale or the CSS drifted. Pete to rule. Do not change either until then.

### 5. Gemini rounds

Round 2 and its two follow-ups (Q5, Q4) and the decision 18 confirm are recorded in the spec's Section 11. Gemini answered round 2 from prompt text only, since it could not open the attachments.

### 6. Section 13b Currency Check (Step 1a)

**13b rewritten where it changed.** Numbered priorities 1-5 unchanged. FRICTION TAX REBUILD rewritten: spec complete and Gemini-cleared, next step is the build awaiting Pete's go, `FRICTION_DOLLARS_VISIBLE` stays false through the build and flipping it is a separate Tier 4 decision. HR-DX overview docs stay held until the build ships. `inaction_cost_*` item marked resolved in design. Added: the latent share headcount bug, the Google Fonts build dependency, the Source Serif 4 and Geist findings, the Upstash env-file item, the `PAYROLL_BASELINE_GRID` docstring, `output-renderer.ts` dead code. The infrastructure line on local Upstash credentials was corrected. Files-to-attach rewritten for the build and the Step-Back.

**Section 14 row WRITTEN (Pete, 2026-09-30):** "Share payloads never carry friction or legal fields. Stripped at write (share/create) and at read (getShareRecord). Locked 2026-09-30, Pete. Commits 2e56044, 8680886." The Session 38 severity-scalar lock (0.6/1.0/1.4 and the 1.4x spread) is unchanged: already REOPENED, superseded when the build ships.

**Test state at close:** `tsc --noEmit` clean, vitest 143/143, 13 Python suites pass (all run at `8680886`). Calibration not re-run (carried forward, unverified this session). No engine, web or test code changed after `8680886`.

**Files changed, git-confirmed:** `web/lib/types.ts`, `web/app/api/share/create/route.ts`, `web/app/api/share/create/route.test.ts` (new), `web/lib/share-store.ts`, `web/lib/share-store.test.ts` (new), `prompts/friction-tax-rebuild-source-verification.md` (new), `prompts/friction-tax-rebuild-build-spec.md` (new). This closeout: `tools/_mob.txt`, `CLAUDE.md` (MOB version cross-reference), `prompts/session-handoff-v4.330.md` (new), `tools/patch_mob_session_closeout_20260930.py` (new).

**Open items carried forward:** see Section 13b. Next Quarterly Step-Back due **2026-10-03**.

**Anything Pete should know at next session start:** the friction rebuild is at spec level and waiting on Pete's go to build. Do not start code until that go. Friction dollars remain hidden on both brands. The share fix is live. Untracked scratch files (`tools/_salience_pilot_*`, `tools/gemini_*`, `tools/qsm_extracted.txt`, `tools/qualitative_review.py`, two patch scripts) were present at session start and were not touched.

MOB v4.330.

## Files to attach next session

- Friction build: prompts/friction-tax-rebuild-build-spec.md, prompts/friction-tax-rebuild-source-verification.md, engine/friction_tax.py, engine/contract.py, api/engine.py, engine/data/intake.py, web/lib/output-text.ts, web/lib/types.ts, web/lib/engine-client.ts, web/components/PrivateOutput.tsx, web/components/ReportDetails.tsx, tools/test_friction_tax.py, tools/test_contract.py.
- Step-Back: tools/_mob.txt, PRV3-Principal-Brief.docx.

## Time-anchored

- Quarterly Step-Back due 2026-10-03.
