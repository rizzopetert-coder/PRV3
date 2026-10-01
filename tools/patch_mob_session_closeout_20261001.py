"""
Closeout patch for the 2026-09-30/10-01 session (MOB v4.330 -> v4.331): friction tax
rebuild shipped.

Edits, all exact-match or prefix-match, any miss aborts with nothing written:
  1. tools/_mob.txt: version header, Section 13b currency changes, Section 14 (Session 38
     row annotated, share row annotated, four new rows), Section 16 entry appended.
  2. CLAUDE.md: MOB version cross-reference, and the expand/contract rule in Engine Rules.
  3. prompts/session-handoff-v4.331.md: new file, extracted from the Section 16 entry only.

Usage:
  python tools/patch_mob_session_closeout_20261001.py --dry-run
  python tools/patch_mob_session_closeout_20261001.py --write
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOB = ROOT / "tools" / "_mob.txt"
CLAUDE = ROOT / "CLAUDE.md"
HANDOFF = ROOT / "prompts" / "session-handoff-v4.331.md"

OLD_V, NEW_V = "v4.330", "v4.331"

# ---------------------------------------------------------------- 13b texts

FRICTION_BULLET = (
    "- **FRICTION TAX REBUILD, SHIPPED 2026-09-30/10-01 (code stages complete, dollars still hidden).** Stages 0-6 plus 3a "
    "landed in 84 commits, `6c067fd..0e41bcb` (per-stage ranges in Section 16). Final production deploys at `0e41bcb`: "
    "prv-3 `dpl_73cJAY5LgKSiHCsdXPJx8V9VjZQu`, prv3-engine `dpl_FbiDwmp3gAHwUrAbfggTsxoH21nS`, both READY. The model is two "
    "dollar channels plus a decision-time receipt (Section 14 rows dated 2026-09-30). Spec: "
    "`prompts/friction-tax-rebuild-build-spec.md` with its Phase 0 addendum (rulings R1-R6, accepted interpretation calls, "
    "the copy register). **`FRICTION_DOLLARS_VISIBLE` remains false** (`web/lib/output-text.ts`). Flipping it is a Tier 4 "
    "decision, and its prerequisite is Pete's review of the \"Copy requiring Pete's review before any flag flip\" register in "
    "the spec addendum (`01b8f3d`). That register includes the condensed heading \"Estimated cost of one departure in this "
    "pattern\" (`web/components/CondensedOutput.tsx:140`), where \"in this pattern\" is inaccurate because the figure is the "
    "industry wage times 0.333 and does not depend on the pattern. All of the rebuild's friction copy is unreviewed Claude "
    "Code drafting that sits behind that flag. Still open from the rebuild: the qualifying-margin question (display only, "
    "does not affect costing)."
)

HRDX_BULLET = (
    "- HR-DX overview docs (Google Drive: HR-DX-Overview, HR-DX-Methodology-Detail): UNBLOCKED, the build has shipped "
    "(2026-09-30/10-01). Pete's call when. They should describe cost as what organizations like the client's typically lose, "
    "as a percent of payroll and a point estimate (engagement measured against the best-run organizations, plus turnover), "
    "not as dollar ranges. Dollars stay hidden in the product, so the docs should not promise a dollar figure in the report."
)

INACTION_BULLET = (
    "- RESOLVED 2026-09-30/10-01 by the rebuild (R5): `service_cost_comparison.inaction_cost_low/high` is removed from the "
    "payload and the type, with no replacement field. Engine `3dc3a8e`, types `234aa74`. The cost comparison reads the "
    "typical-loss estimate and the legal range as two lines, never a sum (decision 14)."
)

COST_LEADIN_BULLET = (
    "- Cost comparison lead-in \"If these conditions go unaddressed\" (`web/components/ReportDetails.tsx`, `CostComparison`). "
    "Re-checked against the live block 2026-10-01 on production and still true, unchanged by the rebuild. While friction "
    "dollars are hidden the lead-in sits over the legal figure alone (live: \"$846,000 – $909,000\" captioned \"Legal "
    "exposure, one-time if a claim arises\", then \"People Tactics & Strategy / Ask for pricing\"), so it reads as if legal "
    "were the whole cost. If the flag flips, the typical-loss line shares it and the problem goes away. Copy review, Pete's "
    "call, part of the flag-flip review. The Copy results version has no lead-in."
)

PAYROLL_BULLET = (
    "- RESOLVED 2026-09-30/10-01: the `PAYROLL_BASELINE_GRID` docstring that said 54 cells and 9 industries was removed with "
    "the grid itself in Stage 4 (`e8a3f72`). The module docstring now describes the two-channel model."
)

RENDERER_BULLET = (
    "- RESOLVED 2026-09-30/10-01: `web/lib/output-renderer.ts` deleted (`f4c9d2a`), it had no callers. The two comments that "
    "named it were updated (`0b57737`)."
)

NEW_ITEMS = [
    "- `the_inner_circle`: legal score above 0 (turnover 1, productivity 0, decision_quality 2, legal 1) but it is not in "
    "`LEGAL_COMPLIANCE_CLUSTER` (30 states, the 31st scorer is this one), so Legal prices it as not applicable. Pre-existing, "
    "pinned by `tools/test_state_criteria.py`. Needs Pete's ruling. Fixing it deliberately changes the Legal baseline: "
    "re-capture with `python tools/capture_legal_baseline.py --write` (after removing the existing fixture on purpose) and "
    "record the diff in Section 16.",
    "- Legal moving to May 2025 wages: a future decision, held by R1. Legal reads the frozen `_LEGAL_WAGE_DATA_MAY2023` "
    "(`engine/friction_tax.py`) so it stays byte-identical to the Phase 0 baseline. Moving it changes the Ohio compensatory "
    "figures (42 of 870 baseline blocks, every Ohio jurisdiction set) and needs its own baseline re-capture.",
    "- UNVERIFIED: `is_test` on two UI-driven production sessions (Technology, 175 employees, `completed_at` about 13:24 and "
    "13:36 UTC on 2026-10-01). Claude Code had no Upstash credentials and would not decrypt the Vercel secret. The "
    "`diagnostic-aggregate` list has no per-session key, so the records are identified by time, industry and size. Pete to "
    "check in the Upstash console (and a third, aborted run never completed and wrote no record). The driver injected "
    "`x-prv3-test-run: 1` into the page's `/api/diagnostic/*` fetches. (Pete's closeout request dated the sessions "
    "2026-09-30, the runtime clock read 2026-10-01 UTC.)",
    "- Copy results carries 36 conditions with full prose, 25,701 characters on a live Technology/175 report (2026-10-01). "
    "Outside the rebuild's scope. It is pre-existing and by lock: Section 14 \"Copy results mirrors on-screen content only\" "
    "(2026-09-28) and `buildResultsText` copy every condition's full prose because every card is expandable on screen. Open "
    "question for Pete and Claude.ai: whether that length sits against the Brief's output-precision principle (the Brief was "
    "not available to Claude Code in this session, so that comparison was not made). Its Cost comparison lines also open "
    "with a spaced em-dash list prefix (\"— Legal exposure...\"). That is the documented list idiom in `output-text.ts`, but "
    "the CLAUDE.md standing rule reserves em-dashes for a genuine interruption, so check it against the house dash style.",
    "- Runtime-log status summaries twice reported \"2 distinct values total, showing top 1\" with 200 the only one shown "
    "(2026-10-01, both projects). The second value was never displayed and 5xx queries returned nothing, so it is not a 5xx. "
    "Low priority, identify it when convenient.",
]

LAST_UPDATED_PREFIX = "Last updated: This session (Claude Code), 2026-09-30 -- rewritten per convention."
LAST_UPDATED_NEW = (
    "Last updated: This session (Claude Code), 2026-09-30/10-01 -- rewritten per convention. Numbered priorities 1-5 "
    "unchanged, the severity follow-on gate stays #1. Rewritten: FRICTION TAX REBUILD (now SHIPPED, dollars still hidden, "
    "flag flip gated on Pete's copy review), HR-DX overview docs (unblocked), the cost comparison lead-in item (re-checked "
    "live). Resolved by the rebuild: `inaction_cost_*`, `output-renderer.ts`, the `PAYROLL_BASELINE_GRID` docstring. Added: "
    "`the_inner_circle` legal cluster gap, Legal May 2025 wages (future), `is_test` unverified on two UI sessions, Copy "
    "results length and dash style, runtime-log second status value. Files-to-attach rewritten for the Step-Back, the "
    "severity gate, the copy-register review and the HR-DX doc update. Next Quarterly Step-Back due 2026-10-03."
)

ATTACH_FRICTION_PREFIX = "- If working on the friction tax rebuild (the build):"
ATTACH_NEW_LINES = [
    "- If working the severity follow-on state-scoping gate (priority 1): engine/data/questions.py (`severity_trigger`, "
    "`severity_follow_on_id`, `severity_input_mapping`), engine/severity.py, engine/main.py (`accumulate_one_answer`), "
    "web/app/api/diagnostic/session/answer/route.ts, tools/diagnostic_question_audit.py, tools/_mob.txt.",
    "- If reviewing the friction copy register (Pete's flag-flip prerequisite): prompts/friction-tax-rebuild-build-spec.md "
    "(the addendum section \"Copy requiring Pete's review before any flag flip\"), engine/contract.py (`_friction_receipts`), "
    "engine/friction_tax.py (the framing constants and channel inputs), web/lib/output-text.ts, "
    "web/components/ReportDetails.tsx, web/components/CondensedOutput.tsx.",
    "- If updating the HR-DX overview docs: Google Drive HR-DX-Overview and HR-DX-Methodology-Detail, "
    "prompts/friction-tax-rebuild-build-spec.md, prompts/friction-tax-rebuild-source-verification.md, "
    "engine/friction_tax.py (inputs and vintages), tools/_mob.txt.",
]

# ---------------------------------------------------------------- Section 14

SESSION38_OLD = "Superseded once the rebuild ships. See Section 13b and Section 16 (2026-09-28/29).**"
SESSION38_NEW = (
    SESSION38_OLD
    + " **SUPERSEDED 2026-09-30 by the friction rebuild: `SEVERITY_SCALAR` and the 1.4x spread were removed from "
    "`engine/friction_tax.py` and `engine/contract.py` in Stage 4 (`e8a3f72`, `3dc3a8e`) and the tests rewritten (`b5ed7dd`, "
    "`f824ec4`, `e965ec5`). Severity no longer moves the friction figure. Row kept for history, not deleted. See the "
    "Section 14 rows dated 2026-09-30 and Section 16 (2026-09-30/10-01).**"
)

SHARE_OLD = "Stripped at write (share/create) and at read (getShareRecord). Locked 2026-09-30, Pete. Commits 2e56044, 8680886. |"
SHARE_NEW = (
    "Stripped at write (share/create) and at read (getShareRecord). Locked 2026-09-30, Pete. Commits 2e56044, 8680886. "
    "**EXTENDED 2026-09-30 (R6, Pete):** the guarded names are now `friction_tax_estimate`, `legal_tail_risk_band`, "
    "`friction_receipts` and `channels` (ledger rows carry `channels`, but the ledger is never written to a share). The "
    "read-time strip in `getShareRecord` removes all four (`0a804a8`), and `web/lib/share-payload-guard.test.ts` (`c0d67be`) "
    "fails if any appears in a share payload at write or at read, at any depth. |"
)

SEC14_ROWS = [
    "| **Friction model: two channels plus a decision-time receipt** | LOCKED 2026-09-30, Pete. The friction figure is two "
    "dollar channels, engagement (P x (0.70 - 0.31) x 0.18, 7.02 percent of payroll) and turnover (P x q x 0.42 x 0.333), plus "
    "a decision-time receipt with no dollar figure, per decisions 1-18 in `prompts/friction-tax-rebuild-source-verification.md`. "
    "Identified states only switch channels on, channels never stack or scale by state count, severity is not an input, the "
    "result is a point estimate, and at the 1,000 intake cap dollars are withheld and only percent of payroll is shown. JOLTS "
    "monthly quits rates are stored rounded to 2 decimals and annualized times 12 (R3). Shipped in Stages 4 and 6 "
    "(`e8a3f72..c00b8a7`, `234aa74..0b57737`). | This session (Claude Code), 2026-09-30/10-01 | MOB v4.331 |",
    "| **Legal reads a frozen wage table and stays byte-identical** | LOCKED 2026-09-30, Pete (R1). Legal/Compliance reads "
    "`_LEGAL_WAGE_DATA_MAY2023` in `engine/friction_tax.py`, not the refreshed friction wages, and must stay byte-identical to "
    "the Phase 0 baseline (`tools/fixtures/legal_compliance_baseline.*`, checked by `python tools/capture_legal_baseline.py "
    "--check`). Any Legal change is deliberate, re-captured and the diff recorded, never silent. Moving Legal to May 2025 "
    "wages is a separate future decision. Commits `8e837e9`, baseline `6c067fd`, `517dbed`, `fc87f9a`. | This session "
    "(Claude Code), 2026-09-30/10-01 | MOB v4.331 |",
    "| **Condensed departure figure is industry wage x 0.333, a single value, behind the flag** | LOCKED 2026-09-30, Pete "
    "(R2). The condensed cost of one departure is the industry wage (OEWS May 2025) times 0.333, returned as "
    "`condensed_departure_cost` by the engine and carried as `departure_cost` in the payload, rendered only behind "
    "`FRICTION_DOLLARS_VISIBLE`. The old 0.50 to 0.75 range is retired, and its fields are read as no figure, never converted. "
    "Hidden branch shows no block and no copy. Commits `060603b` (hide), `e27658a..b3e794e` (single value). | This session "
    "(Claude Code), 2026-09-30/10-01 | MOB v4.331 |",
    "| **Cross-project payload changes use expand/contract** | LOCKED 2026-09-30, Pete. prv-3 and prv3-engine deploy "
    "separately from one push, so a payload shape change that crosses them is done in two pushes. Expand: the engine emits both "
    "the old and the new field for one deploy cycle, and the web reads the new one tolerantly. Contract: a later push removes "
    "the old field once the web reads only the new one. Reason: the Stage 5 deploy race (a window of about 30 seconds where an "
    "old-web client would have thrown on `payload.financial_range`). Also in CLAUDE.md Engine Rules. | This session (Claude "
    "Code), 2026-09-30/10-01 | MOB v4.331 |",
]

# ---------------------------------------------------------------- Section 16

SECTION16 = r"""## SESSION CLOSEOUT (2026-09-30/10-01, terminal Claude Code) -- friction tax rebuild shipped (code stages complete, dollars still hidden)
## -- MOB v4.330 -> v4.331

