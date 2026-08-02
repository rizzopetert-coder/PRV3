"""
PRV3 -- Rework tools/test_friction_tax.py for Calibration Set 3
(STATE_MULTIPLIERS is now a dict[str, StateMultiplierEntry], fully
populated for all 57 states, rather than dict[str, Optional[float]] with
all 57 values None).

Scope (per Pete's explicit instructions):
  Test 2:      invert calibration_complete assertion (False -> True on a
               real, fully unmocked call). Expected low/high computed
               from real grid + real org_type scalar + real
               STATE_MULTIPLIERS["decision_paralysis"].multiplier, not
               hardcoded, matching this file's existing convention
               (see tests 4-6's own comment).
  Tests 4-9:   convert bare-float monkey-patches
               (_ft.STATE_MULTIPLIERS[sid] = 0.1) to StateMultiplierEntry
               instances via a small _test_multiplier_entry() helper.
               CHOICE: keep monkey-patching (not switched to real
               values) -- this preserves the original test author's
               intent of decoupling formula-correctness checks from
               whatever Set 3's real calibration numbers say, so these
               tests won't need to change again if a Set 3 value is
               later corrected. Minimal diff: only the assignment lines
               change shape, hand-computed expected values (e.g. the
               literal 0.1) are untouched.
  Test 14:     invert "all None" to "all populated," add a count check
               (57) and a type/range check (StateMultiplierEntry,
               multiplier in [1.0, 1.4]).
  Test 15:     invert the 324-combination exhaustive
               calibration_complete=False assertion to
               calibration_complete=True (real data now satisfies every
               combination).
  Test 16:     REPURPOSED, not removed. The old "positive confirmation"
               test (monkey-patch one real entry, confirm the gate can
               flip True) is redundant now that True is the default
               state for any real, recognized state_id. Recommendation:
               repurpose to a genuine edge case not otherwise covered --
               state_ids containing one real, populated state ALONGSIDE
               one unrecognized state_id must still yield
               calibration_complete=False (the unrecognized id resolves
               to None, and `all(v is not None ...)` must catch it even
               when mixed with real values, not just when every id is
               unrecognized).
  Tests 1, 3, 10-13: left untouched. Confirmed no incidental impact --
               none of these five reference STATE_MULTIPLIERS' value
               shape (1/10/11/12 don't touch STATE_MULTIPLIERS at all;
               3 only checks bool(state_ids); 13 only reads
               STATE_MULTIPLIERS.keys(), never .values()).

Also adds StateCriterionScore, StateMultiplierEntry to the import list
from engine.friction_tax (needed for the new helper + test 14's type
check).

Usage:
  python tools/patch_test_friction_tax_set3.py --dry-run
  python tools/patch_test_friction_tax_set3.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "tools" / "test_friction_tax.py"


# ---------------------------------------------------------------------------
# Module docstring update (describes the 16 checks -- several assertions
# have inverted).
# ---------------------------------------------------------------------------

DOCSTRING_OLD = (
    '"""\n'
    "PRV3 Output Layer -- Friction Tax Unit Tests\n"
    "\n"
    "Verifies:\n"
    "  1. SEVERITY_SCALAR: correct values for all three tiers\n"
    "  2. compute_friction_tax: calibration_complete=False on a real, unmocked\n"
    "     call -- STATE_MULTIPLIERS is now the sole CALIBRATION TARGET gate,\n"
    "     grid + org_type are both real/populated for every valid combination\n"
    "  3. compute_friction_tax: calibration_complete=False for empty state list\n"
    "  4. compute_friction_tax: correct structure when calibrated (grid +\n"
    "     org_type are REAL, unmocked -- only STATE_MULTIPLIERS is monkey-\n"
    "     patched. Expected value is computed from the real, live\n"
    "     PAYROLL_BASELINE_GRID entry, not a hardcoded duplicate number)\n"
    "  5. compute_friction_tax: high = low * 1.4\n"
    "  6. compute_friction_tax: correct severity scalar applied\n"
    "  7. compute_friction_tax: multi-state averaging computes a real\n"
    "     arithmetic mean (grid + org_type real, only two state multipliers\n"
    "     monkey-patched)\n"
    "  8. compute_friction_tax: calibration_complete False when the grid cell\n"
    "     is forced back to None (org_type real, state_multiplier mocked)\n"
    "  9. compute_friction_tax: calibration_complete False when the org_type\n"
    "     scalar is forced back to None (grid real, state_multiplier mocked)\n"
    "  10. PAYROLL_BASELINE_GRID: exactly 54 cells, all combinations present,\n"
    "      every cell's payroll_floor_annual independently recomputed and\n"
    "      verified against industry_wage x headcount_midpoint\n"
    "  11. PAYROLL_BASELINE_GRID: all 9 industries (not just 6) carry a\n"
    "      source/citation_id\n"
    "  12. ORG_TYPE_SCALARS: exactly 6 entries matching IntakeData.org_type,\n"
    "      each with the correct finalized scalar value and a non-empty\n"
    "      source note\n"
    "  13. STATE_MULTIPLIERS: all state IDs match engine state registry\n"
    "  14. STATE_MULTIPLIERS: all values are None (CALIBRATION TARGET) at this stage\n"
    "  15. compute_friction_tax: calibration_complete is False across the\n"
    "      full real 6x9x6 (headcount x industry x org_type) combination\n"
    "      space with real, unmodified data -- exhaustive, not spot-checked\n"
    "  16. compute_friction_tax: POSITIVE confirmation -- temporarily\n"
    "      populating one real STATE_MULTIPLIERS entry (grid + org_type\n"
    "      already real, nothing else mocked) makes calibration_complete\n"
    "      genuinely flip True, proving the gate can fire and isn't\n"
    "      coincidentally or incorrectly always False\n"
    '"""\n'
)

