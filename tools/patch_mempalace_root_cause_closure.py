"""
PRV3 MOB Update -- MemPalace silent non-persistence root-cause + fix closeout

Updates tools/_mob.txt:
  - Section 13a (Decision Register): "MemPalace mine -- silent non-persistence"
    row -- Open (root cause unknown, confirmed 3x) -> Closed (root cause found
    and fixed, empirically verified via direct SQLite inspection and
    mempalace_search, not citation or exit-status).
  - Section 16 (Session Log): new entry summarizing the investigation and fix.
  - Version bump v4.112 -> v4.113 (Decision Register item closed, real
    mechanism now on permanent record -- material workstream status change).

Updates CLAUDE.md:
  - MOB version cross-reference v4.112 -> v4.113.

Usage:
  python tools/patch_mempalace_root_cause_closure.py --dry-run
  python tools/patch_mempalace_root_cause_closure.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================================
# tools/_mob.txt
# ============================================================================

OLD_ROW = "| MemPalace mine -- silent non-persistence, confirmed recurring | 3 | Open -- confirmed THREE times now, root cause unknown |"

NEW_ROW_HEAD = "| MemPalace mine -- silent non-persistence -- RESOLVED, root cause identified and fixed | 3 | Closed -- root cause found, fixed, and empirically verified this session |"

NEW_ROW_BODY = (
    "Confirmed non-persistent three separate times before this session (Session 70, "
    "August 2, and August 5 2026) with root cause genuinely unknown at each prior "
    "occurrence. This session traced it to ground truth via direct SQLite inspection "
    "of chroma.sqlite3 (not mine's exit status, not mempalace_status alone), not any "
    "external citation: mempalace's installed chromadb 1.5.8 backend batches HNSW "
    "vector-index persistence behind a per-process, in-memory counter "
    "(_num_log_records_since_last_persist in chromadb's local_persistent_hnsw.py) that "
    "only calls _persist() once it crosses hnsw:sync_threshold (chromadb's default: "
    "1000). That counter resets to zero every time a fresh PersistentClient is "
    "constructed -- since mempalace mine runs as a short-lived CLI process per "
    "invocation and no single session's write volume approaches 1000, the threshold "
    "could structurally never be crossed, so the HNSW vector index backlog could only "
    "grow, never compact, regardless of how many times mine ran. Confirmed "
    "empirically: embeddings_queue held 813 unprocessed rows spanning 2026-07-23 "
    "through this session's own diary write, with one segment's max_seq_id frozen at "
    "its exact oldest queued row (zero progress since July 23). Separately confirmed "
    "that no data was ever actually lost -- the METADATA segment (a separate, "
    "non-threshold-gated SQLite table) already held full content for every \"stuck\" "
    "item, including today's diary entry, which is why mempalace_diary_read (a "
    "metadata-path lookup) worked all session while mempalace_search (which depends "
    "on the HNSW vector index) came up empty. Also confirmed, independently: "
    "write_log.jsonl (previously cited in this same Decision Register as "
    "verification evidence for suspecting non-persistence) only ever logs "
    "diary_write MCP calls -- it never logged mine/upsert operations at all, so no "
    "prior session's \"verified via write_log.jsonl\" check could ever have caught "
    "this either way, regardless of what it showed. METHOD NOTE, logged honestly: "
    "initial diagnosis leaned on two specific external citations (GitHub issues "
    "#1006/#1202 and a discussion titled \"the road that nearly made me quit\") "
    "surfaced via WebFetch/WebSearch -- those results were NOT trusted as "
    "verification, since their phrasing mirrored the query's own wording almost "
    "verbatim, a known fabrication signature already caught multiple times with "
    "Gemini citations in this project (memory 18). The actual root cause and fix "
    "were established entirely from first-hand evidence (direct SQLite queries "
    "against the live database, the installed mempalace/chromadb source code) "
    "independent of whether those citations are real. FIX APPLIED: "
    "collection.modify(metadata=...) was tried first as the lowest-risk option and "
    "confirmed NOT to work -- it only touches a cosmetic .metadata property that "
    "nothing in mempalace's own code reads; the real, load-bearing HNSW config "
    "lives in collections.schema_str, which is only writable at collection-creation "
    "time. Adapted mempalace's own existing repair.py::rebuild_index() (previously "
    "scoped to mempalace_drawers only, built for an unrelated HNSW-bloat problem) to "
    "cover both mempalace_drawers and mempalace_closets: extract all records via "
    "collection.get() (safe against the stall, reads the unaffected metadata "
    "segment), verify extracted count against a live pre-established baseline (863 "
    "closets / 24136 drawers, both matched exactly, zero loss), back up "
    "chroma.sqlite3 to a freshly dated file before deleting anything, delete and "
    "recreate each collection with hnsw:sync_threshold set explicitly to 10 at "
    "creation time (verified via direct schema_str read, not .metadata), and "
    "re-upsert everything. Post-rebuild counts matched pre-rebuild extraction "
    "exactly for both collections (863/863, 24136/24136). embeddings_queue backlog "
    "dropped from 813 to 2 (both dated after the rebuild itself, not old stuck "
    "content). Verified via mempalace_search, not just row counts, that all three "
    "previously \"lost\" sessions -- August 5 (today's own diary write), August 2, "
    "and July 23 -- are now directly retrievable, closing the loop empirically "
    "rather than assuming the fix worked. Two backups retained, not yet cleaned up: "
    "~/.mempalace/palace.backup-2026-08-05 (full palace, pre-investigation) and "
    "~/.mempalace/palace/chroma.sqlite3.backup-pre-rebuild-20260805-235726 "
    "(immediately pre-rebuild). Per Pete's original framing, this was a "
    "diagnostic/fix attempt, not a MemPalace-replacement decision -- the "
    "mcp-memory-service/Cognee/mem0/Graphiti alternatives comparison noted in the "
    "prior entry stays logged for reference but does not need to be acted on now "
    "that the actual mechanism is fixed at the source."
)

NEW_ROW_TAIL = (
    " | This session (Claude Code) | Closed -- no further check-in. If "
    "non-persistence recurs, treat it as a new incident -- the specific mechanism "
    "identified here (per-process sync_threshold counter reset) is fixed at the "
    "source (sync_threshold lowered to 10, verified in schema_str) for both "
    "collections, not merely worked around |"
)

edit(
    "tools/_mob.txt",
    OLD_ROW,
    NEW_ROW_HEAD + " " + NEW_ROW_BODY + NEW_ROW_TAIL,
)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.112",
    "\\\\\\#\\\\\\# MOB v4.113",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — MemPalace silent non-persistence root-caused and fixed, "
    "closes a three-times-confirmed Decision Register item | Full detail in Section "
    "13a's MemPalace mine row. Root cause: chromadb 1.5.8's HNSW vector-index "
    "persistence is gated by a per-process in-memory counter against "
    "hnsw:sync_threshold (default 1000) that resets on every new PersistentClient "
    "-- since mempalace mine runs as a short-lived CLI process per invocation, "
    "typical per-session write volume never crossed that threshold, so the "
    "vector-index backlog could only grow, never compact. Confirmed via direct "
    "SQLite inspection of chroma.sqlite3, not citation or exit-status: 813 rows "
    "stuck in embeddings_queue since 2026-07-23, one segment's compactor frozen at "
    "zero progress. Content itself was never lost -- the separate, "
    "non-threshold-gated METADATA segment held everything throughout, which is why "
    "mempalace_diary_read worked all session while mempalace_search came up empty. "
    "Fix: extended mempalace's existing repair.py::rebuild_index() (previously "
    "drawers-only) to cover both mempalace_drawers and mempalace_closets -- extract "
    "via collection.get(), verify count against a live baseline, back up "
    "chroma.sqlite3, delete and recreate with hnsw:sync_threshold=10 set explicitly "
    "at creation time (the only code path confirmed to actually write to "
    "collections.schema_str -- collection.modify() was tried first and confirmed "
    "NOT to touch it), re-upsert. Zero data loss verified both ways: exact count "
    "match pre/post (863/863 closets, 24136/24136 drawers) and direct "
    "mempalace_search confirmation that all three previously \"lost\" sessions (Aug "
    "5, Aug 2, July 23) are now retrievable. Also surfaced and logged: "
    "write_log.jsonl never logged mine operations at all, only diary_write -- so no "
    "prior session's \"verified via write_log.jsonl\" check could have caught this "
    "regardless. Two specific external citations surfaced during initial diagnosis "
    "(GitHub issues #1006/#1202, a discussion titled \"the road that nearly made me "
    "quit\") were explicitly NOT trusted as verification -- their phrasing mirrored "
    "the query's own wording, a known fabrication signature -- the real fix rests "
    "entirely on first-hand evidence from the live database and installed source. "
    "MOB version bumped v4.112 → v4.113 per standing protocol -- closes a Decision "
    "Register item open and reconfirmed three separate times, with the real "
    "mechanism now on permanent record. | This session (Claude Code) | MOB v4.113 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.111 |",
    "| This session (Claude Code) | MOB v4.111 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.112 |",
    "| MOB version | v4.113 |",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    by_file: dict[str, list[tuple[str, str]]] = {}
    for path, old, new in EDITS:
        by_file.setdefault(path, []).append((old, new))

    for rel_path, pairs in by_file.items():
        full_path = REPO_ROOT / rel_path
        content = full_path.read_text(encoding="utf-8")
        for old, new in pairs:
            count = content.count(old)
            if count != 1:
                print(f"ABORT: {rel_path}: expected exactly 1 match for anchor, found {count}")
                print(f"  anchor (first 120 chars): {old[:120]!r}")
                sys.exit(1)
            content = content.replace(old, new, 1)

        if args.dry_run:
            print(f"=== {rel_path}: {len(pairs)} edit(s) would apply cleanly ===")
        else:
            full_path.write_text(content, encoding="utf-8")
            print(f"=== {rel_path}: {len(pairs)} edit(s) written ===")

    if args.dry_run:
        print("\nDry run complete. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
