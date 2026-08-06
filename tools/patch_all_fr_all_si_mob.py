"""
PRV3 MOB Update -- ALL-FR-01/ALL-SI-01 SEVER-14 fix + Bucket 3 additions

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: trims the "5 profiles
    confirmed genuinely short" open item to a concise "RESOLVED/
    DISPOSITIONED" pointer now that all 5 have a disposition (2 fixed, 3
    deferred to Bucket 3). Full narrative in the new Section 16 entry.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.116 -> v4.117.

Updates CLAUDE.md:
  - MOB version cross-reference v4.116 -> v4.117.

Usage:
  python tools/patch_all_fr_all_si_mob.py --dry-run
  python tools/patch_all_fr_all_si_mob.py --write
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

OLD_SENTENCE = (
    "OPEN, new and smaller: 5 profiles (ALL-FR-01, ALL-SI-01, APT-BF-01, "
    "ATT-GD-01, ATT-NL-01) confirmed genuinely short -- all Endemic-expected, "
    "capped at Entrenched (raw 2.00) with only one fireable trigger each, "
    "structurally the same two-trigger-needed pattern ATT-DC-01 already "
    "resolved -- needs either a second independent trigger identified for "
    "each, or a tier-expectation reconsideration; Pete's call, not resolved "
    "here. OPEN, PHASE-2-PENDING: SEVER-09 (the_second_close, routes via "
    "inert Q27A) is the one Track A item still not live -- parked with the "
    "rest of that category. OPEN, PARKED: ATT-BC-02/Q03A (prior session, "
    "Pete's explicit instruction, rationale on record there). OPEN, "
    "UNTOUCHED: Bucket 3 (49 profiles, not wired at all) -- not yet "
    "investigated for live-reachability, apply the same "
    "LIVE-REACHABLE/PHASE-2-PENDING split whenever taken up, explicitly "
    "flagged as its own dedicated future session given its size."
)

NEW_SENTENCE = (
    "RESOLVED/DISPOSITIONED, closes the 5-profile two-trigger item: 2 fixed "
    "(ALL-FR-01, ALL-SI-01, via new SEVER-14 on Q09's option E -- full "
    "detail in Section 16's session log, confirmed via full regression, "
    "held for commit go-ahead), 3 deferred to Bucket 3 (APT-BF-01, "
    "ATT-GD-01, ATT-NL-01 -- no clean second trigger exists, reasoning on "
    "record in Section 16, not re-derived here). OPEN, PHASE-2-PENDING: "
    "SEVER-09 (the_second_close, routes via inert Q27A) is the one Track A "
    "item still not live -- parked with the rest of that category. OPEN, "
    "PARKED: ATT-BC-02/Q03A (prior session, Pete's explicit instruction, "
    "rationale on record there). OPEN, UNTOUCHED: Bucket 3 (49 profiles "
    "not wired at all, plus APT-BF-01/ATT-GD-01/ATT-NL-01 added this "
    "session -- 52 total) -- not yet investigated for live-reachability, "
    "apply the same LIVE-REACHABLE/PHASE-2-PENDING split whenever taken "
    "up, explicitly flagged as its own dedicated future session given its "
    "size."
)

edit("tools/_mob.txt", OLD_SENTENCE, NEW_SENTENCE)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.116",
    "\\\\\\#\\\\\\# MOB v4.117",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — ALL-FR-01/ALL-SI-01 second-trigger fix (SEVER-14), "
    "5-profile two-trigger item fully dispositioned (2 fixed, 3 to Bucket "
    "3) | Full detail in Section 13b's Priority Queue item 3. "
    "ALL-FR-01/ALL-SI-01 (the_fracture/silosolation) FIXED: Q09's options "
    "C/D/E were already confirmed (prior session) as a full-field-identical "
    "tie -- E (\"There's a significant unresolved conflict I'm not sure how "
    "to address\") reads as the genuinely more severe option than C "
    "(currently selected, \"tension that's mostly contained\"), losing only "
    "on list-order. Flipped E's severity_trigger to True; the already-"
    "shipped Bucket 1 tie-break rule (commit 44e85fc) selects it "
    "automatically -- confirmed empirically, no selection-logic change "
    "needed. New follow-on SEVER-14 (\"How long has this conflict been "
    "present?\", duration_band up to 18mo_plus) built to the Track A/"
    "SEVER-06 style precedent, honestly following from E's own framing, "
    "not fabricated to hit a number. Confirmed zero blast radius beyond "
    "these two states before touching anything -- Q09's state_targets is "
    "exactly [the_fracture, silosolation], nothing else in the library "
    "targets either state via Q09. _SEVERITY_FOLLOW_ON_TARGETS extended "
    "with both SEVER-08 (existing) and SEVER-14 (new) for each profile, "
    "the same two-trigger pattern ATT-DC-01 already uses. Full 172-profile "
    "byte-for-byte regression: 6 profiles changed (both states x all 3 "
    "profile types), ALL-FR-01 and ALL-SI-01 both now correctly reach "
    "Endemic (raw=4.00); the -02/-03 sibling variants unaffected in tier "
    "-- cosmetic Q09 answer-selection change only (E instead of C, "
    "dimensionally identical, zero effect on their own dimensional "
    "matching), since they're not opted into _SEVERITY_FOLLOW_ON_TARGETS, "
    "same pattern already established for the AUT-UP siblings. 169/172 "
    "baseline unchanged, same 3 pre-existing gaps verified per-state; "
    "the_fracture and silosolation both still 3/3 on their own dimensional "
    "pass criteria, confirming E/C's dimensional identity holds in "
    "practice, not just in the option data. All other Python test suites "
    "re-run clean. Confirmed via full regression -- held for commit "
    "go-ahead, not yet committed. APT-BF-01, ATT-GD-01, ATT-NL-01 -- added "
    "to Bucket 3 scope (needs-new-question-design category), no code "
    "change, reasoning on record so it isn't re-derived later: APT-BF-01 "
    "(built_to_fail) has no live second question at all -- Q03A carries a "
    "trigger but is Phase-2-pending/inert, Q35/Q36/Q39 are the only other "
    "wired questions and are all confirmed excluded from live Phase 1 "
    "(the same Aptitude-addenda gap already on record elsewhere in this "
    "file) -- needs genuinely new question design or a tier-expectation "
    "reconsideration, Pete's call, deferred. ATT-GD-01 (groundhog_day) and "
    "ATT-NL-01 (narrative_lock) each have a live candidate question (Q17 "
    "for both, Q34 also for ATT-NL-01), but both were checked directly, "
    "not assumed usable: the_broken_compass (already correctly calibrated "
    "at Entrenched across all its profile types via its own single "
    "trigger) ties into the exact same full-field-identical winning option "
    "group on both Q17 and Q34 -- confirmed by checking whether any other "
    "option in either tied group could route around it, and it can't; the "
    "collision is structural to the tied group, not avoidable by choosing "
    "a different option within it. A full-strength new trigger there would "
    "push the_broken_compass to an incorrect Endemic overshoot; capping "
    "the new trigger's magnitude to protect it would leave "
    "groundhog_day/narrative_lock short of Endemic's 3.96 threshold either "
    "way. Deliberately not fixed -- would trade one correct profile for "
    "two incorrect ones -- deferred to Bucket 3, needs real new question "
    "design that doesn't route through Q17/Q34's shared tied group. MOB "
    "version bumped v4.116 → v4.117 per standing protocol -- closes the "
    "5-profile side item cleanly (2 fixed, 3 precisely dispositioned into "
    "Bucket 3), Bucket 3 scope grows from 49 to 52 with reasoning on "
    "record. | This session (Claude Code) | MOB v4.117 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.116 |",
    "| This session (Claude Code) | MOB v4.116 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.116 |",
    "| MOB version | v4.117 |",
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
