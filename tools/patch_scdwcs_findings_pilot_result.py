"""
Fold the SCD-WCS salience-differentiation pilot result (the_unformed_leader/
the_dormant_talent, commit 043b8ad) into prompts/scd-wcs-cluster-map-findings.md
-- the first-ever remediation result for this investigation. Updates the
stale "not yet remediated / no vectors or salience weights changed" status
line, the rank-7/9/11 candidate-cluster bullet, and adds a full pilot-result
section before Cross-references.

Usage:
    python patch_scdwcs_findings_pilot_result.py --dry-run
    python patch_scdwcs_findings_pilot_result.py --write
"""
import argparse
import difflib
from pathlib import Path

DOC_PATH = Path("prompts/scd-wcs-cluster-map-findings.md")

OLD_STATUS = (
    "Status: **OPEN, fully scoped, not yet remediated.** Investigation only —\n"
    "no engine code touched, no vectors or salience weights changed. This\n"
    "document is the durable record consolidating the original findings\n"
)
NEW_STATUS = (
    "Status: **OPEN, fully scoped, PILOT COMPLETE (1 of 11 clusters).**\n"
    "First remediation result landed 2026-08-20 (commit 043b8ad) — see\n"
    "\"Pilot result\" below. Remaining 10 clusters not attempted; general\n"
    "remediation sequencing still undecided, Pete's call. This\n"
    "document is the durable record consolidating the original findings\n"
)

OLD_RANK_BULLET = (
    "- **Salience-weight differentiation** is the cheaper, more mechanical\n"
    "  layer — could resolve several smaller clusters (e.g. rank 7, 9, 11\n"
    "  above, each 2-state) without touching any dimensional_vector at all,\n"
    "  the same kind of fix that already differentiates `the_untouchable`\n"
    "  from `the_inner_circle`.\n"
)
NEW_RANK_BULLET = (
    "- **Salience-weight differentiation** is the cheaper, more mechanical\n"
    "  layer — could resolve several smaller clusters (e.g. rank 7, 9, 11\n"
    "  above, each 2-state) without touching any dimensional_vector at all,\n"
    "  the same kind of fix that already differentiates `the_untouchable`\n"
    "  from `the_inner_circle`. Rank 7 now piloted (see \"Pilot result\"\n"
    "  below) — mechanically validated, but narrative-correct\n"
    "  differentiation was not achievable within calibration-safe bounds\n"
    "  for that cluster. One data point, not a confirmed pattern for 9/11\n"
    "  or the remaining clusters.\n"
)

OLD_TAIL = (
    "No remediation approach is being recommended here. Pete's call on\n"
    "sequencing — salience-first, full vector re-authoring, or staged by\n"
    "cluster size — whenever this gets picked up.\n"
    "\n"
    "## Cross-references\n"
)
NEW_TAIL = (
    "No remediation approach is being recommended here. Pete's call on\n"
    "sequencing — salience-first, full vector re-authoring, or staged by\n"
    "cluster size — whenever this gets picked up.\n"
    "\n"
    "## Pilot result — rank-7 cluster (`the_unformed_leader` / `the_dormant_talent`)\n"
    "\n"
    "First-ever remediation result for this investigation. Commit `043b8ad`,\n"
    "2026-08-20. Salience-only differentiation — `dimensional_vector`\n"
    "deliberately untouched, by design, to test whether salience alone can\n"
    "move ranking outcomes before committing to the larger 51-state\n"
    "remediation project.\n"
    "\n"
    "**Two passes.** First (`the_dormant_talent` aptitude 2.5→1.5, attitude\n"
    "1.0→2.0 — making attitude fully dominant, per the real\n"
    "`descriptive_prose`) broke the tie but regressed calibration profile\n"
    "`APT-DT-02` below its moderate-tier prominence threshold — caught by a\n"
    "full-suite regression, not assumed clean. Second pass searched smaller\n"
    "deltas against the real calibration pipeline (not hand-derived\n"
    "extrapolation — the underlying formula is weighted cosine, nonlinear).\n"
    "Landed on `the_dormant_talent` aptitude=2.0/attitude=1.3\n"
    "(`the_unformed_leader`'s originally proposed attitude=0.6 unchanged,\n"
    "its own 3 profiles held 3/3 throughout both passes).\n"
    "\n"
    "**Mechanically validated:**\n"
    "- Tie fully broken: 175/175 calibration profiles tied before this\n"
    "  change → 0/175 tied after, score gap range 0.000633–0.139833.\n"
    "- Zero cross-contamination: full 58-state × 175-profile comparison\n"
    "  (10,150 pairs), not spot-checked — every other state's score\n"
    "  byte-identical before/after in every single profile. Traced to the\n"
    "  formula itself (`rank_states()`, `engine/accumulation.py:572-588`):\n"
    "  each state's score depends only on the session vector and that\n"
    "  state's own profile vector and salience weights, no cross-state term.\n"
    "- Full regression exactly at the 171/175 baseline — same 4\n"
    "  pre-existing failures (`identity_erosion`, `invisible_burnout`,\n"
    "  `leadership_deafness`, `the_untouchable`), nothing new.\n"
    "- `APT-DT-02` passes with real margin: +0.064 above its threshold,\n"
    "  not a bare clear.\n"
    "\n"
    "**Real, load-bearing tension found, not routed around.** Every\n"
    "candidate tested that preserved attitude as the dominant dimension for\n"
    "`the_dormant_talent` (matching the actual `descriptive_prose` —\n"
    "retained capability plus a willingness failure) failed `APT-DT-02`,\n"
    "whose underlying session vector carries strong aptitude signal. Every\n"
    "candidate that kept aptitude dominant passed with real margin. The\n"
    "landed value keeps aptitude dominant on both states — **this is not a\n"
    "finished clinical differentiation**, only the largest safe tie-break\n"
    "found by search.\n"
    "\n"
    "**Open question this raises, Pete's call, not resolved here:** when\n"
    "salience-only can't achieve narrative-correct differentiation within\n"
    "calibration-safe bounds, does that cluster get left as a\n"
    "mechanical-only fix, get combined with a targeted vector nudge, or get\n"
    "deferred to the larger vector re-authoring pass? No general answer\n"
    "yet — this is one confirmed data point, not assumed to generalize to\n"
    "the other 8 salience-uniform clusters. Needs testing against a few\n"
    "more before any pattern can be claimed. This pilot's scope was\n"
    "deliberately one cluster — its result is the signal to bring back for\n"
    "a sequencing conversation, not a green light to mechanically repeat\n"
    "the search across the rest.\n"
    "\n"
    "## Cross-references\n"
)

OLD_XREF_TAIL = (
    "- `engine/data/salience.py` — `SALIENCE_PROFILES`, per-state weighting.\n"
)
NEW_XREF_TAIL = (
    "- `engine/data/salience.py` — `SALIENCE_PROFILES`, per-state weighting.\n"
    "- `tools/_salience_pilot_search.py` (untracked, scratch) — the delta\n"
    "  search used to find the pilot's final magnitude against the real\n"
    "  calibration pipeline.\n"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = DOC_PATH.read_text(encoding="utf-8")

    for label, old, new in [
        ("status line", OLD_STATUS, NEW_STATUS),
        ("rank-7/9/11 bullet", OLD_RANK_BULLET, NEW_RANK_BULLET),
        ("pilot result section", OLD_TAIL, NEW_TAIL),
        ("cross-references", OLD_XREF_TAIL, NEW_XREF_TAIL),
    ]:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        text = text.replace(old, new, 1)

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
