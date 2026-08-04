"""
PRV3 -- Fold Legal/Compliance Addendum 9 (administrative closeout: the
package is ready for Gemini as-is, OSHA jurisdictional research paused
not abandoned) into prompts/friction-tax-legal-compliance-methodology.md,
following Addendum 8. No Status line change -- Pete's framing is that
this is administrative closeout, not new design content.

Also restructures tools/_mob.txt's Section 13b Priority Queue as a full
atomic block replacement (safer than piecemeal edits given every item's
number shifts):
  - /diagnostic Stages 4-5 rescoping moves to the top (item 1),
    reconfirmed this session as the highest-leverage next step
  - The old combined item 3 (Legal/Compliance tail-risk methodology,
    grown long across 5 addenda) is split into two clean items per
    Pete's exact text: "Legal/Compliance package -- ready for Gemini
    review as-is" and "OSHA jurisdictional research -- PAUSED"
  - The old item 4 (Demographic Applicability Filter, which had evolved
    entirely into OSHA jurisdictional research content) is retired --
    its content is now the new "OSHA jurisdictional research" item
  - Item 5's stale "item 4" cross-reference (to the ADA/FMLA lead) is
    corrected to a name-based reference, since item 4 now means
    something different after this restructure

Usage:
  python tools/patch_legal_compliance_addendum9_and_priority_restructure.py --dry-run
  python tools/patch_legal_compliance_addendum9_and_priority_restructure.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM9_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum9_fixed.md"
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM9_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)


# ============================================================
# tools/_mob.txt -- full Priority Queue block replacement
# ============================================================

_OLD_QUEUE = """1. Option A rescale + multi-state compounding redesign IMPLEMENTED and verified this session (engine/friction_tax.py) -- CLOSES the item open since the output-ceiling bug was caught earlier this session. All 57 states' raw_score/multiplier recomputed under the new [0.05, 0.25] / [0, 6] mapping (Legal/Compliance excluded from the sum, its score preserved for the separate design); compute_friction_tax()'s mean_multiplier fully replaced with the Step 1-3 anchor-plus-diminishing-layers aggregation (geometric decay, K=0.05 breadth loading, N=1 guard forcing loading=1.0 for a single identified state). Verified, not just reasoned about: tools/test_friction_tax.py rewritten 37->45 checks, 45/45 pass, including explicit single-state continuity (bit-for-bit exact match across 10 real states), the N=1 guard, hand-derived Step 1/Step 3 multi-state math (two breadth scenarios), and extrapolation beyond R_max=6. All other engine test suites pass unaffected; 172-profile calibration suite unchanged at 169/172, confirming this change is isolated to Friction Tax and doesn't touch state routing/scoring; tsc clean (FrictionTaxEstimate's {low, high, currency} shape unaffected by the internal formula change).
2. Reopen the deferred "urgency window" (Diagnostic Dimension Expansion) alongside #1 -- same compounding design conversation applied to urgency, not dollar cost, done together rather than re-deriving the reasoning separately later.
3. Legal/Compliance tail-risk methodology -- sourcing and classification CLOSED (all 30 states across 5 clusters -- Cluster 1 now 4 states/was 3, Cluster 2 now 11 states/was 12, `the_untouchable` moved Cluster 2 -> Cluster 1 per Addendum 4, resolving Gemini's review flag; all 5 clusters have sourced dollar curves, Addenda 1-2; see prompts/friction-tax-legal-compliance-methodology.md). Cluster 3 interpolation LOCKED (Addendum 4): scope-modulated, not path-modulated -- the administrative ($1,465/worker) to litigation ($2,930/worker) range stays a fixed pair regardless of rubric score (preserving Addendum 2's genuine path-uncertainty), while the rubric score instead modulates affected-worker-count/scope via Cluster 2's existing per-capita mechanism, resolving the disagreement with Gemini's proposed binary step function. **Cluster 4 RESOLVED (Addendum 5) -- structural reframe, not a minor edit:** the original single "uncapped, sanction-driven" SEC-anchored curve only ever described one org_type's reality; replaced with three org_type-gated sub-tracks -- 4a SEC/Dodd-Frank (org_type=Publicly traded, unchanged design, correctly scoped now), 4b general private-sector retaliation (org_type=Founder-led/Privately held professional leadership/Nonprofit/most PE-VC-backed, anchored to 42 U.S.C. Sec 1981a(b)(3)'s statutory cap mapped onto PRV3's headcount buckets, $50K-$300K, California's uncapped FEHA flagged as the first concrete jurisdictions-override case), 4c government (org_type=Government, qualitative only -- no dollar figure, genuinely thin MSPB settlement data, not a research shortfall). See prompts/friction-tax-legal-compliance-methodology.md (Addendum 5). Cross-state aggregation (Addendum 3) now needs org_type-gating resolved before within-cluster decay can run for any Cluster 4 state -- not a structural change to Addendum 3 itself, but a new implementation prerequisite. Cross-state aggregation design is ready for Gemini review, alongside the rest of the Legal/Compliance package.
4. Demographic Applicability Filter -- systematic pass across Clusters 1, 2, 3, 5 -- IN PROGRESS. Jurisdictions pass -- California confirmed across all 5 clusters (Addendum 6): Cluster 1 (FEHA lowers ADA/Title VII's 15-employee threshold to 5, any size for harassment), Cluster 2 (CA exposure already captured indirectly via real-settlement per-claimant rates, no new gap), Cluster 3 (PAGA adds $100-200/aggrieved employee per pay period, compounds with time -- worked example: 50 employees, 26 pay periods, $130K/year in PAGA penalties alone before back wages), Cluster 4 (already resolved via Addendum 5's 4b caveat), Cluster 5 (Cal/OSHA serious-violation cap $25,000 vs. federal $16,550, ~51% higher). Bigger finding from this pass: 22 states run their own OSHA-approved State Plans required to be "at least as effective" as federal OSHA (equal or higher penalties, never lower) -- Cluster 5's flat federal figures are confirmed as a floor across ~22 states' worth of clients, not a national accuracy figure; materially bigger gap than the California findings themselves. Jurisdictions pass, Cluster 5 -- design locked (Addendum 8): statutory max + actual average, both as a range, consistent with the rest of the design's low/high presentation -- the two numbers can diverge enormously within one state (Oregon: $16,131 statutory vs. $604 actual average, ~27x gap). 11/22 states touched. Real gap: only Oregon has both numbers -- 10 states need backfill on actual-average data, ~11 states still fully unresearched. Scope larger than originally estimated: locking the both-numbers design expanded remaining work rather than closing it. Every state checked so far has produced a genuinely distinct finding -- no simple pattern has emerged, treat remaining research as comparable effort per state, not diminishing. CORRECTION (this session): Washington was originally miscategorized as exceeding federal; corrected and moved to clean parity alongside Alaska/Hawaii -- its WAC floor mechanisms (serious: federal max or $7,000; willful/repeat: federal max or $70,000, whichever is more) both currently sit below federal's own live maximums, so Washington's effective penalties equal federal's exactly. Other high-protection states outside the OSHA State Plan list (NY/MA/IL/WA candidates for other clusters) -- not started, real scoped gap, explicitly NOT assumed accurate by default. Original two leads from Addendum 5, still open: (a) ADA (15+ employees) / FMLA (50+ employees) coverage thresholds for Clusters 1 and 2's "Under 25" headcount bucket -- partially addressed for CA clients via FEHA's lower 5-employee threshold (Addendum 6), federal-baseline states still open, and see the separate intake headcount precision redesign proposal (item 5) which resolves this more completely once implemented; (b) `HIGH_HAZARD_INDUSTRIES` PULLED this session (engine/data/intake.py:285): `{"Manufacturing & Industrial", "Healthcare & Life Sciences"}` -- Construction and Logistics are NOT in the current intake industry list (per the file's own comment, pending intake list expansion if added), so Cluster 5's `is_high_hazard`-based gating can only ever cover these 2 of PRV3's 9 industry values as currently scoped; still needs building into Cluster 5's OSHA-based figures, not yet done.
5. Intake headcount precision redesign -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-headcount-precision-redesign.md). SCHEMA-LEVEL SCOPE -- larger than any other Friction Tax proposal this session: replaces the 6-value headcount bucket dropdown with a precise numeric "about how many employees" stepper (variable increment: steps of 1 from 1-50, 5 from 50-250, 25 from 250-500, 100 above 500). Originates directly from item 4's ADA/FMLA coverage-threshold lead -- a precise number resolves the bucket-boundary ambiguity completely. Also affects Cluster 4's Title VII damage-cap tiers (100/200/500) and Cluster 5's OSHA penalty-reduction tiers (25/100/250), both currently approximating against bucket edges that don't align with the real statutory boundaries. Blocks nothing currently in progress, but should be SEQUENCED BEFORE Clusters 1, 2, 4, 5 are finalized against Gemini, since their threshold logic changes once headcount is precise rather than bucketed -- reviewing those clusters against Gemini before this resolves risks reviewing logic that's about to change underneath it. Confirmed this session: no bucket-derivation logic exists anywhere in the codebase today -- PAYROLL_BASELINE_GRID and HEADCOUNT_MIDPOINTS (engine/friction_tax.py) are both keyed directly by the 6 bucket strings (built via `for headcount in HEADCOUNT_BUCKETS`), with no function anywhere that maps a precise int to a bucket; this would need to be built from scratch as part of implementation, not adapted from something existing. IntakeData.headcount's type change (str -> int) and whether IntakeEcho should echo a precise number or bucket-like language client-facing are both still open questions in the doc, not yet decided.
6. Intake industry taxonomy expansion -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-industry-taxonomy-expansion.md). SCHEMA-LEVEL SCOPE, same flag as item 5 -- second intake-schema proposal this session, kept deliberately separate from the headcount-precision redesign per Pete's direction, not combined. Adds "Construction" (NAICS Sector 23) and "Transportation & Warehousing" (NAICS Sectors 48-49) to INTAKE_FIELDS["industry"], expanding 9 -> 11 values. Originates from the Demographic Applicability Filter's Cluster 5 finding that is_high_hazard (HIGH_HAZARD_INDUSTRIES) can only ever fire for 2 of the 9 current industry values, while BLS ranks construction and transportation/warehousing among the highest injury/fatality-rate industries nationally -- both currently fall into "Other," indistinguishable from anything else that doesn't fit. REAL DEPENDENCY, not just a code change: PAYROLL_BASELINE_GRID expands from 6x9=54 cells to 6x11=66 cells -- 12 new cells (Construction and Transportation & Warehousing x all 6 headcount buckets) need genuine SUSB/BLS payroll-baseline research sourced before this is implementation-ready, comparable in scope to the original 54-cell population work, not trivial. HIGH_HAZARD_INDUSTRIES update itself is straightforward (add both new values to the existing set).
7. /diagnostic Stages 4-5 rescoping -- no surviving plan doc, requires Pete to rescope from scratch. Prioritized above other backlog items because it's a live user-facing surface gap, not because it's ready to start.
8. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.
9. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).
10. Infrastructure housekeeping, opportunistic/lower priority: weak-profile test limitation (generate_answers() weak branch ignoring target_state), calibration runner's untested severity follow-on questions (parked, do not raise unless Pete reopens), test_contract.py pre-existing liability_block KeyError, MemPalace drawer-write issue."""

