"""
PRV3 MOB Update -- Q12/leadership_deafness investigation resolved
(dead-end, read-only, no code changes), new future item logged,
new-design pile corrected (groundhog_day/narrative_lock fully closed,
remove from pile), exact running total re-confirmed at 72/85.

Updates tools/_mob.txt:
  - Section 13b (Session Priority Queue), item 3: replaces the stale
    "Q12 under active investigation" tail with the resolved dead-end
    finding, the new future item, and the corrected 6-state new-design
    pile.
  - Section 16 (Session Log): new entry with full detail.
  - Version bump v4.125 -> v4.126.

Updates CLAUDE.md:
  - MOB version cross-reference v4.125 -> v4.126.

Usage:
  python tools/patch_q12_investigation_mob.py --dry-run
  python tools/patch_q12_investigation_mob.py --write
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
    "OPEN: Q12/leadership_deafness under active "
    "investigation -- Pete described a new symptom (group-wide "
    "accountability failure, no leadership standard) none of Q12's "
    "existing options capture; proposed option F (attitude_liability: "
    "0.75) confirmed via in-memory, non-destructive test to win outright "
    "for leadership_deafness, but the SAME test surfaced that "
    "the_untouchable is Q12's only other Attitude-primary state and "
    "would ALSO reroute to F, whose content doesn't honestly fit "
    "the_untouchable's actual condition (specific protected "
    "individuals, not group-wide accountability failure) -- Pete "
    "rejected F at 0.75 as-is on this basis. Investigating alternatives "
    "(tunable dimensional split, a parallel sixth option G fitting "
    "the_untouchable's own theme, or a confirmed dead-end) before any "
    "Q12 content is touched. 12 profiles remain open across the "
    "remaining items: 2 confirmed dead-ends (the_arbitrary_standard, "
    "the_overloaded_manager), 2 needing new question design "
    "(transition_paralysis, invisible_performance_management), 2 known "
    "PHASE-2-PENDING harness gaps (paper_shield, the_second_close), 1 "
    "(ATT-UT-01) needing a second trigger pending the Q12 "
    "investigation, and EXP-MAF-01/APT-BF-01 needing an unidentified "
    "second trigger. 2 category (a) states remain untouched pending a "
    "dedicated Gemini scoping pass."
)

NEW_TAIL = (
    "RESOLVED, Q12/leadership_deafness investigation: confirmed "
    "structural dead-end, read-only, no code touched. leadership_"
    "deafness and the_untouchable share both Q12 and the same "
    "primary_dimension (Attitude/attitude_liability, verified directly "
    "for both, not assumed) -- best_option_for_state() has exactly one "
    "discriminating field per state, so any option winning outright for "
    "one always wins for the other. Confirmed this is a taxonomic fact, "
    "not just a harness simplification: both states' full 8-field "
    "profile_vectors are near-identical, differing only on "
    "attitude_liability (0.5 vs 0.6), every other field 0.1 for both. "
    "Empirically tested (in-memory, non-destructive, 3 separate runs) "
    "whether a parallel sixth option (path b) could give each state its "
    "own honest answer -- confirmed it cannot: whichever option has the "
    "single highest value wins for BOTH states regardless of list order "
    "or which was 'authored for' which state; a higher-tier second "
    "option just displaces the first for both, it doesn't create a "
    "second selection path. No dimensional tuning, combination, or "
    "second option resolves this -- confirmed dead-end for Q12 "
    "specifically as the vehicle for this content. NEW FUTURE ITEM "
    "logged (not scoped, not scheduled): leadership_deafness's group-"
    "unaccountability symptom, described by Pete as \"a group of "
    "managers who are not accountable, actively making damaging "
    "decisions, and who lack a coherent leadership or values model\" -- "
    "NOT a severity-tier gap (leadership_deafness's severity math is "
    "already fully closed via Q04+Q08, ATT-LD-01/02/03 all reach their "
    "locked tier), a narrative/identification-accuracy gap: no existing "
    "question distinguishes this specific pattern from adjacent ones. "
    "Needs genuinely new, independently-wired question design if "
    "pursued -- falls under the same Gemini architecture-review gate as "
    "the rest of the new-design pile. NEW-DESIGN PILE CORRECTED: "
    "confirmed directly via run_profile() that groundhog_day and "
    "narrative_lock are now FULLY closed (all 6 profile variants -- "
    "ATT-GD-01/02/03, ATT-NL-01/02/03 -- reach their locked tier, not "
    "just partially per Pete's question) via the Q17/Q34 unlock several "
    "rounds back -- both REMOVED from the pile entirely, not merely "
    "downgraded. Pile is now 6 states, not 7: built_to_fail, invisible_"
    "performance_management, transition_paralysis, the_overloaded_"
    "manager (dead-end), the_arbitrary_standard (dead-end), and the new "
    "leadership_deafness group-unaccountability item just logged. EXACT "
    "running total re-confirmed via direct recount against the full "
    "85-profile list (not incremental arithmetic, matching Pete's "
    "standing instruction): 72 of 85 CLOSED, 7 SHORT (APT-BF-01, "
    "ATT-UT-01, AUT-FG-01, AUT-HI-01, AUT-TV-01, EXP-DIA-01, EXP-MAF-01 "
    "-- all pending an unidentified or undecided second trigger), 6 "
    "OPEN (ALL-AS-01/the_arbitrary_standard and APT-OM-01/the_"
    "overloaded_manager, dead-ends; AUT-PS-01/paper_shield and "
    "ALL-SC-01/the_second_close, known PHASE-2-PENDING harness gaps; "
    "AUT-TP-01/transition_paralysis and EXP-IPM-01/invisible_"
    "performance_management, needing new question design) -- sums to "
    "85, matches the committed record exactly. ATT-UT-01 still needs a "
    "second trigger via Q12 -- unaffected by the Q12/F dead-end finding "
    "above, since ATT-UT-01's own path was never contingent on F "
    "specifically, just on some future Q12 or Q05-adjacent content; "
    "remains open, no candidate identified. 2 category (a) states "
    "remain untouched pending a dedicated Gemini scoping pass."
)

edit("tools/_mob.txt", OLD_TAIL, NEW_TAIL)

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.125",
    "\\\\\\#\\\\\\# MOB v4.126",
)

SESSION_LOG_ENTRY = (
    "\n| August 2026 — Q12/leadership_deafness investigation resolved "
    "(dead-end, no code changes), new future item logged, new-design "
    "pile corrected to 6 states, running total re-confirmed at 72/85 | "
    "Full detail in Section 13b's Priority Queue item 3. Completed the "
    "Q12 investigation opened last round. Path (a) -- tunable "
    "dimensional split: confirmed leadership_deafness and the_"
    "untouchable share primary_dimension Attitude (verified directly "
    "for both), and best_option_for_state() only ever discriminates on "
    "a state's single mapped field, so no dimensional tuning can "
    "differentiate two states sharing that field on the same question. "
    "Went further than the mechanism check: pulled both states' full "
    "8-field profile_vectors directly and found them near-identical "
    "(0.1 on every field for both except attitude_liability, 0.5 vs "
    "0.6) -- this is a taxonomic fact baked into the state definitions, "
    "not just a harness limitation. Path (b) -- a parallel sixth option: "
    "tested empirically rather than reasoned abstractly, three separate "
    "in-memory non-destructive runs (confirmed no files touched via git "
    "status each time) -- same-tier F/G pair always resolves to "
    "whichever is listed first, for BOTH states identically; a "
    "higher-tier G displaces F for BOTH states too. Confirmed no "
    "combination of new options can give the two states independent "
    "answers as long as they share both the question and the primary "
    "dimension. Path (c): reported plainly -- genuine structural dead "
    "end for Q12 as the vehicle, matching the same honesty standard "
    "applied to the_overloaded_manager and the_arbitrary_standard "
    "earlier this session. Logged the underlying symptom as a new "
    "future item rather than dropping it: leadership_deafness's group-"
    "unaccountability pattern (Pete's description: a group of managers "
    "not accountable, actively making damaging decisions, no coherent "
    "leadership/values model) is a narrative/identification-accuracy "
    "gap, not a severity gap -- leadership_deafness's severity math is "
    "already fully closed via Q04+Q08. Needs genuinely new, "
    "independently-wired question design, same Gemini gate as the rest "
    "of the pile. While logging it, checked Pete's question about "
    "groundhog_day/narrative_lock's current status directly rather than "
    "assuming \"now partially resolved\": confirmed via run_profile() "
    "that all 6 profile variants (ATT-GD-01/02/03, ATT-NL-01/02/03) are "
    "FULLY closed, not partially -- both states removed from the "
    "new-design pile entirely, correcting it from 7 states to 6 (5 "
    "carried over + the 1 new leadership_deafness item). Re-confirmed "
    "the exact running total via direct recount against the full "
    "85-profile list, same method as before, not incremental addition: "
    "72 CLOSED, 7 SHORT, 6 OPEN, sums to 85 -- matches the committed "
    "record exactly, no drift found. MOB version bumped v4.125 → "
    "v4.126 per standing protocol -- Q12 investigation closed out "
    "honestly as a dead-end, new future item on record, new-design pile "
    "corrected with verified evidence rather than an assumption, "
    "running total re-verified. | This session (Claude Code) | MOB "
    "v4.126 |"
)

edit(
    "tools/_mob.txt",
    "| This session (Claude Code) | MOB v4.125 |",
    "| This session (Claude Code) | MOB v4.125 |" + SESSION_LOG_ENTRY,
)

# ============================================================================
# CLAUDE.md
# ============================================================================

edit(
    "CLAUDE.md",
    "| MOB version | v4.125 |",
    "| MOB version | v4.126 |",
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