**Startup Protocol ran in the terminal Claude Code session.** The diary read ran and succeeded (the Qdrant shutdown traceback at exit is harmless). The MOB header read v4.330. The Python suites, tsc, vitest and the 175-profile calibration were all run live in the session (calibration 171/175, measured, which retires the earlier "carried forward, unverified" note). `gh` is not installed, so open research-refresh PRs could not be checked (unverified, not zero). `research/refresh-log/pending-integration.json` was `[]` (0 proposed, 0 deferred).

**One-line summary:** the friction tax rebuild was built and shipped in full per the spec and Pete's rulings R1-R6 (stages 0 through 6 plus 3a), the false-model dollars stay hidden behind `FRICTION_DOLLARS_VISIBLE` (false), and Legal/Compliance stayed byte-identical to a baseline recorded before the first refactor commit.

### 1. Shipped

84 commits, `6c067fd..0e41bcb`, all on main, docs and code, pushed per round. Final production deploys at `0e41bcb`: prv-3 `dpl_73cJAY5LgKSiHCsdXPJx8V9VjZQu`, prv3-engine `dpl_FbiDwmp3gAHwUrAbfggTsxoH21nS`, both READY. Every commit carries the MOB v4.330 tag in its message (the version bump lands in this closeout).

- **Stage 0, Legal byte-identical baseline:** `6c067fd` (capture script, modes dry-run, write, check), `517dbed` (gzipped canonical JSON, 344,520 grid rows and 175 calibration profiles), `fc87f9a` (sha256 manifest with per-block hashes). Pushed, deploys `dpl_7YengemXMgHQyB6vSGJWYvn4H5y1` and `dpl_uoP7bt4FjMHRrPuw7xb36uFQt8pP` READY. Deterministic across runs. Sensitivity proven: one changed wage altered 42 of 870 blocks, all Ohio.
- **Spec addendum:** `fb3323f` (Phase 0 corrections and rulings R1-R6, W and q verified, 6b recomputed), then `f573130` (accepted interpretation calls, Stage 5 field name) and `01b8f3d` (copy register), with patch scripts `dade35a`, `36e602f`, `0e41bcb`.
- **Stage 1, state criteria registry:** `7f31c4e..fdbc957` (7 commits). `engine/data/state_criteria.py` holds 58 states with four integer scores, Legal and the receipt switch read it. Byte-identical.
- **Stage 2, org list ownership:** `92b40b5..8330dac`. Comment-only edits plus `tools/test_org_type_lists.py`. Non-comment before/after comparison identical. Deploys `dpl_CpMcHeZQ2TR7ejDeddY67kTgq5zR`, `dpl_7R1VAAHiDjihvqNwCQRma1g26SEN` READY, live `/diagnostic` showed the same six org types.
- **Stage 3a, condensed hide (pulled forward):** `060603b..7f8e3ae`. The "cost of one departure" block, and its "roughly 50-75%" copy, sit behind `FRICTION_DOLLARS_VISIBLE`. Deploys `dpl_8UZP5nV8aqHrAY48uantNYnqxy1y`, `dpl_7xP62hB4JqAhS6yvCUNA8jWEByAC`. Live condensed run through the UI: `/api/condensed-complete` 200, no dollar figure.
- **Stage 3, wage refresh:** `8e837e9..e0fd289`. `_LEGAL_WAGE_DATA_MAY2023` frozen for Legal, `_INDUSTRY_WAGE_DATA` refreshed to OEWS May 2025 (all 11 values verified against the primary files). `--check` byte-identical. Deploys `dpl_9gqiYKzwZYUgZRgF8hRrjUbkC9gd`, `dpl_54PaLnRe9Bp8Vt2s8f4USuXjKvj8`. Live tagged full session (Technology, 175): legal block unchanged in form, `$841,039` to `$865,841`.
- **Condensed intro copy:** `e26fd46..1855074`. Pete's approved copy replaced the line that promised "a rough sense of what it costs". Deploys `dpl_8pCR3xmN5CK57JcfKtvZ9k24VGcP`, `dpl_Hg12SJAZ1zamKhNGUy7KYkh5w6ps`. Live line confirmed.
- **Stage 4, two-channel function (engine):** `e8a3f72..c00b8a7`. New `compute_friction_tax(state_ids, org_size, industry)`, `friction_receipts` sibling, ledger `channels`, `inaction_cost_*` removed (R5), share-payload name guard (R6). Removed with zero remaining readers: `STATE_MULTIPLIERS`, `PAYROLL_BASELINE_GRID`, `SEVERITY_SCALAR`, the 1.4x spread, `ORG_TYPE_SCALARS`, the magnitude constants. Tests rewritten with hand-computed literals (all ten spec 6b rows, the 7.02 factor, the cap, the guard). 247 friction checks passed on the first run.
- **Stage 6, web types and consumers (pulled ahead of Stage 5):** `234aa74..0b57737`. Tolerant readers for the old, new and missing shapes, ledger without per-row figures, `output-renderer.ts` deleted. Five new consumer test files. Deploys `dpl_Gf25ZZqhbWA1D8uLmjD41uAabjKv`, `dpl_8VehVSasz2EQHwQ6o6KxkRxXFV1W`. Live: tagged full session total `$1,852,348.57` (9.2018 percent, Technology/175), matching the hand-computed literal. A real UI drive end to end rendered the full report with no friction dollars, legal `$846,000 – $909,000`, console clean. A share round trip (`FZ0TqOTszqcEkLIsFfb9x`) carried none of the four guarded names and no dollar figures. Copy results captured live: all dollar figures legal, no typical-loss line, no inaction figure.
- **Stage 5, condensed single value:** `e27658a..b3e794e`. `condensed_departure_cost` (industry wage x 0.333) replaces the 0.50 to 0.75 range. Live: Technology gave `38304.99`, no old range key, no dollar rendered, intro unchanged. Final deploys above (the Stage 5 engine build `dpl_AM5DppvQn3ckVb1eGDEYG8VaWibP` was cancelled by the following docs push, whose build includes Stage 5).
- **Runtime logs:** no 5xx on any new deployment, checked after the Stage 3, Stage 4 and 6, and Stage 5 pushes.

