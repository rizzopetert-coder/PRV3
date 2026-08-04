"""
PRV3 -- Implement the Legal/Compliance mechanism-aware exposure design
in engine/friction_tax.py: INDUSTRY_NON_EXEMPT_RATIO, the 30-state
mechanism classification (Addenda 1, 2, 4), all five clusters' dollar
curves (Addendum 10's log-scale formula for Clusters 1/4a/4b/5,
Addendum 2's tier selection for Cluster 2, Addendum 4's scope-modulated
per-capita design for Cluster 3), and cross-state aggregation (Addendum
3: within-cluster geometric decay, across-cluster simple addition, N=1
guard).

Explicitly NOT implemented here, per Pete's direct scope and Addendum
9: any jurisdictional multiplier logic (California FEHA/PAGA overrides,
OSHA State Plan variation). Cluster 5 uses the statutory-max curve only
(Addendum 10) -- actual-average deferred alongside the paused
jurisdictional research. This is a new, standalone
compute_legal_compliance_exposure() function -- NOT wired into
compute_friction_tax()'s return dict, contract.py, or web/lib/types.ts.
That integration is separately scoped, unaddressed here.

Usage:
  python tools/patch_legal_compliance_engine_implementation.py --dry-run
  python tools/patch_legal_compliance_engine_implementation.py --write
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

NEW_CODE = '''

# -- Legal/Compliance -- mechanism-aware exposure (Addenda 1-10) ----------------
# prompts/friction-tax-legal-compliance-methodology.md. Separate from the
# attritional compute_friction_tax() above -- Legal/Compliance scales by
# mechanism (and for Cluster 4, org_type/headcount), not by payroll
# baseline. Standalone function, NOT wired into compute_friction_tax()'s
# return dict, engine/contract.py, or web/lib/types.ts -- that
# integration is separately scoped. Jurisdictional multiplier logic
# (California FEHA/PAGA overrides, OSHA State Plan variation, Addenda
# 6-9) is explicitly NOT implemented here -- deferred per Addendum 9.

# -- Industry non-exempt ratio ----------------------------------------------------
# Real BLS data (Addendum 10, source of record). Feeds Cluster 3's
# affected-subgroup calculation: headcount_midpoint x
# INDUSTRY_NON_EXEMPT_RATIO[industry]. Sources: BLS CPS cpsaat18c.pdf
# (total employed by industry, 2025) and cpsaat45.pdf (hourly-paid
# workers by industry, 2025); BLS CES (state/local government
# employment, June 2026); BLS nonprofit sector research data (2022,
# most recent available).

INDUSTRY_NON_EXEMPT_RATIO: dict[str, float] = {
    "Manufacturing & Industrial": 0.557,
    "Healthcare & Life Sciences": 0.560,
    "Financial Services": 0.285,
    "Professional Services": 0.227,
    "Retail & Hospitality": 0.662,
    # BLS "Information" sector -- narrower than colloquial "Technology,"
    # likely understates the real ratio.
    "Technology": 0.280,
    # Blends CPS + CES surveys, softer confidence than the others.
    "Government & Public Sector": 0.44,
    # Education component only -- "Nonprofit" is genuinely untracked by
    # BLS (confirmed via a 2024 Senate oversight letter to DOL), not a
    # research gap on this project's end.
    "Nonprofit & Education": 0.135,
    # Real national aggregate, BLS 2025.
    "Other": 0.556,
}

assert set(INDUSTRY_NON_EXEMPT_RATIO.keys()) == set(INDUSTRIES), (
    "INDUSTRY_NON_EXEMPT_RATIO keys must match INDUSTRIES exactly"
)


# -- Mechanism classification -----------------------------------------------------
# All 30 Legal-scoring states, classified into 5 mechanism clusters
# (prompts/friction-tax-legal-compliance-methodology.md, Addenda 1, 2,
# 4). Each state's "legal" score (used below for interpolation/tier
# selection) is NOT duplicated here -- it's read directly from
# STATE_MULTIPLIERS[state_id].criteria["legal"].score, already recorded
# above.

LEGAL_COMPLIANCE_CLUSTER: dict[str, int] = {
    # Cluster 1 -- Individual/isolated claim (4 states)
    "invisible_performance_management": 1,
    "the_paper_tiger": 1,
    "built_to_fail": 1,
    "the_untouchable": 1,
    # Cluster 2 -- Class/systemic discrimination (11 states)
    "disparate_impact_architecture": 2,
    "the_arbitrary_standard": 2,
    "the_pay_fog": 2,
    "pay_exposure": 2,
    "the_diversity_ceiling": 2,
    "the_inside_track": 2,
    "the_unexamined_algorithm": 2,
    "sequential_decision_blindness": 2,
    "the_tolerated_violation": 2,
    "the_wrong_reward": 2,
    "distributed_culture_fragmentation": 2,
    # Cluster 3 -- Wage-and-hour (2 states)
    "cultural_overtime": 3,
    "compression_crisis": 3,
    # Cluster 4 -- Whistleblower/regulatory, org_type-gated at compute
    # time into 4a/4b/4c (6 states)
    "hr_capture": 4,
    "heard_and_ignored": 4,
    "the_policy_lag": 4,
    "the_basement_standard": 4,
    "dueling_narratives": 4,
    "the_suppression_filter": 4,
    # Cluster 5 -- Safety/regulatory (7 states)
    "the_unreported_hazard": 5,
    "the_unlocked_door": 5,
    "invisible_burnout": 5,
    "the_undefined_role": 5,
    "the_unsolved_problem": 5,
    "groundhog_day": 5,
    "the_exposed": 5,
}

_LEGAL_CLUSTER_COUNTS_EXPECTED = {1: 4, 2: 11, 3: 2, 4: 6, 5: 7}

assert len(LEGAL_COMPLIANCE_CLUSTER) == 30, (
    f"LEGAL_COMPLIANCE_CLUSTER must classify all 30 Legal-scoring states, "
    f"found {len(LEGAL_COMPLIANCE_CLUSTER)}"
)
for _cluster_num, _expected_count in _LEGAL_CLUSTER_COUNTS_EXPECTED.items():
    _actual_count = sum(1 for v in LEGAL_COMPLIANCE_CLUSTER.values() if v == _cluster_num)
    assert _actual_count == _expected_count, (
        f"Cluster {_cluster_num}: expected {_expected_count} states, found {_actual_count}"
    )
for _lc_sid, _lc_cluster in LEGAL_COMPLIANCE_CLUSTER.items():
    assert _lc_sid in STATE_MULTIPLIERS, (
        f"LEGAL_COMPLIANCE_CLUSTER references unknown state {_lc_sid!r}"
    )
    _lc_score = STATE_MULTIPLIERS[_lc_sid].criteria["legal"].score
    assert _lc_score in (1, 2), (
        f"{_lc_sid}: classified into Cluster {_lc_cluster} but its recorded "
        f"'legal' score is {_lc_score}, not in {{1, 2}} -- Addendum 10's "
        f"interpolation formula requires the real 1-2 domain"
    )
del _cluster_num, _expected_count, _actual_count, _lc_sid, _lc_cluster, _lc_score


# -- Dollar-curve anchors ----------------------------------------------------------
# Addendum 10: fraction(score) = floor * (ceiling / floor) ** (score - 1),
# score in {1, 2}. score=1 -> floor exactly, score=2 -> ceiling exactly.
# Applies to Clusters 1, 4a, 4b, 5. Cluster 2 uses its own discrete
# tier-selection mechanism (Addendum 2), not this formula.

@dataclass(frozen=True)
class LegalDollarCurve:
    """One cluster's (or sub-track's) floor/ceiling for Addendum 10's formula."""
    floor: float
    ceiling: float


