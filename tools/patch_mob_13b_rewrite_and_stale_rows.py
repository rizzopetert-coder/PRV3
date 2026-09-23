"""
tools/_mob.txt -- combined pass, four edits, per Pete's explicit instructions
(2026-09-23, "cleanup pass" session): Section 13b wholesale rewrite, four
Section 13 stale-row closures, a new Section 16 DATED NOTE (folding in the
Step 6 closeout-protocol-amendment line since Steps 1-5 aren't committed
yet), and the header version bump v4.323 -> v4.324.

Section boundaries for 13b are found programmatically (searching for the
unambiguous plain substrings "13b. Session Priority Queue" and
"14. Locked Decisions Log", then trimming backward through the preceding
backslash-escaped header markers) rather than hand-transcribing the
backslash run-lengths -- this file uses inconsistent escaping across
different rows (plain "--" in most body text, real em-dashes in a few
specific rows, a 3-backslash-per-hash convention on top-level section
headers only) and hand-copying it wrong once already produced a silent
mismatch during this same session's drafting. Programmatic boundary
detection removes that whole class of error.

Usage:
    python tools/patch_mob_13b_rewrite_and_stale_rows.py --dry-run
    python tools/patch_mob_13b_rewrite_and_stale_rows.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

# -- Edit 1: header version bump ---------------------------------------------
HEADER_OLD = 'MOB v4.323\n'
HEADER_NEW = 'MOB v4.324\n'

# -- Edit 2-5: four Section 13 stale rows ------------------------------------
ROW_ANCHORS = [
    (
        '| Service-specific path design | How each of the four resolution services presents on the site. What a practitioner-directed arrival finds. |\n',
        '| Service-specific path design | How each of the four resolution services presents on the site. What a practitioner-directed arrival finds. **CLOSED -- superseded, 2026-09-23.** Shipped: four dedicated landing pages at the live routes /people-tactics-and-strategy, /training-and-development, /executive-advisory, /first-call (confirmed via `ls web/app`, 2026-09-23), each with full locked body copy and a diagnostic CTA -- commits `bdd5624` (People Tactics & Strategy), `7604da5` (Training & Development), `fcce77f` (Executive Advisory), all 2026-09-21; routes themselves created in `f4568c7` (2026-09-21 00:44, "feat: service tier landing pages + persistent sidebar, route renaming"). |\n',
    ),
    (
        '| Menu execution layout | How the two-tier structure looks on the page. Weight and position of Diagnostic relative to the four. |\n',
        '| Menu execution layout | How the two-tier structure looks on the page. Weight and position of Diagnostic relative to the four. **CLOSED -- superseded, 2026-09-23.** Shipped in commit `f4568c7` (2026-09-21 00:44, "feat: service tier landing pages + persistent sidebar, route renaming"): `ServiceSidebar.tsx` renders the four-section stacked sidebar on every route except /diagnostic, where it collapses to a discreet "SERVICES" trigger strip -- the exact weight/position-of-Diagnostic-relative-to-the-four question this row asked, confirmed directly in that commit message. Refined in `ade8ead` (left-move/gap-spacing) and `53545d4` (scroll-fix), both 2026-09-21. |\n',
    ),
    (
        '| FullInstrumentPlaceholder copy | Review and adjust before deployment. Current: "The full diagnostic is being prepared." — placeholder copy only. |\n',
        '| FullInstrumentPlaceholder copy | Review and adjust before deployment. Current: "The full diagnostic is being prepared." — placeholder copy only. **CLOSED -- moot, 2026-09-23.** The component no longer exists anywhere in the codebase (zero grep matches, confirmed 2026-09-23) -- replaced by the real DiagnosticFlow component, commit 37ab8a7, per the Path 1 row below. |\n',
    ),
    (
        '| TransitionBar threshold | Phase 1→2 fires at ≥3 states || ≥1 signature selected. Confirm this threshold is correct against live usage before deployment. |\n',
        '| TransitionBar threshold | Phase 1→2 fires at ≥3 states || ≥1 signature selected. Confirm this threshold is correct against live usage before deployment. **CLOSED -- moot, 2026-09-23.** The component no longer exists anywhere in the codebase (zero grep matches, confirmed 2026-09-23). |\n',
    ),
]

# -- Edit 6: Section 13b wholesale rewrite -----------------------------------
NEW_13B_BODY = '''Forward-looking session state, confirmed with Pete at closeout. Updated at each session close so a fresh session can pick up cleanly with no lost context. Not a Tier 3 Decision Register item -- a working queue, expected to be rewritten wholesale each time it's updated rather than accumulate history like 13a.

Priority order for next session, in sequence. **Rewritten wholesale 2026-09-23** (full verification pass against live repo state and the last three Section 16 closeouts, Pete's explicit sequencing -- full detail in Section 16's 2026-09-23 dated note):

1. Severity follow-on state-scoping gate -- live production defect. `severity_trigger` fires without awareness of the respondent's destination state. Two gate designs falsified on real data. Next step: third design proposal through Gemini gate, not a build.
2. 92 pre-existing WCAG AA contrast failures (`.text-gray-400`/`.text-gray-500` eyebrow labels, `/about/*` and `/book/memo|case_pattern/*`). Likely single shared-component fix. Verify via `tools/sleuth` before/after.
3. Training & Development teaser -- consolidate the three hardcoded copies (`ServiceSidebar.tsx`, `training-and-development/page.tsx`, `ServicesPageContent.tsx`) into one shared source.
4. sleuth P-10 coined-term scan -- gated on Pete authoring the enumerated term list.
5. book-manifest.ts -- 55 remaining teaser em-dashes, voice pass requiring Pete's review.

Open, not sequenced -- real items, no forced check-in, Pete's call when to pick each up:
- Citation sourcing Phase 2 (FTA-18-FTA-53) -- 36 pieces, not started.
- `private_output.resolution_routing` stale values -- engine debt, deferred to Phase 3; `engine/data/states.py` still serializes pre-S32 service names, bypassed today by the TypeScript `STATE_RESOLUTION_FAMILY` map.
- Service Expectations page -- draft complete, attorney-unreviewed, awaiting Pete's own read. No live route, no code placement.
- SEVER-09/Q27A -- parked, reconfirmed unreachable 2026-09-23 via a fresh `diagnostic_question_audit.py` run.
- `tools/diagnostic_fast_forward.py` -- confirmed structurally unusable against current infrastructure, rework-or-retire decision still undecided.
- OSHA actual-average-penalty backfill -- deferred per Addendum 9, 17 of 22 last-confirmed 2026-09-05; not re-derivable in code, since no live data structure exists yet to count against.
- `StateDrawer`/`AssemblyPanel` mutual viewport overlap on `/diagnostic` -- unverified. Both mount simultaneously on that route; whether they visually collide with each other has not been checked (distinct from `ServiceSidebar`'s own, already-resolved collision risk with them, closed 2026-09-20).
- 12-file salience-pilot cluster (`tools/_salience_pilot_*`) -- unchanged since 2026-08-27, own dedicated pass still pending.
- Bucket 1 remainder -- `gemini_prompts/`, `gemini_responses/`, `qsm_extracted.txt`, `qualitative_review.py`. The 7 `.docx` files previously tracked under this name were tracked and citation-updated 2026-08-29 (commit `060fac9`); this 4-item set is what's actually still pending.
- `tools/patch_*.py` accumulation -- 463 files as of 2026-09-23, replacing the stale "68-file held-recent" framing (that figure couldn't be reconciled against current state -- see Section 16's 2026-09-23 dated note). Needs its own dedicated pass.

Infrastructure carry-forwards, tracked only in Section 16 closeouts until now:
- `gh` CLI still not installed -- needs Pete interactively (a `winget` attempt hit a UAC prompt with nobody present to approve).
- Local dev Upstash Redis credentials missing -- informational only, production already has them.
- Function Storage remediation not executed.
- Dropbox Sign provisioning unconfirmed.
- Next Quarterly Step-Back due **2026-10-03**.

Explicitly parked, do not resurface unless Pete reopens:
- Attorney review of engagement agreement Section 3.
- LinkedIn 19-week content calendar.
- LinkedIn BD legal read -- on hold pending attorney review of the four OneDigital covenant provisions (Sections 4/5, 8, 2/9, 7).
- Category E Direction 2 (shelved).
- Real Transaction Path Phase 2 (the Dropbox Sign webhook) and pricing/checkout display -- Phase 1 itself already shipped 2026-08-25 and needs no further work to keep functioning.

Closed since the 2026-09-07 rewrite, dropped from the active list entirely -- full detail Section 13a and Section 16, not reproduced here: the four 2026-09-07 numbered priority items (Legal/Compliance friction-tax wiring -- Block 4d shipped; PARTIAL coverage-threshold verification -- 51/51 CONFIRMED; `extreme_high_confidence` -- root-caused and fixed; v2 token migration -- decided not to migrate, closed as a deliberate non-action, not a completed migration). The ADA/FMLA/OSHA headcount-threshold gating sub-item -- retired, its own framing didn't hold up: the 2026-09-05 gate build covered Clusters 1, 2, 4b, not 5, and Cluster 5 (the actual safety/regulatory cluster) uses a separate statutory-max-curve mechanism by design, never in scope for this gate. The "Bucket 1's 7 .docx files" framing -- superseded, all 7 tracked 2026-08-29, replaced above by the genuine 4-item remainder.

Files to attach next session, categorized by likely next task:
- Always: tools/_mob.txt (current version).
- If resuming the transaction path (parked indefinitely, not an active queue item -- see Explicitly parked above): prompts/real-transaction-path-phase1-gemini-request.md, web/app/engage/page.tsx, web/app/api/engage/initiate/route.ts.

Last updated: This session (Claude Code), 2026-09-23 -- full wholesale rewrite following a complete verification pass of the prior 2026-09-07 priority order against live repo state and the last three Section 16 closeouts (all four numbered items confirmed genuinely closed; open items reconciled against Section 13 and recent closeouts; two framing errors retired). Full detail: Section 16's 2026-09-23 dated note. (Prior update: 2026-09-07 -- full resequencing per Pete's explicit 4-item priority order.)

'''

# -- Edit 7: new Section 16 DATED NOTE, appended at end of file -------------
DATED_NOTE = '''## DATED NOTE (2026-09-23) -- Section 13b reconciled against live repo
## state, four numbered items confirmed closed, protocol gap named

Section 13b (Session Priority Queue) sat unrewritten from 2026-09-07 through this date -- 16 days across which all four of its numbered priority items closed, and several new open items accumulated in Section 13 and three separate Section 16 closeouts, without 13b ever reflecting any of it. This session ran a full verification pass against live repo state (not the MOB's own prior claims) before rewriting 13b wholesale (see Section 13b above).

**All four 2026-09-07 numbered items confirmed genuinely closed, each independently verified against live source, not just re-read from the MOB:**
- **#1 Legal/Compliance wiring** -- closed via commit `fba8f62` ("ui: render legal_tail_risk_exposure -- Block 4d"). Confirmed live in `web/components/PrivateOutput.tsx` today.
- **#2 PARTIAL coverage-threshold verification** -- closed 2026-09-09, 51/51 jurisdictions CONFIRMED, 0 PARTIAL. Enforced by a module-load `assert` at `engine/friction_tax.py:2933`; independently counted live via direct import, not just trusted.
- **#3 `extreme_high_confidence`** -- closed via the root-cause fix (`the_paper_tiger`'s stale `primary_dimension`, Aptitude -> Authority, `engine/data/states.py`). Reconfirmed via a fresh full calibration run this session: `extreme_high_confidence OK`, 171/175 overall, matching the documented baseline.
- **#4 v2 token migration** -- closed as **"decided not to migrate," not a completed migration.** `--home-ink` was deliberately kept isolated from `--ink`, confirmed still distinct in live `web/app/globals.css` today. Flagging this distinction explicitly since "closed" alone could be misread as "homepage now uses v2 tokens" -- it does not.

**Headcount-gating framing correction:** the retired "ADA/FMLA/OSHA headcount-threshold gating for Legal/Compliance Clusters 1, 2, 5" item never matched the code as stated. The 2026-09-05 state-aware coverage-threshold gate build covered Clusters 1, 2, 4b only (`engine/friction_tax.py:2329`). Cluster 5 (safety/regulatory, the actual OSHA-adjacent cluster -- `the_unreported_hazard`, `the_unlocked_door`, `invisible_burnout`, and 4 more) uses a separate statutory-max-curve mechanism by design (`engine/friction_tax.py:2324-2327`) and was never in scope for this gate at all. Not a partial closure -- a framing error, corrected by retiring the item rather than resequencing it.

**Diagnostic question audit regenerated** (separate commit, `8985560`): CORE 42 -> 47, UNREACHABLE 22 -> 17, flagged 96 -> 94 of 101. Q35-Q39 moved UNREACHABLE -> CORE (commit `e8f82a8` wired Q35's stale branch, pulling Q36-39 with it); Q05 lost its missing-option flag (commit `369c1c9`). SEVER-09/Q27A unchanged -- reconfirmed still genuinely unreachable.

**Section 13 stale rows closed, moot rather than actioned:** `FullInstrumentPlaceholder copy` and `TransitionBar threshold` -- zero grep matches for either component anywhere in the codebase, both components no longer exist. `Service-specific path design` and `Menu execution layout` -- superseded by the shipped service landing pages and `ServiceSidebar` (2026-09-20/21 closeouts). All four rows marked CLOSED with a dated note in place, not deleted, per standing discipline for correcting prior claims in an authoritative source.

**Process gap named plainly:** 13b was not rewritten at any closeout between 2026-09-07 and 2026-09-23 despite four separate closures landing against it in that window -- the standing "rewritten wholesale each time it's updated" convention held for the rewrite mechanics once triggered, but nothing was checking whether a rewrite was due in the first place. **Closeout protocol amended: a Section 13b currency check added to CLAUDE.md's Closeout Protocol (new Step 1a, ahead of Step 2's Section 16 write), to prevent a recurrence of this 2026-09-07 to 2026-09-23 staleness gap.** Checked directly for any restatement of the closeout protocol elsewhere in this MOB (e.g. Section 12) that would also need the matching step -- none exists; Section 12 only cross-references CLAUDE.md's own Startup/Closeout Protocol steps, it doesn't restate them. Nothing else to amend.

MOB v4.324.
'''


def build_span_replacement(content: str) -> str:
    start_marker = '13b. Session Priority Queue'
    end_marker = '14. Locked Decisions Log'

    start_text_idx = content.index(start_marker)
    end_text_idx = content.index(end_marker)

    # Walk backward from each marker's start to include its preceding
    # backslash-escaped "#" run (however many backslashes it actually is),
    # so the header bytes are preserved byte-for-byte without hand-typing them.
    def header_start(idx: int) -> int:
        j = idx
        # back over "# " / "#" immediately before the marker text
        while j > 0 and content[j - 1] in ('#',):
            j -= 1
        while j > 0 and content[j - 1] == '\\':
            j -= 1
        return j

    real_start = header_start(start_text_idx)
    real_end = header_start(end_text_idx)

    old_span = content[real_start:real_end]

    # Preserve the original "---" divider immediately before Section 14
    # (however many backslashes precede it) rather than re-authoring it --
    # find the last "---" in old_span, then walk back over its backslash run.
    dash_idx = old_span.rfind('---')
    if dash_idx == -1:
        raise RuntimeError('Could not find the "---" divider before Section 14 -- aborting.')
    j = dash_idx
    while j > 0 and old_span[j - 1] == '\\':
        j -= 1
    divider_and_tail = old_span[j:]  # backslash run + "---" + trailing blank line(s)

    header_prefix = content[real_start:start_text_idx]  # the backslash run + "#" before "13b..."
    new_span = header_prefix + start_marker + '\n\n' + NEW_13B_BODY
    new_span = new_span.rstrip('\n') + '\n\n' + divider_and_tail

    return content[:real_start] + new_span + content[real_end:]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    original_len = len(content)
    new_content = content

    # Edit 1: header version bump
    if new_content.count(HEADER_OLD) != 1:
        print(f'ERROR: header version anchor found {new_content.count(HEADER_OLD)} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    new_content = new_content.replace(HEADER_OLD, HEADER_NEW, 1)

    # Edit 2-5: four stale rows
    for old, new in ROW_ANCHORS:
        count = new_content.count(old)
        if count != 1:
            print(f'ERROR: row anchor found {count} times, expected 1.', file=sys.stderr)
            print(f'Anchor: {old[:120]}', file=sys.stderr)
            sys.exit(1)
        new_content = new_content.replace(old, new, 1)

    # Edit 6: Section 13b wholesale rewrite
    new_content = build_span_replacement(new_content)

    # Edit 7: Section 16 DATED NOTE append -- matches the file's own
    # established separator between adjacent Section 16 entries: blank
    # line, plain "---" (no backslash escaping -- that's inline body
    # markdown, not a top-level section divider), blank line.
    new_content = new_content.rstrip('\n') + '\n\n---\n\n' + DATED_NOTE.strip('\n') + '\n'

    if args.dry_run:
        print('DRY RUN -- all anchors found, span replacement + append applied cleanly.')
        print(f'Old length: {original_len}, new length: {len(new_content)}, delta: {len(new_content) - original_len}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {original_len}, new length: {len(new_content)}, delta: {len(new_content) - original_len}')


if __name__ == '__main__':
    main()
