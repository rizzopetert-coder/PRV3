# Mem0 Pilot — Diary-Equivalent Continuity Layer

Date: 2026-08-23/24
Status: **PILOT, not adoption.** This document reports a real, working parallel continuity layer built and exercised this session. It is not a decision to replace MemPalace, is not reflected as a locked decision anywhere in `tools/_mob.txt`, and nothing in the existing MemPalace installation or its stored data was touched, disabled, or migrated. The adoption question stays explicitly open for Pete, after this pilot and at least one more real session's use.

---

## Task 1 — Wrapper location and design

**Reused the exact configuration already verified in the prior trial** (`prompts/mempalace-alternative-trial-cognee-mem0.md`) rather than building a fresh one: the same install at `C:\mem0_trial_venv` (mem0ai 2.0.18, qdrant-client, fastembed), the same on-disk qdrant path (`C:\mem0_trial_venv\qdrant_data`), and the same `infer=False` configuration that passed 20/20 real writes in the original reliability test. Reusing it rather than reinstalling means this pilot's real diary content is running through code and infrastructure that was already stress-tested, not a fresh, unverified setup.

**Wrapper file:** `C:\mem0_trial_venv\prv3_diary.py` — a single, self-contained, ~150-line Python module. No new dependencies beyond what the prior trial already installed and confirmed working (`mem0ai`, `qdrant-client`, `fastembed`).

**Two functions, mirroring MemPalace's diary tool shape directly:**
- `write_entry(agent_name, entry, topic="general")` — mirrors `mempalace_diary_write`. `agent_name` maps to Mem0's `user_id`, giving each agent its own namespace (the same isolation role MemPalace's per-agent diary wing plays). `topic` and a real `written_at` timestamp are stored as metadata. `infer=False` on every call means the entry is stored verbatim — no LLM rewriting, no "fact extraction," what you write is byte-for-byte what gets embedded and retrieved.
- `read_recent(agent_name, last_n=10)` — mirrors `mempalace_diary_read`. Retrieves all entries for that agent, filters to `metadata.type == "diary"` client-side, sorts by Mem0's real `created_at` timestamp (descending — most recent first), returns the top `last_n`.

**A CLI wrapper** (`python prv3_diary.py write --agent ... --topic ... --entry ...` / `python prv3_diary.py read --agent ... --last-n ...`) makes both functions callable without writing a new script each time, without building a full MCP server — deliberately not attempting MemPalace's knowledge graph, wings, cross-agent coordination, or mining tools. This pilot is scoped to exactly one function: session-continuity notes, the one that's currently broken and load-bearing.

### A real bug found and fixed before trusting it with real content

Before writing anything real, the wrapper was smoke-tested with throwaway content under a separate agent namespace (`smoke-test-agent`). The first version's `read_recent()` used a server-side nested filter (`filters={"user_id": ..., "AND": [{"metadata.type": "diary"}]}`) that this qdrant-backed Mem0 version does not support — it silently matched **zero results**, with no error raised. Confirmed via direct debugging that a plain `user_id` filter retrieves the entry correctly, with metadata fully intact (`topic`, `type`, `written_at` all present and correct). Fixed by dropping the fragile server-side nested filter and relying on the client-side `metadata.type == "diary"` check that was already present as a fallback. Re-verified working before the real write in Task 2.

This is worth naming plainly: a real, silent-failure-shaped bug was caught in this wrapper's own first version, in the exact style the prior trial's GitHub-issue research flagged as a known Mem0 risk class (silent write/read failures with a success-looking response). It was caught here because the smoke-test step existed and its result was actually checked, not assumed — the same discipline the wrapper is meant to bring to session continuity in the first place.

---

## Task 2 — Real use, this session's actual closeout

**Write:** one real entry, agent `claude-code`, topic `prv3-session-continuity`, summarizing this session's actual state (MOB version, six workstreams closed, MemPalace's confirmed-still-broken status, the comprehensive assessment's corrections, the Quarterly Step-Back redefinition, the Engagement Agreement finding, and next-session priorities) — genuine content, not a test string, since Pete may read this back for real next session.

**Read-back verification, not just a non-error check:**
- Retrieved 1 entry for agent `claude-code`.
- Topic matched exactly (`prv3-session-continuity`).
- Full entry length: 2,598 characters, retrieved intact.
- Content matched byte-for-byte against the original text on multiple independent spot-checks (the opening sentence, a specific mid-entry phrase about the transaction-path gap, the wrapper's own file-path self-reference near the end).

**Result: PASS.** Write and read-back both succeeded, content verified exact, using real session content rather than synthetic test strings.

**Fresh, same-day MemPalace comparison (Task 2.3), not assumed from earlier in this session:** both `mempalace_status` and `mempalace_diary_write` were called again, right now, independently of every earlier check today. **Both returned "Connection closed"** — identical to every prior check this session. No change, no improvement, no regression. This is a genuine, same-moment data point, not a stale one carried forward.

---

## What this pilot does NOT cover

Stated plainly, so this isn't mistaken for a broader capability than it is:

- **No knowledge graph.** MemPalace's `mempalace_kg_add`/`kg_query`/`kg_timeline`/`kg_stats` have no equivalent here. This wrapper stores and retrieves flat text entries with light metadata, nothing more.
- **No wings, rooms, or cross-agent coordination beyond simple namespacing.** `agent_name` → `user_id` gives basic per-agent isolation, not MemPalace's fuller wing/room structure, tunnels, or multi-agent discovery tools (`mempalace_list_wings`, `mempalace_find_tunnels`, etc.).
- **No mine-equivalent.** This pilot has no analog to `mempalace mine` — no project-file or transcript mining, no automated drawer-filing from repository content. It is diary-only, by explicit scope, matching the task that created it.
- **No multi-tenant access control, no AAAK-format enforcement, no diary-read pagination beyond a simple `last_n` cutoff.**
- **Single-machine, single-collection.** Everything lives in one local qdrant collection at `C:\mem0_trial_venv\qdrant_data`, shared with the original trial's synthetic test data (isolated by `user_id`, not physically separate) — not a production-grade deployment consideration yet, just what this pilot needed.

## What's genuinely working, and what that's worth

For the one function that matters most right now — writing a real session-continuity note and reading it back correctly at the start of the next session — this pilot did exactly that, once, for real, today, while MemPalace's equivalent calls failed in the same moment. That's a real, positive data point for this specific narrow use case. It is one real use, not a track record — the honest read, consistent with the prior trial's own caveats, is that this needs at least one more real session's use (writing at close, reading back at the *next* session's actual start, not the same session) before it means anything close to a track record.

## Standing status

No MOB entry claims MemPalace is replaced. Nothing MemPalace-related was touched, disabled, or migrated — its own diary/status calls were exercised read-only, for comparison, exactly as before. This file itself, and the wrapper it documents, are the full extent of what changed. The adoption decision — pilot further, adopt, or set aside — is explicitly Pete's, to be made after seeing this and using it for real at least once more.
