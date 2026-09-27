"""
Final closeout for the hr-dx polish arc (Pete, 2026-09-26/27). MOB v4.326 -> v4.327.

  1. CLAUDE.md: Quarterly Step-Back "Next due" corrected from September 19 to
     2026-10-03 (Section 13b's date), and the MOB version cross-reference.
  2. Section 16: backfilled entry for the 2026-09-24/25 pre-session hr-dx work,
     inserted chronologically (immediately before the 2026-09-26 closeout).
     Reconstructed from git log + commit bodies, the local main reflog, and
     `vercel ls` Production deployments filtered by commit. Marked as such,
     with its unfillable gaps listed.
  3. Section 13b: every item closed by this session and the polish batch is
     closed in place (same convention as the aggregate-cleanup bullet). The
     driver answer-steering item stays open. New: separate-Preview-database
     backlog item (deferred by Pete), engine-preview upkeep note, untracked
     uv.lock note. Files-to-attach and Last-updated lines refreshed.
  4. Section 16: this session's closeout entry, appended at the end.
  5. prompts/session-handoff-v4.327.md, derived from (4).

Anchors: whole-line replacements are keyed on a line prefix that must match
exactly once at a line start. Insertions are keyed on an exact unique line.
MOB and CLAUDE.md are CRLF (MOB with BOM), read and written as bytes-decoded
text with newline='' so nothing else in either file changes.

Usage:
    python tools/patch_mob_session_closeout_20260927.py --dry-run
    python tools/patch_mob_session_closeout_20260927.py --write
"""
import argparse
import pathlib
import sys

MOB = pathlib.Path('tools/_mob.txt')
CLAUDE = pathlib.Path('CLAUDE.md')
HANDOFF = pathlib.Path('prompts/session-handoff-v4.327.md')
NL = '\r\n'

