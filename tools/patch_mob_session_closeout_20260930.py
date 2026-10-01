"""
Closeout patch for the 2026-09-30 session (MOB v4.329 -> v4.330).

Edits, all exact-match or prefix-match, any miss aborts with nothing written:
  1. tools/_mob.txt: version header, Section 13b currency changes, Section 16 entry appended.
  2. CLAUDE.md: MOB version cross-reference.
  3. prompts/session-handoff-v4.330.md: new file, reformatted from the Section 16 entry only.

Usage:
  python tools/patch_mob_session_closeout_20260930.py --dry-run
  python tools/patch_mob_session_closeout_20260930.py --write
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOB = ROOT / "tools" / "_mob.txt"
CLAUDE = ROOT / "CLAUDE.md"
HANDOFF = ROOT / "prompts" / "session-handoff-v4.330.md"

# ---------------------------------------------------------------- 13b texts

FRICTION_BULLET = (
    "- **FRICTION TAX REBUILD (opened 2026-09-28/29, spec complete and Gemini-cleared 2026-09-30).** "
    "Friction-tax dollar figures are hidden on both brands behind `FRICTION_DOLLARS_VISIBLE = false` "
    "(`web/lib/output-text.ts`, `2cbb212`, `b1922f4`). The build spec is `prompts/friction-tax-rebuild-build-spec.md` "
    "(`87a8ded`, status \"Gemini-cleared 2026-09-30. Awaiting Pete's go to build.\"). Research, sources and "
    "decisions 1-18 are in `prompts/friction-tax-rebuild-source-verification.md`. **Next step: the build per the spec, "
    "awaiting Pete's go.** Spec Section 10 gives the order, and the Legal/Compliance byte-identical baseline (Section 8) "
    "is recorded first, before any refactor commit. The old \"verify Gallup, Q12 and BLS\" next step is done. "
    "Shape of the design: two dollar channels (engagement as P x (0.70 - 0.31) x 0.18, turnover as P x q x 0.42 x 0.333) "
    "plus a decision-time receipt with no dollar figure, identified states only switch channels on, severity does not move "
    "the figure, point estimate, `friction_receipts` sibling field, percent of payroll at every headcount and dollars "
    "withheld at the 1,000 intake cap, headcount guard N of at least 2. The 0.6/1.0/1.4 severity scalars and the 1.4x "
    "spread (Section 14, Session 38 lock) stay REOPENED and are superseded when the build ships. "
    "**`FRICTION_DOLLARS_VISIBLE` stays false through the build. Flipping it is a separate Tier 4 decision.** "
    "Still open: the qualifying-margin question for display only (sweep 2026-09-28: margin or cap changes never moved "
    "the lead, routing or pathway, and calibration is unaffected). The Gemini prompts and responses live in Claude.ai, "
    "not in the repo (rounds recorded in spec Section 11)."
)

HRDX_BULLET = (
    "- HR-DX overview docs (Google Drive: HR-DX-Overview, HR-DX-Methodology-Detail): the friction substance is now "
    "settled at spec level (Gemini-cleared 2026-09-30). Update stays held until the build ships. They will describe cost "
    "as typical loss and percent of payroll, not as dollar ranges."
)

INACTION_BULLET = (
    "- `service_cost_comparison.inaction_cost_low/high` still ships in the payload (typed in `web/lib/types.ts`) with a "
    "mixed-timeframe meaning (annual friction plus one-time legal) and is no longer rendered since `bc80783` split the "
    "two. Resolved in the rebuild design by decision 14 (two lines, typical-loss point estimate and legal tail-risk "
    "range, not a sum). Ships with the build."
)

NEW_ITEMS = [
    "- Path 1 share headcount string bug, LATENT (`web/components/DiagnosticFlow.tsx:916` sends `String(organization_size)`). "
    "Path 1 sharing is disabled (`DiagnosticFlow.tsx:930`), so it is never sent. Fix when Path 1 sharing is enabled. "
    "Self-select shares send a real number and are unaffected.",
    "- Builds depend on the Google Fonts fetch at build time (`next/font/google`, `web/app/layout.tsx:9`). The fix is "
    "`next/font/local`. Not urgent, a failed build never replaces production. Evidence: the `4445210` production deploy "
    "(`dpl_B1PohBFwEqAcnf9cX5tM1hKMSqhj`) ERRORed in Turbopack on a next/font/google lookup for Source Serif 4, "
    "later deploys READY with no font change, so likely transient.",
    "- Source Serif 4 is dormant OD-07 infrastructure (added `2d063f7`, 2026-07-21, mapped to `--font-serif` at "
    "`web/app/globals.css:213`, no consumers anywhere in `web/`, not in the Session 58 identity lock at "
    "`tools/_mob.txt:542`, introduced with OD-07 Stage 1 (2d063f7). The OD-07 row (rolled back in b8860b5, infrastructure 'left in place, dormant') covers its --font-serif mapping in globals.css but does not name the font import in layout.tsx). It is still loaded and preloaded on every page via the "
    "`Link` response header. Recommendation: stop loading it, keep the other OD-07 infrastructure dormant. Pete's "
    "decision is pending. "
    "Geist and Geist Mono were checked 2026-09-30: Geist Sans is the live body font (`web/app/globals.css:199`, `:478`), "
    "Geist Mono has no consumers (`--font-mono` is IBM Plex Mono), and both are preloaded.",
    "- The `.env.local` Upstash database returned a rate-limit error on PING (2026-09-30). Production was unaffected "
    "(tagged session start and answer returned 200, no runtime errors in 24 hours). Pete to confirm which database it is "
    "in the Upstash dashboard. This corrects the earlier \"local dev credentials missing\" line: they are present.",
    "- `PAYROLL_BASELINE_GRID` docstring in `engine/friction_tax.py` says 54 cells and 9 industries. The real grid is 66 "
    "cells and 11 industries (`tools/test_friction_tax.py:526` asserts 66). The grid is removed by the rebuild, so fix the "
    "docstring only if the build is delayed.",
    "- DISCREPANCY: the Session 58 identity lock names Inter as the body font, but the live body font is Geist Sans "
    "(`web/app/globals.css:199`, `:478`). Either the lock is stale or the CSS drifted. Pete to rule. Do not change "
    "either until then.",
    "- `web/lib/output-renderer.ts` has no callers (`renderPrivateOutput`, `renderShareableOutput`). Marked for deletion "
    "in the friction spec, not for update.",
]

INFRA_OLD_PREFIX = "- Local dev Upstash Redis credentials missing"
INFRA_NEW = (
    "- Local dev Upstash Redis credentials are present in `.env.local`, not missing, but that database returned a "
    "rate-limit error on PING 2026-09-30. See the open item above. Production already has its own."
)

ATTACH_FRICTION_PREFIX = "- If working on the friction tax rebuild:"
ATTACH_FRICTION_NEW = (
    "- If working on the friction tax rebuild (the build): prompts/friction-tax-rebuild-build-spec.md, "
    "prompts/friction-tax-rebuild-source-verification.md, engine/friction_tax.py, engine/contract.py, api/engine.py, "
    "engine/data/intake.py, web/lib/output-text.ts, web/lib/types.ts, web/lib/engine-client.ts, "
    "web/components/PrivateOutput.tsx, web/components/ReportDetails.tsx, tools/test_friction_tax.py, "
    "tools/test_contract.py."
)
ATTACH_STEPBACK_NEW = (
    "- If running the Quarterly Step-Back (due 2026-10-03): tools/_mob.txt, PRV3-Principal-Brief.docx."
)

LAST_UPDATED_PREFIX = "Last updated: This session (Claude Code), 2026-09-28/29"
LAST_UPDATED_NEW = (
    "Last updated: This session (Claude Code), 2026-09-30 -- rewritten per convention. Numbered priorities 1-5 unchanged. "
    "Rewritten: FRICTION TAX REBUILD (spec complete and Gemini-cleared, next is the build awaiting Pete's go), HR-DX "
    "overview docs (friction substance settled, still held until the build ships), the `inaction_cost_*` item (resolved in "
    "design by decision 14), the Upstash infrastructure line (credentials present, database rate-limited). Added: Path 1 "
    "share headcount bug (latent), Google Fonts build dependency, Source Serif 4 and Geist font findings, Upstash "
    "rate-limit item, `PAYROLL_BASELINE_GRID` docstring, `output-renderer.ts` dead code. Next Quarterly Step-Back due 2026-10-03."
)

SECTION14_ROW = (
    "| **Share payloads never carry friction or legal fields** | Share payloads never carry friction or legal fields. "
    "Stripped at write (share/create) and at read (getShareRecord). Locked 2026-09-30, Pete. Commits 2e56044, 8680886. |"
)

# ---------------------------------------------------------------- Section 16

SECTION16 = r"""## SESSION CLOSEOUT (2026-09-30, terminal Claude Code) -- friction rebuild verified and specified,
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
- The `.env.local` Upstash database returned a rate-limit error on PING. Production was unaffected. Pete to confirm which database it is. Corrects the "local dev credentials missing" line.
- Source Serif 4 is loaded and preloaded on every page with no consumers, introduced with OD-07 Stage 1 (2d063f7). The OD-07 row (rolled back in b8860b5, infrastructure 'left in place, dormant') covers its --font-serif mapping in globals.css but does not name the font import in layout.tsx. Recommendation: stop loading it. Geist Mono is loaded and preloaded with no consumers. Geist Sans is the live body font. Details in 13b.
- DISCREPANCY: the Session 58 identity lock names Inter as the body font, but the live body font is Geist Sans (web/app/globals.css:199, :478). Either the lock is stale or the CSS drifted. Pete to rule. Do not change either until then.

