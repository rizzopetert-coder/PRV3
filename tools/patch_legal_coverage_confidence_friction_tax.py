"""
engine/friction_tax.py: thread coverage_confidence/partial_state_flag
through LegalPricingResult and LegalCurveLookup, aggregate into
coverage_basis/has_partial_jurisdictions in compute_legal_compliance_exposure(),
and correct the stale "NOT wired" section-header comment (false since
commit 46c1e0c, 2026-08-04). Architecture cleared by Gemini, independently
verified against live source, corrected on one point (Clusters 3/4a/4c/5
get NOT_APPLICABLE, not a hardcoded FEDERAL_FALLBACK), re-confirmed by
Gemini's final review.

Usage:
    python tools/patch_legal_coverage_confidence_friction_tax.py --dry-run
    python tools/patch_legal_coverage_confidence_friction_tax.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

REPLACEMENTS = []

# 1. typing import -- add Literal
REPLACEMENTS.append((
    "from typing import Optional",
    "from typing import Literal, Optional",
))

# 2. stale section-header comment
REPLACEMENTS.append((
    """# -- Legal/Compliance -- mechanism-aware exposure (Addenda 1-10) ----------------
# prompts/friction-tax-legal-compliance-methodology.md. Separate from the
# attritional compute_friction_tax() above -- Legal/Compliance scales by
# mechanism (and for Cluster 4, org_type/headcount), not by payroll
# baseline. Standalone function, NOT wired into compute_friction_tax()'s
# return dict, engine/contract.py, or web/lib/types.ts -- that
# integration is separately scoped. Jurisdictional multiplier logic
# (California FEHA/PAGA overrides, OSHA State Plan variation, Addenda
# 6-9) is explicitly NOT implemented here -- deferred per Addendum 9.""",
    """# -- Legal/Compliance -- mechanism-aware exposure (Addenda 1-10) ----------------
# prompts/friction-tax-legal-compliance-methodology.md. Separate from the
# attritional compute_friction_tax() above -- Legal/Compliance scales by
# mechanism (and for Cluster 4, org_type/headcount), not by payroll
# baseline. WIRED into engine/contract.py's private_output as of commit
# 46c1e0c (2026-08-04, "wire Legal/Compliance tail-risk exposure into
# private output") -- the comment here previously claimed the opposite
# ("NOT wired... that integration is separately scoped") for over a
# month after it stopped being true, and caused the 2026-09-05 Quarterly
# Step-Back to wrongly conclude the module was unwired; corrected here
# after independent verification against live source. As of this
# session, the returned dict also carries coverage_basis and
# has_partial_jurisdictions (see compute_legal_compliance_exposure()'s
# own docstring), distinguishing state-confirmed from federal-fallback
# coverage determinations. Jurisdictional multiplier logic (California
# FEHA/PAGA overrides, OSHA State Plan variation, Addenda 6-9) is
# explicitly NOT implemented here -- deferred per Addendum 9.""",
))

# 3. LegalPricingResult dataclass
REPLACEMENTS.append((
    '''@dataclass(frozen=True)
class LegalPricingResult:
    """One state's pricing outcome. dollar_range is populated only when
    status is PRICED."""
    status: LegalPricingStatus
    dollar_range: Optional[tuple[float, float]]''',
    '''@dataclass(frozen=True)
class LegalPricingResult:
    """One state's pricing outcome. dollar_range is populated only when
    status is PRICED. coverage_confidence reflects whether/how the
    state-coverage-threshold gate resolved for this specific cluster --
    "NOT_APPLICABLE" when no coverage question was ever asked (Clusters
    3, 4a, 4c, 5, and every early NOT_APPLICABLE return that doesn't
    consult jurisdiction), never None/null. partial_state_flag mirrors
    CoverageResult.partial_state_flag when the gate actually ran; False
    when coverage_confidence is "NOT_APPLICABLE", since a
    partial-jurisdiction caveat cannot apply to a determination that
    never consulted jurisdictions at all."""
    status: LegalPricingStatus
    dollar_range: Optional[tuple[float, float]]
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool''',
))

