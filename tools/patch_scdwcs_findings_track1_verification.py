"""
Add the Track 1 membership verification pass to
prompts/scd-wcs-cluster-map-findings.md -- same tie-vs-genuine
decomposition check already run on the_uninitiated, applied to the
remaining 3 provisional Track 1 members. Last characterization pass for
this session per Pete's instruction -- no code changes, no direction
proposed, no further investigation initiated after this regardless of
result.

Usage:
    python patch_scdwcs_findings_track1_verification.py --dry-run
    python patch_scdwcs_findings_track1_verification.py --write
"""
import argparse
import difflib
from pathlib import Path

DOC_PATH = Path("prompts/scd-wcs-cluster-map-findings.md")

OLD_TAIL = (
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
NEW_TAIL = (
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
    "## Track 1 membership verification — 0 of 3 remaining candidates confirmed clean\n"
    "\n"
    "**Characterization only, 2026-08-20 — the last characterization pass\n"
    "for this session. No code changes, no direction proposed, no further\n"
    "investigation initiated regardless of result.** `the_uninitiated`\n"
    "turned out to hide a cross-cluster asymmetry rather than a simple\n"
    "same-cluster neighbor-steal (above). Before treating the remaining 3\n"
    "provisional Track 1 members as confirmed, the same tie-vs-genuine\n"
    "decomposition check — for every stolen profile, confirm it's a real\n"
    "score win rather than an insertion-order tie-break against a\n"
    "cluster-mate, then check whether the genuine wins concentrate on one\n"
    "identifiable cluster/state or spread across a separate one — was run\n"
    "on all 3. **None came back clean.**\n"
    "\n"
    "**`the_unexamined_algorithm` — SURPRISE.** Has no cluster of its own\n"
    "(genuinely unique vector), so same-cluster tie-break can't apply at\n"
    "all — confirmed 0 of 11 stolen profiles are tie-artifacts, all 11 are\n"
    "genuine wins. But they spread across three different clusters, not\n"
    "one: rank-3 (6, 54.5%), rank-2 (4, 36.4%), rank-9 (1, 9%). Structurally\n"
    "can't be a same-cluster neighbor-steal (no cluster to be narrow\n"
    "about), and isn't a clean single cross-cluster pairing either — a\n"
    "smaller-scale version of Track 2's broad-attractor shape (multiple\n"
    "clusters), far less extreme than `built_to_fail`/`invisible_"
    "performance_management` but not Track 1's shape.\n"
    "\n"
    "**`the_second_close` — SURPRISE.** 3 of 5 stolen profiles are\n"
    "tie-artifacts against `silosolation`, its own rank-6 cluster-mate\n"
    "(scores confirmed byte-identical) — already covered by rank-6's known\n"
    "uniform tie, not new dominance. The only 2 genuine wins are both\n"
    "against `the_fracture` (rank-9, already characterized and declined as\n"
    "low-stakes). Once the tie-artifact noise is stripped, there's almost\n"
    "no real signal left, and what remains points at an unrelated,\n"
    "already-closed cluster rather than confirming a clean pairing within\n"
    "rank-6.\n"
    "\n"
    "**`culture_drift` — SURPRISE.** 1 of 5 stolen profiles is a\n"
    "tie-artifact against `wellbeing_theater`, its own rank-11 cluster-mate.\n"
    "The 4 genuine wins split across two different clusters:\n"
    "`the_broken_compass` ×3 (rank-1, 75%) and `the_inner_circle` ×1\n"
    "(rank-10, 25% — notable that this is a genuine win, not a tie, despite\n"
    "`the_inner_circle`'s already-resolved differentiation). Not a single\n"
    "clean pairing.\n"
    "\n"
    "**Net: 0 of the 4 original \"narrow neighbor-stealer\" candidates\n"
    "(`the_uninitiated` plus these 3) survive verification as a clean\n"
    "same-cluster Track 1 pairing.** Worth stating plainly as its own\n"
    "finding: the \"narrow, same-dimension theft\" heuristic from the\n"
    "dominance-mechanism investigation does not reliably predict a clean\n"
    "same-cluster pairing once actually checked — 0-for-4 as a screening\n"
    "criterion in this session's data, not a pattern to keep trusting at\n"
    "face value. Track 1, as originally scoped (a set of clean,\n"
    "structurally-similar-to-rank-7 pairings ready for pilot-style\n"
    "remediation), currently has no confirmed members. Each of the 4 is\n"
    "its own more complex case — three additional cross-cluster-flavored\n"
    "patterns alongside `the_uninitiated`'s, none yet diagnosed further,\n"
    "none assigned anywhere. Not scoped or actioned here — this is the\n"
    "last characterization pass for the session, per explicit instruction,\n"
    "regardless of what it found.\n"
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
