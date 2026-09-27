"""
Session closeout 2026-09-26 (terminal Claude Code) -- MOB v4.325 -> v4.326.

Writes, per CLAUDE.md's Closeout Protocol:
  - tools/_mob.txt: version bump; Section 13b currency amendments (Step 1a);
    Section 14 locked-decisions row; Section 16 closeout entry appended.
  - CLAUDE.md: MOB version cross-reference (v4.325 -> v4.326).
  - prompts/session-handoff-v4.326.md: derived from the Section 16 entry.

Usage:
    python tools/patch_mob_session_closeout_20260926.py --dry-run
    python tools/patch_mob_session_closeout_20260926.py --write
"""
import argparse
import pathlib
import sys

MOB = pathlib.Path('tools/_mob.txt')
CLAUDE = pathlib.Path('CLAUDE.md')
HANDOFF = pathlib.Path('prompts/session-handoff-v4.326.md')

NL = '\r\n'  # _mob.txt uses CRLF line endings


def crlf(s: str) -> str:
    return s.replace('\r\n', '\n').replace('\n', NL)


# ── 13b amendments ────────────────────────────────────────────────────────────
OLD_FF = ('- `tools/diagnostic_fast_forward.py` -- confirmed structurally unusable against current '
          'infrastructure, rework-or-retire decision still undecided.')
NEW_FF = ('- `tools/diagnostic_fast_forward.py` -- rework-or-retire still undecided, but its failure '
          'modes are now concrete (2026-09-26): its `DEFAULT_INTAKE` is missing `org_type` and '
          '`significant_events` (session/start now 400s on it), and its answer loop does not handle the '
          '`status: "narrative"` response. Its `PreviewClient`/`choose_option_id` core still works -- a '
          'scratchpad wrapper reusing them unmodified (adding `x-debug-brand`, the narrative step, and '
          'result capture) drove every live Preview and Production session this session. The wrapper '
          'was never committed.')

ANCHOR_OPEN_END = ('Logged as a known issue, not investigated further this session -- no fix attempted.')
NEW_OPEN_ITEMS = '''
- hr-dx follow-ups after the 2026-09-26 Production launch (full detail in Section 16's 2026-09-26 entry):
  - Two Production test records to delete from Redis list `diagnostic-aggregate` (Pete, Upstash console -- hard deletes of production data are Pete's to run). Records carry no session ID or brand, only `industry`, `organization_size`, `final_state_rankings`, `completed_at`. Identify via `LRANGE diagnostic-aggregate -5 -1`: both have industry "Technology", organization_size 175, final_state_rankings[0] "Built to Fail", and `completed_at` near 2026-09-26T23:59:5xZ (hr-dx session `O_xGNJ7u8jdQ_52GsUVnj`) and 2026-09-27T00:00:3xZ (principalresolution.com session `hRVuj6kk-LvM88VoNhVei`). Remove each with `LREM diagnostic-aggregate 1 '<exact JSON>'`, not a positional LTRIM. Unverified: whether Preview and Production share one Upstash instance (both sets of credentials are Sensitive) -- if they do, roughly 20 Preview test completions from 2026-09-26 also landed in the same list.
  - hr-dx "About this report" drawer copy -- currently the generic fallback ("The recommended next step is below, matched to what was found."), Pete's 2026-09-26 decision to revisit only after F/I/J landed. F/I/J is now live, so the revisit is due.
  - Copy residual, PR brand: the AI renders compound families as a singular subject ("People Tactics & Strategy and First Call is built for..."). Next lever, if wanted: frame the prompt value as one offering rather than two names.
  - Copy residual, both brands: AI-generated narrative questions occasionally use an em-dash (2 of roughly 10 observed, one in Production). Lever: `engine/narrative.py`'s question-generation system prompt.
  - `web/lib/diagnostic-completion.ts` `[DIAG] synthesis fallback` log is PERMANENT by design (surfaces `parse_error`). Only the live run proves the log line itself -- no unit test covers it.
- Section 16 logging gap, 2026-09-24/25: the pre-2026-09-26 hr-dx build work (Part A routing wall-off, TC-* wiring, hostname branding, the Preview-build/bypass debugging commits through `6058ca9`) has no Section 16 closeout entry. Flagged, not backfilled -- this session only has direct evidence for its own work.'''

