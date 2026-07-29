"""
PRV3 -- Durable write: prompts/friction-tax-client-copy.md

New file, content supplied verbatim by Pete, "[today's date]" filled in.
Follows the existing prompts/*.md handoff-doc convention (e.g.
prompts/friction-tax-unit-decision.md, prompts/friction-tax-band-
segmentation.md). Approved client-facing copy, held in reserve --
neither destination (private report estimate, site methodology page)
exists yet. No code changes, no placement built.

Usage:
  python tools/patch_friction_tax_client_copy.py --dry-run
  python tools/patch_friction_tax_client_copy.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "prompts" / "friction-tax-client-copy.md"

APPROVAL_DATE = "2026-07-29"

CONTENT = f"""# Friction Tax: Client-Facing Explanation Copy

Approved {APPROVAL_DATE}. Neither destination exists yet -- saved here so
it isn't lost before the friction tax build (band segmentation, value
population) and the site placement catch up.

## Short version -- for near the estimate in the private report

This estimate reflects what this condition typically costs to sustain.
It's calculated from your organization's size and industry, adjusted for
how your company is structured, and scaled to how deeply the pattern has
taken hold. The range reflects real uncertainty in any cost estimate,
not imprecision in the diagnosis.

## Long version -- for a site methodology page

**How We Calculate Estimated Cost**

Every organizational condition in this assessment carries a financial
cost, whether or not anyone has put a number on it. We estimate that
cost in four steps.

First, we start with a payroll baseline: what a company of your size, in
your industry, typically spends on payroll each year, drawn from
published wage and compensation research.

Second, we adjust that baseline for how your organization is structured.
A founder-led company, a private-equity-backed company, a nonprofit, and
a public company pay differently for well-documented reasons, and the
estimate reflects that.

Third, we apply a cost factor specific to the condition identified.
Research on turnover, disengagement, and lost productivity tells us
roughly what each kind of dysfunction costs an organization as a share
of payroll when it goes unaddressed.

Fourth, we scale the estimate to how deeply the condition has taken
root. A pattern that is just beginning to show costs less than one that
has become how the organization normally operates.

The result is a range, not a single figure. Any estimate of
organizational cost carries real uncertainty, and presenting a range is
more honest than false precision.

## Placement (not yet built)
- Short version: private report, adjacent to the rendered
  friction_tax_estimate figure once that field is actually wired into
  the live pipeline (currently not called anywhere -- see
  prompts/friction-tax-band-segmentation.md).
- Long version: a site methodology page. No such page currently exists;
  this is content in reserve until that page is scoped.

## Status
Content approved. No placement built. No code changes made as part of
this write.
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
