"""
PRV3 -- Combined write: tools/_mob.txt version header bump (v4.70 -> v4.71),
new Section 16 session log row (Report Depth Tier 4 authored-content
sub-items closed), new Section 13a Decision Register row (Section 13's
Current Workstream summary flagged as stale, Tier 3 informational), and
CLAUDE.md's MOB version cross-reference update.

Per Pete's explicit direction: no sequential "Session N" number (the
file's own numbering was discontinued after Session 72 in favor of
date/topic titles for the last 7+ entries) -- this entry matches that
same title convention, using today's actual date (August 2026). Section
13 itself is NOT touched in this task -- its staleness is logged as a
new, separate Decision Register row instead, per Pete's explicit call.

Usage:
  python tools/patch_mob_v71_session_log.py --dry-run
  python tools/patch_mob_v71_session_log.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

# ── CLAUDE.md: version cross-reference ──────────────────────────────────────

CLAUDE_ANCHOR = "| MOB version | v4.70 |"
CLAUDE_REPLACEMENT = "| MOB version | v4.71 |"

# ── tools/_mob.txt: version header ──────────────────────────────────────────

MOB_HEADER_ANCHOR = "\\\\\\#\\\\\\# MOB v4.70"
MOB_HEADER_REPLACEMENT = "\\\\\\#\\\\\\# MOB v4.71"

# ── tools/_mob.txt: new Section 16 row ──────────────────────────────────────

SECTION16_ANCHOR = (
    "MOB v4.70. |\n"
    "| **May 2026 — Session 1** | Taxonomy consolidation (108 to 47 states)"
)

NEW_SESSION16_ROW = (
    "| **August 2026 — Report Depth Tier 4, authored-content sub-items "
    "closed** | **Resolution-family copy:** 4 blurbs authored (structural, "
    "developmental, investigative, directional), replacing COPY PENDING "
    "placeholders in RESOLUTION_FAMILY_DESCRIPTIONS. No schema change -- "
    "architecture was already locked (static, non-LLM-generated, S34/S42). "
    "Rewrote one sub-item mid-session per Pete's note that \"This isn't X. "
    "It's Y.\" read as a repeated construction across two of the four. "
    "tools/test_resolution_families.py 101/0, service-name check clean on "
    "all four. Committed 95fc404. **State-prose schema:** sent to Gemini "
    "for structural review (open question: static StateProfile field vs. "
    "expanded LLM synthesis field). Gemini recommended Option C -- static "
    "descriptive_prose field on StateProfile, zero output_synthesis.py "
    "involvement, consistent with P-12 token-cost discipline and the "
    "existing clinical boundary (engine owns state truth, LLM "
    "contextualizes, never re-describes). Direct-read verification of "
    "Gemini's proposed schema locations caught a real error before any "
    "code was written: Gemini named engine/output.py as home to "
    "_IDENTIFIED_STATE_FIELDS and _STATE_DISTRIBUTION_ENTRY_FIELDS -- both "
    "constants actually live in engine/contract.py, along with the "
    "assemble_output() construction site and validate_schema(). Corrected "
    "before build. Logged as another confirmed instance of the Gemini "
    "plausible-but-wrong-specifics pattern (see existing MOB entries on "
    "Boeing/Allstate citations, the 44% Authority-density fabrication, and "
    "the Alliance/Authority field-swap pattern) -- this one caught by CC's "
    "own direct-read discipline rather than Claude.ai's verification step, "
    "worth noting as the pattern isn't confined to citations/figures, it "
    "extends to file-location claims in architecture handoffs. Schema "
    "build surfaced a second scope question CC flagged before writing "
    "rather than deciding unilaterally: making descriptive_prose a "
    "required field on web/lib/types.ts's StateRef would have cascaded "
    "into a 7-file change (engine-client.ts's inline mirror type, 3 route "
    "handlers, two computeWeights() helper widenings) rather than the "
    "3-file change as originally scoped. Pete chose Option 2 -- optional "
    "field, defer the route/engine-client wiring to the content-population "
    "follow-on task. Schema committed 3df6dd5. 169/172 calibration "
    "unchanged, zero regressions, tsc clean. **Content population:** all "
    "57 states' descriptive_prose authored (third-person diagnostic "
    "register, distinct from web/data/taxonomy.ts's second-person "
    "self-recognition voice -- different audience moment, pre- vs. "
    "post-diagnosis) and populated via the "
    "STATE_PROFILES[...].descriptive_prose = \"...\" pattern, matching the "
    "existing dimensional_vector post-construction-assignment convention. "
    "57/57 verified against the live registry pre-write, zero duplicates, "
    "zero missing. Committed df8af18. **Deferred StateRef wiring completed "
    "in the same task:** engine-client.ts's inline EngineResult mirror "
    "types, the Path 1 answer/route.ts mapping, and computeWeights() "
    "widened in both result/route.ts and share/create/route.ts so "
    "descriptive_prose survives the existing {id, name, score} narrowing "
    "step instead of being silently dropped. tsc clean, full suite + "
    "172-profile calibration unchanged (169/172), zero regressions. "
    "Committed 63cd521. **Also this session:** pre-existing "
    "test_contract.py section-12 liability_block KeyError, previously "
    "only in Section 16 narrative across multiple past sessions, given a "
    "proper Section 13a Decision Register row (Tier 3, informational, no "
    "urgency). Committed 3536095, no version bump (pure documentation of "
    "an already-known issue). **Report Depth Tier 4 status:** "
    "resolution-family copy and state-prose both CLOSED. Remaining on "
    "Tier 4: visual/layout treatment (\"color and dynamism\"), which was "
    "scoped from the start as a separate frontend-design pass, not a "
    "content task -- not started. CLAUDE.md MOB version cross-reference "
    "updated v4.70->v4.71. MOB version bumped to v4.71 -- Report Depth "
    "Tier 4's two authored-content sub-items fully closed (resolution-"
    "family copy, 57-state descriptive prose schema and content), each "
    "involving new locked or completed content and a schema decision, "
    "warrants a bump per the closeout protocol. MOB v4.71. |\n"
)

# ── tools/_mob.txt: new Section 13a Decision Register row ──────────────────

SECTION13A_ANCHOR = (
    '| No forced check-in -- worth a real fix whenever engine/contract.py\'s '
    'private_output block or test_contract.py\'s section 12 gets touched '
    'for an unrelated reason, at which point it is a cheap fix to make '
    'while already in that code |\n'
)

NEW_SECTION13A_ROW = (
    "| Section 13's Current Workstream summary is stale | 3 | Open, "
    "informational -- no urgency, not blocking | Section 13's \"Current "
    "Workstream\" heading and its opening paragraphs still describe "
    "Session 31-era Workstream 1/2/3 and Phase 1/2 framing, and have not "
    "been updated to reflect anything from the last several dozen "
    "sessions of real work -- Path 1, /book, Diagnostic Dimension "
    "Expansion, Report Depth Initiative, friction tax, and more. "
    "Confirmed via direct grep of the live file: zero mentions of "
    "\"Report Depth\" or any comparable recent workstream name anywhere "
    "in Section 13. Section 13a (this Decision Register) and Section 16 "
    "(Session Log) have functionally superseded Section 13's top summary "
    "as the actual living trackers of current status, but Section 13 "
    "itself was never folded in or retired. Surfaced while confirming "
    "where to log Report Depth Tier 4's new status this session -- not "
    "fixed here, per Pete's explicit instruction to defer | This session "
    "(Claude Code) -- surfaced, not fixed | Whenever Pete opens a "
    "dedicated task for the Section 13 rewrite -- not a forced check-in |\n"
)


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

    claude_text = _apply(claude_text, CLAUDE_ANCHOR, CLAUDE_REPLACEMENT, "CLAUDE.md MOB version cross-reference")
    mob_text = _apply(mob_text, MOB_HEADER_ANCHOR, MOB_HEADER_REPLACEMENT, "tools/_mob.txt version header")
    mob_text = _apply(mob_text, SECTION16_ANCHOR, NEW_SESSION16_ROW + SECTION16_ANCHOR, "tools/_mob.txt Section 16 new row")
    mob_text = _apply(mob_text, SECTION13A_ANCHOR, SECTION13A_ANCHOR + NEW_SECTION13A_ROW, "tools/_mob.txt Section 13a new row")

    print("All 4 anchors found and unique. Changes:")
    print("=" * 72)
    print("1. CLAUDE.md -- MOB version v4.70 -> v4.71")
    print("2. tools/_mob.txt -- header MOB v4.70 -> v4.71")
    print("3. tools/_mob.txt -- new Section 16 row (Report Depth Tier 4")
    print("   authored-content sub-items closed, date/topic title, no")
    print("   sequential session number)")
    print("4. tools/_mob.txt -- new Section 13a row (Section 13 Current")
    print("   Workstream summary flagged stale, Tier 3 informational)")
    print("=" * 72)

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    CLAUDE_MD.write_text(claude_text, encoding="utf-8")
    MOB_FILE.write_text(mob_text, encoding="utf-8")
    print("\nWROTE CLAUDE.md")
    print("WROTE tools/_mob.txt")


if __name__ == "__main__":
    main()
