#!/usr/bin/env python
"""
PRV3 -- patch_mob_fast_forward_tool.py
Logs the new dev-only diagnostic fast-forward tool (tools/diagnostic_fast_forward.py,
commit bae2296) and, as its own separate entry, the built_to_fail /
calibration-vs-live-signal finding surfaced while building and verifying it.
Bumps MOB version v4.66 -> v4.67.

Usage:
  python tools/patch_mob_fast_forward_tool.py --dry-run
  python tools/patch_mob_fast_forward_tool.py --write
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
    "MOB version v4.66 -> v4.67",
    "\\\\\\#\\\\\\# MOB v4.66",
    "\\\\\\#\\\\\\# MOB v4.67",
)

# ── 2. Section 13a: append new tool + finding rows after the last existing row
OLD_LAST_13A_ROW = '''| Untracked pre-existing file pile (~94 entries: documents/*.docx, prompts/*.md, various tools/patch_*.py and diagnostic scripts) | N/A — repo hygiene, not a Tier 1-4 workflow item | Open, deliberately deferred | Surfaced during this session's closeout `git status` review. Confirmed to predate this session entirely -- none of it was touched, reviewed, or verified here. Two files from this session's own actual work (.gitignore, tools/test_main.py) were identified separately, committed on their own (8873dd2), and are not part of this pile. Pete's explicit call: a pile this size deserves its own dedicated pass, not a tail-end closeout decision -- left untouched on purpose so a future session knows it was seen and deliberately skipped, not missed | This session (2026-07-23) | Whenever Pete schedules a dedicated pass for it -- not a forced check-in, not something to chip away at incidentally during unrelated work |'''

NEW_13A_ROWS = OLD_LAST_13A_ROW + '''
| Diagnostic fast-forward tool -- tools/diagnostic_fast_forward.py, Preview-only | N/A -- dev tooling, not a Tier 1-4 workflow item | Shipped, live-verified | CLI (zero external Python dependencies) drives the REAL live Path 1 API (session/start, session/answer, and a new read-only session/resume route) against a Preview deployment, reusing calibration_runner.py's state-targeting logic (best_option_for_state / _neutral_option) unmodified -- new logic is limited to severity targeting (SEVER-## follow-ons, which generate_answers() never simulates) and the HTTP driving loop itself, following whatever question_id the live route returns at each step since checkpoints/severity follow-ons/Q28 are dynamically spliced in, not precomputed. Mode 1 (complete) posts the finished result to a new dev-only /api/dev/diagnostic-preview route/page, rendering it through the real <PrivateOutput> component with a visible "DEV / TEST ONLY" banner -- backed by a new DevDiagnosticPreviewPayload type deliberately distinct from PrivateOutputPayload (whose own doc comment is an absolute "NEVER serialized to persistent storage" contract), same field shapes via reused sub-types, new top-level name, so that contract is never given an exception, per Pete's explicit choice among three options presented. Mode 2 (jump) stops before a requested core question position and prints a /diagnostic?session=<id> resume link -- required an additive change to DiagnosticFlow.tsx and diagnostic/page.tsx (a ?session= query param skips the intake gate and resumes directly), confirmed via a rigorous before/after regression check that the no-param path a real respondent uses is byte-for-byte unchanged (every diff reduced to two known inert artifacts: Next's per-request hydration nonce and React's own Suspense-boundary comment markers). Both new backend routes 404 before touching Redis if VERCEL_ENV is "production" -- not independently live-tested against Production itself since the code was never deployed there, correct by construction (VERCEL_ENV is Vercel's own reliable per-environment signal), flagged as such rather than overclaimed. Live-verified on Preview: Mode 1's viewer renders real content end-to-end; Mode 2's resume endpoint returned the correct live question/position for a real session, and Pete manually confirmed the resume link lands correctly in-browser, closing the one gap automated testing couldn't reach. Commit bae2296 | This session (Claude Code) | Closed -- no further check-in. Tool is ready for use; if a future session needs the same Preview-only driving pattern for something else, this is the reusable precedent |
| built_to_fail calibration-vs-live-signal finding -- informational, no action requested | N/A -- calibration/content fact, not a Tier 1-4 workflow item | Confirmed, informational only | Surfaced while building and verifying the fast-forward tool above: two live Phase 1 sessions targeting built_to_fail (and a third targeting the_overloaded_manager) both failed to land that state as primary, contradicting the MOB's own repeated finding (Session 69 and others) that built_to_fail "reliably achieves rank-1" in the calibration confusion matrix. Root cause: calibration_runner.py's `_CORE_QUESTION_IDS` (the offline test harness's answer-generation scope) includes every "Q..." question in QUESTION_LIBRARY, which covers Q35-39 (Aptitude addenda) -- but Phase 1's live flow (`PHASE_1_QUESTION_SEQUENCE`, session-store.ts) explicitly excludes Q35-39 by design ("no Aptitude addenda", per that file's own header comment). built_to_fail is wired to Q20 (a real Phase-1-reachable core question) plus Q03A/Q35/Q36/Q39 -- of these, only Q20 is actually reachable in a live Phase 1 session; Q03A is excluded too, since Phase 1's locked intake adapter always takes the Q03B branch. So built_to_fail's calibration-proven dominance is earned partly on signal a live Phase 1 session structurally cannot access. This does NOT invalidate the calibration suite itself, which correctly tests what it's scoped to test -- it flags that calibration confidence numbers are not a direct proxy for live-flow behavior, and that gap is currently undocumented anywhere else. No fix proposed or requested here | This session (Claude Code) | No forced check-in -- informational, for whoever next reasons about calibration-vs-live parity or extends Phase 1's reachable question set |'''

edit("Section 13a: append fast-forward tool + calibration-vs-live-signal finding rows", OLD_LAST_13A_ROW, NEW_13A_ROWS)

# ── 3. Section 14: new locked/shipped entry, prepended before the /book go-live entry
OLD_SECTION14_ANCHOR = "| **July 2026 — /book go-live: 87 pieces published to Production**"
NEW_SECTION14_ENTRY = """| **July 2026 — Diagnostic fast-forward tool shipped (Preview-only) + calibration-vs-live-signal finding** | New dev tool: `tools/diagnostic_fast_forward.py`, two modes, drives the real live Path 1 API against a Preview deployment rather than the offline calibration harness -- reuses `best_option_for_state()`/`_neutral_option()` unmodified for state-targeting; new logic is severity targeting (a real gap, since `generate_answers()` never simulates `SEVER-##` follow-ons) and the HTTP driving loop, which follows whatever `question_id` the live route actually returns at each step rather than a precomputed list. **Mode 1 (complete)** posts the finished result to a new dev-only viewer (`/api/dev/diagnostic-preview` + `/dev/diagnostic-preview/[id]`), rendered through the real `<PrivateOutput>` component. Building this surfaced a real persistence-contract conflict: `PrivateOutputPayload`'s own doc comment is an absolute "NEVER serialized to persistent storage" contract -- resolved per Pete's explicit choice (one of three options presented) by defining a new, genuinely separate `DevDiagnosticPreviewPayload` type with the same field shapes rather than creating an exception to that contract. **Mode 2 (jump)** stops before a requested question and prints a `/diagnostic?session=<id>` resume link -- required a new read-only `session/resume` API route plus an additive `?session=` capability in `DiagnosticFlow.tsx` and `diagnostic/page.tsx`. The no-param path every real respondent uses was proven byte-for-byte unchanged via a rigorous before/after diff (every apparent difference traced to two known, inert artifacts: Next's per-request hydration nonce and React's own Suspense-boundary comment markers). Both new backend routes refuse to serve on Production (`VERCEL_ENV` check, before Redis is ever touched) -- correct by construction, not independently live-tested since this code was never deployed to Production. Live-verified on Preview end to end; Pete manually confirmed the Mode 2 resume link lands correctly in-browser. **Separate finding, logged on its own:** testing surfaced that `built_to_fail` -- documented elsewhere in this MOB as the state that "reliably achieves rank-1" in calibration -- did not land as primary state in live Phase 1 runs. Root cause: `calibration_runner.py`'s test-answer generation scope includes Q35-39 (Aptitude addenda), which Phase 1's actual live flow structurally never reaches (`session-store.ts`'s own "no Aptitude addenda" scope comment) -- `built_to_fail`'s calibration confidence rests partly on signal a live session cannot access. Not a defect in the calibration suite, which correctly tests what it's scoped to test; flags that calibration numbers aren't a direct proxy for live-flow behavior. No action requested, informational only. Full detail on both in Section 13a. Commit bae2296. CLAUDE.md MOB version cross-reference updated v4.66->v4.67. MOB version bumped to v4.67 -- a new standing dev tool plus a calibration-parity finding worth carrying forward both warrant a bump per the closeout protocol. MOB v4.67. |
| **July 2026 — /book go-live: 87 pieces published to Production**"""

edit("Section 14: prepend fast-forward tool + finding entry", OLD_SECTION14_ANCHOR, NEW_SECTION14_ENTRY)

# ── 4. Section 16 Session Log: appended at end of file ─────────────────────────
OLD_LOG_TAIL = '''| **May 2026 — Session 1** | Taxonomy consolidation (108 to 47 states), name register audit, Liability Risk Framework, Leadership Competency Framework, Signal Map. All 47 states profiled. Four cluster identifiers confirmed. Eight root conditions named. MOB v1.0 created. |'''
NEW_LOG_ENTRY = '''| **July 2026 — Diagnostic fast-forward tool + calibration-vs-live-signal finding** | Built `tools/diagnostic_fast_forward.py` (Preview-only, two modes: complete-to-report and jump-to-question-N), driving the real live Path 1 API rather than the offline calibration harness, reusing state-targeting logic unmodified. New: severity targeting (a gap `generate_answers()` always had), a dynamic HTTP driving loop, a new dev-only completed-report viewer (backed by a genuinely separate `DevDiagnosticPreviewPayload` type per Pete's explicit call, not an exception to `PrivateOutputPayload`'s persistence contract), and an additive `?session=` resume capability in `DiagnosticFlow.tsx`/`diagnostic/page.tsx` -- the no-param path proven byte-for-byte unchanged via rigorous before/after diffing. Live-verified on Preview both modes; Pete manually confirmed the resume link in-browser. Separately logged: `built_to_fail` did not reliably land as primary state in live testing despite calibration's "reliably rank-1" finding -- traced to `calibration_runner.py` exercising Q35-39 questions Phase 1's live flow never reaches. Informational only, no action requested. Commit bae2296. Full detail in Section 14 and Section 13a. MOB v4.66->v4.67. |
| **May 2026 — Session 1** | Taxonomy consolidation (108 to 47 states), name register audit, Liability Risk Framework, Leadership Competency Framework, Signal Map. All 47 states profiled. Four cluster identifiers confirmed. Eight root conditions named. MOB v1.0 created. |'''

edit("Section 16: append session-log entry at end of file", OLD_LOG_TAIL, NEW_LOG_ENTRY)


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
