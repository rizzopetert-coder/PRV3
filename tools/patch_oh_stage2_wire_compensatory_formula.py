"""
PRV3 -- Stage 2 of the OH compensatory-damages pricing build (Priority
Queue item 9). Wires the real R.C. 2315.21 formula into
_single_state_legal_pricing() (Clusters 1, 2, 4b), via a new shared
_oh_compensatory_damages_pricing() helper:

  compensatory_base = _INDUSTRY_WAGE_DATA[industry] x
  _JURISDICTION_MULTIPLIER_DATA["OH"] (Stage 1). General employer: 2x
  compensatory, uncapped, is_floor=True. Small employer/individual
  defendant (_oh_is_small_employer()): 2x compensatory, hard-capped at
  $350,000 -- the real statutory cap also allows 10% of net worth as an
  alternative, but net_worth is not collected at intake, so this can
  OVERSTATE the real cap for a low-net-worth org. Flagged via a new
  field, may_overstate_for_uncollected_net_worth, added to both
  LegalPricingResult and LegalCurveLookup (Pete-confirmed field name and
  design -- a new field, not an inverted reuse of is_floor, since is_floor
  means the opposite direction everywhere else in this file).

Cluster 4b (_cluster_4_curve_for_org_type()) gained a new required
industry parameter (previously unused by that function) so its own Ohio
branch can reach _INDUSTRY_WAGE_DATA. Its OH branch converts
_oh_compensatory_damages_pricing()'s LegalPricingResult into this
function's own LegalCurveLookup shape via a flat curve (floor == ceiling)
-- _legal_score_fraction(curve, score) collapses to exactly `floor` for
any score when floor == ceiling, confirmed by reading that function's
own body, not assumed -- so Ohio's dollar figure reaches the final
LegalPricingResult unscaled by score, matching Clusters 1/2's own
unscaled dollar_range=(v, v).

coverage_confidence/partial_state_flag are threaded through from each
call site's own already-resolved coverage gate, replacing the prior
QUALITATIVE_ONLY early-returns' hardcoded "NOT_APPLICABLE"/False -- that
hardcoding was fine with no dollar figure to caveat; now that this is
PRICED, every other PRICED branch in this function threads real
coverage info through, and Ohio should not be the one exception.

Verification before this patch was written (see this session's own
report): 189/189 tests pass (tools/test_friction_tax.py, itself updated
in a companion, non-engine change), validate.py baseline unchanged
(37/4, same 4 pre-existing unrelated failures), and a 36,000-combination
ripple check (all 30 Legal-scoring taxonomy states x all 50 non-OH
CONFIRMED jurisdictions x industry/headcount/org_type/org_size variation)
confirmed ZERO behavioral change for any non-OH jurisdiction and
confirmed the new field defaults to False in every one of those cases.

This patch's EDITS are derived mechanically (Python difflib, line-level,
merged across small gaps) from the actual before/after file states, not
retyped by hand -- avoids transcription error in a change this size.

Usage:
  python tools/patch_oh_stage2_wire_compensatory_formula.py --dry-run
  python tools/patch_oh_stage2_wire_compensatory_formula.py --write
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

edit(
    F,
    '    itself before this build."""\n    status: LegalPricingStatus\n    dollar_range: Optional[tuple[float, float]]\n    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]\n    partial_state_flag: bool\n    is_floor: bool = False\n',
    '    itself before this build.\n\n    may_overstate_for_uncollected_net_worth (Priority Queue item 9,\n    this session -- Ohio\'s R.C. 2315.21 compensatory-damages build) is\n    the opposite direction from is_floor, deliberately kept as its own\n    field rather than an inverted reuse of is_floor: the small-employer/\n    individual-defendant branch\'s real statutory cap is\n    min(2x compensatory, 10% of net worth, $350,000), but net_worth\n    isn\'t collected at intake, so this codebase computes\n    min(2x compensatory, $350,000) -- a figure that can be HIGHER than\n    the real cap for a low-net-worth organization, not lower. Reusing\n    is_floor here (even inverted) would make one field mean opposite\n    things depending on which branch set it. False by default so every\n    pre-existing construction site needs no change; set True only by\n    Ohio\'s small-employer branch. Not yet consumed by any output layer\n    -- same "no consumer yet" status is_floor itself already carries;\n    UI-facing framing is explicitly out of scope for this build."""\n    status: LegalPricingStatus\n    dollar_range: Optional[tuple[float, float]]\n    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]\n    partial_state_flag: bool\n    is_floor: bool = False\n    may_overstate_for_uncollected_net_worth: bool = False\n',
)

