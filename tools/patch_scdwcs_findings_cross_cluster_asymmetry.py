"""
Add the_uninitiated's dominance characterization to
prompts/scd-wcs-cluster-map-findings.md as a fourth, distinct dominance
pattern -- "cross-cluster asymmetry" -- separate from Track 1 (narrow
same-cluster neighbor-stealing) and Track 2 (broad cross-dimensional
attraction). Diagnostic only, no code changes, no differentiation
candidate proposed.

Usage:
    python patch_scdwcs_findings_cross_cluster_asymmetry.py --dry-run
    python patch_scdwcs_findings_cross_cluster_asymmetry.py --write
"""
import argparse
import difflib
from pathlib import Path

DOC_PATH = Path("prompts/scd-wcs-cluster-map-findings.md")

OLD_TAIL = (
    "Not scoped or actioned here. Both tracks, their relative priority\n"
    "against each other and against `invisible_performance_management`'s\n"
    "own unscoped investigation, and whether Track 1 continues at all given\n"
    "rank-1/rank-2's scale (see \"Full cluster characterization\" above) are\n"
    "all Pete's call.\n"
    "\n"
    "## Cross-references\n"
)
NEW_TAIL = (
    "Not scoped or actioned here. Both tracks, their relative priority\n"
    "against each other and against `invisible_performance_management`'s\n"
    "own unscoped investigation, and whether Track 1 continues at all given\n"
    "rank-1/rank-2's scale (see \"Full cluster characterization\" above) are\n"
    "all Pete's call.\n"
    "\n"
    "## A fourth dominance pattern — cross-cluster asymmetry (`the_uninitiated`)\n"
    "\n"
    "**Characterization only, 2026-08-20. No code changed, no differentiation\n"
    "candidate proposed.** `the_uninitiated` (rank-2, 12.6% false rank-1, the\n"
    "session's second-largest dominance signal) was initially assigned to\n"
    "Track 1 on the strength of its \"narrow, same-dimension\" theft shape.\n"
    "Pulling the actual 22 stolen profiles and checking each one directly —\n"
    "not assuming a clean pairing exists — shows something structurally\n"
    "different from both tracks.\n"
    "\n"
    "**The 22 decompose into three distinct groups, not one:**\n"
    "\n"
    "1. **6 are pure tie-break artifacts, not new dominance at all.**\n"
    "   `decision_paralysis` (×3) and `the_lost_map` (×3) are\n"
    "   `the_uninitiated`'s own rank-2 cluster-mates. Checked directly: scores\n"
    "   are byte-identical in all 6 cases (e.g. `AUT-DP-01`: both\n"
    "   `0.985507`). This is rank-2's already-logged 10-way uniform tie —\n"
    "   `the_uninitiated` only wins the insertion-order tie-break, nothing\n"
    "   new is happening here.\n"
    "2. **14 of the remaining 16 (87.5%) are genuine wins concentrated on one\n"
    "   other cluster: rank-3.** `the_uninitiated` genuinely outscores 7 of\n"
    "   rank-3's 8 states (`the_founders_grip` ×3, `disparate_impact_"
    "architecture`\n"
    "   ×3, `sequential_decision_blindness` ×3, `heard_and_ignored` ×2,\n"
    "   `hr_capture` ×1, `the_tolerated_violation` ×1, `the_unsolved_problem`\n"
    "   ×1 — real score gaps, 0.023–0.065, not ties).\n"
    "3. **2 are a smaller, separate, cross-dimensional side note** — genuine\n"
    "   wins against `decision_blindness` (rank-9, alliance-dominant, not\n"
    "   authority-dominant), the largest single gap of the set (0.250), but\n"
    "   rank-9 is already characterized and declined.\n"
    "\n"
    "**The real finding is #2 — a cluster-vs-cluster asymmetry, not a\n"
    "1-to-1 pairing and not a same-cluster tie.** `the_uninitiated`\n"
    "(rank-2) and rank-3 both key off the same dimension (authority) and\n"
    "share the identical salience *shape* (authority=2.5/2.5, rest 0.4/0.4)\n"
    "— but their vectors differ in concentration: `the_uninitiated`'s\n"
    "authority_liability sits at 0.45 with a 0.15 floor elsewhere; rank-3's\n"
    "sits at 0.6 with a 0.1 floor elsewhere — objectively the *sharper,\n"
    "more concentrated* vector of the two. Despite that, the *less*\n"
    "concentrated `the_uninitiated` systematically beats rank-3 across 7 of\n"
    "its 8 states. This directly contradicts the simple \"sharper vector\n"
    "wins\" intuition, and sharpens (not just confirms) the\n"
    "dominance-mechanism investigation's earlier finding that vector\n"
    "concentration doesn't predict dominance magnitude — here it's not just\n"
    "non-predictive, it points the wrong way.\n"
    "\n"
    "**Why this doesn't belong in either existing track:** fixing it would\n"
    "mean reweighting `the_uninitiated` against an entire separate 8-state\n"
    "cluster simultaneously, not a 1-to-1 pairing (Track 1's shape) and not\n"
    "a single broad attractor with no clean opponent (Track 2's shape) —\n"
    "structurally closer to a two-cluster remediation project than a pilot.\n"
    "rank-3 itself remains fully uniform and has only had the earlier\n"
    "stakes/narrative pass (see \"Full cluster characterization\" above) —\n"
    "it needs its own dedicated look before any fix here makes sense.\n"
    "\n"
    "**Logged as a fourth, distinct dominance pattern — \"cross-cluster\n"
    "asymmetry\"** — separate from Track 1 (narrow same-cluster\n"
    "neighbor-stealing) and Track 2 (broad cross-dimensional attraction).\n"
    "Flagged as needing further diagnosis, specifically: what property\n"
    "actually predicts which of two competing clusters wins, since peak\n"
    "concentration was just ruled out (and ruled out in the wrong\n"
    "direction, not just as a non-predictor). Not assigned to either track\n"
    "until that's understood. No differentiation candidate proposed, no\n"
    "code touched.\n"
    "\n"
    "## Cross-references\n"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = DOC_PATH.read_text(encoding="utf-8")

    count = text.count(OLD_TAIL)
    if count != 1:
        raise SystemExit(f"ABORT: expected exactly 1 match, found {count}")
    text = text.replace(OLD_TAIL, NEW_TAIL, 1)

    if args.dry_run:
        original = DOC_PATH.read_text(encoding="utf-8")
        print(f"\n{'=' * 80}\nDIFF: {DOC_PATH}\n{'=' * 80}")
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            text.splitlines(keepends=True),
            fromfile=f"{DOC_PATH} (before)",
            tofile=f"{DOC_PATH} (after)",
        )
        print("".join(diff))
        print("\nDry run complete. No files written. Re-run with --write to apply.")
    else:
        DOC_PATH.write_text(text, encoding="utf-8")
        print(f"WROTE: {DOC_PATH}")


if __name__ == "__main__":
    main()
