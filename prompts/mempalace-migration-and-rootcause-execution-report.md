# MemPalace Migration + Root-Cause Pass — Execution Report

Date: 2026-08-24. Executing `prompts/mempalace-migration-and-rootcause-TODO.md`. Task A run first per instruction; Task B follows. Task A is **not complete** — paused at a real, unanticipated scope finding requiring Pete's decision, documented below rather than resolved unilaterally. Task B ran its full 45-minute time-box and is complete, with a plausible-but-unconfirmed result, reported honestly as such.

---

## Task A — Migration: partial, correctness-verified, paused on a real timing finding

### Copy freshness — refreshed, not assumed

Per the spec's explicit warning, the existing `C:\mempalace_readonly_copy` was checked against the live file before use: same byte size (1,793,785,856) but a 13-minute-newer mtime. Refreshed rather than trusted on the size match alone. **The refresh caught a real change:** total source rows went from 72,794 (at the feasibility check) to **72,795** — one more entry landed in `mempalace_drawers` between the feasibility check and this task, timestamped `2026-08-24 01:46:29`, consistent with a diary write from the prior session's closeout. **The real migration target is 72,795, not 72,794** — noted as a legitimate source-count change, not a migration discrepancy.

### Mapping design, decided and documented before any write (per the spec's explicit requirement)

The real metadata was characterized first, not assumed from the two samples in the feasibility report. Full coverage check across all 72,795 rows found:

