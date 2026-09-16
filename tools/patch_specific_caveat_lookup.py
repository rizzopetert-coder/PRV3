"""
PRV3 -- Per-state specific caveats for the flat_cap/state_specific_tiers
is_floor scoping follow-up (Priority Queue item 9's deferred is_floor
piece). Design confirmed this session (Gemini-reviewed, two flagged
claims independently re-verified against live source before being
treated as confirmed -- see this session's own verification report).

Adds a new identifier-only field, specific_caveat_jurisdiction, to
LegalPricingResult and LegalCurveLookup -- the SPECIFIC jurisdiction
(a 2-letter code, or None) that drove a state_specific_flat or
state_specific_tiers result, wherever one exists. friction_tax.py never
carries prose -- it reports only an identifier, matching every existing
field on these dataclasses (bool/enum/number, never a display string).
contract.py owns the actual 7 caveat sentences (_SPECIFIC_CAVEAT_TEXT),
matching that file's own existing LEGAL_TAIL_RISK_CAVEAT_TEXT precedent,
and resolves the identifier to text (or None, for any of the other 25
state_specific_flat/tiers jurisdictions with no specific caveat written)
via a single dict lookup -- no second "which states have a caveat" list
duplicated in friction_tax.py.

Two tie-break rules, deliberately NOT homogenized (verified this
session against the existing test suite before writing this patch):
- _resolve_flat_cap(): MAXIMUM VALUE wins, order-independent --
  pre-existing, already-shipped behavior for FL/ID/KS/VA, unchanged
  here. Its return type changes from Optional[float] to
  Optional[tuple[float, str]] -- safe because it has exactly 2 call
  sites (both edited by this same patch) and zero direct unit tests
  (confirmed by grep before writing this patch).
- _state_specific_tiers_driver() (new): FIRST-ENCOUNTERED-IN-INPUT-
  LIST wins, proven via the existing _oh_drives_tiers_result(['OH',
  'TX']) vs (['TX','OH']) test pair (tools/test_friction_tax.py:1896-
  1907) -- this new helper copies that exact loop shape rather than
  reinventing it, so it inherits the same proven tie-break.
  Deliberately not consolidated with _oh_drives_tiers_result()/
  _co_drives_federal_tier_deferral() -- those answer a narrower yes/no
  question about one specific state; this one needs the actual
  winning jurisdiction id.

Verified this session before writing this patch: at most one specific
caveat can ever apply per session, since jurisdictions is a single
session-level parameter (not per-state) feeding these pure-function
resolvers identically for every contributing Legal-scoring taxonomy
state in compute_legal_compliance_exposure()'s loop -- confirmed by
reading that loop directly. compute_legal_compliance_exposure()'s own
new session-level field is therefore a "first non-None wins"
assignment, not a real conflict to resolve.

Usage:
  python tools/patch_specific_caveat_lookup.py --dry-run
  python tools/patch_specific_caveat_lookup.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


F = "engine/friction_tax.py"
C = "engine/contract.py"

# -- 1. LegalPricingResult: add specific_caveat_jurisdiction field --------

edit(
    F,
    '    UI-facing framing is explicitly out of scope for this build."""\n'
    '    status: LegalPricingStatus\n'
    '    dollar_range: Optional[tuple[float, float]]\n'
    '    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]\n'
    '    partial_state_flag: bool\n'
    '    is_floor: bool = False\n'
    '    may_overstate_for_uncollected_net_worth: bool = False\n',
    '    UI-facing framing is explicitly out of scope for this build.\n\n'
    '    specific_caveat_jurisdiction (is_floor scoping follow-up, this\n'
    '    session) is the 2-letter jurisdiction id that drove a\n'
    '    state_specific_flat or state_specific_tiers result, when one of\n'
    '    the two has a specific, verified caveat sentence written for it\n'
    '    (contract.py\'s _SPECIFIC_CAVEAT_TEXT) -- None otherwise, including\n'
    '    for jurisdictions in those two categories with no specific caveat\n'
    '    written. An identifier only, not prose -- same convention as every\n'
    '    other field here; the actual sentences live in contract.py.\n'
    '    """\n'
    '    status: LegalPricingStatus\n'
    '    dollar_range: Optional[tuple[float, float]]\n'
    '    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]\n'
    '    partial_state_flag: bool\n'
    '    is_floor: bool = False\n'
    '    may_overstate_for_uncollected_net_worth: bool = False\n'
    '    specific_caveat_jurisdiction: Optional[str] = None\n',
)

