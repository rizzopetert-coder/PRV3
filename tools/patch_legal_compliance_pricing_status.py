"""
PRV3 -- Add LegalPricingStatus to engine/friction_tax.py's Legal/
Compliance layer, distinguishing "real exposure, genuinely unpriced"
(Cluster 4c / Government) and "a lookup that should have succeeded
didn't" (a genuine data-integrity gap) from "not applicable at all" --
previously all three collapsed to a bare None with no signal.

- LegalPricingStatus enum (PRICED, NOT_APPLICABLE, QUALITATIVE_ONLY,
  DATA_INTEGRITY_GAP), LegalPricingResult and LegalCurveLookup
  dataclasses.
- _cluster_4_curve_for_org_type() returns LegalCurveLookup instead of
  Optional[LegalDollarCurve].
- _single_state_legal_range() renamed to _single_state_legal_pricing(),
  returns LegalPricingResult instead of Optional[tuple[float, float]].
- compute_legal_compliance_exposure()'s loop: PRICED/NOT_APPLICABLE
  behavior unchanged; QUALITATIVE_ONLY and DATA_INTEGRITY_GAP both
  collected into a new unpriced_state_ids list; DATA_INTEGRITY_GAP
  additionally logged via logging.getLogger(__name__) (new
  infrastructure for this file -- confirmed no prior logging pattern
  exists anywhere in engine/). has_unpriced_conditions/
  unpriced_state_ids added to all three of the function's return
  statements.
- 13 existing tests in tools/test_friction_tax.py updated for the two
  new return keys, including real new assertions on the Government/4c
  test (has_unpriced_conditions=True, unpriced_state_ids=["hr_capture"]).

Usage:
  python tools/patch_legal_compliance_pricing_status.py --dry-run
  python tools/patch_legal_compliance_pricing_status.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


ENGINE = "engine/friction_tax.py"
TEST_FILE = "tools/test_friction_tax.py"

# ---------------------------------------------------------------------
# engine/friction_tax.py
# ---------------------------------------------------------------------

edit(
    ENGINE,
    "from __future__ import annotations\n"
    "\n"
    "from dataclasses import dataclass\n"
    "from typing import Optional\n",
    "from __future__ import annotations\n"
    "\n"
    "import logging\n"
    "from dataclasses import dataclass\n"
    "from enum import Enum\n"
    "from typing import Optional\n"
    "\n"
    "_logger = logging.getLogger(__name__)\n",
)

edit(
    ENGINE,
    'def _legal_score_fraction(curve: LegalDollarCurve, score: int) -> float:\n'
    '    return curve.floor * (curve.ceiling / curve.floor) ** (score - 1)\n'
    '\n'
    '\n'
    '# Cluster 1 -- Individual/isolated claim (Addendum 1).',
    'def _legal_score_fraction(curve: LegalDollarCurve, score: int) -> float:\n'
    '    return curve.floor * (curve.ceiling / curve.floor) ** (score - 1)\n'
    '\n'
    '\n'
    'class LegalPricingStatus(Enum):\n'
    '    """\n'
    '    Distinguishes why a given state did or didn\'t contribute a dollar\n'
    '    range, so callers can tell "real exposure, genuinely unpriced" apart\n'
    '    from "not applicable at all" and from "a data problem" -- all three\n'
    '    previously collapsed to a bare None.\n'
    '    """\n'
    '    PRICED = "priced"\n'
    '    NOT_APPLICABLE = "not_applicable"\n'
    '    QUALITATIVE_ONLY = "qualitative_only"\n'
    '    DATA_INTEGRITY_GAP = "data_integrity_gap"\n'
    '\n'
    '\n'
    '@dataclass(frozen=True)\n'
    'class LegalPricingResult:\n'
    '    """One state\'s pricing outcome. dollar_range is populated only when\n'
    '    status is PRICED."""\n'
    '    status: LegalPricingStatus\n'
    '    dollar_range: Optional[tuple[float, float]]\n'
    '\n'
    '\n'
    '@dataclass(frozen=True)\n'
    'class LegalCurveLookup:\n'
    '    """Result of resolving a Cluster 4 sub-track curve. curve is\n'
    '    populated only when status is PRICED."""\n'
    '    curve: Optional[LegalDollarCurve]\n'
    '    status: LegalPricingStatus\n'
    '\n'
    '\n'
    '# Cluster 1 -- Individual/isolated claim (Addendum 1).',
)

