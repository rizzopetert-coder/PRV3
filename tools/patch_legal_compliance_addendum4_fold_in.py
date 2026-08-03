"""
PRV3 -- Fold Legal/Compliance Addendum 4 (Cluster 3 locked, the_untouchable
reclassified, Addendum 3 unblocked) into
prompts/friction-tax-legal-compliance-methodology.md, following Addendum 3.

Updates the doc's Status line to reflect both Gemini-review open items
now resolved and Addendum 3 unblocked/ready for review.

Also updates tools/_mob.txt Section 13b: closes the two remaining
sub-items under Legal/Compliance (Cluster 3 disagreement,
the_untouchable reclassification), notes Addendum 3 is now ready for
Gemini review, and records the classification count change (Cluster 1
3->4, Cluster 2 12->11).

Usage:
  python tools/patch_legal_compliance_addendum4_fold_in.py --dry-run
  python tools/patch_legal_compliance_addendum4_fold_in.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM4_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum4_fixed.md"
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

edit(
    DOC,
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
)

edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM4_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.83",
    "\\\\\\#\\\\\\# MOB v4.84",
)

edit(
    "tools/_mob.txt",
    "3. Legal/Compliance tail-risk methodology -- sourcing CLOSED (all 30 states across 5 clusters, all 5 clusters have sourced dollar curves, Addenda 1-2; see prompts/friction-tax-legal-compliance-methodology.md). Three open sub-items surfaced by Gemini's architecture review, none yet resolved: (a) Cross-state aggregation design -- PROPOSED this session (Addendum 3): within-cluster geometric decay (reuses the attritional design's Step 1 math exactly, applied to per-cluster dollar position instead of per-criterion raw score), across-cluster simple addition (no breadth premium, deliberately -- a departure from the attritional Factor B precedent, justified in Addendum 3 on the grounds that different clusters represent legally separate, cumulative claims rather than one entangled condition). Status: proposed, blocked on (b) below -- NOT ready for Gemini review yet. (b) Cluster 3 interpolation disagreement -- Gemini's review proposed a binary step function for Cluster 3, which conflicts with Addendum 2's path-uncertainty (administrative/litigation low/high pair) design for that same cluster; unresolved. (c) the_untouchable reclassification -- currently classified Cluster 2 (class/systemic discrimination); Gemini's review suggests likely Cluster 1 (individual/isolated claim) instead; unresolved.",
    "3. Legal/Compliance tail-risk methodology -- sourcing and classification CLOSED (all 30 states across 5 clusters -- Cluster 1 now 4 states/was 3, Cluster 2 now 11 states/was 12, `the_untouchable` moved Cluster 2 -> Cluster 1 per Addendum 4, resolving Gemini's review flag; all 5 clusters have sourced dollar curves, Addenda 1-2; see prompts/friction-tax-legal-compliance-methodology.md). Cluster 3 interpolation LOCKED this session (Addendum 4): scope-modulated, not path-modulated -- the administrative ($1,465/worker) to litigation ($2,930/worker) range stays a fixed pair regardless of rubric score (preserving Addendum 2's genuine path-uncertainty), while the rubric score instead modulates affected-worker-count/scope via Cluster 2's existing per-capita mechanism, resolving the disagreement with Gemini's proposed binary step function. Structural consequence: Cluster 3 no longer needs a bespoke interpolation rule. Cross-state aggregation design (Addendum 3: within-cluster geometric decay, across-cluster simple addition) is now UNBLOCKED and ready for Gemini review, alongside a fresh review of both resolutions above.",
)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum4_text = ADDENDUM4_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    addendum4_nested = addendum4_text.replace(
        "# Addendum 4 — Cluster 3 Synthesis Locked, the_untouchable Reclassified, Addendum 3 Unblocked",
        "## Addendum 4 — Cluster 3 Synthesis Locked, the_untouchable Reclassified, Addendum 3 Unblocked",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM4_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM4_PLACEHOLDER__", addendum4_nested)
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
