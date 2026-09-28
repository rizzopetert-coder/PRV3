"""
Session closeout 2026-09-27/28 (terminal Claude Code): MOB v4.327 -> v4.328.

Reconstructed at closeout from git 7546b41..b9174e9, this session's reports,
and deployed state (Pete's instruction). Edits:
  1. Version line v4.327 -> v4.328.
  2. Section 13b: driver-steering item extended, 11 new open items added,
     engine-preview upkeep note, files-to-attach and "Last updated" refreshed.
  3. Section 14: five locked-decision rows after the last Section 14 row.
  4. Section 16: closeout entry appended at the end of the file.
  5. CLAUDE.md Key References: MOB version v4.327 -> v4.328.

Usage: python tools/patch_mob_session_closeout_20260928.py --dry-run | --write
"""
import argparse
import pathlib
import sys

MOB = pathlib.Path('tools/_mob.txt')
CLA = pathlib.Path('CLAUDE.md')

VERSION_OLD = r'\\\#\\\# MOB v4.327'
VERSION_NEW = r'\\\#\\\# MOB v4.328'

# ── 13b ─────────────────────────────────────────────────────────────────────
STEER_PREFIX = '- `tools/diagnostic_fast_forward.py` answer-steering is too weak to reach most hr-dx pathways live'
STEER_APPEND = (
    ' **Update 2026-09-27/28:** still open, and wider than hr-dx pathways. It never reached `dueling_narratives` '
    '(Executive Advisory + People Tactics & Strategy), and during the causation-override fix (`79c419d`) it could not '
    'land an override state on hr-dx: 7 completed tagged Production hr-dx runs targeting `the_uninitiated`, '
    '`the_founders_grip`, `decision_paralysis`, `the_broken_compass`, `the_diversity_ceiling`, `the_burned_credibility` '
    'and `wellbeing_theater` all led with compound-family states (`built_to_fail`, `the_suppression_filter`, '
    '`the_overloaded_manager`, `the_unexamined_algorithm`), which the override skips by design. The same '
    '`the_founders_grip`/`decision_paralysis` Emerging targets did reach `the_uninitiated` on principalresolution.com.'
)

NEW_OPEN_ANCHOR = '- Separate Upstash database for Preview -- backlog, deferred by Pete 2026-09-26/27.'
NEW_OPEN = [
    '- Pass 2 content (logged 2026-09-27/28, not started): (1) about 325 answer options have no `observation_text` '
    '(187 core plus 138 SEVER-*, TC-* excluded since zero-signal, counted directly 2026-09-28), so receipts and '
    'evidence can only quote the options that have one. (2) Strength-phrased (`observation_valence="asset"`) text for '
    'the core answers that carry asset signal: reported in session as 37 answers, but a raw count of core options with '
    'any positive `*_asset` contribution gives 67 across 51 questions, so pin the scope before writing. Until this is '
    'written the report\'s asset strength panel shows no quoted evidence for any respondent (0 asset-valence texts '
    'exist, `12fa91d`).',
    '- ShareableOutput never live-tested since the Phase 2 reorder: compile, lint and build only.',
    '- 205 spaced dashes across 91 core questions (house-style pass, not started). TC-* and Q51 are done '
    '(`176e201`, `de4af1a`, `553cd27`).',
    '- Narrative-question intake grounding (Gemini reviewed, not built). Gemini\'s proposed intake field `role_level` '
    'is UNVERIFIED against the real intake schema: it exists in the legacy intake type (`web/lib/types.ts`) and '
    'main.py\'s legacy-intake mapping (where it feeds `principal_role`), while the live Path 1 wire intake sends '
    '`principal_role`. Confirm the live field before any build.',
    '- Web routes\' function duration limit unverified: `session/answer` and `session/narrative` set no '
    '`maxDuration`, and the Vercel CLI cannot read the project default. Check `prv-3` Functions settings in the '
    'Vercel dashboard. Worst-case engine synthesis is now 45s (Call 1 || Call 2 at 30s, then Call 3 at 15s), '
    'measured completions about 19s.',
    '- PR condensed verdict copy reads oddly ("First Call is present in the work...", from the compound backup '
    'copy in `engine/resolution_families.py`). Copy review, Pete\'s call.',
    '- Condensed report locked-indicators line still contains an em-dash (`web/components/CondensedOutput.tsx`, '
    '"All indicators locked — unlock the full diagnostic...").',
    '- `service_cost_comparison.inaction_cost_low/high` still ships in the payload (typed in `web/lib/types.ts`) '
    'with a mixed-timeframe meaning (annual friction plus one-time legal) and is no longer rendered since `bc80783` '
    'split the two. Remove or redefine.',
    '- Executive summary voice still needs tuning: live output opens with lines like "Here\'s the thing:". '
    'Length is fixed (`6c56571`), voice is not.',
]

