"""
PRV3 -- Combined write: fixes a real row-boundary corruption in
tools/_mob.txt Section 16 (introduced by this session's own earlier
v4.71 patch script, patch_mob_v71_session_log.py) and adds the new v4.72
session log entry (Friction Tax restructure + private-path wiring),
version header bump, and CLAUDE.md cross-reference update.

BUG FOUND AND FIXED, not just worked around: the v4.71 patch script's
Section 16 anchor was "MOB v4.70. |\\n| **May 2026 -- Session 1**...",
which spans the boundary between the end of the v4.70 row and the start
of the Session 1 row. Its replacement (NEW_ROW + ANCHOR) inserted the new
v4.71 row's text *before* "MOB v4.70. |" instead of after a real row
break -- splicing the v4.71 row's content into the middle of the v4.70
row's own cell (right before its closing "MOB v4.70. |" marker) and
leaving that marker orphaned on its own line afterward. Net effect: the
v4.70 and v4.71 rows were merged into one malformed table row, followed
by a stray "MOB v4.70. |" line with no cell content before the Session 1
row. Confirmed via direct index search -- exactly one occurrence of each
anchor substring used below, so this is a targeted, verified fix, not a
guess.

This script:
  1. Splits the merged row back into two clean, independent rows -- the
     v4.70 row now correctly ends "... MOB v4.70. |", and the v4.71 row
     begins as a genuinely new row immediately after.
  2. Removes the orphaned "MOB v4.70. |" line and, in the same edit,
     inserts the new v4.72 row in the correct place (immediately after
     the now-properly-terminated v4.71 row, before the Session 1 row) --
     matching the append point convention used by the last several
     entries.
  3. Bumps the tools/_mob.txt version header v4.71 -> v4.72.
  4. Updates CLAUDE.md's MOB version cross-reference v4.71 -> v4.72.

Usage:
  python tools/patch_mob_v72_session_log.py --dry-run
  python tools/patch_mob_v72_session_log.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

# ── Fix 1: split the merged v4.70/v4.71 row back into two clean rows ────────

ROW_SPLIT_ANCHOR = (
    "all warrant a bump per the closeout protocol. | **August 2026"
)
ROW_SPLIT_REPLACEMENT = (
    "all warrant a bump per the closeout protocol. MOB v4.70. |\n"
    "| **August 2026"
)

# ── Fix 2 + new entry: remove the orphaned line, insert the v4.72 row ──────

ORPHAN_ANCHOR = (
    "MOB v4.71. |\n"
    "MOB v4.70. |\n"
    "| **May 2026"
)

NEW_ROW = (
    "| **August 2026 — Friction Tax: code restructure and private-path "
    "wiring** | **Architecture:** prompts/friction-tax-architecture-"
    "decision.md's 54-cell composite grid "
    "(Dict[Tuple[str, str], PayrollBaselineEntry], keyed by 6 headcount "
    "buckets x 9 industries from IntakeData) was Gemini-proposed, "
    "CC-verified against real code, and Pete-approved 2026-07-29 -- "
    "already past its structural gate before this session's build work "
    "started. This session executed the build: replaced the old 5-key "
    "headcount-only _ORG_SIZE_BANDS (whose keys didn't even match "
    "IntakeData.headcount's real string values) with the full 54-cell "
    "grid, added ORG_TYPE_SCALARS (6-entry multiplicative scalar table), "
    "updated compute_friction_tax()'s signature and internal sequence "
    "per the architecture doc's 5 steps. STATE_MULTIPLIERS and the "
    "locked severity/range math untouched. Closed a previously-flagged "
    "test gap in the same pass -- multi-state averaging logic had zero "
    "coverage across all 4 existing tests; added real multi-state "
    "coverage. 23/23, validated in isolation before touching real files. "
    "Committed 413a51c. **Pipeline wiring investigation surfaced a real "
    "gap the task's own framing missed:** compute_friction_tax() was "
    "confirmed not called anywhere in the live pipeline, but the deeper "
    "finding was that PrivateOutputBlock.friction_tax_estimate was typed "
    "as a bare Optional[float] and never assigned by "
    "build_private_block() -- structurally None regardless of "
    "calibration status, not just because values aren't populated yet. "
    "Direct-read investigation (before any wiring code was written, per "
    "this session's established discipline) confirmed friction_tax_"
    "estimate already exists at all three contract layers "
    "(web/lib/types.ts, engine/output.py, engine/contract.py) but the "
    "three shapes didn't agree with each other or with "
    "compute_friction_tax()'s real 6-key return -- required a "
    "reconciliation decision, not just a function call. **Decisions "
    "locked:** null-as-calibration-signal (no calibration_complete field "
    "added to any wire type; PrivateOutput.tsx's existing reserved Block "
    "6 render slot already treats null as \"render nothing,\" confirmed "
    "still correct, zero new UI branch needed) -- adopted over adding "
    "explicit calibration state to the wire type. Shareable path "
    "deliberately excluded from this wiring (Pete's Option 3 call): "
    "share/create/route.ts and the engine's shareable_output "
    "construction both untouched, since whether a financial exposure "
    "estimate belongs in the report meant to leave the confidential "
    "engagement is a product/positioning decision, not a plumbing "
    "default, and it's inert either way until real values exist. "
    "**Wiring executed:** engine/output.py's "
    "PrivateOutputBlock.friction_tax_estimate type-fixed to match the "
    "3-field wire shape (low/high/currency) but deliberately left "
    "unassigned -- the real computation happens in contract.py's "
    "assemble_output(), which has the intake context "
    "(headcount/industry/org_type) that build_private_block() "
    "structurally lacks; computing it in both places would mean "
    "redundant computation with worse context in one of them. Real call "
    "wired at contract.py's existing insertion point, deriving state_ids "
    "from identified_states, severity_tier from sev.tier, "
    "org_size/industry/org_type from the already-assembled intake "
    "object. Both Path 1 (answer/route.ts) and Path B (result/route.ts) "
    "hardcoded nulls removed. web/lib/engine-client.ts's inline "
    "EngineResult mirror type caught and fixed in the same pass -- the "
    "recurring inline-mirror-type gap (cascade_risk, headline, "
    "descriptive_prose, now this) would have produced a real tsc error "
    "at both route call sites otherwise. **Net effect:** zero behavioral "
    "change to any real output today -- compute_friction_tax() returns "
    "calibration_complete: False for every session until the benchmark "
    "research populates real values, so friction_tax_estimate renders "
    "null exactly as it did before, just through real plumbing instead "
    "of a hardcode. tsc clean, 169/172 calibration unchanged, zero "
    "regressions across the full suite for both the restructure "
    "(413a51c) and the wiring (86b2ba4). **Vestigial field flagged, not "
    "removed:** PrivateOutputBlock.friction_tax_estimate is now "
    "correctly-typed but permanently unassigned and unread -- logged as "
    "a Tier 3 informational Decision Register cleanup item rather than "
    "removed in this task, per Pete's call to keep this task's footprint "
    "matched to what was scoped. **Status:** Friction Tax architecture "
    "and pipeline wiring CLOSED. Remaining: the benchmark research pass "
    "(54 payroll_floor_annual cells, 6 ORG_TYPE_SCALARS, 57 "
    "STATE_MULTIPLIERS) from real sources per prompts/friction-tax-unit-"
    "decision.md, independently verified before any value is written, "
    "per standing Gemini-verification discipline. Not started. CLAUDE.md "
    "MOB version cross-reference updated v4.71->v4.72. MOB version "
    "bumped to v4.72 -- closes the Friction Tax architecture and "
    "pipeline-wiring thread carried since v4.69, warrants a bump per the "
    "closeout protocol. MOB v4.72. |\n"
    "| **May 2026"
)

# ── CLAUDE.md: version cross-reference ──────────────────────────────────────

CLAUDE_ANCHOR = "| MOB version | v4.71 |"
CLAUDE_REPLACEMENT = "| MOB version | v4.72 |"

# ── tools/_mob.txt: version header ──────────────────────────────────────────

MOB_HEADER_ANCHOR = "\\\\\\#\\\\\\# MOB v4.71"
MOB_HEADER_REPLACEMENT = "\\\\\\#\\\\\\# MOB v4.72"


def _apply(text: str, anchor: str, replacement: str, label: str) -> str:
    count = text.count(anchor)
    if count == 0:
        print(f"ABORT -- anchor not found: {label}", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches): {label}", file=sys.stderr)
        sys.exit(1)
    return text.replace(anchor, replacement)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    claude_text = CLAUDE_MD.read_text(encoding="utf-8")
    mob_text = MOB_FILE.read_text(encoding="utf-8")

    mob_text = _apply(mob_text, ROW_SPLIT_ANCHOR, ROW_SPLIT_REPLACEMENT, "row-boundary corruption fix (v4.70/v4.71 split)")
    mob_text = _apply(mob_text, ORPHAN_ANCHOR, "MOB v4.71. |\n" + NEW_ROW, "orphaned line removal + new v4.72 row insertion")
    mob_text = _apply(mob_text, MOB_HEADER_ANCHOR, MOB_HEADER_REPLACEMENT, "tools/_mob.txt version header")
    claude_text = _apply(claude_text, CLAUDE_ANCHOR, CLAUDE_REPLACEMENT, "CLAUDE.md MOB version cross-reference")

    print("All 4 anchors found and unique. Changes:")
    print("=" * 72)
    print("1. tools/_mob.txt -- FIX: split the v4.70/v4.71 rows that were")
    print("   merged into one malformed row by this session's earlier")
    print("   v4.71 patch script (real corruption, not cosmetic)")
    print("2. tools/_mob.txt -- FIX: remove the orphaned 'MOB v4.70. |'")
    print("   line, insert the new v4.72 row in its place")
    print("3. tools/_mob.txt -- header MOB v4.71 -> v4.72")
    print("4. CLAUDE.md -- MOB version v4.71 -> v4.72")
    print("=" * 72)

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    MOB_FILE.write_text(mob_text, encoding="utf-8")
    CLAUDE_MD.write_text(claude_text, encoding="utf-8")
    print("\nWROTE tools/_mob.txt")
    print("WROTE CLAUDE.md")


if __name__ == "__main__":
    main()
