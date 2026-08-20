"""
MOB update: fold the Track 1 membership verification into the Decision
Register. Corrects a real overclaim in the prior entry -- the blocker
column stated Track 1 membership was "confirmed via direct
score-by-score check" for the_unexamined_algorithm/the_second_close/
culture_drift, but that check had not actually been run yet at that
point (only the_uninitiated had been verified). Running it now finds
none of the 3 are clean same-cluster pairings either -- Track 1
currently has zero confirmed members. Last characterization pass for
the session per explicit instruction -- no code changes, no direction
proposed, nothing further initiated regardless of result.

Version bump: v4.217 -> v4.218 (workstream status materially changed --
Track 1 membership corrected to zero, a real revision not an addition).

Usage:
    python patch_mob_scdwcs_track1_verification.py --dry-run
    python patch_mob_scdwcs_track1_verification.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "4TH DOMINANCE PATTERN FOUND (cross-cluster asymmetry), two-track "
    "recommendation revised, Pete's call not decided"
)
NEW_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "TRACK 1 HAS ZERO CONFIRMED MEMBERS (verification found 3 more "
    "cross-cluster surprises), sequencing recommendation needs "
    "re-reading, Pete's call not decided"
)

OLD_BLOCKER = (
    "None active -- this pass is diagnostic-only, no code changed, "
    "nothing to block. Two-track sequencing RECOMMENDATION stands, "
    "REVISED membership (not a decision -- Pete's call): Track 1 "
    "(narrow same-CLUSTER neighbor-stealers, confirmed via direct "
    "score-by-score check, not just theft-shape inference: "
    "the_unexamined_algorithm, the_second_close, culture_drift -- "
    "the_uninitiated REMOVED, see below) is structurally similar to "
    "rank-7's confirmed salience-only success, candidate for continued "
    "pilot-style remediation. Track 2 (broad cross-dimensional "
    "attractors: invisible_performance_management, built_to_fail) is "
    "confirmed unfixable via salience alone -- real dimensional_vector "
    "authoring work, the harder track. the_overloaded_manager remains "
    "an open, small-sample (n=4) anomaly fitting neither track. NEW: "
    "the_uninitiated is a 4th pattern, cross-cluster asymmetry -- see "
    "detail column. Open questions for Pete: does Track 1 continue as "
    "a pilot (rank-6/rank-5 are the cleanest candidates), does Track 2 "
    "get scoped at all given its authoring-project scale, what "
    "diagnosis does the cross-cluster asymmetry pattern need before it "
    "joins either track, and does rank-1/rank-2/rank-3's own scale "
    "change the calculus on continuing the cluster/tie track at all. "
    "Not scoped or actioned here."
)
NEW_BLOCKER = (
    "None active -- this pass is diagnostic-only, no code changed, "
    "nothing to block. CORRECTION to the prior entry: it claimed "
    "the_unexamined_algorithm/the_second_close/culture_drift were "
    "\"confirmed via direct score-by-score check\" as Track 1 members -- "
    "that check had not actually been run yet at that point, only "
    "the_uninitiated had been. Running it now on all 3: NONE are clean. "
    "the_unexamined_algorithm has no cluster of its own (0 tie-artifacts "
    "possible) but its 11 genuine wins spread across 3 clusters "
    "(rank-3 55%, rank-2 36%, rank-9 9%) -- a smaller-scale broad "
    "attractor, not narrow. the_second_close is 60% tie-artifact "
    "(silosolation, its own rank-6 cluster-mate) with only 2 genuine "
    "wins left, both against an unrelated already-declined cluster "
    "(rank-9/the_fracture). culture_drift is 20% tie-artifact "
    "(wellbeing_theater, own rank-11 cluster-mate) with genuine wins "
    "split across rank-1 (75%) and rank-10 (25%). **Track 1, as "
    "originally scoped, currently has ZERO confirmed members** -- all 4 "
    "candidates checked this session (the_uninitiated plus these 3) "
    "turned out to be cross-cluster-flavored surprises, not clean "
    "same-cluster pairings. The \"narrow same-dimension theft\" "
    "heuristic is 0-for-4 as a screening criterion in this session's "
    "data. Track 2 (invisible_performance_management, built_to_fail) is "
    "unaffected by this correction -- still confirmed unfixable via "
    "salience alone, still the harder track. the_overloaded_manager "
    "remains an open n=4 anomaly. This was the last characterization "
    "pass for the session per explicit instruction -- nothing further "
    "initiated regardless of this result. The two-track sequencing "
    "recommendation needs re-reading in light of Track 1 currently "
    "being empty, not discarded outright -- Pete's call."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on the "
    "revised two-track recommendation, the new 4th-pattern question "
    "(cross-cluster asymmetry -- what predicts which cluster wins, and "
    "whether rank-3 gets its own dedicated look), and every earlier open "
    "question -- whether Track 1 continues (rank-6/rank-5 as the "
    "cleanest remaining candidates), whether/when Track 2's "
    "dimensional_vector authoring work gets scoped, and how "
    "invisible_performance_management's own unscoped investigation and "
    "rank-1/rank-2/rank-3's scale factor into overall priority. Not a "
    "forced check-in; this is diagnostic input, a recommendation to "
    "weigh, not a decision made or a green light to build anything. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on how to "
    "read the sequencing question now that Track 1 has zero confirmed "
    "members -- whether rank-6/rank-5 (untested this session, still the "
    "only unverified small-cluster candidates) get checked with this "
    "same decomposition method before anything is called Track 1 again, "
    "whether the 4 cross-cluster-flavored surprises found so far "
    "(the_uninitiated, the_unexamined_algorithm, the_second_close, "
    "culture_drift) deserve their own remediation category distinct "
    "from both original tracks, and every earlier open question "
    "(Track 2 scoping, invisible_performance_management, "
    "rank-1/rank-2/rank-3 scale). Not a forced check-in; this session's "
    "characterization work is done per explicit instruction -- next "
    "steps are Pete's call, nothing initiated further. |"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    mob_text = MOB_PATH.read_text(encoding="utf-8")

    for label, old, new in [
        ("title", OLD_TITLE, NEW_TITLE),
        ("blocker", OLD_BLOCKER, NEW_BLOCKER),
        ("tail (last touched / next check-in)", OLD_TAIL, NEW_TAIL),
    ]:
        count = mob_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        mob_text = mob_text.replace(old, new, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.217"
    version_new = "\\\\\\#\\\\\\# MOB v4.218"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.217 |"
    claude_new = "| MOB version | v4.218 |"
    count = claude_text.count(claude_old)
    if count != 1:
        raise SystemExit(f"ABORT [CLAUDE.md version]: expected exactly 1 match, found {count}")
    claude_text = claude_text.replace(claude_old, claude_new, 1)

    if args.dry_run:
        for path, original, new_text in [
            (MOB_PATH, MOB_PATH.read_text(encoding="utf-8"), mob_text),
            (CLAUDE_MD_PATH, CLAUDE_MD_PATH.read_text(encoding="utf-8"), claude_text),
        ]:
            print(f"\n{'=' * 80}\nDIFF: {path}\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
            )
            print("".join(diff))
        print("\nDry run complete. No files written. Re-run with --write to apply.")
    else:
        MOB_PATH.write_text(mob_text, encoding="utf-8")
        CLAUDE_MD_PATH.write_text(claude_text, encoding="utf-8")
        print(f"WROTE: {MOB_PATH}")
        print(f"WROTE: {CLAUDE_MD_PATH}")


if __name__ == "__main__":
    main()
