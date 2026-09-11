"""
engine/friction_tax.py: Phase 2a of damages_cap_treatment
(prompts/damages-cap-treatment-phase2-spec.md) -- AR, DE, TN, MD, MO,
TX, CO.

AR/DE/TN/TX: confirmed this session to need ZERO code changes -- their
tier data is already genuinely unconsumed, same generic-curve-plus-
is_floor=True treatment every state_specific_tiers state already gets
via Phase 1's corrections (is_floor is computed generically from the
resolved treatment category, not stored per-state, so TX already
inherits is_floor=True today).

MD/MO: new is_combined_cap field on StateCoverageThreshold, set True
for these two only -- their own comments already confirm a combined
compensatory-and-punitive cap. Not consumed by any pricing logic yet,
same as flat_cap's incremental-encoding precedent in Phase 1.

CO: new _co_drives_federal_tier_deferral() helper + one new branch in
_cluster_4_curve_for_org_type() only (NOT Cluster 1 -- confirmed this
session that Cluster 1's curve is an unrelated generic methodology,
not the federal Title VII bracket table CO's statute defers to; only
Cluster 4b's ceiling table already IS that federal table). At
headcount >= _FEDERAL_DEFAULT_THRESHOLD, when CO is confirmed to be the
specific jurisdiction driving a state_specific_tiers resolution
(not just present alongside a different driving tiers state), the
treatment label is swapped to "federal_cap_applies" for the rest of
that resolution -- the ceiling value doesn't change (Cluster 4b's
table already governs regardless), only is_floor flips to False, since
the number is now Colorado's own real, confirmed answer at that
headcount, not a placeholder.

Usage:
    python tools/patch_damages_cap_phase2a_build.py --dry-run
    python tools/patch_damages_cap_phase2a_build.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

# ---- Edit 1: StateCoverageThreshold dataclass -- is_combined_cap field ----

DATACLASS_OLD = '''    flat_cap:         Populated only for damages_cap_treatment ==
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

DATACLASS_NEW = '''    flat_cap:         Populated only for damages_cap_treatment ==
                      "state_specific_flat" states (FL, ID, KS, VA) --
                      the actual flat dollar figure from each state's
                      own citation, pulled directly from source (Phase
                      1, item 4). Clamped against the generic curve's
                      ceiling (min(curve.ceiling, flat_cap)) in Clusters
                      1 and 4b -- see resolve_damages_treatment() and
                      _resolve_flat_cap() below. None for every other
                      damages_cap_treatment value.
    is_combined_cap:  True only for MD and MO (Phase 2a) -- these two
                      states' own state_specific_tiers dollar figures
                      cap compensatory and punitive damages TOGETHER as
                      one combined number, confirmed directly against
                      each state's own statute text (MD: Md. State
                      Gov't Code Sec20-1013(e)(2); MO: RSMo
                      Sec213.111(4), which explicitly excludes back
                      pay/front pay from the same combined cap). False
                      (the default) for every other state, including
                      the other 7 state_specific_tiers states, whose
                      combined-vs-split structure has NOT been
                      independently verified either way -- False here
                      means "not confirmed combined," not "confirmed
                      split." Not consumed by any pricing logic yet --
                      same precedent as is_floor in Phase 1: encode the
                      statutory truth once confirmed, even before an
                      output layer exists to consume it, so a future
                      "detailed compensatory/punitive breakdown"
                      feature can't silently double-count a combined
                      cap as two independent ones.
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
    flat_cap: Optional[float] = None
    is_combined_cap: bool = False'''

# ---- Edit 2: MD entry -- is_combined_cap=True ----

MD_OLD = '''        damages_cap_treatment="state_specific_tiers",  # $50,000 (15-100 employees) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (501+), Md. State Gov't Code §20-1009(b)(3)
        confidence="CONFIRMED",
        citation="Md. State Gov't Code §20-601(d), §20-611, §20-1009(b)(3), §20-1013(e)(2).",
    ),'''

MD_NEW = '''        damages_cap_treatment="state_specific_tiers",  # $50,000 (15-100 employees) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (501+), Md. State Gov't Code §20-1009(b)(3)
        confidence="CONFIRMED",
        citation="Md. State Gov't Code §20-601(d), §20-611, §20-1009(b)(3), §20-1013(e)(2).",
        is_combined_cap=True,
    ),'''

# ---- Edit 3: MO entry -- is_combined_cap=True ----

MO_OLD = '''        damages_cap_treatment="state_specific_tiers",  # combined compensatory (non-pecuniary)-and-punitive cap: $50,000 (more than 5 and fewer than 101 employees, i.e. 6-100 -- matches MHRA's own 6-employee coverage threshold) / $100,000 (101-200) / $200,000 (201-500) / $500,000 (500+); back pay/front pay not subject to these caps
        confidence="CONFIRMED",
        citation="Missouri Human Rights Act, RSMo §213.010; §213.111(4); SB 43 eff. Aug. 28, 2017.",
    ),'''

MO_NEW = '''        damages_cap_treatment="state_specific_tiers",  # combined compensatory (non-pecuniary)-and-punitive cap: $50,000 (more than 5 and fewer than 101 employees, i.e. 6-100 -- matches MHRA's own 6-employee coverage threshold) / $100,000 (101-200) / $200,000 (201-500) / $500,000 (500+); back pay/front pay not subject to these caps
        confidence="CONFIRMED",
        citation="Missouri Human Rights Act, RSMo §213.010; §213.111(4); SB 43 eff. Aug. 28, 2017.",
        is_combined_cap=True,
    ),'''

# ---- Edit 4: new _co_drives_federal_tier_deferral() helper ----

HELPER_ANCHOR_OLD = '''def _cluster_4_curve_for_org_type(
    org_type: str, org_size: str, headcount: int, jurisdictions: list[str]
) -> LegalCurveLookup:'''

HELPER_ANCHOR_NEW = '''def _co_drives_federal_tier_deferral(jurisdictions: list[str], headcount) -> bool:
    """
    True only when Colorado is the SPECIFIC jurisdiction
    resolve_damages_treatment() would resolve a state_specific_tiers
    result from, AND headcount has cleared the federal 15-employee
    floor Colorado's own statute defers to at that point (C.R.S.
    Sec24-34-405(3)(d)(II)(A)/(II)(B)) -- Colorado's own comment is the
    only one among all 9 state_specific_tiers states that describes
    deferring to federal Title VII tiers at any headcount; the other 8
    keep their own (unmodeled) tiers at every headcount. Cannot be a
    blanket check on the resolved treatment string alone -- that would
    also fire for a jurisdictions list whose real driving state is TX,
    AR, etc. (also state_specific_tiers, but non-deferring).

    Re-derives resolve_damages_treatment()'s own priority-resolution
    loop rather than changing that function's return contract to
    additionally expose the winning jurisdiction -- three existing call
    sites and the test suite depend on it returning a bare string.

    Known limitation, not fixed here: if two state_specific_tiers
    jurisdictions tie for best_rank (e.g. CO and TX both selected),
    resolve_damages_treatment()'s own strict `>` comparison means
    whichever is encountered FIRST in the input list wins -- this
    function inherits that same input-order dependency rather than
    resolving it, since disambiguating which specific tiers state
    governs a multi-tiers-state selection is a pre-existing gap this
    Phase 2a build didn't create and isn't scoped to fix.
    """
    if not isinstance(headcount, (int, float)) or headcount < _FEDERAL_DEFAULT_THRESHOLD:
        return False
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
    return best_jid == "CO"


def _cluster_4_curve_for_org_type(
    org_type: str, org_size: str, headcount: int, jurisdictions: list[str]
) -> LegalCurveLookup:'''

# ---- Edit 5: Cluster 4b -- CO federal-deferral branch ----

CLUSTER4B_OLD = '''        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.NOT_APPLICABLE,
            coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag,
        )
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)'''

CLUSTER4B_NEW = '''        return LegalCurveLookup(
            curve=None, status=LegalPricingStatus.NOT_APPLICABLE,
            coverage_confidence="CONFIRMED", partial_state_flag=coverage.partial_state_flag,
        )
    if treatment == "state_specific_tiers" and _co_drives_federal_tier_deferral(jurisdictions, headcount):
        # Colorado's own statute explicitly defers to the federal Title
        # VII tier table at 15+ employees -- swap in that treatment
        # label for the rest of this resolution. Cluster 4b's ceiling
        # table below IS that same federal bracket table already (per
        # its own comment), so the ceiling VALUE doesn't change here --
        # only is_floor does, since the number is now Colorado's own
        # real, confirmed answer at this headcount, not a placeholder.
        # Inverted shape vs. the no_damages_available branch above:
        # that one returns early BELOW its threshold; this one lets
        # normal resolution continue with a corrected label ABOVE one.
        # Phase 2a, prompts/damages-cap-treatment-phase2-spec.md.
        treatment = "federal_cap_applies"
    ceiling = _CLUSTER_4B_CEILING_BY_HEADCOUNT.get(org_size)'''

EDITS = [
    ('StateCoverageThreshold dataclass -- is_combined_cap field', DATACLASS_OLD, DATACLASS_NEW),
    ('MD entry -- is_combined_cap=True', MD_OLD, MD_NEW),
    ('MO entry -- is_combined_cap=True', MO_OLD, MO_NEW),
    ('_co_drives_federal_tier_deferral() helper', HELPER_ANCHOR_OLD, HELPER_ANCHOR_NEW),
    ('Cluster 4b -- CO federal-deferral branch', CLUSTER4B_OLD, CLUSTER4B_NEW),
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
