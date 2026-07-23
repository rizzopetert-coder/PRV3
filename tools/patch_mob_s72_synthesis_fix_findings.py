#!/usr/bin/env python
"""
PRV3 -- patch_mob_s72_synthesis_fix_findings.py
Updates tools/_mob.txt for this session's arc: synthesis timeout root-cause
fix (max_retries=1, commit 72a97b9), the separate Production ANTHROPIC_API_KEY
finding (401 AuthenticationError, distinct root cause, Pete action item),
settings.local.json Decision Register row closed (commits 69525ce/7c98a59),
and /book publish-readiness sweep findings folded into the existing
publish-decision row.

Edits:
  1. Section 13a: .claude/settings.local.json row -- marked Resolved.
  2. Section 13a: synthesis-timeout row -- split into two rows (retry-count
     fix RESOLVED; Production API key CONFIRMED, not fixed, Pete action).
  3. Section 13a: /book publish decision row -- this session's sweep
     findings folded in (nav/manifest/citation/shadow-model clean; two
     new gaps found: zero published entries, markdown body unwired).
  4. Section 14: new locked-decision entry appended (max_retries=1 fix).
  5. Section 16: new session-log entry appended.
  6. Version bump v4.62 -> v4.63 (new locked decision + Decision Register
     status changes -- material, not session-log-only).

Ordering note: this file's session log and locked-decisions sections have
inconsistent prepend/append conventions from years of prior sessions (own
prior commentary already flags this). New entries here are appended at the
end of their respective sections/file -- simplest, lowest-risk convention,
not an attempt to fix historical ordering.

Usage:
  python tools/patch_mob_s72_synthesis_fix_findings.py --dry-run
  python tools/patch_mob_s72_synthesis_fix_findings.py --write
"""
import argparse
import sys
from pathlib import Path

TARGET = Path(__file__).parents[1] / "tools" / "_mob.txt"

CHANGES = []


def edit(label, old, new):
    CHANGES.append((label, old, new))


# ── 1. Version bump ───────────────────────────────────────────────────────────
edit(
    "MOB version v4.62 -> v4.63",
    "\\\\\\#\\\\\\# MOB v4.62",
    "\\\\\\#\\\\\\# MOB v4.63",
)

# ── 2. Section 13a: settings.local.json row -- closed ─────────────────────────
edit(
    "Section 13a: settings.local.json row resolved",
    "| .claude/settings.local.json tracked in git (should be gitignored) | N/A — repo hygiene, not a Tier 1-4 workflow item | Open, no urgency | Committed since Session 37 (b3d58a6), no .gitignore entry excludes it — the file Claude Code's own convention treats as a personal, gitignored override is actually checked into this repo. Current tracked content confirmed safe (permissions allowlist only, no secrets ever committed there) — surfaced while confirming where VERCEL_TOKEN should NOT go (S71 Path 1 credential-access work). No urgency beyond not forgetting it exists — but a file positioned to silently absorb someone's next local override belongs on the record | Session 71 (Claude Code) | Session 72 — untrack (`git rm --cached`) and add to `.gitignore` |",
    "| .claude/settings.local.json tracked in git — RESOLVED | N/A — repo hygiene, not a Tier 1-4 workflow item | Resolved | Untracked via `git rm --cached` (commit 69525ce) and added to `.gitignore` (commit 7c98a59 -- two commits because the gitignore edit wasn't staged before the first landed, caught and fixed same session). Confirmed via `git ls-files` no longer tracked; confirmed via local filesystem check the file still exists on disk, untouched, not deleted. No prior `.claude/` pattern existed in `.gitignore` to explain the original gap -- plain omission, not a broken pattern that should have caught this | This session (Claude Code) | Closed -- no further check-in |",
)

