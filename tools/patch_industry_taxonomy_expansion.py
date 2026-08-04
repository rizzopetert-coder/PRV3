"""
PRV3 -- Log the intake industry taxonomy expansion proposal
(prompts/intake-industry-taxonomy-expansion.md) as a new Priority Queue
item, next to the headcount-precision proposal, same schema-level-scope
flag. Notes the real PAYROLL_BASELINE_GRID research dependency (12 new
cells, genuine SUSB/BLS sourcing needed).

Usage:
  python tools/patch_industry_taxonomy_expansion.py --dry-run
  python tools/patch_industry_taxonomy_expansion.py --write
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
    "\\\\\\#\\\\\\# MOB v4.88",
    "\\\\\\#\\\\\\# MOB v4.89",
)

edit(
    "tools/_mob.txt",
    """5. Intake headcount precision redesign -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-headcount-precision-redesign.md). SCHEMA-LEVEL SCOPE -- larger than any other Friction Tax proposal this session: replaces the 6-value headcount bucket dropdown with a precise numeric "about how many employees" stepper (variable increment: steps of 1 from 1-50, 5 from 50-250, 25 from 250-500, 100 above 500). Originates directly from item 4's ADA/FMLA coverage-threshold lead -- a precise number resolves the bucket-boundary ambiguity completely. Also affects Cluster 4's Title VII damage-cap tiers (100/200/500) and Cluster 5's OSHA penalty-reduction tiers (25/100/250), both currently approximating against bucket edges that don't align with the real statutory boundaries. Blocks nothing currently in progress, but should be SEQUENCED BEFORE Clusters 1, 2, 4, 5 are finalized against Gemini, since their threshold logic changes once headcount is precise rather than bucketed -- reviewing those clusters against Gemini before this resolves risks reviewing logic that's about to change underneath it. Confirmed this session: no bucket-derivation logic exists anywhere in the codebase today -- PAYROLL_BASELINE_GRID and HEADCOUNT_MIDPOINTS (engine/friction_tax.py) are both keyed directly by the 6 bucket strings (built via `for headcount in HEADCOUNT_BUCKETS`), with no function anywhere that maps a precise int to a bucket; this would need to be built from scratch as part of implementation, not adapted from something existing. IntakeData.headcount's type change (str -> int) and whether IntakeEcho should echo a precise number or bucket-like language client-facing are both still open questions in the doc, not yet decided.
6. /diagnostic Stages 4-5 rescoping -- no surviving plan doc, requires Pete to rescope from scratch. Prioritized above other backlog items because it's a live user-facing surface gap, not because it's ready to start.
7. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.
8. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).
9. Infrastructure housekeeping, opportunistic/lower priority: weak-profile test limitation (generate_answers() weak branch ignoring target_state), calibration runner's untested severity follow-on questions (parked, do not raise unless Pete reopens), test_contract.py pre-existing liability_block KeyError, MemPalace drawer-write issue.""",
    """5. Intake headcount precision redesign -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-headcount-precision-redesign.md). SCHEMA-LEVEL SCOPE -- larger than any other Friction Tax proposal this session: replaces the 6-value headcount bucket dropdown with a precise numeric "about how many employees" stepper (variable increment: steps of 1 from 1-50, 5 from 50-250, 25 from 250-500, 100 above 500). Originates directly from item 4's ADA/FMLA coverage-threshold lead -- a precise number resolves the bucket-boundary ambiguity completely. Also affects Cluster 4's Title VII damage-cap tiers (100/200/500) and Cluster 5's OSHA penalty-reduction tiers (25/100/250), both currently approximating against bucket edges that don't align with the real statutory boundaries. Blocks nothing currently in progress, but should be SEQUENCED BEFORE Clusters 1, 2, 4, 5 are finalized against Gemini, since their threshold logic changes once headcount is precise rather than bucketed -- reviewing those clusters against Gemini before this resolves risks reviewing logic that's about to change underneath it. Confirmed this session: no bucket-derivation logic exists anywhere in the codebase today -- PAYROLL_BASELINE_GRID and HEADCOUNT_MIDPOINTS (engine/friction_tax.py) are both keyed directly by the 6 bucket strings (built via `for headcount in HEADCOUNT_BUCKETS`), with no function anywhere that maps a precise int to a bucket; this would need to be built from scratch as part of implementation, not adapted from something existing. IntakeData.headcount's type change (str -> int) and whether IntakeEcho should echo a precise number or bucket-like language client-facing are both still open questions in the doc, not yet decided.
6. Intake industry taxonomy expansion -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-industry-taxonomy-expansion.md). SCHEMA-LEVEL SCOPE, same flag as item 5 -- second intake-schema proposal this session, kept deliberately separate from the headcount-precision redesign per Pete's direction, not combined. Adds "Construction" (NAICS Sector 23) and "Transportation & Warehousing" (NAICS Sectors 48-49) to INTAKE_FIELDS["industry"], expanding 9 -> 11 values. Originates from the Demographic Applicability Filter's Cluster 5 finding that is_high_hazard (HIGH_HAZARD_INDUSTRIES) can only ever fire for 2 of the 9 current industry values, while BLS ranks construction and transportation/warehousing among the highest injury/fatality-rate industries nationally -- both currently fall into "Other," indistinguishable from anything else that doesn't fit. REAL DEPENDENCY, not just a code change: PAYROLL_BASELINE_GRID expands from 6x9=54 cells to 6x11=66 cells -- 12 new cells (Construction and Transportation & Warehousing x all 6 headcount buckets) need genuine SUSB/BLS payroll-baseline research sourced before this is implementation-ready, comparable in scope to the original 54-cell population work, not trivial. HIGH_HAZARD_INDUSTRIES update itself is straightforward (add both new values to the existing set).
7. /diagnostic Stages 4-5 rescoping -- no surviving plan doc, requires Pete to rescope from scratch. Prioritized above other backlog items because it's a live user-facing surface gap, not because it's ready to start.
8. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.
9. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).
10. Infrastructure housekeeping, opportunistic/lower priority: weak-profile test limitation (generate_answers() weak branch ignoring target_state), calibration runner's untested severity follow-on questions (parked, do not raise unless Pete reopens), test_contract.py pre-existing liability_block KeyError, MemPalace drawer-write issue.""",
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