DOCSTRING_NEW = (
    '"""\n'
    "PRV3 Output Layer -- Friction Tax Unit Tests\n"
    "\n"
    "Verifies:\n"
    "  1. SEVERITY_SCALAR: correct values for all three tiers\n"
    "  2. compute_friction_tax: calibration_complete=True on a real, fully\n"
    "     unmocked call -- all three calibration axes (grid, org_type,\n"
    "     STATE_MULTIPLIERS) are now populated. Expected low/high computed\n"
    "     from real, live values, not hardcoded\n"
    "  3. compute_friction_tax: calibration_complete=False for empty state list\n"
    "  4. compute_friction_tax: correct structure when calibrated (grid +\n"
    "     org_type are REAL, unmocked -- STATE_MULTIPLIERS is monkey-patched\n"
    "     with a synthetic StateMultiplierEntry to decouple this formula\n"
    "     check from Set 3's real calibration values. Expected value is\n"
    "     computed from the real, live PAYROLL_BASELINE_GRID entry, not a\n"
    "     hardcoded duplicate number)\n"
    "  5. compute_friction_tax: high = low * 1.4\n"
    "  6. compute_friction_tax: correct severity scalar applied\n"
    "  7. compute_friction_tax: multi-state averaging computes a real\n"
    "     arithmetic mean (grid + org_type real, only two state multipliers\n"
    "     monkey-patched)\n"
    "  8. compute_friction_tax: calibration_complete False when the grid cell\n"
    "     is forced back to None (org_type real, state_multiplier mocked)\n"
    "  9. compute_friction_tax: calibration_complete False when the org_type\n"
    "     scalar is forced back to None (grid real, state_multiplier mocked)\n"
    "  10. PAYROLL_BASELINE_GRID: exactly 54 cells, all combinations present,\n"
    "      every cell's payroll_floor_annual independently recomputed and\n"
    "      verified against industry_wage x headcount_midpoint\n"
    "  11. PAYROLL_BASELINE_GRID: all 9 industries (not just 6) carry a\n"
    "      source/citation_id\n"
    "  12. ORG_TYPE_SCALARS: exactly 6 entries matching IntakeData.org_type,\n"
    "      each with the correct finalized scalar value and a non-empty\n"
    "      source note\n"
    "  13. STATE_MULTIPLIERS: all state IDs match engine state registry\n"
    "  14. STATE_MULTIPLIERS: all 57 values are populated StateMultiplierEntry\n"
    "      records with a real multiplier in [1.0, 1.4] (Calibration Set 3 is\n"
    "      complete, no CALIBRATION TARGET placeholders remain)\n"
    "  15. compute_friction_tax: calibration_complete is True across the\n"
    "      full real 6x9x6 (headcount x industry x org_type) combination\n"
    "      space with real, unmodified data -- exhaustive, not spot-checked\n"
    "  16. compute_friction_tax: state_ids mixing one real, populated state\n"
    "      with one unrecognized state_id must still yield\n"
    "      calibration_complete=False -- repurposed from the old \"positive\n"
    "      confirmation\" test, which became redundant once True was the\n"
    "      default state for any real state_id\n"
    '"""\n'
)