def _legal_score_fraction(curve: LegalDollarCurve, score: int) -> float:
    return curve.floor * (curve.ceiling / curve.floor) ** (score - 1)


# Cluster 1 -- Individual/isolated claim (Addendum 1).
_CLUSTER_1_CURVE = LegalDollarCurve(floor=50_000.0, ceiling=450_000.0)

# Cluster 2 -- Class/systemic discrimination, two discrete tiers (Addendum 2).
# NOT the log-scale formula -- score selects a tier outright.
_CLUSTER_2_TIER_2A = (1_800.0, 2_500.0)   # compensatory-only, score=1
_CLUSTER_2_TIER_2B = (25_000.0, 31_000.0)  # punitive-inclusive, score=2

# Cluster 3 -- Wage-and-hour, per-worker rates (Addendum 4, locked).
# Score modulates affected-worker SCOPE (Addendum 10's 25%/75%, design
# judgment, not sourced), not these two rates.
_CLUSTER_3_ADMIN_RATE_PER_WORKER = 1_465.0
_CLUSTER_3_LITIGATION_RATE_PER_WORKER = 2_930.0
_CLUSTER_3_SCOPE_FRACTION_BY_SCORE: dict[int, float] = {1: 0.25, 2: 0.75}

# Cluster 4a -- SEC/Dodd-Frank, org_type == "Publicly traded" (Addendum 5,
# ceiling corrected in Addendum 10 to the real average-total-organizational-
# sanction midpoint, NOT the $279M historic outlier).
_CLUSTER_4A_CURVE = LegalDollarCurve(floor=25_000.0, ceiling=33_000_000.0)