_NEW_QUEUE = """1. /diagnostic Stages 4-5 rescoping -- TOP PRIORITY, reconfirmed this session by both Pete and Claude.ai as the highest-leverage next step: a live, user-facing surface gap with no implemented competitor for attention, unlike the Legal/Compliance items below, which remain entirely in design and unshipped. No surviving plan doc -- requires Pete to rescope from scratch.
2. Option A rescale + multi-state compounding redesign IMPLEMENTED and verified this session (engine/friction_tax.py) -- CLOSES the item open since the output-ceiling bug was caught earlier this session. All 57 states' raw_score/multiplier recomputed under the new [0.05, 0.25] / [0, 6] mapping (Legal/Compliance excluded from the sum, its score preserved for the separate design); compute_friction_tax()'s mean_multiplier fully replaced with the Step 1-3 anchor-plus-diminishing-layers aggregation (geometric decay, K=0.05 breadth loading, N=1 guard forcing loading=1.0 for a single identified state). Verified, not just reasoned about: tools/test_friction_tax.py rewritten 37->45 checks, 45/45 pass, including explicit single-state continuity (bit-for-bit exact match across 10 real states), the N=1 guard, hand-derived Step 1/Step 3 multi-state math (two breadth scenarios), and extrapolation beyond R_max=6. All other engine test suites pass unaffected; 172-profile calibration suite unchanged at 169/172, confirming this change is isolated to Friction Tax and doesn't touch state routing/scoring; tsc clean (FrictionTaxEstimate's {low, high, currency} shape unaffected by the internal formula change).
3. Reopen the deferred "urgency window" (Diagnostic Dimension Expansion) alongside #2 -- same compounding design conversation applied to urgency, not dollar cost, done together rather than re-deriving the reasoning separately later.
4. Legal/Compliance package -- ready for Gemini review as-is (full classification across 5 clusters, 5 sourced dollar curves, cross-state aggregation design, Cluster 4's org_type-gated reframe). See prompts/friction-tax-legal-compliance-methodology.md, Addenda 1-5. Send now, don't wait on jurisdictional research (item 5 below).
5. OSHA jurisdictional research -- PAUSED, not abandoned (Addendum 9). Full scope documented for pickup without rediscovery: 11/22 OSHA State Plan states researched, 11 fully unresearched (Nevada, New Mexico, North Carolina, Puerto Rico, Tennessee, Utah, Vermont, Virginia, Wyoming, plus formal Minnesota/Michigan writeup), 10 of the 11 researched states need actual-average-penalty backfill (only Oregon currently has both statutory-max and actual-average figures). Resume directly from Addendum 9's scope list when reprioritized -- no rescoping needed, unlike item 1 above.
6. Intake headcount precision redesign -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-headcount-precision-redesign.md). SCHEMA-LEVEL SCOPE -- larger than any other Friction Tax proposal this session: replaces the 6-value headcount bucket dropdown with a precise numeric "about how many employees" stepper (variable increment: steps of 1 from 1-50, 5 from 50-250, 25 from 250-500, 100 above 500). Originates directly from the Demographic Applicability Filter's ADA (15+ employees) / FMLA (50+ employees) coverage-threshold lead for Clusters 1 and 2 -- a precise number resolves the bucket-boundary ambiguity completely. Also affects Cluster 4's Title VII damage-cap tiers (100/200/500) and Cluster 5's OSHA penalty-reduction tiers (25/100/250), both currently approximating against bucket edges that don't align with the real statutory boundaries. Blocks nothing currently in progress, but should be SEQUENCED BEFORE Clusters 1, 2, 4, 5 are finalized against Gemini, since their threshold logic changes once headcount is precise rather than bucketed -- reviewing those clusters against Gemini before this resolves risks reviewing logic that's about to change underneath it. Confirmed this session: no bucket-derivation logic exists anywhere in the codebase today -- PAYROLL_BASELINE_GRID and HEADCOUNT_MIDPOINTS (engine/friction_tax.py) are both keyed directly by the 6 bucket strings (built via `for headcount in HEADCOUNT_BUCKETS`), with no function anywhere that maps a precise int to a bucket; this would need to be built from scratch as part of implementation, not adapted from something existing. IntakeData.headcount's type change (str -> int) and whether IntakeEcho should echo a precise number or bucket-like language client-facing are both still open questions in the doc, not yet decided.
7. Intake industry taxonomy expansion -- PROPOSED, NOT REVIEWED, NOT IMPLEMENTED (prompts/intake-industry-taxonomy-expansion.md). SCHEMA-LEVEL SCOPE, same flag as item 6 -- second intake-schema proposal this session, kept deliberately separate from the headcount-precision redesign per Pete's direction, not combined. Adds "Construction" (NAICS Sector 23) and "Transportation & Warehousing" (NAICS Sectors 48-49) to INTAKE_FIELDS["industry"], expanding 9 -> 11 values. Originates from the Demographic Applicability Filter's Cluster 5 finding that is_high_hazard (HIGH_HAZARD_INDUSTRIES) can only ever fire for 2 of the 9 current industry values, while BLS ranks construction and transportation/warehousing among the highest injury/fatality-rate industries nationally -- both currently fall into "Other," indistinguishable from anything else that doesn't fit. REAL DEPENDENCY, not just a code change: PAYROLL_BASELINE_GRID expands from 6x9=54 cells to 6x11=66 cells -- 12 new cells (Construction and Transportation & Warehousing x all 6 headcount buckets) need genuine SUSB/BLS payroll-baseline research sourced before this is implementation-ready, comparable in scope to the original 54-cell population work, not trivial. HIGH_HAZARD_INDUSTRIES update itself is straightforward (add both new values to the existing set).
8. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.
9. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).
10. Infrastructure housekeeping, opportunistic/lower priority: weak-profile test limitation (generate_answers() weak branch ignoring target_state), calibration runner's untested severity follow-on questions (parked, do not raise unless Pete reopens), test_contract.py pre-existing liability_block KeyError, MemPalace drawer-write issue."""

edit("tools/_mob.txt", "\\\\\\#\\\\\\# MOB v4.91", "\\\\\\#\\\\\\# MOB v4.92")
edit("tools/_mob.txt", _OLD_QUEUE, _NEW_QUEUE)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum9_text = ADDENDUM9_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    addendum9_nested = addendum9_text.replace(
        "# Addendum 9 — Jurisdictional Research: Scoped Backlog, Not Lost",
        "## Addendum 9 — Jurisdictional Research: Scoped Backlog, Not Lost",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM9_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM9_PLACEHOLDER__", addendum9_nested)
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