### 2. Gates at close

15 Python suites pass (the original 13 plus `tools/test_state_criteria.py` and `tools/test_org_type_lists.py`), `tsc --noEmit` clean, vitest 245/245 (21 files), calibration 171/175 with the same four ATT-* failures (`ATT-UT-02`, `ATT-IB-02`, `ATT-LD-02`, `ATT-IE-02`, severity 175/175), measured live this session at every stage, and `python tools/capture_legal_baseline.py --check` byte-identical. No gate was skipped.

### 3. Decisions (Pete)

- **R1:** Legal keeps a frozen May 2023 wage table (`_LEGAL_WAGE_DATA_MAY2023`), separate from refreshed friction wages. **R2:** the condensed figure moves behind `FRICTION_DOLLARS_VISIBLE`, the 50-75% copy removed, not reworded. **R3:** JOLTS rates stored rounded to 2 decimals, 6b recomputed. **R4:** gzip storage of the baseline accepted. **R5:** `inaction_cost_*` removed with no replacement. **R6:** share-payload name guard in Stage 4.
- **Stage 3a resequencing:** the condensed hide ships before the wage refresh, because Stage 3 changed a public figure that was not yet hidden. **Stage 6 ahead of Stage 5.** **The condensed intro copy.** **Accepted interpretation calls:** `driving_factors` dropped from the estimate, the two ledger notes deleted, the share strip covers four top-level names.
- **Expand/contract** for any payload shape change that crosses prv-3 and prv3-engine (Section 14 and CLAUDE.md Engine Rules).

