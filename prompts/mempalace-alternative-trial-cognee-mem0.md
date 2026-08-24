# MemPalace Alternative Trial — Cognee and Mem0 (Free/Local Tiers)

Date: 2026-08-23
Scope: evidence-gathering only. No recommendation, no go/no-go call — that's Pete's decision, made from the findings below, not from either vendor's own claims. No PRV3 application code, engine, or web-layer files were touched. Both candidates were installed into isolated venvs (`C:\mem_trial_venv`, `C:\mem0_trial_venv`), outside the PRV3 repo, with no real MemPalace data migrated — synthetic/throwaway content only.

---

## Cognee

### Install experience

`pip install cognee` initially **failed** at a deeply nested temp path (`...scratchpad\mem_trial_venv\Lib\site-packages\litellm\proxy\guardrails\...\block_age_discrimination.jsonl`) — a Windows long-path limit hit by one of `litellm`'s own bundled files, not anything specific to this trial's setup. Re-running the identical install at a short root-level path (`C:\mem_trial_venv`) succeeded cleanly. This is a real, reproducible Windows install hazard for anyone installing Cognee into a deeply nested project path (a `node_modules`-style structure, a long username, a CI cache directory) — worth knowing before assuming a plain `pip install cognee` will just work.

**Dependency weight, confirmed by direct count: ~92 packages**, including `litellm`, `boto3`, `instructor`, `lancedb`/`pylance`, `fastapi`, `fastapi-users`, `sqlalchemy`, `alembic`, `gunicorn`. This is a substantially heavier install than either MemPalace or Mem0 (see below) — closer to a small application server than a lightweight memory client.

### Default configuration, confirmed by direct inspection (not assumed)

- Relational DB provider: `sqlite` (confirmed local).
- Graph DB provider: `ladybug` — **not** KuzuDB, contrary to the commonly-cited "SQLite/LanceDB/KuzuDB" description of Cognee's default stack. That description is stale for the installed version (Cognee 1.5.3); the graph layer has since moved to an embedded library called `ladybug`. Reported here as found, not assumed to still be accurate in future releases either.
- Vector engine: wraps LanceDB under the hood (confirmed via the dependency list — `lancedb`, `pylance`, `lance-namespace` — the direct class object is a `_VectorEngineHandle` wrapper, not inspected further).
- **On first real use, Cognee also defaults to `authentication=required, multi_tenant=enabled`** — real user/tenant/auth machinery, not something a single-user local memory tool would obviously need, confirmed via its own startup log line. A real, substantial migration suite runs on first use: 28 separate Alembic migrations (users, sessions, multi-tenant permissions, API keys, notebooks, sync operations), executed automatically. This is a meaningfully heavier internal architecture than "a local memory store," closer to a multi-user backend service running embedded.

### The decisive finding — Task 1.1

**Cognee's `add()` step itself — not just `cognify()` — fails immediately with `LLMAPIKeyNotSetError` (HTTP-style status 422) when no LLM API key is configured.** Confirmed directly: with all `*_API_KEY`/`OPENAI`/`LLM` environment variables deliberately unset, calling `cognee.add()` on two lines of synthetic text raised `LLMAPIKeyNotSetError: LLM API key is not set.` before `cognify()` was ever reached. Cognee's default LLM provider is `openai`.

**Cognee does support genuinely local LLM providers** (`ollama`, `llama_cpp`) — confirmed by direct inspection of `cognee/infrastructure/llm/config.py`'s `KNOWN_LLM_PROVIDERS`/`LOCAL_LLM_PROVIDERS` sets. But using them requires installing and running a separate local inference server plus downloading a model (typically multiple gigabytes) — genuinely free, but not the out-of-box default, and a meaningfully heavier setup than MemPalace's or Mem0's local paths. **This trial did not install Ollama or download a model** — a multi-GB download and a new local server process is disproportionate to a client-library evaluation and wasn't separately authorized. This is reported as a real scope limit, not a finding of infeasibility: the local path likely works, just wasn't exercised here.

