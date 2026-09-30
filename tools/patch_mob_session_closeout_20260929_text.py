# Text content, part 1 of 3 (13b and Section 14), for
# tools/patch_mob_session_closeout_20260929.py (MOB v4.328 -> v4.329).

NUMBERED_HEADER = (
    "Priority order for next session, in sequence. Unchanged since the 2026-09-23 wholesale "
    "rewrite (full detail in Section 16's 2026-09-23 dated note). Pete confirmed 2026-09-29 that "
    "his friction-rebuild list does not replace them, and the severity follow-on gate stays #1:"
)

KEEP_OPEN_PREFIXES = [
    "- Citation sourcing Phase 2",
    "- `private_output.resolution_routing` stale values",
    "- Service Expectations page",
    "- SEVER-09/Q27A",
    "- `tools/diagnostic_fast_forward.py` answer-steering",
    "- Asset-scoring calibration, Tier 1",
    "- ShareableOutput never live-tested",
    "- 205 spaced dashes",
    "- PR condensed verdict copy",
    "- Condensed report locked-indicators line",
    "- `service_cost_comparison.inaction_cost_low/high`",
    "- Separate Upstash database for Preview",
    "- OSHA actual-average-penalty",
    "- `StateDrawer`/`AssemblyPanel`",
    "- 12-file salience-pilot",
    "- Bucket 1 remainder",
    "- `tools/patch_*.py` accumulation",
    "- ATT-* moderate-tier",
]