# ---------------------------------------------------------------------------
# Import block -- add StateCriterionScore, StateMultiplierEntry.
# ---------------------------------------------------------------------------

IMPORT_OLD = (
    "from engine.friction_tax import (\n"
    "    SEVERITY_SCALAR,\n"
    "    STATE_MULTIPLIERS,\n"
    "    PAYROLL_BASELINE_GRID,\n"
    "    PayrollBaselineEntry,\n"
    "    ORG_TYPE_SCALARS,\n"
    "    OrgTypeScalarEntry,\n"
    "    HEADCOUNT_BUCKETS,\n"
    "    INDUSTRIES,\n"
    "    HEADCOUNT_MIDPOINTS,\n"
    "    compute_friction_tax,\n"
    ")\n"
)

IMPORT_NEW = (
    "from engine.friction_tax import (\n"
    "    SEVERITY_SCALAR,\n"
    "    STATE_MULTIPLIERS,\n"
    "    StateCriterionScore,\n"
    "    StateMultiplierEntry,\n"
    "    PAYROLL_BASELINE_GRID,\n"
    "    PayrollBaselineEntry,\n"
    "    ORG_TYPE_SCALARS,\n"
    "    OrgTypeScalarEntry,\n"
    "    HEADCOUNT_BUCKETS,\n"
    "    INDUSTRIES,\n"
    "    HEADCOUNT_MIDPOINTS,\n"
    "    compute_friction_tax,\n"
    ")\n"
)


# ---------------------------------------------------------------------------
# Helper for synthetic StateMultiplierEntry fixtures, inserted right after
# the check() helper definition.
# ---------------------------------------------------------------------------

HELPER_ANCHOR_OLD = (
    "def check(label, condition, detail=\"\"):\n"
    "    if condition:\n"
    "        PASS.append(label)\n"
    "    else:\n"
    "        FAIL.append(f\"{label}: {detail}\")\n"
)

HELPER_ANCHOR_NEW = (
    "def check(label, condition, detail=\"\"):\n"
    "    if condition:\n"
    "        PASS.append(label)\n"
    "    else:\n"
    "        FAIL.append(f\"{label}: {detail}\")\n"
    "\n"
    "\n"
    "def _test_multiplier_entry(multiplier: float) -> StateMultiplierEntry:\n"
    "    \"\"\"Synthetic StateMultiplierEntry for monkey-patching -- not real calibration data.\"\"\"\n"
    "    return StateMultiplierEntry(\n"
    "        multiplier=multiplier,\n"
    "        raw_score=0,\n"
    "        criteria={\n"
    "            \"turnover\": StateCriterionScore(score=0, rationale=\"test fixture, not real calibration data\"),\n"
    "            \"productivity\": StateCriterionScore(score=0, rationale=\"test fixture, not real calibration data\"),\n"
    "            \"decision_quality\": StateCriterionScore(score=0, rationale=\"test fixture, not real calibration data\"),\n"
    "            \"legal\": StateCriterionScore(score=0, rationale=\"test fixture, not real calibration data\"),\n"
    "        },\n"
    "    )\n"
)


# ---------------------------------------------------------------------------
# Test 2 -- invert calibration_complete assertion.
# ---------------------------------------------------------------------------

