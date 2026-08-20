"""
MOB update: fold the SCD-WCS salience-differentiation pilot result
(the_unformed_leader/the_dormant_talent, commit 043b8ad) into the
Decision Register -- the first-ever remediation result for the SCD-WCS
investigation. Mechanically validated (tie broken 0/175, zero
cross-contamination, baseline regression preserved), but a narrative
compromise -- aptitude stays dominant on both states, not the
attitude-dominant differentiation the real descriptive_prose argues for.
One confirmed data point, not assumed to generalize to the other 8
salience-uniform clusters. Explicitly NOT a green light to repeat the
search across the remaining clusters -- that's its own sequencing
decision, still open, still Pete's call.

Version bump: v4.212 -> v4.213 (workstream status materially changed --
first remediation result landed, real open question surfaced).

Usage:
    python patch_mob_scdwcs_pilot_result.py --dry-run
    python patch_mob_scdwcs_pilot_result.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, root "
    "cause confirmed, remediation not started"
)
NEW_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "PILOT COMPLETE (1 of 11 clusters), remediation sequencing question open"
)

OLD_BLOCKER = (
    "None active -- Pete's call on sequencing and timing for the full "
    "remediation."
)
NEW_BLOCKER = (
    "None active on the pilot itself (closed, commit 043b8ad). Real open "
    "question the pilot raised, Pete's call: when salience-only can't "
    "achieve narrative-correct differentiation within calibration-safe "
    "bounds (confirmed true for this cluster), does that cluster get left "
    "as a mechanical-only fix, combined with a targeted vector nudge, or "
    "deferred to the larger vector re-authoring pass? No general answer "
    "yet -- needs testing against a few more clusters before any pattern "
    "can be claimed. Not a blocker on sequencing timing/priority, which "
    "remains Pete's call as before."
)

OLD_DETAIL_TAIL = (
    "Full findings, complete cluster map (all 11 clusters, member states, "
    "salience patterns), and the 7 unique states: "
    "prompts/scd-wcs-cluster-map-findings.md."
)
NEW_DETAIL_TAIL = (
    "Full findings, complete cluster map (all 11 clusters, member states, "
    "salience patterns), and the 7 unique states: "
    "prompts/scd-wcs-cluster-map-findings.md. **Pilot result, first-ever "
    "remediation for this investigation (commit 043b8ad, 2026-08-20):** "
    "the_unformed_leader/the_dormant_talent (rank-7 cluster, smallest "
    "cleanest 2-state uniform-salience pair) -- salience-only "
    "differentiation, dimensional_vector deliberately untouched. Two "
    "passes: first (aptitude 1.5/attitude 2.0, making attitude fully "
    "dominant per the real descriptive_prose) broke the tie but regressed "
    "APT-DT-02 below its moderate-tier prominence threshold -- caught by "
    "full-suite regression, not assumed clean. Second pass searched "
    "smaller deltas against the real calibration pipeline (not hand-derived "
    "extrapolation -- the underlying formula is weighted cosine, "
    "nonlinear); landed on aptitude=2.0/attitude=1.3 for the_dormant_talent "
    "(the_unformed_leader's originally proposed attitude=0.6 unchanged, 3/3 "
    "held throughout both passes). **Mechanically validated:** tie fully "
    "broken (175/175 tied before -> 0/175 after, gap range "
    "0.000633-0.139833), zero cross-contamination (full 58-state x "
    "175-profile comparison, not spot-checked -- every other state's score "
    "byte-identical before/after in every profile), full regression exactly "
    "at the 171/175 baseline (same 4 known pre-existing failures, nothing "
    "new), APT-DT-02 passes with real margin (+0.064, not a bare clear). "
    "**Real, load-bearing tension found, not routed around:** every "
    "candidate tested that preserved attitude as the dominant dimension "
    "(matching the actual descriptive_prose -- retained capability plus a "
    "willingness failure) failed APT-DT-02, whose session vector carries "
    "strong aptitude signal. Every candidate keeping aptitude dominant "
    "passed with real margin. The landed value keeps aptitude dominant on "
    "both states -- explicitly NOT a finished clinical differentiation, "
    "the largest safe tie-break found by search. **Scope discipline held:** "
    "this pilot covered exactly one cluster; its result (a real, unresolved "
    "narrative-vs-calibration tension) is the signal to bring back for a "
    "sequencing conversation, not confirmation to mechanically repeat the "
    "search across the remaining 8 salience-uniform clusters -- not "
    "attempted, not assumed to generalize."
)

OLD_TOUCHED_AND_CHECKIN = (
    "This session (Claude Code), 2026-08-19 | Pete's call on sequencing "
    "(salience-first, full vector re-authoring, or staged by cluster "
    "size) and on when to open the full remediation. No forced check-in."
)
NEW_TOUCHED_AND_CHECKIN = (
    "This session (Claude Code), 2026-08-20 | Pete's call on the "
    "sequencing question the pilot raised (mechanical-only vs. targeted "
    "vector nudge vs. defer-to-full-remediation, when narrative fidelity "
    "isn't achievable within calibration-safe bounds) before any further "
    "clusters are attempted -- not a forced check-in, but this pilot's "
    "own result is the open item, not a green light to proceed."
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
        ("last touched + next check-in", OLD_TOUCHED_AND_CHECKIN, NEW_TOUCHED_AND_CHECKIN),
    ]:
        count = mob_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        mob_text = mob_text.replace(old, new, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.212"
    version_new = "\\\\\\#\\\\\\# MOB v4.213"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.212 |"
    claude_new = "| MOB version | v4.213 |"
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