NEW_OPEN = [
    "- **FRICTION TAX REBUILD (new workstream, opened 2026-09-28/29).** Friction-tax dollar figures "
    "are hidden on both brands behind `FRICTION_DOLLARS_VISIBLE = false` (`web/lib/output-text.ts`, "
    "`2cbb212`, `b1922f4`) until the rebuild clears Gemini and Pete. Why: the magnitude audit found all "
    "58 `STATE_MULTIPLIERS` entries rubric-scored with no research citation, the 5-25% payroll range "
    "untraceable to any source record (`prompts/friction-tax-state-multiplier-methodology.md:48` is the "
    "only trail), and per-affected-employee research (Gallup 18% of a disengaged employee's salary, SHRM "
    "replacement cost, `prompts/friction-tax-unit-decision.md:16-21`) applied to total payroll. "
    "Claude.ai primary-source research (relayed, not verified in this environment): BLS JOLTS Table 22, "
    "Work Institute 33.3% of salary per voluntary exit, Gallup engagement (May 2026: 31% engaged, 17% "
    "actively disengaged) and its 18%-of-salary method, McKinsey 2019 decision time. **Gemini round "
    "returned and reviewed 2026-09-29, outcome approved by Pete with Claude.ai's corrections.** Accepted: "
    "P1 baseline structure, P3 show both the typical baseline and the excess, P5 per-channel position "
    "replaces the halving, P8 qualifying margin moot for costing (still open for display), P9 condensed "
    "\"cost of one departure\" moves to Work Institute 33.3%. P6 APPROVED BY PETE: the 0.6/1.0/1.4 "
    "severity scalars are replaced by position within the cited bound (Section 14 severity-scalar lock, "
    "with the high = 1.4x low spread, marked REOPENED 2026-09-29, superseded once the rebuild ships). P2 "
    "amended: discount productivity loss for leavers' partial year, and first verify whether Gallup's 18% "
    "already includes turnover cost. P4 amended: no above-typical adjustment for any channel without a "
    "cited within-industry spread (candidate: Gallup Q12 meta-analysis quartile differences for turnover "
    "and productivity, to be verified, and the cross-industry JOLTS spread is rejected as a bound). P7: "
    "headline turnover uses Gallup's 42% preventable share (HC-038). New requirement: replace the 20% "
    "manager share with the BLS OEWS management-occupation share by industry, manager wage from BLS. "
    "Framing rule: the baseline is presented as \"what organizations like yours typically lose\", never as "
    "normal or acceptable. **Next:** primary-source verification of the three open items (Gallup 18% "
    "composition, Gallup Q12 quartile spread, BLS management share by industry), then a build spec. No "
    "code until the spec clears Pete. Also in scope: the qualifying-margin question for display (sweep "
    "2026-09-28: margin or cap changes never moved the lead, routing or pathway, and calibration is "
    "unaffected), resourcing the condensed \"cost of one departure\" (today industry wage x 50-75%, "
    "`api/engine.py:283-289`), and the payload, which still carries friction dollars (hidden in display "
    "only, and `inaction_cost_*` sums friction and legal). The Gemini prompt and response live in "
    "Claude.ai, not in the repo.",
    "- Narrative-question intake grounding. **Corrected 2026-09-28:** `role_level` IS the live wire field "
    "(`web/components/DiagnosticFlow.tsx:144-147`, validated at `session/start/route.ts:46`), mapped to "
    "`principal_role` inside the engine (`engine/main.py:225`). The question-generation call receives no "
    "intake at all (`session/answer/route.ts:277-280`, `engine/narrative.py:574-577`). That exclusion was "
    "incidental, not a recorded decision: the `9148aba` fix script says passing intake is a data-contract "
    "change that routes through Gemini. Gemini round cleared by Pete, response not yet reviewed. Not built.",
    "- HR-DX overview docs (Google Drive: HR-DX-Overview, HR-DX-Methodology-Detail): update held until "
    "the friction substance is settled. They will describe cost as cited ranges.",
    "- Calibration (Tier 1, alongside the asset item below): Q01-B (\"Bigger decisions get complicated "
    "here even when smaller ones don't.\") carries negative authority_liability (-0.15) on a "
    "problem-phrased answer. It is now excluded from ledger evidence by the weight filter (`1d4b900`). "
    "Q18-E's conditional asset scoring no longer surfaces as receipt or ledger evidence (liability-only "
    "ranking, `22c03f3`) but still feeds the scores.",
    "- Receipts quote the answer most relevant to the condition, not to the legal category, so a legal "
    "step (\"Workplace safety and regulatory: The Undefined Role\") can quote an answer that reads as "
    "unrelated to its category. Copy or ranking review.",
    "- Legal caveat text (`LEGAL_TAIL_RISK_CAVEAT_TEXT`) still has two spaced \"--\", and legal step "
    "weights display 12.5% / 6.25% / 3.125% as \"12%\" / \"6%\" / \"3%\" (`engine/contract.py` legal "
    "receipts, `:.0%` format).",
    "- Cost comparison lead-in \"If these conditions go unaddressed\" now sits over the legal figure alone "
    "(friction hidden), so it reads as if legal were the whole cost. Copy review.",
    "- Call 1 fallback repeats one paragraph in three places (`engine/data/fallback_synthesis.py:37-41`). "
    "When Call 2 fails, the on-screen TC review shows referral chips over expanded answers with no section "
    "headings or counts (`web/components/ReportDetails.tsx:221, 251-253`). Copy results mirrors that state.",
    "- /book citations: LIB-020 (`web/content/book/methodology/candor-as-an-organizational-variable.md:17`) "
    "Gallup strengths-feedback figures (65,672 / 14.9%, 530 / 12.5%, 469 / 8.9%) need citation entries. "
    "Line 23's Project Aristotle \"across every metric the study tracked\" overclaims the source. "
    "`research/refresh-log/tracked-claims.json:153-161` says /book cites the 70% change-failure figure, "
    "which no /book file does (stale note). Context: the Hammer library "
    "(`C:\\Users\\rizzo\\PRV2\\src\\data\\hammer-citations.json`, 111 entries) has about 71 insights whose "
    "number is attributed to a source other than the entry's verified title and URL. None of those figures "
    "appears on any PRV3 surface (scan 2026-09-28).",
    "- Small items: `direct_reports` is collected and stored but used by nothing (engine or AI). "
    "`tools/test_phase1_report_data.py` only passes when run from the repo root. A retired `mempalace` MCP "
    "server still registers in this environment from outside `.mcp.json`.",
    "- Executive summary voice, hr-dx only: live output opens with lines like \"Here's the thing:\". The "
    "principalresolution.com summary follows Pete's no-TC paragraph order (what is happening, what it costs "
    "in working terms, what would have to change, `9efa505`).",
    "- Pass 2 content, remaining scope: the uncovered observation texts, recounted 2026-09-29. 289 options "
    "have no `observation_text`: 151 core (85 on live-reachable questions, 66 on unreachable ones) plus 138 "
    "SEVER-* (134 reachable). TC-* excluded (zero-signal). Strength texts are CLOSED, below.",
]