# ── 3. Section 13a: synthesis-timeout row -- split into two ───────────────────
OLD_SYNTH_ROW = "| Synthesis call failing / falling back to static copy (5s LOCKED timeout, output_synthesis.py) | N/A — confirmed pre-launch defect, not a Tier 1-4 workflow item | Confirmed pre-launch defect in prv-3 — must be fixed before cutover. Zero current user impact: confirmed this session (Pete, direct) that prv-2 is the current live iteration actually serving real traffic at principalresolution.com / www.principalresolution.com; prv-3 (everything Path 1 built and tested this session, and the project this finding was found in) is the next iteration, not yet cut over — Pete controls cutover timing explicitly. An earlier framing in this same session briefly treated the alias structure as an open question / possible live-incident signal before Pete corrected it directly — noted here so it isn't rediscovered as new | Reproduced 3x identically on a Preview deployment (17.424s, 17.471s, 17.767s, all is_fallback=true) with a genuine APITimeoutError and visible Anthropic SDK auto-retry (two retry attempts logged, ~0.9s then ~0.4s backoff) — captured via temporary, uncommitted diagnostic logging added to output_synthesis.py's exception handler, deployed only to an ephemeral non-git `vercel deploy` build, then reverted via `git checkout --` and independently re-verified clean (`git status --porcelain` / `git diff` both empty) before this row was written. One Pete-authorized synthetic test call against prv-3's actual Production deployment (prv-3.vercel.app, confirmed via `vercel alias ls` as the real alias target of the current Ready Production build) also returned is_fallback=true, but with a materially different timing signature — 4.483s, too fast to contain even one full 5s-timeout-plus-retry cycle. Same symptom (fallback served instead of real synthesis), not yet confirmed to be the same root cause — the fast-fail shape is more consistent with an immediate API-level error or a different exception type than with the Preview timeout pattern. The real exception for the Production fast-fail has not been captured — doing so would require a second temporary-logging deploy, this time to Production itself rather than an ephemeral non-git build, which is a heavier and riskier action than the single plain HTTP test call already authorized; not done without a separate explicit go-ahead. No retry/timeout config has been changed anywhere — diagnosis only, per Pete's explicit instruction | Session 71 (Claude Code) | Before prv-3 cutover — must be resolved (or explicitly accepted as an understood, low-risk gap) before Pete authorizes cutting prv-3 over to serve real traffic. Not a session-number check-in |"

NEW_SYNTH_ROWS = """| Synthesis call timing out on first attempt (retry-count multiplying the 5s LOCKED timeout) — RESOLVED | N/A — confirmed pre-launch defect, fix committed | Root cause CONFIRMED and FIXED, not yet deployed/live-verified | Root cause confirmed via direct inspection of the installed Anthropic SDK source (0.119.0), not just timing correlation: `Anthropic()` was constructed with no `max_retries` override, so the SDK default (2 retries, 3 total attempts) applied -- each attempt gets its own full 5s timeout (the same request-options object, carrying the 5s LOCKED timeout, is reused across every retry in the SDK's loop), so a single logical "give up after 5s" call was actually taking ~3x5s+backoff (~17s), matching the Preview reproduction (17.4/17.5/17.8s) almost exactly. Fix: `max_retries=1` (not 0) per Pete's explicit trade-off decision -- keeps one retry for resilience against a single transient blip, accepting a longer worst-case fallback (~10.5s) instead of the fastest possible fail (~5s). Verified empirically, not just theoretically: a real non-responding local server, exercising the actual `synthesize()` code path (not mocked), measured the raw SDK retry loop at 10.551s (2 attempts, 5.4s apart), matching the ~10.4-10.5s prediction; the full wrapper measured ~12.3-12.5s, the extra ~1.8-2s isolated separately as `anthropic`'s own cold-import cost, unrelated to retry/backoff timing. Committed 72a97b9. 5s LOCKED timeout value itself unchanged, nothing else touched | This session (Claude Code) | Before prv-3 cutover -- confirm the fix holds under a real Preview/Production round trip once deployed, alongside the separate ANTHROPIC_API_KEY row below |
| Production ANTHROPIC_API_KEY invalid — 401 AuthenticationError on every synthesis call | N/A — confirmed active defect, distinct root cause from the timeout row above | Confirmed, NOT fixed -- Pete action required | Captured via Pete-authorized temporary diagnostic logging (server-side `print()` only, never in the HTTP response), deployed to `prv-3.vercel.app` Production with a locally-generated one-off `ENGINE_SECRET` override so the real Sensitive-flagged secret was never read. One authorized synthetic test call reproduced the previously-observed fast-fail (1.76s this run, 4.483s previously) and the log captured the real exception: `anthropic.AuthenticationError: Error code: 401 -- {'type': 'authentication_error', 'message': 'API key is invalid.'}`. This is NOT the same bug as the Preview timeout above -- auth errors are not in the SDK's retryable set, so there is no retry and no backoff, which is exactly why Production's fast-fail (~1.8-4.5s) never matched the timeout math (~17s uncapped / ~10.5s post-fix) no matter how it was modeled. Production's `ANTHROPIC_API_KEY` is invalid right now -- every single synthesis call fails, deterministically, 100% of the time, for a reason that has nothing to do with the retry/timeout fix. Diagnostic logging fully reverted (`git checkout --`, confirmed clean via both `git status --porcelain` and `git diff` independently) and Production redeployed clean from committed `main` to restore the `prv-3.vercel.app` alias before this row was written | This session (Claude Code) | Pete to rotate/replace `ANTHROPIC_API_KEY` in the Vercel dashboard (Production scope) -- not a Claude Code action. Before prv-3 cutover, both this row and the retry-fix row above need to be clear |"""