### 4. CORRECTIONS

- **(a)** W and q were never verified against primary sources before 2026-09-30. The verification doc held no W table and no JOLTS values, only the NAICS mapping and the 11-0000 share and wage. Both were verified this session: all 11 W values match the OEWS May 2025 files (`nat3d_M2025_dl.xlsx`, `nat3d_owner_M2025_dl.xlsx`), all 11 q values match JOLTS Table 22 (the two blended rows recompute to 3.367 and 1.6395).
- **(b)** The spec's claim that only `get_industry_wage` and the grid read `_INDUSTRY_WAGE_DATA` was wrong. The Ohio compensatory-damages formula read it too, so the planned wage refresh would have broken Legal byte-identity. Found in Phase 0, resolved by R1.
- **(c)** The 2026-09-28 option C hide did not cover the condensed "cost of one departure" figure, which stayed public until Stage 3a (`060603b`). The same class of gap as the share leak (2026-09-30 corrections).
- **(d)** Process deviation in Stage 3a: Claude Code omitted the condensed block instead of stopping to propose copy as instructed. The stop would also have caught the intro line that the hide made false ("a rough sense of what it costs"), which stayed live until it was fixed in the next round (`e26fd46`).
- **(e)** A Stage 5 deploy race window of about 30 seconds: the new engine ran against the old web, and an old-web condensed client would have thrown on `payload.financial_range`. No condensed session ran in that window and the logs show no 5xx. This is the reason for the expand/contract rule.
- **(f)** A tooling slip in Stage 6, caught and fixed before any commit: an edit removed the `FRICTION_DOLLARS_VISIBLE` definition along with two notes that sat beside it. It was restored verbatim from HEAD and the final diff does not touch it.

