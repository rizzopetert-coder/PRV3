"""
PRV3 MOB update -- Option A rescale + multi-state compounding redesign
IMPLEMENTED and verified (engine/friction_tax.py). Closes Priority Queue
item 1, open since the output-ceiling bug was caught earlier this
session.

Usage:
  python tools/patch_mob_option_a_implemented.py --dry-run
  python tools/patch_mob_option_a_implemented.py --write
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
    "\\\\\\#\\\\\\# MOB v4.79",
    "\\\\\\#\\\\\\# MOB v4.80",
)

edit(
    "tools/_mob.txt",
    "1. Option A rescale LOCKED -- Gemini-reviewed and cleared this session (structural check + worked dollar-figure plausibility check across mild/typical/severe scenarios, all landing in a defensible 3%-49% of payroll range). Full formula and rationale in prompts/friction-tax-state-multiplier-methodology.md: target range [0.05, 0.25] (payroll fraction) replacing [1.0, 1.4], raw score range [0, 6] (3 criteria x 0-2 -- Legal/Compliance no longer part of this rubric) replacing [0, 8]. Option B (hard cap gate) dropped. Ready for implementation in compute_friction_tax(). DEPENDENCIES for whoever implements: (a) recompute each of the 57 states' raw_total using only the 3 remaining criteria (turnover, productivity, decision_quality), dropping the original Legal/Compliance sub-score, before applying the new formula; (b) the multi-state compounding redesign's breadth range is corrected from [1,4] to [1,3] and its Step 2 normalization mapping updated to [0.05, 0.25]/[0, 6] (both already corrected in prompts/friction-tax-multistate-compounding-methodology.md this session); (c) the single-state continuity check must be verified against [0, 6], not the original [0, 8].",
    "1. Option A rescale + multi-state compounding redesign IMPLEMENTED and verified this session (engine/friction_tax.py) -- CLOSES the item open since the output-ceiling bug was caught earlier this session. All 57 states' raw_score/multiplier recomputed under the new [0.05, 0.25] / [0, 6] mapping (Legal/Compliance excluded from the sum, its score preserved for the separate design); compute_friction_tax()'s mean_multiplier fully replaced with the Step 1-3 anchor-plus-diminishing-layers aggregation (geometric decay, K=0.05 breadth loading, N=1 guard forcing loading=1.0 for a single identified state). Verified, not just reasoned about: tools/test_friction_tax.py rewritten 37->45 checks, 45/45 pass, including explicit single-state continuity (bit-for-bit exact match across 10 real states), the N=1 guard, hand-derived Step 1/Step 3 multi-state math (two breadth scenarios), and extrapolation beyond R_max=6. All other engine test suites pass unaffected; 172-profile calibration suite unchanged at 169/172, confirming this change is isolated to Friction Tax and doesn't touch state routing/scoring; tsc clean (FrictionTaxEstimate's {low, high, currency} shape unaffected by the internal formula change).",
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