edit("Section 13a: synthesis-timeout row split (fix resolved + new API key row)", OLD_SYNTH_ROW, NEW_SYNTH_ROWS)

# ── 4. Section 13a: /book publish decision row -- sweep findings folded in ────
edit(
    "Section 13a: /book publish decision row updated with sweep findings",
    "| /book publish decision (50 drafted pieces) | 3 | Deferred | No decision made — not blocked externally | This session (discussed, not decided) | Session 72 |",
    "| /book publish decision (88 drafted pieces, corrected from earlier 50/71 progression-snapshot figures) | 3 | Deferred | No decision made -- not blocked externally. This session's readiness sweep (Claude Code): nav link confirmed live on every route (mounted once in root layout, single non-responsive markup shared by desktop/mobile); manifest/content cross-reference clean (88 manifest entries, 88 content files, zero missing, zero orphans); citation-free compliance re-verified by direct read of all 36 FTA-18-FTA-53 pieces (Session 57 finding holds, zero external claims without citation, the-unexamined-algorithm's real citations confirmed still attached); shadow-model sweep clean (zero hits for Pete's name or OneDigital across all 88 files). Two gaps found that block real discoverability regardless of this decision: (1) all 88 entries are `status: draft` or `parked`, zero `published` -- both the index page and the `[type]/[slug]` page gate strictly on `published`, so `/book` currently renders 'Coming soon.' live, confirmed by fetching it; (2) the `[type]/[slug]` page never renders the markdown body, only title+teaser -- a code comment describes this as deferred to a 'content migration pass' that appears not to have happened. Neither gap is a defect introduced this session -- both pre-exist, newly surfaced by this sweep | This session (Claude Code) | Session 72 -- and whenever Pete is ready to decide, the two gaps above need scoping alongside the publish decision itself, not discovered again after |",
)

