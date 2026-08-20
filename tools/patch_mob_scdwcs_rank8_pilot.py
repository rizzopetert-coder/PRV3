"""
MOB update: fold the SCD-WCS rank-8 pilot result (built_to_fail/
the_paper_tiger, commit 58a19a0) into the Decision Register. Framed as
two explicitly separate parts, same as the findings doc: (1) the
tie-break itself, mechanically safe, same kind of result as rank-7;
(2) the dominance finding -- built_to_fail's 28% false-rank-1 rate is a
taxonomy-wide pattern this pilot's scope can't touch, and the pilot's
real significance is reframing built_to_fail as the first
evidence-backed candidate for the dimensional_vector re-authoring layer.

Version bump: v4.213 -> v4.214 (workstream status materially changed --
second remediation result landed, first evidence-backed vector-layer
candidate surfaced).

Usage:
    python patch_mob_scdwcs_rank8_pilot.py --dry-run
    python patch_mob_scdwcs_rank8_pilot.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "PILOT COMPLETE (1 of 11 clusters), remediation sequencing question open"
)
NEW_TITLE = (
    "SCD-WCS / primary-state ranking investigation -- FULLY SCOPED, "
    "2 PILOTS LANDED + 1 VERIFICATION DECLINED (3 of 11 clusters "
    "touched), first vector-layer candidate identified"
)

OLD_BLOCKER = (
    "None active on the pilot itself (closed, commit 043b8ad). Real "
    "open question the pilot raised, Pete's call: when salience-only "
    "can't achieve narrative-correct differentiation within "
    "calibration-safe bounds (confirmed true for this cluster), does "
    "that cluster get left as a mechanical-only fix, combined with a "
    "targeted vector nudge, or deferred to the larger vector "
    "re-authoring pass? No general answer yet -- needs testing against "
    "a few more clusters before any pattern can be claimed. Not a "
    "blocker on sequencing timing/priority, which remains Pete's call "
    "as before."
)
NEW_BLOCKER = (
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

OLD_DETAIL_TAIL = (
    "**Scope discipline held:** this pilot covered exactly one cluster; "
    "its result (a real, unresolved narrative-vs-calibration tension) "
    "is the signal to bring back for a sequencing conversation, not "
    "confirmation to mechanically repeat the search across the "
    "remaining 8 salience-uniform clusters -- not attempted, not "
    "assumed to generalize."
)
NEW_DETAIL_TAIL = (
    "**Scope discipline held:** this pilot covered exactly one cluster; "
    "its result (a real, unresolved narrative-vs-calibration tension) "
    "is the signal to bring back for a sequencing conversation, not "
    "confirmation to mechanically repeat the search across the "
    "remaining 8 salience-uniform clusters -- not attempted, not "
    "assumed to generalize. **Rank-9 cluster check (the_fracture/"
    "decision_blindness), verification-only, no code changed:** initial "
    "working hypothesis (Alliance/Authority split) revised after direct "
    "checks -- the mechanism has real precedent elsewhere "
    "(the_suppression_filter's Authority secondary) but "
    "decision_blindness's own descriptive_prose explicitly rules out an "
    "authority/exclusion framing for this pair. Both states also route "
    "to the same resolution_family (\"Intervention + Executive "
    "Counsel\") -- low practical stakes regardless. Logged as a real "
    "tie, accurately authored, not prioritized for further pursuit. "
    "**Rank-8 pilot (built_to_fail/the_paper_tiger), SHIPPED, commit "
    "58a19a0 -- two explicitly separate results, not collapsed into "
    "one:** (1) The tie-break: mechanically safe, same kind of success "
    "as rank-7. Both states shared an identical dimensional_vector plus "
    "identical salience, guaranteed exact-tie on 175/175 profiles. "
    "built_to_fail's salience stays unchanged (approved as-is); "
    "the_paper_tiger differentiated on two axes (aptitude reduced, "
    "authority raised -- real precedent, the_suppression_filter's own "
    "Authority secondary carries the same magnitude class -- attitude "
    "raised, both per its real descriptive_prose). 4 candidates searched "
    "against the real pipeline, all passed identically clean; landed on "
    "aptitude=1.0/authority=1.0/attitude=1.5, best worst-case gap floor "
    "(min 0.0195) among candidates tested. Tie fully broken (175/175 -> "
    "0/175), zero cross-contamination (full 58x175 comparison -- one "
    "methodology note: a first pass showed 350 false-positive "
    "contamination hits from comparing against a stale pre-rank-7 "
    "baseline, caught and corrected before reporting), regression "
    "exactly at the 171/175 baseline, real margin on all 4 affected "
    "profiles (built_to_fail's own 3 untouched at a perfect 0.0000 "
    "self-match; the_paper_tiger's 4 pass with 0.077-0.143 gap to "
    "rank-1). (2) The dominance finding, the pilot's actually "
    "significant result: built_to_fail wins a false rank-1 in 49/175 "
    "profiles (28%), quantified directly from the calibration snapshot. "
    "This rate does NOT move at any tested magnitude (aptitude 1.0-2.0, "
    "a wide spread) -- confirmed structurally, not just empirically: "
    "built_to_fail and the_paper_tiger share an identical "
    "dimensional_vector, and built_to_fail's own fixed aptitude weight "
    "(2.5) beats any the_paper_tiger-only salience reweighting on "
    "the_paper_tiger's own aptitude-flavored profiles. Only 4 of the 49 "
    "false-rank-1 profiles are the_paper_tiger's; the other 45 are "
    "unrelated states entirely -- a taxonomy-wide dominance pattern this "
    "pilot's scope was never going to reach. **This is the first "
    "concrete, evidence-backed candidate in the whole SCD-WCS "
    "investigation for the dimensional_vector re-authoring layer** -- "
    "built_to_fail specifically, not an item in an undifferentiated "
    "43+-state backlog."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on the "
    "sequencing question the pilot raised (mechanical-only vs. targeted "
    "vector nudge vs. defer-to-full-remediation, when narrative fidelity "
    "isn't achievable within calibration-safe bounds) before any further "
    "clusters are attempted -- not a forced check-in, but this pilot's "
    "own result is the open item, not a green light to proceed. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on both "
    "open questions -- rank-7's mechanical-only/vector-nudge/defer "
    "sequencing question, and whether built_to_fail becomes a named "
    "priority whenever the dimensional_vector re-authoring layer opens "
    "-- before any further clusters are attempted. Not a forced "
    "check-in; both pilots' results are themselves the open items, not "
    "a green light to continue mechanically through the remaining "
    "clusters. |"
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

    version_old = "\\\\\\#\\\\\\# MOB v4.213"
    version_new = "\\\\\\#\\\\\\# MOB v4.214"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.213 |"
    claude_new = "| MOB version | v4.214 |"
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