# 4. LegalCurveLookup dataclass
REPLACEMENTS.append((
    '''@dataclass(frozen=True)
class LegalCurveLookup:
    """Result of resolving a Cluster 4 sub-track curve. curve is
    populated only when status is PRICED."""
    curve: Optional[LegalDollarCurve]
    status: LegalPricingStatus''',
    '''@dataclass(frozen=True)
class LegalCurveLookup:
    """Result of resolving a Cluster 4 sub-track curve. curve is
    populated only when status is PRICED. coverage_confidence/
    partial_state_flag carry the same meaning as LegalPricingResult's
    fields of the same name -- "NOT_APPLICABLE"/False for the 4a
    (Publicly traded) and 4c (Government) early-return branches, which
    never call resolve_coverage_gate(); the real CoverageResult values
    for every 4b fallthrough branch (not-applies, DATA_INTEGRITY_GAP,
    and PRICED alike), since the gate genuinely runs for all three."""
    curve: Optional[LegalDollarCurve]
    status: LegalPricingStatus
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool''',
))

# 5. _cluster_4_curve_for_org_type()
REPLACEMENTS.append((
    '''    if org_type == "Publicly traded":
        return LegalCurveLookup(curve=_CLUSTER_4A_CURVE, status=LegalPricingStatus.PRICED)
    if org_type == "Government":
        return LegalCurveLookup(curve=None, status=LegalPricingStatus.QUALITATIVE_ONLY)
    coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
    if not coverage.applies:
        return LegalCurveLookup(curve=None, status=LegalPricingStatus.NOT_APPLICABLE)
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)
    if ceiling is None:
        return LegalCurveLookup(curve=None, status=LegalPricingStatus.DATA_INTEGRITY_GAP)
    return LegalCurveLookup(
        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=ceiling),
        status=LegalPricingStatus.PRICED,
    )''',
    '''    if org_type == "Publicly traded":
        return LegalCurveLookup(
            curve=_CLUSTER_4A_CURVE, status=LegalPricingStatus.PRICED,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False,
        )
    if org_type == "Government":
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.QUALITATIVE_ONLY,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False,
        )
    coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
    if not coverage.applies:
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.NOT_APPLICABLE,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        )
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)
    if ceiling is None:
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.DATA_INTEGRITY_GAP,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        )
    return LegalCurveLookup(
        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=ceiling),
        status=LegalPricingStatus.PRICED,
        coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
    )''',
))

# 6. _single_state_legal_pricing() -- early NOT_APPLICABLE returns + all cluster branches
REPLACEMENTS.append((
    '''    cluster = LEGAL_COMPLIANCE_CLUSTER.get(state_id)
    if cluster is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)
    entry = STATE_MULTIPLIERS.get(state_id)
    if entry is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)
    score = entry.criteria["legal"].score
    if score == 0:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)

    if cluster == 1:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)
        v = _legal_score_fraction(_CLUSTER_1_CURVE, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))
    if cluster == 2:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)
        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r)
    if cluster == 3:
        affected = _cluster_3_affected_workers(org_size, industry, score)
        r = (
            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,
            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,
        )
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r)
    if cluster == 4:
        lookup = _cluster_4_curve_for_org_type(org_type, org_size, headcount, jurisdictions)
        if lookup.curve is None:
            return LegalPricingResult(status=lookup.status, dollar_range=None)
        v = _legal_score_fraction(lookup.curve, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))
    if cluster == 5:
        v = _legal_score_fraction(_CLUSTER_5_CURVE, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v))
    return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None)''',
    '''    cluster = LEGAL_COMPLIANCE_CLUSTER.get(state_id)
    if cluster is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    entry = STATE_MULTIPLIERS.get(state_id)
    if entry is None:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    score = entry.criteria["legal"].score
    if score == 0:
        return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)

    if cluster == 1:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
        v = _legal_score_fraction(_CLUSTER_1_CURVE, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
    if cluster == 2:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
    if cluster == 3:
        affected = _cluster_3_affected_workers(org_size, industry, score)
        r = (
            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,
            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,
        )
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    if cluster == 4:
        lookup = _cluster_4_curve_for_org_type(org_type, org_size, headcount, jurisdictions)
        if lookup.curve is None:
            return LegalPricingResult(status=lookup.status, dollar_range=None,
                coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)
        v = _legal_score_fraction(lookup.curve, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)
    if cluster == 5:
        v = _legal_score_fraction(_CLUSTER_5_CURVE, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
    return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
        coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)''',
))

