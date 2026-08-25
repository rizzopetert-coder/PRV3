# MemPalace Root Cause — Read-Only HNSW/SQLite Diagnostic Pass (2026-08-25)

Read-only investigation only. Nothing pruned, rebuilt, deleted, or written. `mempalace repair prune`/`rebuild` not run, per standing constraint.

## What was checked

The live palace's `chroma.sqlite3` (`C:\Users\rizzo\.mempalace\palace\chroma.sqlite3`) is a real SQLite file, fully readable via a strict read-only URI connection (`file:...?mode=ro`), completely bypassing chromadb's Python API and the HNSW binary index — this is the same escape hatch already established in prior sessions (the document/metadata layer survives even though `count()`/`get()`/`query()` segfault on `mempalace_drawers`). Additionally, each collection's HNSW vector segment persists an `index_metadata.pickle` alongside the binary index files (`data_level0.bin`, `header.bin`, `length.bin`, `link_lists.bin`) — a plain Python pickle of primitives (dicts, ints, `None`), safely readable with `pickle.load()` without invoking hnswlib or chromadb at all.

`mempalace_drawers` collection ID: `baa24935-710b-49df-b472-9a5e04ad0c7b`. Its VECTOR (HNSW) segment: `952aae47-d623-4a4a-b82d-5bef901ed227` — this is the one that segfaults on `count()`/`get()`/`query()`. Its METADATA segment (`0c16b8c6-5064-4e13-bb84-451703d42e04`, SQLite-backed, no on-disk directory — normal chromadb layout) has 69,801 rows and is fully intact.

Used `mempalace_closets` (collection `eaae55b3-6407-4b9c-8803-034fcea98f84`, VECTOR segment `e90cec88-2e60-4ec4-87c7-d8e87a22f065`) as a healthy control throughout, since it does not crash.

## Findings, in the order they were checked — including a self-correction

1. **`embeddings` SQLite table, ruled out as the differentiator.** Initially found `mempalace_drawers`' VECTOR segment has 0 rows in the `embeddings` bookkeeping table despite a large `max_seq_id` (117965) and a 126MB `data_level0.bin` — looked like a desync. **Corrected immediately**: the healthy `mempalace_closets` VECTOR segment shows the *identical* pattern (0 `embeddings` rows, `max_seq_id` 107334). This is normal chromadb lifecycle behavior for VECTOR-type segments, not specific to the crashing collection. Not the mechanism.

2. **`index_metadata.pickle` — the real, quantified, differentiating finding.** Compared both collections' persisted hnswlib metadata directly:

   | | `mempalace_drawers` (crashing) | `mempalace_closets` (healthy) |
   |---|---|---|
   | `total_elements_added` | 75,609 | 3,100 |
   | `id_to_label` / `label_to_id` size | 69,604 | 2,978 |
   | Orphaned slots (added, no longer mapped) | **6,005 (7.9%)** | 122 (3.9%) |
   | `dimensionality` | `None` (both — not the mechanism, common to both) | `None` |

   `mempalace_drawers` has roughly double the proportional rate of elements that were added to the index at some point but are no longer reachable through the current `id_to_label`/`label_to_id` mapping — 6,005 orphaned slots, a real and substantial number, not noise.

## Refined hypothesis — more specific than the standing "duplicate-ID/HNSW bloat" theory

hnswlib's persisted index format is known to use soft deletes: removing an item clears its entry from `label_to_id`/`id_to_label` but does not necessarily reclaim its slot in `data_level0.bin` or clean up references to it in `link_lists.bin` (the graph's adjacency structure). A large accumulation of orphaned slots — as found here — is exactly the shape of input that could produce a dangling graph reference: a `link_lists.bin` edge that still points to a label no longer present in the id/label mapping. If chromadb's `count()`/`get()`/`query()` code path touches this inconsistency (e.g., iterating live labels while cross-referencing the graph), an unhandled dangling reference in the C++ layer is a plausible, concrete segfault mechanism — more specific than "duplicate IDs," and now quantified rather than theoretical. Not proven; this remains one level more precise, not a confirmed root cause.

## Next step, short of prune/rebuild — not attempted here, flagged as the natural continuation

hnswlib's `header.bin` (100 bytes, fixed layout: `offsetLevel0_`, `max_elements_`, `cur_element_count`, `size_data_per_element_`, `label_offset_`, `offsetData_`, `maxlevel_`, `enterpoint_node_`, `maxM_`, `maxM0_`, `M_`, `mult_`, `ef_construction_`) would give the single most direct confirmation: whether the graph's own internal `cur_element_count` matches `total_elements_added` (75,609) or something else entirely. **Deliberately not attempted here** — getting the exact byte offsets/types wrong (size_t width, struct packing) risks reporting fabricated numbers as fact, which is worse than not checking. If this is worth pursuing, the safest version is a `struct.unpack()` against a verified reference of hnswlib's exact save-format for the chromadb version in use (checkable via chromadb's own vendored hnswlib source, still entirely read-only — no need to run prune/rebuild or import chromadb itself).

## Not done

No `count()`/`get()`/`query()` call attempted (would crash, and wasn't needed — this entire pass used SQLite + pickle directly). No file written, moved, deleted, or modified. No `repair prune`/`rebuild`. `C:\mem0_trial_venv` and the migration process untouched throughout.
