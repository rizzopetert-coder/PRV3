"""
PRV3 -- Documentation-staleness fix (Part 1) + repo-wide prompts/*.md
sweep (Part 2), prompts/friction-tax-state-multiplier-methodology.md.
Third confirmed instance of the status-line-fixed-but-body-not-swept
pattern (first: MC_CENTROID_39 session's Friction Tax correction;
second: the multi-state compounding doc, commit 9c4d2bc).

Independently re-verified before this edit, not taken on faith:
  - engine/friction_tax.py's STATE_MULTIPLIERS dict confirmed 58/58
    populated (57 original states + the_inner_circle), zero
    placeholder/None entries.
  - _attritional_fraction() confirmed implementing the exact frozen
    [0, 6] -> [0.05, 0.25] mapping this doc's "Combination function"
    section describes, and its own docstring cites this document by
    name.
  - Both cited commits (469b148 scoring, 8de807a rescaled
    implementation) confirmed accurate via git blame -- no correction
    needed to the doc's header.

Part 2 (repo-wide sweep, prompts/*.md): every file checked for the
same specific mismatch shape (header claims done/implemented, a later
section still describes that work as pending). Zero further hits.
friction-tax-legal-compliance-methodology.md re-confirmed clean per
Pete's standing instruction not to re-flag without new evidence. Five
adjacent-but-different-shape findings logged for awareness only, not
fixed (reverse pattern -- doc says "not yet done" but is now actually
done, no header contradiction to fix): friction-tax-architecture-
decision.md, friction-tax-band-segmentation.md, friction-tax-unit-
decision.md, intake-headcount-precision-redesign.md, and diagnostic-
dimension-expansion.md's unsequenced build order. Plus one differently-
shaped contradiction (superseded-header-but-still-actionable-next-
steps, not done-vs-pending): diagnostic-reskin-stages-4-5-rescope.md.

Usage:
  python tools/patch_friction_tax_state_multiplier_doc_and_sweep.py --dry-run
  python tools/patch_friction_tax_state_multiplier_doc_and_sweep.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-state-multiplier-methodology.md"
MOB = "tools/_mob.txt"
CLAUDE = "CLAUDE.md"

# ---------------------------------------------------------------------
# 1. Replace the stale "Next steps" section.
# ---------------------------------------------------------------------

edit(
    DOC,
    "## Next steps (in order)\n"
    "\n"
    "1. Recompute each of the 57 states' raw_total using only the 3 remaining criteria (turnover, productivity, decision_quality), dropping the original Legal/Compliance sub-score from the closed Set 3 scoring worksheet.\n"
    "2. Apply the rescaled interpolation formula above to derive final multiplier values against the new [0.05, 0.25] / [0, 6] mapping.\n"
    "3. CC implements: STATE_MULTIPLIERS values updated, compute_friction_tax() updated to treat the result as a payroll fraction rather than a bare multiplier (touches contract.py / web/lib/types.ts per the Legal/Compliance doc's structural-implications note), tests updated, run under dry-run-before-write protocol.\n"
    "4. Coordinate with the multi-state compounding implementation (prompts/friction-tax-multistate-compounding-methodology.md) — both touch compute_friction_tax() and must land consistently, including the single-state continuity check against [0, 6] / [0.05, 0.25], not the original [0, 8] / [1.0, 1.4].\n",
    "## Implementation status\n"
    "\n"
    "All four steps completed. Independently re-verified this session (2026-08-08), not restated "
    "from the header alone: engine/friction_tax.py's STATE_MULTIPLIERS dict carries 58 populated "
    "entries (the original 57 states plus the_inner_circle, added in a later session -- see note "
    "below), zero placeholder/None values, recomputed against the 3 remaining criteria (turnover, "
    "productivity, decision_quality) per item 1. _attritional_fraction() implements the exact "
    "rescaled interpolation formula from item 2 (`_FRACTION_MIN + (_FRACTION_MAX - _FRACTION_MIN) * "
    "((raw_total - _R_MIN) / (_R_MAX - _R_MIN))`, with _R_MIN=0.0, _R_MAX=6.0, _FRACTION_MIN=0.05, "
    "_FRACTION_MAX=0.25), and its own docstring cites this document by name as the source of the "
    "frozen-range design. compute_friction_tax() treats the result as a payroll fraction throughout, "
    "per item 3. Coordination with the multi-state compounding doc (item 4) confirmed landed together "
    "in the same commit -- single-state continuity holds against the [0, 6] / [0.05, 0.25] mapping "
    "(tools/test_friction_tax.py checks 7-8, 93/93 passing). Commits confirmed accurate via git blame: "
    "469b148 (2026-08-02, original scoring) and 8de807a (2026-08-03, rescaled implementation) -- "
    "matching this document's own header exactly, no correction needed there.\n"
    "\n"
    "No genuinely forward-looking items remain in this section.\n"
    "\n"
    "Note, flagged not fixed (out of this pass's scope -- this fix is scoped to the Next steps "
    "section only): this document's own \"Status\" line above and the \"Known adjacent issue\" "
    "section still say \"all 57 states populated.\" That is stale on a different axis -- "
    "STATE_MULTIPLIERS is 58/58 as of a later session, the_inner_circle included -- worth a "
    "follow-up pass.\n",
)

# ---------------------------------------------------------------------
# 2. Amend the existing status-line-staleness Decision Register row
#    into a running list (Pete's explicit preference over opening a
#    fresh row), folding in the third instance and the Part 2 sweep
#    result.
# ---------------------------------------------------------------------

OLD_ROW = (
    "| Status-line-fixed-but-body-not-swept staleness pattern -- second instance flagged | 3 | "
    "Informational, no forced check-in | Second confirmed instance of the same pattern: a doc's own "
    "status/header line gets corrected to reflect completed work, but a later section (here, "
    "prompts/friction-tax-multistate-compounding-methodology.md's \"Next steps\") still describes "
    "that same work as pending, because the header fix didn't trigger a full-document consistency "
    "pass. First instance: the MC_CENTROID_39 session's Friction Tax redesign-staleness correction "
    "(commits 5139a16, f06d537), where prompts/*.md docs and two Decision Register rows still "
    "described the multi-state compounding redesign as pending review 5 days after it actually "
    "shipped (commit 8de807a). This instance independently re-verified before fixing, not taken on "
    "faith: engine/friction_tax.py's compute_friction_tax() confirmed carrying all three design steps "
    "live, tools/test_friction_tax.py's single-state continuity and N=1 guard checks confirmed real "
    "(not just comment-referenced), commit 8de807a confirmed accurate via git blame. Fixed, commit "
    "9c4d2bc. No code change either time -- both instances were documentation-only. Worth a "
    "full-document consistency pass (not just the header) whenever a status line gets corrected in "
    "any prompts/*.md file going forward, in case this recurs elsewhere. | This session (Claude Code) "
    "| No forced check-in -- informational, revisit only if a third instance surfaces |\n"
)

NEW_ROW = (
    "| Status-line-fixed-but-body-not-swept staleness pattern -- three confirmed instances, "
    "repo sweep complete | 3 | Informational, no forced check-in | Third confirmed instance of the "
    "same pattern, this one caught via a deliberate repo-wide sweep rather than incidentally: a "
    "doc's own status/header line gets corrected to reflect completed work, but a later section "
    "still describes that same work as pending, because the header fix didn't trigger a "
    "full-document consistency pass. Instance 1: the MC_CENTROID_39 session's Friction Tax "
    "redesign-staleness correction (commits 5139a16, f06d537), where prompts/*.md docs and two "
    "Decision Register rows still described the multi-state compounding redesign as pending review "
    "5 days after it actually shipped (commit 8de807a). Instance 2: "
    "prompts/friction-tax-multistate-compounding-methodology.md's \"Next steps\" section, fixed "
    "commit 9c4d2bc. Instance 3 (this row): prompts/friction-tax-state-multiplier-methodology.md's "
    "\"Next steps\" section listed all 4 steps as pending work despite the header already saying "
    "\"Scoring complete... implemented\" -- independently re-verified before fixing, not taken on "
    "faith: engine/friction_tax.py's STATE_MULTIPLIERS dict confirmed 58/58 populated with zero "
    "placeholder entries, _attritional_fraction() confirmed implementing the exact frozen [0, 6] -> "
    "[0.05, 0.25] mapping and citing this document by name in its own docstring, commits 469b148 "
    "(scoring) and 8de807a (rescaled implementation) both confirmed accurate via git blame. Fixed, "
    "commit PENDING_HASH. **Repo-wide sweep (this session):** every file in prompts/*.md checked for "
    "the same specific mismatch shape (header claims done/implemented, later section describes the "
    "same work as pending) -- zero further hits beyond the three instances above; "
    "prompts/friction-tax-legal-compliance-methodology.md re-confirmed clean (its header honestly "
    "says in-progress, its pending items are real and current, not stale). Five adjacent-but-"
    "different-shape findings surfaced during the sweep, flagged for awareness only, not fixed (out "
    "of this sweep's scope, doesn't match the specific pattern being hunted): "
    "prompts/friction-tax-architecture-decision.md, prompts/friction-tax-band-segmentation.md, and "
    "prompts/friction-tax-unit-decision.md all have a self-consistent \"Status\"/\"Not yet done\" "
    "section (no header contradiction -- none of these docs ever claimed completion) that is now "
    "factually stale, since PAYROLL_BASELINE_GRID, ORG_TYPE_SCALARS, and STATE_MULTIPLIERS are all "
    "fully populated today; prompts/intake-headcount-precision-redesign.md's header literally says "
    "\"NOT implemented\" even though the redesign shipped across 3 phases in a later session -- same "
    "reverse shape, header included this time but still self-consistent with its own body, not a "
    "done-vs-pending contradiction. prompts/diagnostic-dimension-expansion.md's unsequenced \"Build "
    "order\" section is similarly stale (the whole initiative is closed) but the doc's own title "
    "never claimed completion either. prompts/diagnostic-reskin-stages-4-5-rescope.md's \"Next "
    "steps\" section still lists Stage 4/5 as actionable directly beneath a header that explicitly "
    "says the plan is superseded and \"do not pick Stage 4 back up\" -- a different contradiction "
    "shape (superseded-vs-still-actionable, not done-vs-pending), also not fixed here. No code "
    "changes anywhere in this row's history -- all three fixed instances and all five adjacent "
    "findings are documentation-only. | This session (Claude Code) | No forced check-in -- "
    "informational, revisit only if a fourth instance of the specific pattern surfaces; the five "
    "adjacent findings are Pete's call whether to schedule a cleanup pass |\n"
)

edit(MOB, OLD_ROW, NEW_ROW)

# ---------------------------------------------------------------------
# 3. Version bump.
# ---------------------------------------------------------------------

edit(MOB, "\\\\\\#\\\\\\# MOB v4.131", "\\\\\\#\\\\\\# MOB v4.132")
edit(CLAUDE, "| MOB version | v4.131 |", "| MOB version | v4.132 |")


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
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