**Verdict on "free and local": does not hold at default settings.** A genuinely free/local configuration exists but requires substantial additional setup beyond `pip install cognee` — closer in weight to standing up a second local service than to configuring a client library.

### Reliability test (Task 2)

**Not run.** Cognee's most basic write operation (`add()`) cannot execute at all without either a paid OpenAI API key or the separate Ollama/llama_cpp setup this trial didn't attempt. There is no way to perform a genuine free/local write-reliability test against Cognee's actual storage layer without first solving that dependency — this is itself the most important finding about Cognee, more decisive than a reliability number would have been.

One real, spontaneous reliability signal did surface anyway, before the write ever reached the LLM gate: Cognee's own `prune_data` (reset) step logged a real, recovered error on this machine's first run — `record_operation: failed to persist prune_data record ((sqlite3.OperationalError) unable to open database file`) — a SQLite access/locking issue on Windows, encountered on the very first real invocation, before any content write was attempted. It was non-fatal (the run proceeded, "Database deleted successfully" followed immediately after), but it's a real rough edge on the exact class of operation (first-run local DB setup) that this trial exists to stress-test.

### Independent corroboration (GitHub issue tracker, `topoteretes/cognee`)

- **Issue #2119**: `cognee.add()` and `cognify()` hang indefinitely (10+ minutes of silent retries) when configured against a local OpenAI-compatible LLM endpoint (Ollama, llama-cpp-python) on macOS. This directly corroborates that the local-LLM path this trial didn't attempt has its own documented reliability problem — a hang, not a crash — meaning skipping it here wasn't just proportionate caution, it likely avoided a real known failure mode.
- **Issue #2038**: a missing `raise` statement in `config.py`'s `set_vector_db_config()` causes silent validation failures — a config-layer instance of the exact "fails silently, reports success" failure class MemPalace's own undiagnosed exit-code-5 belongs to.
- **Issue #2022**: a documented crash loop on Docker deployment, involving `sqlalchemy.exc.ProgrammingError` on an `ALTER TYPE` migration and a `NoSuchTableError` — the same general category (migration/database-access failure) as this trial's own first-run SQLite error above, though a different specific cause.