# ── 13b whole-line replacements: (line prefix, new full line) ──────────────
LINE_REPLACEMENTS = [
    ('- `tools/diagnostic_fast_forward.py` -- rework-or-retire still undecided',
     '- CLOSED 2026-09-26/27 -- `tools/diagnostic_fast_forward.py` reworked into the permanent session '
     'driver (`e836d79`): current intake (`org_type`, `significant_events`), the narrative step, '
     '`--brand`, `--narrative-text`, `--json-out`, a Production guard (`--allow-production`), and the '
     '`x-prv3-test-run` tag on every request. Its answer-steering gap is tracked as its own open item, '
     'next bullet.'),
    ('  - hr-dx "About this report" drawer copy -- currently the generic fallback',
     '  - CLOSED 2026-09-26/27 -- hr-dx drawer copy shipped (`d60107c`): four family-specific texts '
     '(structure, capability, leadership, urgent) selected by a neutral `hr_pathway` payload field, plus the '
     'Executive Advisory AI-context string simplified to plain "HR Consulting". Live-confirmed in Production '
     'for urgent and for the no-routing generic drawer. Structure, capability, leadership, and the Executive '
     'Advisory context are verified by tests only, see the driver answer-steering item.'),
    ('  - Copy residual, PR brand:',
     '  - CLOSED 2026-09-26/27 -- PR compound-family grammar (`ce9ad29`): the synthesis prompt renders '
     'compounds as "A with B", live Production output read "People Tactics & Strategy with First Call is '
     'built for...".'),
    ('  - Copy residual, both brands:',
     '  - CLOSED 2026-09-26/27 -- narrative-question em-dashes (`b675d9f`): a punctuation rule in the '
     'question-generation prompt plus a deterministic guard (`_enforce_house_punctuation`) that rewrites any '
     'em-dash, spaced en-dash, double hyphen, or semicolon to a comma. Every narrative question observed '
     'since was clean.'),
    ('- Section 16 logging gap, 2026-09-24/25:',
     '- CLOSED 2026-09-26/27 -- Section 16 logging gap for 2026-09-24/25: backfilled as a clearly marked '
     'reconstructed entry, placed chronologically before the 2026-09-26 closeout, built from git history, '
     'the `main` reflog, and Vercel deployment records. What it could not recover is listed in the entry.'),
    ('- `prv-3` general-Preview `ENGINE_BASE_URL` still holds',
     '- CLOSED 2026-09-26/27 -- `prv-3` `ENGINE_BASE_URL`, both scopes: Production = '
     '`https://prv3-engine-peter-rizzos-projects.vercel.app` (stable prod alias). General Preview = '
     '`https://prv3-engine-git-engine-preview-peter-rizzos-projects.vercel.app`, the git alias of the new '
     'long-lived `engine-preview` branch (Pete chose Preview-to-Preview over Previews hitting Production). '
     'The branch-scoped Preview row is gone with its branch.'),
    ('- `.claude/launch.json` carries an uncommitted',
     '- CLOSED 2026-09-26/27 -- `.claude/launch.json` now tracked (`7fbc77c`), Pete reversed the earlier '
     'keep-out call.'),
    ('- `vercel-routing-migration` branch still exists',
     '- CLOSED 2026-09-26/27 -- `vercel-routing-migration` branch deleted locally and on origin (0 unmerged '
     'commits). Its leftover branch-scoped `ANTHROPIC_API_KEY` row on `prv3-engine` removed. Pete added a '
     'general Preview `ANTHROPIC_API_KEY` row (Sensitive, no branch restriction), verified by a tagged Preview '
     'session through `engine-preview` (`is_fallback: false`, Anthropic 200 on `/api/complete` in that '
     'deployment\'s logs).'),
    ('- If revisiting hr-dx copy (drawer, compound-family grammar, narrative em-dashes):',
     '- If revisiting hr-dx copy: web/data/results-pathway-detail-hr.ts (drawer texts), '
     'engine/resolution_families.py (HR context strings and backup copy), engine/output_synthesis.py '
     '(`_family_as_prose`, synthesis prompt), engine/narrative.py (question-generation prompt and guard).'),
    ('- If reworking or retiring tools/diagnostic_fast_forward.py:',
     '- If tuning the fast_forward driver\'s answer-steering: tools/diagnostic_fast_forward.py '
     '(`choose_option_id`), engine/data/states.py (target-state signals), web/lib/resolution-family.ts '
     '(`hrPathwayForRouting`).'),
    ('- If changing Vercel env/project config: prompts/session-handoff-v4.326.md',
     '- If changing Vercel env/project config: prompts/session-handoff-v4.327.md (current row-by-row state '
     'of both projects and the `engine-preview` branch).'),
    ('Last updated: This session (Claude Code), 2026-09-26 (closeout pass)',
     'Last updated: This session (Claude Code), 2026-09-26/27 (final closeout of the hr-dx polish arc) -- no '
     'numbered priority item closed or resequenced. Closed in place: fast_forward rework, drawer copy, both '
     'copy residuals, the 2026-09-24/25 logging gap, both `ENGINE_BASE_URL` scopes, launch.json, the branch '
     'and its dead key row. Added: driver answer-steering (open), separate Preview database (backlog, '
     'deferred), `engine-preview` upkeep, untracked `uv.lock`.'),
]

# ── 13b insertions after an (already replaced or existing) line prefix ─────
LINE_INSERTIONS = [
    ('- `tools/diagnostic_fast_forward.py` answer-steering is too weak',
     '- Separate Upstash database for Preview -- backlog, deferred by Pete 2026-09-26/27. Preview and '
     'Production share one database (confirmed 2026-09-26). Pete chose the `is_test` tag over a separate '
     'database for now, not pursued. Revisit is Pete\'s call.'),
    ('- CLOSED 2026-09-26/27 -- `vercel-routing-migration` branch deleted',
     '- `engine-preview` branch (new 2026-09-26/27, long-lived): exists so `prv3-engine` has a stable Preview '
     'alias for `prv-3`\'s general Preview `ENGINE_BASE_URL`. It carries two empty build-trigger commits on '
     'top of `d60107c` (`fdf3d60`, `e8fa02e`), so refresh it by merging `main` into it and pushing, not by '
     'fast-forward. Do not delete it while the Preview row points at its alias.' + NL +
     '- Untracked `uv.lock` at the repo root (timestamped 2026-09-24 23:39), a byproduct of the '
     '`pyproject.toml` commits for `prv3-engine`. Never committed. Keep or remove is Pete\'s call.'),
]