### 5. Verification gaps carried

- `is_test` on the two UI-driven production sessions is unverified (no Upstash credentials, see 13b). The sessions are Technology/175, `completed_at` about 13:24 and 13:36 UTC on 2026-10-01.
- The raw engine response for Stage 5 was not inspected directly (it is server-side). The new field was confirmed by its value in the route's payload and the old range's absence by the code.
- `api/engine.py` could only be compile-checked locally (`fastapi` is not installed in the local venv), then verified live.

### 6. Section 13b Currency Check (Step 1a)

**13b rewritten where it changed.** Numbered priorities 1-5 unchanged, the severity follow-on gate stays #1. FRICTION TAX REBUILD rewritten as SHIPPED with the commit range, the final deploys, `FRICTION_DOLLARS_VISIBLE` still false and the flag flip gated on Pete's review of the copy register (`01b8f3d`, including the condensed "in this pattern" inaccuracy). Marked RESOLVED: `inaction_cost_*` (`3dc3a8e`, `234aa74`), `output-renderer.ts` (`f4c9d2a`), the `PAYROLL_BASELINE_GRID` docstring (`e8a3f72`). HR-DX overview docs marked UNBLOCKED. The cost comparison lead-in item re-checked against the live block and rewritten. Added: `the_inner_circle` legal cluster gap, Legal May 2025 wages (future), `is_test` unverified, Copy results length and dash style, the runtime-log second status value. Files-to-attach rewritten.

