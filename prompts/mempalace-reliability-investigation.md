# MemPalace Reliability Investigation

2026-08-23. Originally diagnostic only. **Updated same day: the Unicode/install-routing bug (§2, §5 below) has since been fixed and verified — see the new §6 at the end of this file.** Every claim traced to a real, checkable source: crash dumps, installed package files, MCP config, or a direct reproduction, not inference from the MOB's summary alone.

## Headline finding

**Two of the three documented failure modes have real, identified root causes. The third remains undetermined.** And a structural discovery along the way: this machine has two entirely separate `mempalace` installations, and the one that actually runs by default is a plain, unmodified PyPI install — not the local development checkout that turned out to have a (currently irrelevant) locally-patched copy of the exact file at fault.

## 1. The environment: two installations, only one of which actually runs

`where mempalace` resolves two entries, in this order:

1. `C:\Users\rizzo\AppData\Local\Programs\Python\Python312\Scripts\mempalace.exe` — a normal, non-editable `pip install`, reports `mempalace` core paired with `chromadb==1.5.8`.
2. `C:\Users\rizzo\AppData\Roaming\Python\Python314\Scripts\mempalace.exe` — an **editable install** (`pip install -e`) pointing at a local source checkout, `C:\Users\rizzo\mempalace-src`.

Windows PATH resolution picks the first match — **#1 (Python 3.12) is what actually executes** for a bare `mempalace` invocation, confirmed directly: an earlier traceback from this same session (`mempalace.exe\__main__.py` → `Python312\Lib\site-packages\mempalace\...`) shows the 3.12 install firing, and the `python.exe` crash dump analyzed below (§3) loads `python312.dll`, confirming the segfault also happened inside this same install, not the dev checkout.

**The local dev checkout (`C:\Users\rizzo\mempalace-src`) is on branch `develop`, 133 commits ahead of the `v3.3.0` tag** (`git describe --tags` → `v3.3.0-133-gd4c9424`), up to date with `origin/develop`. It carries one uncommitted local change:

```diff
--- a/mempalace/miner.py
+++ b/mempalace/miner.py
@@ -779,7 +779,7 @@ def mine(
-    print(f"{'─' * 55}\n")
+    print(f"{'-' * 55}\n")
```

That `─` (U+2500) is the exact character behind the cosmetic `UnicodeEncodeError` first diagnosed two sessions ago. **Someone (unclear who, or when) already found and patched this exact bug — but in the checkout that doesn't run.** The fix has zero effect on the real, PATH-resolved `mempalace` command. This is worth flagging plainly: if a future session edits files under `mempalace-src` expecting it to change real behavior, it won't, unless invocation is explicitly redirected there.

## 2. Root cause, failure mode 1 — the cosmetic `UnicodeEncodeError`

**Confirmed, reproducible, precisely located.** This environment's default `sys.stdout.encoding` is `cp1252` (confirmed directly, both in an interactive-style check and inside a piped/non-tty subprocess — `isatty()` False, encoding still `cp1252`; the Windows console's own active code page is a *third*, different value, 437, underscoring that this isn't simply "whatever the console says" but Python's own Windows-specific default for redirected/non-console streams). `cp1252` cannot represent most Unicode punctuation.

Scanning the **real, executing** `miner.py` (Python 3.12 install) for non-ASCII characters inside `print()` calls found five:

| Line | Character | Codepoint |
|---|---|---|
| 607 | `→` | U+2192 |
| 779 | `—` | U+2014 |
| 784 | `─` | U+2500 |
| 814 | `✓` | U+2713 |
| 852 | `—` | U+2014 |

