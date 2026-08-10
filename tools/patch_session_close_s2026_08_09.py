"""
PRV3 -- Session close, 2026-08-09 (per CLAUDE.md's Closeout Protocol).

Covers the full session arc from commit 5f66e07 (validate.py baseline-vector
fix) through fa34b3d (/book/toc hub page), MOB v4.129/v4.130 through v4.135.
Verified against the live repo before writing, not taken from the session
summary alone:
  - Confirmed via `python -m engine.data.validate`-equivalent (direct script
    run): 40/41 passing, the one remaining failure is the already-logged
    cluster_id gap (informational, not a code fix) -- no PRIOR_ADJUSTER_INDEX
    failures remain, so old Priority Queue item 7 is genuinely closed, not
    just "contained half" as its pre-session commit message said.
  - Confirmed via `git log --name-only 5f66e07..fa34b3d` that this session
    never touched friction_tax.py, resolution_families.py, test_contract.py,
    or IntakeEcho/types.ts -- old Priority Queue items 1 (OSHA backfill), 2
    (STATE_CAUSATION_OVERRIDES authoring), 4 (ADA/FMLA/OSHA headcount
    gating), 5 (dated IntakeEcho collapse), and 6 (test_contract.py hidden
    failures) all carry forward unchanged, not re-derived.
  - Confirmed old Priority Queue item 3 (severity-tier 85-profile
    reachability) was already fully resolved in a prior session (81/85
    closed + narrative-fit gap tracked separately in the Decision Register)
    -- moved to closed history, not carried as active.
  - Confirmed current MOB version (v4.135, both tools/_mob.txt and
    CLAUDE.md) via direct grep before bumping.

Usage:
  python tools/patch_session_close_s2026_08_09.py --dry-run
  python tools/patch_session_close_s2026_08_09.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MOB = "tools/_mob.txt"
CLAUDE = "CLAUDE.md"

# ---------------------------------------------------------------------
# 1. Version bump, header.
# ---------------------------------------------------------------------

edit(
    MOB,
    "\\\\\\#\\\\\\# MOB v4.135",
    "\\\\\\#\\\\\\# MOB v4.136",
)

edit(
    CLAUDE,
    "| MOB version | v4.135 |",
    "| MOB version | v4.136 |",
)

# ---------------------------------------------------------------------
# 2. Decision Register (Section 13a) -- two new rows, inserted after the
#    Mechanism 1 deprecation row (the last row in the table).
# ---------------------------------------------------------------------

DR_ANCHOR = (
    "Priority Queue item 7 (validate.py's two now-deprecated-mechanism checks) "
    "remains open, unrelated cadence. |\n"
)

DR_NEW_ROWS = (
    "| A1 (diagnostic usability, free-text \"Other\" option) -- sent to Gemini "
    "for architecture review, awaiting response | 3 | Open -- pending Gemini | "
    "Response not yet received | Category A item A1 (adding a free-text "
    "\"Other\" option to the relevant intake/diagnostic question) was sent to "
    "Gemini for architecture review this session, scoped to the P-03 "
    "clinical-boundary implications of accepting free-text input in a "
    "diagnostic context -- a different concern than the schema-collision "
    "reviews used for prior content batches. Not implemented -- no code "
    "changes made pending Gemini's response. | This session (Claude Code) | "
    "Reopen once Gemini's review returns -- not a scheduled check-in |\n"
    "| Infrastructure findings -- no Preview environment; no custom domain "
    "yet (SSO gates public access) | 3 | Confirmed, informational -- not a "
    "gap, working as intended | N/A | Two infrastructure facts confirmed "
    "directly this session, not assumed. (1) prv-3 has no separate Vercel "
    "Preview environment -- every commit to main deploys straight to "
    "production. This resolved a standing ambiguity in the session's "
    "working assumptions and changed the default workflow going forward: "
    "dry-run -> Pete confirms -> write -> full regression -> commit -> push "
    "in one pass by default, holding only for unretested production-facing "
    "surfaces, structural decisions not yet through Gemini review, or "
    "anything that feels higher-risk in the moment. (2) prv-3 has no custom "
    "domain yet (Porkbun wiring pending) -- Vercel's Deployment Protection "
    "(SSO gate) currently blocks public/unauthenticated access to the "
    "deployed app. Confirmed this is expected, pre-launch behavior, not a "
    "bug or regression -- logged so a future session doesn't rediscover it "
    "as a surprise or spend time debugging apparent inaccessibility. | "
    "This session (Claude Code) | No forced check-in -- reopen only if Pete "
    "begins the custom-domain/Porkbun work, at which point the SSO-gating "
    "behavior needs a deliberate decision about what replaces it |\n"
)

edit(MOB, DR_ANCHOR, DR_ANCHOR + DR_NEW_ROWS)

# ---------------------------------------------------------------------
# 3. Section 13b -- full wholesale rewrite.
# ---------------------------------------------------------------------

NEW_13B = r"""\\\# 13b. Session Priority Queue

