# PRV3 — Engage Protocol for Claude.ai Sessions

This document governs how Claude.ai sessions engage with PRV3 work. Read it in full at the
start of every session. It is the Claude.ai equivalent of CLAUDE.md — adapted for the
constraints of a web session (no terminal, no file system, no `gh` commands).

PRV3 Principal Brief governs. Pete decides everything.

---

## Step 1 — Read the MOB

Read `tools/_mob.txt` from project knowledge before doing anything else. If it is not
available, ask Pete to paste it. Do not start work without it.

The MOB is the institutional memory layer for PRV3. It records locked decisions, workstream
status, and the session log. Everything in the MOB has been decided by Pete. Do not propose
changes to locked decisions without surfacing them to Pete first.

---

## Step 2 — Read the Principal Brief

Read `documents/PRV3-Principal-Brief.docx` from project knowledge. If the brief is not
available, ask Pete which section is relevant to today's session.

The Principal Brief governs. The MOB supplements it. When they conflict, ask Pete.

---

## Step 2a — Check Research Integration Status

Claude.ai cannot run `gh` commands or read the live repo state directly. Use one of these
two methods to check:

**Method A (preferred):** Ask Pete directly — "Are there any open research-refresh PRs, or any
pending-integration entries with status 'proposed' that haven't been applied yet?"

**Method B (if Pete has uploaded the file):** Search project knowledge for
`pending-integration.json` and look for any entry where `"status": "proposed"`. Any such
entry represents a merged PR whose proposed content edit has not yet been applied to the
live files.

**If Pete confirms open entries exist:** Treat resolving them — drafting the actual content
edit, or confirming a rejection — as a candidate top-priority item for this session, alongside
whatever Pete originally opened the session to do. Do not silently proceed past an unintegrated
finding.

**Important asymmetry:** Claude Code's check is authoritative. It can actually run
`gh pr list --label research-refresh --state open` and read the live ledger. Claude.ai's check
depends on Pete relaying the answer or the ledger file being in project knowledge. This is a
known limitation of the Claude.ai surface — do not imply the check is equivalent. If in doubt,
ask Pete whether Claude Code has already confirmed the ledger state this session.

---

## Step 3 — Report Session Status

Before beginning any work, report:

- MOB version and current workstream status
- Any open items from the MOB that Pete may want to address
- Any pending research integration flagged (Step 2a)
- What Pete wants to work on today, confirmed in your own words

Wait for Pete to confirm before proceeding.

---

## Standing Rules

### Voice and Copy

- No semicolons in any string or copy.
- No coined terms requiring a glossary in any output string.
- Brand voice: 40% blunt, 60% servant leader. Direct and warm.
- Shadow model: no personal name, no affiliated entity reference in any copy that will appear
  on the commercial surface or in client-facing materials.

### Architectural Decisions

Any decision affecting multiple files, data contracts, or integration behavior routes through
Gemini before Claude Code executes. Pete decides. Propose; do not unilaterally commit.

When a handoff to Gemini or Claude Code is needed, write a self-contained brief that does not
require Gemini or Claude Code to read this conversation. Include: what was decided, what files
are affected, what the exact change is, and what acceptance criteria to verify.

### Retrieval and Gaps

If project knowledge does not contain a file you need, say so explicitly. Do not reconstruct
from memory — PRV3 architecture and copy decisions are in the MOB and the Principal Brief, not
in your training data.

Never hallucinate content that should come from the MOB. If you do not have it, say so and ask
Pete to paste the relevant section.

### Engine Rules

- Do not propose changes to the scoring engine's calibration target values without data.
  Data-first calibration principle applies.
- `engine/data/states.py` is the authoritative state registry — 47 states, locked.
- Do not add or remove states without Pete's explicit decision.

---

## Research Refresh Integration Workflow

When a `pending-integration.json` entry needs to be resolved:

1. Read the refresh report referenced by `refresh_report` (Pete pastes the relevant section
   if the file is not in project knowledge).
2. For each NEEDS REVIEW finding, evaluate the proposed edit and recommend: apply as proposed,
   apply with modifications, or reject with documented reason.
3. Write a Claude Code handoff brief for any edit that should be applied — include the exact
   before/after text and which file(s) to update.
4. After Claude Code applies the edit and Pete confirms the commit hash, update
   `pending-integration.json`: set `status` to `applied` and record the `applied_commit`.
5. If Pete decides not to apply a finding, set `status` to `rejected` and record
   `rejected_reason` so the decision is not lost.

The `pending-integration.json` ledger is the single source of truth for this lifecycle. Do not
re-derive pending state from git history or PR status — read the ledger directly.

---

## Key References

| Item | Value |
|---|---|
| MOB file | `tools/_mob.txt` |
| MemPalace wing | `prv3` |
| Engine state count | 47 (locked) |
| Research refresh ledger | `research/refresh-log/pending-integration.json` |
| Refresh claims registry | `research/refresh-log/tracked-claims.json` |
| Refresh reports directory | `research/refresh-log/` |
| Gemini handoff template | `prompts/gemini-handoff.md` |

---

*PRV3 Principal Brief governs. Pete confirms everything.*
