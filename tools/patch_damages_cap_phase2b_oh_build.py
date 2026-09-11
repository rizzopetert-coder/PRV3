"""
engine/friction_tax.py: Phase 2b (OH) --
prompts/damages-cap-treatment-phase2-spec.md, superseded framing
(this session's investigation found the original economic_loss/
net_worth schema-gap framing was imprecise -- see that doc's updated
OH section).

Resolves Ohio to QUALITATIVE_ONLY rather than the generic curve every
other still-unbuilt state_specific_tiers state falls through to.
Mirrors Cluster 3's unclassifiable-headcount precedent (real, non-zero
exposure this codebase genuinely can't resolve a number for right now)
rather than Cluster 4c's Government case (no data exists by design) --
confirmed this session these are two structurally different existing
QUALITATIVE_ONLY consumers, not one.

Root problem, confirmed directly against live code before this patch:
no cluster's dollar curve represents a compensatory-damages figure
anywhere in this codebase (grepped -- every "compensatory" hit is
comment/citation prose, never a computed value), which both of R.C.
2315.21's branches multiply against; the small-employer/individual-
defendant branch additionally needs net_worth, which isn't collected
at intake and was never going to be solved by adding economic_loss.

Three call sites, not one -- confirmed by reading the live code before
editing, not assumed: resolve_damages_treatment() is independently
consulted in Cluster 1, Cluster 2, and Cluster 4b (via
_cluster_4_curve_for_org_type()), same as the existing
no_damages_available federal-floor branch and unlike CO's Phase 2a fix
(which only belonged in Cluster 4b, since only that cluster's ceiling
table happens to be the federal data CO's statute defers to) -- Ohio's
gap applies to every cluster equally, so all three need the branch.

_oh_is_small_employer() is built as a standalone, directly-testable
helper (R.C. 2315.21(D)(2)(b)'s <=100/<=500-if-manufacturing gate) but
deliberately NOT called from any of the three pricing branches -- both
of R.C. 2315.21's branches resolve to the identical QUALITATIVE_ONLY
LegalPricingResult today, so calling it there would be a discarded
result with no effect, not real logic. It exists tested and ready for
whenever a future citation/prose distinction or a real compensatory-
damages/net_worth pricing path is built and actually needs it.

Usage:
    python tools/patch_damages_cap_phase2b_oh_build.py --dry-run
    python tools/patch_damages_cap_phase2b_oh_build.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

# ---- Edit 1: two new helpers, inserted after _co_drives_federal_tier_deferral() ----

HELPERS_ANCHOR_OLD = '''    return best_jid == "CO"


def _cluster_4_curve_for_org_type('''

HELPERS_ANCHOR_NEW = '''    return best_jid == "CO"


def _oh_drives_tiers_result(jurisdictions: list[str]) -> bool:
    """
    True only when Ohio is the SPECIFIC jurisdiction
    resolve_damages_treatment() would resolve a state_specific_tiers
    result from -- same re-derivation of that function's own priority
    loop as _co_drives_federal_tier_deferral() above, same reason
    (resolve_damages_treatment() returns only a category string, not
    which jurisdiction won, and a blanket check on the resolved
    treatment string alone would also fire for TX, AR, etc.).

    Unlike CO's helper, this carries no headcount gate -- Ohio's
    QUALITATIVE_ONLY status applies at every headcount; headcount only
    selects which of R.C. 2315.21's two statutory branches would
    govern (see _oh_is_small_employer() below), a question this
    function doesn't answer.

    Same known limitation as _co_drives_federal_tier_deferral(),
    inherited not introduced: a tie between two state_specific_tiers
    jurisdictions resolves by input order, not disambiguated here.
    """
    best_jid: Optional[str] = None
    best_rank = -1
    for jid in jurisdictions:
        entry = STATE_COVERAGE_THRESHOLDS.get(jid)
        if entry is None or entry.confidence != "CONFIRMED":
            continue
        rank = _DAMAGES_TREATMENT_PRIORITY.get(entry.damages_cap_treatment, -1)
        if rank > best_rank:
            best_rank = rank
            best_jid = jid
    return best_jid == "OH"


def _oh_is_small_employer(headcount, industry: str) -> bool:
    """
    Ohio's own small-employer/individual-defendant gate, R.C.
    2315.21(D)(2)(b): <=100 full-time employees generally, <=500 if
    NAICS-manufacturing-classified. Uses this app's "Manufacturing &
    Industrial" INTAKE_FIELDS["industry"] bucket as an approximation of
    the real NAICS test -- confirmed NOT identical this session: the
    app bucket may sweep in adjacent non-manufacturing industrial
    activity (utilities, mining) that wouldn't actually qualify under
    Ohio's statute. No NAICS-level intake data exists to resolve this
    precisely; flagged here and in STATE_COVERAGE_THRESHOLDS["OH"]'s
    own citation comment, not resolved by this helper.

    Non-numeric headcount (unclassifiable input) returns False -- the
    general branch's statutory mechanics are the more conservative
    default to name when headcount can't be confirmed at all.

    Deliberately NOT called by any of the three damages_cap_treatment
    pricing branches (Clusters 1, 2, 4b) -- both of R.C. 2315.21's
    branches resolve to the identical QUALITATIVE_ONLY
    LegalPricingResult today (no compensatory-damages figure exists in
    this codebase to apply either multiplier to, and net_worth isn't
    collected regardless of which branch applies), so invoking this
    helper there would compute a real answer and then discard it. It's
    a standalone, directly-tested piece of correct logic, ready for
    whenever a future citation/prose distinction or a real pricing
    path for either R.C. 2315.21 branch is built and actually consumes
    it -- not wired into the pricing path prematurely.
    """
    if not isinstance(headcount, (int, float)):
        return False
    if headcount <= 100:
        return True
    return industry == "Manufacturing & Industrial" and headcount <= 500


def _cluster_4_curve_for_org_type('''

# ---- Edit 2: Cluster 1 branch ----

CLUSTER1_OLD = '''        flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
        curve = _CLUSTER_1_CURVE if flat_cap is None else LegalDollarCurve(
            floor=_CLUSTER_1_CURVE.floor, ceiling=min(_CLUSTER_1_CURVE.ceiling, flat_cap),
        )'''

CLUSTER1_NEW = '''        if treatment == "state_specific_tiers" and _oh_drives_tiers_result(jurisdictions):
            # Ohio's real cap can't be computed by this codebase today --
            # confirmed this session: no cluster's dollar curve represents
            # a compensatory-damages figure (Cluster 1's included), which
            # both of R.C. 2315.21's branches multiply against, and the
            # small-employer/individual-defendant branch additionally
            # needs net_worth, never collected at intake. Real, non-zero
            # exposure exists -- QUALITATIVE_ONLY, mirroring Cluster 3's
            # unclassifiable-headcount precedent (a number genuinely
            # can't be resolved) rather than Cluster 4c's Government case
            # (no data exists by design) -- confirmed this session these
            # are two structurally different existing QUALITATIVE_ONLY
            # consumers, not one. _oh_is_small_employer() computes which
            # of R.C. 2315.21's two branches would govern, for
            # correctness and future use -- not called here, since both
            # branches resolve identically today. Phase 2b, prompts/
            # damages-cap-treatment-phase2-spec.md.
            return LegalPricingResult(status=LegalPricingStatus.QUALITATIVE_ONLY, dollar_range=None,
                coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
        flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
        curve = _CLUSTER_1_CURVE if flat_cap is None else LegalDollarCurve(
            floor=_CLUSTER_1_CURVE.floor, ceiling=min(_CLUSTER_1_CURVE.ceiling, flat_cap),
        )'''

# ---- Edit 3: Cluster 2 branch ----

CLUSTER2_OLD = '''            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag)
        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B'''

CLUSTER2_NEW = '''            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag)
        if treatment == "state_specific_tiers" and _oh_drives_tiers_result(jurisdictions):
            # Same reasoning as Cluster 1 above -- Ohio's real cap can't
            # be computed by this codebase today (no compensatory-damages
            # figure exists anywhere, net_worth isn't collected). Phase
            # 2b, prompts/damages-cap-treatment-phase2-spec.md.
            return LegalPricingResult(status=LegalPricingStatus.QUALITATIVE_ONLY, dollar_range=None,
                coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)
        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B'''

# ---- Edit 4: Cluster 4b branch ----

CLUSTER4B_OLD = '''        treatment = "federal_cap_applies"
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)'''

CLUSTER4B_NEW = '''        treatment = "federal_cap_applies"
    if treatment == "state_specific_tiers" and _oh_drives_tiers_result(jurisdictions):
        # Same reasoning as Clusters 1/2 -- Ohio's real cap can't be
        # computed by this codebase today. Returned before the ceiling
        # lookup below, unlike Colorado's branch above (which relabels
        # treatment and lets normal resolution continue) -- Ohio has no
        # substitute number to fall through to. Phase 2b, prompts/
        # damages-cap-treatment-phase2-spec.md.
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.QUALITATIVE_ONLY,
            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False,
        )
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)'''

# ---- Edit 5: OH's STATE_COVERAGE_THRESHOLDS citation comment ----

OH_ENTRY_OLD = '''    "OH": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_tiers",  # H.B. 352 (Employment Law Uniformity Act), eff. Apr. 15, 2021, codified Ohio's Tort Reform Act caps onto R.C. ch. 4112 claims. R.C. 2315.18: non-economic compensatory capped at the greater of $250,000 or 3x economic loss, max $350,000. R.C. 2315.21: punitive capped at 2x compensatory, or for "small employers" (<=100 employees, 500 for manufacturing) at 10% of net worth up to $350,000
        confidence="CONFIRMED",
        citation="Ohio Civil Rights Act, R.C. ch. 4112; R.C. 2315.18; R.C. 2315.21; H.B. 352 eff. Apr. 15, 2021.",
    ),'''

OH_ENTRY_NEW = '''    "OH": StateCoverageThreshold(
        thresholds={"general": 4},
        # H.B. 352 (Employment Law Uniformity Act), eff. Apr. 15, 2021,
        # codified Ohio's Tort Reform Act caps onto R.C. ch. 4112 claims.
        # General employer: punitive damages capped at 2x compensatory
        # damages, no dollar ceiling, no net-worth alternative (R.C.
        # 2315.21(D)(2)). Small employer (<=100 FT employees, or <=500 if
        # NAICS-manufacturing-classified) or individual defendant: capped
        # at the LESSER of 2x compensatory OR 10% of net worth at time of
        # tort, up to $350,000 (R.C. 2315.21(D)(2)(b)). Resolved
        # QUALITATIVE_ONLY -- this codebase has no compensatory-damages-
        # specific figure to apply either multiplier to, and does not
        # collect net_worth. Small-employer routing (were it ever wired
        # in -- see _oh_is_small_employer()) uses this app's
        # "Manufacturing & Industrial" industry bucket as an
        # approximation of Ohio's NAICS-manufacturing test -- confirmed
        # this session that the two are not identical (the app bucket may
        # sweep in adjacent non-manufacturing industrial activity like
        # utilities or mining); flagged here, not resolved, since no
        # NAICS-level intake data exists to resolve it precisely.
        damages_cap_treatment="state_specific_tiers",
        confidence="CONFIRMED",
        citation="Ohio Civil Rights Act, R.C. ch. 4112; R.C. 2315.18; R.C. 2315.21; H.B. 352 eff. Apr. 15, 2021.",
    ),'''

EDITS = [
    ('two new helpers: _oh_drives_tiers_result, _oh_is_small_employer', HELPERS_ANCHOR_OLD, HELPERS_ANCHOR_NEW),
    ('Cluster 1 OH branch', CLUSTER1_OLD, CLUSTER1_NEW),
    ('Cluster 2 OH branch', CLUSTER2_OLD, CLUSTER2_NEW),
    ('Cluster 4b OH branch', CLUSTER4B_OLD, CLUSTER4B_NEW),
    ('OH citation comment update', OH_ENTRY_OLD, OH_ENTRY_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