# -- 2. LegalCurveLookup: add specific_caveat_jurisdiction field ----------

edit(
    F,
    '    small-employer branch specifically."""\n'
    '    curve: Optional[LegalDollarCurve]\n'
    '    status: LegalPricingStatus\n'
    '    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]\n'
    '    partial_state_flag: bool\n'
    '    is_floor: bool = False\n'
    '    may_overstate_for_uncollected_net_worth: bool = False\n',
    '    small-employer branch specifically. specific_caveat_jurisdiction\n'
    '    carries the same meaning as LegalPricingResult\'s own field of that\n'
    '    name -- forwarded the same way, into the Cluster 4 dispatch\'s\n'
    '    final LegalPricingResult."""\n'
    '    curve: Optional[LegalDollarCurve]\n'
    '    status: LegalPricingStatus\n'
    '    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]\n'
    '    partial_state_flag: bool\n'
    '    is_floor: bool = False\n'
    '    may_overstate_for_uncollected_net_worth: bool = False\n'
    '    specific_caveat_jurisdiction: Optional[str] = None\n',
)

# -- 3. _resolve_flat_cap(): return (value, winning jid), tie-break unchanged --

edit(
    F,
    'def _resolve_flat_cap(jurisdictions: list[str]) -> Optional[float]:\n'
    '    """\n'
    '    Maximum flat_cap among CONFIRMED state_specific_flat jurisdictions\n'
    '    in the input -- extends resolve_damages_treatment()\'s own\n'
    '    highest-exposure-wins principle down to the actual dollar figure,\n'
    '    needed because that function returns a category string, not a\n'
    '    specific state; with more than one state_specific_flat jurisdiction\n'
    '    selected, something has to pick which state\'s own flat_cap governs.\n'
    '    None if no CONFIRMED state_specific_flat jurisdiction is present in\n'
    '    the input, or if one is present but its flat_cap is unpopulated (a\n'
    '    data gap, not expected once all 4 real flat_cap states are\n'
    '    populated).\n'
    '    """\n'
    '    best: Optional[float] = None\n'
    '    for jid in jurisdictions:\n'
    '        entry = STATE_COVERAGE_THRESHOLDS.get(jid)\n'
    '        if entry is None or entry.confidence != "CONFIRMED":\n'
    '            continue\n'
    '        if entry.damages_cap_treatment != "state_specific_flat":\n'
    '            continue\n'
    '        if entry.flat_cap is None:\n'
    '            continue\n'
    '        if best is None or entry.flat_cap > best:\n'
    '            best = entry.flat_cap\n'
    '    return best\n',
    'def _resolve_flat_cap(jurisdictions: list[str]) -> Optional[tuple[float, str]]:\n'
    '    """\n'
    '    (value, winning jurisdiction id) for the MAXIMUM flat_cap among\n'
    '    CONFIRMED state_specific_flat jurisdictions in the input -- extends\n'
    '    resolve_damages_treatment()\'s own highest-exposure-wins principle\n'
    '    down to the actual dollar figure, needed because that function\n'
    '    returns a category string, not a specific state; with more than\n'
    '    one state_specific_flat jurisdiction selected, something has to\n'
    '    pick which state\'s own flat_cap governs.\n\n'
    '    Tie-break is MAXIMUM VALUE, not input order -- pre-existing,\n'
    '    already-shipped behavior (Phase 1 item 4), unchanged by adding the\n'
    '    jurisdiction id to the return value; the returned jid is whichever\n'
    '    entry actually produced the returned max value, tracked in the\n'
    '    same pass, not a separately re-derived identity. Deliberately\n'
    '    different from _state_specific_tiers_driver()\'s first-encountered-\n'
    '    wins rule below -- the two are governed by different, independently\n'
    '    proven rules and must not be homogenized.\n\n'
    '    None if no CONFIRMED state_specific_flat jurisdiction is present in\n'
    '    the input, or if one is present but its flat_cap is unpopulated (a\n'
    '    data gap, not expected once all 4 real flat_cap states are\n'
    '    populated).\n'
    '    """\n'
    '    best: Optional[float] = None\n'
    '    best_jid: Optional[str] = None\n'
    '    for jid in jurisdictions:\n'
    '        entry = STATE_COVERAGE_THRESHOLDS.get(jid)\n'
    '        if entry is None or entry.confidence != "CONFIRMED":\n'
    '            continue\n'
    '        if entry.damages_cap_treatment != "state_specific_flat":\n'
    '            continue\n'
    '        if entry.flat_cap is None:\n'
    '            continue\n'
    '        if best is None or entry.flat_cap > best:\n'
    '            best = entry.flat_cap\n'
    '            best_jid = jid\n'
    '    return (best, best_jid) if best is not None else None\n',
)

