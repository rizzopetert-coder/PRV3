"""
PRV3 MOB Update -- Part 2: splice-numbering display bug, leaked dev
annotation/template placeholder, full splice-mechanism enumeration, the
Q28/Q31 conditional-design investigation, and the course-corrected build
(Q28 real conditional splice, Q31 parked, counter/label fix, copy fixes)

Updates tools/_mob.txt:
  - Section 14 (Locked Decisions Log): new entry appended after the
    "Path 1 genuinely live-verified" entry (ascending order, this
    section's newest tail)
  - Section 16 (Session Log): new one-line entry prepended before the
    prior entry's log line (descending order, this section's newest head)
  - Version bump v4.59 -> v4.60 (material workstream status change --
    investigation findings, a course-corrected design resolution, and a
    completed build all logged together)

Updates CLAUDE.md:
  - MOB version cross-reference v4.59 -> v4.60

Documentation-only change -- no product code touched by this script.
(Product code change committed alongside this MOB entry, same commit
batch, per Pete's explicit instruction to update this entry before
commit rather than after.)

Usage:
  python tools/patch_mob_part2_investigation.py --dry-run
  python tools/patch_mob_part2_investigation.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ═══════════════════════════════════════════════════════════════════════════
# tools/_mob.txt
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.59",
    "\\\\\\#\\\\\\# MOB v4.60",
)

# --- Section 14 (Locked Decisions Log, ascending -- append after newest tail) ---

LIVE_VERIFIED_ENTRY_TAIL = (
    "This is the first time in this project's history that a live session, "
    "through the real deployed API and real Redis, has produced a "
    "severity tier other than the 'Emerging' constant. MOB v4.59. |"
)

PART2_ENTRY = (
    "| **July 2026 — Live session investigation + course-corrected build: "
    "splice-numbering display bug, leaked dev annotation, template "
    "placeholder, Q28/Q31 design gap** | Surfaced by Pete's own manual "
    "live Preview session (the same session confirming Part 1's real "
    "severity firing) showing 'Question 36 of 34' / 'Question 40 of 34' "
    "and adaptive question text leaking verbatim dev annotations. "
    "**Counter root cause, confirmed exactly:** web/components/"
    "DiagnosticFlow.tsx:15 (`const TOTAL_QUESTIONS = 34`, fixed constant, "
    "never touched again), :238 (`questionNumber: questionNumber + 1`, "
    "incremented on every answer with zero awareness of whether the next "
    "question is core, a checkpoint distinguisher, or a severity "
    "follow-on), :161 (renders the raw counter against the fixed "
    "denominator directly). Confirmed independently via the Part 1 live "
    "round trip: that test session answered 38 total questions (34 core + "
    "2 checkpoint distinguishers + 2 severity follow-ons) to reach true "
    "completion -- had the browser UI driven it, it would have shown "
    "'Question 38 of 34' at the final step, the same bug pattern Pete saw "
    "mid-session. **Leaked annotation, source confirmed:** "
    "engine/data/questions.py:538-540 (Q28) and :582-583 (Q31) concatenate "
    "a dev note describing intended conditional behavior directly into "
    "question_text -- the exact string get_question_copy() returns "
    "verbatim to the client, not a rendering bug pulling the wrong field. "
    "**Template placeholder, confirmed and design ambiguity flagged "
    "beyond 'unimplemented':** '[earlier legal/compliance/HR matter]' is "
    "meant to reference back to whichever of Q06's options the principal "
    "selected -- but Q06 is a weighted_multi_select (4 real options + "
    "None), so even a working substitution needs a rule for which "
    "selected item to name if more than one was picked, an ambiguity in "
    "the design itself, left explicitly deferred, not resolved by this "
    "pass. **Full splice-mechanism enumeration:** (1) Phase 2 checkpoint "
    "distinguishers -- trigger: Shannon entropy over the accumulated "
    "ranking at fixed positions Q11/Q19/Q27; parent = the checkpoint "
    "position itself, not one specific answered question; multiplicity "
    "0-2 per parent (MAX_DISTINGUISHERS_PER_CHECKPOINT). (2) Severity "
    "follow-ons (SEVER-01..13) -- trigger: a specific core question's "
    "specific option carries severity_trigger=true; parent = the exact "
    "triggering question_id, known at splice time; multiplicity always 0 "
    "or 1 per parent (a session answers each core question once). "
    "(3) Q28/Q31 'Q06-conditional' -- confirmed NOT a splice mechanism at "
    "all as originally found: PHASE_1_QUESTION_SEQUENCE included both "
    "unconditionally, no skip/conditional-include logic existed anywhere, "
    "despite both questions' own embedded annotations claiming adaptive "
    "firing. **Q28/Q31 relationship investigated per Pete's direct "
    "challenge** (Q31's own 'Q28 not yet asked' guard would be "
    "permanently unreachable if Q28 fires deterministically whenever the "
    "same Q06 condition is true, which is exactly what Q28's annotation "
    "claims -- a real contradiction as literally written, not assumed). "
    "Found via tools/qsm_extracted.txt (the original pre-implementation "
    "Question Signal Map source) that the spec's checkpoints were "
    "originally Q12/Q20/Q28 -- one number higher than the implemented "
    "Q11/Q19/Q27 -- confirming real numbering drift occurred between spec "
    "and implementation, though this doesn't fully recover Q31's original "
    "intended relationship to Q28 on its own. **Claude Code's first-pass "
    "proposed resolution (build the guard as real, defensive, "
    "currently-inert logic) was course-corrected by Pete before any code "
    "was written**, applying the same principle already used once this "
    "session for Trajectory (Category A): correct-but-currently-inert "
    "code is worse than no code, since it produces a plausible-looking "
    "mechanism that can never actually produce a different outcome given "
    "today's data. Under a single Q06 condition, Q31's 'not yet asked' "
    "guard is mathematically proven to always evaluate as blocking -- "
    "building it would be dead code dressed as live defensive logic, the "
    "same landmine already avoided once tonight. **Resolution actually "
    "built:** Q28 is now a real conditional splice off Q06 (fires when A "
    "or B is selected), mirroring the existing severity/checkpoint splice "
    "pattern exactly, inserted immediately after Q06 rather than at its "
    "old fixed position 28. Q31 is excluded from "
    "web/lib/session-store.ts's PHASE_1_QUESTION_SEQUENCE entirely -- "
    "content intact in engine/data/questions.py, not deleted, not "
    "spliced, not guarded, no firing logic of any kind -- with an inline "
    "comment marking it explicitly PARKED and stating do not build firing "
    "logic until a real distinguishing condition is found or authored, "
    "not the current self-contradicting one. **Counter fix built:** "
    "web/lib/session-store.ts gains coreQuestionPosition() (a static "
    "indexOf+1 lookup against the now-32-entry PHASE_1_QUESTION_SEQUENCE, "
    "replacing the incrementing-counter pattern entirely, so a question's "
    "displayed position is always correct regardless of how many splices "
    "occurred earlier in the session) plus spliceLabel()/"
    "resolveQuestionLabel() for the '[parent][letter]' scheme, applied "
    "uniformly to checkpoint distinguishers, severity follow-ons, and "
    "Q28. Both session/start and session/answer routes now return a "
    "label object alongside each question; DiagnosticFlow.tsx renders "
    "'Question N of TOTAL' for core questions or 'Follow-up [label]' for "
    "spliced ones, replacing the fixed TOTAL_QUESTIONS=34 constant and "
    "its naive per-answer increment entirely. **Leaked annotation and "
    "placeholder fixed:** both Q28 and Q31's question_text stripped of "
    "the parenthetical dev annotation regardless of firing status; Q28's "
    "'[earlier legal/compliance/HR matter]' replaced with generic "
    "non-substituted phrasing ('You mentioned an earlier legal, "
    "compliance, or HR matter...'). The multi-select reference ambiguity "
    "stays explicitly deferred, not resolved by adding conditional "
    "firing. **Testing:** 4 pre-existing vitest assertions updated for "
    "the new 32-entry base length (all length/index math re-derived, not "
    "guessed -- checkpoint-triggering positions Q11/Q19/Q27B all sit "
    "before Q28's removal point so their own base indices are unchanged; "
    "only totals and Q34's final index shift); 1 test's Q28/Q31 "
    "illustrative example reworded to a generic multi-parent case since "
    "Q31 no longer fires under the current design; 12 new tests added for "
    "coreQuestionPosition/spliceLabel/resolveQuestionLabel and the "
    "Q28/Q31 exclusion itself -- vitest 36/36, tsc clean. Full Python "
    "regression sweep clean; 172-profile v23 suite unchanged at 169/172, "
    "verified not assumed. Confirmed via direct engine invocation that "
    "get_question_copy('Q28')/('Q31') both now return clean text with no "
    "leaked annotation and no unresolved template placeholder. "
    "**web/components/DiagnosticFlow.tsx already carried uncommitted, "
    "paused /diagnostic reskin changes (Stage 3, awaiting Pete's Stage 4 "
    "decision) before this task touched it** -- flagged explicitly, not "
    "silently mixed in. The two sets of changes are structurally "
    "orthogonal (styling-token class-name swaps vs. state/data-flow "
    "logic) so low collision risk, but both now sit uncommitted in the "
    "same file until Pete decides how to handle the reskin. **Open item "
    "carried, per Pete's explicit instruction:** non-integer parent ID "
    "labeling (Q03B/Q27B + letter format) deferred, documented only -- no "
    "current live case triggers it; spliceLabel() falls back to the raw "
    "parent ID rather than crashing if this is ever hit before it's "
    "resolved. MOB v4.60. |"
)

edit("tools/_mob.txt", LIVE_VERIFIED_ENTRY_TAIL, LIVE_VERIFIED_ENTRY_TAIL + "\n" + PART2_ENTRY)

# --- Section 16 (Session Log, descending -- prepend before newest head) ---

LIVE_VERIFIED_LOG_HEAD = (
    "| **July 2026 — Path 1 genuinely live-verified (real Preview round "
    "trip)** | Credential-access gap closed by Pete (vercel login/link/env "
    "pull). Deployment Protection bypass resolved via Pete-provisioned "
    "VERCEL_AUTOMATION_BYPASS_SECRET. Real HTTP round trip against a fresh "
    "Preview deployment (exact committed HEAD): session/start -> 38 "
    "answers -> completion, SEVER-04 deliberate + SEVER-05 incidental "
    "follow-ons both fired live, Q11 checkpoint distinguishers fired live, "
    "tier=Entrenched score=50.0, hand-verified against raw math. "
    "Independently confirmed via direct Upstash query (aggregate write "
    "matched, session key deleted per Transition Rule) -- not just trusted "
    "from the app's own response. Bypass secret briefly exposed in tool "
    "output mid-run (JWT in a Set-Cookie header), caught and redacted "
    "immediately, rotated by Pete, confirmed done. Decision Register Path "
    "1 row (open since Session 71) closed RESOLVED. Full detail in "
    "Section 14. MOB v4.59. |"
)

PART2_LOG_LINE = (
    "| **July 2026 — Splice counter bug, leaked annotation, Q28/Q31 "
    "design gap: investigated and fixed** | Counter root cause confirmed "
    "(DiagnosticFlow.tsx's fixed TOTAL_QUESTIONS=34 constant plus a naive "
    "per-answer increment with no splice awareness) and replaced with a "
    "static indexOf+1 lookup plus a '[parent][letter]' label scheme for "
    "spliced questions. Leaked dev annotation and an unresolved "
    "'[earlier legal/compliance/HR matter]' placeholder both stripped "
    "from Q28/Q31's question_text. Q28/Q31's self-contradicting guard "
    "investigated via the original pre-implementation Question Signal "
    "Map (confirms real spec-to-implementation numbering drift); "
    "Claude Code's first-pass guard-based proposal was course-corrected "
    "by Pete (same 'don't build correct-but-inert code' principle as "
    "Trajectory) -- Q28 built as a real conditional splice off Q06, Q31 "
    "excluded from the live sequence entirely and marked PARKED, content "
    "intact. vitest 36/36, tsc clean, 172-profile v23 suite unchanged at "
    "169/172. Full detail in Section 14. MOB v4.60. |"
)

edit("tools/_mob.txt", LIVE_VERIFIED_LOG_HEAD, PART2_LOG_LINE + "\n" + LIVE_VERIFIED_LOG_HEAD)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.59 |",
    "| MOB version | v4.60 |",
)


# ---------------------------------------------------------------------------

def apply(dry_run: bool):
    changed_files: dict[str, str] = {}
    errors = []

    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = changed_files.get(rel_path)
        if text is None:
            if not path.exists():
                errors.append(f"MISSING FILE: {rel_path}")
                continue
            text = path.read_text(encoding="utf-8")

        count = text.count(old)
        if count != 1:
            errors.append(
                f"{rel_path}: expected 1 match, found {count}\n"
                f"  --- anchor (first 160 chars) ---\n  {old[:160]!r}"
            )
            continue

        changed_files[rel_path] = text.replace(old, new, 1)

    print("=" * 72)
    print(f"MOB PART2-INVESTIGATION PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"Files touched: {len(changed_files)}")
    for rel_path in changed_files:
        print(f"  - {rel_path}")

    if errors:
        print("\nERRORS:" if dry_run else "\nERRORS — nothing written:")
        for e in errors:
            print(f"\n[ERROR] {e}")
        if not dry_run:
            sys.exit(1)
        return

    if dry_run:
        print("\nDry run OK — all anchors matched exactly once. No files written.")
        return

    for rel_path, text in changed_files.items():
        (REPO_ROOT / rel_path).write_text(text, encoding="utf-8")
    print("\nAll files written.")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