TEST2_OLD = (
    "# -- 2. calibration_complete False on a real, unmocked call --------------------\n"
    "\n"
    "result = compute_friction_tax(\n"
    "    state_ids=[\"decision_paralysis\"],\n"
    "    severity_tier=\"Entrenched\",\n"
    "    org_size=\"100-249\",\n"
    "    industry=\"Professional Services\",\n"
    "    org_type=\"Government\",\n"
    ")\n"
    "check(\n"
    "    \"calibration_complete False on a real call (STATE_MULTIPLIERS is the sole remaining gate)\",\n"
    "    result[\"calibration_complete\"] is False,\n"
    "    f\"got calibration_complete={result['calibration_complete']}\",\n"
    ")\n"
    "check(\n"
    "    \"low is None when calibration incomplete\",\n"
    "    result[\"low\"] is None,\n"
    "    f\"got low={result['low']}\",\n"
    ")\n"
    "check(\n"
    "    \"high is None when calibration incomplete\",\n"
    "    result[\"high\"] is None,\n"
    "    f\"got high={result['high']}\",\n"
    ")\n"
    "check(\n"
    "    \"currency is USD regardless of calibration\",\n"
    "    result[\"currency\"] == \"USD\",\n"
    "    f\"got currency={result['currency']}\",\n"
    ")\n"
)

TEST2_NEW = (
    "# -- 2. calibration_complete True on a real, fully unmocked call ---------------\n"
    "# All three axes (grid, org_type, STATE_MULTIPLIERS) are real -- nothing\n"
    "# monkey-patched. Expected low/high computed from real, live values, not\n"
    "# hardcoded.\n"
    "\n"
    "result = compute_friction_tax(\n"
    "    state_ids=[\"decision_paralysis\"],\n"
    "    severity_tier=\"Entrenched\",\n"
    "    org_size=\"100-249\",\n"
    "    industry=\"Professional Services\",\n"
    "    org_type=\"Government\",\n"
    ")\n"
    "_real_grid_entry_t2 = PAYROLL_BASELINE_GRID[(\"100-249\", \"Professional Services\")]\n"
    "_real_org_type_scalar_t2 = ORG_TYPE_SCALARS[\"Government\"].scalar\n"
    "_real_multiplier_t2 = STATE_MULTIPLIERS[\"decision_paralysis\"].multiplier\n"
    "_expected_low_t2 = round(\n"
    "    _real_grid_entry_t2.payroll_floor_annual * _real_org_type_scalar_t2 * _real_multiplier_t2 * 1.0,\n"
    "    2,\n"
    ")\n"
    "check(\n"
    "    \"calibration_complete True on a real, fully unmocked call (all three axes now populated)\",\n"
    "    result[\"calibration_complete\"] is True,\n"
    "    f\"got calibration_complete={result['calibration_complete']}\",\n"
    ")\n"
    "check(\n"
    "    \"low computed correctly on a real, fully unmocked call\",\n"
    "    result[\"low\"] == _expected_low_t2,\n"
    "    f\"expected {_expected_low_t2}, got low={result['low']}\",\n"
    ")\n"
    "check(\n"
    "    \"high == low * 1.4 on a real, fully unmocked call\",\n"
    "    result[\"high\"] == round(_expected_low_t2 * 1.4, 2),\n"
    "    f\"expected {round(_expected_low_t2 * 1.4, 2)}, got high={result['high']}\",\n"
    ")\n"
    "check(\n"
    "    \"currency is USD\",\n"
    "    result[\"currency\"] == \"USD\",\n"
    "    f\"got currency={result['currency']}\",\n"
    ")\n"
)


# ---------------------------------------------------------------------------
# Tests 4-9 -- wrap bare-float monkey-patches in _test_multiplier_entry().
# Four distinct assignment sites across tests 4-9.
# ---------------------------------------------------------------------------

ASSIGN_DP_01_OLD = '_ft.STATE_MULTIPLIERS["decision_paralysis"] = 0.1\n'
ASSIGN_DP_01_NEW = '_ft.STATE_MULTIPLIERS["decision_paralysis"] = _test_multiplier_entry(0.1)\n'

ASSIGN_EXPOSED_03_OLD = '_ft.STATE_MULTIPLIERS["the_exposed"] = 0.3\n'
ASSIGN_EXPOSED_03_NEW = '_ft.STATE_MULTIPLIERS["the_exposed"] = _test_multiplier_entry(0.3)\n'


def _replace_all_occurrences(text: str, old: str, new: str, label: str, expected_count: int) -> str:
    count = text.count(old)
    if count != expected_count:
        print(
            f"ABORT -- {label}: expected {expected_count} occurrence(s), found {count}",
            file=sys.stderr,
        )
        sys.exit(1)
    return text.replace(old, new)


