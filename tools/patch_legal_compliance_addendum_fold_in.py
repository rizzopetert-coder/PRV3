"""
PRV3 -- Fold the Legal/Compliance mechanism-classification addendum into
prompts/friction-tax-legal-compliance-methodology.md as new sections
(not a replacement of the existing open items).

Also updates tools/_mob.txt Section 13b: marks the Legal/Compliance
taxonomy classification task complete, notes the two remaining
sub-items (a third verified per-claimant rate for Cluster 2, and the
Cluster 3 wage-and-hour multiplier formula) before implementation.

Usage:
  python tools/patch_legal_compliance_addendum_fold_in.py --dry-run
  python tools/patch_legal_compliance_addendum_fold_in.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDENDUM_CONTENT_PATH = Path(
    r"C:\Users\rizzo\AppData\Local\Temp\claude\c--Users-rizzo-PRV3"
    r"\750c13ed-f59b-40de-b172-846de52f8b13\scratchpad\addendum_fixed.md"
)

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

# --- (a) Status line ---
edit(
    DOC,
    """**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. NOT yet reviewed by Gemini, NOT yet implemented. Does not
supersede the Option A attritional-criteria rescale (turnover/productivity/decision-quality),
which proceeds independently — this doc is specifically the deferred Legal/Compliance item
that Option A explicitly excluded.""",
    """**Status:** Design in progress. Direction has shifted twice already this session as real data
falsified two earlier approaches. All 30 Legal-scoring states are now classified into 5
mechanism clusters, with 4 of 5 clusters' dollar curves sourced (Addendum, below) -- ready
for Gemini architecture review. NOT yet implemented. Does not supersede the Option A
attritional-criteria rescale (turnover/productivity/decision-quality), which proceeds
independently -- this doc is specifically the deferred Legal/Compliance item that Option A
explicitly excluded.""",
)

# --- (b) bridging note in "Current direction" section ---
edit(
    DOC,
    """4. **Whistleblower/regulatory exposure** — explicitly NOT headcount-scaled. Driven by the
   underlying violation's sanction size; a 40-person company with a real SEC-triggering
   violation faces the same order of magnitude as a much larger company. E2 flags this as the
   single most extreme financial-consequence narrative in the taxonomy for exactly this reason
   — headcount offers no protection here. Needs its own uncapped treatment, likely closer to
   "if present, flag at real-world severity" than any scaled formula.

## Open questions, unresolved""",
    """4. **Whistleblower/regulatory exposure** — explicitly NOT headcount-scaled. Driven by the
   underlying violation's sanction size; a 40-person company with a real SEC-triggering
   violation faces the same order of magnitude as a much larger company. E2 flags this as the
   single most extreme financial-consequence narrative in the taxonomy for exactly this reason
   — headcount offers no protection here. Needs its own uncapped treatment, likely closer to
   "if present, flag at real-world severity" than any scaled formula.

**Expanded to 5 clusters this session** -- a distinct Safety/regulatory cluster (per-incident,
OSHA-penalty-driven) was split out from the 4 buckets above once real states were classified
against them. See the Addendum below for the complete 5-cluster classification and sourced
dollar curves.

## Open questions, unresolved""",
)

# --- (d) annotate open-question items 1 and 5 ---
edit(
    DOC,
    """1. **Does each Legal-criterion taxonomy state need to be classified by mechanism type** (which
   of the four buckets above it belongs to) before this design can be implemented? This is real
   classification work across however many of the 57 states carry a nonzero Legal score — not
   yet scoped, not started.""",
    """1. **Does each Legal-criterion taxonomy state need to be classified by mechanism type** (which
   of the four buckets above it belongs to) before this design can be implemented? This is real
   classification work across however many of the 57 states carry a nonzero Legal score — not
   yet scoped, not started. **RESOLVED this session -- see Addendum below: all 30 states
   classified across 5 clusters (the original 4 buckets plus a newly split-out Safety/
   regulatory cluster).**""",
)

edit(
    DOC,
    """5. **A second verified per-claimant or per-mechanism rate** is needed before the $2,500 Beck
   figure is treated as anything more than a single illustrative data point.""",
    """5. **A second verified per-claimant or per-mechanism rate** is needed before the $2,500 Beck
   figure is treated as anything more than a single illustrative data point. **Partially
   addressed this session (see Addendum): Clusters 4 and 5 now have sourced floors/ceilings.
   Cluster 2's per-claimant range still rests on exactly two verified data points (Beck v.
   Boeing, Velez v. Novartis) -- a third would strengthen it, per the Addendum's own "Still
   open" list.**""",
)