Forward-looking session state, confirmed with Pete at closeout. Updated at each session close so a fresh session can pick up cleanly with no lost context. Not a Tier 3 Decision Register item -- a working queue, expected to be rewritten wholesale each time it's updated rather than accumulate history like 13a.

Priority order for next session, in sequence:

1. A1 (Category A, free-text "Other" option) -- with Gemini for architecture review (P-03 clinical-boundary implications), awaiting response. No action until it returns. See Decision Register (Section 13a) for the corresponding row.
2. A5 (Q16/Q29 duplicate removal) + Structure 3 (diagnostic Q37/38/39 core-to-splice conversion) -- parked together, both blocked on the same landmine: engine/accumulation.py:539's `scale = N / 44.0` core-question-count coupling, confirmed via the A5 regression test (170/175->163/175, 58/58->57/58 HC) and Gemini architecture review. Needs a dedicated MC_CENTROID-style recalibration effort (Monte Carlo regen + CENTROID_FIELD_SCALARS reconvergence) before either can proceed -- not a quick fix, comparable scope to the original MC_CENTROID_39 arc. Not scheduled -- Pete to reopen when ready to commit to that effort.
3. A6 (escape-hatch options, Category A) -- explicitly no action. Pete's case-by-case call, not scheduled.
4. Category D (free condensed diagnostic tier, business idea) -- parked, not developed.
5. Category E (branding/visual-identity refresh) -- this session's original ask, never reached. OD-07 rollback rationale confirmed unrecoverable (no diary entry exists for that date, confirmed via search this session) -- revisiting OD-07 is Pete's fresh call, not weighable against documented history that doesn't exist.
6. /book/toc's fuller vision (clusters, media, other intersection vectors beyond the flat state list) -- logged, not scheduled.
7. Q05 (Category B) -- flagged early in this session but never independently re-examined live. Status unclear, worth confirming next session before treating it as resolved or open.
8. OSHA jurisdictional research -- statutory-maximum roster COMPLETE, 22/22 states, zero remaining conflicts or gaps (Addenda 6-8, 12, 13, 14). Actual-average-penalty backfill: confirmed, clean actual-average figures now exist for four states -- Oregon ($604), South Carolina ($2,019), Michigan ($1,217.24, FY2021 FAME report, Addendum 13), and California (FY2023 Comprehensive FAME Report, SAMM 8, size-segmented by headcount, total $8,777.88, Addendum 9, with a supplementary per-inspection SWRU figure added since). Kentucky and Maryland each have an actual-average-shaped figure on record but both are explicitly flagged as not directly comparable (Kentucky pending FRL-percentage confirmation; Maryland predates the 2024 reform). Remaining backfill scope (Washington, Alaska, Hawaii, Arizona, Indiana, Iowa, Nevada, Tennessee, Utah, North Carolina, Puerto Rico, Vermont, Virginia, Wyoming) is explicitly NOT URGENT -- see Addendum 9's own priority framing. Untouched this session.
9. STATE_CAUSATION_OVERRIDES per-state authoring pass -- Pete's own clinical judgment, not started: for states with a single-family default (compound-default states are structurally immune to overrides by design), decide whether and how a session's causation_pattern (single_point vs. diffuse) should route to a different resolution_family than that state's default. STATE_CAUSATION_OVERRIDES ships empty -- zero live effect until entries are authored. UNDATED, deliberately -- no forcing trigger or deadline. Untouched this session.
10. Build ADA/FMLA/OSHA headcount-threshold gating logic for Legal/Compliance Clusters 1, 2, 5 -- currently does not exist anywhere in engine/friction_tax.py. Cluster 1 uses a single flat curve with no org_size parameter; Cluster 2 selects by score only, no headcount involved; Cluster 5 uses a single flat statutory curve with no OSHA 25/100/250 small-business reduction schedule wired in anywhere. Only Cluster 4b has real headcount-bucket-keyed logic today. Building real ADA-15/FMLA-50/OSHA-25-100-250 gating for Clusters 1/2/5 would be new logic, not a fix. Untouched this session.
11. DATED FOLLOW-UP: collapse IntakeEcho.organization_size and AnonymizedCompletion.organization_size from string | number back to number-only, once ShareableOutputPayload's 30-day KV TTL has fully cycled past the deployment carrying commits b76b607/3b5056b/e5f6592. Target date needs reconfirming against the actual push/deploy timestamp when checked -- the original ~September 4, 2026 estimate was computed from a session date before those commits were confirmed pushed. Untouched this session.
12. DATED, test_contract.py sections 12/13: running the full script (unblocked in an earlier session) surfaced 3 pre-existing hidden failures, none caused by that unblocking fix: (a) a friction_tax_estimate CALIBRATION TARGET assertion that assumes the pre-calibration state, likely stale now that Friction Tax Sets 1-3 are fully calibrated; (b) a "passing case" fixture missing the `descriptive_prose` field that the real output schema now includes; (c) a downstream 0-of-3 suite failure caused directly by (b). Not fixed -- flagged, not silently expanded into. Untouched this session.