**Section 14:** the Session 38 row (0.6/1.0/1.4 and the 1.4x spread) annotated SUPERSEDED 2026-09-30 in place. The 2026-09-30 share row annotated EXTENDED (R6) rather than duplicated. Four new rows: the two-channel friction model, the frozen Legal wage table, the condensed single value, and expand/contract. CLAUDE.md Engine Rules gained the expand/contract rule.

**Test state at close:** 15 Python suites pass, `tsc --noEmit` clean, vitest 245/245, calibration 171/175 (same four ATT-* failures), `--check` byte-identical, all run at `0e41bcb`.

**Files changed, git-confirmed:** `engine/friction_tax.py`, `engine/contract.py`, `engine/data/state_criteria.py` (new), `engine/data/intake.py` (comment), `api/engine.py`, `web/lib/types.ts`, `web/lib/output-text.ts`, `web/lib/engine-client.ts`, `web/lib/diagnostic-completion.ts`, `web/lib/dev-diagnostic-preview.ts`, `web/lib/share-store.ts`, `web/lib/condensed-departure-cost.ts` (new), `web/lib/output-renderer.ts` (deleted), `web/app/api/result/route.ts`, `web/app/api/diagnostic/condensed/answer/route.ts`, `web/components/PrivateOutput.tsx`, `ReportDetails.tsx`, `CondensedOutput.tsx`, `CondensedDiagnosticFlow.tsx`, `DiagnosticFlow.tsx` and `SelfSelectIntakeModal.tsx` (comments), many new and rewritten test files, `tools/capture_legal_baseline.py` and `tools/fixtures/legal_compliance_baseline.*` (new), `prompts/friction-tax-rebuild-build-spec.md`, and the patch scripts. This closeout: `tools/_mob.txt`, `CLAUDE.md`, `prompts/session-handoff-v4.331.md` (new), `tools/patch_mob_session_closeout_20261001.py` (new).

