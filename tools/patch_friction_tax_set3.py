"""
PRV3 -- Implement Calibration Set 3 (STATE_MULTIPLIERS) in
engine/friction_tax.py, per the Gemini-reviewed schema and Pete's 5-step
instructions.

STEP 1: Add StateCriterionScore + StateMultiplierEntry frozen dataclasses,
        placed in the "State multiplier table" section, immediately above
        STATE_MULTIPLIERS itself (mirrors where OrgTypeScalarEntry and
        HeadcountMidpointEntry each sit directly above their own table).
STEP 2: Replace the 57 x None STATE_MULTIPLIERS table with the verbatim
        contents of tools/state_multipliers_population.py (byte-level
        verified separately -- 117/117 real em-dashes, 0 mojibake).
STEP 3: Add a module-load validation block after STATE_MULTIPLIERS:
        criteria keys, raw_score sum check, per-score range, multiplier
        range.
STEP 4 (per Pete's revision): Remove _DEFAULT_MULTIPLIER entirely rather
        than setting it to None -- confirmed via repo-wide grep that its
        only live-code references are the two lines being removed here
        (engine/friction_tax.py:459 definition, :512 usage). All other
        hits are historical patch scripts already applied/committed, and
        one doc note in prompts/friction-tax-state-multiplier-
        methodology.md describing the old fallback behavior -- neither
        is live code, both left untouched. Usage site (compute_friction_tax)
        updated to the StateMultiplierEntry-aware form with a literal
        None fallback (no constant reference).
Docstring updates (module + compute_friction_tax()) confirmed by Pete --
both currently assert STATE_MULTIPLIERS is the blocking gate and
calibration_complete is "still False for every real session," which
becomes actively false the moment this patch lands. Updated to reflect
that all three calibration axes are now populated.

Does not touch tools/test_friction_tax.py (Step 5 is a separate,
subsequent action after this dry-run is confirmed). Does not delete
tools/state_multipliers_population.py (deletion happens as its own
explicit step after this patch is confirmed written).

Usage:
  python tools/patch_friction_tax_set3.py --dry-run
  python tools/patch_friction_tax_set3.py --write
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "engine" / "friction_tax.py"
POPULATION_FILE = REPO_ROOT / "tools" / "state_multipliers_population.py"


# ---------------------------------------------------------------------------
# Piece 1: module docstring update (calibration status no longer "False for
# every real session" -- all three axes populated as of this patch).
# ---------------------------------------------------------------------------

DOCSTRING_OLD = (
    "Computes an estimated financial consequence range for the identified\n"
    "organizational state cluster. PAYROLL_BASELINE_GRID is fully populated\n"
    "(payroll_floor_annual = industry_wage x headcount_midpoint for all 54\n"
    "cells, both real and sourced). STATE_MULTIPLIERS remains the sole\n"
    "CALIBRATION TARGET gate -- calibration_complete is still False for every\n"
    "real session until that research pass lands. ORG_TYPE_SCALARS and\n"
    "HEADCOUNT_MIDPOINTS were finalized 2026-08-01 -- see the source note on\n"
    "each entry.\n"
)

DOCSTRING_NEW = (
    "Computes an estimated financial consequence range for the identified\n"
    "organizational state cluster. All three calibration axes are now\n"
    "populated: PAYROLL_BASELINE_GRID (all 54 cells, industry_wage x\n"
    "headcount_midpoint), ORG_TYPE_SCALARS, and STATE_MULTIPLIERS (all 57\n"
    "states scored across the 4-criterion rubric -- see\n"
    "prompts/friction-tax-state-multiplier-methodology.md).\n"
    "calibration_complete now returns True for any real, recognized\n"
    "(org_size, industry, org_type, state_ids) combination. ORG_TYPE_SCALARS\n"
    "and HEADCOUNT_MIDPOINTS were finalized 2026-08-01, STATE_MULTIPLIERS\n"
    "2026-08-02 -- see the source note on each entry.\n"
)


# ---------------------------------------------------------------------------
# Piece 2: STATE_MULTIPLIERS section -- dataclasses + table + validation.
# Replaces the whole "State multiplier table" section header comment,
# the old plain dict type, the 57 x None entries, and _DEFAULT_MULTIPLIER.
# ---------------------------------------------------------------------------

OLD_SECTION_HEADER_AND_TABLE = None  # populated in main() after reading TARGET_FILE, anchor is exact text below

SECTION_ANCHOR_START = (
    "# -- State multiplier table -------------------------------------------------------\n"
    "# Per-state friction multiplier applied to the adjusted payroll baseline\n"
    "# (payroll basis, not revenue -- see prompts/friction-tax-unit-decision.md).\n"
    "# All values CALIBRATION TARGET -- populated from source research.\n"
    "# Keys: state_id strings matching engine/data/states.py registry (57 states).\n"
    "\n"
    "STATE_MULTIPLIERS: dict[str, Optional[float]] = {\n"
)

SECTION_ANCHOR_END = (
    "}\n"
    "\n"
    "_DEFAULT_MULTIPLIER: float = 0.0\n"
)

NEW_HEADER_AND_DATACLASSES = (
    "# -- State multiplier table -------------------------------------------------------\n"
    "# Per-state friction multiplier applied to the adjusted payroll baseline\n"
    "# (payroll basis, not revenue -- see prompts/friction-tax-unit-decision.md).\n"
    "# FINALIZED 2026-08-02 -- all 57 states scored across a 4-criterion rubric\n"
    "# (turnover/retention, productivity/output, decision-quality/velocity,\n"
    "# legal/compliance), each 0-2, min-max interpolated onto [1.0, 1.4]. See\n"
    "# prompts/friction-tax-state-multiplier-methodology.md for full methodology.\n"
    "# Keys: state_id strings matching engine/data/states.py registry (57 states).\n"
    "\n"
    "@dataclass(frozen=True)\n"
    "class StateCriterionScore:\n"
    "    \"\"\"One 0-2 criterion score and its rationale for a single state.\"\"\"\n"
    "    score: int\n"
    "    rationale: str\n"
    "\n"
    "\n"
    "@dataclass(frozen=True)\n"
    "class StateMultiplierEntry:\n"
    "    \"\"\"One state's friction multiplier and its 4-criterion scoring basis.\"\"\"\n"
    "    multiplier: float\n"
    "    raw_score: int\n"
    "    criteria: dict[str, StateCriterionScore]\n"
    "\n"
    "\n"
)

VALIDATION_BLOCK = (
    "\n"
    "_STATE_MULTIPLIER_CRITERIA_KEYS = {\"turnover\", \"productivity\", \"decision_quality\", \"legal\"}\n"
    "\n"
    "for _sid, _entry in STATE_MULTIPLIERS.items():\n"
    "    assert set(_entry.criteria.keys()) == _STATE_MULTIPLIER_CRITERIA_KEYS, (\n"
    "        f\"{_sid}: criteria keys {set(_entry.criteria.keys())} != \"\n"
    "        f\"{_STATE_MULTIPLIER_CRITERIA_KEYS}\"\n"
    "    )\n"
    "    _criteria_sum = sum(_c.score for _c in _entry.criteria.values())\n"
    "    assert _criteria_sum == _entry.raw_score, (\n"
    "        f\"{_sid}: raw_score {_entry.raw_score} != sum of criteria scores {_criteria_sum}\"\n"
    "    )\n"
    "    for _cname, _c in _entry.criteria.items():\n"
    "        assert 0 <= _c.score <= 2, f\"{_sid}.{_cname}: score {_c.score} out of [0, 2]\"\n"
    "    assert 1.0 <= _entry.multiplier <= 1.4, (\n"
    "        f\"{_sid}: multiplier {_entry.multiplier} out of [1.0, 1.4]\"\n"
    "    )\n"
    "del _sid, _entry, _criteria_sum, _cname, _c\n"
)


# ---------------------------------------------------------------------------
# Piece 3: compute_friction_tax() usage + its own docstring.
# ---------------------------------------------------------------------------

USAGE_OLD = (
    "    state_multiplier_values = [\n"
    "        STATE_MULTIPLIERS.get(sid, _DEFAULT_MULTIPLIER)\n"
    "        for sid in state_ids\n"
    "    ]\n"
)

USAGE_NEW = (
    "    state_multiplier_values = [\n"
    "        STATE_MULTIPLIERS[sid].multiplier if sid in STATE_MULTIPLIERS else None\n"
    "        for sid in state_ids\n"
    "    ]\n"
)

COMPUTE_DOCSTRING_OLD = (
    "    Returns low=None, high=None, calibration_complete=False when any\n"
    "    required value is a CALIBRATION TARGET or the (org_size, industry)\n"
    "    pair isn't a recognized grid cell. Downstream renderer treats this as\n"
    "    \"estimate pending calibration.\" As of this pass, PAYROLL_BASELINE_GRID\n"
    "    and ORG_TYPE_SCALARS are fully populated -- STATE_MULTIPLIERS is the\n"
    "    sole remaining gate.\n"
    "    \"\"\"\n"
)

COMPUTE_DOCSTRING_NEW = (
    "    Returns low=None, high=None, calibration_complete=False when any\n"
    "    required value is missing or the (org_size, industry) pair, org_type,\n"
    "    or a state_id isn't a recognized key. As of this pass, all three\n"
    "    calibration axes (PAYROLL_BASELINE_GRID, ORG_TYPE_SCALARS,\n"
    "    STATE_MULTIPLIERS) are fully populated, so calibration_complete now\n"
    "    returns True for any real, recognized combination.\n"
    "    \"\"\"\n"
)


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

    text = TARGET_FILE.read_text(encoding="utf-8")
    pop_text = POPULATION_FILE.read_text(encoding="utf-8")

    if not pop_text.startswith("STATE_MULTIPLIERS: dict[str, StateMultiplierEntry] = {"):
        print("ABORT -- population file does not start with expected header", file=sys.stderr)
        sys.exit(1)
    pop_table = pop_text.rstrip("\n") + "\n"  # exact verbatim table, ends "}\n"

    # Step: docstring update
    text = _replace_once(text, DOCSTRING_OLD, DOCSTRING_NEW, "module docstring")

    # Steps 1-4: locate the full STATE_MULTIPLIERS section (old header through
    # _DEFAULT_MULTIPLIER line) and replace it with new dataclasses + table +
    # validation block + new _DEFAULT_MULTIPLIER.
    start_idx = text.find(SECTION_ANCHOR_START)
    if start_idx == -1:
        print("ABORT -- section start anchor not found", file=sys.stderr)
        sys.exit(1)
    end_idx = text.find(SECTION_ANCHOR_END, start_idx)
    if end_idx == -1:
        print("ABORT -- section end anchor not found", file=sys.stderr)
        sys.exit(1)
    end_idx += len(SECTION_ANCHOR_END)

    old_full_section = text[start_idx:end_idx]
    new_full_section = (
        NEW_HEADER_AND_DATACLASSES
        + pop_table
        + VALIDATION_BLOCK
    )
    text = text[:start_idx] + new_full_section + text[end_idx:]

    # Step 4b: update the one live usage site
    text = _replace_once(text, USAGE_OLD, USAGE_NEW, "state_multiplier_values usage")

    # compute_friction_tax docstring update
    text = _replace_once(text, COMPUTE_DOCSTRING_OLD, COMPUTE_DOCSTRING_NEW, "compute_friction_tax docstring")

    print("=" * 78)
    print("MODULE DOCSTRING -- old vs new")
    print("=" * 78)
    print("--- OLD ---")
    print(DOCSTRING_OLD)
    print("--- NEW ---")
    print(DOCSTRING_NEW)

    print("=" * 78)
    print(f"STATE_MULTIPLIERS SECTION -- old section was {len(old_full_section)} chars, "
          f"new section is {len(new_full_section)} chars")
    print("=" * 78)
    print("--- OLD (header) ---")
    print(SECTION_ANCHOR_START.rstrip("\n"))
    print("... (57 x None entries) ...")
    print(SECTION_ANCHOR_END.rstrip("\n"))
    print()
    print("--- NEW (header + dataclasses) ---")
    print(NEW_HEADER_AND_DATACLASSES.rstrip("\n"))
    print("... (57 StateMultiplierEntry records, verbatim from "
          "tools/state_multipliers_population.py) ...")
    print("--- NEW (validation block; _DEFAULT_MULTIPLIER removed entirely) ---")
    print(VALIDATION_BLOCK.rstrip("\n"))

    print("=" * 78)
    print("USAGE SITE -- old vs new")
    print("=" * 78)
    print("--- OLD ---")
    print(USAGE_OLD)
    print("--- NEW ---")
    print(USAGE_NEW)

    print("=" * 78)
    print("compute_friction_tax() DOCSTRING -- old vs new")
    print("=" * 78)
    print("--- OLD ---")
    print(COMPUTE_DOCSTRING_OLD)
    print("--- NEW ---")
    print(COMPUTE_DOCSTRING_NEW)

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        # Sanity-compile the resulting text to catch syntax errors before write.
        try:
            compile(text, str(TARGET_FILE), "exec")
            print("Syntax check: PASSED (resulting file compiles).")
        except SyntaxError as e:
            print(f"Syntax check: FAILED -- {e}", file=sys.stderr)
            sys.exit(1)
        return

    TARGET_FILE.write_text(text, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
