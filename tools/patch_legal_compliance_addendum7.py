"""
PRV3 -- Fold Legal/Compliance Addendum 7 (OSHA State Plan research, 7 of
22 states, in progress -- Washington's finding corrected before append)
into prompts/friction-tax-legal-compliance-methodology.md, following
Addendum 6. Updates the doc's Status line and tools/_mob.txt's item 4
(Demographic Applicability Filter) to reflect 7/22 progress.

Washington correction: the source addendum originally placed Washington
in the "exceeds federal" category. WAC 296-900-14010 (serious) and WAC
296-900-14020 (willful/repeat) are two different violation categories
with two different statutory floors ($7,000 and $70,000 respectively,
"or federal max, whichever is more"), not two competing figures for one
category as originally implied -- both floors sit below federal's own
current live maximums, so Washington's effective penalties equal
federal's exactly. Corrected to clean parity (alongside Alaska, Hawaii)
before this script was written, flagged inline as a correction, not a
refinement.

Usage:
  python tools/patch_legal_compliance_addendum7.py --dry-run
  python tools/patch_legal_compliance_addendum7.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM7_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum7_fixed.md"
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
    """**Status:** Design in progress. Direction has shifted several times this session as real data
falsified earlier approaches. All 30 Legal-scoring states are classified into 5 mechanism
clusters -- `the_untouchable` reclassified Cluster 2 -> Cluster 1 (Addendum 4, resolving
Gemini's review flag). Cluster 3's interpolation is locked: scope-modulated, not
path-modulated (Addendum 4). Cluster 4 fully resolved into three org_type-gated sub-tracks
(Addendum 5). All 5 clusters now have sourced dollar curves, and the cross-state aggregation
design (Addendum 3) is UNBLOCKED and ready for Gemini review. Systematic jurisdictions
pass complete for California across all 5 clusters (Addendum 6). **OSHA State Plan research
for Cluster 5 IN PROGRESS, 7 of 22 states (Addendum 7)** -- California, Washington, Oregon,
Alaska, Hawaii, Arizona, Indiana researched; variation confirmed genuinely bidirectional
(exceeds federal flat, exceeds federal conditionally/outcome-triggered, clean statutory
parity, statutory parity with documented under-enforcement, and genuinely below federal, all
represented across just 7 states) -- NOT a finished input for implementation, 15 states
remain. Explicitly scoped, not assumed complete: the other 49 states outside Cluster 5's OSHA
research, and the 15 remaining OSHA State Plan states specifically, have NOT been checked --
flagged in the design as known-incomplete jurisdictional treatment, not silently treated as
accurate everywhere outside what's actually been researched. NOT yet implemented. Does not
supersede the Option A attritional-criteria rescale (turnover/productivity/decision-quality),
which proceeds independently -- this doc is specifically the deferred Legal/Compliance item
that Option A explicitly excluded.""",
)

edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM7_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.89",
    "\\\\\\#\\\\\\# MOB v4.90",
)

edit(
    "tools/_mob.txt",
    '''Bigger finding from this pass: 22 states run their own OSHA-approved State Plans required to be "at least as effective" as federal OSHA (equal or higher penalties, never lower) -- Cluster 5's flat federal figures are confirmed as a floor across ~22 states' worth of clients, not a national accuracy figure; materially bigger gap than the California findings themselves. Remaining ~21 OSHA State Plan states + other high-protection states (NY/MA/IL/WA candidates) -- not started, real scoped gap, explicitly NOT assumed accurate by default.''',
    '''Bigger finding from this pass: 22 states run their own OSHA-approved State Plans required to be "at least as effective" as federal OSHA (equal or higher penalties, never lower) -- Cluster 5's flat federal figures are confirmed as a floor across ~22 states' worth of clients, not a national accuracy figure; materially bigger gap than the California findings themselves. Jurisdictions pass, Cluster 5 -- 7 of 22 OSHA State Plan states researched (CA, WA, OR, AK, HI, AZ, IN), 15 remaining (Addendum 7). Every state checked so far has produced a genuinely distinct finding -- no simple pattern has emerged, treat remaining research as comparable effort per state, not diminishing. CORRECTION (this session): Washington was originally miscategorized as exceeding federal; corrected and moved to clean parity alongside Alaska/Hawaii -- its WAC floor mechanisms (serious: federal max or $7,000; willful/repeat: federal max or $70,000, whichever is more) both currently sit below federal's own live maximums, so Washington's effective penalties equal federal's exactly. Other high-protection states outside the OSHA State Plan list (NY/MA/IL/WA candidates for other clusters) -- not started, real scoped gap, explicitly NOT assumed accurate by default.''',
)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum7_text = ADDENDUM7_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    addendum7_nested = addendum7_text.replace(
        "# Addendum 7 — OSHA State Plan Research, 7 of 22 States (In Progress)",
        "## Addendum 7 — OSHA State Plan Research, 7 of 22 States (In Progress)",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM7_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM7_PLACEHOLDER__", addendum7_nested)
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
