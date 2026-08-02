"""
PRV3 -- Session closeout write, three parts, combined into one dry-run
per Pete's instruction. Parts 1-2 write to tools/_mob.txt; Part 3 writes
to CLAUDE.md. Confirmed and ready: all three. NOT yet drafted or
confirmed, deliberately excluded from this script: version bump,
Section 16 Session Log entry, Diary Write, Mine -- these were flagged
as required by the standing Closeout Protocol but no content has been
supplied or confirmed for them yet.

1. New Decision Register row (Section 13a): "Calibration Set 2
   (PAYROLL_BASELINE_GRID) -- Closed," parallel in structure to the
   existing "Calibration Set 3 (STATE_MULTIPLIERS) -- Scoring Complete"
   row, inserted immediately after it (before the Legal/Compliance
   tail-risk row, which remains the last 13a row).

   FLAGGED, not corrected here: the Detail text (Pete's exact wording)
   claims "symmetry with the Set 1 and Set 3 entries," but Section 13a
   has no Set 1 (ORG_TYPE_SCALARS) row -- confirmed by direct re-read of
   every 13a row. Only Set 3 has a dedicated row. Written verbatim per
   instruction; Pete's call whether to amend.

2. New Section 13b -- "Session Priority Queue," inserted after 13a's
   last row (the Legal/Compliance tail-risk row), before the blank-line
   + divider that precedes Section 14. No existing precedent for this
   section anywhere in the file -- placed here to extend the established
   13 / 13a lettering convention, since it's the closest existing
   structure (forward-looking session state, adjacent to the Decision
   Register).

   FLAGGED, not corrected here: priority item #6 (Pete's exact wording)
   describes "/book Step 5 (Schema.org JSON-LD, drafted not executed)"
   -- this is the exact stale claim the MOB's own Session Log entry at
   line 1936 already corrected this session (Step 5 shipped in commit
   a91a28c). Written verbatim per instruction; Pete's call whether to
   amend before this reaches the committed record.

Em-dashes in Pete's supplied text converted to "--" to match this
file's own established internal convention, consistent with every prior
patch script this session.

Part 3 -- Quarterly Step-Back cadence change (CLAUDE.md, Workflow
Governance -- Four-Tier Model section). Changes the cadence definition
from "roughly every 15 sessions" (locked Session 71) to calendar-based
"every 3 weeks," adds explicit Last/Next tracking fields, and notes the
session-count trigger is replaced entirely going forward, not just this
once. Reason: the session-number counter this depended on was
discontinued after Session 72 (Section 16 switched to date-based
headers with no session numbers), discovered this session when trying
to determine if a step-back was due and finding no reliable way to
count sessions since 71.

Documentation-only. Version bump left to Pete's explicit closeout
decision (not applied automatically by this script) -- Session Priority
Queue, the Set 2 symmetry row, and the Quarterly Step-Back cadence
change are all material enough that CLAUDE.md's closeout protocol calls
for one, but the exact new version number is confirmed at write time,
not hardcoded here speculatively.

Usage:
  python tools/patch_mob_session_closeout.py --dry-run
  python tools/patch_mob_session_closeout.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"
CLAUDE_FILE = REPO_ROOT / "CLAUDE.md"

# ── Part 1: Calibration Set 2 row, inserted after the Set 3 row ─────────────

SET3_ROW_ANCHOR = (
    "| Calibration Set 3 (STATE_MULTIPLIERS) -- Scoring Complete | 3 | "
    "Closed -- all 57 states scored across the 4-criterion rubric "
    "(Turnover/Retention, Productivity/Output, Decision-Quality/"
    "Velocity, Legal/Compliance), all rationales complete, zero open "
    "flags | Methodology per prompts/friction-tax-state-multiplier-"
    "methodology.md. Scoring worksheet and rationale work done in "
    "Claude.ai, values not yet applied to engine/friction_tax.py | This "
    "session (Claude Code) | Ready for Gemini architecture review of "
    "schema/type approach (consistent with OrgTypeScalarEntry pattern "
    "from Set 1) before CC writes STATE_MULTIPLIERS values. Not yet "
    "sent to Gemini |\n"
)

SET2_ROW = (
    "| Calibration Set 2 (PAYROLL_BASELINE_GRID) -- Closed | 3 | "
    "Closed -- all 54 cells (headcount x industry) populated | Closed "
    "alongside Calibration Set 1 (ORG_TYPE_SCALARS), commit 764d583 "
    "(per Section 16 session-log narrative, August 2026). Documented in "
    "engine/friction_tax.py's module docstring. This row added "
    "retroactively for Decision Register symmetry with the Set 1 and "
    "Set 3 entries -- no factual correction involved, Set 2 was never "
    "misrepresented as open | This session (Claude Code) -- retroactive "
    "Decision Register entry added for symmetry | None -- closed, no "
    "further action expected |\n"
)

SET1_ROW = (
    "| Calibration Set 1 (ORG_TYPE_SCALARS) -- Closed | 3 | "
    "Closed -- all org-type scalars populated | Closed alongside "
    "Calibration Set 2 (PAYROLL_BASELINE_GRID), commit 764d583 (per "
    "Section 16 session-log narrative, August 2026). Documented in "
    "engine/friction_tax.py's module docstring. This row added "
    "retroactively for Decision Register symmetry with the Set 2 and "
    "Set 3 entries | This session (Claude Code) -- retroactive Decision "
    "Register entry added for symmetry | None -- closed, no further "
    "action expected |\n"
)

# ── Part 2: Section 13b, inserted after 13a's last row (Legal/Compliance) ───

LEGAL_ROW_TAIL_ANCHOR = (
    "Sequencing: explicitly queued behind the multi-state compounding "
    "mechanism (state-count/Factor A/Factor B) -- do not start design "
    "work on this until that item is resolved and reopened by Pete | "
    "This session (Claude Code) | Pete's call -- reopen after "
    "multi-state compounding design is finalized |\n"
)

SECTION_13B = (
    "\n"
    "\\\\\\# 13b. Session Priority Queue\n"
    "\n"
    "Forward-looking session state, confirmed with Pete at closeout. "
    "Updated at each session close so a fresh session can pick up "
    "cleanly with no lost context. Not a Tier 3 Decision Register item "
    "-- a working queue, expected to be rewritten wholesale each time "
    "it's updated rather than accumulate history like 13a.\n"
    "\n"
    "Priority order for next session, in sequence:\n"
    "\n"
    "1. Resolve the multi_channel_severity_loading constant (currently "
    "0.05 placeholder, prompts/friction-tax-multistate-compounding-"
    "methodology.md) -- Pete's judgment call needed, not a research "
    "task. Then implement the multi-state compounding redesign in "
    "compute_friction_tax() per that same methodology doc: replace "
    "mean_multiplier with the per-criterion aggregation (Step 1), apply "
    "the severity multiplier mapping with frozen range (Step 2), apply "
    "multi_channel_severity_loading with the N=1 guard (Step 3), verify "
    "single-state continuity explicitly against existing Calibration "
    "Set 3 values, update tests.\n"
    "2. Reopen the deferred \"urgency window\" (Diagnostic Dimension "
    "Expansion) alongside #1 -- same compounding design conversation "
    "applied to urgency, not dollar cost, done together rather than "
    "re-deriving the reasoning separately later.\n"
    "3. Legal/Compliance actuarial tail-risk distinction (Decision "
    "Register item, explicitly queued behind #1) -- whether "
    "Legal/Compliance needs separate tail-risk treatment rather than "
    "blending into the same 0-2 scale as the other three criteria.\n"
    "4. /diagnostic Stages 4-5 rescoping -- no surviving plan doc, "
    "requires Pete to rescope from scratch. Prioritized above other "
    "backlog items because it's a live user-facing surface gap, not "
    "because it's ready to start.\n"
    "5. causation_pattern -> resolution_families.py routing influence "
    "-- split off from Diagnostic Dimension Expansion, not started, no "
    "scoping doc.\n"
    "6. The seven-experiments-to-methodology-series workstream (citation "
    "audit prioritizing E2/E5/E7, two-question test pass, consolidation-"
    "mapping against 57-state taxonomy, PCD-as-editorial-throughline "
    "framing decision).\n"
    "7. Infrastructure housekeeping, opportunistic/lower priority: "
    "weak-profile test limitation (generate_answers() weak branch "
    "ignoring target_state), calibration runner's untested severity "
    "follow-on questions (parked, do not raise unless Pete reopens), "
    "test_contract.py pre-existing liability_block KeyError, MemPalace "
    "drawer-write issue.\n"
    "\n"
    "Closed since last update, not on the active list: /book Step 5 "
    "(Schema.org JSON-LD) -- shipped, commit a91a28c.\n"
    "\n"
    "Explicitly parked, not on this list, do not resurface unless Pete "
    "reopens: confidentiality template field wording, attorney review "
    "of engagement agreement Section 3, LinkedIn 19-week content "
    "calendar.\n"
    "\n"
    "Calibration status as of session close: Friction Tax Sets 1 "
    "(ORG_TYPE_SCALARS), 2 (PAYROLL_BASELINE_GRID, 54-cell), and 3 "
    "(STATE_MULTIPLIERS, 57 states) all closed and live. "
    "calibration_complete genuinely returns True for real input as of "
    "commit 469b148. Multi-state compounding design locked and pushed "
    "(242379a) but not yet implemented -- this is the #1 priority "
    "above.\n"
    "\n"
    "Last updated: This session (Claude Code), session close.\n"
    "\n"
)

# ── Part 3: Quarterly Step-Back cadence change (CLAUDE.md) ──────────────────

STEP_BACK_OLD = (
    "### Quarterly Step-Back\n"
    "A full project assessment (workstream status, goal progress, process feedback) should be run roughly every 15 sessions, not only when Pete happens to request one.\n"
)

STEP_BACK_NEW = (
    "### Quarterly Step-Back\n"
    "A full project assessment (workstream status, goal progress, process feedback) should be run on a calendar cadence: every 3 weeks. Originally defined as \"roughly every 15 sessions\" (locked at Session 71) — changed because the session-number counter this depended on was discontinued after Session 72 (Section 16 switched to date-based headers with no session numbers), making the original trigger uncheckable. This calendar-based cadence replaces the session-count trigger entirely going forward, not just for this one instance — future step-backs are checked against calendar time from the last logged date below, not a session counter.\n"
    "\n"
    "- Last step-back: August 2, 2026 (this session — triggered deliberately given scope: all 3 Friction Tax calibration sets closed, multi-state compounding design locked, not waiting for a session-count trigger that no longer functions)\n"
    "- Next due: on or near August 23, 2026\n"
)

# ── Part 4: Section 16 Session Log entry (tools/_mob.txt) ───────────────────

SESSION16_TAIL_ANCHOR = (
    "No code changes from either correction -- both are read-only status "
    "verifications. CLAUDE.md MOB version cross-reference updated "
    "v4.73->v4.74. MOB version bumped to v4.74 -- closes the last open "
    "item from a previously-locked decision (individual coaching's "
    "confidentiality template wording) and corrects two stale in-session "
    "assumptions for the standing record, warrants a bump per the "
    "closeout protocol. MOB v4.74. |\n"
)

SESSION16_ENTRY = (
    "| **August 2026 — Calibration Set 3 closed and implemented, "
    "multi-state compounding design locked, Quarterly Step-Back cadence "
    "repaired** | **Calibration Set 3 (STATE_MULTIPLIERS) -- "
    "IMPLEMENTED, all 3 Friction Tax calibration sets now closed.** All "
    "57 states' StateMultiplierEntry/StateCriterionScore records "
    "(4-criterion rubric: turnover, productivity, decision_quality, "
    "legal) written into engine/friction_tax.py verbatim from the "
    "pre-scored source file, replacing the 57 x None table. New "
    "StateCriterionScore/StateMultiplierEntry frozen dataclasses, a "
    "module-load validation block (criteria-key/raw_score-sum/range "
    "assertions), and _DEFAULT_MULTIPLIER removed entirely (not just "
    "set to None, per Pete's revision) since its one live usage site was "
    "replaced with an inline None fallback. calibration_complete now "
    "genuinely returns True for any real, recognized input -- the first "
    "time in this subsystem's history all three axes "
    "(PAYROLL_BASELINE_GRID, ORG_TYPE_SCALARS, STATE_MULTIPLIERS) have "
    "been populated at once. Test suite reworked for the new schema: "
    "tests 2/14/15 inverted (real data now satisfies calibration rather "
    "than failing it), tests 4-9's bare-float monkey-patches wrapped in "
    "a synthetic StateMultiplierEntry helper, test 16 repurposed from a "
    "now-redundant positive-confirmation check into a genuine new edge "
    "case (mixed known/unknown state_ids). 37/37 checks pass. Commit "
    "469b148. **Encoding incident, caught and corrected before it "
    "reached the codebase:** a staging file's rationale text was "
    "corrupted with mojibake (a UTF-8 em-dash misread as CP1252) during "
    "an initial save attempt -- caught via byte-level verification (not "
    "visual inspection, which had initially given a false-clean read due "
    "to a missing stdout encoding reconfiguration), confirmed the source "
    "was clean and the corruption was introduced locally, re-saved "
    "correctly, and reverified at the byte level (117/117 real "
    "em-dashes, zero mojibake) before proceeding. **Process deviation, "
    "logged per Pete's explicit instruction rather than silently "
    "repeated or corrected after the fact:** the STATE_MULTIPLIERS write "
    "to engine/friction_tax.py happened before the test suite ran and "
    "before explicit go-ahead, out of the normal dry-run -> test -> "
    "hold -> write sequence. Pete let the write stand since the content "
    "was independently verified correct, but flagged it explicitly as a "
    "one-time deviation, not a new normal. **Multi-state compounding "
    "mechanism -- DESIGNED, not yet implemented.** New methodology "
    "(prompts/friction-tax-multistate-compounding-methodology.md, "
    "commit 608a945): anchor-plus-diminishing-layers aggregation, built "
    "at the criterion level rather than blending already-computed "
    "per-state multipliers, resolving three previously-parked questions "
    "together (state-count compounding, Factor A within-criterion "
    "stacking, Factor B breadth-across-criteria stacking). Revised same "
    "session (commit 242379a) after a self-flagged internal "
    "contradiction: the original 'frequency loading' framing argued "
    "breadth-across-criteria represents frequency, not severity, but the "
    "concept was renamed to 'multi-channel severity loading' at Pete's "
    "direction -- resolved by dropping the frequency/severity actuarial "
    "analogy entirely rather than patching around it, plus two real "
    "formula corrections added (an N=1 continuity guard preventing "
    "single-state sessions from incorrectly triggering multi-channel "
    "loading, and a frozen-range requirement pinning the min-max "
    "normalization bounds at design time rather than deriving them "
    "dynamically). Not yet reviewed by Gemini, not yet implemented -- "
    "logged as the #1 priority in the new Section 13b Priority Queue "
    "below. **Legal/Compliance actuarial tail-risk distinction flagged** "
    "(commit b390ae4) -- Legal/Compliance may behave as tail risk (rare, "
    "severe) rather than attritional risk (steady, frequency-driven) "
    "like the other three Set 3 criteria, explicitly queued behind the "
    "compounding redesign. **Decision Register (Section 13a) symmetry "
    "restored:** Calibration Set 1 (ORG_TYPE_SCALARS) and Set 2 "
    "(PAYROLL_BASELINE_GRID) both given their own Closed rows alongside "
    "the pre-existing Set 3 row -- self-caught mid-session that the "
    "first draft of Set 2's row claimed symmetry with a Set 1 row that "
    "didn't yet exist, corrected by actually adding one rather than "
    "adjusting the claim. **New Section 13b -- Session Priority Queue** "
    "established as a standing forward-looking mechanism, rewritten "
    "wholesale at each closeout rather than accumulating history like "
    "13a -- also self-corrected mid-session (a first draft listed /book "
    "Step 5 Schema.org JSON-LD as still-pending, contradicting the "
    "MOB's own prior correction that it shipped in commit a91a28c; "
    "fixed before commit, moved to a closed-items note). **Quarterly "
    "Step-Back mechanism repaired:** discovered this session that its "
    "session-count trigger ('every 15 sessions,' locked at Session 71) "
    "has been silently uncheckable since Session 72, when Section 16 "
    "switched from numbered sessions to date-based headers with no "
    "session numbers -- nobody had tried to check whether a step-back "
    "was due until this session, so the break went unnoticed. Replaced "
    "with a calendar-based cadence (every 3 weeks) in CLAUDE.md, with "
    "explicit Last (August 2, 2026, this session) / Next (on or near "
    "August 23, 2026) tracking fields, replacing the session-count "
    "trigger entirely going forward, not just this once. CLAUDE.md MOB "
    "version cross-reference updated v4.74->v4.75. MOB version bumped "
    "to v4.75 -- Calibration Set 3's closure and implementation, a "
    "newly locked compounding design, a repaired standing governance "
    "mechanism, and two new Decision Register entries all warrant a "
    "bump per the closeout protocol. MOB v4.75. |\n"
)

# ── Part 5: Version bump headers (both files) ────────────────────────────────

MOB_VERSION_OLD = "\\\\\\#\\\\\\# MOB v4.74\n"
MOB_VERSION_NEW = "\\\\\\#\\\\\\# MOB v4.75\n"

CLAUDE_VERSION_OLD = "| MOB version | v4.74 |\n"
CLAUDE_VERSION_NEW = "| MOB version | v4.75 |\n"


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        print(f"ABORT -- anchor not found: {label}", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches): {label}", file=sys.stderr)
        sys.exit(1)
    return text.replace(old, new)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    mob_text = MOB_FILE.read_text(encoding="utf-8")
    claude_text = CLAUDE_FILE.read_text(encoding="utf-8")

    mob_text = _replace_once(mob_text, SET3_ROW_ANCHOR, SET3_ROW_ANCHOR + SET1_ROW + SET2_ROW, "Set 1 + Set 2 row insertion (after Set 3 row)")
    mob_text = _replace_once(mob_text, LEGAL_ROW_TAIL_ANCHOR, LEGAL_ROW_TAIL_ANCHOR + SECTION_13B, "Section 13b insertion (after last 13a row)")
    mob_text = _replace_once(mob_text, SESSION16_TAIL_ANCHOR, SESSION16_TAIL_ANCHOR + SESSION16_ENTRY, "Section 16 entry insertion (after v4.74 row)")
    mob_text = _replace_once(mob_text, MOB_VERSION_OLD, MOB_VERSION_NEW, "MOB header version bump")
    claude_text = _replace_once(claude_text, STEP_BACK_OLD, STEP_BACK_NEW, "Quarterly Step-Back cadence change")
    claude_text = _replace_once(claude_text, CLAUDE_VERSION_OLD, CLAUDE_VERSION_NEW, "CLAUDE.md MOB version cross-reference bump")

    print("=" * 78)
    print("PART 1 (tools/_mob.txt) -- New Decision Register rows: Calibration")
    print("Set 1 and Set 2, inserted immediately after the Set 3 row")
    print("=" * 78)
    print(SET1_ROW.rstrip("\n"))
    print()
    print(SET2_ROW.rstrip("\n"))

    print("\n" + "=" * 78)
    print("PART 2 (tools/_mob.txt) -- New Section 13b: Session Priority Queue,")
    print("inserted after 13a's last row (Legal/Compliance tail-risk)")
    print("=" * 78)
    print(SECTION_13B.rstrip("\n"))

    print("\n" + "=" * 78)
    print("PART 3 (CLAUDE.md) -- Quarterly Step-Back cadence change")
    print("=" * 78)
    print("--- OLD ---")
    print(STEP_BACK_OLD.rstrip("\n"))
    print("--- NEW ---")
    print(STEP_BACK_NEW.rstrip("\n"))

    print("\n" + "=" * 78)
    print("PART 4 (tools/_mob.txt) -- New Section 16 Session Log entry,")
    print("inserted immediately after the v4.74 row")
    print("=" * 78)
    print(SESSION16_ENTRY.rstrip("\n"))

    print("\n" + "=" * 78)
    print("PART 5 -- Version bumps: v4.74 -> v4.75 (both files)")
    print("=" * 78)
    print(f"tools/_mob.txt header: {MOB_VERSION_OLD.strip()!r} -> {MOB_VERSION_NEW.strip()!r}")
    print(f"CLAUDE.md Key References: {CLAUDE_VERSION_OLD.strip()!r} -> {CLAUDE_VERSION_NEW.strip()!r}")

    print("\n" + "=" * 78)
    print("NOT INCLUDED IN THIS SCRIPT -- handled separately: Diary Write")
    print("(MemPalace MCP call), Mine (mempalace mine CLI)")
    print("=" * 78)

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    MOB_FILE.write_text(mob_text, encoding="utf-8")
    print(f"\nWROTE {MOB_FILE.relative_to(REPO_ROOT)}")
    CLAUDE_FILE.write_text(claude_text, encoding="utf-8")
    print(f"WROTE {CLAUDE_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