CLOSED_IN_PLACE = [
    "- CLOSED 2026-09-28 -- web routes' function duration: `maxDuration = 60` pinned on `session/answer` "
    "and `session/narrative` (`138704a`, `996e398`, patch script `8061470`), and the prv-3 build accepted it. "
    "prv3-engine stays at 300 via the root `vercel.json`. Live: `az80d4bubc8SGYligUfXG` (PR), "
    "`qcugvnHEtnFJCnkXZEhTf` (hr-dx).",
    "- CLOSED 2026-09-28 -- Pass 2 strength texts: 33 asset-valence texts, 3 DIST-CM liability texts and 3 "
    "house-dash rewrites (Q02-C, Q07-A, Q09-D), valence totals 106 liability / 6 neutral / 33 asset "
    "(`1aed5be`), strength evidence capped at 5 (`13b421e`). Live strength panels quote evidence on both brands.",
    "- CLOSED 2026-09-28 -- \"Primary asset domain\" line removed from the report and Copy results. It "
    "described the lead condition, not the respondent. The payload field stays (engine contract). "
    "`6d7607c`, `e581c85`.",
    "- CLOSED 2026-09-28 -- unrounded legal figure (\"$604,214.4\"): every displayed dollar figure is now "
    "3 significant figures, half up, never $0 (`22c03f3`, `6d7607c`, `e581c85`, `a00f71b`, `de421df`).",
]

KEEP_FILE_PREFIXES = [
    "- If revisiting hr-dx copy",
    "- If tuning the fast_forward driver",
    "- If changing Vercel env/project config",
    "- If resuming the transaction path",
    "- If resuming book-manifest.ts's teaser",
    "- If touching the condensed report",
    "- If doing asset calibration",
]

NEW_FILES_TO_ATTACH = [
    "- Always: tools/_mob.txt (current version).",
    "- If working on the friction tax rebuild: engine/friction_tax.py (STATE_MULTIPLIERS, compute_friction_tax, "
    "PAYROLL_BASELINE_GRID), engine/contract.py (`_build_friction_tax_ledger`, `_friction_driving_factors`), "
    "web/lib/output-text.ts (`FRICTION_DOLLARS_VISIBLE`), web/components/PrivateOutput.tsx, api/engine.py "
    "(condensed range), prompts/friction-tax-*.md, and the Gemini rebuild prompt and response (Claude.ai, not in the repo).",
    "- If working on the report (both brands): engine/contract.py, engine/main.py, engine/output_synthesis.py, "
    "engine/tactical_synthesis.py, engine/exec_summary.py, web/components/ReportDetails.tsx, "
    "web/components/PrivateOutput.tsx, web/components/CopyResultsButton.tsx, web/lib/output-text.ts, "
    "tools/test_phase1_report_data.py.",
    "- If writing Pass 2 content: engine/data/questions.py (`_observation_text_tags`, `_observation_valence_tags`), "
    "tools/diagnostic_question_audit.py (reachability), tools/patch_pass2_observation_texts.py (the pattern).",
    "- If working on citations: web/lib/book-citations.ts, "
    "web/content/book/methodology/candor-as-an-organizational-variable.md, research/refresh-log/tracked-claims.json, "
    "C:\\Users\\rizzo\\PRV2\\src\\data\\hammer-citations.json (outside the repo).",
    "- If building narrative intake grounding: web/components/DiagnosticFlow.tsx, "
    "web/app/api/diagnostic/session/answer/route.ts, engine/narrative.py, engine/main.py.",
]

LAST_UPDATED = (
    "Last updated: This session (Claude Code), 2026-09-28/29 -- rewritten wholesale per convention. "
    "Numbered priorities 1-5 unchanged. Closed in place: web route duration, Pass 2 strength texts, "
    "Primary asset domain, unrounded legal figure. Rewritten: Pass 2 (remaining scope recounted), "
    "narrative intake grounding (corrected), executive summary voice (hr-dx only). Added: friction tax "
    "rebuild (with the 2026-09-29 Gemini outcome), hr-dx overview docs, Q01-B calibration, receipt "
    "relevance, legal caveat dashes and weight display, cost comparison lead-in, Call 1 fallback and TC "
    "headings, /book citations, small tooling items. Dropped: prior sessions' CLOSED lines (recorded in "
    "Section 16). Files-to-attach gained friction rebuild, citations and narrative intake."
)

