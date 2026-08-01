"""
PRV3 -- Friction Tax headcount midpoints: finalize all 6 real,
firm-count-weighted values from Census SUSB 2022 detailed-size data.

FINDING, flagged not assumed: no HEADCOUNT_MIDPOINTS structure existed
anywhere in the live file before this task -- the earlier "12/62/174.5/
374.5/749.5/1500" figures existed only as a narrative mention in the
module docstring describing a fabricated citation, never as real code.
There was nothing to "confirm the field name" of; this introduces a new
HeadcountMidpointEntry dataclass + HEADCOUNT_MIDPOINTS dict, following
the same pattern already established twice in this file
(PayrollBaselineEntry, OrgTypeScalarEntry).

Scope, per Pete's explicit instruction: data addition only.
compute_friction_tax() is NOT touched -- payroll_floor_annual still
requires HEADCOUNT_MIDPOINTS x industry wage, a separate follow-on task
once both sides exist. No logic change this pass.

Usage:
  python tools/patch_friction_tax_headcount_midpoints.py --dry-run
  python tools/patch_friction_tax_headcount_midpoints.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
FRICTION_TAX_PY = REPO_ROOT / "engine" / "friction_tax.py"

EDITS = [
    # Edit 1: module docstring -- headcount midpoints are no longer
    # "a separate, unresolved research item."
    (
        'Payroll baseline formula (not yet computable): payroll_floor_annual =\n'
        'industry_wage x headcount_midpoint. Industry wage figures are populated\n'
        'below for 6 of 9 industries (source/citation_id only -- see each\n'
        'PAYROLL_BASELINE_GRID entry). Headcount midpoints are a separate,\n'
        'unresolved research item -- an earlier midpoint set (12/62/174.5/374.5/\n'
        '749.5/1500 for the 6 buckets) cited Census SUSB size-class data that does\n'
        'not actually support those figures (SUSB distributions are bottom-skewed\n'
        'toward the smallest firms; they do not support a "1500 median enterprise\n'
        'size" for the open-ended "1000+" bucket). 1500 remains Pete\'s working\n'
        'placeholder for that bucket specifically, not a cited or final value.\n',

        'Payroll baseline formula (not yet computable): payroll_floor_annual =\n'
        'industry_wage x headcount_midpoint. Industry wage figures are populated\n'
        'below for 6 of 9 industries (source/citation_id only -- see each\n'
        'PAYROLL_BASELINE_GRID entry). Headcount midpoints (HEADCOUNT_MIDPOINTS,\n'
        'below) are now finalized -- real, firm-count-weighted mean employees-per-\n'
        'firm values computed from Census SUSB 2022 detailed-size data, replacing\n'
        'the earlier fabricated SUSB-citation midpoint set (12/62/174.5/374.5/\n'
        '749.5/1500, which cited Census SUSB size-class data that did not\n'
        'actually support those figures). payroll_floor_annual itself is still\n'
        'not computable -- multiplying HEADCOUNT_MIDPOINTS against the sourced\n'
        'industry wages is a separate follow-on task.\n',
    ),
    # Edit 2: insert HEADCOUNT_MIDPOINTS after PAYROLL_BASELINE_GRID,
    # before the Org type scalar section.
    (
        '    for headcount in HEADCOUNT_BUCKETS\n'
        '    for industry in INDUSTRIES\n'
        '}\n'
        '\n'
        '\n'
        '# -- Org type scalar --------------------------------------------------------------\n',

        '    for headcount in HEADCOUNT_BUCKETS\n'
        '    for industry in INDUSTRIES\n'
        '}\n'
        '\n'
        '\n'
        '# -- Headcount midpoints ----------------------------------------------------------\n'
        '# Firm-count-weighted mean employees-per-firm for each headcount bucket.\n'
        '# Source: Census SUSB 2022 Annual Data,\n'
        '# us_state_naics_detailedsizes_2022.xlsx ("US & states detailed sizes"),\n'
        '# national All-Industries Total row -- fetched and computed directly from\n'
        '# the real file (2026-08-01), replacing the earlier fabricated SUSB\n'
        '# citation. Not yet wired into compute_friction_tax() -- payroll_floor_\n'
        '# annual still requires this value multiplied by an industry wage figure,\n'
        '# a separate follow-on task once both sides exist.\n'
        '\n'
        '@dataclass(frozen=True)\n'
        'class HeadcountMidpointEntry:\n'
        '    """Firm-count-weighted mean employees per firm for one headcount bucket."""\n'
        '    employees_per_firm: Optional[float]\n'
        '    source: Optional[str]\n'
        '    citation_id: Optional[str]\n'
        '\n'
        '\n'
        'HEADCOUNT_MIDPOINTS: dict[str, HeadcountMidpointEntry] = {\n'
        '    "Under 25": HeadcountMidpointEntry(\n'
        '        employees_per_firm=4.28,\n'
        '        source=(\n'
        '            "Census SUSB 2022 Annual Data, "\n'
        '            "us_state_naics_detailedsizes_2022.xlsx (\'US & states detailed "\n'
        '            "sizes\'), national All-Industries Total row, firm-count-weighted "\n'
        '            "mean employees per firm. Brackets used: <5, 5-9, 10-14, 15-19, "\n'
        '            "20-24 employees (whole brackets, no splitting needed -- real "\n'
        '            "bracket boundaries align exactly at the 24/25 cutoff)."\n'
        '        ),\n'
        '        citation_id="SUSB_2022_detailedsizes_under25",\n'
        '    ),\n'
        '    "25-99": HeadcountMidpointEntry(\n'
        '        employees_per_firm=45.10,\n'
        '        source=(\n'
        '            "Census SUSB 2022 Annual Data, "\n'
        '            "us_state_naics_detailedsizes_2022.xlsx (\'US & states detailed "\n'
        '            "sizes\'), national All-Industries Total row, firm-count-weighted "\n'
        '            "mean employees per firm. Brackets used: 25-29, 30-34, 35-39, "\n'
        '            "40-49, 50-74, 75-99 employees (whole brackets, no splitting "\n'
        '            "needed -- real bracket boundaries align exactly at the 99/100 "\n'
        '            "cutoff)."\n'
        '        ),\n'
        '        citation_id="SUSB_2022_detailedsizes_25to99",\n'
        '    ),\n'
        '    "100-249": HeadcountMidpointEntry(\n'
        '        employees_per_firm=151.53,\n'
        '        source=(\n'
        '            "Census SUSB 2022 Annual Data, "\n'
        '            "us_state_naics_detailedsizes_2022.xlsx (\'US & states detailed "\n'
        '            "sizes\'), national All-Industries Total row, firm-count-weighted "\n'
        '            "mean employees per firm. Brackets used: 100-149, 150-199 "\n'
        '            "employees (whole), plus the 200-299 bracket split 50/50 by "\n'
        '            "uniform-distribution assumption across its two sub-ranges "\n'
        '            "(200-249 used here, 250-299 used in the 250-499 bucket below) "\n'
        '            "-- the real brackets do not break at 249/250, so this bracket "\n'
        '            "required proportional splitting."\n'
        '        ),\n'
        '        citation_id="SUSB_2022_detailedsizes_100to249",\n'
        '    ),\n'
        '    "250-499": HeadcountMidpointEntry(\n'
        '        employees_per_firm=327.50,\n'
        '        source=(\n'
        '            "Census SUSB 2022 Annual Data, "\n'
        '            "us_state_naics_detailedsizes_2022.xlsx (\'US & states detailed "\n'
        '            "sizes\'), national All-Industries Total row, firm-count-weighted "\n'
        '            "mean employees per firm. Brackets used: the 200-299 bracket "\n'
        '            "split 50/50 by uniform-distribution assumption (250-299 half "\n'
        '            "used here, 200-249 half used in the 100-249 bucket above), "\n'
        '            "plus 300-399, 400-499 employees (whole)."\n'
        '        ),\n'
        '        citation_id="SUSB_2022_detailedsizes_250to499",\n'
        '    ),\n'
        '    "500-999": HeadcountMidpointEntry(\n'
        '        employees_per_firm=692.43,\n'
        '        source=(\n'
        '            "Census SUSB 2022 Annual Data, "\n'
        '            "us_state_naics_detailedsizes_2022.xlsx (\'US & states detailed "\n'
        '            "sizes\'), national All-Industries Total row, firm-count-weighted "\n'
        '            "mean employees per firm. Brackets used: 500-749, 750-999 "\n'
        '            "employees (whole brackets, no splitting needed -- these two "\n'
        '            "real brackets exactly span 500-999)."\n'
        '        ),\n'
        '        citation_id="SUSB_2022_detailedsizes_500to999",\n'
        '    ),\n'
        '    "1000+": HeadcountMidpointEntry(\n'
        '        employees_per_firm=2027.26,\n'
        '        source=(\n'
        '            "Census SUSB 2022 Annual Data, "\n'
        '            "us_state_naics_detailedsizes_2022.xlsx (\'US & states detailed "\n'
        '            "sizes\'), national All-Industries Total row, firm-count-weighted "\n'
        '            "mean employees per firm. Brackets used: 1,000-1,499, "\n'
        '            "1,500-1,999, 2,000-2,499, 2,500-4,999 employees. The 5,000+ "\n'
        '            "open bracket was deliberately excluded (Pete\'s Option 2 call) "\n'
        '            "-- including it pulled the mean to approximately 6,230, "\n'
        '            "dominated by a small number of mega-corporations, "\n'
        '            "unrepresentative of this platform\'s realistic client base. "\n'
        '            "This value represents firms in the 1,000-4,999 range only, "\n'
        '            "not the full open-ended 1000+ population."\n'
        '        ),\n'
        '        citation_id="SUSB_2022_detailedsizes_1000to4999",\n'
        '    ),\n'
        '}\n'
        '\n'
        '\n'
        '# -- Org type scalar --------------------------------------------------------------\n',
    ),
]


def _apply(text: str, edits: list) -> tuple[str, list]:
    diffs = []
    for old, new in edits:
        count = text.count(old)
        if count == 0:
            print(f"ABORT -- anchor not found:\n{old!r}", file=sys.stderr)
            sys.exit(1)
        if count > 1:
            print(f"ABORT -- anchor not unique ({count} matches):\n{old!r}", file=sys.stderr)
            sys.exit(1)
        text = text.replace(old, new)
        diffs.append((old, new))
    return text, diffs


def _print_diff(diffs: list) -> None:
    for old, new in diffs:
        for line in old.splitlines():
            print(f"- {line}")
        for line in new.splitlines():
            print(f"+ {line}")
        print()


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = FRICTION_TAX_PY.read_text(encoding="utf-8")
    text, diffs = _apply(text, EDITS)

    print(f"Target: {FRICTION_TAX_PY.relative_to(REPO_ROOT)}")
    print("=" * 72)
    _print_diff(diffs)
    print("=" * 72)

    if args.dry_run:
        print("DRY RUN -- no file written.")
        return

    FRICTION_TAX_PY.write_text(text, encoding="utf-8")
    print(f"WROTE {FRICTION_TAX_PY.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
