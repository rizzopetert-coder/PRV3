"""
engine/friction_tax.py: damages_cap_treatment Phase 1 build, per
prompts/damages-cap-treatment-phase1-spec.md (fully resolved,
Cluster 1 scope confirmed by Pete this session -- item 3's is_floor
flag extends to Cluster 1 as well as Cluster 4b, same curve mechanism,
same reasoning, no principled basis for treating them differently).

Nine edits:
1. LegalPricingResult: add is_floor: bool = False.
2. LegalCurveLookup: add is_floor: bool = False.
3. StateCoverageThreshold: add flat_cap: Optional[float] = None, plus
   a docstring update to the no_damages_available paragraph -- the
   original "MUST treat this value as zero exposure" note predates
   this build's headcount-conditional federal-floor branch (item 2)
   and needed a precision fix, not a reversal: the STATE's own remedy
   is genuinely zero; federal law is a separate, independent channel
   that now prices real exposure once headcount clears the federal
   15-employee floor.
4. New _DAMAGES_TREATMENT_PRIORITY table + resolve_damages_treatment()
   -- highest-exposure-wins across CONFIRMED jurisdictions. Fallback
   for empty/no-CONFIRMED input is "federal_cap_applies" -- the
   real-world-correct default, explicitly NOT claimed to be a literal
   code-level match to resolve_coverage_gate()'s own "FEDERAL_FALLBACK"
   convention (verified distinct before writing this, per Pete's
   explicit instruction to check rather than assume).
5. New _resolve_flat_cap() -- maximum flat_cap among CONFIRMED
   state_specific_flat jurisdictions in the input, needed because
   resolve_damages_treatment() returns a category string, not a
   specific state.
6. Cluster 1 branch (_single_state_legal_pricing): no_damages_available
   federal-floor branch, state_specific_flat clamp, uncapped is_floor.
7. Cluster 2 branch (_single_state_legal_pricing): no_damages_available
   federal-floor branch only -- fixed discrete tiers, no curve to clamp
   or flag.
8. Cluster 4 branch (_single_state_legal_pricing): passes through
   lookup.is_floor.
9. _cluster_4_curve_for_org_type (Cluster 4b): no_damages_available
   federal-floor branch, state_specific_flat clamp, uncapped is_floor
   -- same three behaviors as Cluster 1, mirrored.
10. FL/ID/KS/VA data rows: add flat_cap= (verified directly against
    each state's own live comment before this patch, not transcribed
    unchecked: FL $100,000, ID $1,000, KS $2,000, VA $350,000).

Usage:
    python tools/patch_damages_cap_phase1_build.py --dry-run
    python tools/patch_damages_cap_phase1_build.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

# ---- Edit 1: LegalPricingResult.is_floor -----------------------------------

EDIT1_OLD = '''    never consulted jurisdictions at all."""
    status: LegalPricingStatus
    dollar_range: Optional[tuple[float, float]]
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool'''

EDIT1_NEW = '''    never consulted jurisdictions at all. is_floor (Phase 1,
    prompts/damages-cap-treatment-phase1-spec.md items 3/4) is True
    when the priced dollar_range reflects a generic ceiling standing in
    for a state with no real cap of its own (damages_cap_treatment ==
    "uncapped") or a flat cap that governs only a narrower damage-type
    slice than the figure implies ("state_specific_flat") -- signals
    to a future output layer that the figure should render as a floor,
    not a hard ceiling. False by default so every pre-existing
    construction site needs no change; not yet consumed by any output
    layer, same "no consumer yet" status as damages_cap_treatment
    itself before this build."""
    status: LegalPricingStatus
    dollar_range: Optional[tuple[float, float]]
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool
    is_floor: bool = False'''

# ---- Edit 2: LegalCurveLookup.is_floor --------------------------------------

EDIT2_OLD = '''    for every 4b fallthrough branch (not-applies, DATA_INTEGRITY_GAP,
    and PRICED alike), since the gate genuinely runs for all three."""
    curve: Optional[LegalDollarCurve]
    status: LegalPricingStatus
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool'''

EDIT2_NEW = '''    for every 4b fallthrough branch (not-applies, DATA_INTEGRITY_GAP,
    and PRICED alike), since the gate genuinely runs for all three.
    is_floor carries the same meaning as LegalPricingResult's own field
    of that name (Phase 1, prompts/damages-cap-treatment-phase1-spec.md
    items 3/4) -- forwarded into the final LegalPricingResult by
    _single_state_legal_pricing()'s Cluster 4 branch."""
    curve: Optional[LegalDollarCurve]
    status: LegalPricingStatus
    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]
    partial_state_flag: bool
    is_floor: bool = False'''

# ---- Edit 3: StateCoverageThreshold.flat_cap + docstring update ------------

EDIT3_OLD = '''                      "no_damages_available": neither compensatory nor
                      punitive damages are authorized under this statute
                      at all -- remedies are limited to equitable/make-
                      whole relief (back pay, front pay, reinstatement,
                      injunctive relief, attorney's fees), e.g. ND, WI.
                      Distinct from "uncapped": that value means real
                      damages exist with no ceiling; this value means no
                      damages exist to cap in the first place. A future
                      pricing extension MUST treat this value as zero
                      exposure, not unconstrained exposure -- conflating
                      it with "uncapped" would overstate a state's real
                      exposure, the exact misread this value exists to
                      prevent. Captured for a future pricing extension
                      (adjusting Cluster 1/2/4b's dollar ceiling by
                      state) -- NOT yet consumed by resolve_coverage_gate()
                      or the Cluster 1/2/4b integration below, which only
                      gates applicability, not dollar amount. See the
                      design doc's "Next steps."
    confidence:       "CONFIRMED" (independently verified against primary
                      statute text this session) | "PARTIAL" (not verified
                      this session -- see citation for what the entry
                      actually represents). resolve_coverage_gate() never
                      lets a PARTIAL entry drive a dollar-affecting
                      determination -- see that function's docstring.
    citation:         Primary source, or an explicit note when the entry is
                      an unverified placeholder rather than a researched
                      finding.
    """
    thresholds: dict[str, int]
    damages_cap_treatment: str
    confidence: str
    citation: str'''

EDIT3_NEW = '''                      "no_damages_available": neither compensatory nor
                      punitive damages are authorized under this
                      state's OWN statute at all -- remedies are
                      limited to equitable/make-whole relief (back pay,
                      front pay, reinstatement, injunctive relief,
                      attorney's fees), e.g. ND, WI.
                      Distinct from "uncapped": that value means real
                      damages exist with no ceiling; this value means no
                      damages exist to cap under STATE law specifically.
                      PHASE 1 UPDATE (prompts/damages-cap-treatment-
                      phase1-spec.md item 2, resolve_damages_treatment()
                      + the Cluster 1/2/4b integration below): the
                      state's own remedy is genuinely zero, but federal
                      law (Title VII/ADA) is a separate, independent
                      channel -- real, non-zero exposure is now priced
                      once headcount clears the federal 15-employee
                      floor (_FEDERAL_DEFAULT_THRESHOLD), with
                      NOT_APPLICABLE (genuinely zero) returned only
                      below it. This corrects the module's original
                      "MUST treat this value as zero exposure, not
                      unconstrained exposure" framing, written before
                      this headcount split was scoped -- that guidance
                      still describes the state's own remedy correctly,
                      it just no longer describes this value as a
                      blanket zero regardless of headcount.
    flat_cap:         Populated only for damages_cap_treatment ==
                      "state_specific_flat" states (FL, ID, KS, VA) --
                      the actual flat dollar figure from each state's
                      own citation, pulled directly from source (Phase
                      1, item 4). Clamped against the generic curve's
                      ceiling (min(curve.ceiling, flat_cap)) in Clusters
                      1 and 4b -- see resolve_damages_treatment() and
                      _resolve_flat_cap() below. None for every other
                      damages_cap_treatment value.
    confidence:       "CONFIRMED" (independently verified against primary
                      statute text this session) | "PARTIAL" (not verified
                      this session -- see citation for what the entry
                      actually represents). resolve_coverage_gate() never
                      lets a PARTIAL entry drive a dollar-affecting
                      determination -- see that function's docstring.
    citation:         Primary source, or an explicit note when the entry is
                      an unverified placeholder rather than a researched
                      finding.
    """
    thresholds: dict[str, int]
    damages_cap_treatment: str
    confidence: str
    citation: str
    flat_cap: Optional[float] = None'''

# ---- Edit 4/5: resolve_damages_treatment() + _resolve_flat_cap() ----------
# Inserted right after resolve_coverage_gate() ends, before
# _cluster_4_curve_for_org_type() -- a sibling resolver over the same
# STATE_COVERAGE_THRESHOLDS data, needed by both before either is
# defined at call time (Python resolves module-level function bodies
# at call time, not def time, so placement here is for readability,
# not correctness).

EDIT4_OLD = '''    threshold = _federal_threshold(claim_type)
    return CoverageResult(
        applies=headcount >= threshold,
        threshold=threshold,
        claim_type=claim_type,
        driving_jurisdiction=None,
        confidence="FEDERAL_FALLBACK",
        partial_state_flag=bool(partial_entries),
        partial_jurisdictions_considered=partial_jids,
    )


def _cluster_4_curve_for_org_type('''

EDIT4_NEW = '''    threshold = _federal_threshold(claim_type)
    return CoverageResult(
        applies=headcount >= threshold,
        threshold=threshold,
        claim_type=claim_type,
        driving_jurisdiction=None,
        confidence="FEDERAL_FALLBACK",
        partial_state_flag=bool(partial_entries),
        partial_jurisdictions_considered=partial_jids,
    )


# -- Damages-cap-treatment resolution (Phase 1) -------------------------------
# prompts/damages-cap-treatment-phase1-spec.md. Highest-exposure-wins
# resolution across an org's selected jurisdictions, paralleling
# resolve_coverage_gate()'s own "most-protective wins" pattern but for
# damages_cap_treatment rather than coverage-threshold applicability --
# a related but genuinely separate question (this determines the SHAPE
# of dollar exposure once coverage already applies, not whether it
# applies at all).

_DAMAGES_TREATMENT_PRIORITY: dict[str, int] = {
    "uncapped": 4,
    "state_specific_tiers": 3,
    "state_specific_flat": 3,
    "federal_cap_applies": 2,
    "no_damages_available": 1,
}


def resolve_damages_treatment(jurisdictions: list[str]) -> str:
    """
    Highest-exposure-wins damages_cap_treatment across the CONFIRMED-
    confidence jurisdictions in the input: uncapped > state_specific_tiers
    / state_specific_flat (peers -- both mean "a real independent state
    cap exists"; this function doesn't need to break a tie between the
    two shapes, since a caller cares whether a cap exists and how it's
    shaped, not which shape wins a multi-state tie) > federal_cap_applies
    > no_damages_available.

    PARTIAL-confidence entries never drive this determination -- same
    discipline as resolve_coverage_gate(), though every entry in
    STATE_COVERAGE_THRESHOLDS is CONFIRMED as of the completed
    PARTIAL-state verification workstream (2026-09-10), so this is a
    defensive convention match today, not a live behavior difference.

    Empty input, or a jurisdictions list with no CONFIRMED entry found,
    falls back to "federal_cap_applies" -- the real-world-correct
    default (no verified state law in play means federal law is what
    actually governs). Confirmed NOT a literal code-level match to
    resolve_coverage_gate()'s own "FEDERAL_FALLBACK" convention before
    this function was written, not assumed: that function has no
    damages_cap_treatment-shaped return value to mirror. Same
    underlying real-world legal reasoning, different data shape.
    """
    best: Optional[str] = None
    best_rank = -1
    for jid in jurisdictions:
        entry = STATE_COVERAGE_THRESHOLDS.get(jid)
        if entry is None or entry.confidence != "CONFIRMED":
            continue
        rank = _DAMAGES_TREATMENT_PRIORITY.get(entry.damages_cap_treatment, -1)
        if rank > best_rank:
            best_rank = rank
            best = entry.damages_cap_treatment
    return best if best is not None else "federal_cap_applies"


def _resolve_flat_cap(jurisdictions: list[str]) -> Optional[float]:
    """
    Maximum flat_cap among CONFIRMED state_specific_flat jurisdictions
    in the input -- extends resolve_damages_treatment()'s own
    highest-exposure-wins principle down to the actual dollar figure,
    needed because that function returns a category string, not a
    specific state; with more than one state_specific_flat jurisdiction
    selected, something has to pick which state's own flat_cap governs.
    None if no CONFIRMED state_specific_flat jurisdiction is present in
    the input, or if one is present but its flat_cap is unpopulated (a
    data gap, not expected once all 4 real flat_cap states are
    populated).
    """
    best: Optional[float] = None
    for jid in jurisdictions:
        entry = STATE_COVERAGE_THRESHOLDS.get(jid)
        if entry is None or entry.confidence != "CONFIRMED":
            continue
        if entry.damages_cap_treatment != "state_specific_flat":
            continue
        if entry.flat_cap is None:
            continue
        if best is None or entry.flat_cap > best:
            best = entry.flat_cap
    return best


def _cluster_4_curve_for_org_type('''

# ---- Edit 6: Cluster 1 branch ------------------------------------------------

EDIT6_OLD = '''    if cluster == 1:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
        v = _legal_score_fraction(_CLUSTER_1_CURVE, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)'''

EDIT6_NEW = '''    if cluster == 1:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
        treatment = resolve_damages_treatment(jurisdictions)
        if treatment == "no_damages_available" and headcount < _FEDERAL_DEFAULT_THRESHOLD:
            # State law bars damages outright and federal coverage
            # doesn't independently attach below its own 15-employee
            # floor -- genuinely no exposure to price, not an
            # unpriced-but-real one. Phase 1, prompts/damages-cap-
            # treatment-phase1-spec.md item 2.
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag)
        flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
        curve = _CLUSTER_1_CURVE if flat_cap is None else LegalDollarCurve(
            floor=_CLUSTER_1_CURVE.floor, ceiling=min(_CLUSTER_1_CURVE.ceiling, flat_cap),
        )
        v = _legal_score_fraction(curve, score)
        is_floor = treatment == "uncapped" or flat_cap is not None
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
            is_floor=is_floor)'''

# ---- Edit 7: Cluster 2 branch ------------------------------------------------

EDIT7_OLD = '''    if cluster == 2:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)'''

EDIT7_NEW = '''    if cluster == 2:
        coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
        if not coverage.applies:
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)
        treatment = resolve_damages_treatment(jurisdictions)
        if treatment == "no_damages_available" and headcount < _FEDERAL_DEFAULT_THRESHOLD:
            # Same federal-floor branch as Cluster 1 above. Cluster 2's
            # dollar values are two fixed discrete tiers, not a curve --
            # no clamp or is_floor applies here, structurally exempt
            # from items 3/4, only item 2's applicability question
            # reaches Cluster 2.
            return LegalPricingResult(status=LegalPricingStatus.NOT_APPLICABLE, dollar_range=None,
                coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag)
        r = _CLUSTER_2_TIER_2A if score == 1 else _CLUSTER_2_TIER_2B
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=r,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag)'''

# ---- Edit 8: Cluster 4 branch (pass through is_floor) -----------------------

EDIT8_OLD = '''    if cluster == 4:
        lookup = _cluster_4_curve_for_org_type(org_type, org_size, headcount, jurisdictions)
        if lookup.curve is None:
            return LegalPricingResult(status=lookup.status, dollar_range=None,
                coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)
        v = _legal_score_fraction(lookup.curve, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)'''

EDIT8_NEW = '''    if cluster == 4:
        lookup = _cluster_4_curve_for_org_type(org_type, org_size, headcount, jurisdictions)
        if lookup.curve is None:
            return LegalPricingResult(status=lookup.status, dollar_range=None,
                coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)
        v = _legal_score_fraction(lookup.curve, score)
        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),
            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag,
            is_floor=lookup.is_floor)'''

# ---- Edit 9: _cluster_4_curve_for_org_type (Cluster 4b) --------------------

EDIT9_OLD = '''    coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
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
    )'''

EDIT9_NEW = '''    coverage = resolve_coverage_gate(headcount, jurisdictions, claim_type="general")
    if not coverage.applies:
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.NOT_APPLICABLE,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        )
    treatment = resolve_damages_treatment(jurisdictions)
    if treatment == "no_damages_available" and headcount < _FEDERAL_DEFAULT_THRESHOLD:
        # Same federal-floor branch as Clusters 1/2 above -- state law
        # bars damages outright and federal coverage doesn't
        # independently attach below its own 15-employee floor. Phase
        # 1, prompts/damages-cap-treatment-phase1-spec.md item 2.
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.NOT_APPLICABLE,
            coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag,
        )
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)
    if ceiling is None:
        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.DATA_INTEGRITY_GAP,
            coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        )
    flat_cap = _resolve_flat_cap(jurisdictions) if treatment == "state_specific_flat" else None
    final_ceiling = ceiling if flat_cap is None else min(ceiling, flat_cap)
    is_floor = treatment == "uncapped" or flat_cap is not None
    return LegalCurveLookup(
        curve=LegalDollarCurve(floor=_CLUSTER_4B_FLOOR, ceiling=final_ceiling),
        status=LegalPricingStatus.PRICED,
        coverage_confidence=coverage.confidence, partial_state_flag=coverage.partial_state_flag,
        is_floor=is_floor,
    )'''

# ---- Edit 10: flat_cap values on FL/ID/KS/VA data rows ---------------------

FL_OLD = '''    "FL": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="state_specific_flat",  # flat $100,000 punitive cap, no size-based tiers, Fla. Stat. §760.11(5) (confirmed consistent across a decade of statute versions)
        confidence="CONFIRMED",
        citation="Florida Civil Rights Act, Fla. Stat. §760.10.",
    ),'''

FL_NEW = '''    "FL": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="state_specific_flat",  # flat $100,000 punitive cap, no size-based tiers, Fla. Stat. §760.11(5) (confirmed consistent across a decade of statute versions)
        confidence="CONFIRMED",
        citation="Florida Civil Rights Act, Fla. Stat. §760.10.",
        flat_cap=100_000.0,
    ),'''

ID_OLD = '''    "ID": StateCoverageThreshold(
        thresholds={"general": 5},
        damages_cap_treatment="state_specific_flat",  # Idaho Code §67-5908(3)(e) -- punitive damages capped at a flat $1,000 per willful violation, a single statutory ceiling, not employer-size tiers; actual/economic damages available separately, uncapped by this provision
        confidence="CONFIRMED",
        citation="Idaho Human Rights Act, Idaho Code §67-5902(6); §67-5908(3)(e).",
    ),'''

ID_NEW = '''    "ID": StateCoverageThreshold(
        thresholds={"general": 5},
        damages_cap_treatment="state_specific_flat",  # Idaho Code §67-5908(3)(e) -- punitive damages capped at a flat $1,000 per willful violation, a single statutory ceiling, not employer-size tiers; actual/economic damages available separately, uncapped by this provision
        confidence="CONFIRMED",
        citation="Idaho Human Rights Act, Idaho Code §67-5902(6); §67-5908(3)(e).",
        flat_cap=1_000.0,
    ),'''

KS_OLD = '''    "KS": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_flat",  # $2,000 flat cap on pain/suffering/humiliation damages specifically, not scaled by employer size, K.S.A. §44-1005(k); no punitive damages authority under KAAD
        confidence="CONFIRMED",
        citation="Kansas Act Against Discrimination, K.S.A. §44-1009; §44-1005(k); Woods v. Midwest Conveyor Co.; Sporleder v. U.S. Bancorp.",
    ),'''

KS_NEW = '''    "KS": StateCoverageThreshold(
        thresholds={"general": 4},
        damages_cap_treatment="state_specific_flat",  # $2,000 flat cap on pain/suffering/humiliation damages specifically, not scaled by employer size, K.S.A. §44-1005(k); no punitive damages authority under KAAD
        confidence="CONFIRMED",
        citation="Kansas Act Against Discrimination, K.S.A. §44-1009; §44-1005(k); Woods v. Midwest Conveyor Co.; Sporleder v. U.S. Bancorp.",
        flat_cap=2_000.0,
    ),'''

VA_OLD = '''    "VA": StateCoverageThreshold(
        thresholds={"general": 5},
        damages_cap_treatment="state_specific_flat",  # flat $350,000 punitive cap, Va. Code §8.01-38.1 (confirmed unchanged)
        confidence="CONFIRMED",
        citation="Va. Code §2.2-3905, as amended by SB 637 (Va. Acts ch. 950, 2026), eff. July 1, 2026 -- Virginia Human Rights Act employer threshold now 5, applying uniformly across all protected classes and claim types; the prior 5-20-employee age-discrimination-only carve-out is repealed entirely, not just the general threshold.",
    ),'''

VA_NEW = '''    "VA": StateCoverageThreshold(
        thresholds={"general": 5},
        damages_cap_treatment="state_specific_flat",  # flat $350,000 punitive cap, Va. Code §8.01-38.1 (confirmed unchanged)
        confidence="CONFIRMED",
        citation="Va. Code §2.2-3905, as amended by SB 637 (Va. Acts ch. 950, 2026), eff. July 1, 2026 -- Virginia Human Rights Act employer threshold now 5, applying uniformly across all protected classes and claim types; the prior 5-20-employee age-discrimination-only carve-out is repealed entirely, not just the general threshold.",
        flat_cap=350_000.0,
    ),'''

EDITS = [
    ('LegalPricingResult.is_floor', EDIT1_OLD, EDIT1_NEW),
    ('LegalCurveLookup.is_floor', EDIT2_OLD, EDIT2_NEW),
    ('StateCoverageThreshold.flat_cap + docstring', EDIT3_OLD, EDIT3_NEW),
    ('resolve_damages_treatment() + _resolve_flat_cap()', EDIT4_OLD, EDIT4_NEW),
    ('Cluster 1 branch', EDIT6_OLD, EDIT6_NEW),
    ('Cluster 2 branch', EDIT7_OLD, EDIT7_NEW),
    ('Cluster 4 branch (pass through is_floor)', EDIT8_OLD, EDIT8_NEW),
    ('_cluster_4_curve_for_org_type (Cluster 4b)', EDIT9_OLD, EDIT9_NEW),
    ('FL flat_cap', FL_OLD, FL_NEW),
    ('ID flat_cap', ID_OLD, ID_NEW),
    ('KS flat_cap', KS_OLD, KS_NEW),
    ('VA flat_cap', VA_OLD, VA_NEW),
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
