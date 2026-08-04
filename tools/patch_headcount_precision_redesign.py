"""
PRV3 -- Log the intake headcount precision redesign proposal
(prompts/intake-headcount-precision-redesign.md) as a new Priority
Queue item, flagged schema-level scope and sequenced before Clusters
1, 2, 4, 5 go to Gemini review.

Usage:
  python tools/patch_headcount_precision_redesign.py --dry-run
  python tools/patch_headcount_precision_redesign.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.86",
    "\\\\\\#\\\\\\# MOB v4.87",
)

edit(
    "tools/_mob.txt",
    """4. Demographic Applicability Filter -- systematic pass across Clusters 1, 2, 3, 5 -- NOT STARTED. Two live leads already surfaced (Addendum 5), pull the details next time this is picked up: (a) ADA (15+ employees) / FMLA (50+ employees) coverage thresholds likely affect Clusters 1 and 2's "Under 25" headcount bucket -- employers below the statutory threshold may not be covered by those clusters' mechanisms at all, mirrors Cluster 4's own coverage-threshold caveat (Addendum 5); (b) engine/accumulation.py's existing `is_high_hazard` property (checks `industry` against `HIGH_HAZARD_INDUSTRIES`) should probably gate Cluster 5's OSHA-based figures rather than leaving them industry-blind -- pull the actual HIGH_HAZARD_INDUSTRIES list before scoping this.
5. /diagnostic Stages 4-5 rescoping -- no surviving plan doc, requires Pete to rescope from scratch. Prioritized above other backlog items because it's a live user-facing surface gap, not because it's ready to start.
6. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.
7. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).
8. Infrastructure housekeeping, opportunistic/lower priority: weak-profile test limitation (generate_answers() weak branch ignoring target_state), calibration runner's untested severity follow-on questions (parked, do not raise unless Pete reopens), test_contract.py pre-existing liability_block KeyError, MemPalace drawer-write issue.""",
    """4. Demographic Applicability Filter -- systematic pass across Clusters 1, 2, 3, 5 -- NOT STARTED. Two live leads already surfaced (Addendum 5), pull the details next time this is picked up: (a) ADA (15+ employees) / FMLA (50+ employees) coverage thresholds likely affect Clusters 1 and 2's "Under 25" headcount bucket -- employers below the statutory threshold may not be covered by those clusters' mechanisms at all, mirrors Cluster 4's own coverage-threshold caveat (Addendum 5); (b) engine/accumulation.py's existing `is_high_hazard` property (checks `industry` against `HIGH_HAZARD_INDUSTRIES`) should probably gate Cluster 5's OSHA-based figures rather than leaving them industry-blind -- pull the actual HIGH_HAZARD_INDUSTRIES list before scoping this.
5. Intake headcount precision redesign -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-headcount-precision-redesign.md). SCHEMA-LEVEL SCOPE -- larger than any other Friction Tax proposal this session: replaces the 6-value headcount bucket dropdown with a precise numeric "about how many employees" stepper (variable increment: steps of 1 from 1-50, 5 from 50-250, 25 from 250-500, 100 above 500). Originates directly from item 4's ADA/FMLA coverage-threshold lead -- a precise number resolves the bucket-boundary ambiguity completely. Also affects Cluster 4's Title VII damage-cap tiers (100/200/500) and Cluster 5's OSHA penalty-reduction tiers (25/100/250), both currently approximating against bucket edges that don't align with the real statutory boundaries. Blocks nothing currently in progress, but should be SEQUENCED BEFORE Clusters 1, 2, 4, 5 are finalized against Gemini, since their threshold logic changes once headcount is precise rather than bucketed -- reviewing those clusters against Gemini before this resolves risks reviewing logic that's about to change underneath it. Confirmed this session: no bucket-derivation logic exists anywhere in the codebase today -- PAYROLL_BASELINE_GRID and HEADCOUNT_MIDPOINTS (engine/friction_tax.py) are both keyed directly by the 6 bucket strings (built via `for headcount in HEADCOUNT_BUCKETS`), with no function anywhere that maps a precise int to a bucket; this would need to be built from scratch as part of implementation, not adapted from something existing. IntakeData.headcount's type change (str -> int) and whether IntakeEcho should echo a precise number or bucket-like language client-facing are both still open questions in the doc, not yet decided.
6. /diagnostic Stages 4-5 rescoping -- no surviving plan doc, requires Pete to rescope from scratch. Prioritized above other backlog items because it's a live user-facing surface gap, not because it's ready to start.
7. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.
8. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).
9. Infrastructure housekeeping, opportunistic/lower priority: weak-profile test limitation (generate_answers() weak branch ignoring target_state), calibration runner's untested severity follow-on questions (parked, do not raise unless Pete reopens), test_contract.py pre-existing liability_block KeyError, MemPalace drawer-write issue.""",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
