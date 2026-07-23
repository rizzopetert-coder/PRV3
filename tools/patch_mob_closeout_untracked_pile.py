"""
PRV3 MOB Update -- Closeout: log the ~94-entry pre-existing untracked-file
pile as seen and deliberately deferred, not missed

Updates tools/_mob.txt:
  - Section 13a (Decision Register): new row appended after the OD-07
    closed row (last row in the table)
  - Section 16 (Session Log): new one-line closeout entry prepended
    before the reskin-correction entry's log line
  - Version bump v4.61 -> v4.62 (session log entry -- closeout wrap-up,
    not a locked-decision change)

Updates CLAUDE.md:
  - MOB version cross-reference v4.61 -> v4.62

Documentation-only change -- no product code touched by this script.

Usage:
  python tools/patch_mob_closeout_untracked_pile.py --dry-run
  python tools/patch_mob_closeout_untracked_pile.py --write
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
    "\\\\\\#\\\\\\# MOB v4.61",
    "\\\\\\#\\\\\\# MOB v4.62",
)

# --- Section 13a (Decision Register): new row after the last existing row ---

OD07_ROW_TAIL = (
    "| This session (2026-07-21) | Closed — no further check-in. Building "
    "the three reference mockups into the live site is separate, "
    "un-scoped future work, not tracked as an open item here |"
)

UNTRACKED_PILE_ROW = (
    "| Untracked pre-existing file pile (~94 entries: documents/*.docx, "
    "prompts/*.md, various tools/patch_*.py and diagnostic scripts) | "
    "N/A — repo hygiene, not a Tier 1-4 workflow item | Open, "
    "deliberately deferred | Surfaced during this session's closeout "
    "`git status` review. Confirmed to predate this session entirely -- "
    "none of it was touched, reviewed, or verified here. Two files from "
    "this session's own actual work (.gitignore, tools/test_main.py) "
    "were identified separately, committed on their own (8873dd2), and "
    "are not part of this pile. Pete's explicit call: a pile this size "
    "deserves its own dedicated pass, not a tail-end closeout decision -- "
    "left untouched on purpose so a future session knows it was seen and "
    "deliberately skipped, not missed | This session (2026-07-23) | "
    "Whenever Pete schedules a dedicated pass for it -- not a forced "
    "check-in, not something to chip away at incidentally during "
    "unrelated work |"
)

edit("tools/_mob.txt", OD07_ROW_TAIL, OD07_ROW_TAIL + "\n" + UNTRACKED_PILE_ROW)

# --- Section 16 (Session Log, descending -- prepend before newest head) ---

CORRECTION_LOG_HEAD = (
    "| **July 2026 — DiagnosticFlow.tsx reskin record corrected, planning-"
    "document gap logged** | Corrected an inaccurate prior claim: "
    "DiagnosticFlow.tsx's Stage 3 token content shipped inside commit "
    "290ce8d (whole-file staging swept it in alongside the counter fix), "
    "not held separate as previously reported -- Pete's explicit call: "
    "leave it shipped, not revert. The original 5-stage reskin plan and "
    "its Option C scope decision were never written to a durable file, "
    "confirmed via exhaustive search (prompts/*.md, tools/_mob.txt, "
    "MemPalace) -- zero matches. Stage 3 (token sweep) now confirmed "
    "complete across all three touched files; Stages 4/5's actual scope "
    "is genuinely unrecoverable, flagged for Pete to rescope from "
    "scratch and write down this time. Full detail in Section 14. "
    "MOB v4.61. |"
)

CLOSEOUT_LOG_LINE = (
    "| **July 2026 — Session closeout** | Diary written (AAAK, topic "
    "prv3-severity-wiring-live-verification). Mine run in background "
    "(known cosmetic UnicodeEncodeError precedent from Session 62 if it "
    "crashes at final print -- data filing completes before that point "
    "regardless). Two session-accountable uncommitted files identified "
    "and committed: .gitignore (.env* exclusion, directly relevant after "
    "this session's bypass-secret exposure incident) and "
    "tools/test_main.py (severity_follow_on_id coverage that never made "
    "it into a confirmed batch) -- commit 8873dd2, pushed. ~94-entry "
    "pre-existing untracked file pile confirmed unrelated to this "
    "session, deliberately left unaddressed per Pete's explicit call -- "
    "logged as its own Decision Register row (Section 13a) rather than "
    "silently skipped. Full detail in Section 14 and Section 13a. "
    "MOB v4.62. |"
)

edit("tools/_mob.txt", CORRECTION_LOG_HEAD, CLOSEOUT_LOG_LINE + "\n" + CORRECTION_LOG_HEAD)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.61 |",
    "| MOB version | v4.62 |",
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
    print(f"MOB CLOSEOUT PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
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