BACKFILL_ANCHOR = '## SESSION CLOSEOUT (2026-09-26, terminal Claude Code) -- hr-dx.com' + NL

BACKFILL = '''## BACKFILLED ENTRY (2026-09-24/25, reconstructed 2026-09-26/27 by terminal Claude Code)
## -- pre-2026-09-26 hr-dx build: TC-* questions, brand resolution, routing wall-off,
## domain rename, two-project split Phases 2-3

**Provenance, read first:** this is not a contemporaneous record. No Section 16 entry, no diary entry (the Mem0 diary goes straight from the 2026-09-23 closeout to 2026-09-27), and no handoff file exist for these two days. Reconstructed after the fact, during the v4.327 closeout, from: `git log` and commit message bodies (58 commits, 2026-09-24 14:31 to 2026-09-25 00:17 -0400, every one carrying a `Co-Authored-By: Claude Sonnet 5` trailer), the local `main` reflog, and `vercel ls` Production deployment records filtered by commit SHA. Where a commit body states something, it is reported as the commit states it. The decisions, Pete confirmations, and any Gemini review behind this work are not recoverable from these sources and are not asserted here.

### 1. 2026-09-24 afternoon, committed on `main` directly (45 commits, `d384262` to `6c99e55`)

- **TC-* Tactical & Compliance questions.** 40 questions (10 sections x 4) added to `QUESTION_LIBRARY` (`d384262`, patch script `58b9911`), generated from `C:\\Users\\rizzo\\Downloads\\tactical-compliance-questions-schema-compliant.json` (generator `a73b145`, `web/data/tactical-question-meta.ts` at `9e3ebe1`). Per the commit body: hr_diagnostic only, zero-signal on every option, `state_targets=[]` for all 40, and verified inert against the 175-profile calibration suite (byte-identical output, 171/175 unchanged, the 4 ATT-* prominence failures pre-existing and logged to 13b at `dc850e5`).
- **TC-* session wiring.** Brand-conditional TC-* sequence in `createSession()` (`2fd5172`), `tactical_results` resolved at completion (`a739a2a`, tests `5df5340`), threaded through `DiagnosticFlow` (`3c1d9c0`), rendered by section with the stale Engage CTA fixed on hr_diagnostic (`468c760`). `TACTICAL_REFERRALS` per-section referral mapping (`b3cc900`) is, per its own body, a corrective commit: the completion code depending on it had been committed first without it and did not compile. Its body also records "every section includes HR Consulting per Pete's explicit specialty list".
- **Brand resolution and routing wall-off ("Part A").** Hostname-based `resolveBrand()` (`e290d8e`), `BrandContext` (`93eae1e`), brand from the Host header in session/start (`e69a6be`), middleware routing wall-off for hr_diagnostic (`b3a8b85`), brand metadata scoped to the `/diagnostic` layout (`2719b4b`), self-select entry point hidden on hr_diagnostic (`8aab0ed`), brand-conditional ShareableOutput header (`5dac6c5`). Then a debug-only hr_diagnostic override, `resolveBrandForRequest()` (`119cc5e`), adopted by middleware, the diagnostic layout, and session/start (`f062984`, `347a09d`, `5bdac39`).
- **Domain rename** `hrdiagnostic.com` to `hr-dx.com` (`dfe4f25`, nine comment-only follow-ups, and the MOB ATT-* bullet at `1ceda19`).
- **hr-dx.com root serving the wrong brand.** Homepage content extracted into a client `HomeClient`, and `/` forced dynamic to stop cross-domain cache sharing (`cd2bfc3`, `98a5712`).
- **`3806506`, TEMPORARY middleware diagnostic** (echoes raw Host and brand as response headers). With its patch script `6c99e55` it was the last commit on `main` before the 2026-09-26 merge. Production exposure, checked for this backfill: both Production builds of `6c99e55` are in **Error**, and the last Ready Production build from this stretch is `4f104cd`, so the debug headers never served in Production. Removed in `e368d8d` before the merge.

### 2. 2026-09-24 evening to 2026-09-25 00:17, on `vercel-routing-migration` (13 commits, `2b7b529` to `6058ca9`)

Off-`main` confirmed by the reflog: `main` sits at `6c99e55` from 2026-09-24 17:48 until the 2026-09-26 fast-forward (`e368d8d`).

- **Two-project split, Phase 2:** root `vercel.json` rewritten for Project B, the Python engine (`2b7b529`). **Phase 3:** the 8 engine routes proxied to Project B through `ENGINE_BASE_URL` (`585a80c`). `pyproject.toml` added for the FastAPI entrypoint, then given a full `[project]` table (`060327a`, `8289ac7`).
- **Preview debugging:** three empty Preview build triggers for a rotated `ENGINE_SECRET` and a regenerated, then re-copied, bypass secret (`05ea3b7`, `5fcf67c`, `95a34e9`), and a TEMPORARY question-copy upstream-response diagnostic (`0f3fd67`, patch `6058ca9`), also removed in `e368d8d`. The 2026-09-26 closeout's section 4 records that live Preview sessions were still failing when that session began.

### 3. Gaps this backfill cannot fill

- **Phase 1 of the two-project split has no commit.** Creating `prv3-engine`, changing `prv-3`'s Root Directory to `web`, the Vercel env rows, and the domain setup were dashboard or CLI work with no git trace. When the Root Directory changed, and so exactly when the Production build freeze began, is not recoverable here.
- **Not recorded in any source read:** why the domain became `hr-dx.com`, the authorship and approval of the 40 TC-* question texts (the source JSON is in Pete's Downloads folder, not the repo), and any Gemini review of the Part A design.
- **Test status at the time** is known only where a commit body states it (the TC-* inertness check above). Whether Startup Protocol ran is unknown.
- **Byproduct:** an untracked `uv.lock` at the repo root, timestamped 2026-09-24 23:39, alongside the `pyproject.toml` commits. Never committed, now noted in 13b.

This backfill landed with the v4.327 closeout. The work it describes sits between v4.325 and v4.326.'''.replace('\n', NL)

