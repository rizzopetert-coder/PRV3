"""
tools/_mob.txt -- session closeout, v4.324 -> v4.325. First live run of
CLAUDE.md's new Step 1a (Section 13b Currency Check). Three edits:

1. Section 13b item 2: add the sleuth-baseline-trust precondition.
2. Section 13b "Files to attach": add the book-manifest em-dash scan entry
   for item 5.
3. Section 13b "Last updated" line: reflect this amendment pass.
4. Header version bump v4.324 -> v4.325.
5. New Section 16 closeout entry appended, covering the whole session.

Usage:
    python tools/patch_mob_session_closeout_20260923.py --dry-run
    python tools/patch_mob_session_closeout_20260923.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

HEADER_OLD = 'MOB v4.324\n'
HEADER_NEW = 'MOB v4.325\n'

ITEM2_OLD = '2. 92 pre-existing WCAG AA contrast failures (`.text-gray-400`/`.text-gray-500` eyebrow labels, `/about/*` and `/book/memo|case_pattern/*`). Likely single shared-component fix. Verify via `tools/sleuth` before/after.\n'
ITEM2_NEW = '2. 92 pre-existing WCAG AA contrast failures (`.text-gray-400`/`.text-gray-500` eyebrow labels, `/about/*` and `/book/memo|case_pattern/*`). Likely single shared-component fix. **Precondition, added 2026-09-23:** the committed baseline (`tools/sleuth/output/sleuth_report.md`, commit `47aca05`) could not be independently confirmed fresh -- its crawl\'s build state is unrecoverable (`.next/BUILD_ID` is overwritten on every build, no historical snapshot survives) and the build-freshness check (commit `99d9834`) postdates that crawl and only runs when `--skip-build` is passed, not automatically on every run. Circumstantial signals lean trustworthy (its 92-count matches this item\'s own figure exactly, with no apparent ServiceSidebar contamination, and its commit message describes a deliberate before/after verification), but circumstantial isn\'t verified. **Run a fresh `tools/sleuth` crawl against a freshly-rebuilt `.next` before touching this fix, and treat that fresh crawl -- not `47aca05` -- as the real before/after baseline.**\n'

ATTACH_OLD = '- If resuming the transaction path (parked indefinitely, not an active queue item -- see Explicitly parked above): prompts/real-transaction-path-phase1-gemini-request.md, web/app/engage/page.tsx, web/app/api/engage/initiate/route.ts.\n'
ATTACH_NEW = '- If resuming the transaction path (parked indefinitely, not an active queue item -- see Explicitly parked above): prompts/real-transaction-path-phase1-gemini-request.md, web/app/engage/page.tsx, web/app/api/engage/initiate/route.ts.\n- If resuming book-manifest.ts\'s teaser em-dash pass (item 5): prompts/book-manifest-emdash-scan-2026-09-23.md, web/lib/book-manifest.ts.\n'

LASTUPDATED_OLD = 'Last updated: This session (Claude Code), 2026-09-23 -- full wholesale rewrite following a complete verification pass of the prior 2026-09-07 priority order against live repo state and the last three Section 16 closeouts (all four numbered items confirmed genuinely closed; open items reconciled against Section 13 and recent closeouts; two framing errors retired). Full detail: Section 16\'s 2026-09-23 dated note. (Prior update: 2026-09-07 -- full resequencing per Pete\'s explicit 4-item priority order.)\n'
LASTUPDATED_NEW = 'Last updated: This session (Claude Code), 2026-09-23 (closeout pass) -- item 2 amended with the sleuth-baseline-trust precondition, item 5\'s files-to-attach entry added, per the first live run of CLAUDE.md\'s Step 1a (Section 13b Currency Check). Supersedes the same-day wholesale rewrite earlier this session (full verification pass of the prior 2026-09-07 priority order against live repo state and the last three Section 16 closeouts -- all four numbered items confirmed genuinely closed; open items reconciled against Section 13 and recent closeouts; two framing errors retired). Full detail: Section 16\'s 2026-09-23 closeout entry. (Prior update: 2026-09-07 -- full resequencing per Pete\'s explicit 4-item priority order.)\n'

SECTION16_ENTRY = '''## SESSION CLOSEOUT (2026-09-23, terminal Claude Code) -- Section 13b
## verified and rewritten, closeout protocol amended, session leftovers
## disposed of -- MOB v4.324 -> v4.325

**One-line summary:** Section 13b (Session Priority Queue) verified against live repo state and rewritten wholesale after sitting stale 2026-09-07 -> 2026-09-23; the gap that allowed that is closed with a new CLAUDE.md closeout step; every leftover file from tonight's work was individually disposed of, not left to accumulate; and a sleuth-baseline trustworthiness question was investigated and resolved as "unverified, add a precondition" rather than asserted either way.

### 1. Section 13b verification and rewrite (commit `4584ae9`)

All four of Section 13b's 2026-09-07 numbered priority items independently verified against live source, not re-read from the MOB's own prior claims: **#1 Legal/Compliance wiring** closed via commit `fba8f62` (Block 4d renders `legal_tail_risk_exposure`, confirmed live in `PrivateOutput.tsx`). **#2 PARTIAL coverage-threshold verification** closed 2026-09-09, 51/51 jurisdictions CONFIRMED, enforced by a module-load `assert` at `engine/friction_tax.py:2933`, independently counted via direct import. **#3 `extreme_high_confidence`** closed via `the_paper_tiger`'s stale `primary_dimension` fix, reconfirmed with a fresh calibration run: `extreme_high_confidence OK`, 171/175 overall. **#4 v2 token migration** closed as "decided not to migrate," not a completed migration -- `--home-ink` deliberately kept isolated from `--ink`, confirmed still distinct in live `globals.css`. The ADA/FMLA/OSHA headcount-gating sub-item was retired outright: its framing never matched the code -- the 2026-09-05 gate build covered Clusters 1, 2, 4b, and Cluster 5 (the actual safety/regulatory cluster) uses a separate statutory-max-curve mechanism by design, never in scope for that gate. 13b rewritten wholesale with Pete's 5-item priority order (severity follow-on gate, 92-failure contrast debt, T&D teaser consolidation, sleuth P-10 scan, book-manifest.ts em-dashes), open items reconciled against Section 13 and the last three closeouts.

### 2. Closeout protocol amended (commit `3dbecff`)

New CLAUDE.md Step 1a -- Section 13b Currency Check -- inserted between Step 1 (Diary Write) and Step 2 (Update MOB), so it shapes the Section 16 entry rather than just following it. Exists to close the exact gap that let 13b sit unrewritten for 16 days while four closures landed against it with nothing checking whether a rewrite was due. Checked Section 12 directly for any restatement of the closeout protocol that would also need the matching step -- none exists.

### 3. Diagnostic question audit regenerated (commit `8985560`)

`tools/diagnostic_question_audit_output.md` was stale since 2026-08-11. Fresh run: CORE 42 -> 47, UNREACHABLE 22 -> 17, flagged 96 -> 94 of 101. Q35-Q39 moved UNREACHABLE -> CORE (commit `e8f82a8` wired Q35's stale branch, pulling Q36-39 with it); Q05 lost its missing-option flag (commit `369c1c9`). SEVER-09/Q27A unchanged, reconfirmed still genuinely unreachable.

### 4. Section 13 stale-row closures (folded into commit `4584ae9`)

Four rows marked `**CLOSED**` in place, not deleted: `FullInstrumentPlaceholder copy` and `TransitionBar threshold` -- both components have zero grep matches anywhere in the codebase, confirmed gone. `Service-specific path design` -- superseded by the four live service landing pages (`/people-tactics-and-strategy`, `/training-and-development`, `/executive-advisory`, `/first-call`, confirmed via `ls web/app`), body copy shipped in `bdd5624`/`7604da5`/`fcce77f`, routes created in `f4568c7`. `Menu execution layout` -- superseded by `ServiceSidebar.tsx` (also `f4568c7`), which renders full weight on every route except `/diagnostic`, where it collapses to a "SERVICES" trigger -- the exact weight/position question the row asked, confirmed directly in that commit's own message.

### 5. Session leftovers disposed of individually (commits `bc61f38`, `7fca29e`, `9b4885d`, `355b425`, `47ad4f6`, `44d9a0b`)

`bc61f38`/`7fca29e` -- the two patch scripts behind tonight's MOB/CLAUDE.md writes, committed per the established convention that these scripts are tracked, not scratch. `9b4885d` -- `book-manifest-emdash-scan.md` relocated to `prompts/book-manifest-emdash-scan-2026-09-23.md` as a dated working input for item 5. `355b425` -- `tools/generate_candidate_review_packet.py` committed after fixing a real reusability defect first: its report header hardcoded `"Warm theme, 107 pages"` as a literal string instead of reading `theme`/`pageCount` from the crawl JSON, which would have silently mislabeled any future run against a different crawl. Now derives both fields live. `47ad4f6` -- `tools/sleuth/README.md:72` corrected; it read `"(gitignored, regenerated each run)"`, which was true when written but went stale the moment commit `47aca05` deliberately started tracking `sleuth_report.md`. `44d9a0b` -- `.gitignore` gained an entry for the three per-theme scratch crawl dirs (`tools/sleuth/output_{warm,dark,neutral}/`) generated during tonight's investigation, verified via `git check-ignore -v` before committing that the pattern does not touch the tracked `tools/sleuth/output/` directory. The stale, superseded `content-candidate-review-packet.md` was deleted outright (untracked, served no open item, regenerable on demand by the now-fixed generator).

### 6. The sleuth-tracking question, and why it was correctly a dead end

Proposed stopping tracking of `sleuth_report.md` as regenerable churn, per the general instinct that crawl output shouldn't live in git. Checked before acting, per standing discipline: both commit `47aca05`'s own message and a dated `.gitignore` comment (lines 27-31) record this as Pete's deliberate 2026-09-22 call -- a regenerated report is committed as evidence of a specific fix, not automatically. Correctly stopped, nothing touched. The README's stale line (item 5 above) is what generated the question in the first place -- the actual policy was never in doubt once the commit history and `.gitignore` comment were checked directly.

### 7. The restored crawl, and the baseline-trust investigation it triggered

Earlier this session, a fresh 3-theme sleuth crawl was run and `tools/sleuth/output/sleuth_report.md` was promoted from one of those crawls, overwriting the committed version locally. That promotion was never committed and was investigated, not assumed clean: deterministic findings read 216 -> 230 (up) and candidate findings read 247 -> 190 (down) against the committed baseline. The deterministic increase is **not a regression** -- it traces to the crawl having been served from the stale `.next` build (mtime 2026-09-21 23:38:23 UTC) that predated the ServiceSidebar contrast fix (`3d82192`, 2026-09-22 15:11:49 UTC), the exact staleness class the build-freshness check (commit `99d9834`) was built to catch. The candidate decrease genuinely does trace to commit `c739571` (the finite-verb heuristic tightening), which operates on already-crawled text regardless of build freshness. Because half the artifact was unreliable, none of it was committed as evidence -- `git restore` returned the file to the `47aca05` baseline.

That restoration raised a sharper question, investigated as this closeout's pre-step: is the **committed** `47aca05` baseline itself trustworthy for 13b item 2's before/after? **Verdict: unrecoverable, not confirmed clean.** `.next/BUILD_ID` is overwritten on every build -- there is no way to retroactively confirm what build `47aca05`'s crawl was served from, and the build-freshness check postdates that crawl entirely (it did not exist yet) and in any case only fires when `--skip-build` is explicitly passed, never automatically. Circumstantial signals lean toward trustworthy: its real-AA-finding count (92) matches this item's own separately-tracked figure exactly with no apparent ServiceSidebar contamination, and the commit message describes a deliberate before/after verification methodology ("clears every page the ServiceSidebar teaser renders on, not just the one checked first"). But circumstantial isn't verified, and this session's own standing discipline is not to assert freshness without being able to check it directly. Section 13b item 2 now carries an explicit precondition: a fresh crawl against a freshly-rebuilt `.next` is required before that fix proceeds, and that fresh crawl -- not `47aca05` -- is the real before/after baseline.

### 8. Section 13b Currency Check (Step 1a), first live run

**13b checked, and amended** -- not "no change." Two edits landed against the same-day rewrite: item 2 gained the baseline-trust precondition above; the "Files to attach" list gained an entry for item 5 (`prompts/book-manifest-emdash-scan-2026-09-23.md`, `web/lib/book-manifest.ts`). No other closure or new open item from tonight's work required a 13b change beyond these two -- checked explicitly, not assumed.

**Files changed, git-confirmed:** `tools/_mob.txt` (this closeout's full pass, v4.324 -> v4.325), `CLAUDE.md` (MOB version cross-reference), `prompts/session-handoff-v4.325.md` (new).

**Open items carried forward:** unchanged from Section 13b's 2026-09-23 rewrite except the two amendments above. Next Quarterly Step-Back due **2026-10-03**, unchanged.

**Anything Pete should know at next session start:** this is the first live run of Step 1a -- worth confirming at the next closeout that it actually caught what it was built to catch, rather than becoming a rubber-stamped "no change" by habit. 13b item 2 is now gated on a fresh sleuth crawl against a freshly-rebuilt `.next` -- do not reuse `47aca05` as the before baseline for that fix.

MOB v4.325.
'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    original_len = len(content)
    new_content = content

    for old, new, label in [
        (HEADER_OLD, HEADER_NEW, 'header version'),
        (ITEM2_OLD, ITEM2_NEW, '13b item 2'),
        (ATTACH_OLD, ATTACH_NEW, '13b files-to-attach'),
        (LASTUPDATED_OLD, LASTUPDATED_NEW, '13b last-updated'),
    ]:
        count = new_content.count(old)
        if count != 1:
            print(f'ERROR: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
            sys.exit(1)
        new_content = new_content.replace(old, new, 1)

    # Append Section 16 entry, matching the file's established separator
    # convention between adjacent entries: blank line, plain "---", blank line.
    new_content = new_content.rstrip('\n') + '\n\n---\n\n' + SECTION16_ENTRY.strip('\n') + '\n'

    if args.dry_run:
        print('DRY RUN -- all anchors found exactly once, replacements + append would apply cleanly.')
        print(f'Old length: {original_len}, new length: {len(new_content)}, delta: {len(new_content) - original_len}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {original_len}, new length: {len(new_content)}, delta: {len(new_content) - original_len}')


if __name__ == '__main__':
    main()