Any of these firing under the default `cp1252` stdout crashes with `UnicodeEncodeError`, exit code 1, full traceback printed (confirmed by direct reproduction: `print('\u2192')` under this shell's default environment crashes identically, exit code 1, immediately). This is not a maybe — it's a certainty every time one of these five lines executes without `PYTHONIOENCODING=utf-8` (or equivalent) set first. Only one of the five (line 784, originally line 779 pre-divergence) has ever been patched, and only in the checkout that doesn't run.

**Classification: real MemPalace-side bug** (hardcoded console output not safe for Windows' non-UTF-8 stdout default), **exposed by an environment characteristic** (Windows defaults to `cp1252` for non-console-attached stdout) that a cross-platform CLI should account for but here doesn't.

## 3. Root cause, failure mode 3 — the segmentation fault

**Real crash dump recovered and analyzed; root cause narrowed but not fully proven.** Windows Error Reporting keeps automatic crash dumps at `%LOCALAPPDATA%\CrashDumps`. Three `python.exe` dumps exist:

| File | Timestamp | Likely correlation |
|---|---|---|
| `python.exe.28948.dmp` | **2026-08-22 16:46** | Matches, to the hour, this session's own direct segfault reproduction (`mine`, `PYTHONIOENCODING=utf-8` forced to bypass failure mode 1, exit 139) |
| `python.exe.31584.dmp` | 2026-06-29 22:33 | Unconfirmed — no session record checked against this date; could be unrelated `python.exe` usage (this environment runs many engine/calibration scripts) |
| `python.exe.36640.dmp` | 2026-06-29 22:33 | Same caveat as above |

Extracted the loaded-module list from the Aug 22 dump (string search for `.dll`/`.pyd`/`.exe` names in the minidump's UTF-16LE module-path records — not a full stack unwind, no debugger available in this environment, but informative on its own):

```
_sqlite3.pyd
chromadb_rust_bindings.pyd
python3.dll / python312.dll
sqlite3.dll
ucrtbase.dll / VCRUNTIME140.dll / VCRUNTIME140_1.dll
```

`chromadb_rust_bindings.pyd` — chromadb's native Rust extension — being loaded at crash time, alongside the SQLite modules, is the most direct evidence available: the fault happened somewhere in chromadb's native persistence layer, not in pure-Python mempalace code. This connects directly to a fact already on record from an earlier session's (successful) non-persistence investigation: chromadb 1.5.8's HNSW index only calls `_persist()` once a per-process write counter crosses `hnsw:sync_threshold`, and that threshold was deliberately **lowered from 1000 to 10** as part of the earlier fix — meaning real disk-persist operations through this exact native code path now fire far more often on every `mine` run than they used to. **Working hypothesis, not proven:** the earlier, correct fix for non-persistence increased exposure to a separate, pre-existing native-binding fragility in chromadb's persist path. I did not attempt to re-trigger the segfault a second time this pass — a real crash dump from an actual prior occurrence was already in hand, and deliberately reproducing a native crash again for its own sake didn't seem worth the risk given diagnosis-only scope.

**Classification: most likely a chromadb-dependency-side native bug**, indirectly exposed by mempalace's own (correct, for its stated purpose) threshold change. Not proven to the level of a specific line of Rust source — that would need a debugger session against the dump, out of scope here.

## 4. Failure mode 2 — silent exit-code-5, zero diagnostic output

**Undetermined.** Every direct reproduction of the Unicode crash in this pass produced exit code 1 with a full traceback, not a silent exit-5. No `sys.exit(5)` or comparable was found in a scan of the real `miner.py`/`cli.py`. No log file, WER dump, or other artifact correlating specifically with exit-5 was found anywhere checked (`~/.mempalace` itself has no log files at all — only its data directories; the CrashDumps folder holds only genuine crash (non-zero unhandled-exception-with-dump) events, and exit-5 by definition produced no dump). This may be a distinct native-level fault that Windows didn't capture, a different code path entirely, or something environment-specific that didn't reproduce today. Flagging plainly rather than force-fitting it into either of the two explained modes above.

## 5. Diary-write vs. mine — how independent are they, really?

**Not structurally independent — same install, same package, same underlying storage layer — but exercised very differently.** Traced directly in source, not inferred from behavior:

- **Same Python, same package, confirmed via config, not assumption.** `~/.claude.json`'s MCP server entry for this project hardcodes the launch command: `C:\Users\rizzo\AppData\Local\Programs\Python\Python312\python.exe -u -m mempalace.mcp_server ...` — the identical Python 3.12 install that `mine` runs under when invoked bare. The "diary succeeds, mine fails" pattern is not explained by them running under different pythons or different package copies.
- **No shared function call, but a shared storage layer.** `mcp_server.py` does not import `miner.py` at all (confirmed via grep — zero matches). `tool_diary_write()` calls `col.add(ids=[entry_id], documents=[entry], metadatas=[...])` directly against the same `_get_collection()` chromadb collection object that `mine` ultimately writes into. They are two independent code paths converging on one shared chromadb/Rust-binding backend, not two isolated systems.
- **The real difference is volume and batching, not code.** `diary_write` issues one `.add()` call for one document per invocation. `mine` processes hundreds of files in one run, calling into the same collection repeatedly in a tight loop. That difference in write volume is the most plausible reason `diary_write` rarely (if ever) crosses whatever threshold or timing condition the native persist-path bug depends on, while `mine` — especially post-threshold-lowering — reliably does. Not proven directly (would need to trigger a large enough `diary_write` batch to test), but it's the explanation best supported by what's actually in the code.
- One incidental finding along the way: `tool_diary_write`'s own logging line (`logger.info(f"Diary entry: {entry_id} → {wing}/diary/{topic}")`) also contains a `→` (U+2192) — the same character class that crashes `mine`. It hasn't been observed to crash diary_write, most likely because Python's `logging` module handlers can carry their own explicit encoding independent of `sys.stdout`, not because the character is somehow safe. Not confirmed which handler config this MCP server actually uses — flagged, not chased further.

## Summary characterization

| Failure mode | Root cause | Confidence |
|---|---|---|
| Cosmetic `UnicodeEncodeError` (2 sessions ago) | Hardcoded non-ASCII characters in `miner.py` console output, crashing under this environment's default `cp1252` stdout | **High — directly reproduced, exact lines/characters identified in the real executing install** |
| Segmentation fault (this session, 2 sessions ago) | Native fault inside chromadb's Rust persistence bindings, plausibly connected to the earlier `hnsw:sync_threshold` lowering increasing real persist-path exposure | **Moderate — real crash dump confirms the faulting module, mechanism narrowed but not proven to source-line level** |
| Silent exit-code-5, zero output | Unknown | **Undetermined — no correlating artifact found** |

Overall: **primarily a MemPalace-side bug (failure mode 1) plus a likely chromadb-dependency-side native stability issue (failure mode 3)**, not an environment/integration misconfiguration on this machine beyond "Windows defaults expose a bug MemPalace's own code doesn't account for." The two-installation split (§1) is a separate, real finding worth having on record, but it is not itself a cause of any of the three failure modes — both the original crash and this session's segfault happened in the same install that's actually in use.

## On alternatives (reporting only, not a recommendation)

Pete's standing note flags mcp-memory-service, Cognee, self-hosted mem0, and Graphiti as alternatives worth considering before any replacement decision. What this investigation found:

- Failure mode 1 (Unicode/cp1252) is a shallow, well-understood, single-mechanism bug with an available workaround already in this project's own practice (`PYTHONIOENCODING=utf-8`) and a known, already-drafted (if misplaced) one-line fix. It does not, on its own, point toward needing a different tool.
- Failure mode 3 (segfault) traces to chromadb's native bindings specifically, not to mempalace's own Python logic. Whether that risk would follow into an alternative tool depends on whether that alternative also uses chromadb as its vector-storage backend — **not checked this pass, genuinely unknown**. If an alternative uses a different backend entirely, this specific risk wouldn't transfer; if it also uses chromadb, it plausibly would.
- Neither finding characterizes the *architecture* as unsound — both have identifiable, bounded causes rather than pointing to something systemically unreliable about MemPalace's design.

No recommendation follows from this pass either way — that's explicitly Pete's call, and this investigation wasn't scoped to evaluate the alternatives themselves.

## 6. Fix applied and verified (2026-08-23, same day)

**Scope: the Unicode bug and install-routing only.** Failure mode 2 (silent exit-5) was not touched — stays a separate, still-open investigation, exactly as before.

**Point 1, confirmed before touching anything:** re-verified the MCP config directly (`~/.claude.json`) — the PRV3 server entry hardcodes `C:\Users\rizzo\AppData\Local\Programs\Python\Python312\python.exe`, the same install `where mempalace` resolves first for a bare CLI invocation. The dev checkout's own uncommitted patch (§1) was checked against the actual bug, not trusted on sight: it correctly replaces `─` (U+2500) with `-` — a real, correct fix for the one line it touches. But a broader scan of the checkout's own `miner.py` (not just the one already-patched line) found the same character class at 4 more locations in that file alone, and a full-package scan of the **live** 3.12 install found the identical pattern at roughly 40 more sites across 16 files. The existing patch was correct but far from complete, and — as established in §1 — irrelevant regardless, since it lives in the install that doesn't run.

**Point 2, decision:** fixed the live install directly (option (b) from the task), not repointing MCP config to the dev checkout (option (a)). Reasoning: the dev checkout is 133 commits ahead of `v3.3.0` on `develop` — repointing to it would pull in that entire span of unreviewed upstream changes just to get one already-drafted one-line fix, a much larger and riskier change than the bug warrants. Fixing the live install directly is narrower and targets the exact code that's actually running.

**What was fixed, in the live install only (`Python312\...\mempalace\`):**
- `miner.py`: all 5 non-ASCII characters in `print()` calls (not just the 1 the dev checkout's patch covered) — lines 607 (`→`→`->`), 779 (`—`→`--`), 784 (`─`→`-`), 814 (`✓`→`[OK]`), 852 (`—`→`--`).
- `mcp_server.py`: both non-ASCII characters in `logger.info()` calls — line 657 (`Filed drawer: ... →`) and line 974 (the diary_write logging line flagged as a latent risk in §5 above) — both `→`→`->`.
- Deliberately **not** fixed: the same pattern repeated ~40 more times across 14 other files (`cli.py`, `closet_llm.py`, `convo_miner.py`, `dedup.py`, `dialect.py`, `entity_detector.py`, `exporter.py`, `layers.py`, `migrate.py`, `onboarding.py`, `repair.py`, `room_detector_local.py`, `searcher.py`, `split_mega_files.py`) — none implicated in any reported failure, out of this task's explicit scope. Confirmed via source trace that `cmd_mine` calls directly into `miner.mine()` without passing through any of `cli.py`'s own affected lines, so this doesn't leave a gap in the specific failure mode being fixed. Flagging the wider pattern here for the record, not actioning it.
- Patch script (not committed to this repo, targets files outside it): `tools/patch_mempalace_unicode_fix.py`.

**Retired the redundant second install.** `pip uninstall mempalace` under the Python 3.14 interpreter removed the editable registration — `where mempalace` now resolves to exactly one entry (the fixed 3.12 install). The dev checkout directory itself (`C:\Users\rizzo\mempalace-src`) was left untouched — still on disk, git history intact, its own (now-superseded) local patch still sitting there uncommitted, fully reversible (`pip install -e` again) if ever wanted. Confirmed via `git status` inside the checkout that nothing there was touched by this pass.

**Point 4, verification, and its real limits — stated plainly, not overclaimed:**
- `mempalace mine "..." --dry-run` (the exact original failing conditions — no `PYTHONIOENCODING` override) completed cleanly, exit code 0, zero crash — directly exercising 4 of the 5 patched `miner.py` lines (607, 779, 784, 852) in a live run. An uncaught `UnicodeEncodeError` would have halted the script immediately with a non-zero exit; it didn't.
- The 5th line (814, the `[OK]` checkmark) only fires on a real, non-dry-run write, and **full reproduction of that specific line wasn't safely possible this pass**: both a real `mempalace status` call and a real `mempalace mine` against a disposable throwaway directory segfaulted (exit 139) — the separate, already-documented failure mode 3 (§3), not the Unicode bug. New information from this: the segfault now reproduces on *every* real write attempted today, including a trivial one-file mine and a plain read-only `status` call — more reliably than previously known, not confined to large bulk-mine runs. Indirect evidence the Unicode fix holds on the write path too: no `UnicodeEncodeError` fired before the segfault, and `print()` calls execute strictly in source order, so line 814 (if still broken) would have crashed first, before chromadb's write path is ever reached.
- `mcp_server.py`'s two fixes were not live-round-trip-tested (an actual MCP tool call) — attempted one (`mempalace_status`) and it returned "Connection closed," the same MCP connectivity failure this session has hit repeatedly for reasons unrelated to this fix, not re-diagnosed here.
- Both patched files confirmed to compile cleanly (`python -m py_compile`, zero errors) — rules out any syntax-level mistake in the patch itself, independent of the runtime checks above.

**Failure mode 2 (silent exit-5): status unchanged, reconfirmed still open.** Not investigated, touched, or newly evidenced by this pass — exactly as characterized in §4 above.
