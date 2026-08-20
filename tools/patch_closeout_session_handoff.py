"""
Add the session-handoff-file rule to the standing Closeout Protocol.

New rule: at every session close, after Section 16's closeout entry is
written, also write prompts/session-handoff-v[MOB version].md -- a direct
extract/reformatting of that same Section 16 entry, not independently
authored. Additive only (one file per close, never overwritten), tracked
in git (not gitignored). Section 16 remains authoritative if the two ever
disagree.

Changes:
1. CLAUDE.md -- new Step 3a (Session Handoff File) inserted between Step 3
   (Update MOB) and Step 3b (Commit MOB file); Step 3b's commit language
   extended to include the handoff file.
2. CLAUDE.md -- Key References table, MOB version v4.204 -> v4.205.
3. tools/_mob.txt -- header version stamp v4.204 -> v4.205 (line 9 only;
   the historical 2026-08-19 Section 16 entry's own "MOB v4.204" reference
   is untouched, it documents what version that session closed at).
4. tools/_mob.txt -- Section 14 Locked Decisions Log row for this rule.

Version bump: v4.204 -> v4.205 (standing-instruction change, not a status
note).

Usage:
    python patch_closeout_session_handoff.py --dry-run
    python patch_closeout_session_handoff.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

# -- 1. CLAUDE.md: new Step 3a + extended Step 3b -----------------------------

OLD_STEP3_BLOCK = (
    "Use `pathlib.Path('tools/_mob.txt').write_text(content, "
    "encoding='utf-8')` to overwrite the file.\n"
    "\n"
    "### Step 3b — Commit MOB file\n"
    "After writing `tools/_mob.txt`, include it in the session commit. "
    "This step fires every session without exception.\n"
)
NEW_STEP3_BLOCK = (
    "Use `pathlib.Path('tools/_mob.txt').write_text(content, "
    "encoding='utf-8')` to overwrite the file.\n"
    "\n"
    "### Step 3a — Session Handoff File\n"
    "After Section 16's closeout entry is written, write "
    "`prompts/session-handoff-v[MOB version].md` — a direct "
    "extract/reformatting of that same Section 16 entry, not "
    "independently authored. Cover: the files-to-attach list for the "
    "next session (Section 13b), the full shipped/open/parked status "
    "breakdown, and any time-anchored items. Additive only — one file "
    "per session close, never overwritten, named by the MOB version at "
    "close so it's unambiguous which project state it reflects. "
    "Tracked in git, not gitignored — these are durable records, not "
    "scratch output.\n"
    "\n"
    "This file must never contain information that contradicts or "
    "drifts from Section 16's own entry for that session — it is a "
    "derived, more portable copy for quick reference, not a second "
    "independent record. If the two ever need reconciling, Section 16 "
    "is authoritative.\n"
    "\n"
    "### Step 3b — Commit MOB file\n"
    "After writing `tools/_mob.txt` and "
    "`prompts/session-handoff-v[MOB version].md`, include both in the "
    "session commit. This step fires every session without exception.\n"
)

# -- 2. CLAUDE.md: Key References version ------------------------------------

CLAUDE_VERSION_OLD = "| MOB version | v4.204 |"
CLAUDE_VERSION_NEW = "| MOB version | v4.205 |"

# -- 3. tools/_mob.txt: header version stamp (line 9 only) -------------------

MOB_HEADER_OLD = "\\\\\\#\\\\\\# MOB v4.204"
MOB_HEADER_NEW = "\\\\\\#\\\\\\# MOB v4.205"

# -- 4. tools/_mob.txt: Section 14 new row, appended after the P-14 row ------

P14_SECTION14_ROW_TAIL = (
    "brand-voice shorthand. Locked wording (Pete-confirmed, Claude.ai): "
    "\"When brand voice risks obscuring meaning, plain language wins -- "
    "don't make the reader do the work of decoding what could just be "
    "said directly.\" Added to Section 2's Governing Principles list and "
    "this Section 14 row in the same pass, deliberately not repeating "
    "the P-13 cross-referencing gap noted in the row above (P-13 was "
    "added to Section 2 but missed Section 14 until caught later). | "
    "This session (Claude Code), 2026-08-19 | MOB v4.199 |\n"
)

SESSION_HANDOFF_SECTION14_ROW = (
    "| **August 2026 -- Session handoff file added to standing Closeout "
    "Protocol** | New standing rule: at every session close, after "
    "Section 16's closeout entry is written, also write "
    "`prompts/session-handoff-v[MOB version].md` -- a direct "
    "extract/reformatting of that same Section 16 entry (files-to-attach "
    "list, full shipped/open/parked status breakdown, time-anchored "
    "items), not independently authored. Additive only, one file per "
    "session close, never overwritten, named by the MOB version at "
    "close. Tracked in git, not gitignored -- a durable record, not "
    "scratch output. Must never contradict or drift from Section 16's "
    "own entry for that session; if the two disagree, Section 16 is "
    "authoritative. CLAUDE.md Closeout Protocol updated (new Step 3a, "
    "Step 3b's commit language extended to include the handoff file). "
    "First instance generated retroactively this session: "
    "`prompts/session-handoff-v4.204.md`, derived from the 2026-08-19 "
    "Section 16 close entry and its companion Section 13b update. | "
    "This session (Claude Code), 2026-08-20 | MOB v4.205 |\n"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    mob_text = MOB_PATH.read_text(encoding="utf-8")

    for label, old, new, text_name in [
        ("CLAUDE.md Step 3a/3b", OLD_STEP3_BLOCK, NEW_STEP3_BLOCK, "claude"),
        ("CLAUDE.md Key References version", CLAUDE_VERSION_OLD, CLAUDE_VERSION_NEW, "claude"),
    ]:
        count = claude_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        claude_text = claude_text.replace(old, new, 1)

    count = mob_text.count(MOB_HEADER_OLD)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(MOB_HEADER_OLD, MOB_HEADER_NEW, 1)

    count = mob_text.count(P14_SECTION14_ROW_TAIL)
    if count != 1:
        raise SystemExit(f"ABORT [Section 14 P-14 row tail]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(
        P14_SECTION14_ROW_TAIL,
        P14_SECTION14_ROW_TAIL + SESSION_HANDOFF_SECTION14_ROW,
        1,
    )

    if args.dry_run:
        for path, original, new_text in [
            (CLAUDE_MD_PATH, CLAUDE_MD_PATH.read_text(encoding="utf-8"), claude_text),
            (MOB_PATH, MOB_PATH.read_text(encoding="utf-8"), mob_text),
        ]:
            print(f"\n{'=' * 80}\nDIFF: {path}\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
            )
            print("".join(diff))
        print("\nDry run complete. No files written. Re-run with --write to apply.")
    else:
        CLAUDE_MD_PATH.write_text(claude_text, encoding="utf-8")
        MOB_PATH.write_text(mob_text, encoding="utf-8")
        print(f"WROTE: {CLAUDE_MD_PATH}")
        print(f"WROTE: {MOB_PATH}")


if __name__ == "__main__":
    main()