edit(
    F,
    '    _single_state_legal_pricing()\'s Cluster 4 branch."""\n    curve: Optional[LegalDollarCurve]\n    status: LegalPricingStatus\n    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]\n    partial_state_flag: bool\n    is_floor: bool = False\n',
    '    _single_state_legal_pricing()\'s Cluster 4 branch.\n    may_overstate_for_uncollected_net_worth carries the same meaning as\n    LegalPricingResult\'s own field of that name (Priority Queue item 9,\n    this session) -- forwarded the same way, for Ohio\'s Cluster 4b\n    small-employer branch specifically."""\n    curve: Optional[LegalDollarCurve]\n    status: LegalPricingStatus\n    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"]\n    partial_state_flag: bool\n    is_floor: bool = False\n    may_overstate_for_uncollected_net_worth: bool = False\n',
)

edit(
    F,
    '        # tort, up to $350,000 (R.C. 2315.21(D)(2)(b)). Resolved\n        # QUALITATIVE_ONLY -- this codebase has no compensatory-damages-\n        # specific figure to apply either multiplier to, and does not\n        # collect net_worth. Small-employer routing (were it ever wired\n        # in -- see _oh_is_small_employer()) uses this app\'s\n        # "Manufacturing & Industrial" industry bucket as an\n        # approximation of Ohio\'s NAICS-manufacturing test -- confirmed\n        # this session that the two are not identical (the app bucket may\n        # sweep in adjacent non-manufacturing industrial activity like\n        # utilities or mining); flagged here, not resolved, since no\n        # NAICS-level intake data exists to resolve it precisely.\n',
    '        # tort, up to $350,000 (R.C. 2315.21(D)(2)(b)). Wired to PRICED\n        # (Priority Queue item 9, this session) -- see\n        # _oh_compensatory_damages_pricing() for the real formula:\n        # compensatory base = _INDUSTRY_WAGE_DATA x\n        # _JURISDICTION_MULTIPLIER_DATA["OH"] (prompts/oh-compensatory-\n        # damages-pricing-plan.md). The small-employer/individual-\n        # defendant branch omits the "OR 10% of net worth" alternative\n        # entirely -- net_worth still isn\'t collected at intake -- so its\n        # computed figure can OVERSTATE the real cap for a low-net-worth\n        # organization; flagged via\n        # LegalPricingResult.may_overstate_for_uncollected_net_worth, not\n        # silently accepted. Small-employer routing (see\n        # _oh_is_small_employer()) uses this app\'s "Manufacturing &\n        # Industrial" industry bucket as an approximation of Ohio\'s\n        # NAICS-manufacturing test -- confirmed this session that the two\n        # are not identical (the app bucket may sweep in adjacent\n        # non-manufacturing industrial activity like utilities or\n        # mining); flagged here, not resolved, since no NAICS-level\n        # intake data exists to resolve it precisely.\n',
)

edit(
    F,
    "    Unlike CO's helper, this carries no headcount gate -- Ohio's\n    QUALITATIVE_ONLY status applies at every headcount; headcount only\n    selects which of R.C. 2315.21's two statutory branches would\n    govern (see _oh_is_small_employer() below), a question this\n    function doesn't answer.\n",
    "    Unlike CO's helper, this carries no headcount gate -- Ohio's real\n    formula applies at every headcount (Priority Queue item 9, this\n    session -- previously QUALITATIVE_ONLY at every headcount, before\n    that formula was wired in); headcount only selects which of R.C.\n    2315.21's two statutory branches would govern (see\n    _oh_is_small_employer() below), a question this function doesn't\n    answer.\n",
)