# ---------------------------------------------------------------------------
# Test 14 -- invert "all None" to "all populated."
# ---------------------------------------------------------------------------

TEST14_OLD = (
    "# -- 14. All multipliers are None (CALIBRATION TARGET) --------------------------\n"
    "\n"
    "non_none = {k: v for k, v in STATE_MULTIPLIERS.items() if v is not None}\n"
    "check(\n"
    "    \"All STATE_MULTIPLIERS are None (CALIBRATION TARGET)\",\n"
    "    len(non_none) == 0,\n"
    "    f\"non-None values: {non_none}\",\n"
    ")\n"
)

TEST14_NEW = (
    "# -- 14. All 57 multipliers are populated (Calibration Set 3 complete) ---------\n"
    "\n"
    "non_populated = {k: v for k, v in STATE_MULTIPLIERS.items() if v is None}\n"
    "check(\n"
    "    \"All STATE_MULTIPLIERS are populated (no CALIBRATION TARGET placeholders remain)\",\n"
    "    len(non_populated) == 0,\n"
    "    f\"still-None entries: {non_populated}\",\n"
    ")\n"
    "check(\n"
    "    \"STATE_MULTIPLIERS has exactly 57 entries\",\n"
    "    len(STATE_MULTIPLIERS) == 57,\n"
    "    f\"got {len(STATE_MULTIPLIERS)}\",\n"
    ")\n"
    "check(\n"
    "    \"Every STATE_MULTIPLIERS value is a StateMultiplierEntry with a real multiplier in [1.0, 1.4]\",\n"
    "    all(\n"
    "        isinstance(v, StateMultiplierEntry) and v.multiplier is not None and 1.0 <= v.multiplier <= 1.4\n"
    "        for v in STATE_MULTIPLIERS.values()\n"
    "    ),\n"
    "    \"found a non-StateMultiplierEntry value or an out-of-range multiplier\",\n"
    ")\n"
)


# ---------------------------------------------------------------------------
# Test 15 -- invert exhaustive False assertion to True.
# ---------------------------------------------------------------------------

TEST15_OLD = (
    "# -- 15. calibration_complete False across the full real 6x9x6 space -----------\n"
    "# Exhaustive, not spot-checked. Grid and org_type are now real/populated\n"
    "# for every combination -- this confirms STATE_MULTIPLIERS being fully\n"
    "# None is still sufficient, alone, to keep calibration_complete False\n"
    "# everywhere real data is used.\n"
    "\n"
    "_any_unexpectedly_complete = []\n"
    "for hc in HEADCOUNT_BUCKETS:\n"
    "    for ind in INDUSTRIES:\n"
    "        for ot in ORG_TYPE_SCALARS.keys():\n"
    "            r = compute_friction_tax(\n"
    "                state_ids=[\"decision_paralysis\"],\n"
    "                severity_tier=\"Entrenched\",\n"
    "                org_size=hc,\n"
    "                industry=ind,\n"
    "                org_type=ot,\n"
    "            )\n"
    "            if r[\"calibration_complete\"] is not False:\n"
    "                _any_unexpectedly_complete.append((hc, ind, ot))\n"
    "\n"
    "check(\n"
    "    \"calibration_complete is False for all 324 real (headcount, industry, org_type) combinations\",\n"
    "    len(_any_unexpectedly_complete) == 0,\n"
    "    f\"unexpectedly complete: {_any_unexpectedly_complete}\",\n"
    ")\n"
)

