# MemPalace Migration + Time-Boxed Root-Cause Pass — TODO, NOT YET STARTED

Status as of 2026-08-24 closeout: **queued, not in-progress.** Pete approved both threads below in conversation this session, but the session closed on usage limits before either began. Nothing in this document has been executed. A future session should not assume any partial completion — this is a specification to execute from scratch, not a resumption of interrupted work.

**Honesty note on this document's origin:** Pete's closeout instruction described this task as "drafted, sent" earlier in the session. It was discussed and approved in conversation, but no separate, verbatim task message was actually dispatched before the session closed. This file is a reconstruction — synthesized from the real decision recorded in the Section 16 closeout entry (MOB v4.228) and the concrete findings in `prompts/mempalace-data-extraction-feasibility.md` — not a literal transcript. Treat the scope below as a solid, actionable starting spec, not as recovering an original document word-for-word.

---

## Context, established and verified (do not re-derive — read the source docs)

- `prompts/mempalace-data-extraction-feasibility.md`: MemPalace's underlying data is fully intact — 72,794 real entries (69,800 in `mempalace_drawers`, 2,994 in `mempalace_closets`), zero orphaned rows, zero missing text, verified against the full dataset via direct read-only SQLite against `chroma.sqlite3`'s document/metadata tables. The vector search index (HNSW, binary files) is broken and cannot be read via chromadb's own official API — confirmed via chromadb's client directly, zero MemPalace code involved: segfault on `mempalace_drawers`, a clean but blocking `InternalError` on `mempalace_closets`.
- `prompts/mempalace-alternative-trial-cognee-mem0.md` and `prompts/mem0-pilot-continuity-layer.md`: Mem0's vector-only configuration (`infer=False`, `fastembed` local embedder, `qdrant` backend) is real, working, and already has a live pilot wrapper at `C:\mem0_trial_venv\prv3_diary.py` (currently diary-only in scope).
- A read-only safety copy of the live palace data already exists at `C:\mempalace_readonly_copy` (chroma.sqlite3 + knowledge_graph.sqlite3 + collection segment directories), made during the feasibility check. **Confirm this copy is still current before relying on it** — the live install has continued accepting (partially-succeeding) writes since it was made; a fresh copy may be warranted rather than assuming staleness is fine.
- Three pre-existing backup/recovery directories already sit alongside the live palace directory (`palace.backup-2026-08-05`, `palace_backup_pre_rebuild`, `palace_corrupt_bak`) — this is at least the second known corruption event for this index, not a first-time occurrence. Worth reviewing before the root-cause pass, in case they contain useful prior-incident context.

---

## Task A — Migrate the 72,794 historical entries to Mem0

**Goal:** move MemPalace's real, verified-intact historical content into the Mem0 configuration already piloted this session, so the content survives independent of whether MemPalace's own index is ever fixed.

1. **Source extraction, read-only, from a copy, never the live install directly.** Reuse or refresh the `C:\mempalace_readonly_copy` safety copy. Extract all 72,794 entries via the same direct-SQLite method already proven working in the feasibility check (`embeddings` + `embedding_fulltext_search_content` + `embedding_metadata`, joined on `id`) — do not attempt to go through chromadb's own API for this (it's the confirmed-broken path).
2. **Design the target schema in Mem0 before writing anything.** Key open questions to resolve first, not default silently: does `wing` become Mem0's `user_id` namespace (mirroring the diary pilot's convention) or a metadata field? How do `room`/`hall`/`topic`/`filed_at`/`source_file`/`agent` map onto Mem0's metadata dict? The feasibility report flags that MemPalace's wing→room→hall nesting is a real hierarchy that a flat metadata migration will *not* preserve unless deliberately re-encoded (e.g., a compound key like `"wing/room"` as a single metadata field) — decide and document this choice explicitly rather than losing the hierarchy silently.
3. **Batch the writes, with real verification, not just a completion count.** At minimum: after each batch (suggest batches of a few thousand, not all 72,794 in one call), verify a real sample of that batch is retrievable via Mem0's own `get_all`/`search` with byte-for-byte content match, the same rigor already established in this session's own reliability tests. Log real counts as you go.
4. **Do not delete or modify anything in the source MemPalace install at any point in this task.** Migration is additive to Mem0, not destructive to MemPalace — MemPalace's data staying exactly where it is, untouched, is a hard constraint, not a suggestion, regardless of how the migration goes.
5. **Final verification:** total migrated count matches 72,794 (or a documented, explained discrepancy — do not silently under-migrate), spot-check a meaningful sample (not just the first/last few) for exact content and metadata correctness, and report the real outcome plainly — including any entries that failed to migrate and why, not just an aggregate success rate.

---

## Task B — Time-boxed root-cause pass on the recurring HNSW corruption

**Explicitly scoped as time-boxed, per Pete's own reasoning: not an open-ended investigation, so it doesn't displace higher-priority business work.**

**Hard limit: 45 minutes of active investigation.** When the clock runs out, stop and report whatever was found — a partial or negative result is an acceptable, expected outcome of a time-boxed pass, not a failure to push through. Do not silently extend past the limit because "just a bit more might crack it."

**Reasonable starting points, not a mandated sequence:**
1. Compare the current corruption against what's recoverable about the prior incident(s) — check whether `palace.backup-2026-08-05`, `palace_backup_pre_rebuild`, or `palace_corrupt_bak` (or any accompanying notes/logs from those events) suggest a pattern: same trigger, same collection, same failure signature, or something new this time.
2. Check chromadb's own GitHub issues (`chroma-core/chroma`) for HNSW index corruption reports matching this shape — segfault on read, not just write; a `hnsw:sync_threshold` setting was lowered in an earlier PRV3 session specifically to force more frequent real index persistence, which is exactly the kind of change that could interact with a latent corruption bug. Check whether that's a plausible contributing factor, not assumed.
3. If a specific corrupted file or index segment can be identified (the segment IDs are already known from the feasibility check: `952aae47-...` for `mempalace_drawers`'s vector segment, `e90cec88-...` for `mempalace_closets`'s), a byte-level or structural inspection of that segment's binary files, against the copy only, may be more productive than a purely code-level investigation.
4. If Windows-specific factors are suspected (the earlier reliability investigation found real Windows-specific issues — cp1252 console encoding, `msvcrt` deallocator quirks in an unrelated tool this session), check whether this chromadb version has known Windows-specific HNSW persistence issues.

**Report, regardless of outcome:** what was checked, what was ruled in/out, and — critically — whether the 45 minutes found a fixable root cause, a plausible-but-unconfirmed one, or nothing conclusive. Do not overstate confidence to make the time-boxed pass feel more resolved than it was.

---

## Constraints (apply to both tasks)

- No write, delete, or modify operation against the live `~/.mempalace/palace` directory or any of its files, under any circumstance, in either task.
- Migration (Task A) writes only to Mem0's own storage (`C:\mem0_trial_venv` or a fresh equivalent, the executing session's call, stated explicitly). Root-cause work (Task B) reads only, against copies.
- Neither task is a decision to adopt Mem0 as a MemPalace replacement or to abandon the root-cause fix. Both remain exactly what they were scoped as: a data-safety migration and a time-boxed diagnostic pass. No MOB entry should claim MemPalace is replaced as a result of either task completing.
- Real verification throughout, not assumed success — the standard every check in this session's MemPalace arc was held to.

## When this is picked up

Whoever executes this — reconstruct context from `prompts/mempalace-data-extraction-feasibility.md` and `prompts/mempalace-alternative-trial-cognee-mem0.md` first if not already fresh in context. This file states the scope; those two contain the evidence the scope is built on.