edit(
    ENGINE,
    'def _cluster_4_curve_for_org_type(\n'
    '    org_type: str, org_size: str\n'
    ') -> Optional[LegalDollarCurve]:\n'
    '    """\n'
    '    Addendum 5\'s three org_type-gated sub-tracks. Returns None for\n'
    '    "Government" (4c) -- genuinely no dollar figure (thin MSPB data), not\n'
    '    a zero -- and for any unrecognized org_size in the 4b bracket table.\n'
    '    "PE or VC-backed" defaults to 4b -- the possible 4a edge case (a\n'
    '    registered investment adviser/broker-dealer) isn\'t determinable from\n'
    '    org_type alone, per Addendum 5, and isn\'t resolved here.\n'
    '    """\n'
    '    if org_type == "Publicly traded":\n'
    '        return _CLUSTER_4A_CURVE\n'
    '    if org_type == "Government":\n'
    '        return None\n'
    '    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)\n'
    '    if ceiling is None:\n'
    '        return None\n'
    '    return LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=ceiling)',
    'def _cluster_4_curve_for_org_type(\n'
    '    org_type: str, org_size: str\n'
    ') -> LegalCurveLookup:\n'
    '    """\n'
    '    Addendum 5\'s three org_type-gated sub-tracks. Status is\n'
    '    QUALITATIVE_ONLY for "Government" (4c) -- genuinely no dollar figure\n'
    '    (thin MSPB data), a real, expected outcome, not a data problem.\n'
    '    Status is DATA_INTEGRITY_GAP for any unrecognized org_size in the 4b\n'
    '    bracket table -- that should never happen against real IntakeData\n'
    '    values, so it signals something is wrong, unlike the Government\n'
    '    case. "PE or VC-backed" defaults to 4b -- the possible 4a edge case\n'
    '    (a registered investment adviser/broker-dealer) isn\'t determinable\n'
    '    from org_type alone, per Addendum 5, and isn\'t resolved here.\n'
    '    """\n'
    '    if org_type == "Publicly traded":\n'
    '        return LegalCurveLookup(curve=_CLUSTER_4A_CURVE, status=LegalPricingStatus.PRICED)\n'
    '    if org_type == "Government":\n'
    '        return LegalCurveLookup(curve=None, status=LegalPricingStatus.QUALITATIVE_ONLY)\n'
    '    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)\n'
    '    if ceiling is None:\n'
    '        return LegalCurveLookup(curve=None, status=LegalPricingStatus.DATA_INTEGRITY_GAP)\n'
    '    return LegalCurveLookup(\n'
    '        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=ceiling),\n'
    '        status=LegalPricingStatus.PRICED,\n'
    '    )',
)