CLOSEOUT = '''## SESSION CLOSEOUT (2026-09-26/27, terminal Claude Code, same session continued) -- hr-dx
## polish batch closed, Preview engine isolated, 2026-09-24/25 backfilled -- MOB v4.326 -> v4.327

**One-line summary:** every hr-dx follow-up from the v4.326 closeout is closed: the six-item polish batch, the family-specific drawer copy with a plain "HR Consulting" Executive Advisory context, `prv-3` Previews moved off the Production engine onto a new `engine-preview` branch with its own Preview key, the dead key row removed, and the 2026-09-24/25 Section 16 gap backfilled.

### 1. Shipped on `main` (Production READY on both projects after each push)

- `5d81c1c` -- `is_test` on aggregate records (recorded in the v4.326 addendum).
- `ce9ad29` -- compound families rendered as "A with B" in the synthesis prompt. Live: "People Tactics & Strategy with First Call is built for...".
- `b675d9f` -- narrative questions: punctuation rule in the prompt plus a deterministic guard. No dashes in any narrative question observed since.
- `e836d79` -- `tools/diagnostic_fast_forward.py` reworked into the permanent session driver, used for every live session since.
- `7fbc77c` -- `.claude/launch.json` tracked.
- `d60107c` -- hr-dx drawer copy (four texts, `web/data/results-pathway-detail-hr.ts`, selected by a neutral `hr_pathway` field that only hr_diagnostic payloads carry) and the Executive Advisory context simplified to "HR Consulting". Backup copy is now keyed by engine family, so two families sharing one context string keep distinct backups. Verified: 12/12 Python suites (hr brand 122/122), tsc clean, vitest 118/118, build clean with an unchanged route table, and the HR copy present only in dynamically loaded chunks for hr routes and dev pages. Live: 10 tagged hr-dx Production sessions, urgent confirmed 4 times, the no-routing generic drawer 6 times, no PR names in any payload. Structure, capability, leadership, and the Executive Advisory context are verified by tests only (driver item below).
- `5e1eda9` -- 13b item for the driver's answer-steering gap.

### 2. Vercel and branch config (non-git)

- `vercel-routing-migration` deleted locally and on origin.
- `engine-preview` created from `main` at `d60107c`, plus two empty build triggers (`fdf3d60`, `e8fa02e`). The first was needed because pushing a branch whose commit Production had already built started no Vercel build.
- `prv-3` `ENGINE_BASE_URL`: Production = `https://prv3-engine-peter-rizzos-projects.vercel.app`. General Preview = `https://prv3-engine-git-engine-preview-peter-rizzos-projects.vercel.app`. Values are encrypted, so each was confirmed by a successful CLI write plus the alias existing, not by read-back.
- `prv3-engine`: `ANTHROPIC_API_KEY` Production and general Preview (the Preview row added by Pete via CLI), `ENGINE_SECRET` Production and Preview. The branch-scoped key row for the deleted branch was removed.
- End-to-end check: tagged Preview session `VptEM9KcD72IWi5LW8KMR` through `prv-3-git-engine-preview` reached engine deployment `prv3-engine-992dhvt68` (its logs show the full question sequence and an Anthropic 200 on `/api/complete`), `is_fallback: false`, no `parse_error`, real generated synthesis, 32s end to end. The logs do not break out the AI call's own duration.

### 3. Records

- Section 16 backfill for 2026-09-24/25, placed chronologically before the 2026-09-26 closeout. Reconstructed, marked as such, gaps listed.
- CLAUDE.md: Quarterly Step-Back "Next due" corrected from September 19 to 2026-10-03, matching 13b, per Pete. MOB version cross-reference v4.327.

### 4. Section 13b Currency Check (Step 1a)

**13b checked, and amended** -- not "no change." No numbered priority item closed or resequenced. Closed in place: the fast_forward rework, the drawer copy, both copy residuals, the 2026-09-24/25 logging gap, both `ENGINE_BASE_URL` scopes, launch.json, and the branch with its dead key row. The driver answer-steering item stays open. Added: the separate Preview database as an explicit backlog item (deferred by Pete), `engine-preview` upkeep, and the untracked `uv.lock`. Files-to-attach refreshed.

**Files changed, git-confirmed:** code and config commits listed in section 1. This closeout: `tools/_mob.txt`, `CLAUDE.md`, `prompts/session-handoff-v4.327.md` (new), `tools/patch_mob_session_closeout_20260927.py` (new).

**Open items carried forward:** see Section 13b as amended above. Next Quarterly Step-Back due **2026-10-03**.

**Anything Pete should know at next session start:** Startup Protocol did not run at the start of this continued session either, run it in full next time. `diagnostic-aggregate` holds this session's tagged test records (at least 16 Production, 1 Preview), so exclude `is_test: true` when reading it. The backfill does not recompute the 2026-09-26 entry's "~35h" freeze figure, since when the freeze began is one of its unrecoverable gaps.

MOB v4.327.'''.replace('\n', NL)