# ── 5. Section 14: new locked-decision entry, appended ────────────────────────
OLD_SECTION14_TAIL = "| **July 2026 — Session 69** | Calibration pilot on 6 of the 10 Session 65/67/68 taxonomy-expansion states"
NEW_SECTION14_ENTRY = """| **July 2026 — Session 72 (synthesis timeout fix + Production API key finding)** | Two independent findings about output_synthesis.py's synthesis call, investigated and resolved to different degrees. **Root cause of the Preview timeout (~17s), CONFIRMED and FIXED:** the Anthropic client was constructed with no `max_retries` override, so the SDK default (2 retries, 3 total attempts) applied, each attempt getting its own full 5s LOCKED (Session 42) timeout rather than sharing one budget -- confirmed via direct inspection of the installed SDK source (0.119.0), not just timing correlation. **Fix, `max_retries=1` (not 0), per Pete's explicit trade-off decision:** keeps one retry for resilience against a single transient blip, trading a longer worst-case fallback (~10.5s) for that resilience over the fastest-possible-fail alternative (~5s). Verified empirically: a real non-responding local server, exercising the actual `synthesize()` code path rather than a mock, measured the raw SDK retry loop at 10.551s (2 real connection attempts, 5.4s apart), matching the ~10.4-10.5s prediction; the full wrapper's ~12.3-12.5s gap was isolated separately to `anthropic`'s own ~1.5s cold-import cost, unrelated to retry timing. Full 9/10 test suite clean (same pre-existing test_contract.py liability_block KeyError). Committed 72a97b9. **Separately, the Production fast-fail (previously 4.483s, never explained by the timeout math) was captured and found to be a completely different bug.** Pete authorized a temporary diagnostic-logging deploy to prv-3.vercel.app Production (server-side `print()` only, never in the HTTP response; a locally-generated one-off `ENGINE_SECRET` override meant the real Sensitive-flagged secret was never read). The captured exception: `anthropic.AuthenticationError: 401 -- API key is invalid`. Auth errors aren't in the SDK's retryable set, so there's no retry/backoff -- exactly why the fast-fail timing never matched any timeout-based model. Production's `ANTHROPIC_API_KEY` is invalid right now, causing a deterministic 100% failure rate on every synthesis call, unrelated to the retry-count bug. Diagnostic logging reverted (`git checkout --`, independently re-verified clean via both `git status --porcelain` and `git diff`) and Production redeployed clean from committed `main` before this entry was written. Key rotation is Pete's action item, not yet done. Full detail in Section 13a (two rows: retry-fix RESOLVED, API-key CONFIRMED/not fixed). **Same session, two other independent items closed:** `.claude/settings.local.json` untracked from git and added to `.gitignore` (commits 69525ce, 7c98a59 -- landed as two commits because the gitignore edit wasn't staged before the first landed, caught same session), closing the Decision Register row open since Session 37. `/book` publish-readiness verification (nav link confirmed live on every route; 88 manifest entries cross-referenced clean against 88 content files, zero missing/orphaned; citation-free compliance re-verified by direct read of all 36 FTA-18-FTA-53 pieces, Session 57 finding holds; shadow-model sweep clean, zero hits for Pete's name or OneDigital across all 88 files) surfaced two pre-existing gaps that block real discoverability regardless of the still-open publish decision: zero manifest entries are `status: published` (index renders "Coming soon." live), and the `[type]/[slug]` page never renders the markdown body, only title+teaser. Neither is a defect from this session, both newly surfaced by this sweep, folded into the existing publish-decision Decision Register row rather than opening new ones. CLAUDE.md MOB version cross-reference updated v4.62->v4.63. MOB version bumped to v4.63 -- a locked fix decision (max_retries=1) plus two Decision Register status changes (settings.local.json resolved, synthesis row split) warrant a bump per the closeout protocol. MOB v4.63. |
| **July 2026 — Session 69** | Calibration pilot on 6 of the 10 Session 65/67/68 taxonomy-expansion states"""
edit("Section 14: append Session 72 synthesis-fix entry before Session 69 entry", OLD_SECTION14_TAIL, NEW_SECTION14_ENTRY)

