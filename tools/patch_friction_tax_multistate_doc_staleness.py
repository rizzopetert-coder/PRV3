"""
PRV3 -- Documentation-staleness fix, prompts/friction-tax-multistate-
compounding-methodology.md (Tier 2, no functional code change).

Independently re-verified before this edit, not taken on faith from the
Claude.ai investigation that proposed it:
  - engine/friction_tax.py's compute_friction_tax() carries all three
    design steps live (Step 1 geometric decay w_i = 0.5**i via
    enumerate(), Step 2 combined_multiplier reusing the frozen
    _attritional_fraction() mapping, Step 3 the K=0.05 constant plus a
    real `if len(state_entries) == 1` guard, not an incidental
    breadth-formula coincidence).
  - tools/test_friction_tax.py checks 7 and 8 are real assertions
    (single-state continuity across 10 real states; N=1 guard against
    the_founders_grip, chosen specifically because it's the case most
    likely to accidentally trigger loading if the guard were missing).
    93/93 passing.
  - git blame confirms all of Step 1-3 plus the K constant landed in a
    single commit, 8de807a (2026-08-03) -- matches the doc's own header
    citation exactly, no correction needed there.

The doc's "Next steps" section still described Steps 1-3 as pending
(Gemini review "not yet sent", CC implementation phrased as future
work) despite the header already saying "Implemented and verified."
Replaced with a closure note. Legal/Compliance (former item 4) kept as
a forward pointer, not folded into the closure -- it remains genuinely
separate and unimplemented.

Also adds a new Section 13a Decision Register row (tools/_mob.txt,
Tier 3, informational, no forced check-in) flagging that this is a
second instance of the same status-line-fixed-but-body-not-swept
pattern already on record from the MC_CENTROID_39 session's Friction
Tax correction -- worth a full-document consistency pass whenever a
status line gets corrected, in case it recurs in other prompts/*.md
files. MOB version bumped v4.130 -> v4.131 per standing protocol.

Usage:
  python tools/patch_friction_tax_multistate_doc_staleness.py --dry-run
  python tools/patch_friction_tax_multistate_doc_staleness.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-multistate-compounding-methodology.md"
MOB = "tools/_mob.txt"

# ---------------------------------------------------------------------
# 1. Replace the stale "Next steps" section in the methodology doc.
# ---------------------------------------------------------------------

edit(
    DOC,
    "## Next steps (in order)\n"
    "\n"
    "1. Gemini architecture review of this design (schema/formula implementation questions) — not yet sent.\n"
    "2. multi_channel_severity_loading (K) = 0.05 CLOSED — Pete's final decision, not to be reopened absent new information. Breadth range corrected to 1-3 this session (was 1-4, before Legal/Compliance was split out) — see Step 3; documentation correction only, K itself not reopened.\n"
    "3. CC implementation: replace compute_friction_tax()'s mean_multiplier step with combined_criterion_score aggregation per Step 1 (3 criteria: turnover, productivity, decision_quality), add multi_channel_severity_loading per Step 3 (breadth 1-3), verify single-state continuity explicitly against the rescaled [0, 6] / [0.05, 0.25] mapping (prompts/friction-tax-state-multiplier-methodology.md), update tests.\n"
    "4. Legal/Compliance tail-risk methodology is its own separate, actively in-progress design (prompts/friction-tax-legal-compliance-methodology.md) — no longer gated on this design's implementation.\n",
    "## Implementation status\n"
    "\n"
    "All three steps implemented and verified as designed, commit 8de807a (2026-08-03), MOB v4.80. "
    "Independently re-verified this session (2026-08-08), not restated from the header alone: "
    "engine/friction_tax.py's compute_friction_tax() carries Step 1 (geometric decay aggregation -- "
    "`(0.5 ** i) * score` summed per criterion across identified states, sorted descending), Step 2 "
    "(combined_multiplier via _attritional_fraction(), reusing the frozen [0, 6] -> [0.05, 0.25] mapping "
    "from friction-tax-state-multiplier-methodology.md rather than a separately-derived range), and Step 3 "
    "(module-level _MULTI_CHANNEL_SEVERITY_LOADING_K = 0.05, with an explicit `if len(state_entries) == 1` "
    "guard forcing multi_channel_severity_loading to exactly 1.0 -- confirmed a real conditional in code, "
    "not incidental to the breadth formula happening to also equal 1.0). multi_channel_severity_loading (K) "
    "= 0.05 remains CLOSED, Pete's final decision, not reopened here. Single-state continuity and the N=1 "
    "guard are both exercised by real assertions in tools/test_friction_tax.py (checks 7 and 8, not just "
    "referenced in a comment) -- both passing, full suite 93/93. Confirmed via git blame that all of Step "
    "1-3 plus the K constant landed in a single commit, 8de807a, matching this document's own header "
    "exactly -- no correction needed there.\n"
    "\n"
    "Legal/Compliance tail-risk methodology (former item 4) remains its own separate, actively "
    "in-progress design -- see prompts/friction-tax-legal-compliance-methodology.md. Not gated on this "
    "design's implementation, not folded into the closure above.\n"
    "\n"
    "**Staleness pattern, flagged:** this closes a second instance of the same status-line-fixed-but-"
    "body-not-swept pattern already on record from the MC_CENTROID_39 session's Friction Tax correction "
    "(this document's own header was corrected in a prior session while this section stayed stale) -- "
    "logged to the Decision Register (Section 13a, tools/_mob.txt) as a general pattern worth a "
    "full-document consistency pass whenever a status line gets corrected, not just in this file.\n",
)

# ---------------------------------------------------------------------
# 2. New Decision Register row, Section 13a -- informational, no forced
#    check-in, appended after the cluster_id gap row (the current last
#    row in the table).
# ---------------------------------------------------------------------

NEW_ROW = (
    "| Status-line-fixed-but-body-not-swept staleness pattern -- second instance flagged | 3 | "
    "Informational, no forced check-in | Second confirmed instance of the same pattern: a doc's own "
    "status/header line gets corrected to reflect completed work, but a later section (here, "
    "prompts/friction-tax-multistate-compounding-methodology.md's \"Next steps\") still describes that "
    "same work as pending, because the header fix didn't trigger a full-document consistency pass. First "
    "instance: the MC_CENTROID_39 session's Friction Tax redesign-staleness correction (commits 5139a16, "
    "f06d537), where prompts/*.md docs and two Decision Register rows still described the multi-state "
    "compounding redesign as pending review 5 days after it actually shipped (commit 8de807a). This "
    "instance independently re-verified before fixing, not taken on faith: engine/friction_tax.py's "
    "compute_friction_tax() confirmed carrying all three design steps live, tools/test_friction_tax.py's "
    "single-state continuity and N=1 guard checks confirmed real (not just comment-referenced), commit "
    "8de807a confirmed accurate via git blame. Fixed, commit TBD. No code change either time -- both "
    "instances were documentation-only. Worth a full-document consistency pass (not just the header) "
    "whenever a status line gets corrected in any prompts/*.md file going forward, in case this recurs "
    "elsewhere. | This session (Claude Code) | No forced check-in -- informational, revisit only if a "
    "third instance surfaces |\n"
)

edit(
    MOB,
    "| cluster_id gap -- explained and logged, not fixed | 3 | Informational, no forced check-in |",
    NEW_ROW.rstrip("\n") + "\n"
    "| cluster_id gap -- explained and logged, not fixed | 3 | Informational, no forced check-in |",
)

# ---------------------------------------------------------------------
# 3. Version bump.
# ---------------------------------------------------------------------

edit(MOB, "\\\\\\#\\\\\\# MOB v4.130", "\\\\\\#\\\\\\# MOB v4.131")
edit(CLAUDE := "CLAUDE.md", "| MOB version | v4.130 |", "| MOB version | v4.131 |")


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
