"""
PRV3 MOB Update -- Path 1 severity wiring complete at the code level,
live verification blocked on the Session 71 credential-access gap

Updates tools/_mob.txt:
  - Section 14 (Locked Decisions Log): new entry appended after the
    prior severity-wiring entry (ascending order, this section's
    newest tail)
  - Section 16 (Session Log): new one-line entry prepended before the
    prior severity-wiring log line (descending order, this section's
    newest head)
  - Version bump v4.57 -> v4.58 (material workstream status change --
    Path 1 severity wiring is now code-complete end-to-end)

Updates CLAUDE.md:
  - MOB version cross-reference v4.57 -> v4.58

Documentation-only change -- no product code touched by this script.
(Product code change already committed separately: c82c67a.)

Usage:
  python tools/patch_mob_path1_live_wiring.py --dry-run
  python tools/patch_mob_path1_live_wiring.py --write
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
    "\\\\\\#\\\\\\# MOB v4.57",
    "\\\\\\#\\\\\\# MOB v4.58",
)

# --- Section 14 (Locked Decisions Log, ascending -- append after newest tail) ---

PRIOR_ENTRY_TAIL = (
    "**New prerequisite logged, named and distinct from the now-resolved "
    "orchestrator-wiring prerequisite:** extending generate_answers() to "
    "simulate answering triggered severity follow-ons is required before "
    "duration_band or any other severity weight can be calibrated against "
    "real profile data -- a test-harness gap one level up from the "
    "severity-follow-on-orchestrator-wiring prerequisite this same entry "
    "resolves for Path 1. Not actioned, not scoped further here. MOB v4.57. |"
)

LIVE_WIRING_ENTRY = (
    "| **July 2026 — Path 1 severity wiring complete at the code level, "
    "live verification blocked on Session 71 credential gap** | Completes "
    "the trigger-out/input-in wire contract session/answer/route.ts needs "
    "to actually splice SEVER-## follow-ons into a live session and collect "
    "their answers into severity.tier at completion -- the prior commit "
    "wired the engine layer only. **engine/main.py:** accumulate_one_answer() "
    "gains a third return key, severity_follow_on_id -- surfaces the "
    "just-answered option's own severity_trigger (e.g. Q22-D -> 'SEVER-04') "
    "so the caller knows to splice a follow-on in. This is the missing half "
    "of the prior commit's severity_input, which only covered the follow-on's "
    "own answer, not the triggering question -- a small, necessary addition "
    "beyond the two files Pete named, flagged rather than silently done. "
    "**api/engine.py:** /api/accumulate now passes the full 3-key result "
    "through instead of discarding it to a bare vector; /api/complete threads "
    "severity_inputs into run_accumulated_engine(). **web/lib/engine-client.ts:** "
    "new SeverityInputPayload type, AccumulateResult return shape, "
    "CompletePayload.severity_inputs. **web/lib/session-store.ts:** "
    "DiagnosticSession.severity_inputs (append-only, mirrors answers_log); "
    "new severityFollowOnAlreadyAsked() guards against SEVER-11's documented "
    "dual-trigger case (Q28 and Q31 both map to it, per questions.py's own "
    "header comment) -- safe given Q28 always precedes Q31 in "
    "PHASE_1_QUESTION_SEQUENCE. **session/answer/route.ts:** collects "
    "severity_input into session state, splices severity_follow_on_id via "
    "the existing spliceDistinguishers() (reused directly for a "
    "single-element list, not duplicated), threads severity_inputs into "
    "the Q34 completion call. Commit c82c67a. **Testing:** tools/test_main.py "
    "36/0 (new coverage for severity_follow_on_id firing and non-firing "
    "cases); full Python regression sweep clean; full 172-profile v23 suite "
    "unchanged at 169/172, verified not assumed; test_contract.py's "
    "pre-existing unrelated KeyError confirmed unchanged. tsc --noEmit clean "
    "(one existing test file, engine-client.test.ts, needed severity_inputs: "
    "[] added to two literals, plus 2 new tests exercising real content). "
    "vitest 27/27 -- 5 new tests: spliceDistinguishers() reused for a single "
    "severity follow-on, a compounding-splice case alongside a checkpoint "
    "splice on the same evolving array, and 3 for severityFollowOnAlreadyAsked() "
    "including the SEVER-11 dual-trigger regression case. **Hand-verified the "
    "real trigger-out/input-in contract end-to-end through the actual "
    "modified functions, not reimplemented logic:** Q22-D surfaces "
    "severity_follow_on_id='SEVER-04' with severity_input=None; SEVER-04-D "
    "produces the real SeverityInput dict with severity_follow_on_id=None; "
    "completion with the collected list produces tier=Entrenched, "
    "score=33.33. **NOT yet live-verified -- explicitly blocked, not "
    "skipped:** a genuine browser/Redis/HTTP round trip against Preview was "
    "not performed. Confirmed directly before writing this entry: "
    "ENGINE_URL/ENGINE_SECRET unset, no .env files present, vercel CLI has "
    "no authenticated token in this sandbox -- the identical credential-"
    "access gap tracked in Section 13a's Decision Register, Path 1 row, "
    "since Session 71, not a new or avoidable blocker. The live round trip "
    "is the explicit remaining step before Path 1 can be called genuinely "
    "live, and requires Pete's action on the credential-access path (or "
    "Pete running the check directly against a real Preview deployment), "
    "not further Claude Code work from this sandbox. MOB v4.58. |"
)

edit("tools/_mob.txt", PRIOR_ENTRY_TAIL, PRIOR_ENTRY_TAIL + "\n" + LIVE_WIRING_ENTRY)

# --- Section 16 (Session Log, descending -- prepend before newest head) ---

PRIOR_LOG_HEAD = (
    "| **July 2026 — Severity follow-on wiring shipped (Path 1), new test-"
    "harness prerequisite** | All 13 SEVER-## questions tagged with "
    "severity_input_mapping (engine/data/questions.py); accumulate_one_answer() "
    "and run_accumulated_engine() wired to construct real SeverityInput objects "
    "and call add_input() (engine/main.py), commit 03b40a6. First non-"
    "'Emerging' severity tier ever produced, hand-verified (Entrenched and "
    "Endemic cases). api/engine.py's /api/accumulate route needs a companion "
    "update before Path 1 is live-functional for severity -- flagged, not "
    "fixed this pass. Standalone tools/severity_tier_validation.py (169/172 "
    "v23 baseline untouched) found 150/169 match expected tier, but the real "
    "finding is that generate_answers() never simulates severity follow-on "
    "answers -- a new, named test-harness prerequisite, distinct from and one "
    "level up from the now-resolved orchestrator-wiring prerequisite. Full "
    "detail in Section 14. MOB v4.57. |"
)

LIVE_WIRING_LOG_LINE = (
    "| **July 2026 — Path 1 severity wiring complete at the code level, "
    "live verification blocked** | api/engine.py + web/lib/session-store.ts "
    "+ session/answer/route.ts wired to splice SEVER-## follow-ons into a "
    "live sequence and thread collected severity_inputs into completion, "
    "commit c82c67a. tools/test_main.py 36/0, vitest 27/27, tsc clean, "
    "172-profile v23 suite unchanged at 169/172. Hand-verified the real "
    "trigger-out/input-in contract (Q22-D -> SEVER-04 -> tier=Entrenched) "
    "through the actual modified functions. NOT live-verified -- blocked on "
    "the Session 71 credential-access gap (no ENGINE_URL/ENGINE_SECRET, no "
    "authenticated Vercel token in this sandbox), not a new blocker. Live "
    "browser/Redis round trip against Preview is the explicit remaining "
    "step, requires Pete's action. Full detail in Section 14. MOB v4.58. |"
)

edit("tools/_mob.txt", PRIOR_LOG_HEAD, LIVE_WIRING_LOG_LINE + "\n" + PRIOR_LOG_HEAD)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.57 |",
    "| MOB version | v4.58 |",
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
    print(f"MOB PATH1-LIVE-WIRING PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
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