### 5. Gemini rounds

Round 2 and its two follow-ups (Q5, Q4) and the decision 18 confirm are recorded in the spec's Section 11. Gemini answered round 2 from prompt text only, since it could not open the attachments.

### 6. Section 13b Currency Check (Step 1a)

**13b rewritten where it changed.** Numbered priorities 1-5 unchanged. FRICTION TAX REBUILD rewritten: spec complete and Gemini-cleared, next step is the build awaiting Pete's go, `FRICTION_DOLLARS_VISIBLE` stays false through the build and flipping it is a separate Tier 4 decision. HR-DX overview docs stay held until the build ships. `inaction_cost_*` item marked resolved in design. Added: the latent share headcount bug, the Google Fonts build dependency, the Source Serif 4 and Geist findings, the Upstash rate-limit item, the `PAYROLL_BASELINE_GRID` docstring, `output-renderer.ts` dead code. The infrastructure line on local Upstash credentials was corrected. Files-to-attach rewritten for the build and the Step-Back.

**Section 14 row WRITTEN (Pete, 2026-09-30):** "Share payloads never carry friction or legal fields. Stripped at write (share/create) and at read (getShareRecord). Locked 2026-09-30, Pete. Commits 2e56044, 8680886." The Session 38 severity-scalar lock (0.6/1.0/1.4 and the 1.4x spread) is unchanged: already REOPENED, superseded when the build ships.