Sources:
- [Issue #2119 — hangs indefinitely with local LLM on macOS](https://github.com/topoteretes/cognee/issues/2119)
- [Issue #2038 — silent validation failures, missing raise](https://github.com/topoteretes/cognee/issues/2038)
- [Issue #2022 — database crash loop on deployment](https://github.com/topoteretes/cognee/issues/2022)

### Comparison to MemPalace's actual observed behavior

No clear signal either way on raw write reliability — Cognee couldn't be tested on that axis in this trial. On setup and default-configuration weight, Cognee is clearly heavier and more failure-prone than MemPalace: a Windows long-path install failure on first attempt, a real (if recovered) SQLite error on first real run, a mandatory LLM API dependency MemPalace doesn't have, and independent evidence of an indefinite-hang failure mode on its own advertised free/local path.

---

## Mem0 (self-hosted / open-source, free vector-only tier)

### Install experience

`pip install mem0ai` succeeded cleanly on the first attempt, no path issues, no long-path failures. **Dependency weight: 37 packages** — `qdrant-client` and `openai` are pulled in as defaults, plus standard HTTP/pydantic plumbing. Roughly a third the size of Cognee's install.

### Default configuration, confirmed by direct inspection

- Default vector store: `qdrant`, configured to an embedded local path (`/tmp/qdrant` by default) — no external service required for the vector store itself.
- **Default LLM provider: `openai`. Default embedder provider: also `openai`.** Confirmed directly: instantiating `Memory()` with zero configuration and no API key set fails immediately — `OpenAIError: Missing credentials... set the OPENAI_API_KEY... environment variable`. This failure happens at `Memory.__init__()` itself, **before any write is attempted** — a real architectural finding: Mem0 unconditionally constructs an LLM client at object-construction time, even for use cases (like this trial's) that never intend to call the LLM at all.
- Mem0 does support genuinely local, no-network alternatives for both roles: `ollama` for the LLM, and `huggingface`/`fastembed` for the embedder — confirmed via direct inspection of `LlmFactory`/`EmbedderFactory`'s registered providers.
- **`Memory.add()` has a documented `infer: bool = True` parameter.** Setting `infer=False` skips Mem0's LLM-based fact-extraction step entirely and stores the raw content directly against the configured embedder — the one path in either candidate that reaches a genuinely free, zero-real-API-call write with no separate server to install.

### The decisive finding — Task 1.2

**A fully free, fully local write path exists in Mem0 and was successfully exercised** — `fastembed` (a lightweight, ONNX-based local embedding library, no server, no account, ~35MB of models auto-downloaded from Hugging Face on first use) as the embedder, plus `infer=False` on every write to bypass the LLM entirely. **The LLM client still had to be constructed** (the architectural quirk above), which required a syntactically-present placeholder string as `OPENAI_API_KEY` purely to satisfy the constructor — using a deliberately invalid placeholder value proved no real call was ever attempted (a real call would have failed loudly with a 401; none did, across 20 real writes).

**Verdict on "free and local": holds, but requires non-default configuration to get there.** Out of the box, `Memory()` also demands an OpenAI key, same as Cognee. Unlike Cognee, the path to a genuinely free/local setup is lightweight (one extra `pip install fastembed`, no separate server, no multi-GB model download) and was fully exercised in this trial, not just confirmed to theoretically exist.

### Reliability test (Task 2) — PASS

Two fully separate process instances (`python test_mem0_reliability.py 1`, then a second, independent process `... 2`), simulating the kind of session-restart boundary MemPalace has specifically been failing across:

| Run | Writes attempted | Writes succeeded | Retrieval verified |
|---|---|---|---|
| 1 (fresh process) | 10 | **10/10** | `get_all()` returned all 10; `search()` for a specific known write returned it in the top result with exact matching text |
| 2 (separate fresh process, loading Run 1's persisted data) | 10 | **10/10** | `get_all()` returned all **20** (both runs' content, confirming real cross-process persistence); `search()` correctly surfaced both runs' matching entries |

**20/20 real writes succeeded across both process instances. Retrieval was checked for actual content correctness, not just a non-error return** — every write's exact original text was confirmed present via both a full listing and a targeted search. This directly matches the shape of test MemPalace has been failing (real writes across a process boundary), and Mem0 passed it cleanly under this configuration.

**One real, reproducible rough edge, not a data-loss bug:** at Python interpreter shutdown, Qdrant's client finalizer raises a `ModuleNotFoundError: import of msvcrt halted` on Windows, every run, after all real work already completed successfully. Noisy stderr output on exit, not a failure of any operation — but a real Windows-specific wrinkle, reported honestly rather than omitted for looking clean.

**One documentation-mismatch finding, per Task 2.4:** this installed version (`mem0ai` 2.0.18)'s `get_all()`/`search()` no longer accept `user_id` as a direct keyword argument — it now requires `filters={"user_id": ...}`. The first test script, written against commonly-referenced usage examples, failed on this exact mismatch and had to be corrected before the reliability test could run at all. A real instance of "diverged from documentation," the same skepticism already applied to every other vendor claim this session.

### Independent corroboration (GitHub issue tracker, `mem0ai/mem0`)

This is where the picture gets genuinely mixed, and needs to be reported precisely rather than let this trial's own clean pass stand in for the whole product:

- **Issue #5245** — "Silent memory loss when batch embedding partially fails in V3 add pipeline": `Memory.add()` can silently drop extracted memories when the embedding provider fails on individual items inside a batch; the failure is logged at WARNING level, no exception raised, caller has no way to know.
- **Issue #3009** — "3 out of 5 memory creations lost - Fact extraction inconsistently returns empty results."
- **Issue #4573** — "What we found after auditing 10,134 mem0 entries: 97.8% were junk" — a data-quality (not availability) finding, but a serious independent signal about the LLM-based fact-extraction path specifically.
- **Issue #4985** — switching embedding provider silently drops writes due to a vector-dimension mismatch; a success response with a memory ID is still returned even though nothing was persisted.
- **Issue #3441** — `mem0.add()` silently returns `{'results': []}` and stores nothing when configured with Ollama's `mxbai-embed-large` embedder specifically.
- **Issue #2895** (OpenMemory/Docker variant) — complete data loss on `docker-compose down && up` due to an incorrect volume mount path in the reference deployment script.

**Important scope note:** every one of these silent-loss issues traces to Mem0's **LLM-based fact-extraction pipeline** (`infer=True`, the default) or to specific embedder/provider-switching edge cases — not to the exact configuration this trial exercised (`infer=False`, a single fixed local embedder, no provider switching, no Docker). This trial's clean 20/20 result is real and was genuinely verified, but it does not clear Mem0 of these independently-documented silent-failure patterns — it simply didn't exercise the code paths where they're reported to occur. A production trial using Mem0's default LLM-based extraction mode, or switching embedding providers mid-stream, should not assume this trial's clean result carries over.

Sources:
- [Issue #5245 — silent memory loss, batch embedding partial failure](https://github.com/mem0ai/mem0/issues/5245)
- [Issue #3009 — 3 of 5 memory creations lost](https://github.com/mem0ai/mem0/issues/3009)
- [Issue #4573 — 97.8% of audited entries were junk](https://github.com/mem0ai/mem0/issues/4573)
- [Issue #4985 — silent write loss on embedding provider switch](https://github.com/mem0ai/mem0/issues/4985)
- [Issue #3441 — silent empty-results write with Ollama embedder](https://github.com/mem0ai/mem0/issues/3441)
- [Issue #2895 — OpenMemory Docker volume-path data loss](https://github.com/mem0ai/mem0/issues/2895)

### Comparison to MemPalace's actual observed behavior

On the exact axis this trial was built to test — real writes across process restarts, in the specific configuration exercised — Mem0 passed cleanly where MemPalace has been failing: 20/20 successful writes with verified-correct retrieval, versus MemPalace's confirmed pattern of zero successful real writes across 5+ consecutive attempts (segfault). That is a genuine, positive signal for this specific configuration. It is not a categorical "Mem0 is more reliable than MemPalace" finding — the independent issue tracker shows Mem0 has its own real, documented silent-failure modes, concentrated in a different part of its pipeline (LLM-based extraction, provider switching) than what this trial exercised. The honest comparison is: **better, under the narrow configuration actually tested; unknown, under Mem0's own default (LLM-based) configuration, which this trial deliberately avoided to keep the test free.**

---

## Summary table

| | Cognee | Mem0 (vector-only, `infer=False`) |
|---|---|---|
| Install succeeded | Yes, after a path-length workaround | Yes, first attempt |
| Dependency count | ~92 packages | 37 packages |
| Free/local by default | **No** — `add()` itself requires an LLM API key | **No** — `Memory()` construction requires an LLM API key present |
| Free/local achievable | Yes, via Ollama/llama_cpp — not attempted (heavy: separate server + multi-GB model) | Yes, via `fastembed` + `infer=False` — attempted and confirmed working |
| Real-write reliability test | Not run (blocked by the above) | **20/20 passed**, verified retrieval, across 2 process restarts |
| Own GitHub issues, relevant class | Indefinite hang on local-LLM path (#2119); silent config-validation failure (#2038); migration crash loop (#2022) | Multiple silent write-loss reports, all traced to the LLM-extraction/provider-switch paths this trial didn't exercise |
| Rough edges found firsthand | Windows long-path install failure; first-run SQLite access error (recovered); mandatory multi-tenant auth machinery | `msvcrt` shutdown-time error (benign); `user_id` kwarg API break vs. common docs |

No recommendation is made here. Pete's decision, from this evidence plus whatever weight he puts on the scope caveats above — particularly that Mem0's clean result is real but narrower than "Mem0 is reliable," and that Cognee's local path is unverified rather than confirmed broken.