EP_PREFIX = '- `engine-preview` branch (new 2026-09-26/27, long-lived):'
EP_APPEND = (
    ' Refreshed 2026-09-27/28 by merging `main` (merge `448a9ef`). `diagnostic-aggregate` now holds many tagged '
    '`is_test` records from this session\'s Production verification runs, so always exclude `is_test: true`.'
)

FILES_ANCHOR = '- If resuming book-manifest.ts\'s teaser em-dash pass (item 5):'
FILES_NEW = [
    '- If working on the report (both brands): engine/contract.py (receipts, `_build_asset_evidence`, '
    '`effective_resolution_family`, service_cost_comparison), engine/main.py (`run_accumulated_engine`, three-call '
    'flow), engine/tactical_synthesis.py (Call 2), engine/exec_summary.py (Call 3), web/components/ReportDetails.tsx, '
    'web/components/ConditionsList.tsx, web/components/PrivateOutput.tsx, web/lib/output-text.ts, '
    'tools/test_phase1_report_data.py.',
    '- If writing Pass 2 content: engine/data/questions.py (`observation_text`, `observation_valence`, '
    '`PROBLEM_CONTEXT_VALENCES`), engine/contract.py (`_build_asset_evidence`, `_top_observation_texts`).',
    '- If touching the condensed report: web/components/CondensedOutput.tsx, engine/resolution_families.py '
    '(RESOLUTION_FALLBACK_COPY).',
    '- If doing asset calibration (Tier 1): engine/data/questions.py (SEVER-* 0.25 seeding, Q18-E), '
    'tools/calibration_runner.py.',
]

LAST_PREFIX = 'Last updated: This session (Claude Code), 2026-09-26/27 (final closeout of the hr-dx polish arc)'
LAST_NEW = (
    'Last updated: This session (Claude Code), 2026-09-27/28 (report redesign, override fix, Call 2 timeout) -- no '
    'numbered priority item closed or resequenced, no open-not-sequenced item closed. Extended: driver '
    'answer-steering (dueling_narratives, hr override states), `engine-preview` upkeep. Added: Pass 2 content, '
    'ShareableOutput live test, core-question dashes, narrative intake grounding, web route duration, PR condensed '
    'verdict copy, condensed locked-indicators em-dash, `inaction_cost_*`, executive summary voice. Asset '
    'calibration was already logged (`c9858cc`). Files-to-attach gained four report categories.'
)

# ── 14 ──────────────────────────────────────────────────────────────────────
S14_PREFIX = '| **Cross-assistant operational bridge -- Gemini\'s role expanded to persistent operational assistant** |'
S14_SRC = 'This session (Claude Code), 2026-09-27/28 | MOB v4.328 |'
S14_ROWS = [
    '| **Report architecture: three AI calls with isolated inputs** | LOCKED 2026-09-27, Pete-confirmed, both brands. '
    'Call 1 (output synthesis) is isolated from tactical data. Call 2 (tactical synthesis, '
    '`engine/tactical_synthesis.py`) is fed only the deterministic pre-aggregation (`build_tactical_summary`). Call 3 '
    '(executive summary, `engine/exec_summary.py`) is fed only Call 1\'s liability text and the flagged counts. Call 1 '
    'and Call 2 run in parallel, Call 3 after. A Call 2 or Call 3 failure degrades that piece only (empty findings or '
    'summary), never the report. Timeouts: Call 1 15s, Call 2 30s (`b9174e9`), Call 3 15s. Commits `0141a63`, '
    '`53d2d4d`. | ' + S14_SRC,
    '| **Evidence rule: authored observation text only, valence-gated** | LOCKED 2026-09-27, Pete-confirmed. Receipts '
    'and evidence quote authored `observation_text` only, never raw option text. `observation_valence` gates which '
    'reader may quote it: asset evidence quotes asset-valence text only, receipts and the other problem-context '
    'readers quote liability or neutral only (`PROBLEM_CONTEXT_VALENCES`). Commit `12fa91d`. | ' + S14_SRC,
    '| **Single-state results pass all qualifying states through, collapsed by default** | LOCKED 2026-09-27, '
    'Pete-confirmed. `private_output.all_qualified_states` carries every above-floor state in single and multi mode '
    '(inside `private_output`, the top-level contract stays pinned at 16 fields), rendered as one expandable '
    'conditions list, collapsed by default. Commits `c80f877`, `2a0728e`, `1e8841f`. | ' + S14_SRC,
    '| **Condensed report: locked silhouette and a capped count** | LOCKED 2026-09-27, Pete-confirmed. The condensed '
    'report shows a locked constellation silhouette (no data shape) and a locked "N more conditions" row, where any '
    'count above 3 reads "Several more". Commits `ee6d9fc`, `911852c`, `cb65cdc`. | ' + S14_SRC,
    '| **Pathway, Call 1 and backup copy all read effective_resolution_family** | LOCKED 2026-09-27, Pete-confirmed. '
    '`engine/contract.py` `effective_resolution_family()` (lead state\'s family in both routing modes, then the '
    'causation override) is the single definition of the result\'s family. The displayed pathway, Call 1\'s '
    'resolution_family, the PR backup copy, the hr fallback key and the hr drawer (`hr_pathway`, from '
    '`private_output.resolution_routing`) all read it. Commits `79c419d`, `f990922`. | ' + S14_SRC,
]