# Cluster 4b -- general private-sector retaliation (Addendum 5's real
# Title VII/ADA statutory bracket table, 42 U.S.C. Sec 1981a(b)(3)).
# 100-249's ceiling is the midpoint of its own $50K-$100K straddle range,
# per Addendum 10's stated consistency convention with Cluster 4a's
# midpoint approach -- flagged there as a design choice, not something
# Pete specified for this exact sub-case.
_CLUSTER_4B_FLOOR = 25_000.0
_CLUSTER_4B_CEILING_BY_HEADCOUNT: dict[str, float] = {
    "Under 25": 50_000.0,
    "25-99": 50_000.0,
    "100-249": 75_000.0,
    "250-499": 200_000.0,
    "500-999": 300_000.0,
    "1000+": 300_000.0,
}

# Cluster 5 -- Safety/regulatory, statutory-max curve ONLY (Addendum 10 --
# actual-average curve deferred alongside the paused jurisdictional
# research, Addendum 9).
_CLUSTER_5_CURVE = LegalDollarCurve(floor=16_550.0, ceiling=165_514.0)


def _cluster_4_curve_for_org_type(
    org_type: str, org_size: str
) -> Optional[LegalDollarCurve]:
    """
    Addendum 5's three org_type-gated sub-tracks. Returns None for
    "Government" (4c) -- genuinely no dollar figure (thin MSPB data), not
    a zero -- and for any unrecognized org_size in the 4b bracket table.
    "PE or VC-backed" defaults to 4b -- the possible 4a edge case (a
    registered investment adviser/broker-dealer) isn't determinable from
    org_type alone, per Addendum 5, and isn't resolved here.
    """
    if org_type == "Publicly traded":
        return _CLUSTER_4A_CURVE
    if org_type == "Government":
        return None
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)
    if ceiling is None:
        return None
    return LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=ceiling)


def _cluster_3_affected_workers(org_size: str, industry: str, score: int) -> float:
    """
    Addendum 4 (locked scope-modulated design) + Addendum 10 (25%/75%
    scope percentages). Base subgroup = headcount midpoint x industry
    non-exempt ratio; score narrows/broadens the affected slice.
    """
    midpoint_entry = HEADCOUNT_MIDPOINTS.get(org_size)
    if midpoint_entry is None or midpoint_entry.employees_per_firm is None:
        return 0.0
    ratio = INDUSTRY_NON_EXEMPT_RATIO.get(industry)
    if ratio is None:
        return 0.0
    subgroup = midpoint_entry.employees_per_firm * ratio
    scope_fraction = _CLUSTER_3_SCOPE_FRACTION_BY_SCORE.get(score, 0.0)
    return subgroup * scope_fraction


