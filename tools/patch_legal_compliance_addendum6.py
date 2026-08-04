"""
PRV3 -- Fold Legal/Compliance Addendum 6 (systematic jurisdictions pass,
California confirmed across all 5 clusters, explicitly scoped) into
prompts/friction-tax-legal-compliance-methodology.md, following
Addendum 5. Updates the doc's Status line and tools/_mob.txt's
Demographic Applicability Filter Priority Queue item (item 4) to note
the jurisdictions/California sub-pass is complete while the broader
50-state / 22-OSHA-State-Plan scope remains open.

Usage:
  python tools/patch_legal_compliance_addendum6.py --dry-run
  python tools/patch_legal_compliance_addendum6.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM6_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum6_fixed.md"
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

edit(
    DOC,
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
    """**Status:** Design in progress. Direction has shifted several times this session as real data
falsified earlier approaches. All 30 Legal-scoring states are classified into 5 mechanism
clusters -- `the_untouchable` reclassified Cluster 2 -> Cluster 1 (Addendum 4, resolving
Gemini's review flag). Cluster 3's interpolation is locked: scope-modulated, not
path-modulated (Addendum 4). Cluster 4 fully resolved into three org_type-gated sub-tracks
(Addendum 5). All 5 clusters now have sourced dollar curves, and the cross-state aggregation
design (Addendum 3) is UNBLOCKED and ready for Gemini review. **Systematic jurisdictions
pass complete for California across all 5 clusters (Addendum 6)** -- FEHA/PAGA/Cal-OSHA
findings sourced and ready to build. Explicitly scoped, not assumed complete: the other 49
states, and the other ~21 OSHA-approved State Plan states specifically for Cluster 5 (federal
OSHA figures confirmed as a floor, not a national accuracy figure, across those states), have
NOT been checked -- flagged in the design as known-incomplete jurisdictional treatment, not
silently treated as accurate everywhere outside California. NOT yet implemented. Does not
supersede the Option A attritional-criteria rescale (turnover/productivity/decision-quality),
which proceeds independently -- this doc is specifically the deferred Legal/Compliance item
that Option A explicitly excluded.""",
)

edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM6_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.87",
    "\\\\\\#\\\\\\# MOB v4.88",
)

edit(
    "tools/_mob.txt",
    '''4. Demographic Applicability Filter -- systematic pass across Clusters 1, 2, 3, 5 -- NOT STARTED. Two live leads already surfaced (Addendum 5), pull the details next time this is picked up: (a) ADA (15+ employees) / FMLA (50+ employees) coverage thresholds likely affect Clusters 1 and 2's "Under 25" headcount bucket -- employers below the statutory threshold may not be covered by those clusters' mechanisms at all, mirrors Cluster 4's own coverage-threshold caveat (Addendum 5); (b) engine/accumulation.py's existing `is_high_hazard` property (checks `industry` against `HIGH_HAZARD_INDUSTRIES`) should probably gate Cluster 5's OSHA-based figures rather than leaving them industry-blind -- pull the actual HIGH_HAZARD_INDUSTRIES list before scoping this.''',
    '''4. Demographic Applicability Filter -- systematic pass across Clusters 1, 2, 3, 5 -- IN PROGRESS. Jurisdictions pass -- California confirmed across all 5 clusters (Addendum 6): Cluster 1 (FEHA lowers ADA/Title VII's 15-employee threshold to 5, any size for harassment), Cluster 2 (CA exposure already captured indirectly via real-settlement per-claimant rates, no new gap), Cluster 3 (PAGA adds $100-200/aggrieved employee per pay period, compounds with time -- worked example: 50 employees, 26 pay periods, $130K/year in PAGA penalties alone before back wages), Cluster 4 (already resolved via Addendum 5's 4b caveat), Cluster 5 (Cal/OSHA serious-violation cap $25,000 vs. federal $16,550, ~51% higher). Bigger finding from this pass: 22 states run their own OSHA-approved State Plans required to be "at least as effective" as federal OSHA (equal or higher penalties, never lower) -- Cluster 5's flat federal figures are confirmed as a floor across ~22 states' worth of clients, not a national accuracy figure; materially bigger gap than the California findings themselves. Remaining ~21 OSHA State Plan states + other high-protection states (NY/MA/IL/WA candidates) -- not started, real scoped gap, explicitly NOT assumed accurate by default. Original two leads from Addendum 5, still open: (a) ADA (15+ employees) / FMLA (50+ employees) coverage thresholds for Clusters 1 and 2's "Under 25" headcount bucket -- partially addressed for CA clients via FEHA's lower 5-employee threshold (Addendum 6), federal-baseline states still open, and see the separate intake headcount precision redesign proposal (item 5) which resolves this more completely once implemented; (b) `HIGH_HAZARD_INDUSTRIES` PULLED this session (engine/data/intake.py:285): `{"Manufacturing & Industrial", "Healthcare & Life Sciences"}` -- Construction and Logistics are NOT in the current intake industry list (per the file's own comment, pending intake list expansion if added), so Cluster 5's `is_high_hazard`-based gating can only ever cover these 2 of PRV3's 9 industry values as currently scoped; still needs building into Cluster 5's OSHA-based figures, not yet done.''',
)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum6_text = ADDENDUM6_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    addendum6_nested = addendum6_text.replace(
        "# Addendum 6 — Systematic Jurisdictions Pass: California Confirmed as a Cross-Cluster Outlier",
        "## Addendum 6 — Systematic Jurisdictions Pass: California Confirmed as a Cross-Cluster Outlier",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM6_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM6_PLACEHOLDER__", addendum6_nested)
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