HANDOFF_TEXT = '''# Session handoff -- MOB v4.327 (2026-09-26/27, terminal Claude Code)

Derived from Section 16's 2026-09-26/27 closeout entry in `tools/_mob.txt`. If the two ever disagree, Section 16 is authoritative.

## Summary

Every hr-dx follow-up from the v4.326 closeout is closed: the six-item polish batch, the family-specific drawer copy with a plain "HR Consulting" Executive Advisory context, `prv-3` Previews moved off the Production engine onto a new `engine-preview` branch with its own Preview key, the dead key row removed, and the 2026-09-24/25 Section 16 gap backfilled.

## Shipped this session

| Area | Commits |
|---|---|
| `is_test` on aggregate records | `5d81c1c` |
| Compound-family grammar ("A with B") | `ce9ad29` |
| Narrative-question punctuation (prompt rule + guard) | `b675d9f` |
| fast_forward reworked into the permanent driver | `e836d79` |
| `.claude/launch.json` tracked | `7fbc77c` |
| hr-dx drawer copy + Executive Advisory context | `d60107c` |
| 13b driver answer-steering item | `5e1eda9` |
| `engine-preview` branch (empty build triggers) | `fdf3d60`, `e8fa02e` |

## Vercel config state (non-git)

- `prv-3` `ENGINE_BASE_URL`: Production = `https://prv3-engine-peter-rizzos-projects.vercel.app`. General Preview = `https://prv3-engine-git-engine-preview-peter-rizzos-projects.vercel.app`.
- `prv3-engine`: `ANTHROPIC_API_KEY` Production + general Preview (Pete-added). `ENGINE_SECRET` Production + Preview. SSO protection off project-wide (approved 2026-09-26). The dead branch-scoped key row is removed.
- `engine-preview` branch: long-lived, exists for the stable Preview alias. Refresh by merging `main` into it and pushing, not fast-forward. Do not delete while the Preview row points at it.
- Verified end to end: tagged Preview session through `engine-preview`, `is_fallback: false`, Anthropic 200 in that deployment's logs.

## Records

- Section 16 backfill for 2026-09-24/25 (reconstructed from git, reflog, and Vercel deployment records, gaps listed in the entry).
- CLAUDE.md step-back date corrected to 2026-10-03.

## Open

- Driver answer-steering: hr-dx structure, capability, and leadership pathways and the Executive Advisory context are verified by tests only, not live.
- Separate Upstash database for Preview: backlog, deferred by Pete.
- Untracked `uv.lock` (2026-09-24 pyproject work): keep or remove, Pete's call.
- 13b numbered priorities 1-5 unchanged.

## Parked

Unchanged from Section 13b's "Explicitly parked" list.

## Dated items

- Next Quarterly Step-Back due **2026-10-03**.

## Files to attach next session

- Always: `tools/_mob.txt`.
- hr-dx copy work: `web/data/results-pathway-detail-hr.ts`, `engine/resolution_families.py`, `engine/output_synthesis.py`, `engine/narrative.py`.
- Driver steering: `tools/diagnostic_fast_forward.py`, `engine/data/states.py`, `web/lib/resolution-family.ts`.
- Vercel config changes: this file.

## Anything Pete should know

- Startup Protocol did not run at the start of this continued session. Run it in full next time.
- `diagnostic-aggregate` holds this session's tagged test records (at least 16 Production, 1 Preview). Exclude `is_test: true`.
'''