OLD_UPSTASH = '- Local dev Upstash Redis credentials missing -- informational only, production already has them.'
NEW_UPSTASH = (OLD_UPSTASH + '\n'
               '- `prv-3` general-Preview `ENGINE_BASE_URL` still holds the stale deployment-pinned alias '
               '`https://hr-dx-peter-rizzos-projects.vercel.app` (affects Preview builds of branches other than '
               '`vercel-routing-migration` only). The correct target for a general Preview row is the '
               'relevant branch engine alias or the stable production alias -- Pete\'s call.\n'
               '- `prv3-engine` Deployment Protection (SSO) is off project-wide, Production included -- '
               'Pete-approved 2026-09-26, `ENGINE_SECRET` is the engine\'s application-level auth. Its '
               'automation bypass secret was exposed in a CLI status read and rotated by Pete the same day.\n'
               '- `.claude/launch.json` carries an uncommitted local `prv3-web-start` entry (production-server '
               'launch config used for this session\'s local verification) -- deliberately kept out of every '
               'commit, keep or revert is Pete\'s call.\n'
               '- `vercel-routing-migration` branch still exists locally and on origin after the 2026-09-26 '
               'fast-forward merge (fully contained in `main` at `e368d8d`). Safe to delete -- Pete\'s call.')

ANCHOR_FILES = '- Always: tools/_mob.txt (current version).'
NEW_FILES = (ANCHOR_FILES + '\n'
             '- If revisiting hr-dx copy (drawer, compound-family grammar, narrative em-dashes): '
             'engine/output_synthesis.py (`_family_as_prose`, synthesis prompt), engine/narrative.py '
             '(question-generation prompt), engine/resolution_families.py (`hr_diagnostic_synthesis_family`, '
             'HR backup copy), web/data/orientation-copy.ts, web/components/ResultsOrientationHR.tsx, '
             'prompts/session-handoff-v4.326.md.\n'
             '- If reworking or retiring tools/diagnostic_fast_forward.py: that file, '
             'web/app/api/diagnostic/session/start/route.ts (`validateIntake`), '
             'web/app/api/diagnostic/session/narrative/route.ts.\n'
             '- If changing Vercel env/project config: prompts/session-handoff-v4.326.md (current row-by-row '
             'state of both projects).')

OLD_LAST = 'Last updated: This session (Claude Code), 2026-09-23 (closeout pass)'
NEW_LAST_PREFIX = ('Last updated: This session (Claude Code), 2026-09-26 (closeout pass) -- no numbered '
                   'priority item closed or resequenced; open-not-sequenced list gained the hr-dx post-launch '
                   'follow-ups and the 2026-09-24/25 logging-gap flag, the fast_forward item was made '
                   'concrete, infrastructure carry-forwards gained four config items, files-to-attach gained '
                   'three entries. (Prior update: 2026-09-23 (closeout pass)')

# ── Section 14 row ────────────────────────────────────────────────────────────
S14_ANCHOR = '| **SESSION CLOSEOUT (2026-09-07, terminal Claude Code) -- three Quarterly Step-Back items closed'
S14_ROW = ('| **September 2026 -- hr-dx.com (hr_diagnostic) live in Production on the two-project Vercel '
           'architecture** | Locked 2026-09-26, Pete-confirmed at each step. (1) Two-project split live: '
           '`prv-3` (web, Root Directory `web`) + `prv3-engine` (FastAPI, zero-config routing, no '
           '`vercel.json` rewrites -- they broke every engine route). `prv-3` Production `ENGINE_BASE_URL` = '
           'the stable production alias `prv3-engine-peter-rizzos-projects.vercel.app`, never a '
           'deployment-pinned alias. (2) hr-dx airgap is bundle-level, not render-level: hr-dx must not '
           'DOWNLOAD PR content (tier names, "Principal Resolution", taxonomy, PR-only routes), verified by '
           'chunk scan of what hr-dx pages actually load. Mechanisms: physical route separation, and '
           'next/dynamic from CLIENT components (Next does not code-split from Server Components). (3) '
           'hr_diagnostic results name "HR Consulting" only (engine-side synthesis context + backup copy, '
           'web-side resolution_family/resolution_routing). (4) Engine LLM model `claude-sonnet-5`, '
           'sampling params removed, thinking disabled on content[0].text callers. Full detail: Section 16, '
           '2026-09-26 entry. MOB v4.326. |')

