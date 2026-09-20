"""
PRV3 session-continuity layer (Mem0-backed), replacing MemPalace's
mempalace_diary_write/mempalace_diary_read as of the MemPalace -> Mem0
retirement (tools/_mob.txt Section 13a, "MemPalace retirement" row).
Configuration is the exact one verified in
prompts/mempalace-alternative-trial-cognee-mem0.md and confirmed live
through two full cross-session verification cycles before this retirement
proceeded: local qdrant (embedded, on-disk), fastembed local embedder,
infer=False (no LLM call, no LLM API key genuinely needed at runtime -- a
placeholder value is set below purely to satisfy Memory()'s constructor-time
presence check).

Relocated into this repo (from C:\\mem0_trial_venv\\prv3_diary.py) so
protocol-governing code is version-controlled and travels with the project,
per the Gemini architecture review at
prompts/mempalace-mem0-retirement-gemini-request.md (independently verified,
prompts/mempalace-mem0-retirement-gemini-response-verification.md). The
Python interpreter and its mem0/qdrant-client/fastembed dependencies still
live in the separate venv at C:\\mem0_trial_venv (see
tools/prv3_diary_requirements.txt for the exact installed versions) --
invoke this script with that venv's python.exe, not the main repo's
environment, which does not have these packages installed:

    C:\\mem0_trial_venv\\Scripts\\python.exe tools\\prv3_diary.py read --agent claude-code --last-n 5
    C:\\mem0_trial_venv\\Scripts\\python.exe tools\\prv3_diary.py write --agent claude-code --topic "..." --entry "..."

Scope, deliberately unchanged from the original pilot: this is a diary-only
wrapper (write/read_recent). It does NOT attempt MemPalace's knowledge
graph, wings, cross-agent coordination, or mine-equivalent project-file
mining -- semantic search across a knowledge base (the former
mempalace_search, used at Startup Step 1 for three standing queries) has no
equivalent here and is a real, accepted capability reduction, not an
oversight. See CLAUDE.md's Startup Protocol Step 1 for how this is handled.

COLLISION MITIGATION (Gemini review item (d), independently verified sound):
STORE_PATH below is the dedicated, exclusive on-disk path for this diary's
production continuity data. Any future bulk migration, evaluation, or
batch-import script MUST target a different on-disk Qdrant path -- Qdrant's
local-mode backend takes a non-blocking exclusive lock on this directory
(confirmed directly against qdrant_client's own local-mode source: a
collision raises RuntimeError immediately, it does not wait or queue) and a
second process pointed at this same path while this diary is in use will
fail loudly, not corrupt data silently. The original migrate_mempalace.py
(C:\\mem0_trial_venv\\migrate_mempalace.py, its one-time job already
complete) shared this exact path historically -- do not reuse that pattern
for any new script going forward.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

# Placeholder ONLY to satisfy openai.OpenAI()'s constructor-time presence
# check inside Memory.__init__() -- infer=False on every write() call below
# means this LLM client is constructed but never actually invoked. Verified
# in the original trial: a real call would 401 loudly on this fake value;
# none did, across 20 writes in the original trial plus every real diary
# write/read since.
os.environ.setdefault("OPENAI_API_KEY", "sk-PLACEHOLDER-NOT-A-REAL-KEY-pilot-only")

from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.vector_stores.configs import VectorStoreConfig

STORE_PATH = "C:/mem0_trial_venv/qdrant_data"
COLLECTION = "prv3_trial"  # reserved for diary continuity -- see COLLISION MITIGATION above

# Root cause of the 2026-09-20 "writes sometimes unretrievable" investigation,
# found AFTER an initial (wrong) diagnosis: Memory.get_all()'s own default is
# `top_k: int = 20` -- read_recent() below called it with no top_k override at
# all, so it silently truncated to at most 20 candidates before this file's
# own last_n slicing/sorting ever ran. Confirmed directly: as of this fix,
# the claude-code agent already has 29 real entries -- 9 already past the
# silent cap -- and two entries this same session had been reported as
# "unretrievable" (quarterly-step-back-4-reconciled,
# diary-reliability-bug-tracked-numpy-removal-gated-future-task) were BOTH
# proven present, correctly timestamped, sitting just past position 20 in an
# unordered scroll, the entire time -- there was never any data loss or write
# non-persistence; the write path's own synchronous SQLite commit (persist(),
# qdrant_client/local/persistence.py) was already durable and reliable. This
# constant is generously sized for this diary's real, low-volume, per-agent
# usage pattern (dozens of entries per agent, not thousands) -- not set to
# the collection's own total point count (72,795+, inherited from the old
# MemPalace migration) since a get_all() scan of that size on every read
# would trade a truncation bug for a real performance cost this diary never
# needs to pay.
_GET_ALL_TOP_K = 5000

_memory_instance: Memory | None = None


def _get_memory() -> Memory:
    global _memory_instance
    if _memory_instance is None:
        config = MemoryConfig(
            vector_store=VectorStoreConfig(
                provider="qdrant",
                config={
                    "collection_name": COLLECTION,
                    "embedding_model_dims": 384,  # fastembed BAAI/bge-small-en-v1.5
                    "path": STORE_PATH,
                    "on_disk": True,
                },
            ),
            embedder=EmbedderConfig(
                provider="fastembed",
                config={"model": "BAAI/bge-small-en-v1.5"},
            ),
        )
        _memory_instance = Memory(config)
    return _memory_instance


def write_entry(agent_name: str, entry: str, topic: str = "general") -> dict:
    """
    Store a real continuity note. Mirrors the former mempalace_diary_write's
    shape: agent_name -> a distinct user_id namespace (mirrors MemPalace's
    per-agent diary wing), topic -> stored as metadata for later filtering/
    display, entry -> the raw note text, stored verbatim (infer=False, so
    no LLM rewrites or extracts "facts" from it -- what you write is
    byte-for-byte what gets embedded and stored).

    Read-after-write verification (2026-09-20, Bug B fix): `m.add()`
    returning successfully only means the Python call didn't raise: it was
    never checked against an independent read. Verifies via the SAME path
    read_recent() actually uses (`m.get_all(filters={"user_id": ...},
    top_k=_GET_ALL_TOP_K)`), not `Memory.get(id)` -- a direct point lookup
    was tried first and rejected, because it bypasses get_all()'s own
    top_k truncation entirely and so cannot detect the real failure mode
    (see `_GET_ALL_TOP_K`'s own comment above): a first version of this
    fix used `m.get(id)`, which reported every write as "verified" even
    for ids that read_recent() could not actually surface, since a direct
    lookup was never subject to the same cap. Any id not found in that
    same-path check is recorded in the returned dict's new `verified`/
    `unverified_ids` keys -- additive fields only, so any other caller of
    this function relying on the pre-existing `results` shape is
    unaffected.
    """
    m = _get_memory()
    timestamp = datetime.now(timezone.utc).isoformat()
    result = m.add(
        entry,
        user_id=agent_name,
        metadata={"topic": topic, "type": "diary", "written_at": timestamp},
        infer=False,
    )
    written_ids = [r["id"] for r in result.get("results", []) if r.get("id")]
    all_for_agent = m.get_all(filters={"user_id": agent_name}, top_k=_GET_ALL_TOP_K)
    all_items = all_for_agent.get("results", all_for_agent) if isinstance(all_for_agent, dict) else all_for_agent
    retrievable_ids = {i.get("id") for i in all_items}
    unverified_ids = [mid for mid in written_ids if mid not in retrievable_ids]
    result["verified"] = len(unverified_ids) == 0
    result["unverified_ids"] = unverified_ids
    m.vector_store.client.close()
    return result


def read_recent(agent_name: str, last_n: int = 10) -> list[dict]:
    """
    Retrieve recent entries for session-start context. Mirrors the former
    mempalace_diary_read: returns the last_n entries for this agent,
    most-recent-first, sorted by the real created_at timestamp Mem0
    assigns at write time (not assumed to already be in order -- get_all()
    makes no ordering guarantee, sorted explicitly here).

    Bug A fix (2026-09-20): `m.get_all()` below now passes an explicit
    `top_k=_GET_ALL_TOP_K`. Without it, `Memory.get_all()`'s own default
    (`top_k: int = 20`) silently truncated the candidate pool to at most
    20 matches BEFORE this function's own last_n slicing/sorting ever ran
    -- confirmed this was the true, complete root cause of "a write
    reports success but the entry doesn't show up on read" (not a write-
    persistence bug: the write path's own SQLite commit was already
    durable, and both entries this session that were reported missing
    were proven present, correctly timestamped, sitting just past
    position 20 in an unordered scroll, the entire time). See
    `_GET_ALL_TOP_K`'s own comment for why this value and not the
    collection's full point count.
    """
    m = _get_memory()
    # NOTE: a server-side nested filter (filters={"user_id": ...,
    # "AND": [{"metadata.type": "diary"}]}) was tried during the original
    # pilot and confirmed unsupported by this qdrant-backed mem0 version --
    # it matched zero results with no error raised. Plain user_id filtering
    # is confirmed working, so the type=diary distinction is applied
    # client-side only, below.
    result = m.get_all(filters={"user_id": agent_name}, top_k=_GET_ALL_TOP_K)
    items = result.get("results", result) if isinstance(result, dict) else result
    diary_items = [i for i in items if (i.get("metadata") or {}).get("type") == "diary"]
    diary_items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
    m.vector_store.client.close()
    return diary_items[:last_n]


def _cli():
    parser = argparse.ArgumentParser(description="PRV3 diary-equivalent continuity layer (Mem0-backed)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_write = sub.add_parser("write")
    p_write.add_argument("--agent", required=True)
    p_write.add_argument("--topic", default="general")
    p_write.add_argument("--entry", required=True)

    p_read = sub.add_parser("read")
    p_read.add_argument("--agent", required=True)
    p_read.add_argument("--last-n", type=int, default=10)

    args = parser.parse_args()

    if args.command == "write":
        result = write_entry(args.agent, args.entry, args.topic)
        if result.get("verified", True):
            print(f"WROTE: {result}")
        else:
            print(
                f"WARNING: write call succeeded but read-after-write "
                f"verification FAILED for id(s) {result.get('unverified_ids')} "
                f"-- this entry may not be retrievable. Full response: {result}"
            )
    elif args.command == "read":
        entries = read_recent(args.agent, args.last_n)
        print(f"=== {len(entries)} recent entries for agent '{args.agent}' ===")
        for e in entries:
            meta = e.get("metadata") or {}
            print(f"[{e.get('created_at')}] (topic: {meta.get('topic', '?')})")
            print(f"  {e.get('memory')}")
            print()


if __name__ == "__main__":
    sys.exit(_cli() or 0)
