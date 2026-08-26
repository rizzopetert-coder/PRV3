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
    """
    m = _get_memory()
    timestamp = datetime.now(timezone.utc).isoformat()
    result = m.add(
        entry,
        user_id=agent_name,
        metadata={"topic": topic, "type": "diary", "written_at": timestamp},
        infer=False,
    )
    return result


def read_recent(agent_name: str, last_n: int = 10) -> list[dict]:
    """
    Retrieve recent entries for session-start context. Mirrors the former
    mempalace_diary_read: returns the last_n entries for this agent,
    most-recent-first, sorted by the real created_at timestamp Mem0
    assigns at write time (not assumed to already be in order -- get_all()
    makes no ordering guarantee, sorted explicitly here).
    """
    m = _get_memory()
    # NOTE: a server-side nested filter (filters={"user_id": ...,
    # "AND": [{"metadata.type": "diary"}]}) was tried during the original
    # pilot and confirmed unsupported by this qdrant-backed mem0 version --
    # it matched zero results with no error raised. Plain user_id filtering
    # is confirmed working, so the type=diary distinction is applied
    # client-side only, below.
    result = m.get_all(filters={"user_id": agent_name})
    items = result.get("results", result) if isinstance(result, dict) else result
    diary_items = [i for i in items if (i.get("metadata") or {}).get("type") == "diary"]
    diary_items.sort(key=lambda i: i.get("created_at", ""), reverse=True)
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
        print(f"WROTE: {result}")
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