# -- 4. New _state_specific_tiers_driver() helper, standalone -------------

edit(
    F,
    '            best_rank = rank\n'
    '            best_jid = jid\n'
    '    return best_jid == "OH"\n'
    '\n'
    '\n'
    '# -- Jurisdiction litigation-risk multiplier (Priority Queue item 9, this\n',
    '            best_rank = rank\n'
    '            best_jid = jid\n'
    '    return best_jid == "OH"\n'
    '\n'
    '\n'
    'def _state_specific_tiers_driver(jurisdictions: list[str]) -> Optional[str]:\n'
    '    """\n'
    '    The SPECIFIC jurisdiction resolve_damages_treatment() would resolve\n'
    '    a state_specific_tiers result from, or None if no state_specific_\n'
    '    tiers jurisdiction wins (whether none is present, or a higher-\n'
    '    ranked category -- uncapped or state_specific_flat -- wins\n'
    '    instead). Same re-derivation of resolve_damages_treatment()\'s own\n'
    '    priority loop as _oh_drives_tiers_result()/\n'
    '    _co_drives_federal_tier_deferral() above, kept standalone rather\n'
    '    than consolidated with either -- those two answer a narrower\n'
    '    yes/no question about one specific state; this one needs the\n'
    '    actual winning jurisdiction id, for the AR/MD/TN per-state caveat\n'
    '    lookup (is_floor scoping follow-up, this session).\n\n'
    '    Tie-break is FIRST-ENCOUNTERED-IN-INPUT-LIST-WINS, identical to\n'
    '    the loop this re-derives -- proven directly by the existing\n'
    '    _oh_drives_tiers_result([\'OH\',\'TX\']) vs ([\'TX\',\'OH\']) test pair\n'
    '    (tools/test_friction_tax.py), which this function\'s own loop shape\n'
    '    reproduces exactly, not reinvented. Deliberately NOT the same\n'
    '    tie-break as _resolve_flat_cap() (maximum value, order-\n'
    '    independent) -- the two are governed by different, independently\n'
    '    proven rules and must not be homogenized.\n'
    '    """\n'
    '    best_jid: Optional[str] = None\n'
    '    best_rank = -1\n'
    '    for jid in jurisdictions:\n'
    '        entry = STATE_COVERAGE_THRESHOLDS.get(jid)\n'
    '        if entry is None or entry.confidence != "CONFIRMED":\n'
    '            continue\n'
    '        rank = _DAMAGES_TREATMENT_PRIORITY.get(entry.damages_cap_treatment, -1)\n'
    '        if rank > best_rank:\n'
    '            best_rank = rank\n'
    '            best_jid = jid\n'
    '    if best_jid is None:\n'
    '        return None\n'
    '    winning_entry = STATE_COVERAGE_THRESHOLDS[best_jid]\n'
    '    return best_jid if winning_entry.damages_cap_treatment == "state_specific_tiers" else None\n'
    '\n'
    '\n'
    '# -- Jurisdiction litigation-risk multiplier (Priority Queue item 9, this\n',
)