Closed since last update, not on the active list -- full detail in Section 13a (Decision Register) and Section 16 (Session Log), not reproduced here: validate.py's two remaining failures (baseline-vector check fixed, cluster_id gap explained/logged as inert -- closes the former item 7 for real, distinct from the pre-session "contained half" close of its PRIOR_ADJUSTER_INDEX half); three Friction-Tax documentation status-line-staleness instances found and fixed, repo-wide prompts/*.md sweep confirmed clean; two live production bugs (headcount-stepper literal-escape rendering, flaky-remount input) found via live browser testing, root-caused, fixed, and independently re-verified live; Category A item A4 (Q42 N/A option) shipped; Category B's numbering-scheme confusion resolved via live browser verification, 6+ questions rewritten for self-contained pronoun references, 17 additional text-only edits (Track 1), 2 more targeted rewords plus a new option (Track 2, Q48/Q49), two new conditional follow-up structures shipped (Structure 1 at position 34/Q41 with SEVER-30/31, Structure 2 at position 36/Q43 with SEVER-32) including a real ancestry-labeling fix for follow-up-of-a-follow-up cases, all live-verified in browser; new standing rule locked (multi-item appositive lists use "(such as X, Y, and Z)" parenthetical style, CLAUDE.md); Category C's five items all shipped (synthesis block reorder, asset-tone system-prompt reword, new /book/toc hub page, primary-state descriptive_prose rendering, secondary-state hyperlinks with short-version summaries, welcome/framing intro copy); old Priority Queue item 3 (severity-tier 85-profile reachability gap) -- fully resolved in a prior session, 81/85 closed via the 12-question package (Q40-51) plus the MC_CENTROID_39 recalibration, remaining 4 OPEN items reclassified as PHASE-2-PENDING (blocked on live intake, not a design gap) rather than active work; the leadership_deafness narrative-fit gap stays open and separate, untouched, its own undated future item, not part of this closure.

