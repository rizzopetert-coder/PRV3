"""
PRV3 -- Durable write: prompts/friction-tax-band-segmentation.md

New file, content supplied verbatim by Pete, "[today's date]" filled in.
Follows the existing prompts/*.md handoff-doc convention (e.g.
prompts/friction-tax-unit-decision.md, prompts/diagnostic-dimension-
expansion.md). Structural decision record only -- no code changes, no
STATE_MULTIPLIERS/band_low values populated, not yet sent to Gemini.

Usage:
  python tools/patch_friction_tax_band_segmentation.py --dry-run
  python tools/patch_friction_tax_band_segmentation.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "prompts" / "friction-tax-band-segmentation.md"

DECISION_DATE = "2026-07-28"

CONTENT = f"""# Friction Tax: Org-Size Band Segmentation Decision

Decided {DECISION_DATE}. Follows prompts/friction-tax-unit-decision.md
(payroll-based units, not revenue-based).

## Problem
band_low as a flat headcount-only figure (5 bands) is too imprecise --
a 50-person law firm and a 50-person retail chain have very different
typical payroll profiles at the same headcount, since compensation
varies wildly by role mix and industry.

## Decision
Segment band_low by headcount x industry (5 x 9 = 45 cells), using
IntakeData.industry's existing 9 categories (Professional Services,
Healthcare & Life Sciences, Financial Services, Technology, Manufacturing
& Industrial, Retail & Hospitality, Nonprofit & Education, Government &
Public Sector, Other). This extends an existing pattern in the codebase
-- HIGH_HAZARD_INDUSTRIES already segments Manufacturing/Healthcare for
a different (Safety & Wellbeing) multiplier, so industry-based
segmentation isn't new architecture.

org_type (6 categories: Founder-led, PE or VC-backed, Privately held
professional leadership, Nonprofit, Publicly traded, Government) is NOT
a fully independent third axis (5 x 9 x 6 = 270 cells is not
researchable against real sources). Instead, org_type applies as a
secondary modifier on top of the headcount x industry grid -- exact
modifier mechanism (e.g. a documented nonprofit pay discount) to be
scoped separately once real benchmark research clarifies what's
actually citable.

## Rationale
Industry is the more researchable axis: published compensation
benchmarks (BLS wage data, PayScale, comp surveys) are standardly
segmented by industry and company size. Ownership structure isn't a
standard benchmarking axis in the same way, though specific narrower
comparisons (e.g. nonprofit vs. for-profit pay gaps) are real and
citable -- hence treating it as a modifier rather than a primary axis.

## Separate finding, logged here to not lose it
_ORG_SIZE_BANDS's keys ("1_to_25", "26_to_100", "101_to_500",
"501_to_2500", "2501_plus") do not match IntakeData.headcount's actual
values ("Under 25", "25-99", "100-249", "250-499", "500-999", "1000+")
-- different string format and different bucket boundaries entirely.
Not urgent since compute_friction_tax() isn't wired into the live
pipeline yet, but a headcount-string translation layer will be needed
whenever it is, independent of whether this segmentation decision
changes anything else about the structure.

## Status
Structural decision only. Not yet sent to Gemini for architecture
review (required before CC builds the actual 45-cell restructure). No
code changes made. STATE_MULTIPLIERS and band_low values remain None.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if TARGET_FILE.exists():
        print(f"ABORT -- {TARGET_FILE.relative_to(REPO_ROOT)} already exists", file=sys.stderr)
        sys.exit(1)

    print(f"New file: {TARGET_FILE.relative_to(REPO_ROOT)}")
    print("=" * 72)
    print(CONTENT)
    print("=" * 72)
    print("No other files touched by this script.")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TARGET_FILE.write_text(CONTENT, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
