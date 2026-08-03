"""
PRV3 -- Option A rescale locked (Gemini-reviewed, cleared) + Legal/Compliance
fully split out of the 4-criterion rubric down to 3.

Rewrites, in full, two prompts docs whose numeric bases changed together
this session (target range, raw-score range, breadth range are all
cross-referenced between them and must stay consistent):

  - prompts/friction-tax-state-multiplier-methodology.md
      Combination function rescaled: target range [1.0, 1.4] -> [0.05, 0.25]
      (payroll fraction), raw score range [0, 8] -> [0, 6] (3 criteria x 0-2,
      Legal/Compliance removed from this rubric's raw score). Status line
      corrected (scoring has long been complete; this doc previously said
      otherwise). Gemini review of the rescale (structural + worked
      dollar-figure plausibility check, 3%-49% of payroll) logged as cleared.

  - prompts/friction-tax-multistate-compounding-methodology.md
      "4 criteria" -> "3 criteria" throughout Steps 1 and 3 (Legal/Compliance
      no longer part of this loop). Breadth range [1,4] -> [1,3] in Step 3's
      multi_channel_severity_loading formula and worked examples. Step 2's
      frozen-range note updated to [0, 6] / [0.05, 0.25]. K=0.05's CLOSED
      rationale corrected: the rejected 0.15 alternative's max swing is 30%
      at the corrected breadth range (was calculated as 45% under the old
      4-criterion range) -- K itself is NOT reopened, this is an arithmetic
      correction only. "Explicitly deferred" section rewritten: Legal/
      Compliance is no longer deferred-pending-a-conversation, it already
      has its own separate, actively in-progress design.

Also updates tools/_mob.txt:
  - Version bump v4.78 -> v4.79
  - Section 13b Priority Queue item 1: Option A marked Gemini-reviewed and
    LOCKED (was "next: Gemini re-review"), with the raw-score-range and
    breadth-range dependencies spelled out for whoever implements.
  - Section 14 lock entry for multi_channel_severity_loading (K)=0.05:
    45% max-swing figure corrected to 30% (breadth range 1-4 -> 1-3),
    documentation correction only, K not reopened.

Usage:
  python tools/patch_ftm_option_a_3criteria.py --dry-run
  python tools/patch_ftm_option_a_3criteria.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRATCH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad"
)

FULL_REWRITES: list[tuple[str, str, str]] = [
    (
        "prompts/friction-tax-state-multiplier-methodology.md",
        "Scoring not yet started",  # marker that must be present in current file
        str(SCRATCH / "state_multiplier_new.md"),
    ),
    (
        "prompts/friction-tax-multistate-compounding-methodology.md",
        "the four underlying criterion scores",  # marker that must be present
        str(SCRATCH / "compounding_new.md"),
    ),
]

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.78",
    "\\\\\\#\\\\\\# MOB v4.79",
)

edit(
    "tools/_mob.txt",
    "1. Option A confirmed (Pete, reconfirmed this session) — rescale Set 3's target mapping from [1.0, 1.4] to a payroll-fraction range, sourced at roughly 5%-25% (productivity 14-18% Gallup Q12-solid; turnover ~13% typical/~38% elevated-solid; decision-quality ~5-7% Track B reconstruction-softer, no direct source). Scope is now clean: Legal/Compliance is fully split out to its own mechanism-aware design (prompts/friction-tax-legal-compliance-methodology.md) and no longer needs to share this range, which removes the original objection to Option A (stretching one range to awkwardly fit both attritional and tail risk). Option B (hard cap gate) is no longer under consideration. Next: Gemini architecture re-review of the rescale, scoped to the three attritional criteria only, before CC implements.",
    "1. Option A rescale LOCKED -- Gemini-reviewed and cleared this session (structural check + worked dollar-figure plausibility check across mild/typical/severe scenarios, all landing in a defensible 3%-49% of payroll range). Full formula and rationale in prompts/friction-tax-state-multiplier-methodology.md: target range [0.05, 0.25] (payroll fraction) replacing [1.0, 1.4], raw score range [0, 6] (3 criteria x 0-2 -- Legal/Compliance no longer part of this rubric) replacing [0, 8]. Option B (hard cap gate) dropped. Ready for implementation in compute_friction_tax(). DEPENDENCIES for whoever implements: (a) recompute each of the 57 states' raw_total using only the 3 remaining criteria (turnover, productivity, decision_quality), dropping the original Legal/Compliance sub-score, before applying the new formula; (b) the multi-state compounding redesign's breadth range is corrected from [1,4] to [1,3] and its Step 2 normalization mapping updated to [0.05, 0.25]/[0, 6] (both already corrected in prompts/friction-tax-multistate-compounding-methodology.md this session); (c) the single-state continuity check must be verified against [0, 6], not the original [0, 8].",
)

edit(
    "tools/_mob.txt",
    "| **August 2026 — Friction Tax multi_channel_severity_loading (K) locked at 0.05** | Pete's final decision, closing the last open parameter of the multi-state compounding redesign (methodology locked 608a945→242379a). Treats the multi-area premium as a tiebreaker, not a primary cost driver: the strongest alternative considered (0.15) tops out at a 45% max swing at full breadth, proportionate to the depth lever's 40% max swing and well under severity's ~133% max swing. Not to be reopened absent new information. Implementation (Priority Queue item 1) is the remaining step, now flagged to be sequenced after Gemini review of the newly surfaced Friction Tax output-ceiling plausibility finding (Section 13a) since both touch compute_friction_tax(). MOB v4.76. |",
    "| **August 2026 — Friction Tax multi_channel_severity_loading (K) locked at 0.05** | Pete's final decision, closing the last open parameter of the multi-state compounding redesign (methodology locked 608a945→242379a). Treats the multi-area premium as a tiebreaker, not a primary cost driver: the strongest alternative considered (0.15) tops out at a 30% max swing at full breadth, proportionate to the depth lever's 40% max swing and well under severity's ~133% max swing. Not to be reopened absent new information. Implementation (Priority Queue item 1) is the remaining step, now flagged to be sequenced after Gemini review of the newly surfaced Friction Tax output-ceiling plausibility finding (Section 13a) since both touch compute_friction_tax(). **CORRECTION (this session, documentation only -- K not reopened):** the 45% figure above was calculated under the original 4-criterion breadth range (1-4). Legal/Compliance has since been split out to its own separate design (prompts/friction-tax-legal-compliance-methodology.md), correcting the breadth range to 1-3 -- the alternative's actual max swing is 30%, and K=0.05's own max swing at full breadth is 10%, making K=0.05 even more conservative relative to the depth lever's 40% max than originally calculated, not less. MOB v4.76. |",
)


def apply(dry_run: bool) -> int:
    changed = 0

    for rel_path, marker, new_content_path in FULL_REWRITES:
        path = REPO_ROOT / rel_path
        current = path.read_text(encoding="utf-8")
        if marker not in current:
            print(f"ERROR: {rel_path} -- expected marker not found: {marker!r}")
            print("  File may have changed since this script was written.")
            return 1
        new_content = Path(new_content_path).read_text(encoding="utf-8")
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- marker confirmed present, would rewrite "
                  f"({len(current)} -> {len(new_content)} chars)")
        else:
            path.write_text(new_content, encoding="utf-8")
            print(f"WRITTEN: {rel_path} ({len(current)} -> {len(new_content)} chars)")
        changed += 1

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

    print(f"\n{changed}/{len(FULL_REWRITES) + len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
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
