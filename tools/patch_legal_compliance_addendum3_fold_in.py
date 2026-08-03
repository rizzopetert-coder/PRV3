"""
PRV3 -- Fold Legal/Compliance Addendum 3 (cross-state aggregation design)
into prompts/friction-tax-legal-compliance-methodology.md, following
Addendum 2. Updates the doc's Status line to explicitly walk back "ready
for Gemini review" -- Addendum 3 is NOT ready, blocked on Cluster 3's
interpolation disagreement and the_untouchable's pending reclassification.

Also updates tools/_mob.txt Section 13b: adds the cross-state aggregation
design as a new sub-item under the Legal/Compliance line, and surfaces
two previously-untracked open items from Gemini's architecture review
(Cluster 3 disagreement, the_untouchable reclassification) that neither
this doc nor the MOB had logged before this addendum.

Usage:
  python tools/patch_legal_compliance_addendum3_fold_in.py --dry-run
  python tools/patch_legal_compliance_addendum3_fold_in.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM3_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum3_fixed.md"
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

edit(
    DOC,
    """**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. All 30 Legal-scoring states are now classified into 5
mechanism clusters, and all 5 clusters now have sourced dollar curves (Addenda 1 and 2,
below) -- ready for Gemini architecture review. NOT yet implemented. Does not supersede the
Option A attritional-criteria rescale (turnover/productivity/decision-quality), which
proceeds independently -- this doc is specifically the deferred Legal/Compliance item that
Option A explicitly excluded.""",
    """**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. All 30 Legal-scoring states are classified into 5
mechanism clusters, with one reclassification still pending (`the_untouchable`, currently
Cluster 2, likely Cluster 1 per Gemini's review -- unresolved), and all 5 clusters have
sourced dollar curves (Addenda 1 and 2). A cross-state aggregation design is now proposed
(Addendum 3, below: within-cluster geometric decay, across-cluster simple addition) but is
NOT yet ready for Gemini review -- blocked on Cluster 3's interpolation disagreement
(path-uncertainty pair vs. rubric-score mapping, surfaced by Gemini's review, unresolved)
resolving first. NOT yet implemented. Does not supersede the Option A attritional-criteria
rescale (turnover/productivity/decision-quality), which proceeds independently -- this doc
is specifically the deferred Legal/Compliance item that Option A explicitly excluded.""",
)

edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM3_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.82",
    "\\\\\\#\\\\\\# MOB v4.83",
)

edit(
    "tools/_mob.txt",
    "3. Legal/Compliance tail-risk methodology -- CLOSED this session: mechanism classification complete (all 30 states across 5 clusters) AND all 5 clusters now have sourced dollar curves (Addendum 2: Cluster 2 restructured into two tiers, compensatory ~$1,800-2,500/claimant vs. punitive-inclusive ~$25,000-31,000/claimant, resolved via a third verified data point, Jock v. Sterling Jewelers; Cluster 3 fully sourced, administrative path $1,465/worker, litigation path $2,930/worker, using the corrected FLSA 2x multiplier). See prompts/friction-tax-legal-compliance-methodology.md (Addenda 1 and 2). Design-level open items remain (tier-selection logic is a judgment call, not sourced evidence; per-cluster rubric-score-to-dollar-curve shape not decided; Cluster 3's affected-subgroup definition needs data-availability confirmation) but the sourcing gap blocking implementation is closed. Ready for Gemini architecture review.",
    "3. Legal/Compliance tail-risk methodology -- sourcing CLOSED (all 30 states across 5 clusters, all 5 clusters have sourced dollar curves, Addenda 1-2; see prompts/friction-tax-legal-compliance-methodology.md). Three open sub-items surfaced by Gemini's architecture review, none yet resolved: (a) Cross-state aggregation design -- PROPOSED this session (Addendum 3): within-cluster geometric decay (reuses the attritional design's Step 1 math exactly, applied to per-cluster dollar position instead of per-criterion raw score), across-cluster simple addition (no breadth premium, deliberately -- a departure from the attritional Factor B precedent, justified in Addendum 3 on the grounds that different clusters represent legally separate, cumulative claims rather than one entangled condition). Status: proposed, blocked on (b) below -- NOT ready for Gemini review yet. (b) Cluster 3 interpolation disagreement -- Gemini's review proposed a binary step function for Cluster 3, which conflicts with Addendum 2's path-uncertainty (administrative/litigation low/high pair) design for that same cluster; unresolved. (c) the_untouchable reclassification -- currently classified Cluster 2 (class/systemic discrimination); Gemini's review suggests likely Cluster 1 (individual/isolated claim) instead; unresolved.",
)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum3_text = ADDENDUM3_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    addendum3_nested = addendum3_text.replace(
        "# Addendum 3 — Cross-State Legal/Compliance Aggregation",
        "## Addendum 3 — Cross-State Legal/Compliance Aggregation",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM3_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM3_PLACEHOLDER__", addendum3_nested)
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
