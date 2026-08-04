"""
PRV3 -- Fold Legal/Compliance Addendum 5 (Cluster 4 resolved into three
org_type-gated sub-tracks -- a structural reframe) into
prompts/friction-tax-legal-compliance-methodology.md, following
Addendum 4. Also logs the IntakeEcho org_type gap as a new Decision
Register entry, and updates Section 13b: Cluster 4 marked resolved,
plus a new Priority Queue item for the systematic Demographic
Applicability Filter pass across Clusters 1, 2, 3, 5.

Usage:
  python tools/patch_legal_compliance_addendum5_and_intakeecho.py --dry-run
  python tools/patch_legal_compliance_addendum5_and_intakeecho.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM5_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum5_fixed.md"
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

edit(
    DOC,
    """**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. All 30 Legal-scoring states are classified into 5
mechanism clusters -- `the_untouchable` reclassified Cluster 2 -> Cluster 1 (Addendum 4,
resolving Gemini's review flag). Cluster 3's interpolation is locked: scope-modulated (rubric
score sets affected-worker-count via Cluster 2's existing per-capita mechanism), not
path-modulated (administrative/litigation stays a fixed low/high pair regardless of score),
resolving the Addendum 2 vs. Gemini's-review disagreement. All 5 clusters have sourced dollar
curves (Addenda 1 and 2). The cross-state aggregation design (Addendum 3: within-cluster
geometric decay, across-cluster simple addition) is now UNBLOCKED and ready for Gemini
review, alongside a fresh review of both resolutions above. NOT yet implemented. Does not
supersede the Option A attritional-criteria rescale (turnover/productivity/decision-quality),
which proceeds independently -- this doc is specifically the deferred Legal/Compliance item
that Option A explicitly excluded.""",
    """**Status:** Design in progress. Direction has shifted several times this session as real data
falsified earlier approaches. All 30 Legal-scoring states are classified into 5 mechanism
clusters -- `the_untouchable` reclassified Cluster 2 -> Cluster 1 (Addendum 4, resolving
Gemini's review flag). Cluster 3's interpolation is locked: scope-modulated, not
path-modulated (Addendum 4). **Cluster 4 fully resolved this session into three org_type-
gated sub-tracks (Addendum 5) -- a structural reframe, not a minor edit:** 4a SEC/Dodd-Frank
(org_type=Publicly traded), 4b general private-sector retaliation (org_type=Founder-led /
Privately held professional leadership / Nonprofit / most PE-VC-backed, statutory-cap-
anchored), 4c government (org_type=Government, qualitative only, no dollar figure -- thin
MSPB data). All 5 clusters now have sourced dollar curves, and the cross-state aggregation
design (Addendum 3) is UNBLOCKED and ready for Gemini review, alongside the rest of the
Legal/Compliance package. NOT yet implemented. Does not supersede the Option A attritional-
criteria rescale (turnover/productivity/decision-quality), which proceeds independently --
this doc is specifically the deferred Legal/Compliance item that Option A explicitly
excluded.""",
)

edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM5_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.85",
    "\\\\\\#\\\\\\# MOB v4.86",
)

# --- Decision Register: new row for the IntakeEcho org_type gap,
# inserted after the Cluster 4 finding row added last session ---
edit(
    "tools/_mob.txt",
    "Pete's call -- reopen Cluster 4 design once org_type-based gating (or an explicit non-gated fallback) is decided |",
    "Pete's call -- reopen Cluster 4 design once org_type-based gating (or an explicit non-gated fallback) is decided |\n| web/lib/types.ts IntakeEcho missing org_type -- flagged, not urgent | 3 | Open -- not urgent, Legal/Compliance not yet implemented | None yet -- becomes a real blocker only once Legal/Compliance client-facing output needs org_type surfaced | IntakeEcho (web/lib/types.ts -- the type that echoes intake context into client-facing PrivateOutputPayload/ShareableOutputPayload) carries `industry` but not `org_type`, confirmed by direct read while pulling the real intake schema for the Cluster 4 SEC-applicability finding. org_type is the field that drives which Legal/Compliance regulatory sub-track applies (Addendum 5: 4a SEC / 4b general private-sector / 4c government) -- if that needs to be surfaced client-facing (e.g. so the client understands why their exposure range reflects one track and not another), IntakeEcho needs a new field. Not urgent now since Legal/Compliance isn't implemented yet, but flagged here so it isn't rediscovered as a surprise later. | This session (Claude Code) | Whenever Legal/Compliance implementation reaches the client-facing output design step -- not a forced check-in before then |",
)

# --- Section 13b Priority Queue: item 3 updated (Cluster 4 resolved),
# new item 4 inserted (systematic Demographic Applicability Filter
# pass), items 4-7 renumbered to 5-8 ---
edit(
    "tools/_mob.txt",
    """3. Legal/Compliance tail-risk methodology -- sourcing and classification CLOSED (all 30 states across 5 clusters -- Cluster 1 now 4 states/was 3, Cluster 2 now 11 states/was 12, `the_untouchable` moved Cluster 2 -> Cluster 1 per Addendum 4, resolving Gemini's review flag; all 5 clusters have sourced dollar curves, Addenda 1-2; see prompts/friction-tax-legal-compliance-methodology.md). Cluster 3 interpolation LOCKED this session (Addendum 4): scope-modulated, not path-modulated -- the administrative ($1,465/worker) to litigation ($2,930/worker) range stays a fixed pair regardless of rubric score (preserving Addendum 2's genuine path-uncertainty), while the rubric score instead modulates affected-worker-count/scope via Cluster 2's existing per-capita mechanism, resolving the disagreement with Gemini's proposed binary step function. Structural consequence: Cluster 3 no longer needs a bespoke interpolation rule. Cross-state aggregation design (Addendum 3: within-cluster geometric decay, across-cluster simple addition) is now UNBLOCKED and ready for Gemini review, alongside a fresh review of both resolutions above.
4. /diagnostic Stages 4-5 rescoping -- no surviving plan doc, requires Pete to rescope from scratch. Prioritized above other backlog items because it's a live user-facing surface gap, not because it's ready to start.
5. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.
6. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).
7. Infrastructure housekeeping, opportunistic/lower priority: weak-profile test limitation (generate_answers() weak branch ignoring target_state), calibration runner's untested severity follow-on questions (parked, do not raise unless Pete reopens), test_contract.py pre-existing liability_block KeyError, MemPalace drawer-write issue.""",
    """3. Legal/Compliance tail-risk methodology -- sourcing and classification CLOSED (all 30 states across 5 clusters -- Cluster 1 now 4 states/was 3, Cluster 2 now 11 states/was 12, `the_untouchable` moved Cluster 2 -> Cluster 1 per Addendum 4, resolving Gemini's review flag; all 5 clusters have sourced dollar curves, Addenda 1-2; see prompts/friction-tax-legal-compliance-methodology.md). Cluster 3 interpolation LOCKED (Addendum 4): scope-modulated, not path-modulated -- the administrative ($1,465/worker) to litigation ($2,930/worker) range stays a fixed pair regardless of rubric score (preserving Addendum 2's genuine path-uncertainty), while the rubric score instead modulates affected-worker-count/scope via Cluster 2's existing per-capita mechanism, resolving the disagreement with Gemini's proposed binary step function. **Cluster 4 RESOLVED (Addendum 5) -- structural reframe, not a minor edit:** the original single "uncapped, sanction-driven" SEC-anchored curve only ever described one org_type's reality; replaced with three org_type-gated sub-tracks -- 4a SEC/Dodd-Frank (org_type=Publicly traded, unchanged design, correctly scoped now), 4b general private-sector retaliation (org_type=Founder-led/Privately held professional leadership/Nonprofit/most PE-VC-backed, anchored to 42 U.S.C. Sec 1981a(b)(3)'s statutory cap mapped onto PRV3's headcount buckets, $50K-$300K, California's uncapped FEHA flagged as the first concrete jurisdictions-override case), 4c government (org_type=Government, qualitative only -- no dollar figure, genuinely thin MSPB settlement data, not a research shortfall). See prompts/friction-tax-legal-compliance-methodology.md (Addendum 5). Cross-state aggregation (Addendum 3) now needs org_type-gating resolved before within-cluster decay can run for any Cluster 4 state -- not a structural change to Addendum 3 itself, but a new implementation prerequisite. Cross-state aggregation design is ready for Gemini review, alongside the rest of the Legal/Compliance package.
4. Demographic Applicability Filter -- systematic pass across Clusters 1, 2, 3, 5 -- NOT STARTED. Two live leads already surfaced (Addendum 5), pull the details next time this is picked up: (a) ADA (15+ employees) / FMLA (50+ employees) coverage thresholds likely affect Clusters 1 and 2's "Under 25" headcount bucket -- employers below the statutory threshold may not be covered by those clusters' mechanisms at all, mirrors Cluster 4's own coverage-threshold caveat (Addendum 5); (b) engine/accumulation.py's existing `is_high_hazard` property (checks `industry` against `HIGH_HAZARD_INDUSTRIES`) should probably gate Cluster 5's OSHA-based figures rather than leaving them industry-blind -- pull the actual HIGH_HAZARD_INDUSTRIES list before scoping this.
5. /diagnostic Stages 4-5 rescoping -- no surviving plan doc, requires Pete to rescope from scratch. Prioritized above other backlog items because it's a live user-facing surface gap, not because it's ready to start.
6. causation_pattern -> resolution_families.py routing influence -- split off from Diagnostic Dimension Expansion, not started, no scoping doc.
7. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).
8. Infrastructure housekeeping, opportunistic/lower priority: weak-profile test limitation (generate_answers() weak branch ignoring target_state), calibration runner's untested severity follow-on questions (parked, do not raise unless Pete reopens), test_contract.py pre-existing liability_block KeyError, MemPalace drawer-write issue.""",
)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum5_text = ADDENDUM5_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    addendum5_nested = addendum5_text.replace(
        "# Addendum 5 — Cluster 4 Resolved: Three Sub-Tracks Replace the Single Uncapped Curve",
        "## Addendum 5 — Cluster 4 Resolved: Three Sub-Tracks Replace the Single Uncapped Curve",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM5_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM5_PLACEHOLDER__", addendum5_nested)
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