- **4 distinct wings**, not just PRV3 content: `prv3` (58,199), `claude` (8,361), `prv2` (6,161 — a different, earlier project), `wing_claude-code` (74, this session's diary entries). This MemPalace install holds cross-project data, not PRV3-only — the migration covers all of it, matching the TODO's own framing of a general data-safety measure, not a PRV3-scoped one.
- **19 distinct room values**, **9 distinct hall values**, and metadata field coverage that varies by row (only `wing`, `room`, `chroma:document` are on all 72,795 rows; `filed_at`/`source_file` ~93%; `hall` ~84%; `entities` ~35%; `type`/`topic`/`date`/`agent` only on the 74 diary rows). Fields beyond what the TODO anticipated were found and included: `chunk_index`, `added_by`, `normalize_version`, `source_mtime`, `source`, `ingest_mode`, `extract_mode`, `drawer_count`.

**Decisions made:**
- `user_id` = the real `wing` value verbatim — preserves MemPalace's own top-level namespace as Mem0's natural partition boundary, matching the existing pilot's own convention.
- Every metadata key actually present on a row is carried over verbatim under its original name — not forced to one fixed schema, since coverage is genuinely uneven.
- New synthesized field `mempalace_path` = `f"{wing}/{room}"`, explicitly re-encoding the wing→room containment. `hall` is deliberately **not** folded into this path: confirmed via the data itself that hall is a cross-cutting tag, not a third hierarchy level (the same room appears under multiple halls).
- New field `mempalace_embedding_id` preserves the original ID verbatim as a stable cross-reference/de-dup key.
- Content source: `embedding_fulltext_search_content.c0` directly (the canonical text), not the redundant `chroma:document` metadata duplicate.
- Target: a new, separate Mem0 collection (`mempalace_migration`) in the already-working `C:\mem0_trial_venv` install, kept apart from the pilot's own diary/test collection (`prv3_trial`) so bulk migrated content doesn't mix with already-verified pilot data.

### Real work done and verified

- **1,050 real entries migrated, 0 failures** (a 50-row correctness test, then a 1,000-row throughput test, both against real source rows, both with metadata and content confirmed correctly written).
- Extraction confirmed working via the same direct-SQLite method already proven in the feasibility check — `embeddings` + `embedding_fulltext_search_content` + `embedding_metadata`, joined on `id`, never through chromadb's own (confirmed-broken) API.

### The real, unanticipated finding: throughput

Measured **twice independently** (50 rows, then 1,000 rows): a sustained rate of **~2 entries/second**. Profiled to find the cause — 87% of per-call time (0.449s of 0.514s average) is genuine CPU-bound ONNX model inference (`onnxruntime...run`), not a bug or an avoidable overhead. Two legitimate optimizations were tried and both failed to meaningfully help:
- **True batching** (`model.embed(list_of_20_texts)` in one call vs. one-by-one): no improvement — 9.68s either way for 20 items, suggesting this ONNX session doesn't benefit from batching on this hardware.
- **Truncating embedding input to 2,000 characters** (content still stored in full — only the text handed to the embedder would be shortened): no meaningful speedup (9.67s vs. 9.68s for 20 items), and cosine similarity between full and truncated embeddings averaged 0.997 anyway, confirming the model's own context window already caps what it actually uses.

**At the confirmed rate, the full 72,795-entry migration requires approximately 9.6 hours of continuous compute** — far beyond what the spec's "batches of a few thousand" language implied, and beyond what's reasonable to run silently within one session without checking first.

### Why this wasn't decided unilaterally

The spec's own Task-ordering instruction ("if you think B should come first, flag that reasoning to Pete before switching order rather than deciding unilaterally") sets the standard this finding is held to: a 9.6-hour runtime is a material, unanticipated scope change from what was implicitly planned for, and picking a workaround myself — truncating scope to an arbitrary partial migration and calling it done, or silently launching a 9+ hour unattended background process — would substitute my own judgment for a real decision that's genuinely Pete's to make. Options, for Pete's decision:

1. **Run the full migration as a genuine long-running background process** (~9.6 hours), checkable via `C:\mem0_trial_venv\migration_progress.log`, not blocking this or future sessions but running independently on this machine.
2. **Migrate a defined, representative subset now** (e.g., all of `wing_claude-code` plus a capped sample of each other wing) as a bounded "phase 1," with the remainder explicitly queued for later.
3. **Hold the full migration for a dedicated future session** with an explicit multi-hour time allocation, rather than run it opportunistically in the background of other work.

The migration script (`C:\mem0_trial_venv\migrate_mempalace.py`) is built, correctness-verified on 1,050 real entries, and ready to resume from any offset — none of the above options require rebuilding anything, only a decision on how to spend the ~9.6 hours of compute.

---

## Task B — Time-boxed root-cause pass (45-minute hard cap, fully used, ~40 minutes active investigation)

### What was checked

**1. The three backup/recovery directories.** A real correction to the earlier feasibility report's framing: `palace_backup_pre_rebuild` and `palace_corrupt_bak` are **byte-identical** (same files, same UUIDs, same timestamps) — one July 1 snapshot under two directory names, not two separate incidents. Combined with the August 5 backup, this is **2 distinct historical snapshots, not 3 independent corruption events** as the earlier framing implied. The July 1 snapshot includes a `chroma.sqlite3.bak_opt1` file, suggesting a database optimization/compaction was attempted around that time — a real, if inconclusive, data point.

**2. A real write-ahead log, not previously checked:** `~/.mempalace/wal/write_log.jsonl`, 59 entries spanning 2026-04-16 through 2026-08-23. Every single entry shows `"result": null`. **This initially looked like strong independent evidence of a months-long silent-failure pattern** — but direct source inspection resolved it cleanly: `_wal_log()`'s `result` parameter (in `mcp_server.py`) is **never passed at any of its 6 call sites** in the entire file (`add_drawer`, `delete_drawer`, `update_drawer`, `kg_add`, `kg_invalidate`, `diary_write`). It's a pre-write intent log only, by current implementation — `result: null` is the permanent, universal state regardless of whether the underlying operation actually succeeds. **This is not evidence of a 4-month failure streak; it's dead/unfinished logging code.** Flagged as a real, separate, minor code-quality gap (the parameter exists but was never wired up), explicitly not conflated with the actual crash investigation.

**3. `hnsw:sync_threshold`, specifically checked per the spec's own suggestion.** Not found anywhere in the currently-installed MemPalace package's source, and the collections' own stored `config_json_str` in `chroma.sqlite3` is empty (`{}`) for both `mempalace_drawers` and `mempalace_closets`. No evidence this setting is currently in effect at all — **the specific `sync_threshold` theory does not hold up** against direct inspection, at least not as a currently-active configuration.

**4. A real, substantive finding: MemPalace ships its own `repair.py` module,** with a docstring stating plainly: *"When ChromaDB's HNSW index accumulates duplicate entries (from repeated `add()` calls with the same ID), `link_lists.bin` can grow unbounded — terabytes on large palaces — eventually causing segfaults."* This is the tool's own developer describing, in advance, a failure mode matching exactly what's been observed this session — meaning this is very likely a **known, previously-encountered issue**, not a novel one. `repair.py` provides `scan`/`prune`/`rebuild` operations, with `rebuild` explicitly designed to extract from `chroma.sqlite3` ("the source of truth") and recreate the HNSW index fresh — architecturally identical in spirit to the migration this task is already doing.

**5. Direct evidence check against the duplicate-ID theory.** Checked whether the two 67-million-character monster entries found in the feasibility check share an `embedding_id` (which would directly prove a duplicate-add happened): they do not — distinct IDs (`drawer_claude_technical_...`, `drawer_prv2_technical_...`). A full-table scan for any duplicate `embedding_id` values across all 72,795 rows found **zero** duplicates at the current SQL layer. This doesn't rule out the `repair.py`-documented cause — the SQL layer could have deduplicated/overwritten past duplicate-add events while the HNSW binary layer retained orphaned bloat from before that overwrite, which is exactly the SQL/HNSW divergence `repair.py`'s design implies — but it means the theory isn't directly confirmed by present-state evidence either.

**6. Checked the actual `link_lists.bin` file sizes for both segments, looking for the "unbounded growth" pattern `repair.py` describes:** `mempalace_drawers` (69,801 entries): 646,788 bytes ≈ 9.27 bytes/entry. `mempalace_closets` (2,994 entries): 26,748 bytes ≈ 8.94 bytes/entry. **These are proportional to entry count, not showing the disproportionate bloat** that would make the duplicate-ID theory a confirmed, direct match for what's currently on disk — a real, honest negative data point against treating this as fully confirmed.

**7. Mechanistic link between the read-crash (Task 1 of the feasibility check) and write-crashes (mine/diary_write), established directly from source:** `diary_write`'s actual write call is a single `col.add(...)` — chromadb's own client API. Since HNSW is a graph-based index where inserting a new vector requires traversing the *existing* graph structure to find attachment points, an `add()` call plausibly needs to touch the same corrupted index region that `count()`/`get()`/`query()` already crash on — a coherent explanation for why both read and write operations against `mempalace_drawers` fail, without needing two separate root causes.

### Honest conclusion: plausible-but-unconfirmed, not proven

**What was ruled out:** the `sync_threshold` theory (not present in current config). The "4-month silent failure" reading of the write-ahead log (a logging artifact, not real evidence).

**What remains plausible, grounded in the tool's own developer documentation, but not directly confirmed by current file-size evidence:** MemPalace's own `repair.py` describes exactly this failure class (duplicate-ID `add()` calls bloating `link_lists.bin` until segfault) as a known, anticipated problem with existing purpose-built tooling to fix it. The mechanistic link between read-crashes and write-crashes (both requiring HNSW graph traversal) is sound and directly grounded in source, not speculation. But the specific file-size check for "unbounded" bloat came back proportional, not anomalous — so this is not a slam-dunk confirmed root cause, it's the single most concrete, evidence-grounded candidate found in the time available, with one piece of counter-evidence (file size) not yet reconciled.

**Not overstating this:** 45 minutes was enough to find a strong, source-grounded hypothesis and the tool's own author's prior anticipation of this exact failure class — it was not enough to definitively prove or disprove it against this specific install's actual corrupted state. `mempalace repair scan` (read-only, per its own docstring) against the copy would be the natural next diagnostic step, not attempted here as it falls outside this pass's 45-minute cap.

---

## What happens next — Pete's call

**Task A:** the migration script is built, correctness-verified, and paused pending a decision on how to spend the ~9.6 hours of compute the full run requires (see the three options above).

**Task B:** the `repair.py`-documented duplicate-ID/HNSW-bloat theory is the strongest lead found, but not confirmed. Running `mempalace repair scan` (read-only, against the copy, never the live install) would be the logical next step if Pete wants to pursue this further — not run in this pass, since it wasn't reached within the 45-minute cap and running an unfamiliar tool's `scan` operation for the first time deserved its own considered pass rather than being squeezed in at the very end of a time-boxed investigation.

Neither task's outcome changes anything about MemPalace's status: no data was deleted, modified, or migrated destructively; the live `~/.mempalace/palace` directory was never opened by either task. This remains a pilot and a diagnostic pass, not a decision to adopt Mem0 or abandon the root-cause fix.