# -- 5. Cluster 4b call site: unpack tuple, resolve tiers driver, thread field --

edit(
    F,
    '    flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None\n'
    '    final_ceiling = ceiling if flat_cap is None else min(ceiling, flat_cap)\n'
    '    is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None\n'
    '    return LegalCurveLookup(\n'
    '        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=final_ceiling),\n'
    '        status=LegalPricingStatus.PRICED,\n'
    '        coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,\n'
    '        is_floor=is_floor,\n'
    '    )\n',
    '    flat_cap_result = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None\n'
    '    flat_cap = flat_cap_result[0] if flat_cap_result is not None else None\n'
    '    final_ceiling = ceiling if flat_cap is None else min(ceiling, flat_cap)\n'
    '    is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None\n'
    '    specific_caveat_jurisdiction = flat_cap_result[1] if flat_cap_result is not None else None\n'
    '    if specific_caveat_jurisdiction is None and treatment == "state_specific_tiers":\n'
    '        specific_caveat_jurisdiction = _state_specific_tiers_driver(jurisdictions)\n'
    '    return LegalCurveLookup(\n'
    '        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=final_ceiling),\n'
    '        status=LegalPricingStatus.PRICED,\n'
    '        coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,\n'
    '        is_floor=is_floor,\n'
    '        specific_caveat_jurisdiction=specific_caveat_jurisdiction,\n'
    '    )\n',
)

# -- 6. Cluster 1 call site: unpack tuple, resolve tiers driver, thread field --

edit(
    F,
    '        flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None\n'
    '        curve = _CLUSTER_1_CURVE if flat_cap is None else LegalDollarCurve(\n'
    '            floor=_CLUSTER_1_CURVE.floor, ceiling=min(_CLUSTER_1_CURVE.ceiling, flat_cap),\n'
    '        )\n'
    '        v = _legal_score_fraction(curve, score)\n'
    '        is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),\n'
    '            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,\n'
    '            is_floor=is_floor)\n',
    '        flat_cap_result = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None\n'
    '        flat_cap = flat_cap_result[0] if flat_cap_result is not None else None\n'
    '        curve = _CLUSTER_1_CURVE if flat_cap is None else LegalDollarCurve(\n'
    '            floor=_CLUSTER_1_CURVE.floor, ceiling=min(_CLUSTER_1_CURVE.ceiling, flat_cap),\n'
    '        )\n'
    '        v = _legal_score_fraction(curve, score)\n'
    '        is_floor = treatment in ("uncapped", "state_specific_tiers") or flat_cap is not None\n'
    '        specific_caveat_jurisdiction = flat_cap_result[1] if flat_cap_result is not None else None\n'
    '        if specific_caveat_jurisdiction is None and treatment == "state_specific_tiers":\n'
    '            specific_caveat_jurisdiction = _state_specific_tiers_driver(jurisdictions)\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),\n'
    '            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,\n'
    '            is_floor=is_floor, specific_caveat_jurisdiction=specific_caveat_jurisdiction)\n',
)

# -- 7. Cluster 4 dispatch: forward specific_caveat_jurisdiction ----------

edit(
    F,
    '        v = _legal_score_fraction(lookup.curve, score)\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),\n'
    '            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag,\n'
    '            is_floor=lookup.is_floor,\n'
    '            may_overstate_for_uncollected_net_worth=lookup.may_overstate_for_uncollected_net_worth)\n',
    '        v = _legal_score_fraction(lookup.curve, score)\n'
    '        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),\n'
    '            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag,\n'
    '            is_floor=lookup.is_floor,\n'
    '            may_overstate_for_uncollected_net_worth=lookup.may_overstate_for_uncollected_net_worth,\n'
    '            specific_caveat_jurisdiction=lookup.specific_caveat_jurisdiction)\n',
)

# -- 8. compute_legal_compliance_exposure(): session-level aggregation ----