edit(
    ENGINE,
    'def _single_state_legal_range(\n'
    '    state_id: str,\n'
    '    org_size: str,\n'
    '    industry: str,\n'
    '    org_type: str,\n'
    ') -> Optional[tuple[float, float]]:\n'
    '    """\n'
    '    (low, high) for one Legal-scoring state in isolation, or None if the\n'
    '    state isn\'t Legal-scoring, its "legal" score is 0 (no exposure), or\n'
    '    (Cluster 4 + org_type == "Government") -- genuinely no dollar figure.\n'
    '    """\n'
    '    cluster = LEGAL_COMPLIANCE_CLUSTER.get(state_id)\n'
    '    if cluster is None:\n'
    '        return None\n'
    '    entry = STATE_MULTIPLIERS.get(state_id)\n'
    '    if entry is None:\n'
    '        return None\n'
    '    score = entry.criteria["legal"].score\n'
    '    if score == 0:\n'
    '        return None\n'
    '\n'
    '    if cluster == 1:\n'
    '        v = _legal_score_fraction(_CLUSTER_1_CURVE, score)\n'
    '        return (v, v)\n'
    '    if cluster == 2:\n'
    '        return _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B\n'
    '    if cluster == 3:\n'
    '        affected = _cluster_3_affected_workers(org_size, industry, score)\n'
    '        return (\n'
    '            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,\n'
    '            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,\n'
    '        )\n'
    '    if cluster == 4:\n'
    '        curve = _cluster_4_curve_for_org_type(org_type, org_size)\n'
    '        if curve is None:\n'
    '            return None\n'
    '        v = _legal_score_fraction(curve, score)\n'
    '        return (v, v)\n'
    '    if cluster == 5:\n'
    '        v = _legal_score_fraction(_CLUSTER_5_CURVE, score)\n'
    '        return (v, v)\n'
    '    return None',
    'def _single_state_legal_pricing(\n'
    '    state_id: str,\n'
    '    org_size: str,\n'
    '    industry: str,\n'
    '    org_type: str,\n'
    ') -> LegalPricingResult:\n'
    '    """\n'
    '    One Legal-scoring state\'s pricing outcome in isolation. status is\n'
    '    NOT_APPLICABLE (dollar_range=None) if the state isn\'t Legal-scoring\n'
    '    at all or its "legal" score is 0 (no exposure) -- both silent,\n'
    '    unchanged from the prior bare-None behavior. For Cluster 4, status\n'
    '    is forwarded directly from _cluster_4_curve_for_org_type()\n'
    '    (QUALITATIVE_ONLY for Government, DATA_INTEGRITY_GAP for an\n'
    '    unrecognized org_size), distinguishing real-but-unpriced exposure\n'
    '    from a genuine data gap -- previously both collapsed to None here\n'
    '    too.\n'
    '    """\n'
    '    cluster = LEGAL_COMPLIANCE_CLUSTER.get(state_id)\n'
    '    if cluster is None:\n'
    '        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)\n'
    '    entry = STATE_MULTIPLIERS.get(state_id)\n'
    '    if entry is None:\n'
    '        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)\n'
    '    score = entry.criteria["legal"].score\n'
    '    if score == 0:\n'
    '        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)\n'
    '\n'
    '    if cluster == 1:\n'
    '        v = _legal_score_fraction(_CLUSTER_1_CURVE, score)\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))\n'
    '    if cluster == 2:\n'
    '        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r)\n'
    '    if cluster == 3:\n'
    '        affected = _cluster_3_affected_workers(org_size, industry, score)\n'
    '        r = (\n'
    '            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,\n'
    '            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,\n'
    '        )\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r)\n'
    '    if cluster == 4:\n'
    '        lookup = _cluster_4_curve_for_org_type(org_type, org_size)\n'
    '        if lookup.curve is None:\n'
    '            return LegalPricingResult(status=lookup.status, dollar_range=None)\n'
    '        v = _legal_score_fraction(lookup.curve, score)\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))\n'
    '    if cluster == 5:\n'
    '        v = _legal_score_fraction(_CLUSTER_5_CURVE, score)\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))\n'
    '    return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)',
)

