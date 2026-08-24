# MemPalace Data Extraction Feasibility — Read-Only Investigation

Date: 2026-08-23/24
Scope: read-only investigation only. No write, delete, modify, or migrate operation was performed against the real MemPalace data at any point. A full filesystem copy was made first (per the task's own constraint, since chromadb has no true read-only mode), and every test below ran against the copy exclusively.

---

## Central finding — is it safe to read directly? **PARTIAL, and the split matters a lot.**

- **Chromadb's own official Python client API is NOT safely usable against this data.** A fresh script, importing `chromadb` directly with zero MemPalace code involved, **segfaults** on `mempalace_drawers` the moment any operation that touches the vector index is called (`count()`, `get()`, `query()` all go through the same code path). This reproduced on the untouched **copy**, using only chromadb's own client — confirming the crash is not specific to MemPalace's own code, but to chromadb (or this specific index data) itself. This is a real, meaningfully worse finding than "MemPalace's code has a bug": the underlying library itself cannot safely serve this data through its normal API.
- **But the underlying data is not lost.** Bypassing chromadb's Python API entirely and reading `chroma.sqlite3` directly via plain, read-only SQLite (the same file chromadb itself uses for document/metadata storage, architecturally separate from the binary HNSW vector-index files that are actually broken) works cleanly, with zero crashes, zero errors, and **complete, verbatim, exactly-as-written text for all 72,794 real entries**, confirmed against the full dataset, not a sample.

**In short: the vector search index is broken and cannot be read via chromadb's own API without crashing. The actual documents underneath it are intact, complete, and fully extractable via a different, safe path.** This changes the shape of the decision Pete is making — this is not "the data may be gone," it's "the data is fine, the index built on top of it is what's broken."

---

## Task 1 — Method and precise crash isolation

**Location, from MemPalace's own source, no CLI/MCP call made:** `os.path.expanduser("~/.mempalace/palace")` — `DEFAULT_PALACE_PATH` in the live install's `config.py`, confirmed against the actual resolved `~/.mempalace/config.json` (`"palace_path": "C:\\Users\\rizzo/.mempalace/palace"`). Found via direct source/file read only — no `mempalace status`, `mine`, `search`, or MCP tool call was made in Task 1.

**Background, noticed but not investigated further (out of this task's scope):** three prior backup/recovery directories already exist alongside the live `palace/` directory — `palace.backup-2026-08-05`, `palace_backup_pre_rebuild`, `palace_corrupt_bak` — real evidence that this install has already been through at least one corruption-and-rebuild cycle before this investigation began. Worth knowing as context; not opened or touched here.

**Copy made before any chromadb code ran, per the task's explicit constraint** (chromadb's `PersistentClient` has no read-only mode): the live `chroma.sqlite3` (1,793,785,856 bytes, size-verified identical after copy) and its 4 collection-segment UUID directories were copied to `C:\mempalace_readonly_copy`, along with `knowledge_graph.sqlite3`. The old `chroma.sqlite3.backup-pre-rebuild-20260805-235726` file was deliberately not copied (not part of the current live data). **Every test below ran only against this copy — the original `~/.mempalace/palace` directory was never opened by any script in this task.**

**Isolated, step-by-step results** (each step run as its own separate process, to pin down exactly where a crash occurs rather than losing that information to a single crashed process):

| Step | Operation | Result |
|---|---|---|
| 1 | `import chromadb` | OK — version 1.5.8, matches the live install exactly |
| 2 | `chromadb.PersistentClient(path=copy)` | OK — opens cleanly |
| 3 | `client.list_collections()` | OK — 2 collections found: `mempalace_drawers`, `mempalace_closets` |
| 4a | `client.get_collection('mempalace_drawers')` | OK |
| 4b | `.count()` on that collection object | **SEGFAULT (exit 139)** — reproduced twice, isolated |
| 5 | `get_collection('mempalace_closets')` then `.count()` | No crash — instead a clean, catchable `chromadb.errors.InternalError: ...Error loading hnsw index` |
| 6 | `.get(limit=3, ...)` on `mempalace_closets` (skipping count/query) | Same clean `InternalError` — get() also requires the broken HNSW segment reader in this chromadb version, not just count/query |

**Reading this precisely:** `get_collection()` alone never crashes for either collection — only an operation that actually needs the HNSW vector index (`count`, `get`, `query`) does. `mempalace_drawers`'s index failure manifests as a hard segfault (a native Rust-binding crash, unrecoverable, no Python exception). `mempalace_closets`'s index failure manifests as a clean, catchable Python exception with the same root message ("Error loading hnsw index") — a real difference in severity between the two collections' index corruption, not a difference in whether they're corrupted.

---

## Task 2 — What's actually there (via direct, read-only SQLite access, bypassing chromadb's API entirely)

Chromadb 1.5.8 stores documents and metadata in real SQL tables inside `chroma.sqlite3` — separate from the binary HNSW index files that are actually broken. Read with Python's own `sqlite3` module, opened explicitly read-only (`mode=ro`), zero chromadb or MemPalace code involved.

### Real counts and date ranges

| Collection | Real entries | Oldest | Newest |
|---|---|---|---|
| `mempalace_drawers` | **69,800** | 2026-08-06 04:02:30 | 2026-08-24 01:23:51 (today) |
| `mempalace_closets` | **2,994** | 2026-08-06 03:57:53 | 2026-08-22 02:22:04 |
| **Total** | **72,794** | | |

**Completeness verified against the full dataset, not a sample:** all 72,794 `embeddings` rows have a matching, non-empty full-text content row (0 orphaned/missing), and all 72,794 have a `wing` metadata field present (0 missing). The raw data layer is complete, not partially corrupted.

### Structure of a real entry, confirmed by direct sample

Two representative real samples (content shown, not redacted — both are non-sensitive: one is this session's own diary entry, the other is PRV3 taxonomy content already public in this repo):

**A diary entry** (`embedding_id: diary_wing_claude-code_20260823_212351106197_73ba3ea373df`):
```
text: "SESSION:2026-08-24|MOB.v4.227|Mem0_pilot_continuity_layer.BUILT+smoke_tested+
       real_write_verified|MemPalace.fresh_check.this_call"
metadata:
  agent: claude-code
  wing: wing_claude-code
  room: diary
  hall: hall_diary
  topic: prv3-session-continuity
  type: diary_entry
  date: 2026-08-23
  filed_at: 2026-08-23T21:23:51.106197
  chroma:document: <same text, duplicated as a metadata field -- standard chromadb pattern>
```

**A mined-file entry** (`embedding_id: drawer_prv3_scripts_...`):
```
text: <a real chunk of JSON content, verbatim, from tools/_salience_pilot_after.json>
metadata:
  wing: prv3
  room: scripts
  hall: technical  (varies per entry -- "consciousness" also seen in another sample)
  source_file: C:\Users\rizzo\PRV3\tools\_salience_pilot_after.json
  added_by: mempalace
  filed_at: 2026-08-22T15:00:52.871093
  chunk_index / source_mtime / normalize_version: present as keys, null in these samples
  entities: present occasionally (e.g. "Leadership") -- not on every row
```

### An important finding beyond what this task asked, too significant not to report

The single most recent `mempalace_drawers` row (`filed_at: 2026-08-23T21:23:51.106197`) is **exactly** this session's own `mempalace_diary_write` call made during the earlier Mem0 pilot task — the one that returned **"Connection closed"** to me as the caller. Its full content was pulled back from this raw SQL layer and matches the text I sent **byte-for-byte**, with completely correct metadata (`agent: claude-code`, `topic: prv3-session-continuity`, `wing`/`room`/`hall` all correctly populated).

**This means the write itself succeeded and was durably committed to the SQLite layer, even though the MCP call reported failure.** The failure that's been observed and reported all session as "MemPalace's core write function has zero confirmed successes" is real at the level of *the response reaching the caller* — but at least for `diary_write`, the underlying data capture is not necessarily failing at all. The most consistent explanation: the SQL-layer write commits first, and the crash (or connection loss) happens in a later step — most likely HNSW index construction/persistence, the exact layer confirmed broken in Task 1 above. This is inference from strong, direct timestamp/content correlation, not independently confirmed by tracing MemPalace's own code in this task — flagged clearly as such, not asserted as fully proven. It is a real, actionable finding worth Pete's attention regardless: recent "failed" diary writes may not be lost, just unconfirmed to the caller and unsearchable via chromadb's broken vector index.

### Task 2.3 — Is raw text stored verbatim and independently retrievable? **Yes, confirmed directly.**

Text lives in `embedding_fulltext_search_content.c0`, a real SQL column, completely independent of the embedding vector itself (stored separately in the broken binary HNSW files). This is the mechanism that made Task 1's SQL-layer bypass possible at all. **A text-level migration to Mem0 does not require reconstructing anything from the vector index** — the plaintext is already sitting in a plain, readable SQL table, one JOIN away from its metadata.

### Task 2.4 — Do MemPalace's structural concepts map cleanly to Mem0's flatter model?

**Mostly yes, with one clean gap and one real loss to be honest about:**

- **Wings, rooms, halls, topics, agent, timestamps** — all stored as simple key-value metadata pairs on each entry (confirmed directly above), not as a separate relational or graph structure. This maps very directly onto Mem0's own metadata-dict model — exactly the pattern this session's Mem0 pilot already used (`topic` as metadata, `agent_name` as `user_id`). No structural loss expected here; it's a relabeling exercise (`wing`→ a metadata field or `user_id` namespace, `room`/`hall` → metadata fields), not a re-architecture.
- **Knowledge graph relationships (`entities`, `triples` in `knowledge_graph.sqlite3`) — genuinely nothing to migrate.** Both tables exist with a real, defined schema (subject/predicate/object triples, typed entities) but are **completely empty, 0 rows in each**, confirmed by direct query. This isn't data that would be lost in a migration — it was never populated in the first place.
- **The one real structural loss, if migrated as flat metadata:** MemPalace's wing/room/hall hierarchy is a nested taxonomy (a wing contains rooms, a hall is a cross-cutting category); Mem0's model has no native concept of hierarchy or containment between metadata fields — it would flatten to sibling key-value pairs with no enforced parent-child relationship. Practically minor (nothing currently queries that hierarchy relationally, since the KG tables that would do so are empty), but real: the *hierarchy itself*, not just the *content*, would not survive a literal migration without deliberately re-encoding it.

---

## Disposition of the copy

The safety copy remains at `C:\mempalace_readonly_copy` (~1.75 GB: `chroma.sqlite3`, `knowledge_graph.sqlite3`, and the 4 collection-segment directories) — not deleted, in case Pete or a future task wants to inspect it further or use it as the basis for an actual extraction. It was never written to during this investigation. The original `~/.mempalace/palace` directory was never opened by any script in this task and remains exactly as it was.

## What this task does not answer

Per its own explicit scope: no migration was attempted, and no recommendation is made on whether to pursue one. This task answers "is the data intact and extractable" (yes, via the SQL bypass) and "can it be read without going through the crashing path" (yes, precisely characterized above) — the decision of what to do with that answer is Pete's.