**Test state at close:** `tsc --noEmit` clean, vitest 143/143, 13 Python suites pass (all run at `8680886`). Calibration not re-run (carried forward, unverified this session). No engine, web or test code changed after `8680886`.

**Files changed, git-confirmed:** `web/lib/types.ts`, `web/app/api/share/create/route.ts`, `web/app/api/share/create/route.test.ts` (new), `web/lib/share-store.ts`, `web/lib/share-store.test.ts` (new), `prompts/friction-tax-rebuild-source-verification.md` (new), `prompts/friction-tax-rebuild-build-spec.md` (new). This closeout: `tools/_mob.txt`, `CLAUDE.md` (MOB version cross-reference), `prompts/session-handoff-v4.330.md` (new), `tools/patch_mob_session_closeout_20260930.py` (new).

**Open items carried forward:** see Section 13b. Next Quarterly Step-Back due **2026-10-03**.

**Anything Pete should know at next session start:** the friction rebuild is at spec level and waiting on Pete's go to build. Do not start code until that go. Friction dollars remain hidden on both brands. The share fix is live. Untracked scratch files (`tools/_salience_pilot_*`, `tools/gemini_*`, `tools/qsm_extracted.txt`, `tools/qualitative_review.py`, two patch scripts) were present at session start and were not touched.

MOB v4.330.
"""

# ---------------------------------------------------------------- handoff

HANDOFF_FILES = """## Files to attach next session