edit(
    ENGINE,
    '    Jurisdictional multipliers (California FEHA/PAGA overrides, OSHA\n'
    '    State Plan variation, Addenda 6-9) are NOT applied here -- deferred,\n'
    '    per Addendum 9. Cluster 5 uses the statutory-max curve only (Addendum\n'
    '    10) -- actual-average deferred alongside that same paused research.\n'
    '\n'
    '    Returns {"low": float | None, "high": float | None, "currency": "USD"}.\n'
    '    low/high are None if no identified state carries real, priceable\n'
    '    Legal/Compliance exposure.\n'
    '    """\n'
    '    per_state_ranges: dict[str, tuple[float, float]] = {}\n'
    '    for sid in state_ids:\n'
    '        r = _single_state_legal_range(sid, org_size, industry, org_type)\n'
    '        if r is not None:\n'
    '            per_state_ranges[sid] = r\n'
    '\n'
    '    if not per_state_ranges:\n'
    '        return {"low": None, "high": None, "currency": "USD"}\n'
    '\n'
    '    if len(per_state_ranges) == 1:\n'
    '        low, high = next(iter(per_state_ranges.values()))\n'
    '        return {"low": round(low, 2), "high": round(high, 2), "currency": "USD"}\n'
    '\n'
    '    by_cluster: dict[int, list[tuple[float, float]]] = {}\n'
    '    for sid, r in per_state_ranges.items():\n'
    '        by_cluster.setdefault(LEGAL_COMPLIANCE_CLUSTER[sid], []).append(r)\n'
    '\n'
    '    total_low = 0.0\n'
    '    total_high = 0.0\n'
    '    for ranges in by_cluster.values():\n'
    '        ranges_sorted = sorted(ranges, key=lambda r: r[0], reverse=True)\n'
    '        total_low += sum((0.5 ** i) * low for i, (low, _high) in enumerate(ranges_sorted))\n'
    '        total_high += sum((0.5 ** i) * high for i, (_low, high) in enumerate(ranges_sorted))\n'
    '\n'
    '    return {"low": round(total_low, 2), "high": round(total_high, 2), "currency": "USD"}',
    '    Jurisdictional multipliers (California FEHA/PAGA overrides, OSHA\n'
    '    State Plan variation, Addenda 6-9) are NOT applied here -- deferred,\n'
    '    per Addendum 9. Cluster 5 uses the statutory-max curve only (Addendum\n'
    '    10) -- actual-average deferred alongside that same paused research.\n'
    '\n'
    '    NOT_APPLICABLE states (not Legal-scoring, or a "legal" score of 0)\n'
    '    are silently excluded, unchanged from before this status system\n'
    '    existed. QUALITATIVE_ONLY states (real exposure, genuinely no dollar\n'
    '    figure -- Cluster 4c/Government) and DATA_INTEGRITY_GAP states (a\n'
    '    lookup that should have succeeded didn\'t) are both collected into\n'
    '    unpriced_state_ids; a DATA_INTEGRITY_GAP additionally logs a\n'
    '    warning, since it signals a real data problem rather than an\n'
    '    intentional design outcome. The N=1 guard above triggers on exactly\n'
    '    one PRICED state -- QUALITATIVE_ONLY/DATA_INTEGRITY_GAP states never\n'
    '    enter the aggregation, regardless of how many are also present.\n'
    '\n'
    '    Returns {"low": float | None, "high": float | None, "currency": "USD",\n'
    '    "has_unpriced_conditions": bool, "unpriced_state_ids": list[str]}.\n'
    '    low/high are None if no identified state carries real, priceable\n'
    '    Legal/Compliance exposure -- has_unpriced_conditions can still be\n'
    '    True in that case if every identified Legal-scoring state was\n'
    '    QUALITATIVE_ONLY/DATA_INTEGRITY_GAP.\n'
    '    """\n'
    '    per_state_ranges: dict[str, tuple[float, float]] = {}\n'
    '    unpriced_state_ids: list[str] = []\n'
    '    for sid in state_ids:\n'
    '        result = _single_state_legal_pricing(sid, org_size, industry, org_type)\n'
    '        if result.status == LegalPricingStatus.PRICED:\n'
    '            per_state_ranges[sid] = result.dollar_range\n'
    '        elif result.status == LegalPricingStatus.QUALITATIVE_ONLY:\n'
    '            unpriced_state_ids.append(sid)\n'
    '        elif result.status == LegalPricingStatus.DATA_INTEGRITY_GAP:\n'
    '            unpriced_state_ids.append(sid)\n'
    '            _logger.warning(\n'
    '                "Legal/Compliance pricing data-integrity gap for state_id=%r "\n'
    '                "(org_size=%r, industry=%r, org_type=%r) -- expected a "\n'
    '                "priceable curve but none was found",\n'
    '                sid, org_size, industry, org_type,\n'
    '            )\n'
    '        # NOT_APPLICABLE: silently excluded, unchanged from before.\n'
    '\n'
    '    has_unpriced_conditions = bool(unpriced_state_ids)\n'
    '\n'
    '    if not per_state_ranges:\n'
    '        return {\n'
    '            "low": None,\n'
    '            "high": None,\n'
    '            "currency": "USD",\n'
    '            "has_unpriced_conditions": has_unpriced_conditions,\n'
    '            "unpriced_state_ids": unpriced_state_ids,\n'
    '        }\n'
    '\n'
    '    if len(per_state_ranges) == 1:\n'
    '        low, high = next(iter(per_state_ranges.values()))\n'
    '        return {\n'
    '            "low": round(low, 2),\n'
    '            "high": round(high, 2),\n'
    '            "currency": "USD",\n'
    '            "has_unpriced_conditions": has_unpriced_conditions,\n'
    '            "unpriced_state_ids": unpriced_state_ids,\n'
    '        }\n'
    '\n'
    '    by_cluster: dict[int, list[tuple[float, float]]] = {}\n'
    '    for sid, r in per_state_ranges.items():\n'
    '        by_cluster.setdefault(LEGAL_COMPLIANCE_CLUSTER[sid], []).append(r)\n'
    '\n'
    '    total_low = 0.0\n'
    '    total_high = 0.0\n'
    '    for ranges in by_cluster.values():\n'
    '        ranges_sorted = sorted(ranges, key=lambda r: r[0], reverse=True)\n'
    '        total_low += sum((0.5 ** i) * low for i, (low, _high) in enumerate(ranges_sorted))\n'
    '        total_high += sum((0.5 ** i) * high for i, (_low, high) in enumerate(ranges_sorted))\n'
    '\n'
    '    return {\n'
    '        "low": round(total_low, 2),\n'
    '        "high": round(total_high, 2),\n'
    '        "currency": "USD",\n'
    '        "has_unpriced_conditions": has_unpriced_conditions,\n'
    '        "unpriced_state_ids": unpriced_state_ids,\n'
    '    }',
)