# ── Section 16 entry ──────────────────────────────────────────────────────────
S16 = '''

---

## SESSION CLOSEOUT (2026-09-26, terminal Claude Code) -- hr-dx.com
## airgapped and live in Production, two-project split live, Production
## freeze resolved -- MOB v4.325 -> v4.326

**One-line summary:** hr-dx.com (hr_diagnostic) went from a routing-level wall-off to a verified bundle-level airgap, brand-safe results and AI text, and a working two-project (`prv-3` + `prv3-engine`) deployment -- fast-forward merged to `main` (`6c99e55..e368d8d`) and verified end to end in Production, which also ended a ~35-hour Production build freeze.

### 1. PRV3 chrome off hr-dx: route-group split, then chrome restored for principalresolution.com

`f855d0a` -- every PRV3 route moved into `app/(site)/` with NavBar/MobileMenu/ServiceSidebar in `(site)/layout.tsx`; `app/diagnostic/` stays outside. URLs and the Static/Dynamic route table unchanged. `d301975` -- chrome restored on principalresolution.com's `/diagnostic` and 404s: `DiagnosticChrome` (client) loads `SiteChrome` via next/dynamic for principal_resolution only. The first attempt (static import in the server layout, and next/dynamic from the server layout) shipped the chrome chunk to hr-dx -- caught by chunk scan, never committed. Root `not-found.tsx` is chrome-free (it is embedded in every route's payload); `(site)/not-found.tsx` + a `(site)/[...missing]` catch-all give PR 404s chrome.

### 2. Bundle-level airgap: everything hr-dx downloads, not just what it renders

The standard adopted this session: hr-dx must not download PR content. Verified each time by fetching every chunk hr-dx `/`, `/diagnostic`, `/diagnostic?session=` actually load (script tags + RSC payload) and grepping them. `879103c` -- self-select (Path B) moved to `app/(site)/diagnostic/self-select/`: the taxonomy (state names, signatures) was in hr-dx's bundle via a static import. `0643e8e` -- item E ("Principal Resolution's services"), item G (tier-keyed "About this report" details) and PrivateOutput's `/book/toc` + engage CTA split into brand modules loaded via next/dynamic from client components. Final scan (`d301975` build): 14 chunks per hr-dx page, 0 hits on 14 terms.

### 3. F/I/J: brand-safe results and AI text

`ed46564` -- brand threaded web -> `/api/complete` -> engine. hr_diagnostic gets `resolution_family`/`resolution_routing` "HR Consulting", an HR synthesis context string (service references + urgency cue), and a tier-agnostic HR backup-copy table. `cd514c3` -- First Call backup copy reworded (Pete). `95a4491` -- Sonnet 5 echoes the context string verbatim: hr-dx cue now "HR Consulting on an urgent basis[, through ...]", PR compounds rendered "A and B" on the prompt line only (the "+" key still drives the backup lookup), and `parse_error` added to the `/api/complete` synthesis output (additive -- every consumer maps named fields).

### 4. Why nothing worked live at first: four stacked infrastructure causes

Each found from logs, not assumed: (a) `prv-3`'s only `ENGINE_BASE_URL` row (Preview+Production) pointed at a deployment-pinned alias of an old `main` engine; the two dashboard edits meant to fix it never saved -- CLI writes did. (b) `prv3-engine` SSO protection was on for all deployments; disabled project-wide via CLI (Pete-approved). (c) `vercel.json` rewrote all 8 engine routes to `/api/engine.py`, which FastAPI 404'd -- removed (`e9eefd9`), 8/8 routes then reached the app. (d) The engine called `claude-sonnet-4-6` and fell back in 0.6-2.8s on every call -- migrated to `claude-sonnet-5` in all 8 code sites + 2 tests (`f278676`), with `temperature` removed (400 on Sonnet 5) and thinking disabled on `content[0].text` callers. Also: `prv3-engine` had no `ANTHROPIC_API_KEY` at all (Pete added Preview and a distinct `prv3-engine-production` key via CLI).

### 5. Production freeze and merge

Root cause of the freeze: `main`'s legacy `builds`-style `vercel.json` under `prv-3`'s new Root Directory `web` failed Edge packaging (`middleware.js: @/lib/brand` unsupported module), 3 builds in ERROR over ~35h, Production held on a pre-split deployment. Production env prepped first: `prv-3` Production `ENGINE_BASE_URL` = `https://prv3-engine-peter-rizzos-projects.vercel.app` (stable prod alias, confirmed via project inspection), `prv3-engine` Production `ANTHROPIC_API_KEY`. `e368d8d` removed the two TEMPORARY diagnostics (middleware debug headers, question-copy DIAG). Fast-forward merge `6c99e55..e368d8d`, both Production builds READY.

### 6. Live verification

Preview: healthy AI path on both brands (9-12s per synthesis, rule checks pass, no banned jargon), backup path forced twice via a temporary branch-scoped `ANTHROPIC_BASE_URL=https://forced-failure.invalid` (removed and revert confirmed each time), diagnostic log showed `API error: Connection error.` Production (`e368d8d`): principalresolution.com `/`, `/about`, `/book`, `/book/toc`, `/diagnostic` 200 with nav; hr-dx.com `/`, `/diagnostic` 200 with no PR content, `/book`, `/about`, `/diagnostic/self-select`, `/api/result` 404. hr-dx session `O_xGNJ7u8jdQ_52GsUVnj`: "HR Consulting" both fields, real AI text, 0 PR terms. PR session `hRVuj6kk-LvM88VoNhVei`: real AI text. Both completions logged on the new production engine `dpl_6Es6muar` with `api.anthropic.com ... 200 OK`.

### 7. Section 13b Currency Check (Step 1a)

**13b checked, and amended** -- not "no change." No numbered priority item closed or resequenced. Added to open-not-sequenced: the hr-dx post-launch follow-ups (two Production test records to delete, drawer copy revisit now due, two copy residuals, the permanent diagnostic log note) and the 2026-09-24/25 Section 16 logging-gap flag. The fast_forward item made concrete. Infrastructure carry-forwards gained: stale general-Preview `ENGINE_BASE_URL`, `prv3-engine` protection off, `launch.json` unstaged, `vercel-routing-migration` branch deletion. Files-to-attach gained three entries.

**Files changed, git-confirmed:** 18 commits this session on `vercel-routing-migration` (8 of them empty Preview build triggers), fast-forwarded into `main` at `e368d8d`. This closeout: `tools/_mob.txt`, `CLAUDE.md` (MOB version cross-reference), `prompts/session-handoff-v4.326.md` (new), `tools/patch_mob_session_closeout_20260926.py` (new).

**Open items carried forward:** see Section 13b as amended above. Next Quarterly Step-Back due **2026-10-03**, unchanged.

**Anything Pete should know at next session start:** Production is live on the new architecture for both brands. Delete the two Production test records (13b). CLAUDE.md's Startup Protocol did not run at the start of this session (it opened mid-task) -- Step 1 diary read, Step 2 MOB read, Step 3 test suite, and Step 3a research check were not performed at start; tests were run throughout the work instead.

MOB v4.326.'''