# 7. compute_legal_compliance_exposure() -- aggregation + three return paths
REPLACEMENTS.append((
    '''    headcount = org_size
    jurisdictions = jurisdictions or []
    org_size = resolve_headcount_bucket(org_size)
    per_state_ranges: dict[str, tuple[float, float]] = {}
    unpriced_state_ids: list[str] = []
    for sid in state_ids:
        result = _single_state_legal_pricing(
            sid, org_size, industry, org_type, headcount, jurisdictions
        )
        if result.status == LegalPricingStatus.PRICED:
            per_state_ranges[sid] = result.dollar_range
        elif result.status == LegalPricingStatus.QUALITATIVE_ONLY:
            unpriced_state_ids.append(sid)
        elif result.status == LegalPricingStatus.DATA_INTEGRITY_GAP:
            unpriced_state_ids.append(sid)
            _logger.warning(
                "Legal/Compliance pricing data-integrity gap for state_id=%r "
                "(org_size=%r, industry=%r, org_type=%r) -- expected a "
                "priceable curve but none was found",
                sid, org_size, industry, org_type,
            )
        # NOT_APPLICABLE: silently excluded, unchanged from before.

    has_unpriced_conditions = bool(unpriced_state_ids)

    if not per_state_ranges:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "band": _legal_exposure_band(None),
            "has_unpriced_conditions": has_unpriced_conditions,
            "unpriced_state_ids": unpriced_state_ids,
        }

    if len(per_state_ranges) == 1:
        low, high = next(iter(per_state_ranges.values()))
        rounded_low = round(low, 2)
        return {
            "low": rounded_low,
            "high": round(high, 2),
            "currency": "USD",
            "band": _legal_exposure_band(rounded_low),
            "has_unpriced_conditions": has_unpriced_conditions,
            "unpriced_state_ids": unpriced_state_ids,
        }

    by_cluster: dict[int, list[tuple[float, float]]] = {}
    for sid, r in per_state_ranges.items():
        by_cluster.setdefault(LEGAL_COMPLIANCE_CLUSTER[sid], []).append(r)

    total_low = 0.0
    total_high = 0.0
    for ranges in by_cluster.values():
        ranges_sorted = sorted(ranges, key=lambda r: r[0], reverse=True)
        total_low += sum((0.5 ** i) * low for i, (low, _high) in enumerate(ranges_sorted))
        total_high += sum((0.5 ** i) * high for i, (_low, high) in enumerate(ranges_sorted))

    rounded_total_low = round(total_low, 2)
    return {
        "low": rounded_total_low,
        "high": round(total_high, 2),
        "currency": "USD",
        "band": _legal_exposure_band(rounded_total_low),
        "has_unpriced_conditions": has_unpriced_conditions,
        "unpriced_state_ids": unpriced_state_ids,
    }''',
    '''    headcount = org_size
    jurisdictions = jurisdictions or []
    org_size = resolve_headcount_bucket(org_size)
    per_state_ranges: dict[str, tuple[float, float]] = {}
    unpriced_state_ids: list[str] = []
    coverage_confidences: set[str] = set()
    has_partial_jurisdictions = False
    for sid in state_ids:
        result = _single_state_legal_pricing(
            sid, org_size, industry, org_type, headcount, jurisdictions
        )
        if result.status == LegalPricingStatus.PRICED:
            per_state_ranges[sid] = result.dollar_range
            if result.coverage_confidence != "NOT_APPLICABLE":
                coverage_confidences.add(result.coverage_confidence)
                if result.partial_state_flag:
                    has_partial_jurisdictions = True
        elif result.status == LegalPricingStatus.QUALITATIVE_ONLY:
            unpriced_state_ids.append(sid)
        elif result.status == LegalPricingStatus.DATA_INTEGRITY_GAP:
            unpriced_state_ids.append(sid)
            _logger.warning(
                "Legal/Compliance pricing data-integrity gap for state_id=%r "
                "(org_size=%r, industry=%r, org_type=%r) -- expected a "
                "priceable curve but none was found",
                sid, org_size, industry, org_type,
            )
        # NOT_APPLICABLE: silently excluded, unchanged from before.

    has_unpriced_conditions = bool(unpriced_state_ids)

    # coverage_basis: excludes NOT_APPLICABLE entirely (a state priced only
    # via Clusters 3/4a/4c/5 never asked the coverage question, so it
    # contributes nothing to this determination). None when no PRICED
    # result ever consulted the coverage gate at all.
    if not coverage_confidences:
        coverage_basis = None
    elif coverage_confidences == {"CONFIRMED"}:
        coverage_basis = "state_specific"
    elif coverage_confidences == {"FEDERAL_FALLBACK"}:
        coverage_basis = "federal_baseline"
    else:
        coverage_basis = "mixed"

    if not per_state_ranges:
        return {
            "low": None,
            "high": None,
            "currency": "USD",
            "band": _legal_exposure_band(None),
            "has_unpriced_conditions": has_unpriced_conditions,
            "unpriced_state_ids": unpriced_state_ids,
            "coverage_basis": coverage_basis,
            "has_partial_jurisdictions": has_partial_jurisdictions,
        }

    if len(per_state_ranges) == 1:
        low, high = next(iter(per_state_ranges.values()))
        rounded_low = round(low, 2)
        return {
            "low": rounded_low,
            "high": round(high, 2),
            "currency": "USD",
            "band": _legal_exposure_band(rounded_low),
            "has_unpriced_conditions": has_unpriced_conditions,
            "unpriced_state_ids": unpriced_state_ids,
            "coverage_basis": coverage_basis,
            "has_partial_jurisdictions": has_partial_jurisdictions,
        }

    by_cluster: dict[int, list[tuple[float, float]]] = {}
    for sid, r in per_state_ranges.items():
        by_cluster.setdefault(LEGAL_COMPLIANCE_CLUSTER[sid], []).append(r)

    total_low = 0.0
    total_high = 0.0
    for ranges in by_cluster.values():
        ranges_sorted = sorted(ranges, key=lambda r: r[0], reverse=True)
        total_low += sum((0.5 ** i) * low for i, (low, _high) in enumerate(ranges_sorted))
        total_high += sum((0.5 ** i) * high for i, (_low, high) in enumerate(ranges_sorted))

    rounded_total_low = round(total_low, 2)
    return {
        "low": rounded_total_low,
        "high": round(total_high, 2),
        "currency": "USD",
        "band": _legal_exposure_band(rounded_total_low),
        "has_unpriced_conditions": has_unpriced_conditions,
        "unpriced_state_ids": unpriced_state_ids,
        "coverage_basis": coverage_basis,
        "has_partial_jurisdictions": has_partial_jurisdictions,
    }''',
))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    new_content = content
    errors = []
    for i, (old, new) in enumerate(REPLACEMENTS, 1):
        count = new_content.count(old)
        if count != 1:
            errors.append(f'Replacement #{i}: found {count} times, expected exactly 1.')
            continue
        new_content = new_content.replace(old, new, 1)

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(REPLACEMENTS)} replacements found exactly once, would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