def _single_state_legal_range(
    state_id: str,
    org_size: str,
    industry: str,
    org_type: str,
) -> Optional[tuple[float, float]]:
    """
    (low, high) for one Legal-scoring state in isolation, or None if the
    state isn't Legal-scoring, its "legal" score is 0 (no exposure), or
    (Cluster 4 + org_type == "Government") -- genuinely no dollar figure.
    """
    cluster = LEGAL_COMPLIANCE_CLUSTER.get(state_id)
    if cluster is None:
        return None
    entry = STATE_MULTIPLIERS.get(state_id)
    if entry is None:
        return None
    score = entry.criteria["legal"].score
    if score == 0:
        return None

    if cluster == 1:
        v = _legal_score_fraction(_CLUSTER_1_CURVE, score)
        return (v, v)
    if cluster == 2:
        return _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B
    if cluster == 3:
        affected = _cluster_3_affected_workers(org_size, industry, score)
        return (
            affected * _CLUSTER_3_ADMIN_RATE_PER_WORKER,
            affected * _CLUSTER_3_LITIGATION_RATE_PER_WORKER,
        )
    if cluster == 4:
        curve = _cluster_4_curve_for_org_type(org_type, org_size)
        if curve is None:
            return None
        v = _legal_score_fraction(curve, score)
        return (v, v)
    if cluster == 5:
        v = _legal_score_fraction(_CLUSTER_5_CURVE, score)
        return (v, v)
    return None


def compute_legal_compliance_exposure(
    state_ids: list[str],
    org_size: str,
    industry: str,
    org_type: str,
) -> dict:
    """
    Cross-state aggregation (Addendum 3): within-cluster geometric decay
    (w_i = 0.5**(i-1), reusing the attritional Step 1 shape -- ranked by
    each state's own low end, highest first), across-cluster simple
    addition (no breadth premium -- Addendum 3's explicit, justified
    departure from the attritional design's Factor B). N=1 guard: exactly
    one Legal-scoring state in the profile collapses the output to that
    state's own individual range, no aggregation logic engaged.

    Jurisdictional multipliers (California FEHA/PAGA overrides, OSHA
    State Plan variation, Addenda 6-9) are NOT applied here -- deferred,
    per Addendum 9. Cluster 5 uses the statutory-max curve only (Addendum
    10) -- actual-average deferred alongside that same paused research.

    Returns {"low": float | None, "high": float | None, "currency": "USD"}.
    low/high are None if no identified state carries real, priceable
    Legal/Compliance exposure.
    """
    per_state_ranges: dict[str, tuple[float, float]] = {}
    for sid in state_ids:
        r = _single_state_legal_range(sid, org_size, industry, org_type)
        if r is not None:
            per_state_ranges[sid] = r

    if not per_state_ranges:
        return {"low": None, "high": None, "currency": "USD"}

    if len(per_state_ranges) == 1:
        low, high = next(iter(per_state_ranges.values()))
        return {"low": round(low, 2), "high": round(high, 2), "currency": "USD"}

    by_cluster: dict[int, list[tuple[float, float]]] = {}
    for sid, r in per_state_ranges.items():
        by_cluster.setdefault(LEGAL_COMPLIANCE_CLUSTER[sid], []).append(r)

    total_low = 0.0
    total_high = 0.0
    for ranges in by_cluster.values():
        ranges_sorted = sorted(ranges, key=lambda r: r[0], reverse=True)
        total_low += sum((0.5 ** i) * low for i, (low, _high) in enumerate(ranges_sorted))
        total_high += sum((0.5 ** i) * high for i, (_low, high) in enumerate(ranges_sorted))

    return {"low": round(total_low, 2), "high": round(total_high, 2), "currency": "USD"}
'''

edit(
    ENGINE,
    '    return {\n'
    '        "low": low,\n'
    '        "high": high,\n'
    '        "currency": "USD",\n'
    '        "org_size_label": org_size,\n'
    '        "severity_scalar": severity_scalar,\n'
    '        "calibration_complete": True,\n'
    '    }\n',
    '    return {\n'
    '        "low": low,\n'
    '        "high": high,\n'
    '        "currency": "USD",\n'
    '        "org_size_label": org_size,\n'
    '        "severity_scalar": severity_scalar,\n'
    '        "calibration_complete": True,\n'
    '    }\n'
    + NEW_CODE,
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