edit(
    F,
    '    has_partial_jurisdictions = False\n'
    '    has_uncollected_net_worth_caveat = False\n'
    '    for sid in state_ids:\n'
    '        result = _single_state_legal_pricing(\n'
    '            sid, org_size, industry, org_type, headcount, jurisdictions\n'
    '        )\n'
    '        if result.status == LegalPricingStatus.PRICED:\n'
    '            per_state_ranges[sid] = result.dollar_range\n'
    '            if result.may_overstate_for_uncollected_net_worth:\n'
    '                has_uncollected_net_worth_caveat = True\n',
    '    has_partial_jurisdictions = False\n'
    '    has_uncollected_net_worth_caveat = False\n'
    '    specific_caveat_jurisdiction: Optional[str] = None\n'
    '    for sid in state_ids:\n'
    '        result = _single_state_legal_pricing(\n'
    '            sid, org_size, industry, org_type, headcount, jurisdictions\n'
    '        )\n'
    '        if result.status == LegalPricingStatus.PRICED:\n'
    '            per_state_ranges[sid] = result.dollar_range\n'
    '            if result.may_overstate_for_uncollected_net_worth:\n'
    '                has_uncollected_net_worth_caveat = True\n'
    '            if specific_caveat_jurisdiction is None and result.specific_caveat_jurisdiction is not None:\n'
    '                # First non-None wins -- not a real ambiguity: jurisdictions\n'
    '                # is a single session-level input feeding the same pure\n'
    '                # resolvers for every contributing state, so any two\n'
    '                # non-None values here are guaranteed identical (verified\n'
    '                # this session before this patch was written).\n'
    '                specific_caveat_jurisdiction = result.specific_caveat_jurisdiction\n',
)

edit(
    F,
    '            "coverage_basis": coverage_basis,\n'
    '            "has_partial_jurisdictions": has_partial_jurisdictions,\n'
    '            "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,\n'
    '        }\n'
    '\n'
    '    if len(per_state_ranges) == 1:\n',
    '            "coverage_basis": coverage_basis,\n'
    '            "has_partial_jurisdictions": has_partial_jurisdictions,\n'
    '            "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,\n'
    '            "specific_caveat_jurisdiction": specific_caveat_jurisdiction,\n'
    '        }\n'
    '\n'
    '    if len(per_state_ranges) == 1:\n',
)

edit(
    F,
    '            "coverage_basis": coverage_basis,\n'
    '            "has_partial_jurisdictions": has_partial_jurisdictions,\n'
    '            "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,\n'
    '        }\n'
    '\n'
    '    by_cluster: dict[int, list[tuple[float, float]]] = {}\n',
    '            "coverage_basis": coverage_basis,\n'
    '            "has_partial_jurisdictions": has_partial_jurisdictions,\n'
    '            "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,\n'
    '            "specific_caveat_jurisdiction": specific_caveat_jurisdiction,\n'
    '        }\n'
    '\n'
    '    by_cluster: dict[int, list[tuple[float, float]]] = {}\n',
)

edit(
    F,
    '        "coverage_basis": coverage_basis,\n'
    '        "has_partial_jurisdictions": has_partial_jurisdictions,\n'
    '        "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,\n'
    '    }\n',
    '        "coverage_basis": coverage_basis,\n'
    '        "has_partial_jurisdictions": has_partial_jurisdictions,\n'
    '        "has_uncollected_net_worth_caveat": has_uncollected_net_worth_caveat,\n'
    '        "specific_caveat_jurisdiction": specific_caveat_jurisdiction,\n'
    '    }\n',
)

# -- 9. contract.py: _SPECIFIC_CAVEAT_TEXT dict + resolution into the output dict --