# --- (c) insert the full addendum as a new section, right before "Structural implications" ---
edit(
    DOC,
    """## Structural implications (bigger than Option A)""",
    "__ADDENDUM_PLACEHOLDER__\n\n## Structural implications (bigger than Option A)",
)

# --- (e) Next steps updates ---
edit(
    DOC,
    """1. Classify which of the 57 states carry a Legal/Compliance score, and which mechanism bucket
   (individual / class-discrimination / wage-hour / whistleblower) each represents — real
   research and taxonomy work, not yet started.
2. Find a second verified class-action per-claimant rate to test the $2,500 figure against.
3. Resolve the wage-and-hour multiplier question in light of DOL's 2025 liquidated-damages
   policy change.
4. Resolve the four open questions above (mechanism-selection logic, probability-weighting,
   client-facing prominence, and rate verification).
5. Gemini architecture review — not yet sent, and shouldn't be until the above is further
   resolved, since the mechanism-aware structure is still actively changing.""",
    """1. ~~Classify which of the 57 states carry a Legal/Compliance score, and which mechanism
   bucket each represents~~ **DONE this session -- see Addendum: all 30 states classified
   across 5 mechanism clusters.**
2. Find a second verified class-action per-claimant rate to test the $2,500 figure against
   (Cluster 2 specifically -- Clusters 4 and 5 now have sourced floors/ceilings per the
   Addendum; still open for Cluster 2).
3. Resolve the wage-and-hour multiplier question in light of DOL's 2025 liquidated-damages
   policy change (Cluster 3, per the Addendum -- not yet built into a formula).
4. Resolve the four open questions above (mechanism-selection logic, probability-weighting,
   client-facing prominence, and rate verification).
5. Gemini architecture review -- classification and cluster structure now ready per the
   Addendum (all 30 states classified, 4/5 clusters' dollar curves sourced). Items 2 and 3
   above (Cluster 2's third data point, Cluster 3's multiplier formula) remain open and can be
   resolved in parallel with or before that review, per Pete's call.""",
)


# ============================================================
# tools/_mob.txt
# ============================================================

edit(
    "tools/_mob.txt",
    '3. Legal/Compliance tail-risk methodology -- mechanism-aware design in progress, see prompts/friction-tax-legal-compliance-methodology.md. Next concrete step: classify which of the 57 states carry a Legal score and which mechanism bucket each represents (individual claim / class-discrimination / wage-hour / whistleblower) -- real taxonomy work, not started.',
    '3. Legal/Compliance tail-risk methodology -- mechanism classification COMPLETE this session: all 30 Legal-scoring states classified across 5 mechanism clusters (individual claim, class-discrimination, wage-hour, whistleblower, and a newly split-out safety/regulatory cluster), 4 of 5 clusters\' dollar curves sourced, see prompts/friction-tax-legal-compliance-methodology.md (Addendum). Two sub-items remain before implementation: (a) a third verified per-claimant rate for Cluster 2 (currently rests on exactly two verified data points, Beck v. Boeing and Velez v. Novartis), (b) the Cluster 3 wage-and-hour multiplier formula, given DOL\'s mid-2025 liquidated-damages policy change. Ready for Gemini architecture review in parallel with resolving those two.',
)


def apply(dry_run: bool) -> int:
    changed = 0
    addendum_text = ADDENDUM_CONTENT_PATH.read_text(encoding="utf-8").rstrip("\n")
    # Wrap the addendum's own H1 down to an H2-nested block under a new
    # top-level section heading, and demote its internal H2s to H3s so it
    # nests cleanly as a subsection of this doc rather than competing at
    # the same heading level.
    addendum_nested = addendum_text.replace(
        "# Addendum — Mechanism Classification & Cluster Dollar Curves",
        "## Addendum — Mechanism Classification & Cluster Dollar Curves",
        1,
    ).replace("\n## ", "\n### ")

    for rel_path, old, new in EDITS:
        if "__ADDENDUM_PLACEHOLDER__" in new:
            new = new.replace("__ADDENDUM_PLACEHOLDER__", addendum_nested)
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
