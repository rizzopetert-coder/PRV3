"""
MOB update: fold the dominance-mechanism investigation (7 states,
cross-cutting) and two-track sequencing synthesis into the Decision
Register. Diagnostic only -- no code touched, no weight numbers
proposed. The two-track synthesis is explicitly logged as a
recommendation for Pete's decision, not a decision already made.

Version bump: v4.215 -> v4.216 (workstream status materially changed --
sequencing recommendation now available, real mechanism findings
logged).

Usage:
    python patch_mob_scdwcs_dominance_mechanism.py --dry-run
    python patch_mob_scdwcs_dominance_mechanism.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "ALL 11 CLUSTERS CHARACTERIZED (2 pilots landed, 1 verification "
    "declined, 8 characterized this pass), full sequencing input ready, "
    "1 new out-of-scope dominance finding"
)
NEW_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "ALL 11 CLUSTERS CHARACTERIZED + DOMINANCE MECHANISM DIAGNOSED, "
    "two-track sequencing RECOMMENDATION ready (Pete's call, not decided)"
)

OLD_BLOCKER = (
    "None active -- this pass is verification-only, no code changed, "
    "nothing to block. Three open questions now, all Pete's call, none "
    "a blocker on timing/priority: (1) rank-7's open question stands "
    "unchanged -- mechanical-only fix, targeted vector nudge, or defer "
    "to full remediation, when narrative fidelity isn't achievable "
    "within calibration-safe bounds? One confirmed data point, not a "
    "pattern. (2) built_to_fail (rank-8) is a named, evidence-backed "
    "candidate for the dimensional_vector re-authoring layer -- does "
    "that layer get scoped around specific high-impact states first, "
    "rather than treated as one undifferentiated 43+-state backlog? "
    "(3) NEW: does the cluster/tie remediation track (this whole "
    "investigation) continue at all given rank-1/rank-2's scale "
    "(10-11 states each, closer to the full vector-reauthoring project "
    "than a pilot), or does focus shift toward the newly surfaced "
    "invisible_performance_management finding -- a bigger, structurally "
    "different problem (33.7% false rank-1, no tie or cluster involved "
    "at all) than anything a salience pilot touches? Not scoped or "
    "actioned here."
)
NEW_BLOCKER = (
    "None active -- this pass is diagnostic-only, no code changed, "
    "nothing to block. A two-track sequencing RECOMMENDATION is now "
    "logged (not a decision -- Pete's call): Track 1 (narrow "
    "same-dimension neighbor-stealers: the_uninitiated, "
    "the_unexamined_algorithm, the_second_close, culture_drift) is "
    "structurally similar to rank-7's confirmed salience-only success, "
    "candidate for continued pilot-style remediation. Track 2 (broad "
    "cross-dimensional attractors: invisible_performance_management, "
    "built_to_fail) is confirmed unfixable via salience alone -- real "
    "dimensional_vector authoring work, the harder track, sequenced "
    "separately from Track 1's lighter pilots. the_overloaded_manager "
    "logged as an open, small-sample (n=4) anomaly fitting neither "
    "track. Open questions for Pete: does Track 1 continue as a fourth "
    "pilot (rank-6/rank-5 are the cleanest candidates), does Track 2 "
    "get scoped at all given its authoring-project scale, and does "
    "rank-1/rank-2's own scale change the calculus on continuing the "
    "cluster/tie track versus shifting focus to Track 2. Not scoped or "
    "actioned here."
)

OLD_DETAIL_TAIL = (
    "the_unexamined_algorithm (11/175, 6.3%), the_overloaded_manager "
    "(4/175, 2.3%). No salience or tie remediation touches this class "
    "of problem -- flagged as needing its own future investigation, "
    "independent of the cluster/tie remediation track this whole "
    "investigation has been about."
)
NEW_DETAIL_TAIL = (
    "the_unexamined_algorithm (11/175, 6.3%), the_overloaded_manager "
    "(4/175, 2.3%). No salience or tie remediation touches this class "
    "of problem -- flagged as needing its own future investigation, "
    "independent of the cluster/tie remediation track this whole "
    "investigation has been about. **Dominance-mechanism investigation, "
    "2026-08-20 -- diagnostic only, no code touched, no weight numbers "
    "proposed:** examined the same 7 dominant states together rather "
    "than one at a time. dimensional_vector magnitude/concentration, "
    "SALIENCE_PROFILES entry, and every stolen profile's true target's "
    "own dominant field, pulled directly for each. Full detail: "
    "prompts/scd-wcs-cluster-map-findings.md, \"Dominance-mechanism "
    "investigation\" section. Three direct findings: (a) salience "
    "presence/magnitude is a CONSTANT across all 7 (every one has a "
    "sharp custom 2.5 entry), not a variable that explains dominance -- "
    "falsifies the \"lacking an entry = generalist attractor\" "
    "hypothesis outright. (b) vector magnitude/concentration doesn't "
    "correlate with dominance magnitude in any consistent direction -- "
    "invisible_performance_management has the LOWEST concentration of "
    "the top two dominators yet wins the most. (c) The aptitude-signal "
    "hypothesis specifically checked against built_to_fail does NOT "
    "hold -- confirmed directly: its 49 stolen profiles span all four "
    "dimensions roughly evenly, not concentrated on aptitude-flavored "
    "targets. Real pattern found instead: a magnitude-of-dominance "
    "split -- the two biggest dominators (invisible_performance_"
    "management, built_to_fail, both >25%) steal broadly across all "
    "four dimensions; four of the remaining five (the_uninitiated, "
    "the_unexamined_algorithm, the_second_close, culture_drift) steal "
    "almost exclusively from targets sharing their own dominant "
    "dimension -- a narrow same-dimension effect, structurally "
    "different from the broad attractor effect. the_overloaded_manager "
    "fits neither pattern (steals only from attitude-dominant targets "
    "despite being aptitude-dominant with an authority secondary; one "
    "case checked directly at the dimension_summary level showed no "
    "elevated aptitude OR attitude signal, doesn't explain the win "
    "either) -- logged as a genuine open anomaly, n=4, not forced into "
    "either track. **Two-track sequencing synthesis logged as a "
    "recommendation for Pete's decision, not a decision made:** Track 1 "
    "(narrow neighbor-stealers) is candidate for continued pilot-style "
    "remediation, same process as rank-7/8/9 -- structurally similar to "
    "rank-7's confirmed success. Track 2 (broad attractors) is real "
    "clinical/taxonomic dimensional_vector authoring work, confirmed "
    "not fixable via salience alone (rank-8's actual pilot evidence, "
    "reinforced by this session's broader theft-pattern data), the "
    "harder track, sequenced separately from Track 1."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on all "
    "three open questions above -- the cluster/tie remediation track's "
    "own sequencing (rank-7 pattern, built_to_fail priority, whether "
    "rank-6/rank-5 become a fourth pilot) AND whether attention shifts "
    "toward invisible_performance_management's larger, structurally "
    "different dominance problem instead. Not a forced check-in; this "
    "full characterization pass is the complete input for that "
    "conversation, not a recommendation or a green light to continue "
    "either track. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on the "
    "two-track recommendation and every open question feeding it -- "
    "whether Track 1 continues (rank-6/rank-5 as the next candidates), "
    "whether/when Track 2's dimensional_vector authoring work gets "
    "scoped, and how invisible_performance_management's own unscoped "
    "investigation and rank-1/rank-2's scale factor into the overall "
    "priority. Not a forced check-in; this is the complete diagnostic "
    "input for that conversation, a recommendation to weigh, not a "
    "decision made or a green light to build anything. |"
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
        ("detail tail", OLD_DETAIL_TAIL, NEW_DETAIL_TAIL),
        ("tail (last touched / next check-in)", OLD_TAIL, NEW_TAIL),
    ]:
        count = mob_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        mob_text = mob_text.replace(old, new, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.215"
    version_new = "\\\\\\#\\\\\\# MOB v4.216"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.215 |"
    claude_new = "| MOB version | v4.216 |"
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
