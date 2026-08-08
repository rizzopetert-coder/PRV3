"""
Two unrelated pieces of work, bundled per Pete's explicit sequencing
this session:

1. DOCUMENTATION-ONLY CORRECTIONS (no code/logic change): the Friction
   Tax multi-state compounding redesign turned out to already be fully
   implemented (commit 8de807a, 2026-08-03, MOB v4.80) -- five days
   before this session, unrelated to tonight's MC_CENTROID_39 work.
   Both prompts/*.md design docs and two tools/_mob.txt Section 13a
   Decision Register rows still describe it as pending/not-yet-
   reviewed/blocking-implementation. Corrected to point at the real
   commit instead of a future step. Scoped narrowly to the specific
   stale status/next-step language Pete named -- NOT touching either
   doc's "Next steps" numbered lists beyond what's directly quoted
   here, since those weren't explicitly in scope for this pass.

2. STATE_MULTIPLIERS addition for the_inner_circle (engine/
   friction_tax.py): the one genuinely new, real gap this investigation
   surfaced -- the_inner_circle (58th state, added this session,
   commit 8f36282) was never scored under the original Calibration Set
   3 pass, so tools/test_friction_tax.py's coverage-completeness check
   currently fails with "missing: {'the_inner_circle'}". Added per
   Pete's direct 4-criterion scoring call. raw_score = 1+0+2 = 3
   (legal excluded from the sum, per the module's own established
   convention -- see _ATTRITIONAL_CRITERIA_KEYS). multiplier verified
   against the live _attritional_fraction(3) == 0.15000000000000002,
   not hand-computed -- matches the exact float artifact already
   stored for other raw_score=3 states (e.g. invisible_performance_
   management, wellbeing_theater), confirming this is the real
   unrounded formula output, not a rounding mismatch. Inserted at the
   end of the dict (after what_nobody_says, the last existing entry)
   rather than alphabetically -- confirmed via direct inspection that
   the dict's existing 57 entries are grouped by original scoring
   batch, not alphabetical, so appending at the end matches how Q40-
   Q51 were appended to _QDATA earlier this session, and is the least
   disruptive insertion point.

Usage:
  python tools/patch_friction_tax_doc_staleness_and_inner_circle.py --dry-run
  python tools/patch_friction_tax_doc_staleness_and_inner_circle.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ============================================================================
# 1a. prompts/friction-tax-multistate-compounding-methodology.md
# ============================================================================

edit(
    "prompts/friction-tax-multistate-compounding-methodology.md",
    "# Friction Tax — Multi-State Compounding Methodology (Proposed, Not Yet Implemented)\n"
    "\n"
    "**Status:** Design proposed and confirmed with Pete this session. NOT yet reviewed by Gemini, NOT yet implemented. Do not build against this until both have happened.\n",
    "# Friction Tax — Multi-State Compounding Methodology (Implemented)\n"
    "\n"
    "**Status:** Implemented and verified. Gemini-reviewed and cleared, then implemented in compute_friction_tax() -- commit 8de807a (2026-08-03), MOB v4.80. tools/test_friction_tax.py rewritten 37->45 checks, 45/45 passing at the time of that commit. (Documentation correction made in a later session -- this status line previously read as pending/not-yet-reviewed, describing a step that had already happened and passed.)\n",
)

# ============================================================================
# 1b. prompts/friction-tax-state-multiplier-methodology.md
# ============================================================================

edit(
    "prompts/friction-tax-state-multiplier-methodology.md",
    "**Status:** Scoring complete, all 57 states populated (Calibration Set 3, commit 469b148). Combination function rescaled this session (Option A, below) -- Gemini-reviewed and cleared (structural check + worked dollar-figure plausibility check across mild/typical/severe scenarios, all landing in a defensible 3%-49% of payroll range). Not yet implemented in compute_friction_tax().\n",
    "**Status:** Scoring complete, all 57 states populated (Calibration Set 3, commit 469b148). Combination function rescaled (Option A, below) -- Gemini-reviewed and cleared (structural check + worked dollar-figure plausibility check across mild/typical/severe scenarios, all landing in a defensible 3%-49% of payroll range), then implemented in compute_friction_tax() -- commit 8de807a (2026-08-03), MOB v4.80. (Documentation correction made in a later session -- this status line previously read \"Not yet implemented,\" describing a step that had already happened and passed.)\n",
)

# ============================================================================
# 2. tools/_mob.txt Section 13a -- two Decision Register rows
# ============================================================================

# Row: "Multi-state compounding mechanism for Friction Tax"
edit(
    "tools/_mob.txt",
    "| Multi-state compounding mechanism for Friction Tax | 3 | Open -- flagged, not scoped, not designed |",
    "| Multi-state compounding mechanism for Friction Tax | 3 | Closed -- implemented, commit 8de807a (2026-08-03), MOB v4.80 |",
)
edit(
    "tools/_mob.txt",
    "This was the last open parameter blocking implementation -- see Priority Queue item 1, and see the new Friction Tax output-ceiling plausibility row above for a separate finding that should be reviewed before implementing this redesign, since both touch compute_friction_tax()'s math | This session (Claude Code) -- evidence added, K closed | Pete's call -- reopen when ready to design the compounding mechanism (state-count averaging, within-criterion stacking, breadth-across-criteria stacking, plus the_untouchable cross-state evidence) |",
    "This was the last open parameter blocking implementation. **CORRECTED, later session:** both this design and the Friction Tax output-ceiling plausibility rescale (row above) were Gemini-reviewed, cleared, and fully implemented in compute_friction_tax() five days before this correction was made -- commit 8de807a (2026-08-03), MOB v4.80, tools/test_friction_tax.py rewritten 37->45 checks (45/45 passing at the time). The prior \"reviewed before implementing... blocking implementation\" framing was stale, describing an already-completed step as still pending. | This session (Claude Code) -- doc correction only, no new design work | Closed -- no further check-in |",
)

# Row: "Friction Tax output-ceiling plausibility"
edit(
    "tools/_mob.txt",
    "Next: Gemini architecture re-review of the rescale, scoped to the three attritional criteria only, before CC implements. See Priority Queue item 1 | This session (Claude Code) | Gemini re-review of the rescale (attritional-only scope) -- once returned, CC implements; no further Pete-level decision expected on Option A itself unless Gemini's review surfaces a problem |",
    "**CORRECTED, later session:** the Gemini re-review described as \"Next\" below already happened and passed five days before this correction was made -- commit 8de807a (2026-08-03), MOB v4.80, fully implemented in compute_friction_tax(), tools/test_friction_tax.py rewritten 37->45 checks (45/45 passing at the time). See Priority Queue item 1 | This session (Claude Code) -- doc correction only, no new design work | Closed -- no further check-in |",
)

# ============================================================================
# 3. engine/friction_tax.py -- STATE_MULTIPLIERS addition, the_inner_circle
# ============================================================================

edit(
    "engine/friction_tax.py",
    '    "what_nobody_says": StateMultiplierEntry(\n'
    '        multiplier=0.18333333333333335,\n'
    '        raw_score=4,\n'
    '        criteria={\n'
    '            "turnover": StateCriterionScore(\n'
    '                score=2,\n'
    '                rationale="People who\'ve learned what happens to whoever speaks up may eventually leave rather than continue carrying a problem they can\'t voice — a direct retention cost.",\n'
    '            ),\n'
    '            "productivity": StateCriterionScore(\n'
    '                score=1,\n'
    '                rationale="Energy spent managing around an unspoken known problem is a moderate, ongoing drag on output.",\n'
    '            ),\n'
    '            "decision_quality": StateCriterionScore(\n'
    '                score=1,\n'
    '                rationale="Decisions get made without the accurate information that exists but isn\'t being raised — a moderate quality gap.",\n'
    '            ),\n'
    '            "legal": StateCriterionScore(\n'
    '                score=0,\n'
    '                rationale="No identifiable compliance category from organizational silence alone, absent a specific underlying violation.",\n'
    '            ),\n'
    '        },\n'
    '    ),\n'
    '}\n',
    '    "what_nobody_says": StateMultiplierEntry(\n'
    '        multiplier=0.18333333333333335,\n'
    '        raw_score=4,\n'
    '        criteria={\n'
    '            "turnover": StateCriterionScore(\n'
    '                score=2,\n'
    '                rationale="People who\'ve learned what happens to whoever speaks up may eventually leave rather than continue carrying a problem they can\'t voice — a direct retention cost.",\n'
    '            ),\n'
    '            "productivity": StateCriterionScore(\n'
    '                score=1,\n'
    '                rationale="Energy spent managing around an unspoken known problem is a moderate, ongoing drag on output.",\n'
    '            ),\n'
    '            "decision_quality": StateCriterionScore(\n'
    '                score=1,\n'
    '                rationale="Decisions get made without the accurate information that exists but isn\'t being raised — a moderate quality gap.",\n'
    '            ),\n'
    '            "legal": StateCriterionScore(\n'
    '                score=0,\n'
    '                rationale="No identifiable compliance category from organizational silence alone, absent a specific underlying violation.",\n'
    '            ),\n'
    '        },\n'
    '    ),\n'
    '    "the_inner_circle": StateMultiplierEntry(\n'
    '        multiplier=0.15000000000000002,\n'
    '        raw_score=3,\n'
    '        criteria={\n'
    '            "turnover": StateCriterionScore(\n'
    '                score=1,\n'
    '                rationale="Those excluded from the protected in-group face reduced advancement and visibility, driving moderate voluntary attrition; the in-group itself is insulated, limiting the signal\'s reach.",\n'
    '            ),\n'
    '            "productivity": StateCriterionScore(\n'
    '                score=0,\n'
    '                rationale="Decisions within the circle can be efficient on their own terms even when damaging elsewhere; no direct organizational output drag scored.",\n'
    '            ),\n'
    '            "decision_quality": StateCriterionScore(\n'
    '                score=2,\n'
    '                rationale="Core to the state — decisions are consequence-shielded and groupthink-protected by design, the clearest and strongest signal of the three criteria.",\n'
    '            ),\n'
    '            "legal": StateCriterionScore(\n'
    '                score=1,\n'
    '                rationale="Exclusionary in-group dynamics create moderate disparate-treatment and retaliation exposure for those shut out, though the state\'s core mechanism is protective self-dealing rather than a direct regulatory or compliance violation.",\n'
    '            ),\n'
    '        },\n'
    '    ),\n'
    '}\n',
)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    by_file: dict[str, list[tuple[str, str]]] = {}
    for path, old, new in EDITS:
        by_file.setdefault(path, []).append((old, new))

    for rel_path, pairs in by_file.items():
        full_path = REPO_ROOT / rel_path
        content = full_path.read_text(encoding="utf-8")
        for old, new in pairs:
            count = content.count(old)
            if count != 1:
                print(f"ABORT: {rel_path}: expected exactly 1 match for anchor, found {count}")
                print(f"  anchor (first 150 chars): {old[:150]!r}")
                sys.exit(1)
            content = content.replace(old, new, 1)

        if args.dry_run:
            print(f"=== {rel_path}: {len(pairs)} edit(s) would apply cleanly ===")
        else:
            full_path.write_text(content, encoding="utf-8")
            print(f"=== {rel_path}: {len(pairs)} edit(s) written ===")

    if args.dry_run:
        print("\nDry run complete. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
