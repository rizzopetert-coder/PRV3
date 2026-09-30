# Session handoff -- MOB v4.329 (2026-09-28/29, Claude.ai + terminal Claude Code)

Derived from Section 16's 2026-09-28/29 closeout entry in `tools/_mob.txt`. If the two ever disagree, Section 16 is authoritative.

## Summary

Route timeouts were pinned, the principalresolution.com report gained an executive summary, Copy results was limited to what the screen shows, strength evidence was written, receipts and ledger evidence were made liability-only, dollars are shown at 3 significant figures, and friction-tax dollar figures are hidden on both brands until a Gemini-reviewed rebuild. Startup Protocol ran in full.

## Shipped this session

| Area | Commits |
|---|---|
| maxDuration 60 on session/answer and session/narrative (engine stays 300) | `138704a`, `996e398`, `8061470` |
| Executive summary on principalresolution.com (gating, no-TC prompt) | `6aa0377`, `9efa505` |
| Copy results on-screen only, incl. Call 2 failure state | `5029492`, `f533331`, `8386f3c`, `57ceca1` |
| Pass 2 strength texts (106/6/33) and evidence cap 5 | `1aed5be`, `13b421e` |
| Report batch tests and patch scripts | `3a82dcc`, `a83c290`, `a86fdc0`, `3014f96`, `75cdf05`, `47eed36` |
| Presentation: asset domain removed, ledger grouped, liability-only evidence, 0.20 receipt floor, legal wording, 3 sig figs | `22c03f3`, `6d7607c`, `e581c85`, `a00f71b`, `de421df`, `62cf162`, `555a8ed`, `1d4b900`, `cd2553e`, `0212843`, `794d89f`, `0909e2e` |
| Option (C): friction dollars hidden, Call 1 and Call 2 no-dollar rule | `2cbb212`, `b1922f4`, `0f9eec7`, `fd01aef`, `512b080`, `88e561e`, `beab15d`, `d7c7d8c`, `2bad54f` |

Live sessions (all tagged `is_test`): `az80d4bubc8SGYligUfXG`, `qcugvnHEtnFJCnkXZEhTf` (duration), `Bp_8pp_wNLiROmU6EZU9N`, `kzaicO1H9X8HJs-VHf1pG` (report batch), `uYtZxoSslkS7BMBhJZ2kj` (presentation), `oW88iAbxzV5SrXtgyowwO`, `L_XIXebx8HdYaTqZwB4CA` (option C).

## Correction filed

The Section 14 three-call lock applies to both brands, but until `6aa0377` the code gave principalresolution.com no executive summary. Fixed in `6aa0377` and `9efa505`, live on `Bp_8pp_wNLiROmU6EZU9N`. The lock row itself needed no edit.

## Locked this session (Section 14)

- Copy results mirrors on-screen content only.
- Strength evidence capped at 5, ordered by contribution.
- Receipt and ledger evidence rank on liability fields only. Receipts need weight >= 0.20 and never repeat.
- Calculation steps stay visible (Pete, decision D).
- Display dollars at 3 significant figures, half up, never $0.
- Friction dollars hidden until the rebuild clears Gemini and Pete (`FRICTION_DOLLARS_VISIBLE`).
- Hammer insight numbers are never reused, only figures verified against their own source.

REOPENED 2026-09-29 by Pete: the Session 38 severity-scalar lock (0.6/1.0/1.4 and high = 1.4x low), superseded once the rebuild ships. Flagged, not moved: the 2026-09-26 hr-dx lock row still sits in Section 16's table. Pete's call.

## Findings (read-only)

- Narrative question gets no intake, incidental, not decided (`9148aba`).
- Qualifying-rule sweep: margin or cap changes never moved lead, routing or pathway, and calibration is unaffected.
- Friction magnitude: 58 multipliers unsourced, 5-25% range untraceable, per-affected-employee research applied to total payroll.
- Hammer library at `C:\Users\rizzo\PRV2\src\data\hammer-citations.json`, 111 entries, about 71 misattributed insights, none on any PRV3 surface.

## Open (13b)

- FRICTION TAX REBUILD: Gemini outcome approved 2026-09-29 (P1, P3, P5, P8, P9 accepted, P6 approved, P2 and P4 amended, P7 42% preventable, BLS OEWS management share, framing rule). Next: verify Gallup 18% composition, Gallup Q12 quartile spread, BLS management share by industry, then a build spec. No code until the spec clears Pete. Also the display qualifying margin, the condensed "cost of one departure", and the payload that still carries friction dollars.
- Narrative intake grounding: corrected (`role_level` is the live field, the question prompt gets no intake). Gemini round cleared, response not yet reviewed.
- HR-DX overview docs held until the friction substance is settled.
- Pass 2 remaining scope: 289 options without observation text (151 core, 138 SEVER-*).
- Calibration: Q18-E conditional asset scoring, Q01-B negative liability on a problem answer. Asset calibration (SEVER-* 0.25 seeding) unchanged.
- Receipt relevance to the legal category, legal caveat "--" and weight display, cost comparison lead-in, Call 1 fallback repeats, TC headings on Call 2 failure.
- /book: LIB-020 line-17 Gallup figures need citations, Project Aristotle overclaim, stale tracked-claims 70% note.
- direct_reports unused, report-data test root-only, retired mempalace server still registers.
- Executive summary voice (hr-dx only).
- Kept: ShareableOutput live check, 205 core dashes, driver steering, `engine-preview` upkeep, `is_test` records.
- 13b numbered priorities 1-5 unchanged.

## Parked

Unchanged from Section 13b's "Explicitly parked" list.

## Dated items

- Next Quarterly Step-Back due **2026-10-03**.

## Files to attach next session

- Always: `tools/_mob.txt`.
- Friction tax rebuild: `engine/friction_tax.py`, `engine/contract.py`, `web/lib/output-text.ts`, `web/components/PrivateOutput.tsx`, `api/engine.py`, `prompts/friction-tax-*.md`, the Gemini prompt and response (Claude.ai).
- Report work: `engine/contract.py`, `engine/main.py`, `engine/output_synthesis.py`, `engine/tactical_synthesis.py`, `engine/exec_summary.py`, `web/components/ReportDetails.tsx`, `web/components/PrivateOutput.tsx`, `web/components/CopyResultsButton.tsx`, `web/lib/output-text.ts`, `tools/test_phase1_report_data.py`.
- Pass 2: `engine/data/questions.py`, `tools/diagnostic_question_audit.py`, `tools/patch_pass2_observation_texts.py`.
- Citations: `web/lib/book-citations.ts`, the LIB-020 piece, `research/refresh-log/tracked-claims.json`, the PRV2 Hammer file.
- Narrative intake: `web/components/DiagnosticFlow.tsx`, `web/app/api/diagnostic/session/answer/route.ts`, `engine/narrative.py`, `engine/main.py`.
- Vercel config: `prompts/session-handoff-v4.327.md`.

## Anything Pete should know

- Friction dollars are hidden on both brands (`FRICTION_DOLLARS_VISIBLE` in `web/lib/output-text.ts`). The payload still carries them.
- The friction rebuild's next step is primary-source verification, not code.
- Test state at close: tsc clean, vitest 139/139, 13 Python suites pass, calibration 171/175.
- Exclude `is_test: true` when reading `diagnostic-aggregate`.