HANDOFF_CONTENT = '''# Session handoff -- MOB v4.326 (2026-09-26, terminal Claude Code)

Derived from Section 16's 2026-09-26 closeout entry in `tools/_mob.txt`. If the two ever disagree, Section 16 is authoritative.

## Summary

hr-dx.com (hr_diagnostic) is live in Production on the two-project Vercel architecture (`prv-3` web + `prv3-engine` FastAPI), with a verified bundle-level airgap (hr-dx downloads no PR content), brand-safe results and AI text ("HR Consulting"), and the engine on `claude-sonnet-5`. `vercel-routing-migration` was fast-forward merged to `main` (`6c99e55..e368d8d`), which also ended a ~35-hour Production build freeze.

## Shipped this session

| Area | Commits |
|---|---|
| Route-group split, chrome off hr-dx | `f855d0a` |
| Chrome restored on PR `/diagnostic` + 404s, airgapped | `d301975` |
| Self-select physical route airgap (taxonomy) | `879103c` |
| Item E / item G / PrivateOutput brand code-split | `0643e8e` |
| F/I/J brand-safe results + AI text + backup copy | `ed46564`, `cd514c3`, `95a4491` |
| `vercel.json` engine rewrites removed | `e9eefd9` |
| Model `claude-sonnet-4-6` -> `claude-sonnet-5` + diagnostic log | `f278676` |
| TEMPORARY diagnostics removed | `e368d8d` |
| Fast-forward merge to `main`, Production verified | `e368d8d` |

## Vercel config state (non-git)

- `prv-3` `ENGINE_BASE_URL`: Production = `https://prv3-engine-peter-rizzos-projects.vercel.app` (stable prod alias). Preview (`vercel-routing-migration`) = branch engine alias. Preview (general) = stale `https://hr-dx-peter-rizzos-projects.vercel.app` (open item).
- `prv3-engine`: `ANTHROPIC_API_KEY` Production (`prv3-engine-production` key) + Preview (`vercel-routing-migration`). `ENGINE_SECRET` Production + Preview. SSO protection off project-wide (approved). Bypass secret rotated.
- Domains on `prv-3` Production: `hr-dx.com`, `www.hr-dx.com`, `principalresolution.com`, `www.principalresolution.com`, `prv-3.vercel.app`.

## Open

- Delete two Production test records from Redis `diagnostic-aggregate` (Pete -- see 13b for identification: industry "Technology", organization_size 175, top state "Built to Fail", completed_at ~2026-09-26T23:59:5xZ and ~2026-09-27T00:00:3xZ, remove with `LREM`). Unverified whether Preview shares the same Upstash instance.
- hr-dx "About this report" drawer copy revisit -- due now that F/I/J is live.
- Copy residuals: PR compound grammar ("A and B is built..."), occasional em-dash in AI-generated narrative questions.
- Stale general-Preview `ENGINE_BASE_URL`.
- `.claude/launch.json` unstaged local change (kept out of every commit).
- `vercel-routing-migration` branch still exists (fully merged, safe to delete -- Pete's call).
- `tools/diagnostic_fast_forward.py` rework-or-retire (stale intake, no narrative handling).
- Section 16 logging gap for the 2026-09-24/25 pre-session hr-dx work (flagged, not backfilled).

## Parked

Unchanged from Section 13b's "Explicitly parked" list.

## Dated items

- Next Quarterly Step-Back due **2026-10-03**.

## Files to attach next session

- Always: `tools/_mob.txt`.
- hr-dx copy work: `engine/output_synthesis.py`, `engine/narrative.py`, `engine/resolution_families.py`, `web/data/orientation-copy.ts`, `web/components/ResultsOrientationHR.tsx`, this file.
- fast_forward rework: `tools/diagnostic_fast_forward.py`, `web/app/api/diagnostic/session/start/route.ts`, `web/app/api/diagnostic/session/narrative/route.ts`.
- Vercel config changes: this file.
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    mob = MOB.read_bytes().decode('utf-8')  # preserve CRLF (read_text would normalize to LF)
    orig_len = len(mob)
    edits = [
        ('\\\\\\#\\\\\\# MOB v4.325', '\\\\\\#\\\\\\# MOB v4.326', 'version header'),
        (OLD_FF, NEW_FF, '13b fast_forward item'),
        (ANCHOR_OPEN_END, ANCHOR_OPEN_END + crlf(NEW_OPEN_ITEMS), '13b new open items'),
        (OLD_UPSTASH, crlf(NEW_UPSTASH), '13b infra carry-forwards'),
        (ANCHOR_FILES, crlf(NEW_FILES), '13b files to attach'),
        (OLD_LAST, NEW_LAST_PREFIX, '13b last-updated line'),
    ]
    for old, new, label in edits:
        n = mob.count(old)
        if n != 1:
            print(f'ERROR: MOB :: {label} anchor found {n} times.', file=sys.stderr)
            sys.exit(1)
        mob = mob.replace(old, new, 1)
        print(f'[MOB :: {label}] OK')

    i = mob.find(S14_ANCHOR)
    if i < 0 or mob.count(S14_ANCHOR) != 1:
        print('ERROR: Section 14 anchor row not unique.', file=sys.stderr)
        sys.exit(1)
    line_end = mob.index(NL, i)
    mob = mob[:line_end] + NL + NL + S14_ROW + mob[line_end:]
    print('[MOB :: Section 14 row] OK')

    if not mob.rstrip().endswith('MOB v4.325.'):
        print('ERROR: MOB does not end with the expected prior closeout line.', file=sys.stderr)
        sys.exit(1)
    mob = mob.rstrip('\r\n') + crlf(S16) + NL
    print('[MOB :: Section 16 entry appended] OK')

    claude = CLAUDE.read_text(encoding='utf-8')
    if claude.count('| MOB version | v4.325 |') != 1:
        print('ERROR: CLAUDE.md MOB version row not found exactly once.', file=sys.stderr)
        sys.exit(1)
    claude = claude.replace('| MOB version | v4.325 |', '| MOB version | v4.326 |', 1)
    print('[CLAUDE.md :: MOB version] OK')

    if HANDOFF.exists():
        print(f'ERROR: {HANDOFF} already exists (handoffs are additive, never overwritten).', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f'DRY RUN -- all anchors found. MOB would grow by {len(mob) - orig_len} chars. Nothing written.')
        return
    MOB.write_text(mob, encoding='utf-8', newline='')
    CLAUDE.write_text(claude, encoding='utf-8')
    HANDOFF.write_text(HANDOFF_CONTENT, encoding='utf-8')
    print(f'WROTE: {MOB}\nWROTE: {CLAUDE}\nWROTE: {HANDOFF}')


if __name__ == '__main__':
    main()
