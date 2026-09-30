# Text content, part 2 of 3 (Section 16 entry), for
# tools/patch_mob_session_closeout_20260929.py (MOB v4.328 -> v4.329).

SECTION_16 = r'''## SESSION CLOSEOUT (2026-09-28/29, Claude.ai + terminal Claude Code) -- report integrity,
## friction dollars hidden, friction rebuild opened -- MOB v4.328 -> v4.329

**Startup Protocol ran in full this session:** diary read, MOB v4.328 confirmed, all 13 Python suites passed, vitest 130/130, research ledger (`pending-integration.json`) empty. `gh` is still not installed, so the open research-refresh PR check could not run.

**One-line summary:** route timeouts were pinned, the principalresolution.com report gained an executive summary, Copy results was limited to what the screen shows, strength evidence was written, receipts and ledger evidence were made liability-only, dollars are shown at 3 significant figures, and friction-tax dollar figures are hidden on both brands until a Gemini-reviewed rebuild.

### 1. Function duration (13b item CLOSED)

`maxDuration = 60` pinned on `session/answer` and `session/narrative` (`138704a`, `996e398`, patch script `8061470`). prv3-engine stays at 300 via the root `vercel.json` (Pete dropped that hunk). The prv-3 build accepted 60 with no warning. Live: `az80d4bubc8SGYligUfXG` (PR), `qcugvnHEtnFJCnkXZEhTf` (hr-dx), both non-fallback.

### 2. Report batch (`8061470..47eed36`)

- Executive summary now renders on principalresolution.com: Call 3 runs when Call 2 succeeded or was never attempted (`6aa0377`), with a no-TC prompt carrying Pete's B2 wording and "Do not quote numbers" (`9efa505`). The hr-dx prompt and input stay byte-identical (pinned test). The hr brand test harness now picks Call 1 by system prompt (`a83c290`).
- Copy results limited to on-screen content, including the Call 2 failure state (`5029492`, `f533331`, `8386f3c`, `57ceca1`). Ohio caveat dash fixed at its source (one shared constant).
- Pass 2 strength texts: 33 asset + 3 DIST-CM liability + 3 dash rewrites, valence counts 106/6/33 (`1aed5be`, Q21-A per E2). Strength evidence capped at 5 (`13b421e`). Blank resolution-family line hidden.
- Tests `3a82dcc`, patch scripts `a86fdc0`, `3014f96`, `75cdf05`, `47eed36`. Live: `Bp_8pp_wNLiROmU6EZU9N` (PR), `kzaicO1H9X8HJs-VHf1pG` (hr-dx).

**CORRECTION (2026-09-28):** The Section 14 lock "Report architecture: three AI calls with isolated inputs" (MOB v4.328) applies to both brands. Until commit `6aa0377`, the code ran Call 3 only when Call 2 succeeded (engine/main.py:996). Call 2 is attempted only when a session has TC answers, which principalresolution.com sessions never have, so no principalresolution.com report received an executive summary. Found in the 2026-09-28 report inventory. Fixed in `6aa0377` (gating) and `9efa505` (no-TC prompt): Call 3 now runs when Call 1 is not a fallback and Call 2 either succeeded or was never attempted. Without TC answers it uses a separate system prompt (Pete's wording, "Do not quote numbers") and leaves the gap-count line out of its input. The hr-dx prompt and input are unchanged, pinned byte-for-byte in tools/test_phase1_report_data.py. Live-verified on session `Bp_8pp_wNLiROmU6EZU9N`. The Section 14 row was correct and needs no edit.

### 3. Presentation fixes (`47eed36..0909e2e`)

"Primary asset domain" line removed. Ledger rows grouped by shared evidence (the highest-standalone-estimate display was later superseded by option C). Receipts ranked on liability only with a 0.20 minimum and no forced reuse. Ledger evidence liability-only with weight > 0 (A3). One existing test conflicted with A3, and the batch stopped before any write. Pete chose option (a): Q01-B is now asserted absent (`1d4b900`). Legal weighting wording made accurate for any number of conditions. All dollars rounded to 3 significant figures. Commits `22c03f3`, `6d7607c`, `e581c85`, `a00f71b`, `de421df`, `62cf162`, `555a8ed`, `1d4b900`, patch scripts `cd2553e`, `0212843`, `794d89f`, `0909e2e`. Live: `uYtZxoSslkS7BMBhJZ2kj`.

### 4. Investigations (read-only)

- Narrative intake: the question-generation call gets no intake, and that was incidental, not a recorded decision (`9148aba`). The prior 13b note had the wire field backwards.
- Qualifying rule (score >= -0.40 and within 0.05 of rank 1, no cap, 0.05 a "CALIBRATION TARGET" with no recorded rationale): a margin and cap sweep over 533 simulated sessions never altered the lead, routing or pathway, and calibration pass rates are unaffected (the criteria do not read the qualifying set).
- Friction magnitude audit: all 58 multipliers are rubric-scored with no research citation, the 5-25% range is untraceable to a source record, and per-affected-employee research is applied to total payroll.
- Hammer library located at `C:\Users\rizzo\PRV2\src\data\hammer-citations.json` (outside the repo): 111 entries, HC-001 to HC-111, 109 VERIFIED and 2 UNVERIFIED by URL, about 71 insights attribute their number to a source other than the verified one. Public-content scan: NONE of those figures appears on any PRV3 surface.

### 5. Option (C) (`0909e2e..2bad54f`)

Friction dollar figures hidden on both brands behind `FRICTION_DOLLARS_VISIBLE = false`. The ledger now reads "The answers behind these conditions" with the note "Conditions that rest on the same answers share a row." The methodology footnote and friction steps are hidden, and the cost comparison drops the friction line (the whole block is omitted without priced legal exposure). Call 1 and Call 2 prompts forbid dollar figures and payroll percentages (Call 3's hr-dx prompt still byte-identical). A server-render test of the real report component pins it. Commits `2cbb212`, `b1922f4`, `0f9eec7`, `fd01aef`, `512b080`, `88e561e`, `beab15d`, patch scripts `d7c7d8c`, `2bad54f`. Live: `oW88iAbxzV5SrXtgyowwO` (PR), `L_XIXebx8HdYaTqZwB4CA` (hr-dx). No friction figure, "Friction tax", "Highest standalone" or "Sources include" on either brand, screen or Copy results, and no "$", "%" or "payroll" in any AI output.

### 6. Primary-source research and the Gemini round (Claude.ai, relayed, not verified in this environment)

Research: BLS JOLTS Table 22, Work Institute 33.3%, Gallup engagement (May 2026: 31/17) and its 18%-of-salary method, McKinsey 2019 decision time. The Gemini rebuild prompt was drafted, and the round returned and was reviewed 2026-09-29. Pete approved the outcome with Claude.ai's corrections: P1, P3, P5, P8 and P9 accepted, P6 approved (severity scalars and the 1.4x spread REOPENED in Section 14), P2 and P4 amended, P7 uses the 42% preventable share, the manager share moves to BLS OEWS by industry, and a framing rule applies. Full detail in 13b's FRICTION TAX REBUILD entry. Next: verify Gallup 18% composition, the Gallup Q12 quartile spread and the BLS management share by industry, then a build spec. No code until the spec clears Pete.

### 7. Section 13b Currency Check (Step 1a)

**13b rewritten wholesale.** Numbered priorities 1-5 unchanged (Pete confirmed his list does not replace them). Closed in place: web route duration, Pass 2 strength texts, Primary asset domain, unrounded legal figure. Remaining Pass 2 scope recounted: 289 options without observation text (151 core, 138 SEVER-*). Added: the friction tax rebuild and the other new open items listed there. Narrative intake grounding corrected. Executive summary voice now applies to hr-dx only.

**Section 14:** seven locked rows added (Copy results on-screen only, strength evidence cap, liability-only evidence ranking with the 0.20 receipt floor, calculation steps visible, 3 significant figures, friction dollars hidden, Hammer numbers never reused). The Session 38 severity-scalar lock (0.6/1.0/1.4 and the 1.4x spread) is marked REOPENED 2026-09-29 by Pete, not deleted. **Flag carried forward:** the 2026-09-26 hr-dx Production lock row (MOB v4.326) still sits inside Section 16's table, not Section 14. Pete's call.

**Test state at close:** tsc clean, vitest 139/139, 13 Python suites pass, calibration 171/175 (severity 175/175, run at `2bad54f`).

**Files changed, git-confirmed:** code commits listed above. This closeout: `tools/_mob.txt`, `CLAUDE.md` (MOB version cross-reference), `prompts/session-handoff-v4.329.md` (new), `tools/patch_mob_session_closeout_20260929.py` and its three text files (new).

**Open items carried forward:** see Section 13b as rewritten. Next Quarterly Step-Back due **2026-10-03**.

**Anything Pete should know at next session start:** friction dollars are hidden on both brands, and the switch is `FRICTION_DOLLARS_VISIBLE` in `web/lib/output-text.ts`. The payload still carries them. The friction rebuild's next step is primary-source verification, not code. `diagnostic-aggregate` holds this session's tagged `is_test` records (7 sessions listed above), so exclude `is_test: true`.

MOB v4.329.
'''
