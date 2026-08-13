"""
PRV3 -- MOB update, Claude.ai handoff session 2026-08-13.

Three edits to tools/_mob.txt:
(1) Version header v4.150 -> v4.151.
(2) Section 13a (Decision Register): new row -- Category E Direction 2
    shelved, Direction 1 Refinement opened. Gemini review required before
    any build.
(3) Section 13b (Session Priority Queue): rewritten wholesale per standing
    convention -- was stale at its 2026-08-09 snapshot straight through the
    entire 2026-08-11 session, closing that gap now. Q05 marked closed per
    Pete's explicit confirmation this session.

Run with --dry-run first (default). Pass --write to apply.
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path("tools/_mob.txt")

OLD_VERSION = "\\\\\\#\\\\\\# MOB v4.150"
NEW_VERSION = "\\\\\\#\\\\\\# MOB v4.151"

DIRECTION3_ROW_TAIL = (
    "Category E's three-direction sequencing is now fully explored "
    "(Directions 1 and 3 shipped, Direction 2 -- the four-dial "
    "instrument-panel reframe -- remains concept-level, Pete's call "
    "whenever he wants to pick it up) |"
)

NEW_13A_ROW = (
    "| Category E Direction 2 (four-dial instrument panel) -- SHELVED; "
    "Direction 1 REFINEMENT opened (legibility, motion, interpretability) "
    "| 3 | Direction 2 shelved, not reopening without Pete's explicit "
    "call; Direction 1 Refinement approved concept -- Gemini architecture "
    "review required before any build, not done yet | Gemini architecture "
    "review of Direction 1 Refinement has not happened -- touches "
    "ConstellationField's shipped rendering system directly (axis-label "
    "legibility, entrance animation, hover/tap-to-reveal interactivity), "
    "no exception for polish-flavored changes per standing protocol. No "
    "code changes until it clears | Live review of the shipped Direction "
    "1 ConstellationField (prv-3.vercel.app, \"The Uninitiated\" / "
    "Endemic profile) surfaced the real problem wasn't \"one shape vs. "
    "four dials\" -- three concrete gaps found: (1) doesn't feel "
    "dynamic/2026-built, (2) axis labels and on-shape text read too "
    "small to be reader-friendly, (3) no viewer can tell what the shape "
    "means without narration. Direction 2 (four separate dials) would "
    "carry the identical illegibility and interpretability gap, "
    "multiplied by four -- replacing the shape doesn't address either "
    "finding, so Direction 2 no longer has a clear job and is shelved "
    "rather than built. Direction 1 Refinement scoped instead as three "
    "parts: legibility (axis label sizing/weight), motion (CSS-only "
    "entrance animation on load plus hover/tap-to-reveal per vertex, no "
    "Framer Motion per the existing standing call), and interpretability "
    "(the same hover/tap state surfaces plain-brand-voice on-demand "
    "explanation of each dimension's read, resolving the narration gap "
    "without permanently cluttering the shape's resting state). Grounded "
    "in P-06 (Principal Brief): \"The instrument meets the user where "
    "they are... cannot assume the user has done it first\" -- a result "
    "the user can't interpret without outside narration is a direct "
    "P-06 gap, not a polish item. Two durable planning artifacts written "
    "this session in Claude.ai and committed here: "
    "prompts/category-e-direction2-instrument-panel.md (the shelved "
    "spec, kept as the durable record of why -- three shapes considered "
    "for Direction 2's disposition were replace/supplement/shelve, "
    "shelve chosen) and "
    "prompts/category-e-direction1-refinement-legibility-motion.md (the "
    "new refinement spec). New candidate standing communication "
    "principle surfaced, explicitly NOT YET LOCKED, Pete's call on exact "
    "wording and placement (likely a P-06 addendum or its own "
    "governing-principle line, not decided): \"spoon-feed meaning when "
    "not speaking plainly in brand voice\" -- stated as a general "
    "communication standard, not scoped to just this diagnostic "
    "feature. Do not add to CLAUDE.md or the Principal Brief until Pete "
    "confirms wording/placement. Open items unresolved: exact copy for "
    "each dimension's on-demand explanation (needs brand-voice pass, "
    "P-10: 40% blunt, 60% servant leader, no coined terms); motion "
    "implementation approach (CSS-only confirmed, specific entrance "
    "mechanism -- path draw-in vs. scale/fade -- not chosen); mobile "
    "tap-to-reveal pattern (hover doesn't exist on touch, not a "
    "straight port of the desktop mechanism). | Claude.ai session, "
    "2026-08-13 | Pete's call -- reopen once ready to send Direction 1 "
    "Refinement to Gemini for architecture review; no code changes "
    "before that clears. Direction 2 stays shelved indefinitely unless "
    "Pete explicitly reopens it |"
)

OLD_13B_HEADER = "\\\\\\# 13b. Session Priority Queue"

NEW_13B_BODY = """\\\\\\# 13b. Session Priority Queue

