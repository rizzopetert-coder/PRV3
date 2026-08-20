"""
MOB update: fold the_uninitiated's cross-cluster asymmetry finding into
the Decision Register as a fourth, distinct dominance pattern. Also
corrects the Track 1 membership list -- the_uninitiated was provisionally
listed there based on its "narrow, same-dimension" theft shape alone;
direct verification of all 22 stolen profiles shows it's actually a
cluster-vs-cluster asymmetry (rank-2 vs rank-3), not a same-cluster
neighbor-steal, so it moves out of Track 1's membership list into its
own fourth-pattern category. Diagnostic only, no code changes, no
differentiation candidate proposed.

Version bump: v4.216 -> v4.217 (workstream status materially changed --
new dominance pattern identified, Track 1 membership corrected).

Usage:
    python patch_mob_scdwcs_cross_cluster_asymmetry.py --dry-run
    python patch_mob_scdwcs_cross_cluster_asymmetry.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "ALL 11 CLUSTERS CHARACTERIZED + DOMINANCE MECHANISM DIAGNOSED, "
    "two-track sequencing RECOMMENDATION ready (Pete's call, not decided)"
)
NEW_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "4TH DOMINANCE PATTERN FOUND (cross-cluster asymmetry), two-track "
    "recommendation revised, Pete's call not decided"
)

OLD_BLOCKER = (
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
NEW_BLOCKER = (
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

OLD_DETAIL_TAIL = (
    "confirmed not fixable via salience alone (rank-8's actual pilot "
    "evidence, reinforced by this session's broader theft-pattern "
    "data), the harder track, sequenced separately from Track 1."
)
NEW_DETAIL_TAIL = (
    "confirmed not fixable via salience alone (rank-8's actual pilot "
    "evidence, reinforced by this session's broader theft-pattern "
    "data), the harder track, sequenced separately from Track 1. "
    "**the_uninitiated re-"
    "characterized, 2026-08-20 -- moved OUT of Track 1, a 4th pattern "
    "found instead:** initially assigned to Track 1 on theft-shape alone "
    "(\"narrow, same-dimension\"). Pulling and checking all 22 stolen "
    "profiles directly (not assuming a clean pairing) found something "
    "different. Full detail: prompts/scd-wcs-cluster-map-findings.md, "
    "\"A fourth dominance pattern\" section. The 22 decompose into 3 "
    "groups: 6 are pure tie-break artifacts (decision_paralysis x3, "
    "the_lost_map x3 -- both rank-2 cluster-mates, scores confirmed "
    "byte-identical, already covered by rank-2's known 10-way tie, not "
    "new dominance). 14 of the remaining 16 (87.5%) are genuine wins "
    "(real score gaps, 0.023-0.065, not ties) concentrated on ONE OTHER "
    "CLUSTER: rank-3 -- the_uninitiated genuinely outscores 7 of rank-3's "
    "8 states. 2 are a smaller cross-dimensional side note against "
    "decision_blindness (rank-9, already declined). **The real finding: "
    "a cluster-vs-cluster asymmetry, not a 1-to-1 pairing and not a "
    "same-cluster tie.** rank-2 and rank-3 key off the same dimension "
    "(authority) and share identical salience shape (2.5/0.4x3 on both "
    "sides), but rank-3's vector is objectively SHARPER/more "
    "concentrated (0.6 dominant/0.1 floor vs the_uninitiated's 0.45 "
    "dominant/0.15 floor) -- yet the LESS concentrated the_uninitiated "
    "systematically wins. Directly contradicts \"sharper vector wins\" "
    "intuition, sharpens (not just confirms) the earlier finding that "
    "concentration doesn't predict dominance -- here it points the "
    "wrong direction, not just fails to predict. **Why this fits "
    "neither track:** fixing it means reweighting the_uninitiated "
    "against an entire separate 8-state cluster simultaneously, not a "
    "1-to-1 pairing (Track 1's shape) and not a single broad attractor "
    "with no clean opponent (Track 2's shape) -- structurally closer to "
    "a two-cluster remediation project than a pilot. rank-3 remains "
    "fully uniform, only had the earlier stakes/narrative pass, needs "
    "its own dedicated look first. Logged as a 4th, distinct pattern -- "
    "\"cross-cluster asymmetry\" -- flagged as needing further "
    "diagnosis (what property actually predicts which of two competing "
    "clusters wins, since peak concentration was just ruled out, and "
    "ruled out backwards) before it belongs in either track. No "
    "differentiation candidate proposed, no code touched."
)

OLD_TAIL = (
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
NEW_TAIL = (
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

    version_old = "\\\\\\#\\\\\\# MOB v4.216"
    version_new = "\\\\\\#\\\\\\# MOB v4.217"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.216 |"
    claude_new = "| MOB version | v4.217 |"
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
