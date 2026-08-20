"""
Add the rank-9 cluster check result (the_fracture/decision_blindness --
real tie, accurately authored, low downstream impact, not pursued
further) to prompts/scd-wcs-cluster-map-findings.md. Verification-only
finding, no code changed, distinct in kind from the rank-7 "Pilot
result" section above it. Revises the initial (weaker) working
hypothesis reported before this check: not a schema limitation --
precedent for an Alliance-primary/Authority-secondary split exists
elsewhere in the taxonomy (the_suppression_filter) -- the real finding
is narrower, no textual basis in decision_blindness's own
descriptive_prose for that specific pattern.

Usage:
    python patch_scdwcs_findings_rank9_rank8.py --dry-run
    python patch_scdwcs_findings_rank9_rank8.py --write
"""
import argparse
import difflib
from pathlib import Path

DOC_PATH = Path("prompts/scd-wcs-cluster-map-findings.md")

OLD_TAIL = (
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
NEW_TAIL = (
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
    "## Cluster check — rank-9 (`the_fracture` / `decision_blindness`)\n"
    "\n"
    "Verification pass only, 2026-08-20 — no code changed. `SALIENCE_PROFILES`\n"
    "confirmed byte-identical for both (`engine/data/salience.py`, ALLIANCE —\n"
    "HIGH tier), `dimensional_vector` confirmed identical (`alliance_liability`\n"
    "dominant at 0.6, matches the cluster map's rank-9 row).\n"
    "\n"
    "**Not a schema limitation — the real finding is narrower.** An initial\n"
    "working hypothesis (Alliance-liability for `the_fracture`,\n"
    "Authority-liability/exclusion-from-decision-rights for\n"
    "`decision_blindness`) was checked against the live `descriptive_prose`\n"
    "and against precedent elsewhere in the taxonomy. The mechanism itself is\n"
    "real: `the_suppression_filter` (also Alliance-primary) already carries an\n"
    "Authority-secondary weight (`authority_liability/asset = 1.0`, above the\n"
    "0.4 floor) — an Alliance/Authority split is an authored pattern in this\n"
    "schema, not an invented one. What doesn't hold up is applying it to this\n"
    "pair: `decision_blindness`'s own prose explicitly rules out an\n"
    "authority/exclusion framing — *\"The decision-maker wasn't negligent. The\n"
    "information simply never reached them, because nobody's job was making\n"
    "sure it did\"* — an information-routing gap, not a decision-rights\n"
    "exclusion. No confident secondary-dimension read was found for either\n"
    "state in this pair.\n"
    "\n"
    "**Low downstream impact, independent of the above.** Both states route to\n"
    "the same `resolution_family` — `\"Intervention + Executive Counsel\"` —\n"
    "confirmed via direct read of `engine/data/states.py`. Whichever state wins\n"
    "an unresolved tie here, a real respondent gets the same resolution\n"
    "recommendation either way.\n"
    "\n"
    "**Logged as:** a real tie, accurately authored given the available\n"
    "textual grounding, low practical/product stakes — not prioritized for\n"
    "further pursuit. Not a candidate for a salience or vector remediation\n"
    "pass unless the underlying descriptive_prose for one of these two states\n"
    "changes.\n"
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
