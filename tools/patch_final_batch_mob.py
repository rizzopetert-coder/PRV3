"""
PRV3 MOB Update -- AUT-HI-01 + ATT-UT-01 closure (commit 637f648), exact
running total re-confirmed at 74/85, dead-end pile reconciled into 3
clean buckets by root cause.

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    tail with the closure summary and the reconciled pile.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.126 -> v4.127.

Updates CLAUDE.md:
  - MOB version cross-reference v4.126 -> v4.127.

Usage:
  python tools/patch_final_batch_mob.py --dry-run
  python tools/patch_final_batch_mob.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================================
# tools/_mob.txt -- Section 13b, Priority Queue item 3
# ============================================================================

OLD_TAIL = (
    "ATT-UT-01 still needs "
    "a second trigger via Q12 -- unaffected by the Q12/F dead-end "
    "finding above, since ATT-UT-01's own path was never contingent on "
    "F specifically, just on some future Q12 or Q05-adjacent content; "
    "remains open, no candidate identified. 2 category (a) states "
    "remain untouched pending a dedicated Gemini scoping pass."
)

NEW_TAIL = (
    "Ninth Bucket 3 fix CLOSED and committed (commit 637f648): batched "
    "workup across all 7 SHORT profiles (APT-BF-01, ATT-UT-01, "
    "AUT-FG-01, AUT-HI-01, AUT-TV-01, EXP-DIA-01, EXP-MAF-01), same "
    "mechanism-viability-first discipline as the earlier big batch. "
    "Full wiring enumerated per state (every question, live or inert, "
    "not just live candidates) -- confirmed 5 of the 7 (APT-BF-01, "
    "AUT-FG-01, AUT-TV-01, EXP-DIA-01, EXP-MAF-01) never had a second "
    "question wired at all, live or inert; their existing trigger IS "
    "their only lever, CONFIRMED-DEAD-END, no new work possible without "
    "genuinely new question design. The other 2 had real, live, "
    "untriggered second candidates: AUT-HI-01 (heard_and_ignored) via "
    "Q06, reusing the already-approved SEVER-27 content built for "
    "the_tolerated_violation/disparate_impact_architecture two rounds "
    "back -- pure table addition, zero new content, CLEAN. ATT-UT-01 "
    "(the_untouchable) via Q12 -- C/D full-field-identical tie, D's "
    "\"specific managers... concentrated issues\" framing a closer "
    "thematic fit than C's capacity framing, content call confirmed by "
    "Pete, new SEVER-29. Flipping D relies on the tie-break rule to "
    "reroute the_untouchable AND leadership_deafness (Q12's only other "
    "Attitude-primary state) from C to D -- verified directly, "
    "leadership_deafness confirmed byte-for-byte identical on all 3 "
    "profile variants (already fully closed via Q04+Q08, not opted "
    "into SEVER-29) despite its own live answer changing. Full "
    "172-profile byte-for-byte regression: exactly 2 profiles changed "
    "(AUT-HI-01, ATT-UT-01), both closing to Endemic (score 66.67, raw "
    "4.00), 170/172 unchanged. All 5 Python test suites re-run clean. "
    "EXACT running total re-confirmed via direct recount (not "
    "incremental arithmetic): 74 of 85 CLOSED, 5 SHORT (APT-BF-01, "
    "AUT-FG-01, AUT-TV-01, EXP-DIA-01, EXP-MAF-01 -- the 5 newly-"
    "confirmed dead-ends from this batch), 6 OPEN (unchanged from prior "
    "round). DEAD-END PILE RECONCILED into 3 clean buckets by root "
    "cause/dependency, per Pete's explicit request, rather than one "
    "undifferentiated list: (1) NEEDS GENUINELY NEW QUESTION DESIGN, 7 "
    "states, no live or inert content exists at all beyond each "
    "state's existing single trigger -- built_to_fail (APT-BF-01), "
    "the_founders_grip (AUT-FG-01), the_tolerated_violation (AUT-TV-01), "
    "disparate_impact_architecture (EXP-DIA-01), motivational_"
    "architecture_failure (EXP-MAF-01), confirmed this round; plus "
    "the_overloaded_manager and the_arbitrary_standard, confirmed "
    "earlier (zero real signal on every candidate question's relevant "
    "dimensional field). All 7 need the same Gemini architecture-review "
    "gate before any content gets drafted. (2) PHASE-2-PENDING, blocked "
    "on live intake, NOT a design gap -- transition_paralysis (AUT-TP-01, "
    "Q03A already exists with a trigger already built, just structurally "
    "hardcoded off in PHASE_1_QUESTION_SEQUENCE) and invisible_"
    "performance_management (EXP-IPM-01, Q35 already exists as part of "
    "the Aptitude addenda, same live-intake exclusion) -- both re-"
    "verified directly this round (full wiring enumerated, not assumed "
    "from memory): content already exists or has a natural home for "
    "both, the blocker is Phase 2 launching, not authoring. Deliberately "
    "kept separate from bucket (1) -- these don't need Gemini design "
    "work, they need Phase 2's live-intake gate to open. (3) NARRATIVE-"
    "FIT GAP, NOT A SEVERITY GAP -- leadership_deafness's group-"
    "unaccountability symptom (logged last round): severity math "
    "already fully closed via Q04+Q08, this is purely an identification/"
    "narrative-accuracy concern. Kept separate from both other buckets "
    "since it isn't blocked on anything structural, it simply hasn't "
    "been scoped -- would need the same new-question-design treatment "
    "as bucket (1) if pursued, but for a different underlying reason "
    "(accuracy, not reachability). 2 category (a) states remain "
    "untouched pending a dedicated Gemini scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.126",
    "\\\\\\#\\\\\\# MOB v4.127",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Ninth Bucket 3 fix (AUT-HI-01 + ATT-UT-01) "
    "closed and committed, commit 637f648; running total 74/85; "
    "dead-end pile reconciled into 3 buckets by root cause | Full "
    "detail in Section 13b's Priority Queue item 3. Ran the batched "
    "workup across all 7 remaining SHORT profiles, same mechanism-"
    "viability-first discipline established for the_overloaded_manager/"
    "the_arbitrary_standard: enumerated EVERY question (live or inert) "
    "wired to each state before evaluating candidates, not just live "
    "ones, to avoid missing a genuine second lever. Found 5 of 7 "
    "(APT-BF-01, AUT-FG-01, AUT-TV-01, EXP-DIA-01, EXP-MAF-01) never "
    "had a second question of any kind wired -- their existing trigger "
    "is structurally their only lever, confirmed dead-end, not a "
    "blast-radius or content problem. The other 2 had real candidates: "
    "AUT-HI-01 via Q06 (pure reuse of already-Pete-approved SEVER-27 "
    "content, zero new authoring) and ATT-UT-01 via Q12 (D's content "
    "read as a closer the_untouchable fit than C's, content call "
    "confirmed by Pete, same tie-break-reroute mechanism as Q02/Q33). "
    "Implemented both, verified the Q12 reroute affects leadership_"
    "deafness's live answer but confirmed byte-for-byte identical on "
    "severity for all 3 of its profile variants -- already fully closed, "
    "not opted into the new trigger. Full 172-profile regression: "
    "exactly 2 profiles changed, both reaching Endemic (66.67, raw "
    "4.00) via normalized score, not just tier label; 170/172 "
    "unchanged. All 5 Python test suites re-run clean. Recomputed the "
    "exact running total via direct recount, same method as every "
    "prior count tonight: 74 CLOSED, 5 SHORT, 6 OPEN, sums to 85. "
    "Reconciled the accumulated dead-end/open-item list into 3 "
    "distinct buckets per Pete's explicit request, since they'd been "
    "informally mixed together across several rounds' worth of session "
    "log entries: (1) 7 states needing genuinely new question design "
    "(zero content exists beyond each state's own single trigger, all "
    "gated by the same Gemini architecture-review requirement); (2) 2 "
    "states blocked on Phase 2 launching specifically, not a design gap "
    "-- transition_paralysis and invisible_performance_management both "
    "already have content built (Q03A, Q35 respectively), just "
    "structurally excluded from live Phase 1 -- re-verified this "
    "distinction directly via full wiring enumeration, not assumed from "
    "Pete's framing alone; (3) leadership_deafness's group-"
    "unaccountability item, a narrative-accuracy gap with zero severity-"
    "tier consequence, kept separate since it isn't blocked on anything "
    "structural the way bucket (2) is. MOB version bumped v4.126 → "
    "v4.127 per standing protocol -- ninth Bucket 3 fix shipped, "
    "running total re-verified precisely, the full session's "
    "accumulated open-item list reconciled into a clean, durable "
    "3-bucket structure for future reference. | This session (Claude "
    "Code) | MOB v4.127 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.126 |",
    "| This session (Claude Code) | MOB v4.126 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.126 |",
    "| MOB version | v4.127 |",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    by_file: dict[str, list[tuple[str, str]]] = {}
    for path, old, new in EDITS:
        by_file.setdefault(path, []).append((old, new))

    for rel_path, pairs in by_file.items():
        full_path = REPO_ROOT / rel_path
        content = full_path.read_text(encoding="utf-8")
        for old, new in pairs:
            count = content.count(old)
            if count != 1:
                print(f"ABORT: {rel_path}: expected exactly 1 match for anchor, found {count}")
                print(f"  anchor (first 120 chars): {old[:120]!r}")
                sys.exit(1)
            content = content.replace(old, new, 1)

        if args.dry_run:
            print(f"=== {rel_path}: {len(pairs)} edit(s) would apply cleanly ===")
        else:
            full_path.write_text(content, encoding="utf-8")
            print(f"=== {rel_path}: {len(pairs)} edit(s) written ===")

    if args.dry_run:
        print("\nDry run complete. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