edit(
    C,
    '    "of being challenged. If any of these conditions concern you, this is worth "\n'
    '    "a conversation with employment counsel, not just this number."\n'
    ')\n',
    '    "of being challenged. If any of these conditions concern you, this is worth "\n'
    '    "a conversation with employment counsel, not just this number."\n'
    ')\n'
    '\n'
    '# is_floor scoping follow-up, this session -- 7 verified per-state\n'
    '# caveats for the flat_cap component-vs-total mismatch (FL/ID/KS/VA)\n'
    '# and the state_specific_tiers unmodeled-carve-out cases (AR/MD/TN).\n'
    '# Keyed by the jurisdiction id LegalPricingResult/LegalCurveLookup\'s\n'
    '# specific_caveat_jurisdiction reports -- friction_tax.py carries only\n'
    '# that identifier, never prose; this dict is the single source of\n'
    '# truth for which jurisdictions have a specific caveat written at all\n'
    '# (a jurisdiction id not present here, e.g. any other state_specific_\n'
    '# flat/tiers state, resolves to None via .get() below, no separate\n'
    '# allow-list needed in friction_tax.py). Texts verbatim, Pete-confirmed,\n'
    '# do not alter.\n'
    '_SPECIFIC_CAVEAT_TEXT: dict[str, str] = {\n'
    '    "FL": (\n'
    '        "This figure reflects only punitive damages, capped at $100,000 "\n'
    '        "under Fla. Stat. Sec 760.11(5). Compensatory damages are legally "\n'
    '        "available in addition and aren\'t capped by this provision -- the "\n'
    '        "real total could be materially higher than what\'s reflected here."\n'
    '    ),\n'
    '    "ID": (\n'
    '        "This figure reflects only punitive damages, capped at $1,000 per "\n'
    '        "violation under Idaho Code Sec 67-5908(3)(e). Actual and economic "\n'
    '        "damages, including back pay, are legally available in addition "\n'
    '        "and aren\'t capped by this provision -- the real total could be "\n'
    '        "materially higher than what\'s reflected here."\n'
    '    ),\n'
    '    "KS": (\n'
    '        "This figure reflects only pain-and-suffering damages, capped at "\n'
    '        "$2,000 under K.S.A. Sec 44-1005(k). Back pay and other economic "\n'
    '        "damages are legally available in addition and aren\'t capped by "\n'
    '        "this provision -- the real total could be materially higher than "\n'
    '        "what\'s reflected here."\n'
    '    ),\n'
    '    "VA": (\n'
    '        "This figure reflects only punitive damages, capped at $350,000 "\n'
    '        "under Va. Code Sec 8.01-38.1. Compensatory damages are legally "\n'
    '        "available in addition and aren\'t capped under Virginia law -- "\n'
    '        "the real total could be materially higher than what\'s reflected "\n'
    '        "here."\n'
    '    ),\n'
    '    "AR": (\n'
    '        "Arkansas law doesn\'t cap damages for retaliation claims "\n'
    '        "specifically -- if this involves retaliation, the actual limit "\n'
    '        "could be materially higher than what\'s reflected here."\n'
    '    ),\n'
    '    "MD": (\n'
    '        "In Howard, Montgomery, and Prince George\'s counties, Maryland "\n'
    '        "law offers an uncapped alternative to this limit -- if this "\n'
    '        "claim would qualify, the actual limit could be materially "\n'
    '        "higher than what\'s reflected here."\n'
    '    ),\n'
    '    "TN": (\n'
    '        "Tennessee law doesn\'t cap damages for race-discrimination "\n'
    '        "claims brought under 42 U.S.C. Sec 1981 -- if this involves "\n'
    '        "such a claim, the actual limit could be materially higher than "\n'
    '        "what\'s reflected here."\n'
    '    ),\n'
    '}\n',
)

edit(
    C,
    '            "has_partial_jurisdictions": legal_result["has_partial_jurisdictions"],\n'
    '            "has_uncollected_net_worth_caveat": legal_result["has_uncollected_net_worth_caveat"],\n'
    '        }\n',
    '            "has_partial_jurisdictions": legal_result["has_partial_jurisdictions"],\n'
    '            "has_uncollected_net_worth_caveat": legal_result["has_uncollected_net_worth_caveat"],\n'
    '            "specific_caveat": _SPECIFIC_CAVEAT_TEXT.get(legal_result["specific_caveat_jurisdiction"]),\n'
    '        }\n',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print("ERROR:", rel_path, "-- expected 1 match, found", count)
            print("  old (first 200 chars):", repr(old[:200]))
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print("OK (dry-run):", rel_path, "-- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print("WRITTEN:", rel_path)
        changed += 1
    print()
    print(changed, "/", len(EDITS), "edits", "validated" if dry_run else "applied")
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