edit(
    F,
    "    Deliberately NOT called by any of the three damages_cap_treatment\n    pricing branches (Clusters 1, 2, 4b) -- both of R.C. 2315.21's\n    branches resolve to the identical QUALITATIVE_ONLY\n    LegalPricingResult today (no compensatory-damages figure exists in\n    this codebase to apply either multiplier to, and net_worth isn't\n    collected regardless of which branch applies), so invoking this\n    helper there would compute a real answer and then discard it. It's\n    a standalone, directly-tested piece of correct logic, ready for\n    whenever a future citation/prose distinction or a real pricing\n    path for either R.C. 2315.21 branch is built and actually consumes\n    it -- not wired into the pricing path prematurely.\n",
    "    Called by _oh_compensatory_damages_pricing() (Priority Queue item 9,\n    this session) to route between R.C. 2315.21's two branches, now that\n    a real compensatory-damages base exists (_JURISDICTION_MULTIPLIER_DATA\n    x _INDUSTRY_WAGE_DATA) for both branches to apply their multiplier\n    to. Previously deliberately uncalled -- both branches resolved to\n    the identical QUALITATIVE_ONLY LegalPricingResult, so invoking this\n    helper would have computed a real answer and then discarded it.\n",
)

edit(
    F,
    'def _cluster_4_curve_for_org_type(\n    org_type: str, org_size: str, headcount: int, jurisdictions: list[str]\n) -> LegalCurveLookup:\n    """\n',
    '# R.C. 2315.21(D)(2)(b) -- the small-employer/individual-defendant hard\n# ceiling. Confirmed real statutory figure, not a placeholder.\n_OH_SMALL_EMPLOYER_CAP: float = 350_000.0\n\n\ndef _oh_compensatory_damages_pricing(\n    industry: str,\n    headcount,\n    coverage_confidence: Literal["CONFIRMED", "FEDERAL_FALLBACK", "NOT_APPLICABLE"],\n    partial_state_flag: bool,\n) -> LegalPricingResult:\n    """\n    Ohio\'s own R.C. 2315.21 compensatory-damages formula (Priority Queue\n    item 9, this session). Shared by all three call sites that can reach\n    Ohio\'s state_specific_tiers treatment -- Clusters 1, 2, and 4b (via\n    _cluster_4_curve_for_org_type(), which wraps this into a flat\n    LegalDollarCurve -- see that call site) -- since the underlying legal\n    question (which of R.C. 2315.21\'s two branches applies, and for how\n    much) doesn\'t depend on which Legal-scoring taxonomy state triggered\n    the check.\n\n    compensatory_base = _INDUSTRY_WAGE_DATA[industry]\'s real BLS OEWS wage\n    x _JURISDICTION_MULTIPLIER_DATA["OH"]\'s EEOC/QCEW-derived litigation-\n    risk multiplier (prompts/oh-compensatory-damages-pricing-plan.md).\n    "OH" is hardcoded, not looked up from a jurisdictions list -- this\n    function is only ever reached once _oh_drives_tiers_result() has\n    already confirmed Ohio specifically governs, so the multiplier for\n    the governing jurisdiction is always Ohio\'s own.\n\n    General employer (_oh_is_small_employer() False): 2x compensatory,\n    uncapped -- is_floor=True, standard semantics (this figure may\n    understate the real answer, same as every other "uncapped" treatment\n    in this file).\n\n    Small employer/individual defendant (True): 2x compensatory, hard-\n    capped at _OH_SMALL_EMPLOYER_CAP. The real statutory cap is\n    min(2x compensatory, 10% of net worth, $350,000) -- net_worth isn\'t\n    collected at intake, so this omits that third term entirely. The\n    result is is_floor=False (this is a hard ceiling, not a floor) AND\n    may_overstate_for_uncollected_net_worth=True (a low-net-worth\n    organization\'s real cap could be lower than what\'s computed here --\n    the opposite direction from every other is_floor=True caveat in this\n    file, which is exactly why this is its own field, not a reused one).\n\n    coverage_confidence/partial_state_flag are threaded through from the\n    caller\'s own already-resolved coverage gate (or Cluster 4b\'s own\n    lookup) rather than hardcoded to "NOT_APPLICABLE"/False -- the prior\n    QUALITATIVE_ONLY early-returns this replaces discarded that real\n    information because there was no dollar figure to caveat with it;\n    now that this is PRICED, every other PRICED branch in this function\n    threads it through, and Ohio shouldn\'t be the one exception.\n\n    Returns DATA_INTEGRITY_GAP if industry isn\'t a recognized\n    _INDUSTRY_WAGE_DATA key -- should never happen against real\n    IntakeData.industry values (confirmed against the live\n    engine/data/intake.py INTAKE_FIELDS list), so this signals a real\n    data problem rather than an intentional design outcome, same\n    convention as every other DATA_INTEGRITY_GAP in this file.\n    """\n    wage_entry = _INDUSTRY_WAGE_DATA.get(industry)\n    if wage_entry is None:\n        _logger.warning(\n            "OH compensatory-damages pricing data-integrity gap: "\n            "unrecognized industry=%r has no _INDUSTRY_WAGE_DATA entry",\n            industry,\n        )\n        return LegalPricingResult(status=LegalPricingStatus.DATA_INTEGRITY_GAP, dollar_range=None,\n            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)\n    compensatory_base = wage_entry[0] * _JURISDICTION_MULTIPLIER_DATA["OH"][0]\n    if _oh_is_small_employer(headcount, industry):\n        v = min(2.0 * compensatory_base, _OH_SMALL_EMPLOYER_CAP)\n        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),\n            coverage_confidence=coverage_confidence, partial_state_flag=partial_state_flag,\n            is_floor=False, may_overstate_for_uncollected_net_worth=True)\n    v = 2.0 * compensatory_base\n    return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),\n        coverage_confidence=coverage_confidence, partial_state_flag=partial_state_flag,\n        is_floor=True)\n\n\ndef _cluster_4_curve_for_org_type(\n    org_type: str, org_size: str, headcount: int, jurisdictions: list[str], industry: str,\n) -> LegalCurveLookup:\n    """\n    industry (Priority Queue item 9, this session) is used only by the\n    Ohio state_specific_tiers branch below, to look up\n    _INDUSTRY_WAGE_DATA for _oh_compensatory_damages_pricing(). Every\n    other branch in this function is industry-independent, unchanged.\n\n',
)

