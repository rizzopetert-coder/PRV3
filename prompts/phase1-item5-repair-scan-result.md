# `mempalace repair scan` — Result Against the Read-Only Copy

Date: 2026-08-24. Read-only, against `C:\mempalace_readonly_copy` only, `scan` operation only (no `prune`, no `rebuild`) — never against the live `~/.mempalace/palace` install.

## Copy freshness

Checked before running: live `chroma.sqlite3` and the copy are byte-identical in size (1,793,785,856 bytes both sides, matching the state from the prior task). No refresh needed — no real content has changed since the last refresh, confirmed by size match rather than assumed.

## Result: scan segfaults, does not complete

Ran `mempalace.repair.scan_palace(palace_path=r"C:\mempalace_readonly_copy")` as an isolated subprocess (so a crash wouldn't affect anything else), with an explicit path override so it never touches live config or the live install.

**Precisely characterized where it dies, via unbuffered output:**
```
Palace: C:\mempalace_readonly_copy
Loading...
[SEGFAULT, exit 139]
```

The collection opens successfully ("Loading..." prints, matching the prior finding that `get_collection()` alone never crashes). The crash happens on the very next line of `repair.py`'s own `scan_palace()` — `col.count()` (line 96), called before the actual per-ID scanning loop ever begins.

## What this confirms — independent reconfirmation, not new information, but from a different angle

This is the **third independent confirmation** of the same root cause, now via MemPalace's own official diagnostic tool rather than a fresh test script: `count()` on `mempalace_drawers` segfaults, full stop, regardless of which code calls it. Direct chromadb API testing (the original feasibility check) found this; a fresh isolated reproduction on a byte-verified copy found it again; now MemPalace's own `repair.py` — purpose-built specifically to diagnose and fix this exact failure class — cannot even get past its own first diagnostic step.

**Against the `repair.py`-documented duplicate-ID/HNSW-bloat theory specifically:** this doesn't confirm or refute the theory directly — `scan_palace()` never gets far enough to actually scan for corrupt/duplicate IDs, since it crashes before the ID-listing step even starts. What it does confirm is that **`scan` itself is not currently a usable diagnostic path for `mempalace_drawers`** — the tool's own author built `scan` → `prune` → `rebuild` as a three-step recovery path, but `scan`, the read-only first step, cannot complete against this specific corruption. This is a real, concrete data point for any future decision about pursuing the root-cause fix further: **the natural next diagnostic step doesn't work either, and `rebuild` (which bypasses the broken index entirely by reading only from `chroma.sqlite3`, "the source of truth," and recreating the HNSW structure fresh) may be the only path in `repair.py`'s own toolkit that could actually succeed** — though `rebuild` is explicitly destructive-adjacent (deletes and recreates the collection) and was explicitly out of scope for this pass, consistent with the standing hard constraint against anything but read-only operations against MemPalace data this session.

`COLLECTION_NAME` in `repair.py` is a hardcoded module constant (`"mempalace_drawers"`) — `scan_palace()` has no way to target `mempalace_closets` instead, so this result is specific to drawers; closets was not (and structurally cannot be, via this exact function) separately tested here.

## Bottom line

Scan: **attempted, did not complete, crashed the same way everything else touching this index crashes.** Not a new finding in terms of root cause, but a real, useful confirmation that the tool's own intended recovery path is itself blocked at its first step — relevant context for whoever picks up the root-cause thread next.