# ---------------------------------------------------------------------
# tools/test_friction_tax.py -- 13 assertions updated for the 2 new keys
# ---------------------------------------------------------------------

edit(
    TEST_FILE,
    '    _r_n1 == {"low": 50_000.0, "high": 50_000.0, "currency": "USD"},',
    '    _r_n1 == {\n'
    '        "low": 50_000.0, "high": 50_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_cross == {"low": _expected_cross, "high": _expected_cross, "currency": "USD"},',
    '    _r_cross == {\n'
    '        "low": _expected_cross, "high": _expected_cross, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_decay == {"low": _expected_decay, "high": _expected_decay, "currency": "USD"},',
    '    _r_decay == {\n'
    '        "low": _expected_decay, "high": _expected_decay, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_tier_2b == {"low": 25_000.0, "high": 31_000.0, "currency": "USD"},',
    '    _r_tier_2b == {\n'
    '        "low": 25_000.0, "high": 31_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_tier_2a == {"low": 1_800.0, "high": 2_500.0, "currency": "USD"},',
    '    _r_tier_2a == {\n'
    '        "low": 1_800.0, "high": 2_500.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_cluster3 == {"low": _co_expected_low, "high": _co_expected_high, "currency": "USD"},',
    '    _r_cluster3 == {\n'
    '        "low": _co_expected_low, "high": _co_expected_high, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_4a == {"low": 33_000_000.0, "high": 33_000_000.0, "currency": "USD"},',
    '    _r_4a == {\n'
    '        "low": 33_000_000.0, "high": 33_000_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_4b == {"low": 200_000.0, "high": 200_000.0, "currency": "USD"},',
    '    _r_4b == {\n'
    '        "low": 200_000.0, "high": 200_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_4b_floor == {"low": 25_000.0, "high": 25_000.0, "currency": "USD"},',
    '    _r_4b_floor == {\n'
    '        "low": 25_000.0, "high": 25_000.0, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    "Cluster 4, org_type=\'Government\' routes to 4c: no dollar figure -- None, not zero",\n'
    '    _r_4c == {"low": None, "high": None, "currency": "USD"},',
    '    "Cluster 4, org_type=\'Government\' routes to 4c: no dollar figure -- None, not zero, "\n'
    '    "and now surfaced via has_unpriced_conditions/unpriced_state_ids rather than silently vanishing",\n'
    '    _r_4c == {\n'
    '        "low": None, "high": None, "currency": "USD",\n'
    '        "has_unpriced_conditions": True, "unpriced_state_ids": ["hr_capture"],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_never_classified == {"low": None, "high": None, "currency": "USD"},',
    '    _r_never_classified == {\n'
    '        "low": None, "high": None, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    _r_zero_score == {"low": None, "high": None, "currency": "USD"},',
    '    _r_zero_score == {\n'
    '        "low": None, "high": None, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)
edit(
    TEST_FILE,
    '    compute_legal_compliance_exposure([], "100-249", "Professional Services", "Founder-led")\n'
    '    == {"low": None, "high": None, "currency": "USD"},',
    '    compute_legal_compliance_exposure([], "100-249", "Professional Services", "Founder-led")\n'
    '    == {\n'
    '        "low": None, "high": None, "currency": "USD",\n'
    '        "has_unpriced_conditions": False, "unpriced_state_ids": [],\n'
    '    },',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
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