TEST15_NEW = (
    "# -- 15. calibration_complete True across the full real 6x9x6 space ------------\n"
    "# Exhaustive, not spot-checked. All three calibration axes are now real\n"
    "# and populated for every combination -- confirms calibration_complete\n"
    "# genuinely returns True everywhere real data is used, not just in the\n"
    "# single spot-checked case from test 2.\n"
    "\n"
    "_any_unexpectedly_incomplete = []\n"
    "for hc in HEADCOUNT_BUCKETS:\n"
    "    for ind in INDUSTRIES:\n"
    "        for ot in ORG_TYPE_SCALARS.keys():\n"
    "            r = compute_friction_tax(\n"
    "                state_ids=[\"decision_paralysis\"],\n"
    "                severity_tier=\"Entrenched\",\n"
    "                org_size=hc,\n"
    "                industry=ind,\n"
    "                org_type=ot,\n"
    "            )\n"
    "            if r[\"calibration_complete\"] is not True:\n"
    "                _any_unexpectedly_incomplete.append((hc, ind, ot))\n"
    "\n"
    "check(\n"
    "    \"calibration_complete is True for all 324 real (headcount, industry, org_type) combinations\",\n"
    "    len(_any_unexpectedly_incomplete) == 0,\n"
    "    f\"unexpectedly incomplete: {_any_unexpectedly_incomplete}\",\n"
    ")\n"
)


# ---------------------------------------------------------------------------
# Test 16 -- repurposed from "positive confirmation" to a mixed
# known/unknown state_ids edge case.
# ---------------------------------------------------------------------------

TEST16_OLD = (
    "# -- 16. POSITIVE confirmation: the gate genuinely can flip True ---------------\n"
    "# Grid and org_type are real and untouched here -- only one real\n"
    "# STATE_MULTIPLIERS entry is temporarily populated. If this doesn't flip\n"
    "# calibration_complete to True, the gate itself is broken, not just\n"
    "# \"correctly incomplete.\"\n"
    "\n"
    "_original_multiplier_positive = STATE_MULTIPLIERS.get(\"decision_paralysis\")\n"
    "_ft.STATE_MULTIPLIERS[\"decision_paralysis\"] = 0.2\n"
    "result_positive = compute_friction_tax(\n"
    "    state_ids=[\"decision_paralysis\"],\n"
    "    severity_tier=\"Entrenched\",\n"
    "    org_size=\"500-999\",\n"
    "    industry=\"Technology\",\n"
    "    org_type=\"Nonprofit\",\n"
    ")\n"
    "check(\n"
    "    \"calibration_complete genuinely flips True with real grid + org_type + one real state_multiplier\",\n"
    "    result_positive[\"calibration_complete\"] is True,\n"
    "    f\"got {result_positive['calibration_complete']} -- gate may be broken, not just incomplete\",\n"
    ")\n"
    "check(\n"
    "    \"positive-confirmation result produces a real, non-None low/high\",\n"
    "    result_positive[\"low\"] is not None and result_positive[\"high\"] is not None,\n"
    "    f\"got low={result_positive['low']}, high={result_positive['high']}\",\n"
    ")\n"
    "_ft.STATE_MULTIPLIERS[\"decision_paralysis\"] = _original_multiplier_positive\n"
)

