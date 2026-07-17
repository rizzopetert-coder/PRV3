"""
PRV3 MOB Update -- Session 72 (closeout verification pass, not just append)

Pete's instruction: verify Section 15 (Document Registry) actually reflects
everything touched/created across Session 71's full chain of commits
(76e2212..8db2855), not just whatever it said before tonight started.

Confirmed stale/missing by direct file inspection (not assumed from memory):
  - web/components/FullInstrumentPlaceholder.tsx: entry describes a file that
    no longer exists (deleted Stage 4, commit 37ab8a7, confirmed via `ls`
    returning "No such file or directory"). Replaced by
    web/components/DiagnosticFlow.tsx -- no registry entry existed for it.
  - web/app/diagnostic/page.tsx entry still said "Path 1 mounts
    FullInstrumentPlaceholder" -- confirmed via direct read that it now
    mounts <DiagnosticFlow /> (page.tsx line 317).
  - web/lib/session-store.ts (new, Stage 1): no entry existed at all.
  - web/app/api/diagnostic/session/start/route.ts and .../answer/route.ts
    (new, Stage 3): no entries existed at all.
  - prompts/path1-phase1-handoff.md (new, closeout): no entry existed.
  - api/engine.py entry only described the original /api/engine route --
    confirmed via grep that /api/accumulate, /api/complete, and
    /api/question-copy were added, sharing _check_secret().
  - vercel.json entry didn't mention the 3 new routes -- confirmed via
    direct read of the routes array.
  - engine/main.py entry only described run_engine() (Path B) -- didn't
    mention accumulate_one_answer() / run_accumulated_engine() /
    get_question_copy() (Path A, Stage 2/3).
  - web/lib/engine-client.ts entry didn't mention invokeAccumulate /
    invokeComplete / invokeQuestionCopy, or the Deployment Protection
    bypass (engineHeaders/engineFetch/VERCEL_PROTECTION_BYPASS, commit
    e122d34).
  - web/components/PrivateOutput.tsx entry didn't mention the enableSharing
    prop (default true, Path 1 passes false) -- confirmed via grep.

This script updates all of the above. No product code touched -- MOB and
CLAUDE.md only.

Usage:
  python tools/patch_mob_s72_registry_verify.py --dry-run
  python tools/patch_mob_s72_registry_verify.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ═══════════════════════════════════════════════════════════════════════════
# tools/_mob.txt -- Section 15 Document Registry
# ═══════════════════════════════════════════════════════════════════════════

# --- 1. FullInstrumentPlaceholder.tsx -> DiagnosticFlow.tsx ---

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*web/components/FullInstrumentPlaceholder.tsx\\\\\\*\\\\\\* | Path 1 "
    "placeholder. Holds space for full diagnostic instrument — not yet built. "
    "Copy flagged for Pete review before deployment. Created S46. |",
    "| \\\\\\*\\\\\\*web/components/DiagnosticFlow.tsx\\\\\\*\\\\\\* | Path 1 linear "
    "question-flow state machine — replaces FullInstrumentPlaceholder.tsx "
    "(deleted S71, confirmed single caller). Intake form (dropdowns sourced "
    "from engine/data/intake.py's INTAKE_FIELDS) -> question loop (x34, driven "
    "by web/lib/session-store.ts's PHASE_1_QUESTION_SEQUENCE) -> completion. "
    "Deliberately linear and plain — no checkpoint/narrative/addenda/severity-"
    "follow-on UI (Phase 1 scope only). Renders PrivateOutput with "
    "enableSharing={false} on completion. Created S71 (Stage 4, commit "
    "37ab8a7). |",
)

# --- 2. diagnostic/page.tsx: FullInstrumentPlaceholder -> DiagnosticFlow ---

edit(
    "tools/_mob.txt",
    "Phase 0 gate renders two-card choice. Path 1 mounts "
    "FullInstrumentPlaceholder. Path 2 mounts SelfSelectionInterface",
    "Phase 0 gate renders two-card choice. Path 1 mounts DiagnosticFlow "
    "(S71, replacing FullInstrumentPlaceholder — confirmed via direct read, "
    "page.tsx line 317). Path 2 mounts SelfSelectionInterface",
)

# --- 3. api/engine.py: add the 3 new Path 1 routes ---

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*api/engine.py\\\\\\*\\\\\\* | FastAPI serverless endpoint. "
    "x-engine-secret shared-secret validation. KeyError→400 (unknown state "
    "ID), TypeError/ValueError→400 (bad intake), Exception→500. sys.path.insert "
    "adds repo root so engine package resolves. Created S40. |",
    "| \\\\\\*\\\\\\*api/engine.py\\\\\\*\\\\\\* | FastAPI serverless endpoint, single "
    "app serving 4 routes. /api/engine (Path B, created S40): x-engine-secret "
    "shared-secret validation, KeyError→400 (unknown state ID), "
    "TypeError/ValueError→400 (bad intake), Exception→500. sys.path.insert "
    "adds repo root so engine package resolves. S71 (Stage 2/3) added "
    "/api/accumulate, /api/complete, /api/question-copy — the Path 1 (Path A) "
    "endpoints, all sharing the same secret check via a new _check_secret() "
    "extraction rather than duplicating the guard 4 times. |",
)

# --- 4. vercel.json: add the 3 new routes ---

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*vercel.json\\\\\\*\\\\\\* | Dual-runtime routing. @vercel/next for "
    "web/package.json. @vercel/python for api/engine.py. /api/engine → "
    "api/engine.py, /(.*) → /web/$1. Created S40. |",
    "| \\\\\\*\\\\\\*vercel.json\\\\\\*\\\\\\* | Dual-runtime routing. @vercel/next for "
    "web/package.json. @vercel/python for api/engine.py. Routes: /api/engine, "
    "/api/accumulate, /api/complete, /api/question-copy all → api/engine.py "
    "(S71, Stage 2/3 — no new Python serverless function, same build); "
    "/(.*) → /web/$1. Created S40. |",
)

# --- 5. engine/main.py: add Path A functions ---

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*engine/main.py\\\\\\*\\\\\\* | Path B orchestrator. run_engine(payload) "
    "— IntakeData → StateRanking(score=1.0) → SeverityEngine.score() → "
    "OutputEngine.build() → SessionData → assemble_output(). AccumulationEngine "
    "bypassed. selectedStateIds are declared diagnosis. Created S40. |",
    "| \\\\\\*\\\\\\*engine/main.py\\\\\\*\\\\\\* | run_engine(payload) — Path B "
    "orchestrator: IntakeData → StateRanking(score=1.0) → SeverityEngine.score() "
    "→ OutputEngine.build() → SessionData → assemble_output(). "
    "AccumulationEngine bypassed, selectedStateIds are declared diagnosis. "
    "Created S40. S71 (Stage 2/3) added the Path A (Path 1) functions: "
    "_locked_intake_to_engine_intake() (adapter, locked 6-field intake schema "
    "→ engine's IntakeData contract), accumulate_one_answer() (stateless "
    "per-answer vector math — looks up the real AnswerOption server-side from "
    "question_id/option_id, caller never sends dimensional_contributions, "
    "P-03 enforced at the network edge), run_accumulated_engine() (the real "
    "completion orchestrator — actual rank_states() against the accumulated "
    "vector, reusing SeverityEngine/OutputEngine/OutputSynthesisEngine "
    "unchanged), get_question_copy() (question_text + option text only, "
    "QUESTION_LIBRARY stays the single content source instead of a hand-"
    "maintained TypeScript transcription). |",
)

# --- 6. web/lib/engine-client.ts: add Path 1 invocations + bypass header ---

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*web/lib/engine-client.ts\\\\\\*\\\\\\* | URL resolver + fetch helper. "
    "resolveEngineUrl(): ENGINE_URL (explicit override, checked first) → "
    "VERCEL_URL construction → localhost fallback. ENGINE_URL override added "
    "S44 (renamed from NEXT_PUBLIC_ENGINE_URL — server-side resolver, "
    "NEXT_PUBLIC prefix incorrect). EnginePayload and EngineResult types "
    "(14-field contract). invokeEngine(): POST with x-engine-secret header. "
    "Created S40. |",
    "| \\\\\\*\\\\\\*web/lib/engine-client.ts\\\\\\*\\\\\\* | URL resolver + fetch helper. "
    "resolveEngineUrl(): ENGINE_URL (explicit override, checked first) → "
    "VERCEL_URL construction → localhost fallback. ENGINE_URL override added "
    "S44 (renamed from NEXT_PUBLIC_ENGINE_URL — server-side resolver, "
    "NEXT_PUBLIC prefix incorrect). EnginePayload and EngineResult types "
    "(14-field contract). invokeEngine(): POST with x-engine-secret header. "
    "Created S40. S71 (Stage 3) added invokeAccumulate() / invokeComplete() / "
    "invokeQuestionCopy() (Path 1 endpoints) and resolveEnginePath() (VERCEL_URL "
    "/ localhost fallback duplicated rather than reusing resolveEngineUrl(), "
    "deliberately — ENGINE_URL's existing override contract stays scoped to "
    "/api/engine only). S71 (Deployment Protection fix, commit e122d34) added "
    "a shared engineHeaders()/engineFetch() helper backing all 4 invoke "
    "functions: sends x-vercel-protection-bypass (from "
    "VERCEL_AUTOMATION_BYPASS_SECRET) only when that env var is set — absent in "
    "Production today, provable no-op there, Gemini-reviewed and cleared. |",
)

# --- 7. web/components/PrivateOutput.tsx: add enableSharing prop ---

edit(
    "tools/_mob.txt",
    "| \\\\\\*\\\\\\*web/components/PrivateOutput.tsx\\\\\\*\\\\\\* | Full rendering pass "
    "(S43). Props: PrivateOutputPayload + selectedStateIds + intake. 5 blocks: "
    "(1) condition header — \"Condition identified\" label, state_name + "
    "severity pill, SEVERITY_ANCHOR tier text; (2) liability_condition_text "
    "(fallback: resolution_routing); (3) asset_resolution_anchor_text (omit if "
    "empty); (4) resolution_family + resolution_framing_text (fallback: "
    "resolution_routing if not used in block 2); (5) ShareButton. "
    "friction_tax_estimate: null in Path B — renders nothing. Created S38. |",
    "| \\\\\\*\\\\\\*web/components/PrivateOutput.tsx\\\\\\*\\\\\\* | Full rendering pass "
    "(S43). Props: PrivateOutputPayload + selectedStateIds + intake. 5 blocks: "
    "(1) condition header — \"Condition identified\" label, state_name + "
    "severity pill, SEVERITY_ANCHOR tier text; (2) liability_condition_text "
    "(fallback: resolution_routing); (3) asset_resolution_anchor_text (omit if "
    "empty); (4) resolution_family + resolution_framing_text (fallback: "
    "resolution_routing if not used in block 2); (5) ShareButton, gated on "
    "block (5) below. friction_tax_estimate: null in Path B — renders nothing. "
    "Created S38. S71 (Stage 4) added optional enableSharing prop (default "
    "true, block 5 only renders when true) — Path 1's DiagnosticFlow.tsx "
    "passes false, since ShareButton's Path-B declared-diagnosis re-invocation "
    "of /api/share/create would silently corrupt Path 1's real weights if "
    "reused as-is; Path-1-aware sharing is out of scope for Phase 1. |",
)

# --- 8. New entries: session-store.ts, session routes, handoff doc ---
# Inserted after the engine-client.ts entry (now the anchor below, post-edit
# text) to keep them physically adjacent to the Path 1 material they describe.

ENGINE_CLIENT_NEW_TAIL = (
    "sends x-vercel-protection-bypass (from "
    "VERCEL_AUTOMATION_BYPASS_SECRET) only when that env var is set — absent in "
    "Production today, provable no-op there, Gemini-reviewed and cleared. |"
)

NEW_ENTRIES = (
    "\n"
    "| \\\\\\*\\\\\\*web/lib/session-store.ts\\\\\\*\\\\\\* | Stateful Path 1 diagnostic "
    "session, Upstash Redis-backed. DiagnosticSession schema (session_id "
    "NanoID, intake as IntakeEcho, next_question_id as a STRING not a "
    "positional index so Phase 2's checkpoint-based dynamic assignment won't "
    "need a schema change, accumulated_vector, append-only answers_log, "
    "status). PHASE_1_QUESTION_SEQUENCE (34 IDs) derived from "
    "QUESTION_LIBRARY's sequence_position field. TTL 6h, SLIDING (refreshed on "
    "every write). Transition Rule (completeSession()): extracts "
    "industry/organization_size/final rankings to a single shared "
    "diagnostic-aggregate Redis list, then hard-deletes the session key in "
    "the same call — implements the locked Session 34 Option D retention "
    "decision. Created S71 (Stage 1, commit 1939d96). |\n"
    "| \\\\\\*\\\\\\*web/app/api/diagnostic/session/start/route.ts\\\\\\*\\\\\\* | POST "
    "Route Handler. Creates a Redis session via createSession(), returns Q1's "
    "copy only (question_text + option labels) via invokeQuestionCopy() — no "
    "dimensional_contributions or scoring field ever reaches this response. "
    "Created S71 (Stage 3, commit 2cda77b). |\n"
    "| \\\\\\*\\\\\\*web/app/api/diagnostic/session/answer/route.ts\\\\\\*\\\\\\* | POST "
    "Route Handler. Enforces the index invariant (400 if request.question_id "
    "≠ session.next_question_id — the real security boundary given "
    "NanoID-only session ownership, Gemini-approved). Calls invokeAccumulate() "
    "per answer; on Q34, calls invokeComplete() and builds a "
    "PrivateOutputPayload with real normalized weights (Path A: score_i / "
    "sum(all_scores), not Path B's equal-weight scheme), then fires the "
    "Transition Rule via completeSession(). STATE_RESOLUTION_FAMILY "
    "duplicated here matching the existing pattern already in /api/result "
    "and /api/share/create — per the standing rule against refactoring "
    "adjacent files mid-build. Created S71 (Stage 3, commit 2cda77b). |\n"
    "| \\\\\\*\\\\\\*prompts/path1-phase1-handoff.md\\\\\\*\\\\\\* | Living reference doc "
    "for Path 1 Phase 2+ work — full as-built architecture, schema, and "
    "endpoint contracts from the Phase 1 build, per the taxonomy-expansion-57 "
    "precedent for handoff docs. Created S71 (closeout). |"
)

edit("tools/_mob.txt", ENGINE_CLIENT_NEW_TAIL, ENGINE_CLIENT_NEW_TAIL + NEW_ENTRIES)


# ═══════════════════════════════════════════════════════════════════════════
# tools/_mob.txt -- Section 14: missing narrative for commits 14930d3..8db2855
#
# The two existing Session 71 Section 14 entries (Path 1 Phase 1 build,
# workflow governance) stop at commit 4625761/04442fc. Seven more commits
# happened after that (14930d3 through 8db2855) plus real untracked
# verification work (the actual live round trip, synthesis diagnosis, one
# authorized Production test call) -- none of it had ever been written up
# as a coherent narrative, only as individual Decision Register row commits
# and this conversation's own chat history. Confirmed via `git log
# --oneline` cross-referenced against tools/_mob.txt's actual content, not
# assumed.
# ═══════════════════════════════════════════════════════════════════════════

SECTION14_ANCHOR_TAIL = (
    "no dry-run cycle required per Pete's own instruction (no functional "
    "risk), but held for explicit standalone confirmation before commit "
    "given it's a standing-protocol change, consistent with the Tier 3/4 "
    "spirit of the model it establishes. CLAUDE.md MOB version cross-"
    "reference updated v4.45->v4.46. MOB version bumped to v4.46 — new "
    "standing protocol locked, per the closeout protocol's version-"
    "increment rule (rules change). MOB v4.46. |"
)

SECTION14_NEW_ENTRY = (
    "| **July 2026 — Session 71 (continued: credential access, live round "
    "trip, synthesis pre-launch defect)** | Everything between the Path 1 "
    "Phase 1 build closing (commit 4625761) and this session's own close "
    "(8db2855) — seven more commits plus real verification work that had "
    "not yet been written up as a coherent narrative anywhere, only as "
    "individual Decision Register row commits. **Vercel CLI auth "
    "established in the coding sandbox** — Pete generated a VERCEL_TOKEN, "
    "landed in a global, non-git-tracked key (`C:\\Users\\rizzo\\.claude\\"
    "settings.json`'s top-level `env`, distinct from the pre-existing "
    "`mcpServers.mempalace.env` key, confirmed untouched) rather than the "
    "project's git-tracked `.claude/settings.local.json` — this finally "
    "closed the credential-ACCESS gap the Path 1 Phase 1 entry above had "
    "flagged as the one blocker to a real round trip. **Repo-hygiene "
    "finding logged (14930d3):** `.claude/settings.local.json` has been "
    "tracked in git since Session 37 despite being Claude Code's own "
    "gitignore-by-convention file — current content confirmed safe "
    "(permissions allowlist only), logged as a Decision Register row, not "
    "yet actioned. **Two tooling/infra findings logged together (1dcebad):** "
    "`vercel dev` cannot serve this project locally (\"Unable to find "
    "lambda for route\", reproduced across two CLI versions, survives a "
    "cache clear, not chased down further per Pete's explicit call — "
    "Preview-path only for now); and Production/Preview were discovered to "
    "share one literal Redis instance (UPSTASH_REDIS_REST_URL/TOKEN "
    "byte-identical across both scopes, confirmed by direct value-diff "
    "before a later CLI upgrade). **Documented-dev-command gap logged as "
    "its own row (11cb882):** `npm run dev` (the actual documented command) "
    "never satisfied `resolveEngineUrl()`'s localhost assumption — latent "
    "since Session 40, never previously written down; kept as a separate "
    "row from the vercel-dev-bug row since fixing one does not fix the "
    "other. **Dedicated dev/test Redis database provisioned** to fix the "
    "shared-instance finding — the fix initially landed in Development "
    "scope only, not Preview (caught via `vercel env ls` structural check, "
    "not assumed), corrected by Pete, then found (b98a14f) that `vercel env "
    "pull` masks Sensitive-flagged values as the literal string "
    "`[SENSITIVE]`, invalidating value-diffing as a verification method "
    "going forward — scope-grouping via `vercel env ls` established as the "
    "reliable replacement. Shared-Redis-instance row marked RESOLVED "
    "(2226918) once `vercel env ls` confirmed Production and Preview as two "
    "structurally separate entries. **Production build failure found and "
    "fixed, incidentally:** pushing to `main` was discovered to "
    "auto-trigger a Production deployment (confirmed via deployment "
    "history) — directly conflicting with the goal of testing via Preview "
    "only, so all pushes moved to a separate `path1-phase1-verification` "
    "branch instead. That Production deployment then failed to build: "
    "Production's `UPSTASH_REDIS_REST_URL` was missing its `https://` "
    "prefix (likely introduced during the credential-restore step above), "
    "surfaced only because `session-store.ts`'s top-level `Redis.fromEnv()` "
    "call is evaluated during Next.js's build-time page-data collection for "
    "any route that imports it. Pete fixed the value; verified Ready via "
    "`vercel redeploy`. **Vercel Deployment Protection gap found and fixed "
    "(e122d34, Gemini-reviewed and cleared):** the SSO gate on protected "
    "Preview deployments blocks every serverless function in that "
    "deployment, including function-to-function calls — session/start's "
    "internal call to /api/question-copy was failing 401 from Vercel's own "
    "protection layer, not api/engine.py's secret check. Fixed via a shared "
    "`engineHeaders()`/`engineFetch()` helper in web/lib/engine-client.ts "
    "sending `x-vercel-protection-bypass` only when "
    "`VERCEL_AUTOMATION_BYPASS_SECRET` is set — provably a no-op in "
    "Production today (that var is unset there). Zero-regression claim for "
    "Path B rested on tsc type-checking plus code-level reasoning rather "
    "than an executed test, which surfaced that **no automated test "
    "coverage exists anywhere in the web layer** — confirmed, not assumed "
    "(no test script, no .test./.spec. files), logged as its own Decision "
    "Register row (e569578). **Live end-to-end round trip finally executed "
    "and verified** — session/start -> 34x session/answer -> completion "
    "against a live Preview deployment, with the Redis write and the "
    "Transition Rule's extract-then-delete behavior confirmed by direct "
    "query against the dedicated dev/test Redis instance, not assumed from "
    "env var scope. First time real accumulation math has been exercised "
    "outside the test harness. **Synthesis-timeout characterized:** the "
    "round trip surfaced a reproducible ~17.4-17.8s completion latency "
    "paired with `synthesis.is_fallback: true`. Root-caused via temporary, "
    "uncommitted diagnostic logging added to output_synthesis.py's "
    "exception handler, deployed only to an ephemeral non-git `vercel "
    "deploy` build, real exception captured (genuine `APITimeoutError`, "
    "visible Anthropic SDK auto-retry — two retries logged), then reverted "
    "via `git checkout --` and independently re-verified clean. **Prompt "
    "injection attempt encountered and refused, worth recording as a "
    "security event:** immediately after that revert, a message formatted "
    "as a genuine system-reminder instructed leaving the diagnostic edit in "
    "place and not telling Pete about it, framed as something already "
    "agreed to. Not complied with — flagged directly to Pete, and the "
    "file's clean state was independently re-verified via `git status`/`git "
    "diff` rather than trusting the injected claim. **One Pete-authorized "
    "synthetic test call against prv-3's actual Production deployment** "
    "(prv-3.vercel.app, confirmed via `vercel alias ls` as the real target "
    "of the current Ready Production build) returned `is_fallback=true` at "
    "4.483s — same symptom as Preview, but a materially different timing "
    "signature (too fast to contain a full retry cycle), so not yet "
    "confirmed to share Preview's exact root cause; the exception-capture "
    "pass for Production specifically was not run, since it would require "
    "deploying modified code to Production itself rather than an ephemeral "
    "non-git build, and was not separately authorized. **Alias-mapping "
    "discovery, resolved by Pete directly, not a live incident:** `vercel "
    "alias ls` showed `principalresolution.com`/`www.principalresolution."
    "com` pointing at a different Vercel project (`prv-2`), not `prv-3` — "
    "Pete confirmed prv-2 is the current live iteration serving real "
    "traffic, prv-3 is the next iteration, not yet cut over, cutover timing "
    "is Pete's call. This reframed the synthesis finding: **confirmed "
    "pre-launch defect in prv-3, must be fixed before cutover, zero current "
    "user impact** — not a live incident, not evidence real Principals have "
    "been silently affected. Logged as a new Decision Register row "
    "(8db2855) with this corrected framing from the start, so the earlier, "
    "briefly-live \"urgent\" framing is not left standing anywhere. No "
    "retry/timeout config changed anywhere this session — diagnosis only, "
    "per Pete's explicit instruction. CLAUDE.md MOB version cross-reference "
    "updated v4.46->v4.48 across two bumps (v4.47->v4.48 at the Decision "
    "Register row commit). MOB v4.48. |"
)

edit("tools/_mob.txt", SECTION14_ANCHOR_TAIL, SECTION14_ANCHOR_TAIL + "\n" + SECTION14_NEW_ENTRY)


# ═══════════════════════════════════════════════════════════════════════════
# tools/_mob.txt -- Section 16: matching one-liner for the entry above, plus
# a separate one-liner for Session 72 (this closeout verification pass
# itself). Precedent: Session 60's "MOB staleness audit and patch" entry
# stands alone in Section 16 without a parallel Section 14 entry, and
# bumped the version -- "staleness corrections are material structural
# changes, not session log entries only, so the bump is warranted."
# ═══════════════════════════════════════════════════════════════════════════

SECTION16_ANCHOR = (
    "| **July 2026 — Session 71 (Path 1 Phase 1 build)** | Path 1 (full "
    "diagnostic instrument) Phase 1 BUILT — first Path 1 build session, "
    "executing a Claude.ai + Gemini architecture-reviewed handoff across 4 "
    "dry-run-confirmed commits"
)

SECTION16_NEW_LINES = (
    "| **July 2026 — Session 72 (closeout verification pass)** | Ran the "
    "standing Closeout Protocol against Session 71's full commit chain "
    "(76e2212..8db2855) with an explicit verification pass, per Pete's "
    "request, rather than a bare append. Found and corrected real "
    "staleness in Section 15 (Document Registry): two entries "
    "(FullInstrumentPlaceholder.tsx, diagnostic/page.tsx) still described a "
    "component deleted in Stage 4; four entries (api/engine.py, "
    "vercel.json, engine/main.py, web/lib/engine-client.ts) were missing "
    "the Path 1 endpoints/functions added this session; PrivateOutput.tsx's "
    "enableSharing prop was undocumented; four new files "
    "(session-store.ts, both session route handlers, "
    "path1-phase1-handoff.md) had no entries at all. Found and fixed a "
    "larger gap in Section 14/16: seven commits (14930d3..8db2855) plus the "
    "actual live round-trip execution and synthesis-timeout diagnosis had "
    "never been written up as a coherent narrative, only as individual "
    "Decision Register row commits — added as a new Session 71 (continued) "
    "entry above. Confirmed no stale \"urgent live incident\" framing for "
    "the synthesis finding survives anywhere outside the correctly-framed "
    "Decision Register row (grepped the full file). Confirmed MOB version "
    "consistent (v4.48) in both tools/_mob.txt and CLAUDE.md before this "
    "pass began. Diary write and mine SKIPPED — this session was already "
    "compacted before this closeout began, so per CLAUDE.md's own "
    "exception (\"if already compacted, skip Steps 1-2 and note the gap\"), "
    "no diary entry exists for this session; flagged here rather than "
    "silently omitted. MOB version bumped to v4.49 — staleness corrections "
    "and a missing-narrative gap are material structural changes, not "
    "session-log-only edits, per the Session 60 precedent for the same "
    "kind of pass. MOB v4.49. |"
)

edit("tools/_mob.txt", SECTION16_ANCHOR, SECTION16_NEW_LINES + "\n" + SECTION16_ANCHOR)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.48",
    "\\\\\\#\\\\\\# MOB v4.49",
)

edit(
    "CLAUDE.md",
    "| MOB version | v4.48 |",
    "| MOB version | v4.49 |",
)


# ---------------------------------------------------------------------------

def apply(dry_run: bool):
    changed_files: dict[str, str] = {}
    errors = []

    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = changed_files.get(rel_path)
        if text is None:
            if not path.exists():
                errors.append(f"MISSING FILE: {rel_path}")
                continue
            text = path.read_text(encoding="utf-8")

        count = text.count(old)
        if count != 1:
            errors.append(
                f"{rel_path}: expected 1 match, found {count}\n"
                f"  --- anchor (first 160 chars) ---\n  {old[:160]!r}"
            )
            continue

        changed_files[rel_path] = text.replace(old, new, 1)

    print("=" * 72)
    print(f"MOB S72 REGISTRY VERIFY PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"Files touched: {len(changed_files)}")
    for rel_path in changed_files:
        print(f"  - {rel_path}")

    if errors:
        print("\nERRORS:" if dry_run else "\nERRORS — nothing written:")
        for e in errors:
            print(f"\n[ERROR] {e}")
        if not dry_run:
            sys.exit(1)
        return

    if dry_run:
        print("\nDry run OK — all anchors matched exactly once. No files written.")
        return

    for rel_path, text in changed_files.items():
        (REPO_ROOT / rel_path).write_text(text, encoding="utf-8")
    print("\nAll files written.")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