edit(
    F,
    '        # Same reasoning as Clusters 1/2 -- Ohio\'s real cap can\'t be\n        # computed by this codebase today. Returned before the ceiling\n        # lookup below, unlike Colorado\'s branch above (which relabels\n        # treatment and lets normal resolution continue) -- Ohio has no\n        # substitute number to fall through to. Phase 2b, prompts/\n        # damages-cap-treatment-phase2-spec.md.\n        return LegalCurveLookup(\n            curve=None, status=LegalPricingStatus.QUALITATIVE_ONLY,\n            coverage_confidence="NOT_APPLICABLE", partial_state_flag=False,\n',
    "        # Ohio's real formula, wired in (Priority Queue item 9, this\n        # session). Returned before the ceiling lookup below, same shape\n        # as before this build -- Ohio's own formula is independent of\n        # Cluster 4b's headcount-bracket ceiling table entirely.\n        # Converted from _oh_compensatory_damages_pricing()'s\n        # LegalPricingResult into this function's own LegalCurveLookup\n        # shape via a flat curve (floor == ceiling): _legal_score_fraction\n        # (curve, score) = floor * (ceiling/floor)**(score-1) collapses to\n        # exactly `floor` for any score when floor == ceiling (that ratio\n        # is 1, and 1**anything == 1) -- confirmed by reading\n        # _legal_score_fraction()'s own body, not assumed -- so this\n        # formula's dollar figure reaches the final LegalPricingResult\n        # unscaled by score, matching Clusters 1/2's own unscaled\n        # dollar_range=(v, v).\n        oh_result = _oh_compensatory_damages_pricing(\n            industry, headcount, coverage.confidence, coverage.partial_state_flag,\n        )\n        if oh_result.status != LegalPricingStatus.PRICED:\n            return LegalCurveLookup(\n                curve=None, status=oh_result.status,\n                coverage_confidence=oh_result.coverage_confidence,\n                partial_state_flag=oh_result.partial_state_flag,\n            )\n        oh_v = oh_result.dollar_range[0]\n        return LegalCurveLookup(\n            curve=LegalDollarCurve(floor=oh_v, ceiling=oh_v),\n            status=LegalPricingStatus.PRICED,\n            coverage_confidence=oh_result.coverage_confidence,\n            partial_state_flag=oh_result.partial_state_flag,\n            is_floor=oh_result.is_floor,\n            may_overstate_for_uncollected_net_worth=oh_result.may_overstate_for_uncollected_net_worth,\n",
)

