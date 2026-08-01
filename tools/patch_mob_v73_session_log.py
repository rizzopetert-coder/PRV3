"""
PRV3 -- Combined write: tools/_mob.txt version header bump (v4.72 ->
v4.73), new Section 16 session log row (Friction Tax value calibration,
Sets 1 and 2 closed), and CLAUDE.md's MOB version cross-reference
update.

Anchor learned from the v4.71 row-boundary bug earlier this session:
insert AFTER the full "MOB v4.72. |\\n" closing marker (preserving it
verbatim in the replacement), not on a substring that could straddle
the row boundary incorrectly.

Usage:
  python tools/patch_mob_v73_session_log.py --dry-run
  python tools/patch_mob_v73_session_log.py --write
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

CLAUDE_ANCHOR = "| MOB version | v4.72 |"
CLAUDE_REPLACEMENT = "| MOB version | v4.73 |"

# ── tools/_mob.txt: version header ──────────────────────────────────────────

MOB_HEADER_ANCHOR = "\\\\\\#\\\\\\# MOB v4.72"
MOB_HEADER_REPLACEMENT = "\\\\\\#\\\\\\# MOB v4.73"

# ── tools/_mob.txt: new Section 16 row ──────────────────────────────────────

SECTION16_ANCHOR = "MOB v4.72. |\n| **May 2026"

NEW_ROW = (
    "| **August 2026 — Friction Tax: value calibration, Sets 1 and 2 "
    "closed** | **Research workflow decision:** given this session's "
    "earlier pattern of Gemini-sourced figures pairing a real citation "
    "with a fabricated or mismatched finding (Publicly traded scalar, "
    "Government scalar -- see the friction-tax restructure entry above), "
    "Pete opted to have Gemini lead the full three-set research pass "
    "(org-type scalars, payroll grid, state multipliers) as originally "
    "planned, then run independent verification via the Research feature "
    "rather than spot-checks alone, given the scale (117 total values). "
    "The verification pass confirmed the pattern was not isolated: "
    "real-source-wrong-number errors surfaced across all three sets, not "
    "just the two already caught, alongside several genuinely confirmed "
    "figures (Gallup 18%, Housman & Minor $12,489, the SHRM/Gallup "
    "replacement-cost band, Liberty Mutual's 3-5x indirect-cost ratio) "
    "and clearly-flagged unverifiable proprietary sources (Aon Radford, "
    "PitchBook -- the latter's cited report title does not appear to "
    "exist under that name). **Set 1 (ORG_TYPE_SCALARS) closed.** Of 6 "
    "categories, 4 corrected to parity (1.00) after their claimed "
    "differentials failed verification -- Publicly traded and "
    "Government's claims traced to real sources with fabricated or "
    "mismatched findings (detailed in the restructure entry); "
    "Nonprofit's claimed -10% was directly contradicted by the actual "
    "data (BLS Monthly Labor Review 2024 shows nonprofit wages "
    "near-parity to higher on a raw basis); Founder-led and PE/VC-backed "
    "had no verifiable public differential (proprietary sources, one "
    "title not found). Government corrected to 1.05, the real CBO "
    "headline finding (was misattributed at 1.17). Required a real "
    "schema addition mid-task: new OrgTypeScalarEntry dataclass to carry "
    "source/citation alongside each scalar, matching the existing "
    "PayrollBaselineEntry pattern -- flagged by CC rather than silently "
    "built. Committed d2c6a49. **Headcount midpoints closed with genuine "
    "computed data**, not assumption. The original SUSB citation "
    "justifying the 6 bucket midpoints was fabricated (Census SUSB "
    "distributions are bottom-skewed, don't support \"centers at 12\" "
    "for the 1-24 bucket or a 1,500 \"median enterprise size\" for "
    "1000+). Claude.ai's sandboxed environment couldn't fetch the real "
    "Census SUSB data file directly (robots-disallowed), so the task was "
    "hard-handed to CC, which has real network access on Pete's machine. "
    "CC found the actual right file after an initial wrong file only had "
    "coarse bands, and found the real detailed brackets are "
    "finer-grained than the literature-derived approximation used to "
    "scope the task (no clean break at 249/250, requiring the 200-299 "
    "bracket to be split 50/50 across the \"100-249\" and \"250-499\" "
    "buckets). All 6 midpoints computed as genuine firm-count-weighted "
    "means from the real 2022 SUSB detailed-size file, independently "
    "validated against the file's own reported grand total to the "
    "digit. The \"1000+\" bucket required a deliberate methodology "
    "call: the raw weighted mean (6,230) was almost entirely driven by "
    "a small number of true mega-corporations in the open-ended 5,000+ "
    "bracket, producing a Fortune-500-scale figure unrepresentative of "
    "this platform's realistic client base. Pete chose to exclude the "
    "5,000+ tail entirely, recomputing the \"1000+\" midpoint from the "
    "1,000-4,999 range only (2,027.26). Committed 57d642b. **Set 2 "
    "(PAYROLL_BASELINE_GRID, 54 cells) closed.** All 9 industry wage "
    "inputs now real: 4 previously confirmed unchanged (Professional "
    "Services, Healthcare, Financial Services, Other), 2 previously "
    "corrected unchanged (Government -- wrong sector code fixed; "
    "Technology -- reclassified off a Publishing Industries mismatch), "
    "and 3 closed this pass. Manufacturing & Industrial confirmed exact "
    "against BLS OEWS directly. Retail & Hospitality and Nonprofit & "
    "Education required real computation rather than a single-sector "
    "lookup -- both are genuine employment-weighted means across their "
    "actual BLS component sectors (Retail Trade + Food Services + "
    "Accommodation; Educational Services + NAICS 813000 nonprofit/civic "
    "organizations), not approximations. A real arithmetic discrepancy "
    "surfaced between the handoff's rounded figure and CC's independent "
    "recomputation for Retail & Hospitality ($39,650 vs. $39,651) -- "
    "caught, verified, resolved in favor of the more precise number, "
    "documented rather than silently picked. Structural fix required "
    "mid-task: HEADCOUNT_MIDPOINTS had to move earlier in the file as a "
    "real computational dependency rather than descriptive text once the "
    "grid started actually multiplying against it. All 54 cells now "
    "hold real computed payroll_floor_annual values. Test suite expanded "
    "to 35 checks, including independent per-cell recomputation against "
    "the module's own arithmetic and a new positive-confirmation test "
    "proving calibration_complete correctly flips True when given fully "
    "real data across every table except STATE_MULTIPLIERS -- confirming "
    "the remaining False result is correctly gated, not coincidentally "
    "stuck. Committed 764d583. **Status:** Friction Tax calibration -- "
    "ORG_TYPE_SCALARS and PAYROLL_BASELINE_GRID (Sets 1 and 2) fully "
    "populated with genuine, independently-verified or "
    "independently-computed values. STATE_MULTIPLIERS (Set 3, 57 "
    "states) remains the only unpopulated table -- calibration_complete "
    "will return False for every real session until it's closed. Not "
    "started. CLAUDE.md MOB version cross-reference updated "
    "v4.72->v4.73. MOB version bumped to v4.73 -- closes two of three "
    "friction tax calibration sets with genuinely verified/computed "
    "values, a material workstream status change, warrants a bump per "
    "the closeout protocol. MOB v4.73. |\n"
    "| **May 2026"
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
    mob_text = _apply(mob_text, SECTION16_ANCHOR, "MOB v4.72. |\n" + NEW_ROW, "tools/_mob.txt Section 16 new row")

    print("All 3 anchors found and unique. Changes:")
    print("=" * 72)
    print("1. CLAUDE.md -- MOB version v4.72 -> v4.73")
    print("2. tools/_mob.txt -- header MOB v4.72 -> v4.73")
    print("3. tools/_mob.txt -- new Section 16 row (Friction Tax value")
    print("   calibration, Sets 1 and 2 closed)")
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