**Open items carried forward:** see Section 13b. Next Quarterly Step-Back due **2026-10-03**.

**Anything Pete should know at next session start:** the friction rebuild is shipped and live, and friction dollars are still hidden (`FRICTION_DOLLARS_VISIBLE = false`). Flipping it is Tier 4 and needs Pete's review of the copy register first. The old dollar model is gone from the engine, so there is nothing to restore by flipping the flag except the new typical-loss figure and receipts. The payload still carries the friction estimate and receipts in the API response, they are only hidden in the display. Legal/Compliance must stay byte-identical, run `python tools/capture_legal_baseline.py --check` after any engine change. Untracked scratch files (`tools/_salience_pilot_*`, `tools/gemini_*`, `tools/qsm_extracted.txt`, `tools/qualitative_review.py`, two patch scripts) were present at session start and untouched.

MOB v4.331.
"""

# ---------------------------------------------------------------- handoff

HANDOFF_FILES = """## Files to attach next session

- Quarterly Step-Back (due 2026-10-03): tools/_mob.txt, PRV3-Principal-Brief.docx.
- Severity follow-on gate (priority 1): engine/data/questions.py, engine/severity.py, engine/main.py, web/app/api/diagnostic/session/answer/route.ts, tools/diagnostic_question_audit.py, tools/_mob.txt.
- Pete's friction copy-register review: prompts/friction-tax-rebuild-build-spec.md (addendum section "Copy requiring Pete's review before any flag flip"), engine/contract.py, engine/friction_tax.py, web/lib/output-text.ts, web/components/ReportDetails.tsx, web/components/CondensedOutput.tsx.
- HR-DX overview doc update: Google Drive HR-DX-Overview and HR-DX-Methodology-Detail, prompts/friction-tax-rebuild-build-spec.md, prompts/friction-tax-rebuild-source-verification.md, engine/friction_tax.py.

## Time-anchored