edit(
    F,
    '            # Ohio\'s real cap can\'t be computed by this codebase today --\n            # confirmed this session: no cluster\'s dollar curve represents\n            # a compensatory-damages figure (Cluster 1\'s included), which\n            # both of R.C. 2315.21\'s branches multiply against, and the\n            # small-employer/individual-defendant branch additionally\n            # needs net_worth, never collected at intake. Real, non-zero\n            # exposure exists -- QUALITATIVE_ONLY, mirroring Cluster 3\'s\n            # unclassifiable-headcount precedent (a number genuinely\n            # can\'t be resolved) rather than Cluster 4c\'s Government case\n            # (no data exists by design) -- confirmed this session these\n            # are two structurally different existing QUALITATIVE_ONLY\n            # consumers, not one. _oh_is_small_employer() computes which\n            # of R.C. 2315.21\'s two branches would govern, for\n            # correctness and future use -- not called here, since both\n            # branches resolve identically today. Phase 2b, prompts/\n            # damages-cap-treatment-phase2-spec.md.\n            return LegalPricingResult(status=LegalPricingStatus.QUALITATIVE_ONLY, dollar_range=None,\n                coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)\n',
    "            # Ohio's real formula, wired in (Priority Queue item 9, this\n            # session) -- see _oh_compensatory_damages_pricing()'s own\n            # docstring for the full formula, the small-employer net-\n            # worth caveat, and why coverage_confidence/partial_state_flag\n            # are threaded through here rather than hardcoded.\n            return _oh_compensatory_damages_pricing(\n                industry, headcount, coverage.confidence, coverage.partial_state_flag,\n            )\n",
)

edit(
    F,
    '            # Same reasoning as Cluster 1 above -- Ohio\'s real cap can\'t\n            # be computed by this codebase today (no compensatory-damages\n            # figure exists anywhere, net_worth isn\'t collected). Phase\n            # 2b, prompts/damages-cap-treatment-phase2-spec.md.\n            return LegalPricingResult(status=LegalPricingStatus.QUALITATIVE_ONLY, dollar_range=None,\n                coverage_confidence="NOT_APPLICABLE", partial_state_flag=False)\n',
    "            # Same reasoning as Cluster 1 above -- Ohio's real formula,\n            # wired in (Priority Queue item 9, this session). See\n            # _oh_compensatory_damages_pricing()'s own docstring.\n            return _oh_compensatory_damages_pricing(\n                industry, headcount, coverage.confidence, coverage.partial_state_flag,\n            )\n",
)

edit(
    F,
    '        lookup = _cluster_4_curve_for_org_type(org_type, org_size, headcount, jurisdictions)\n        if lookup.curve is None:\n            return LegalPricingResult(status=lookup.status, dollar_range=None,\n                coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)\n        v = _legal_score_fraction(lookup.curve, score)\n        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),\n            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag,\n            is_floor=lookup.is_floor)\n',
    '        lookup = _cluster_4_curve_for_org_type(org_type, org_size, headcount, jurisdictions, industry)\n        if lookup.curve is None:\n            return LegalPricingResult(status=lookup.status, dollar_range=None,\n                coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag)\n        v = _legal_score_fraction(lookup.curve, score)\n        return LegalPricingResult(status=LegalPricingStatus.PRICED, dollar_range=(v, v),\n            coverage_confidence=lookup.coverage_confidence, partial_state_flag=lookup.partial_state_flag,\n            is_floor=lookup.is_floor,\n            may_overstate_for_uncollected_net_worth=lookup.may_overstate_for_uncollected_net_worth)\n',
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
