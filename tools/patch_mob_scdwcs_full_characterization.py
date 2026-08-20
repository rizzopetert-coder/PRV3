"""
MOB update: fold the full 11-cluster SCD-WCS characterization pass into
the Decision Register. Characterization-only, no code touched, no
weight numbers proposed. Covers the 8 remaining clusters (ranks 1, 2, 3,
4, 5, 6, 10, 11), consolidated with the 3 already-piloted/checked
clusters (7, 8, 9), plus the separately flagged
invisible_performance_management finding (pure vector-strength
dominance, structurally different from every tie/cluster finding in
this investigation).

Version bump: v4.214 -> v4.215 (workstream status materially changed --
full-taxonomy characterization complete, new out-of-scope finding
surfaced, real sequencing input now available).

Usage:
    python patch_mob_scdwcs_full_characterization.py --dry-run
    python patch_mob_scdwcs_full_characterization.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "2 PILOTS LANDED + 1 VERIFICATION DECLINED (3 of 11 clusters "
    "touched), first vector-layer candidate identified"
)
NEW_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "ALL 11 CLUSTERS CHARACTERIZED (2 pilots landed, 1 verification "
    "declined, 8 characterized this pass), full sequencing input ready, "
    "1 new out-of-scope dominance finding"
)

OLD_BLOCKER = (
    "None active on either landed pilot (both closed, commits 043b8ad "
    "and 58a19a0). Two open questions now, both Pete's call, neither a "
    "blocker on timing/priority: (1) rank-7's open question stands "
    "unchanged -- when salience-only can't achieve narrative-correct "
    "differentiation within calibration-safe bounds, mechanical-only "
    "fix, targeted vector nudge, or defer to full remediation? Still "
    "one confirmed data point (rank-7), not a pattern. (2) NEW from "
    "rank-8: built_to_fail is now a named, evidence-backed candidate "
    "for the dimensional_vector re-authoring layer -- does that layer "
    "get scoped around specific high-impact states like built_to_fail "
    "first, rather than treated as one undifferentiated 43+-state "
    "backlog? Not scoped or actioned here."
)
NEW_BLOCKER = (
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

OLD_DETAIL_TAIL = (
    "**This is the first concrete, evidence-backed candidate in the "
    "whole SCD-WCS investigation for the dimensional_vector re-authoring "
    "layer** -- built_to_fail specifically, not an item in an "
    "undifferentiated 43+-state backlog."
)
NEW_DETAIL_TAIL = (
    "**This is the first concrete, evidence-backed candidate in the "
    "whole SCD-WCS investigation for the dimensional_vector re-authoring "
    "layer** -- built_to_fail specifically, not an item in an "
    "undifferentiated 43+-state backlog. **Full 11-cluster "
    "characterization pass, 2026-08-20 -- verification-only, no code "
    "touched, no weight numbers proposed anywhere in this pass.** Same "
    "depth as the rank-8/rank-9 checks (SALIENCE_PROFILES, live "
    "descriptive_prose, dimensional_vector, resolution_family per "
    "state), applied to the 8 remaining clusters (ranks 1, 2, 3, 4, 5, "
    "6, 10, 11), consolidated with the 3 already-piloted/checked "
    "clusters into one table. Full detail: "
    "prompts/scd-wcs-cluster-map-findings.md, \"Full cluster "
    "characterization\" section. Headline reads: rank 1 (11 states) and "
    "rank 2 (10 states) are large, high-stakes (real resolution_family "
    "spread), and narratively real, but that scale is closer to the "
    "full vector-reauthoring project than a quick pilot -- rank 2 also "
    "carries a real dominance signal (the_uninitiated, 22/175, 12.6%). "
    "Rank 6 (3 states, every pairwise resolution_family differs) and "
    "rank 5 (3 states, partial stakes) read as the cleanest remaining "
    "small-pilot candidates if that path continues. Rank 3 and rank 11 "
    "read as low-value/cosmetic, same category as rank 9's already-"
    "logged finding. Rank 4 and rank 10 are partially resolved already "
    "-- rank 10's existing split (the_untouchable/the_inner_circle) is "
    "confirmed well-grounded by its own real narrative distinction, a "
    "validated precedent not an open item. **Separately flagged, a "
    "structurally different kind of finding, not a tie or cluster "
    "question at all:** three genuinely-unique-vector states (no "
    "cluster-mate, no tie to break) show major false-rank-1 dominance "
    "on raw vector strength alone -- invisible_performance_management "
    "(59/175, 33.7%, ZERO true rank-1 ever -- the single largest "
    "dominance problem in the entire taxonomy, larger than "
    "built_to_fail's 28%), the_unexamined_algorithm (11/175, 6.3%), "
    "the_overloaded_manager (4/175, 2.3%). No salience or tie "
    "remediation touches this class of problem -- flagged as needing "
    "its own future investigation, independent of the cluster/tie "
    "remediation track this whole investigation has been about."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on both "
    "open questions -- rank-7's mechanical-only/vector-nudge/defer "
    "sequencing question, and whether built_to_fail becomes a named "
    "priority whenever the dimensional_vector re-authoring layer opens "
    "-- before any further clusters are attempted. Not a forced "
    "check-in; both pilots' results are themselves the open items, not "
    "a green light to continue mechanically through the remaining "
    "clusters. |"
)
NEW_TAIL = (
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

    version_old = "\\\\\\#\\\\\\# MOB v4.214"
    version_new = "\\\\\\#\\\\\\# MOB v4.215"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.214 |"
    claude_new = "| MOB version | v4.215 |"
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
