"""
PRV3 -- MOB update: Category D (free condensed diagnostic) concept sketch
written to prompts/category-d-condensed-diagnostic.md. Planning artifact
only -- no code changes, no engine writes.

Version bump v4.140 -> v4.141: new durable planning doc + Decision
Register row tracking a new business-idea investigation, not a
session-log-only change.

Usage:
  python tools/patch_mob_category_d_sketch.py --dry-run
  python tools/patch_mob_category_d_sketch.py --write
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
    "| A.3 (back/forward/reset) -- PARTIALLY SHIPPED: reset + look-back only | 3 | **Reset + look-back closed and shipped; edit-and-replay explicitly parked, own scoped item** | Edit-and-replay -- Pete's deliberate descope this session, not forgotten: requires a truncate-and-replay design (cut question_sequence/answers_log/severity_inputs/checkpoint_q11-27/accumulated_vector back to the edited position, discard everything downstream, replay forward reusing session/answer/route.ts's existing per-step splice/checkpoint/accumulate logic) -- buildable, not architectural, but real, careful work, deliberately not bundled into this pass | Confirmed via direct source read before any code changed: zero navigation controls existed anywhere in DiagnosticFlow.tsx (the one pre-existing \"Start over\" button lived on the error phase only, never shown during a normal in-progress session) -- the original 2026-08-09 report was still fully accurate, nothing had changed since. BUILD, both genuinely non-mutating with respect to session/engine state: (1) Reset -- same kind of action as the pre-existing error-phase button (client-state discard only, no backend delete/expire call; an abandoned session already ages out via its existing 6-hour sliding TTL regardless of how it was abandoned, same as a closed browser tab today), now reachable during a normal in-progress session too (not just after an error) and now clears intake + history, reusing one shared handleReset() for both the error-phase and question-phase buttons rather than two divergent implementations. (2) Look-back -- a purely client-side mirror (new AnsweredEntry[] history state + read-only HistoryPanel component, toggled via a \"Review your answers so far\" link) of what this browser tab already rendered and submitted as the respondent progressed -- never reads or touches accumulated_vector/question_sequence/checkpoints/severity_inputs, confirmed by construction (built from the same `question`/`optionIds` values already in handleAnswer()'s closure, not a new data source). Built as local React state rather than a new backend endpoint, since Phase 1 is single-tab/single-sitting by design -- the pre-existing dev-only ?session= resume param is a different, narrower mechanism (jumps to current position, doesn't carry history) and is untouched by this change. VERIFICATION: tsc --noEmit clean (same combined pass as A.2 above, both shipped together). No calibration-suite relevance -- pure UI addition, zero engine/scoring touch, confirmed by inspection not a separate regression run. Live browser verification held for Pete post-push, same reasoning as A.2's row above. | This session (Claude Code) | Reopen edit-and-replay whenever Pete wants to commit to that scoped effort -- not a forced check-in, the truncate-and-replay approach is already designed and ready to pick up |"
)

NEW_ROW = (
    '\n'
    '| Category D (free condensed diagnostic) -- concept sketch drafted | 3 | **Exploratory, not approved for build** | N/A | prompts/category-d-condensed-diagnostic.md written -- a durable planning artifact, no code changes, no engine writes. Concept: a <5-minute free experience (8-10 questions, drawn entirely from the existing 42 core questions -- zero new content, zero new taxonomy, zero calibration risk) producing a real-but-thin report as a lead-capture point funneling toward the paid full Dx. Result shape truncates the full report structurally (top state only, 2-3 indicators, one-paragraph synthesis, a simple single-benchmark financial figure instead of full Friction Tax) with truncation shown visibly, not silently omitted. The financial mechanic is explicitly NOT Friction Tax\'s multi-state compounding model -- flagged as needing its own (lighter) Demographic Applicability Filter pass per the existing locked protocol before any real benchmark figure ships. Full diagnostic stays exactly as-is (free, ungated) regardless of this build -- any paywall/lead-capture gating decision for the full Dx is explicitly a separate, later decision, not blocking. Three open questions logged unresolved, Pete\'s call: exact question count (8-10, or review concrete candidates first), visible-truncation UI treatment, and the full-Dx gating mechanism. | This session (Claude Code) | Pete\'s call -- reopen when ready to review concrete candidate questions and move toward a build decision, not a forced check-in |\n'
)


def apply(dry_run: bool) -> int:
    changed = 0
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count != 1:
        print(f"ERROR: {MOB} -- expected 1 match for anchor, found {count}")
        return 1
    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROW, 1)
    if dry_run:
        print(f"OK (dry-run): {MOB} -- anchor found, would insert 1 new row")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"WRITTEN: {MOB} -- 1 new row inserted")
    changed += 1

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.140", "\\\\\\#\\\\\\# MOB v4.141"),
        ("CLAUDE.md", "| MOB version | v4.140 |", "| MOB version | v4.141 |"),
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