SECTION_14_ROWS = [
    "| **Copy results mirrors on-screen content only** | LOCKED 2026-09-28, Pete-confirmed, both brands. "
    "`buildResultsText` (`web/lib/output-text.ts`) emits only what `PrivateOutput` renders, in its order and "
    "with its omit-when-empty rules: no dimensional percentages, net asset scores, 0-100 severity scores, "
    "engine metadata or intake echo. The Call 2 failure state copies what the screen shows (referral chips "
    "over the answer list). Brand-specific extras (PR book links, engage CTA, About-this-report drawer) are "
    "left out on both brands. Commits `5029492`, `f533331`, `8386f3c`, `57ceca1`. | This session (Claude "
    "Code), 2026-09-28/29 | MOB v4.329 |",
    "| **Strength evidence capped at 5, ordered by contribution** | LOCKED 2026-09-28, Pete-confirmed. "
    "`_build_asset_evidence` quotes at most 5 asset-valence texts, highest contribution to a leading asset "
    "axis first, ties in question order. Commit `13b421e`. | This session (Claude Code), 2026-09-28/29 | MOB v4.329 |",
    "| **Receipt and ledger evidence rank on liability fields only** | LOCKED 2026-09-28, Pete-confirmed. "
    "Receipt steps and ledger rows rank problem or neutral answers on `*_liability` contributions only, so "
    "an answer's asset signal can never make it look like evidence of a problem. Receipts quote an answer "
    "only at weight >= 0.20 (`_RECEIPT_EVIDENCE_MIN_WEIGHT`, chosen from calibration data) and never repeat "
    "one, the line is omitted instead. Ledger evidence requires weight > 0 with no 0.20 floor. Commits "
    "`22c03f3`, `1d4b900`. | This session (Claude Code), 2026-09-28/29 | MOB v4.329 |",
    "| **Calculation steps stay visible** | LOCKED 2026-09-28, Pete (decision D). The \"How this figure was "
    "calculated\" steps stay visible as written, condition names included. While friction dollars are "
    "hidden (row below) only the friction steps are hidden, the legal steps stay. | This session (Claude "
    "Code), 2026-09-28/29 | MOB v4.329 |",
    "| **Display dollars at 3 significant figures** | LOCKED 2026-09-28, Pete-confirmed. Every displayed "
    "dollar figure, screen, Copy results and condensed report, is rounded to 3 significant figures, half up, "
    "and a nonzero value never renders as $0. One formatter per language (`formatUsd`/`formatUsdRange` in "
    "`web/lib/output-text.ts`, `_usd` in `engine/contract.py`). Payload values stay unrounded. Commits "
    "`22c03f3`, `6d7607c`, `e581c85`, `a00f71b`, `de421df`. | This session (Claude Code), 2026-09-28/29 | MOB v4.329 |",
    "| **Friction dollars hidden until the rebuild clears Gemini and Pete** | LOCKED 2026-09-28/29, Pete "
    "(option C), both brands. `FRICTION_DOLLARS_VISIBLE = false` (`web/lib/output-text.ts`) is the single "
    "reversible switch: the ledger reads \"The answers behind these conditions\", the methodology footnote "
    "and friction steps are hidden, and the cost comparison drops the friction line. Legal exposure is "
    "unchanged. The engine keeps computing and the payload is unchanged. Call 1 and Call 2 prompts forbid "
    "dollar figures and percentages of payroll. Commits `2cbb212`, `b1922f4`, `0f9eec7`, `fd01aef`. | This "
    "session (Claude Code), 2026-09-28/29 | MOB v4.329 |",
    "| **Hammer insight numbers are never reused** | LOCKED 2026-09-28/29, Pete. Numbers from Hammer "
    "library insight text (`C:\\Users\\rizzo\\PRV2\\src\\data\\hammer-citations.json`) are never reused. Only "
    "a figure verified against the entry's own cited source may be published. About 71 of the 111 insights "
    "attribute their number to a source other than the entry's verified title and URL. | This session "
    "(Claude Code), 2026-09-28/29 | MOB v4.329 |",
]

REOPENED_MARKER = (
    "**REOPENED 2026-09-29 by Pete (friction tax rebuild, Gemini P6): the 0.6/1.0/1.4 severity scalars and "
    "the high = 1.4x low spread are to be replaced by position within the cited bound. Superseded once the "
    "rebuild ships. See Section 13b and Section 16 (2026-09-28/29).**"
)