Forward-looking session state, confirmed with Pete at closeout. Updated at each session close so a fresh session can pick up cleanly with no lost context. Not a Tier 3 Decision Register item -- a working queue, expected to be rewritten wholesale each time it's updated rather than accumulate history like 13a.

Priority order for next session, in sequence:

1. Category E, Direction 1 Refinement (legibility, motion, interpretability) -- approved concept, needs Gemini architecture review before any build (touches ConstellationField's shipped rendering system directly). Not started. See Decision Register (Section 13a) for full spec detail and the two durable planning artifacts (prompts/category-e-direction1-refinement-legibility-motion.md, prompts/category-e-direction2-instrument-panel.md).
2. Candidate standing principle ("spoon-feed meaning when not speaking plainly in brand voice") -- NOT YET LOCKED. Needs Pete's confirmation on exact wording and placement (likely P-06 addendum or its own governing-principle line) before it's added to CLAUDE.md or the Principal Brief.
3. Category D (free condensed diagnostic tier, business idea) -- parked, not developed. Unchanged.
4. /book/toc's fuller vision (clusters, media, other intersection vectors beyond the flat state list) -- approved concept, awaiting build scoping pass (primary_dimension frontend-availability check not yet done). Unchanged.
5. Primary-state/intended-target match rate (1/58 in real calibration data) -- flagged, standalone investigation candidate, Pete's call on if/when to open this thread. Unchanged.
6. SEVER-09 dead trigger (Q27A's only parent, itself unreachable in live Phase 1) -- parked, not scheduled, harmless. Unchanged.
7. tools/diagnostic_fast_forward.py -- confirmed structurally unusable against current infrastructure (no Preview environment exists, own production guard correctly refuses prv-3.vercel.app). Rework-or-retire decision needed whenever Pete picks it up.
8. Pre-existing session-store.test.ts failures (6, stale sequence-length assertions predating the 2026-08-11 session's N=44->42 recalibration) -- still unfixed, reconfirmed unrelated at every Category E commit, real gap worth its own pass.
9. OSHA jurisdictional research -- statutory-maximum roster COMPLETE, 22/22 states. Actual-average-penalty backfill: 4 states clean (Oregon, South Carolina, Michigan, California), Kentucky/Maryland flagged not directly comparable, remaining 14 states explicitly NOT URGENT. Untouched.
10. STATE_CAUSATION_OVERRIDES per-state authoring pass -- Pete's own clinical judgment, not started, UNDATED deliberately. Untouched.
11. ADA/FMLA/OSHA headcount-threshold gating for Legal/Compliance Clusters 1, 2, 5 -- does not exist anywhere in engine/friction_tax.py today, would be new logic not a fix. Untouched.
12. DATED FOLLOW-UP: collapse IntakeEcho.organization_size and AnonymizedCompletion.organization_size from string | number back to number-only, once ShareableOutputPayload's 30-day KV TTL has fully cycled past the deployment carrying commits b76b607/3b5056b/e5f6592. Target date needs reconfirming against the actual push/deploy timestamp when checked. Untouched.
13. DATED, test_contract.py sections 12/13: 3 pre-existing hidden failures (friction_tax_estimate calibration-target assertion likely stale post-calibration; a passing-case fixture missing descriptive_prose; one downstream 0-of-3 failure caused by the fixture gap). Not fixed, flagged only. Untouched.

Closed since last update, not on the active list -- full detail in Section 13a (Decision Register) and Section 16 (Session Log), not reproduced here: A1 (free-text "Other" elaboration) shipped full stack; A5 + Structure 3 combined recalibration shipped (N: 44 -> 42, 171/175, 58/58 HC); new diagnostic_question_audit.py tool built and shipped, A6 closed via it (no structural issue found); A.2 (Q06 multi-select) and A.3 (reset + look-back) shipped; Q46 topical-mismatch flag closed by decision, not a gap; Category E Directions 1 and 3 both shipped and live-verified (rendering-quality upgrade, editorial/typographic hero cluster display); Category E Direction 2 SHELVED and Direction 1 Refinement opened (this update -- see new Section 13a row); Q05 -- CLOSED, resolved via the same live before/after check Pete ran on A.2/A.3 and Category E Direction 1 in the 2026-08-11 session, confirmed by Pete this session.

Files to attach next session, categorized by likely next task:
- Always: tools/_mob.txt (current version).
- If resuming Category E Direction 1 Refinement or sending it to Gemini: prompts/category-e-direction1-refinement-legibility-motion.md, web/components/ConstellationField.tsx (path to confirm), web/app/globals.css.
- If continuing Category D (business idea) or /book/toc's fuller vision: no specific files pre-identified beyond prompts/category-d-condensed-diagnostic.md and prompts/book-toc-fuller-vision.md -- both need their own scoping pass first.

Explicitly parked, not on this list, do not resurface unless Pete reopens: confidentiality template field wording, attorney review of engagement agreement Section 3, LinkedIn 19-week content calendar, Category E Direction 2 (shelved, see above).

Calibration status as of session close: Friction Tax Sets 1 (ORG_TYPE_SCALARS), 2 (PAYROLL_BASELINE_GRID, 66-cell), and 3 (STATE_MULTIPLIERS, 58 states) all closed and live, unchanged. Multi-state compounding design locked and implemented (Option A rescale), unchanged. Full 172(+3)-profile suite verification held at 171/175, 58/58 HC as of the 2026-08-11 session's close, unchanged this update -- no engine/calibration-adjacent code touched this update (documentation and prompt-file commits only).

Last updated: This session (Claude Code), 2026-08-13, closing the Section 13b staleness gap flagged in this session's own Claude.ai handoff -- 13b had not been rewritten since 2026-08-09 despite two full sessions' worth of work (2026-08-11's Category A/B/C/E shipping arc, this session's Direction 2 shelve / Direction 1 Refinement open decision) landing in Section 13a and Section 16 in the interim."""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    content = MOB_PATH.read_text(encoding="utf-8")
    original = content

    # (1) version bump
    if content.count(OLD_VERSION) != 1:
        print(f"FAIL: expected exactly 1 occurrence of version header, found {content.count(OLD_VERSION)}")
        sys.exit(1)
    content = content.replace(OLD_VERSION, NEW_VERSION, 1)

    # (2) new 13a row, inserted right after the Direction 3 SHIPPED row
    if content.count(DIRECTION3_ROW_TAIL) != 1:
        print(f"FAIL: expected exactly 1 occurrence of Direction 3 row tail anchor, found {content.count(DIRECTION3_ROW_TAIL)}")
        sys.exit(1)
    content = content.replace(
        DIRECTION3_ROW_TAIL,
        DIRECTION3_ROW_TAIL + "\n" + NEW_13A_ROW,
        1,
    )

    # (3) 13b wholesale rewrite -- header through the old "Last updated:" line,
    # stopping before the trailing "\---" section separator.
    if content.count(OLD_13B_HEADER) != 1:
        print(f"FAIL: expected exactly 1 occurrence of 13b header, found {content.count(OLD_13B_HEADER)}")
        sys.exit(1)
    start = content.index(OLD_13B_HEADER)
    separator = "\n\n\n\\\\---\n"
    sep_index = content.index(separator, start)
    content = content[:start] + NEW_13B_BODY + content[sep_index:]

    if content == original:
        print("FAIL: no changes produced")
        sys.exit(1)

    print(f"Diff size: {len(content) - len(original):+d} chars")
    print("Edits applied in memory: version bump, new 13a row, 13b rewrite.")

    if args.write:
        MOB_PATH.write_text(content, encoding="utf-8")
        print("WRITTEN.")
    else:
        print("DRY RUN -- no file written. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