- Quarterly Step-Back due 2026-10-03.
"""

CLAUDE_RULE = (
    "- Payload shape changes that cross `prv3-engine` and `prv-3` use expand/contract. The two projects deploy separately\n"
    "  from one push, so there is a window where the web runs against the other shape. Expand: the engine emits both the old\n"
    "  and the new field for one deploy cycle and the web reads the new one tolerantly (old, new and missing shapes all safe,\n"
    "  a throw in a hidden or gated path still counts as unsafe). Contract: a later push removes the old field once the web\n"
    "  reads only the new one. Locked 2026-09-30, Pete, after the Stage 5 deploy race (an old-web client would have thrown\n"
    "  on `payload.financial_range` for about 30 seconds). Also in `tools/_mob.txt` Section 14.\n"
)


def build_handoff(section16: str) -> str:
    body = section16.replace(
        "## SESSION CLOSEOUT",
        "# Session handoff, MOB v4.331 (extract of Section 16)\n\nSource: tools/_mob.txt Section 16, entry "
        "`SESSION CLOSEOUT (2026-09-30/10-01`. If this file and Section 16 ever differ, Section 16 is authoritative.\n\n"
        "## SESSION CLOSEOUT",
        1,
    )
    return body.rstrip("\n") + "\n\n" + HANDOFF_FILES


def replace_line(lines, prefix, new, label):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, f"{label}: expected 1 match for prefix, got {len(hits)}"
    lines[hits[0]] = new
    return hits[0]


def sub_in_line(lines, prefix, old, new, label):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, f"{label}: expected 1 line for prefix, got {len(hits)}"
    assert lines[hits[0]].count(old) == 1, f"{label}: substring count {lines[hits[0]].count(old)}"
    lines[hits[0]] = lines[hits[0]].replace(old, new)


def main():
    mode = "--write" if "--write" in sys.argv else "--dry-run"
    text = MOB.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)

    hv = [i for i, l in enumerate(lines) if l.strip() == r"\\\#\\\# MOB " + OLD_V]
    assert len(hv) == 1, f"version header matches: {len(hv)}"
    lines[hv[0]] = r"\\\#\\\# MOB " + NEW_V

    # 13b
    i1 = replace_line(lines, "- **FRICTION TAX REBUILD (opened 2026-09-28/29", FRICTION_BULLET, "friction")
    i2 = replace_line(lines, "- HR-DX overview docs (Google Drive", HRDX_BULLET, "hrdx")
    i3 = replace_line(lines, "- `service_cost_comparison.inaction_cost_low/high` still ships", INACTION_BULLET, "inaction")
    i4 = replace_line(lines, "- Cost comparison lead-in \"If these conditions go unaddressed\"", COST_LEADIN_BULLET, "leadin")
    i5 = replace_line(lines, "- `PAYROLL_BASELINE_GRID` docstring in `engine/friction_tax.py` says 54 cells", PAYROLL_BULLET, "payroll")
    i6 = replace_line(lines, "- `web/lib/output-renderer.ts` has no callers", RENDERER_BULLET, "renderer")
    i7 = replace_line(lines, LAST_UPDATED_PREFIX, LAST_UPDATED_NEW, "lastupdated")
    i8 = [i for i, l in enumerate(lines) if l.startswith(ATTACH_FRICTION_PREFIX)]
    assert len(i8) == 1, "attach friction line"
    lines[i8[0]:i8[0] + 1] = ATTACH_NEW_LINES

    ih = [i for i, l in enumerate(lines) if l.startswith("Infrastructure carry-forwards")]
    assert len(ih) == 1
    j = ih[0] - 1
    while lines[j].strip() == "":
        j -= 1
    for k, item in enumerate(NEW_ITEMS):
        lines.insert(j + 1 + k, item)

    # Section 14
    sub_in_line(lines, "| \\\\\\*\\\\\\*Session 38\\\\\\*\\\\\\*", SESSION38_OLD, SESSION38_NEW, "session38")
    sub_in_line(lines, "| **Share payloads never carry friction or legal fields**", SHARE_OLD, SHARE_NEW, "share row")
    ish = [i for i, l in enumerate(lines) if l.startswith("| **Share payloads never carry friction or legal fields**")]
    assert len(ish) == 1
    ins = []
    for row in SEC14_ROWS:
        ins.extend(["", row])
    lines[ish[0] + 1:ish[0] + 1] = ins

    # Section 16 entry appended
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines.append("")
    lines.extend(SECTION16.rstrip("\n").split("\n"))
    lines.append("")
    new_text = nl.join(lines)

    ctext = CLAUDE.read_text(encoding="utf-8")
    assert f"| MOB version | {OLD_V} |" in ctext, "CLAUDE.md MOB version row"
    new_ctext = ctext.replace(f"| MOB version | {OLD_V} |", f"| MOB version | {NEW_V} |", 1)
    anchor = "  expansion. See `prompts/scd-wcs-cluster-map-findings.md`.)\n"
    assert new_ctext.count(anchor) == 1, "CLAUDE.md engine rules anchor"
    new_ctext = new_ctext.replace(anchor, anchor + CLAUDE_RULE, 1)

    handoff = build_handoff(SECTION16)

    # house rules on new text: no semicolons, no em-dashes (the 13b lead-in item quotes the live "–" en dash figure
    # and the Copy results item quotes the list prefix deliberately)
    new_texts = (SECTION16 + "".join(NEW_ITEMS) + FRICTION_BULLET + HRDX_BULLET + INACTION_BULLET + PAYROLL_BULLET
                 + RENDERER_BULLET + LAST_UPDATED_NEW + "".join(SEC14_ROWS) + SESSION38_NEW + SHARE_NEW
                 + "".join(ATTACH_NEW_LINES))
    print("semicolons in new text:", new_texts.count(";"))
    print("em-dashes in new text (the one quoted list prefix is deliberate):", new_texts.count("—"))
    print(f"MOB lines {len(text.splitlines())} -> {len(new_text.splitlines())}; 13b lines replaced at "
          f"{i1+1},{i2+1},{i3+1},{i4+1},{i5+1},{i6+1},{i7+1}")
    print("handoff chars:", len(handoff))

    if mode == "--write":
        MOB.write_text(new_text, encoding="utf-8")
        CLAUDE.write_text(new_ctext, encoding="utf-8")
        HANDOFF.write_text(handoff, encoding="utf-8")
        print("written")
    else:
        print("[dry-run] nothing written")


if __name__ == "__main__":
    main()