TEST16_NEW = (
    "# -- 16. Mixed known/unknown state_ids -- calibration_complete stays False -----\n"
    "# Repurposed from the old \"positive confirmation\" test, which became\n"
    "# redundant once calibration_complete=True was the default state for any\n"
    "# real state_id (see test 2). This covers a genuine edge case not\n"
    "# otherwise tested: a state_ids list mixing one real, populated state\n"
    "# with one unrecognized state_id must still yield\n"
    "# calibration_complete=False -- the unrecognized id resolves to None and\n"
    "# the all(v is not None ...) check must catch it even when mixed with\n"
    "# real values, not just when every id in the list is unrecognized.\n"
    "\n"
    "result_mixed = compute_friction_tax(\n"
    "    state_ids=[\"decision_paralysis\", \"not_a_real_state\"],\n"
    "    severity_tier=\"Entrenched\",\n"
    "    org_size=\"500-999\",\n"
    "    industry=\"Technology\",\n"
    "    org_type=\"Nonprofit\",\n"
    ")\n"
    "check(\n"
    "    \"calibration_complete False when state_ids mixes one real state with one unrecognized state\",\n"
    "    result_mixed[\"calibration_complete\"] is False,\n"
    "    f\"got {result_mixed['calibration_complete']}\",\n"
    ")\n"
    "check(\n"
    "    \"low/high are None when any state_id in the list is unrecognized\",\n"
    "    result_mixed[\"low\"] is None and result_mixed[\"high\"] is None,\n"
    "    f\"got low={result_mixed['low']}, high={result_mixed['high']}\",\n"
    ")\n"
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


def build_new_text(text: str) -> str:
    text = _replace_once(text, DOCSTRING_OLD, DOCSTRING_NEW, "module docstring")
    text = _replace_once(text, IMPORT_OLD, IMPORT_NEW, "import block")
    text = _replace_once(text, HELPER_ANCHOR_OLD, HELPER_ANCHOR_NEW, "check() helper / new fixture helper")
    text = _replace_once(text, TEST2_OLD, TEST2_NEW, "test 2")
    # decision_paralysis is monkey-patched to 0.1 at 2 sites (test 4-6 setup,
    # test 8 setup -- test 9 reuses test 8's still-active monkey-patch and
    # doesn't reassign it)
    text = _replace_all_occurrences(text, ASSIGN_DP_01_OLD, ASSIGN_DP_01_NEW, "decision_paralysis = 0.1 (tests 4-6, 8)", 2)
    # the_exposed is monkey-patched to 0.3 at 1 site (test 7)
    text = _replace_all_occurrences(text, ASSIGN_EXPOSED_03_OLD, ASSIGN_EXPOSED_03_NEW, "the_exposed = 0.3 (test 7)", 1)
    text = _replace_once(text, TEST14_OLD, TEST14_NEW, "test 14")
    text = _replace_once(text, TEST15_OLD, TEST15_NEW, "test 15")
    text = _replace_once(text, TEST16_OLD, TEST16_NEW, "test 16")
    return text


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Write the resulting text to this path instead of TARGET_FILE (for dry-run test execution).",
    )
    args = parser.parse_args()

    text = TARGET_FILE.read_text(encoding="utf-8")
    new_text = build_new_text(text)

    print("=" * 78)
    print("1. MODULE DOCSTRING")
    print("=" * 78)
    print("--- summary: describes inverted assertions for tests 2, 14, 15, 16 ---")

    print("=" * 78)
    print("2. IMPORT BLOCK")
    print("=" * 78)
    print("--- OLD ---")
    print(IMPORT_OLD)
    print("--- NEW ---")
    print(IMPORT_NEW)

    print("=" * 78)
    print("3. NEW HELPER: _test_multiplier_entry()")
    print("=" * 78)
    print(HELPER_ANCHOR_NEW)

    print("=" * 78)
    print("4. TEST 2 -- inverted (False -> True on real unmocked call)")
    print("=" * 78)
    print("--- OLD ---")
    print(TEST2_OLD)
    print("--- NEW ---")
    print(TEST2_NEW)

    print("=" * 78)
    print("5. TESTS 4-9 -- monkey-patch assignments wrapped in _test_multiplier_entry()")
    print("=" * 78)
    print(f"  {ASSIGN_DP_01_OLD.strip()}  ->  {ASSIGN_DP_01_NEW.strip()}   (2 occurrences: tests 4-6, 8)")
    print(f"  {ASSIGN_EXPOSED_03_OLD.strip()}  ->  {ASSIGN_EXPOSED_03_NEW.strip()}   (1 occurrence: test 7)")

    print("=" * 78)
    print("6. TEST 14 -- inverted (all None -> all populated + count + type/range check)")
    print("=" * 78)
    print("--- OLD ---")
    print(TEST14_OLD)
    print("--- NEW ---")
    print(TEST14_NEW)

    print("=" * 78)
    print("7. TEST 15 -- inverted (324x False -> 324x True)")
    print("=" * 78)
    print("--- OLD ---")
    print(TEST15_OLD)
    print("--- NEW ---")
    print(TEST15_NEW)

    print("=" * 78)
    print("8. TEST 16 -- repurposed (positive confirmation -> mixed known/unknown state_ids)")
    print("=" * 78)
    print("--- OLD ---")
    print(TEST16_OLD)
    print("--- NEW ---")
    print(TEST16_NEW)

    try:
        compile(new_text, str(TARGET_FILE), "exec")
        print("\nSyntax check: PASSED (resulting file compiles).")
    except SyntaxError as e:
        print(f"\nSyntax check: FAILED -- {e}", file=sys.stderr)
        sys.exit(1)

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(new_text, encoding="utf-8")
        print(f"\nWrote dry-run content to {out_path} (real file untouched).")
        return

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TARGET_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