# ── 16 ──────────────────────────────────────────────────────────────────────
S16 = r'''

## SESSION CLOSEOUT (2026-09-27/28, terminal Claude Code, same session continued) -- report
## redesign for both brands, bug and copy passes, causation-override fix -- MOB v4.327 -> v4.328

**RECONSTRUCTED AT CLOSEOUT.** Nothing was logged in the MOB between the v4.327 addendum (`7546b41`) and this entry apart from one 13b item (`c9858cc`). This entry is rebuilt from `git log 7546b41..b9174e9` (30 commits, every hash below checked against it), this session's own reports (part of the session was compacted, so earlier work is known from its summary plus git), and the deployed state. Gaps are listed in section 7 rather than filled.

**One-line summary:** the report was redesigned for both brands (silent engine data, then a new layout and five new sections), four user-facing bugs and three copy passes were fixed, the causation override now drives the narrative as well as the pathway, and Call 2's timeout was doubled after a live worst case of 13.9s.

### 1. Four bug fixes

- `9148aba` -- the narrative question read "principal" as a school principal ("your school"). Cause: the prompt's "principal" framing plus no intake in the call. The question now never assumes an organization type.
- `50b573e` -- TC-* questions showed raw IDs and a "Follow-up" label. They now get their own tactical label, and raw question IDs are never shown.
- `a02e9b8` -- Back inside the TC section erased the session. Cause: a `narrative_fired` guard blocked all later undo once an early (Q27) narrative had fired. Undo is now blocked only across the narrative boundary (`narrative_answer_count`).
- `f10d407` -- the intake "Other" field lost focus on every keystroke. Cause: `SignificantEventsField` was defined inside `IntakeForm`, so it remounted each render. Hoisted out.

### 2. Copy passes

- `176e201` TC-HRPOL-01, `de4af1a` the remaining 20 TC-* rewrites (Pete-approved), `553cd27` Q51 options.
- RESOLUTION_FALLBACK_COPY: 2 new compound entries plus em-dash removal on 11 entries (`70f43bb`, `15ff117`, Pete's exact text). The table now has zero em-dashes, and `tools/test_phase1_report_data.py` fails on any new one.

### 3. Report redesign (applies to BOTH brands)

- **Phase 1 engine, shipped silent, then wired in Phase 3:** driving_factors receipts on friction and legal exposure (`5792efd`), asset evidence with the SEVER-* 0.25 baseline subtracted (`fa10703`), `all_qualified_states` and `service_cost_comparison` (`c80f877`, `2a0728e`), the three AI calls (`0141a63`), web types and pass-through (`05afed3`).
- **Valence pass (`12fa91d`):** `observation_valence` on `AnswerOption`, 109 texts tagged (103 liability, 6 neutral, 0 asset). Asset evidence quotes asset-valence text only, receipts and the other observation readers quote liability or neutral only, and receipts vary per condition.
- **Phase 2:** a conditions list replaces the hero and severity sections (`1e8841f`, with the hr-dx bundle airgap kept clean in `c827e4a`). The condensed report redesign has a locked silhouette and a locked-count row (`ee6d9fc`). The count is capped above 3 (`911852c`), and the silhouette is darkened (`cb65cdc`).
- **Phase 3 (`53d2d4d`):** executive summary, tactical synthesis with the raw answers collapsed, receipts, cost comparison, and an asset strength panel. Follow-up fixes: the lead state's resolution family for multi-state results (`9c55695`), the executive summary held to 2-3 sentences with a prompt rule plus a guard (`6c56571`), friction and legal shown as separate figures (`bc80783`), and Copy results including the new sections (`aa1c646`).
- **Causation-override bug (`79c419d`):** the pathway showed the overridden family while Call 1 and the backup copy were written for the pre-override one (live example: `the_uninitiated` plus diffuse showed Training & Development but read as First Call). `effective_resolution_family()` is now the single source for the pathway, Call 1, the backup copy and the hr fallback key, at all three call sites (full engine, self-select Path B, `assemble_output`). A negative control against the old main.py failed 5 of the new checks. Live on principalresolution.com: two tagged Production sessions reached `the_uninitiated` plus diffuse, and both the pathway and Call 1 read Training & Development. On hr-dx.com the driver could not reach an override state (section 5 and 13b). A code trace confirmed the hr drawer reads the same post-override value, pinned by a vitest (`f990922`, test only).
- **Call 2 timeout 15s to 30s (`b9174e9`):** a live Production hr-dx session with all 40 TC answers flagged (`SMpZ1p2mHkjfT_-S0CLnC`) measured call1 8.0s, call2 13.9s, call3 2.2s, and 19.0s for the final request, with tactical findings for all 10 sections and 40 of 40 flagged. Call 1 and Call 3 are unchanged at 15s.

### 4. Lapses, recorded honestly

- `engine/tactical_synthesis.py` and `engine/exec_summary.py` (`0141a63`) were written directly, not through a dry-run patch script. `tools/patch_phase1_three_call.py` states they were "created alongside this script" and only checks they exist. One vitest block was also written directly (Pete-reported, not pinned to a file in this reconstruction).
- `c80f877` was committed with `tools/test_contract.py` failing (the top level went to 17 fields against the pinned 16). The commit command chained the suite and the commit without gating on the result. `2a0728e` fixed it by moving the field into `private_output`. The transcript confirms no push happened in between. Commits are now gated on the suite passing.

### 5. Discovery

Before `9c55695`, most hr-dx results were multi-state, and `private.resolution_family` is populated only in single mode, so they carried an empty resolution family. The hr-dx drawer therefore showed generic copy on most results until then. The earlier reading of these as below-threshold "no routing" results was wrong.

### 6. Section 13b Currency Check (Step 1a)

**13b checked, and amended** -- not "no change." No numbered priority item closed or resequenced, and no open-not-sequenced item closed (none of this session's fixes were 13b items). Extended: driver answer-steering (`dueling_narratives`, hr override states), `engine-preview` upkeep (merge `448a9ef`, `is_test` records). Added: Pass 2 content, ShareableOutput live test, 205 core-question dashes, narrative intake grounding (`role_level` UNVERIFIED), web route duration limit, PR condensed verdict copy, condensed locked-indicators em-dash, `inaction_cost_*`, and executive summary voice. Asset calibration was already logged (`c9858cc`), unchanged. Files-to-attach gained four report categories.

**Section 14:** five locked rows added (report architecture, evidence rule, all qualifying states, condensed report, effective_resolution_family). **Flagged, not moved:** the 2026-09-26 hr-dx Production lock row (MOB v4.326) sits inside Section 16's table (around line 2508), not in Section 14. It is left in place for Pete to decide.

### 7. Gaps this reconstruction cannot fill

- Production READY was confirmed directly only for the engine deploys of `79c419d` and `b9174e9` in the post-compaction part of the session. Earlier per-commit deploy confirmations are known only from the session summary, not re-verified here.
- The Phase 1 to 3 live-test session IDs from before compaction are not all recoverable. Only the ones quoted above are.
- Which vitest block was written directly is not pinned.
- The "37 core answers with asset signal" figure could not be reproduced (a raw count gives 67, see 13b).
- Earlier in the session Claude reported "11 hr-dx production runs" for the override check. The accurate count is 7 completed runs (plus 4 driver runs that wrote no output).

**Test state at close:** 13 Python suites all pass (`tools/test_phase1_report_data.py` 100/100), vitest 130/130, tsc clean.

**Files changed, git-confirmed:** code commits listed above. This closeout: `tools/_mob.txt`, `CLAUDE.md` (MOB version cross-reference), `prompts/session-handoff-v4.328.md` (new), `tools/patch_mob_session_closeout_20260928.py` (new).

**Open items carried forward:** see Section 13b as amended above. Next Quarterly Step-Back due **2026-10-03**.

**Anything Pete should know at next session start:** Startup Protocol did not run at the start of this continued session. Run it in full next time. The report redesign is live on both brands, and the asset strength panel shows no quoted evidence for anyone until Pass 2 is written. `diagnostic-aggregate` holds many tagged `is_test` records from this session, so exclude `is_test: true`.

MOB v4.328.
'''