CLAUDE_EDITS = [
    ('- Next due: on or near September 19, 2026',
     '- Next due: on or near October 3, 2026 (matches MOB Section 13b, corrected here 2026-09-27 per Pete, '
     'the earlier "September 19" was stale. The locked biweekly cadence is unchanged, the 2026-08-28 '
     'biweekly lock stands as-is)'),
    ('| MOB version | v4.326 |', '| MOB version | v4.327 |'),
]


def replace_line(text: str, prefix: str, new_line: str, label: str) -> str:
    key = NL + prefix
    if text.count(key) != 1:
        print(f'ERROR: {label}: prefix found {text.count(key)} times at a line start: {prefix!r}', file=sys.stderr)
        sys.exit(1)
    start = text.index(key) + len(NL)
    end = text.index(NL, start)
    return text[:start] + new_line + text[end:]


def insert_after_line(text: str, prefix: str, new_lines: str, label: str) -> str:
    key = NL + prefix
    if text.count(key) != 1:
        print(f'ERROR: {label}: prefix found {text.count(key)} times at a line start: {prefix!r}', file=sys.stderr)
        sys.exit(1)
    end = text.index(NL, text.index(key) + len(NL))
    return text[:end] + NL + new_lines + text[end:]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    if HANDOFF.exists():
        print(f'ERROR: {HANDOFF} already exists (handoffs are never overwritten).', file=sys.stderr)
        sys.exit(1)

    raw = MOB.read_bytes().decode('utf-8')
    before_len = len(raw.split(NL))
    mob = raw

    # Version header
    if mob.count('# MOB v4.326' + NL) != 1:
        print('ERROR: MOB version header not found exactly once.', file=sys.stderr)
        sys.exit(1)
    mob = mob.replace('# MOB v4.326' + NL, '# MOB v4.327' + NL, 1)
    print('[MOB :: header v4.326 -> v4.327] OK')

    for prefix, new_line in LINE_REPLACEMENTS:
        mob = replace_line(mob, prefix, new_line, '13b replace')
        print(f'[MOB :: 13b replace] {prefix[:70]} OK')
    for prefix, new_lines in LINE_INSERTIONS:
        mob = insert_after_line(mob, prefix, new_lines, '13b insert')
        print(f'[MOB :: 13b insert after] {prefix[:70]} OK')

    if mob.count(BACKFILL_ANCHOR) != 1:
        print('ERROR: 2026-09-26 closeout header not found exactly once.', file=sys.stderr)
        sys.exit(1)
    preceding = mob[:mob.index(BACKFILL_ANCHOR)]
    if not preceding.endswith('MOB v4.325.' + NL + NL + '---' + NL + NL):
        print('ERROR: unexpected text before the 2026-09-26 closeout header.', file=sys.stderr)
        sys.exit(1)
    mob = mob.replace(BACKFILL_ANCHOR, BACKFILL + NL + NL + '---' + NL + NL + BACKFILL_ANCHOR, 1)
    print('[MOB :: Section 16 backfill inserted before the 2026-09-26 closeout] OK')

    if not mob.rstrip(NL).endswith('MOB version unchanged (v4.326).'):
        print('ERROR: MOB does not end with the v4.326 addendum.', file=sys.stderr)
        sys.exit(1)
    mob = mob.rstrip(NL) + NL + NL + '---' + NL + NL + CLOSEOUT + NL
    print('[MOB :: Section 16 closeout appended] OK')

    claude = CLAUDE.read_bytes().decode('utf-8')
    for old, new in CLAUDE_EDITS:
        if old.startswith('- Next due'):
            claude = replace_line(claude, old, new, 'CLAUDE.md step-back')
        else:
            if claude.count(old) != 1:
                print(f'ERROR: CLAUDE.md anchor found {claude.count(old)} times: {old!r}', file=sys.stderr)
                sys.exit(1)
            claude = claude.replace(old, new, 1)
        print(f'[CLAUDE.md] {old[:60]} OK')

    # Integrity: only additions/in-place line swaps. Every original line that is
    # not one of the replaced 13b lines or the header must still be present, in order.
    replaced_prefixes = [p for p, _ in LINE_REPLACEMENTS]
    orig_lines = [l for l in raw.split(NL)
                  if not any(l.startswith(p) for p in replaced_prefixes) and l != '\\\\\\#\\\\\\# MOB v4.326']
    new_lines = mob.split(NL)
    it = iter(new_lines)
    missing = [l for l in orig_lines if not any(l == n for n in it)]
    if missing:
        print(f'ERROR: {len(missing)} original lines lost or reordered, first: {missing[0][:100]!r}', file=sys.stderr)
        sys.exit(1)
    print(f'[integrity] every untouched original line preserved in order ({len(orig_lines)} lines), '
          f'{before_len} -> {len(new_lines)} lines')
    print(f'[semicolons in new MOB text] backfill={BACKFILL.count(";")} closeout={CLOSEOUT.count(";")} '
          f'13b={sum(n.count(";") for _, n in LINE_REPLACEMENTS + LINE_INSERTIONS)} handoff={HANDOFF_TEXT.count(";")}')

    if args.dry_run:
        print('DRY RUN -- all anchors found. Nothing written.')
        return
    MOB.write_text(mob, encoding='utf-8', newline='')
    print(f'WROTE: {MOB}')
    CLAUDE.write_text(claude, encoding='utf-8', newline='')
    print(f'WROTE: {CLAUDE}')
    HANDOFF.write_text(HANDOFF_TEXT, encoding='utf-8')
    print(f'WROTE: {HANDOFF}')


if __name__ == '__main__':
    main()