- Friction build: prompts/friction-tax-rebuild-build-spec.md, prompts/friction-tax-rebuild-source-verification.md, engine/friction_tax.py, engine/contract.py, api/engine.py, engine/data/intake.py, web/lib/output-text.ts, web/lib/types.ts, web/lib/engine-client.ts, web/components/PrivateOutput.tsx, web/components/ReportDetails.tsx, tools/test_friction_tax.py, tools/test_contract.py.
- Step-Back: tools/_mob.txt, PRV3-Principal-Brief.docx.

## Time-anchored

- Quarterly Step-Back due 2026-10-03.
"""


def build_handoff(section16: str) -> str:
    body = section16.replace("## SESSION CLOSEOUT", "# Session handoff, MOB v4.330 (extract of Section 16)\n\nSource: tools/_mob.txt Section 16, entry `SESSION CLOSEOUT (2026-09-30`. If this file and Section 16 ever differ, Section 16 is authoritative.\n\n## SESSION CLOSEOUT", 1)
    return body.rstrip("\n") + "\n\n" + HANDOFF_FILES


def replace_line(lines, prefix, new, label):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, f"{label}: expected 1 match for prefix, got {len(hits)}"
    lines[hits[0]] = new
    return hits[0]


def main():
    mode = "--write" if "--write" in sys.argv else "--dry-run"
    text = MOB.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)

    # version header
    hv = [i for i, l in enumerate(lines) if l.strip() == r"\\\#\\\# MOB v4.329"]
    assert len(hv) == 1, f"version header matches: {len(hv)}"
    lines[hv[0]] = r"\\\#\\\# MOB v4.330"

    i1 = replace_line(lines, "- **FRICTION TAX REBUILD", FRICTION_BULLET, "friction")
    i2 = replace_line(lines, "- HR-DX overview docs (Google Drive", HRDX_BULLET, "hrdx")
    i3 = replace_line(lines, "- `service_cost_comparison.inaction_cost_low/high` still ships", INACTION_BULLET, "inaction")
    i4 = replace_line(lines, INFRA_OLD_PREFIX, INFRA_NEW, "infra")
    i5 = replace_line(lines, LAST_UPDATED_PREFIX, LAST_UPDATED_NEW, "lastupdated")
    i6 = replace_line(lines, ATTACH_FRICTION_PREFIX, ATTACH_FRICTION_NEW, "attach")
    lines.insert(i6 + 1, ATTACH_STEPBACK_NEW)

    # Section 14 row: after the "Hammer insight numbers are never reused" row
    ih14 = [i for i, l in enumerate(lines) if l.startswith("| **Hammer insight numbers are never reused**")]
    assert len(ih14) == 1, f"Section 14 anchor: {len(ih14)}"
    lines[ih14[0] + 1:ih14[0] + 1] = ["", SECTION14_ROW]

    # new open items: insert after the last "Open, not sequenced" bullet, i.e. right before the blank line that precedes "Infrastructure carry-forwards"
    ih = [i for i, l in enumerate(lines) if l.startswith("Infrastructure carry-forwards")]
    assert len(ih) == 1
    j = ih[0] - 1
    while lines[j].strip() == "":
        j -= 1
    for k, item in enumerate(NEW_ITEMS):
        lines.insert(j + 1 + k, item)

    # Section 16 entry appended after the final non-empty line
    while lines and lines[-1].strip() == "":
        lines.pop()
    lines.append("")
    lines.extend(SECTION16.rstrip("\n").split("\n"))
    lines.append("")
    new_text = nl.join(lines)

    ctext = CLAUDE.read_text(encoding="utf-8")
    assert "| MOB version | v4.329 |" in ctext, "CLAUDE.md MOB version row"
    new_ctext = ctext.replace("| MOB version | v4.329 |", "| MOB version | v4.330 |", 1)

    handoff = build_handoff(SECTION16)

    bad = [c for c in (";", "—") if c in SECTION16 or c in "".join(NEW_ITEMS) or c in FRICTION_BULLET + HRDX_BULLET + INACTION_BULLET + INFRA_NEW + LAST_UPDATED_NEW + ATTACH_FRICTION_NEW]
    print("semicolons/em-dashes in new text:", bad or "none")
    print(f"MOB lines {len(text.split(nl))} -> {len(lines)}; replaced 13b lines at {i1+1},{i2+1},{i3+1},{i4+1},{i5+1},{i6+1}")
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