def edit_line_by_prefix(lines, prefix, fn, label):
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(idx) != 1:
        print(f'ERROR {label}: prefix matched {len(idx)} lines', file=sys.stderr)
        sys.exit(1)
    fn(idx[0])
    print(f'[MOB :: {label}] OK (line {idx[0] + 1})')


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    a = ap.parse_args()

    mob = MOB.read_text(encoding='utf-8')
    if mob.count(VERSION_OLD) != 1:
        print(f'ERROR version line x{mob.count(VERSION_OLD)}', file=sys.stderr)
        sys.exit(1)
    mob = mob.replace(VERSION_OLD, VERSION_NEW, 1)
    print('[MOB :: version v4.327 -> v4.328] OK')

    lines = mob.split('\n')

    def steer(i):
        lines[i] = lines[i] + STEER_APPEND
    edit_line_by_prefix(lines, STEER_PREFIX, steer, '13b driver steering extended')

    def ep(i):
        lines[i] = lines[i] + EP_APPEND
    edit_line_by_prefix(lines, EP_PREFIX, ep, '13b engine-preview upkeep')

    def last(i):
        lines[i] = LAST_NEW
    edit_line_by_prefix(lines, LAST_PREFIX, last, '13b last-updated line')

    def s14(i):
        lines[i:i + 1] = [lines[i]] + [x for row in S14_ROWS for x in ('', row)]
    edit_line_by_prefix(lines, S14_PREFIX, s14, 'Section 14 five rows')

    def new_open(i):
        lines[i:i] = NEW_OPEN
    edit_line_by_prefix(lines, NEW_OPEN_ANCHOR, new_open, '13b nine new open items')

    def files(i):
        lines[i + 1:i + 1] = FILES_NEW
    edit_line_by_prefix(lines, FILES_ANCHOR, files, '13b files-to-attach')

    mob = '\n'.join(lines).rstrip('\n') + S16
    print('[MOB :: Section 16 entry appended] OK')

    # Order check: the new 14 rows must sit inside Section 14, before Section 15.
    i14 = mob.index('| **Report architecture: three AI calls with isolated inputs**')
    if not (mob.index(r'\\\# 14. Locked Decisions Log') < i14 < mob.index(r'\\\# 15. Document Registry')):
        print('ERROR: Section 14 rows landed outside Section 14', file=sys.stderr)
        sys.exit(1)
    i13b = mob.index('- Pass 2 content (logged 2026-09-27/28')
    if not (mob.index(r'\\\# 13b. Session Priority Queue') < i13b < mob.index(r'\\\# 14. Locked Decisions Log')):
        print('ERROR: 13b items landed outside 13b', file=sys.stderr)
        sys.exit(1)
    print('[MOB :: placement checks] OK')

    cla = CLA.read_text(encoding='utf-8')
    old, new = '| MOB version | v4.327 |', '| MOB version | v4.328 |'
    if cla.count(old) != 1:
        print(f'ERROR CLAUDE.md version row x{cla.count(old)}', file=sys.stderr)
        sys.exit(1)
    cla = cla.replace(old, new, 1)
    print('[CLAUDE.md :: MOB version v4.327 -> v4.328] OK')

    if a.dry_run:
        print(f'DRY RUN -- nothing written. MOB would grow by {len(mob) - len(MOB.read_text(encoding="utf-8"))} chars.')
        return
    MOB.write_text(mob, encoding='utf-8')
    CLA.write_text(cla, encoding='utf-8')
    print('WROTE tools/_mob.txt, CLAUDE.md')


if __name__ == '__main__':
    main()
