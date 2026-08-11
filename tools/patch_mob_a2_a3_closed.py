"""
PRV3 -- MOB update: A.2 (Q06 multi-select) shipped, A.3 (reset + look-back)
partially shipped with edit-and-replay explicitly parked as its own scoped
item.

Version bump v4.139 -> v4.140: two shipped items touching live respondent-
facing behavior, not a session-log-only change.

Usage:
  python tools/patch_mob_a2_a3_closed.py --dry-run
  python tools/patch_mob_a2_a3_closed.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MOB = "tools/_mob.txt"

ANCHOR = (
    '| A6 (Section A.6, diagnostic-usability-findings-2026-08-09.md -- option-count/adequacy review) -- CLOSED, no structural issue found | 3 | **Closed -- reviewed via the new audit tool, no action needed** | N/A | 101 total questions audited (42 core, 37 spliced-live, 22 unreachable). Option-count signal: only 2 questions flagged as binary (2-option), both core -- Q41 and Q43 (Structure 1/2\'s yes/no gates) -- same legitimate factual-gate pattern already confirmed in this session\'s earlier live walkthrough for Q33/Q35-equivalent questions, not perception scales being forced into two options. The "no doesn\'t-apply/N-A option" keyword scan hit 96/101 questions -- logged as weak signal, not a finding, per Pete\'s explicit framing: that heuristic is near-universal across the library as currently worded and should not be re-run as if it were meaningful without narrowing it first (e.g. scoping to questions where an N-A option would plausibly change the respondent\'s ability to answer honestly, not a blanket keyword absence check). | This session (Claude Code) | Closed -- no further check-in. Reopen only if Pete wants a narrower pass at the "no N/A option" signal specifically, or if the audit tool surfaces something new on a future re-run |'
)

NEW_ROWS = (
    '\n'
    '| A.2 (Q06 select-all-that-apply) -- SHIPPED, full stack | 3 | **Closed -- built, verified, zero calibration movement** | N/A | Confirmed via direct source read (not a live-browser walk) before any code changed: Q06 is genuinely authored as format="weighted_multi_select" ("Select all that apply") but get_question_copy() stripped format before it ever reached the wire, and every downstream layer (QuestionCopy, QuestionView, AnswerRequest, AccumulatePayload, accumulate_one_answer) was single-option end to end -- not stale, not a design misread, never built. BUILD: wire contract widened to option_ids: string[] everywhere (one code path, not a dual option_id/option_ids branch) -- engine/main.py (format added to get_question_copy()\'s return; new accumulate_answers() wrapper loops the UNCHANGED accumulate_one_answer() once per selected option, threading accumulated_vector through sequentially -- confirmed necessary, not hypothetical: Q06\'s A option, severity_trigger=true -> SEVER-27, and D option, severity_trigger=true -> SEVER-21, mean a real multi-select answer selecting both fires two severity follow-ons from one submission), api/engine.py (/api/accumulate reads option_ids, calls accumulate_answers()), web/lib/engine-client.ts (QuestionCopy.format, AccumulatePayload.option_ids, AccumulateResult pluralized to severity_inputs/severity_follow_on_ids), web/lib/session-store.ts (AnswerLogEntry.option_ids), web/app/api/diagnostic/session/answer/route.ts (AnswerRequest widened + validated; severity-follow-on splice loop now handles multiple new IDs per submission, reusing spliceDistinguishers()\'s existing multi-ID capability and the checkpoint path\'s letterIndex labeling pattern rather than a parallel reimplementation; Q06->Q28 and Q44->Q45 conditions rewritten as .includes() checks), web/components/DiagnosticFlow.tsx (QuestionView gets a checkbox-plus-continue path gated on format === "weighted_multi_select", single-select path unchanged in behavior -- every click now sends a 1-element array through the same onAnswer(optionIds: string[]) callback). "None of the above" is mutually-exclusive-clearing (Pete-confirmed design), detected by text match ("none of the above") rather than a hardcoded option_id, so it generalizes to any future multi-select question without a code change -- matches the intake form\'s SignificantEventsField convention in spirit, not a literal shared-code reuse (different component, different data shape). Also updated to match the same wire contract, since both talk to the live API: web/lib/session-store.test.ts (3 literals), tools/diagnostic_fast_forward.py (would have silently broken next run otherwise). VERIFICATION: tsc --noEmit clean. Direct smoke test confirmed accumulate_answers(Q06, ["A","D"]) fires both SEVER-27 and SEVER-21, and the single-option path is byte-for-byte unchanged behavior. All Python unit suites identical to baseline (test_main 36/36, test_accumulation 43/43, test_output 112/112, test_checkpoint 58/58, test_severity 56/56, test_resolution_families 84/84, test_output_synthesis 56/56, test_contract 140/140). Full 172(+3)-profile regression: 171/175, zero movement -- generate_answers() never exercises Q06\'s multi-select path (always selects exactly one option), so nothing here could have moved it, confirmed not assumed. engine/data/validate.py 40/41, same pre-existing unrelated cluster_id gap. Live browser verification held for Pete post-push (Claude.ai + claude-in-chrome, same pairing as the original A.2/A.3 investigation walkthrough) -- no browser tool available in this Claude Code session, and no Preview environment exists to test against pre-push either; Pete\'s explicit call to push first and verify live on Production after, consistent with this project\'s existing no-Preview default workflow. | This session (Claude Code) | Closed -- no further check-in once Pete\'s post-push live verification confirms clean. If it doesn\'t, treat as a new incident, not a reopening of this row |\n'
    '| A.3 (back/forward/reset) -- PARTIALLY SHIPPED: reset + look-back only | 3 | **Reset + look-back closed and shipped; edit-and-replay explicitly parked, own scoped item** | Edit-and-replay -- Pete\'s deliberate descope this session, not forgotten: requires a truncate-and-replay design (cut question_sequence/answers_log/severity_inputs/checkpoint_q11-27/accumulated_vector back to the edited position, discard everything downstream, replay forward reusing session/answer/route.ts\'s existing per-step splice/checkpoint/accumulate logic) -- buildable, not architectural, but real, careful work, deliberately not bundled into this pass | Confirmed via direct source read before any code changed: zero navigation controls existed anywhere in DiagnosticFlow.tsx (the one pre-existing "Start over" button lived on the error phase only, never shown during a normal in-progress session) -- the original 2026-08-09 report was still fully accurate, nothing had changed since. BUILD, both genuinely non-mutating with respect to session/engine state: (1) Reset -- same kind of action as the pre-existing error-phase button (client-state discard only, no backend delete/expire call; an abandoned session already ages out via its existing 6-hour sliding TTL regardless of how it was abandoned, same as a closed browser tab today), now reachable during a normal in-progress session too (not just after an error) and now clears intake + history, reusing one shared handleReset() for both the error-phase and question-phase buttons rather than two divergent implementations. (2) Look-back -- a purely client-side mirror (new AnsweredEntry[] history state + read-only HistoryPanel component, toggled via a "Review your answers so far" link) of what this browser tab already rendered and submitted as the respondent progressed -- never reads or touches accumulated_vector/question_sequence/checkpoints/severity_inputs, confirmed by construction (built from the same `question`/`optionIds` values already in handleAnswer()\'s closure, not a new data source). Built as local React state rather than a new backend endpoint, since Phase 1 is single-tab/single-sitting by design -- the pre-existing dev-only ?session= resume param is a different, narrower mechanism (jumps to current position, doesn\'t carry history) and is untouched by this change. VERIFICATION: tsc --noEmit clean (same combined pass as A.2 above, both shipped together). No calibration-suite relevance -- pure UI addition, zero engine/scoring touch, confirmed by inspection not a separate regression run. Live browser verification held for Pete post-push, same reasoning as A.2\'s row above. | This session (Claude Code) | Reopen edit-and-replay whenever Pete wants to commit to that scoped effort -- not a forced check-in, the truncate-and-replay approach is already designed and ready to pick up |\n'
)


def apply(dry_run: bool) -> int:
    changed = 0
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count != 1:
        print(f"ERROR: {MOB} -- expected 1 match for anchor, found {count}")
        return 1
    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROWS, 1)
    if dry_run:
        print(f"OK (dry-run): {MOB} -- anchor found, would insert 2 new rows")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"WRITTEN: {MOB} -- 2 new rows inserted")
    changed += 1

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.139", "\\\\\\#\\\\\\# MOB v4.140"),
        ("CLAUDE.md", "| MOB version | v4.139 |", "| MOB version | v4.140 |"),
    ]
    for rel_path, old, new in version_edits:
        p = REPO_ROOT / rel_path
        t = p.read_text(encoding="utf-8")
        c = t.count(old)
        if c != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {c}")
            return 1
        nt = t.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            p.write_text(nt, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1

    print(f"\n{changed}/3 edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
