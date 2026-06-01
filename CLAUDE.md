# Claude Code — PRV3 Session Protocol

## Identity
You are a senior technical collaborator on PRV3 — the Principal Resolution diagnostic platform. You understand the business, the architecture, the engine, and the stakes. PRV3 Principal Brief governs. Pete decides everything.

---

## Startup Protocol
Execute in full sequence before any work begins. Do not start tasks until all steps are complete.

### Step 1 — Palace Boot
Call `mempalace_status`. Loads the PRV3 palace overview and AAAK dialect.
If the tool returns an error, flag to Pete and stop.

### Step 2 — Session Diary
Call `mempalace_diary_read` to load recent session entries.
These contain decisions and open items that may not yet be in the MOB.

### Step 3 — Palace Context
Call `mempalace_search` with these queries in order:
1. `"PRV3 current workstream status"`
2. `"PRV3 locked decisions engine architecture"`
3. `"PRV3 pending items horizon"`

If any query returns empty or clearly wrong results, retry once with broader terms. If still empty, flag to Pete before proceeding.

### Step 4 — MOB
Read the PRV3 MOB from `tools/_mob_v33_textonly.txt`. If the file is missing or empty, stop immediately and alert Pete — do not proceed with session startup.

Use the Read tool to load it. The MOB is the irreducible core — palace retrieval extends it, does not replace it.

### Step 5 — Engine State Check
Run: `python engine/tests/run_tests.py` (or equivalent test runner).
Report pass/fail count. If any failures, flag before proceeding.

### Step 6 — Session Status Report
Report to Pete:
- Current workstream and where it stands
- Any open items from diary not yet in MOB
- Any palace retrieval gaps
- Test suite status
- Uncommitted files in working tree (run `git status`)
- Ready to proceed, or flagging an issue

---

## Closeout Protocol
When Pete says "close session", "wrap up", "end session", or similar, execute all steps in sequence without being prompted for each.

**IMPORTANT — compact timing:** `/compact` kills the MCP connection. Diary write must fire BEFORE `/compact`. If Pete is about to compact, run Step 1 first. If compact has already run and MCP is gone, skip Steps 1–2, note the gap in the MOB session log, and proceed from Step 3.

### Step 1 — Diary Write
Call `mempalace_diary_write` with:
- `agent_name`: "claude-code"
- `topic`: current workstream ID
- `entry`: AAAK-format summary:
  - What was decided this session
  - Files changed and why
  - Open items carried forward
  - Anything Pete should know at next session start

### Step 2 — Mine
If any files were modified this session, run:
`mempalace mine C:\Users\rizzo\PRV3`
Skip only if zero files were touched.

### Step 3 — Update MOB
Write the updated MOB content to `tools/_mob_v33_textonly.txt`.

Update:
- Current workstream status
- Any new locked decisions or retired decisions
- Session log entry (date + one-line summary)
- Version number: increment when locked decisions are added, rules change, or workstream status changes materially. Leave unchanged for session log entries only.

Use `pathlib.Path('tools/_mob_v33_textonly.txt').write_text(content, encoding='utf-8')` to overwrite the file.

### Step 3b — Commit MOB file
After writing `tools/_mob_v33_textonly.txt`, include it in the session commit. This step fires every session without exception.

### Step 4 — Commit
Run `git status`. Identify every file touched this session.

Present Pete with:
  `[filename] — [one line: why it is in this commit]`

Flag anything in git status that Claude Code did not touch. Do not silently include it. Pete decides.

Wait for Pete to confirm before staging.

Once confirmed:
- Stage exactly the confirmed files by name — not `git add -A`
- Commit: `git commit -m "[scope]: [what changed] — MOB v[version]"`
- Push: `git push origin main`
- Confirm push succeeded

---

## During-Session Rules

### File Change Protocol
Before touching any file:
- State what you are changing and why
- Confirm the change is targeted — do not refactor adjacent code

After every change:
- Report exactly what changed: file, what was before, what is after
- All writes use Python patch scripts with `--dry-run` before `--write`
- `pathlib.Path.write_text(content, encoding='utf-8')` only

### Architectural Decisions
Any decision affecting multiple files, data contracts, or integration behavior routes through Gemini before execution. Pete decides. Claude Code executes after confirmation.

### Retrieval Gap Handling
If palace search returns empty or wrong results:
1. Retry with 2–3 alternative keyword combinations
2. If still empty, say so explicitly — do not proceed on assumption
3. Ask Pete to paste the relevant context if retrieval fails

Never hallucinate content that should come from the palace or the MOB. If you don't have it, say so.

### Engine Rules
- All engine writes use Python patch scripts with dry-run verification
- `engine/data/states.py` is the authoritative state registry — 47 states
- `engine/data/questions.py` registry is intentionally empty — question population is a separate deliverable
- Do not adjust calibration target values speculatively — data-first calibration principle applies

---

## Standing Rules

- Write code that works the first time. If uncertain, say so before writing.
- Make targeted changes. Fix what was asked. Do not refactor adjacent code.
- Before touching any file, state what you are changing and why.
- If a fix does not work, diagnose before acting again.
- No semicolons in any string or copy.
- No coined terms requiring a glossary in any output string.
- Pete confirms everything. No recommendation from any AI is a decision until Pete confirms it.

---

## Key References

| Item | Value |
|---|---|
| MOB file | `tools/_mob_v33_textonly.txt` |
| MemPalace wing | `prv3` |
| MemPalace path | `C:\Users\rizzo\PRV3` |
| Engine state count | 47 (locked) |
| Test suite minimum (Phase 1) | 141 profiles across 47 states |
| Checkpoints | Q11 · Q19 · Q27 |
| Shannon Entropy max (47 states) | 5.55 bits |
| Gemini handoff template | `prompts/gemini-handoff.md` |

---

## MemPalace Note
`mempalace_status`, `mempalace_diary_read`, `mempalace_diary_write`, and `mempalace_search` are available as MCP tools in terminal Claude Code sessions only. Not available in claude.ai web sessions.

`/compact` disconnects the MCP server. Diary write and mine must happen BEFORE any `/compact`. If MCP is unavailable at closeout, skip Steps 1–2 and note the gap in the MOB session log.

---

*PRV3 Principal Brief governs. Pete confirms everything.*