# ── 6. Section 16 Session Log: new entry appended at end of file ──────────────
OLD_LOG_TAIL = "| \\\\\\*\\\\\\*May 2026 — Session 1\\\\\\*\\\\\\* | Taxonomy consolidation (108 to 47 states), name register audit, Liability Risk Framework, Leadership Competency Framework, Signal Map. All 47 states profiled. Four cluster identifiers confirmed. Eight root conditions named. MOB v1.0 created. |"
NEW_LOG_ENTRY = """| **July 2026 — Session 72 (synthesis timeout fix, Production API key finding, repo hygiene, /book compliance sweep)** | Three independent tasks, each held for its own dry-run/review checkpoint, no batched commits. **Task 1 -- synthesis timeout.** Confirmed root cause via direct SDK source inspection (not timing correlation alone): default `max_retries=2` meant 3 total attempts, each getting a full 5s LOCKED timeout rather than sharing one budget, matching the ~17s Preview reproduction. Fixed with `max_retries=1` (Pete's explicit choice over 0 -- keeps one retry for resilience against a transient blip, ~10.5s worst case instead of ~5s). Timing verified empirically against a real non-responding local server exercising the actual `synthesize()` code path: raw SDK loop measured 10.551s, matching the prediction; the fuller ~12.3-12.5s wrapper figure was isolated to `anthropic`'s own cold-import cost, not retry/backoff. Full 9/10 suite clean (same pre-existing test_contract.py failure). Committed 72a97b9. Separately, Pete authorized capturing the Production fast-fail's real exception -- deployed temporary server-log-only diagnostic logging to prv-3.vercel.app Production (one-off `ENGINE_SECRET` override so the real secret was never read), captured `anthropic.AuthenticationError: 401 -- API key is invalid`, a completely different bug from the timeout (auth errors aren't retried, explaining why the fast-fail never matched any timeout model). Production's `ANTHROPIC_API_KEY` is invalid right now, 100% failure rate, unrelated to the retry fix. Diagnostic logging reverted and independently re-verified clean; Production redeployed clean from `main`. Key rotation is Pete's action item. **Task 2 -- repo hygiene.** `.claude/settings.local.json` untracked (`git rm --cached`) and added to `.gitignore`, closing the Decision Register row open since Session 37 -- landed as two commits (69525ce, 7c98a59) after a staging slip caught same session. **Task 3 -- /book publish readiness.** Nav link confirmed live (not just in source) on every route; manifest count corrected to the real figure, 88 entries (53 FTA + 35 LIB), cross-referenced clean against 88 content files (zero missing, zero orphaned) -- superseding the MOB's stale 71-entry progression snapshot. Citation-free compliance re-verified by direct read of all 36 FTA-18-FTA-53 pieces (Session 57's finding holds). Shadow-model sweep (Pete's name, OneDigital) clean across all 88 files. Two pre-existing gaps surfaced, not fixed this session: zero manifest entries are `status: published` (the live index currently renders "Coming soon."), and the `[type]/[slug]` page never renders the markdown body, only title+teaser. Full detail in Section 14 and Section 13a (three rows updated: settings.local.json resolved, synthesis row split into two, /book publish-decision row updated with sweep findings). MOB v4.62->v4.63. |
| **May 2026 — Session 1** | Taxonomy consolidation (108 to 47 states), name register audit, Liability Risk Framework, Leadership Competency Framework, Signal Map. All 47 states profiled. Four cluster identifiers confirmed. Eight root conditions named. MOB v1.0 created. |"""
edit("Section 16: append Session 72 log entry at end of file", OLD_LOG_TAIL, NEW_LOG_ENTRY)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    if not TARGET.exists():
        print(f"ERROR: target not found: {TARGET}")
        sys.exit(1)

    text = TARGET.read_text(encoding="utf-8")

    if args.dry_run:
        print(f"DRY RUN -- target: {TARGET}")
        print(f"  {len(CHANGES)} change(s) to apply:")
        all_ok = True
        for label, old, new in CHANGES:
            count = text.count(old)
            status = f"OK ({count}x)" if count == 1 else ("MISS" if count == 0 else f"AMBIGUOUS ({count}x)")
            if count != 1:
                all_ok = False
            print(f"  [{status}] {label}")
        if not all_ok:
            print("\n  ERROR: one or more OLD strings not found exactly once in target.")
            sys.exit(1)
        print("\n  All anchors matched exactly once. Ready for --write.")
        return

    for label, old, new in CHANGES:
        count = text.count(old)
        if count != 1:
            print(f"ERROR: OLD string for '{label}' matched {count} times (expected 1) -- aborting.")
            sys.exit(1)

    new_text = text
    for label, old, new in CHANGES:
        new_text = new_text.replace(old, new, 1)

    if new_text == text:
        print("ERROR: no changes produced.")
        sys.exit(1)

    TARGET.write_text(new_text, encoding="utf-8")
    print(f"WRITTEN: {TARGET}")
    print(f"  {len(CHANGES)} change(s) applied")


if __name__ == "__main__":
    main()