Files to attach next session, categorized by likely next task:
- Always: tools/_mob.txt (current version).
- If resuming A1 or checking Gemini's response: no new files needed -- check the Gemini thread directly.
- If picking up the A5/Structure 3 recalibration effort: engine/accumulation.py, tools/harness_s27_autonomous_calibration.py, tools/calibration_runner.py (same files as any MC_CENTROID-style effort).
- If continuing Category D (business idea) or Category E (branding refresh): no specific files pre-identified -- neither has been scoped yet, will need discovery work first.
- If checking Q05's status or doing any further diagnostic question review: engine/data/questions.py, web/lib/session-store.ts.

Explicitly parked, not on this list, do not resurface unless Pete reopens: confidentiality template field wording, attorney review of engagement agreement Section 3, LinkedIn 19-week content calendar.

Calibration status as of session close: Friction Tax Sets 1 (ORG_TYPE_SCALARS), 2 (PAYROLL_BASELINE_GRID, 66-cell), and 3 (STATE_MULTIPLIERS, 58 states) all closed and live, unchanged this session. Multi-state compounding design locked and implemented (Option A rescale), unchanged this session. MC_CENTROID_39 recalibration RESOLVED (prior session, IMPASSE at 57/58 HC, since closed to 58/58 via the_inner_circle's added test coverage). Full 172(+3)-profile suite verification held throughout this session's Category A/B/C work at every stage that touched engine or calibration-adjacent code (Structures 1/2), zero regressions -- content/copy-only edits (Category C, Track 1/2 rewording) did not require regression runs and none were claimed.

Last updated: This session (Claude Code), 2026-08-09, session close -- validate.py's two remaining failures resolved, three Friction Tax documentation staleness instances fixed, two live production bugs found and fixed via browser testing, Category A (A4 shipped, A1 sent to Gemini, A5 parked with Structure 3, A6 explicitly not scheduled), Category B (numbering confusion resolved, 25+ question-text edits across two tracks, two new conditional follow-up structures with an ancestry-labeling fix, Structure 3 parked with A5, new appositive-list style rule), Category C (all five items shipped: synthesis reorder, asset-tone reword, /book/toc hub page, descriptive_prose rendering for primary and secondary states, welcome copy), and two infrastructure findings confirmed and logged (no Preview environment -- default workflow updated to commit+push together; no custom domain yet, SSO gates public access as expected). Session closeout: Decision Register updated with 2 new rows (A1 pending Gemini, infrastructure findings), Section 13b rewritten wholesale per standing convention, Section 16 session log entry written covering the full commit arc (5f66e07..fa34b3d).


\\---
"""

# Full-span replacement: header through Section 14's header, replaced
# wholesale (13b's own stated convention -- not an exact-match single edit,
# since reproducing the entire multi-page old body as the "old" side of a
# diff would be both huge and brittle). Located and replaced by start/end
# marker in apply() rather than a static (old, new) tuple.

FULL_SPAN_REPLACEMENTS: list[tuple[str, str, str, str]] = [
    (
        MOB,
        "\\\\\\# 13b. Session Priority Queue",
        "\\\\\\# 14. Locked Decisions Log",
        NEW_13B + "\n",
    ),
]

# ---------------------------------------------------------------------
# 4. Section 16 -- append the session-close log entry at end of file.
# ---------------------------------------------------------------------

SECTION16_NEW_ROW = (
    "| August 2026 -- Session close: validate.py resolved, Friction Tax doc "
    "staleness fixed, two live production bugs fixed, Category A/B/C "
    "shipped, infrastructure findings logged (commits 5f66e07..fa34b3d) | "
    "Full commit arc for this session, MOB v4.129/v4.130 through v4.135. "
    "**validate.py (commit 5f66e07, MOB v4.130):** fixed the baseline-vector "
    "check (flipped from asserting all 58 states remain at BASELINE_VALUE, "
    "a pre-calibration invariant that can never pass again, to asserting "
    "none do) and closed out the cluster_id gap as explained/logged, not "
    "fixed -- 40/41 passing, the one remaining failure is the cluster_id row "
    "itself, informational by design. Re-confirmed this session via a "
    "direct script run before writing this entry: still 40/41, no "
    "PRIOR_ADJUSTER_INDEX failures remain, closing the former Priority "
    "Queue item 7 for real. **Friction Tax documentation staleness (commits "
    "9c4d2bc, b5f3ab0, MOB v4.131/v4.132):** two more instances of the "
    "status-line-fixed-but-body-not-swept pattern found and fixed "
    "(friction-tax-multistate-compounding-methodology.md and "
    "friction-tax-state-multiplier-methodology.md's stale Next-steps "
    "sections), repo-wide prompts/*.md sweep confirmed no further "
    "instances -- third and fourth confirmed occurrences of a pattern first "
    "caught in an earlier session. **Two live production bugs (commit "
    "262b99f, MOB v4.133):** found via Pete's wife's live use of the "
    "diagnostic (the first real, non-Pete user) -- a literal \\u2212 escape "
    "rendering on the headcount stepper's decrement button, and a flaky "
    "controlled-component remount bug on the same field caused by "
    "HeadcountStepper being declared nested inside IntakeForm (redeclared "
    "as a new function reference on every keystroke, forcing React to "
    "remount the underlying DOM). Fixed by hoisting HeadcountStepper to "
    "module scope and correcting the escape-sequence rendering. Flagged, "
    "not fixed: IntakeForm's other two nested render-body helpers "
    "(field(), SignificantEventsField()) carry the identical anti-pattern, "
    "not yet symptomatic since their interaction model is discrete-click, "
    "not keystroke-buffered -- logged as its own Decision Register row. "
    "**Category A (diagnostic usability, commits c1d6986 through f60e115):** "
    "A4 (Q42 N/A option) shipped, commit ffca474. A5 (Q16/Q29 duplicate "
    "removal) attempted, caused a real regression (170/175->163/175, "
    "58/58->57/58 HC), root-caused to engine/accumulation.py:539's "
    "hardcoded scale = N/44.0 coupling -- the same MC_CENTROID_39-style "
    "landmine encountered when Q40-51 were added, reverted cleanly, parked "
    "pending a dedicated recalibration effort. A1 (free-text \"Other\" "
    "option) sent to Gemini for architecture review, P-03 clinical-boundary "
    "implications, awaiting response -- new Decision Register row. A6 "
    "(escape-hatch options) explicitly no action, Pete's case-by-case call. "
    "**Category B (question numbering + content, commits 7627b85 through "
    "1e2a904):** resolved a real on-screen-position-vs-engine-question-id "
    "numbering confusion via live browser verification against "
    "PHASE_1_QUESTION_SEQUENCE's real array contents, not assumption. "
    "Rewrote 6+ questions carrying dangling pronoun references to be "
    "self-contained (commit 52e99ac and follow-ons), then 17 further "
    "text-only edits (Track 1, commit e7d71f7) plus Q21's own "
    "differentiation reword (commit 6525832), plus 2 more targeted rewords "
    "with a new missing option (Track 2, Q48/Q49, commit fd16bcc). Built "
    "and shipped two new Gemini-reviewed conditional follow-up structures: "
    "Structure 1 (3-deep chain at position 34/Q41, SEVER-30/31) and "
    "Structure 2 (2-deep chain at position 36/Q43, SEVER-32), commit "
    "1e2a904 -- including a real fix to spliceLabel() so a follow-up of a "
    "follow-up resolves its ancestry label correctly instead of falling "
    "back to the raw parent ID, live-verified in browser including the "
    "depth-2 edge case. Structure 3 (positions 37/38/39) parked alongside "
    "A5 -- same core-question-count/recalibration landmine, confirmed via "
    "Gemini review plus direct testing; Gemini's review understated this "
    "difficulty, logged as a scope-blindness instance distinct from "
    "citation fabrication. New standing rule locked in CLAUDE.md: "
    "multi-item appositive lists use \"(such as X, Y, and Z)\" parenthetical "
    "style rather than an em-dash-set-off list. **Category C (report "
    "UX/copy, commits 7e2542f, fa34b3d):** all five items shipped -- "
    "synthesis block reordered (observable indicators before prose), "
    "asset-tone system prompt reworded to be less blunt while preserving "
    "honesty, new /book/toc hub page built (all 58 states via existing "
    "descriptive_prose, zero new content authoring), primary state's "
    "descriptive_prose now rendered (mirrors the severity-tier badge "
    "pattern), secondary states now hyperlink to /book/toc#{slug} with a "
    "first-sentence short-version summary beneath each name, and a "
    "welcome/framing message added to the intake phase. New shared "
    "web/lib/state-slug.ts and web/lib/book-state-index.ts extracted for "
    "this and reused rather than duplicated. **Infrastructure findings:** "
    "confirmed no separate Vercel Preview environment exists -- every "
    "commit to main deploys straight to production -- which changed the "
    "session's default workflow to commit+push together, holding only for "
    "unretested production-facing surfaces, structural decisions not yet "
    "through Gemini review, or anything higher-risk in the moment. "
    "Confirmed prv-3 has no custom domain yet (Porkbun wiring pending), so "
    "Vercel's Deployment Protection (SSO gate) currently blocks public "
    "access -- confirmed expected, not a bug. Both logged as new Decision "
    "Register rows this closeout. **Verification held throughout:** full "
    "172(+3)-profile regression run at every engine/calibration-adjacent "
    "checkpoint (Structures 1/2), zero regressions; content/copy-only work "
    "(Category C, Track 1/2 rewording) did not require and did not claim a "
    "regression run. **Session closeout (this entry):** Decision Register "
    "gains 2 new rows (A1 pending Gemini, infrastructure findings); Section "
    "13b rewritten wholesale per standing convention, folding in the "
    "session's still-open items (A1, A5+Structure 3, A6, Category D, "
    "Category E, /book/toc's fuller vision, Q05's unclear status) plus a "
    "files-to-attach breakdown for next session; old Priority Queue item 3 "
    "(severity-tier reachability) confirmed already closed in a prior "
    "session and moved out of the active list; former item 7 "
    "(PRIOR_ADJUSTER_INDEX validate.py checks) confirmed fully closed this "
    "session, not just the pre-session \"contained half.\" | This session "
    "(Claude Code) | MOB v4.136 |\n"
)

def apply(dry_run: bool) -> int:
    changed = 0

    # Simple exact-match single edits.
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 200 chars): {old[:200]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1

    # Full-span replacements (start marker .. end marker, replace the whole span).
    for rel_path, start_marker, end_marker, replacement in FULL_SPAN_REPLACEMENTS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        start_idx = text.find(start_marker)
        if start_idx == -1:
            print(f"ERROR: {rel_path} -- start marker not found: {start_marker!r}")
            return 1
        end_idx = text.find(end_marker, start_idx)
        if end_idx == -1:
            print(f"ERROR: {rel_path} -- end marker not found after start: {end_marker!r}")
            return 1
        old_span = text[start_idx:end_idx]
        new_text = text[:start_idx] + replacement + text[end_idx:]
        if dry_run:
            print(
                f"OK (dry-run): {rel_path} -- span found "
                f"({len(old_span)} chars), would replace with "
                f"{len(replacement)} chars"
            )
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN (span): {rel_path}")
        changed += 1

    # Section 16 append -- insert the new row immediately before the FINAL
    # existing row in the file (the file's last line is the most recent
    # Section 16 entry; Section 16 is the very last section in the file).
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    if not text.rstrip("\n").endswith("MOB v4.130 |"):
        print("ERROR: tools/_mob.txt does not end with the expected v4.130 catch-up row -- refusing to append blindly")
        return 1
    if dry_run:
        print("OK (dry-run): tools/_mob.txt -- would append new Section 16 row at end of file")
    else:
        with path.open("a", encoding="utf-8") as f:
            f.write(SECTION16_NEW_ROW)
        print("WRITTEN (append): tools/_mob.txt -- Section 16 row appended")
    changed += 1

    print(f"\n{changed} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
